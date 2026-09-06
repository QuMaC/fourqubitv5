"""Compare L-BFGS, Adam, and Adan on the same robust CR GRAPE problem.

Each optimizer runs in a **fresh Python subprocess** so JAX/XLA memory is
released between runs (same pattern as ``cr_grape_robust_zz_sweep_subprocess.py``).

Knobs match ``cr_grape_robust_test.py`` except the ZZ span is 0.3 MHz.
Adam/Adan history is recorded every step (``adam_log_every=1``).

```bash
cd hm_sim
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
python -u HM/simulator/two_qubit_simulator/optimization/optimization_tests/cr_grape_robust_optimizer_compare.py
```

Do **not** pass ``--worker`` yourself; the parent does that.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from dataclasses import asdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    FIRST_ORDER_OPTIMIZERS,
    KNOWN_OPTIMIZERS,
    _annotate_amp_grid,
    _normalize_optimizer,
    amp_grid_plot_tag,
)
from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    FIDELITY_METRICS,
    FidelityMetric,
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
    fidelity_metric_label,
)

USE_JAX_GRAD = True
RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "results", "robust_optimizer_compare"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# GRAPE knobs (same as cr_grape_robust_test.py, ZZ span = 0.3 MHz)
# ---------------------------------------------------------------------------

CR_PULSE_PARAMS = {"amp_mhz": 21, "t_rise_ns": 16, "phase_rad": 0.0}
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 122
N_LINK_SAMPLES = 8

USE_SEED_NPZ = False
SEED_NPZ = os.path.join(
    os.path.dirname(__file__),
    "results",
    "robust_dynamiqs_True",
    "cr_grape_robust_zz0p3MHz_mms_l0p3_20260825_133120.npz",
)

ZZ_SHIFT_MHZ = 0.3
SHIFTS_MHZ = None
WEIGHTS = None

FIDELITY_METRIC: FidelityMetric = "mean_minus_spread"
SPREAD_PENALTY_LAMBDA = 0.3

TARGET_GATE = "zx_m90"
AMP_BOUND_MHZ = 48
AMP_STEP_KHZ = 0.55
MAXITER = 360   
OPTIMIZE = True
ADAM_LR = 0.04
ADAM_STEPS = 360
ADAM_LOG_EVERY = 1
EVOLUTION = "comp"
N_SUB = 16
QUBIT_PAIR = [1, 2]
N_LEVELS = 4
SHOW_PROGRESS = True

OPTIMIZERS = ("lbfgs", "adam", "adan")
SKIP_EXISTING = True

OPT_COLORS = {
    "lbfgs": "tab:blue",
    "adam": "tab:orange",
    "adan": "tab:green",
}


def _run_dir(results_dir: str, optimizer: str) -> str:
    return os.path.join(results_dir, _normalize_optimizer(optimizer))


def _summary_json_path(results_dir: str) -> str:
    return os.path.join(results_dir, "optimizer_compare_summary.json")


def _convergence_png_path(results_dir: str) -> str:
    return os.path.join(results_dir, "optimizer_compare_convergence.png")


def _newest_glob(pattern: str) -> str | None:
    paths = sorted(glob.glob(pattern), key=os.path.getmtime)
    return paths[-1] if paths else None


def _run_complete(out_dir: str) -> bool:
    npz = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.npz"))
    if npz is None:
        return False
    try:
        with np.load(npz, allow_pickle=False) as data:
            return "flat_knobs_opt" in data.files and data["flat_knobs_opt"].size > 0
    except OSError:
        return False


def _load_flat_knobs_seed() -> np.ndarray | None:
    if not USE_SEED_NPZ:
        print(f"Seed: flat-top (USE_SEED_NPZ=False; path kept at {SEED_NPZ!r})", flush=True)
        return None
    if not SEED_NPZ or not os.path.isfile(SEED_NPZ):
        raise FileNotFoundError(f"USE_SEED_NPZ=True but SEED_NPZ not found: {SEED_NPZ}")
    with np.load(SEED_NPZ, allow_pickle=False) as data:
        knobs = np.asarray(data["flat_knobs_opt"], dtype=complex).reshape(-1)
    print(
        f"Seed: warm-start from {os.path.basename(SEED_NPZ)} ({knobs.size} flat knobs)",
        flush=True,
    )
    return knobs


def _build_config(results_dir: str, optimizer: str) -> RobustCRGrapeConfig:
    return RobustCRGrapeConfig(
        flat_len_ns=FLAT_LEN_NS,
        n_flat_knobs=N_FLAT_KNOBS,
        seed_amp_mhz=CR_PULSE_PARAMS["amp_mhz"],
        seed_phase_rad=CR_PULSE_PARAMS["phase_rad"],
        t_rise_ns=CR_PULSE_PARAMS["t_rise_ns"],
        n_link_samples=N_LINK_SAMPLES,
        zz_shift_mhz=ZZ_SHIFT_MHZ,
        shifts_mhz=SHIFTS_MHZ,
        weights=WEIGHTS,
        fidelity_metric=FIDELITY_METRIC,
        spread_penalty_lambda=SPREAD_PENALTY_LAMBDA,
        target_gate=TARGET_GATE,
        amp_bound_mhz=AMP_BOUND_MHZ,
        amp_step_khz=AMP_STEP_KHZ,
        maxiter=MAXITER,
        qubit_pair=list(QUBIT_PAIR),
        n_levels=N_LEVELS,
        n_sub=N_SUB,
        optimize=OPTIMIZE,
        show_progress=SHOW_PROGRESS,
        results_dir=results_dir,
        use_jax_grad=USE_JAX_GRAD,
        optimizer=_normalize_optimizer(optimizer),
        adam_lr=ADAM_LR,
        adam_steps=ADAM_STEPS,
        adam_log_every=ADAM_LOG_EVERY,
        evolution=EVOLUTION,
    )


def _row_from_saved(out_dir: str, optimizer: str, *, resumed_skip: bool) -> dict:
    jpath = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.json"))
    if jpath is None:
        raise RuntimeError(f"run complete but JSON missing: {out_dir}")
    with open(jpath, encoding="utf-8") as f:
        payload = json.load(f)
    seed_m = payload.get("seed_metrics") or {}
    final_m = payload.get("final_metrics") or {}
    history = payload.get("history") or []
    cfg = payload.get("config") or {}
    return {
        "optimizer": _normalize_optimizer(optimizer),
        "seed_process_fidelity": float(seed_m.get("process_fidelity", float("nan"))),
        "final_process_fidelity": float(final_m.get("process_fidelity", float("nan"))),
        "final_process_fidelity_a": float(final_m.get("process_fidelity_a", float("nan"))),
        "final_process_fidelity_b": float(final_m.get("process_fidelity_b", float("nan"))),
        "fidelity_spread": float(final_m.get("fidelity_spread", float("nan"))),
        "n_optimizer_iters": len(history),
        "target_gate": payload.get("target_gate", "?"),
        "config_optimizer": cfg.get("optimizer"),
        "results_dir": out_dir,
        "json_path": jpath,
        "resumed_skip": resumed_skip,
    }


def _convergence_curve_from_json(json_path: str) -> tuple[np.ndarray, np.ndarray]:
    with open(json_path, encoding="utf-8") as f:
        payload = json.load(f)
    seed_f = float(payload["seed_metrics"]["process_fidelity"])
    history = payload.get("history") or []
    iters = np.array([0] + [int(h["iteration"]) + 1 for h in history], dtype=int)
    f_proc = np.array(
        [seed_f] + [float(h["process_fidelity"]) for h in history],
        dtype=float,
    )
    return iters, f_proc


def _print_summary_table(rows: list[dict]) -> None:
    header = (
        f"{'opt':>8}  {'seed_F':>8}  {'final_F':>8}  {'delta_F':>8}  "
        f"{'F_a':>8}  {'F_b':>8}  {'spread':>8}  {'n_hist':>6}  skip"
    )
    print("\n" + header, flush=True)
    print("-" * len(header), flush=True)
    for row in rows:
        print(
            f"{row['optimizer']:>8}  "
            f"{row['seed_process_fidelity']:8.5f}  "
            f"{row['final_process_fidelity']:8.5f}  "
            f"{row['final_process_fidelity'] - row['seed_process_fidelity']:8.5f}  "
            f"{row['final_process_fidelity_a']:8.5f}  "
            f"{row['final_process_fidelity_b']:8.5f}  "
            f"{row['fidelity_spread']:8.5f}  "
            f"{row['n_optimizer_iters']:6d}  "
            f"{row.get('resumed_skip', False)!s:>5}",
            flush=True,
        )
    print(flush=True)


def plot_convergence_overlay(rows: list[dict], out_png: str, *, config: RobustCRGrapeConfig) -> str:
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for row in rows:
        iters, f_proc = _convergence_curve_from_json(row["json_path"])
        name = row["optimizer"]
        dense = len(iters) > 40
        ax.plot(
            iters,
            f_proc,
            "-" if dense else "o-",
            ms=4,
            lw=1.6,
            color=OPT_COLORS.get(name, "0.35"),
            label=(
                f"{name}  F_seed={f_proc[0]:.5f}  "
                f"F_final={f_proc[-1]:.5f}  n={len(iters) - 1}"
            ),
        )
    metric = config.resolved_fidelity_metric()
    ax.set_xlabel("optimizer iteration (0 = seed)")
    ax.set_ylabel("combined process fidelity")
    ax.grid(alpha=0.35)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_title(
        f"Robust GRAPE optimizer compare  |  target={TARGET_GATE}  |  "
        f"ZZ span={config.zz_span_mhz():.4g} MHz  |  "
        f"metric={fidelity_metric_label(metric)}"
        f"{amp_grid_plot_tag(config.amp_step_khz)}"
    )
    _annotate_amp_grid(fig, config.amp_step_khz)
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"Saved {out_png}", flush=True)
    return out_png


def _save_summary(results_dir: str, *, config: RobustCRGrapeConfig, rows: list[dict]) -> None:
    json_path = _summary_json_path(results_dir)
    payload = {
        "config": asdict(config),
        "optimizers": list(OPTIMIZERS),
        "zz_shift_mhz": ZZ_SHIFT_MHZ,
        "rows": rows,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    conv_png = _convergence_png_path(results_dir)
    if rows:
        plot_convergence_overlay(rows, conv_png, config=config)
    print(f"Saved {json_path}", flush=True)


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
    env.setdefault("XLA_PYTHON_CLIENT_ALLOCATOR", "platform")
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    )
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = repo_root if not prev else f"{repo_root}{os.pathsep}{prev}"
    return env


def _run_one_inprocess(optimizer: str) -> dict:
    opt_name = _normalize_optimizer(optimizer)
    out_dir = _run_dir(RESULTS_DIR, opt_name)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n{'=' * 64}", flush=True)
    print(f"optimizer={opt_name}  |  pid={os.getpid()}", flush=True)
    print(f"{'=' * 64}", flush=True)

    config = _build_config(out_dir, opt_name)
    seed_knobs = _load_flat_knobs_seed()
    opt = RobustCRGrapeOptimizer(config, flat_knobs_seed=seed_knobs)
    result = opt.run()
    result.save(out_dir)
    return _row_from_saved(out_dir, opt_name, resumed_skip=False)


def _spawn_worker(optimizer: str) -> None:
    cmd = [
        sys.executable,
        "-u",
        os.path.abspath(__file__),
        "--worker",
        "--optimizer",
        _normalize_optimizer(optimizer),
    ]
    print(
        f"\n>>> subprocess: optimizer={optimizer}  "
        f"(fresh process; exits after this run)",
        flush=True,
    )
    proc = subprocess.run(cmd, env=_subprocess_env(), check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"worker failed: optimizer={optimizer}  exit_code={proc.returncode}  "
            f"(segfault often shows as -11 / 139)"
        )
    if not _run_complete(_run_dir(RESULTS_DIR, optimizer)):
        raise RuntimeError(
            f"worker exited 0 but no usable NPZ in {_run_dir(RESULTS_DIR, optimizer)}"
        )


def run_optimizer_compare() -> list[dict]:
    names = [_normalize_optimizer(n) for n in OPTIMIZERS]
    for name in names:
        if name not in KNOWN_OPTIMIZERS:
            raise ValueError(f"unknown optimizer {name!r}; use one of {KNOWN_OPTIMIZERS}")
        if name in FIRST_ORDER_OPTIMIZERS and not USE_JAX_GRAD:
            raise ValueError(f"optimizer={name!r} requires USE_JAX_GRAD=True")

    print("Fidelity metrics available:", flush=True)
    for key, desc in FIDELITY_METRICS.items():
        marker = " <-- selected" if key == FIDELITY_METRIC else ""
        print(f"  {key:18s}  {desc}{marker}", flush=True)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    config = _build_config(RESULTS_DIR, "lbfgs")
    print(
        f"\nOptimizer compare: {names}  |  ZZ span={config.zz_span_mhz():.4g} MHz  "
        f"|  flat={FLAT_LEN_NS:.0f} ns  knobs={N_FLAT_KNOBS}  n_levels={N_LEVELS}",
        flush=True,
    )
    print(
        f"use_jax_grad={USE_JAX_GRAD}  maxiter={MAXITER}  "
        f"adam_steps={ADAM_STEPS}  adam_log_every={ADAM_LOG_EVERY}  "
        f"skip_existing={SKIP_EXISTING}",
        flush=True,
    )

    rows: list[dict] = []
    failures: list[str] = []
    n_skipped = 0
    n_ran = 0

    for name in names:
        out_dir = _run_dir(RESULTS_DIR, name)
        os.makedirs(out_dir, exist_ok=True)
        if SKIP_EXISTING and _run_complete(out_dir):
            row = _row_from_saved(out_dir, name, resumed_skip=True)
            rows.append(row)
            n_skipped += 1
            print(
                f"\nSKIP optimizer={name}  F_final={row['final_process_fidelity']:.5f}",
                flush=True,
            )
            _save_summary(RESULTS_DIR, config=config, rows=rows)
            continue
        try:
            _spawn_worker(name)
            row = _row_from_saved(out_dir, name, resumed_skip=False)
            rows.append(row)
            n_ran += 1
            _save_summary(RESULTS_DIR, config=config, rows=rows)
            _print_summary_table(rows)
        except RuntimeError as exc:
            failures.append(f"{name}: {exc}")
            print(f"\nFAILED optimizer={name}: {exc}", flush=True)

    _print_summary_table(rows)
    print(
        f"Done. skipped={n_skipped}  ran={n_ran}  failed={len(failures)}  "
        f"Summary: {_summary_json_path(RESULTS_DIR)}",
        flush=True,
    )
    if failures:
        raise RuntimeError("one or more optimizer workers failed:\n  " + "\n  ".join(failures))
    return rows


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Compare L-BFGS / Adam / Adan on robust CR GRAPE. "
        "Run with no args for the parent orchestrator."
    )
    p.add_argument(
        "--worker",
        action="store_true",
        help="Internal: run a single optimizer then exit (parent sets this).",
    )
    p.add_argument("--optimizer", type=str, default=None)
    return p.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    if args.worker:
        if not args.optimizer:
            raise SystemExit("--worker requires --optimizer")
        _run_one_inprocess(args.optimizer)
    else:
        run_optimizer_compare()
