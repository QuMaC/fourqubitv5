"""Bessel and Butterworth envelopes match the analog filter and the one-pole API."""

from __future__ import annotations

import jax

jax.config.update("jax_enable_x64", True)

import numpy as np
import jax.numpy as jnp
import scipy.signal as signal

from HM.simulator.two_qubit_simulator.engine.envelope_filters import (
    FILTERS,
    bessel,
    butterworth,
    envelope_name,
    sample_envelope,
    single_pole,
    zoh_trace,
)


F_3DB = 350e6
DT_NS = 1.0


def _lsim_zoh(kind: str, order: int, knobs: np.ndarray, n_per_bin: int = 32):
    """SciPy analog filter on the same piecewise-constant samples."""
    wn = 2.0 * np.pi * F_3DB
    if kind == "butterworth":
        system = signal.butter(order, wn, btype="low", analog=True, output="ba")
    else:
        system = signal.bessel(
            order, wn, btype="low", analog=True, output="ba", norm="mag"
        )
    knobs = np.asarray(knobs, dtype=float).reshape(-1)
    n = knobs.size
    dt_s = DT_NS * 1e-9
    t = np.linspace(0.0, n * dt_s, n * n_per_bin + 1)
    # interp=False keeps the staircase. Linear interpolation rounds the jumps
    # the DAC hold does not make, and the traces then disagree by ~1e-2.
    idx = np.clip(np.floor(t / dt_s + 1e-12).astype(int), 0, n - 1)
    _tout, y, _x = signal.lsim(system, knobs[idx], t, interp=False)
    return y


def test_zoh_trace_holds_each_sample() -> None:
    t, y = zoh_trace(np.array([1.0, -2.0, 3.5]), 1.0)
    np.testing.assert_allclose(t, [0.0, 1.0, 2.0, 3.0])
    np.testing.assert_allclose(y, [1.0, -2.0, 3.5, 3.5])
    t_c, y_c = zoh_trace(np.array([1 + 2j, 3 - 4j]), 2.0)
    np.testing.assert_allclose(t_c, [0.0, 2.0, 4.0])
    np.testing.assert_allclose(y_c, [1 + 2j, 3 - 4j, 3 - 4j])


def test_registered_names() -> None:
    assert set(FILTERS) >= {
        "identity",
        "lp_350mhz",
        "bessel4_350mhz",
        "butterworth4_350mhz",
    }
    assert envelope_name("bessel4_350mhz") == "bessel4_350mhz"
    assert envelope_name(bessel(200e6, order=3)) == "bessel3_200MHz"
    assert envelope_name(butterworth(200e6, order=2)) == "butterworth2_200MHz"


def test_order1_matches_single_pole() -> None:
    rng = np.random.default_rng(0)
    knobs = rng.normal(size=24) + 1j * rng.normal(size=24)
    _t, y_pole = sample_envelope(single_pole(F_3DB), knobs, DT_NS, n_per_bin=8)
    _t, y_but = sample_envelope(butterworth(F_3DB, order=1), knobs, DT_NS, n_per_bin=8)
    _t, y_bes = sample_envelope(bessel(F_3DB, order=1), knobs, DT_NS, n_per_bin=8)
    np.testing.assert_allclose(y_but, y_pole, rtol=0, atol=1e-9)
    np.testing.assert_allclose(y_bes, y_pole, rtol=0, atol=1e-9)


def test_matches_scipy_lsim() -> None:
    rng = np.random.default_rng(1)
    real = rng.normal(size=20)
    imag = rng.normal(size=20)
    knobs = real + 1j * imag
    for kind, factory in (
        ("butterworth", butterworth(F_3DB, order=4)),
        ("bessel", bessel(F_3DB, order=4)),
    ):
        _t, y = sample_envelope(factory, knobs, DT_NS, n_per_bin=32)
        y_re = _lsim_zoh(kind, 4, real, n_per_bin=32)
        y_im = _lsim_zoh(kind, 4, imag, n_per_bin=32)
        np.testing.assert_allclose(np.real(y), y_re, rtol=1e-5, atol=1e-5)
        np.testing.assert_allclose(np.imag(y), y_im, rtol=1e-5, atol=1e-5)


def test_step_shape() -> None:
    knobs = np.ones(80)
    _t, y_pole = sample_envelope("lp_350mhz", knobs, DT_NS, n_per_bin=16)
    _t, y_bes = sample_envelope("bessel4_350mhz", knobs, DT_NS, n_per_bin=16)
    _t, y_but = sample_envelope("butterworth4_350mhz", knobs, DT_NS, n_per_bin=16)
    for y in (y_pole, y_bes, y_but):
        assert abs(np.imag(y)).max() < 1e-8
        np.testing.assert_allclose(np.real(y[-1]), 1.0, rtol=0, atol=1e-6)
    # One pole chases the step and does not cross it. Butterworth rings.
    # Bessel stays close to a monotonic edge.
    assert np.real(y_pole).max() <= 1.0 + 1e-8
    assert np.real(y_but).max() > 1.05
    assert np.real(y_bes).max() < 1.02


def test_real_linear_on_iq() -> None:
    rng = np.random.default_rng(2)
    i = rng.normal(size=16)
    q = rng.normal(size=16)
    factory = "bessel4_350mhz"
    _t, y = sample_envelope(factory, i + 1j * q, DT_NS)
    _t, yi = sample_envelope(factory, i, DT_NS)
    _t, yq = sample_envelope(factory, q, DT_NS)
    np.testing.assert_allclose(y, yi + 1j * yq, rtol=0, atol=1e-8)


def test_grad_and_jit() -> None:
    factory = bessel(F_3DB, order=4)

    def loss(x):
        knobs = jnp.array([0.0, x[0] + 1j * x[1], -0.4, 0.2], dtype=jnp.complex128)
        env = factory(knobs, DT_NS * 1e-3)
        ts = jnp.linspace(0.0, 4e-3, 33)
        return jnp.sum(jnp.real(env(ts)))

    g = jax.jit(jax.grad(loss))(jnp.array([0.7, -0.2]))
    assert np.all(np.isfinite(np.asarray(g)))
    assert np.linalg.norm(np.asarray(g)) > 0.0


if __name__ == "__main__":
    test_zoh_trace_holds_each_sample()
    test_registered_names()
    test_order1_matches_single_pole()
    test_matches_scipy_lsim()
    test_step_shape()
    test_real_linear_on_iq()
    test_grad_and_jit()
    print("envelope filter tests passed")
