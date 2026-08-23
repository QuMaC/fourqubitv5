"""Phase 4: grape_cost FD vs AD + evolve_comp parity."""
from __future__ import annotations

import numpy as np
import jax
import jax.numpy as jnp

from HM.simulator.two_qubit_simulator.engine import two_q_pulse_sim_dynamiqs  # noqa: F401
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    _templates_1ns,
    assemble_cr_half_jax,
    echoed_timeline_jax,
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    DEFAULT_CR_PULSE_PARAMS,
    _knobs_to_x,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    embed_in_full,
    process_fidelity,
    zx_target_unitary,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    u_comp_from_psi_jax,
)
from HM.simulator.two_qubit_simulator.optimization.grape_cost_jax import (
    GrapeStatics,
    grape_cost,
)

# Use a length that matches a real GRAPE config and divides knobs cleanly.
FLAT_LEN_NS = 184.0
N_KNOBS = 46
T_RISE = 16
N_LINK = 8
ATOL_U = 1e-7
ATOL_F = 1e-6
ATOL_GRAD_REL = 5e-4   # ODE + FD eps; tighten if your machine is clean


def _build_exp() -> CR_len_sweep:
    return CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        engine="dynamiqs",
        n_sub=14,
        cr_pulse_params={
            **DEFAULT_CR_PULSE_PARAMS,
            "amp_mhz": -32.0,
            "phase_rad": 0.0,
            "t_rise_ns": T_RISE,
        },
    )


def _seed_knobs() -> np.ndarray:
    """Constant complex amp (one value repeated) — like a flat seed."""
    return np.full(N_KNOBS, 21.0 + 0.0j, dtype=complex)


def _make_statics(exp, sim, evolution: str) -> GrapeStatics:
    rise, fall = _templates_1ns(T_RISE)
    gate = "zx_m90"
    U_comp = zx_target_unitary(gate)
    return GrapeStatics(
        rise=rise,
        fall=fall,
        n_flat=int(round(FLAT_LEN_NS)),
        n_link_samples=N_LINK,
        x_pi=jnp.asarray(exp.build_x_pi()),
        U_target_full=jnp.asarray(embed_in_full(U_comp, dim=sim.dim)),
        U_target_comp=jnp.asarray(U_comp),
        comp_indices=tuple(sim.comp_idx),
        channel_names=("q1_drive", "q2_drive", "cr_drive"),
        evolution=evolution,
        leakage_weight=0.0,
    )


def test_evolve_comp_matches_propagator_columns() -> None:
    exp = _build_exp()
    sim = exp.simulator
    rise, fall = _templates_1ns(T_RISE)
    knobs = _seed_knobs()
    cr_plus, _ = assemble_cr_half_jax(
        knobs, rise=rise, fall=fall, n_flat=int(FLAT_LEN_NS), n_link_samples=N_LINK
    )
    timeline = echoed_timeline_jax(
        cr_plus, exp.build_x_pi(), channel_names=("q1_drive", "q2_drive", "cr_drive")
    )
    # NumPy dict for engine validate (values can be jnp; asarray inside H build)
    tl = {k: np.asarray(v) for k, v in timeline.items()}

    U = sim.run_propagator(tl, return_numpy=True)
    psi = np.asarray(sim.evolve_comp(tl))
    assert psi.shape == (4, sim.dim, 1)
    for j, idx in enumerate(sim.comp_idx):
        np.testing.assert_allclose(psi[j, :, 0], U[:, idx], atol=ATOL_U, rtol=ATOL_U)
        print("ket", j, "idx", idx, "max|d|", np.max(np.abs(psi[j, :, 0] - U[:, idx])))
    # layout check
    U_comp_U = U[np.ix_(sim.comp_idx, sim.comp_idx)]
    U_comp_psi = np.asarray(u_comp_from_psi_jax(psi, tuple(sim.comp_idx)))
    np.testing.assert_allclose(U_comp_psi, U_comp_U, atol=ATOL_U, rtol=ATOL_U)
    print("evolve_comp vs U columns ok")


def test_cost_comp_matches_full_and_numpy() -> None:
    exp = _build_exp()
    sim = exp.simulator
    knobs = _seed_knobs()
    x = jnp.asarray(_knobs_to_x(knobs))

    st_comp = _make_statics(exp, sim, "comp")
    st_full = _make_statics(exp, sim, "full")

    c_comp = float(grape_cost(x, sim, st_comp))
    c_full = float(grape_cost(x, sim, st_full))
    print("cost comp", c_comp, "cost full", c_full)
    np.testing.assert_allclose(c_comp, c_full, atol=ATOL_F, rtol=ATOL_F)

    # NumPy reference: build timeline NumPy path + process_fidelity
    from HM.simulator.two_qubit_simulator.engine.pulses import (
        assemble_cr_half_from_flat_knobs,
    )
    cr_np, _ = assemble_cr_half_from_flat_knobs(
        knobs, flat_len_ns=FLAT_LEN_NS, t_rise_ns=T_RISE, dt_ns=1.0, n_link_samples=N_LINK
    )
    tl_np = exp._build_timeline_from_cr_half(cr_np, x_pi=exp.build_x_pi())
    U_np = exp._propagator_from_timeline(tl_np)
    Ut = embed_in_full(zx_target_unitary("zx_m90"), dim=U_np.shape[0])
    F_np = process_fidelity(U_np, Ut)
    c_np = -F_np
    print("cost numpy", c_np, "F_np", F_np)
    np.testing.assert_allclose(c_comp, c_np, atol=1e-5, rtol=1e-5)


def test_fd_vs_ad() -> None:
    exp = _build_exp()
    sim = exp.simulator
    knobs = _seed_knobs()
    x0 = jnp.asarray(_knobs_to_x(knobs))
    statics = _make_statics(exp, sim, "comp")

    def cost_only(x):
        return grape_cost(x, sim, statics)

    # First without jit — easier to debug
    c, g = jax.value_and_grad(cost_only)(x0)
    print("AD cost", float(c), "||g||", float(jnp.linalg.norm(g)))

    eps = 1e-6
    n = int(x0.shape[0])
    indices = [0, 1, min(17, n - 1)]
    for i in indices:
        e = jnp.zeros_like(x0).at[i].set(eps)
        fd = (cost_only(x0 + e) - cost_only(x0 - e)) / (2 * eps)
        gi = float(g[i])
        fdi = float(fd)
        rel = abs(gi - fdi) / max(1e-8, abs(fdi))
        print(f"idx {i:3d}  AD={gi:+.6e}  FD={fdi:+.6e}  |d|={abs(gi-fdi):.3e}  rel={rel:.3e}")
        assert rel < ATOL_GRAD_REL or abs(gi - fdi) < 1e-5

    # Optional jit smoke
    cost_vg = jax.jit(jax.value_and_grad(cost_only))
    c2, g2 = cost_vg(x0)
    c3, g3 = cost_vg(x0 * 1.0)  # second call uses cache
    np.testing.assert_allclose(float(c2), float(c), atol=1e-10)
    print("jit value_and_grad ok", float(c2), g2.shape)

if __name__ == "__main__":
    test_evolve_comp_matches_propagator_columns()
    test_cost_comp_matches_full_and_numpy()
    test_fd_vs_ad()
    print("PHASE 4 OK")