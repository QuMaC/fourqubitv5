import json
import logging
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from qm import QuantumMachinesManager
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import fetching_tool, progress_counter

from Configuration_Files.config_dictionaries import cr_amp, cr_phase
from Helper_Functions.CR_fitters import (
    CR_Hamiltonian_tomography,
    bloch_functions,
    fit_cos,
    normalize_data,
    rabi_fit,
)
from Helper_Functions.helper_functionsv2 import S2N
from Helper_Functions.qua_program_funcs import HT_setPhase_local_phase
from HM.two_qubit_experiments.two_qubit_base import TwoQubitExperiment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class CRLocalPhaseSweep(TwoQubitExperiment):
    """
    Iterative CR local-phase calibration using Hamiltonian tomography.
    """

    def __init__(self, q_list: List[int], **kwargs):
        super().__init__(q_list=q_list, expt_name="cr_local_phase_sweep", **kwargs)

        self.simulate = bool(kwargs.get("simulate", False))
        self.save_data = bool(kwargs.get("save_data", True))
        self.save_plot = bool(kwargs.get("save_plot", True))
        self.show_plot = bool(kwargs.get("show_plot", True))
        self.plot_live = bool(kwargs.get("plot_live", True))
        self.plot_local = bool(kwargs.get("plot_local", True))
        self.plot_rabi = bool(kwargs.get("plot_rabi", False))
        self.update_calib = bool(kwargs.get("update_calib", True))
        self.max_phase_update_fraction = float(kwargs.get("max_phase_update_fraction", 0.10))
        self.pi_12 = bool(kwargs.get("pi_12", True))
        self.echo_p = bool(kwargs.get("echo_p", False))

        self.t_min_ns = int(kwargs.get("t_min_ns", 4))
        self.t_max_ns = int(kwargs.get("t_max_ns", 1000))
        self.dt_ns = int(kwargs.get("dt_ns", 4))
        self.wait_init = int(kwargs.get("wait_init", 250_000))
        self.wait_t = int(kwargs.get("wait_t", 4))
        self.wait_rr = int(kwargs.get("wait_rr", 16))
        self.n_avg = int(kwargs.get("n_avg", 200))
        self.phase_tolerance = float(kwargs.get("phase_tolerance", 0.005))
        self.max_trials = int(kwargs.get("max_trials", 7))
        self.snr_halt_threshold = float(kwargs.get("snr_halt_threshold", 90.0))

        self.cr_elem = f"cr_c{self.q_control_no}t{self.q_target_no}"
        self.initial_phase = float(kwargs.get("initial_phase", cr_phase[self.cr_elem]))
        self.cr_amp = float(kwargs.get("cr_amp", cr_amp[self.cr_elem]))
        self._qmm = None

        self.t_min = int(self.t_min_ns / 4)
        self.t_max = int(self.t_max_ns / 4)
        self.dt = int(self.dt_ns / 4)
        self.t_list = np.arange(self.t_min, self.t_max, self.dt)
        self.t_list_ns = 2 * 4 * self.t_list

        self.results = {
            "control_q": self.q_control_no,
            "target_q": self.q_target_no,
            "cr_elem": self.cr_elem,
            "params": {
                "t_min_ns": self.t_min_ns,
                "t_max_ns": self.t_max_ns,
                "dt_ns": self.dt_ns,
                "wait_init": self.wait_init,
                "wait_t": self.wait_t,
                "wait_rr": self.wait_rr,
                "n_avg": self.n_avg,
                "phase_tolerance": self.phase_tolerance,
                "max_trials": self.max_trials,
                "simulate": self.simulate,
                "max_phase_update_fraction": self.max_phase_update_fraction,
                "pi_12": self.pi_12,
                "echo_p": self.echo_p,
                "cr_amp": self.cr_amp,
                "initial_phase": self.initial_phase,
            },
            "trials": [],
            "summary": {},
            "artifacts": [],
        }

    @staticmethod
    def _wrap_phase_unit_cycle(phase):
        phase = float(phase)
        if phase > 1:
            phase -= 1
        elif phase < -1:
            phase += 1
        return phase

    @staticmethod
    def _phase_distance_cycles(new_phase, old_phase):
        # Compare phases on a wrapped cycle so 0.99 and -1.01 are close.
        d = float(new_phase) - float(old_phase)
        while d > 1.0:
            d -= 2.0
        while d < -1.0:
            d += 2.0
        return abs(d)

    def _init_live_plot(self, job, p):
        if not self.plot_live:
            return None
        plt.ion()
        plt.rcParams["figure.figsize"] = (15, 10)
        fig, ax = plt.subplots(3, 3, sharex=True, sharey="row")
        interrupt_on_close(fig, job)
        fig.suptitle(f"CR Tomography : Phase {p:.6f}", fontsize=15)
        axbig = fig.add_subplot(111, frameon=False)
        axbig.set_xlabel("Time (us)", labelpad=20, fontsize=15)
        axbig.set_ylabel("Amplitude", labelpad=50, fontsize=15)
        axbig.set_xticks([])
        axbig.set_yticks([])
        lines = []
        tc = ["Control 0", "Control 1"]
        labels = ["Z", "Y", "X"]
        for i in range(2):
            for j in range(3):
                lines.append(
                    ax[i, j].plot(
                        1e-3 * self.t_list_ns,
                        1e-4 * np.random.rand(len(self.t_list_ns)),
                        marker=".",
                        label="I",
                    )[0]
                )
                lines.append(ax[i, j].plot(1e-3 * self.t_list_ns, [0] * len(self.t_list_ns), marker=".", label="Q")[0])
                ax[i, j].set_title(tc[i] + " Target: " + labels[j])
                ax[i, j].grid()
                ax[i, j].legend(loc="upper right")
        for i in range(2):
            lines.append(ax[2, i].plot(1e-3 * self.t_list_ns, [0] * len(self.t_list_ns), marker=".", label="I")[0])
            lines.append(ax[2, i].plot(1e-3 * self.t_list_ns, [0] * len(self.t_list_ns), marker=".", label="Q")[0])
            ax[2, i].set_title(f"Control {i}")
            ax[2, i].grid()
            ax[2, i].legend(loc="upper right")
        lines.append(ax[2, 2].plot(1e-3 * self.t_list_ns, [0] * len(self.t_list_ns), marker=".", label="I")[0])
        lines.append(ax[2, 2].plot(1e-3 * self.t_list_ns, [0] * len(self.t_list_ns), marker=".", label="Q")[0])
        ax[2, 2].set_title("Target Rabi")
        ax[2, 2].grid()
        ax[2, 2].legend(loc="upper right")
        fig.set_tight_layout(True)
        if self.show_plot:
            plt.show()
        return {"fig": fig, "ax": ax, "lines": lines}

    def _update_live_plot(self, live_plot, I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg):
        if live_plot is None:
            return
        fig = live_plot["fig"]
        ax = live_plot["ax"]
        lines = live_plot["lines"]
        Ic0 = np.average(I_c_avg[:, 0].reshape(len(self.t_list), 3), axis=1)
        Ic1 = np.average(I_c_avg[:, 1].reshape(len(self.t_list), 3), axis=1)
        lines[12].set_ydata(Ic0)
        lines[13].set_ydata(Ic0)
        lines[14].set_ydata(Ic1)
        lines[15].set_ydata(Ic1)
        lines[16].set_ydata(I_rabi_avg)
        for i in range(0, 6):
            lines[2 * i].set_ydata(I_t_avg[:, i])
            lines[2 * i + 1].set_ydata(Q_t_avg[:, i])
        for i in range(3):
            for j in range(3):
                ax[i, j].relim()
                ax[i, j].autoscale_view()
        fig.set_tight_layout(True)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.1)

    def _save_trial_local_fit_figures(self, time_list, vals1, vals2, cdata, phase_value, trial_idx):
        if not self.plot_local:
            return
        colors = ["red", "blue", "green"]
        labels = ["Z", "Y", "X"]

        fig0 = plt.figure()
        for i in range(3):
            plt.plot(time_list, vals1[i], color=colors[i], label=labels[i])
            plt.plot(time_list, cdata[i][0], ".", color=colors[i])
        plt.grid()
        plt.title(f"CR local fit phase={phase_value:.6f} control=0 trial={trial_idx}")
        plt.legend()
        plt.ylabel("Expectation Value")
        plt.xlabel("Time (ns)")

        fig1 = plt.figure()
        for i in range(3):
            plt.plot(time_list, vals2[i], color=colors[i], label=labels[i])
            plt.plot(time_list, cdata[i][1], ".", color=colors[i])
        plt.grid()
        plt.title(f"CR local fit phase={phase_value:.6f} control=1 trial={trial_idx}")
        plt.legend()
        plt.ylabel("Expectation Value")
        plt.xlabel("Time (ns)")

        if self.save_plot:
            path0 = str(self.path_to_save) + f"_trial_{trial_idx}_control0_fit.png"
            path1 = str(self.path_to_save) + f"_trial_{trial_idx}_control1_fit.png"
            fig0.savefig(path0, bbox_inches="tight")
            fig1.savefig(path1, bbox_inches="tight")
            self.results["artifacts"].extend([path0, path1])
            logger.info("Saved plot: %s", path0)
            logger.info("Saved plot: %s", path1)
        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig0)
            plt.close(fig1)

    def _run_one_trial(self, phase_value, trial_idx, norm_off_pair):
        job = HT_setPhase_local_phase(
            self._qmm,
            self.cr_elem,
            phase_value,
            self.t_min,
            self.t_max,
            self.dt,
            self.n_avg,
            self.wait_init,
            self.wait_t,
            self.wait_rr,
            self.q_control_str,
            self.q_target_str,
            self.pi_12,
            self.simulate,
            self.echo_p,
            self.cr_amp,
        )

        results = fetching_tool(
            job,
            data_list=["I_t_avg", "Q_t_avg", "I_c_avg", "Q_c_avg", "I_rabi_avg", "Q_rabi_avg", "iteration"],
            mode="live",
        )
        live_plot = self._init_live_plot(job, phase_value)
        while results.is_processing():
            I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg, iteration = results.fetch_all()
            progress_counter(iteration, self.n_avg, start_time=results.get_start_time())
            self._update_live_plot(live_plot, I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg)
            snr_i, _ = S2N(I_rabi_avg)
            if snr_i > self.snr_halt_threshold:
                job.halt()

        I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg, _iteration = results.fetch_all()
        self._update_live_plot(live_plot, I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg)
        if self.save_plot and live_plot is not None:
            path_live = str(self.path_to_save) + f"_trial_{trial_idx}_tomography_live.png"
            live_plot["fig"].savefig(path_live, bbox_inches="tight")
            self.results["artifacts"].append(path_live)
            logger.info("Saved plot: %s", path_live)
        Ic0 = np.average(I_c_avg[:, 0].reshape(len(self.t_list), 3), axis=1)
        Qc0 = np.average(Q_c_avg[:, 0].reshape(len(self.t_list), 3), axis=1)
        Ic1 = np.average(I_c_avg[:, 1].reshape(len(self.t_list), 3), axis=1)
        Qc1 = np.average(Q_c_avg[:, 1].reshape(len(self.t_list), 3), axis=1)
        t_list_ns_data = self.t_list_ns.reshape(len(self.t_list_ns), 1)
        itarget_data = np.hstack((t_list_ns_data, I_t_avg))

        t_data = itarget_data.transpose()
        time_list = t_data[0]
        rabi_i = 1e3 * I_rabi_avg

        norm, off = norm_off_pair
        if norm is None or off is None:
            res_i = fit_cos(time_list, rabi_i)
            pars = [res_i["amp"], res_i["freq"], 0, res_i["phase"], res_i["offset"]]
            norm, off = pars[0], pars[4]
            if self.plot_rabi:
                fig = plt.figure()
                plt.plot(self.t_list, rabi_i)
                plt.plot(self.t_list, rabi_fit(self.t_list, *pars))
                plt.grid()
                plt.title(f"Target rabi fit trial {trial_idx}")
                if self.save_plot:
                    pth = str(self.path_to_save) + f"_trial_{trial_idx}_rabi_fit.png"
                    fig.savefig(pth, bbox_inches="tight")
                    self.results["artifacts"].append(pth)
                    logger.info("Saved plot: %s", pth)
                if self.show_plot:
                    plt.show(block=False)
                else:
                    plt.close(fig)

        c0_data = 1e3 * t_data[1:4]
        c1_data = 1e3 * t_data[4:7]
        cdata = []
        for i in range(3):
            cdata.append([c0_data[i], c1_data[i]])
        cdata = normalize_data(cdata, off, norm)

        int_strengths, ivals = CR_Hamiltonian_tomography(cdata, time_list, bloch_params=True, init_vals=None)
        int_strengths = np.array(int_strengths, dtype=float)
        str_phase = float(np.arctan2(int_strengths[2], int_strengths[0]) * (1 / (2 * np.pi)))
        str_ac_phase = float(np.arctan2(int_strengths[3], int_strengths[1]) * (1 / (2 * np.pi)))
        str_phase = self._wrap_phase_unit_cycle(str_phase)
        str_ac_phase = self._wrap_phase_unit_cycle(str_ac_phase)

        ox1, oy1, del1, d1 = ivals[0]
        ox2, oy2, del2, d2 = ivals[1]
        vals1 = bloch_functions(time_list, ox1, oy1, del1, d1)
        vals2 = bloch_functions(time_list, ox2, oy2, del2, d2)
        self._save_trial_local_fit_figures(time_list, vals1, vals2, cdata, phase_value, trial_idx)

        return {
            "phase_in": float(phase_value),
            "int_strengths_hz": int_strengths,
            "int_strengths_mhz": 1e3 * int_strengths,
            "str_phase_correction": str_phase,
            "str_ac_phase_correction": str_ac_phase,
            "norm": float(norm),
            "offset": float(off),
            "Ic0": Ic0,
            "Qc0": Qc0,
            "Ic1": Ic1,
            "Qc1": Qc1,
            "I_t_avg": I_t_avg,
            "Q_t_avg": Q_t_avg,
            "I_rabi_avg": I_rabi_avg,
            "Q_rabi_avg": Q_rabi_avg,
            "time_ns": self.t_list_ns.copy(),
            "norm_off_pair": (float(norm), float(off)),
        }

    def _save_summary_plot(self):
        trials = self.results.get("trials", [])
        if len(trials) == 0:
            return
        trial_idx = np.arange(1, len(trials) + 1)
        phase_in = np.array([t["phase_in"] for t in trials], dtype=float)
        phase_out = np.array([t["phase_out"] for t in trials], dtype=float)
        zx = np.array([t["int_strengths_mhz"][0] for t in trials], dtype=float)
        zy = np.array([t["int_strengths_mhz"][2] for t in trials], dtype=float)

        fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
        axes[0].plot(trial_idx, phase_in, "o-", label="phase in")
        axes[0].plot(trial_idx, phase_out, "o-", label="phase out")
        axes[0].set_ylabel("CR phase (cycles)")
        axes[0].grid(True)
        axes[0].legend()

        axes[1].plot(trial_idx, zx, "o-", label="ZX (MHz)")
        axes[1].plot(trial_idx, zy, "o-", label="ZY (MHz)")
        axes[1].set_xlabel("Trial")
        axes[1].set_ylabel("Interaction strength (MHz)")
        axes[1].grid(True)
        axes[1].legend()
        fig.suptitle(f"CR local-phase sweep q{self.q_control_no}->q{self.q_target_no}")
        fig.tight_layout()

        if self.save_plot:
            fig_path = str(self.path_to_save) + f"_q{self.q_control_no}_q{self.q_target_no}_summary.png"
            fig.savefig(fig_path, bbox_inches="tight")
            self.results["artifacts"].append(fig_path)
            logger.info("Saved plot: %s", fig_path)
        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

    def _update_calibration_file(self, phase_opt):
        phase_path = self.config_files_path + "/Pulse_Calibrations/cr_phase.json"
        with open(phase_path, "r") as fptr:
            phase_dict = json.load(fptr)
        old_val = float(phase_dict[self.cr_elem])
        new_val = float(phase_opt)
        abs_diff = self._phase_distance_cycles(new_val, old_val)
        rel_diff = abs_diff / max(abs(old_val), 1e-12)
        # Guard criterion: percentage change with respect to previous calibrated value.
        update_fail_flag = bool(rel_diff > self.max_phase_update_fraction)
        applied = not update_fail_flag

        if applied:
            phase_dict[self.cr_elem] = new_val
            with open(phase_path, "w") as fptr:
                json.dump(phase_dict, fptr, indent=2)

        self.results["summary"]["calibration_update"] = {
            "path": phase_path,
            "key": self.cr_elem,
            "old_phase": old_val,
            "new_phase": new_val,
            "abs_phase_diff_cycles": abs_diff,
            "relative_phase_diff": rel_diff,
            "max_phase_update_fraction": self.max_phase_update_fraction,
            "update_fail_flag": update_fail_flag,
            "applied": applied,
        }
        if update_fail_flag:
            logger.warning(
                "CR phase update blocked for %s: old=%.6f new=%.6f abs_diff=%.6f rel_diff=%.6f",
                self.cr_elem,
                old_val,
                new_val,
                abs_diff,
                rel_diff,
            )

    def run(self):
        if self.refresh_qm_config:
            self.refresh_qm_config_from_disk()
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        phase_value = float(self.initial_phase)
        str_phase = 1.0
        trial_idx = 0
        acc_ac_phase = 0.0
        norm_off_pair = (None, None)
        last_trial = None

        try:
            while abs(str_phase) > self.phase_tolerance and trial_idx < self.max_trials:
                trial_idx += 1
                trial = self._run_one_trial(phase_value, trial_idx, norm_off_pair)
                last_trial = trial
                norm_off_pair = trial["norm_off_pair"]

                str_phase = float(trial["str_phase_correction"])
                str_ac_phase = float(trial["str_ac_phase_correction"])
                phase_next = self._wrap_phase_unit_cycle(phase_value - str_phase)
                acc_ac_phase = self._wrap_phase_unit_cycle(acc_ac_phase - str_ac_phase)

                trial_entry = {
                    "trial_idx": trial_idx,
                    "phase_in": float(phase_value),
                    "phase_out": float(phase_next),
                    "str_phase_correction": str_phase,
                    "str_ac_phase_correction": str_ac_phase,
                    "int_strengths_mhz": trial["int_strengths_mhz"],
                }
                self.results["trials"].append(trial_entry)
                logger.info(
                    "Trial %s phase %.6f -> %.6f | ZX %.4f MHz ZY %.4f MHz",
                    trial_idx,
                    phase_value,
                    phase_next,
                    float(trial["int_strengths_mhz"][0]),
                    float(trial["int_strengths_mhz"][2]),
                )
                phase_value = phase_next

            if last_trial is None:
                raise RuntimeError("No CR local-phase trials were completed.")

            # Re-run once at the final optimized phase so the reported final strengths
            # correspond to measurements taken exactly at that phase.
            final_trial = self._run_one_trial(phase_value, trial_idx + 1, norm_off_pair)

            self.results["summary"] = {
                "optimal_phase": float(phase_value),
                "ac_phase_accumulated": float(acc_ac_phase),
                "final_int_strengths_mhz": final_trial["int_strengths_mhz"],
                "last_iter_int_strengths_mhz": last_trial["int_strengths_mhz"],
                "trials_completed": int(trial_idx),
                "converged": bool(abs(str_phase) <= self.phase_tolerance),
                "phase_tolerance": float(self.phase_tolerance),
            }
            final_strengths = self.results["summary"]["final_int_strengths_mhz"]
            logger.info(
                "Optimal CR phase %.6f cycles\n"
                "Strengths at optimal phase:\n"
                " ZX = %.6f MHz\n"
                " IX = %.6f MHz\n"
                " ZY = %.6f MHz\n"
                " IY = %.6f MHz\n"
                " ZZ = %.6f MHz\n"
                " IZ = %.6f MHz",
                phase_value,
                float(final_strengths[0]),
                float(final_strengths[1]),
                float(final_strengths[2]),
                float(final_strengths[3]),
                float(final_strengths[4]),
                float(final_strengths[5]),
            )

            self._save_summary_plot()
            if self.update_calib:
                self._update_calibration_file(phase_value)
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


def perform_cr_local_phase_sweep(control_qubit: int, target_qubit: int, **kwargs) -> CRLocalPhaseSweep:
    exp = CRLocalPhaseSweep(q_list=[control_qubit, target_qubit], **kwargs)
    exp.run()
    return exp


def perform_cr_local_phase_sweep_for_pairs(
    pair_list: Iterable[Tuple[int, int]],
    **kwargs,
) -> Dict[str, CRLocalPhaseSweep]:
    out = {}
    for control_qubit, target_qubit in pair_list:
        key = f"q{control_qubit}_q{target_qubit}"
        out[key] = perform_cr_local_phase_sweep(control_qubit, target_qubit, **kwargs)
    return out


if __name__ == "__main__":
    perform_cr_local_phase_sweep(
        control_qubit=1,
        target_qubit=2,
        save_data=True,
        save_plot=True,
        show_plot=True,
        update_calib=True,
        simulate=False,
        # save_data=True,
        max_phase_update_fraction=1,
        n_avg=400,
    )
