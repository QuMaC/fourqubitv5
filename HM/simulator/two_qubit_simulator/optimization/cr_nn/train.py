"""Checkpointed Adan training for the robust echoed-CR neural pulse model."""

from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import sys
import time
from typing import Callable

import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np
import optax

from .checkpoint import (
    config_from_checkpoint,
    load_checkpoint,
    save_checkpoint,
)
from .config import CRNNConfig
from .cost import BatchMetrics, batch_loss, build_physics
from .model import CRPulseMLP, count_parameters
from .sampling import (
    TrainingBatch,
    duration_for_step,
    duration_order,
    sample_batch,
)


class PauseController:
    """Turn signals into a checkpoint request handled between training steps."""

    def __init__(self) -> None:
        self.requested = False
        self.reason = ""
        self._sigint_count = 0

    def install(self) -> None:
        signal.signal(signal.SIGINT, self._handle)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._handle)

    def _handle(self, signum, _frame) -> None:
        name = signal.Signals(signum).name
        if signum == signal.SIGINT:
            self._sigint_count += 1
            if self._sigint_count > 1:
                raise KeyboardInterrupt
        self.requested = True
        self.reason = name
        print(
            f"\n{name} received. Training will checkpoint after the current step. "
            "Press Ctrl+C again to interrupt immediately.",
            flush=True,
        )


def make_optimizer(config: CRNNConfig):
    if config.optimizer.lower() != "adan":
        raise ValueError("the first CR NN training path is locked to Adan")
    return optax.adan(
        learning_rate=float(config.learning_rate),
        weight_decay=float(config.weight_decay),
    )


def make_train_step(
    *,
    duration_ns: int,
    physics,
    config: CRNNConfig,
    optimizer,
) -> Callable:
    """Create one compiled update whose timeline length is static."""
    duration = int(duration_ns)

    @eqx.filter_jit
    def train_step(model, optimizer_state, batch: TrainingBatch):
        def loss_fn(current_model):
            return batch_loss(
                current_model,
                batch,
                duration_ns=duration,
                physics=physics,
                config=config,
            )

        (loss, metrics), grads = eqx.filter_value_and_grad(
            loss_fn,
            has_aux=True,
        )(model)
        params = eqx.filter(model, eqx.is_inexact_array)
        updates, optimizer_state = optimizer.update(
            grads,
            optimizer_state,
            params,
        )
        model = eqx.apply_updates(model, updates)
        grad_norm = optax.global_norm(grads)
        return model, optimizer_state, loss, metrics, grad_norm

    return train_step


