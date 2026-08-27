import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from qm import QuantumMachinesManager, SimulationConfig
from qm.qua import (
    align,
    assign,
    declare,
    declare_stream,
    fixed,
    for_,
    program,
    save,
    stream_processing,
)

import Configuration_Files.configuration_4qubitsv3 as _qm_cfg
from Configuration_Files.configuration_4qubitsv3 import cluster_name, qm_ip
from HM.single_qubit_experiments.ro_fidelity import perform_ro_fidelity
from HM.two_qubit_experiments.two_qubit_base import TwoQubitExperiment
from Helper_Functions.macros import CNOT_macro, Hadamard, cooldown, measure_macro

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class BellStateCorrelations(TwoQubitExperiment):
    """
    Bell-state correlation experiment for a control-target qubit pair.

    Run ro_fidelity (or equivalent readout calibration) on both resonators first
    so demarcations/rotation are up to date.
    """

    def __init__(self, q_list: List[int], **kwargs):
        super().__init__(q_list=q_list, expt_name="bell_state_correlations", **kwargs)
        self.n_shots = int(kwargs.get("n_shots", 25_000))
        self.wait_init = int(kwargs.get("wait_init", 250_000))
        self.wait_rr = int(kwargs.get("wait_rr", 8))
        self.ac_flag = bool(kwargs.get("ac_flag", False))
        self.simulate = bool(kwargs.get("simulate", False))
        self.save_data = bool(kwargs.get("save_data", False))
        self.save_plot = bool(kwargs.get("save_plot", True))
        self.show_plot = bool(kwargs.get("show_plot", True))
        self.precal = bool(kwargs.get("precal", False))
        self.precal_n_runs = int(kwargs.get("precal_n_runs", 10_000))
        self.precal_save_data = bool(kwargs.get("precal_save_data", True))
        self.precal_save_plot = bool(kwargs.get("precal_save_plot", True))
        self.precal_show_plot = bool(kwargs.get("precal_show_plot", False))
        self._qmm = None
        self._qm = None

        self.results = {
            "control_q": self.q_control_no,
            "target_q": self.q_target_no,
            "params": {
                "n_shots": self.n_shots,
                "wait_init": self.wait_init,
                "wait_rr": self.wait_rr,
                "ac_flag": self.ac_flag,
                "simulate": self.simulate,
                "save_plot": self.save_plot,
                "precal": self.precal,
                "precal_n_runs": self.precal_n_runs,
            },
            "raw": {},
            "correlations": {},
            "precalibration": {},
            "artifacts": [],
        }

    def _run_precalibrations(self):
        logger.info(
            "Running readout precalibration (ro_fidelity) for q%s and q%s",
            self.q_control_no,
            self.q_target_no,
        )
        precal_payload = {}
        for q_no in (self.q_control_no, self.q_target_no):
            exp = perform_ro_fidelity(
                q_no=q_no,
                rr_no=q_no,
                n_runs=self.precal_n_runs,
                update_config=True,
                save_data=self.precal_save_data,
                save_plot=self.precal_save_plot,
                show_plot=self.precal_show_plot,
            )
            fidelity_percent = None
            try:
                fidelity_percent = float(exp.results["analysis"]["fidelity_percent"])
            except Exception:
                fidelity_percent = None
            precal_payload[f"q{q_no}"] = {
                "fidelity_percent": fidelity_percent,
                "n_runs": self.precal_n_runs,
            }
        self.results["precalibration"] = precal_payload

    def _load_demarcations(self) -> Tuple[float, float]:
        demarcation_path = Path(self.config_files_path) / "Readout_Settings" / "demarcations.json"
        with open(demarcation_path, "r") as fptr:
            demarcations = json.load(fptr)
        target_threshold = float(demarcations[str(self.q_target_no)])
        control_threshold = float(demarcations[str(self.q_control_no)])
        return target_threshold, control_threshold

    def _build_program(self):
        dem_target, dem_control = self._load_demarcations()
        elem_list = [
            self.q_control_str,
            self.q_target_str,
            self.cr_elem,
            self.cr_ac_elem,
        ]

        with program() as bell_state_prog:
            n = declare(int)
            i_target = declare(fixed)
            i_control = declare(fixed)
            q_dummy = declare(fixed)
            target_excited = declare(bool)
            control_excited = declare(bool)

            i_target_st = declare_stream()
            i_control_st = declare_stream()
            target_bool_st = declare_stream()
            control_bool_st = declare_stream()

            with for_(n, 0, n < self.n_shots, n + 1):
                cooldown(time=self.wait_init)
                align(*elem_list)

                Hadamard(self.q_control_str)
                align(self.q_control_str, self.cr_elem)
                CNOT_macro(self.q_control_str, self.q_target_str, self.ac_flag)

                measure_macro(
                    self.q_target_str,
                    self.rr_target_str,
                    self.out_target,
                    i_target,
                    q_dummy,
                    pi_12=True,
                )
                measure_macro(
                    self.q_control_str,
                    self.rr_control_str,
                    self.out_control,
                    i_control,
                    q_dummy,
                    pi_12=True,
                )

                assign(target_excited, i_target > dem_target)
                assign(control_excited, i_control > dem_control)

                save(i_target, i_target_st)
                save(i_control, i_control_st)
                save(target_excited, target_bool_st)
                save(control_excited, control_bool_st)

            with stream_processing():
                i_target_st.save_all("I_target")
                i_control_st.save_all("I_control")
                target_bool_st.save_all("target_excited")
                control_bool_st.save_all("control_excited")

        return bell_state_prog

    @staticmethod
    def _fetch_array(handle_data):
        if isinstance(handle_data, dict) and "value" in handle_data:
            handle_data = handle_data["value"]
        return np.asarray(handle_data).reshape(-1)

    def _compute_correlations(self, target_excited: np.ndarray, control_excited: np.ndarray):
        target_excited = np.asarray(target_excited, dtype=bool).reshape(-1)
        control_excited = np.asarray(control_excited, dtype=bool).reshape(-1)
        if target_excited.size != control_excited.size:
            raise ValueError("Target and control arrays must have same length.")

        c00 = int(np.sum((~control_excited) & (~target_excited)))
        c01 = int(np.sum((~control_excited) & target_excited))
        c10 = int(np.sum(control_excited & (~target_excited)))
        c11 = int(np.sum(control_excited & target_excited))
        total = c00 + c01 + c10 + c11
        if total == 0:
            raise RuntimeError("No measurements captured.")

        matrix = np.array(
            [[c00 / total, c01 / total], [c10 / total, c11 / total]],
            dtype=float,
        )
        measured_probs = {
            "00": float(c00) / float(total),
            "01": float(c01) / float(total),
            "10": float(c10) / float(total),
            "11": float(c11) / float(total),
        }
        ideal_probs = {
            "00": 0.5,
            "01": 0.0,
            "10": 0.0,
            "11": 0.5,
        }
        state_fidelity = self.calculate_state_fidelity(
            counts_ideal=ideal_probs,
            counts_measured=measured_probs,
            is_probability=True,
        )
        coincidence_00_11 = float(c00 + c11) / float(total)
        return matrix, {
            "c00": c00,
            "c01": c01,
            "c10": c10,
            "c11": c11,
            "total": total,
            "state_fidelity_to_ideal_00_11": float(state_fidelity),
            "coincidence_00_11": float(coincidence_00_11),
        }

    def _plot_correlations(self, corr_matrix: np.ndarray, total: int):
        fig = plt.figure()
        plt.imshow(corr_matrix)
        plt.xticks([0, 1])
        plt.yticks([0, 1])
        plt.ylabel("Control")
        plt.xlabel("Target")
        plt.text(0, 0, f"{100 * corr_matrix[0, 0]:.1f}%", ha="center", va="center", color="k")
        plt.text(1, 0, f"{100 * corr_matrix[0, 1]:.1f}%", ha="center", va="center", color="w")
        plt.text(0, 1, f"{100 * corr_matrix[1, 0]:.1f}%", ha="center", va="center", color="w")
        plt.text(1, 1, f"{100 * corr_matrix[1, 1]:.1f}%", ha="center", va="center", color="k")
        plt.title(f"Bell-state correlations q{self.q_control_no}-q{self.q_target_no} (N={total})")

        state_fidelity = 100.0 * float(
            self.results.get("correlations", {}).get("counts", {}).get("state_fidelity_to_ideal_00_11", np.nan)
        )
        note_lines = [
            f"Ideal target: 00/11 = 50/50",
            f"State fidelity to ideal 00/11: {state_fidelity:.2f}%",
        ]
        if self.precal:
            ctrl_f = self.results.get("precalibration", {}).get(f"q{self.q_control_no}", {}).get("fidelity_percent")
            tgt_f = self.results.get("precalibration", {}).get(f"q{self.q_target_no}", {}).get("fidelity_percent")
            if ctrl_f is not None:
                note_lines.append(f"Precal RO fidelity q{self.q_control_no}: {float(ctrl_f):.2f}%")
            if tgt_f is not None:
                note_lines.append(f"Precal RO fidelity q{self.q_target_no}: {float(tgt_f):.2f}%")
        fig.text(
            0.02,
            0.02,
            "\n".join(note_lines),
            ha="left",
            va="bottom",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.75, edgecolor="none"),
        )
        self.register_figure("correlation_matrix", fig)

        if self.save_plot:
            fig_path = str(self.path_to_save) + f"_q{self.q_control_no}_q{self.q_target_no}_corr.svg"
            plt.tight_layout()
            plt.savefig(fig_path, bbox_inches="tight")
            self.results["artifacts"].append(fig_path)
            logger.info(f"Saved Bell-state correlation figure: {fig_path}")

        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

    def _save_experiment_data(self):
        save_path = str(self.path_to_save) + f"_q{self.q_control_no}_q{self.q_target_no}.json"
        self.save_json(self.results, save_path)
        self.results["artifacts"].append(save_path)
        return save_path

    def _plot_simulation_ports(self, samples):
        qe_t_i = self.dac_mapping[self.q_target_str][1][0]
        qe_t_q = self.dac_mapping[self.q_target_str][1][1]
        qe_c_i = self.dac_mapping[self.q_control_str][1][0]
        qe_c_q = self.dac_mapping[self.q_control_str][1][1]
        rr_c_i = self.dac_mapping[self.rr_control_str][1][0]
        rr_c_q = self.dac_mapping[self.rr_control_str][1][1]
        rr_t_i = self.dac_mapping[self.rr_target_str][1][0]
        rr_t_q = self.dac_mapping[self.rr_target_str][1][1]
        con_ctrl = f"con{self.dac_mapping[self.q_control_str][0]}"
        con_tgt = f"con{self.dac_mapping[self.q_target_str][0]}"

        control_i = getattr(samples, con_ctrl).analog[f"{qe_c_i}"]
        control_q = getattr(samples, con_ctrl).analog[f"{qe_c_q}"]
        target_i = getattr(samples, con_tgt).analog[f"{qe_t_i}"]
        target_q = getattr(samples, con_tgt).analog[f"{qe_t_q}"]
        rd_c_i = getattr(samples, con_ctrl).analog[f"{rr_c_i}"]
        rd_c_q = getattr(samples, con_ctrl).analog[f"{rr_c_q}"]
        rd_t_i = getattr(samples, con_tgt).analog[f"{rr_t_i}"]
        rd_t_q = getattr(samples, con_tgt).analog[f"{rr_t_q}"]

        plt.figure()
        plt.plot(control_i, label="control_I")
        plt.plot(control_q, label="control_Q")
        plt.plot(target_i, label="target_I")
        plt.plot(target_q, label="target_Q")
        plt.plot(rd_c_i, label="rd_c_I")
        plt.plot(rd_c_q, label="rd_c_Q")
        plt.plot(rd_t_i, label="rd_t_I")
        plt.plot(rd_t_q, label="rd_t_Q")
        plt.grid()
        plt.legend()
        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close()

    def run(self):
        self._qmm = QuantumMachinesManager(host=qm_ip, cluster_name=cluster_name)
        try:
            if self.refresh_qm_config:
                self.refresh_qm_config_from_disk()
            if self.precal:
                self._run_precalibrations()

            bell_prog = self._build_program()

            if self.simulate:
                sim_job = self._qmm.simulate(_qm_cfg.config, bell_prog, SimulationConfig(int(10_000)))
                self._plot_simulation_ports(sim_job.get_simulated_samples())
                self.results["simulation_only"] = True
                return self.results

            self._qm = self._qmm.open_qm(_qm_cfg.config)
            job = self._qm.execute(bell_prog)
            job.result_handles.wait_for_all_values()

            i_target = self._fetch_array(job.result_handles.get("I_target").fetch_all())
            i_control = self._fetch_array(job.result_handles.get("I_control").fetch_all())
            target_excited = self._fetch_array(job.result_handles.get("target_excited").fetch_all()).astype(bool)
            control_excited = self._fetch_array(job.result_handles.get("control_excited").fetch_all()).astype(bool)

            corr_matrix, counts = self._compute_correlations(target_excited, control_excited)
            self.results["raw"] = {
                "I_target": i_target,
                "I_control": i_control,
                "target_excited": target_excited,
                "control_excited": control_excited,
            }
            self.results["correlations"] = {
                "counts": counts,
                "matrix": corr_matrix,
            }

            self._plot_correlations(corr_matrix, counts["total"])
            if self.save_data:
                path = self._save_experiment_data()
                logger.info(f"Saved Bell-state data: {path}")
            return self.results
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


def perform_bell_state_correlations(
    control_qubit: int,
    target_qubit: int,
    **kwargs,
) -> BellStateCorrelations:
    exp = BellStateCorrelations(q_list=[control_qubit, target_qubit], **kwargs)
    exp.run()
    return exp


def perform_bell_state_correlations_for_pairs(
    pair_list: Iterable[Tuple[int, int]],
    **kwargs,
) -> Dict[str, BellStateCorrelations]:
    experiments = {}
    for control_qubit, target_qubit in pair_list:
        key = f"q{control_qubit}_q{target_qubit}"
        experiments[key] = perform_bell_state_correlations(control_qubit, target_qubit, **kwargs)
    return experiments


if __name__ == "__main__":
    perform_bell_state_correlations(
        control_qubit=1,
        target_qubit=2,
        n_shots=25_000,
        save_data=False,
        show_plot=True,
        save_plot=True,
        simulate=False,
        precal=False,
    )
