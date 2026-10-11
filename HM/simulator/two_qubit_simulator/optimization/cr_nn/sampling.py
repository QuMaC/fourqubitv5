"""Sampling of CR neural-network requests."""

from __future__ import annotations

from typing import NamedTuple

import jax
import jax.numpy as jnp
import numpy as np

from .config import CRNNConfig, normalize_inputs


class TrainingBatch(NamedTuple):
    normalized_x: jnp.ndarray
    duration_ns: int
    robustness_mhz: jnp.ndarray
    amp_bound_mhz: jnp.ndarray
    coupling_mhz: jnp.ndarray


def duration_order(config: CRNNConfig) -> tuple[int, ...]:
    """A deterministic shuffled order that is resumed by global step."""
    rng = np.random.default_rng(config.random_seed)
    values = np.asarray(config.durations_ns, dtype=int)
    return tuple(int(v) for v in rng.permutation(values))


def duration_for_step(
    order: tuple[int, ...],
    global_step: int,
) -> int:
    if not order:
        raise ValueError("duration order must be non-empty")
    return int(order[int(global_step) % len(order)])


def sample_batch(
    config: CRNNConfig,
    key: jax.Array,
    *,
    duration_ns: int,
    batch_size: int | None = None,
) -> tuple[jax.Array, TrainingBatch]:
    """Sample continuous S, Amax, and J for one static-duration kernel."""
    size = int(config.batch_size if batch_size is None else batch_size)
    if size < 1:
        raise ValueError("batch_size must be positive")
    duration = int(duration_ns)
    if duration not in config.durations_ns:
        raise ValueError(f"duration {duration} is not in {config.durations_ns}")

    key, s_key, a_key, j_key = jax.random.split(key, 4)
    shape = (size,)
    robustness = jax.random.uniform(
        s_key,
        shape,
        minval=config.robustness_min_mhz,
        maxval=config.robustness_max_mhz,
        dtype=jnp.float64,
    )
    amp_bound = jax.random.uniform(
        a_key,
        shape,
        minval=config.amp_min_mhz,
        maxval=config.amp_max_mhz,
        dtype=jnp.float64,
    )
    coupling = jax.random.uniform(
        j_key,
        shape,
        minval=config.coupling_min_mhz,
        maxval=config.coupling_max_mhz,
        dtype=jnp.float64,
    )
    durations = jnp.full(shape, float(duration), dtype=jnp.float64)
    normalized = normalize_inputs(
        config,
        durations,
        robustness,
        amp_bound,
        coupling,
    )
    return key, TrainingBatch(
        normalized_x=normalized,
        duration_ns=duration,
        robustness_mhz=robustness,
        amp_bound_mhz=amp_bound,
        coupling_mhz=coupling,
    )
