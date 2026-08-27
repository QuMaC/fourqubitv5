import json
import logging
import time
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
    fixed,
    for_,
    play,
    program,
    save,
    stream_processing,
    update_frequency,
    wait,
)
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import fetching_tool, progress_counter
from scipy.optimize import curve_fit
try:
    from termcolor import cprint
except Exception:
    def cprint(msg, *args, **kwargs):
        print(msg)

from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json
from Helper_Functions.macros import cooldown, measure_macro
from Helper_Functions.spectro_helper import normalize
from Helper_Functions.helper_functionsv2 import S2N

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


def _ramsey_model(t_us, amp, tau_us, offset, freq_mhz, phase):
    return amp * np.exp(-t_us / tau_us) * np.sin(2 * np.pi * freq_mhz * t_us + phase) + offset


class RamseyDetuning(SingleQubitExperiment):
    """
    Single Ramsey experiment with adaptive time-window/mesh checks.

    This mirrors the legacy Ramsey detuning script but follows the
    SingleQubitExperiment class structure used in HM experiments.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="ramsey_detuning",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )
        self.n_avgs = int(kwargs.get("n_avgs", 1000))
        self.detuning_mhz = float(kwargs.get("detuning_mhz", 1.0))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250_000))
        self.active_reset = bool(kwargs.get("active_reset", False))
        self.update_time_limits = bool(kwargs.get("update_time_limits", True))
        self.save_data = bool(kwargs.get("save_data", True))
        self.snr_fit_threshold = float(kwargs.get("snr_fit_threshold", 5.0))
        self.snr_stop_threshold = float(kwargs.get("snr_stop_threshold", 30.0))
        self.min_avg_bound = int(kwargs.get("min_avg_bound", 70))
        self.plot_live = bool(kwargs.get("plot_live", True))

        self.ramsey_limits_path = self.config_files_path + "/Pulse_Calibrations/ramsey_time_limits.json"
        self.redo_flag_path = self.single_qubit_experiments_path + "/cached_jsons/ramsey_redo.json"
        self.cache_path = self.single_qubit_experiments_path + "/cached_jsons/ramsey_cache_json.json"

        self._time_limits = self._load_time_limits()
        # Optional explicit overrides:
        # - t_min_ns, t_max_ns, dt_ns (preferred)
        # - t_min_clk, t_max_clk, dt_clk
        t_min_ns_override = kwargs.get("t_min_ns", None)
        t_max_ns_override = kwargs.get("t_max_ns", None)
        dt_ns_override = kwargs.get("dt_ns", None)
        t_min_clk_override = kwargs.get("t_min_clk", None)
        t_max_clk_override = kwargs.get("t_max_clk", None)
        dt_clk_override = kwargs.get("dt_clk", None)

        self.t_min_clk = int(self._time_limits["t_min"] // self.clock_cycle_dur_ns)
        self.t_max_clk = int(self._time_limits["t_max"] // self.clock_cycle_dur_ns)
        self.dt_clk = int(max(1, self._time_limits["dt"] // self.clock_cycle_dur_ns))

        if t_min_ns_override is not None:
            self.t_min_clk = int(float(t_min_ns_override) // self.clock_cycle_dur_ns)
        elif t_min_clk_override is not None:
            self.t_min_clk = int(t_min_clk_override)

        if t_max_ns_override is not None:
            self.t_max_clk = int(float(t_max_ns_override) // self.clock_cycle_dur_ns)
        elif t_max_clk_override is not None:
            self.t_max_clk = int(t_max_clk_override)

        if dt_ns_override is not None:
            self.dt_clk = int(max(1, float(dt_ns_override) // self.clock_cycle_dur_ns))
        elif dt_clk_override is not None:
            self.dt_clk = int(max(1, int(dt_clk_override)))

        if self.t_max_clk <= self.t_min_clk:
            raise ValueError("t_max must be greater than t_min.")

        self.t_list_clk = np.arange(self.t_min_clk, self.t_max_clk, self.dt_clk, dtype=int)
        if self.t_list_clk.size < 6:
            raise ValueError("Ramsey sweep has too few points. Increase t_max or reduce dt.")
        self.t_list_us = self.t_list_clk * self.clock_cycle_dur_ns * 1e-3

        self._qmm = None
        self._qm = None
        self._I = None
        self._Q = None
        self._fit_params = None

        self.results = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "params": {
                "n_avgs": self.n_avgs,
                "min_avg_bound": self.min_avg_bound,
                "detuning_mhz": self.detuning_mhz,
                "rep_rate_clk": self.rep_rate_clk,
                "t_min_clk": int(self.t_min_clk),
                "t_max_clk": int(self.t_max_clk),
                "dt_clk": int(self.dt_clk),
                "update_time_limits": self.update_time_limits,
            },
            "flags": {"redo": False},
            "figures": [],
        }

    def _load_time_limits(self):
        default_limits = {"t_min": 16, "t_max": 30_000, "dt": 100}
        q_key = str(self.q_no)
        payload = {}
        try:
            with open(self.ramsey_limits_path, "r") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError):
            payload = {}

        if q_key not in payload:
            payload[q_key] = default_limits
            with open(self.ramsey_limits_path, "w") as fh:
                json.dump(payload, fh, indent=2)
        return payload[q_key]

    @staticmethod
    def _fit_ramsey_trace(t_us: np.ndarray, y: np.ndarray):
        if len(t_us) < 6:
            raise RuntimeError("Not enough points for Ramsey fit.")

        n = len(y)
        dt_us = t_us[1] - t_us[0]
        fft_freq = np.fft.fftfreq(n, d=dt_us)
        fft_mag = np.abs(np.fft.fft(y))
        pos = np.where(fft_freq > 0)[0]
        if len(pos) == 0:
            freq_guess = 0.2
        else:
            freq_guess = float(abs(fft_freq[pos[np.argmax(fft_mag[pos])]]))
            freq_guess = max(freq_guess, 1e-3)

        amp_guess = 0.5 * float(np.ptp(y))
        offset_guess = float(np.median(y))
        tau_guess = max(1.0, 0.3 * float(np.max(t_us)))
        p0 = [max(amp_guess, 1e-6), tau_guess, offset_guess, freq_guess, np.pi / 2]

        bounds = (
            [0.0, 0.05, -np.inf, 1e-4, -np.pi],
            [np.inf, 5 * max(tau_guess, np.max(t_us)), np.inf, np.inf, np.pi],
        )
        params, cov = curve_fit(
            _ramsey_model,
            t_us,
            y,
            p0=p0,
            bounds=bounds,
            maxfev=4000,
        )
        return params, cov

    def _write_redo_flag(self, redo: bool):
        payload = {"redo": bool(redo)}
        with open(self.redo_flag_path, "w") as fh:
            json.dump(payload, fh, indent=2)
        self.results["flags"]["redo"] = bool(redo)

    def _update_limits(self, t_max_ns: int = None, dt_ns: int = None):
        if not self.update_time_limits:
            return
        q_key = str(self.q_no)
        with open(self.ramsey_limits_path, "r") as fh:
            payload = json.load(fh)
        if q_key not in payload:
            payload[q_key] = {}
        if t_max_ns is not None:
            payload[q_key]["t_max"] = int(max(t_max_ns, self.clock_cycle_dur_ns))
        if dt_ns is not None:
            payload[q_key]["dt"] = int(max(dt_ns, self.clock_cycle_dur_ns))
        with open(self.ramsey_limits_path, "w") as fh:
            json.dump(payload, fh, indent=2)

    def _build_program(self):
        q_if_detuned_hz = int(self.q_if + self.detuning_mhz * 1e6)
        with program() as ramsey_prog:
            n = declare(int)
            t = declare(int)
            I = declare(fixed)
            Q = declare(fixed)
            I_st = declare_stream()
            Q_st = declare_stream()
            n_st = declare_stream()
            I_ar = declare(fixed)
            Q_ar = declare(fixed)

            update_frequency(self.q_str, q_if_detuned_hz)
            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(t, self.t_min_clk, t < self.t_max_clk, t + self.dt_clk):
                    cooldown(
                        time=self.rep_rate_clk,
                        active_reset=self.active_reset,
                        qe=self.q_str,
                        qe_12=None,
                        rr=self.rr_str,
                        out=self.out,
                        I=I_ar,
                        Q=Q_ar,
                        pi_12=False,
                        dem=None,
                    )
                    play("X90", self.q_str)
                    wait(t, self.q_str)
                    play("X90", self.q_str)
                    align(self.q_str, self.rr_str)
                    measure_macro(self.q_str, self.rr_str, self.out, I, Q, pi_12=False)
                    save(I, I_st)
                    save(Q, Q_st)
                save(n, n_st)

            with stream_processing():
                I_st.buffer(len(self.t_list_clk)).average().save("I")
                Q_st.buffer(len(self.t_list_clk)).average().save("Q")
                n_st.save("iteration")
        return ramsey_prog

    def run_experiment(self):
        self._write_redo_flag(False)
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        self._qm = self._qmm.open_qm(self.config)
        job = self._qm.execute(self._build_program())
        results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

        fig = None
        ax = None
        if self.plot_live:
            fig, ax = plt.subplots()
            interrupt_on_close(fig, job)

        while results.is_processing():
            I, Q, iteration = results.fetch_all()
            progress_counter(iteration, self.n_avgs, start_time=results.get_start_time())

            if self.plot_live:
                ax.cla()
                ax.plot(self.t_list_us, I, ".-", label="I")
                ax.set(xlabel="Time (us)", ylabel="Ramsey amplitude")
                ax.grid(True)
                ax.legend()
                ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                plt.tight_layout()
                plt.pause(0.2)

            min_avg_before_checks = self.min_avg_bound if self.n_avgs > self.min_avg_bound else 0
            if iteration < min_avg_before_checks:
                continue

            snr, _ = S2N(normalize(I))
            if snr < self.snr_fit_threshold:
                continue

            try:
                fit_params, _ = self._fit_ramsey_trace(self.t_list_us, I)
            except Exception:
                continue

            tau_us = float(fit_params[1])
            freq_mhz = abs(float(fit_params[3]))
            t_max_us = float(np.max(self.t_list_us))
            dt_us = float(self.t_list_us[1] - self.t_list_us[0])

            flag_max_time_low = t_max_us < 2.5 * tau_us
            flag_max_time_high = t_max_us > 15.0 * tau_us
            flag_dt_low = dt_us < 1.0 / (40.0 * max(freq_mhz, 1e-6))
            flag_dt_high = dt_us > 1.0 / (10.0 * max(freq_mhz, 1e-6))

            if flag_max_time_low or flag_max_time_high or flag_dt_low or flag_dt_high:
                t_max_ns_new = None
                dt_ns_new = None

                if flag_max_time_low:
                    t_max_ns_new = int(max(2.5 * tau_us * 1e3, self._time_limits["t_min"] + 500))
                elif flag_max_time_high:
                    t_max_ns_new = int(max(2.0 * tau_us * 1e3, self.clock_cycle_dur_ns))

                if flag_dt_low:
                    dt_ns_new = int(max((1.0 / (40.0 * max(freq_mhz, 1e-6))) * 1e3 - 4, 16))
                elif flag_dt_high:
                    dt_ns_new = int(max((1.0 / (20.0 * max(freq_mhz, 1e-6))) * 1e3 + 1, 16))

                self._update_limits(t_max_ns=t_max_ns_new, dt_ns=dt_ns_new)
                self._write_redo_flag(True)
                job.halt()
                break
            else:
                self._write_redo_flag(False)

            if snr > self.snr_stop_threshold:
                job.halt()
                break

        if fig is not None:
            plt.close(fig)

        self._I = np.asarray(job.result_handles.get("I").fetch_all())
        self._Q = np.asarray(job.result_handles.get("Q").fetch_all())

    def analyze_and_plot(self):
        if self._I is None:
            raise RuntimeError("No data available. Run run_experiment() first.")
        fit_params, fit_cov = self._fit_ramsey_trace(self.t_list_us, self._I)
        self._fit_params = fit_params

        fit_trace = _ramsey_model(self.t_list_us, *fit_params)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(self.t_list_us, self._I, "-", alpha=0.25, linewidth=1.2, label="_nolegend_")
        ax.plot(self.t_list_us, self._I, ".", alpha=0.9, label="I")
        ax.plot(self.t_list_us, fit_trace, "-", label="fit")
        ax.set_xlabel("Time (us)")
        ax.set_ylabel("Ramsey amplitude")
        ax.set_title(
            f"Ramsey q{self.q_no}: "
            f"T2={fit_params[1]:.2f} us, "
            f"applied detuning={self.detuning_mhz:.4f} MHz, "
            f"observed detuning={fit_params[3]:.4f} MHz"
        )
        ax.grid(True)
        ax.legend()
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        fig.tight_layout()
        plt.show(block=False)

        fig_path = str(self.path_to_save) + f"_q{self.q_no}_ramsey.png"
        fig.savefig(fig_path, bbox_inches="tight")
        self.results["figures"].append(fig_path)
        cprint(f"Figure saved: {Path(fig_path).as_uri()}", "green")

        self.results["fit"] = {
            "amp": float(fit_params[0]),
            "tau_us": float(fit_params[1]),
            "offset": float(fit_params[2]),
            "freq_mhz": float(fit_params[3]),
            "phase": float(fit_params[4]),
            "max_cov": float(np.max(fit_cov)),
        }
        self.results["data"] = {
            "t_us": self.t_list_us,
            "I": self._I,
            "Q": self._Q,
            "I_fit": fit_trace,
        }

        with open(self.cache_path, "w") as fh:
            json.dump({"det": float(fit_params[3])}, fh, indent=2)

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


def perform_ramsey_detuning(q_no: int, rr_no: int = None, **kwargs):
    exp = RamseyDetuning(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    qubit_list = [
        # 1,
        2,
        # 3,
        # 4,
        # 5,
        # 6,
    ]
    for qubit in qubit_list:
        perform_ramsey_detuning(
            q_no=qubit,
            detuning_mhz=0.2,
            n_avgs=1000,
            save_data=True,
        )
