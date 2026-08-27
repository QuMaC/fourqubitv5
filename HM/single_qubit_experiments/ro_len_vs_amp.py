import logging
import time
from copy import deepcopy
from pathlib import Path
import json

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
from qm import QuantumMachinesManager
from qm.qua import (
    amp,
    align,
    declare,
    declare_stream,
    demod,
    fixed,
    for_,
    for_each_,
    measure,
    play,
    program,
    save,
    stream_processing,
    wait,
)
from qualang_tools.analysis.discriminator import two_state_discriminator
from termcolor import cprint

from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json

try:
    from tqdm.auto import tqdm
except Exception:
    tqdm = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class RoLenVsAmpCalibration(SingleQubitExperiment):
    """
    2D sweep of readout amplitude multiplier vs accumulated integration length.

    Notes
    -----
    - Uses runtime config override to force resonator readout waveform amplitude to 1.0.
    - Sets integration-weight length to the max integration length of this sweep.
    - Ensures readout pulse length is at least as long as that integration window.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="ro_len_vs_amp",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )
        self.n_runs = int(kwargs.get("n_runs", 10_000))
        self.chunk_size_clk = int(kwargs.get("chunk_size_clk", 50))
        self.a_min = float(kwargs.get("a_min", 0.005))
        self.a_max = float(kwargs.get("a_max", 0.30))
        self.da = float(kwargs.get("da", 0.005))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250_000))
        self.wait_rr = int(kwargs.get("wait_rr", 16))
        self.override_ro_amp_unity = bool(kwargs.get("override_ro_amp_unity", True))
        self.runtime_ro_waveform_sample = float(kwargs.get("runtime_ro_waveform_sample", 0.4))
        self.save_data = bool(kwargs.get("save_data", True))
        self.update_config = bool(kwargs.get("update_config", True))
        self.show_progress = bool(kwargs.get("show_progress", True))
        self.selection_metric = str(kwargs.get("selection_metric", "hybrid")).lower() #hybrid, fidelity, dprime
        self.selection_weights = kwargs.get(
            "selection_weights",
            {"fidelity": 0.6, "dprime": 0.3, "compactness": 0.1},
        )
        analysis_modes = kwargs.get("analysis_modes", None)
        if analysis_modes is None:
            self.analysis_modes = [self.selection_metric]
        else:
            if isinstance(analysis_modes, str):
                analysis_modes = [analysis_modes]
            self.analysis_modes = [str(m).lower() for m in analysis_modes]
            if len(self.analysis_modes) == 0:
                self.analysis_modes = [self.selection_metric]
        # Keep order while removing duplicates.
        self.analysis_modes = list(dict.fromkeys(self.analysis_modes))
        self.validate_best_with_ro_fidelity = bool(kwargs.get("validate_best_with_ro_fidelity", True))
        self.validation_n_runs = int(kwargs.get("validation_n_runs", self.n_runs))
        self.validation_show_plot = bool(kwargs.get("validation_show_plot", True))
        self.validation_save_plot = bool(kwargs.get("validation_save_plot", True))
        self.validation_save_data = bool(kwargs.get("validation_save_data", self.save_data))

        t_array_clk = kwargs.get("t_array_clk", None)
        if t_array_clk is not None:
            t_array_obj = np.asarray(t_array_clk, dtype=object).ravel()
            if t_array_obj.size == 0:
                raise ValueError("t_array_clk must contain at least one integration length.")
            if not all(
                isinstance(v, (int, np.integer)) and not isinstance(v, (bool, np.bool_))
                for v in t_array_obj.tolist()
            ):
                raise ValueError(
                    "t_array_clk must contain only integer clock-cycle values "
                    "(bools/floats are not allowed)."
                )
            t_array_clk = np.asarray(t_array_obj, dtype=int)
            if t_array_clk.size == 0:
                raise ValueError("t_array_clk must contain at least one integration length.")
            if np.any(t_array_clk <= 0):
                raise ValueError("t_array_clk must contain strictly positive clock-cycle lengths.")
            if np.any(np.diff(t_array_clk) <= 0):
                raise ValueError("t_array_clk must be strictly increasing.")
            if np.any(t_array_clk % self.chunk_size_clk != 0):
                raise ValueError(
                    "All entries in t_array_clk must be divisible by chunk_size_clk. "
                    f"chunk_size_clk={self.chunk_size_clk}, got t_array_clk={t_array_clk.tolist()}"
                )
            self.integration_lengths_clk = t_array_clk.astype(int)
            self.integ_len_clk_max = int(self.integration_lengths_clk[-1])
        else:
            self.integ_len_clk_max = int(kwargs.get("integ_len_clk_max", self.integ_len))
            if self.integ_len_clk_max % self.chunk_size_clk != 0:
                raise ValueError(
                    f"integ_len_clk_max={self.integ_len_clk_max} must be divisible by "
                    f"chunk_size_clk={self.chunk_size_clk}"
                )
            self.integration_lengths_clk = np.arange(
                self.chunk_size_clk,
                self.integ_len_clk_max + self.chunk_size_clk,
                self.chunk_size_clk,
                dtype=int,
            )

        self.ro_len_clk_runtime = int(
            kwargs.get("ro_len_clk_runtime", max(int(self.ro_len), self.integ_len_clk_max))
        )
        self.arr_size_full = int(self.integ_len_clk_max // self.chunk_size_clk)
        self.integration_indices = (self.integration_lengths_clk // self.chunk_size_clk - 1).astype(int)
        self.arr_size = int(len(self.integration_lengths_clk))
        self.integration_lengths_ns = self.integration_lengths_clk * self.clock_cycle_dur_ns
        self.amps = np.arange(self.a_min, self.a_max + self.da / 2, self.da)

        if not (0.0 < abs(self.runtime_ro_waveform_sample) <= 0.5):
            raise ValueError(
                "runtime_ro_waveform_sample must satisfy 0 < |sample| <= 0.5. "
                f"Got {self.runtime_ro_waveform_sample}"
            )
        self.amp_scalars = self.amps * self.runtime_ro_waveform_sample
        if np.any(np.abs(self.amp_scalars) > 2.0):
            raise ValueError(
                f"Requested amplitude sweep requires |amp({np.max(self.amp_scalars)})| > 2 after normalization. "
                "Lower a_max or increase runtime_ro_waveform_sample (<=0.5)."
            )
        if self.selection_metric not in {"fidelity", "dprime", "hybrid"}:
            raise ValueError("selection_metric must be one of: fidelity, dprime, hybrid")
        for mode in self.analysis_modes:
            if mode not in {"fidelity", "dprime", "hybrid"}:
                raise ValueError("analysis_modes must contain only: fidelity, dprime, hybrid")

        self._qmm = None
        self._qm = None
        self._runtime_config = None

        self._I0_raw = None
        self._Q0_raw = None
        self._I1_raw = None
        self._Q1_raw = None

        self.results = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "params": {
                "n_runs": self.n_runs,
                "chunk_size_clk": self.chunk_size_clk,
                "a_min": self.a_min,
                "a_max": self.a_max,
                "da": self.da,
                "rep_rate_clk": self.rep_rate_clk,
                "wait_rr": self.wait_rr,
                "integ_len_clk_max": self.integ_len_clk_max,
                "t_array_clk": self.integration_lengths_clk,
                "ro_len_clk_runtime": self.ro_len_clk_runtime,
                "override_ro_amp_unity": self.override_ro_amp_unity,
                "runtime_ro_waveform_sample": self.runtime_ro_waveform_sample,
                "update_config": self.update_config,
                "show_progress": self.show_progress,
                "selection_metric": self.selection_metric,
                "selection_weights": self.selection_weights,
                "analysis_modes": self.analysis_modes,
                "validate_best_with_ro_fidelity": self.validate_best_with_ro_fidelity,
                "validation_n_runs": self.validation_n_runs,
                "validation_show_plot": self.validation_show_plot,
                "validation_save_plot": self.validation_save_plot,
                "validation_save_data": self.validation_save_data,
            },
            "figures": [],
        }

    def _build_runtime_config(self):
        cfg = deepcopy(self.config)
        rr_key = str(self.rr_no)
        ro_pulse_name = cfg["elements"][self.rr_str]["operations"]["readout"]
        ro_wf_name = cfg["pulses"][ro_pulse_name]["waveforms"]["I"]

        cfg["pulses"][ro_pulse_name]["length"] = int(self.ro_len_clk_runtime * self.clock_cycle_dur_ns)

        if self.override_ro_amp_unity:
            cfg["waveforms"][ro_wf_name] = {
                "type": "constant",
                "sample": float(self.runtime_ro_waveform_sample),
            }

        target_weight_len_ns = int(self.integ_len_clk_max * self.clock_cycle_dur_ns)
        for weight_name in (
            f"integW_cos_rr{rr_key}",
            f"integW_sin_rr{rr_key}",
            f"integW_minus_sin_rr{rr_key}",
        ):
            if weight_name not in cfg["integration_weights"]:
                continue
            for quad in ("cosine", "sine"):
                old_coeff, _old_len = cfg["integration_weights"][weight_name][quad][0]
                coeff_real = float(np.real(old_coeff))
                cfg["integration_weights"][weight_name][quad] = [(coeff_real, target_weight_len_ns)] #check this out

        return cfg

    def _build_program(self):
        with program() as iq_blobs_prog:
            n = declare(int)
            a = declare(fixed)
            I0 = declare(fixed, size=self.arr_size_full)
            Q0 = declare(fixed, size=self.arr_size_full)
            I1 = declare(fixed, size=self.arr_size_full)
            Q1 = declare(fixed, size=self.arr_size_full)
            I0_st = declare_stream()
            Q0_st = declare_stream()
            I1_st = declare_stream()
            Q1_st = declare_stream()

            with for_each_(a, self.amp_scalars.tolist()): #check amp_scalars
                with for_(n, 0, n < self.n_runs, n + 1):
                    wait(self.rep_rate_clk, self.q_str)
                    play("I", self.q_str)
                    align(self.q_str, self.rr_str)
                    wait(self.wait_rr, self.rr_str)
                    measure(
                        "readout" * amp(a),
                        self.rr_str,
                        None,
                        demod.accumulated("integW_cos", I0, self.chunk_size_clk, self.out),
                        demod.accumulated("integW_minus_sin", Q0, self.chunk_size_clk, self.out),
                    )
                    for idx in self.integration_indices.tolist():
                        save(I0[idx], I0_st)
                        save(Q0[idx], Q0_st)

                    align(self.rr_str, self.q_str)
                    wait(self.rep_rate_clk, self.q_str)
                    play("X180", self.q_str)
                    align(self.q_str, self.rr_str)
                    wait(self.wait_rr, self.rr_str)
                    measure(
                        "readout" * amp(a),
                        self.rr_str,
                        None,
                        demod.accumulated("integW_cos", I1, self.chunk_size_clk, self.out),
                        demod.accumulated("integW_minus_sin", Q1, self.chunk_size_clk, self.out),
                    )
                    for idx in self.integration_indices.tolist(): #CHECK THIS OUT
                        save(I1[idx], I1_st)
                        save(Q1[idx], Q1_st)

            with stream_processing():
                I0_st.save_all("I0")
                Q0_st.save_all("Q0")
                I1_st.save_all("I1")
                Q1_st.save_all("Q1")

        return iq_blobs_prog

    @staticmethod
    def _reshape_raw(data: np.ndarray, n_amps: int, n_runs: int, arr_size: int):
        # Raw stream order is [amp, shot, chunk]; transpose to [amp, chunk, shot].
        return np.transpose(data.reshape(n_amps, n_runs, arr_size), (0, 2, 1))

    @staticmethod
    def _normalize_to_unit_interval(arr: np.ndarray):
        a = np.asarray(arr, dtype=float)
        lo = np.min(a)
        hi = np.max(a)
        if hi - lo < 1e-15:
            return np.ones_like(a)
        return (a - lo) / (hi - lo)

    @staticmethod
    def _point_metrics(I0: np.ndarray, Q0: np.ndarray, I1: np.ndarray, Q1: np.ndarray):
        angle, _threshold, fidelity, _gg, _ge, _eg, _ee = two_state_discriminator(
            I0,
            Q0,
            I1,
            Q1,
            b_print=False,
            b_plot=False,
        )
        z0 = (np.asarray(I0) + 1j * np.asarray(Q0)) * np.exp(1j * angle)
        z1 = (np.asarray(I1) + 1j * np.asarray(Q1)) * np.exp(1j * angle)
        x0 = z0.real
        x1 = z1.real
        mu0 = float(np.mean(x0))
        mu1 = float(np.mean(x1))
        var0 = float(np.var(x0))
        var1 = float(np.var(x1))
        sigma0 = float(np.sqrt(var0))
        sigma1 = float(np.sqrt(var1))
        dprime = abs(mu1 - mu0) / np.sqrt(0.5 * (var0 + var1) + 1e-15)
        compactness = 1.0 / (sigma0 + sigma1 + 1e-15)
        return float(fidelity), float(dprime), float(compactness)

    def _selection_score_2d_for_mode(
        self,
        mode: str,
        fidelity_2d: np.ndarray,
        dprime_2d: np.ndarray,
        compactness_2d: np.ndarray,
    ):
        mode = str(mode).lower()
        if mode == "fidelity":
            score_2d = fidelity_2d.copy()
            label = "Fidelity (%)"
        elif mode == "dprime":
            score_2d = dprime_2d.copy()
            label = "d-prime"
        else:
            wf = float(self.selection_weights.get("fidelity", 0.6))
            wd = float(self.selection_weights.get("dprime", 0.3))
            wc = float(self.selection_weights.get("compactness", 0.1))
            wsum = wf + wd + wc
            if wsum <= 0:
                wf, wd, wc = 0.6, 0.3, 0.1
                wsum = 1.0
            wf, wd, wc = wf / wsum, wd / wsum, wc / wsum
            score_2d = (
                wf * self._normalize_to_unit_interval(fidelity_2d)
                + wd * self._normalize_to_unit_interval(dprime_2d)
                + wc * self._normalize_to_unit_interval(compactness_2d)
            )
            label = "Hybrid selection score"
        return score_2d, label

    def run_experiment(self):
        if self.override_ro_amp_unity:
            self._runtime_config = self._build_runtime_config()
        else:
            cprint(f"Using ro_amp from config: {self.ro_amp}", "green")
            self._runtime_config = self.config
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        self._qm = self._qmm.open_qm(self._runtime_config)
        job = self._qm.execute(self._build_program())
        job.result_handles.wait_for_all_values()

        self._I0_raw = np.asarray(job.result_handles.get("I0").fetch_all()["value"])
        self._Q0_raw = np.asarray(job.result_handles.get("Q0").fetch_all()["value"])
        self._I1_raw = np.asarray(job.result_handles.get("I1").fetch_all()["value"])
        self._Q1_raw = np.asarray(job.result_handles.get("Q1").fetch_all()["value"])

    def analyze_and_plot(self):
        if self._I0_raw is None:
            raise RuntimeError("No data available. Run run_experiment() first.")

        n_amps = len(self.amps)
        #divide the amps by 0.4? or not?
        # self.amps = self.amps / self.runtime_ro_waveform_sample
        I0_3d = self._reshape_raw(self._I0_raw, n_amps, self.n_runs, self.arr_size)
        Q0_3d = self._reshape_raw(self._Q0_raw, n_amps, self.n_runs, self.arr_size)
        I1_3d = self._reshape_raw(self._I1_raw, n_amps, self.n_runs, self.arr_size)
        Q1_3d = self._reshape_raw(self._Q1_raw, n_amps, self.n_runs, self.arr_size)

        fidelity_2d = np.zeros((n_amps, self.arr_size), dtype=float)
        dprime_2d = np.zeros((n_amps, self.arr_size), dtype=float)
        compactness_2d = np.zeros((n_amps, self.arr_size), dtype=float)
        total_points = n_amps * self.arr_size
        pbar = None
        if self.show_progress:
            if tqdm is not None:
                pbar = tqdm(total=total_points, desc="Fidelity map", unit="pt")
            else:
                logger.info(
                    "Progress bar requested but tqdm is unavailable; "
                    "falling back to periodic logger updates."
                )

        completed = 0
        for amp_idx in range(n_amps):
            for int_idx in range(self.arr_size):
                fidelity, dprime, compactness = self._point_metrics(
                    I0_3d[amp_idx, int_idx],
                    Q0_3d[amp_idx, int_idx],
                    I1_3d[amp_idx, int_idx],
                    Q1_3d[amp_idx, int_idx],
                )
                fidelity_2d[amp_idx, int_idx] = fidelity
                dprime_2d[amp_idx, int_idx] = dprime
                compactness_2d[amp_idx, int_idx] = compactness
                completed += 1
                if pbar is not None:
                    pbar.update(1)
                elif self.show_progress and (completed % max(1, total_points // 20) == 0):
                    percent = 100.0 * completed / total_points
                    logger.info(f"Fidelity map progress: {percent:5.1f}%")

        if pbar is not None:
            pbar.close()

        self.results["sweep"] = {
            "amps": self.amps,
            "integration_lengths_clk": self.integration_lengths_clk,
            "integration_lengths_ns": self.integration_lengths_ns,
            "fidelity_2d": fidelity_2d,
            "dprime_2d": dprime_2d,
            "compactness_2d": compactness_2d,
        }
        # Fidelity envelopes used for mode-agnostic visualization helpers.
        # 1) Best fidelity at each duration (maximize over amplitudes).
        best_amp_idx_per_duration = np.argmax(fidelity_2d, axis=0)
        best_fidelity_per_duration = fidelity_2d[best_amp_idx_per_duration, np.arange(self.arr_size)]
        # 2) Best duration at each amplitude (maximize over durations).
        best_duration_idx_per_amp = np.argmax(fidelity_2d, axis=1)
        best_duration_per_amp = self.integration_lengths_clk[best_duration_idx_per_amp]
        best_fidelity_per_amp = fidelity_2d[np.arange(len(self.amps)), best_duration_idx_per_amp]
        self.results["figures"] = []
        self.results["analyses"] = {}

        for mode in self.analysis_modes:
            selection_score_2d, colorbar_label = self._selection_score_2d_for_mode(
                mode, fidelity_2d, dprime_2d, compactness_2d
            )

            best_flat_idx = int(np.argmax(selection_score_2d))
            best_amp_idx, best_int_idx = np.unravel_index(best_flat_idx, fidelity_2d.shape)
            best_amp = float(self.amps[best_amp_idx])
            best_integ_clk = int(self.integration_lengths_clk[best_int_idx])
            best_integ_ns = int(self.integration_lengths_ns[best_int_idx])
            best_fidelity = float(fidelity_2d[best_amp_idx, best_int_idx])
            best_dprime = float(dprime_2d[best_amp_idx, best_int_idx])
            best_compactness = float(compactness_2d[best_amp_idx, best_int_idx])
            best_selection_score = float(selection_score_2d[best_amp_idx, best_int_idx])

            I0_best = I0_3d[best_amp_idx, best_int_idx]
            Q0_best = Q0_3d[best_amp_idx, best_int_idx]
            I1_best = I1_3d[best_amp_idx, best_int_idx]
            Q1_best = Q1_3d[best_amp_idx, best_int_idx]

            # Keep best-point metrics from the sweep data itself.
            angle, threshold, _fid_plot, gg, ge, eg, ee = two_state_discriminator(
                I0_best, Q0_best, I1_best, Q1_best, b_print=False, b_plot=False
            )
            best_ro_len_clk = int(max(self.ro_len_clk_runtime, best_integ_clk))
            validation_result = None
            iq_blob_source = "inline_ro_len_vs_amp"
            iq_blob_path = None
            if self.validate_best_with_ro_fidelity:
                try:
                    from HM.single_qubit_experiments.ro_fidelity import (
                        validate_ro_point_with_ro_fidelity,
                    )

                    validation_exp = validate_ro_point_with_ro_fidelity(
                        q_no=self.q_no,
                        rr_no=self.rr_no,
                        ro_amp=best_amp,
                        ro_len_clk=best_ro_len_clk,
                        integ_len_clk=best_integ_clk,
                        n_runs=self.validation_n_runs,
                        rep_rate_clk=self.rep_rate_clk,
                        wait_rr=self.wait_rr,
                        save_data=self.validation_save_data,
                        save_plot=self.validation_save_plot,
                        show_plot=self.validation_show_plot,
                        query_LOs=False,
                    )
                    validation_result = {
                        "requested_point": {
                            "ro_amp": best_amp,
                            "ro_len_clk": best_ro_len_clk,
                            "integ_len_clk": best_integ_clk,
                        },
                        "analysis": validation_exp.results.get("analysis"),
                        "figures": validation_exp.results.get("figures", []),
                    }
                    if validation_result["figures"]:
                        iq_blob_path = str(validation_result["figures"][0])
                        iq_blob_source = "ro_fidelity_validation"
                        self.results["figures"].append(iq_blob_path)
                        cprint(f"Figure saved: {Path(iq_blob_path).as_uri()}", "green")
                except Exception as exc:
                    logger.exception(
                        f"[{mode}] ro_fidelity validation failed for q{self.q_no} rr{self.rr_no}: {exc}. "
                        "Falling back to inline IQ blob from ro_len_vs_amp sweep."
                    )

            if iq_blob_path is None:
                plt.figure()
                two_state_discriminator(I0_best, Q0_best, I1_best, Q1_best, b_print=True, b_plot=True)
                fig_iq = plt.gcf()
                fig_iq.subplots_adjust(bottom=0.22)
                fig_iq.text(
                    0.02,
                    0.04,
                    f"mode = {mode}\n"
                    f"q{self.q_no} rr{self.rr_no}\n"
                    f"best ro_amp = {best_amp:.4f}\n"
                    f"best integ_len = {best_integ_clk} clk ({best_integ_ns} ns)\n"
                    f"fidelity = {best_fidelity:.2f}%\n"
                    f"dprime = {best_dprime:.3f}",
                    transform=fig_iq.transFigure,
                    va="bottom",
                    ha="left",
                    fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none"),
                )
                iq_blob_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}_{mode}_best_iq_blob.png"
                plt.tight_layout()
                plt.savefig(iq_blob_path, bbox_inches="tight")
                plt.show(block=False)
                self.results["figures"].append(iq_blob_path)
                cprint(f"Figure saved: {Path(iq_blob_path).as_uri()}", "green")

            fig2, ax2 = plt.subplots(figsize=(9, 6))
            extent = [
                float(self.integration_lengths_clk[0]),
                float(self.integration_lengths_clk[-1]),
                float(self.amps[0]),
                float(self.amps[-1]),
            ]
            # Use a red/white/blue colormap and auto-scale to each map's data range.
            imshow_kwargs = {"cmap": "bwr"}
            im = ax2.imshow(
                selection_score_2d,
                aspect="auto",
                origin="lower",
                extent=extent,
                interpolation="nearest",
                **imshow_kwargs,
            )
            ax2.scatter(best_integ_clk, best_amp, marker="x", s=120, color="white", label="Best point")
            ax2.plot(
                best_duration_per_amp,
                self.amps,
                color="cyan",
                linewidth=2.0,
                alpha=0.95,
                label="Best-fidelity duration per amplitude",
            )
            ax2.set_xlabel("Integration length (clock cycles)")
            ax2.set_ylabel("Readout amplitude")
            ax2.set_title(f"Readout {mode} map (q{self.q_no}, rr{self.rr_no})")
            ax2.legend(loc="lower right")
            cbar = fig2.colorbar(im, ax=ax2)
            cbar.set_label(colorbar_label)
            heatmap_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}_{mode}_2d.png"
            fig2.tight_layout()
            fig2.savefig(heatmap_path, bbox_inches="tight")
            plt.show(block=False)
            self.results["figures"].append(heatmap_path)
            cprint(f"Figure saved: {Path(heatmap_path).as_uri()}", "green")

            fig3, ax3 = plt.subplots(figsize=(9, 5))
            ax3.plot(
                self.integration_lengths_clk,
                best_fidelity_per_duration,
                ".-",
                label="Best fidelity vs duration (max over amplitude)",
            )
            best_duration_idx = int(np.argmax(best_fidelity_per_duration))
            best_duration_for_linecut = int(self.integration_lengths_clk[best_duration_idx])
            ax3.axvline(
                best_duration_for_linecut,
                color="k",
                linestyle="--",
                label=f"Best fidelity duration = {best_duration_for_linecut} clk",
            )
            ax3.set_xlabel("Integration length (clock cycles)")
            ax3.set_ylabel("Fidelity (%)")
            ax3.set_title(f"Best-fidelity linecut (q{self.q_no}, rr{self.rr_no})")
            ax3.grid(True)
            ax3.legend()
            lineplot_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}_{mode}_linecut.png"
            fig3.tight_layout()
            fig3.savefig(lineplot_path, bbox_inches="tight")
            plt.show(block=False)
            self.results["figures"].append(lineplot_path)
            cprint(f"Figure saved: {Path(lineplot_path).as_uri()}", "green")

            mode_best_point = {
                "amp_index": int(best_amp_idx),
                "integration_index": int(best_int_idx),
                "ro_amp": best_amp,
                "integration_length_clk": best_integ_clk,
                "integration_length_ns": best_integ_ns,
                "fidelity_percent": best_fidelity,
                "dprime": best_dprime,
                "compactness": best_compactness,
                "selection_metric": mode,
                "selection_score": best_selection_score,
                "angle_rad": float(angle),
                "threshold": float(threshold),
                "best_ro_len_clk": best_ro_len_clk,
                "confusion": {
                    "gg": float(gg),
                    "ge": float(ge),
                    "eg": float(eg),
                    "ee": float(ee),
                },
            }
            self.results["analyses"][mode] = {
                "best_point": mode_best_point,
                "best_iq_blob": {
                    "I0": I0_best,
                    "Q0": Q0_best,
                    "I1": I1_best,
                    "Q1": Q1_best,
                },
                "selection_score_2d": selection_score_2d,
                "best_fidelity_per_duration": best_fidelity_per_duration,
                "best_duration_per_amp_clk": best_duration_per_amp,
                "best_fidelity_per_amp": best_fidelity_per_amp,
                "validation": validation_result,
                "figures": {
                    "best_iq_blob": iq_blob_path,
                    "best_iq_blob_source": iq_blob_source,
                    "map_2d": heatmap_path,
                    "linecut": lineplot_path,
                },
            }
            logger.info(
                f"[{mode}] Best point q{self.q_no}: amp={best_amp:.4f}, "
                f"integ={best_integ_clk} clk ({best_integ_ns} ns), "
                f"fidelity={best_fidelity:.2f}%, dprime={best_dprime:.3f}, "
                f"score={best_selection_score:.4f}"
            )

        primary_mode = self.analysis_modes[0]
        self.results["best_point"] = self.results["analyses"][primary_mode]["best_point"]
        self.results["best_iq_blob"] = self.results["analyses"][primary_mode]["best_iq_blob"]
        self.results["sweep"]["selection_score_2d"] = self.results["analyses"][primary_mode]["selection_score_2d"]

    def update_config_dicts(self):
        if "best_point" not in self.results:
            raise RuntimeError("No best point available. Run analyze_and_plot() first.")

        rr_key = str(self.rr_no)
        best_ro_amp = float(self.results["best_point"]["ro_amp"])
        best_integ_len_clk = int(self.results["best_point"]["integration_length_clk"])
        best_ro_len_clk = int(max(self.ro_len_clk_runtime, best_integ_len_clk))

        ro_amp_path = self.config_files_path + "/Readout_Settings/ro_amp.json"
        with open(ro_amp_path, "r") as fh:
            ro_amp_dict = json.load(fh)
        ro_amp_dict[rr_key] = best_ro_amp
        with open(ro_amp_path, "w") as fh:
            json.dump(ro_amp_dict, fh, indent=2)

        integ_len_path = self.config_files_path + "/Readout_Settings/integ_len_clk.json"
        with open(integ_len_path, "r") as fh:
            integ_len_dict = json.load(fh)
        integ_len_dict[rr_key] = best_integ_len_clk
        with open(integ_len_path, "w") as fh:
            json.dump(integ_len_dict, fh, indent=2)

        ro_len_path = self.config_files_path + "/Readout_Settings/ro_len_clk.json"
        with open(ro_len_path, "r") as fh:
            ro_len_dict = json.load(fh)
        ro_len_dict[rr_key] = best_ro_len_clk
        with open(ro_len_path, "w") as fh:
            json.dump(ro_len_dict, fh, indent=2)

        self.results["updated_config"] = {
            "ro_amp": {"path": ro_amp_path, "value": best_ro_amp},
            "integ_len_clk": {"path": integ_len_path, "value": best_integ_len_clk},
            "ro_len_clk": {"path": ro_len_path, "value": best_ro_len_clk},
        }
        logger.info(
            f"Updated readout config for rr{rr_key}: "
            f"ro_amp={best_ro_amp:.4f}, integ_len_clk={best_integ_len_clk}, ro_len_clk={best_ro_len_clk}"
        )

    def save_experiment_data(self):
        json_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}.json"
        save_json(self.results, json_path)
        cprint(f"Data saved: {Path(json_path).as_uri()}", "green")
        return json_path

    def run(self):
        t0 = time.time()
        try:
            self.run_experiment()
            self.analyze_and_plot()
            if self.update_config:
                if len(self.analysis_modes) > 1:
                    self.results["update_config_skipped"] = (
                        "Skipped because multiple analysis modes were requested "
                        "(debug workflow)."
                    )
                    logger.info(self.results["update_config_skipped"])
                else:
                    self.update_config_dicts()
            if self.save_data:
                self.save_experiment_data()
        finally:
            if self._qm is not None:
                try:
                    self._qm.close()
                except Exception:
                    pass
            if self._qmm is not None:
                try:
                    self._qmm.close()
                except Exception:
                    pass
        elapsed = time.time() - t0
        logger.info(f"Total time: {int(elapsed // 60)}m {elapsed % 60:.1f}s")
        return self.results


def perform_ro_len_vs_amp(q_no: int, rr_no: int = None, **kwargs):
    exp = RoLenVsAmpCalibration(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


def recreate_ro_len_vs_amp_plots_from_json(
    json_path: str,
    save_plots: bool = True,
    show_plots: bool = True,
    output_dir: str = None,
):
    """
    Recreate ro_len_vs_amp figures from a saved experiment JSON file.

    Parameters
    ----------
    json_path : str
        Path to JSON file saved by RoLenVsAmpCalibration.
    save_plots : bool
        Save recreated figures to disk.
    show_plots : bool
        Display figures using matplotlib.
    output_dir : str
        Optional directory to save figures. Defaults to JSON's directory.

    Returns
    -------
    dict
        {"figures": [<paths>], "best_point": {...}}
    """
    json_file = Path(json_path)
    with open(json_file, "r") as fh:
        data = json.load(fh)

    q_no = int(data["q_no"])
    rr_no = int(data["rr_no"])

    amps = np.asarray(data["sweep"]["amps"], dtype=float)
    integration_lengths_clk = np.asarray(data["sweep"]["integration_lengths_clk"], dtype=float)
    integration_lengths_ns = np.asarray(data["sweep"]["integration_lengths_ns"], dtype=float)
    fidelity_2d = np.asarray(data["sweep"]["fidelity_2d"], dtype=float)

    best = data.get("best_point", {})
    best_amp = float(best.get("ro_amp", best.get("amp_multiplier")))
    best_integ_clk = float(best["integration_length_clk"])
    best_integ_ns = float(best.get("integration_length_ns", best_integ_clk * 4))
    best_fidelity = float(best["fidelity_percent"])

    save_dir = Path(output_dir) if output_dir is not None else json_file.parent
    save_dir.mkdir(parents=True, exist_ok=True)
    stem = json_file.stem
    saved_paths = []

    # Recreate 2D fidelity heatmap.
    fig2, ax2 = plt.subplots(figsize=(9, 6))
    extent = [
        float(integration_lengths_clk[0]),
        float(integration_lengths_clk[-1]),
        float(amps[0]),
        float(amps[-1]),
    ]
    im = ax2.imshow(
        fidelity_2d,
        aspect="auto",
        origin="lower",
        extent=extent,
        interpolation="nearest",
    )
    ax2.scatter(best_integ_clk, best_amp, marker="x", s=120, color="white", label="Best point")
    ax2.set_xlabel("Integration length (clock cycles)")
    ax2.set_ylabel("Readout amplitude")
    ax2.set_title(f"Readout fidelity 2D sweep (q{q_no}, rr{rr_no})")
    ax2.legend(loc="lower right")
    cbar = fig2.colorbar(im, ax=ax2)
    cbar.set_label("Fidelity (%)")
    if save_plots:
        heatmap_path = save_dir / f"{stem}_fidelity_2d_replot.png"
        fig2.tight_layout()
        fig2.savefig(str(heatmap_path), bbox_inches="tight")
        saved_paths.append(str(heatmap_path))
    if show_plots:
        plt.show(block=False)

    # Recreate linecut at best amp.
    best_amp_idx = int(np.argmin(np.abs(amps - best_amp)))
    fig3, ax3 = plt.subplots(figsize=(9, 5))
    ax3.plot(integration_lengths_clk, fidelity_2d[best_amp_idx], ".-")
    ax3.axvline(best_integ_clk, color="k", linestyle="--", label=f"Best = {best_integ_clk:.0f} clk")
    ax3.set_xlabel("Integration length (clock cycles)")
    ax3.set_ylabel("Fidelity (%)")
    ax3.set_title(
        f"Fidelity vs integration length at best amp={best_amp:.4f} "
        f"(q{q_no}, rr{rr_no})"
    )
    ax3.grid(True)
    ax3.legend()
    if save_plots:
        linecut_path = save_dir / f"{stem}_best_amp_linecut_replot.png"
        fig3.tight_layout()
        fig3.savefig(str(linecut_path), bbox_inches="tight")
        saved_paths.append(str(linecut_path))
    if show_plots:
        plt.show(block=False)

    # Recreate best IQ blob.
    iq_data = data["best_iq_blob"]
    I0_best = np.asarray(iq_data["I0"], dtype=float)
    Q0_best = np.asarray(iq_data["Q0"], dtype=float)
    I1_best = np.asarray(iq_data["I1"], dtype=float)
    Q1_best = np.asarray(iq_data["Q1"], dtype=float)
    plt.figure()
    two_state_discriminator(
        I0_best,
        Q0_best,
        I1_best,
        Q1_best,
        b_print=True,
        b_plot=True,
    )
    fig_iq = plt.gcf()
    fig_iq.subplots_adjust(bottom=0.22)
    fig_iq.text(
        0.02,
        0.04,
        f"q{q_no} rr{rr_no}\n"
        f"best ro_amp = {best_amp:.4f}\n"
        f"best integ_len = {best_integ_clk:.0f} clk ({best_integ_ns:.0f} ns)\n"
        f"fidelity = {best_fidelity:.2f}%",
        transform=fig_iq.transFigure,
        va="bottom",
        ha="left",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none"),
    )
    if save_plots:
        blob_path = save_dir / f"{stem}_best_iq_blob_replot.png"
        plt.tight_layout()
        plt.savefig(str(blob_path), bbox_inches="tight")
        saved_paths.append(str(blob_path))
    if show_plots:
        plt.show(block=False)

    return {
        "figures": saved_paths,
        "best_point": {
            "ro_amp": best_amp,
            "integration_length_clk": best_integ_clk,
            "integration_length_ns": best_integ_ns,
            "fidelity_percent": best_fidelity,
        },
    }


if __name__ == "__main__":
    #if you don't want to use tstart tstop, then just don't pass it. 
    #the code will default to the eariler form of execution
    selection_weights = {
        "fidelity": 0.5, #raw fidelity calculated by the two state discriminator
        "dprime": 0.25, # the distance between the mean of the two states in the I axis
        "compactness": 0.25, #the sigma in the I axis and the Q axis contributes to the compactness
    }
    analysis_modes = ["fidelity", "dprime", "hybrid"]
    chunk_size_clk = 25
    t_array_clk = np.arange(50, 500, chunk_size_clk).astype(int)
    qubit_list = [
        1,
        # 2,
        # 3,
        4,
        # 5,
        # 6,
    ]
    for qubit in qubit_list:
        perform_ro_len_vs_amp(
            q_no=qubit,
            n_runs=10_000,
            a_min=0.005,
            a_max=1,
            da=0.005,
            chunk_size_clk=chunk_size_clk,
            save_data=True,
            selection_weights=selection_weights,
            t_array_clk=t_array_clk,
            analysis_modes=analysis_modes,
            # update_config=True,
        )
