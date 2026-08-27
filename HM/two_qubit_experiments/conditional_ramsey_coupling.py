"""
Conditional Ramsey on the target qubit with the control in |0⟩ vs |1⟩ (π pulse),
for ZZ / coupling extraction (frequency beating between branches).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from qm import QuantumMachinesManager, SimulationConfig
from qm.qua import (
    align,
    declare,
    declare_stream,
    fixed,
    for_,
    program,
    save,
    stream_processing,
    update_frequency,
    wait,
)
from scipy.optimize import curve_fit
from termcolor import cprint

import Configuration_Files.configuration_4qubitsv3 as _qm_cfg
from Configuration_Files.configuration_4qubitsv3 import ExpName, cluster_name, qm_ip, qubit_to_ring_map
from Configuration_Files.config_dictionaries import q12_IF, q_IF, q_LO
from HM.two_qubit_experiments.two_qubit_base import TwoQubitExperiment
from Helper_Functions.analysis_functions import ramsey_fitting
from Helper_Functions.helper_functionsv2 import Halted, file_saver_
from Helper_Functions.macros import cooldown, measure_macro, play_X180, play_X90

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


def _ramsey_fit_model(t, a, f, d, p, c):
    return a * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c


class ConditionalRamseyCouplingCalc(TwoQubitExperiment):
    """
    Ramsey fringe measurement on the target with control ground vs excited.

    ``q_list`` is ``[control, target]`` (same convention as other two-qubit experiments).

    ``update_dict`` — optional write to ``CrossKerr.json`` (values in MHz, same units as on disk):
        * ``False`` / ``None``: do not modify CrossKerr.
        * ``True``: set ``str(target_qubit)`` to the fitted ZZ shift ``zz_error_mhz`` (``0.5 * total_det``).
        * ``dict`` e.g. ``{"1": 0.02}``: merge those keys into CrossKerr (manual MHz values).
    """

    def __init__(self, q_list: List[int], **kwargs):
        super().__init__(q_list=q_list, expt_name="conditional_ramsey_coupling", **kwargs)
        self.n_avg = int(kwargs.get("n_avg", 200))
        self.det_mhz = float(kwargs.get("det_mhz", 2.5))
        self.t_min = int(kwargs.get("t_min_clk", 4))
        self.t_max = int(kwargs.get("t_max_clk", 5000 // 4))
        self.dt = int(kwargs.get("dt_clk", 4))
        self.wait_init = int(kwargs.get("wait_init", 250_000 if not self.simulate else 100))
        self.pi_12 = bool(kwargs.get("pi_12", True))
        self.simulate = bool(kwargs.get("simulate", False))
        self.save_data = bool(kwargs.get("save_data", True))
        self.save_plot = bool(kwargs.get("save_plot", True))
        self.show_plot = bool(kwargs.get("show_plot", True))
        self.plot_live = bool(kwargs.get("plot_live", True))
        self.data_master_folder = kwargs.get("data_master_folder", ExpName)
        self.update_dict: Union[bool, Dict[str, float], None] = kwargs.get("update_dict", False)

        self.t_list = np.arange(self.t_min, self.t_max, self.dt)
        self._qmm = None
        self._qm = None

        self.results: Dict = {
            "control_q": self.q_control_no,
            "target_q": self.q_target_no,
            "params": {
                "n_avg": self.n_avg,
                "det_mhz": self.det_mhz,
                "t_min_clk": self.t_min,
                "t_max_clk": self.t_max,
                "dt_clk": self.dt,
                "wait_init": self.wait_init,
                "pi_12": self.pi_12,
                "simulate": self.simulate,
                "plot_live": self.plot_live,
                "update_dict": self.update_dict,
            },
            "raw": {},
            "analysis": {},
            "artifacts": [],
            "updated_config": {},
        }

    def _build_program(self):
        qubit_if = q_IF[str(self.q_target_no)]
        det_hz = self.det_mhz * 1e6

        with program() as ramsey:
            n = declare(int)
            i0 = declare(fixed)
            i0_st = declare_stream()
            q0 = declare(fixed)
            q0_st = declare_stream()
            i0c = declare(fixed)
            i0c_st = declare_stream()
            q0c = declare(fixed)
            q0c_st = declare_stream()
            i1 = declare(fixed)
            i1_st = declare_stream()
            q1 = declare(fixed)
            q1_st = declare_stream()
            i1c = declare(fixed)
            i1c_st = declare_stream()
            q1c = declare(fixed)
            q1c_st = declare_stream()
            t = declare(int)

            update_frequency(self.q_target_str, int(qubit_if + det_hz))
            with for_(n, 0, n < self.n_avg, n + 1):
                with for_(t, self.t_min, t < self.t_max, t + self.dt):
                    cooldown(time=self.wait_init)
                    play_X90(self.q_target_str)
                    wait(t, self.q_target_str)
                    play_X90(self.q_target_str)
                    align()
                    measure_macro(
                        self.q_target_str,
                        self.rr_target_str,
                        self.out_target,
                        i0,
                        q0,
                        pi_12=self.pi_12,
                    )
                    measure_macro(
                        self.q_control_str,
                        self.rr_control_str,
                        self.out_control,
                        i0c,
                        q0c,
                        pi_12=self.pi_12,
                    )
                    save(i0, i0_st)
                    save(q0, q0_st)
                    save(i0c, i0c_st)
                    save(q0c, q0c_st)

                    align()
                    cooldown(time=self.wait_init)
                    align(self.q_target_str, self.q_control_str)
                    play_X180(self.q_control_str)
                    align(self.q_control_str, self.q_target_str)
                    play_X90(self.q_target_str)
                    wait(t, self.q_target_str)
                    play_X90(self.q_target_str)
                    align()
                    measure_macro(
                        self.q_target_str,
                        self.rr_target_str,
                        self.out_target,
                        i1,
                        q1,
                        pi_12=self.pi_12,
                    )
                    measure_macro(
                        self.q_control_str,
                        self.rr_control_str,
                        self.out_control,
                        i1c,
                        q1c,
                        pi_12=self.pi_12,
                    )
                    save(i1, i1_st)
                    save(q1, q1_st)
                    save(i1c, i1c_st)
                    save(q1c, q1c_st)

            n_t = len(self.t_list)
            with stream_processing():
                i0_st.buffer(n_t).average().save("I0")
                q0_st.buffer(n_t).average().save("Q0")
                i0c_st.buffer(n_t).average().save("I0c")
                q0c_st.buffer(n_t).average().save("Q0c")
                i1_st.buffer(n_t).average().save("I1")
                q1_st.buffer(n_t).average().save("Q1")
                i1c_st.buffer(n_t).average().save("I1c")
                q1c_st.buffer(n_t).average().save("Q1c")

        return ramsey

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

        fig = plt.figure()
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
        self.register_figure("simulation_ports", fig)
        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

    def _live_plot_loop(self, job):
        res_handles = job.result_handles
        i0_h = res_handles.get("I0")
        q0_h = res_handles.get("Q0")
        i1_h = res_handles.get("I1")
        q1_h = res_handles.get("Q1")
        i0c_h = res_handles.get("I0c")
        q0c_h = res_handles.get("Q0c")
        i1c_h = res_handles.get("I1c")
        q1c_h = res_handles.get("Q1c")

        for h in (i0_h, q0_h, i1_h, q1_h, i0c_h, q0c_h, i1c_h, q1c_h):
            h.wait_for_values(1)

        plt.ion()
        fig, ax = plt.subplots(2)
        fig.suptitle("Conditional Ramsey")
        lines = []
        tc = ["Target", "Control"]
        t_us = 4e-3 * self.t_list
        for i in range(2):
            lines.append(ax[i].plot(t_us, [0] * len(t_us), marker=".", label="0")[0])
            lines.append(ax[i].plot(t_us, [0] * len(t_us), marker=".", label="1")[0])
            ax[i].set_title(tc[i])
            ax[i].set_ylabel("Ramsey Amplitude")
            ax[i].grid()
            ax[i].legend()
        ax[1].set_xlabel("Time (us)")
        self.register_figure("live_conditional_ramsey", fig)

        while res_handles.is_processing():
            i0 = i0_h.fetch_all()
            q0 = q0_h.fetch_all()
            i1 = i1_h.fetch_all()
            q1 = q1_h.fetch_all()
            i0c = i0c_h.fetch_all()
            q0c = q0c_h.fetch_all()
            i1c = i1c_h.fetch_all()
            q1c = q1c_h.fetch_all()
            i_vals = [i0, i1, i0c, i1c]
            for i in range(2):
                lines[2 * i].set_ydata(i_vals[2 * i])
                lines[2 * i + 1].set_ydata(i_vals[2 * i + 1])
                ax[i].relim()
                ax[i].autoscale_view()
                fig.set_tight_layout(True)
                fig.canvas.draw()
                fig.canvas.flush_events()
            plt.pause(1)

        if not self.show_plot:
            plt.close(fig)

    def _analyze_and_plot(self, i0, q0, i1, q1, i0c, q0c, i1c, q1c):
        t_list_us = 4e-3 * self.t_list

        pars0, _ = curve_fit(
            f=_ramsey_fit_model,
            xdata=t_list_us,
            ydata=i0,
            p0=[(max(i0) - min(i0)) / 2, self.det_mhz, 50, np.pi, np.mean(i0)],
            bounds=(-np.inf, np.inf),
            maxfev=2000,
        )

        res_1, _, _ = ramsey_fitting(t_list_us, i1)
        pars1 = [res_1[0], res_1[3], res_1[1], res_1[4], res_1[2]]

        total_det = float(np.abs(np.round(abs(pars0[1]) - abs(pars1[1]), 4)))

        qc = str(self.q_control_no)
        qt = str(self.q_target_no)
        qc_f = q_LO[qc] + q_IF[qc]
        qt_f = q_LO[qt] + q_IF[qt]
        f_shift = total_det * 1e6
        zz_hz = f_shift / 2
        d1 = (q12_IF[qc] - q_IF[qc]) * 1e-6
        d2 = (q12_IF[qt] - q_IF[qt]) * 1e-6
        del12 = 1e-6 * (qc_f - qt_f)
        j_sq = -zz_hz * (del12 + d1) * (d2 - del12) / (d1 + d2)
        if j_sq > 0:
            j_hz = float(np.sqrt(j_sq))
        else:
            j_hz = float(np.sqrt(-j_sq))

        ring_c = qubit_to_ring_map[self.q_control_no][0]
        ring_t = qubit_to_ring_map[self.q_target_no][0]

        logger.info("Fitted Ramsey (control |0⟩ branch): f=%s MHz, T2*=%s µs", pars0[1], pars0[2])
        logger.info("Fitted Ramsey (control |1⟩ branch): f=%s MHz, T2*=%s µs", pars1[1], pars1[2])
        cprint(
            f"Total detuning |0⟩ vs |1⟩: {1e3 * total_det:.4g} kHz",
            "yellow",
            attrs=["bold"],
        )
        cprint(
            f"ZZ (half shift) estimate: {0.5 * total_det:.6g} MHz",
            "yellow",
            attrs=["bold"],
        )
        logger.info("Effective coupling J: %s MHz", j_hz * 1e-3)

        self.results["analysis"] = {
            "pars0": [float(x) for x in pars0],
            "pars1": [float(x) for x in pars1],
            "total_det_mhz": total_det,
            "zz_error_mhz": float(0.5 * total_det),
            "J_mhz": float(j_hz * 1e-3),
            "t_list_us": t_list_us.tolist(),
        }
        self.results["raw"] = {
            "I0": np.asarray(i0).tolist(),
            "Q0": np.asarray(q0).tolist(),
            "I1": np.asarray(i1).tolist(),
            "Q1": np.asarray(q1).tolist(),
            "I0c": np.asarray(i0c).tolist(),
            "Q0c": np.asarray(q0c).tolist(),
            "I1c": np.asarray(i1c).tolist(),
            "Q1c": np.asarray(q1c).tolist(),
        }

        fig, (ax_t, ax_c) = plt.subplots(
            2,
            1,
            figsize=(9, 7),
            sharex=True,
            constrained_layout=True,
        )
        ax_t.plot(t_list_us, i0, "-*", color="red")
        ax_t.plot(t_list_us, _ramsey_fit_model(t_list_us, *pars0), label=f"Control |0⟩  f={pars0[1]:.4f} MHz  T2*={pars0[2]:.1f} µs", color="red")
        ax_t.plot(t_list_us, i1, "--", color="blue")
        ax_t.plot(t_list_us, _ramsey_fit_model(t_list_us, *pars1), label=f"Control |1⟩  f={pars1[1]:.4f} MHz  T2*={pars1[2]:.1f} µs", color="blue")
        ax_t.set_ylabel("Signal")
        ax_t.set_title(
            f"Target (Ramsey) — Control R{ring_c} → Target R{ring_t}"
        )
        ax_t.legend(fontsize=8)
        ax_t.grid()

        # Coupling summary text box
        zz_khz = 0.5 * total_det * 1e3
        j_mhz = j_hz * 1e-3
        textstr = (
            f"Δf (|0⟩−|1⟩) = {1e3 * total_det:.2f} kHz\n"
            f"ZZ/2π  = {zz_khz:.3f} kHz\n"
            f"J/2π   = {j_mhz:.4f} MHz\n"
            f"Δ_ctrl  = {d1:.3f} MHz   Δ_tgt = {d2:.3f} MHz\n"
            f"δ₁₂     = {del12:.3f} MHz"
        )
        ax_t.text(
            0.98, 0.97, textstr,
            transform=ax_t.transAxes,
            fontsize=8,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", alpha=0.85),
            family="monospace",
        )

        ax_c.plot(t_list_us, i0c, "^", color="red", label="Control |0⟩")
        ax_c.plot(t_list_us, i1c, "^", color="blue", label="Control |1⟩")
        ax_c.set_xlabel("t (us)")
        ax_c.set_ylabel("Signal")
        ax_c.set_title(f"Control readout I | Control R{ring_c}, Target R{ring_t}")
        ax_c.legend()
        ax_c.grid()

        fig.suptitle(
            f"Conditional Ramsey: q{self.q_control_no} (control), q{self.q_target_no} (target)"
            f"  |  ZZ/2π = {zz_khz:.2f} kHz,  J/2π = {j_mhz:.3f} MHz",
            fontsize=11,
        )
        self.register_figure("conditional_ramsey_analysis", fig)

        if self.save_plot:
            panel_path = (
                str(self.path_to_save)
                + f"_q{self.q_control_no}_q{self.q_target_no}_conditional_ramsey_panels.png"
            )
            fig.savefig(panel_path, bbox_inches="tight", dpi=150)
            self.results["artifacts"].append(panel_path)
            logger.info("Saved figure: %s", panel_path)
            cprint(f"Figure saved: {Path(panel_path).resolve().as_uri()}", "green")

        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

        if self.save_data:
            file_saver_(
                np.transpose([t_list_us, i0, q0, i1, q1]),
                file_name=str(Path(__file__).resolve()),
                suffix=f"Control_{self.q_control_str}_Target_{self.q_target_str}",
                master_folder=self.data_master_folder,
                header_string="Time(us), I_0, Q_0, I_1, Q_1",
            )

        return self.results

    def update_coupling_json(self) -> None:
        """Write all derived coupling values for this pair to ``coupling_vals.json``."""
        an = self.results.get("analysis", {})
        if not an:
            logger.warning("coupling_vals update skipped: no analysis results.")
            return

        path = f"{self.config_files_path}/System_Parameters/coupling_vals.json"
        try:
            with open(path, "r", encoding="utf-8") as fh:
                cv = json.load(fh)
        except FileNotFoundError:
            cv = {}

        key = f"c{self.q_control_no}_t{self.q_target_no}"
        cv[key] = {
            "zz_khz": float(round(an["zz_error_mhz"] * 1e3, 6)),
            "J_mhz": float(round(an["J_mhz"], 6)),
            "total_det_mhz": float(round(an["total_det_mhz"], 6)),
            "f0_mhz": float(round(an["pars0"][1], 6)),
            "f1_mhz": float(round(an["pars1"][1], 6)),
            "T2star_0_us": float(round(an["pars0"][2], 3)),
            "T2star_1_us": float(round(an["pars1"][2], 3)),
        }

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(cv, fh, indent=2)
            fh.write("\n")

        self.results["updated_config"]["coupling_vals"] = {"path": path, "key": key, "values": cv[key]}
        logger.info("Updated coupling_vals.json [%s]: %s", key, cv[key])
        cprint(f"coupling_vals.json updated ({key}): {Path(path).resolve().as_uri()}", "cyan")

    def update_cross_kerr_json(self) -> None:
        """Write ZZ shifts to ``Configuration_Files/System_Parameters/CrossKerr.json`` (MHz on disk)."""
        ud = self.update_dict
        if ud is False or ud is None or (isinstance(ud, dict) and len(ud) == 0):
            return
        if "analysis" not in self.results or "zz_error_mhz" not in self.results["analysis"]:
            logger.warning("CrossKerr update skipped: no analysis results.")
            return

        path = f"{self.config_files_path}/System_Parameters/CrossKerr.json"
        with open(path, "r", encoding="utf-8") as fh:
            ck = json.load(fh)

        changes: Dict[str, Dict[str, float]] = {}
        if ud is True:
            key = str(self.q_target_no)
            new_val = float(self.results["analysis"]["zz_error_mhz"])
            old_val = float(ck.get(key, 0.0))
            ck[key] = new_val
            changes[key] = {"old_mhz": old_val, "new_mhz": new_val}
        elif isinstance(ud, dict):
            for k, v in ud.items():
                key = str(k)
                new_val = float(v)
                old_val = float(ck.get(key, 0.0))
                ck[key] = new_val
                changes[key] = {"old_mhz": old_val, "new_mhz": new_val}
        else:
            logger.warning("update_dict must be True or a non-empty dict; got %r", ud)
            return

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(ck, fh, indent=2)
            fh.write("\n")

        self.results["updated_config"]["cross_kerr"] = {"path": path, "changes": changes}
        logger.info("Updated CrossKerr.json: %s", changes)
        cprint(f"CrossKerr.json updated: {Path(path).resolve().as_uri()}", "green")

    def run(self):
        self._qmm = QuantumMachinesManager(host=qm_ip, cluster_name=cluster_name)
        try:
            if self.refresh_qm_config:
                self.refresh_qm_config_from_disk()

            ramsey = self._build_program()

            if self.simulate:
                sim_job = self._qmm.simulate(_qm_cfg.config, ramsey, SimulationConfig(int(10_000)))
                self._plot_simulation_ports(sim_job.get_simulated_samples())
                self.results["simulation_only"] = True
                raise Halted()

            self._qm = self._qmm.open_qm(_qm_cfg.config)
            job = self._qm.execute(ramsey)
            # print(job.execution_report())
            print(job.execution_report())

            if self.plot_live:
                self._live_plot_loop(job)
            else:
                job.result_handles.wait_for_all_values()

            rh = job.result_handles
            i0 = rh.get("I0").fetch_all()
            q0 = rh.get("Q0").fetch_all()
            i1 = rh.get("I1").fetch_all()
            q1 = rh.get("Q1").fetch_all()
            i0c = rh.get("I0c").fetch_all()
            q0c = rh.get("Q0c").fetch_all()
            i1c = rh.get("I1c").fetch_all()
            q1c = rh.get("Q1c").fetch_all()

            self._analyze_and_plot(i0, q0, i1, q1, i0c, q0c, i1c, q1c)
            self.update_coupling_json()
            self.update_cross_kerr_json()

            if self.save_data:
                out_json = str(self.path_to_save) + f"_q{self.q_control_no}_q{self.q_target_no}.json"
                self.save_json(self.results, out_json)
                self.results["artifacts"].append(out_json)
                logger.info("Saved results: %s", out_json)

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


def perform_conditional_ramsey_coupling_calc(
    control_qubit: int,
    target_qubit: int,
    **kwargs,
) -> ConditionalRamseyCouplingCalc:
    """
    Run conditional Ramsey and coupling-related analysis for one control–target pair.

    Parameters
    ----------
    control_qubit, target_qubit
        Same indexing as the legacy script: Ramsey is on ``target_qubit``; the π pulse
        is applied on ``control_qubit``.
    update_dict
        If ``True``, writes ``zz_error_mhz`` to ``CrossKerr.json`` for ``target_qubit``.
        If a ``dict`` of ``{qubit_id: mhz}``, merges those entries (MHz on disk).
    """
    exp = ConditionalRamseyCouplingCalc(q_list=[control_qubit, target_qubit], **kwargs)
    try:
        exp.run()
    except Halted:
        pass
    return exp


def perform_conditional_ramsey_coupling_for_pairs(
    pair_list: List[Tuple[int, int]],
    **kwargs,
) -> Dict[str, ConditionalRamseyCouplingCalc]:
    out = {}
    for control_qubit, target_qubit in pair_list:
        key = f"q{control_qubit}_q{target_qubit}"
        out[key] = perform_conditional_ramsey_coupling_calc(control_qubit, target_qubit, **kwargs)
    return out


if __name__ == "__main__":
    qubit_pairs = [
        [1,2],
        [2,1]
        # [3, 2],
        # [2, 3],
        # [4, 1],
        # [1, 4],
    ]
    for ctrl, target in qubit_pairs:
        perform_conditional_ramsey_coupling_calc(
            control_qubit=ctrl,
            target_qubit=target,
            save_data=True,
            show_plot=True,
            save_plot=True,
            simulate=False,
            plot_live=True,
            n_avg=200,
        )
