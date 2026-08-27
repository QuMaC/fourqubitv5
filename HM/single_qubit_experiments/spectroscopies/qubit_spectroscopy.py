
import time
import json
import logging
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from termcolor import cprint

from qm.qua import (
    program, declare, declare_stream, for_,
    update_frequency, play, amp, align, save, stream_processing, fixed,
)
from qm import QuantumMachinesManager
from qualang_tools.results import fetching_tool
from qualang_tools.plot import interrupt_on_close

from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json
from Helper_Functions.macros import cooldown, measure_macro
from Helper_Functions.spectro_helper import (
    normalize, S2N_1, does_signal_exist1, check_I_or_Q,
    closest_pair, find_nearest,
)
from Configuration_Files.config_dictionaries import u

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class QubitSpectroscopy(SingleQubitExperiment):
    """
    QUA-based qubit spectroscopy with adaptive power sweep and iterative zoom-in.

    Workflow
    --------
    1. Wide frequency sweep at two drive powers (SNR-based early stopping per sweep).
    2. Peak detection across both powers; identify f01 vs f02/2 via anharmonicity pairing.
    3. Iterative zoom-in, halving the window each pass, until < 0.8 MHz wide.
    4. Optionally update JSON config files with the calibrated IF, LO, and anharmonicity.

    Key kwargs
    ----------
    n_avgs        : int    QUA averages per sweep                   (default: 1000)
    n_samples     : int    Frequency points in the wide sweep       (default: 2000)
    f_min_MHz     : float  Wide sweep lower IF bound in MHz         (default: -400)
    f_max_MHz     : float  Wide sweep upper IF bound in MHz         (default:  400)
    anharm_MHz    : float  Expected anharmonicity in MHz            (default:  280)
    update_config : bool   Write results to JSON config files       (default: False)
    save_data     : bool   Save raw data to JSON                    (default: False)
    query_LOs     : bool   Query hardware LOs on init               (default: False)
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="qubit_spec",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )

        self.n_avgs        = int(kwargs.get("n_avgs", 1000))
        self.n_samples     = int(kwargs.get("n_samples", 2000))
        self.f_min_MHz     = float(kwargs.get("f_min_MHz", -400))
        self.f_max_MHz     = float(kwargs.get("f_max_MHz",  400))
        self.anharm_MHz    = float(kwargs.get("anharm_MHz", 280))
        self.update_config = bool(kwargs.get("update_config", False))
        self.save_data = bool(kwargs.get("save_data", False))
        self.use_rotated = bool(kwargs.get("use_rotated", False))
        # Drive amplitude range, scaled by resonator external bandwidth.
        # This keeps the qubit drive power consistent regardless of how leaky the resonator is.
        ext_bw_path = self.system_params_path + "/external_bandwidth.json"
        with open(ext_bw_path, "r") as fh:
            ext_bw = json.load(fh)
        ext_bw_val = float(ext_bw[str(q_no)])

        if q_no < 5:
            power_scale = abs(np.round(4.9296223 / ext_bw_val, 5) * 1.2)
        else:
            power_scale = abs(np.round(2.9296223 / ext_bw_val, 5)) * 2

        a_min = np.round(0.05 * 1.5, 4)   # 0.075 — raw, used as zoom amplitude
        a_max = np.round(0.40 * 1.5, 4)   # 0.6
        self.amp_range = [
            np.round(a_min * power_scale, 4),
            # Cap a_max at 0.8 *before* scaling, then clip the product at 0.95
            # (matches original: min(min([a_max, 0.8]) * power_scale, 0.95))
            min(np.round(min(a_max, 0.8) * power_scale, 4), 0.95),
        ]
        # Zoom phase always uses the raw (unscaled) a_min — exactly as in the
        # reference script where amp1 = a_min (not a_min * power_scale).
        self._a_min_zoom = float(a_min)   # 0.075 for all qubits

        # Results
        self.q_if_calibrated_MHz: float      = None
        self.anharmonicity_MHz:   float      = None
        self.twoby2_lines:        np.ndarray = None
        self.best_quadrature:     int        = None   # 0=I, 1=Q
        self.data_wide:           list       = []     # [[I, Q], …] one entry per amp
        self.freqs_wide:          np.ndarray = None
        self.data_fin:            np.ndarray = None   # columns: [freq_Hz, I, Q]

        self._qmm = None

    # ------------------------------------------------------------------
    # QUA program
    # ------------------------------------------------------------------

    def _build_program(
        self,
        f_min_hz: int,
        f_max_hz: int,
        df_hz:    int,
        q_amp:    float,
        n_freqs:  int,
    ):
        """
        Compile a QUA spectroscopy program.

        n_freqs must equal len(np.arange(f_min_hz, f_max_hz, df_hz)) so that
        stream_processing buffer size matches the inner loop iteration count.
        """
        qe  = self.q_str
        rr  = self.rr_str
        out = self.out

        with program() as prog:
            n    = declare(int)
            I    = declare(fixed)
            I_st = declare_stream()
            Q    = declare(fixed)
            Q_st = declare_stream()
            f    = declare(int)
            n_st = declare_stream()

            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(f, f_min_hz, f < f_max_hz, f + df_hz):
                    cooldown(time=20000)
                    update_frequency(qe, f)
                    play("const" * amp(q_amp), qe, duration=20000)
                    align(rr, qe)
                    measure_macro(qe, rr, out, I, Q, pi_12=False)
                    save(I, I_st)
                    save(Q, Q_st)
                save(n, n_st)

            with stream_processing():
                I_st.buffer(n_freqs).average().save("I")
                Q_st.buffer(n_freqs).average().save("Q")
                n_st.save("iteration")

        return prog

    # ------------------------------------------------------------------
    # Live plotting with SNR-based early stopping
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Axis helpers
    # ------------------------------------------------------------------

    def _abs_freq_transforms(self):
        """
        Return a (forward, inverse) function pair for secondary_xaxis that
        converts IF in MHz ↔ absolute frequency in GHz using self.q_lo.
        """
        q_lo_MHz = self.q_lo_val_MHz   # already in MHz (set by SingleQubitExperiment)

        def if_to_ghz(x):
            return (np.asarray(x) + self.q_lo_val_MHz) * 1e-3

        def ghz_to_if(x):
            return np.asarray(x) * 1e3 - q_lo_MHz

        return if_to_ghz, ghz_to_if

    def _add_abs_freq_axis(self, ax):
        """Attach a top secondary x-axis showing absolute frequency in GHz."""
        fwd, inv = self._abs_freq_transforms()
        secax = ax.secondary_xaxis("top", functions=(fwd, inv))
        secax.set_xlabel("Abs. Freq (GHz)")
        return secax

    def _processed_quadratures(self, I: np.ndarray, Q: np.ndarray):
        """
        Return analysis quadratures according to self.use_rotated.
        When enabled, apply one global IQ rotation angle per trace.
        """
        I = np.asarray(I)
        Q = np.asarray(Q)
        if not self.use_rotated:
            return I, Q

        signal = I + 1j * Q
        n_pts = len(signal)
        if n_pts < 8:
            return I, Q

        # First-pass centering using robust medians to detect the dominant feature.
        median_complex = np.median(signal.real) + 1j * np.median(signal.imag)
        centered0 = signal - median_complex
        peak_idx = int(np.argmax(np.abs(centered0)))

        # Build a background mask that excludes the feature region.
        guard = max(5, n_pts // 20)
        lo_guard = max(0, peak_idx - guard)
        hi_guard = min(n_pts, peak_idx + guard + 1)
        bg_mask = np.ones(n_pts, dtype=bool)
        bg_mask[lo_guard:hi_guard] = False

        # Fallback when too many points are excluded (small traces).
        min_bg_pts = max(6, n_pts // 4)
        if np.count_nonzero(bg_mask) >= min_bg_pts:
            bg_mean = np.mean(signal[bg_mask])
        else:
            bg_mean = np.mean(signal)

        centered = signal - bg_mean

        # Estimate a single complex response vector around the strongest feature.
        half_win = max(3, n_pts // 50)
        lo = max(0, peak_idx - half_win)
        hi = min(n_pts, peak_idx + half_win + 1)
        delta = np.mean(centered[lo:hi])

        if np.abs(delta) < 1e-15:
            theta = 0.0
        else:
            theta = -np.angle(delta)

        rotated_signal = centered * np.exp(1j * theta)
        return np.real(rotated_signal), np.imag(rotated_signal)

    def _run_with_live_plot(
        self,
        job,
        freqs:         np.ndarray,
        amp_val:       float,
        snr_threshold: float = 1.0,
    ):
        """
        Stream data from a running QUA job and plot I/Q live.
        Halts the job early when either quadrature's SNR exceeds snr_threshold.

        Returns
        -------
        I, Q : np.ndarray  (final fetch after halt or completion)
        """
        res_handles = job.result_handles
        print("extracting res_handles")
        nrows = 4 if self.use_rotated else 2
        fig, axs = plt.subplots(nrows, 1, sharex=True)
        print("about to fetch results")
        results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")
        print("fetched results")
        interrupt_on_close(fig, job)

        I, Q = None, None
        while res_handles.is_processing():
            I, Q, iteration = results.fetch_all()
            I_proc, Q_proc = self._processed_quadratures(I, Q)

            if self.use_rotated:
                traces = [I, Q, I_proc, Q_proc]
                labels = ["I_raw", "Q_raw", "I_rotated", "Q_rotated"]
            else:
                traces = [I, Q]
                labels = ["I", "Q"]

            for i, (ax, data, label) in enumerate(zip(axs, traces, labels)):
                ax.cla()
                ax.plot(freqs * 1e-6, data, marker=".", label=label)
                ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                ax.set(xlabel="IF (MHz)", ylabel="Quadrature Amplitude")
                ax.legend()
                ax.grid()
                if i == 0:
                    self._add_abs_freq_axis(ax)

            fig.suptitle(f"Qubit spectroscopy — q{self.q_no}  amp={amp_val:.4f}")
            plt.tight_layout()
            plt.pause(1)

            snr_i, _ = S2N_1(normalize(I_proc))
            snr_q, _ = S2N_1(normalize(Q_proc))
            logger.debug(f"SNR_I={snr_i:.2f}  SNR_Q={snr_q:.2f}")

            if snr_i > snr_threshold or snr_q > snr_threshold:
                job.halt()

        I = res_handles.get("I").fetch_all()
        Q = res_handles.get("Q").fetch_all()
        return I, Q

    # ------------------------------------------------------------------
    # Wide sweep (Phase 1)
    # ------------------------------------------------------------------

    def _wide_sweep(self) -> tuple:
        """
        Execute a spectroscopy sweep at each amplitude in self.amp_range.

        Returns
        -------
        data       : list of [I, Q] arrays, one entry per amplitude
        freqs_wide : shared frequency axis in Hz
        """
        span     = self.f_max_MHz - self.f_min_MHz
        df_hz    = int(span * u.MHz // self.n_samples)
        f_min_hz = int(self.f_min_MHz * u.MHz)
        f_max_hz = int(self.f_max_MHz * u.MHz)
        freqs    = np.arange(f_min_hz, f_max_hz, df_hz)
        n_freqs  = len(freqs)

        data = []
        for amp_val in self.amp_range:
            amp_val    = float(np.round(amp_val, 4))
            snr_thresh = 0.6 if amp_val < 0.2 else 1.0

            prog = self._build_program(f_min_hz, f_max_hz, df_hz, amp_val, n_freqs)
            qm   = self._qmm.open_qm(self.config)
            job  = qm.execute(prog)
            I, Q = self._run_with_live_plot(job, freqs, amp_val, snr_threshold=snr_thresh)
            qm.close()

            I_proc, Q_proc = self._processed_quadratures(I, Q)
            data.append([I_proc, Q_proc])
            self.data_wide.append([I_proc, Q_proc])

        return data, freqs

    # ------------------------------------------------------------------
    # Peak detection helpers
    # ------------------------------------------------------------------

    def _find_peaks_wide(
        self,
        sig:        np.ndarray,
        freqs:      np.ndarray,
        height:     float = 0.4,
        prominence: float = 0.2,
    ) -> np.ndarray:
        """
        Filter sig with a moving average, roll to compensate filter delay, find peaks.
        Returns peak frequencies in MHz.
        """
        _, fltd, w = does_signal_exist1(sig, alpha=0.5)
        normed = np.roll(normalize(fltd[w:-w + 1]), -w // 2)
        peaks, _ = find_peaks(normed, height=height, prominence=prominence)
        if len(peaks) == 0:
            return np.array([])
        # Compensate for moving-average group delay before mapping to the raw frequency axis.
        peak_idx = np.clip(peaks + (w // 2), 0, len(freqs) - 1)
        return freqs[peak_idx] * 1e-6

    def _select_quadrature(self, data: list) -> int:
        """Return 0 (I) or 1 (Q) for whichever quadrature shows the clearest signal."""
        indices = [
            check_I_or_Q(d, alpha1=0.5)
            for d in data
            if check_I_or_Q(d, alpha1=0.5) is not None
        ]
        return indices[0] if indices else 0

    # ------------------------------------------------------------------
    # Anharmonicity-based qubit identification
    # ------------------------------------------------------------------

    def _identify_qubit_peaks(
        self,
        peak_list: list,
    ) -> tuple:
        """
        Cross-validate peak lists from multiple power sweeps and pair f01/f02*2 peaks
        using the expected anharmonicity spacing.

        For each power level we try to find pairs (a, b) where b - a ≈ anharm/2.
        `b` is the f01 candidate and `a` is the f02/2 sideband.
        A peak is considered confirmed when it appears at the same frequency (within
        5 MHz) in at least 2 other power levels.

        Returns
        -------
        qubits       : ndarray of confirmed f01 frequencies in MHz
        twoby2_lines : ndarray of f02/2 frequencies in MHz, or False if not found
        """
        half_anharm = self.anharm_MHz / 2
        ceiling     = half_anharm + 10.0      # = 150 MHz for default anharm=280 MHz
                                              # matches original: if b - a < 150

        p_arr, p_arr_02 = [], []
        for freq_list in peak_list:
            tmp      = freq_list.copy()
            set_01   = []
            set_02   = []

            if len(tmp) == 0:
                pass
            elif len(tmp) <= 2:
                set_01.append(float(np.max(tmp)))
                if len(tmp) == 2:
                    set_02.append(float(np.min(tmp)))
            else:
                while len(tmp) > 2:
                    a, b = closest_pair(tmp, half_anharm)
                    if b - a < ceiling:
                        set_01.append(b)
                        set_02.append(a)
                    idx_b = np.where(tmp == b)[0][0]
                    tmp   = np.delete(tmp, idx_b)
                    idx_a = np.where(tmp == a)[0][0]
                    tmp   = np.delete(tmp, idx_a)

            p_arr.append(set_01)
            p_arr_02.append(set_02)

        if not p_arr or not p_arr[0]:
            return np.array([]), False

        required_confirmations = max(1, min(2, len(p_arr) - 1))
        det_index = []
        for q_idx, val in enumerate(p_arr[0]):
            det_count = 0
            for i, other in enumerate(p_arr[1:], start=1):
                if not other:
                    continue
                nearest, _ = find_nearest(np.array(other), val)
                if abs(nearest - val) < 5:
                    det_count += 1
                    det_index.append([q_idx, i])
            # Confirm only if this candidate is seen in enough additional sweeps.
            if det_count < required_confirmations:
                det_index = [x for x in det_index if x[0] != q_idx]

        if not det_index:
            # Fallback: if cross-sweep confirmation fails (common when power-dependent
            # shifts distort one sweep), keep candidates from the reference sweep so
            # the run can continue and zoom-in can disambiguate.
            return np.array(p_arr[0], dtype=float), False

        det_arr  = np.transpose(np.array(det_index))
        indices  = set(det_arr[0].tolist())
        qubits   = np.array(p_arr[0])[list(indices)]

        ref_i       = det_index[0][1]
        emp_flg     = [1 if p else 0 for p in p_arr_02]
        twoby2_lines = False
        if (
            np.sum(emp_flg) > 0
            and ref_i < len(p_arr_02)
            and p_arr_02[ref_i]
            and all(i < len(p_arr_02[ref_i]) for i in indices)
        ):
            twoby2_lines = np.array(p_arr_02[ref_i])[list(indices)]

        return qubits, twoby2_lines

    # ------------------------------------------------------------------
    # Zoom-in sweep (Phase 2)
    # ------------------------------------------------------------------

    def _zoom_sweep(self, f_center_MHz: float, best_quad: int) -> float:
        """
        Iteratively narrow the sweep window around f_center_MHz.
        Each pass shrinks the window by 3× and reduces the drive amplitude by 5×.
        Stops when the window is narrower than 0.8 MHz.

        Returns
        -------
        f_center_hz : float  Final qubit IF in Hz
        """
        f_min   = f_center_MHz - 20.0
        f_max   = f_center_MHz + 20.0
        amp_val = self._a_min_zoom    # raw a_min = 0.075, unscaled (matches original)

        # Initialise so we always have a value even if we break on the first check
        f_center_hz = f_center_MHz * u.MHz

        while True:
            logger.info(f"Zoom window: [{f_min:.4f}, {f_max:.4f}] MHz  amp={amp_val:.5f}")
            if f_max - f_min < 0.8:
                break

            span     = f_max - f_min
            df_hz    = int(span * 5 * u.MHz // self.n_samples)
            f_min_hz = int(f_min * u.MHz)
            f_max_hz = int(f_max * u.MHz)
            freqs    = np.arange(f_min_hz, f_max_hz, df_hz)
            n_freqs  = len(freqs)

            prog = self._build_program(f_min_hz, f_max_hz, df_hz, amp_val, n_freqs)
            time.sleep(0.5)
            qm  = self._qmm.open_qm(self.config)
            job = qm.execute(prog)
            I, Q = self._run_with_live_plot(job, freqs, amp_val, snr_threshold=2.0)
            qm.close()

            I_proc, Q_proc = self._processed_quadratures(I, Q)
            sig = I_proc if best_quad == 0 else Q_proc
            _, fltd, w = does_signal_exist1(sig, alpha=0.5, win_s=30)
            normed = normalize(fltd[w:-w + 1])
            peaks, props = find_peaks(normed, height=0.5, prominence=0.5)

            if len(peaks) == 0:
                logger.warning("No peak in zoom sweep — doubling amplitude and retrying")
                amp_val *= 2
                continue

            best_idx    = int(peaks[np.argmax(props["peak_heights"])])
            raw_idx     = int(np.clip(best_idx + (w // 2), 0, len(freqs) - 1))
            f_center_hz = float(freqs[raw_idx])
            f_center_MHz = f_center_hz * 1e-6

            logger.info(
                f"Zoom: peak at {f_center_MHz:.4f} MHz  "
                f"window=[{f_min:.3f}, {f_max:.3f}] MHz"
            )

            # Store this iteration's data; the last stored values are the final result
            self.data_fin  = np.column_stack([freqs, I, Q])
            self.freqs_fin = freqs

            f_range  = span / 3
            f_min    = f_center_MHz - f_range / 2
            f_max    = f_center_MHz + f_range / 2
            amp_val /= 5

        return f_center_hz

    # ------------------------------------------------------------------
    # Core experiment sequence
    # ------------------------------------------------------------------

    def run_experiment(self):
        """
        Full two-phase qubit spectroscopy.

        Phase 1 — wide sweep
            Run at each amplitude in self.amp_range over [f_min_MHz, f_max_MHz].
            Use SNR-based early stopping so we don't over-average once the signal
            is visible.  Detect peaks and pair f01/f02*2 via anharmonicity.

        Phase 2 — zoom-in
            Iteratively narrow the window around the found f01, reducing drive
            power each pass, until the window is < 0.8 MHz.
        """
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)

        # --- Phase 1 ---
        logger.info(
            f"Wide sweep: q{self.q_no}  IF=[{self.f_min_MHz}, {self.f_max_MHz}] MHz  "
            f"amps={self.amp_range}"
        )
        data, freqs_wide   = self._wide_sweep()
        self.freqs_wide    = freqs_wide
        best_quad          = self._select_quadrature(data)
        self.best_quadrature = best_quad

        peak_list = [self._find_peaks_wide(d[best_quad], freqs_wide) for d in data]

        # Diagnostic: show raw peaks found per sweep (mirrors original's print output)
        for sweep_i, pl in enumerate(peak_list):
            logger.info(f"  Sweep {sweep_i} (amp={self.amp_range[sweep_i]:.4f}): "
                        f"peaks = {np.round(pl, 2)} MHz  (n={len(pl)})")

        qubits, twoby2_lines = self._identify_qubit_peaks(peak_list)

        if len(qubits) == 0:
            raise RuntimeError(
                "No qubit found in wide sweep — try widening the frequency range or "
                "adjusting the drive power.\n"
                f"  amp_range={self.amp_range}, peaks per sweep: {[len(p) for p in peak_list]}"
            )

        if len(qubits) > 1:
            # Prefer the candidate nearest the currently configured qubit IF.
            expected_if_MHz = float(self.q_if * 1e-6)
            best_idx = int(np.argmin(np.abs(qubits - expected_if_MHz)))
            logger.warning(
                f"Multiple candidates: {np.round(qubits, 3)} MHz — "
                f"using nearest to configured IF ({expected_if_MHz:.3f} MHz)"
            )
            f_center_MHz = float(qubits[best_idx])
        else:
            f_center_MHz = float(qubits[0])
        self.twoby2_lines = twoby2_lines

        logger.info(f"Qubits seen: {np.round(qubits, 3)} MHz")
        if twoby2_lines is not False and len(twoby2_lines) > 0:
            self.anharmonicity_MHz = float(2 * (f_center_MHz - twoby2_lines[0]))
            logger.info(
                f"f01 ≈ {f_center_MHz:.3f} MHz | "
                f"anharmonicity ≈ {self.anharmonicity_MHz:.1f} MHz"
            )
        else:
            logger.info(f"f01 ≈ {f_center_MHz:.3f} MHz | 02/2 line not detected")
            cprint(
                f"q{self.q_no}: f02/2 line not detected; anharmonicity not updated.",
                "red",
            )

        # --- Phase 2 ---
        logger.info("Starting zoom-in sweep…")
        q_if_hz = self._zoom_sweep(f_center_MHz, best_quad)
        self.q_if_calibrated_MHz = q_if_hz * 1e-6
        logger.info(f"Final qubit IF = {self.q_if_calibrated_MHz:.6f} MHz")

    # ------------------------------------------------------------------
    # Analysis and plotting
    # ------------------------------------------------------------------

    def analyze_and_plot(self):
        """
        Produce a 3-panel summary figure (I, Q, magnitude) from the final zoom-in
        data.  Saves the figure to the experiment's dated output directory.

        Returns I, Q arrays for the caller's use.
        """
        if self.data_fin is None:
            raise RuntimeError("No data — call run_experiment() first.")

        freqs = self.data_fin[:, 0]
        I     = self.data_fin[:, 1]
        Q     = self.data_fin[:, 2]
        signal = I + 1j * Q
        mag = np.abs(signal)
        I_proc, Q_proc = self._processed_quadratures(I, Q)

        if self.use_rotated:
            traces = [I, Q, mag, I_proc, Q_proc]
            labels = ["I_raw", "Q_raw", "|I+jQ|", "I_rotated", "Q_rotated"]
            nrows = 5
        else:
            traces = [I, Q, mag]
            labels = ["I", "Q", "|I+jQ|"]
            nrows = 3

        fig, axs = plt.subplots(nrows, 1, sharex=True, figsize=(10, 8))
        for i, (ax, dat, label) in enumerate(zip(axs, traces, labels)):
            ax.plot(freqs * 1e-6, dat, marker=".", label=label)
            ax.set_xlabel("IF (MHz)")
            ax.set_ylabel("Amplitude (a.u.)")
            ax.legend()
            ax.grid(True)
            if i == 0:
                self._add_abs_freq_axis(ax)

        title = f"Qubit spectroscopy — q{self.q_no}  IF = {self.q_if_calibrated_MHz:.4f} MHz"
        if self.anharmonicity_MHz is not None:
            title += f"\nAnharmonicity = {self.anharmonicity_MHz:.1f} MHz"
        fig.suptitle(title)
        plt.tight_layout()

        save_path = str(self.path_to_save) + f"_q{self.q_no}.png"
        plt.savefig(save_path, bbox_inches="tight")
        cprint(f"Figure saved: {Path(save_path).as_uri()}", "green")
        plt.show(block=False)

        return I, Q

    # ------------------------------------------------------------------
    # Config dict updates
    # ------------------------------------------------------------------

    def update_config_dicts(self):
        """
        Write calibrated qubit parameters to JSON config files.

        Always writes
        -------------
        q_IF.json — calibrated IF in MHz

        If update_config=True, also writes
        ------------------------------------
        q_LO.json            — LO frequency in GHz (queried from hardware)
        anharmonicities.json — anharmonicity in MHz
        fq_vals.json         — absolute qubit frequency = IF + LO (MHz)
        """
        if self.q_if_calibrated_MHz is None:
            raise RuntimeError("No calibration result — call run_experiment() first.")

        sp_path = self.system_params_path
        q_key   = str(self.q_no)

        # Always update q_IF
        q_if_path = sp_path + "/q_IF.json"
        with open(q_if_path, "r") as fh:
            q_if_dict = json.load(fh)
        q_if_dict[q_key] = self.q_if_calibrated_MHz
        with open(q_if_path, "w") as fh:
            json.dump(q_if_dict, fh, indent=6)
        logger.info(f"q_IF[{q_key}] = {self.q_if_calibrated_MHz:.6f} MHz")

        if not self.update_config:
            return

        timestamp = self.get_timestamp_str()

        # Query hardware LO
        import pyvisa as visa
        from Configuration_Files.configuration_4qubitsv3 import dac_mapping
        from Helper_Functions.helper_functionsv2 import keyer

        dac_key     = keyer(f"q{self.q_no}", dac_mapping)[0]
        rm          = visa.ResourceManager()
        q_lo_rns    = rm.open_resource(self.LO_IP_dict["q_LO"][dac_key])
        lo_freq_GHz = q_lo_rns.query_ascii_values("SOUR:FREQ:CW?")[0] / 1e9
        rm.close()

        q_lo_path = sp_path + "/q_LO.json"
        with open(q_lo_path, "r") as fh:
            lo_dict = json.load(fh)
        lo_dict[q_key] = round(lo_freq_GHz, 6)
        with open(q_lo_path, "w") as fh:
            json.dump(lo_dict, fh, indent=6)
        logger.info(f"q_LO[{q_key}] = {lo_freq_GHz:.6f} GHz")

        if self.anharmonicity_MHz is not None:
            anh_path = sp_path + "/anharmonicities.json"
            with open(anh_path, "r") as fh:
                dets = json.load(fh)
            dets[q_key] = round(self.anharmonicity_MHz, 3)
            with open(anh_path, "w") as fh:
                json.dump(dets, fh, indent=6)
            logger.info(f"anharmonicities[{q_key}] = {self.anharmonicity_MHz:.3f} MHz")

        # Absolute qubit frequency = IF (MHz) + LO (GHz → MHz)
        fq_abs_MHz = self.q_if_calibrated_MHz + lo_freq_GHz * 1e3
        fq_path    = sp_path + "/fq_vals.json"
        with open(fq_path, "r") as fh:
            fq_dict = json.load(fh)
        fq_dict.setdefault("fq_vals", {})[q_key] = round(fq_abs_MHz, 6)
        fq_dict["timestamp"] = timestamp
        with open(fq_path, "w") as fh:
            json.dump(fq_dict, fh, indent=6)
        logger.info(f"fq_vals[{q_key}] = {fq_abs_MHz:.3f} MHz | ts={timestamp}")

    # ------------------------------------------------------------------
    # Save raw data
    # ------------------------------------------------------------------

    def save_experiment_data(self):
        """Save wide-sweep and final zoom-in data to a JSON file."""
        if self.q_if_calibrated_MHz is None:
            raise RuntimeError("No data — call run_experiment() first.")

        result = {
            "q_no":                self.q_no,
            "rr_no":               self.rr_no,
            "q_if_calibrated_MHz": self.q_if_calibrated_MHz,
            "anharmonicity_MHz":   self.anharmonicity_MHz,
            "n_avgs":              self.n_avgs,
            "amp_range":           self.amp_range,
            "freqs_wide_Hz":       self.freqs_wide,
            "data_wide":           [{"I": d[0], "Q": d[1]} for d in self.data_wide],
        }
        if self.data_fin is not None:
            result["data_fin"] = {
                "freqs_Hz": self.data_fin[:, 0],
                "I":        self.data_fin[:, 1],
                "Q":        self.data_fin[:, 2],
            }

        json_path = str(self.path_to_save) + f"_q{self.q_no}.json"
        save_json(result, json_path)
        cprint(f"Data saved: {Path(json_path).as_uri()}", "green")

    # ------------------------------------------------------------------
    # Top-level orchestration
    # ------------------------------------------------------------------

    def run(self):
        """connect → run_experiment → analyze_and_plot → update_config_dicts → (save)."""
        t0 = time.time()
        try:
            # self.restore_saved_los()
            self.run_experiment()
            self.analyze_and_plot()
            if self.update_config:
                self.update_config_dicts()
            if self.save_data:
                self.save_experiment_data()
            else:
                cprint(f"Data not saved", "red")
        finally:
            if self._qmm is not None:
                try:
                    self._qmm.close()
                except Exception:
                    pass
        elapsed = time.time() - t0
        logger.info(f"Total time: {int(elapsed // 60)}m {elapsed % 60:.1f}s")
        return self.q_if_calibrated_MHz


# ---------------------------------------------------------------------------
# Module-level convenience wrapper
# ---------------------------------------------------------------------------

def perform_qubit_spectroscopy(q_no: int, rr_no: int = None, **kwargs):
    """Instantiate QubitSpectroscopy, run the full sequence, and return the object."""
    exp = QubitSpectroscopy(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    q_list = [
        # 1,
        # 2,
        # 3,
        4,
        # 5,
        # 6,
    ]

    for q in q_list:
        perform_qubit_spectroscopy(
            q_no=q,
            n_avgs=100,
            n_samples=2000,
            f_min_MHz=-400,
            f_max_MHz=400,
            use_rotated=True,
            update_config=True ,
            save_data=True,
        )
