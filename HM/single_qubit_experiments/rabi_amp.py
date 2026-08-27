import time
import json
import logging
from pathlib import Path
import datetime

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from termcolor import cprint

from qm.qua import (
    program,
    declare,
    declare_stream,
    for_,
    save,
    stream_processing,
    fixed,
    amp,
    play,
    wait,
    align,
    reset_frame,
    frame_rotation_2pi,
)
from qm import QuantumMachinesManager, QuantumMachine
from qualang_tools.results import fetching_tool, progress_counter
from qualang_tools.plot import interrupt_on_close

from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json
from Helper_Functions.macros import cooldown, measure_macro
from Helper_Functions.spectro_helper import normalize, S2N_1

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class RabiAmplitudeCalibration(SingleQubitExperiment):

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="rabi_amp",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )
        self.n_avgs = int(kwargs.get("n_avgs", 5000))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250000))
        self.wait_q = int(kwargs.get("wait_q", 4))
        self.n_fit_points = int(kwargs.get("n_fit_points", 2000))
        self.snr_stop = float(kwargs.get("snr_stop", 15.0))
        self.min_avg_bound = int(kwargs.get("min_avg_bound", kwargs.get("snr_stop_min_avg", 70)))
        self.rotation_method = str(kwargs.get("rotation_method", "pca")).lower()
        self.peak = bool(kwargs.get("peak", True))
        self.update_config = bool(kwargs.get("update_config", True))
        self.save_data = bool(kwargs.get("save_data", False))
        self.pulse_name = str(kwargs.get("pulse_name", "grft"))
        self.calibs = kwargs.get("calibs", ["X180", "X90", "Y180", "Y90"])
        n_pulses_override = kwargs.get("n_pulses", None)
        self.n_pulses = int(n_pulses_override) if n_pulses_override is not None else None
        amp_override = kwargs.get("amp_override", None)
        self.amp_override = None
        self.amp_override_mode = "none"
        if amp_override is not None:
            if not isinstance(amp_override, dict):
                raise ValueError(
                    "amp_override must be a dict with either "
                    "{amin, amax, da} or {span, center/center_point, da}"
                )
            self.amp_override = {}
            if "amin" in amp_override and amp_override["amin"] is not None:
                self.amp_override["amin"] = float(amp_override["amin"])
            if "amax" in amp_override and amp_override["amax"] is not None:
                self.amp_override["amax"] = float(amp_override["amax"])
            if "span" in amp_override and amp_override["span"] is not None:
                self.amp_override["span"] = float(amp_override["span"])
            if "center" in amp_override:
                self.amp_override["center"] = (
                    float(amp_override["center"]) if amp_override["center"] is not None else None
                )
            if "center_point" in amp_override:
                self.amp_override["center_point"] = (
                    float(amp_override["center_point"])
                    if amp_override["center_point"] is not None
                    else None
                )
            if "da" in amp_override and amp_override["da"] is not None:
                self.amp_override["da"] = float(amp_override["da"])
            if ("amin" in self.amp_override) or ("amax" in self.amp_override):
                self.amp_override_mode = "amin_amax"
            elif "span" in self.amp_override:
                self.amp_override_mode = "span_center"
        self.fit_quadrature = str(kwargs.get("fit_quadrature", "I")).upper()
        self.use_rotated = bool(kwargs.get("use_rotated", False))
        self.normalize_plot_trace_per_calib = bool(
            kwargs.get("normalize_plot_trace_per_calib", True)
        )
        self.auto_scale_sweep_with_n_pulses = bool(
            kwargs.get("auto_scale_sweep_with_n_pulses", True)
        )
        # amp_selection_mode:
        # - "sine_fit": pick from sine-fit amplitude and scale by n_pulses when n_pulses > 1
        # - "zoomed_in_peak": pick local peak/dip closest to previous calibration, no scaling
        # - "sine_local_poly": estimate pi from sine, then local poly-4 refinement near estimate
        amp_selection_mode = kwargs.get("amp_selection_mode", None)
        if amp_selection_mode is None:
            # Backward-compatible typo alias used in ad-hoc scripts.
            amp_selection_mode = kwargs.get("amp_seletion_method", None)
        if amp_selection_mode is None:
            # Backward compatibility with older toggle.
            legacy_phase_pick = bool(kwargs.get("pick_amp_from_phase_rotation", False))
            amp_selection_mode = "sine_fit" if legacy_phase_pick else "zoomed_in_peak"
        self.amp_selection_mode = str(amp_selection_mode).lower()
        if self.amp_selection_mode not in {"sine_fit", "zoomed_in_peak", "sine_local_poly"}:
            raise ValueError(
                "amp_selection_mode must be 'sine_fit', 'zoomed_in_peak', or 'sine_local_poly'"
            )
        if self.fit_quadrature not in ("I", "Q"):
            raise ValueError("fit_quadrature must be 'I' or 'Q'")

        with open(self.config_files_path + "/Pulse_Calibrations/calib_vals.json", "r") as fh:
            self.calib_vals = json.load(fh)

        self.results_by_calib = {}
        self.fit_params_by_calib = {}
        self.best_amp_by_calib = {}
        self._rabi_scaling_data = {"I": [], "Q": []}
        self._rotation_angles_rad = []
        self._qmm = None

    @staticmethod
    def _circular_mean(angles_rad: np.ndarray) -> float:
        angles = np.asarray(angles_rad, dtype=float)
        if angles.size == 0:
            return 0.0
        return float(np.angle(np.mean(np.exp(1j * angles))))

    @staticmethod
    def _local_mean(arr: np.ndarray, idx: int, half_window: int = 1) -> float:
        lo = max(0, int(idx) - int(half_window))
        hi = min(len(arr), int(idx) + int(half_window) + 1)
        return float(np.mean(np.asarray(arr, dtype=float)[lo:hi]))

    @staticmethod
    def _minmax_normalize(arr: np.ndarray) -> np.ndarray:
        data = np.asarray(arr, dtype=float)
        if data.size == 0:
            return data
        dmin = float(np.min(data))
        dmax = float(np.max(data))
        span = dmax - dmin
        if np.isclose(span, 0.0):
            return data.copy()
        return (data - dmin) / span

    def _infer_rotation_pi_flip(self):
        """
        Infer whether an additional +pi phase flip is needed.

        Heuristic: compare rotated-I near 0-drive and near previously calibrated pi.
        If I(pi_prev) < I(0), mark flip=True.
        """
        preferred_calibs = ["X180", "Y180", "X90", "Y90"]
        for calib in preferred_calibs:
            blob = self.results_by_calib.get(calib)
            if not isinstance(blob, dict):
                continue
            amps = np.asarray(blob.get("amps", []), dtype=float)
            i_trace = np.asarray(blob.get("I", []), dtype=float)
            if amps.size < 3 or i_trace.size != amps.size:
                continue

            n_pulses = max(1, int(blob.get("n_pulses", 1)))
            target_gate_amp = self._target_gate_amp_for_calib(calib)
            if self.amp_selection_mode in {"sine_fit", "sine_local_poly"} and n_pulses > 1:
                target_seq_amp = float(target_gate_amp) / float(n_pulses)
            else:
                target_seq_amp = float(target_gate_amp)

            idx_zero = int(np.argmin(np.abs(amps - float(np.min(amps)))))
            idx_pi = int(np.argmin(np.abs(amps - target_seq_amp)))
            i_zero = self._local_mean(i_trace, idx_zero, half_window=1)
            i_pi = self._local_mean(i_trace, idx_pi, half_window=1)
            needs_flip = bool(i_pi < i_zero)
            return needs_flip, {
                "calib_used": calib,
                "zero_amp_seq": float(amps[idx_zero]),
                "target_pi_amp_seq": float(target_seq_amp),
                "nearest_pi_amp_seq": float(amps[idx_pi]),
                "i_zero_local_mean": float(i_zero),
                "i_pi_local_mean": float(i_pi),
            }

        return False, {
            "calib_used": None,
            "reason": "No suitable calibration trace found for flip inference.",
        }

    def _get_amp_sweep(self, calib: str):
        vals = self.calib_vals[str(self.q_no)]
        input_regime = "calib_vals"
        if self.amp_override is not None:
            da = float(self.amp_override.get("da", vals["da"]))
            if "amin" in self.amp_override or "amax" in self.amp_override:
                a_min = float(self.amp_override.get("amin", vals["amin"]))
                a_max = float(self.amp_override.get("amax", vals["amax"]))
                input_regime = "amin_amax"
            elif "span" in self.amp_override:
                span = float(self.amp_override["span"])
                if span <= 0:
                    raise ValueError("amp_override['span'] must be > 0")
                center = self.amp_override.get("center", self.amp_override.get("center_point", None))
                if center is None:
                    # Fallback center is previous calibrated pi amplitude for this axis.
                    center = self.Y180_amp if "Y" in calib else self.X180_amp
                center = float(center)
                a_min = center - 0.5 * span
                a_max = center + 0.5 * span
                input_regime = "span_center"
            else:
                a_min = float(vals["amin"])
                a_max = float(vals["amax"])
                input_regime = "calib_vals"
        else:
            a_min = float(vals["amin"])
            a_max = float(vals["amax"])
            da = float(vals["da"])
        if da <= 0:
            raise ValueError("Sweep step size da must be > 0")
        if a_max <= a_min:
            raise ValueError(f"Invalid sweep bounds: amax ({a_max}) must be > amin ({a_min})")
        n_pulses = self.n_pulses if self.n_pulses is not None else int(vals["n_pulses"])

        if "90" in calib:
            a_min *= 0.5
            a_max *= 0.5
            da *= 0.5

        # For multi-pulse sequences, calibrate in sequence-amplitude space.
        # A first extremum appears roughly at gate_amp / n_pulses, so scale the
        # sweep window down to avoid selecting high-order extrema.
        if (
            self.auto_scale_sweep_with_n_pulses
            and input_regime == "calib_vals"
            and self.amp_selection_mode in {"sine_fit", "sine_local_poly"}
            and int(n_pulses) > 1
        ):
            a_min /= float(n_pulses)
            a_max /= float(n_pulses)
            da /= float(n_pulses)

        # Remove floating-point artifacts from sweep parameters (display + stepping).
        a_min = float(np.round(a_min, 12))
        a_max = float(np.round(a_max, 12))
        da = float(np.round(da, 12))

        amps = np.arange(a_min, a_max + da / 2, da)
        return amps, n_pulses, a_min, a_max, da

    def _build_program(self, amps: np.ndarray, n_pulses: int, calib: str):
        qe = self.q_str
        rr = self.rr_str
        out = self.out
        a_min = float(amps[0])
        a_max = float(amps[-1])
        if len(amps) > 1:
            da = float(amps[1] - amps[0])
        else:
            da = 1e-3
        n_amp_pts = int(len(amps))
        da_str = np.format_float_positional(float(da), precision=12, trim="-")
        cprint(f"da: {da_str}", "green", attrs=["bold"])
        is_y = ("Y" in calib)
        is_90 = ("90" in calib)

        with program() as prog:
            n = declare(int)
            i = declare(int)
            I = declare(fixed)
            Q = declare(fixed)
            a = declare(fixed)
            I_st = declare_stream()
            Q_st = declare_stream()
            n_st = declare_stream()

            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(a, a_min, a < a_max + da / 2, a + da):
                    cooldown(time=self.rep_rate_clk)
                    reset_frame(qe)
                    if is_y:
                        frame_rotation_2pi(0.25, qe)

                    with for_(i, 0, i < n_pulses, i + 1):
                        play(self.pulse_name * amp(a), qe)
                        wait(self.wait_q, qe)
                        if is_90:
                            play(self.pulse_name * amp(a), qe)
                            wait(self.wait_q, qe)

                    align(rr, qe)
                    measure_macro(qe, rr, out, I, Q, pi_12=False)
                    save(I, I_st)
                    save(Q, Q_st)
                save(n, n_st)

            with stream_processing():
                I_st.buffer(n_amp_pts).average().save("I")
                Q_st.buffer(n_amp_pts).average().save("Q")
                n_st.save("iteration")

        return prog

    @staticmethod
    def _poly4(x, p4, p3, p2, p1, p0):
        return p4 * x**4 + p3 * x**3 + p2 * x**2 + p1 * x + p0

    @staticmethod
    def _local_extrema_indices(y: np.ndarray, mode: str = "max") -> np.ndarray:
        """Return local extrema indices for a 1D curve."""
        y = np.asarray(y, dtype=float)
        if y.size < 3:
            return np.array([], dtype=int)
        if mode == "max":
            mask = (y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:])
        elif mode == "min":
            mask = (y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:])
        else:
            raise ValueError("mode must be 'max' or 'min'")
        return np.where(mask)[0] + 1

    def _target_gate_amp_for_calib(self, calib: str) -> float:
        base_pi_amp = self.Y180_amp if "Y" in calib else self.X180_amp
        return 0.5 * float(base_pi_amp) if "90" in calib else float(base_pi_amp)

    @staticmethod
    def _pi_sine_amp_from_angular_frequency(w: float) -> float:
        """Amplitude span for pi radians of the fitted sine phase."""
        w_abs = abs(float(w))
        if w_abs <= 1e-12:
            raise ValueError("Invalid angular frequency for sine-fit pi amplitude.")
        return float(np.pi / w_abs)

    def _select_extremum_near_target_seq_amp(
        self, amp_dense: np.ndarray, fit_dense: np.ndarray, target_seq_amp: float
    ) -> float:
        """Pick local extremum closest to target sequence amplitude."""
        mode = "max" if self.peak else "min"
        extrema_idx = self._local_extrema_indices(fit_dense, mode=mode)
        if extrema_idx.size == 0:
            return float(amp_dense[int(np.argmax(fit_dense) if self.peak else np.argmin(fit_dense))])
        seq_candidates = np.asarray(amp_dense[extrema_idx], dtype=float)
        best_idx = int(np.argmin(np.abs(seq_candidates - float(target_seq_amp))))
        return float(seq_candidates[best_idx])

    def _select_amp_from_fit(
        self, amp_dense: np.ndarray, fit_dense: np.ndarray, calib: str, n_pulses: int
    ) -> float:
        """
        Pick calibration amplitude from fitted trace.
        For multi-pulse runs, choose the extremum whose scaled gate amplitude is
        closest to the previously calibrated target (pi for 180, pi/2 for 90).
        Otherwise use the leftmost local extremum.
        """
        if self.peak:
            extrema_idx = self._local_extrema_indices(fit_dense, mode="max")
            if extrema_idx.size:
                if int(n_pulses) > 1:
                    target_gate_amp = self._target_gate_amp_for_calib(calib)
                    seq_candidates = np.asarray(amp_dense[extrema_idx], dtype=float)
                    if self.amp_selection_mode == "zoomed_in_peak":
                        candidate_metric = seq_candidates
                    else:
                        candidate_metric = np.asarray(
                            [
                                self._scale_sequence_amp_to_gate_amp(a, n_pulses, calib)
                                for a in seq_candidates
                            ],
                            dtype=float,
                        )
                    best_idx = int(np.argmin(np.abs(candidate_metric - target_gate_amp)))
                    return float(seq_candidates[best_idx])
                return float(amp_dense[int(extrema_idx[0])])
            return float(amp_dense[int(np.argmax(fit_dense))])
        extrema_idx = self._local_extrema_indices(fit_dense, mode="min")
        if extrema_idx.size:
            if int(n_pulses) > 1:
                target_gate_amp = self._target_gate_amp_for_calib(calib)
                seq_candidates = np.asarray(amp_dense[extrema_idx], dtype=float)
                if self.amp_selection_mode == "zoomed_in_peak":
                    candidate_metric = seq_candidates
                else:
                    candidate_metric = np.asarray(
                        [
                            self._scale_sequence_amp_to_gate_amp(a, n_pulses, calib)
                            for a in seq_candidates
                        ],
                        dtype=float,
                    )
                best_idx = int(np.argmin(np.abs(candidate_metric - target_gate_amp)))
                return float(seq_candidates[best_idx])
            return float(amp_dense[int(extrema_idx[0])])
        return float(amp_dense[int(np.argmin(fit_dense))])

    def _fit_poly4(self, amps: np.ndarray, trace: np.ndarray, calib: str, n_pulses: int):
        coeff = np.polyfit(amps, trace, 4)
        fit_at_amps = self._poly4(amps, *coeff)
        mse = self._mse(trace, fit_at_amps)
        amp_dense = np.linspace(float(amps[0]), float(amps[-1]), self.n_fit_points)
        fit_dense = self._poly4(amp_dense, *coeff)
        best_amp = self._select_amp_from_fit(amp_dense, fit_dense, calib, n_pulses)
        return {
            "model": "poly4",
            "best_amp": best_amp,
            "amp_dense": amp_dense,
            "fit_dense": fit_dense,
            "mse": mse,
            "params": {
                "power0": float(coeff[0]),
                "power1": float(coeff[1]),
                "power2": float(coeff[2]),
                "power3": float(coeff[3]),
                "power4": float(coeff[4]),
            },
        }

    def _fit_sine(self, amps: np.ndarray, trace: np.ndarray, calib: str, n_pulses: int):
        if len(amps) < 4:
            return None

        x = np.asarray(amps, dtype=float)
        y = np.asarray(trace, dtype=float)
        x0 = float(x[0])
        x_shift = x - x0
        x_span = float(x_shift[-1] - x_shift[0])
        if x_span <= 0:
            return None

        diffs = np.diff(x)
        step = float(np.median(np.abs(diffs)))
        if step <= 0:
            return None

        freq_min = 1.0 / (4.0 * x_span)
        freq_max = 0.5 / step
        if freq_max <= freq_min:
            return None

        n_grid = int(np.clip(6 * len(x), 80, 500))
        freqs = np.linspace(freq_min, freq_max, n_grid)

        best = None
        for f in freqs:
            w = 2.0 * np.pi * f
            s = np.sin(w * x_shift)
            c = np.cos(w * x_shift)
            design = np.column_stack((s, c, np.ones_like(x_shift)))
            try:
                beta, *_ = np.linalg.lstsq(design, y, rcond=None)
            except np.linalg.LinAlgError:
                continue
            y_hat = design @ beta
            mse = self._mse(y, y_hat)
            if best is None or mse < best["mse"]:
                best = {"w": w, "beta": beta, "mse": mse}

        if best is None:
            return None

        b_sin, c_cos, offset = best["beta"]
        sine_amp = float(np.hypot(b_sin, c_cos))
        phase = float(np.arctan2(c_cos, b_sin))
        w_best = float(best["w"])
        mse = float(best["mse"])

        amp_dense = np.linspace(float(amps[0]), float(amps[-1]), self.n_fit_points)
        x_dense_shift = amp_dense - x0
        fit_dense = b_sin * np.sin(w_best * x_dense_shift) + c_cos * np.cos(w_best * x_dense_shift) + offset
        best_amp = self._select_amp_from_fit(amp_dense, fit_dense, calib, n_pulses)
        amp_pick_method = "closest_prev_calib" if int(n_pulses) > 1 else "leftmost_extrema"

        return {
            "model": "sine",
            "best_amp": best_amp,
            "amp_dense": amp_dense,
            "fit_dense": fit_dense,
            "mse": mse,
            "params": {
                "sine_amplitude": sine_amp,
                "angular_frequency": w_best,
                "phase": phase,
                "offset": float(offset),
                "amp_pick_method": amp_pick_method,
            },
        }

    def _fit_trace(self, amps: np.ndarray, trace: np.ndarray, calib: str, n_pulses: int):
        poly_result = None
        try:
            poly_result = self._fit_poly4(amps, trace, calib, n_pulses)
        except Exception as exc:
            logger.warning("poly4 fit failed: %s", exc)

        sine_result = self._fit_sine(amps, trace, calib, n_pulses)

        candidates = [res for res in (poly_result, sine_result) if res is not None]
        if not candidates:
            raise RuntimeError("Both poly4 and sine fits failed")

        selected = min(candidates, key=lambda res: res["mse"])
        selected["poly4_mse"] = poly_result["mse"] if poly_result is not None else None
        selected["sine_mse"] = sine_result["mse"] if sine_result is not None else None
        return selected

    def _scale_sequence_amp_to_gate_amp(self, selected_amp: float, n_pulses: int, calib: str) -> float:
        """
        Convert fitted sequence amplitude to single-gate amplitude.

        Assumes selected_amp corresponds to the first sequence peak (total pi rotation).
        - For X/Y180: pulses_per_iter=1, target gate angle = pi.
        - For X/Y90 : pulses_per_iter=2, target gate angle = pi/2.
        """
        pulses_per_iter = 2 if "90" in calib else 1
        target_angle_over_pi = 0.5 if "90" in calib else 1.0
        scale_factor = float(n_pulses) * pulses_per_iter * target_angle_over_pi
        return float(selected_amp) * scale_factor

    def _run_one_calib(self, qm: QuantumMachine, calib: str):
        amps, n_pulses, a_min, a_max, da = self._get_amp_sweep(calib)
        prog = self._build_program(amps, n_pulses, calib)
        job = qm.execute(prog)
        job_sim = qm.simulate(prog, SimulationConfig(int(10000)))
        
        results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

        fig, axs = plt.subplots(2, 1, sharex=True)
        interrupt_on_close(fig, job)
        while results.is_processing():
            I, Q, iteration = results.fetch_all()
            progress_counter(iteration, self.n_avgs, start_time=results.get_start_time())
            axs[0].cla()
            axs[1].cla()
            axs[0].plot(amps, I, ".-", label="I")
            axs[1].plot(amps, Q, ".-", label="Q")
            axs[0].set(ylabel="Rabi response (a.u.)")
            axs[1].set(xlabel="Pulse amplitude", ylabel="Rabi response (a.u.)")
            for ax in axs:
                ax.grid(True)
                ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                ax.legend()
            fig.suptitle(
                f"Power Rabi q{self.q_no} - {calib} | pi_len={int(self.pi_len_ns)} ns"
            )
            plt.tight_layout()
            plt.pause(0.2)

            snr_i, _ = S2N_1(normalize(I))
            snr_q, _ = S2N_1(normalize(Q))
            min_avg_before_snr_stop = (
                self.min_avg_bound if self.n_avgs > self.min_avg_bound else 0
            )
            if (
                iteration >= min_avg_before_snr_stop
                and (snr_i > self.snr_stop or snr_q > self.snr_stop)
            ):
                job.halt()

        plt.close(fig)
        
        I_raw = np.asarray(job.result_handles.get("I").fetch_all())
        Q_raw = np.asarray(job.result_handles.get("Q").fetch_all())
        I_bounds, Q_bounds, rotation_angle_rad = self._processed_quadratures(
            I_raw,
            Q_raw,
            scale_with_rabi_bounds=False,
            method=self.rotation_method,
            return_angle=True,
        )
        self._rotation_angles_rad.append(float(rotation_angle_rad))
        self._rabi_scaling_data["I"].append(np.asarray(I_bounds, dtype=float))
        self._rabi_scaling_data["Q"].append(np.asarray(Q_bounds, dtype=float))

        if self.use_rotated:
            I, Q = np.asarray(I_bounds, dtype=float), np.asarray(Q_bounds, dtype=float)
            if self.normalize_plot_trace_per_calib:
                I = self._minmax_normalize(I)
                Q = self._minmax_normalize(Q)
        else:
            I, Q = I_raw, Q_raw
        fit_trace = I if self.fit_quadrature == "I" else Q
        fit_result = self._fit_trace(amps, fit_trace, calib, n_pulses)
        sine_pi_seq_amp = None
        sine_pi_gate_amp = None
        poly_local_gate_amp = None
        if self.amp_selection_mode == "sine_fit":
            sine_result = self._fit_sine(amps, fit_trace, calib, n_pulses)
            if sine_result is None:
                raise RuntimeError("amp_selection_mode='sine_fit' requires a valid sine fit.")
            fit_result = sine_result
            w = float(sine_result["params"]["angular_frequency"])
            pi_sine_amp = self._pi_sine_amp_from_angular_frequency(w)
            selected_amp = self._select_extremum_near_target_seq_amp(
                np.asarray(sine_result["amp_dense"], dtype=float),
                np.asarray(sine_result["fit_dense"], dtype=float),
                target_seq_amp=pi_sine_amp,
            )
            gate_amp = self._scale_sequence_amp_to_gate_amp(selected_amp, n_pulses, calib)
            sine_pi_seq_amp = float(pi_sine_amp)
            sine_pi_gate_amp = self._scale_sequence_amp_to_gate_amp(pi_sine_amp, n_pulses, calib)
            amp_pick_method = "extremum_near_n_times_pi_sine_amp"
        elif self.amp_selection_mode == "sine_local_poly":
            sine_result = self._fit_sine(amps, fit_trace, calib, n_pulses)
            if sine_result is None:
                raise RuntimeError("amp_selection_mode='sine_local_poly' requires a valid sine fit.")
            fit_result = sine_result
            w = float(sine_result["params"]["angular_frequency"])
            sine_pi_seq_amp = self._pi_sine_amp_from_angular_frequency(w)
            sine_pi_gate_amp = self._scale_sequence_amp_to_gate_amp(sine_pi_seq_amp, n_pulses, calib)

            # If sine pi estimate sits in swept bounds, refine locally with poly4.
            amps_arr = np.asarray(amps, dtype=float)
            in_bounds = bool(np.min(amps_arr) <= sine_pi_seq_amp <= np.max(amps_arr))
            half_span_seq = 0.5 * sine_pi_seq_amp
            local_mask = np.abs(amps_arr - sine_pi_seq_amp) <= half_span_seq
            local_count = int(np.sum(local_mask))
            if in_bounds and local_count >= 5:
                x_local = amps_arr[local_mask]
                y_local = np.asarray(fit_trace, dtype=float)[local_mask]
                poly_coeff = np.polyfit(x_local, y_local, 4)
                p4 = np.poly1d(poly_coeff)
                dp = np.polyder(p4)
                d2p = np.polyder(dp)

                roots = dp.r
                real_roots = np.asarray([r.real for r in roots if np.isreal(r)], dtype=float)
                in_window = real_roots[(real_roots >= x_local.min()) & (real_roots <= x_local.max())]
                if in_window.size > 0:
                    second_derivs = np.asarray([d2p(r) for r in in_window], dtype=float)
                    # Infer expected extremum type from sine around estimate.
                    xd = np.linspace(x_local.min(), x_local.max(), 400)
                    yd = (
                        sine_result["params"]["sine_amplitude"]
                        * np.sin(sine_result["params"]["angular_frequency"] * (xd - float(amps[0]))
                                 + sine_result["params"]["phase"])
                        + sine_result["params"]["offset"]
                    )
                    center_idx = int(np.argmin(np.abs(xd - sine_pi_seq_amp)))
                    ydd = np.gradient(np.gradient(yd, xd), xd)[center_idx]
                    if ydd < 0:
                        candidate_idx = np.where(second_derivs < 0)[0]  # maxima
                    else:
                        candidate_idx = np.where(second_derivs > 0)[0]  # minima
                    candidate_roots = in_window[candidate_idx] if candidate_idx.size > 0 else in_window
                    selected_amp = float(candidate_roots[int(np.argmin(np.abs(candidate_roots - sine_pi_seq_amp)))])
                    gate_amp = self._scale_sequence_amp_to_gate_amp(selected_amp, n_pulses, calib)
                    poly_local_gate_amp = gate_amp
                    amp_pick_method = "sine_estimate_plus_local_poly4_extremum"
                else:
                    # No internal extremum in local window; use nearest global fit extremum.
                    selected_amp = self._select_extremum_near_target_seq_amp(
                        np.asarray(sine_result["amp_dense"], dtype=float),
                        np.asarray(sine_result["fit_dense"], dtype=float),
                        target_seq_amp=sine_pi_seq_amp,
                    )
                    gate_amp = self._scale_sequence_amp_to_gate_amp(selected_amp, n_pulses, calib)
                    amp_pick_method = "sine_estimate_fallback_no_poly_extremum"
            else:
                # Out-of-range or sparse local data: nearest global fit extremum to sine estimate.
                selected_amp = self._select_extremum_near_target_seq_amp(
                    np.asarray(sine_result["amp_dense"], dtype=float),
                    np.asarray(sine_result["fit_dense"], dtype=float),
                    target_seq_amp=sine_pi_seq_amp,
                )
                gate_amp = self._scale_sequence_amp_to_gate_amp(selected_amp, n_pulses, calib)
                amp_pick_method = (
                    "sine_estimate_fallback_out_of_bounds"
                    if not in_bounds
                    else "sine_estimate_fallback_insufficient_local_points"
                )
        else:
            selected_amp = float(fit_result["best_amp"])
            gate_amp = float(selected_amp)
            amp_pick_method = "zoomed_in_peak"
        amp_dense = fit_result["amp_dense"]
        fit_dense = fit_result["fit_dense"]
        poly4_mse = fit_result.get("poly4_mse", None)
        sine_mse = fit_result.get("sine_mse", None)
        if fit_result.get("model") == "poly4" and poly4_mse is None:
            poly4_mse = float(fit_result["mse"])
        if fit_result.get("model") == "sine" and sine_mse is None:
            sine_mse = float(fit_result["mse"])
        logger.info(
            (
                "%s selected sequence amp = %.8f, scaled gate amp = %.8f (n_pulses=%d; "
                "fit on %s, model=%s, mse=%0.3e, poly4_mse=%s, sine_mse=%s)"
            ),
            calib,
            selected_amp,
            gate_amp,
            n_pulses,
            self.fit_quadrature,
            fit_result["model"],
            fit_result["mse"],
            f"{poly4_mse:.3e}" if poly4_mse is not None else "None",
            f"{sine_mse:.3e}" if sine_mse is not None else "None",
        )

        self.results_by_calib[calib] = {
            "amps": amps,
            "I": I,
            "Q": Q,
            "n_pulses": n_pulses,
            "a_min": a_min,
            "a_max": a_max,
            "da": da,
            "fit_model": fit_result["model"],
            "selected_sequence_amp": selected_amp,
            "scaled_gate_amp": gate_amp,
            "amp_pick_method": amp_pick_method,
            "sine_pi_sequence_amp": sine_pi_seq_amp,
            "sine_pi_gate_amp": sine_pi_gate_amp,
            "poly_local_gate_amp": poly_local_gate_amp,
        }
        fit_params = {
            "fit_quadrature": self.fit_quadrature,
            "fit_model": fit_result["model"],
            "amp_pick_method": amp_pick_method,
            "fit_mse": float(fit_result["mse"]),
            "poly4_mse": poly4_mse,
            "sine_mse": sine_mse,
            "selected_sequence_amp": float(selected_amp),
            "scaled_gate_amp": float(gate_amp),
            "n_pulses": int(n_pulses),
            "sine_pi_sequence_amp": None if sine_pi_seq_amp is None else float(sine_pi_seq_amp),
            "sine_pi_gate_amp": None if sine_pi_gate_amp is None else float(sine_pi_gate_amp),
            "poly_local_gate_amp": None if poly_local_gate_amp is None else float(poly_local_gate_amp),
        }
        fit_params.update(fit_result["params"])
        self.fit_params_by_calib[calib] = fit_params
        self.best_amp_by_calib[calib] = gate_amp

        # Save fit plot per calibration
        fig2, axs2 = plt.subplots(1, 2, figsize=(12, 4.8))
        ax_fit, ax_iq = axs2

        ax_fit.plot(amps, I, ".", label="I data")
        ax_fit.plot(amps, Q, ".", label="Q data")
        selected_label = "4th-order fit" if fit_result["model"] == "poly4" else "sine fit"
        ax_fit.plot(
            amp_dense,
            fit_dense,
            "-",
            label=f"{self.fit_quadrature} {selected_label} (MSE={fit_result['mse']:.2e})",
        )
        amp_min_plot = float(np.min(amps))
        amp_max_plot = float(np.max(amps))
        if amp_min_plot <= float(selected_amp) <= amp_max_plot:
            ax_fit.axvline(
                selected_amp,
                color="k",
                linestyle="--",
                label=f"Selected seq amp={selected_amp:.6f}",
            )
            if sine_pi_seq_amp is not None and amp_min_plot <= float(sine_pi_seq_amp) <= amp_max_plot:
                ax_fit.axvline(
                    float(sine_pi_seq_amp),
                    color="tab:purple",
                    linestyle=":",
                    linewidth=1.5,
                    label=f"Sine pi est (seq)={float(sine_pi_seq_amp):.6f}",
                )
        else:
            ax_fit.text(
                0.02,
                0.03,
                (
                    f"Seq amp {selected_amp:.6f} outside sweep "
                    f"[{amp_min_plot:.6f}, {amp_max_plot:.6f}]"
                ),
                transform=ax_fit.transAxes,
                fontsize=8,
                ha="left",
                va="bottom",
                bbox={"facecolor": "white", "alpha": 0.65, "edgecolor": "none"},
            )
        ax_fit.text(
            0.02,
            0.97,
            f"Gate amplitude = {gate_amp:.6f}",
            transform=ax_fit.transAxes,
            fontsize=8,
            ha="left",
            va="top",
            bbox={"facecolor": "white", "alpha": 0.65, "edgecolor": "none"},
        )
        if sine_pi_gate_amp is not None:
            ax_fit.text(
                0.02,
                0.90,
                f"Sine-fit gate estimate = {float(sine_pi_gate_amp):.6f}",
                transform=ax_fit.transAxes,
                fontsize=8,
                ha="left",
                va="top",
                bbox={"facecolor": "white", "alpha": 0.65, "edgecolor": "none"},
            )
        ax_fit.set_xlabel("Drive amplitude")
        ax_fit.set_ylabel("Rabi response (a.u.)")
        ax_fit.set_title(
            f"Power Rabi q{self.q_no} - {calib} | N={n_pulses} | pi_len={int(self.pi_len_ns)} ns"
        )
        ax_fit.grid(True)
        ax_fit.legend(loc="best", fontsize=8, framealpha=0.8)
        ax_fit.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

        # Show pre-rotation readout channels directly versus drive amplitude.
        ax_iq.plot(amps, I_raw, "o-", markersize=3, linewidth=1, alpha=0.9, label="I raw")
        ax_iq.plot(amps, Q_raw, "o-", markersize=3, linewidth=1, alpha=0.9, label="Q raw")
        ax_iq.set_xlabel("Drive amplitude")
        ax_iq.set_ylabel("Readout response (a.u.)")
        ax_iq.set_title("Raw I/Q (before rotation)")
        ax_iq.grid(True)
        ax_iq.legend()
        ax_iq.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

        plot_path = str(self.path_to_save) + f"_q{self.q_no}_{calib}.png"
        fig2.savefig(plot_path, bbox_inches="tight")
        cprint(f"Figure saved: {Path(plot_path).as_uri()}", "green")
        plt.show(block=False)

    def run_experiment(self):
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        qm = self._qmm.open_qm(self.config)
        # print(self.config["elements"][self.q_str]["mixInputs"])
        # print(self.config["elements"][self.q_str]["intermediate_frequency"])
        # exit()
        try:
            for calib in self.calibs:
                logger.info(f"Running power Rabi for q{self.q_no}: {calib}")
                self._run_one_calib(qm, calib)
        finally:
            try:
                qm.close()
            except Exception:
                pass

    def analyze_and_plot(self):
        """No-op: per-calibration fit plots are generated in _run_one_calib()."""
        return self.best_amp_by_calib

    def update_config_dicts(self):
        if not self.update_config:
            return

        amp_scale_path = self.config_files_path + "/Pulse_Calibrations/amp_scale.json"
        with open(amp_scale_path, "r") as fh:
            amp_scale = json.load(fh)

        q_key = str(self.q_no)
        if q_key not in amp_scale:
            amp_scale[q_key] = {}

        for calib, val in self.best_amp_by_calib.items():
            amp_scale[q_key][calib] = float(val)
            logger.info(f"amp_scale[{q_key}][{calib}] = {val:.8f}")

        with open(amp_scale_path, "w") as fh:
            json.dump(amp_scale, fh, indent=6)

        rabi_scaling_path = self.config_files_path + "/Pulse_Calibrations/rabi_scaling.json"
        try:
            with open(rabi_scaling_path, "r") as fh:
                rabi_scaling = json.load(fh)
        except (OSError, json.JSONDecodeError):
            rabi_scaling = {}

        if "rabi_scalings" not in rabi_scaling or not isinstance(rabi_scaling["rabi_scalings"], dict):
            rabi_scaling["rabi_scalings"] = {}

        q_key = str(self.q_no)
        I_all = (
            np.concatenate(self._rabi_scaling_data["I"])
            if self._rabi_scaling_data["I"]
            else np.array([], dtype=float)
        )
        Q_all = (
            np.concatenate(self._rabi_scaling_data["Q"])
            if self._rabi_scaling_data["Q"]
            else np.array([], dtype=float)
        )

        if I_all.size and Q_all.size:
            prev_entry = rabi_scaling["rabi_scalings"].get(q_key, {})
            if self._rotation_angles_rad:
                rotation_angle_rad = self._circular_mean(np.asarray(self._rotation_angles_rad, dtype=float))
            else:
                rotation_angle_rad = float(prev_entry.get("rotation_angle_rad", 0.0))
            needs_pi_flip, flip_meta = self._infer_rotation_pi_flip()
            rotation_angle_applied_rad = float(
                self.to_pm_pi(rotation_angle_rad + (np.pi if needs_pi_flip else 0.0))
            )
            rotation_angle_applied_deg = float(np.degrees(rotation_angle_applied_rad))
            qubit_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated_entry = dict(prev_entry)
            updated_entry.update({
                "I_min": float(np.min(I_all)),
                "I_max": float(np.max(I_all)),
                "I_mean": float(np.mean(I_all)),
                "Q_min": float(np.min(Q_all)),
                "Q_max": float(np.max(Q_all)),
                "Q_mean": float(np.mean(Q_all)),
                "rotation_angle_rad": float(rotation_angle_rad),
                "rotation_needs_pi_flip": bool(needs_pi_flip),
                "rotation_angle_applied_rad": float(rotation_angle_applied_rad),
                "rotation_method": str(self.rotation_method),
                "rotation_flip_inference": flip_meta,
                "qubit_calibration_datetime": qubit_dt,
            })
            rabi_scaling["rabi_scalings"][q_key] = updated_entry
            logger.info(
                (
                    "Updated rabi_scaling for q%s: I[%0.6f, %0.6f], Q[%0.6f, %0.6f], "
                    "angle_applied=%0.3f deg, pi_flip=%s"
                ),
                q_key,
                rabi_scaling["rabi_scalings"][q_key]["I_min"],
                rabi_scaling["rabi_scalings"][q_key]["I_max"],
                rabi_scaling["rabi_scalings"][q_key]["Q_min"],
                rabi_scaling["rabi_scalings"][q_key]["Q_max"],
                rotation_angle_applied_deg,
                str(needs_pi_flip),
            )

            rabi_scaling["calibration_datetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            with open(rabi_scaling_path, "w") as fh:
                json.dump(rabi_scaling, fh, indent=4)

    def save_experiment_data(self):
        payload = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "n_avgs": self.n_avgs,
            "rep_rate_clk": self.rep_rate_clk,
            "wait_q": self.wait_q,
            "pulse_name": self.pulse_name,
            "peak": self.peak,
            "calibs": self.calibs,
            "best_amp_by_calib": self.best_amp_by_calib,
            "fit_params_by_calib": self.fit_params_by_calib,
            "results_by_calib": self.results_by_calib,
        }
        json_path = str(self.path_to_save) + f"_q{self.q_no}.json"
        save_json(payload, json_path)
        cprint(f"Data saved: {Path(json_path).as_uri()}", "green")
        return payload

    def run(self):
        t0 = time.time()
        cprint(f"Running Rabi amplitude calibration for q{self.q_no}", "green", attrs=["bold"])
        cprint(f"Starting time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", "green", attrs=["bold"])
        try:
            self.run_experiment()
            self.analyze_and_plot()
            self.update_config_dicts()
            if self.save_data:
                self.save_experiment_data()
        finally:
            if self._qmm is not None:
                try:
                    self._qmm.close()
                except Exception:
                    pass

        elapsed = time.time() - t0
        logger.info(f"Total time: {int(elapsed // 60)}m {elapsed % 60:.1f}s")
        return self.best_amp_by_calib


def perform_rabi_amp(q_no: int, rr_no: int = None, **kwargs):
    """Instantiate RabiAmplitudeCalibration, run it, and return the object."""
    exp = RabiAmplitudeCalibration(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    amp_override = {
        # Either amin and amax or span and center must be provided
        "amin": 0.01,
        "amax":1,
        "da": 0.01,

        # "span": 0.1,
        # "center": None,
        # "da": 0.001,

    }
    rotation_method = "var_fft" #pca, endpoint, median_angle, var_fft, none
    amp_selection_mode = "sine_local_poly" #sine_fit, zoomed_in_peak, sine_local_poly
    q_list = [
        # 1,
        # 2,
        3,
        # 4,
        # 5,
        # 6,
    ]
    for q in q_list:
        perform_rabi_amp(
            q_no=q,
            n_avgs=500,
            n_pulses = 1,
            amp_override = amp_override,
            update_config=True,
            save_data=False,
            use_rotated = True,
            rotation_method = rotation_method,
            min_avg_bound = 200,
            amp_selection_mode = amp_selection_mode,
        )
