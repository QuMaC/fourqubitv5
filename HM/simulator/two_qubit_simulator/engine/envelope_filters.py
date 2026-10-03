"""Drive-envelope filters for the dynamiqs engine.

A filter is a factory ``(knobs, dt_us) -> envelope(t)``.

``knobs`` is the complex DAC hold, one value per sample. ``t`` and ``dt_us``
are in microseconds. ``envelope(t)`` is the complex baseband value that the
carrier multiplies. Real and imaginary parts are filtered by the same real
transfer function.

Pass a key or a factory as ``envelope=`` when building the dynamiqs simulator,
or assign ``simulator.envelope`` before the next shot:

    envelope="identity"          # hold each knob flat
    envelope="lp_350mhz"         # one pole, 3 dB at 350 MHz
    envelope=single_pole(200e6)  # same shape, different cutoff
    envelope=my_factory          # my_factory(knobs, dt_us) -> envelope(t)

``my_factory`` and the function it returns have to be JAX-traceable
(``jnp``, ``lax.scan``). The Schrödinger solver calls ``envelope(t)`` at
whatever times it needs. The factory is where the filter memory is built,
on the full timeline, before that.
"""

from __future__ import annotations

from collections.abc import Callable

import jax
import jax.numpy as jnp
import numpy as np

# (knobs, dt_us) -> (t -> complex scalar)
EnvelopeFactory = Callable


def identity_envelope(knobs: jnp.ndarray, dt_us: float) -> Callable:
    """Hold each knob flat until the next sample."""
    n_eps = knobs.shape[0]

    def envelope(t):
        n = jnp.floor(t / dt_us).astype(jnp.int32)
        n = jnp.clip(n, 0, n_eps - 1)
        return knobs[n]

    return envelope


def _left_edges(knobs: jnp.ndarray, a: jnp.ndarray) -> jnp.ndarray:
    """Filter state at the left edge of every sample. ``a = exp(-wc * dt)``."""

    def step(y, xk):
        y_next = a * y + (1.0 - a) * xk
        return y_next, y

    y0 = jnp.zeros((), dtype=knobs.dtype)
    _, y_left = jax.lax.scan(step, y0, knobs)
    return y_left


def single_pole(f_3db_hz: float = 350e6) -> EnvelopeFactory:
    """First-order low-pass, 3 dB at ``f_3db_hz``.

    One pole at ``s = -2 pi f_3db_hz``. Inside a hold the output is the
    exponential chase from the left-edge value toward that knob.
    """

    def factory(knobs: jnp.ndarray, dt_us: float) -> Callable:
        wc_per_us = 2.0 * jnp.pi * f_3db_hz * 1e-6
        a = jnp.exp(-wc_per_us * dt_us)
        y_left = _left_edges(knobs, a)
        n_eps = knobs.shape[0]

        def envelope(t):
            n = jnp.floor(t / dt_us).astype(jnp.int32)
            n = jnp.clip(n, 0, n_eps - 1)
            tau = t - n * dt_us
            xn = knobs[n]
            yn = y_left[n]
            return xn + (yn - xn) * jnp.exp(-wc_per_us * tau)

        return envelope

    mhz = f_3db_hz * 1e-6
    factory.__name__ = f"single_pole_{mhz:g}MHz"
    return factory


FILTERS: dict[str, EnvelopeFactory] = {
    "identity": identity_envelope,
    "lp_350mhz": single_pole(350e6),
}


def resolve_envelope(envelope: str | EnvelopeFactory) -> EnvelopeFactory:
    """Return a factory from a registered name or from a callable."""
    if isinstance(envelope, str):
        try:
            return FILTERS[envelope]
        except KeyError as exc:
            known = ", ".join(sorted(FILTERS))
            raise KeyError(
                f"unknown envelope {envelope!r}. Known names: {known}."
            ) from exc
    if callable(envelope):
        return envelope
    raise TypeError(
        "envelope must be a filter name or a factory (knobs, dt_us) -> envelope(t), "
        f"got {type(envelope).__name__}"
    )


def envelope_name(envelope: str | EnvelopeFactory) -> str:
    """Short label for plot titles."""
    if isinstance(envelope, str):
        return envelope
    return getattr(envelope, "__name__", "custom")


def sample_envelope(
    envelope: str | EnvelopeFactory,
    knobs,
    dt_ns: float,
    n_per_bin: int = 16,
):
    """Sample the envelope ``sesolve`` evaluates, in nanoseconds.

    ``knobs`` is one channel, complex or real. The filter state starts at 0,
    which is what the solver does at the start of a timeline. Returns
    ``(t_ns, values)`` with ``values`` complex and the same length as ``t_ns``.
    The last time is the right edge of the last sample.
    """
    knobs = jnp.asarray(knobs).reshape(-1)
    if not jnp.iscomplexobj(knobs):
        knobs = knobs.astype(jnp.complex128)
    dt_ns = float(dt_ns)
    dt_us = dt_ns * 1e-3
    n_bins = int(knobs.shape[0])
    n_per_bin = max(1, int(n_per_bin))
    t_ns = jnp.linspace(0.0, n_bins * dt_ns, n_bins * n_per_bin + 1)
    values = resolve_envelope(envelope)(knobs, dt_us)(t_ns * 1e-3)
    return np.asarray(t_ns), np.asarray(values)
