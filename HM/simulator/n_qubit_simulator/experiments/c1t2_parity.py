"""Replay one c1t2 GRAPE archive on the n-qubit engine.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.c1t2_parity
"""

from __future__ import annotations

import numpy as np
import dynamiqs as dq
from dynamiqs import method as dq_method
import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)
from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    echoed_c1t2_timeline,
    embed_c1t2_timeline,
    load_grape_sidecar,
    load_optimized_cr_half,
    rebuild_cr_half,
)
from HM.simulator.two_qubit_simulator.base_classes.device_base import (
    TwoQubitSimulatorBase,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    echoed_timeline_jax as echoed_timeline_2q,
)


# Keep this identical to c1t2_waveform_identity.C1T2_NPZ_PATH.
C1T2_NPZ_PATH = (
    "/home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5/HM/simulator/"
    "two_qubit_simulator/optimization/optimization_tests/results/"
    "robust_lp350mhz/"
    "cr_grape_robust_zz0p15MHz_mms_l0p3_20261003_191251.npz"
)

_AMPLITUDE_ATOL = 1e-8


def _numpy_basis(dims: tuple[int, ...], occupations: tuple[int, ...]) -> np.ndarray:
    if len(dims) != len(occupations):
        raise ValueError("occupation count does not match dims")
    dim = 1
    for local_dim in dims:
        dim *= int(local_dim)
    index = 0
    for occupation, local_dim in zip(occupations, dims):
        index = index * int(local_dim) + int(occupation)
    vector = np.zeros((dim, 1), dtype=np.complex128)
    vector[index, 0] = 1.0
    return vector


def _spectator_ground_slice(sim, state) -> np.ndarray:
    vector = np.asarray(dq.to_jax(state)).reshape(-1)
    n0, n1 = sim.dims[0], sim.dims[1]
    tail = 1
    for local_dim in sim.dims[2:]:
        tail *= int(local_dim)
    sliced = np.empty(n0 * n1, dtype=np.complex128)
    for control in range(n0):
        for target in range(n1):
            flat = control * n1 + target
            sliced[flat] = vector[flat * tail]
    return sliced


