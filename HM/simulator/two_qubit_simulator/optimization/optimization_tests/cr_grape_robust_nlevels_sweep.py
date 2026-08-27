"""Seed-only n_levels × ZZ-span fidelity sweep on dynamiqs / JAX (no GRAPE).

For each Hilbert-space truncation ``n_levels`` and each ZZ span, evaluate a
fixed flat-top (or custom) seed pulse at the two robust detunings
``+/- zz_shift/2``. Uses ``use_jax_grad=True`` so evolution is dynamiqs
(Tsit5) with batched frames. No optimization, no pulse/convergence dumps —
only ``summary.json`` and fidelity plots (one line per ``n_levels``).

Seed source (first match wins)
-----------------------------
1. ``SEED_KNOBS`` — complex array of length ``N_FLAT_KNOBS``
2. ``SEED_NPZ`` — robust GRAPE ``.npz``; loads ``SEED_NPZ_KEY``
   (``flat_knobs_opt`` or ``flat_knobs_seed``)
3. else calibrated flat-top from ``CR_PULSE_PARAMS``

Keep ``FLAT_LEN_NS`` / ``t_rise_ns`` / ``N_LINK_SAMPLES`` consistent with
the waveform that produced those knobs.

ZZ span convention
------------------
``zz_shift_mhz`` is the *full* span. Cases are at ``+/- zz_shift_mhz / 2``.

Edit the knobs below, then run this file directly.
"""

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    FIDELITY_METRICS,
    FidelityMetric,
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
)

RESULTS_NAME = "seed_nlevels_zz_sweep_dynamiqs"
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", RESULTS_NAME)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Knobs — edit these
# ---------------------------------------------------------------------------

CR_PULSE_PARAMS = {"amp_mhz": 21.0, "t_rise_ns": 16, "phase_rad": 0.0}
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 61
N_LINK_SAMPLES = 8

# Custom waveform (optional). Prefer SEED_KNOBS; else load from SEED_NPZ.
SEED_KNOBS: np.ndarray | None = None
SEED_NPZ: str | None = None
SEED_NPZ_KEY = "flat_knobs_opt"  # or "flat_knobs_seed"

# Full ZZ span sweep (kHz). Each value is zz_shift; cases are +/- span/2.
ZZ_SPANS_KHZ = list(range(0, 301, 50))  # 0, 50, ..., 300
# ZZ_SPANS_KHZ = [180]  # 0, 50, ..., 300

# Transmon levels per qubit (Hilbert dim = n_levels**2).
N_LEVELS_VALS = [3, 4, 5, 6, 7] 

WEIGHTS = (0.5, 0.5)
FIDELITY_METRIC: FidelityMetric = "mean_minus_spread"
SPREAD_PENALTY_LAMBDA = 0.3

TARGET_GATE = "zx_m90"  # inferred from seed; or "zx_90" / "zx_m90"
QUBIT_PAIR = [1, 2]
# Passed for API parity; unused by dynamiqs Path A (Tsit5).
N_SUB = 2
USE_JAX_GRAD = True
EVOLUTION = "comp"


def _summary_path(results_dir: str) -> str:
    return os.path.join(results_dir, "summary.json")


def _plot_path(results_dir: str) -> str:
    return os.path.join(results_dir, "seed_fidelity_vs_zz_by_nlevels.png")


def _plot_nlevels_path(results_dir: str) -> str:
    return os.path.join(results_dir, "seed_fidelity_vs_nlevels_by_zz.png")


def _plot_delta_nlevels_path(results_dir: str) -> str:
    return os.path.join(results_dir, "seed_fidelity_delta_vs_nlevels_by_zz.png")


def _load_knobs_from_npz(path: str, key: str) -> np.ndarray:
    with np.load(path, allow_pickle=False) as d:
        if key in d.files:
            knobs = np.asarray(d[key]).reshape(-1)
        elif f"{key}_real" in d.files and f"{key}_imag" in d.files:
            knobs = (
                np.asarray(d[f"{key}_real"], dtype=float)
                + 1j * np.asarray(d[f"{key}_imag"], dtype=float)
            ).reshape(-1)
        else:
            raise KeyError(
                f"{path} has no {key!r} (or {key}_real/_imag). "
                f"Available: {sorted(d.files)}"
            )
    if not np.iscomplexobj(knobs):
        knobs = knobs.astype(complex)
    return knobs


