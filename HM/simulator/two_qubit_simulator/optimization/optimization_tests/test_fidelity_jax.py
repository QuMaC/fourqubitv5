"""Compare fidelity_jax to optimization/fidelity.py."""
from __future__ import annotations

import numpy as np
import jax
import jax.numpy as jnp

# Enables x64 via dq.set_precision("double") at import.
from HM.simulator.two_qubit_simulator.engine import two_q_pulse_sim_dynamiqs  # noqa: F401

from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    DEFAULT_COMP_INDICES,
    average_gate_fidelity,
    comp_block,
    embed_in_full,
    leakage_from_comp,
    process_fidelity,
    zx_target_unitary,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    average_gate_fidelity_jax,
    comp_block_jax,
    leakage_from_comp_jax,
    process_fidelity_jax,
)

ATOL = 1e-14


def _random_matrix(dim: int, rng: np.random.Generator) -> np.ndarray:
    """Complex 9×9, not unitary. The formula does not require U to be unitary."""
    re = rng.normal(size=(dim, dim))
    im = rng.normal(size=(dim, dim))
    return (re + 1j * im) / np.sqrt(2)


def test_identity_is_one() -> None:
    dim = 9
    I = np.eye(dim, dtype=complex)
    Ut = embed_in_full(np.eye(4, dtype=complex), dim=dim)
    F = process_fidelity_jax(I, Ut)
    assert F.shape == ()
    np.testing.assert_allclose(np.asarray(F), 1.0, atol=ATOL, rtol=0)
    print("identity F", float(F))


def test_perfect_zx_is_one() -> None:
    dim = 9
    U_t_comp = zx_target_unitary("zx_m90")
    U = embed_in_full(U_t_comp, dim=dim)
    F = process_fidelity_jax(U, U)
    np.testing.assert_allclose(np.asarray(F), 1.0, atol=ATOL, rtol=0)
    print("perfect zx_m90 F", float(F))


def test_matches_numpy_random() -> None:
    rng = np.random.default_rng(0)
    dim = 9
    Ut = embed_in_full(zx_target_unitary("zx_m90"), dim=dim)
    U = _random_matrix(dim, rng)

    F_np = process_fidelity(U, Ut)
    F_jx = process_fidelity_jax(U, Ut)
    np.testing.assert_allclose(np.asarray(F_jx), F_np, atol=ATOL, rtol=ATOL)

    np.testing.assert_allclose(
        np.asarray(comp_block_jax(U)),
        comp_block(U),
        atol=ATOL,
        rtol=ATOL,
    )
    np.testing.assert_allclose(
        np.asarray(average_gate_fidelity_jax(U, zx_target_unitary("zx_m90"))),
        average_gate_fidelity(U, zx_target_unitary("zx_m90")),
        atol=ATOL,
        rtol=ATOL,
    )
    np.testing.assert_allclose(
        np.asarray(leakage_from_comp_jax(U)),
        leakage_from_comp(U),
        atol=ATOL,
        rtol=ATOL,
    )
    print("random U  F_np", F_np, "F_jx", float(F_jx))


def test_transpose_is_not_the_same() -> None:
    rng = np.random.default_rng(1)
    U = _random_matrix(9, rng)
    # Ut = embed_in_full(zx_target_unitary("zx_90"), dim=9)
    Ut = _random_matrix(9, rng)
    F = float(process_fidelity_jax(U, Ut))
    FT = float(process_fidelity_jax(U.T, Ut))
    assert abs(F - FT) > 1e-6
    print("F(U)", F, "F(U.T)", FT)


def test_matches_numpy_parity_seed() -> None:
    """One real propagator. Layout is whatever run_propagator already uses."""
    from HM.simulator.two_qubit_simulator.optimization.optimization_tests.engine_parity_seed import (
        FLAT_LEN_NS,
        build_exp,
    )

    exp = build_exp("dynamiqs", n_sub=14)
    x_pi = exp.build_x_pi()
    timeline = exp._build_timeline(FLAT_LEN_NS, x_pi=x_pi)
    U = np.asarray(exp._propagator_from_timeline(timeline))
    Ut = embed_in_full(zx_target_unitary("zx_m90"), dim=U.shape[0])

    F_np = process_fidelity(U, Ut)
    F_jx = process_fidelity_jax(U, Ut)
    np.testing.assert_allclose(np.asarray(F_jx), F_np, atol=ATOL, rtol=ATOL)
    print("parity seed F_np", F_np, "F_jx", float(F_jx))


def test_process_fidelity_under_jit() -> None:
    Ut = jnp.asarray(embed_in_full(zx_target_unitary("zx_m90"), dim=9))

    @jax.jit
    def F_of(U):
        return process_fidelity_jax(U, Ut)

    rng = np.random.default_rng(2)
    U0 = jnp.asarray(_random_matrix(9, rng))
    a = F_of(U0)
    b = F_of(U0 * 1.01)
    assert a.shape == ()
    assert b.shape == ()
    assert not np.allclose(np.asarray(a), np.asarray(b))
    print("jit F", float(a), a.dtype)


if __name__ == "__main__":
    test_identity_is_one()
    test_perfect_zx_is_one()
    test_matches_numpy_random()
    test_transpose_is_not_the_same()
    test_matches_numpy_parity_seed()
    test_process_fidelity_under_jit()
    print("PHASE 3 OK")