def main() -> None:
    if not C1T2_NPZ_PATH:
        raise SystemExit(
            "Set C1T2_NPZ_PATH in c1t2_parity.py to the same local GRAPE .npz "
            "used for waveform identity."
        )

    sidecar = load_grape_sidecar(C1T2_NPZ_PATH)
    n_levels = sidecar["n_levels"]
    saved_half, knobs = load_optimized_cr_half(C1T2_NPZ_PATH)
    rebuilt = rebuild_cr_half(knobs, sidecar)
    half_error = float(jnp.max(jnp.abs(saved_half - rebuilt)))
    print("rebuilt half max abs error", half_error)
    assert half_error < 1e-12

    pair_timeline = echoed_c1t2_timeline(saved_half)
    n_half = int(saved_half.shape[0])
    n_echo = int((pair_timeline["q1_drive"].shape[0] - 2 * n_half) // 2)
    x_pi = pair_timeline["q1_drive"][n_half : n_half + n_echo]
    trusted = echoed_timeline_2q(saved_half, x_pi)
    for name in ("q1_drive", "q2_drive", "cr_drive"):
        error = float(jnp.max(jnp.abs(pair_timeline[name] - trusted[name])))
        assert error < 1e-12

    reference_base = TwoQubitSimulatorBase(
        qubit_pair=[1, 2],
        engine="dynamiqs",
        n_levels=n_levels,
        dt_sample_ns=1.0,
    )
    reference = reference_base.simulator

    pair_base = NQubitSimulatorBase(
        qubit_ids=(1, 2),
        n_levels=n_levels,
        dt_sample_ns=1.0,
    )
    overrides = None if n_levels == 3 else {1: n_levels, 2: n_levels}
    spectator_base = NQubitSimulatorBase(
        qubit_ids=(1, 2, 4, 6),
        n_levels=3,
        levels_by_qubit=overrides,
        dt_sample_ns=1.0,
    )
    for edge in spectator_base.coupling_edges:
        edge.enabled = {edge.qubit_i, edge.qubit_j} == {1, 2}

    pair = pair_base.simulator
    spectators = spectator_base.simulator
    # 412 ns with a discontinuity every nanosecond. The engine default 1e-10
    # leaves the dimension-144 slice about 1e-7 away from the 2Q state.
    parity_method = dq_method.Tsit5(atol=1e-12, rtol=1e-12, max_steps=1_000_000)
    reference._integrator_method = parity_method
    pair._integrator_method = parity_method
    spectators._integrator_method = parity_method
    print("integrator tol", 1e-12)
    pair_embedded = embed_c1t2_timeline(pair_timeline, pair.channel_names)
    spectator_embedded = embed_c1t2_timeline(
        pair_timeline,
        spectators.channel_names,
    )

    assert pair.dims == (n_levels, n_levels)
    assert pair.dim == n_levels * n_levels
    assert spectators.dims == (n_levels, n_levels, 3, 3)
    assert spectators.dim == n_levels * n_levels * 9
    assert pair._sesolve_options.save_states is False
    assert spectators._sesolve_options.save_states is False

    enabled = sorted(
        edge.name for edge in spectator_base.coupling_edges if edge.enabled
    )
    disabled = sorted(
        edge.name for edge in spectator_base.coupling_edges if not edge.enabled
    )
    print("enabled edges", enabled)
    print("disabled edges", disabled)
    assert enabled == ["c1_t2"]
    assert disabled == ["c1_t4", "c1_t6"]

    c1_t2 = next(
        edge for edge in pair_base.coupling_edges if edge.name == "c1_t2"
    )
    assert abs(c1_t2.J_MHz - float(reference.J_MHz)) < 1e-9
    assert abs(pair.qubits[0].anharm_MHz - reference.qubits[0].anharm_MHz) < 1e-9
    assert abs(pair.qubits[1].anharm_MHz - reference.qubits[1].anharm_MHz) < 1e-9

    delta_nq = pair.qubits[0].frame_MHz - pair.qubits[1].frame_MHz
    delta_2q = float(np.asarray(reference.delta_qq_MHz))
    print("coupling detuning n-qubit", delta_nq, "2Q", delta_2q)
    assert abs(delta_nq - delta_2q) < 1e-6

    cr_delta_nq = (
        pair.drive_lines["cr_c1_t2"].carrier_MHz - pair.qubits[0].frame_MHz
    )
    cr_delta_2q = (
        reference.drive_lines["cr_drive"].carrier_MHz
        - float(reference.qubits[0].frame_MHz)
    )
    print("CR detuning n-qubit", cr_delta_nq, "2Q", cr_delta_2q)
    assert abs(cr_delta_nq - cr_delta_2q) < 1e-6

    reference_timeline = {
        name: np.asarray(pair_timeline[name])
        for name in ("q1_drive", "q2_drive", "cr_drive")
    }
    worst = 0.0
    worst_spectator = 0.0
    for control in range(n_levels):
        for target in range(n_levels):
            psi_ref = _numpy_basis((n_levels, n_levels), (control, target))
            out_ref = reference.run_shot(
                reference_timeline,
                psi0=psi_ref,
            ).full().reshape(-1)

            out_pair = np.asarray(
                dq.to_jax(
                    pair.run_shot(
                        pair_embedded,
                        psi0=dq.basis(pair.dims, (control, target)),
                    )
                )
            ).reshape(-1)
            out_spec = spectators.run_shot(
                spectator_embedded,
                psi0=dq.basis(spectators.dims, (control, target, 0, 0)),
            )
            sliced = _spectator_ground_slice(spectators, out_spec)
            spectator_population = 1.0 - float(np.sum(np.abs(sliced) ** 2))

            pair_error = float(np.max(np.abs(out_pair - out_ref)))
            slice_error = float(np.max(np.abs(sliced - out_ref)))
            worst = max(worst, pair_error, slice_error)
            worst_spectator = max(worst_spectator, spectator_population)
            print(
                "input",
                (control, target),
                "pair error",
                pair_error,
                "spectator-slice error",
                slice_error,
                "spectator population",
                spectator_population,
                flush=True,
            )
            assert pair_error < _AMPLITUDE_ATOL
            assert slice_error < _AMPLITUDE_ATOL
            assert spectator_population < _AMPLITUDE_ATOL

    print("worst amplitude error", worst)
    print("worst spectator population", worst_spectator)
    print("PHASE 2 OK")


if __name__ == "__main__":
    main()
