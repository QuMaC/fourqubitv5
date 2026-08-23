"""Phase 6: batched ±frame vs sequential; short robust L-BFGS + JAX jac smoke."""
from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from HM.simulator.two_qubit_simulator.engine import two_q_pulse_sim_dynamiqs  # noqa: F401
from HM.simulator.two_qubit_simulator.engine.pulses import (
    assemble_cr_half_from_flat_knobs,
    seed_flat_knobs_from_calibrated_cr,
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import DEFAULT_CR_PULSE_PARAMS
from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    embed_in_full,
    process_fidelity,
    zx_target_unitary,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    process_fidelity_comp_jax,
    u_comp_from_psi_jax,
)


def _make_exp() -> CR_len_sweep:
    return CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        engine="dynamiqs",
        n_sub=14,
        cr_pulse_params={
            **DEFAULT_CR_PULSE_PARAMS,
            "amp_mhz": -21.0,
            "phase_rad": 0.0,
            "t_rise_ns": 16,
        },
    )


def test_batch_frame_shapes_and_parity() -> None:
    exp = _make_exp()
    sim = exp.simulator
    f1 = float(sim.qubits[1].frame_MHz)
    s = 0.1

    knobs = seed_flat_knobs_from_calibrated_cr(
        n_flat_knobs=61,
        flat_len_ns=122.0,
        amp_mhz=-21.0,
        phase_rad=0.0,
        t_rise_ns=16,
        dt_ns=1.0,
    )
    cr, _ = assemble_cr_half_from_flat_knobs(
        knobs, flat_len_ns=122.0, t_rise_ns=16, dt_ns=1.0, n_link_samples=8
    )
    x_pi = exp.build_x_pi()
    timeline = exp._build_timeline_from_cr_half(cr, x_pi=x_pi)

    sim.set_target_frame(f1 + jnp.asarray([+s, -s], dtype=jnp.float64))
    print("set delta_qq", sim.delta_qq_MHz)
    psi = sim.evolve_comp(timeline)
    print("batched psi.shape", tuple(psi.shape))
    assert psi.shape == (2, 4, 9, 1), psi.shape

    Ut = zx_target_unitary("zx_90")
    Ut_full = embed_in_full(Ut, dim=9, comp_indices=sim.comp_idx)

    F_batch = []
    for i in range(2):
        U_comp = u_comp_from_psi_jax(psi[i], sim.comp_idx)
        F_batch.append(float(process_fidelity_comp_jax(U_comp, Ut)))

    F_seq = []
    for shift in (+s, -s):
        sim.set_target_frame(f1 + float(shift))
        U = exp._propagator_from_timeline(timeline)
        F_seq.append(float(process_fidelity(U, Ut_full)))

    print("F_batch", F_batch, "F_seq", F_seq)
    for a, b in zip(F_batch, F_seq):
        assert abs(a - b) < 5e-4, (a, b)
    print("PHASE 6 SHAPE+PARITY OK")


def test_robust_lbfgs_smoke() -> None:
    cfg = RobustCRGrapeConfig(
        flat_len_ns=122.0,
        n_flat_knobs=61,
        seed_amp_mhz=-21.0,
        seed_phase_rad=0.0,
        zz_shift_mhz=0.2,
        fidelity_metric="weighted_mean",
        maxiter=3,
        use_jax_grad=True,
        optimizer="lbfgs",
        evolution="comp",
        n_sub=14,
        show_progress=True,
        optimize=True,
        target_gate="zx_90",
    )
    opt = RobustCRGrapeOptimizer(cfg)

    x0 = np.column_stack(
        [opt.flat_knobs_seed.real, opt.flat_knobs_seed.imag]
    ).ravel()
    c, g = opt._cost_and_grad(x0)
    gnorm = float(np.linalg.norm(g))
    print("seed cost", float(c), "grad_norm", gnorm)
    assert np.isfinite(float(c))
    assert gnorm > 0.0

    # Clear warm-compile eval from history before minimize (run() warms again).
    opt.eval_history.clear()
    opt._last_eval_metrics = None

    result = opt.run()
    n_eval = len(result.eval_history)
    print(
        "final F_comb",
        result.final_metrics["process_fidelity"],
        "Fa",
        result.final_metrics["process_fidelity_a"],
        "Fb",
        result.final_metrics["process_fidelity_b"],
        "n_eval",
        n_eval,
    )
    assert result.scipy_result is not None
    assert n_eval < 120, f"too many evals: {n_eval}"
    print("PHASE 6 OK")


if __name__ == "__main__":
    test_batch_frame_shapes_and_parity()
    test_robust_lbfgs_smoke()
