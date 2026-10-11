"""Differentiable two-bound echoed-CR loss for neural pulse training."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

import jax
import jax.numpy as jnp
import numpy as np

from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    _templates_1ns,
    assemble_cr_half_jax,
    echoed_timeline_jax,
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    zx_target_unitary,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    leakage_from_psi_jax,
    process_fidelity_comp_jax,
    u_comp_from_psi_jax,
)
from HM.simulator.two_qubit_simulator.optimization.grape_cost_jax import (
    combine_robust_fidelities_jax,
)

from .config import CRNNConfig
from .model import CRPulseMLP, center_crop_flat, flat_knobs_200
from .sampling import TrainingBatch


@dataclass(frozen=True)
class CRNNPhysics:
    simulator: object
    rise: jnp.ndarray
    fall: jnp.ndarray
    x_pi: jnp.ndarray
    target_comp: jnp.ndarray
    comp_indices: tuple[int, ...]
    target_frame_mhz: float


class RequestMetrics(NamedTuple):
    loss: jnp.ndarray
    fidelity_combined: jnp.ndarray
    fidelity_low: jnp.ndarray
    fidelity_high: jnp.ndarray
    fidelity_spread: jnp.ndarray
    leakage: jnp.ndarray


class BatchMetrics(NamedTuple):
    loss: jnp.ndarray
    fidelity_combined: jnp.ndarray
    fidelity_min: jnp.ndarray
    fidelity_spread: jnp.ndarray
    leakage: jnp.ndarray


def build_physics(config: CRNNConfig) -> CRNNPhysics:
    """Build the fixed c1t2 simulator and pulse templates once."""
    config.validate()
    exp = CR_len_sweep(
        qubit_pair=list(config.qubit_pair),
        echoed_cr=True,
        n_levels=int(config.n_levels),
        engine="dynamiqs",
        envelope=config.envelope,
        dt_sample_ns=float(config.dt_sample_ns),
        cr_pulse_params={
            "amp_mhz": float(config.seed_amp_mhz),
            "phase_rad": float(config.seed_phase_rad),
            "t_rise_ns": int(config.t_rise_ns),
        },
    )
    sim = exp.simulator
    frame1 = float(np.asarray(sim.qubits[1].frame_MHz).reshape(()))
    rise, fall = _templates_1ns(config.t_rise_ns)
    return CRNNPhysics(
        simulator=sim,
        rise=jnp.asarray(rise, dtype=jnp.float64),
        fall=jnp.asarray(fall, dtype=jnp.float64),
        x_pi=jnp.asarray(exp.build_x_pi(), dtype=jnp.complex128),
        target_comp=jnp.asarray(
            zx_target_unitary(config.target_gate),
            dtype=jnp.complex128,
        ),
        comp_indices=tuple(int(i) for i in sim.comp_idx),
        target_frame_mhz=frame1,
    )


def _fidelity_and_leakage(
    psi_one: jnp.ndarray,
    physics: CRNNPhysics,
) -> tuple[jnp.ndarray, jnp.ndarray]:
    u_comp = u_comp_from_psi_jax(psi_one, physics.comp_indices)
    fidelity = process_fidelity_comp_jax(u_comp, physics.target_comp)
    leakage = leakage_from_psi_jax(psi_one, physics.comp_indices)
    return fidelity, leakage


def request_metrics_from_flat(
    flat_200: jnp.ndarray,
    *,
    coupling_mhz,
    robustness_mhz,
    duration_ns: int,
    physics: CRNNPhysics,
    config: CRNNConfig,
) -> RequestMetrics:
    """Score one fixed waveform at target-frame shifts (-S, +S)."""
    duration = int(duration_ns)
    flat = center_crop_flat(flat_200, duration)
    cr_plus, _ = assemble_cr_half_jax(
        flat,
        rise=physics.rise,
        fall=physics.fall,
        n_flat=duration,
        n_link_samples=config.n_link_samples,
    )
    timeline = echoed_timeline_jax(cr_plus, physics.x_pi)
    half_width = jnp.asarray(robustness_mhz, dtype=jnp.float64)
    frames = physics.target_frame_mhz + jnp.stack([-half_width, half_width])
    psi = physics.simulator.evolve_comp(
        timeline,
        target_frame_MHz=frames,
        J_MHz=jnp.asarray(coupling_mhz, dtype=jnp.float64),
    )
    if psi.ndim != 4 or psi.shape[0] != 2 or psi.shape[1] != 4:
        raise ValueError(
            "CR NN robust evolution expected (2, 4, dim, 1), "
            f"got {psi.shape}"
        )
    fidelities, leakages = jax.vmap(
        lambda state: _fidelity_and_leakage(state, physics)
    )(psi)
    combined = combine_robust_fidelities_jax(
        fidelities,
        metric=config.fidelity_metric,
        weights=(0.5, 0.5),
        spread_penalty_lambda=config.spread_penalty_lambda,
    )
    leakage = jnp.mean(leakages)
    score = combined - config.leakage_weight * leakage
    return RequestMetrics(
        loss=-score,
        fidelity_combined=combined,
        fidelity_low=fidelities[0],
        fidelity_high=fidelities[1],
        fidelity_spread=jnp.abs(fidelities[1] - fidelities[0]),
        leakage=leakage,
    )


def batch_loss(
    model: CRPulseMLP,
    batch: TrainingBatch,
    *,
    duration_ns: int,
    physics: CRNNPhysics,
    config: CRNNConfig,
) -> tuple[jnp.ndarray, BatchMetrics]:
    """Mean loss for a same-duration minibatch."""
    flat_batch = jax.vmap(flat_knobs_200, in_axes=(None, 0, 0))(
        model,
        batch.normalized_x,
        batch.amp_bound_mhz,
    )
    metrics = jax.vmap(
        lambda flat, coupling, half_width: request_metrics_from_flat(
            flat,
            coupling_mhz=coupling,
            robustness_mhz=half_width,
            duration_ns=duration_ns,
            physics=physics,
            config=config,
        )
    )(flat_batch, batch.coupling_mhz, batch.robustness_mhz)
    mean_loss = jnp.mean(metrics.loss)
    summary = BatchMetrics(
        loss=mean_loss,
        fidelity_combined=jnp.mean(metrics.fidelity_combined),
        fidelity_min=jnp.min(
            jnp.minimum(metrics.fidelity_low, metrics.fidelity_high)
        ),
        fidelity_spread=jnp.mean(metrics.fidelity_spread),
        leakage=jnp.mean(metrics.leakage),
    )
    return mean_loss, summary


def fidelities_for_shifts(
    flat_200: jnp.ndarray,
    shifts_mhz: jnp.ndarray,
    *,
    coupling_mhz,
    duration_ns: int,
    physics: CRNNPhysics,
    config: CRNNConfig,
) -> tuple[jnp.ndarray, jnp.ndarray]:
    """Score one frozen network waveform on an arbitrary detuning grid."""
    duration = int(duration_ns)
    flat = center_crop_flat(flat_200, duration)
    cr_plus, _ = assemble_cr_half_jax(
        flat,
        rise=physics.rise,
        fall=physics.fall,
        n_flat=duration,
        n_link_samples=config.n_link_samples,
    )
    timeline = echoed_timeline_jax(cr_plus, physics.x_pi)
    frames = physics.target_frame_mhz + jnp.asarray(
        shifts_mhz,
        dtype=jnp.float64,
    ).reshape(-1)
    psi = physics.simulator.evolve_comp(
        timeline,
        target_frame_MHz=frames,
        J_MHz=jnp.asarray(coupling_mhz, dtype=jnp.float64),
    )
    return jax.vmap(lambda state: _fidelity_and_leakage(state, physics))(psi)
