import json
import logging
import time
from pathlib import Path

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from termcolor import cprint

from qm import QuantumMachinesManager, SimulationConfig
from qm.qua import (
    align,
    amp,
    declare,
    declare_stream,
    fixed,
    for_,
    play,
    program,
    reset_frame,
    save,
    stream_processing,
    update_frequency,
)
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import fetching_tool

from Configuration_Files.config_dictionaries import q12_IF, u
from Helper_Functions.macros import cooldown, measure_macro, play_X180
from Helper_Functions.spectro_helper import (
    S2N_1,
    check_I_or_Q,
    does_signal_exist1,
    normalize,
)
from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class EFSpectroscopy(SingleQubitExperiment):
    """
    QUA-based e-f spectroscopy for the q12 element.

    This is the HM version of ``Automation/new_spectro_trial_find12.py``:
    prepare |e> with a ge X180 pulse, sweep a weak/constant drive on q12,
    read out through the resonator, then zoom onto the e-f peak.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="e_f_spectroscopy",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )

        self.q12_str = f"q12_{self.q_no}"
        self.q12_if = q12_IF[str(self.q_no)]

        self.n_avgs = int(kwargs.get("n_avgs", 1000))
        self.n_samples = int(kwargs.get("n_samples", 2000))
        self.update_config = bool(kwargs.get("update_config", False))
        self.save_data = bool(kwargs.get("save_data", False))
        self.use_rotated = bool(kwargs.get("use_rotated", False))

        self.drive_duration_clk = int(kwargs.get("drive_duration_clk", 200))
        self.cooldown_clk = int(kwargs.get("cooldown_clk", 20000))
        self.simulate = bool(kwargs.get("simulate", False))
        self.sim_duration_clk = int(kwargs.get("sim_duration_clk", 60000))

        self.snr_threshold_low_amp = float(kwargs.get("snr_threshold_low_amp", 0.6))
        self.snr_threshold_high_amp = float(kwargs.get("snr_threshold_high_amp", 1.0))
        self.snr_threshold_zoom = float(kwargs.get("snr_threshold_zoom", 2.0))

        self.f_min_MHz, self.f_max_MHz = self._default_wide_range(kwargs)
        self.zoom_half_width_MHz = float(kwargs.get("zoom_half_width_MHz", 20.0))
        self.zoom_stop_width_MHz = float(kwargs.get("zoom_stop_width_MHz", 0.8))

        self.amp_range = self._default_amp_range(kwargs)
        self._a_min_zoom = float(kwargs.get("zoom_amp", 0.075))

        self.best_quadrature = None
        self.q12_if_calibrated_MHz = None
        self.anharmonicity_MHz = None
        self.freqs_wide = None
        self.data_wide = []
        self.stage_traces = []
        self.peak_list_wide = []
        self.freqs_fin = None
        self.data_fin = None
        self._qmm = None

    def _default_wide_range(self, kwargs):
        if "f_min_MHz" in kwargs and "f_max_MHz" in kwargs:
            f_min = float(kwargs["f_min_MHz"])
            f_max = float(kwargs["f_max_MHz"])
        elif "center_MHz" in kwargs and "span_MHz" in kwargs:
            center = float(kwargs["center_MHz"])
            half_span = 0.5 * float(kwargs["span_MHz"])
            f_min = center - half_span
            f_max = center + half_span
        else:
            # Same heuristic as new_spectro_trial_find12.py. It brackets the
            # q12 transition on the low-frequency side of the configured f01 IF.
            q_if_hz = float(self.q_if)
            f_min = -0.8 * (q_if_hz + 150e6) * 1e-6
            f_max = 0.8 * (q_if_hz - 150e6) * 1e-6
        if f_min > f_max:
            f_min, f_max = f_max, f_min
        return f_min, f_max

    def _default_amp_range(self, kwargs):
        if "amp_range" in kwargs:
            return [float(x) for x in kwargs["amp_range"]]

        ext_bw_path = self.system_params_path + "/external_bandwidth.json"
        with open(ext_bw_path, "r") as fh:
            ext_bw = json.load(fh)
        ext_bw_val = float(ext_bw[str(self.q_no)])

        if self.q_no < 5:
            power_scale = abs(np.round(4.9296223 / ext_bw_val, 5))
        else:
            power_scale = abs(np.round(3.9296223 / ext_bw_val, 5))

        a_min = np.round(0.05 * 1.5, 4)
        return [
            float(np.round(0.7 * a_min * power_scale, 4)),
            float(np.round(2.0 * a_min * power_scale, 4)),
        ]

    def _make_freqs(self, f_min_MHz: float, f_max_MHz: float, zoom: bool = False):
        span_MHz = float(f_max_MHz - f_min_MHz)
        if span_MHz <= 0:
            raise ValueError(f"Invalid sweep range: {f_min_MHz} to {f_max_MHz} MHz")
        multiplier = 5 if zoom else 1
        df_hz = max(1, int(span_MHz * multiplier * u.MHz // self.n_samples))
        f_min_hz = int(f_min_MHz * u.MHz)
        f_max_hz = int(f_max_MHz * u.MHz)
        freqs = np.arange(f_min_hz, f_max_hz, df_hz, dtype=int)
        if len(freqs) < 3:
            raise ValueError("Frequency sweep has too few points. Widen range or increase n_samples.")
        return freqs, df_hz

    def _build_program(self, f_min_hz: int, f_max_hz: int, df_hz: int, q_amp: float, n_freqs: int):
        qe = self.q_str
        qe12 = self.q12_str
        rr = self.rr_str
        out = self.out

        with program() as prog:
            n = declare(int)
            I = declare(fixed)
            Q = declare(fixed)
            f = declare(int)
            I_st = declare_stream()
            Q_st = declare_stream()
            n_st = declare_stream()

            with for_(n, 0, n < self.n_avgs, n + 1):
                with for_(f, f_min_hz, f < f_max_hz, f + df_hz):
                    reset_frame(qe)
                    reset_frame(qe12)
                    cooldown(time=self.cooldown_clk, active_reset=False, qe=qe)
                    play_X180(qe)
                    align(qe, qe12)
                    update_frequency(qe12, f)
                    play("const" * amp(q_amp), qe12, duration=self.drive_duration_clk)
                    align(rr, qe12)
                    measure_macro(qe12, rr, out, I, Q, pi_12=False)
                    save(I, I_st)
                    save(Q, Q_st)
                save(n, n_st)

            with stream_processing():
                I_st.buffer(n_freqs).average().save("I")
                Q_st.buffer(n_freqs).average().save("Q")
                n_st.save("iteration")

        return prog

    def _run_with_live_plot(self, job, freqs: np.ndarray, amp_val: float, snr_threshold: float):
        res_handles = job.result_handles
        fig, axs = plt.subplots(2, 1, sharex=True)
        results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")
        interrupt_on_close(fig, job)

        I, Q = None, None
        while res_handles.is_processing():
            I, Q, iteration = results.fetch_all()
            data1 = {"I": I, "Q": Q}

            for i, ax in enumerate(axs.flat):
                ax.cla()
                data_label = list(data1.keys())[i]
                plot_data = data1[data_label]
                ax.plot(freqs * 1e-6, plot_data, marker=".", label=data_label)
                ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                ax.set(xlabel="q12 IF (MHz)", ylabel="Quadrature amplitude")
                ax.legend()
                ax.grid(True)

            I_proc, Q_proc = self._processed_quadratures(I, Q)
            snr_i, _ = S2N_1(normalize(I_proc))
            snr_q, _ = S2N_1(normalize(Q_proc))
            logger.info(f"q{self.q_no} q12 amp={amp_val:.4f}: SNR_I={snr_i:.2f}, SNR_Q={snr_q:.2f}")

            fig.suptitle(f"e-f spectroscopy q{self.q_no}: amp={amp_val:.4f}")
            plt.tight_layout()
            plt.pause(1)

            if snr_i > snr_threshold or snr_q > snr_threshold:
                job.halt()

        I = np.asarray(res_handles.get("I").fetch_all(), dtype=float)
        Q = np.asarray(res_handles.get("Q").fetch_all(), dtype=float)
        return I, Q

    def _processed_quadratures(self, I: np.ndarray, Q: np.ndarray):
        if not self.use_rotated:
            return np.asarray(I), np.asarray(Q)
        return super()._processed_quadratures(np.asarray(I), np.asarray(Q), scale_with_rabi_bounds=False)

    def _find_peaks_for_trace(self, trace: np.ndarray, freqs: np.ndarray, zoom: bool = False):
        win_s = 30 if zoom else None
        if win_s is None:
            _flg, fltd, w_size = does_signal_exist1(trace, alpha=0.5)
        else:
            _flg, fltd, w_size = does_signal_exist1(trace, alpha=0.5, win_s=win_s)

        normed = normalize(fltd[w_size:-w_size + 1])
        if not zoom:
            normed = np.roll(normed, w_size // 2)
            peaks, props = find_peaks(normed, height=0.4, prominence=0.2)
            peak_idx = np.clip(peaks, 0, len(freqs) - 1)
        else:
            peaks, props = find_peaks(normed, height=0.5, prominence=0.5)
            peak_idx = np.clip(peaks + w_size // 2, 0, len(freqs) - 1)

        return peak_idx, props

    def _select_quadrature(self, data: list) -> int:
        indices = [
            check_I_or_Q(d, alpha1=0.5)
            for d in data
            if check_I_or_Q(d, alpha1=0.5) is not None
        ]
        if not indices:
            return 0
        return int(np.bincount(indices).argmax())

    def _wide_sweep(self):
        freqs, df_hz = self._make_freqs(self.f_min_MHz, self.f_max_MHz, zoom=False)
        self.freqs_wide = freqs
        data = []

        for amp_val in self.amp_range:
            amp_val = float(np.round(amp_val, 4))
            snr_threshold = (
                self.snr_threshold_low_amp
                if amp_val < 0.2
                else self.snr_threshold_high_amp
            )
            prog = self._build_program(
                int(freqs[0]),
                int(freqs[0] + len(freqs) * df_hz),
                int(df_hz),
                amp_val,
                len(freqs),
            )
            qm = self._qmm.open_qm(self.config)
            try:
                job = qm.execute(prog)
                I, Q = self._run_with_live_plot(job, freqs, amp_val, snr_threshold)
            finally:
                try:
                    qm.close()
                except Exception:
                    pass
            I_proc, Q_proc = self._processed_quadratures(I, Q)
            data.append([I_proc, Q_proc])
            self.data_wide.append([I_proc, Q_proc])
            self.stage_traces.append(
                {
                    "stage": "wide",
                    "amp": amp_val,
                    "freqs_Hz": freqs.copy(),
                    "I": I.copy(),
                    "Q": Q.copy(),
                    "I_processed": I_proc.copy(),
                    "Q_processed": Q_proc.copy(),
                }
            )

        return data, freqs

    def _initial_center_from_wide_sweep(self, data: list, freqs: np.ndarray):
        self.best_quadrature = self._select_quadrature(data)
        peak_lists = []
        for trace_pair in data:
            peak_idx, _props = self._find_peaks_for_trace(trace_pair[self.best_quadrature], freqs, zoom=False)
            peak_lists.append(freqs[peak_idx] * 1e-6)
        self.peak_list_wide = peak_lists

        for sweep_i, peaks in enumerate(peak_lists):
            logger.info(
                f"Wide sweep {sweep_i} amp={self.amp_range[sweep_i]:.4f}: "
                f"peaks={np.round(peaks, 3)} MHz"
            )

        candidates = np.asarray(peak_lists[0], dtype=float) if peak_lists else np.array([])
        if len(candidates) == 0:
            raise RuntimeError("No e-f candidate found in wide sweep. Try widening f_min/f_max or raising amp.")

        if len(candidates) > 1:
            # Source script retries lower power. Here we choose the candidate nearest
            # the configured q12 IF and let zoom-in disambiguate.
            q12_if_MHz = float(self.q12_if) * 1e-6
            idx = int(np.argmin(np.abs(candidates - q12_if_MHz)))
            logger.warning(
                f"Multiple q12 candidates {np.round(candidates, 3)} MHz; "
                f"using nearest configured q12_IF={q12_if_MHz:.3f} MHz"
            )
            return float(candidates[idx])
        return float(candidates[0])

    def _zoom_sweep(self, f_center_MHz: float):
        f_min = f_center_MHz - self.zoom_half_width_MHz
        f_max = f_center_MHz + self.zoom_half_width_MHz
        amp_val = self._a_min_zoom
        zoom_index = 0

        while True:
            logger.info(f"Zoom q12 window: [{f_min:.4f}, {f_max:.4f}] MHz amp={amp_val:.5f}")
            if f_max - f_min < self.zoom_stop_width_MHz:
                break

            freqs, df_hz = self._make_freqs(f_min, f_max, zoom=True)
            prog = self._build_program(
                int(freqs[0]),
                int(freqs[0] + len(freqs) * df_hz),
                int(df_hz),
                amp_val,
                len(freqs),
            )
            qm = self._qmm.open_qm(self.config)
            try:
                job = qm.execute(prog)
                I, Q = self._run_with_live_plot(job, freqs, amp_val, self.snr_threshold_zoom)
            finally:
                try:
                    qm.close()
                except Exception:
                    pass

            I_proc, Q_proc = self._processed_quadratures(I, Q)
            trace = I_proc if self.best_quadrature == 0 else Q_proc
            peak_idx, props = self._find_peaks_for_trace(trace, freqs, zoom=True)
            self.stage_traces.append(
                {
                    "stage": "zoom",
                    "zoom_index": zoom_index,
                    "amp": float(amp_val),
                    "freqs_Hz": freqs.copy(),
                    "I": I.copy(),
                    "Q": Q.copy(),
                    "I_processed": I_proc.copy(),
                    "Q_processed": Q_proc.copy(),
                }
            )
            zoom_index += 1

            if len(peak_idx) == 0:
                logger.warning("No e-f peak in zoom sweep; doubling q12 amp and retrying same window.")
                amp_val *= 2
                continue

            best = int(peak_idx[np.argmax(props["peak_heights"])])
            f_center_hz = float(freqs[best])
            f_center_MHz = f_center_hz * 1e-6
            self.freqs_fin = freqs
            self.data_fin = np.column_stack([freqs, I, Q, I_proc, Q_proc])

            span = (f_max - f_min) / 3
            f_min = f_center_MHz - span / 2
            f_max = f_center_MHz + span / 2
            amp_val /= 5

        return float(f_center_MHz)

    def run_experiment(self):
        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)

        if self.simulate:
            freqs, df_hz = self._make_freqs(self.f_min_MHz, self.f_max_MHz, zoom=False)
            prog = self._build_program(
                int(freqs[0]),
                int(freqs[0] + len(freqs) * df_hz),
                int(df_hz),
                float(self.amp_range[0]),
                len(freqs),
            )
            job = self._qmm.simulate(self.config, prog, SimulationConfig(self.sim_duration_clk))
            samples = job.get_simulated_samples()
            q_con = f"con{int(self.dac_mapping[self.q_str][0])}"
            con = getattr(samples, q_con, None)
            if con is not None:
                con.plot()
            plt.show()
            logger.info("Simulation completed; skipping hardware execution.")
            return

        data, freqs = self._wide_sweep()
        f_center_MHz = self._initial_center_from_wide_sweep(data, freqs)
        self.q12_if_calibrated_MHz = self._zoom_sweep(f_center_MHz)
        self.anharmonicity_MHz = float(self.q_if * 1e-6 - self.q12_if_calibrated_MHz)
        logger.info(
            f"Final q12 IF = {self.q12_if_calibrated_MHz:.6f} MHz | "
            f"anharmonicity = {self.anharmonicity_MHz:.3f} MHz"
        )

    def analyze_and_plot(self):
        if self.simulate:
            return None
        if self.data_fin is None:
            raise RuntimeError("No final zoom data. Call run_experiment() first.")

        best_label = "I" if self.best_quadrature == 0 else "Q"

        n_stages = max(1, len(self.stage_traces))
        n_cols = 2 if n_stages > 1 else 1
        n_rows = int(np.ceil(n_stages / n_cols))
        fig, axs = plt.subplots(
            n_rows,
            n_cols,
            figsize=(6.5 * n_cols, 3.4 * n_rows),
            squeeze=False,
        )
        axs_flat = axs.ravel()

        for idx, stage in enumerate(self.stage_traces):
            ax = axs_flat[idx]
            freqs_MHz = np.asarray(stage["freqs_Hz"], dtype=float) * 1e-6
            trace = (
                np.asarray(stage["I_processed"], dtype=float)
                if self.best_quadrature == 0
                else np.asarray(stage["Q_processed"], dtype=float)
            )
            trace_norm = normalize(trace)
            if stage["stage"] == "wide":
                title = f"Wide sweep amp={stage['amp']:.4f}"
            else:
                title = f"Zoom {stage['zoom_index']} amp={stage['amp']:.4f}"

            ax.plot(freqs_MHz, trace_norm, marker=".", markersize=2, linewidth=1.4)
            ax.axvline(
                self.q12_if_calibrated_MHz,
                linestyle="--",
                color="red",
                linewidth=1.4,
                label=f"q12 IF = {self.q12_if_calibrated_MHz:.6f} MHz",
            )
            ax.set_title(title)
            ax.set_xlabel("q12 IF (MHz)")
            ax.set_ylabel(f"Norm. {best_label}")
            ax.grid(True)
            ax.legend(fontsize=8, loc="best")

        for ax in axs_flat[n_stages:]:
            ax.axis("off")

        fig.suptitle(
            f"e-f spectroscopy q{self.q_no}: all sweep stages\n"
            f"q12 IF = {self.q12_if_calibrated_MHz:.6f} MHz | "
            f"anharmonicity = {self.anharmonicity_MHz:.3f} MHz",
            y=0.995,
        )
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        save_path = str(self.path_to_save) + f"_q{self.q_no}.png"
        fig.savefig(save_path, bbox_inches="tight")
        self.register_figure("e_f_spectroscopy", fig)
        cprint(f"Figure saved: {Path(save_path).as_uri()}", "green")
        plt.show(block=False)
        return fig

    def update_config_dicts(self):
        if not self.update_config:
            return
        if self.q12_if_calibrated_MHz is None:
            raise RuntimeError("No q12 calibration result. Call run_experiment() first.")

        q_key = str(self.q_no)

        q12_if_path = self.system_params_path + "/q12_IF.json"
        with open(q12_if_path, "r") as fh:
            q12_if_dict = json.load(fh)
        q12_if_dict[q_key] = round(float(self.q12_if_calibrated_MHz), 6)
        with open(q12_if_path, "w") as fh:
            json.dump(q12_if_dict, fh, indent=6)
        logger.info(f"q12_IF[{q_key}] = {self.q12_if_calibrated_MHz:.6f} MHz")

        anh_path = self.system_params_path + "/anharmonicities.json"
        with open(anh_path, "r") as fh:
            anh_dict = json.load(fh)
        anh_dict[q_key] = round(float(self.anharmonicity_MHz), 3)
        with open(anh_path, "w") as fh:
            json.dump(anh_dict, fh, indent=6)
        logger.info(f"anharmonicities[{q_key}] = {self.anharmonicity_MHz:.3f} MHz")

    def save_experiment_data(self):
        if self.q12_if_calibrated_MHz is None:
            raise RuntimeError("No data to save. Call run_experiment() first.")

        payload = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "q12_if_calibrated_MHz": self.q12_if_calibrated_MHz,
            "q_if_MHz": float(self.q_if) * 1e-6,
            "anharmonicity_MHz": self.anharmonicity_MHz,
            "n_avgs": self.n_avgs,
            "n_samples": self.n_samples,
            "amp_range": self.amp_range,
            "f_min_MHz": self.f_min_MHz,
            "f_max_MHz": self.f_max_MHz,
            "best_quadrature": self.best_quadrature,
            "freqs_wide_Hz": self.freqs_wide,
            "peak_list_wide_MHz": self.peak_list_wide,
            "data_wide": [{"I": d[0], "Q": d[1]} for d in self.data_wide],
            "stage_traces": [
                {
                    "stage": stage["stage"],
                    "zoom_index": stage.get("zoom_index"),
                    "amp": stage["amp"],
                    "freqs_Hz": stage["freqs_Hz"],
                    "I": stage["I"],
                    "Q": stage["Q"],
                    "I_processed": stage["I_processed"],
                    "Q_processed": stage["Q_processed"],
                }
                for stage in self.stage_traces
            ],
        }
        if self.data_fin is not None:
            payload["data_fin"] = {
                "freqs_Hz": self.data_fin[:, 0],
                "I": self.data_fin[:, 1],
                "Q": self.data_fin[:, 2],
                "I_processed": self.data_fin[:, 3],
                "Q_processed": self.data_fin[:, 4],
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
                logger.info("Simulation mode enabled; skipped analysis/config/save.")
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
        return self.q12_if_calibrated_MHz


def perform_e_f_spectroscopy(q_no: int, rr_no: int = None, **kwargs):
    exp = EFSpectroscopy(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    for q in [
        1,
        2,
        # 3,
        # 4,
        # 5,
        # 6,
        ]:
        perform_e_f_spectroscopy(
            q_no=q,
            n_avgs=1000,
            n_samples=1000,
            update_config=True,
            save_data=True,
        )
