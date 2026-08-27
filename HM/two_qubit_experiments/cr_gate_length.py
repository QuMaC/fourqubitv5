import json
import logging
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from qm import QuantumMachinesManager

from Configuration_Files.config_dictionaries import cr_amp, cr_len_ns, cr_phase
from Helper_Functions.CR_fitters import fit_cos
from HM.two_qubit_experiments.cr_calibration_common import (
    INT_STRENGTH_LABELS,
    analyze_cr_tomography,
    collect_cr_tomography,
    round_to_multiple,
    save_rabi_fit_plot,
    split_control_traces,
)
from HM.two_qubit_experiments.two_qubit_base import TwoQubitExperiment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class CRGateLengthCalibration(TwoQubitExperiment):
    """
    HM-style no-AC echoed CR gate-length calibration.

    This calibrates the length consumed by ``ZXby2_echo_noAC`` and therefore by
    ``CNOT_macro(..., AC_flg=False)``.
    """

    def __init__(self, q_list: List[int], **kwargs):
        super().__init__(q_list=q_list, expt_name="cr_gate_length", **kwargs)
        self.simulate = bool(kwargs.get("simulate", False))
        self.save_data = bool(kwargs.get("save_data", True))
        self.save_plot = bool(kwargs.get("save_plot", True))
        self.show_plot = bool(kwargs.get("show_plot", True))
        self.plot_live = bool(kwargs.get("plot_live", True))
        self.plot_rabi = bool(kwargs.get("plot_rabi", False))
        self.update_calib = bool(kwargs.get("update_calib", False))
        self.max_len_update_fraction = float(kwargs.get("max_len_update_fraction", 1.0))
        self.save_traces = bool(kwargs.get("save_traces", True))

        self.pi_12 = bool(kwargs.get("pi_12", True))
        self.echo_p = bool(kwargs.get("echo_p", True))
        self.t_min_ns = int(kwargs.get("t_min_ns", 16))
        self.t_max_ns = int(kwargs.get("t_max_ns", 1000))
        self.dt_ns = int(kwargs.get("dt_ns", 4))
        self.round_step_ns = int(kwargs.get("round_step_ns", 8))
        self.search_fraction = float(kwargs.get("search_fraction", 0.5))
        self.fit_points = int(kwargs.get("fit_points", 10_000))
        self.wait_init = int(kwargs.get("wait_init", 250_000))
        self.wait_t = int(kwargs.get("wait_t", 4))
        self.wait_rr = int(kwargs.get("wait_rr", 16))
        self.n_avg = int(kwargs.get("n_avg", 200))
        self.snr_halt_threshold = float(kwargs.get("snr_halt_threshold", 80.0))

        self.phase = float(kwargs.get("phase", cr_phase[self.cr_elem]))
        self.amplitude = float(kwargs.get("amplitude", cr_amp[self.cr_elem]))
        self.current_len_ns = float(kwargs.get("current_len_ns", cr_len_ns[self.cr_elem]))

        self.t_min = int(self.t_min_ns / 4)
        self.t_max = int(self.t_max_ns / 4)
        self.dt = int(self.dt_ns / 4)
        self.t_list = np.arange(self.t_min, self.t_max, self.dt)
        self.t_list_ns = 2 * 4 * self.t_list
        self._qmm = None

        self.results = {
            "control_q": self.q_control_no,
            "target_q": self.q_target_no,
            "cr_elem": self.cr_elem,
            "params": {
                "phase": self.phase,
                "amplitude": self.amplitude,
                "current_len_ns": self.current_len_ns,
                "echo_p": self.echo_p,
                "pi_12": self.pi_12,
                "t_min_ns": self.t_min_ns,
                "t_max_ns": self.t_max_ns,
                "dt_ns": self.dt_ns,
                "round_step_ns": self.round_step_ns,
                "search_fraction": self.search_fraction,
                "fit_points": self.fit_points,
                "wait_init": self.wait_init,
                "wait_t": self.wait_t,
                "wait_rr": self.wait_rr,
                "n_avg": self.n_avg,
                "simulate": self.simulate,
            },
            "summary": {},
            "raw": {},
            "artifacts": [],
        }

    def _fit_gate_length(self, time_ns, cdata):
        y0 = np.asarray(cdata[1][0], dtype=float)
        y1 = np.asarray(cdata[1][1], dtype=float)
        fit0 = fit_cos(time_ns, y0)
        fit1 = fit_cos(time_ns, y1)
        fine_time = np.linspace(float(time_ns[0]), float(time_ns[-1]), self.fit_points)
        fit_y0 = fit0["fitfunc"](fine_time)
        fit_y1 = fit1["fitfunc"](fine_time)

        max_idx = max(1, int(len(fine_time) * self.search_fraction))
        sep = np.abs(fit_y1[:max_idx] - fit_y0[:max_idx])
        raw_gate_len_ns = float(np.round(fine_time[int(np.argmax(sep))], 2))
        rounded_gate_len_ns = float(np.round(round_to_multiple(raw_gate_len_ns, self.round_step_ns), 2))

        return {
            "raw_gate_len_ns": raw_gate_len_ns,
            "rounded_gate_len_ns": rounded_gate_len_ns,
            "fine_time_ns": fine_time,
            "fit_y0": fit_y0,
            "fit_y1": fit_y1,
            "fit0": {k: v for k, v in fit0.items() if k not in ("fitfunc", "rawres")},
            "fit1": {k: v for k, v in fit1.items() if k not in ("fitfunc", "rawres")},
        }

    def _save_gate_length_plot(self, analysis, gate_fit):
        cdata = analysis["cdata"]
        time_ns = analysis["time_ns"]
        colors = ["red", "blue", "green"]
        labels = ["Z", "Y", "X"]

        fig, ax = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
        for i in range(3):
            ax[0].plot(time_ns, cdata[i][0], ".", color=colors[i], label=f"{labels[i]} data")
            ax[1].plot(time_ns, cdata[i][1], ".", color=colors[i], label=f"{labels[i]} data")
        ax[0].plot(gate_fit["fine_time_ns"], gate_fit["fit_y0"], color="blue", linewidth=2.0, label="Y fit")
        ax[1].plot(gate_fit["fine_time_ns"], gate_fit["fit_y1"], color="blue", linewidth=2.0, label="Y fit")
        for axis, control_state in zip(ax, [0, 1]):
            axis.axvline(gate_fit["raw_gate_len_ns"], color="black", linestyle="--", label="selected raw")
            axis.axvline(gate_fit["rounded_gate_len_ns"], color="magenta", linestyle=":", label="rounded")
            axis.set_title(f"Control {control_state}")
            axis.set_xlabel("Time (ns)")
            axis.set_ylabel("Expectation value")
            axis.set_ylim(-1.1, 1.1)
            axis.grid(True)
            axis.legend(loc="best")
        fig.suptitle(
            f"No-AC echoed CR gate length q{self.q_control_no}->q{self.q_target_no}: "
            f"{gate_fit['rounded_gate_len_ns']:.0f} ns"
        )
        fig.tight_layout()

        if self.save_plot:
            fig_path = str(self.path_to_save) + f"_q{self.q_control_no}_q{self.q_target_no}_gate_length.png"
            fig.savefig(fig_path, bbox_inches="tight")
            self.results["artifacts"].append(fig_path)
        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

    def _update_calibration_file(self, gate_len_ns):
        len_path = self.config_files_path + "/Pulse_Calibrations/cr_len_ns.json"
        with open(len_path, "r") as fptr:
            len_dict = json.load(fptr)
        old_val = float(len_dict[self.cr_elem])
        new_val = float(gate_len_ns)
        abs_diff = abs(new_val - old_val)
        rel_diff = abs_diff / max(abs(old_val), 1e-12)
        update_fail_flag = bool(rel_diff > self.max_len_update_fraction)
        applied = not update_fail_flag
        if applied:
            len_dict[self.cr_elem] = int(round(new_val))
            with open(len_path, "w") as fptr:
                json.dump(len_dict, fptr, indent=2)

        self.results["summary"]["calibration_update"] = {
            "path": len_path,
            "key": self.cr_elem,
            "old_len_ns": old_val,
            "new_len_ns": new_val,
            "abs_len_diff_ns": abs_diff,
            "relative_len_diff": rel_diff,
            "max_len_update_fraction": self.max_len_update_fraction,
            "update_fail_flag": update_fail_flag,
            "applied": applied,
        }
        if update_fail_flag:
            logger.warning(
                "CR length update blocked for %s: old=%.2f ns new=%.2f ns rel_diff=%.6f",
                self.cr_elem,
                old_val,
                new_val,
                rel_diff,
            )

    def run(self):
        if self.refresh_qm_config:
            self.refresh_qm_config_from_disk()
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)

        try:
            logger.info("Running no-AC echoed CR gate-length calibration for %s", self.cr_elem)
            I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg = collect_cr_tomography(
                self,
                self._qmm,
                self.phase,
                self.amplitude,
                self.echo_p,
                title=f"No-AC echoed CR gate length {self.cr_elem}",
            )
            analysis = analyze_cr_tomography(self.t_list_ns, I_t_avg, I_rabi_avg)
            gate_fit = self._fit_gate_length(self.t_list_ns, analysis["cdata"])
            save_rabi_fit_plot(self, analysis, suffix="gate_length")
            self._save_gate_length_plot(analysis, gate_fit)

            Ic0, Ic1 = split_control_traces(I_c_avg, len(self.t_list))
            Qc0, Qc1 = split_control_traces(Q_c_avg, len(self.t_list))
            self.results["summary"] = {
                "gate_len_ns": gate_fit["rounded_gate_len_ns"],
                "raw_gate_len_ns": gate_fit["raw_gate_len_ns"],
                "current_len_ns": self.current_len_ns,
                "phase_used": self.phase,
                "amp_used": self.amplitude,
                "int_strength_labels": INT_STRENGTH_LABELS,
                "int_strengths_mhz": analysis["int_strengths_mhz"],
                "str_phase_correction": analysis["str_phase_correction"],
                "str_ac_phase_correction": analysis["str_ac_phase_correction"],
            }
            if self.save_traces:
                self.results["raw"] = {
                    "time_ns": self.t_list_ns.copy(),
                    "I_t_avg": I_t_avg,
                    "Q_t_avg": Q_t_avg,
                    "I_c0": Ic0,
                    "Q_c0": Qc0,
                    "I_c1": Ic1,
                    "Q_c1": Qc1,
                    "I_rabi_avg": I_rabi_avg,
                    "Q_rabi_avg": Q_rabi_avg,
                    "normalized_tomography": analysis["cdata"],
                    "gate_fit": {
                        "fine_time_ns": gate_fit["fine_time_ns"],
                        "fit_y0": gate_fit["fit_y0"],
                        "fit_y1": gate_fit["fit_y1"],
                    },
                }

            if self.update_calib:
                self._update_calibration_file(gate_fit["rounded_gate_len_ns"])
            if self.save_data:
                data_path = str(self.path_to_save) + f"_q{self.q_control_no}_q{self.q_target_no}.json"
                self.save_json(self.results, data_path)
                self.results["artifacts"].append(data_path)
            return self.results
        finally:
            if self._qmm is not None:
                try:
                    self._qmm.close()
                except Exception:
                    pass


def perform_cr_gate_length_calibration(control_qubit: int, target_qubit: int, **kwargs) -> CRGateLengthCalibration:
    exp = CRGateLengthCalibration(q_list=[control_qubit, target_qubit], **kwargs)
    exp.run()
    return exp


def perform_cr_gate_length_calibration_for_pairs(
    pair_list: Iterable[Tuple[int, int]],
    **kwargs,
) -> Dict[str, CRGateLengthCalibration]:
    out = {}
    for control_qubit, target_qubit in pair_list:
        key = f"q{control_qubit}_q{target_qubit}"
        out[key] = perform_cr_gate_length_calibration(control_qubit, target_qubit, **kwargs)
    return out


if __name__ == "__main__":
    perform_cr_gate_length_calibration(
        control_qubit=1,
        target_qubit=4,
        save_data=True,
        save_plot=True,
        show_plot=True,
        update_calib=False,
        simulate=False,
    )

