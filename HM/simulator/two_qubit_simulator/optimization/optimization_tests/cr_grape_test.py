"""Echoed CR GRAPE: flat-top knobs with rise/fall linked to first/last knob."""

from __future__ import annotations

import os

from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    CRGrapeConfig,
    CRGrapeOptimizer,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

CR_PULSE_PARAMS = {"amp_mhz": 32.0, "t_rise_ns": 16, "phase_rad": 0}
FLAT_LEN_NS = 84.0
N_FLAT_KNOBS = 46
TARGET_GATE = None  # inferred from seed pulse; or "zx_90" / "zx_m90"
AMP_BOUND_MHZ = 48.0
LEAKAGE_WEIGHT = 0.0
MAXITER = 80
OPTIMIZE = True  # set True for L-BFGS-B (slow)
LOG_EVERY_EVAL = False


def main() -> None:
    exp = CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        cr_pulse_params=CR_PULSE_PARAMS,
    )

    config = CRGrapeConfig(
        flat_len_ns=FLAT_LEN_NS,
        n_flat_knobs=N_FLAT_KNOBS,
        seed_amp_mhz=CR_PULSE_PARAMS["amp_mhz"],
        seed_phase_rad=CR_PULSE_PARAMS["phase_rad"],
        t_rise_ns=CR_PULSE_PARAMS["t_rise_ns"],
        target_gate=TARGET_GATE,
        amp_bound_mhz=AMP_BOUND_MHZ,
        leakage_weight=LEAKAGE_WEIGHT,
        maxiter=MAXITER,
        optimize=OPTIMIZE,
        log_every_eval=LOG_EVERY_EVAL,
        results_dir=RESULTS_DIR,
    )

    optimizer = CRGrapeOptimizer(config, exp=exp)
    result = optimizer.run()
    result.save(RESULTS_DIR)


if __name__ == "__main__":
    main()
