import json
import logging
import time
from datetime import datetime
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
from HM.utilities.files_utils import get_save_path, save_json
from HM.utilities.report_utils import format_report_value, save_experiment_plots_pdf
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


def _exp_model(t_us, amp, tau_us, offset):
    return amp * np.exp(-t_us / tau_us) + offset


def _ramsey_model(t_us, amp, freq_mhz, tau_us, phase, offset):
    return amp * np.exp(-t_us / tau_us) * np.sin(2 * np.pi * freq_mhz * t_us + phase) + offset


class InterleavedCoherence(SingleQubitExperiment):
    """
    Interleaved Echo/T1/Ramsey coherence calibration.

    Mirrors the legacy script logic while following the HM experiment framework.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="interleaved_coherence",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )
        self.n_avgs = int(kwargs.get("n_avgs", 1000))
        self.points = int(kwargs.get("points", 312))
        self.detuning_mhz = float(kwargs.get("detuning_mhz", 0.2))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250_000))
        self.active_reset = bool(kwargs.get("active_reset", False))
        self.snr_fit_threshold = float(kwargs.get("snr_fit_threshold", 25.0))
        self.snr_stop_threshold = float(kwargs.get("snr_stop_threshold", 25.0))
        self.min_avg_bound = int(kwargs.get("min_avg_bound", 70))
        self.update_time_limits = bool(kwargs.get("update_time_limits", True))
        self.save_data = bool(kwargs.get("save_data", True))
        self.plot_live = bool(kwargs.get("plot_live", True))

        self.coherence_limits_path = self.config_files_path + "/Pulse_Calibrations/coherence_time_limits.json"
        self.redo_flag_path = self.single_qubit_experiments_path + "/cached_jsons/coherence_redo.json"

        self._time_limits = self._load_time_limits()
        self.t_min_clk = int(self._time_limits["t_min"] // self.clock_cycle_dur_ns)
        self.t_max_clk = int(self._time_limits["t_max"] // self.clock_cycle_dur_ns)
        self.dt_clk = int(max(1, (self.t_max_clk - self.t_min_clk) // self.points))
        self.t_list_clk = np.arange(self.t_min_clk, self.t_max_clk, self.dt_clk, dtype=int)
        self.t_list_us = self.t_list_clk * 2 * self.clock_cycle_dur_ns * 1e-3

        self._qmm = None
        self._qm = None
        self._Ir = None
        self._Qr = None
        self._Ie = None
        self._Qe = None
        self._It = None
        self._Qt = None
        self._fits = None
        self.figures = {}

        self.results = {
            "expt_name": self.expt_name,
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "params": {
                "n_avgs": self.n_avgs,
                "min_avg_bound": self.min_avg_bound,
                "points": self.points,
                "detuning_mhz": self.detuning_mhz,
                "t_min_clk": self.t_min_clk,
                "t_max_clk": self.t_max_clk,
                "dt_clk": self.dt_clk,
                "rep_rate_clk": self.rep_rate_clk,
            },
            "flags": {"redo": False},
            "figures": [],
        }

    def _load_time_limits(self):
        default_limits = {"t_min": 16, "t_max": 75_000}
        q_key = str(self.q_no)
        payload = {}
        try:
            with open(self.coherence_limits_path, "r") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError):
            payload = {}
        if q_key not in payload:
            payload[q_key] = default_limits
            with open(self.coherence_limits_path, "w") as fh:
                json.dump(payload, fh, indent=2)
        return payload[q_key]

    def _write_redo_flag(self, redo: bool):
        with open(self.redo_flag_path, "w") as fh:
            json.dump({"redo": bool(redo)}, fh, indent=2)
        self.results["flags"]["redo"] = bool(redo)

    def _update_coherence_tmax(self, t_max_ns: int):
        if not self.update_time_limits:
            return
        q_key = str(self.q_no)
        with open(self.coherence_limits_path, "r") as fh:
            payload = json.load(fh)
        if q_key not in payload:
            payload[q_key] = {}
        payload[q_key]["t_max"] = int(max(t_max_ns, self.clock_cycle_dur_ns))
        with open(self.coherence_limits_path, "w") as fh:
            json.dump(payload, fh, indent=2)

    @staticmethod
    def _fit_exp_trace(t_us: np.ndarray, y: np.ndarray):
        amp_guess = float(np.mean(y[:8]) - np.mean(y[-8:]))
        tau_guess = max(1.0, 0.3 * float(np.max(t_us)))
        offset_guess = float(np.mean(y[-8:]))
        p0 = [amp_guess, tau_guess, offset_guess]
        params, cov = curve_fit(_exp_model, t_us, y, p0=p0, bounds=(-np.inf, np.inf), maxfev=4000)
        return params, cov

    @staticmethod
    def _fit_ramsey_trace(t_us: np.ndarray, y: np.ndarray):
        n = len(y)
        dt_us = t_us[1] - t_us[0]
        fft_freq = np.fft.fftfreq(n, d=dt_us)
        fft_mag = np.abs(np.fft.fft(y))
        pos = np.where(fft_freq > 0)[0]
        freq_guess = 0.2 if len(pos) == 0 else float(abs(fft_freq[pos[np.argmax(fft_mag[pos])]]))
        freq_guess = max(freq_guess, 1e-3)
        amp_guess = max(1e-6, 0.5 * float(np.ptp(y)))
        tau_guess = max(1.0, 0.3 * float(np.max(t_us)))
        p0 = [amp_guess, freq_guess, tau_guess, np.pi / 2, float(np.median(y))]
        bounds = ([0.0, 1e-4, 0.05, -np.pi, -np.inf], [np.inf, np.inf, np.inf, np.pi, np.inf])
        params, cov = curve_fit(_ramsey_model, t_us, y, p0=p0, bounds=bounds, maxfev=5000)
        return params, cov

    def _build_program(self):
        with program() as coherence_prog:
            n = declare(int)
            t = declare(int)
            Ir = declare(fixed)
            Qr = declare(fixed)
            Ie = declare(fixed)
            Qe = declare(fixed)
            It = declare(fixed)
            Qt = declare(fixed)
            I_ar = declare(fixed)
            Q_ar = declare(fixed)

            Ir_st = declare_stream()
            Qr_st = declare_stream()
            Ie_st = declare_stream()
            Qe_st = declare_stream()
            It_st = declare_stream()
            Qt_st = declare_stream()
            n_st = declare_stream()

            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(t, self.t_min_clk, t < self.t_max_clk, t + self.dt_clk):
                    align()

                    # Echo
                    update_frequency(self.q_str, int(self.q_if))
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
                    play("X180", self.q_str)
                    wait(t, self.q_str)
                    play("X90", self.q_str)
                    align(self.q_str, self.rr_str)
                    measure_macro(self.q_str, self.rr_str, self.out, Ie, Qe, pi_12=False)
                    save(Ie, Ie_st)
                    save(Qe, Qe_st)

                    # T1
                    align()
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
                    play("X180", self.q_str)
                    wait(2 * t, self.q_str)
                    align(self.q_str, self.rr_str)
                    measure_macro(self.q_str, self.rr_str, self.out, It, Qt, pi_12=False)
                    save(It, It_st)
                    save(Qt, Qt_st)

                    # Ramsey
                    align()
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
                    update_frequency(self.q_str, int(self.q_if + self.detuning_mhz * 1e6))
                    play("X90", self.q_str)
                    wait(2 * t, self.q_str)
                    play("X90", self.q_str)
                    align(self.q_str, self.rr_str)
                    measure_macro(self.q_str, self.rr_str, self.out, Ir, Qr, pi_12=False)
                    save(Ir, Ir_st)
                    save(Qr, Qr_st)
                save(n, n_st)

            with stream_processing():
                Ir_st.buffer(len(self.t_list_clk)).average().save("Ir")
                Qr_st.buffer(len(self.t_list_clk)).average().save("Qr")
                Ie_st.buffer(len(self.t_list_clk)).average().save("Ie")
                Qe_st.buffer(len(self.t_list_clk)).average().save("Qe")
                It_st.buffer(len(self.t_list_clk)).average().save("It")
                Qt_st.buffer(len(self.t_list_clk)).average().save("Qt")
                n_st.save("iteration")
        return coherence_prog

    def run_experiment(self):
        self._write_redo_flag(False)
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        self._qm = self._qmm.open_qm(self.config)
        job = self._qm.execute(self._build_program())
        results = fetching_tool(job, data_list=["Ir", "Qr", "Ie", "Qe", "It", "Qt", "iteration"], mode="live")

        fig = None
        ax = None
        limit_check_toggle = False
        if self.plot_live:
            fig, ax = plt.subplots()
            interrupt_on_close(fig, job)

        while results.is_processing():
            Ir, Qr, Ie, Qe, It, Qt, iteration = results.fetch_all()
            progress_counter(iteration, self.n_avgs, start_time=results.get_start_time())

            if self.plot_live:
                ax.cla()
                ax.plot(self.t_list_us, It, label="T1")
                ax.plot(self.t_list_us, Ie, label="Echo")
                ax.plot(self.t_list_us, Ir, label="Ramsey")
                ax.set(xlabel="Time (us)", ylabel="Amplitude")
                ax.grid(True)
                ax.legend()
                ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                plt.tight_layout()
                plt.pause(0.2)

            min_avg_before_checks = self.min_avg_bound if self.n_avgs > self.min_avg_bound else 0
            if iteration < min_avg_before_checks:
                continue

            snr, _ = S2N(normalize(It))
            if snr < self.snr_fit_threshold:
                continue

            if not limit_check_toggle:
                limit_check_toggle = True
                try:
                    pars_echo, _ = self._fit_exp_trace(self.t_list_us, Ie)
                    pars_t1, _ = self._fit_exp_trace(self.t_list_us, It)
                    echo_tau_us = float(pars_echo[1])
                    t1_tau_us = float(pars_t1[1])
                except Exception:
                    continue

                t_max_us = float(np.max(self.t_list_us))
                no_time_flag = t_max_us < 0.5 * min(echo_tau_us, t1_tau_us)
                too_much_time_flag = t_max_us > 5.0 * max(echo_tau_us, t1_tau_us)

                if no_time_flag:
                    t_max_ns_new = int(2.0 * max(echo_tau_us, t1_tau_us) * 1e3)
                    self._update_coherence_tmax(t_max_ns_new)
                    self._write_redo_flag(True)
                    job.halt()
                    break
                if too_much_time_flag:
                    t_max_ns_new = int(2.0 * max(echo_tau_us, t1_tau_us) * 1e3)
                    self._update_coherence_tmax(t_max_ns_new)
            else:
                limit_check_toggle = False

            if snr > self.snr_stop_threshold:
                job.halt()
                break

        if fig is not None:
            plt.close(fig)

        self._Ir = np.asarray(job.result_handles.get("Ir").fetch_all())
        self._Qr = np.asarray(job.result_handles.get("Qr").fetch_all())
        self._Ie = np.asarray(job.result_handles.get("Ie").fetch_all())
        self._Qe = np.asarray(job.result_handles.get("Qe").fetch_all())
        self._It = np.asarray(job.result_handles.get("It").fetch_all())
        self._Qt = np.asarray(job.result_handles.get("Qt").fetch_all())

    def analyze_and_plot(self):
        if self._Ir is None:
            raise RuntimeError("No data available. Run run_experiment() first.")

        pars_r, cov_r = self._fit_ramsey_trace(self.t_list_us, self._Ir)
        pars_e, cov_e = self._fit_exp_trace(self.t_list_us, self._Ie)
        pars_t, cov_t = self._fit_exp_trace(self.t_list_us, self._It)
        self._fits = {"ramsey": pars_r, "echo": pars_e, "T1": pars_t}

        Ir_fit = _ramsey_model(self.t_list_us, *pars_r)
        Ie_fit = _exp_model(self.t_list_us, *pars_e)
        It_fit = _exp_model(self.t_list_us, *pars_t)

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(self.t_list_us, self._It, "-", alpha=0.25, linewidth=1.2, label="_nolegend_")
        ax.plot(self.t_list_us, self._It, ".", alpha=0.8, label="T1", color="red")
        ax.plot(self.t_list_us, It_fit, "-", linewidth=2, label=f"T1 fit {pars_t[1]:.2f} us")
        ax.plot(self.t_list_us, self._Ie, "-", alpha=0.25, linewidth=1.2, label="_nolegend_")
        ax.plot(self.t_list_us, self._Ie, ".", alpha=0.8, label="Echo", color="green")
        ax.plot(self.t_list_us, Ie_fit, "-", linewidth=2, label=f"Echo fit {pars_e[1]:.2f} us")
        ax.plot(self.t_list_us, self._Ir, "-", alpha=0.25, linewidth=1.2, label="_nolegend_")
        ax.plot(self.t_list_us, self._Ir, ".", alpha=0.8, label="Ramsey", color="blue")
        ax.plot(self.t_list_us, Ir_fit, "-", linewidth=2, label=f"Ramsey fit {pars_r[2]:.2f} us")
        ax.set_xlabel("Time (us)")
        ax.set_ylabel("Signal")
        ax.set_title(
            f"Interleaved coherence q{self.q_no}: "
            f"Ramsey f={pars_r[1]:.4f} MHz, T2={pars_r[2]:.2f} us, T1={pars_t[1]:.2f} us, T2e={pars_e[1]:.2f} us"
        )
        ax.grid(True)
        ax.legend(fontsize=8)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        fig.tight_layout()
        if self.plot_live:
            plt.show(block=False)

        fig_path = str(self.path_to_save) + f"_q{self.q_no}_interleaved_coherence.png"
        fig.savefig(fig_path, bbox_inches="tight")
        self.figures["final_interleaved_coherence"] = fig
        if not self.plot_live:
            plt.close(fig)
        self.results["figures"].append(fig_path)
        cprint(f"Figure saved: {Path(fig_path).as_uri()}", "green")

        self.results["fit"] = {
            "ramsey": {
                "amp": float(pars_r[0]),
                "freq_mhz": float(pars_r[1]),
                "decay_us": float(pars_r[2]),
                "phase": float(pars_r[3]),
                "offset": float(pars_r[4]),
                "max_cov": float(np.max(cov_r)),
            },
            "echo": {
                "amp": float(pars_e[0]),
                "decay_us": float(pars_e[1]),
                "offset": float(pars_e[2]),
                "max_cov": float(np.max(cov_e)),
            },
            "T1": {
                "amp": float(pars_t[0]),
                "decay_us": float(pars_t[1]),
                "offset": float(pars_t[2]),
                "max_cov": float(np.max(cov_t)),
            },
        }
        self.results["data"] = {
            "t_us": self.t_list_us,
            "Ir": self._Ir,
            "Qr": self._Qr,
            "Ie": self._Ie,
            "Qe": self._Qe,
            "It": self._It,
            "Qt": self._Qt,
            "Ir_fit": Ir_fit,
            "Ie_fit": Ie_fit,
            "It_fit": It_fit,
        }

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


def perform_interleaved_coherence(q_no: int, rr_no: int = None, **kwargs):
    exp = InterleavedCoherence(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


def _interleaved_coherence_summary_lines(records: list[dict]) -> list[str]:
    lines = [
        "Interleaved coherence report",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "q   rr   T1 us     T2 us     T2e us    Ramsey fit MHz",
        "-" * 58,
    ]
    if records:
        for rec in records:
            fit = rec["results"].get("fit", {})
            lines.append(
                f"{rec['q_no']:<3} {rec['rr_no']:<4} "
                f"{format_report_value(fit.get('T1', {}).get('decay_us', np.nan)):>8}  "
                f"{format_report_value(fit.get('ramsey', {}).get('decay_us', np.nan)):>8}  "
                f"{format_report_value(fit.get('echo', {}).get('decay_us', np.nan)):>8}  "
                f"{format_report_value(fit.get('ramsey', {}).get('freq_mhz', np.nan), precision=4):>14}"
            )
    else:
        lines.append("No completed interleaved coherence experiments collected.")
    return lines


def _interleaved_coherence_page_title(record: dict, figure_path: Path) -> str:
    return f"q{record['q_no']} rr{record['rr_no']} final interleaved coherence"


def save_interleaved_coherence_report(
    experiments: list[InterleavedCoherence],
    pdf_path: str | Path | None = None,
    include_summary_page: bool = True,
    print_summary: bool = True,
) -> Path:
    """
    Save one PDF containing the final interleaved coherence plot from each experiment object.
    """
    return save_experiment_plots_pdf(
        experiments,
        pdf_path=pdf_path,
        suffix="interleaved_coherence_report",
        title="Interleaved coherence report",
        plot_filter="interleaved_coherence",
        summary_lines=_interleaved_coherence_summary_lines,
        print_summary_lines=print_summary,
        include_summary_page=include_summary_page,
        summary_page_position="end",
        page_title=_interleaved_coherence_page_title,
    )


def _plot_interleaved_coherence_tracking(records: list[dict], output_path: Path):
    if not records:
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.text(0.5, 0.5, "No coherence records collected.", ha="center", va="center")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)
        return

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    metric_specs = [
        ("t1_us", "T1 (us)", "tab:red"),
        ("t2_us", "T2 (Ramsey) (us)", "tab:blue"),
        ("t2e_us", "T2e (Echo) (us)", "tab:green"),
    ]
    qubits = sorted({int(rec["q_no"]) for rec in records})
    times = np.array([datetime.fromisoformat(rec["timestamp"]) for rec in records], dtype=object)

    for ax, (key, ylabel, color) in zip(axes, metric_specs):
        for q_no in qubits:
            q_mask = np.array([int(rec["q_no"]) == q_no for rec in records])
            y_vals = np.array([rec.get(key, np.nan) for rec in records], dtype=float)
            yq = y_vals[q_mask]
            tq = times[q_mask]
            if np.all(np.isnan(yq)):
                continue
            ax.plot(tq, yq, "o-", alpha=0.9, label=f"q{q_no}")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Timestamp")
    axes[0].set_title("Interleaved coherence drift vs time")
    axes[0].legend(loc="best", fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def run_interleaved_coherence_tracking(
    qubit_list: list[int],
    rr_map: dict[int, int] | None = None,
    sleep_between_cycles_s: float = 0.0,
    run_forever: bool = True,
    max_cycles: int | None = None,
    save_root: str | Path | None = None,
    continue_on_error: bool = True,
    save_every_cycle: bool = True,
    **interleaved_kwargs,
):
    """
    Perpetually run interleaved coherence on multiple qubits and track T1/T2/T2e over time.

    Intended to be imported and called from a separate script (non-CLI workflow).
    """
    if not qubit_list:
        raise ValueError("qubit_list must contain at least one qubit number.")
    if not run_forever and (max_cycles is None or int(max_cycles) < 1):
        raise ValueError("When run_forever=False, max_cycles must be >= 1.")

    qubits = [int(q) for q in qubit_list]
    interleaved_kwargs.setdefault("plot_live", False)
    rr_map = {} if rr_map is None else {int(k): int(v) for k, v in rr_map.items()}

    base_path = get_save_path(
        root_folder=save_root,
        suffix="interleaved_coherence_tracking",
        extension="",
    )
    json_path = Path(str(base_path) + ".json")
    plot_path = Path(str(base_path) + "_T1_T2_T2e_vs_time.png")

    tracker = {
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "qubit_list": qubits,
        "rr_map": rr_map,
        "sleep_between_cycles_s": float(sleep_between_cycles_s),
        "run_forever": bool(run_forever),
        "max_cycles": None if max_cycles is None else int(max_cycles),
        "records": [],
        "errors": [],
        "output_files": {"json": str(json_path), "plot": str(plot_path)},
        "interleaved_kwargs": {k: repr(v) for k, v in interleaved_kwargs.items()},
    }

    def _save_snapshot():
        tracker["updated_at"] = datetime.now().isoformat(timespec="seconds")
        save_json(tracker, json_path)
        _plot_interleaved_coherence_tracking(tracker["records"], plot_path)

    cycle_idx = 0
    t_start = time.time()
    try:
        while True:
            cycle_idx += 1
            tracker["current_cycle"] = cycle_idx
            logger.info(f"Starting interleaved coherence cycle {cycle_idx}")

            for q_no in qubits:
                rr_no = rr_map.get(q_no, q_no)
                ts = datetime.now().isoformat(timespec="seconds")
                logger.info(f"Cycle {cycle_idx}: q{q_no} (rr{rr_no})")
                try:
                    exp = perform_interleaved_coherence(q_no=q_no, rr_no=rr_no, **interleaved_kwargs)
                    fit = exp.results.get("fit", {})
                    tracker["records"].append(
                        {
                            "timestamp": ts,
                            "elapsed_s": float(time.time() - t_start),
                            "cycle": int(cycle_idx),
                            "q_no": int(q_no),
                            "rr_no": int(rr_no),
                            "t1_us": float(fit.get("T1", {}).get("decay_us", np.nan)),
                            "t2_us": float(fit.get("ramsey", {}).get("decay_us", np.nan)),
                            "t2e_us": float(fit.get("echo", {}).get("decay_us", np.nan)),
                            "ramsey_freq_mhz": float(fit.get("ramsey", {}).get("freq_mhz", np.nan)),
                        }
                    )
                except Exception as exc:
                    err = {
                        "timestamp": ts,
                        "elapsed_s": float(time.time() - t_start),
                        "cycle": int(cycle_idx),
                        "q_no": int(q_no),
                        "rr_no": int(rr_no),
                        "error": str(exc),
                    }
                    tracker["errors"].append(err)
                    logger.exception(f"Interleaved coherence failed for q{q_no} in cycle {cycle_idx}")
                    if not continue_on_error:
                        raise

            if save_every_cycle:
                _save_snapshot()

            if not run_forever and cycle_idx >= int(max_cycles):
                logger.info("Reached max_cycles. Exiting coherence tracking loop.")
                break
            if sleep_between_cycles_s > 0:
                time.sleep(float(sleep_between_cycles_s))
    except KeyboardInterrupt:
        logger.info("Interleaved coherence tracking interrupted by user.")
    finally:
        tracker["finished_at"] = datetime.now().isoformat(timespec="seconds")
        tracker["total_elapsed_s"] = float(time.time() - t_start)
        _save_snapshot()
        logger.info(f"Tracking data saved: {json_path}")
        logger.info(f"Tracking plot saved: {plot_path}")

    return tracker


if __name__ == "__main__":
    generate_report = True
    report_experiments = []
    qubit_list = [
         1,
         2,
        #  3,
        # 4,
        # 5,
        # 6,
    ]
    for qubit in qubit_list:
        exp = perform_interleaved_coherence(
            q_no=qubit,
            n_avgs=1000,
            detuning_mhz=0.2,
            save_data=True,
            min_avg_bound=200,
        )
        if generate_report:
            report_experiments.append(exp)

    if generate_report:
        save_interleaved_coherence_report(report_experiments)
