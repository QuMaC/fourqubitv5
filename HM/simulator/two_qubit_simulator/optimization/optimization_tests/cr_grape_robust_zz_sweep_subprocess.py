"""Robust GRAPE ZZ-span sweep (subprocess-per-span) — same knobs as zz_sweep.

Identical to ``cr_grape_robust_zz_sweep.py`` except each ``(zz, mode)`` run is
executed in a **fresh Python process**. When that child exits, JAX/XLA memory
is released to the OS, which avoids the mid-sweep LLVM OOM / segfault seen
when many spans share one long-lived process.

Warm-chain seeds still work: the parent reloads ``flat_knobs_opt`` from the
previous warm span's saved ``.npz`` on disk before launching the next warm
child.

Resume / crash recovery
-----------------------
Same as the non-subprocess script: ``SKIP_EXISTING = True`` skips spans that
already have a usable ``.npz``. Empty mid-crash dirs are re-run.

```bash
cd Hari_6_qubit/fourqubitv5
tmux new -s zz_sweep_sub
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
PYTHONPATH=. /path/to/envs/qumac-env/bin/python -u \\
  HM/simulator/two_qubit_simulator/optimization/optimization_tests/cr_grape_robust_zz_sweep_subprocess.py
```

Edit the knobs below, then run this file directly (do **not** pass
``--worker`` yourself; the parent does that).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from typing import Literal

import numpy as np

from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    FIDELITY_METRICS,
    FidelityMetric,
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
    RobustGrapeResult,
)

# Top results folder name. Use a distinct name (e.g. suffix) for parallel runs
# so summary.json / span dirs do not clash with another live sweep.
RESULTS_NAME = "robust_zz_sweep_dynamiqs"
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", RESULTS_NAME)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Knobs — edit these (keep in sync with cr_grape_robust_zz_sweep.py)
# ---------------------------------------------------------------------------

# Seed pulse (same convention as cr_grape_robust_test.py).
CR_PULSE_PARAMS = {"amp_mhz": 21.0, "t_rise_ns": 16, "phase_rad": 0.0}
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 61
N_LINK_SAMPLES = 8

# Full ZZ span sweep (kHz). Each value is zz_shift; cases are +/- span/2.
ZZ_SPANS_KHZ = list(range(0, 301, 50))  # 0, 50, ..., 300

# "flat" | "warm" | "both"
SEED_MODES: Literal["flat", "warm", "both"] = "both"

WEIGHTS = (0.5, 0.5)
FIDELITY_METRIC: FidelityMetric = "mean_minus_spread"
SPREAD_PENALTY_LAMBDA = 0.3

TARGET_GATE = "zx_m90"  # inferred from seed at each run; or "zx_90" / "zx_m90"
AMP_BOUND_MHZ = 48.0
MAXITER = 180
OPTIMIZE = True
QUBIT_PAIR = [1, 2]
N_LEVELS = 3

# Backend: dynamiqs (default) vs QuTiP FD.
USE_JAX_GRAD = True
# "lbfgs" (default) or "adam"; adam requires USE_JAX_GRAD=True.
OPTIMIZER = "lbfgs"
ADAM_LR = 0.02
ADAM_STEPS = 200
EVOLUTION = "comp"  # robust JAX path locks "comp"
# Passed into CR_len_sweep. Phase 5/6 smoke used 14; QuTiP FD often used 2–4.
N_SUB = 16
SHOW_PROGRESS = True

# If True, skip spans that already have a completed save (resume after crash).
SKIP_EXISTING = True


def _resolve_modes(seed_modes: str) -> list[str]:
    key = str(seed_modes).strip().lower()
    if key == "flat":
        return ["flat"]
    if key == "warm":
        return ["warm"]
    if key == "both":
        return ["flat", "warm"]
    raise ValueError(f"SEED_MODES must be flat|warm|both, got {seed_modes!r}")


def _span_dir(results_dir: str, mode: str, zz_khz: int) -> str:
    return os.path.join(results_dir, mode, f"zz_{zz_khz:03d}_kHz")


def _summary_path(results_dir: str) -> str:
    return os.path.join(results_dir, "summary.json")


def _newest_glob(pattern: str) -> str | None:
    paths = sorted(glob.glob(pattern), key=os.path.getmtime)
    return paths[-1] if paths else None


def _span_complete(out_dir: str) -> bool:
    """True if this span dir has a usable saved NPZ (not an empty mid-crash dir)."""
    npz = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.npz"))
    if npz is None:
        return False
    try:
        with np.load(npz, allow_pickle=False) as data:
            return "flat_knobs_opt" in data.files and data["flat_knobs_opt"].size > 0
    except OSError:
        return False


def _load_flat_knobs_opt(out_dir: str) -> np.ndarray | None:
    npz = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.npz"))
    if npz is None:
        return None
    with np.load(npz, allow_pickle=False) as data:
        if "flat_knobs_opt" not in data.files:
            return None
        return np.asarray(data["flat_knobs_opt"], dtype=complex).reshape(-1)


def _row_from_saved(out_dir: str, zz_khz: int, mode: str) -> dict | None:
    """Rebuild a summary row from the newest JSON in ``out_dir``."""
    jpath = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.json"))
    if jpath is None:
        return None
    with open(jpath, encoding="utf-8") as f:
        payload = json.load(f)
    m = payload.get("final_metrics") or {}
    seed = payload.get("seed_metrics") or {}
    fa = float(m.get("process_fidelity_a", float("nan")))
    fb = float(m.get("process_fidelity_b", float("nan")))
    return {
        "zz_span_khz": int(zz_khz),
        "zz_span_mhz": float(zz_khz) / 1000.0,
        "shifts_mhz": list(payload.get("shifts_mhz") or []),
        "mode": mode,
        "target_gate": payload.get("target_gate", "?"),
        "process_fidelity": float(m.get("process_fidelity", float("nan"))),
        "process_fidelity_a": fa,
        "process_fidelity_b": fb,
        "fidelity_spread": float(m.get("fidelity_spread", abs(fa - fb))),
        "seed_process_fidelity": float(seed.get("process_fidelity", float("nan"))),
        "results_dir": out_dir,
        "resumed_skip": True,
    }


def _write_summary(results_dir: str, rows: list[dict]) -> None:
    path = _summary_path(results_dir)
    payload = {
        "zz_spans_khz": list(ZZ_SPANS_KHZ),
        "seed_modes": SEED_MODES,
        "config": {
            "amp_mhz": CR_PULSE_PARAMS["amp_mhz"],
            "flat_len_ns": FLAT_LEN_NS,
            "n_flat_knobs": N_FLAT_KNOBS,
            "n_link_samples": N_LINK_SAMPLES,
            "fidelity_metric": FIDELITY_METRIC,
            "spread_penalty_lambda": SPREAD_PENALTY_LAMBDA,
            "weights": list(WEIGHTS),
            "amp_bound_mhz": AMP_BOUND_MHZ,
            "maxiter": MAXITER,
            "optimize": OPTIMIZE,
            "target_gate": TARGET_GATE,
            "qubit_pair": list(QUBIT_PAIR),
            "n_levels": N_LEVELS,
            "n_sub": N_SUB,
            "use_jax_grad": USE_JAX_GRAD,
            "optimizer": OPTIMIZER,
            "adam_lr": ADAM_LR,
            "adam_steps": ADAM_STEPS,
            "evolution": EVOLUTION,
            "skip_existing": SKIP_EXISTING,
            "results_name": RESULTS_NAME,
            "subprocess_per_span": True,
        },
        "runs": rows,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Updated {path}", flush=True)


def _print_table(rows: list[dict]) -> None:
    if not rows:
        return
    print("\nZZ-span sweep summary", flush=True)
    print(
        f"{'zz_kHz':>7}  {'mode':>5}  {'F_comb':>9}  {'F_a':>9}  "
        f"{'F_b':>9}  {'|dF|':>9}  target",
        flush=True,
    )
    print("-" * 72, flush=True)
    for r in rows:
        print(
            f"{r['zz_span_khz']:7d}  {r['mode']:>5}  "
            f"{r['process_fidelity']:9.5f}  "
            f"{r['process_fidelity_a']:9.5f}  "
            f"{r['process_fidelity_b']:9.5f}  "
            f"{r['fidelity_spread']:9.5f}  "
            f"{r.get('target_gate', '?')}",
            flush=True,
        )


def _row_from_result(
    *,
    zz_khz: int,
    mode: str,
    result: RobustGrapeResult,
    out_dir: str,
) -> dict:
    m = result.final_metrics
    return {
        "zz_span_khz": int(zz_khz),
        "zz_span_mhz": float(zz_khz) / 1000.0,
        "shifts_mhz": list(result.shifts_mhz),
        "mode": mode,
        "target_gate": result.target_gate,
        "process_fidelity": float(m["process_fidelity"]),
        "process_fidelity_a": float(m["process_fidelity_a"]),
        "process_fidelity_b": float(m["process_fidelity_b"]),
        "fidelity_spread": float(
            m.get(
                "fidelity_spread",
                abs(m["process_fidelity_a"] - m["process_fidelity_b"]),
            )
        ),
        "seed_process_fidelity": float(result.seed_metrics["process_fidelity"]),
        "results_dir": out_dir,
    }


def _make_config(zz_span_mhz: float, results_dir: str) -> RobustCRGrapeConfig:
    return RobustCRGrapeConfig(
        flat_len_ns=FLAT_LEN_NS,
        n_flat_knobs=N_FLAT_KNOBS,
        seed_amp_mhz=CR_PULSE_PARAMS["amp_mhz"],
        seed_phase_rad=CR_PULSE_PARAMS["phase_rad"],
        t_rise_ns=CR_PULSE_PARAMS["t_rise_ns"],
        n_link_samples=N_LINK_SAMPLES,
        zz_shift_mhz=zz_span_mhz,
        shifts_mhz=None,
        weights=WEIGHTS,
        fidelity_metric=FIDELITY_METRIC,
        spread_penalty_lambda=SPREAD_PENALTY_LAMBDA,
        target_gate=TARGET_GATE,
        amp_bound_mhz=AMP_BOUND_MHZ,
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


def _run_one_span_inprocess(
    zz_khz: int,
    mode: str,
    seed_npz: str | None,
) -> dict:
    """Run a single span inside this process (used by --worker children)."""
    zz_mhz = float(zz_khz) / 1000.0
    out_dir = _span_dir(RESULTS_DIR, mode, zz_khz)
    os.makedirs(out_dir, exist_ok=True)

    seed_override = None
    if seed_npz is not None:
        with np.load(seed_npz, allow_pickle=False) as data:
            seed_override = np.asarray(data["flat_knobs_opt"], dtype=complex).reshape(
                -1
            )

    print(f"\n{'=' * 64}", flush=True)
    print(
        f"ZZ span = {zz_khz} kHz ({zz_mhz:.4g} MHz)  |  mode={mode}  |  "
        f"seed={'warm' if seed_override is not None else 'flat-top'}  |  "
        f"pid={os.getpid()}",
        flush=True,
    )
    print(f"{'=' * 64}", flush=True)

    config = _make_config(zz_mhz, out_dir)
    optimizer = RobustCRGrapeOptimizer(config, flat_knobs_seed=seed_override)
    result = optimizer.run()
    result.save(out_dir)
    return _row_from_result(
        zz_khz=zz_khz, mode=mode, result=result, out_dir=out_dir
    )


def _spawn_span_worker(
    zz_khz: int,
    mode: str,
    seed_npz: str | None,
) -> None:
    """Launch one fresh interpreter for a single span; wait until it exits."""
    cmd = [
        sys.executable,
        "-u",
        os.path.abspath(__file__),
        "--worker",
        "--zz-khz",
        str(int(zz_khz)),
        "--mode",
        mode,
    ]
    if seed_npz is not None:
        cmd.extend(["--seed-npz", seed_npz])

    env = os.environ.copy()
    # Soften JAX allocator spikes in each short-lived child.
    env.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
    env.setdefault("XLA_PYTHON_CLIENT_ALLOCATOR", "platform")
    # Ensure HM package imports resolve the same way as an interactive run.
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    )
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        repo_root if not prev else f"{repo_root}{os.pathsep}{prev}"
    )

    print(
        f"\n>>> subprocess: zz={zz_khz} mode={mode}  "
        f"(fresh process; exits after this span)",
        flush=True,
    )
    proc = subprocess.run(cmd, env=env, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"span worker failed: zz={zz_khz} mode={mode}  "
            f"exit_code={proc.returncode}  (segfault often shows as -11 / 139)"
        )
    if not _span_complete(_span_dir(RESULTS_DIR, mode, zz_khz)):
        raise RuntimeError(
            f"span worker exited 0 but no usable NPZ in "
            f"{_span_dir(RESULTS_DIR, mode, zz_khz)}"
        )


def run_robust_zz_sweep() -> list[dict]:
    """Parent: schedule spans; each incomplete span runs in a subprocess."""
    modes = _resolve_modes(SEED_MODES)
    print("Fidelity metrics available:", flush=True)
    for key, desc in FIDELITY_METRICS.items():
        marker = " <-- selected" if key == FIDELITY_METRIC else ""
        print(f"  {key:18s}  {desc}{marker}", flush=True)

    print(
        f"\nZZ span sweep: {ZZ_SPANS_KHZ[0]}..{ZZ_SPANS_KHZ[-1]} kHz "
        f"(step {ZZ_SPANS_KHZ[1] - ZZ_SPANS_KHZ[0] if len(ZZ_SPANS_KHZ) > 1 else 0} kHz)",
        flush=True,
    )
    print(
        f"SEED_MODES={SEED_MODES} -> branches {modes}  |  "
        f"amp={CR_PULSE_PARAMS['amp_mhz']} MHz  flat={FLAT_LEN_NS:.0f} ns  "
        f"knobs={N_FLAT_KNOBS}  n_sub={N_SUB}  "
        f"use_jax_grad={USE_JAX_GRAD}  optimizer={OPTIMIZER!r}  "
        f"skip_existing={SKIP_EXISTING}  results={RESULTS_NAME}  "
        f"subprocess_per_span=True",
        flush=True,
    )
    print(
        "Note: zz_shift is the FULL span; robust cases are +/- span/2. "
        "Warm chain: span 0 = flat-top, later spans inherit previous opt knobs "
        "(via saved NPZ across subprocesses).",
        flush=True,
    )

    # Preflight: what will be skipped vs run.
    todo: list[tuple[int, str]] = []
    for zz_khz in ZZ_SPANS_KHZ:
        for mode in modes:
            out_dir = _span_dir(RESULTS_DIR, mode, zz_khz)
            if SKIP_EXISTING and _span_complete(out_dir):
                print(f"  SKIP  zz={zz_khz:3d} mode={mode}  ({out_dir})", flush=True)
            else:
                status = "empty/incomplete" if os.path.isdir(out_dir) else "new"
                print(f"  RUN   zz={zz_khz:3d} mode={mode}  [{status}]", flush=True)
                todo.append((zz_khz, mode))
    print(f"\nPlanned runs this session: {len(todo)}", flush=True)

    rows: list[dict] = []
    # Warm branch: path to previous completed warm NPZ (disk-backed across kids).
    warm_prev_npz: str | None = None
    n_skipped = 0
    n_ran = 0

    for zz_khz in ZZ_SPANS_KHZ:
        for mode in modes:
            out_dir = _span_dir(RESULTS_DIR, mode, zz_khz)
            os.makedirs(out_dir, exist_ok=True)

            if SKIP_EXISTING and _span_complete(out_dir):
                row = _row_from_saved(out_dir, zz_khz, mode)
                if row is None:
                    raise RuntimeError(
                        f"span marked complete but JSON missing: {out_dir}"
                    )
                rows.append(row)
                n_skipped += 1
                if mode == "warm":
                    npz = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.npz"))
                    if npz is None:
                        raise RuntimeError(
                            f"warm span complete but NPZ missing: {out_dir}"
                        )
                    warm_prev_npz = npz
                    print(
                        f"\nSKIP zz={zz_khz} mode=warm  "
                        f"Fc={row['process_fidelity']:.5f}  "
                        f"(warm seed chain continues from this opt)",
                        flush=True,
                    )
                else:
                    print(
                        f"\nSKIP zz={zz_khz} mode=flat  "
                        f"Fc={row['process_fidelity']:.5f}",
                        flush=True,
                    )
                _write_summary(RESULTS_DIR, rows)
                continue

            seed_npz = warm_prev_npz if mode == "warm" else None
            _spawn_span_worker(zz_khz, mode, seed_npz)

            row = _row_from_saved(out_dir, zz_khz, mode)
            if row is None:
                raise RuntimeError(f"worker finished but JSON missing: {out_dir}")
            # Mark as a fresh run (not a resume skip).
            row = {**row, "resumed_skip": False}
            rows.append(row)
            n_ran += 1
            _write_summary(RESULTS_DIR, rows)
            _print_table(rows)

            if mode == "warm":
                npz = _newest_glob(os.path.join(out_dir, "cr_grape_robust_*.npz"))
                if npz is None:
                    raise RuntimeError(f"warm worker missing NPZ: {out_dir}")
                warm_prev_npz = npz

    print(
        f"\nDone. skipped={n_skipped}  ran={n_ran}  "
        f"Summary: {_summary_path(RESULTS_DIR)}",
        flush=True,
    )
    return rows


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Robust ZZ sweep (subprocess-per-span). "
        "Run with no args for the parent orchestrator."
    )
    p.add_argument(
        "--worker",
        action="store_true",
        help="Internal: run a single span then exit (parent sets this).",
    )
    p.add_argument("--zz-khz", type=int, default=None)
    p.add_argument("--mode", type=str, choices=("flat", "warm"), default=None)
    p.add_argument(
        "--seed-npz",
        type=str,
        default=None,
        help="Optional NPZ with flat_knobs_opt for warm-start.",
    )
    return p.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    if args.worker:
        if args.zz_khz is None or args.mode is None:
            raise SystemExit("--worker requires --zz-khz and --mode")
        _run_one_span_inprocess(args.zz_khz, args.mode, args.seed_npz)
    else:
        run_robust_zz_sweep()
