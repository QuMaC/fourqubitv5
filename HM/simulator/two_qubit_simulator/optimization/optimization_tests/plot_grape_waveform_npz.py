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

Also writes a standalone ``cr_grape_seed.npz`` containing the seed waveform.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


from HM.simulator.two_qubit_simulator.engine.envelope_filters import (
    envelope_name,
    sample_envelope,
)


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


def save_seed_npz(npz_path: Path, out_npz: Path) -> Path:
    """Extract the seed waveform from a GRAPE ``.npz`` and save it standalone."""
    with np.load(npz_path, allow_pickle=False) as d:
        required = ["cr_half_seed_I", "cr_half_seed_Q"]
        missing = [k for k in required if k not in d.files]
        if missing:
            raise KeyError(
                f"Missing seed keys in {npz_path}: {missing}. "
                f"Available keys: {sorted(d.files)}"
            )

        if "t_ns" in d.files:
            t = np.asarray(d["t_ns"], dtype=float).reshape(-1)
        else:
            n = len(np.asarray(d["cr_half_seed_I"]).reshape(-1))
            t = np.arange(n, dtype=float)

        seed_i = np.asarray(d["cr_half_seed_I"], dtype=float).reshape(-1)
        seed_q = np.asarray(d["cr_half_seed_Q"], dtype=float).reshape(-1)

        payload: dict[str, np.ndarray] = {
            "t_ns": t,
            "cr_half_seed_I": seed_i,
            "cr_half_seed_Q": seed_q,
        }
        optional_keys = (
            "flat_knobs_seed",
            "rise_start",
            "flat_start",
            "flat_stop",
            "fall_start",
        )
        for key in optional_keys:
            if key in d.files:
                payload[key] = np.asarray(d[key])

    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out_npz, **payload)
    return out_npz


def plot_npz_waveform(
    npz_path: Path,
    out_png: Path,
    ylim: float | None = None,
    n_sub: int = 2,
    envelope: str | object = "identity",
) -> Path:
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
            t_sample = np.asarray(d["t_ns"], dtype=float).reshape(-1)
            dt = float(t_sample[1] - t_sample[0]) if len(t_sample) > 1 else 1.0
        else:
            n = len(np.asarray(d["cr_half_opt_I"]).reshape(-1))
            t_sample = np.arange(n, dtype=float)
            dt = 1.0

        seed_i = np.asarray(d["cr_half_seed_I"], dtype=float).reshape(-1)
        seed_q = np.asarray(d["cr_half_seed_Q"], dtype=float).reshape(-1)
        opt_i = np.asarray(d["cr_half_opt_I"], dtype=float).reshape(-1)
        opt_q = np.asarray(d["cr_half_opt_Q"], dtype=float).reshape(-1)

        rs = int(np.asarray(d["rise_start"]).item())
        fs = int(np.asarray(d["flat_start"]).item())
        fe = int(np.asarray(d["flat_stop"]).item())
        ds = int(np.asarray(d["fall_start"]).item())

    if not (len(seed_i) == len(seed_q) == len(opt_i) == len(opt_q) == len(t_sample)):
        raise ValueError("Waveform arrays and time axis have inconsistent lengths")

    # n_sub used to redraw the DAC hold on a finer grid. The curve is now the
    # envelope sesolve evaluates, so the solver sample dt is the one that matters.
    del n_sub
    env_label = envelope_name(envelope)
    seed = seed_i + 1j * seed_q
    opt = opt_i + 1j * opt_q
    t, seed_y = sample_envelope(envelope, seed, dt)
    _, opt_y = sample_envelope(envelope, opt, dt)

    all_vals = np.concatenate([seed_y.real, seed_y.imag, opt_y.real, opt_y.imag])
    y_lim = _resolved_ylim(ylim, all_vals)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    panels = (
        ("I", seed_y.real, opt_y.real),
        ("Q", seed_y.imag, opt_y.imag),
    )
    for ax, (label, seed_part, opt_part) in zip(axes, panels):
        ax.plot(t, seed_part, color="0.65", lw=1.2, ls="--", label=f"seed {label} (MHz)")
        ax.plot(t, opt_part, color="tab:green", lw=1.6, label=f"opt {label} (MHz)")
        ax.axvspan(rs * dt, fs * dt, color="tab:blue", alpha=0.08)
        ax.axvspan(fs * dt, fe * dt, color="tab:orange", alpha=0.08)
        ax.axvspan(ds * dt, len(t_sample) * dt, color="tab:purple", alpha=0.08)
        ax.set_ylabel(f"{label} (MHz)")
        ax.set_ylim(-y_lim, y_lim)
        ax.grid(alpha=0.35)
        ax.legend(fontsize=8, loc="upper right")

    axes[1].set_xlabel(
        f"time within one CR half (ns)  |  envelope={env_label}  |  dt={dt:g} ns"
    )
    axes[0].set_title(
        f"CR half envelope seen by sesolve from {npz_path.name}: seed vs optimized "
        f"({env_label}; shared y-limit = ±{y_lim:.3g} MHz)"
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
    out_seed_npz = base_dir / "results" / "cr_grape_seed.npz"

    seed_out = save_seed_npz(npz_path, out_seed_npz)
    print(f"Saved {seed_out}")

    # out = plot_npz_waveform(npz_path, out_png, ylim=ylim)
    # print(f"Saved {out}")


if __name__ == "__main__":
    main()
