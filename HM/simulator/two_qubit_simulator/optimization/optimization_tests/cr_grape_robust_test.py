"""Robust (multi-detuning) echoed CR GRAPE: one pulse optimized across ZZ shifts.

Defaults to dynamiqs + JAX AD (batched frames). Set ``USE_JAX_GRAD = False``
to fall back to the QuTiP / finite-difference path (one experiment per shift).

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
USE_JAX_GRAD = True
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", f"robust_dynamiqs_{USE_JAX_GRAD}")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Knobs — edit these
# ---------------------------------------------------------------------------

# Seed pulse (same convention as cr_grape_robust_zz_sweep.py).
CR_PULSE_PARAMS = {"amp_mhz": 21.0, "t_rise_ns": 16, "phase_rad": 0.0}
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 61  # 46
N_LINK_SAMPLES = 8

# Multi-detuning setup.
# - If SHIFTS_MHZ is None: cases are +/- ZZ_SHIFT_MHZ/2 (two points).
# - Else: any list, e.g. [-0.15, 0.0, 0.15] or [-0.15, 0.05].
ZZ_SHIFT_MHZ = 0.3
SHIFTS_MHZ = None  # e.g. [-0.15, 0.0, 0.15]
# Per-shift weights (length must match N). None → equal 1/N.
WEIGHTS = None

# Combined fidelity metric — pick one of FIDELITY_METRICS:
#   weighted_mean      -> sum_i w_i F_i
#   geometric_mean     -> exp(sum_i w_i log F_i)
#   mean_minus_spread  -> weighted mean - SPREAD_PENALTY_LAMBDA * (max F - min F)

FIDELITY_METRIC: FidelityMetric = "mean_minus_spread"
SPREAD_PENALTY_LAMBDA = 0.3

TARGET_GATE = None  # inferred from seed; or "zx_90" / "zx_m90"
AMP_BOUND_MHZ = 48.0
MAXITER = 180
OPTIMIZE = True  # set True for a real L-BFGS / Adam run


# "lbfgs" (default) or "adam"; adam requires USE_JAX_GRAD=True.
OPTIMIZER = "lbfgs"
ADAM_LR = 0.02
ADAM_STEPS = 200
EVOLUTION = "comp"  # robust JAX path locks "comp"
N_SUB = 16  # passed into CR_len_sweep; unused by dynamiqs Path A
QUBIT_PAIR = [1, 2]
N_LEVELS = 3
SHOW_PROGRESS = True


def run_robust_cr_grape() -> None:
    """Build config from the knobs above, optimize, and save results."""
    print("Fidelity metrics available:")
    for key, desc in FIDELITY_METRICS.items():
        marker = " <-- selected" if key == FIDELITY_METRIC else ""
        print(f"  {key:18s}  {desc}{marker}")
    print(
        f"Backend: use_jax_grad={USE_JAX_GRAD}  optimizer={OPTIMIZER!r}  "
        f"n_sub={N_SUB}  evolution={EVOLUTION!r}"
    )

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
        qubit_pair=list(QUBIT_PAIR),
        n_levels=N_LEVELS,
        n_sub=N_SUB,
        optimize=OPTIMIZE,
        show_progress=SHOW_PROGRESS,
        results_dir=RESULTS_DIR,
        use_jax_grad=USE_JAX_GRAD,
        optimizer=OPTIMIZER,
        adam_lr=ADAM_LR,
        adam_steps=ADAM_STEPS,
        evolution=EVOLUTION,
    )

    optimizer = RobustCRGrapeOptimizer(config)
    result = optimizer.run()
    result.save(RESULTS_DIR)


if __name__ == "__main__":
    run_robust_cr_grape()
