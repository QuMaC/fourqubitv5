"""Differeentialbe echoed-CR cost for dynamiqs GRAPE"""

from __future__ import annotations

from dataclasses import dataclass
import jax
import jax.numpy as jnp
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    CHANNEL_NAMES,
    DEFAULT_ECHO_CHANNEL,
    assemble_cr_half_jax,
    echoed_timeline_jax,
)

from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    leakage_from_comp_jax,
    leakage_from_psi_jax,
    process_fidelity_comp_jax,
    process_fidelity_jax,
    u_comp_from_psi_jax,
)

@dataclass(frozen=True)
class GrapeStatics:
    """These are quantities needed for GRAPE that are static"""

    rise: jnp.ndarray
    fall: jnp.ndarray
    n_flat: int
    n_link_samples: int
    x_pi: jnp.ndarray
    U_target_full: jnp.ndarray
    U_target_comp: jnp.ndarray
    comp_indices: tuple[int, ...]
    channel_names: tuple[str, ...] = tuple(CHANNEL_NAMES) if isinstance(CHANNEL_NAMES, (list, tuple)) else ("q1_drive", "q2_drive", "cr_drive")
    echo_channel: str = DEFAULT_ECHO_CHANNEL
    evolution: str = "comp"
    leakage_weight: float = 0.0


def _x_to_knobs_jax(
    x: jnp.ndarray,
) -> jnp.ndarray:
    """
    Real I/Q vector gets converted to complex knobs at the flat portion
    """
    x = jnp.asarray(x).reshape(-1)

    return x[0::2] + 1j*x[1::2]

def grape_cost(
    x: jnp.ndarray,
    sim,
    statics: GrapeStatics
    ) -> jnp.ndarray:

    """
        Sclaar cost = -(F - w*leakage). Shape ().
        sim: TwoQubitPulseSimulatorDynamiqs (closed over; frames already set)
    """

    knobs = _x_to_knobs_jax(x)

    cr_plus, _ = assemble_cr_half_jax(
        knobs, 
        rise= statics.rise, 
        fall= statics.fall, 
        n_flat= int(statics.n_flat),
        n_link_samples= int(statics.n_link_samples)
    )

    timeline = echoed_timeline_jax(
        cr_plus, 
        statics.x_pi,
        channel_names= statics.channel_names,
        echo_channel= statics.echo_channel,
    )


    if statics.evolution == "comp":
        psi = sim.evolve_comp(timeline)
        U_comp = u_comp_from_psi_jax(psi, statics.comp_indices)
        F = process_fidelity_comp_jax(U_comp=U_comp, U_target_comp=statics.U_target_comp)
        leak = leakage_from_psi_jax(psi, statics.comp_indices)

    elif statics.evolution == "full":
        U = sim.run_propagator(timeline, return_numpy=False)
        F = process_fidelity_jax(U_full=U, U_target_full=statics.U_target_full, comp_indices=statics.comp_indices)
        leak = leakage_from_comp_jax(U_full=U, comp_indices=statics.comp_indices)

    else:
        raise ValueError(f"Invalid evolution: {statics.evolution}")

    return -(F - statics.leakage_weight*leak)



def combine_robust_fidelities_jax(
    f_a: jnp.ndarray,
    f_b: jnp.ndarray,
    metric: str,
    weights: tuple[float, float] = (0.5, 0.5),
    spread_penalty_lambda: float = 0.3,
) -> jnp.ndarray:
    """Combine two process fidelities. Returns shape ()."""
    wa, wb = weights
    if metric == "weighted_mean":
        return wa * f_a + wb * f_b
    if metric == "geometric_mean":
        return jnp.sqrt(jnp.maximum(f_a, 0.0) * jnp.maximum(f_b, 0.0))
    if metric == "mean_minus_spread":
        weighted = wa * f_a + wb * f_b
        return weighted - spread_penalty_lambda * jnp.abs(f_a - f_b)
    raise ValueError(f"Unknown fidelity_metric {metric!r}")


def grape_cost_robust(
    x: jnp.ndarray,
    sim,
    statics: GrapeStatics,
    *,
    fidelity_metric: str = "weighted_mean",
    weights: tuple[float, float] = (0.5, 0.5),
    spread_penalty_lambda: float = 0.3,
) -> jnp.ndarray:
    """Scalar cost for length-2 target frame. sim frames already set."""
    knobs = _x_to_knobs_jax(x)
    cr_plus, _ = assemble_cr_half_jax(
        knobs,
        rise=statics.rise,
        fall=statics.fall,
        n_flat=int(statics.n_flat),
        n_link_samples=int(statics.n_link_samples),
    )
    timeline = echoed_timeline_jax(
        cr_plus,
        statics.x_pi,
        channel_names=statics.channel_names,
        echo_channel=statics.echo_channel,
    )

    if statics.evolution != "comp":
        raise ValueError(
            "Phase 6 grape_cost_robust locks evolution='comp' "
            f"(got {statics.evolution!r})"
        )

    psi = sim.evolve_comp(timeline)
    # Expect (2, 4, dim, 1). If you see (4, 2, dim, 1), swap axes here.
    if psi.ndim != 4 or psi.shape[0] != 2 or psi.shape[1] != 4:
        raise ValueError(
            f"robust evolve_comp expected psi shape (2, 4, dim, 1), got {psi.shape}. "
            "Print shape in the smoke test and fix axis order before jit."
        )

    def _one(psi_one):
        U_comp = u_comp_from_psi_jax(psi_one, statics.comp_indices)
        F = process_fidelity_comp_jax(
            U_comp=U_comp, U_target_comp=statics.U_target_comp
        )
        leak = leakage_from_psi_jax(psi_one, statics.comp_indices)
        return F, leak

    # vmap over detuning axis
    F_batch, leak_batch = jax.vmap(_one)(psi)
    F_comb = combine_robust_fidelities_jax(
        F_batch[0],
        F_batch[1],
        metric=fidelity_metric,
        weights=weights,
        spread_penalty_lambda=spread_penalty_lambda,
    )
    leak_comb = 0.5 * (leak_batch[0] + leak_batch[1])
    return -(F_comb - statics.leakage_weight * leak_comb)