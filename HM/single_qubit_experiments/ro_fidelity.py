import json
import logging
import time
import warnings
from copy import deepcopy
from pathlib import Path

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
from qm import QuantumMachinesManager
from qm.qua import (
    align,
    declare,
    declare_stream,
    demod,
    fixed,
    for_,
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class ReadoutFidelityCalibration(SingleQubitExperiment):
    """
    Single-point readout fidelity calibration using two-state IQ blobs.

    The experiment acquires |g> and |e> clouds, extracts a linear discriminator
    from `two_state_discriminator`, optionally updates config dictionaries, and
    saves both plot and data.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="ro_fidelity",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )
        self.n_runs = int(kwargs.get("n_runs", 10_000))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250_000))
        self.wait_rr = int(kwargs.get("wait_rr", 16))
        self.update_config = bool(kwargs.get("update_config", True))
        self.save_data = bool(kwargs.get("save_data", True))
        self.show_plot = bool(kwargs.get("show_plot", True))
        self.save_plot = bool(kwargs.get("save_plot", True))
        # Optional runtime overrides used for validation workflows.
        # These override the opened QM config only for this run.
        self.runtime_ro_amp = kwargs.get("runtime_ro_amp", None)
        self.runtime_ro_len_clk = kwargs.get("runtime_ro_len_clk", None)
        self.runtime_integ_len_clk = kwargs.get("runtime_integ_len_clk", None)

        self._qmm = None
        self._qm = None
        self._runtime_config = None
        self._I0 = None
        self._Q0 = None
        self._I1 = None
        self._Q1 = None

        self.results = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "params": {
                "n_runs": self.n_runs,
                "rep_rate_clk": self.rep_rate_clk,
                "wait_rr": self.wait_rr,
                "update_config": self.update_config,
                "save_data": self.save_data,
                "runtime_ro_amp": self.runtime_ro_amp,
                "runtime_ro_len_clk": self.runtime_ro_len_clk,
                "runtime_integ_len_clk": self.runtime_integ_len_clk,
            },
            "figures": [],
        }

    def _build_runtime_config(self):
        cfg = deepcopy(self.config)
        rr_key = str(self.rr_no)
        ro_pulse_name = cfg["elements"][self.rr_str]["operations"]["readout"]
        ro_wf_name = cfg["pulses"][ro_pulse_name]["waveforms"]["I"]
        target_ro_len_ns = int(cfg["pulses"][ro_pulse_name]["length"])

        if self.runtime_ro_len_clk is not None:
            target_ro_len_ns = int(self.runtime_ro_len_clk * self.clock_cycle_dur_ns)
            cfg["pulses"][ro_pulse_name]["length"] = target_ro_len_ns

        # Keep waveform length synchronized with pulse length for arbitrary waveforms.
        if (self.runtime_ro_amp is not None) or (self.runtime_ro_len_clk is not None):
            wf_obj = cfg["waveforms"][ro_wf_name]
            target_amp = float(self.runtime_ro_amp) if self.runtime_ro_amp is not None else None
            if wf_obj.get("type") == "constant":
                if target_amp is not None:
                    wf_obj["sample"] = target_amp
            elif "samples" in wf_obj:
                raw_samples = wf_obj.get("samples", [])
                real_samples = []
                imag_max = 0.0
                for x in raw_samples:
                    cx = complex(x)
                    imag_max = max(imag_max, abs(cx.imag))
                    real_samples.append(float(cx.real))
                if imag_max > 1e-10:
                    warnings.warn(
                        f"Readout waveform '{ro_wf_name}' has non-negligible imaginary parts; "
                        "using real part for runtime override."
                    )

                if target_amp is not None:
                    base_amp = float(self.ro_amp) if abs(float(self.ro_amp)) > 1e-15 else None
                    if base_amp is None:
                        max_abs = max((abs(x) for x in real_samples), default=0.0)
                        ratio = 0.0 if max_abs < 1e-15 else target_amp / max_abs
                    else:
                        ratio = target_amp / base_amp
                    real_samples = [x * ratio for x in real_samples]

                n_target = max(1, int(target_ro_len_ns))
                n_current = len(real_samples)
                if n_current == 0:
                    fill_val = 0.0 if target_amp is None else target_amp
                    real_samples = [fill_val] * n_target
                elif n_current != n_target:
                    # Resample to the required ns length to satisfy QM pulse/waveform consistency.
                    x_old = np.linspace(0.0, 1.0, n_current)
                    x_new = np.linspace(0.0, 1.0, n_target)
                    real_samples = np.interp(x_new, x_old, real_samples).tolist()

                wf_obj["samples"] = [float(x) for x in real_samples]
            else:
                # Unknown waveform schema: enforce a simple constant waveform.
                cfg["waveforms"][ro_wf_name] = {
                    "type": "constant",
                    "sample": float(self.ro_amp if target_amp is None else target_amp),
                }

        if self.runtime_integ_len_clk is not None:
            target_len_ns = int(self.runtime_integ_len_clk * self.clock_cycle_dur_ns)
            for weight_name in (
                f"integW_cos_rr{rr_key}",
                f"integW_sin_rr{rr_key}",
                f"integW_minus_sin_rr{rr_key}",
            ):
                if weight_name not in cfg.get("integration_weights", {}):
                    continue
                for quad in ("cosine", "sine"):
                    old_coeff, _old_len = cfg["integration_weights"][weight_name][quad][0]
                    cfg["integration_weights"][weight_name][quad] = [(float(np.real(old_coeff)), target_len_ns)]
        return cfg

    def _build_program(self):
        with program() as iq_blobs_prog:
            n = declare(int)
            I0 = declare(fixed)
            Q0 = declare(fixed)
            I1 = declare(fixed)
            Q1 = declare(fixed)
            I0_st = declare_stream()
            Q0_st = declare_stream()
            I1_st = declare_stream()
            Q1_st = declare_stream()

            with for_(n, 0, n < self.n_runs, n + 1):
                wait(self.rep_rate_clk, self.q_str)
                play("I", self.q_str)
                align(self.q_str, self.rr_str)
                wait(self.wait_rr, self.rr_str)
                measure(
                    "readout",
                    self.rr_str,
                    None,
                    demod.full("integW_cos", I0, self.out),
                    demod.full("integW_minus_sin", Q0, self.out),
                )
                save(I0, I0_st)
                save(Q0, Q0_st)

                align(self.rr_str, self.q_str)
                wait(self.rep_rate_clk, self.q_str)
                play("X180", self.q_str)
                align(self.q_str, self.rr_str)
                wait(self.wait_rr, self.rr_str)
                measure(
                    "readout",
                    self.rr_str,
                    None,
                    demod.full("integW_cos", I1, self.out),
                    demod.full("integW_minus_sin", Q1, self.out),
                )
                save(I1, I1_st)
                save(Q1, Q1_st)

            with stream_processing():
                I0_st.save_all("I0")
                Q0_st.save_all("Q0")
                I1_st.save_all("I1")
                Q1_st.save_all("Q1")

        return iq_blobs_prog

    def run_experiment(self):
        self._runtime_config = self._build_runtime_config()
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        self._qm = self._qmm.open_qm(self._runtime_config)
        job = self._qm.execute(self._build_program())
        job.result_handles.wait_for_all_values()

        self._I0 = np.asarray(job.result_handles.get("I0").fetch_all()["value"])
        self._Q0 = np.asarray(job.result_handles.get("Q0").fetch_all()["value"])
        self._I1 = np.asarray(job.result_handles.get("I1").fetch_all()["value"])
        self._Q1 = np.asarray(job.result_handles.get("Q1").fetch_all()["value"])

    @staticmethod
    def _line_discriminator_from_rotation(angle_rad: float, threshold: float):
        cos_a = float(np.cos(angle_rad))
        sin_a = float(np.sin(angle_rad))
        # Re[(I + iQ)e^{i*angle}] > threshold
        # <=> I*cos(angle) - Q*sin(angle) > threshold
        # <=> Q < (cos/sin) * I - threshold/sin for sin != 0
        if abs(sin_a) < 1e-12:
            return {
                "form": "vertical",
                "x_threshold": float(threshold / cos_a if abs(cos_a) > 1e-12 else np.nan),
            }
        return {
            "form": "slope_intercept",
            "slope": float(cos_a / sin_a),
            "intercept": float(-threshold / sin_a),
            "inequality": "Q < slope * I + intercept",
        }

    def analyze_and_plot(self):
        if self._I0 is None:
            raise RuntimeError("No data available. Run run_experiment() first.")

        angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(
            self._I0,
            self._Q0,
            self._I1,
            self._Q1,
            b_print=True,
            b_plot=True,
        )
        fig = plt.gcf()
        fig.subplots_adjust(bottom=0.20)
        fig.text(
            0.02,
            0.04,
            f"q{self.q_no} rr{self.rr_no}\n"
            f"fidelity = {fidelity:.2f}%\n"
            f"threshold = {threshold:.6g}\n"
            f"ro amp = {self.ro_amp:.6g}\n"
            f"ro len = {self.ro_len} clk\n"
            f"integ len = {self.integ_len} clk",
            transform=fig.transFigure,
            va="bottom",
            ha="left",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none"),
        )

        if self.save_plot:
            fig_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}_iq_blob.png"
            plt.tight_layout()
            plt.savefig(fig_path, bbox_inches="tight")
            self.results["figures"].append(fig_path)
            cprint(f"Figure saved: {Path(fig_path).as_uri()}", "green")

        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

        line = self._line_discriminator_from_rotation(float(angle), float(threshold))
        self.results["analysis"] = {
            "fidelity_percent": float(fidelity),
            "angle_rad": float(angle),
            "angle_deg": float(np.degrees(angle)),
            "threshold": float(threshold),
            "line_discriminator": line,
            "confusion": {
                "gg": float(gg),
                "ge": float(ge),
                "eg": float(eg),
                "ee": float(ee),
            },
        }
        self.results["iq_blob"] = {
            "I0": self._I0,
            "Q0": self._Q0,
            "I1": self._I1,
            "Q1": self._Q1,
        }
        logger.info(
            f"RO fidelity q{self.q_no} rr{self.rr_no}: "
            f"fidelity={float(fidelity):.2f}% threshold={float(threshold):.6g} "
            f"angle={float(np.degrees(angle)):.3f} deg"
        )

    def update_config_dicts(self):
        if "analysis" not in self.results:
            raise RuntimeError("No analysis available. Run analyze_and_plot() first.")

        rr_key = str(self.rr_no)
        rr_phase_key = f"rr{self.rr_no}"
        angle_deg = float(self.results["analysis"]["angle_deg"])
        threshold = float(self.results["analysis"]["threshold"])

        phase_path = self.config_files_path + "/Readout_Settings/optimal_readout_phase.json"
        with open(phase_path, "r") as fh:
            phase_dict = json.load(fh)
        current_phase_deg = float(phase_dict[rr_phase_key])
        updated_phase_deg = float(np.round((current_phase_deg - angle_deg) % 360.0, 3))
        phase_dict[rr_phase_key] = updated_phase_deg
        with open(phase_path, "w") as fh:
            json.dump(phase_dict, fh, indent=2)

        demarcations_path = self.config_files_path + "/Readout_Settings/demarcations.json"
        with open(demarcations_path, "r") as fh:
            demarcations = json.load(fh)
        demarcations[rr_key] = threshold
        with open(demarcations_path, "w") as fh:
            json.dump(demarcations, fh, indent=2)

        self.results["updated_config"] = {
            "optimal_readout_phase": {
                "path": phase_path,
                "key": rr_phase_key,
                "old_deg": current_phase_deg,
                "new_deg": updated_phase_deg,
            },
            "demarcations": {
                "path": demarcations_path,
                "key": rr_key,
                "new_threshold": threshold,
            },
        }
        logger.info(
            f"Updated readout config for rr{rr_key}: "
            f"phase {current_phase_deg:.3f} -> {updated_phase_deg:.3f} deg, "
            f"demarcation={threshold:.6g}"
        )

    def save_experiment_data(self):
        json_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}.json"
        save_json(self.results, json_path)
        cprint(f"Data saved: {Path(json_path).as_uri()}", "green")
        return json_path

    def run(self):
        t0 = time.time()
        try:
            if self.refresh_qm_config:
                self.refresh_qm_config_from_disk()
            self.run_experiment()
            self.analyze_and_plot()
            if self.update_config:
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


def perform_ro_fidelity(q_no: int, rr_no: int = None, **kwargs):
    exp = ReadoutFidelityCalibration(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


def validate_ro_point_with_ro_fidelity(
    q_no: int,
    rr_no: int = None,
    *,
    ro_amp: float = None,
    ro_len_clk: int = None,
    integ_len_clk: int = None,
    n_runs: int = 10_000,
    rep_rate_clk: int = 250_000,
    wait_rr: int = 16,
    save_data: bool = True,
    save_plot: bool = True,
    show_plot: bool = True,
    query_LOs: bool = False,
):
    """
    Validate a chosen readout point using the standard ro_fidelity workflow.

    This helper is intended for cross-checking points selected by other scripts
    (for example ro_len_vs_amp) without mutating calibration dictionaries.
    """
    exp = ReadoutFidelityCalibration(
        q_no=q_no,
        rr_no=rr_no,
        n_runs=n_runs,
        rep_rate_clk=rep_rate_clk,
        wait_rr=wait_rr,
        update_config=False,
        save_data=save_data,
        save_plot=save_plot,
        show_plot=show_plot,
        query_LOs=query_LOs,
        runtime_ro_amp=ro_amp,
        runtime_ro_len_clk=ro_len_clk,
        runtime_integ_len_clk=integ_len_clk,
    )
    exp.run()
    return exp


if __name__ == "__main__":
    qubit_list = [
        1,
        # 2,
        # 3,
        # 4,
        # 5,
        # 6,
    ]
    for qubit in qubit_list:
        perform_ro_fidelity(
            q_no=qubit,
            n_runs=5000,
            save_data=True,
            update_config=True,
        )
