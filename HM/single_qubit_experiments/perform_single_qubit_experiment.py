from dataclasses import dataclass, field
import io
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from PIL import Image, ImageOps

from HM.single_qubit_experiments.spectroscopies.qubit_spectroscopy import perform_qubit_spectroscopy
from HM.single_qubit_experiments.vna_resonator_spectroscopy import perform_vna_resonator_spectroscopy
from HM.single_qubit_experiments.mixer_offset_calibration import perform_complete_mixer_offset_calibration
from HM.single_qubit_experiments.mixer_sideband_calibration import perform_complete_mixer_sideband_calibration
from HM.single_qubit_experiments.rabi_amp import perform_rabi_amp
from HM.single_qubit_experiments.ro_fidelity import perform_ro_fidelity
from HM.single_qubit_experiments.interleaved_coherence import perform_interleaved_coherence
from HM.single_qubit_experiments.ramsey_detuning import perform_ramsey_detuning
from HM.single_qubit_experiments.spectroscopies.e_f_spectroscopy import perform_e_f_spectroscopy
from HM.single_qubit_experiments.spectroscopies.readout_dispersive_shift import perform_readout_dispersive_shift
from HM.single_qubit_experiments.ro_len_vs_amp import perform_ro_len_vs_amp
from HM.utilities.files_utils import get_save_path
_default_vna_resonator_spectroscopy_kwargs = {
    "turn_off_LOs": True,
    "update_config": True,
    "save_data": True,
    "f_search_start": 7.0e9,
    "f_search_stop": 7.75e9,
    "zoom_half_span": 15e6,
    "low_power": -20,
    "n_avgs": 100,
    "if_bw": 1e3,
    "fit_error_threshold": 5e-5,
    # "n_points": 2001,
    # "cmd_delay": 3.0,

}
_default_e_f_spectroscopy_kwargs = {
    "n_avgs": 1000,
    "n_samples": 1000,
    "update_config": False,
    "save_data": True,
}
_default_qubit_spectroscopy_kwargs = {
    "n_avgs": 1000,
    "n_samples": 2000,
    "f_min_MHz": -400,
    "f_max_MHz": 400,
    "update_config": True,
    "save_data": True,
}
_default_mixer_offset_calibration_kwargs = {
    "save_data": True,
}
_default_mixer_sideband_calibration_kwargs = {
    "save_data": True,
}
_default_rabi_amp_kwargs = {
    "use_rotated": True,
    "n_pulses": 12,
    "amp_override": {
        # "span": 0.2,
        # "center": None,
        # "da": 0.01,
        "amin": 0.01,
        "amax":1,
        "da": 0.01,
    },
    "rotation_method": "pca",
    "min_avg_bound": 200,
    "amp_selection_mode": "sine_local_poly",
    "n_avgs": 750,
    "save_data": True,
    "update_config": True,
}
_default_ro_fidelity_kwargs = {
    "n_runs": 10_000,
    "update_config": True,
    "save_data": True,
}
_default_readout_dispersive_shift_kwargs = {
    "n_avgs": 1000,
    "sweep_span_MHz": 20,
    "df_kHz": 10,
    "rep_rate_clk": 250000,
    "save_data": True,
}
_default_ro_len_vs_amp_kwargs = {
    "n_avgs": 1000,
    "ro_len_ns": 100,
    "ro_len_ns_max": 1000,
    "ro_len_ns_step": 100,
    "save_data": True,
}
_default_interleaved_coherence_kwargs = {
    "n_avgs": 201,
    "save_data": True,
}
_default_ramsey_detuning_kwargs = {
    "n_avgs": 1000,
    "detuning_mhz": 1.0,
    "save_data": True,
}

