"""Robust GRAPE: repeated runs from slightly perturbed seeds (subprocess-per-run).

Mirrors ``cr_grape_looped.py`` (identical seed, many cycles) but here each
run starts from the same base flat knobs plus small additive noise. Overlays
combined-fidelity convergence curves so you can see whether different seeds
land in the same basin.

Each optimization runs in a **fresh Python subprocess** (same pattern as
``cr_grape_robust_zz_sweep_subprocess.py``) so JAX/XLA memory is released
when the child exits. This avoids mid-loop LLVM OOM / segfaults.

```bash
cd hm_sim   # repo root on PYTHONPATH
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
python -u HM/simulator/two_qubit_simulator/optimization/optimization_tests/cr_grape_robust_seed_perturb_looped.py
```

Edit the knobs below, then run this file directly (do **not** pass ``--worker``
yourself; the parent does that).
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

from HM.simulator.two_qubit_simulator.engine.pulses import seed_flat_knobs_from_calibrated_cr
from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    FIDELITY_METRICS,
    FidelityMetric,
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
    RobustGrapeResult,
    fidelity_metric_label,
)
from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    _annotate_amp_grid,
    amp_grid_plot_tag,
)

USE_JAX_GRAD = True
RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "results", "robust_seed_perturb_looped"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# GRAPE config (same knobs as cr_grape_robust_test.py)
# ---------------------------------------------------------------------------

CR_PULSE_PARAMS = {"amp_mhz": 21, "t_rise_ns": 16, "phase_rad": 0.0}
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 122
N_LINK_SAMPLES = 8
DT_SAMPLE_NS = 1.0

USE_SEED_NPZ = False
SEED_NPZ = os.path.join(
    os.path.dirname(__file__),
    "results",
    "robust_dynamiqs_True",
    "cr_grape_robust_zz0p15MHz_mms_l0p3_20260829_042038.npz",
)

ZZ_SHIFT_MHZ = 0.18
SHIFTS_MHZ = None
WEIGHTS = None

FIDELITY_METRIC: FidelityMetric = "mean_minus_spread"
SPREAD_PENALTY_LAMBDA = 0.3

TARGET_GATE = "zx_m90"
AMP_BOUND_MHZ = 48
AMP_STEP_KHZ = 0.55  # I/Q amp grid; None = continuous (MHz units)
MAXITER = 400
OPTIMIZE = True

# "lbfgs" (default), "adam", or "adan"; adam/adan require USE_JAX_GRAD=True.
OPTIMIZER = "lbfgs"
ADAM_LR = 0.04
ADAM_STEPS = 300
EVOLUTION = "comp"
N_SUB = 16
QUBIT_PAIR = [1, 2]
N_LEVELS = 4
SHOW_PROGRESS = True

# ---------------------------------------------------------------------------
# Perturbation / loop knobs
# ---------------------------------------------------------------------------

N_RUNS = 10
"""Number of perturbed seeds (excluding the unperturbed base when enabled)."""

INCLUDE_BASE_SEED = True
"""If True, run 0 uses the unperturbed base seed before the noisy runs."""

SEED_NOISE_MHZ = 5.0
"""Std dev of additive Gaussian noise on I and Q flat knobs (MHz)."""

RNG_SEED = 42
"""RNG seed for reproducible perturbations."""

SKIP_EXISTING = True
"""If True, skip runs that already have a usable saved NPZ (resume after crash)."""

SUBPROCESS_PER_RUN = True
"""Launch each GRAPE run in a fresh interpreter (recommended for JAX)."""


def _seeds_dir(results_dir: str) -> str:
    return os.path.join(results_dir, "seeds")


def _runs_dir(results_dir: str) -> str:
    return os.path.join(results_dir, "runs")


def _run_dir(results_dir: str, label: str) -> str:
    return os.path.join(_runs_dir(results_dir), label)


def _manifest_path(results_dir: str) -> str:
    return os.path.join(results_dir, "manifest.json")


def _summary_json_path(results_dir: str) -> str:
    return os.path.join(results_dir, "cr_grape_robust_perturbed_looped.json")


def _summary_npz_path(results_dir: str) -> str:
    return os.path.join(results_dir, "cr_grape_robust_perturbed_looped.npz")


def _convergence_png_path(results_dir: str) -> str:
    return os.path.join(results_dir, "cr_grape_robust_perturbed_convergence.png")


def _newest_glob(pattern: str) -> str | None:
    paths = sorted(glob.glob(pattern), key=os.path.getmtime)
    return paths[-1] if paths else None


def _load_base_flat_knobs() -> np.ndarray:
    """Resolve the unperturbed base flat knobs (NPZ or calibrated flat-top)."""
    if USE_SEED_NPZ:
        if not SEED_NPZ or not os.path.isfile(SEED_NPZ):
            raise FileNotFoundError(f"USE_SEED_NPZ=True but file missing: {SEED_NPZ}")
        with np.load(SEED_NPZ, allow_pickle=False) as data:
            knobs = np.asarray(data["flat_knobs_opt"], dtype=complex).reshape(-1)
        print(f"Base seed: {os.path.basename(SEED_NPZ)} ({knobs.size} knobs)", flush=True)
        return knobs

    knobs = seed_flat_knobs_from_calibrated_cr(
        n_flat_knobs=N_FLAT_KNOBS,
        flat_len_ns=FLAT_LEN_NS,
        amp_mhz=CR_PULSE_PARAMS["amp_mhz"],
        phase_rad=CR_PULSE_PARAMS["phase_rad"],
        t_rise_ns=CR_PULSE_PARAMS["t_rise_ns"],
        dt_ns=DT_SAMPLE_NS,
    )
    print(
        f"Base seed: calibrated flat-top "
        f"(amp={CR_PULSE_PARAMS['amp_mhz']} MHz, flat={FLAT_LEN_NS:.0f} ns)",
        flush=True,
    )
    return knobs


def _perturb_flat_knobs(
    base: np.ndarray,
    rng: np.random.Generator,
    noise_mhz: float,
) -> np.ndarray:
    """Add independent Gaussian noise to I and Q parts of flat knobs."""
    noise = noise_mhz * (
        rng.standard_normal(base.shape) + 1j * rng.standard_normal(base.shape)
    )
    return (base + noise).astype(complex)


def _build_config(results_dir: str) -> RobustCRGrapeConfig:
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
        optimizer=OPTIMIZER,
        adam_lr=ADAM_LR,
        adam_steps=ADAM_STEPS,
        evolution=EVOLUTION,
    )


def _build_run_specs(base_knobs: np.ndarray, rng: np.random.Generator) -> list[dict]:
    specs: list[dict] = []
    if INCLUDE_BASE_SEED:
        specs.append({"label": "base", "noise_mhz": 0.0})
    for i in range(N_RUNS):
        specs.append({"label": f"perturb_{i + 1:02d}", "noise_mhz": SEED_NOISE_MHZ})
    return specs


def _save_seed_npz(results_dir: str, label: str, knobs: np.ndarray) -> str:
    seeds_dir = _seeds_dir(results_dir)
    os.makedirs(seeds_dir, exist_ok=True)
    path = os.path.join(seeds_dir, f"{label}_flat_knobs.npz")
    np.savez(path, flat_knobs_seed=knobs)
    return path


def _write_manifest(
    results_dir: str,
    *,
    base_knobs: np.ndarray,
    run_specs: list[dict],
) -> None:
    payload = {
        "perturbation": {
            "n_runs": N_RUNS,
            "include_base_seed": INCLUDE_BASE_SEED,
            "seed_noise_mhz": SEED_NOISE_MHZ,
            "rng_seed": RNG_SEED,
            "base_seed_source": os.path.basename(SEED_NPZ) if USE_SEED_NPZ else "calibrated_flat_top",
        },
        "config": asdict(_build_config(results_dir)),
        "run_specs": run_specs,
        "subprocess_per_run": SUBPROCESS_PER_RUN,
    }
    with open(_manifest_path(results_dir), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _ensure_seeds_on_disk(
    results_dir: str,
    base_knobs: np.ndarray,
    run_specs: list[dict],
    rng: np.random.Generator,
) -> None:
    """Materialize perturbed flat knobs as NPZ files (parent only, no JAX)."""
    for spec in run_specs:
        label = spec["label"]
        seed_path = os.path.join(_seeds_dir(results_dir), f"{label}_flat_knobs.npz")
        if os.path.isfile(seed_path):
            continue
        if label == "base":
            knobs = base_knobs.copy()
        else:
            knobs = _perturb_flat_knobs(base_knobs, rng, SEED_NOISE_MHZ)
        saved = _save_seed_npz(results_dir, label, knobs)
        spec["seed_npz"] = saved


def _run_complete(out_dir: str) -> bool:
    npz = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.npz"))
    if npz is None:
        return False
    try:
        with np.load(npz, allow_pickle=False) as data:
            return "flat_knobs_opt" in data.files and data["flat_knobs_opt"].size > 0
    except OSError:
        return False


def _row_from_saved(out_dir: str, label: str, noise_mhz: float, *, resumed_skip: bool) -> dict:
    jpath = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.json"))
    if jpath is None:
        raise RuntimeError(f"run complete but JSON missing: {out_dir}")
    with open(jpath, encoding="utf-8") as f:
        payload = json.load(f)
    seed_m = payload.get("seed_metrics") or {}
    final_m = payload.get("final_metrics") or {}
    history = payload.get("history") or []
    return {
        "label": label,
        "noise_mhz": noise_mhz,
        "seed_process_fidelity": float(seed_m.get("process_fidelity", float("nan"))),
        "final_process_fidelity": float(final_m.get("process_fidelity", float("nan"))),
        "n_optimizer_iters": len(history),
        "target_gate": payload.get("target_gate", "?"),
        "results_dir": out_dir,
        "json_path": jpath,
        "resumed_skip": resumed_skip,
    }


def _convergence_curve_from_json(json_path: str) -> tuple[np.ndarray, np.ndarray]:
    with open(json_path, encoding="utf-8") as f:
        payload = json.load(f)
    seed_f = float(payload["seed_metrics"]["process_fidelity"])
    history = payload.get("history") or []
    iters = np.array([0] + [h["iteration"] + 1 for h in history], dtype=int)
    f_proc = np.array(
        [seed_f] + [float(h["process_fidelity"]) for h in history],
        dtype=float,
    )
    return iters, f_proc


def _print_summary_table(rows: list[dict]) -> None:
    header = (
        f"{'#':>3}  {'label':>12}  {'seed_F':>8}  {'final_F':>8}  "
        f"{'delta_F':>8}  {'n_iter':>6}  {'noise':>8}  skip"
    )
    print("\n" + header, flush=True)
    print("-" * len(header), flush=True)
    for i, row in enumerate(rows):
        print(
            f"{i:3d}  "
            f"{row['label']:>12}  "
            f"{row['seed_process_fidelity']:8.5f}  "
            f"{row['final_process_fidelity']:8.5f}  "
            f"{row['final_process_fidelity'] - row['seed_process_fidelity']:8.5f}  "
            f"{row['n_optimizer_iters']:6d}  "
            f"{row['noise_mhz']:8.4g}  "
            f"{row.get('resumed_skip', False)!s:>5}",
            flush=True,
        )
    print(flush=True)


def plot_convergence_overlay(
    rows: list[dict],
    out_png: str,
    *,
    config: RobustCRGrapeConfig,
) -> str:
    fig, ax = plt.subplots(figsize=(9, 5.5))
    cmap = plt.cm.tab10(np.linspace(0, 1, max(len(rows), 1)))

    for i, row in enumerate(rows):
        iters, f_proc = _convergence_curve_from_json(row["json_path"])
        ax.plot(
            iters,
            f_proc,
            "o-",
            ms=3,
            lw=1.2,
            color=cmap[i % 10],
            label=(
                f"{row['label']}  F_seed={f_proc[0]:.5f}  "
                f"F_final={f_proc[-1]:.5f}"
            ),
        )

    metric = config.resolved_fidelity_metric()
    target = rows[0].get("target_gate", "?") if rows else "?"
    ax.set_xlabel("optimizer iteration (0 = seed)")
    ax.set_ylabel("combined process fidelity")
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.35)
    ax.legend(fontsize=7, loc="lower right")
    ax.set_title(
        f"Robust GRAPE convergence — perturbed seeds  |  "
        f"target={target}  |  "
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


def _save_summary(
    results_dir: str,
    *,
    config: RobustCRGrapeConfig,
    base_knobs: np.ndarray,
    rows: list[dict],
) -> dict[str, str]:
    os.makedirs(results_dir, exist_ok=True)
    json_path = _summary_json_path(results_dir)
    npz_path = _summary_npz_path(results_dir)
    conv_png = _convergence_png_path(results_dir)

    payload = {
        "config": asdict(config),
        "perturbation": {
            "n_runs": N_RUNS,
            "include_base_seed": INCLUDE_BASE_SEED,
            "seed_noise_mhz": SEED_NOISE_MHZ,
            "rng_seed": RNG_SEED,
            "subprocess_per_run": SUBPROCESS_PER_RUN,
            "base_seed_source": os.path.basename(SEED_NPZ) if USE_SEED_NPZ else "calibrated_flat_top",
        },
        "runs": [
            {k: v for k, v in row.items() if k not in ("json_path",)}
            for row in rows
        ],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    seed_arrays = []
    for row in rows:
        seed_npz = os.path.join(
            _seeds_dir(results_dir), f"{row['label']}_flat_knobs.npz"
        )
        with np.load(seed_npz, allow_pickle=False) as data:
            seed_arrays.append(np.asarray(data["flat_knobs_seed"], dtype=complex).reshape(-1))

    np.savez(
        npz_path,
        base_flat_knobs_real=base_knobs.real,
        base_flat_knobs_imag=base_knobs.imag,
        perturbed_flat_knobs_real=np.stack([k.real for k in seed_arrays]),
        perturbed_flat_knobs_imag=np.stack([k.imag for k in seed_arrays]),
        run_labels=np.array([r["label"] for r in rows], dtype=object),
        final_process_fidelity=np.array(
            [r["final_process_fidelity"] for r in rows], dtype=float
        ),
        seed_process_fidelity=np.array(
            [r["seed_process_fidelity"] for r in rows], dtype=float
        ),
    )

    if rows:
        plot_convergence_overlay(rows, conv_png, config=config)
    return {"json": json_path, "npz": npz_path, "convergence_png": conv_png}


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


def _run_one_inprocess(label: str, seed_npz: str, noise_mhz: float) -> dict:
    """Run a single perturbed GRAPE optimization in this process (--worker)."""
    out_dir = _run_dir(RESULTS_DIR, label)
    os.makedirs(out_dir, exist_ok=True)

    with np.load(seed_npz, allow_pickle=False) as data:
        seed_knobs = np.asarray(data["flat_knobs_seed"], dtype=complex).reshape(-1)

    print(f"\n{'=' * 64}", flush=True)
    print(
        f"label={label}  noise={noise_mhz:g} MHz  |  pid={os.getpid()}",
        flush=True,
    )
    print(f"{'=' * 64}", flush=True)

    config = _build_config(out_dir)
    optimizer = RobustCRGrapeOptimizer(config, flat_knobs_seed=seed_knobs)
    result = optimizer.run()
    result.save(out_dir)
    return _row_from_saved(out_dir, label, noise_mhz, resumed_skip=False)


def _spawn_run_worker(label: str, seed_npz: str, noise_mhz: float) -> None:
    cmd = [
        sys.executable,
        "-u",
        os.path.abspath(__file__),
        "--worker",
        "--label",
        label,
        "--seed-npz",
        seed_npz,
        "--noise-mhz",
        str(float(noise_mhz)),
    ]
    print(
        f"\n>>> subprocess: label={label}  "
        f"(fresh process; exits after this run)",
        flush=True,
    )
    proc = subprocess.run(cmd, env=_subprocess_env(), check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"run worker failed: label={label}  exit_code={proc.returncode}  "
            f"(segfault often shows as -11 / 139)"
        )
    if not _run_complete(_run_dir(RESULTS_DIR, label)):
        raise RuntimeError(
            f"worker exited 0 but no usable NPZ in {_run_dir(RESULTS_DIR, label)}"
        )


def run_perturbed_robust_grape() -> list[dict]:
    """Parent: schedule perturbed runs; each incomplete run uses a subprocess."""
    print("Fidelity metrics available:", flush=True)
    for key, desc in FIDELITY_METRICS.items():
        marker = " <-- selected" if key == FIDELITY_METRIC else ""
        print(f"  {key:18s}  {desc}{marker}", flush=True)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    config = _build_config(RESULTS_DIR)
    base_knobs = _load_base_flat_knobs()
    rng = np.random.default_rng(RNG_SEED)
    run_specs = _build_run_specs(base_knobs, rng)
    _ensure_seeds_on_disk(RESULTS_DIR, base_knobs, run_specs, rng)
    _write_manifest(RESULTS_DIR, base_knobs=base_knobs, run_specs=run_specs)

    print(
        f"\nPerturbed robust GRAPE: {len(run_specs)} run(s)  "
        f"(noise={SEED_NOISE_MHZ} MHz on I/Q, rng={RNG_SEED})",
        flush=True,
    )
    print(
        f"Backend: use_jax_grad={USE_JAX_GRAD}  optimizer={OPTIMIZER!r}  "
        f"n_levels={N_LEVELS}  zz_span={config.zz_span_mhz():.4g} MHz  "
        f"subprocess_per_run={SUBPROCESS_PER_RUN}  skip_existing={SKIP_EXISTING}",
        flush=True,
    )

    rows: list[dict] = []
    n_skipped = 0
    n_ran = 0

    for spec in run_specs:
        label = spec["label"]
        noise_mhz = float(spec["noise_mhz"])
        seed_npz = os.path.join(_seeds_dir(RESULTS_DIR), f"{label}_flat_knobs.npz")
        out_dir = _run_dir(RESULTS_DIR, label)
        os.makedirs(out_dir, exist_ok=True)

        if SKIP_EXISTING and _run_complete(out_dir):
            row = _row_from_saved(out_dir, label, noise_mhz, resumed_skip=True)
            rows.append(row)
            n_skipped += 1
            print(f"\nSKIP label={label}  F_final={row['final_process_fidelity']:.5f}", flush=True)
            _save_summary(RESULTS_DIR, config=config, base_knobs=base_knobs, rows=rows)
            continue

        if SUBPROCESS_PER_RUN:
            _spawn_run_worker(label, seed_npz, noise_mhz)
        else:
            _run_one_inprocess(label, seed_npz, noise_mhz)

        row = _row_from_saved(out_dir, label, noise_mhz, resumed_skip=False)
        rows.append(row)
        n_ran += 1
        _save_summary(RESULTS_DIR, config=config, base_knobs=base_knobs, rows=rows)
        _print_summary_table(rows)

    print(
        f"\nDone. skipped={n_skipped}  ran={n_ran}  "
        f"summary={_summary_json_path(RESULTS_DIR)}",
        flush=True,
    )
    return rows


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Robust GRAPE perturbed-seed loop (subprocess-per-run). "
        "Run with no args for the parent orchestrator."
    )
    p.add_argument(
        "--worker",
        action="store_true",
        help="Internal: run one perturbed GRAPE job then exit.",
    )
    p.add_argument("--label", type=str, default=None)
    p.add_argument("--seed-npz", type=str, default=None)
    p.add_argument("--noise-mhz", type=float, default=0.0)
    return p.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    if args.worker:
        if not args.label or not args.seed_npz:
            raise SystemExit("--worker requires --label and --seed-npz")
        _run_one_inprocess(args.label, args.seed_npz, float(args.noise_mhz))
    else:
        run_perturbed_robust_grape()
