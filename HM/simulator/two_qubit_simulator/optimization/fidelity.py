from __future__ import annotations

import numpy as np

# Default: qutrit layout (matches cr_len_sweep and the engine's comp_idx).
DEFAULT_COMP_INDICES = [0, 1, 3, 4]
COMP_DIM = 4
ZX_GATE_NAMES = ("zx_90", "zx_m90")

def comp_indices_for_levels(n_levels: int) -> list[int]:
    if n_levels < 2:
        raise ValueError(f"n_levels must be >= 2, got {n_levels}")
    
    if n_levels >= 2:
        return [0, 1, n_levels, n_levels+1]


def zx_90_unitary() -> np.ndarray:
    """ZX(+pi/2) = exp(-i pi/4 ZX) on the 4x4 comp subspace."""
    c = 1 / np.sqrt(2)
    return c * np.array([
        [1, -1j, 0, 0],
        [-1j, 1, 0, 0],
        [0, 0, 1, 1j],
        [0, 0, 1j, 1],
    ], dtype=complex)


def zx_m90_unitary() -> np.ndarray:
    """ZX(-pi/2) = exp(+i pi/4 ZX), the dagger of ``zx_90_unitary()``."""
    return zx_90_unitary().conj().T


def zx_target_unitary(gate: str) -> np.ndarray:
    """Resolve a named ZX target on the comp subspace."""
    if gate == "zx_90":
        return zx_90_unitary()
    if gate == "zx_m90":
        return zx_m90_unitary()
    raise ValueError(f"unknown ZX gate {gate!r}; expected 'zx_90' or 'zx_m90'")


def identity_comp_unitary(comp_dimension: int = COMP_DIM) -> np.ndarray:
    return np.eye(comp_dimension, dtype=complex)

def embed_in_full(
    U_comp: np.ndarray,
    dim: int,
    comp_indices: list[int] | None = None,
) -> np.ndarray:
    comp_indices = comp_indices or DEFAULT_COMP_INDICES
    if U_comp.shape != (len(comp_indices), len(comp_indices)):
        raise ValueError(f"U_comp must have shape {len(comp_indices)}, {len(comp_indices)}, got {U_comp.shape}")
    if len(comp_indices) != COMP_DIM:
        raise ValueError(f"comp_indices must have length {COMP_DIM}, got {len(comp_indices)}")
    if max(comp_indices) >= dim:
        raise ValueError(f"comp_indices must be less than {dim}, got {max(comp_indices)}")

    U_full = np.eye(dim,dtype=complex)
    for i, ri in enumerate(comp_indices):
        for j, rj in enumerate(comp_indices):
            U_full[ri, rj] = U_comp[i, j]
    return U_full


def comp_projector(
    dim: int,
    comp_indices: list[int] | None = None,
) -> np.ndarray:


    comp_indices = comp_indices or DEFAULT_COMP_INDICES
    P = np.zeros((dim, dim), dtype = complex)
    for idx in comp_indices:
        P[idx, idx] = 1.0

    return P

def comp_block(
    U_full: np.ndarray,
    comp_indices: list[int] | None = None,
) -> np.ndarray:
    comp_indices = comp_indices or DEFAULT_COMP_INDICES

    return U_full[np.ix_(comp_indices, comp_indices)]

def process_fidelity(
    U_full: np.ndarray,
    U_target_full: np.ndarray,
    comp_indices: list[int] | None = None,
) -> float:
    comp_indices = comp_indices or DEFAULT_COMP_INDICES
    d = len(comp_indices)
    dim = U_full.shape[0]
    if U_target_full.shape != (dim, dim):
        raise ValueError(f"U_target_full must have shape {dim}, {dim}, got {U_target_full.shape}")

    P = comp_projector(dim, comp_indices)
    M = U_target_full.conj().T@P@U_full@P
    return float(abs(np.trace(M))**2 / d**2)

