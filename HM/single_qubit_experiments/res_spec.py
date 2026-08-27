# Resonator spectroscopy
# Step 0 query the LO and find out the LO frequency
# determine the previous calibrated frequency
# TODO: need to track units for all the rr if lo variables etc

import time
import json
from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from Configuration_Files.config_dictionaries import rr_IF, q_IF, rr_LO, q_LO, f
from HM.utilities.post_processing_utils import return_elec_delay
from HM.utilities.files_utils import save_json
import numpy as np
from Helper_Functions.macros import update_config_rr
from Helper_Functions.spectro_helper import smooth_filter
from qm.qua import program, declare, for_, update_frequency, fixed, declare_stream, wait, measure, save, stream_processing, demod
from qualang_tools.loops import from_array

from qm import QuantumMachinesManager, SimulationConfig, LoopbackInterface
import matplotlib.pyplot as plt
import logging
from termcolor import cprint
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class ResonatorSpectroscopy(SingleQubitExperiment):
    r"""
    Resonator spectroscopy (OPX/QUA) for a single readout resonator.

    How the resonance selection works (detailed, in English):

    - **Build the complex response**:
      - Measure I and Q vs frequency and form `s(f) = I + 1j*Q`.

    - **Iterative phase correction / “flattening”** (`iterative_phase_correct`):
      - Unwrap the measured phase of `s(f)` so it is continuous.
      - Estimate the background *linear* phase slope from the sweep **edges**:
        take phase *differences* (`diff(phase)`) in the first and last
        `phase_slope_edge_npts` points and use a **median** (robust to outliers and to
        the resonance region).
      - Subtract that linear slope versus frequency.
      - Smooth the result with a **reflect-padded moving-average filter**
        (`phase_smooth_window`, forced odd) so the endpoints don’t develop kinks.
      - Remove any remaining constant phase offset by zero-centering the smoothed phase.
      - Repeat for `phase_correction_iters`.
      - Rebuild the final corrected complex signal as **original magnitude + corrected phase**
        (magnitude stays untouched; only phase is flattened).

    - **Compute a robust “phase change vs frequency” curve** (`_robust_phase_slope_rad_per_MHz`):
      - Compute the phase-slope directly from the *complex* signal (instead of from
        `diff(unwrap(angle))`), so a single unwrap jump cannot create a huge fake spike.
      - Apply a **light reflect-padded moving average** (window ≈ `phase_smooth_window`).
      - Build a heavily smoothed **trend** (window ≈ `7×phase_smooth_window`) and subtract it
        to get residuals.
      - Flag narrow spikes using a **MAD-based** threshold and replace flagged points by
        **linear interpolation** between neighboring good points.

    - **Final pick (trend filter + edge ignore)**:
      - Ignore edge regions: `phase_selection_ignore_npts` is computed from
        `phase_selection_ignore_frac`, plus at least `phase_padding_npts` and one smoothing window.
      - Smooth the cleaned phase-slope again with a **heavier reflect-padded moving average**
        (`phase_pick_smooth_window`; if 0 it auto-chooses ≈ 2% of sweep points, min 21).
      - Choose the resonance index as the **minimum** of this heavily-smoothed “trend” curve
        within the non-ignored central region.
    """
    def __init__(self, rr_no: int, q_no: int = None, **kwargs):

        super().__init__(q_no, rr_no, expt_name="res_spec", **kwargs)
        # Keep a record of the previously calibrated resonator frequency (MHz)
        # as loaded from `fr_vals.json` via the base class.
        self.prev_rr_frequency = float(self.fr)
        # If True, show additional readout parameters in plot info box.
        self.verbose = bool(kwargs.get("verbose", False))
        self.update_config = bool(kwargs.get("update_config", False))
        self.sweep_span_MHz = kwargs.get("sweep_span_MHz", 20)
        self.sweep_step_MHz = kwargs.get("sweep_step_MHz", 1e-2)
        self.freq_list_MHz = np.round(np.arange(self.fr - self.sweep_span_MHz/2, self.fr + self.sweep_span_MHz/2, self.sweep_step_MHz), 5)


        ### KWARGS ###
        # Readout length in clock cycles. Must be <= rep_rate_clk for non-negative wait.
        self.ro_len = int(kwargs.get("ro_len", 4000)) #longer ro len means more time to measure the signal
        self.integ_len = kwargs.get("integ_len", 4000) #longer integ len means more time to integrate the signal
        self.calc_e_delay = kwargs.get("calc_e_delay", True)
        self.calc_phase_offset = kwargs.get("calc_phase_offset", True)
        # Phase correction settings (used in analyze_and_plot)
        self.phase_correction_iters = int(
            kwargs.get("phase_correction_iters", kwargs.get("n_phase_correction_iters", 4))
        )
        self.phase_smooth_window = int(kwargs.get("phase_smooth_window", 5))
        self.phase_padding_npts = int(kwargs.get("phase_padding_npts", 5))
        self.phase_slope_edge_npts = int(kwargs.get("phase_slope_edge_npts", 100))
        # Phase-resonance picker robustness controls
        self.phase_selection_ignore_frac = float(kwargs.get("phase_selection_ignore_frac", 0.08))
        self.phase_pick_smooth_window = int(kwargs.get("phase_pick_smooth_window", 0))  # 0 => auto

        ### Overwrite the base class values ###
        # Ensure repetition period is long enough for the readout pulse.
        # (Negative waits make QM compilation fail with "Failed to add job to queue".)
        _default_rep_rate = max(5000, self.ro_len + 4)
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", _default_rep_rate))
        self.rr_amp = kwargs.get("rr_amp", 0.01) #Long RO Low Amplitude


        ## Update the QM config ###
        update_config_rr(self.config, self.q_no, self.rr_no, self.rr_amp, self.integ_len)
        self.rr_IF_sweep_MHz = np.round(self.freq_list_MHz - np.ones_like(self.freq_list_MHz) * self.rr_lo, 5)

        # Integer Hz sweep for QUA loop (avoids step=0 in stream metadata when using declare(int))
        self._f_start_Hz = int(round(self.rr_IF_sweep_MHz[0] * 1e6))
        self._f_step_Hz = max(1, int(round(self.sweep_step_MHz * 1e6)))
        self._n_sweep_points = len(self.freq_list_MHz)
        self._f_stop_Hz = self._f_start_Hz + self._n_sweep_points * self._f_step_Hz  # exact count for buffer
        


    def _estimate_phase_slope_rad_per_MHz(self, unwrapped_phase: np.ndarray) -> float:
        """
        Robust slope estimate for an unwrapped phase vs frequency sweep.

        Uses a median of phase differences from both edges of the sweep to
        avoid resonance region bias. Returns slope in rad/MHz.
        """
        phase_diff = np.asarray(np.diff(unwrapped_phase), dtype=np.float64)
        if phase_diff.size == 0:
            return 0.0

        edge = max(1, int(self.phase_slope_edge_npts))
        edge = min(edge, phase_diff.size)
        samples = np.concatenate([phase_diff[:edge], phase_diff[-edge:]])

        # phase_diff is per-step; divide by step size to get rad/MHz
        return float(np.median(samples) / self.sweep_step_MHz)

    def _smooth_and_pad_phase(self, phase: np.ndarray) -> np.ndarray:
        """
        Smooth an (unwrapped) phase-like array without introducing edge kinks.

        NOTE:
        - `np.convolve(..., mode="same")` behaves like zero-padding at the ends,
          and then splicing the original endpoints back in creates a visible kink
          at the splice boundary. That kink can dominate derivatives and break
          phase-based resonance picking.
        - Here we use reflect-padding and a "valid" convolution so the output is
          the same length *and* smoothly matches the endpoints.
        """
        x = np.asarray(phase, dtype=np.float64)
        n = int(x.size)
        if n == 0:
            return x.copy()

        window = max(1, int(self.phase_smooth_window))
        if window <= 1 or n < 3:
            return x.copy()

        # Prefer an odd window to avoid half-sample shifts.
        if window % 2 == 0:
            window += 1
        window = min(window, n if (n % 2 == 1) else max(1, n - 1))
        if window <= 1:
            return x.copy()

        half = window // 2
        kernel = np.ones(window, dtype=np.float64) / float(window)
        xpad = np.pad(x, (half, half), mode="reflect")
        sm = np.convolve(xpad, kernel, mode="valid")
        # sm is length n
        return sm

    @staticmethod
    def _smooth_reflect(x: np.ndarray, window: int) -> np.ndarray:
        """Reflect-padded moving average, output same length as input."""
        x = np.asarray(x, dtype=np.float64)
        n = int(x.size)
        if n == 0:
            return x.copy()
        window = max(1, int(window))
        if window <= 1 or n < 3:
            return x.copy()
        if window % 2 == 0:
            window += 1
        window = min(window, n if (n % 2 == 1) else max(1, n - 1))
        if window <= 1:
            return x.copy()
        half = window // 2
        kernel = np.ones(window, dtype=np.float64) / float(window)
        xpad = np.pad(x, (half, half), mode="reflect")
        return np.convolve(xpad, kernel, mode="valid")

    def _robust_phase_slope_rad_per_MHz(self, signal: np.ndarray) -> np.ndarray:
        """
        Compute a robust estimate of dphi/df (rad/MHz) from a complex signal.

        Uses the identity:
            dphi/df = Im( s'(f) * conj(s(f)) ) / |s(f)|^2
        which avoids phase unwrap glitches that can create large derivative spikes.
        Then applies smoothing and robust outlier rejection + interpolation.
        """
        s = np.asarray(signal, dtype=np.complex128)
        fMHz = np.asarray(self.freq_list_MHz, dtype=np.float64)
        if s.size == 0:
            return np.asarray([], dtype=np.float64)

        ds_df = np.gradient(s, fMHz)  # complex / MHz
        denom = (np.abs(s) ** 2).astype(np.float64)
        # Prevent blow-ups when |s| is extremely small
        eps = float(np.median(denom) * 1e-12 + 1e-24)
        denom = np.maximum(denom, eps)

        slope = (np.imag(ds_df * np.conj(s)) / denom).astype(np.float64)
        # Light smoothing to reduce point-to-point noise
        slope = self._smooth_reflect(slope, max(3, int(self.phase_smooth_window)))

        # Spike rejection based on residual vs a heavily smoothed trend.
        trend_win = max(11, int(7 * max(3, int(self.phase_smooth_window))))
        trend = self._smooth_reflect(slope, trend_win)
        resid = slope - trend

        rmed = float(np.median(resid))
        rmad = float(np.median(np.abs(resid - rmed)))
        if rmad <= 0:
            return slope

        # Flag spikes relative to the local trend (robust to broad resonance feature).
        bad = np.abs(resid - rmed) > (10.0 * 1.4826 * rmad)
        if not np.any(bad):
            return slope

        good_idx = np.where(~bad)[0]
        if good_idx.size < 2:
            return slope

        slope_clean = slope.copy()
        bad_idx = np.where(bad)[0]
        slope_clean[bad_idx] = np.interp(bad_idx.astype(np.float64), good_idx.astype(np.float64), slope[good_idx])
        return slope_clean

    def iterative_phase_correct(self, signal_uncorrected: np.ndarray, n_iters=None):
        """
        Iteratively remove linear phase slope and return corrected signal.

        Returns:
        - corrected_signal: complex array (same length as input)
        - phases: list of per-iteration smoothed phases (unwrapped, rad)
        - slopes: list of per-iteration estimated slopes (rad/MHz)
        """
        if n_iters is None:
            n_iters = int(self.phase_correction_iters)
        n_iters = max(0, int(n_iters))

        mag = np.abs(signal_uncorrected).astype(np.float64)
        phase0 = np.unwrap(np.angle(signal_uncorrected)).astype(np.float64)

        phases = []
        slopes = []

        phase_current = phase0.copy()
        for _ in range(n_iters):
            slope = self._estimate_phase_slope_rad_per_MHz(phase_current)
            slopes.append(slope)

            phase_corrected = phase_current - slope * self.freq_list_MHz
            phase_smoothed = self._smooth_and_pad_phase(phase_corrected)
            # Center the phase so its mean is zero (phase offset removed)
            phase_smoothed = phase_smoothed - np.mean(phase_smoothed)
            phases.append(phase_smoothed)

            phase_current = phase_smoothed

        corrected = mag * np.exp(1j * (phases[-1] if phases else phase0))
        return corrected, phases, slopes

    def run_experiment(self):

        rr = self.rr_str
        rep_rate_clk = self.rep_rate_clk
        ro_len = self.ro_len
        out = self.out

        wait_clk = rep_rate_clk - ro_len
        if wait_clk < 0:
            logger.warning(
                f"rep_rate_clk ({rep_rate_clk}) < ro_len ({ro_len}); "
                f"clamping wait to 0 (increase rep_rate_clk or decrease ro_len)."
            )
            wait_clk = 0
        
        with program() as rr_spec:
            n = declare(int)
            I = declare(fixed)
            I_st = declare_stream()
            Q = declare(fixed)
            Q_st = declare_stream()
            f = declare(int)
            freqs = np.arange(self._f_start_Hz, self._f_stop_Hz, self._f_step_Hz)
            with for_(n, 0, n < self.n_avg, n + 1):
                with for_(*from_array(f, freqs)):
                    update_frequency(rr, f)
                    wait(wait_clk, rr)
                    measure(
                            "readout",
                             rr,
                            None,
                            demod.full("integW_cos", I, out),
                            demod.full("integW_minus_sin", Q, out)
                            )
                    save(I, I_st)
                    save(Q, Q_st)

            with stream_processing():
                I_st.buffer(self._n_sweep_points).average().save("I")
                Q_st.buffer(self._n_sweep_points).average().save("Q")

        qmm = QuantumMachinesManager(self.qm_ip, cluster_name=self.cluster_name)

        if self.simulate:
            simulation_config = SimulationConfig(
                duration=200000,
                simulation_interface=LoopbackInterface(
                    [("con2", 7, "con2", 1), ("con2", 8, "con2", 2)]
                ),
            )
            job = qmm.simulate(self.config, rr_spec, simulation_config)
            job.get_simulated_samples().con2.plot()
            plt.show()
            sys.exit(0)
        else:
            qm = qmm.open_qm(self.config)
            job = qm.execute(rr_spec)
            job.result_handles.wait_for_all_values()
            I = job.result_handles.get("I").fetch_all()
            Q = job.result_handles.get("Q").fetch_all()

            self.I = I
            self.Q = Q
            return I, Q
    

    def analyze_and_plot(self):
        I_data = self.I
        Q_data = self.Q
        #log the shape of the data
        logger.info(f"Shape of I data: {I_data.shape}")
        logger.info(f"Shape of Q data: {Q_data.shape}")
        logger.info(f"I/Q type: {type(I_data)}")
        signal_uncorrected = I_data + 1j * Q_data

        phase_uncorrected = np.unwrap(np.angle(signal_uncorrected))
        

        corrected_signal, phases, slopes = self.iterative_phase_correct(
            signal_uncorrected, n_iters=self.phase_correction_iters
        )

        # Optional per-iteration corrected signals for plotting (first two iters)
        signal_magnitude = np.abs(signal_uncorrected)


        final_corrected_signal = signal_magnitude * np.exp(1j * phases[-1])
        self.final_corrected_signal = final_corrected_signal

        # Phase-based resonance pick: use a robust dphi/df estimate (rad/MHz)
        # from the complex signal to avoid unwrap/edge spikes.
        final_phase_slope = self._robust_phase_slope_rad_per_MHz(final_corrected_signal)

        npts = int(len(self.freq_list_MHz))
        # Ignore at least 5% and at least one smoothing window worth of points.
        self.phase_selection_ignore_npts = max(
            int(max(0.0, min(0.45, self.phase_selection_ignore_frac)) * npts),
            int(self.phase_padding_npts),
            int(self.phase_smooth_window),
        )
        start = int(self.phase_selection_ignore_npts)
        stop = int(npts - self.phase_selection_ignore_npts)
        if stop <= start + 1:
            # Fallback: if the sweep is too short, don't slice.
            start, stop = 0, npts

        # For picking, use a heavier smoothing so narrow spikes can't win.
        pick_win = int(self.phase_pick_smooth_window)
        if pick_win <= 0:
            pick_win = max(21, int(0.02 * npts))  # ~2% of sweep points
        pick_win = max(pick_win, int(self.phase_smooth_window))
        slope_for_pick = self._smooth_reflect(final_phase_slope, pick_win)

        resonant_frequency_from_slope = int(np.argmin(slope_for_pick[start:stop]) + start)



        ## finding the dip in magnitude
        ### calc the slope of the mags, find out when it drops and then that becomes the drop start
        instantaneous_mag_slope = np.gradient(np.abs(corrected_signal), self.freq_list_MHz)
        mag_analysis_window_npts = max(1, int(3e-2 * len(self.freq_list_MHz)))
        rolling_average_mag_slope = np.convolve(
            instantaneous_mag_slope,
            np.ones(mag_analysis_window_npts) / mag_analysis_window_npts,
            mode="valid",
        )
        # mag_slope_drop_start_index = np.argmin(rolling_average_mag_slope)

        resonant_frequency_from_mag = np.argmin(np.abs(corrected_signal))
        self.detected_resonance_frequency = self.freq_list_MHz[resonant_frequency_from_slope]

        f_res_phase_MHz = float(self.freq_list_MHz[resonant_frequency_from_slope])
        f_res_mag_MHz = float(self.freq_list_MHz[resonant_frequency_from_mag])
        rr_lo_MHz = float(self.rr_lo)
        rr_if_MHz = f_res_phase_MHz - rr_lo_MHz



        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"Resonator {self.rr_no} Spectroscopy OPX")
        # Slightly finer grids on all plots
        for ax in axes.ravel():
            ax.minorticks_on()
            ax.grid(True, which="major", linestyle=":", linewidth=0.7, alpha=0.8)
            ax.grid(True, which="minor", linestyle=":", linewidth=0.4, alpha=0.5)

        axes[0,0].plot(self.freq_list_MHz, phase_uncorrected)
        axes[0,0].set_xlabel("Frequency (MHz)")
        axes[0,0].set_ylabel("Phase (rad)")
        axes[0,0].set_title("Phase")
        for idx, phase in enumerate(phases):
            axes[0,1].plot(self.freq_list_MHz, np.unwrap(np.angle(signal_magnitude * np.exp(1j * phase))), label=f"Iteration {idx}")

        axes[0,1].axvline(
            x=f_res_phase_MHz,
            linestyle="--",
            color="gray",
            label=f"Resonance (phase): {f_res_phase_MHz:.3f} MHz",
        )
        axes[0,1].axvline(
            x=f_res_mag_MHz,
            linestyle="--",
            color="red",
            label=f"Resonance (mag): {f_res_mag_MHz:.3f} MHz",
        )
        axes[0,1].legend(fontsize=8)
        axes[0,1].set_xlabel("Frequency (MHz)")
        axes[0,1].set_ylabel("Phase (rad)")
        axes[0,1].set_title("Phase Corrected")

        axes[1,0].plot(self.freq_list_MHz, np.abs(corrected_signal))
        axes[1,0].axvline(
            x=f_res_phase_MHz,
            linestyle="--",
            color="gray",
            label=f"Resonance (phase): {f_res_phase_MHz:.3f} MHz",
        )
        axes[1,0].axvline(
            x=f_res_mag_MHz,
            linestyle="--",
            color="red",
            label=f"Resonance (mag): {f_res_mag_MHz:.3f} MHz",
        )
        axes[1,0].legend(fontsize=8)

        axes[1,0].set_xlabel("Frequency (MHz)")
        axes[1,0].set_ylabel("Magnitude (a.u.)")
        axes[1,0].set_title("Magnitude Corrected")

        axes[1,1].plot(self.freq_list_MHz[:len(rolling_average_mag_slope)], rolling_average_mag_slope)
        axes[1,1].plot(self.freq_list_MHz, final_phase_slope, alpha=0.7, label="phase slope (clean)")
        axes[1,1].plot(self.freq_list_MHz, slope_for_pick, linewidth=2.0, label="phase slope (trend)")
        # axes[1,1].plot(self.freq_list_MHz,instantaneous_mag_slope)
        axes[1,1].set_xlabel("Frequency (MHz)")
        axes[1,1].set_ylabel("Slope (a.u. / MHz, rad / MHz)")
        axes[1,1].set_title("Mag slope and phase slope (dφ/df)")
        axes[1,1].legend(fontsize=8, loc="best")

        # Bottom-right information box
        info_lines = [
            f"rr_if: {rr_if_MHz:.6f} MHz",
            f"prev_rr_frequency: {float(self.prev_rr_frequency):.6f} MHz",
            f"rr_lo: {rr_lo_MHz:.6f} MHz",
            f"n_avgs: {int(self.n_avg)}",
        ]
        if getattr(self, "verbose", False):
            info_lines += [
                f"readout_amp: {float(self.rr_amp):.6g}",
                f"readout_integ_clk: {int(self.integ_len)}",
                f"readout_ro_len_clk: {int(self.ro_len)}",
            ]
        axes[1,1].text(
            0.98,
            0.02,
            "\n".join(info_lines),
            transform=axes[1,1].transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.85, edgecolor="gray", linewidth=0.8),
        )

        plt.tight_layout()
        plt.savefig(f"{self.path_to_save}_rr_{self.rr_no}.png")
        cprint(f"file saved as: {self.path_to_save}_rr_{self.rr_no}.png", "green")
        plt.show(block=False)
        if self.calc_e_delay:
            elec_delay_ns_est = return_elec_delay(phase_uncorrected, self.freq_list_MHz)
            self.elec_delay_ns = elec_delay_ns_est
        else:
            elec_delay_ns_est = self.elec_delay_ns

        if self.calc_phase_offset:
            pass

        self.fr_calibrated = self.detected_resonance_frequency
        self.rr_if_calibrated = self.detected_resonance_frequency - self.rr_lo
        
        return self.detected_resonance_frequency

    def update_config_dicts(self):
        # update fr and the IF
        # dicts to update: fr val, fr if
        logger.info(f"Updating config dicts for rr{self.rr_no}")
        logger.info(f"Detected resonance frequency: {self.detected_resonance_frequency} MHz")
        logger.info(f"RR LO: {self.rr_lo} MHz")
        logger.info(f"RR IF: {self.rr_if_calibrated} MHz")

        logger.info(f"RR IF calibrated: {self.rr_if_calibrated} MHz")
        timestamp = self.get_timestamp_str()
        logger.info(f"Timestamp: {timestamp}")

        rr_key = str(self.rr_no)

        # IMPORTANT: JSON keys are strings. If we write using an int key (e.g. 1),
        # Python can hold both "1" and 1 as distinct keys, and json.dump() will
        # serialize both as "1" → producing duplicate keys in the output file.
        buffer_fr_vals = dict(self.fr_dict)
        buffer_fr_vals["fr_vals"] = dict(buffer_fr_vals.get("fr_vals", {}))
        buffer_fr_vals["fr_vals"][rr_key] = float(self.fr_calibrated)
        buffer_fr_vals["timestamp"] = timestamp
        with open(self.system_params_path + '/fr_vals.json', 'w') as f:
            json.dump(buffer_fr_vals, f, indent=6)
        
        buffer_rr_if_vals = dict(self.rr_if_dict)
        


        buffer_rr_lo_vals = dict(self.rr_lo_dict)
        for key in buffer_rr_if_vals.keys():
            buffer_rr_if_vals[key] = np.round(buffer_rr_if_vals[key] * 1e-6, 6)

            buffer_rr_lo_vals[key] = np.round(buffer_rr_lo_vals[key] * 1e-9, 6)


        buffer_rr_if_vals[rr_key] = np.round(self.rr_if_calibrated, 6)
        buffer_rr_lo_vals[rr_key] = np.round(self.rr_lo * 1e-3, 6)  # save in GHz


        # exit(0)

        with open(self.system_params_path + '/rr_LO.json', 'w') as f:
            json.dump(buffer_rr_lo_vals, f, indent=6)
        with open(self.system_params_path + '/rr_IF.json', 'w') as f:
            json.dump(buffer_rr_if_vals, f, indent=6)

    def detect_resonance(self, signal_corrected):
        """Return resonator frequency (MHz) from a simple magnitude minimum."""
        mag = np.abs(signal_corrected).astype(np.float64)
        idx = int(np.argmin(mag))
        f_resonant = float(self.freq_list_MHz[idx])
        logger.info(f"Detected resonance at index {idx}, f_res = {f_resonant} MHz (global |S| minimum)")
        return f_resonant

    def calculate_internal_external_bandwidth(self):
        pass

    def save_experiment_data(self):
        result_dict = {
            "rr_no": self.rr_no,
            "q_no": self.q_no,
            "fr_calibrated": self.fr_calibrated,
            "rr_if_calibrated": self.rr_if_calibrated,
            "rr_lo": self.rr_lo,
            "n_avg": self.n_avg,
            "rr_amp": self.rr_amp,
            "integ_len": self.integ_len,
            "ro_len": self.ro_len,

            "freq_list_MHz": self.freq_list_MHz,
            "rr_IF_sweep_MHz": self.rr_IF_sweep_MHz,
            "raw_signal": {
                "I": self.I,
                "Q": self.Q,
            },
            "final_corrected_signal": {
                "I": self.final_corrected_signal.real,
                "Q": self.final_corrected_signal.imag,
            }
        }
        save_json(result_dict, f'{self.path_to_save}_rr_{self.rr_no}.json')
    def run(self):
        start_time = time.time()    
        self.run_experiment()
        self.analyze_and_plot()
        if self.update_config:
            self.update_config_dicts()
        if self.save_data:
            self.save_experiment_data()
        else:
            logger.info("Data not saved")
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")



if __name__ == "__main__":
    rr_no = 4
    rr_nos = [rr_no]
    # rr_nos = range(1, 7)
    # for rr_no in range(1, 7):
    for rr_no in rr_nos:
        q_no = rr_no
        save_data = False
        update_config = False
        n_avg = 500
        rr_amp = 0.04

        res_spec = ResonatorSpectroscopy(rr_no=rr_no, q_no=q_no, n_avg=n_avg, save_data=save_data, update_config=update_config)
        res_spec.run()



        
        