def _resolve_seed_knobs() -> tuple[np.ndarray | None, str]:
    """Return (knobs_or_None, source_label). None → calibrated flat-top."""
    if SEED_KNOBS is not None:
        knobs = np.asarray(SEED_KNOBS, dtype=complex).reshape(-1)
        if knobs.size != N_FLAT_KNOBS:
            raise ValueError(
                f"SEED_KNOBS length {knobs.size} != N_FLAT_KNOBS={N_FLAT_KNOBS}"
            )
        return knobs, "SEED_KNOBS"
    if SEED_NPZ:
        path = os.path.expanduser(SEED_NPZ)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        knobs = _load_knobs_from_npz(path, SEED_NPZ_KEY)
        if knobs.size != N_FLAT_KNOBS:
            raise ValueError(
                f"Loaded {SEED_NPZ_KEY} length {knobs.size} from {path} "
                f"!= N_FLAT_KNOBS={N_FLAT_KNOBS}"
            )
        return knobs, f"SEED_NPZ:{path}#{SEED_NPZ_KEY}"
    return None, "calibrated_flat_top"


def _make_config(zz_span_mhz: float, n_levels: int) -> RobustCRGrapeConfig:
    return RobustCRGrapeConfig(
        flat_len_ns=FLAT_LEN_NS,
        n_flat_knobs=N_FLAT_KNOBS,
        seed_amp_mhz=CR_PULSE_PARAMS["amp_mhz"],
        seed_phase_rad=CR_PULSE_PARAMS["phase_rad"],
        t_rise_ns=CR_PULSE_PARAMS["t_rise_ns"],
        n_link_samples=N_LINK_SAMPLES,
        zz_shift_mhz=zz_span_mhz,
        shifts_mhz=None,
        weights=WEIGHTS,
        fidelity_metric=FIDELITY_METRIC,
        spread_penalty_lambda=SPREAD_PENALTY_LAMBDA,
        target_gate=TARGET_GATE,
        qubit_pair=list(QUBIT_PAIR),
        n_levels=int(n_levels),
        n_sub=N_SUB,
        optimize=False,
        show_progress=False,
        results_dir=RESULTS_DIR,
        use_jax_grad=USE_JAX_GRAD,
        evolution=EVOLUTION,
    )


def _row_from_eval(
    *,
    zz_khz: int,
    n_levels: int,
    shifts_mhz: list[float],
    target_gate: str,
    metrics: dict,
) -> dict:
    return {
        "zz_span_khz": int(zz_khz),
        "zz_span_mhz": float(zz_khz) / 1000.0,
        "n_levels": int(n_levels),
        "shifts_mhz": list(shifts_mhz),
        "target_gate": target_gate,
        "process_fidelity": float(metrics["process_fidelity"]),
        "process_fidelity_a": float(metrics["process_fidelity_a"]),
        "process_fidelity_b": float(metrics["process_fidelity_b"]),
        "fidelity_spread": float(
            metrics.get(
                "fidelity_spread",
                abs(metrics["process_fidelity_a"] - metrics["process_fidelity_b"]),
            )
        ),
        "leakage": float(metrics["leakage"]),
    }


