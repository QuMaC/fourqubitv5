"""Equinox MLP and the fixed 200-sample CR flat-top output contract."""

from __future__ import annotations

import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np

from .config import CRNNConfig


class CRPulseMLP(eqx.Module):
    """Four normalized inputs to 200 complex, 1 ns DAC samples."""

    layers: tuple[eqx.nn.Linear, ...]
    max_flat_samples: int = eqx.field(static=True)
    seed_amp_mhz: float = eqx.field(static=True)

    def __init__(self, config: CRNNConfig, *, key) -> None:
        config.validate()
        widths = (
            config.input_size,
            *([config.hidden_width] * config.hidden_layers),
            config.output_size,
        )
        keys = jax.random.split(key, len(widths) - 1)
        layers = [
            eqx.nn.Linear(n_in, n_out, key=layer_key)
            for n_in, n_out, layer_key in zip(widths[:-1], widths[1:], keys)
        ]

        # Start extremely close to the calibrated flat pulse while retaining
        # nonzero gradients through every hidden layer on the first update.
        final = layers[-1]
        final = eqx.tree_at(
            lambda layer: layer.weight,
            final,
            final.weight * config.init_output_scale,
        )
        if final.bias is not None:
            final = eqx.tree_at(
                lambda layer: layer.bias,
                final,
                jnp.zeros_like(final.bias),
            )
        layers[-1] = final

        self.layers = tuple(layers)
        self.max_flat_samples = int(config.max_flat_samples)
        self.seed_amp_mhz = float(config.seed_amp_mhz)

    def __call__(self, normalized_x: jnp.ndarray) -> jnp.ndarray:
        y = jnp.asarray(normalized_x, dtype=jnp.float64)
        for layer in self.layers[:-1]:
            y = jax.nn.relu(layer(y))
        return self.layers[-1](y)


def flat_knobs_200(
    model: CRPulseMLP,
    normalized_x: jnp.ndarray,
    amp_bound_mhz,
) -> jnp.ndarray:
    """Return 200 smoothly bounded complex DAC samples for one request."""
    raw = model(normalized_x).reshape(model.max_flat_samples, 2)
    bound = jnp.asarray(amp_bound_mhz, dtype=jnp.float64)
    seed_ratio = jnp.clip(model.seed_amp_mhz / bound, -0.999999, 0.999999)
    i = bound * jnp.tanh(jnp.arctanh(seed_ratio) + raw[:, 0] / bound)
    q = bound * jnp.tanh(raw[:, 1] / bound)
    return i + 1j * q


def center_crop_flat(flat_200: jnp.ndarray, duration_ns: int) -> jnp.ndarray:
    """Center-crop a fixed output to a static integer duration at 1 ns."""
    flat_200 = jnp.asarray(flat_200).reshape(-1)
    duration = int(duration_ns)
    n_max = int(flat_200.shape[0])
    if duration < 1 or duration > n_max:
        raise ValueError(f"duration_ns must be in [1, {n_max}], got {duration}")
    if (n_max - duration) % 2:
        raise ValueError(
            f"cannot center-crop {n_max} samples to {duration} with integer edges"
        )
    start = (n_max - duration) // 2
    return jax.lax.dynamic_slice(flat_200, (start,), (duration,))


def centered_plot_row(flat: np.ndarray, max_flat_samples: int = 200) -> np.ndarray:
    """Embed one active flat top in a NaN-padded row for color plots."""
    flat = np.asarray(flat, dtype=complex).reshape(-1)
    n_max = int(max_flat_samples)
    if flat.size > n_max or (n_max - flat.size) % 2:
        raise ValueError("flat cannot be centered on the requested plotting grid")
    row = np.full(n_max, np.nan + 1j * np.nan, dtype=complex)
    start = (n_max - flat.size) // 2
    row[start : start + flat.size] = flat
    return row


def count_parameters(model: CRPulseMLP) -> int:
    """Count trainable array scalars."""
    arrays = jax.tree_util.tree_leaves(eqx.filter(model, eqx.is_array))
    return int(sum(np.prod(array.shape, dtype=np.int64) for array in arrays))