@dataclass
class SingleQubitRunReport:
    q_no: int
    rr_no: int | None
    experiment_objects: dict[str, Any] = field(default_factory=dict)
    figures: dict[str, Any] = field(default_factory=dict)
    figure_titles_by_experiment: dict[str, list[str]] = field(default_factory=dict)
    report_path: str | None = None

    def add_experiment(self, experiment_name: str, experiment_obj: Any, figure_map: dict[str, Any]):
        self.experiment_objects[experiment_name] = experiment_obj
        self.figure_titles_by_experiment[experiment_name] = list(figure_map.keys())
        self.figures.update(figure_map)

    def save_pdf(self, pdf_path: str | Path | None = None, close_figures: bool = False) -> Path:
        if pdf_path is None:
            pdf_path = get_save_path(
                suffix=f"single_qubit_run_report_q{self.q_no}",
                extension="pdf",
            )
        pdf_path = Path(pdf_path)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        with PdfPages(pdf_path) as pdf:
            for fig in self.figures.values():
                pdf.savefig(fig, bbox_inches="tight")

        if close_figures:
            for fig in self.figures.values():
                plt.close(fig)
        self.report_path = str(pdf_path)
        return pdf_path

    @staticmethod
    def _figure_to_rgb_array(fig) -> np.ndarray:
        # Serialize figure to PNG bytes first; this is robust across interactive backends.
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
        buf.seek(0)
        img = plt.imread(buf)
        if img.ndim == 2:
            img = np.stack([img, img, img], axis=-1)
        if img.shape[-1] == 4:
            return img[..., :3]
        return img

    def save_single_page_pdf(
        self,
        pdf_path: str | Path | None = None,
        close_figures: bool = False,
        max_cols: int = 3,
    ) -> Path:
        if pdf_path is None:
            pdf_path = get_save_path(
                suffix=f"single_qubit_run_report_single_page_q{self.q_no}",
                extension="pdf",
            )
        pdf_path = Path(pdf_path)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        n_figs = len(self.figures)
        if n_figs == 0:
            blank = Image.new("RGB", (1400, 1000), color=(255, 255, 255))
            blank.save(str(pdf_path), "PDF", resolution=150.0)
        else:
            cols = max(1, min(int(max_cols), int(math.ceil(math.sqrt(n_figs)))))
            rows = int(math.ceil(n_figs / cols))
            cell_w = 1100
            cell_h = 800
            pad = 24
            header_h = 80
            canvas_w = cols * cell_w + (cols + 1) * pad
            canvas_h = rows * cell_h + (rows + 1) * pad + header_h
            canvas = Image.new("RGB", (canvas_w, canvas_h), color=(255, 255, 255))

            for idx, (_, fig) in enumerate(self.figures.items()):
                img_rgb = self._figure_to_rgb_array(fig)
                if img_rgb.dtype != np.uint8:
                    img_rgb = np.clip(img_rgb * 255.0, 0, 255).astype(np.uint8)
                tile = Image.fromarray(img_rgb, mode="RGB")
                tile = ImageOps.contain(tile, (cell_w, cell_h), method=Image.Resampling.LANCZOS)

                r = idx // cols
                c = idx % cols
                x0 = pad + c * (cell_w + pad) + (cell_w - tile.width) // 2
                y0 = header_h + pad + r * (cell_h + pad) + (cell_h - tile.height) // 2
                canvas.paste(tile, (x0, y0))

            canvas.save(str(pdf_path), "PDF", resolution=150.0)

        if close_figures:
            for fig in self.figures.values():
                plt.close(fig)
        self.report_path = str(pdf_path)
        return pdf_path


def _derive_figure_title(fig, fallback: str) -> str:
    if getattr(fig, "_suptitle", None) is not None and fig._suptitle.get_text():
        return str(fig._suptitle.get_text()).strip()
    for ax in fig.axes:
        title = str(ax.get_title()).strip()
        if title:
            return title
    return fallback


def _collect_new_figures(
    experiment_name: str,
    initial_fignums: set[int],
    title_counts: dict[str, int],
) -> dict[str, Any]:
    new_figure_ids = sorted(set(plt.get_fignums()) - set(initial_fignums))
    figure_map = {}
    for idx, fig_id in enumerate(new_figure_ids, start=1):
        fig = plt.figure(fig_id)
        base_title = _derive_figure_title(fig, fallback=f"{experiment_name}_fig_{idx}")
        report_title = f"{experiment_name}:{base_title}"
        count = title_counts.get(report_title, 0)
        title_counts[report_title] = count + 1
        if count > 0:
            report_title = f"{report_title} ({count + 1})"
        figure_map[report_title] = fig
    return figure_map


