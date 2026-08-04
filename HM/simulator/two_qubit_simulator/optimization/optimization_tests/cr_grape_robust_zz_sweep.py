"""Robust GRAPE ZZ-span sweep: flat-top seed vs warm-chain from previous opt.

ZZ span convention
------------------
``zz_shift_mhz`` is the *full* span. The two robust cases are at
``+/- zz_shift_mhz / 2``. Sweeping 0..300 kHz in 50 kHz steps means spans
``{0, 50, ..., 300} kHz`` -> half-shifts ``{0, +/-25, ..., +/-150} kHz``.

At ZZ = 0 both detunings are identical; we still call robust GRAPE so the
loop is uniform.

Seed modes
----------
- ``flat``: every span starts from the calibrated flat-top seed.
- ``warm``: span 0 starts from flat-top; each later span starts from the
  previous span's *optimized* knobs (same warm branch).
- ``both``: run flat and warm independently for comparison.

Edit the knobs below, then run this file directly.
"""

from __future__ import annotations

import json
import os
from typing import Literal

import numpy as np

from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    FIDELITY_METRICS,
    FidelityMetric,
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
    RobustGrapeResult,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "robust_zz_sweep")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Knobs — edit these
# ---------------------------------------------------------------------------

# Seed pulse (same convention as cr_grape_robust_test.py).
CR_PULSE_PARAMS = {"amp_mhz": 21.0, "t_rise_ns": 16, "phase_rad": 0.0}
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 61
N_LINK_SAMPLES = 8

# Full ZZ span sweep (kHz). Each value is zz_shift; cases are +/- span/2.
ZZ_SPANS_KHZ = list(range(0, 301, 50))  # 0, 50, ..., 300

# "flat" | "warm" | "both"
SEED_MODES: Literal["flat", "warm", "both"] = "both"

WEIGHTS = (0.5, 0.5)
FIDELITY_METRIC: FidelityMetric = "mean_minus_spread"
SPREAD_PENALTY_LAMBDA = 0.3

TARGET_GATE = None  # inferred from seed at each run; or "zx_90" / "zx_m90"
AMP_BOUND_MHZ = 48.0
MAXITER = 80
OPTIMIZE = True
QUBIT_PAIR = [1, 2]
N_LEVELS = 3


def _resolve_modes(seed_modes: str) -> list[str]:
    key = str(seed_modes).strip().lower()
    if key == "flat":
        return ["flat"]
    if key == "warm":
        return ["warm"]
    if key == "both":
        return ["flat", "warm"]
    raise ValueError(f"SEED_MODES must be flat|warm|both, got {seed_modes!r}")


def _span_dir(results_dir: str, mode: str, zz_khz: int) -> str:
    return os.path.join(results_dir, mode, f"zz_{zz_khz:03d}_kHz")


def _summary_path(results_dir: str) -> str:
    return os.path.join(results_dir, "summary.json")


