"""
Plot GRAPE waveforms from saved .npz archives with fidelities from parent JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from HM.simulator.two_qubit_simulator.engine.pulses import (
    expand_samples_held_nsub,
    scale_sample_index,
)

BASE = Path(__file__).resolve().parent / "results"

NPZ_SOURCES = [
    # BASE / "looped" / "cycles_seed_31_MHz" / "cr_grape_looped_all.npz",
    # BASE / "looped" / "cycles_seed_32_MHz" / "cr_grape_looped_all.npz",
    # BASE / "looped" / "cycles_seed_30_MHz" / "cr_grape_looped_all.npz",
    BASE / "robust" / "cr_grape_robust_zz0p1824MHz_mms_l0p3_20260707_070952.npz",
]

LOOPED_SEED_NPZ = BASE / "looped" / "cycles_seed_32_MHz" / "cr_grape_seed.npz"


def _load_json(parent: Path, stem: str) -> dict:
    path = parent / f"{stem}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _shade_regions(
    ax,
    t: np.ndarray,
    rs: int,
    fs: int,
    fe: int,
    ds: int,
    *,
    n_sub: int = 1,
) -> None:
    n_sub = max(1, int(n_sub))
    rs_e = scale_sample_index(rs, n_sub)
    fs_e = scale_sample_index(fs, n_sub)
    fe_e = scale_sample_index(fe, n_sub)
    ds_e = scale_sample_index(ds, n_sub)
    de_e = len(t)
    ax.axvspan(t[rs_e], t[fs_e - 1] if fs_e > rs_e else t[rs_e], color="tab:blue", alpha=0.06)
    ax.axvspan(t[fs_e], t[fe_e - 1] if fe_e > fs_e else t[fs_e], color="tab:orange", alpha=0.06)
    ax.axvspan(t[ds_e], t[de_e - 1] if de_e > ds_e else t[ds_e], color="tab:purple", alpha=0.06)


def _looped_fidelities(parent: Path) -> list[dict]:
    payload = _load_json(parent, "cr_grape_looped_result")
    return [row for row in payload["metrics_table"] if isinstance(row.get("cycle"), int)]


def plot_looped_npz(npz_path: Path, out_png: Path, *, n_sub: int = 2) -> Path:
    parent = npz_path.parent
    fidelities = _looped_fidelities(parent)
    label = parent.name
    n_sub = max(1, int(n_sub))

    with np.load(npz_path, allow_pickle=False) as d:
        t_sample = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        opt_i = np.asarray(d["cr_half_opt_I"], dtype=float)
        opt_q = np.asarray(d["cr_half_opt_Q"], dtype=float)
        is_avg = np.asarray(d["is_average"], dtype=bool).reshape(-1)
        rs = int(np.asarray(d["rise_start"]).item())
        fs = int(np.asarray(d["flat_start"]).item())
        fe = int(np.asarray(d["flat_stop"]).item())
        ds = int(np.asarray(d["fall_start"]).item())

    dt = _dt_ns(t_sample)
    t, _ = expand_samples_held_nsub(opt_i[0], dt, n_sub)
    n_rows = opt_i.shape[0]
    n_cycles = int(np.sum(~is_avg))
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, max(n_cycles, 1)))

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    cycle_idx = 0
    for row in range(n_rows):
        if is_avg[row]:
            color = "black"
            lw = 2.2
            zorder = 5
            avg_f = next(
                (r["process_fidelity"] for r in fidelities if r.get("cycle") == "avg"),
                None,
            )
            if avg_f is None and fidelities:
                avg_f = float(np.mean([r["process_fidelity"] for r in fidelities]))
            leg = f"average  F={avg_f:.5f}" if avg_f is not None else "average"
        else:
            cycle_idx += 1
            color = cmap[cycle_idx - 1]
            lw = 0.9
            zorder = 2
            f_proc = fidelities[cycle_idx - 1]["process_fidelity"]
            leg = f"cycle {cycle_idx:02d}  F={f_proc:.5f}"
            if cycle_idx not in (1, 2, 3, n_cycles):
                leg = None

        for ax, y_arr, comp in zip(axes, (opt_i, opt_q), ("I", "Q")):
            _, y = expand_samples_held_nsub(y_arr[row], dt, n_sub)
            ax.plot(t, y, color=color, lw=lw, alpha=0.75 if not is_avg[row] else 1.0,
                    label=leg if comp == "I" else None, zorder=zorder)
            _shade_regions(ax, t, rs, fs, fe, ds, n_sub=n_sub)
            ax.set_ylabel(f"{comp} (MHz)")
            ax.grid(alpha=0.35)

    axes[0].legend(fontsize=7, loc="upper right", ncol=2)
    axes[1].set_xlabel(
        f"time within one CR half (ns)  |  held at n_sub={n_sub}  "
        f"(dt_sub={dt / n_sub:g} ns)"
    )
    axes[0].set_title(
        f"Looped GRAPE — {label}  |  {n_cycles} cycle(s) + average "
        f"(each sample held ×{n_sub})"
    )
    fig.text(0.99, 0.01, "blue=rise  orange=flat  purple=fall", ha="right", va="bottom",
             fontsize=8, color="0.35")
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def plot_robust_npz(npz_path: Path, out_png: Path, *, n_sub: int = 2) -> Path:
    parent = npz_path.parent
    payload = _load_json(parent, npz_path.stem)
    seed_m = payload["seed_metrics"]
    final_m = payload["final_metrics"]
    n_sub = max(1, int(n_sub))

    with np.load(npz_path, allow_pickle=False) as d:
        t_sample = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        seed_i = np.asarray(d["cr_half_seed_I"], dtype=float).reshape(-1)
        seed_q = np.asarray(d["cr_half_seed_Q"], dtype=float).reshape(-1)
        opt_i = np.asarray(d["cr_half_opt_I"], dtype=float).reshape(-1)
        opt_q = np.asarray(d["cr_half_opt_Q"], dtype=float).reshape(-1)
        rs = int(np.asarray(d["rise_start"]).item())
        fs = int(np.asarray(d["flat_start"]).item())
        fe = int(np.asarray(d["flat_stop"]).item())
        ds = int(np.asarray(d["fall_start"]).item())

    dt = _dt_ns(t_sample)
    t, seed_i_e = expand_samples_held_nsub(seed_i, dt, n_sub)
    _, seed_q_e = expand_samples_held_nsub(seed_q, dt, n_sub)
    _, opt_i_e = expand_samples_held_nsub(opt_i, dt, n_sub)
    _, opt_q_e = expand_samples_held_nsub(opt_q, dt, n_sub)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    for ax, seed_y, opt_y, comp in zip(
        axes,
        (seed_i_e, seed_q_e),
        (opt_i_e, opt_q_e),
        ("I", "Q"),
    ):
        ax.plot(t, seed_y, color="0.65", lw=1.2, ls="--", label=f"seed {comp} (MHz)")
        ax.plot(t, opt_y, color="tab:green", lw=1.6, label=f"opt {comp} (MHz)")
        _shade_regions(ax, t, rs, fs, fe, ds, n_sub=n_sub)
        ax.set_ylabel(f"{comp} (MHz)")
        ax.grid(alpha=0.35)
        ax.legend(fontsize=8, loc="upper right")

    axes[1].set_xlabel(
        f"time within one CR half (ns)  |  held at n_sub={n_sub}  "
        f"(dt_sub={dt / n_sub:g} ns)"
    )
    axes[0].set_title(
        f"Robust CR half: seed vs optimized (each sample held ×{n_sub})"
    )
    summary = (
        f"seed:  F_comb={seed_m['process_fidelity']:.5f}   "
        f"F_a={seed_m['process_fidelity_a']:.5f}   F_b={seed_m['process_fidelity_b']:.5f}\n"
        f"final: F_comb={final_m['process_fidelity']:.5f}   "
        f"F_a={final_m['process_fidelity_a']:.5f}   F_b={final_m['process_fidelity_b']:.5f}"
    )
    fig.text(0.01, 0.005, summary, ha="left", va="bottom", fontsize=8,
             family="monospace", color="0.15")
    fig.text(0.99, 0.005, "blue=rise  orange=flat  purple=fall", ha="right",
             va="bottom", fontsize=8, color="0.45")
    plt.tight_layout(rect=(0, 0.09, 1, 1))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


FFT_N = 8192
CLIP_FRACTION = 0.6


def _dt_ns(t: np.ndarray) -> float:
    """Sample spacing in ns (matches looped_plotter.ipynb: ``t_ns[1] - t_ns[0]``)."""
    t = np.asarray(t, dtype=float).reshape(-1)
    if len(t) < 2:
        raise ValueError("need at least two time samples")
    return float(t[1] - t[0])


def _envelope_fft_components(
    i_mhz: np.ndarray,
    q_mhz: np.ndarray,
    dt_ns: float,
    *,
    n_fft: int = FFT_N,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """FFT(I+iQ), FFT(I), FFT(Q) with zero-padding and fftshift; freq in MHz."""
    i_mhz = np.asarray(i_mhz, dtype=float).reshape(-1)
    q_mhz = np.asarray(q_mhz, dtype=float).reshape(-1)
    f_mhz = np.fft.fftshift(np.fft.fftfreq(n_fft, d=dt_ns)) * 1e3
    a_iq = np.fft.fftshift(np.fft.fft(i_mhz + 1j * q_mhz, n_fft))
    a_i = np.fft.fftshift(np.fft.fft(i_mhz, n_fft))
    a_q = np.fft.fftshift(np.fft.fft(q_mhz, n_fft))
    return f_mhz, a_iq, a_i, a_q


def _plot_fft_db(
    ax,
    f_mhz: np.ndarray,
    spec: np.ndarray,
    sl: slice,
    *,
    label: str,
    color: str,
    lw: float = 1.6,
    ls: str = "-",
    norm_peak: np.ndarray | None = None,
) -> None:
    ax.plot(
        f_mhz[sl],
        _spectrum_db(spec[sl], norm_peak=norm_peak),
        color=color,
        lw=lw,
        ls=ls,
        label=label,
    )


def _freq_clip_slice(n: int, clip_fraction: float = CLIP_FRACTION) -> slice:
    clip_index = int(clip_fraction * n / 2)
    return slice(clip_index, n - clip_index)


def _spectrum_db(mag: np.ndarray, *, norm_peak: np.ndarray | None = None) -> np.ndarray:
    peak = float(np.max(np.abs(norm_peak if norm_peak is not None else mag)))
    return 20.0 * np.log10(np.abs(mag) / peak + 1e-15)


def _style_fft_axis(ax, *, freq_lim: tuple[float, float] = (-200.0, 200.0)) -> None:
    ax.set_xlim(*freq_lim)
    ax.set_ylim(-80, 0)
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Amplitude (dB)")
    ax.grid(alpha=0.35)


def _looped_seed_label(parent: Path) -> str:
    payload = _load_json(parent, "cr_grape_looped_result")
    amp = payload.get("looped_config", {}).get("grape_config", {}).get("seed_amp_mhz")
    folder = parent.name
    if amp is not None:
        return f"{folder} seed  {amp:g} MHz"
    return f"{folder} seed"


def _load_looped_seed(seed_npz: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int, int, int]:
    with np.load(seed_npz, allow_pickle=False) as d:
        t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        seed_i = np.asarray(d["cr_half_seed_I"], dtype=float).reshape(-1)
        seed_q = np.asarray(d["cr_half_seed_Q"], dtype=float).reshape(-1)
        rs = int(np.asarray(d["rise_start"]).item())
        fs = int(np.asarray(d["flat_start"]).item())
        fe = int(np.asarray(d["flat_stop"]).item())
        ds = int(np.asarray(d["fall_start"]).item())
    return t, seed_i, seed_q, rs, fs, fe, ds


def _looped_avg_opt(looped_npz: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    parent = looped_npz.parent
    fidelities = _looped_fidelities(parent)
    with np.load(looped_npz, allow_pickle=False) as d:
        t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        opt_i = np.asarray(d["cr_half_opt_I"], dtype=float)
        opt_q = np.asarray(d["cr_half_opt_Q"], dtype=float)
        is_avg = np.asarray(d["is_average"], dtype=bool).reshape(-1)
    row = int(np.where(is_avg)[0][0])
    f_avg = next(
        (r["process_fidelity"] for r in fidelities if r.get("cycle") == "avg"),
        float(np.mean([r["process_fidelity"] for r in fidelities])),
    )
    return t, opt_i[row], opt_q[row], f_avg


def _overlay_trace_seed(seed_npz: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    t, seed_i, seed_q, *_ = _load_looped_seed(seed_npz)
    return t, seed_i, seed_q, _looped_seed_label(seed_npz.parent)


def _overlay_trace(npz_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Return (t_ns, opt_I, opt_Q, legend_label) for the overlay/FFT comparison trace."""
    parent = npz_path.parent
    if "looped" in npz_path.name:
        fidelities = _looped_fidelities(parent)
        with np.load(npz_path, allow_pickle=False) as d:
            t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
            opt_i = np.asarray(d["cr_half_opt_I"], dtype=float)
            opt_q = np.asarray(d["cr_half_opt_Q"], dtype=float)
            is_avg = np.asarray(d["is_average"], dtype=bool).reshape(-1)
        row = int(np.where(is_avg)[0][0])
        f_avg = next(
            (r["process_fidelity"] for r in fidelities if r.get("cycle") == "avg"),
            float(np.mean([r["process_fidelity"] for r in fidelities])),
        )
        label = f"{parent.name} avg  F={f_avg:.5f}"
        i_y = opt_i[row]
        q_y = opt_q[row]
    else:
        payload = _load_json(parent, npz_path.stem)
        f_final = payload["final_metrics"]["process_fidelity"]
        with np.load(npz_path, allow_pickle=False) as d:
            t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
            i_y = np.asarray(d["cr_half_opt_I"], dtype=float).reshape(-1)
            q_y = np.asarray(d["cr_half_opt_Q"], dtype=float).reshape(-1)
        label = f"robust opt  F={f_final:.5f}"
    return t, i_y, q_y, label