def _attach_figures_to_experiment(experiment_obj: Any, figure_map: dict[str, Any]):
    if experiment_obj is None or not figure_map:
        return
    if hasattr(experiment_obj, "register_figures"):
        experiment_obj.register_figures(figure_map)
        return
    if not hasattr(experiment_obj, "figures") or not isinstance(getattr(experiment_obj, "figures", None), dict):
        try:
            setattr(experiment_obj, "figures", {})
        except Exception:
            return
    experiment_obj.figures.update(figure_map)


def perform_single_qubit_experiment(q_no: int, rr_no: int = None, **kwargs):
    report = SingleQubitRunReport(q_no=q_no, rr_no=rr_no)
    title_counts: dict[str, int] = {}

    for expt in kwargs.get("experiments", []):
        fignums_before = set(plt.get_fignums())
        if expt == "vna_res_spec":
            expt_kwargs = kwargs.get(
                "vna_resonator_spectroscopy_kwargs",
                _default_vna_resonator_spectroscopy_kwargs,
            )
            expt_obj = perform_vna_resonator_spectroscopy(q_no, rr_no, **expt_kwargs)
        elif expt == "qubit_spec":
            expt_kwargs = kwargs.get("qubit_spec_kwargs", _default_qubit_spectroscopy_kwargs)
            expt_obj = perform_qubit_spectroscopy(q_no, rr_no, **expt_kwargs)
        elif expt == "rabi_amp":
            expt_kwargs = kwargs.get("rabi_amp_kwargs", _default_rabi_amp_kwargs)
            expt_obj = perform_rabi_amp(q_no, rr_no, **expt_kwargs)
        elif expt == "ro_fidelity":
            expt_kwargs = kwargs.get("ro_fidelity_kwargs", _default_ro_fidelity_kwargs)
            expt_obj = perform_ro_fidelity(q_no, rr_no, **expt_kwargs)
        elif expt == "readout_dispersive_shift":
            expt_kwargs = kwargs.get("readout_dispersive_shift_kwargs", _default_readout_dispersive_shift_kwargs)
            expt_obj = perform_readout_dispersive_shift(q_no, rr_no, **expt_kwargs)
        elif expt == "ro_len_vs_amp":
            expt_kwargs = kwargs.get("ro_len_vs_amp_kwargs", _default_ro_len_vs_amp_kwargs)
            expt_obj = perform_ro_len_vs_amp(q_no, rr_no, **expt_kwargs)
        elif expt == "e_f_spectroscopy":
            expt_kwargs = kwargs.get("e_f_spectroscopy_kwargs", _default_e_f_spectroscopy_kwargs)
            expt_obj = perform_e_f_spectroscopy(q_no, rr_no, **expt_kwargs)
        elif expt == "interleaved_coherence":
            expt_kwargs = kwargs.get(
                "interleaved_coherence_kwargs",
                _default_interleaved_coherence_kwargs,
            )
            expt_obj = perform_interleaved_coherence(q_no, rr_no, **expt_kwargs)
        elif expt == "ramsey_detuning":
            expt_kwargs = kwargs.get("ramsey_detuning_kwargs", _default_ramsey_detuning_kwargs)
            expt_obj = perform_ramsey_detuning(q_no, rr_no, **expt_kwargs)
        elif expt == "mixer_offset_calibration":
            expt_kwargs = kwargs.get(
                "mixer_offset_calibration_kwargs",
                _default_mixer_offset_calibration_kwargs,
            )
            expt_obj = perform_complete_mixer_offset_calibration(q_no, rr_no, **expt_kwargs)
        elif expt == "mixer_sideband_calibration":
            expt_kwargs = kwargs.get(
                "mixer_sideband_calibration_kwargs",
                _default_mixer_sideband_calibration_kwargs,
            )
            expt_obj = perform_complete_mixer_sideband_calibration(q_no, rr_no, **expt_kwargs)
        else:
            raise ValueError(f"Invalid experiment: {expt}")

        figure_map = _collect_new_figures(expt, fignums_before, title_counts)
        _attach_figures_to_experiment(expt_obj, figure_map)
        report.add_experiment(expt, expt_obj, figure_map)
        print(f"[report] {expt}: collected {len(figure_map)} figure(s)")

    print(f"[report] total collected figures for q{q_no}: {len(report.figures)}")

    report_output_format = kwargs.get("report_output_format")
    save_report = bool(kwargs.get("save_report", False))
    if save_report and report_output_format is None:
        report_output_format = "pdf"

    if report_output_format is not None:
        report_output_format = str(report_output_format).lower()
        report_layout = str(kwargs.get("report_layout", "single_page")).lower()
        if report_output_format == "pdf":
            if report_layout in {"single_page", "single", "giant"}:
                report.save_single_page_pdf(
                    pdf_path=kwargs.get("report_output_path"),
                    close_figures=bool(kwargs.get("close_figures_after_report", False)),
                    max_cols=int(kwargs.get("report_max_cols", 3)),
                )
            else:
                report.save_pdf(
                    pdf_path=kwargs.get("report_output_path"),
                    close_figures=bool(kwargs.get("close_figures_after_report", False)),
                )
        elif report_output_format in {"single_page_pdf", "pdf_single_page"}:
            report.save_single_page_pdf(
                pdf_path=kwargs.get("report_output_path"),
                close_figures=bool(kwargs.get("close_figures_after_report", False)),
                max_cols=int(kwargs.get("report_max_cols", 3)),
            )
        else:
            raise ValueError(
                f"Invalid report_output_format '{report_output_format}'. "
                f"Supported: 'pdf', 'single_page_pdf', 'pdf_single_page'."
            )
    return report




