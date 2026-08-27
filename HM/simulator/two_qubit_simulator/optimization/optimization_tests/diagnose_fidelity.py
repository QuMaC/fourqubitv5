"""Diagnose low process fidelity at |R| minimum vs zx_90 target."""

from __future__ import annotations

import numpy as np
import scipy.linalg as sla

from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    average_gate_fidelity,
    best_zx_gate_metrics,
    comp_block,
    embed_in_full,
    process_fidelity,
    zx_90_unitary,
    zx_m90_unitary,
)

_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_PAULI4 = {
    "I": np.kron(_I2, _I2),
    "ZX": np.kron(_Z, _X),
    "IX": np.kron(_I2, _X),
    "ZY": np.kron(_Z, _Y),
    "IY": np.kron(_I2, _Y),
    "ZZ": np.kron(_Z, _Z),
    "IZ": np.kron(_I2, _Z),
    "XZ": np.kron(_X, _Z),
    "XI": np.kron(_X, _I2),
}


def pauli_decomp(U_comp: np.ndarray) -> dict[str, complex]:
    out = {}
    for lab, P in _PAULI4.items():
        out[lab] = np.trace(P @ U_comp) / 4.0
    return out


def generators_from_comp(U_comp: np.ndarray, T_total_ns: float) -> dict[str, float]:
    Up, _ = sla.polar(U_comp)
    T_us = float(T_total_ns) * 1e-3
    H_eff = 1j * sla.logm(Up) / T_us
    H_eff = 0.5 * (H_eff + H_eff.conj().T)
    out = {}
    for lab in ("ZX", "IX", "ZY", "IY", "ZZ", "IZ"):
        c = np.trace(_PAULI4[lab] @ H_eff) / 4.0
        out[lab] = float(np.real(2.0 * c / (2 * np.pi)))
    return out


def unitary_from_generators_mhz(gens_mhz: dict[str, float], T_total_ns: float) -> np.ndarray:
    T_us = float(T_total_ns) * 1e-3
    H = np.zeros((4, 4), dtype=complex)
    for lab, rate_mhz in gens_mhz.items():
        if lab in _PAULI4:
            H += 2 * np.pi * rate_mhz * _PAULI4[lab]
    return sla.expm(-1j * H * T_us)


def target_variants() -> dict[str, np.ndarray]:
    return {
        "zx_90": zx_90_unitary(),
        "zx_m90": zx_m90_unitary(),
    }


def score_targets(U_full: np.ndarray, targets: dict[str, np.ndarray]) -> None:
    dim = U_full.shape[0]
    print("  Target scan (process F / avg F):")
    for name, Ut in targets.items():
        Ut_full = embed_in_full(Ut, dim=dim)
        fp = process_fidelity(U_full, Ut_full)
        fa = average_gate_fidelity(U_full, Ut)
        print(f"    {name:16s}  F_proc={fp:.4f}  F_avg={fa:.4f}")
    best = best_zx_gate_metrics(U_full)
    print(
        f"    {'best_zx':16s}  gate={best['zx_gate']}  "
        f"F_proc={float(best['process_fidelity']):.4f}  "
        f"F_avg={float(best['average_gate_fidelity']):.4f}"
    )


def run_case(label: str, flat_len: float, amp_mhz: float, phase_rad: float) -> None:
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"  flat={flat_len} ns  amp={amp_mhz} MHz  phase={phase_rad:.4f} rad")
    exp = CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        cr_pulse_params={"amp_mhz": amp_mhz, "t_rise_ns": 16, "phase_rad": phase_rad},
    )
    x_pi = exp.build_x_pi()
    timeline = exp._build_timeline(length=float(flat_len), x_pi=x_pi)
    U = exp._propagator_from_timeline(timeline)
    Uc = comp_block(U)
    t_rise = exp.cr_pulse_params["t_rise_ns"]
    x_pi_len = exp.x_pi_pulse_params["length_ns"]
    T_total = 2 * (2 * t_rise + flat_len) + 2 * x_pi_len

    print(f"  total echoed duration = {T_total:.1f} ns")
    print(f"  |U_comp| (rounded):\n{np.round(np.abs(Uc), 3)}")
    print(f"  Pauli coeffs of U_comp (real part, MHz-scale N/A):")
    decomp = pauli_decomp(Uc)
    for k in ("I", "ZX", "IX", "ZY", "IY", "ZZ", "IZ", "XZ", "XI"):
        c = decomp[k]
        if abs(c) > 0.05:
            print(f"    {k:3s}: {c.real:+.3f}{c.imag:+.3f}j  |c|={abs(c):.3f}")

    gens = generators_from_comp(Uc, T_total)
    print(f"  Matrix-log generators [MHz]:")
    for k, v in gens.items():
        print(f"    {k:3s}: {v:+.4f}")

    # Integrated ZX angle (rough)
    theta_zx = 2 * np.pi * abs(gens["ZX"]) * T_total * 1e-3
    print(f"  |theta_ZX| from generator ~ {theta_zx:.3f} rad  (pi/2 = {np.pi/2:.3f})")

    score_targets(U, target_variants())

    # Target from extracted effective H (best self-consistent target)
    U_eff = unitary_from_generators_mhz(gens, T_total)
    F_eff = average_gate_fidelity(U, U_eff)
    F_eff_proc = process_fidelity(U, embed_in_full(U_eff, dim=9))
    print(f"  F vs matrix-log effective U: F_proc={F_eff_proc:.4f}  F_avg={F_eff:.4f}")

    # How close is U_comp to zx_90 up to local single-qubit gates? (weaker check)
    overlap = np.trace(zx_90_unitary().conj().T @ Uc)
    print(f"  Tr(U_zx90^dag U) = {overlap.real:+.4f}{overlap.imag:+.4f}j  |.|^2/16 = {abs(overlap)**2/16:.4f}")


def main() -> None:
    # |R| minimum case (user's current plot settings)
    run_case("|R| min (user settings)", flat_len=184, amp_mhz=-32.0, phase_rad=2.724)

    # Lab JSON phase, both amp signs
    run_case("Lab phase, amp=+32", flat_len=184, amp_mhz=32.0, phase_rad=0.2139412208060726)
    run_case("Lab phase, amp=-32", flat_len=184, amp_mhz=-32.0, phase_rad=0.2139412208060726)

    # Lab cr_len flat ~244
    run_case("Lab len+phase, amp=-32", flat_len=244, amp_mhz=-32.0, phase_rad=2.724)

    # Old F-max point for contrast
    run_case("Old F-max point", flat_len=500, amp_mhz=-32.0, phase_rad=2.724)


if __name__ == "__main__":
    main()
