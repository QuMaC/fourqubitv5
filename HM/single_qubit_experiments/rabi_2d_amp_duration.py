import time
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
from qm import QuantumMachinesManager
from qualang_tools.results import fetching_tool, progress_counter
from qualang_tools.plot import interrupt_on_close

from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json
from Helper_Functions.macros import cooldown, measure_macro

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class Rabi2DAmplitudeDuration(SingleQubitExperiment):
    """
    2D Rabi experiment: sweep pulse amplitude and duration.

    Produces a color plot of estimated excited-state population.
    - If calibrated population refs are provided, population is computed from them.
    - Otherwise population is an auto-normalized proxy in [0, 1].
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="rabi_2d_amp_duration",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )

        # Sweep axes
        self.amp_min = float(kwargs.get("amp_min", 0.02))
        self.amp_max = float(kwargs.get("amp_max", 0.8))
        self.amp_step = float(kwargs.get("amp_step", 0.02))
        self.t_min_ns = int(kwargs.get("t_min_ns", 16))
        self.t_max_ns = int(kwargs.get("t_max_ns", 1200))
        self.dt_ns = int(kwargs.get("dt_ns", 8))
        self.pulse_name = str(kwargs.get("pulse_name", "grft"))

        # Runtime
        self.n_avgs = int(kwargs.get("n_avgs", 2000))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250000))
        self.pi_12 = bool(kwargs.get("pi_12", False))
        self.dem = float(kwargs.get("dem", 0.0))
        self.live_plot = bool(kwargs.get("live_plot", True))
        self.save_data = bool(kwargs.get("save_data", False))

        # Population conversion
        self.population_quadrature = kwargs.get("population_quadrature", "auto")  # auto, I, Q
        self.invert_population = bool(kwargs.get("invert_population", False))
        self.I_ground = kwargs.get("I_ground", None)
        self.I_excited = kwargs.get("I_excited", None)
        self.Q_ground = kwargs.get("Q_ground", None)
        self.Q_excited = kwargs.get("Q_excited", None)

        self.amps = np.arange(self.amp_min, self.amp_max + self.amp_step / 2, self.amp_step)
        self.t_clk = np.arange(max(4, self.t_min_ns) // 4, self.t_max_ns // 4, max(1, self.dt_ns // 4))
        self.t_ns = 4 * self.t_clk
        if len(self.amps) == 0 or len(self.t_clk) == 0:
            raise ValueError("Empty sweep axis. Check amp/timing limits and steps.")

        self.I_map = None
        self.Q_map = None
        self.population_map = None
        self.selected_quadrature = "I"
        self._qmm = None

    def _build_program(self):
        qe = self.q_str
        rr = self.rr_str
        out = self.out
        n_t = len(self.t_clk)
        n_a = len(self.amps)

        with program() as rabi_2d:
            n = declare(int)
            a = declare(fixed)
            t = declare(int)
            I = declare(fixed)
            Q = declare(fixed)
            I_st = declare_stream()
            Q_st = declare_stream()
            n_st = declare_stream()

            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(a, float(self.amps[0]), a < float(self.amps[-1]) + self.amp_step / 2, a + self.amp_step):
                    with for_(t, int(self.t_clk[0]), t < int(self.t_clk[-1]) + max(1, self.dt_ns // 4), t + max(1, self.dt_ns // 4)):
                        cooldown(
                            time=self.rep_rate_clk,
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
                        play(self.pulse_name * amp(a), qe, t)
                        measure_macro(qe, rr, out, I, Q, pi_12=self.pi_12)
                        save(I, I_st)
                        save(Q, Q_st)
                save(n, n_st)

            with stream_processing():
                # Shape: [n_amp, n_time]
                I_st.buffer(n_t).buffer(n_a).average().save("I")
                Q_st.buffer(n_t).buffer(n_a).average().save("Q")
                n_st.save("iteration")

        return rabi_2d

    @staticmethod
    def _ensure_shape(data: np.ndarray, n_amp: int, n_t: int):
        arr = np.asarray(data)
        if arr.shape == (n_amp, n_t):
            return arr
        if arr.shape == (n_t, n_amp):
            return arr.T
        return np.reshape(arr, (n_amp, n_t))

    def _choose_quadrature(self, I_map: np.ndarray, Q_map: np.ndarray):
        if self.population_quadrature in ("I", "Q"):
            return self.population_quadrature
        i_span = float(np.nanpercentile(I_map, 95) - np.nanpercentile(I_map, 5))
        q_span = float(np.nanpercentile(Q_map, 95) - np.nanpercentile(Q_map, 5))
        return "I" if i_span >= q_span else "Q"

    def _signal_to_population(self, signal_2d: np.ndarray, quad: str):
        # Calibrated conversion if references are provided.
        if quad == "I" and self.I_ground is not None and self.I_excited is not None:
            g, e = float(self.I_ground), float(self.I_excited)
            if abs(e - g) > 1e-12:
                pop = (signal_2d - g) / (e - g)
                return np.clip(pop, 0.0, 1.0)
        if quad == "Q" and self.Q_ground is not None and self.Q_excited is not None:
            g, e = float(self.Q_ground), float(self.Q_excited)
            if abs(e - g) > 1e-12:
                pop = (signal_2d - g) / (e - g)
                return np.clip(pop, 0.0, 1.0)

        # Fallback: normalized proxy population.
        lo = float(np.nanpercentile(signal_2d, 5))
        hi = float(np.nanpercentile(signal_2d, 95))
        if abs(hi - lo) < 1e-12:
            pop = np.zeros_like(signal_2d, dtype=float)
        else:
            pop = (signal_2d - lo) / (hi - lo)
        pop = np.clip(pop, 0.0, 1.0)
        return 1.0 - pop if self.invert_population else pop

    def run_experiment(self):
        prog = self._build_program()
        n_amp = len(self.amps)
        n_t = len(self.t_ns)
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        qm = self._qmm.open_qm(self.config)
        try:
            job = qm.execute(prog)
            results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

            if self.live_plot:
                fig, ax = plt.subplots()
                interrupt_on_close(fig, job)

            while results.is_processing():
                I_live, Q_live, iteration = results.fetch_all()
                progress_counter(iteration, self.n_avgs, start_time=results.get_start_time())
                I_map = self._ensure_shape(I_live, n_amp, n_t)
                Q_map = self._ensure_shape(Q_live, n_amp, n_t)
                quad = self._choose_quadrature(I_map, Q_map)
                signal = I_map if quad == "I" else Q_map
                pop = self._signal_to_population(signal, quad)

                if self.live_plot:
                    ax.cla()
                    im = ax.imshow(
                        pop,
                        origin="lower",
                        aspect="auto",
                        extent=[self.t_ns[0], self.t_ns[-1], self.amps[0], self.amps[-1]],
                        cmap="viridis",
                        vmin=0.0,
                        vmax=1.0,
                    )
                    ax.set_xlabel("Pulse duration (ns)")
                    ax.set_ylabel("Pulse amplitude")
                    ax.set_title(f"Rabi 2D q{self.q_no} - population ({quad})")
                    if len(fig.axes) == 1:
                        fig.colorbar(im, ax=ax, label="Estimated population")
                    plt.tight_layout()
                    plt.pause(0.2)

            self.I_map = self._ensure_shape(job.result_handles.get("I").fetch_all(), n_amp, n_t)
            self.Q_map = self._ensure_shape(job.result_handles.get("Q").fetch_all(), n_amp, n_t)
        finally:
            try:
                qm.close()
            except Exception:
                pass

    def analyze_and_plot(self):
        if self.I_map is None or self.Q_map is None:
            raise RuntimeError("No data to analyze. Run run_experiment() first.")

        self.selected_quadrature = self._choose_quadrature(self.I_map, self.Q_map)
        signal = self.I_map if self.selected_quadrature == "I" else self.Q_map
        self.population_map = self._signal_to_population(signal, self.selected_quadrature)

        fig, ax = plt.subplots()
        im = ax.imshow(
            self.population_map,
            origin="lower",
            aspect="auto",
            extent=[self.t_ns[0], self.t_ns[-1], self.amps[0], self.amps[-1]],
            cmap="viridis",
            vmin=0.0,
            vmax=1.0,
        )
        ax.set_xlabel("Pulse duration (ns)")
        ax.set_ylabel("Pulse amplitude")
        ax.set_title(
            f"Rabi 2D q{self.q_no} - Estimated population "
            f"({self.selected_quadrature} quadrature)"
        )
        fig.colorbar(im, ax=ax, label="Estimated population")
        plt.tight_layout()

        save_path = str(self.path_to_save) + f"_q{self.q_no}.png"
        fig.savefig(save_path, bbox_inches="tight")
        cprint(f"Figure saved: {Path(save_path).as_uri()}", "green")
        plt.show(block=False)
        return self.population_map

    def update_config_dicts(self):
        # This scan is diagnostic by default; no config writes.
        return

    def save_experiment_data(self):
        payload = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "n_avgs": self.n_avgs,
            "amp_sweep": self.amps,
            "duration_ns_sweep": self.t_ns,
            "I_map": self.I_map,
            "Q_map": self.Q_map,
            "selected_quadrature": self.selected_quadrature,
            "population_map": self.population_map,
            "population_refs": {
                "I_ground": self.I_ground,
                "I_excited": self.I_excited,
                "Q_ground": self.Q_ground,
                "Q_excited": self.Q_excited,
                "invert_population": self.invert_population,
            },
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
        return self.population_map


def perform_rabi_2d_amp_duration(q_no: int, rr_no: int = None, **kwargs):
    """Instantiate and run 2D Rabi amplitude-duration scan."""
    exp = Rabi2DAmplitudeDuration(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    q_list = [1]
    for q in q_list:
        perform_rabi_2d_amp_duration(
            q_no=q,
            amp_min=0.02,
            amp_max=0.8,
            amp_step=0.01,
            t_min_ns=4,
            t_max_ns=800,
            dt_ns=4,
            n_avgs=100,
            save_data=False,
            rep_rate_clk=25e4,

        )