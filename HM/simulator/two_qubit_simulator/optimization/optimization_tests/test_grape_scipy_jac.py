"""Phase 5: compare SciPy L-BFGS-B + JAX jac vs Adam (30 steps) and plot F."""
from __future__ import annotations

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from HM.simulator.two_qubit_simulator.engine import two_q_pulse_sim_dynamiqs  # noqa: F401
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    CRGrapeConfig,
    CRGrapeOptimizer,
    DEFAULT_CR_PULSE_PARAMS,
    GrapeResult,
)

N_STEPS = 60
OUT_DIR = Path(__file__).resolve().parent / "phase5_lbfgs_vs_adam"
PLOT_PATH = OUT_DIR / "fidelity_vs_iter_lbfgs_vs_adam.png"


def _make_exp() -> CR_len_sweep:
    return CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        engine="dynamiqs",
        n_sub=14,
        cr_pulse_params={
            **DEFAULT_CR_PULSE_PARAMS,
            "amp_mhz": -32.0,
            "phase_rad": 0.0,
            "t_rise_ns": 16,
        },
    )


def _make_config(*, optimizer: str) -> CRGrapeConfig:
    return CRGrapeConfig(
        flat_len_ns=122.0,
        n_flat_knobs=61,
        seed_amp_mhz=-21.0,
        seed_phase_rad=0.0,
        maxiter=N_STEPS,
        adam_steps=N_STEPS,
        adam_lr=0.2,
        use_jax_grad=True,
        optimizer=optimizer,
        evolution="comp",
        show_progress=True,
        optimize=True,
        log_every_eval=False,
    )


def _fidelity_curve(result: GrapeResult) -> tuple[np.ndarray, np.ndarray]:
    """Iteration index and process fidelity from optimizer history (+ seed at -1)."""
    seed_F = float(result.seed_metrics["process_fidelity"])
    if not result.history:
        return np.array([-1]), np.array([seed_F])
    iters = np.array([int(row["iteration"]) for row in result.history], dtype=int)
    Fs = np.array(
        [float(row["process_fidelity"]) for row in result.history], dtype=float
    )
    return np.concatenate([[-1], iters]), np.concatenate([[seed_F], Fs])


def _run_one(*, optimizer: str, label: str) -> GrapeResult:
    print("\n" + "=" * 60)
    print(f"  {label}  (optimizer={optimizer!r}, steps={N_STEPS})")
    print("=" * 60)
    exp = _make_exp()
    cfg = _make_config(optimizer=optimizer)
    opt = CRGrapeOptimizer(cfg, exp=exp)
    t0 = time.perf_counter()
    result = opt.run()
    elapsed = time.perf_counter() - t0
    n_eval = len(result.eval_history)
    seed_F = float(result.seed_metrics["process_fidelity"])
    final_F = float(result.final_metrics["process_fidelity"])
    msg = getattr(result.scipy_result, "message", None)
    print(
        f"[{label}] wall={elapsed:.1f}s  n_eval={n_eval}  "
        f"n_hist={len(result.history)}  "
        f"seed_F={seed_F:.6f}  final_F={final_F:.6f}"
    )
    if msg is not None:
        print(f"[{label}] scipy: {msg}")
    return result


def plot_lbfgs_vs_adam(lbfgs: GrapeResult, adam: GrapeResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    it_l, F_l = _fidelity_curve(lbfgs)
    it_a, F_a = _fidelity_curve(adam)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)

    ax = axes[0]
    ax.plot(
        it_l,
        F_l,
        "o-",
        label=f"SciPy L-BFGS + jac (n_hist={len(lbfgs.history)})",
    )
    ax.plot(
        it_a,
        F_a,
        "s-",
        label=f"Adam (n_hist={len(adam.history)})",
    )
    ax.set_xlabel("iteration (−1 = seed)")
    ax.set_ylabel("process fidelity")
    ax.set_title(f"F vs iteration ({N_STEPS} steps)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    ax = axes[1]
    labels = ["L-BFGS + jac", "Adam"]
    finals = [
        float(lbfgs.final_metrics["process_fidelity"]),
        float(adam.final_metrics["process_fidelity"]),
    ]
    nevals = [len(lbfgs.eval_history), len(adam.eval_history)]
    x = np.arange(2)
    bars = ax.bar(x, finals, color=["C0", "C1"], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("final process fidelity")
    ax.set_title("Final F (annotations = n_eval)")
    lo = min(finals)
    hi = max(finals)
    pad = max(0.002, 0.05 * (hi - lo + 1e-12))
    ax.set_ylim(lo - pad, hi + pad)
    for bar, n in zip(bars, nevals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"n_eval={n}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.grid(True, axis="y", alpha=0.3)

    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"\nWrote plot: {path}")


def main() -> None:
    print(
        "Both paths use use_jax_grad=True on dynamiqs.\n"
        "  lbfgs → SciPy minimize(..., jac=True)\n"
        "  adam  → optax Adam (adam_steps=N_STEPS)"
    )
    lbfgs = _run_one(optimizer="lbfgs", label="SciPy L-BFGS-B + JAX jac")
    adam = _run_one(optimizer="adam", label="Adam (optax)")
    plot_lbfgs_vs_adam(lbfgs, adam, PLOT_PATH)

    print("\n--- summary ---")
    for name, r in [("L-BFGS + jac", lbfgs), ("Adam", adam)]:
        print(
            f"  {name}: final_F={r.final_metrics['process_fidelity']:.6f}  "
            f"n_eval={len(r.eval_history)}  n_hist={len(r.history)}"
        )


if __name__ == "__main__":
    main()
