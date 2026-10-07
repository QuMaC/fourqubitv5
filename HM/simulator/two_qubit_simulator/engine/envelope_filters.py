"""Drive-envelope filters for the dynamiqs engine.

A filter is a factory ``(knobs, dt_us) -> envelope(t)``.

``knobs`` is the complex DAC hold, one value per sample. ``t`` and ``dt_us``
are in microseconds. ``envelope(t)`` is the complex baseband value that the
carrier multiplies. Real and imaginary parts are filtered by the same real
transfer function.

Pass a key or a factory as ``envelope=`` when building the dynamiqs simulator,
or assign ``simulator.envelope`` before the next shot:

    envelope="identity"              # hold each knob flat
    envelope="lp_350mhz"             # one pole, 3 dB at 350 MHz
    envelope="bessel4_350mhz"        # 4th-order Bessel, 3 dB at 350 MHz
    envelope="butterworth4_350mhz"   # 4th-order Butterworth, 3 dB at 350 MHz
    envelope=single_pole(200e6)      # same one-pole shape, different cutoff
    envelope=bessel(350e6, order=4)
    envelope=butterworth(350e6, order=2)
    envelope=my_factory              # my_factory(knobs, dt_us) -> envelope(t)

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


def _analog_lowpass_modes(
    kind: str,
    order: int,
    f_3db_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Poles and residues of a unity-DC-gain low-pass, in rad/µs.

    ``H(s) = sum_j r_j / (s - p_j)`` with ``s`` in rad/µs, so it lines up with
    ``envelope(t)`` where ``t`` is in microseconds. ``|H|`` is ``1/sqrt(2)`` at
    ``f_3db_hz``. Poles come from SciPy; the residue sum is the partial-fraction
    form the zero-order hold steps in closed form.
    """
    import scipy.signal as signal

    order = int(order)
    if order < 1 or order > 8:
        raise ValueError(f"filter order must be from 1 to 8, got {order}")
    f_3db_hz = float(f_3db_hz)
    if f_3db_hz <= 0.0:
        raise ValueError(f"f_3db_hz must be positive, got {f_3db_hz}")

    wn = 2.0 * np.pi * f_3db_hz  # rad/s
    if kind == "butterworth":
        _z, poles, gain = signal.butter(
            order, wn, btype="low", analog=True, output="zpk"
        )
    elif kind == "bessel":
        # norm="mag" puts the -3 dB point at wn. Delay-normalized Bessel
        # defines its cutoff from group delay, so the 3 dB frequency would differ.
        _z, poles, gain = signal.bessel(
            order, wn, btype="low", analog=True, output="zpk", norm="mag"
        )
    else:
        raise ValueError(f"unknown low-pass kind {kind!r}")

    poles = np.asarray(poles, dtype=np.complex128).reshape(-1)
    gain = complex(gain)
    if poles.size != order:
        raise RuntimeError(f"{kind} order {order} returned {poles.size} poles")
    if np.any(np.real(poles) >= 0.0):
        raise RuntimeError(f"{kind} order {order} has a right-half-plane pole")

    # Unity DC gain. SciPy low-passes already aim for this; rescale so a held
    # sample settles on that sample.
    dc = gain / np.prod(-poles)
    gain = gain / dc

    residues = np.empty(order, dtype=np.complex128)
    for j in range(order):
        others = np.concatenate([poles[:j], poles[j + 1 :]])
        residues[j] = gain / np.prod(poles[j] - others) if order > 1 else gain

    dc_modes = np.sum(residues / -poles)
    if abs(dc_modes - 1.0) > 1e-8:
        raise RuntimeError(f"{kind} order {order} DC gain is {dc_modes}, not 1")
    h_at_cut = np.sum(residues / (1j * wn - poles))
    if abs(abs(h_at_cut) - 1.0 / np.sqrt(2.0)) > 1e-4:
        raise RuntimeError(
            f"{kind} order {order} gain at {f_3db_hz:g} Hz is "
            f"{abs(h_at_cut):.6f}, expected {1.0 / np.sqrt(2.0):.6f}"
        )

    # t in the solver is microseconds: s_us = s_si / 1e6, r_us = r_si / 1e6.
    return poles * 1e-6, residues * 1e-6


