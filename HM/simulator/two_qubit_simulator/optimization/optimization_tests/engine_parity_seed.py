"""Compare QuTiP vs dynamiqs on one echoed-CR seed timeline.

Also sweep QuTiP ``n_sub`` and plot ZX(-pi/2) process fidelity. Dynamiqs Path A
(Tsit5) ignores ``n_sub``, so it is a single horizontal reference.

Phase 1 gate: stop and debug if |F_q - F_d| is ~0.01. Proceed to Phase 2
if max|Uq-Ud| is ~1e-3 to 1e-6 and F agrees at that level.

Run from fourqubitv5/ so HM imports:

    python -m HM.simulator.two_qubit_simulator.optimization.optimization_tests.engine_parity_seed
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import DEFAULT_CR_PULSE_PARAMS
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    embed_in_full,
    leakage_from_comp,
    process_fidelity,
    zx_target_unitary,
)

FLAT_LEN_NS = 122.0
NSUB_SWEEP = (1, 2, 4, 8, 14, 16, 32, 64, 128, 256, 512)


def build_exp(engine: str, n_sub: int = 14) -> CR_len_sweep:
    return CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        n_sub=n_sub,
        engine=engine,
        cr_pulse_params={
            **DEFAULT_CR_PULSE_PARAMS,
            "amp_mhz": 21.0,
            "phase_rad": 0.0,
            "t_rise_ns": 16,
        },
    )


def _zx_m90_fidelity(U: np.ndarray) -> float:
    Ut = embed_in_full(zx_target_unitary("zx_m90"), dim=U.shape[0])
    return float(process_fidelity(U, Ut))


def compare_one(n_sub_qutip: int = 14) -> None:
    exp_q = build_exp("qutip", n_sub=n_sub_qutip)
    exp_d = build_exp("dynamiqs", n_sub=14)  # n_sub unused on Path A Tsit5

    print("delta_qq qutip   ", exp_q.simulator.delta_qq_MHz)
    print("delta_qq dynamiqs", exp_d.simulator.delta_qq_MHz)

    x_pi = exp_q.build_x_pi()
    timeline = exp_q._build_timeline(FLAT_LEN_NS, x_pi=x_pi)

    U_q = exp_q._propagator_from_timeline(timeline)
    U_d = exp_d._propagator_from_timeline(timeline)

    dim = U_q.shape[0]
    print("U shapes", U_q.shape, U_d.shape, "dim", dim)

    du = np.max(np.abs(U_q - U_d))
    print("max |Uq - Ud|", du)

    for name in ("zx_90", "zx_m90"):
        Ut = embed_in_full(zx_target_unitary(name), dim=dim)
        Fq = process_fidelity(U_q, Ut)
        Fd = process_fidelity(U_d, Ut)
        print(
            name,
            "F_q", Fq,
            "F_d", Fd,
            "|dF|", abs(Fq - Fd),
            "leak_q", leakage_from_comp(U_q),
            "leak_d", leakage_from_comp(U_d),
        )


def sweep_nsub_zx_m90() -> str:
    """QuTiP F(zx_m90) vs n_sub; dynamiqs is one Tsit5 point (n_sub unused)."""
    exp_d = build_exp("dynamiqs", n_sub=14)
    x_pi = exp_d.build_x_pi()
    timeline = exp_d._build_timeline(FLAT_LEN_NS, x_pi=x_pi)
    U_d = exp_d._propagator_from_timeline(timeline)
    F_d = _zx_m90_fidelity(U_d)
    print(f"\ndynamiqs Tsit5  F(zx_m90)={F_d:.8f}  (n_sub unused)")

    n_subs = []
    F_qs = []
    dUs = []
    for n_sub in NSUB_SWEEP:
        exp_q = build_exp("qutip", n_sub=n_sub)
        U_q = exp_q._propagator_from_timeline(timeline)
        F_q = _zx_m90_fidelity(U_q)
        du = float(np.max(np.abs(U_q - U_d)))
        n_subs.append(n_sub)
        F_qs.append(F_q)
        dUs.append(du)
        print(
            f"qutip n_sub={n_sub:3d}  F(zx_m90)={F_q:.8f}  "
            f"|F_q-F_d|={abs(F_q - F_d):.3e}  max|Uq-Ud|={du:.3e}"
        )

    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)
    out_png = os.path.join(out_dir, "engine_parity_zx_m90_vs_nsub.png")

    fig, axes = plt.subplots(2, 1, figsize=(7.5, 7.0), sharex=True)
    axes[0].plot(n_subs, F_qs, "o-", color="tab:blue", label="QuTiP (uses n_sub)")
    axes[0].axhline(
        F_d,
        color="tab:orange",
        linestyle="--",
        label=f"dynamiqs Tsit5 ({F_d:.6f})",
    )
    axes[0].set_ylabel("process fidelity  ZX(-π/2)")
    axes[0].set_title("Echoed-CR seed: ZX-m90 fidelity vs QuTiP n_sub")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.3)

    axes[1].semilogy(n_subs, dUs, "s-", color="tab:green")
    axes[1].set_xlabel("n_sub  (QuTiP substeps per sample)")
    axes[1].set_ylabel("max |U_qutip − U_dynamiqs|")
    axes[1].grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"\nsaved {out_png}")
    return out_png


def main() -> None:
    compare_one(n_sub_qutip=14)
    sweep_nsub_zx_m90()


if __name__ == "__main__":
    main()
