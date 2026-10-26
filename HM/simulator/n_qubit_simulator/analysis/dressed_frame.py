"""Dressed eigenbasis and reference frames for spectator analysis.

The engine rotates every qubit at its ``frame_MHz`` and has no detuning term,
so ``frame_MHz`` is the bare frequency of the model. These helpers diagonalize
the static lab Hamiltonian, retune bare frequencies so dressed frequencies hit
a target, and read final states back in a dressed rotating frame.
"""

from __future__ import annotations

from dataclasses import dataclass

import dynamiqs as dq
import jax.numpy as jnp
import numpy as np


@dataclass
class DressedBasis:
    """Dressed states of one static configuration, indexed by bare label.

    Column ``k`` of ``vectors`` is the dressed state whose largest bare
    component is the bare basis state ``k``. Its phase makes that component
    real and positive.
    """

    energies_MHz: np.ndarray
    vectors: np.ndarray
    occupations: np.ndarray
    min_overlap: float


def _position(sim, qubit_id: int) -> int:
    return [qubit.qubit_id for qubit in sim.qubits].index(qubit_id)


def occupation_table(sim) -> np.ndarray:
    """Row ``i`` is the occupation of qubit ``i`` in every bare basis state."""
    return np.array(np.unravel_index(np.arange(sim.dim), sim.dims))


def static_hamiltonian_MHz(sim) -> np.ndarray:
    """Lab-frame Hamiltonian with every drive off, in MHz, not angular."""

    lowering = [np.asarray(dq.to_jax(operator)) for operator in sim.a]
    H = np.zeros((sim.dim, sim.dim), dtype=np.complex128)
    for position, qubit in enumerate(sim.qubits):
        a = lowering[position]
        ad = a.conj().T
        H += qubit.frame_MHz * (ad @ a)
        H += 0.5 * qubit.anharm_MHz * (ad @ ad @ a @ a)
    for edge in sim.coupling_edges:
        if not edge.enabled:
            continue
        hop = (
            lowering[_position(sim, edge.qubit_i)].conj().T
            @ lowering[_position(sim, edge.qubit_j)]
        )
        H += edge.J_MHz * (hop + hop.conj().T)
    return H


def dressed_basis(sim) -> DressedBasis:
    """Diagonalize the static Hamiltonian and label states by bare overlap."""

    energies, vectors = np.linalg.eigh(static_hamiltonian_MHz(sim))
    labels = np.argmax(np.abs(vectors) ** 2, axis=0)
    if np.unique(labels).size != sim.dim:
        raise RuntimeError(
            "dressed states do not map one-to-one onto bare labels"
        )
    order = np.argsort(labels)
    energies = energies[order]
    vectors = vectors[:, order]
    diagonal = np.diag(vectors)
    vectors = vectors * np.exp(-1j * np.angle(diagonal))
    return DressedBasis(
        energies_MHz=energies,
        vectors=vectors,
        occupations=occupation_table(sim),
        min_overlap=float(np.min(np.abs(diagonal) ** 2)),
    )


def _single_label(sim, position: int) -> tuple[int, ...]:
    return tuple(1 if index == position else 0 for index in range(len(sim.dims)))


def single_excitation_MHz(sim, basis: DressedBasis) -> dict[int, float]:
    """Dressed 0-to-1 frequency of each qubit, every other qubit in 0."""

    vacuum = basis.energies_MHz[sim.basis_index((0,) * len(sim.dims))]
    return {
        qubit.qubit_id: float(
            basis.energies_MHz[sim.basis_index(_single_label(sim, position))]
            - vacuum
        )
        for position, qubit in enumerate(sim.qubits)
    }


def static_zz_MHz(sim, basis: DressedBasis, qubit_a: int, qubit_b: int) -> float:
    """Dressed E11 - E10 - E01 + E00 for two qubits, the rest in 0."""

    position_a = _position(sim, qubit_a)
    position_b = _position(sim, qubit_b)

    def energy(occ_a: int, occ_b: int) -> float:
        label = [0] * len(sim.dims)
        label[position_a] = occ_a
        label[position_b] = occ_b
        return float(basis.energies_MHz[sim.basis_index(tuple(label))])

    return energy(1, 1) - energy(1, 0) - energy(0, 1) + energy(0, 0)


def compensate_frames(
    sim,
    target_MHz: dict[int, float],
    *,
    tol_MHz: float = 1e-10,
    max_iterations: int = 30,
) -> DressedBasis:
    """Shift bare frequencies until dressed frequencies equal ``target_MHz``.

    Mutates ``Qubit.frame_MHz`` in place. Drive carriers are not touched.
    Returns the dressed basis of the final configuration.
    """

    missing = {qubit.qubit_id for qubit in sim.qubits} - set(target_MHz)
    if missing:
        raise KeyError(f"no target frequency for qubits {sorted(missing)}")

    for _ in range(max_iterations):
        basis = dressed_basis(sim)
        dressed = single_excitation_MHz(sim, basis)
        residual = {
            qubit_id: target_MHz[qubit_id] - frequency
            for qubit_id, frequency in dressed.items()
        }
        if max(abs(value) for value in residual.values()) < tol_MHz:
            return basis
        for qubit in sim.qubits:
            qubit.frame_MHz += residual[qubit.qubit_id]
    raise RuntimeError(
        f"frame compensation did not converge in {max_iterations} iterations"
    )


def dressed_states(sim, basis: DressedBasis, labels) -> dq.QArray:
    """Batch of dressed kets, shape ``(n_labels, dim, 1)``."""

    columns = [basis.vectors[:, sim.basis_index(tuple(label))] for label in labels]
    batch = np.stack(columns)[:, :, None]
    return dq.asqarray(jnp.asarray(batch), dims=sim.dims)


def dressed_amplitudes(
    sim,
    basis: DressedBasis,
    final_states,
    duration_us: float,
    reference_MHz: dict[int, float],
) -> np.ndarray:
    """Final states in the dressed basis and the reference frame.

    Row ``b`` belongs to initial state ``b``. Column ``k`` is the amplitude on
    the dressed state labelled by bare index ``k``. ``basis`` must belong to
    the frames that the shot ran with.
    """

    psi = np.asarray(dq.to_jax(final_states)).reshape(-1, sim.dim)
    frames = np.array([qubit.frame_MHz for qubit in sim.qubits])
    reference = np.array([reference_MHz[qubit.qubit_id] for qubit in sim.qubits])
    frame_energy = frames @ basis.occupations
    reference_energy = reference @ basis.occupations

    lab = psi * np.exp(-2j * np.pi * frame_energy * duration_us)[None, :]
    dressed = lab @ basis.vectors.conj()
    return dressed * np.exp(2j * np.pi * reference_energy * duration_us)[None, :]
