"""Idle check of the dressed frame on both Phase 3 chips.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.spectator_idle_zz
"""

from __future__ import annotations

import itertools
import json

import numpy as np

from HM.simulator.n_qubit_simulator.analysis.dressed_frame import (
    dressed_amplitudes,
    dressed_states,
    single_excitation_MHz,
    static_zz_MHz,
)
from HM.simulator.n_qubit_simulator.base_classes import device_base
from HM.simulator.n_qubit_simulator.engine.timelines import Timeline
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


IDLE_NS = 412
CHIPS = (
    (CONTROL_SIDE_CHIP, ("c1_t4", "c1_t6")),
    (TARGET_SIDE_CHIP, ("c3_t2",)),
)
# Pair ZZ is fitted to the paper. Chip ZZ can move when another qubit sits
# nearby. Q2 and Q6 are 2.2 MHz apart, so c1_t6 is allowed a wider bar.
CHIP_ZZ_REL_TOL = 0.05
CHIP_ZZ_REL_TOL_BY_EDGE = {"c1_t6": 0.15}


def check_chip(
    qubit_ids: tuple[int, ...],
    spectator_edges: tuple[str, ...],
    n_active: int,
    expected_kHz: dict[str, float],
) -> None:
    sim = build_chip(qubit_ids, n_active).simulator
    reference = ground_reference_MHz(sim)
    basis = configure(sim, (ACTIVE_EDGE,) + spectator_edges, reference)

    print("chip", qubit_ids, "dims", sim.dims, "dimension", sim.dim)
    dressed = single_excitation_MHz(sim, basis)
    residual = max(abs(dressed[q] - reference[q]) for q in reference)
    for qubit in sim.qubits:
        print(
            f"  Q{qubit.qubit_id} bare - calibrated "
            f"{1e3 * (qubit.frame_MHz - qubit.f_qubit_MHz):8.2f} kHz"
        )
    print("  compensation residual MHz", residual)
    print("  smallest dressed-bare overlap", basis.min_overlap)
    assert residual < 1e-9

    labels = list(itertools.product((0, 1), repeat=len(sim.dims)))
    idle = Timeline(
        sim.channel_names,
        n_samples=IDLE_NS,
        dt_ns=sim.dt_sample_ns,
    ).finalize()
    duration_us = IDLE_NS * sim.dt_sample_us
    final = sim.run_shot_batch(idle, dressed_states(sim, basis, labels))
    amplitudes = dressed_amplitudes(sim, basis, final, duration_us, reference)

    reference_vector = np.array([reference[q.qubit_id] for q in sim.qubits])
    worst_leave = 0.0
    worst_phase = 0.0
    for row, label in enumerate(labels):
        index = sim.basis_index(label)
        detuning_MHz = basis.energies_MHz[index] - reference_vector @ np.array(label)
        predicted = -2.0 * np.pi * detuning_MHz * duration_us
        amplitude = amplitudes[row, index]
        worst_leave = max(worst_leave, 1.0 - abs(amplitude) ** 2)
        worst_phase = max(
            worst_phase,
            abs(float(np.angle(amplitude * np.exp(-1j * predicted)))),
        )
    print("  worst population leaving its dressed state", worst_leave)
    print("  worst phase error rad", worst_phase)
    assert worst_leave < 1e-8
    assert worst_phase < 1e-6

    for edge in sim.coupling_edges:
        if not edge.enabled:
            continue
        zz_kHz = 1e3 * static_zz_MHz(sim, basis, edge.qubit_i, edge.qubit_j)
        expected = expected_kHz[edge.name]
        rel_tol = CHIP_ZZ_REL_TOL_BY_EDGE.get(edge.name, CHIP_ZZ_REL_TOL)
        print(
            f"  {edge.name}  chip ZZ {zz_kHz:7.2f} kHz  "
            f"expected {expected:7.2f} kHz  J {edge.J_MHz:.4f} MHz"
        )
        assert abs(zz_kHz - expected) < rel_tol * expected

    if 3 in qubit_ids:
        shift_kHz = 1e3 * static_zz_MHz(sim, basis, 3, 2)
        with np.load(C1T2_NPZ_PATH, allow_pickle=False) as data:
            span_kHz = 1e3 * float(data["zz_span_mhz"])
        print(
            f"  Q2 moves {shift_kHz:.1f} kHz when Q3 flips. "
            f"The pulse was optimized for a {span_kHz:.1f} kHz span."
        )


def main() -> None:
    n_active = active_levels()
    with device_base._PAPER_CROSS_KERR.open(encoding="utf-8") as handle:
        expected_kHz = dict(json.load(handle)["nearest_neighbour_khz"])
    lab = device_base._load_json("coupling_vals.json")
    expected_kHz[ACTIVE_EDGE] = 1e3 * float(lab[ACTIVE_EDGE]["total_det_mhz"])

    for qubit_ids, spectator_edges in CHIPS:
        check_chip(qubit_ids, spectator_edges, n_active, expected_kHz)
    print("SPECTATOR IDLE OK")


if __name__ == "__main__":
    main()
