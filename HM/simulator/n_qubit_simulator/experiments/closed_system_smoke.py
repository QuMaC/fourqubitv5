"""Phase 1 smoke test for the six-qutrit dynamiqs engine.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.closed_system_smoke
"""

from __future__ import annotations

import dynamiqs as dq
import jax
import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)
from HM.simulator.n_qubit_simulator.engine.constants import TWOPI
from HM.simulator.n_qubit_simulator.engine.timelines import Timeline


def main() -> None:
    base = NQubitSimulatorBase(n_levels=3, dt_sample_ns=1.0)
    sim = base.simulator

    print("backend", jax.default_backend())
    print("devices", jax.devices())
    print("dims", sim.dims)
    print("dimension", sim.dim)
    print("edges", len(sim.coupling_edges))
    print("channels", len(sim.channel_names))
    print(
        "synthetic edges",
        [
            edge.name
            for edge in sim.coupling_edges
            if not edge.is_calibrated
        ],
    )
    print(
        "CALIBRATION REVIEW: Q6 anharmonicity",
        sim.qubits[5].anharm_MHz,
        "MHz from",
        sim.qubits[5].anharmonicity_source,
    )

    expected_edges = (
        ("c1_t2", 1, 2),
        ("c1_t4", 1, 4),
        ("c1_t6", 1, 6),
        ("c3_t2", 3, 2),
        ("c3_t4", 3, 4),
        ("c3_t6", 3, 6),
        ("c5_t2", 5, 2),
        ("c5_t4", 5, 4),
        ("c5_t6", 5, 6),
    )
    actual_edges = tuple(
        (edge.name, edge.qubit_i, edge.qubit_j)
        for edge in sim.coupling_edges
    )
    expected_channels = (
        "q1_drive",
        "q2_drive",
        "q3_drive",
        "q4_drive",
        "q5_drive",
        "q6_drive",
        "cr_c1_t2",
        "cr_c1_t4",
        "cr_c1_t6",
        "cr_c3_t2",
        "cr_c3_t4",
        "cr_c3_t6",
        "cr_c5_t2",
        "cr_c5_t4",
        "cr_c5_t6",
    )
    assert actual_edges == expected_edges
    assert sim.channel_names == expected_channels
    assert sim.drive_lines["cr_c1_t2"].target_qubit_id == 1
    assert (
        sim.drive_lines["cr_c1_t2"].carrier_MHz
        == sim.qubits[1].f_qubit_MHz
    )

    idle_builder = Timeline(
        sim.channel_names,
        n_samples=20,
        dt_ns=sim.dt_sample_ns,
    )
    idle_timeline = idle_builder.finalize()

    probe_builder = Timeline(
        sim.channel_names,
        n_samples=20,
        dt_ns=sim.dt_sample_ns,
    )
    probe_builder.add(
        "q1_drive",
        0.0,
        jnp.full(20, 0.25 + 0.10j, dtype=jnp.complex128),
    )
    probe_builder.add(
        "cr_c1_t2",
        0.0,
        jnp.full(20, -0.40 + 0.30j, dtype=jnp.complex128),
    )
    probe_timeline = probe_builder.finalize()

    for label, timeline in (
        ("idle", idle_timeline),
        ("complex-drive", probe_timeline),
    ):
        H = sim.hamiltonian(timeline)
        for t_us in (0.0, 0.0030, 0.0035, 0.0070, 0.0075, 0.020):
            matrix = dq.to_jax(H(t_us))
            error = jnp.max(jnp.abs(matrix - matrix.conj().T))
            print(
                "timeline",
                label,
                "t_us",
                t_us,
                "Hermiticity error",
                float(error),
            )
            assert matrix.shape == (729, 729)
            assert float(error) < 1e-10

    probe_time_us = 0.0073
    probe_matrix = dq.to_jax(
        sim.hamiltonian(probe_timeline)(probe_time_us)
    )
    vacuum_index = sim.basis_index((0, 0, 0, 0, 0, 0))
    q1_index = sim.basis_index((1, 0, 0, 0, 0, 0))
    q2_index = sim.basis_index((0, 1, 0, 0, 0, 0))

    c1_t2 = next(
        edge for edge in sim.coupling_edges if edge.name == "c1_t2"
    )
    coupling_delta_MHz = (
        sim.qubits[0].frame_MHz - sim.qubits[1].frame_MHz
    )
    expected_q1_from_q2 = (
        TWOPI
        * c1_t2.J_MHz
        * jnp.exp(
            1j * TWOPI * coupling_delta_MHz * probe_time_us
        )
    )
    observed_q1_from_q2 = probe_matrix[q1_index, q2_index]
    print("Q2 to Q1 coupling element", observed_q1_from_q2)
    assert jnp.allclose(
        observed_q1_from_q2,
        expected_q1_from_q2,
        rtol=1e-10,
        atol=1e-10,
    )

    self_epsilon = 0.25 + 0.10j
    cr_epsilon = -0.40 + 0.30j
    cr_delta_MHz = (
        sim.drive_lines["cr_c1_t2"].carrier_MHz
        - sim.qubits[0].frame_MHz
    )
    expected_q1_from_vacuum = 0.5 * TWOPI * (
        self_epsilon
        + cr_epsilon
        * jnp.exp(-1j * TWOPI * cr_delta_MHz * probe_time_us)
    )
    observed_q1_from_vacuum = probe_matrix[q1_index, vacuum_index]
    print("vacuum to Q1 drive element", observed_q1_from_vacuum)
    assert jnp.allclose(
        observed_q1_from_vacuum,
        expected_q1_from_vacuum,
        rtol=1e-10,
        atol=1e-10,
    )

    initial_occupations = (1, 0, 0, 0, 0, 0)
    psi0 = dq.basis(sim.dims, initial_occupations)
    final_state = sim.run_shot(idle_timeline, psi0=psi0)
    norm = sim.measure_state_norm(final_state)
    vector = dq.to_jax(final_state).reshape(-1)

    populations = {}
    for qubit_position, qubit in enumerate(sim.qubits):
        occupations = tuple(
            1 if position == qubit_position else 0
            for position in range(6)
        )
        index = sim.basis_index(occupations)
        populations[f"Q{qubit.qubit_id}"] = float(
            jnp.abs(vector[index]) ** 2
        )

    print("final state shape", final_state.shape)
    print("final norm", norm)
    print("single-excitation populations", populations)
    print("single-excitation population sum", sum(populations.values()))

    assert sim.dims == (3,) * 6
    assert sim.dim == 729
    assert len(sim.coupling_edges) == 9
    assert len(sim.channel_names) == 15
    assert final_state.shape == (729, 1)
    assert abs(norm - 1.0) < 1e-8
    assert abs(sum(populations.values()) - 1.0) < 1e-8
    assert sim._sesolve_options.save_states is False

    print("PHASE 1 OK")


if __name__ == "__main__":
    main()