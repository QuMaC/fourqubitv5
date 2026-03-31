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
    int as qua_int,
    amp,
    play,
    wait,
)
from qm import QuantumMachinesManager
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


class RabiAmplitudePrecisionCalibration(SingleQubitExperiment):
    """
    Precision power-Rabi around current calibrated amplitudes.

    HM-style rewrite of Automation/Scripts/PulseCalib_Power-Rabi_precision_user_in.py.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="rabi_amp_precision",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )

        self.n_avgs = int(kwargs.get("n_avgs", 200))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250000))
        self.wait_q = int(kwargs.get("wait_q", 4))
        self.wait_rr = int(kwargs.get("wait_rr", 16))
        self.n_pulses = int(kwargs.get("n_pulses", 25))
        self.n_fit_points = int(kwargs.get("n_fit_points", 2000))
        self.snr_stop = float(kwargs.get("snr_stop", 15.0))
        self.peak = bool(kwargs.get("peak", True))
        self.pi_12 = bool(kwargs.get("pi_12", True))
        self.update_config = bool(kwargs.get("update_config", True))
        self.save_data = bool(kwargs.get("save_data", False))
        self.pulse_name = str(kwargs.get("pulse_name", "grft"))
        self.calibs = kwargs.get("calibs", ["Pi", "Piby2"])
        self.save_legacy_fit_json = bool(kwargs.get("save_legacy_fit_json", False))

        amp_scale_path = self.config_files_path + "/Pulse_Calibrations/amp_scale.json"
        with open(amp_scale_path, "r") as fh:
            self.amp_scale_dict = json.load(fh)

        self.results_by_calib = {}
        self.fit_params_by_calib = {}
        self.best_amp_by_calib = {}
        self._qmm = None

    def _get_amp_sweep(self, calib: str):
        center = float(self.amp_scale_dict[str(self.q_no)]["X180"])
        a_min = center * 0.97
        a_max = center * 1.03
        da = center * 0.06 / 1250.0
        if calib == "Piby2":
            a_min *= 0.5
            a_max *= 0.5
            da *= 0.5
        amps = np.arange(a_min, a_max + da / 2, da)
        return amps, a_min, a_max, da

    def _build_program(self, amps: np.ndarray, calib: str):
        qe = self.q_str
        rr = self.rr_str
        out = self.out

        a_min = float(amps[0])
        a_max = float(amps[-1])
        da = float(amps[1] - amps[0]) if len(amps) > 1 else 1e-4
        n_amp_pts = int(len(amps))
        pulse_multiplier = 2 if calib == "Piby2" else 1

        ro_clk = int(self.ro_len)
        cooldown_time = max(
            4,
            int(
                self.rep_rate_clk
                - self.n_pulses * (self.pi_len_ns + pulse_multiplier * self.wait_q)
                - self.wait_rr
                - ro_clk
            ),
        )

        with program() as prog:
            n = declare(qua_int)
            i = declare(qua_int)
            I = declare(fixed)
            Q = declare(fixed)
            a = declare(fixed)
            I_st = declare_stream()
            Q_st = declare_stream()
            n_st = declare_stream()

            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(a, a_min, a < a_max + da / 2, a + da):
                    cooldown(
                        time=cooldown_time,
                        active_reset=False,
                        qe=qe,
                        qe_12=None,
                        rr=rr,
                        out=out,
                        I=I,
                        Q=Q,
                        pi_12=False,
                        dem=0,
                    )

                    with for_(i, 0, i < self.n_pulses, i + 1):
                        play(self.pulse_name * amp(a), qe)
                        wait(self.wait_q, qe)
                        if calib == "Piby2":
                            play(self.pulse_name * amp(a), qe)
                            wait(self.wait_q, qe)

                    measure_macro(qe, rr, out, I, Q, pi_12=self.pi_12)
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

    def _fit_trace(self, amps: np.ndarray, I: np.ndarray):
        coeff = np.polyfit(amps, I, 4)
        amp_dense = np.linspace(float(amps[0]), float(amps[-1]), self.n_fit_points)
        fit_dense = self._poly4(amp_dense, *coeff)
        if self.peak:
            best_amp = float(amp_dense[int(np.argmax(fit_dense))])
        else:
            best_amp = float(amp_dense[int(np.argmin(fit_dense))])
        return coeff, best_amp, amp_dense, fit_dense

    def _run_one_calib(self, qm, calib: str):
        amps, a_min, a_max, da = self._get_amp_sweep(calib)
        prog = self._build_program(amps, calib)
        job = qm.execute(prog)
        results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

        fig, ax = plt.subplots()
        interrupt_on_close(fig, job)
        while results.is_processing():
            I, Q, iteration = results.fetch_all()
            progress_counter(iteration, self.n_avgs, start_time=results.get_start_time())
            ax.cla()
            ax.plot(amps, I, ".-", label="I")
            ax.set(xlabel="Pulse amplitude", ylabel="Rabi response (a.u.)")
            ax.grid(True)
            ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
            ax.legend()
            fig.suptitle(f"Precision Power Rabi q{self.q_no} - {calib}")
            plt.tight_layout()
            plt.pause(0.2)

            snr_i, _ = S2N_1(normalize(I))
            if snr_i > self.snr_stop:
                job.halt()

        plt.close(fig)
        I = np.asarray(job.result_handles.get("I").fetch_all())
        Q = np.asarray(job.result_handles.get("Q").fetch_all())

        coeff, best_amp, amp_dense, fit_dense = self._fit_trace(amps, I)
        logger.info(f"{calib} precision amplitude = {best_amp:.8f}")

        self.results_by_calib[calib] = {
            "amps": amps,
            "I": I,
            "Q": Q,
            "a_min": a_min,
            "a_max": a_max,
            "da": da,
            "n_pulses": self.n_pulses,
        }
        self.fit_params_by_calib[calib] = {
            "power0": float(coeff[0]),
            "power1": float(coeff[1]),
            "power2": float(coeff[2]),
            "power3": float(coeff[3]),
            "power4": float(coeff[4]),
            "gate_amp": float(best_amp),
        }
        self.best_amp_by_calib[calib] = best_amp

        fig2, ax2 = plt.subplots()
        ax2.plot(amps, I, ".", label="I data")
        ax2.plot(amp_dense, fit_dense, "-", label="4th order fit")
        ax2.axvline(best_amp, color="k", linestyle="--", label=f"Best amp={best_amp:.6f}")
        ax2.set_xlabel("Drive amplitude")
        ax2.set_ylabel("Rabi response (a.u.)")
        ax2.set_title(f"Precision Power Rabi q{self.q_no} - {calib} | N={self.n_pulses}")
        ax2.grid(True)
        ax2.legend()
        ax2.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        plot_path = str(self.path_to_save) + f"_q{self.q_no}_{calib}.png"
        fig2.savefig(plot_path, bbox_inches="tight")
        cprint(f"Figure saved: {Path(plot_path).as_uri()}", "green")
        plt.show(block=False)

    def run_experiment(self):
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        qm = self._qmm.open_qm(self.config)
        try:
            for calib in self.calibs:
                logger.info(f"Running precision power Rabi for q{self.q_no}: {calib}")
                self._run_one_calib(qm, calib)
        finally:
            try:
                qm.close()
            except Exception:
                pass

    def analyze_and_plot(self):
        return self.best_amp_by_calib

    def update_config_dicts(self):
        if not self.update_config:
            return

        amp_scale_path = self.config_files_path + "/Pulse_Calibrations/amp_scale.json"
        with open(amp_scale_path, "r") as fh:
            amp_scale = json.load(fh)

        q_key = str(self.q_no)
        amp_scale.setdefault(q_key, {})
        for calib, val in self.best_amp_by_calib.items():
            if calib == "Pi":
                amp_scale[q_key]["X180"] = float(val)
                amp_scale[q_key]["Y180"] = float(val)
                logger.info(f"amp_scale[{q_key}][X180/Y180] = {val:.8f}")
            elif calib == "Piby2":
                amp_scale[q_key]["X90"] = float(val)
                amp_scale[q_key]["Y90"] = float(val)
                logger.info(f"amp_scale[{q_key}][X90/Y90] = {val:.8f}")

        with open(amp_scale_path, "w") as fh:
            json.dump(amp_scale, fh, indent=6)

        if self.save_legacy_fit_json:
            legacy_path = self.config_files_path + "/power_rabi_fit.json"
            with open(legacy_path, "w") as fh:
                json.dump(self.fit_params_by_calib, fh, indent=6)
            logger.info(f"Legacy fit file updated: {legacy_path}")

    def save_experiment_data(self):
        payload = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "n_avgs": self.n_avgs,
            "rep_rate_clk": self.rep_rate_clk,
            "wait_q": self.wait_q,
            "wait_rr": self.wait_rr,
            "n_pulses": self.n_pulses,
            "pulse_name": self.pulse_name,
            "peak": self.peak,
            "pi_12": self.pi_12,
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


def perform_rabi_amp_precision(q_no: int, rr_no: int = None, **kwargs):
    """Instantiate precision Rabi amplitude calibration, run it, return object."""
    exp = RabiAmplitudePrecisionCalibration(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    q_list = [
        3,
    ]
    for q in q_list:
        perform_rabi_amp_precision(
            q_no=q,
            n_avgs=200,
            n_pulses=25,
            pi_12=True,
            update_config=True,
            save_data=False,
        )