def average_gate_fidelity(
    U_full: np.ndarray,
    U_target_comp: np.ndarray,
    comp_indices: list[int] | None = None,
) -> float:
    """
    Average gate fidelity from the comp-subspace block.

    U_target_comp is 4×4 (e.g. from zx_90_unitary()).
    U_full is the full propagator (e.g. 9×9).
    """
    comp_indices = comp_indices or DEFAULT_COMP_INDICES
    d = len(comp_indices)

    if U_target_comp.shape != (d, d):
        raise ValueError(f"U_target_comp must be {d}×{d}, got {U_target_comp.shape}")

    U_comp = comp_block(U_full, comp_indices)
    overlap = np.trace(U_target_comp.conj().T @ U_comp)
    return float((abs(overlap) ** 2 + d) / (d * (d + 1)))

def leakage_from_comp(
    U_full: np.ndarray,
    comp_indices: list[int] | None = None,
) -> float:
    """
    Mean leakage over comp input states.

    For each comp input column j: leakage_j = 1 - Σ_i |U_ij|² (sum over comp rows i).
    Returns average over the 4 comp columns.
    """
    comp_indices = comp_indices or DEFAULT_COMP_INDICES
    U_comp = comp_block(U_full, comp_indices)
    comp_weight = np.sum(np.abs(U_comp) ** 2, axis=0)  # axis=0 = sum over rows
    return float(np.mean(1.0 - comp_weight))


def _metrics_against_comp_target(
    U_full: np.ndarray,
    U_target_comp: np.ndarray,
    comp_indices: list[int],
) -> dict[str, float]:
    dim = U_full.shape[0]
    U_target_full = embed_in_full(U_target_comp, dim=dim, comp_indices=comp_indices)
    return {
        "process_fidelity": process_fidelity(U_full, U_target_full, comp_indices),
        "average_gate_fidelity": average_gate_fidelity(
            U_full, U_target_comp, comp_indices
        ),
        "leakage": leakage_from_comp(U_full, comp_indices),
    }


def best_zx_gate_metrics(
    U_full: np.ndarray,
    comp_indices: list[int] | None = None,
) -> dict[str, float | str]:
    """
    Score ``U_full`` against both ZX(+pi/2) and ZX(-pi/2); return the better match.

    Echoed CR sign conventions (amp/phase) determine which ZX direction is
    implemented; this avoids penalizing a good pulse with the wrong target sign.
    """
    comp_indices = comp_indices or DEFAULT_COMP_INDICES
    scored = {}
    for name in ZX_GATE_NAMES:
        scored[name] = _metrics_against_comp_target(
            U_full, zx_target_unitary(name), comp_indices
        )
    best = max(ZX_GATE_NAMES, key=lambda n: scored[n]["process_fidelity"])
    out: dict[str, float | str] = {
        "zx_gate": best,
        **scored[best],
        "process_fidelity_zx_90": scored["zx_90"]["process_fidelity"],
        "process_fidelity_zx_m90": scored["zx_m90"]["process_fidelity"],
        "average_gate_fidelity_zx_90": scored["zx_90"]["average_gate_fidelity"],
        "average_gate_fidelity_zx_m90": scored["zx_m90"]["average_gate_fidelity"],
    }
    return out


def gate_metrics(
    U_full: np.ndarray,
    gate: str = "best_zx",
    comp_indices: list[int] | None = None,
) -> dict[str, float | str]:
    """
    Return process fidelity, average gate fidelity, and leakage.

    gate:
        ``"best_zx"`` or ``"auto"`` — pick ZX(+pi/2) vs ZX(-pi/2) by higher F_proc
        ``"zx_90"`` / ``"zx_m90"`` — fixed signed target
        ``"identity"`` — identity on the comp subspace
    """
    comp_indices = comp_indices or DEFAULT_COMP_INDICES

    if gate in ("best_zx", "auto"):
        return best_zx_gate_metrics(U_full, comp_indices)
    if gate == "identity":
        return _metrics_against_comp_target(
            U_full, identity_comp_unitary(), comp_indices
        )
    if gate in ZX_GATE_NAMES:
        return _metrics_against_comp_target(
            U_full, zx_target_unitary(gate), comp_indices
        )
    raise ValueError(
        f"unknown gate {gate!r}; expected 'best_zx', 'auto', 'zx_90', "
        f"'zx_m90', or 'identity'"
    )
# if __name__ == "__main__":
if __name__ == "__main__":
    pass