def _metrics_dict(
    *,
    step: int,
    duration_ns: int,
    metrics: BatchMetrics,
    grad_norm,
    elapsed_s: float,
) -> dict[str, float | int | str]:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "step": int(step),
        "duration_ns": int(duration_ns),
        "loss": float(np.asarray(metrics.loss)),
        "fidelity_combined": float(np.asarray(metrics.fidelity_combined)),
        "fidelity_min": float(np.asarray(metrics.fidelity_min)),
        "fidelity_spread": float(np.asarray(metrics.fidelity_spread)),
        "leakage": float(np.asarray(metrics.leakage)),
        "grad_norm": float(np.asarray(grad_norm)),
        "elapsed_s": float(elapsed_s),
    }


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def _write_run_config(output_dir: Path, config: CRNNConfig) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "config.json"
    tmp = output_dir / ".config.json.tmp"
    tmp.write_text(
        json.dumps(config.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    os.replace(tmp, path)


def _pause_file_requested(output_dir: Path) -> bool:
    pause_file = output_dir / "PAUSE"
    if not pause_file.exists():
        return False
    pause_file.unlink()
    return True


def _build_new_state(config: CRNNConfig):
    root_key = jax.random.PRNGKey(config.random_seed)
    model_key, train_key = jax.random.split(root_key)
    model = CRPulseMLP(config, key=model_key)
    optimizer = make_optimizer(config)
    optimizer_state = optimizer.init(eqx.filter(model, eqx.is_inexact_array))
    return model, optimizer, optimizer_state, train_key, 0, duration_order(config)


def _build_resumed_state(
    checkpoint_path: str | Path,
    config: CRNNConfig,
):
    model_key = jax.random.PRNGKey(config.random_seed)
    model_template = CRPulseMLP(config, key=model_key)
    optimizer = make_optimizer(config)
    optimizer_state_template = optimizer.init(
        eqx.filter(model_template, eqx.is_inexact_array)
    )
    model, optimizer_state, train_key, metadata, resolved = load_checkpoint(
        checkpoint_path,
        model_template=model_template,
        optimizer_state_template=optimizer_state_template,
    )
    order = tuple(int(v) for v in metadata["duration_order"])
    return (
        model,
        optimizer,
        optimizer_state,
        train_key,
        int(metadata["global_step"]),
        order,
        metadata,
        resolved,
    )


def train(
    config: CRNNConfig,
    *,
    output_dir: str | Path,
    resume: str | Path | None = None,
    fixed_duration_ns: int | None = None,
    warm_all_durations: bool = False,
) -> Path:
    """Train until config.train_steps or a clean pause request."""
    config.validate()
    output = Path(output_dir).expanduser().resolve()
    _write_run_config(output, config)

    cache_dir = output / ".jax_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    jax.config.update("jax_compilation_cache_dir", str(cache_dir))
    print(
        f"JAX backend={jax.default_backend()} devices={jax.devices()} "
        f"x64={jax.config.x64_enabled}",
        flush=True,
    )

    physics = build_physics(config)
    if resume is None:
        (
            model,
            optimizer,
            optimizer_state,
            train_key,
            global_step,
            order,
        ) = _build_new_state(config)
        print("Starting a new training run.", flush=True)
    else:
        (
            model,
            optimizer,
            optimizer_state,
            train_key,
            global_step,
            order,
            resume_metadata,
            resolved,
        ) = _build_resumed_state(resume, config)
        print(f"Resumed {resolved} at step {global_step}.", flush=True)
        stored_fixed = resume_metadata["fixed_duration_ns"]
        if fixed_duration_ns is None and stored_fixed is not None:
            fixed_duration_ns = int(stored_fixed)
        elif fixed_duration_ns is not None and (
            stored_fixed is None
            or int(fixed_duration_ns) != int(stored_fixed)
        ):
            raise ValueError(
                "fixed duration differs from the checkpoint: "
                f"{fixed_duration_ns} != {stored_fixed}"
            )

    print(
        f"model=4 -> {config.hidden_layers}x{config.hidden_width} -> "
        f"{config.output_size}; parameters={count_parameters(model):,}",
        flush=True,
    )
    if fixed_duration_ns is not None:
        fixed_duration_ns = int(fixed_duration_ns)
        if fixed_duration_ns not in config.durations_ns:
            raise ValueError(
                f"fixed duration {fixed_duration_ns} not in {config.durations_ns}"
            )

    kernels = {
        int(duration): make_train_step(
            duration_ns=int(duration),
            physics=physics,
            config=config,
            optimizer=optimizer,
        )
        for duration in config.durations_ns
    }

    if warm_all_durations:
        print("Compiling all 13 duration kernels with one update each.", flush=True)
        warm_key = train_key
        for duration in config.durations_ns:
            warm_key, batch = sample_batch(
                config,
                warm_key,
                duration_ns=int(duration),
            )
            # Execute and discard the update. Warming kernels must not alter
            # the checkpointed optimization trajectory.
            kernels[int(duration)](
                model,
                optimizer_state,
                batch,
            )
        print("All duration kernels compiled.", flush=True)

    controller = PauseController()
    controller.install()
    metrics_path = output / "metrics.jsonl"
    last_metrics: dict[str, float] = {}
    started = time.monotonic()
    paused = False
    pause_reason = ""

    try:
        while global_step < config.train_steps:
            if _pause_file_requested(output):
                paused = True
                pause_reason = "PAUSE file"
                break

            duration = (
                fixed_duration_ns
                if fixed_duration_ns is not None
                else duration_for_step(order, global_step)
            )
            next_key, batch = sample_batch(
                config,
                train_key,
                duration_ns=duration,
            )
            step_started = time.monotonic()
            (
                next_model,
                next_optimizer_state,
                _loss,
                metrics,
                grad_norm,
            ) = kernels[duration](model, optimizer_state, batch)

            # Commit the PRNG and train state only after a complete update.
            model = next_model
            optimizer_state = next_optimizer_state
            train_key = next_key
            global_step += 1
            record = _metrics_dict(
                step=global_step,
                duration_ns=duration,
                metrics=metrics,
                grad_norm=grad_norm,
                elapsed_s=time.monotonic() - step_started,
            )
            last_metrics = {
                key: float(value)
                for key, value in record.items()
                if key
                in {
                    "loss",
                    "fidelity_combined",
                    "fidelity_min",
                    "fidelity_spread",
                    "leakage",
                    "grad_norm",
                }
            }
            if global_step == 1 or global_step % config.log_every == 0:
                _append_jsonl(metrics_path, record)
                print(
                    f"step={global_step}/{config.train_steps} T={duration} ns "
                    f"F={record['fidelity_combined']:.8f} "
                    f"Fmin={record['fidelity_min']:.8f} "
                    f"spread={record['fidelity_spread']:.3e} "
                    f"grad={record['grad_norm']:.3e} "
                    f"dt={record['elapsed_s']:.2f}s",
                    flush=True,
                )
            if global_step % config.checkpoint_every == 0:
                saved = save_checkpoint(
                    output,
                    global_step=global_step,
                    model=model,
                    optimizer_state=optimizer_state,
                    rng_key=train_key,
                    config=config,
                    duration_order=order,
                    last_metrics=last_metrics,
                    fixed_duration_ns=fixed_duration_ns,
                )
                print(f"checkpoint={saved}", flush=True)

            if controller.requested:
                paused = True
                pause_reason = controller.reason
                break
    except KeyboardInterrupt:
        paused = True
        pause_reason = "immediate KeyboardInterrupt"

    saved = save_checkpoint(
        output,
        global_step=global_step,
        model=model,
        optimizer_state=optimizer_state,
        rng_key=train_key,
        config=config,
        duration_order=order,
        last_metrics=last_metrics,
        fixed_duration_ns=fixed_duration_ns,
    )
    total_s = time.monotonic() - started
    status = "paused" if paused else "completed"
    print(
        f"Training {status} at step {global_step}; checkpoint={saved}; "
        f"wall={total_s:.1f}s"
        + (f"; reason={pause_reason}" if pause_reason else ""),
        flush=True,
    )
    return saved


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="HM/simulator/two_qubit_simulator/optimization/"
        "optimization_tests/results/cr_nn",
    )
    parser.add_argument("--resume", default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--learning-rate", type=float, default=None)
    parser.add_argument("--checkpoint-every", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=None)
    parser.add_argument("--fixed-duration", type=int, default=None)
    parser.add_argument("--warm-all-durations", action="store_true")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="full 5x1024 model, two steps, batch one",
    )
    parser.add_argument(
        "--tiny-smoke",
        action="store_true",
        help="2x32 wiring model, two steps, batch one",
    )
    return parser


def _config_from_args(args: argparse.Namespace) -> CRNNConfig:
    if args.resume is not None:
        config = config_from_checkpoint(args.resume)
    else:
        config = CRNNConfig()

    changes = {}
    for arg_name, field_name in (
        ("steps", "train_steps"),
        ("batch_size", "batch_size"),
        ("learning_rate", "learning_rate"),
        ("checkpoint_every", "checkpoint_every"),
        ("log_every", "log_every"),
    ):
        value = getattr(args, arg_name)
        if value is not None:
            changes[field_name] = value
    if args.smoke:
        changes.setdefault("train_steps", 2)
        changes.setdefault("batch_size", 1)
        changes.setdefault("checkpoint_every", 1)
        changes.setdefault("log_every", 1)
    if args.tiny_smoke:
        changes.setdefault("train_steps", 2)
        changes.setdefault("batch_size", 1)
        changes.setdefault("checkpoint_every", 1)
        changes.setdefault("log_every", 1)
        changes.update(hidden_width=32, hidden_layers=2)
    config = replace(config, **changes)
    config.validate()
    return config


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.smoke and args.tiny_smoke:
        raise SystemExit("choose at most one of --smoke and --tiny-smoke")
    config = _config_from_args(args)
    train(
        config,
        output_dir=args.output_dir,
        resume=args.resume,
        fixed_duration_ns=args.fixed_duration,
        warm_all_durations=args.warm_all_durations,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
