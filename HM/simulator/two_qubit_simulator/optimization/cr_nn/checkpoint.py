"""Atomic, resumable checkpoints for long CR neural-network training runs."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any
import uuid

import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np

from .config import CRNNConfig


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _checkpoint_root(output_dir: str | Path) -> Path:
    root = Path(output_dir).expanduser().resolve() / "checkpoints"
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_checkpoint(
    output_dir: str | Path,
    *,
    global_step: int,
    model,
    optimizer_state,
    rng_key: jax.Array,
    config: CRNNConfig,
    duration_order: tuple[int, ...],
    last_metrics: dict[str, float] | None = None,
    fixed_duration_ns: int | None = None,
) -> Path:
    """Write one complete checkpoint directory, then atomically publish it."""
    root = _checkpoint_root(output_dir)
    step = int(global_step)
    final_dir = root / f"step_{step:09d}_{uuid.uuid4().hex[:12]}"
    tmp_dir = Path(tempfile.mkdtemp(prefix=".checkpoint-", dir=root))
    try:
        eqx.tree_serialise_leaves(
            tmp_dir / "state.eqx",
            (model, optimizer_state),
        )
        metadata = {
            "format_version": 2,
            "global_step": step,
            "rng_key": np.asarray(rng_key, dtype=np.uint32).tolist(),
            "duration_order": [int(v) for v in duration_order],
            "fixed_duration_ns": (
                None if fixed_duration_ns is None else int(fixed_duration_ns)
            ),
            "config": config.to_dict(),
            "last_metrics": dict(last_metrics or {}),
        }
        metadata_path = tmp_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        os.replace(tmp_dir, final_dir)
    except BaseException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    _atomic_text(root / "latest", final_dir.name + "\n")
    _prune_checkpoints(root, keep=config.keep_checkpoints)
    return final_dir


def _prune_checkpoints(root: Path, *, keep: int) -> None:
    if keep < 1:
        return
    checkpoints = sorted(
        (path for path in root.glob("step_*") if path.is_dir()),
        key=lambda path: path.stat().st_mtime_ns,
    )
    for old in checkpoints[:-keep]:
        shutil.rmtree(old)


def resolve_checkpoint(path: str | Path) -> Path:
    """Resolve an output directory, checkpoints directory, or step directory."""
    candidate = Path(path).expanduser().resolve()
    if (candidate / "state.eqx").is_file():
        return candidate
    if (candidate / "checkpoints").is_dir():
        candidate = candidate / "checkpoints"
    latest = candidate / "latest"
    if not latest.is_file():
        raise FileNotFoundError(f"no checkpoint found under {path}")
    name = latest.read_text(encoding="utf-8").strip()
    resolved = candidate / name
    if not (resolved / "state.eqx").is_file():
        raise FileNotFoundError(f"latest checkpoint is incomplete: {resolved}")
    return resolved


def read_metadata(path: str | Path) -> tuple[Path, dict[str, Any]]:
    checkpoint = resolve_checkpoint(path)
    metadata = json.loads(
        (checkpoint / "metadata.json").read_text(encoding="utf-8")
    )
    if int(metadata.get("format_version", -1)) != 2:
        raise ValueError(f"unsupported checkpoint format in {checkpoint}")
    return checkpoint, metadata


def load_checkpoint(
    path: str | Path,
    *,
    model_template,
    optimizer_state_template,
):
    """Restore arrays into caller-created model and optimizer templates."""
    checkpoint, metadata = read_metadata(path)
    model, optimizer_state = eqx.tree_deserialise_leaves(
        checkpoint / "state.eqx",
        (model_template, optimizer_state_template),
    )
    rng_key = np.asarray(metadata["rng_key"], dtype=np.uint32)
    return (
        model,
        optimizer_state,
        jnp.asarray(rng_key),
        metadata,
        checkpoint,
    )


def config_from_checkpoint(path: str | Path) -> CRNNConfig:
    _, metadata = read_metadata(path)
    return CRNNConfig.from_dict(metadata["config"])
