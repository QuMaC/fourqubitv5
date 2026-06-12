from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path
from typing import Any
import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from HM.utilities.files_utils import get_save_path

try:
    from termcolor import cprint, colored
except Exception:
    def cprint(msg, *args, **kwargs):
        print(msg)
    def colored(msg, *args, **kwargs):
        return msg


_COUPLING_JSON = (
    Path(__file__).resolve().parents[2]
    / "Configuration_Files" / "System_Parameters" / "coupling_vals.json"
)

_COL_HEADERS = ["pair", "ZZ/2π (kHz)", "J/2π (MHz)", "Δf (MHz)", "f₀ (MHz)", "f₁ (MHz)", "T2*₀ (µs)", "T2*₁ (µs)"]
_COL_KEYS    = [None,   "zz_khz",      "J_mhz",      "total_det_mhz", "f0_mhz", "f1_mhz", "T2star_0_us", "T2star_1_us"]
_COL_FMT     = [None,   ".3f",         ".4f",         ".4f",           ".4f",    ".4f",    ".1f",         ".1f"]


def show_coupling_table(
    path: str | Path | None = None,
    *,
    plot: bool = True,
    show_plot: bool = True,
) -> dict:
    """
    Load ``coupling_vals.json`` and display as a terminal table + optional matplotlib figure.

    Parameters
    ----------
    path      : override the default JSON path.
    plot      : if True, also render a matplotlib table figure.
    show_plot : if True, call ``plt.show(block=False)`` on the figure.

    Returns the raw dict loaded from JSON.
    """
    src = Path(path) if path else _COUPLING_JSON
    with open(src, "r", encoding="utf-8") as fh:
        data: dict = json.load(fh)

    # ── terminal ──────────────────────────────────────────────────────────────
    col_w = [10, 14, 12, 12, 12, 12, 12, 12]
    header = "  ".join(h.ljust(w) for h, w in zip(_COL_HEADERS, col_w))
    sep    = "  ".join("-" * w for w in col_w)
    print()
    cprint(f"  Coupling values  ({src.name})", "cyan", attrs=["bold"])
    print("  " + sep)
    print("  " + colored(header, attrs=["bold"]))
    print("  " + sep)
    for pair, vals in data.items():
        row_cells = [pair.ljust(col_w[0])]
        for key, fmt, w in zip(_COL_KEYS[1:], _COL_FMT[1:], col_w[1:]):
            v = vals.get(key, float("nan"))
            cell = format(float(v), fmt) if v != 0.0 else colored(format(float(v), fmt), "dark_grey")
            row_cells.append(str(cell).ljust(w))
        print("  " + "  ".join(row_cells))
    print("  " + sep)
    print()

    # ── matplotlib figure ─────────────────────────────────────────────────────
    if plot:
        pairs = list(data.keys())
        table_data = []
        for pair in pairs:
            vals = data[pair]
            row = [pair] + [
                format(float(vals.get(k, float("nan"))), f)
                for k, f in zip(_COL_KEYS[1:], _COL_FMT[1:])
            ]
            table_data.append(row)

        fig_h = max(2.0, 0.45 * (len(pairs) + 2))
        fig, ax = plt.subplots(figsize=(13, fig_h))
        ax.axis("off")
        tbl = ax.table(
            cellText=table_data,
            colLabels=_COL_HEADERS,
            cellLoc="center",
            loc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(9)
        tbl.auto_set_column_width(list(range(len(_COL_HEADERS))))
        # Style header row
        for col in range(len(_COL_HEADERS)):
            tbl[0, col].set_facecolor("#2b4c7e")
            tbl[0, col].set_text_props(color="white", fontweight="bold")
        # Alternating row shading; highlight non-zero cells
        for row_idx, pair in enumerate(pairs, start=1):
            vals = data[pair]
            for col_idx in range(len(_COL_HEADERS)):
                cell = tbl[row_idx, col_idx]
                cell.set_facecolor("#f0f4ff" if row_idx % 2 == 0 else "white")
                if col_idx > 0:
                    key = _COL_KEYS[col_idx]
                    if vals.get(key, 0.0) != 0.0:
                        cell.set_facecolor("#d4edda")  # green tint for filled values

        ax.set_title(
            f"Coupling values  —  {src.name}",
            fontsize=11, fontweight="bold", pad=10,
        )
        fig.tight_layout()

        if show_plot:
            plt.show(block=False)

    return data


def format_report_value(value: Any, precision: int = 2) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "nan"
    if not np.isfinite(value):
        return "nan"
    return f"{value:.{precision}f}"


def collect_experiment_plot_records(
    experiments: Iterable[Any],
    plot_filter: str | Callable[[Path], bool] | None = None,
) -> list[dict[str, Any]]:
    """
    Collect saved result plot paths from experiment objects.

    Experiments are expected to expose saved plot paths in ``exp.results["figures"]``.
    ``plot_filter`` can be a substring or a callable that accepts a Path.
    """
    records = []
    for exp in experiments:
        if exp is None:
            continue

        results = getattr(exp, "results", {}) or {}
        figure_items = []
        figures = getattr(exp, "figures", None)
        if isinstance(figures, dict):
            figure_items = [(str(label), fig) for label, fig in figures.items() if fig is not None]
        elif isinstance(figures, (list, tuple)):
            figure_items = [(f"figure_{idx}", fig) for idx, fig in enumerate(figures, start=1) if fig is not None]

        figure_paths = [Path(path) for path in results.get("figures", []) if path]
        if plot_filter is not None:
            if callable(plot_filter):
                figure_paths = [path for path in figure_paths if plot_filter(path)]
            else:
                figure_paths = [path for path in figure_paths if str(plot_filter) in path.stem]
                figure_items = [
                    (label, fig) for label, fig in figure_items if str(plot_filter) in label
                ] or figure_items

        records.append(
            {
                "experiment": exp,
                "experiment_name": results.get("expt_name", getattr(exp, "expt_name", exp.__class__.__name__)),
                "q_no": results.get("q_no", getattr(exp, "q_no", None)),
                "rr_no": results.get("rr_no", getattr(exp, "rr_no", None)),
                "figures": figure_items,
                "figure_paths": figure_paths,
                "results": results,
            }
        )
    return records


def _default_summary_lines(records: list[dict[str, Any]]) -> list[str]:
    lines = ["Experiment plot report", f"Generated: {datetime.now().isoformat(timespec='seconds')}", ""]
    if not records:
        lines.append("No experiment objects collected.")
        return lines

    lines.append("Experiment                q    rr   plots")
    lines.append("-" * 45)
    for rec in records:
        q_text = "" if rec["q_no"] is None else str(rec["q_no"])
        rr_text = "" if rec["rr_no"] is None else str(rec["rr_no"])
        n_plots = len(rec["figures"]) if rec["figures"] else len(rec["figure_paths"])
        lines.append(
            f"{str(rec['experiment_name'])[:24]:<24} "
            f"{q_text:<4} {rr_text:<4} {n_plots:>5}"
        )
    return lines


def _add_summary_page(pdf: PdfPages, summary_lines: list[str], title: str):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis("off")
    lines = [title, f"Generated: {datetime.now().isoformat(timespec='seconds')}", ""]
    if summary_lines:
        lines = summary_lines

    ax.text(
        0.05,
        0.95,
        "\n".join(lines),
        va="top",
        ha="left",
        family="monospace",
        fontsize=11,
        transform=ax.transAxes,
    )
    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def save_experiment_plots_pdf(
    experiments: Iterable[Any],
    pdf_path: str | Path | None = None,
    *,
    suffix: str = "experiment_plot_report",
    title: str = "Experiment plot report",
    plot_filter: str | Callable[[Path], bool] | None = None,
    summary_lines: list[str] | Callable[[list[dict[str, Any]]], list[str]] | None = None,
    print_summary_lines: bool = True,
    include_summary_page: bool = True,
    summary_page_position: str = "end",
    page_title: Callable[[dict[str, Any], Path], str] | None = None,
) -> Path:
    """
    Save one PDF containing saved result plots from experiment objects.

    This is intentionally experiment-agnostic. Individual experiments can make small
    wrappers that pass a plot filter and experiment-specific summary lines.
    """
    records = collect_experiment_plot_records(experiments, plot_filter=plot_filter)
    if callable(summary_lines):
        resolved_summary_lines = summary_lines(records)
    elif summary_lines is None:
        resolved_summary_lines = _default_summary_lines(records)
    else:
        resolved_summary_lines = list(summary_lines)

    if print_summary_lines:
        for line in resolved_summary_lines:
            print(f"[report] {line}" if line else "[report]")

    expected_plot_pages = sum(len(rec["figures"]) if rec["figures"] else len(rec["figure_paths"]) for rec in records)
    print(f"[report] collected {expected_plot_pages} plot(s) from {len(records)} experiment object(s)")

    if pdf_path is None:
        pdf_path = get_save_path(suffix=suffix, extension="pdf")
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    summary_position = str(summary_page_position).lower()
    if summary_position not in {"start", "end"}:
        raise ValueError("summary_page_position must be 'start' or 'end'.")

    plot_pages = 0
    with PdfPages(pdf_path) as pdf:
        if include_summary_page and summary_position == "start":
            _add_summary_page(pdf, resolved_summary_lines, title)

        for rec in records:
            if rec["figures"]:
                for _, fig in rec["figures"]:
                    pdf.savefig(fig, bbox_inches="tight")
                    plot_pages += 1
                continue

            for figure_path in rec["figure_paths"]:
                if not figure_path.exists():
                    cprint(f"[report] missing plot: {figure_path}", "yellow")
                    continue

                img = plt.imread(figure_path)
                fig, ax = plt.subplots(figsize=(11, 8.5))
                ax.imshow(img)
                ax.axis("off")
                if page_title is not None:
                    ax.set_title(page_title(rec, figure_path))
                fig.tight_layout()
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)
                plot_pages += 1

        if include_summary_page and summary_position == "end":
            _add_summary_page(pdf, resolved_summary_lines, title)

    cprint(f"[report] PDF saved with {plot_pages} plot page(s): {pdf_path.resolve().as_uri()}", "green")
    return pdf_path
