"""Shared chip setup for the Phase 3 spectator experiments."""

from __future__ import annotations

from HM.simulator.n_qubit_simulator.analysis.dressed_frame import (
    DressedBasis,
    compensate_frames,
    dressed_basis,
    single_excitation_MHz,
)
from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)
from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    load_grape_sidecar,
)
from HM.simulator.n_qubit_simulator.experiments.c1t2_parity import (
    C1T2_NPZ_PATH,
)


ACTIVE_EDGE = "c1_t2"
CONTROL_SIDE_CHIP = (1, 2, 4, 6)
TARGET_SIDE_CHIP = (1, 2, 3)


def active_levels() -> int:
    """Truncation the GRAPE archive was optimized at."""
    return load_grape_sidecar(C1T2_NPZ_PATH)["n_levels"]


def build_chip(
    qubit_ids: tuple[int, ...],
    n_active_levels: int,
) -> NQubitSimulatorBase:
    """Q1 and Q2 at the GRAPE truncation, spectators at 3 levels."""

    if tuple(qubit_ids[:2]) != (1, 2):
        raise ValueError("Phase 3 chips start with the active pair Q1, Q2")
    overrides = (
        None
        if n_active_levels == 3
        else {1: n_active_levels, 2: n_active_levels}
    )
    return NQubitSimulatorBase(
        qubit_ids=qubit_ids,
        n_levels=3,
        levels_by_qubit=overrides,
        dt_sample_ns=1.0,
    )


def set_edges(sim, enabled_names) -> None:
    enabled_names = set(enabled_names)
    unknown = enabled_names - {edge.name for edge in sim.coupling_edges}
    if unknown:
        raise KeyError(f"chip has no edges {sorted(unknown)}")
    for edge in sim.coupling_edges:
        edge.enabled = edge.name in enabled_names


def reset_frames(sim) -> None:
    for qubit in sim.qubits:
        qubit.frame_MHz = qubit.f_qubit_MHz


def ground_reference_MHz(sim) -> dict[int, float]:
    """Dressed frequencies of the Phase 2 model, only ``c1_t2`` on.

    Spectators are uncoupled in that model, so their reference is their
    calibrated frequency.
    """

    reset_frames(sim)
    set_edges(sim, (ACTIVE_EDGE,))
    return single_excitation_MHz(sim, dressed_basis(sim))


def configure(sim, enabled_names, target_MHz) -> DressedBasis:
    """Switch ``enabled_names`` on and retune bare frequencies to the target."""

    reset_frames(sim)
    set_edges(sim, enabled_names)
    return compensate_frames(sim, target_MHz)
