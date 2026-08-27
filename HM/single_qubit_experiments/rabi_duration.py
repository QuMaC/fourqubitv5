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
    save,
    stream_processing,

    fixed,
    amp,
    play,
)
from qm import QuantumMachinesManager, SimulationConfig
from qualang_tools.results import fetching_tool, progress_counter
from qualang_tools.plot import interrupt_on_close

from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json
from Helper_Functions.macros import cooldown, measure_macro
from Helper_Functions.analysis_functions import fit_cos
from Helper_Functions.spectro_helper import normalize, S2N_1

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class RabiDurationCalibration(SingleQubitExperiment):
    """
    Time-domain Rabi pulse-length calibration in HM experiment style.

    Rewrites Automation/Scripts/TimeDomain_Rabi_user_in.py into a reusable class.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="rabi_duration",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )
        # Sweep settings
        self.t_min_ns = int(kwargs.get("t_min_ns", 16))
        self.t_max_ns = int(kwargs.get("t_max_ns", 1000))
        self.dt_ns = int(kwargs.get("dt_ns", 4))
        self.rabi_amp = float(kwargs.get("rabi_amp", None))
        self.n_avgs = int(kwargs.get("n_avgs", 100000))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250000))
        if self.rabi_amp is None:
            self.rabi_amp = self.X180_amp

        # Readout / fitting behavior
        self.snr_stop = float(kwargs.get("snr_stop", 15.0))
        self.fit_skip_points = int(kwargs.get("fit_skip_points", 20))
        self.pi_12 = bool(kwargs.get("pi_12", False))
        self.dem = float(kwargs.get("dem", 3.123e-05))
        self.sim_duration_clk = int(kwargs.get("sim_duration_clk", 20000))
        self.sim_rep_rate_clk = int(kwargs.get("sim_rep_rate_clk", 100))

        # Update/save behavior
        self.update_config = bool(kwargs.get("update_config", True))
        self.update_lengths_if_slow = bool(kwargs.get("update_lengths_if_slow", True))
        self.save_data = bool(kwargs.get("save_data", False))

        # Internal results
        self.t_list_ns = None
        self.I = None
        self.Q = None
        self.fit_I = None
        self.fit_Q = None
        self.best_quadrature = "I"
        self.pi_len_ns_calibrated = None
        self.rabi_plot_amp = None
        self.guess_amp_for_power_rabi = None
        self.slow_flag = False
        self._qmm = None


    def _build_program(self):
        qe = self.q_str
        rr = self.rr_str
        out = self.out
        rep_rate_clk = self.sim_rep_rate_clk if self.simulate else self.rep_rate_clk

        t_min_raw = int(self.t_min_ns // 4)
        # QUA dynamic play durations must be >= 4 clock cycles.
        t_min = max(4, t_min_raw)
        t_max = int(self.t_max_ns // 4)
        dt = max(1, int(self.dt_ns // 4))
        if t_min != t_min_raw:
            logger.warning(
                f"t_min_ns={self.t_min_ns} ns is too short for QUA dynamic duration. "
                f"Using {4 * t_min} ns minimum instead."
            )
        if t_max <= t_min:
            raise ValueError(
                f"Invalid duration sweep: t_max_ns={self.t_max_ns} must be greater than "
                f"minimum allowed t_min_ns={4 * t_min}."
            )
        t_list_clk = np.arange(t_min, t_max, dt)
        self.t_list_ns = 4 * t_list_clk
        n_t_pts = len(t_list_clk)

        with program() as prog:
            n = declare(int)
            I = declare(fixed)
            Q = declare(fixed)
            t = declare(int)
            I_st = declare_stream()
            Q_st = declare_stream()
            n_st = declare_stream()

            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(t, t_min, t < t_max, t + dt):
                    cooldown(
                        time=rep_rate_clk,
                        active_reset=False,
                        qe=qe,
                        qe_12=None,
                        rr=rr,
                        out=out,
                        I=I,
                        Q=Q,
                        pi_12=False,
                        dem=self.dem,
                    )
                    play("grft" * amp(self.rabi_amp), qe, t)
                    measure_macro(qe, rr, out, I, Q, pi_12=self.pi_12)
                    save(I, I_st)
                    save(Q, Q_st)
                save(n, n_st)

            with stream_processing():
                I_st.buffer(n_t_pts).average().save("I")
                Q_st.buffer(n_t_pts).average().save("Q")
                n_st.save("iteration")

        return prog

    @staticmethod
    def _safe_fit_cos(t_ns: np.ndarray, trace: np.ndarray, skip_pts: int):
        idx0 = min(max(skip_pts, 0), max(len(t_ns) - 2, 0))
        return fit_cos(t_ns[idx0:], trace[idx0:])

    def run_experiment(self):
        prog = self._build_program()
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        if self.simulate:
            job = self._qmm.simulate(self.config, prog, SimulationConfig(int(self.sim_duration_clk)))
            samples = job.get_simulated_samples()
            # Plot controllers carrying q/rr outputs so generated pulses are visible.
            q_con = f"con{int(self.dac_mapping[self.q_str][0])}"
            rr_con = f"con{int(self.dac_mapping[self.rr_str][0])}"
            con_names = [q_con] if q_con == rr_con else [q_con, rr_con]
            plotted = False
            for con_name in con_names:
                con_samples = getattr(samples, con_name, None)
                if con_samples is not None:
                    con_samples.plot()
                    plotted = True
            if not plotted:
                # Fallback for unexpected mappings/configs.
                for con_name in ("con1", "con2", "con3", "con4"):
                    con_samples = getattr(samples, con_name, None)
                    if con_samples is not None:
                        con_samples.plot()
                        plotted = True
                        break
            plt.show()
            logger.info("Simulation completed; skipping hardware execution.")
            return

        qm = self._qmm.open_qm(self.config)
        try:
            job = qm.execute(prog)
            results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

            fig, axs = plt.subplots(2, 1, sharex=True)
            interrupt_on_close(fig, job)
            fit_error = False
            snr_i = 0.0
            snr_q = 0.0

            while results.is_processing():
                I, Q, iteration = results.fetch_all()
                progress_counter(iteration, self.n_avgs, start_time=results.get_start_time())

                try:
                    res_I = self._safe_fit_cos(self.t_list_ns, I, self.fit_skip_points)
                    res_Q = self._safe_fit_cos(self.t_list_ns, Q, self.fit_skip_points)
                    fit_error = False
                except RuntimeError:
                    fit_error = True
                    res_I = None
                    res_Q = None

                axs[0].cla()
                axs[1].cla()
                axs[0].plot(self.t_list_ns, I, marker=".", label="I")
                axs[1].plot(self.t_list_ns, Q, marker=".", label="Q")

                if not fit_error:
                    axs[0].plot(self.t_list_ns, res_I["fitfunc"](self.t_list_ns), label="I_fit")
                    axs[1].plot(self.t_list_ns, res_Q["fitfunc"](self.t_list_ns), label="Q_fit")
                    pi_time_i = 0.5 * float(res_I["period"])
                    pi_time_q = 0.5 * float(res_Q["period"])
                    snr_i, _ = S2N_1(normalize(I))
                    snr_q, _ = S2N_1(normalize(Q))
                    if snr_i >= snr_q:
                        fig.suptitle(f"Time Rabi: Pi time = {pi_time_i:.2f} ns for amp = {self.rabi_amp:.3f}")
                    else:
                        fig.suptitle(f"Time Rabi: Pi time = {pi_time_q:.2f} ns for amp = {self.rabi_amp:.3f}")
                    if snr_i > self.snr_stop or snr_q > self.snr_stop:
                        job.halt()
                else:
                    fig.suptitle("Time Rabi: waiting for stable fit...")

                for ax in axs:
                    ax.set(xlabel="Time (ns)", ylabel="Rabi amplitude")
                    ax.grid(True)
                    ax.legend()
                    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                plt.tight_layout()
                plt.pause(0.25)

            self.I = np.asarray(job.result_handles.get("I").fetch_all())
            self.Q = np.asarray(job.result_handles.get("Q").fetch_all())
        finally:
            try:
                qm.close()
            except Exception:
                pass

    def analyze_and_plot(self):
        if self.I is None or self.Q is None:
            raise RuntimeError("No data to analyze. Run run_experiment() first.")

        self.fit_I = fit_cos(self.t_list_ns, self.I)
        self.fit_Q = fit_cos(self.t_list_ns, self.Q)

        snr_i, _ = S2N_1(normalize(self.I))
        snr_q, _ = S2N_1(normalize(self.Q))

        if snr_i >= snr_q:
            self.best_quadrature = "I"
            fit = self.fit_I
            trace = self.I
        else:
            self.best_quadrature = "Q"
            fit = self.fit_Q
            trace = self.Q

        self.pi_len_ns_calibrated = 0.5 * float(fit["period"])
        self.rabi_plot_amp = float(fit["amp"])
        self.guess_amp_for_power_rabi = float(
            self.rabi_amp * (self.pi_len_ns_calibrated / float(self.pi_len_ns))
        )

        logger.info(f"Pi pulse = {self.pi_len_ns_calibrated:.2f} ns")
        logger.info(f"Rabi plot amplitude = {abs(self.rabi_plot_amp):.6g}")
        logger.info(f"Guess amp for Power Rabi = {self.guess_amp_for_power_rabi:.3f}")

        fig, ax = plt.subplots()
        ax.plot(self.t_list_ns, trace, ".", label=self.best_quadrature)
        ax.plot(self.t_list_ns, fit["fitfunc"](self.t_list_ns), "-", label=f"{self.best_quadrature}_fit")
        ax.set_xlabel("Time (ns)")
        ax.set_ylabel("Rabi amplitude")
        ax.set_title(
            f"Time Rabi q{self.q_no}: Pi = {self.pi_len_ns_calibrated:.2f} ns, "
            f"guess amp = {self.guess_amp_for_power_rabi:.3f}"
        )
        ax.grid(True)
        ax.legend()
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

        save_path = str(self.path_to_save) + f"_q{self.q_no}.png"
        fig.savefig(save_path, bbox_inches="tight")
        cprint(f"Figure saved: {Path(save_path).as_uri()}", "green")
        plt.show(block=False)

    def update_config_dicts(self):
        if not self.update_config:
            return
        if self.pi_len_ns_calibrated is None:
            raise RuntimeError("No fit result to update config.")

        q_key = str(self.q_no)
        scale = self.guess_amp_for_power_rabi
        mixer_sat_pwr = 1.1 if scale > 0.4 else 1.0
        mixer_sat_pwr_piby2 = 1.1 if scale > 0.7 else 1.0

        amp_scale_path = self.config_files_path + "/Pulse_Calibrations/amp_scale.json"
        with open(amp_scale_path, "r") as fh:
            amp_scale = json.load(fh)

        if scale < 1.0:
            amp_scale[q_key]["X180"] = float(scale * mixer_sat_pwr)
            amp_scale[q_key]["Y180"] = float(scale * mixer_sat_pwr)
            amp_scale[q_key]["X90"] = float(scale * 0.5 * mixer_sat_pwr_piby2)
            amp_scale[q_key]["Y90"] = float(scale * 0.5 * mixer_sat_pwr_piby2)
            self.slow_flag = False
        else:
            self.slow_flag = True
            amp_scale[q_key]["X180"] = float(self.rabi_amp)
            amp_scale[q_key]["Y180"] = float(self.rabi_amp)
            amp_scale[q_key]["X90"] = float(self.rabi_amp / 2)
            amp_scale[q_key]["Y90"] = float(self.rabi_amp / 2)

        with open(amp_scale_path, "w") as fh:
            json.dump(amp_scale, fh, indent=6)

        # Optional pulse-length stretch when Rabi is too slow (legacy behavior).
        if self.slow_flag and self.update_lengths_if_slow:
            new_len_ns = int(((self.rabi_amp * self.pi_len_ns_calibrated // 4) + 1) * 4) * 3
            pi_len_path = self.config_files_path + "/Pulse_Calibrations/pi_len_ns.json"
            piby2_len_path = self.config_files_path + "/Pulse_Calibrations/piby2_len_ns.json"

            with open(pi_len_path, "r") as fh:
                pi_vals = json.load(fh)
            with open(piby2_len_path, "r") as fh:
                piby2_vals = json.load(fh)

            pi_vals[q_key] = int(new_len_ns)
            piby2_vals[q_key] = int(new_len_ns)

            with open(pi_len_path, "w") as fh:
                json.dump(pi_vals, fh, indent=6)
            with open(piby2_len_path, "w") as fh:
                json.dump(piby2_vals, fh, indent=6)
            logger.info(f"Rabi too slow; updated pulse lengths to {new_len_ns} ns")

        # Update calib_vals used by power-rabi amplitude calibration.
        calib_vals_path = self.config_files_path + "/Pulse_Calibrations/calib_vals.json"
        with open(calib_vals_path, "r") as fh:
            calib_vals = json.load(fh)

        x180 = float(amp_scale[q_key]["X180"])
        calib_vals[q_key]["amin"] = float(0.85 * x180)
        calib_vals[q_key]["amax"] = float(min(1.0, 1.15 * x180))
        calib_vals[q_key]["da"] = float(scale * 0.3 / 100.0)
        calib_vals[q_key]["n_pulses"] = int(7 if self.slow_flag else 5)

        with open(calib_vals_path, "w") as fh:
            json.dump(calib_vals, fh, indent=6)

        logger.info(
            f"Updated amp_scale + calib_vals for q{self.q_no} | "
            f"X180={amp_scale[q_key]['X180']:.6f}, X90={amp_scale[q_key]['X90']:.6f}"
        )

    def save_experiment_data(self):
        fit_I = {k: v for k, v in self.fit_I.items() if k not in ("fitfunc", "rawres")}
        fit_Q = {k: v for k, v in self.fit_Q.items() if k not in ("fitfunc", "rawres")}
        payload = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "rabi_amp": self.rabi_amp,
            "n_avgs": self.n_avgs,
            "t_list_ns": self.t_list_ns,
            "I": self.I,
            "Q": self.Q,
            "best_quadrature": self.best_quadrature,
            "pi_len_ns_calibrated": self.pi_len_ns_calibrated,
            "guess_amp_for_power_rabi": self.guess_amp_for_power_rabi,
            "fit_data_I": fit_I,
            "fit_data_Q": fit_Q,
        }
        json_path = str(self.path_to_save) + f"_q{self.q_no}.json"
        save_json(payload, json_path)
        cprint(f"Data saved: {Path(json_path).as_uri()}", "green")
        return payload

    def run(self):
        t0 = time.time()
        try:
            self.run_experiment()
            if self.simulate:
                logger.info("Simulation mode enabled; skipped analysis and config updates.")
                return None
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
        return self.pi_len_ns_calibrated


def perform_rabi_duration(q_no: int, rr_no: int = None, **kwargs):
    """Instantiate RabiDurationCalibration, run full sequence, return object."""
    exp = RabiDurationCalibration(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    q_list = [
        1,
    ]
    for q in q_list:
        perform_rabi_duration(
            q_no=q,
            t_min_ns=16,
            t_max_ns=64,
            dt_ns=16,
            rabi_amp=0.8,
            n_avgs=1,
            update_config=False,
            save_data=False,
            simulate=True,
        )
