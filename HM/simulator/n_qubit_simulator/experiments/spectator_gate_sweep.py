"""Replay the c1t2 GRAPE gate with spectator couplings switched on.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.spectator_gate_sweep
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import numpy as np

from HM.simulator.n_qubit_simulator.analysis.dressed_frame import (
    dressed_amplitudes,
    dressed_states,
    single_excitation_MHz,
    static_zz_MHz,
)
from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    echoed_c1t2_timeline,
    embed_c1t2_timeline,
    load_optimized_cr_half,
)
from HM.simulator.n_qubit_simulator.experiments.spectator_setup import (
    ACTIVE_EDGE,
    C1T2_NPZ_PATH,
    CONTROL_SIDE_CHIP,
    TARGET_SIDE_CHIP,
    active_levels,
    build_chip,
    configure,
    ground_reference_MHz,
)
from HM.simulator.two_qubit_simulator.base_classes.device_base import (
    TwoQubitSimulatorBase,
)


COMPUTATIONAL = ((0, 0), (0, 1), (1, 0), (1, 1))
ACTIVE_CHANNELS = ("q1_drive", "q2_drive", "cr_c1_t2")
RESULTS_DIR = Path(__file__).resolve().parent / "results"

CONTROL_SIDE_CASES = (
    ("baseline", (), ((0, 0),)),
    ("+c1_t4", ("c1_t4",), ((0, 0), (1, 0))),
    ("+c1_t6", ("c1_t6",), ((0, 0), (0, 1))),
    ("+c1_t4+c1_t6", ("c1_t4", "c1_t6"), ((0, 0), (1, 0), (0, 1), (1, 1))),
)


def overlap_fidelity(A: np.ndarray, B: np.ndarray) -> float:
    """|Tr(A^dagger B)|^2 / 16 for two 4x4 computational blocks."""
    return float(abs(np.trace(A.conj().T @ B)) ** 2 / 16.0)


def gate_branch(sim, basis, reference, timeline, spectators) -> dict:
    """Computational block and losses with spectators started in ``spectators``."""

    labels = [active + tuple(spectators) for active in COMPUTATIONAL]
    indices = [sim.basis_index(label) for label in labels]
    n_samples = len(next(iter(timeline.values())))
    final = sim.run_shot_batch(timeline, dressed_states(sim, basis, labels))
    amplitudes = dressed_amplitudes(
        sim,
        basis,
        final,
        n_samples * sim.dt_sample_us,
        reference,
    )

    block = amplitudes[:, indices].T
    spectator_rows = basis.occupations[2:, :]
    in_branch = np.all(
        spectator_rows == np.array(spectators, dtype=int).reshape(-1, 1),
        axis=0,
    )
    branch_population = (np.abs(amplitudes) ** 2)[:, in_branch].sum(axis=1)
    computational_population = (np.abs(block) ** 2).sum(axis=0)
    return {
        "block": block,
        "spectator_excitation": float(np.mean(1.0 - branch_population)),
        "active_leakage": float(
            np.mean(branch_population - computational_population)
        ),
    }


def assert_spectator_channels_idle(timeline: dict) -> None:
    for name, envelope in timeline.items():
        if name in ACTIVE_CHANNELS:
            continue
        assert float(np.max(np.abs(np.asarray(envelope)))) == 0.0, name


def print_branch(chip: str, case: str, spectators, branch: dict, baseline) -> None:
    label = "".join(str(occupation) for occupation in spectators)
    print(
        f"{chip:12} {case:18} {label:4} "
        f"F_vs_baseline {overlap_fidelity(baseline, branch['block']):.6f}  "
        f"spectator excitation {branch['spectator_excitation']:.2e}  "
        f"active leakage {branch['active_leakage']:.2e}",
        flush=True,
    )


def run_control_side(pair_timeline: dict, n_active: int) -> dict:
    sim = build_chip(CONTROL_SIDE_CHIP, n_active).simulator
    timeline = embed_c1t2_timeline(pair_timeline, sim.channel_names)
    assert_spectator_channels_idle(timeline)
    reference = ground_reference_MHz(sim)

    results = {}
    for case, extra_edges, branches in CONTROL_SIDE_CASES:
        enabled = (ACTIVE_EDGE,) + extra_edges
        basis = configure(sim, enabled, reference)
        assert sorted(e.name for e in sim.coupling_edges if e.enabled) == sorted(
            enabled
        )
        for spectators in branches:
            branch = gate_branch(sim, basis, reference, timeline, spectators)
            results[(case, spectators)] = branch
            baseline = results[("baseline", (0, 0))]["block"]
            print_branch("Q1Q2Q4Q6", case, spectators, branch, baseline)
    return results


def run_target_side(pair_timeline: dict, n_active: int) -> tuple[dict, float]:
    sim = build_chip(TARGET_SIDE_CHIP, n_active).simulator
    timeline = embed_c1t2_timeline(pair_timeline, sim.channel_names)
    assert_spectator_channels_idle(timeline)
    reference = ground_reference_MHz(sim)
    edges = (ACTIVE_EDGE, "c3_t2")

    results = {}
    basis = configure(sim, (ACTIVE_EDGE,), reference)
    results[("baseline", (0,))] = gate_branch(sim, basis, reference, timeline, (0,))
    baseline = results[("baseline", (0,))]["block"]
    print_branch("Q1Q2Q3", "baseline", (0,), results[("baseline", (0,))], baseline)

    basis = configure(sim, edges, reference)
    zz_MHz = static_zz_MHz(sim, basis, 3, 2)
    for spectators in ((0,), (1,)):
        branch = gate_branch(sim, basis, reference, timeline, spectators)
        results[("ground-calibrated", spectators)] = branch
        print_branch("Q1Q2Q3", "ground-calibrated", spectators, branch, baseline)

    midpoint = dict(reference)
    midpoint[2] = reference[2] - 0.5 * zz_MHz
    basis = configure(sim, edges, midpoint)
    offset_kHz = 1e3 * (single_excitation_MHz(sim, basis)[2] - reference[2])
    print(f"midpoint: Q2 with Q3 in |0> sits {offset_kHz:.2f} kHz from Phase 2")
    for spectators in ((0,), (1,)):
        branch = gate_branch(sim, basis, reference, timeline, spectators)
        results[("midpoint", spectators)] = branch
        print_branch("Q1Q2Q3", "midpoint", spectators, branch, baseline)
    return results, zz_MHz


def two_qubit_frame_model(
    pair_timeline: dict,
    n_active: int,
    shifts_MHz,
) -> dict[float, np.ndarray]:
    """Computational blocks of the 2Q engine with the target frame moved."""

    reference = TwoQubitSimulatorBase(
        qubit_pair=[1, 2],
        engine="dynamiqs",
        n_levels=n_active,
        dt_sample_ns=1.0,
    ).simulator
    lab_frame = float(reference.qubits[1].frame_MHz)
    timeline = {
        name: np.asarray(pair_timeline[name])
        for name in ("q1_drive", "q2_drive", "cr_drive")
    }
    blocks = {}
    for shift in shifts_MHz:
        reference.set_target_frame(lab_frame + shift)
        states = np.asarray(reference.evolve_comp(timeline))
        blocks[shift] = states[:, reference.comp_idx, 0].T
    reference.set_target_frame(lab_frame)
    return blocks


def _jsonable_block(block: np.ndarray) -> list:
    return [[[float(z.real), float(z.imag)] for z in row] for row in block]


def main() -> None:
    n_active = active_levels()
    saved_half, _knobs = load_optimized_cr_half(C1T2_NPZ_PATH)
    pair_timeline = echoed_c1t2_timeline(saved_half)
    with np.load(C1T2_NPZ_PATH, allow_pickle=False) as data:
        design_span_MHz = float(data["zz_span_mhz"])
    print("active levels", n_active, "design span MHz", design_span_MHz)

    control = run_control_side(pair_timeline, n_active)
    target, zz_MHz = run_target_side(pair_timeline, n_active)

    baseline_difference = float(
        np.max(
            np.abs(
                control[("baseline", (0, 0))]["block"]
                - target[("baseline", (0,))]["block"]
            )
        )
    )
    print("baseline block difference between chips", baseline_difference)
    assert baseline_difference < 1e-6

    both = "+c1_t4+c1_t6"
    ground = control[(both, (0, 0))]["block"]
    control_branches = {
        "Q4 flipped": overlap_fidelity(ground, control[(both, (1, 0))]["block"]),
        "Q6 flipped": overlap_fidelity(ground, control[(both, (0, 1))]["block"]),
        "both flipped": overlap_fidelity(ground, control[(both, (1, 1))]["block"]),
    }
    print("control-side branch fidelity vs Q4 Q6 in 00:", control_branches)

    target_branches = {
        placement: overlap_fidelity(
            target[(placement, (0,))]["block"],
            target[(placement, (1,))]["block"],
        )
        for placement in ("ground-calibrated", "midpoint")
    }

    shifts = {
        "ground-calibrated": (0.0, zz_MHz),
        "midpoint": (-0.5 * zz_MHz, 0.5 * zz_MHz),
        "design": (-0.5 * design_span_MHz, 0.5 * design_span_MHz),
    }
    model = two_qubit_frame_model(
        pair_timeline,
        n_active,
        sorted({0.0, *shifts["ground-calibrated"], *shifts["midpoint"], *shifts["design"]}),
    )
    model_branches = {
        placement: overlap_fidelity(model[low], model[high])
        for placement, (low, high) in shifts.items()
    }
    model_vs_baseline = {
        placement: [overlap_fidelity(model[0.0], model[s]) for s in shifts[placement]]
        for placement in ("ground-calibrated", "midpoint")
    }

    print(f"Q3 shifts Q2 by {1e3 * zz_MHz:.2f} kHz")
    for placement in ("ground-calibrated", "midpoint"):
        print(
            f"{placement:18} branch fidelity: n-qubit {target_branches[placement]:.6f}  "
            f"2Q frame model {model_branches[placement]:.6f}"
        )
        full = [
            overlap_fidelity(
                target[("baseline", (0,))]["block"],
                target[(placement, s)]["block"],
            )
            for s in ((0,), (1,))
        ]
        print(
            f"{'':18} F_vs_baseline Q3=0, Q3=1: n-qubit "
            f"{full[0]:.6f}, {full[1]:.6f}  2Q frame model "
            f"{model_vs_baseline[placement][0]:.6f}, "
            f"{model_vs_baseline[placement][1]:.6f}"
        )
    print(
        f"design span ±{0.5e3 * design_span_MHz:.1f} kHz, 2Q frame model branch "
        f"fidelity {model_branches['design']:.6f}"
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"phase3_spectator_sweep_{stamp}.json"
    payload = {
        "archive": C1T2_NPZ_PATH,
        "active_levels": n_active,
        "q3_on_q2_zz_kHz": 1e3 * zz_MHz,
        "design_span_kHz": 1e3 * design_span_MHz,
        "control_side": {
            f"{case} {''.join(map(str, s))}": {
                "spectator_excitation": branch["spectator_excitation"],
                "active_leakage": branch["active_leakage"],
                "block": _jsonable_block(branch["block"]),
            }
            for (case, s), branch in control.items()
        },
        "target_side": {
            f"{case} {''.join(map(str, s))}": {
                "spectator_excitation": branch["spectator_excitation"],
                "active_leakage": branch["active_leakage"],
                "block": _jsonable_block(branch["block"]),
            }
            for (case, s), branch in target.items()
        },
        "control_side_branch_fidelity": control_branches,
        "target_side_branch_fidelity": target_branches,
        "two_qubit_frame_model_branch_fidelity": model_branches,
    }
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print("saved", out_path)
    print("PHASE 3 OK")


if __name__ == "__main__":
    main()