def _write_summary(results_dir: str, rows: list[dict]) -> None:
    path = _summary_path(results_dir)
    payload = {
        "zz_spans_khz": list(ZZ_SPANS_KHZ),
        "seed_modes": SEED_MODES,
        "config": {
            "amp_mhz": CR_PULSE_PARAMS["amp_mhz"],
            "flat_len_ns": FLAT_LEN_NS,
            "n_flat_knobs": N_FLAT_KNOBS,
            "n_link_samples": N_LINK_SAMPLES,
            "fidelity_metric": FIDELITY_METRIC,
            "spread_penalty_lambda": SPREAD_PENALTY_LAMBDA,
            "weights": list(WEIGHTS),
            "amp_bound_mhz": AMP_BOUND_MHZ,
            "maxiter": MAXITER,
            "optimize": OPTIMIZE,
            "target_gate": TARGET_GATE,
            "qubit_pair": list(QUBIT_PAIR),
            "n_levels": N_LEVELS,
        },
        "runs": rows,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Updated {path}")


def _print_table(rows: list[dict]) -> None:
    if not rows:
        return
    print("\nZZ-span sweep summary")
    print(
        f"{'zz_kHz':>7}  {'mode':>5}  {'F_comb':>9}  {'F_a':>9}  "
        f"{'F_b':>9}  {'|dF|':>9}  target"
    )
    print("-" * 72)
    for r in rows:
        print(
            f"{r['zz_span_khz']:7d}  {r['mode']:>5}  "
            f"{r['process_fidelity']:9.5f}  "
            f"{r['process_fidelity_a']:9.5f}  "
            f"{r['process_fidelity_b']:9.5f}  "
            f"{r['fidelity_spread']:9.5f}  "
            f"{r.get('target_gate', '?')}"
        )


def _row_from_result(
    *,
    zz_khz: int,
    mode: str,
    result: RobustGrapeResult,
    out_dir: str,
) -> dict:
    m = result.final_metrics
    return {
        "zz_span_khz": int(zz_khz),
        "zz_span_mhz": float(zz_khz) / 1000.0,
        "shifts_mhz": list(result.shifts_mhz),
        "mode": mode,
        "target_gate": result.target_gate,
        "process_fidelity": float(m["process_fidelity"]),
        "process_fidelity_a": float(m["process_fidelity_a"]),
        "process_fidelity_b": float(m["process_fidelity_b"]),
        "fidelity_spread": float(
            m.get(
                "fidelity_spread",
                abs(m["process_fidelity_a"] - m["process_fidelity_b"]),
            )
        ),
        "seed_process_fidelity": float(result.seed_metrics["process_fidelity"]),
        "results_dir": out_dir,
    }


def _make_config(zz_span_mhz: float, results_dir: str) -> RobustCRGrapeConfig:
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
        amp_bound_mhz=AMP_BOUND_MHZ,
        maxiter=MAXITER,
        qubit_pair=list(QUBIT_PAIR),
        n_levels=N_LEVELS,
        optimize=OPTIMIZE,
        results_dir=results_dir,
    )


def run_robust_zz_sweep() -> list[dict]:
    """Sweep ZZ spans; optionally compare flat-top vs warm-chain seeds."""
    modes = _resolve_modes(SEED_MODES)
    print("Fidelity metrics available:")
    for key, desc in FIDELITY_METRICS.items():
        marker = " <-- selected" if key == FIDELITY_METRIC else ""
        print(f"  {key:18s}  {desc}{marker}")

    print(
        f"\nZZ span sweep: {ZZ_SPANS_KHZ[0]}..{ZZ_SPANS_KHZ[-1]} kHz "
        f"(step {ZZ_SPANS_KHZ[1] - ZZ_SPANS_KHZ[0] if len(ZZ_SPANS_KHZ) > 1 else 0} kHz)"
    )
    print(
        f"SEED_MODES={SEED_MODES} -> branches {modes}  |  "
        f"amp={CR_PULSE_PARAMS['amp_mhz']} MHz  flat={FLAT_LEN_NS:.0f} ns  "
        f"knobs={N_FLAT_KNOBS}"
    )
    print(
        "Note: zz_shift is the FULL span; robust cases are +/- span/2. "
        "Warm chain: span 0 = flat-top, later spans inherit previous opt knobs."
    )

    rows: list[dict] = []
    # Warm branch carries the previous optimized knobs; flat always uses None.
    warm_prev_opt: np.ndarray | None = None

    for zz_khz in ZZ_SPANS_KHZ:
        zz_mhz = float(zz_khz) / 1000.0
        for mode in modes:
            out_dir = _span_dir(RESULTS_DIR, mode, zz_khz)
            os.makedirs(out_dir, exist_ok=True)

            # Warm: ZZ=0 (or first span) uses flat-top; later spans warm-start.
            seed_override = None
            if mode == "warm" and warm_prev_opt is not None:
                seed_override = warm_prev_opt

            print(f"\n{'=' * 64}")
            print(
                f"ZZ span = {zz_khz} kHz ({zz_mhz:.4g} MHz)  |  mode={mode}  |  "
                f"seed={'warm' if seed_override is not None else 'flat-top'}"
            )
            print(f"{'=' * 64}")

            config = _make_config(zz_mhz, out_dir)
            optimizer = RobustCRGrapeOptimizer(
                config, flat_knobs_seed=seed_override
            )
            result = optimizer.run()
            result.save(out_dir)

            row = _row_from_result(
                zz_khz=zz_khz, mode=mode, result=result, out_dir=out_dir
            )
            rows.append(row)
            _write_summary(RESULTS_DIR, rows)
            _print_table(rows)

            if mode == "warm":
                warm_prev_opt = result.flat_knobs_opt.copy()

    print(f"\nDone. Summary: {_summary_path(RESULTS_DIR)}")
    return rows


if __name__ == "__main__":
    run_robust_zz_sweep()
