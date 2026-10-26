"""Warm n_sub=2 robust GRAPE at 200 kHz, same seed as the Windows 200 kHz run.

Seed is Windows 150 kHz ``flat_knobs_opt`` (identical to Windows 200
``flat_knobs_seed``). Same maxiter=80 so the Linux output can be compared
to the Windows 200 pulse that hit the iteration limit.
"""

from __future__ import annotations

import json
import os

import numpy as np

from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    FIDELITY_METRICS,
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
)

RESULTS_NAME = "robust_zz_sweep_nsub2_warm_windows200"
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", RESULTS_NAME)
OUT_DIR = os.path.join(RESULTS_DIR, "warm", "zz_200_kHz")
os.makedirs(OUT_DIR, exist_ok=True)

SEED_NPZ = (
    "/home/hm/IITB/TIFR/Software/robust_external/windows_lab_desktop/"
    "robust_grape_zz_sweep_archive/robust_zz_sweep/warm/zz_150_kHz/"
    "cr_grape_robust_zz0p15MHz_mms_l0p3_20260806_201930.npz"
)
SEED_NPZ_KEY = "flat_knobs_opt"  # Windows 150 opt == Windows 200 seed

CR_PULSE_PARAMS = {"amp_mhz": 21.0, "t_rise_ns": 16, "phase_rad": 0.0}
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 61
N_LINK_SAMPLES = 8
ZZ_SHIFT_MHZ = 0.20
WEIGHTS = (0.5, 0.5)
FIDELITY_METRIC = "mean_minus_spread"
SPREAD_PENALTY_LAMBDA = 0.3
TARGET_GATE = "zx_m90"
AMP_BOUND_MHZ = 48.0
MAXITER = 80
N_SUB = 2
QUBIT_PAIR = [1, 2]
N_LEVELS = 3


def _load_knobs(path: str, key: str) -> np.ndarray:
    with np.load(path, allow_pickle=False) as d:
        if key not in d.files:
            raise KeyError(f"{path} has no {key!r}. Available: {sorted(d.files)}")
        knobs = np.asarray(d[key]).reshape(-1)
    if knobs.size != N_FLAT_KNOBS:
        raise ValueError(f"{key} length {knobs.size} != N_FLAT_KNOBS={N_FLAT_KNOBS}")
    if not np.iscomplexobj(knobs):
        knobs = knobs.astype(complex)
    return knobs


def run() -> None:
    seed_knobs = _load_knobs(SEED_NPZ, SEED_NPZ_KEY)
    print("Fidelity metrics available:")
    for key, desc in FIDELITY_METRICS.items():
        marker = " <-- selected" if key == FIDELITY_METRIC else ""
        print(f"  {key:18s}  {desc}{marker}")
    print(
        f"\nWarm n_sub={N_SUB} GRAPE  |  ZZ={ZZ_SHIFT_MHZ*1000:.0f} kHz  |  "
        f"seed=Windows 150 {SEED_NPZ_KEY} (same x0 as Windows 200)"
    )
    print(f"  {SEED_NPZ}")
    print(
        f"  knobs={N_FLAT_KNOBS}  max|u|={np.max(np.abs(seed_knobs)):.4f} MHz  "
        f"maxiter={MAXITER}  results={RESULTS_NAME}"
    )

    config = RobustCRGrapeConfig(
        flat_len_ns=FLAT_LEN_NS,
        n_flat_knobs=N_FLAT_KNOBS,
        seed_amp_mhz=CR_PULSE_PARAMS["amp_mhz"],
        seed_phase_rad=CR_PULSE_PARAMS["phase_rad"],
        t_rise_ns=CR_PULSE_PARAMS["t_rise_ns"],
        n_link_samples=N_LINK_SAMPLES,
        zz_shift_mhz=ZZ_SHIFT_MHZ,
        shifts_mhz=None,
        weights=WEIGHTS,
        fidelity_metric=FIDELITY_METRIC,
        spread_penalty_lambda=SPREAD_PENALTY_LAMBDA,
        target_gate=TARGET_GATE,
        amp_bound_mhz=AMP_BOUND_MHZ,
        maxiter=MAXITER,
        qubit_pair=list(QUBIT_PAIR),
        n_levels=N_LEVELS,
        n_sub=N_SUB,
        optimize=True,
        results_dir=OUT_DIR,
    )
    optimizer = RobustCRGrapeOptimizer(config, flat_knobs_seed=seed_knobs)
    result = optimizer.run()
    result.save(OUT_DIR)

    m = result.final_metrics
    summary = {
        "zz_spans_khz": [200],
        "seed_modes": "warm",
        "seed_source": f"SEED_NPZ:{SEED_NPZ}#{SEED_NPZ_KEY}",
        "compare_to": (
            "windows_lab_desktop/robust_grape_zz_sweep_archive/robust_zz_sweep/"
            "warm/zz_200_kHz/cr_grape_robust_zz0p2MHz_mms_l0p3_20260807_144507"
        ),
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
            "optimize": True,
            "target_gate": TARGET_GATE,
            "qubit_pair": list(QUBIT_PAIR),
            "n_levels": N_LEVELS,
            "n_sub": N_SUB,
            "results_name": RESULTS_NAME,
        },
        "runs": [
            {
                "zz_span_khz": 200,
                "zz_span_mhz": ZZ_SHIFT_MHZ,
                "shifts_mhz": list(result.shifts_mhz),
                "mode": "warm",
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
                "results_dir": OUT_DIR,
            }
        ],
    }
    summary_path = os.path.join(RESULTS_DIR, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nDone. Summary: {summary_path}")


if __name__ == "__main__":
    run()
