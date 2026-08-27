import time
import json
import logging
from pathlib import Path

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
    update_frequency,
    save,
    stream_processing,
    fixed,
    align,
)
from qm import QuantumMachinesManager, SimulationConfig
from qualang_tools.loops import from_array

from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json
from Helper_Functions.macros import cooldown, measure_macro, play_X180

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class ReadoutDispersiveShift(SingleQubitExperiment):
    
    """
    QUA resonator sweep with 3 prepared qubit states:
      - |g> (ground)
      - |e> (first excited)
      - |f> (second excited, prepared by X180 on q and X180 on q12)

    The analysis overlays all three resonator responses so the three dispersive
    dips are directly visible on one figure.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="readout_dispersive_shift",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )

        self.n_avgs = int(kwargs.get("n_avgs", 400))
        self.sweep_span_MHz = float(kwargs.get("sweep_span_MHz", 20.0))
        self.df_kHz = float(kwargs.get("df_kHz", 10.0))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", max(2000, int(self.ro_len) + 4)))
        self.simulate = bool(kwargs.get("simulate", False))
        self.save_data = bool(kwargs.get("save_data", True))
        self.apply_elec_delay_phase_corr = bool(kwargs.get("apply_elec_delay_phase_corr", True))
        self.sim_duration_clk = int(kwargs.get("sim_duration_clk", 60000))

        self.freq_list_hz = self._build_frequency_axis()
        self.freq_list_ghz = None

        self.Ig = None
        self.Qg = None
        self.Ie = None
        self.Qe = None
        self.If = None
        self.Qf = None

        self.results = {}
        self.dispersive_shifts_kHz = {}
        self._qmm = None

    def _build_frequency_axis(self) -> np.ndarray:
        center_if_hz = int(round(float(self.rr_if)))
        half_span_hz = int(round(0.5 * self.sweep_span_MHz * 1e6))
        df_hz = max(1, int(round(self.df_kHz * 1e3)))
        f_start = center_if_hz - half_span_hz
        f_stop = center_if_hz + half_span_hz
        freqs = np.arange(f_start, f_stop, df_hz, dtype=int)
        if freqs.size < 3:
            raise ValueError(
                "Frequency axis has too few points. Increase sweep_span_MHz or decrease df_kHz."
            )
        return freqs

    def _build_program(self):
        qe = self.q_str
        rr = self.rr_str
        out = self.out
        n_freqs = int(len(self.freq_list_hz))

        with program() as prog:
            n = declare(int)
            f = declare(int)

            Ig = declare(fixed)
            Qg = declare(fixed)
            Ie = declare(fixed)
            Qe = declare(fixed)
            If_ = declare(fixed)
            Qf = declare(fixed)

            Ig_st = declare_stream()
            Qg_st = declare_stream()
            Ie_st = declare_stream()
            Qe_st = declare_stream()
            If_st = declare_stream()
            Qf_st = declare_stream()

            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(*from_array(f, self.freq_list_hz)):
                    update_frequency(rr, f)

                    # |g>
                    cooldown(time=self.rep_rate_clk, qe=qe)
                    measure_macro(qe, rr, out, Ig, Qg, pi_12=False)
                    save(Ig, Ig_st)
                    save(Qg, Qg_st)

                    # |e> = X180 |g>
                    align()
                    cooldown(time=self.rep_rate_clk, qe=qe)
                    play_X180(qe)
                    measure_macro(qe, rr, out, Ie, Qe, pi_12=False)
                    save(Ie, Ie_st)
                    save(Qe, Qe_st)

                    # |f> = X180_ef X180_ge |g>
                    # measure_macro(..., pi_12=True) applies the q12 pulse.
                    align()
                    cooldown(time=self.rep_rate_clk, qe=qe)
                    play_X180(qe)
                    measure_macro(qe, rr, out, If_, Qf, pi_12=True)
                    save(If_, If_st)
                    save(Qf, Qf_st)

            with stream_processing():
                Ig_st.buffer(n_freqs).average().save("Ig")
                Qg_st.buffer(n_freqs).average().save("Qg")
                Ie_st.buffer(n_freqs).average().save("Ie")
                Qe_st.buffer(n_freqs).average().save("Qe")
                If_st.buffer(n_freqs).average().save("If")
                Qf_st.buffer(n_freqs).average().save("Qf")

        return prog

    def run_experiment(self):
        prog = self._build_program()
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)

        if self.simulate:
            job = self._qmm.simulate(self.config, prog, SimulationConfig(duration=self.sim_duration_clk))
            samples = job.get_simulated_samples()
            q_con = f"con{int(self.dac_mapping[self.q_str][0])}"
            rr_con = f"con{int(self.dac_mapping[self.rr_str][0])}"
            con_names = [q_con] if q_con == rr_con else [q_con, rr_con]
            for con_name in con_names:
                con = getattr(samples, con_name, None)
                if con is not None:
                    con.plot()
            plt.show()
            logger.info("Simulation completed; skipping hardware fetch.")
            return

        qm = self._qmm.open_qm(self.config)
        try:
            job = qm.execute(prog)
            job.result_handles.wait_for_all_values()
            self.Ig = np.asarray(job.result_handles.get("Ig").fetch_all(), dtype=float)
            self.Qg = np.asarray(job.result_handles.get("Qg").fetch_all(), dtype=float)
            self.Ie = np.asarray(job.result_handles.get("Ie").fetch_all(), dtype=float)
            self.Qe = np.asarray(job.result_handles.get("Qe").fetch_all(), dtype=float)
            self.If = np.asarray(job.result_handles.get("If").fetch_all(), dtype=float)
            self.Qf = np.asarray(job.result_handles.get("Qf").fetch_all(), dtype=float)
        finally:
            try:
                qm.close()
            except Exception:
                pass

    def _state_analysis(self, I: np.ndarray, Q: np.ndarray) -> dict:
        signal_raw = I + 1j * Q
        signal = signal_raw.copy()

        if self.apply_elec_delay_phase_corr:
            e_delay_ns = float(self.elec_delay_ns)
            p_offset_rad = float(self.phase_offset_rad)
            signal = signal * np.exp(1j * 2 * np.pi * self.freq_list_ghz * e_delay_ns + 1j * p_offset_rad)

        mag = np.abs(signal)
        phase = np.angle(signal)
        real = np.real(signal)
        idx = int(np.argmin(mag))
        f_res = float(self.freq_list_ghz[idx])
        return {
            "signal": signal,
            "phase": phase,
            "real": real,
            "mag": mag,
            "idx_res": idx,
            "f_res_ghz": f_res,
        }

    def analyze_and_plot(self):
        if self.simulate:
            return {}
        if any(x is None for x in (self.Ig, self.Qg, self.Ie, self.Qe, self.If, self.Qf)):
            raise RuntimeError("No acquired data. Call run_experiment() first.")

        self.freq_list_ghz = self.rr_lo_val_MHz * 1e-3 + self.freq_list_hz * 1e-9

        self.results = {
            "g": self._state_analysis(self.Ig, self.Qg),
            "e": self._state_analysis(self.Ie, self.Qe),
            "f": self._state_analysis(self.If, self.Qf),
        }

        f_g = self.results["g"]["f_res_ghz"]
        f_e = self.results["e"]["f_res_ghz"]
        f_f = self.results["f"]["f_res_ghz"]
        self.dispersive_shifts_kHz = {
            "g-e": float((f_e - f_g) * 1e6),
            "e-f": float((f_f - f_e) * 1e6),
            "g-f": float((f_f - f_g) * 1e6),
        }

        fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharex=True)
        state_colors = {"g": "tab:blue", "e": "tab:red", "f": "tab:green"}
        labels = {"g": "|g>", "e": "|e>", "f": "|f>"}

        for st in ("g", "e", "f"):
            res = self.results[st]
            color = state_colors[st]
            lbl = labels[st]
            axes[0].plot(self.freq_list_ghz, res["phase"], color=color, label=lbl)
            axes[1].plot(self.freq_list_ghz, res["real"], color=color, label=lbl)
            axes[2].plot(self.freq_list_ghz, res["mag"], color=color, label=lbl)
            for ax in axes:
                ax.axvline(res["f_res_ghz"], linestyle="--", color=color, alpha=0.7)
            axes[2].plot(
                res["f_res_ghz"],
                res["mag"][res["idx_res"]],
                marker="o",
                color=color,
                markersize=5,
            )

        axes[0].set_title("Phase")
        axes[0].set_ylabel("rad")
        axes[1].set_title("Real(IQ)")
        axes[1].set_ylabel("a.u.")
        axes[2].set_title("Magnitude (three dips)")
        axes[2].set_ylabel("a.u.")

        for ax in axes:
            ax.set_xlabel("Frequency (GHz)")
            ax.grid(True)
            ax.legend(fontsize=9)

        fig.suptitle(
            f"Readout dispersive dips q{self.q_no}/rr{self.rr_no} | "
            f"g-e: {self.dispersive_shifts_kHz['g-e']:.1f} kHz, "
            f"e-f: {self.dispersive_shifts_kHz['e-f']:.1f} kHz, "
            f"g-f: {self.dispersive_shifts_kHz['g-f']:.1f} kHz"
        )
        plt.tight_layout()

        save_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}.png"
        fig.savefig(save_path, bbox_inches="tight")
        self.register_figure("readout_dispersive_shift", fig)
        cprint(f"Figure saved: {Path(save_path).as_uri()}", "green")
        plt.show(block=False)
        return self.results

    def save_experiment_data(self):
        if self.simulate:
            return None
        if not self.results:
            raise RuntimeError("No analyzed data to save. Call analyze_and_plot() first.")

        payload = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "n_avgs": self.n_avgs,
            "sweep_span_MHz": self.sweep_span_MHz,
            "df_kHz": self.df_kHz,
            "rep_rate_clk": self.rep_rate_clk,
            "rr_lo_MHz": self.rr_lo_val_MHz,
            "rr_if_center_Hz": float(self.rr_if),
            "freq_list_hz": self.freq_list_hz,
            "freq_list_ghz": self.freq_list_ghz,
            "state_data": {
                "g": {"I": self.Ig, "Q": self.Qg},
                "e": {"I": self.Ie, "Q": self.Qe},
                "f": {"I": self.If, "Q": self.Qf},
            },
            "resonances_ghz": {
                "g": float(self.results["g"]["f_res_ghz"]),
                "e": float(self.results["e"]["f_res_ghz"]),
                "f": float(self.results["f"]["f_res_ghz"]),
            },
            "dispersive_shifts_kHz": self.dispersive_shifts_kHz,
            "apply_elec_delay_phase_corr": self.apply_elec_delay_phase_corr,
            "elec_delay_ns": float(self.elec_delay_ns),
            "phase_offset_rad": float(self.phase_offset_rad),
        }
        json_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}.json"
        save_json(payload, json_path)
        cprint(f"Data saved: {Path(json_path).as_uri()}", "green")
        return payload

    def run(self):
        t0 = time.time()
        try:
            self.run_experiment()
            if not self.simulate:
                self.analyze_and_plot()
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
        return self.results


def perform_readout_dispersive_shift(q_no: int, rr_no: int = None, **kwargs):
    exp = ReadoutDispersiveShift(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    for q in [
        # 1,
        # 2,
        # 3,
        4,
    ]:
        perform_readout_dispersive_shift(
            q_no=q,
            n_avgs=300,
            sweep_span_MHz=20,
            df_kHz=10,
            rep_rate_clk=250000,
            save_data=True,
            simulate=False,
        )