def plot_looped_seed_npz(
    seed_npz: Path, looped_npz: Path, out_png: Path, *, n_sub: int = 2
) -> Path:
    """Looped run: initial seed vs optimized average envelope."""
    parent = seed_npz.parent
    t_sample, seed_i, seed_q, rs, fs, fe, ds = _load_looped_seed(seed_npz)
    _, opt_i, opt_q, f_avg = _looped_avg_opt(looped_npz)
    n_sub = max(1, int(n_sub))
    dt = _dt_ns(t_sample)
    t, seed_i_e = expand_samples_held_nsub(seed_i, dt, n_sub)
    _, seed_q_e = expand_samples_held_nsub(seed_q, dt, n_sub)
    _, opt_i_e = expand_samples_held_nsub(opt_i, dt, n_sub)
    _, opt_q_e = expand_samples_held_nsub(opt_q, dt, n_sub)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    for ax, seed_y, opt_y, comp in zip(
        axes,
        (seed_i_e, seed_q_e),
        (opt_i_e, opt_q_e),
        ("I", "Q"),
    ):
        ax.plot(t, seed_y, color="0.65", lw=1.2, ls="--", label=f"seed {comp} (MHz)")
        ax.plot(
            t,
            opt_y,
            color="tab:blue",
            lw=1.6,
            label=f"opt avg {comp}  F={f_avg:.5f}",
        )
        _shade_regions(ax, t, rs, fs, fe, ds, n_sub=n_sub)
        ax.set_ylabel(f"{comp} (MHz)")
        ax.grid(alpha=0.35)
        ax.legend(fontsize=8, loc="upper right")

    axes[1].set_xlabel(
        f"time within one CR half (ns)  |  held at n_sub={n_sub}  "
        f"(dt_sub={dt / n_sub:g} ns)"
    )
    axes[0].set_title(
        f"Looped GRAPE seed vs optimized average — {parent.name} "
        f"(each sample held ×{n_sub})"
    )
    fig.text(0.99, 0.005, "blue=rise  orange=flat  purple=fall", ha="right",
             va="bottom", fontsize=8, color="0.45")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def plot_looped_seed_fft(seed_npz: Path, looped_npz: Path, out_png: Path) -> Path:
    """FFT of looped seed vs optimized average (I+iQ, I only, Q only)."""
    parent = seed_npz.parent
    t, seed_i, seed_q, *_ = _load_looped_seed(seed_npz)
    _, opt_i, opt_q, f_avg = _looped_avg_opt(looped_npz)
    dt_ns = _dt_ns(t)

    f_mhz, a_seed_iq, a_seed_i, a_seed_q = _envelope_fft_components(
        seed_i, seed_q, dt_ns
    )
    _, a_opt_iq, a_opt_i, a_opt_q = _envelope_fft_components(opt_i, opt_q, dt_ns)
    sl = _freq_clip_slice(len(f_mhz))

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    panel_specs = (
        (a_seed_iq, a_opt_iq, r"$I+iQ$"),
        (a_seed_i, a_opt_i, r"$I$ only"),
        (a_seed_q, a_opt_q, r"$Q$ only"),
    )
    for ax, (seed_spec, opt_spec, comp) in zip(axes, panel_specs):
        seed_norm = a_seed_i if comp == r"$I+iQ$" else None
        _plot_fft_db(
            ax,
            f_mhz,
            seed_spec,
            sl,
            label=f"seed {comp}",
            color="0.65",
            lw=1.2,
            ls="--",
            norm_peak=seed_norm,
        )
        _plot_fft_db(
            ax,
            f_mhz,
            opt_spec,
            sl,
            label=f"opt avg {comp}  F={f_avg:.5f}",
            color="tab:blue",
            lw=1.6,
        )
        _style_fft_axis(ax)
        ax.set_ylabel("Amplitude (dB)")
        ax.legend(fontsize=8, loc="upper right")

    axes[0].set_title(
        f"Looped seed vs opt FFT — {parent.name}  (n_fft={FFT_N}, dt={dt_ns:g} ns)"
    )
    axes[2].set_xlabel("Frequency (MHz)")
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def plot_looped_fft(npz_path: Path, out_png: Path) -> Path:
    parent = npz_path.parent
    fidelities = _looped_fidelities(parent)
    label = parent.name

    with np.load(npz_path, allow_pickle=False) as d:
        t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        opt_i = np.asarray(d["cr_half_opt_I"], dtype=float)
        opt_q = np.asarray(d["cr_half_opt_Q"], dtype=float)
        is_avg = np.asarray(d["is_average"], dtype=bool).reshape(-1)

    dt_ns = _dt_ns(t)
    row = int(np.where(is_avg)[0][0])
    f_avg = next(
        (r["process_fidelity"] for r in fidelities if r.get("cycle") == "avg"),
        float(np.mean([r["process_fidelity"] for r in fidelities])),
    )

    f_mhz, a_iq, a_i, a_q = _envelope_fft_components(opt_i[row], opt_q[row], dt_ns)
    sl = _freq_clip_slice(len(f_mhz))

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    panels = (
        (a_iq, r"$I+iQ$", "black"),
        (a_i, r"$I$ only", "C1"),
        (a_q, r"$Q$ only", "C0"),
    )
    for ax, (spec, comp_label, color) in zip(axes, panels):
        _plot_fft_db(
            ax,
            f_mhz,
            spec,
            sl,
            label=f"{comp_label}  F={f_avg:.5f}",
            color=color,
        )
        _style_fft_axis(ax)
        ax.set_ylabel("Amplitude (dB)")
        ax.legend(fontsize=9, loc="upper right")

    axes[0].set_title(
        f"Looped GRAPE FFT — {label}  |  n_fft={FFT_N}  |  dt={dt_ns:g} ns"
    )
    axes[2].set_xlabel("Frequency (MHz)")
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def plot_robust_fft(npz_path: Path, out_png: Path) -> Path:
    parent = npz_path.parent
    payload = _load_json(parent, npz_path.stem)

    with np.load(npz_path, allow_pickle=False) as d:
        t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        seed_i = np.asarray(d["cr_half_seed_I"], dtype=float).reshape(-1)
        seed_q = np.asarray(d["cr_half_seed_Q"], dtype=float).reshape(-1)
        opt_i = np.asarray(d["cr_half_opt_I"], dtype=float).reshape(-1)
        opt_q = np.asarray(d["cr_half_opt_Q"], dtype=float).reshape(-1)

    dt_ns = _dt_ns(t)
    f_mhz, a_seed_iq, a_seed_i, a_seed_q = _envelope_fft_components(
        seed_i, seed_q, dt_ns
    )
    _, a_opt_iq, a_opt_i, a_opt_q = _envelope_fft_components(opt_i, opt_q, dt_ns)
    sl = _freq_clip_slice(len(f_mhz))

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    panel_specs = (
        (a_seed_iq, a_opt_iq, r"$I+iQ$"),
        (a_seed_i, a_opt_i, r"$I$ only"),
        (a_seed_q, a_opt_q, r"$Q$ only"),
    )
    for ax, (seed_spec, opt_spec, comp) in zip(axes, panel_specs):
        seed_norm = a_seed_i if comp == r"$I+iQ$" else None
        _plot_fft_db(
            ax,
            f_mhz,
            seed_spec,
            sl,
            label=f"seed {comp}",
            color="0.65",
            lw=1.2,
            ls="--",
            norm_peak=seed_norm,
        )
        _plot_fft_db(
            ax,
            f_mhz,
            opt_spec,
            sl,
            label=f"opt {comp}",
            color="tab:green",
            lw=1.6,
        )
        _style_fft_axis(ax)
        ax.set_ylabel("Amplitude (dB)")
        ax.legend(fontsize=8, loc="upper right")

    axes[0].set_title(f"Robust CR half FFT (n_fft={FFT_N}): $I$, $Q$, $I+iQ$")
    axes[2].set_xlabel("Frequency (MHz)")
    seed_m = payload["seed_metrics"]
    final_m = payload["final_metrics"]
    summary = (
        f"seed:  F_comb={seed_m['process_fidelity']:.5f}   "
        f"final: F_comb={final_m['process_fidelity']:.5f}   "
        f"dt={dt_ns:g} ns"
    )
    fig.text(0.01, 0.005, summary, ha="left", va="bottom", fontsize=8,
             family="monospace", color="0.15")
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def plot_fft_i_vs_iq(npz_path: Path, out_png: Path) -> Path:
    """Reference-style comparison: FFT(I) real vs FFT(I+iQ) complex."""
    with np.load(npz_path, allow_pickle=False) as d:
        t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        i_y = np.asarray(d["cr_half_opt_I"], dtype=float)
        q_y = np.asarray(d["cr_half_opt_Q"], dtype=float)
        if i_y.ndim == 2:
            is_avg = np.asarray(d["is_average"], dtype=bool).reshape(-1)
            row = int(np.where(is_avg)[0][0])
            i_y = i_y[row]
            q_y = q_y[row]
        else:
            i_y = i_y.reshape(-1)
            q_y = q_y.reshape(-1)

    dt_ns = _dt_ns(t)
    f_mhz, a_iq, a_i, a_q = _envelope_fft_components(i_y, q_y, dt_ns)
    sl = _freq_clip_slice(len(f_mhz))

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    panels = (
        (a_iq, r"$I+iQ$", "C2"),
        (a_i, r"$I$ only", "C1"),
        (a_q, r"$Q$ only", "C0"),
    )
    for ax, (spec, label, color) in zip(axes, panels):
        _plot_fft_db(ax, f_mhz, spec, sl, label=label, color=color)
        _style_fft_axis(ax)
        ax.set_ylabel("Amplitude (dB)")
        ax.legend(fontsize=9, loc="upper right")

    axes[0].set_title(f"Envelope spectrum — {npz_path.parent.name}  (n_fft={FFT_N})")
    axes[2].set_xlabel("Frequency (MHz)")
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def plot_fft_overlay(
    npz_paths: list[Path],
    out_png: Path,
    *,
    seed_npz: Path | None = None,
) -> Path:
    """Overlay FFT spectra: I+iQ, I only, and Q only (dB, notebook style)."""
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    colors = ("tab:blue", "tab:orange", "tab:green")
    linestyles = ("-", "--", "-")
    panel_ylabels = (r"$I+iQ$ (dB)", r"$I$ only (dB)", r"$Q$ only (dB)")

    f_mhz = None
    sl = None
    if seed_npz is not None and seed_npz.exists():
        t, i_y, q_y, label = _overlay_trace_seed(seed_npz)
        dt_ns = _dt_ns(t)
        f_mhz, a_iq, a_i, a_q = _envelope_fft_components(i_y, q_y, dt_ns)
        sl = _freq_clip_slice(len(f_mhz))
        for ax, spec in zip(axes, (a_iq, a_i, a_q)):
            _plot_fft_db(
                ax,
                f_mhz,
                spec,
                sl,
                label=label,
                color="0.45",
                lw=1.4,
                ls=":",
            )

    for npz_path, color, ls in zip(npz_paths, colors, linestyles):
        t, i_y, q_y, label = _overlay_trace(npz_path)
        dt_ns = _dt_ns(t)
        f_mhz, a_iq, a_i, a_q = _envelope_fft_components(i_y, q_y, dt_ns)
        sl = _freq_clip_slice(len(f_mhz))
        for ax, spec in zip(axes, (a_iq, a_i, a_q)):
            _plot_fft_db(
                ax,
                f_mhz,
                spec,
                sl,
                label=label,
                color=color,
                lw=1.8,
                ls=ls,
            )

    for ax, ylab in zip(axes, panel_ylabels):
        _style_fft_axis(ax)
        ax.set_ylabel(ylab)
        ax.legend(fontsize=8, loc="lower right")

    axes[0].set_title(rf"GRAPE envelope FFT — n_fft={FFT_N}, fftshift, dB")
    axes[2].set_xlabel("Frequency (MHz)")
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def plot_overlay(
    npz_paths: list[Path],
    out_png: Path,
    *,
    seed_npz: Path | None = None,
) -> Path:
    """Overlay average/optimized I and Q quadratures from each source."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    colors = ("tab:blue", "tab:orange", "tab:green")
    linestyles = ("-", "--", "-")

    if seed_npz is not None and seed_npz.exists():
        t, opt_i, opt_q, label = _overlay_trace_seed(seed_npz)
        for ax, opt_y, comp in zip(axes, (opt_i, opt_q), ("I", "Q")):
            ax.plot(t, opt_y, color="0.45", lw=1.4, ls=":",
                    label=label if comp == "I" else None)

    for npz_path, color, ls in zip(npz_paths, colors, linestyles):
        t, opt_i, opt_q, label = _overlay_trace(npz_path)

        for ax, opt_y, comp in zip(axes, (opt_i, opt_q), ("I", "Q")):
            ax.plot(t, opt_y, color=color, lw=1.8, ls=ls, label=label if comp == "I" else None)
            ax.set_ylabel(f"{comp} (MHz)")
            ax.grid(alpha=0.35)

    axes[0].set_title("GRAPE optimized I/Q envelopes — looped averages vs robust")
    axes[0].legend(fontsize=9, loc="lower right")
    axes[1].set_xlabel("time within one CR half (ns)")
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def main() -> None:
    outputs: list[Path] = []
    for npz_path in NPZ_SOURCES:
        if not npz_path.exists():
            raise FileNotFoundError(npz_path)
        if "looped" in npz_path.name:
            out = plot_looped_npz(npz_path, npz_path.parent / "cr_grape_looped_waveforms.png")
            fft_out = plot_looped_fft(npz_path, npz_path.parent / "cr_grape_looped_fft.png")
        else:
            out = plot_robust_npz(npz_path, npz_path.parent / f"{npz_path.stem}_waveform.png")
            fft_out = plot_robust_fft(npz_path, npz_path.parent / f"{npz_path.stem}_fft.png")
        outputs.append(out)
        outputs.append(fft_out)
        print(f"Saved {out}")
        print(f"Saved {fft_out}")

    seed_npz = LOOPED_SEED_NPZ if LOOPED_SEED_NPZ.exists() else None
    if seed_npz is not None:
        looped_npz = seed_npz.parent / "cr_grape_looped_all.npz"
        seed_wave = plot_looped_seed_npz(
            seed_npz, looped_npz, seed_npz.parent / "cr_grape_seed_waveform.png"
        )
        seed_fft = plot_looped_seed_fft(
            seed_npz, looped_npz, seed_npz.parent / "cr_grape_seed_fft.png"
        )
        outputs.extend((seed_wave, seed_fft))
        print(f"Saved {seed_wave}")
        print(f"Saved {seed_fft}")

    overlay = plot_overlay(
        NPZ_SOURCES, BASE / "grape_waveforms_overlay.png", seed_npz=seed_npz
    )
    outputs.append(overlay)
    print(f"Saved {overlay}")

    fft_overlay = plot_fft_overlay(
        NPZ_SOURCES, BASE / "grape_waveforms_fft_overlay.png", seed_npz=seed_npz
    )
    outputs.append(fft_overlay)
    print(f"Saved {fft_overlay}")

    i_vs_iq = plot_fft_i_vs_iq(
        NPZ_SOURCES[-1], BASE / "grape_waveforms_fft_i_vs_iq.png"
    )
    outputs.append(i_vs_iq)
    print(f"Saved {i_vs_iq}")


if __name__ == "__main__":
    main()
