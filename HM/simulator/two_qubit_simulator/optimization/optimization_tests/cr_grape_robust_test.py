"""Robust (two-detuning) echoed CR GRAPE: one pulse optimized across a ZZ shift.

Edit the knobs below, then run this file directly.
"""

from __future__ import annotations

import os

from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    FIDELITY_METRICS,
    FidelityMetric,
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "robust")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Knobs — edit these
# ---------------------------------------------------------------------------

# Seed pulse (same convention as cr_grape_test.py).
CR_PULSE_PARAMS = {"amp_mhz": 21.0, "t_rise_ns": 16, "phase_rad": 0.0}
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 61#46
N_LINK_SAMPLES = 8

# Two-detuning setup. ZZ_SHIFT_MHZ expands to +/- ZZ_SHIFT_MHZ/2.
# Set SHIFTS_MHZ to an explicit pair to override (e.g. [-0.15, 0.05]).
ZZ_SHIFT_MHZ = 0.3
SHIFTS_MHZ = None
WEIGHTS = (0.5, 0.5)

# Combined fidelity metric — pick one of FIDELITY_METRICS:
#   weighted_mean      -> w_a*F_a + w_b*F_b
#   geometric_mean     -> sqrt(F_a * F_b)
#   mean_minus_spread  -> weighted mean - SPREAD_PENALTY_LAMBDA * |F_a - F_b|
FIDELITY_METRIC: FidelityMetric = "mean_minus_spread"
SPREAD_PENALTY_LAMBDA = 0.3

TARGET_GATE = None  # inferred from seed; or "zx_90" / "zx_m90"
AMP_BOUND_MHZ = 48.0
MAXITER = 80
OPTIMIZE = False  # set False for a fast seed-only check


def run_robust_cr_grape() -> None:
    """Build config from the knobs above, optimize, and save results."""
    for key, desc in FIDELITY_METRICS.items():
        marker = " <-- selected" if key == FIDELITY_METRIC else ""
        print(f"  {key:18s}  {desc}{marker}")

    config = RobustCRGrapeConfig(
        flat_len_ns=FLAT_LEN_NS,
        n_flat_knobs=N_FLAT_KNOBS,
        seed_amp_mhz=CR_PULSE_PARAMS["amp_mhz"],
        seed_phase_rad=CR_PULSE_PARAMS["phase_rad"],
        t_rise_ns=CR_PULSE_PARAMS["t_rise_ns"],
        n_link_samples=N_LINK_SAMPLES,
        zz_shift_mhz=ZZ_SHIFT_MHZ,
        shifts_mhz=SHIFTS_MHZ,
        weights=WEIGHTS,
        fidelity_metric=FIDELITY_METRIC,
        spread_penalty_lambda=SPREAD_PENALTY_LAMBDA,
        target_gate=TARGET_GATE,
        amp_bound_mhz=AMP_BOUND_MHZ,
        maxiter=MAXITER,
        optimize=OPTIMIZE,
        results_dir=RESULTS_DIR,
    )

    optimizer = RobustCRGrapeOptimizer(config)
    result = optimizer.run()
    result.save(RESULTS_DIR)


if __name__ == "__main__":
    run_robust_cr_grape()