if __name__ == "__main__":
    import time

    # Optional tweaks for this run.
    _default_rabi_amp_kwargs["use_rotated"] = True
    _default_rabi_amp_kwargs["n_pulses"] = 1

    expt_kwargs_base = {
        "experiments": [
            "vna_res_spec",            # Resonator spectroscopy
            "qubit_spec",                # Qubit spectroscopy
            "mixer_offset_calibration",
            "mixer_sideband_calibration",
            "rabi_amp",
            "ro_fidelity",
            "interleaved_coherence",
            # "readout_dispersive_shift",
            # "ro_len_vs_amp",
            # "e_f_spectroscopy",
            # "ramsey_detuning",
        ],
        # Per-experiment kwargs (used only if that experiment is in "experiments").
        "qubit_spec_kwargs": _default_qubit_spectroscopy_kwargs,
        "vna_resonator_spectroscopy_kwargs": _default_vna_resonator_spectroscopy_kwargs,
        "rabi_amp_kwargs": _default_rabi_amp_kwargs,
        "ro_fidelity_kwargs": _default_ro_fidelity_kwargs,
        "interleaved_coherence_kwargs": _default_interleaved_coherence_kwargs,
        "ramsey_detuning_kwargs": _default_ramsey_detuning_kwargs,
        "mixer_offset_calibration_kwargs": _default_mixer_offset_calibration_kwargs,
        "mixer_sideband_calibration_kwargs": _default_mixer_sideband_calibration_kwargs,
        # Report kwargs.
        "save_report": True,
        "report_output_format": "pdf",
        "report_layout": "single_page",   # "single_page" (default) or "multi_page"
        "report_max_cols": 3,             # applies to single-page tiling
        "close_figures_after_report": True,
        # "report_output_path": r"D:\QUA\Master_Scripts\fourqubitv5_Hari\HM\data_misc\my_report.pdf",
    }

    qubit_nos = [
        # 1,
        2,
        # 3,
        # 4,
        # 5,
        # 6,
    ]

    time_started = time.time()
    for q_no in qubit_nos:
        expt_kwargs = dict(expt_kwargs_base)
        expt_kwargs["report_output_path"] = str(
            get_save_path(suffix=f"single_qubit_run_report_q{q_no}", extension="pdf")
        )
        report = perform_single_qubit_experiment(q_no, **expt_kwargs)
        print(f"q{q_no}: report saved to {report.report_path}")












    ##### Timekeeping
    time_ended = time.time()
    elapsed = time_ended - time_started
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = elapsed % 60
    print(f"Total time for the entire set of qubits taken: {hours}h {minutes}m {seconds:.1f}s")