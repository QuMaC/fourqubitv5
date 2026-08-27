import json
import logging
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from qm import QuantumMachinesManager

from Configuration_Files.config_dictionaries import cr_amp, cr_phase
from HM.two_qubit_experiments.cr_calibration_common import (
    INT_STRENGTH_LABELS,
    analyze_cr_tomography,
    collect_cr_tomography,
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


class CRAmplitudeSweep(TwoQubitExperiment):
    """
    HM-style no-AC CR amplitude sweep using Hamiltonian tomography.

    The sweep reports Hamiltonian strengths versus CR amplitude. It does not write
    ``cr_amp.json`` unless ``update_calib=True`` and an amplitude is selected.
    """

    def __init__(self, q_list: List[int], **kwargs):
        super().__init__(q_list=q_list, expt_name="cr_amp_sweep", **kwargs)
        self.simulate = bool(kwargs.get("simulate", False))
        self.save_data = bool(kwargs.get("save_data", True))
        self.save_plot = bool(kwargs.get("save_plot", True))
        self.show_plot = bool(kwargs.get("show_plot", True))
        self.plot_live = bool(kwargs.get("plot_live", True))
        self.save_live_plot = bool(kwargs.get("save_live_plot", True))
        self.plot_local = bool(kwargs.get("plot_local", True))
        self.plot_rabi = bool(kwargs.get("plot_rabi", False))
        self.update_calib = bool(kwargs.get("update_calib", False))
        self.auto_select = bool(kwargs.get("auto_select", False))
        self.target_zx_mhz = kwargs.get("target_zx_mhz", None)
        self.selected_amp = kwargs.get("selected_amp", None)
        self.max_amp_update_fraction = float(kwargs.get("max_amp_update_fraction", 1.0))
        self.save_traces = bool(kwargs.get("save_traces", True))
        plot_formats = kwargs.get("plot_formats", ("svg",))
        if isinstance(plot_formats, str):
            plot_formats = (plot_formats,)
        self.plot_formats = tuple(str(fmt).lstrip(".") for fmt in plot_formats)
        self.fit_max_cycles = kwargs.get("fit_max_cycles", "auto")
        self.fit_max_cycles_at_max_amp = float(kwargs.get("fit_max_cycles_at_max_amp", 4.0))
        self.fit_min_cycles = float(kwargs.get("fit_min_cycles", 1.0))
        self.fit_initial_state_weight = float(kwargs.get("fit_initial_state_weight", 0.0))
        self.fit_affine_output = bool(kwargs.get("fit_affine_output", True))

        self.pi_12 = bool(kwargs.get("pi_12", True))
        self.echo_p = bool(kwargs.get("echo_p", False))
        self.t_min_ns = int(kwargs.get("t_min_ns", 4))
        self.t_max_ns = int(kwargs.get("t_max_ns", 1000))
        self.dt_ns = int(kwargs.get("dt_ns", 4))
        self.wait_init = int(kwargs.get("wait_init", 250_000))
        self.wait_t = int(kwargs.get("wait_t", 4))
        self.wait_rr = int(kwargs.get("wait_rr", 16))
        self.n_avg = int(kwargs.get("n_avg", 200))
        self.snr_halt_threshold = float(kwargs.get("snr_halt_threshold", 80.0))

        amp_list = kwargs.get("amp_list", None)
        self.amp_list = np.array(amp_list if amp_list is not None else np.linspace(0.05, 0.8, 10), dtype=float)
        self.initial_phase = float(kwargs.get("initial_phase", cr_phase[self.cr_elem]))
        self.current_amp = float(kwargs.get("initial_amp", cr_amp[self.cr_elem]))

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
                "amp_list": self.amp_list,
                "initial_phase": self.initial_phase,
                "current_amp": self.current_amp,
                "echo_p": self.echo_p,
                "pi_12": self.pi_12,
                "t_min_ns": self.t_min_ns,
                "t_max_ns": self.t_max_ns,
                "dt_ns": self.dt_ns,
                "wait_init": self.wait_init,
                "wait_t": self.wait_t,
                "wait_rr": self.wait_rr,
                "n_avg": self.n_avg,
                "simulate": self.simulate,
                "auto_select": self.auto_select,
                "target_zx_mhz": self.target_zx_mhz,
                "selected_amp": self.selected_amp,
                "save_live_plot": self.save_live_plot,
                "plot_local": self.plot_local,
                "plot_formats": self.plot_formats,
                "fit_max_cycles": self.fit_max_cycles,
                "fit_max_cycles_at_max_amp": self.fit_max_cycles_at_max_amp,
                "fit_min_cycles": self.fit_min_cycles,
                "fit_initial_state_weight": self.fit_initial_state_weight,
                "fit_affine_output": self.fit_affine_output,
            },
            "trials": [],
            "summary": {},
            "artifacts": [],
        }

    def _score_trial(self, trial):
        strengths = np.array(trial["int_strengths_mhz"], dtype=float)
        zx, ix, zy, iy = strengths[0], strengths[1], strengths[2], strengths[3]
        leakage_penalty = abs(zy) + 0.5 * (abs(ix) + abs(iy)) + 1e-12
        if self.target_zx_mhz is not None:
            return -abs(abs(zx) - abs(float(self.target_zx_mhz))) - 0.25 * leakage_penalty
        return abs(zx) / leakage_penalty

    def _select_amp(self):
        if self.selected_amp is not None:
            return float(self.selected_amp), "selected_amp"
        if not self.auto_select or len(self.results["trials"]) == 0:
            return None, "not_selected"
        best = max(self.results["trials"], key=self._score_trial)
        return float(best["amp"]), "auto_select"

    def _fit_max_cycles_for_amp(self, amp_value):
        if self.fit_max_cycles is None:
            return None
        if isinstance(self.fit_max_cycles, str):
            if self.fit_max_cycles.lower() != "auto":
                raise ValueError("fit_max_cycles must be None, a number, or 'auto'.")
            max_amp = max(float(np.max(np.abs(self.amp_list))), abs(float(amp_value)), 1e-12)
            scaled_cycles = self.fit_max_cycles_at_max_amp * abs(float(amp_value)) / max_amp
            return max(self.fit_min_cycles, scaled_cycles)
        return float(self.fit_max_cycles)

    @staticmethod
    def _scale_fit_seed(fit_seed, amp_value, previous_amp):
        if fit_seed is None or previous_amp is None or abs(previous_amp) < 1e-12:
            return fit_seed
        scale = float(amp_value) / float(previous_amp)
        scaled_seed = []
        for params in fit_seed:
            params_scaled = np.array(params, dtype=float).copy()
            params_scaled[:3] *= scale
            scaled_seed.append(params_scaled)
        return scaled_seed

    def _save_figure(self, fig, suffix):
        if not self.save_plot:
            return
        for fmt in self.plot_formats:
            fig_path = str(self.path_to_save) + f"_{suffix}.{fmt}"
            fig.savefig(fig_path, bbox_inches="tight")
            self.results["artifacts"].append(fig_path)
            logger.info("Saved plot: %s", fig_path)

    def _save_tomography_fit_plot(self, analysis, amp_value):
        if not self.plot_local:
            return
        time_ns = analysis["time_ns"]
        cdata = analysis["cdata"]
        fit_vals = [analysis["fit_vals_control0"], analysis["fit_vals_control1"]]
        strengths = np.array(analysis["int_strengths_mhz"], dtype=float)
        colors = ["red", "blue", "green"]
        labels = ["Z", "Y", "X"]

        fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
        for control_idx, axis in enumerate(axes):
            for tomo_idx, (label, color) in enumerate(zip(labels, colors)):
                axis.plot(
                    time_ns,
                    cdata[tomo_idx][control_idx],
                    ".",
                    color=color,
                    alpha=0.7,
                    label=f"{label} data",
                )
                axis.plot(time_ns, fit_vals[control_idx][tomo_idx], color=color, linewidth=2.0, label=f"{label} fit")
            axis.set_title(f"Control {control_idx}")
            axis.set_xlabel("Time (ns)")
            axis.set_ylabel("Expectation value")
            axis.set_ylim(-1.1, 1.1)
            axis.grid(True)
            axis.legend(loc="best", fontsize=8)
        fig.suptitle(
            f"No-AC CR amplitude {amp_value:.6f} q{self.q_control_no}->q{self.q_target_no}\n"
            f"ZX={strengths[0]:.4f} MHz, IX={strengths[1]:.4f} MHz, "
            f"ZY={strengths[2]:.4f} MHz, IY={strengths[3]:.4f} MHz"
        )
        if analysis.get("max_fit_cycles") is not None:
            fit_note = f"Bounded Bloch fit: max {analysis['max_fit_cycles']:.2f} cycles"
            if analysis.get("affine_output"):
                fit_note += ", affine readout scale/offset"
            if analysis.get("initial_state_weight", 0.0) > 0:
                fit_note += f", t=0 anchor weight {analysis['initial_state_weight']:.1f}"
            fig.text(
                0.5,
                0.01,
                fit_note,
                ha="center",
                va="bottom",
                fontsize=9,
            )
        fig.tight_layout()

        self._save_figure(fig, f"amp_{amp_value:.6f}_tomography_fit")
        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

    def _save_summary_plot(self):
        trials = self.results.get("trials", [])
        if len(trials) == 0:
            return
        amps = np.array([t["amp"] for t in trials], dtype=float)
        strengths = np.array([t["int_strengths_mhz"] for t in trials], dtype=float)
        scores = np.array([self._score_trial(t) for t in trials], dtype=float)

        fig, axes = plt.subplots(3, 1, figsize=(9, 10), sharex=True)
        for idx, label in enumerate(INT_STRENGTH_LABELS[:4]):
            axes[0].plot(amps, strengths[:, idx], "o-", label=label)
        axes[0].set_ylabel("Strength (MHz)")
        axes[0].grid(True)
        axes[0].legend()

        axes[1].plot(amps, [t["str_phase_correction"] for t in trials], "o-", label="ZX/ZY phase correction")
        axes[1].plot(amps, [t["str_ac_phase_correction"] for t in trials], "o-", label="IX/IY phase correction")
        axes[1].set_ylabel("Phase correction (cycles)")
        axes[1].grid(True)
        axes[1].legend()

        axes[2].plot(amps, scores, "o-", label="selection score")
        axes[2].set_xlabel("CR amplitude")
        axes[2].set_ylabel("Score")
        axes[2].grid(True)
        axes[2].legend()
        fig.suptitle(f"No-AC CR amplitude sweep q{self.q_control_no}->q{self.q_target_no}")
        fig.tight_layout()

        self._save_figure(fig, f"q{self.q_control_no}_q{self.q_target_no}_summary")
        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

    def _update_calibration_file(self, amp_opt):
        amp_path = self.config_files_path + "/Pulse_Calibrations/cr_amp.json"
        with open(amp_path, "r") as fptr:
            amp_dict = json.load(fptr)
        old_val = float(amp_dict[self.cr_elem])
        new_val = float(amp_opt)
        abs_diff = abs(new_val - old_val)
        rel_diff = abs_diff / max(abs(old_val), 1e-12)
        update_fail_flag = bool(rel_diff > self.max_amp_update_fraction)
        applied = not update_fail_flag
        if applied:
            amp_dict[self.cr_elem] = new_val
            with open(amp_path, "w") as fptr:
                json.dump(amp_dict, fptr, indent=2)

        self.results["summary"]["calibration_update"] = {
            "path": amp_path,
            "key": self.cr_elem,
            "old_amp": old_val,
            "new_amp": new_val,
            "abs_amp_diff": abs_diff,
            "relative_amp_diff": rel_diff,
            "max_amp_update_fraction": self.max_amp_update_fraction,
            "update_fail_flag": update_fail_flag,
            "applied": applied,
        }
        if update_fail_flag:
            logger.warning(
                "CR amplitude update blocked for %s: old=%.6f new=%.6f rel_diff=%.6f",
                self.cr_elem,
                old_val,
                new_val,
                rel_diff,
            )

    def run(self):
        if self.refresh_qm_config:
            self.refresh_qm_config_from_disk()
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        norm_off_pair = (None, None)
        fit_seed = None
        previous_amp = None

        try:
            for amp_value in self.amp_list:
                amp_value = float(amp_value)
                fit_seed = self._scale_fit_seed(fit_seed, amp_value, previous_amp)
                max_fit_cycles = self._fit_max_cycles_for_amp(amp_value)
                logger.info("Running no-AC CR amplitude %.6f for %s", amp_value, self.cr_elem)
                I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg = collect_cr_tomography(
                    self,
                    self._qmm,
                    self.initial_phase,
                    amp_value,
                    self.echo_p,
                    title=f"No-AC CR amplitude sweep amp={amp_value:.6f}",
                    plot_suffix=f"amp_{amp_value:.6f}_live_tomography",
                )
                analysis = analyze_cr_tomography(
                    self.t_list_ns,
                    I_t_avg,
                    I_rabi_avg,
                    norm_off_pair,
                    fit_init_vals=fit_seed,
                    max_fit_cycles=max_fit_cycles,
                    initial_state_weight=self.fit_initial_state_weight,
                    affine_output=self.fit_affine_output,
                )
                norm_off_pair = (analysis["norm"], analysis["offset"])
                fit_seed = [analysis["fit_params_control0"], analysis["fit_params_control1"]]
                previous_amp = amp_value
                save_rabi_fit_plot(self, analysis, suffix=f"amp_{amp_value:.6f}")
                self._save_tomography_fit_plot(analysis, amp_value)

                Ic0, Ic1 = split_control_traces(I_c_avg, len(self.t_list))
                Qc0, Qc1 = split_control_traces(Q_c_avg, len(self.t_list))
                trial = {
                    "amp": amp_value,
                    "int_strength_labels": INT_STRENGTH_LABELS,
                    "int_strengths_hz": analysis["int_strengths_hz"],
                    "int_strengths_mhz": analysis["int_strengths_mhz"],
                    "str_phase_correction": analysis["str_phase_correction"],
                    "str_ac_phase_correction": analysis["str_ac_phase_correction"],
                    "max_fit_cycles": analysis["max_fit_cycles"],
                    "initial_state_weight": analysis["initial_state_weight"],
                    "affine_output": analysis["affine_output"],
                    "affine_fit_params_control0": analysis["affine_fit_params_control0"],
                    "affine_fit_params_control1": analysis["affine_fit_params_control1"],
                    "bounded_fit": analysis["bounded_fit"],
                    "norm": analysis["norm"],
                    "offset": analysis["offset"],
                }
                if self.save_traces:
                    trial.update(
                        {
                            "time_ns": self.t_list_ns.copy(),
                            "I_t_avg": I_t_avg,
                            "Q_t_avg": Q_t_avg,
                            "I_c0": Ic0,
                            "Q_c0": Qc0,
                            "I_c1": Ic1,
                            "Q_c1": Qc1,
                            "I_rabi_avg": I_rabi_avg,
                            "Q_rabi_avg": Q_rabi_avg,
                        }
                    )
                self.results["trials"].append(trial)

            amp_opt, selection_method = self._select_amp()
            self.results["summary"] = {
                "optimal_amp": amp_opt,
                "selection_method": selection_method,
                "current_amp": self.current_amp,
                "phase_used": self.initial_phase,
                "trials_completed": len(self.results["trials"]),
            }
            self._save_summary_plot()
            if self.update_calib:
                if amp_opt is None:
                    logger.warning("update_calib=True but no CR amplitude was selected; cr_amp.json was not changed.")
                    self.results["summary"]["calibration_update"] = {"applied": False, "reason": "no_selected_amp"}
                else:
                    self._update_calibration_file(amp_opt)
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


def perform_cr_amp_sweep(control_qubit: int, target_qubit: int, **kwargs) -> CRAmplitudeSweep:
    exp = CRAmplitudeSweep(q_list=[control_qubit, target_qubit], **kwargs)
    exp.run()
    return exp


def perform_cr_amp_sweep_for_pairs(
    pair_list: Iterable[Tuple[int, int]],
    **kwargs,
) -> Dict[str, CRAmplitudeSweep]:
    out = {}
    for control_qubit, target_qubit in pair_list:
        key = f"q{control_qubit}_q{target_qubit}"
        out[key] = perform_cr_amp_sweep(control_qubit, target_qubit, **kwargs)
    return out


if __name__ == "__main__":
    perform_cr_amp_sweep(
        control_qubit=1,
        target_qubit=2,
        amp_list=np.linspace(0.05, 0.8, 20),
        save_data=True,
        save_plot=True,
        plot_formats=("svg",),
        save_live_plot=True,
        plot_local=True,
        plot_rabi=False,
        fit_max_cycles="auto",
        fit_min_cycles=1.0,
        fit_max_cycles_at_max_amp=4.0,
        fit_initial_state_weight=0.0,
        fit_affine_output=True,
        show_plot=True,
        update_calib=False,
        simulate=False,
    )

