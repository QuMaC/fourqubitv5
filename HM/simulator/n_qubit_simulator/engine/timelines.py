"""Fixed-shape pulse timelines for the n-qubit simulator."""

from __future__ import annotations

from collections.abc import Sequence

from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
    _configure_jax,
)

import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.engine.constants import DT_SAMPLE_NS


class Timeline:
    """One equal-length complex JAX buffer per registered channel."""

    def __init__(
        self,
        channels: Sequence[str],
        *,
        n_samples: int,
        dt_ns: float = DT_SAMPLE_NS,
    ) -> None:
        self.channels = tuple(channels)
        self.n_samples = int(n_samples)
        self.dt_ns = float(dt_ns)

        if not self.channels:
            raise ValueError("timeline requires at least one channel")
        if len(set(self.channels)) != len(self.channels):
            raise ValueError("timeline channel names must be unique")
        if self.n_samples <= 0:
            raise ValueError("n_samples must be positive")
        if self.dt_ns <= 0.0:
            raise ValueError("dt_ns must be positive")

        self._buf = {
            channel: jnp.zeros(self.n_samples, dtype=jnp.complex128)
            for channel in self.channels
        }

    @property
    def duration_us(self) -> float:
        return self.n_samples * self.dt_ns * 1e-3

    def add(
        self,
        channel: str,
        start_ns: float,
        waveform,
    ) -> None:
        """Add a waveform to one channel without changing buffer shape."""

        if channel not in self._buf:
            raise KeyError(f"unknown timeline channel {channel!r}")
        start_float = float(start_ns) / self.dt_ns
        start = int(round(start_float))
        if abs(start_float - start) > 1e-9:
            raise ValueError("start_ns must align with the timeline sample grid")

        values = jnp.asarray(waveform, dtype=jnp.complex128).reshape(-1)
        stop = start + int(values.shape[0])
        if start < 0 or stop > self.n_samples:
            raise ValueError(
                f"waveform interval [{start}, {stop}) is outside "
                f"{self.n_samples} samples"
            )
        self._buf[channel] = self._buf[channel].at[start:stop].add(values)

    def finalize(self) -> dict[str, jnp.ndarray]:
        """Return all channels in their fixed registry order."""
        return {channel: self._buf[channel] for channel in self.channels}