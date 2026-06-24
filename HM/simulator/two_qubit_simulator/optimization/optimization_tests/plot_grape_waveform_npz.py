"""
plot_grape_waveform_npz.py
==========================
Simple utility to plot a GRAPE CR-half waveform saved in ``cr_grape_pulse.npz``.

The plot matches the style used by ``optimization/cr_grape.py``:
  - seed vs optimized envelopes for I and Q,
  - rise/flat/fall regions shaded in blue/orange/purple.

Unlike the original helper, this utility forces the same symmetric y-limits on
both quadrature panels (for example, setting ``ylim = 32`` gives
``[-32, 32]`` MHz on both I and Q).
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _resolved_ylim(user_ylim: float | None, values: np.ndarray) -> float:
    """Return a positive symmetric y-limit magnitude for both I/Q panels."""
    if user_ylim is not None:
        if user_ylim <= 0:
            raise ValueError(f"ylim must be positive, got {user_ylim}")
        return float(user_ylim)

    peak = float(np.max(np.abs(values)))
    if peak <= 0:
        return 1.0
    # Round up to a neat 1 MHz boundary with a little margin.
    return float(np.ceil(1.05 * peak))


def plot_npz_waveform(npz_path: Path, out_png: Path, ylim: float | None = None) -> Path:
    with np.load(npz_path, allow_pickle=False) as d:
        required = [
            "cr_half_seed_I",
            "cr_half_seed_Q",
            "cr_half_opt_I",
            "cr_half_opt_Q",
            "rise_start",
            "flat_start",
            "flat_stop",
            "fall_start",
        ]
        missing = [k for k in required if k not in d.files]
        if missing:
            raise KeyError(
                f"Missing keys in {npz_path}: {missing}. Available keys: {sorted(d.files)}"
            )

        # Prefer saved t-axis if present; otherwise assume 1 ns sampling.
        if "t_ns" in d.files:
            t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        else:
            n = len(np.asarray(d["cr_half_opt_I"]).reshape(-1))
            t = np.arange(n, dtype=float)

        seed_i = np.asarray(d["cr_half_seed_I"], dtype=float).reshape(-1)
        seed_q = np.asarray(d["cr_half_seed_Q"], dtype=float).reshape(-1)
        opt_i = np.asarray(d["cr_half_opt_I"], dtype=float).reshape(-1)
        opt_q = np.asarray(d["cr_half_opt_Q"], dtype=float).reshape(-1)

        rs = int(np.asarray(d["rise_start"]).item())
        fs = int(np.asarray(d["flat_start"]).item())
        fe = int(np.asarray(d["flat_stop"]).item())
        ds = int(np.asarray(d["fall_start"]).item())
        de = len(t)

    if not (len(seed_i) == len(seed_q) == len(opt_i) == len(opt_q) == len(t)):
        raise ValueError("Waveform arrays and time axis have inconsistent lengths")

    all_vals = np.concatenate([seed_i, seed_q, opt_i, opt_q])
    y_lim = _resolved_ylim(ylim, all_vals)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    panels = (
        ("I", seed_i, opt_i),
        ("Q", seed_q, opt_q),
    )
    for ax, (label, seed_y, opt_y) in zip(axes, panels):
        ax.plot(t, seed_y, color="0.65", lw=1.2, ls="--", label=f"seed {label} (MHz)")
        ax.plot(t, opt_y, color="tab:green", lw=1.6, label=f"opt {label} (MHz)")
        ax.axvspan(t[rs], t[fs - 1] if fs > rs else t[rs], color="tab:blue", alpha=0.08)
        ax.axvspan(t[fs], t[fe - 1] if fe > fs else t[fs], color="tab:orange", alpha=0.08)
        ax.axvspan(t[ds], t[de - 1] if de > ds else t[ds], color="tab:purple", alpha=0.08)
        ax.set_ylabel(f"{label} (MHz)")
        ax.set_ylim(-y_lim, y_lim)
        ax.grid(alpha=0.35)
        ax.legend(fontsize=8, loc="upper right")

    axes[1].set_xlabel("time within one CR half (ns)")
    axes[0].set_title(
        f"CR half envelope from {npz_path.name}: seed vs optimized "
        f"(shared y-limit = ±{y_lim:.3g} MHz)"
    )
    fig.text(
        0.99,
        0.01,
        "blue=rise  orange=flat  purple=fall",
        ha="right",
        va="bottom",
        fontsize=8,
        color="0.35",
    )
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    return out_png


def main() -> None:
    # Set these in-file, same style as other experiment scripts.
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    ylim = 35.0  # MHz; set to None for auto-scaling
    npz_path = base_dir / "results" / "cr_grape_pulse.npz"
    out_png = base_dir / "results" / f"cr_grape_waveform_equal_ylim_{ylim}.png"

    out = plot_npz_waveform(npz_path, out_png, ylim=ylim)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
