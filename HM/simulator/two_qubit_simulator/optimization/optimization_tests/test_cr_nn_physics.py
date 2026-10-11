"""Slow physics and gradient smoke tests for the CR neural pulse path."""

from __future__ import annotations

from dataclasses import replace

import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np

from HM.simulator.two_qubit_simulator.engine.pulses import (
    assemble_cr_half_from_flat_knobs,
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_nn.config import CRNNConfig
from HM.simulator.two_qubit_simulator.optimization.cr_nn.cost import (
    batch_loss,
    build_physics,
)
from HM.simulator.two_qubit_simulator.optimization.cr_nn.model import CRPulseMLP
from HM.simulator.two_qubit_simulator.optimization.cr_nn.sampling import (
    sample_batch,
)


def test_parametric_engine_matches_installed_state() -> None:
    exp = CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=4,
        engine="dynamiqs",
        envelope="bessel4_350mhz",
        cr_pulse_params={
            "amp_mhz": 21.0,
            "phase_rad": 0.0,
            "t_rise_ns": 16,
        },
    )
    sim = exp.simulator
    knobs = np.full(20, 21.0 + 0.0j)
    cr_half, _ = assemble_cr_half_from_flat_knobs(
        knobs,
        flat_len_ns=20,
        t_rise_ns=16,
        dt_ns=1,
        n_link_samples=8,
    )
    timeline = exp._build_timeline_from_cr_half(cr_half, x_pi=exp.build_x_pi())
    frame0 = float(np.asarray(sim.qubits[1].frame_MHz).reshape(()))
    frames = frame0 + jnp.asarray([-0.12, 0.12], dtype=jnp.float64)
    coupling = 3.0

    dynamic = sim.evolve_comp(
        timeline,
        target_frame_MHz=frames,
        J_MHz=jnp.asarray(coupling),
    )
    original_j = sim.J_MHz
    sim.J_MHz = coupling
    sim.set_target_frame(frames)
    installed = sim.evolve_comp(timeline)
    sim.J_MHz = original_j
    sim.set_target_frame(frame0)

    assert dynamic.shape == (2, 4, 16, 1)
    np.testing.assert_allclose(dynamic, installed, rtol=1e-11, atol=1e-11)


def test_network_to_sesolve_gradient_is_finite() -> None:
    config = replace(
        CRNNConfig(),
        hidden_width=8,
        hidden_layers=2,
        batch_size=1,
    )
    physics = build_physics(config)
    model = CRPulseMLP(config, key=jax.random.PRNGKey(4))
    _key, batch = sample_batch(
        config,
        jax.random.PRNGKey(5),
        duration_ns=80,
    )

    def loss_fn(current_model):
        return batch_loss(
            current_model,
            batch,
            duration_ns=80,
            physics=physics,
            config=config,
        )

    (loss, _metrics), grads = eqx.filter_value_and_grad(
        loss_fn,
        has_aux=True,
    )(model)
    leaves = jax.tree_util.tree_leaves(eqx.filter(grads, eqx.is_array))
    norm = jnp.sqrt(sum(jnp.sum(jnp.abs(leaf) ** 2) for leaf in leaves))
    assert jnp.isfinite(loss)
    assert jnp.isfinite(norm)
    assert float(norm) > 0.0


if __name__ == "__main__":
    test_parametric_engine_matches_installed_state()
    test_network_to_sesolve_gradient_is_finite()
    print("CR NN PHYSICS TESTS OK")
