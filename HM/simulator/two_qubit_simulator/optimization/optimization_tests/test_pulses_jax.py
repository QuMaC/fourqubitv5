"""Bit-match pulses_jax against engine/pulses.py + CR_len_sweep layout."""
from __future__ import annotations

import numpy as np
import jax.numpy as jnp
from HM.simulator.two_qubit_simulator.engine.pulses import (
    assemble_cr_half_from_flat_knobs,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    CHANNEL_NAMES,

    assemble_cr_half_jax,
    echoed_timeline_jax,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import _templates_1ns
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep


def _random_knobs(n_knobs: int, rng: np.random.Generator) -> np.ndarray:
    amp = rng.uniform(5.0, 30.0, size=n_knobs)
    phase = rng.uniform(-np.pi, np.pi, size=n_knobs)
    return amp * np.exp(1j * phase)


def test_assemble_matches_numpy() -> None:
    t_rise_ns = 16
    dt_ns = 1.0
    n_link = 8
    rise, fall = _templates_1ns(t_rise_ns)
    rng = np.random.default_rng(0)

    cases = [
        (46, 184.0),   # regular GRAPE default: 4 samples per knob
        (61, 122.0),   # robust-style: 2 samples per knob
        (184, 184.0),  # one knob per sample
        (1, 184.0),    # single complex amp (seed-like)
    ]
    for n_knobs, flat_len_ns in cases:
        knobs = _random_knobs(n_knobs, rng)
        wf_np, sl_np = assemble_cr_half_from_flat_knobs(
            knobs,
            flat_len_ns=flat_len_ns,
            t_rise_ns=t_rise_ns,
            dt_ns=dt_ns,
            n_link_samples=n_link,
        )
        n_flat = int(round(flat_len_ns / dt_ns))
        wf_jx, sl_jx = assemble_cr_half_jax(
            knobs,  # numpy in is ok; function jnp.asarray's
            rise=rise,
            fall=fall,
            n_flat=n_flat,
            n_link_samples=n_link,
        )
        np.testing.assert_allclose(np.asarray(wf_jx), wf_np, atol=1e-14, rtol=1e-14)
        assert sl_jx == sl_np
        print("assemble ok", n_knobs, n_flat, "len", wf_np.size)

    try:
        assemble_cr_half_jax(
            _random_knobs(3, rng),
            rise=rise,
            fall=fall,
            n_flat=10,
            n_link_samples=n_link,
        )
    except ValueError:
        print("uneven (3, 10) rejected ok")
    else:
        raise AssertionError("expected ValueError when n_knobs does not divide n_flat")


def test_echoed_timeline_matches_numpy() -> None:
    exp = CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        engine="qutip",
        n_sub=2,
    )
    x_pi = exp.build_x_pi()
    rng = np.random.default_rng(1)
    knobs = _random_knobs(46, rng)
    cr_plus, _ = assemble_cr_half_from_flat_knobs(
        knobs,
        flat_len_ns=184.0,
        t_rise_ns=16,
        dt_ns=1.0,
        n_link_samples=8,
    )
    tl_np = exp._build_timeline_from_cr_half(cr_plus, x_pi=x_pi)
    tl_jx = echoed_timeline_jax(cr_plus, x_pi, channel_names=tuple(exp.channels))

    assert set(tl_jx) == set(tl_np) == set(CHANNEL_NAMES)
    for name in CHANNEL_NAMES:
        np.testing.assert_allclose(
            np.asarray(tl_jx[name]), tl_np[name], atol=0, rtol=0
        )
        print(name, "len", tl_np[name].size, "maxabs", np.max(np.abs(tl_np[name])))
    assert tl_np["q2_drive"].shape == tl_np["cr_drive"].shape
    assert np.allclose(tl_np["q2_drive"], 0.0)


def test_assemble_under_jit() -> None:
    import jax

    rise, fall = _templates_1ns(16)
    n_flat = 184
    knobs0 = _random_knobs(46, np.random.default_rng(2))

    @jax.jit
    def wf_len(knobs):
        wf, _ = assemble_cr_half_jax(
            knobs, rise=rise, fall=fall, n_flat=n_flat, n_link_samples=8
        )
        return wf

    a = wf_len(jnp.asarray(knobs0))
    b = wf_len(jnp.asarray(knobs0 * 1.01))
    assert a.shape == b.shape
    assert not np.allclose(np.asarray(a), np.asarray(b))
    print("jit assemble ok", a.shape, a.dtype)


if __name__ == "__main__":
    test_assemble_matches_numpy()
    test_echoed_timeline_matches_numpy()
    test_assemble_under_jit()