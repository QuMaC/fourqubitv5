"""Process fidelity for jax"""

from __future__ import annotations

import jax.numpy as jnp
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    DEFAULT_COMP_INDICES,
    COMP_DIM,
)

def _idx(comp_indices: list[int] | tuple[int, ...] | None) -> jnp.ndarray:
    """Static computational indices as a 1-d int array"""

    if comp_indices is None:
        comp_indices = DEFAULT_COMP_INDICES
    return jnp.asarray(comp_indices, dtype=jnp.int64)

def comp_projector_jax(
    dim: int, 
    comp_indices: list[int] | tuple[int, ...] | None = None,

) -> jnp.ndarray:
    """P, shape (dim, dim). Ones on the computational diagonal."""

    dim = int(dim)
    idx  = _idx(comp_indices)

    P = jnp.zeros((dim, dim), dtype=jnp.complex128)
    return P.at[idx, idx].set(1.0)

def comp_block_jax(
    U_full: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
    
) -> jnp.ndarray:
    """U_comp but the 4x4 computational block. U_comp[a,b] = U_full[comp_a,comp_b] for a,b in comp_indices."""

    idx = _idx(comp_indices)
    # idx[:, None] is a column; idx is a row. Advanced indexing → outer pair of indices.
    # Same as NumPy U_full[np.ix_(comp_indices, comp_indices)].
    return U_full[idx[:, None], idx]


def process_fidelity_jax(
    U_full: jnp.ndarray,
    U_target_full: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Neilsen process fidelity on the computational subspace.
    U_full, U_target_full: dim, dim is complex
    returns: 0-d real array (float64), shape ()
    """

    U_full = jnp.asarray(U_full)
    U_target_full = jnp.asarray(U_target_full)
    idx = _idx(comp_indices)
    d = int(idx.shape[0])
    dim = int(U_full.shape[0])

    P = comp_projector_jax(dim, comp_indices)
    M = U_target_full.conj().T @ P @ U_full @ P 

    F = jnp.abs(jnp.trace(M))**2/(d*d)

    return F


def average_gate_fidelity_jax(
    U_full: jnp.ndarray,
    U_target_comp: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Average gate fidelity from the 4x4 block. U_target_comp is 4x4, not 9x9. """

    U_full = jnp.asarray(U_full)
    U_target_comp = jnp.asarray(U_target_comp)
    idx = _idx(comp_indices)
    d = int(idx.shape[0])

    U_comp = comp_block_jax(U_full, comp_indices)
    overlap = jnp.trace(U_target_comp.conj().T @ U_comp)
    return (jnp.abs(overlap)**2 + d)/(d*(d+1))
    
    
def leakage_from_comp_jax(
    U_full: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Mean leakage of the four computational input kets"""

    U_comp = comp_block_jax(jnp.asarray(U_full), comp_indices)

    #axis = 0: sum over rows -> one number per input column
    comp_weight = jnp.sum(jnp.abs(U_comp)**2, axis=0)

    return jnp.mean(1.0- comp_weight)


def u_comp_from_psi_jax(
    psi: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """U_comp from the 4x4 computational block. psi is (4, dim, 1)."""

    psi = jnp.asarray(psi)
    if psi.ndim == 3:
        psi = psi[..., 0]

    idx = _idx(comp_indices)

    return psi[:, idx].T

def process_fidelity_comp_jax(
    U_comp: jnp.ndarray,
    U_target_comp: jnp.ndarray,
) -> jnp.ndarray:
    """Process fidelity from 4×4 blocks. Returns shape ()."""
    U_comp = jnp.asarray(U_comp)
    U_target_comp = jnp.asarray(U_target_comp)
    d = int(U_comp.shape[0])
    overlap = jnp.trace(U_target_comp.conj().T @ U_comp)
    return jnp.abs(overlap) ** 2 / (d * d)


def leakage_from_psi_jax(
    psi: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Mean leakage of the four computational inputs. Shape ()."""
    U_comp = u_comp_from_psi_jax(psi, comp_indices)
    comp_weight = jnp.sum(jnp.abs(U_comp) ** 2, axis=0)
    return jnp.mean(1.0 - comp_weight)