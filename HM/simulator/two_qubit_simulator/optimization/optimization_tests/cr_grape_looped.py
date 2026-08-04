"""Looped echoed CR GRAPE: repeated runs from the same seed."""

from __future__ import annotations

import os

from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    CRGrapeConfig,
    run_looped_grape,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "looped")
os.makedirs(RESULTS_DIR, exist_ok=True)

CR_PULSE_PARAMS = {"amp_mhz": 30.0, "t_rise_ns": 16, "phase_rad": 0}
FLAT_LEN_NS = 84.0
N_FLAT_KNOBS = 46
N_LINK_SAMPLES = 8
TARGET_GATE = None
AMP_BOUND_MHZ = 48.0
LEAKAGE_WEIGHT = 0.0
MAXITER = 80
N_CYCLES = 1
OPTIMIZE = True
SAVE_INDIVIDUAL_CYCLES = True
CHECKPOINT_AFTER_EACH_CYCLE = True


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
        n_link_samples=N_LINK_SAMPLES,
        target_gate=TARGET_GATE,
        amp_bound_mhz=AMP_BOUND_MHZ,
        leakage_weight=LEAKAGE_WEIGHT,
        maxiter=MAXITER,
        optimize=OPTIMIZE,
        results_dir=RESULTS_DIR,
    )

    run_looped_grape(
        n_cycles=N_CYCLES,
        grape_config=config,
        exp=exp,
        save_individual_cycles=SAVE_INDIVIDUAL_CYCLES,
        checkpoint_after_each_cycle=CHECKPOINT_AFTER_EACH_CYCLE,
        results_dir=RESULTS_DIR,
        save=True,
    )


if __name__ == "__main__":
    main()
