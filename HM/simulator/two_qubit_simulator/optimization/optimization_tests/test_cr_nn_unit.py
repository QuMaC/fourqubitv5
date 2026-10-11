"""Fast unit tests for the CR neural pulse model and checkpoints."""

from __future__ import annotations

from dataclasses import replace
import tempfile

import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np
import optax

from HM.simulator.two_qubit_simulator.optimization.cr_nn.checkpoint import (
    load_checkpoint,
    save_checkpoint,
)
from HM.simulator.two_qubit_simulator.optimization.cr_nn.config import (
    CRNNConfig,
    normalize_inputs,
)
from HM.simulator.two_qubit_simulator.optimization.cr_nn.model import (
    CRPulseMLP,
    center_crop_flat,
    count_parameters,
    flat_knobs_200,
)


def _tiny_config() -> CRNNConfig:
    return replace(
        CRNNConfig(),
        hidden_width=8,
        hidden_layers=2,
        batch_size=1,
        keep_checkpoints=2,
    )


def test_normalized_input_endpoints() -> None:
    config = CRNNConfig()
    low = normalize_inputs(
        config,
        min(config.durations_ns),
        config.robustness_min_mhz,
        config.amp_min_mhz,
        config.coupling_min_mhz,
    )
    high = normalize_inputs(
        config,
        max(config.durations_ns),
        config.robustness_max_mhz,
        config.amp_max_mhz,
        config.coupling_max_mhz,
    )
    np.testing.assert_allclose(low, -np.ones(4), atol=1e-12)
    np.testing.assert_allclose(high, np.ones(4), atol=1e-12)


def test_model_output_and_center_crop() -> None:
    config = _tiny_config()
    model = CRPulseMLP(config, key=jax.random.PRNGKey(1))
    x = normalize_inputs(
        config,
        120,
        0.15,
        50.0,
        config.coupling_center_mhz,
    )
    flat = flat_knobs_200(model, x, 50.0)
    cropped = center_crop_flat(flat, 120)
    assert flat.shape == (200,)
    assert cropped.shape == (120,)
    assert count_parameters(model) == 3712
    assert float(jnp.max(jnp.abs(flat.real))) <= 50.0
    assert float(jnp.max(jnp.abs(flat.imag))) <= 50.0


def test_checkpoint_round_trip() -> None:
    config = _tiny_config()
    model = CRPulseMLP(config, key=jax.random.PRNGKey(2))
    optimizer = optax.adan(config.learning_rate, weight_decay=0.0)
    params = eqx.filter(model, eqx.is_inexact_array)
    state = optimizer.init(params)
    key = jax.random.PRNGKey(3)

    with tempfile.TemporaryDirectory() as tmp:
        saved = save_checkpoint(
            tmp,
            global_step=17,
            model=model,
            optimizer_state=state,
            rng_key=key,
            config=config,
            duration_order=config.durations_ns,
            last_metrics={"fidelity_combined": 0.9},
            fixed_duration_ns=80,
        )
        loaded_model, loaded_state, loaded_key, metadata, resolved = load_checkpoint(
            tmp,
            model_template=CRPulseMLP(config, key=jax.random.PRNGKey(99)),
            optimizer_state_template=state,
        )
        assert resolved == saved
        assert metadata["global_step"] == 17
        assert metadata["fixed_duration_ns"] == 80
        np.testing.assert_array_equal(loaded_key, key)
        original = jax.tree_util.tree_leaves(eqx.filter(model, eqx.is_array))
        restored = jax.tree_util.tree_leaves(
            eqx.filter(loaded_model, eqx.is_array)
        )
        for left, right in zip(original, restored):
            np.testing.assert_array_equal(left, right)
        assert jax.tree_util.tree_structure(loaded_state) == jax.tree_util.tree_structure(
            state
        )
        second = save_checkpoint(
            tmp,
            global_step=17,
            model=model,
            optimizer_state=state,
            rng_key=key,
            config=config,
            duration_order=config.durations_ns,
            fixed_duration_ns=80,
        )
        assert second != saved
        assert second.is_dir()


if __name__ == "__main__":
    test_normalized_input_endpoints()
    test_model_output_and_center_crop()
    test_checkpoint_round_trip()
    print("CR NN UNIT TESTS OK")