def _modal_zoh_envelope(
    poles_per_us: np.ndarray,
    residues_per_us: np.ndarray,
    name: str,
) -> EnvelopeFactory:
    """Exact zero-order-hold response of ``sum r/(s-p)``.

    The factory scans the mode state at the left edge of every DAC sample.
    ``envelope(t)`` then applies the closed form inside that sample, which is
    what ``sesolve`` evaluates between the 1 ns discontinuities.
    """
    # NumPy, not JAX. FILTERS is built at import, which is before
    # dq.set_precision("double"). Casting here would freeze complex64.
    poles_np = np.ascontiguousarray(poles_per_us, dtype=np.complex128)
    r_over_p_np = np.ascontiguousarray(
        np.asarray(residues_per_us, dtype=np.complex128) / poles_np,
        dtype=np.complex128,
    )

    def factory(knobs: jnp.ndarray, dt_us: float) -> Callable:
        poles = jnp.asarray(poles_np)
        r_over_p = jnp.asarray(r_over_p_np)
        knobs = jnp.asarray(knobs).reshape(-1).astype(poles.dtype)
        dt = jnp.asarray(dt_us, dtype=poles.real.dtype)
        n_eps = knobs.shape[0]
        decay = jnp.exp(poles * dt)
        # y(dt) = exp(p dt) y + (r/p) (exp(p dt) - 1) u
        step_gain = r_over_p * (decay - 1.0)

        def step(y, u):
            y_next = decay * y + step_gain * u
            return y_next, y

        y0 = jnp.zeros((poles.shape[0],), dtype=poles.dtype)
        _final, y_left = jax.lax.scan(step, y0, knobs)

        def envelope(t):
            t = jnp.asarray(t, dtype=jnp.float64)
            n = jnp.floor(t / dt).astype(jnp.int32)
            n = jnp.clip(n, 0, n_eps - 1)
            tau = t - n.astype(jnp.float64) * dt
            u = knobs[n]
            y0_n = y_left[n]
            decay_tau = jnp.exp(poles * jnp.expand_dims(tau, -1))
            y = decay_tau * y0_n + r_over_p * (decay_tau - 1.0) * jnp.expand_dims(u, -1)
            return jnp.sum(y, axis=-1)

        return envelope

    factory.__name__ = name
    return factory


def butterworth(f_3db_hz: float = 350e6, order: int = 4) -> EnvelopeFactory:
    """Butterworth low-pass, 3 dB at ``f_3db_hz``, driven by the DAC hold.

    Maximally flat passband. Order 2 and above rings on a step, so a sharp
    knob jump shows a small overshoot instead of the one-pole hook. Order 1
    is the same filter as ``single_pole``.
    """
    poles, residues = _analog_lowpass_modes("butterworth", order, f_3db_hz)
    mhz = float(f_3db_hz) * 1e-6
    return _modal_zoh_envelope(poles, residues, f"butterworth{int(order)}_{mhz:g}MHz")


def bessel(f_3db_hz: float = 350e6, order: int = 4) -> EnvelopeFactory:
    """Bessel low-pass, 3 dB at ``f_3db_hz``, driven by the DAC hold.

    Nearly constant group delay, so pulse edges round and stay put. A step
    has almost no overshoot: the shark-fin hooks of ``lp_350mhz`` become a
    smooth corner. The 3 dB frequency matches ``butterworth`` (SciPy
    ``norm='mag'``), rather than the delay-normalized Bessel cutoff.
    """
    poles, residues = _analog_lowpass_modes("bessel", order, f_3db_hz)
    mhz = float(f_3db_hz) * 1e-6
    return _modal_zoh_envelope(poles, residues, f"bessel{int(order)}_{mhz:g}MHz")


FILTERS: dict[str, EnvelopeFactory] = {
    "identity": identity_envelope,
    "lp_350mhz": single_pole(350e6),
    "bessel4_350mhz": bessel(350e6, order=4),
    "butterworth4_350mhz": butterworth(350e6, order=4),
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


def zoh_trace(knobs, dt_ns: float):
    """DAC samples held flat for ``dt_ns``, including the right edge.

    ``knobs`` is one channel, complex or real, one value per sample. Returns
    ``(t_ns, values)`` of length ``n_samples + 1``. Plot with
    ``Axes.step(..., where="post")``.
    """
    y = np.asarray(knobs).reshape(-1)
    if y.size < 1:
        raise ValueError("knobs must contain at least one sample")
    t_ns = np.arange(y.size + 1, dtype=float) * float(dt_ns)
    held = np.concatenate([y, y[-1:]])
    return t_ns, held


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