def _write_summary(results_dir: str, rows: list[dict], seed_source: str) -> None:
    path = _summary_path(results_dir)
    payload = {
        "zz_spans_khz": list(ZZ_SPANS_KHZ),
        "n_levels_vals": list(N_LEVELS_VALS),
        "seed_source": seed_source,
        "config": {
            "amp_mhz": CR_PULSE_PARAMS["amp_mhz"],
            "flat_len_ns": FLAT_LEN_NS,
            "n_flat_knobs": N_FLAT_KNOBS,
            "n_link_samples": N_LINK_SAMPLES,
            "seed_npz": SEED_NPZ,
            "seed_npz_key": SEED_NPZ_KEY if SEED_NPZ else None,
            "fidelity_metric": FIDELITY_METRIC,
            "spread_penalty_lambda": SPREAD_PENALTY_LAMBDA,
            "weights": list(WEIGHTS),
            "optimize": False,
            "target_gate": TARGET_GATE,
            "qubit_pair": list(QUBIT_PAIR),
            "n_sub": N_SUB,
            "use_jax_grad": USE_JAX_GRAD,
            "evolution": EVOLUTION,
            "results_name": RESULTS_NAME,
        },
        "runs": rows,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Updated {path}")


def _print_table(rows: list[dict]) -> None:
    if not rows:
        return
    print("\nSeed n_levels × ZZ summary (dynamiqs / JAX)")
    print(
        f"{'n_lev':>5}  {'zz_kHz':>7}  {'F_comb':>9}  {'F_a':>9}  "
        f"{'F_b':>9}  {'|dF|':>9}  {'leak':>9}  target"
    )
    print("-" * 82)
    for r in rows:
        print(
            f"{r['n_levels']:5d}  {r['zz_span_khz']:7d}  "
            f"{r['process_fidelity']:9.5f}  "
            f"{r['process_fidelity_a']:9.5f}  "
            f"{r['process_fidelity_b']:9.5f}  "
            f"{r['fidelity_spread']:9.5f}  "
            f"{r['leakage']:9.5f}  "
            f"{r.get('target_gate', '?')}"
        )


def _plot_fidelity_vs_zz(
    rows: list[dict], out_png: str, seed_source: str
) -> None:
    """One F_comb vs ZZ line per n_levels."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    cmap = plt.cm.viridis
    n_lines = max(len(N_LEVELS_VALS), 1)

    for i, n_levels in enumerate(N_LEVELS_VALS):
        subset = [r for r in rows if r["n_levels"] == n_levels]
        subset.sort(key=lambda r: r["zz_span_khz"])
        if not subset:
            continue
        zz = [r["zz_span_khz"] for r in subset]
        f_c = [r["process_fidelity"] for r in subset]
        color = cmap(i / max(n_lines - 1, 1))
        ax.plot(
            zz,
            f_c,
            "o-",
            ms=4,
            lw=1.4,
            color=color,
            label=f"n_levels={n_levels}",
        )

    ax.set_xlabel("ZZ span (kHz)  [cases at ±span/2]")
    ax.set_ylabel("seed process fidelity (combined)")
    seed_short = seed_source if len(seed_source) < 60 else seed_source[-57:] + "…"
    ax.set_title(
        f"Seed fidelity vs ZZ (dynamiqs)  |  flat={FLAT_LEN_NS:.0f} ns  "
        f"knobs={N_FLAT_KNOBS}  |  metric={FIDELITY_METRIC}\n"
        f"seed={seed_short}"
    )
    ax.grid(alpha=0.35)
    ax.legend(fontsize=8, ncol=2, loc="best")
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"Saved {out_png}")


def _plot_fidelity_vs_nlevels(
    rows: list[dict],
    out_png: str,
    seed_source: str,
    zz_spans_khz: list[int] | None = None,
) -> None:
    """One F_comb vs n_levels line per ZZ frequency."""
    zz_list = list(zz_spans_khz) if zz_spans_khz is not None else list(ZZ_SPANS_KHZ)
    if not zz_list:
        zz_list = sorted({int(r["zz_span_khz"]) for r in rows})

    fig, ax = plt.subplots(figsize=(9, 5.5))
    cmap = plt.cm.tab10 if len(zz_list) <= 10 else plt.cm.viridis
    n_lines = max(len(zz_list), 1)

    for i, zz_khz in enumerate(zz_list):
        subset = [r for r in rows if int(r["zz_span_khz"]) == int(zz_khz)]
        subset.sort(key=lambda r: r["n_levels"])
        if not subset:
            continue
        n_levs = [r["n_levels"] for r in subset]
        f_c = [r["process_fidelity"] for r in subset]
        color = cmap(i / max(n_lines - 1, 1)) if n_lines > 10 else cmap(i % 10)
        ax.plot(
            n_levs,
            f_c,
            "o-",
            ms=4,
            lw=1.4,
            color=color,
            label=f"ZZ={zz_khz} kHz",
        )

    ax.set_xlabel("n_levels  (transmon levels per qubit)")
    ax.set_ylabel("seed process fidelity (combined)")
    seed_short = seed_source if len(seed_source) < 60 else seed_source[-57:] + "…"
    ax.set_title(
        f"Seed fidelity vs n_levels (dynamiqs)  |  flat={FLAT_LEN_NS:.0f} ns  "
        f"knobs={N_FLAT_KNOBS}  |  metric={FIDELITY_METRIC}\n"
        f"seed={seed_short}"
    )
    ax.grid(alpha=0.35)
    ax.legend(fontsize=8, ncol=2, loc="best")
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"Saved {out_png}")


def _plot_fidelity_delta_vs_nlevels(
    rows: list[dict],
    out_png: str,
    seed_source: str,
    zz_spans_khz: list[int] | None = None,
) -> None:
    """ΔF = F(n_levels) − F(previous) vs higher n_levels; one colour per ZZ."""
    zz_list = list(zz_spans_khz) if zz_spans_khz is not None else list(ZZ_SPANS_KHZ)
    if not zz_list:
        zz_list = sorted({int(r["zz_span_khz"]) for r in rows})

    fig, ax = plt.subplots(figsize=(9, 5.5))
    cmap = plt.cm.tab10 if len(zz_list) <= 10 else plt.cm.viridis
    n_lines = max(len(zz_list), 1)

    for i, zz_khz in enumerate(zz_list):
        subset = [r for r in rows if int(r["zz_span_khz"]) == int(zz_khz)]
        subset.sort(key=lambda r: r["n_levels"])
        if len(subset) < 2:
            continue
        n_levs = [r["n_levels"] for r in subset]
        f_c = [r["process_fidelity"] for r in subset]
        x = n_levs[1:]
        dF = [f_c[j] - f_c[j - 1] for j in range(1, len(f_c))]
        color = cmap(i / max(n_lines - 1, 1)) if n_lines > 10 else cmap(i % 10)
        ax.plot(
            x,
            dF,
            "o-",
            ms=4,
            lw=1.4,
            color=color,
            label=f"ZZ={zz_khz} kHz",
        )

    ax.axhline(0.0, color="0.5", lw=0.9, ls="--")
    ax.set_xlabel("n_levels  (Δ from previous n_levels → this)")
    ax.set_ylabel("ΔF = F(n_levels) − F(previous)")
    seed_short = seed_source if len(seed_source) < 60 else seed_source[-57:] + "…"
    ax.set_title(
        f"Seed fidelity step Δ vs n_levels (dynamiqs)  |  flat={FLAT_LEN_NS:.0f} ns  "
        f"knobs={N_FLAT_KNOBS}  |  metric={FIDELITY_METRIC}\n"
        f"seed={seed_short}"
    )
    ax.grid(alpha=0.35)
    ax.legend(fontsize=8, ncol=2, loc="best")
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"Saved {out_png}")


def run_seed_nlevels_zz_sweep() -> list[dict]:
    """Evaluate seed fidelity over n_levels × ZZ grid on dynamiqs / JAX."""
    seed_knobs, seed_source = _resolve_seed_knobs()

    print("Fidelity metrics available:")
    for key, desc in FIDELITY_METRICS.items():
        marker = " <-- selected" if key == FIDELITY_METRIC else ""
        print(f"  {key:18s}  {desc}{marker}")

    print(
        f"\nSeed-only sweep (no GRAPE, dynamiqs/JAX): "
        f"n_levels={N_LEVELS_VALS}  ×  "
        f"ZZ={ZZ_SPANS_KHZ[0]}..{ZZ_SPANS_KHZ[-1]} kHz"
    )
    print(
        f"seed={seed_source}  flat={FLAT_LEN_NS:.0f} ns  "
        f"knobs={N_FLAT_KNOBS}  use_jax_grad={USE_JAX_GRAD}  "
        f"results={RESULTS_NAME}"
    )

    rows: list[dict] = []
    for n_levels in N_LEVELS_VALS:
        for zz_khz in ZZ_SPANS_KHZ:
            zz_mhz = float(zz_khz) / 1000.0
            print(f"\n{'=' * 64}")
            print(
                f"n_levels={n_levels}  |  ZZ span = {zz_khz} kHz "
                f"({zz_mhz:.4g} MHz)"
            )
            print(f"{'=' * 64}")

            config = _make_config(zz_mhz, n_levels)
            optimizer = RobustCRGrapeOptimizer(
                config, flat_knobs_seed=seed_knobs
            )
            metrics = optimizer.evaluate_seed()
            print(
                f"  F_comb={metrics['process_fidelity']:.5f}  "
                f"F_a={metrics['process_fidelity_a']:.5f}  "
                f"F_b={metrics['process_fidelity_b']:.5f}  "
                f"leak={metrics['leakage']:.5f}  "
                f"target={optimizer.target_gate}"
            )

            rows.append(
                _row_from_eval(
                    zz_khz=zz_khz,
                    n_levels=n_levels,
                    shifts_mhz=list(optimizer.shifts),
                    target_gate=optimizer.target_gate,
                    metrics=metrics,
                )
            )
            _write_summary(RESULTS_DIR, rows, seed_source)
            _print_table(rows)

    _plot_fidelity_vs_zz(rows, _plot_path(RESULTS_DIR), seed_source)
    _plot_fidelity_vs_nlevels(rows, _plot_nlevels_path(RESULTS_DIR), seed_source)
    _plot_fidelity_delta_vs_nlevels(
        rows, _plot_delta_nlevels_path(RESULTS_DIR), seed_source
    )
    print(f"\nDone. Summary: {_summary_path(RESULTS_DIR)}")
    return rows


def replot_from_summary(summary_path: str | None = None) -> None:
    """Rebuild plots from an existing summary.json (no re-evaluation)."""
    path = summary_path or _summary_path(RESULTS_DIR)
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    rows = payload["runs"]
    seed_source = payload.get("seed_source", "unknown")
    zz_spans = payload.get("zz_spans_khz")
    out_dir = os.path.dirname(path)
    _plot_fidelity_vs_zz(rows, _plot_path(out_dir), seed_source)
    _plot_fidelity_vs_nlevels(
        rows, _plot_nlevels_path(out_dir), seed_source, zz_spans_khz=zz_spans
    )
    _plot_fidelity_delta_vs_nlevels(
        rows,
        _plot_delta_nlevels_path(out_dir),
        seed_source,
        zz_spans_khz=zz_spans,
    )


if __name__ == "__main__":
    run_seed_nlevels_zz_sweep()
