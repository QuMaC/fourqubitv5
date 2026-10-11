"""Evaluate a CR NN checkpoint and generate waveform and fidelity portraits."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys

import equinox as eqx
import jax
import jax.numpy as jnp
import matplotlib.pyplot as plt
import numpy as np

from HM.simulator.two_qubit_simulator.engine.envelope_filters import (
    sample_envelope,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    assemble_cr_half_jax,
    echoed_timeline_jax,
)

from .checkpoint import config_from_checkpoint, load_checkpoint
from .config import CRNNConfig, normalize_inputs
from .cost import build_physics, fidelities_for_shifts
from .model import (
    CRPulseMLP,
    center_crop_flat,
    centered_plot_row,
    flat_knobs_200,
)
from .train import make_optimizer


@dataclass(frozen=True)
class Request:
    duration_ns: int
    robustness_mhz: float
    amp_bound_mhz: float
    coupling_mhz: float


def validate_request(config: CRNNConfig, request: Request) -> None:
    if int(request.duration_ns) not in config.durations_ns:
        raise ValueError(
            f"duration must be one of {config.durations_ns}, "
            f"got {request.duration_ns}"
        )
    if not (
        config.robustness_min_mhz
        <= request.robustness_mhz
        <= config.robustness_max_mhz
    ):
        raise ValueError("robustness half-width is outside the trained range")
    if not config.amp_min_mhz <= request.amp_bound_mhz <= config.amp_max_mhz:
        raise ValueError("amplitude bound is outside the trained range")
    if not (
        config.coupling_min_mhz
        <= request.coupling_mhz
        <= config.coupling_max_mhz
    ):
        raise ValueError("coupling is outside the trained range")


def load_model(checkpoint_path: str | Path):
    config = config_from_checkpoint(checkpoint_path)
    template = CRPulseMLP(
        config,
        key=jax.random.PRNGKey(config.random_seed),
    )
    optimizer = make_optimizer(config)
    optimizer_state = optimizer.init(eqx.filter(template, eqx.is_inexact_array))
    model, _state, _key, metadata, resolved = load_checkpoint(
        checkpoint_path,
        model_template=template,
        optimizer_state_template=optimizer_state,
    )
    return config, model, metadata, resolved


def waveform_for_request(
    config: CRNNConfig,
    model: CRPulseMLP,
    request: Request,
) -> tuple[np.ndarray, np.ndarray]:
    validate_request(config, request)
    x = normalize_inputs(
        config,
        float(request.duration_ns),
        request.robustness_mhz,
        request.amp_bound_mhz,
        request.coupling_mhz,
    )
    flat_200 = flat_knobs_200(model, x, request.amp_bound_mhz)
    active = center_crop_flat(flat_200, request.duration_ns)
    return np.asarray(flat_200), np.asarray(active)


def _axis_requests(
    config: CRNNConfig,
    axis: str,
    reference: Request,
) -> tuple[np.ndarray, list[Request], str]:
    if axis == "duration":
        values = np.asarray(config.durations_ns, dtype=float)
        requests = [
            Request(int(v), reference.robustness_mhz, reference.amp_bound_mhz, reference.coupling_mhz)
            for v in values
        ]
        return values, requests, "flat duration (ns)"
    if axis == "robustness":
        values = np.linspace(
            config.robustness_min_mhz,
            config.robustness_max_mhz,
            31,
        )
        requests = [
            Request(reference.duration_ns, float(v), reference.amp_bound_mhz, reference.coupling_mhz)
            for v in values
        ]
        return 1e3 * values, requests, "robustness half-width S (kHz)"
    if axis == "amplitude":
        values = np.arange(config.amp_min_mhz, config.amp_max_mhz + 0.1, 5.0)
        requests = [
            Request(reference.duration_ns, reference.robustness_mhz, float(v), reference.coupling_mhz)
            for v in values
        ]
        return values, requests, "I/Q amplitude bound (MHz)"
    if axis == "coupling":
        values = np.linspace(
            config.coupling_min_mhz,
            config.coupling_max_mhz,
            21,
        )
        requests = [
            Request(reference.duration_ns, reference.robustness_mhz, reference.amp_bound_mhz, float(v))
            for v in values
        ]
        return values, requests, "J12 (MHz)"
    raise ValueError(f"unknown portrait axis {axis!r}")


def _save_heatmap(
    rows: np.ndarray,
    y_values: np.ndarray,
    *,
    y_label: str,
    x_label: str,
    title: str,
    path: Path,
) -> None:
    components = (
        (rows.real, "I (MHz)", "RdBu_r"),
        (rows.imag, "Q (MHz)", "RdBu_r"),
        (np.abs(rows), "magnitude (MHz)", "viridis"),
        (np.angle(rows), "phase (rad)", "twilight"),
    )
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)
    extent = [0.0, float(rows.shape[1] - 1), float(y_values[0]), float(y_values[-1])]
    for ax, (image, label, cmap) in zip(axes.ravel(), components):
        im = ax.imshow(
            image,
            origin="lower",
            aspect="auto",
            interpolation="nearest",
            extent=extent,
            cmap=cmap,
        )
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(label)
        fig.colorbar(im, ax=ax)
    fig.suptitle(title)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def make_portrait(
    config: CRNNConfig,
    model: CRPulseMLP,
    *,
    axis: str,
    reference: Request,
    output_dir: Path,
) -> tuple[Path, Path]:
    y_values, requests, y_label = _axis_requests(config, axis, reference)
    raw_rows = []
    filtered_rows = []
    rise, fall, x_pi = build_physics_templates(config)
    max_cr_half = max(config.durations_ns) + int(rise.size) + int(fall.size)
    max_timeline = 2 * max_cr_half + 2 * int(x_pi.size)

    for request in requests:
        _flat_200, active = waveform_for_request(config, model, request)
        raw_rows.append(centered_plot_row(active, config.max_flat_samples))

        cr_plus, _ = assemble_cr_half_jax(
            jnp.asarray(active),
            rise=rise,
            fall=fall,
            n_flat=request.duration_ns,
            n_link_samples=config.n_link_samples,
        )
        timeline = echoed_timeline_jax(cr_plus, x_pi)
        _time_ns, filtered = sample_envelope(
            config.envelope,
            np.asarray(timeline["cr_drive"]),
            config.dt_sample_ns,
            n_per_bin=1,
        )
        row = np.full(max_timeline + 1, np.nan + 1j * np.nan, dtype=complex)
        row[: filtered.size] = filtered
        filtered_rows.append(row)

    raw = np.asarray(raw_rows)
    filtered = np.asarray(filtered_rows)
    raw_path = output_dir / f"portrait_{axis}_raw_flat.png"
    filtered_path = output_dir / f"portrait_{axis}_bessel_timeline.png"
    _save_heatmap(
        raw,
        y_values,
        y_label=y_label,
        x_label="centered 1 ns flat-output coordinate",
        title=f"CR NN raw flat output versus {axis}",
        path=raw_path,
    )
    _save_heatmap(
        filtered,
        y_values,
        y_label=y_label,
        x_label="1 ns echoed-timeline coordinate",
        title=f"CR-drive timeline seen through {config.envelope} versus {axis}",
        path=filtered_path,
    )
    np.savez_compressed(
        output_dir / f"portrait_{axis}.npz",
        y_values=y_values,
        raw_flat=raw,
        bessel_timeline=filtered,
    )
    return raw_path, filtered_path


_TEMPLATE_CACHE: dict[tuple, tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]] = {}


def build_physics_templates(
    config: CRNNConfig,
) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """Reuse the exact templates while producing many cheap portrait rows."""
    key = (
        config.qubit_pair,
        config.n_levels,
        config.t_rise_ns,
        config.envelope,
    )
    if key not in _TEMPLATE_CACHE:
        physics = build_physics(config)
        _TEMPLATE_CACHE[key] = (physics.rise, physics.fall, physics.x_pi)
    return _TEMPLATE_CACHE[key]


def make_detuning_plot(
    config: CRNNConfig,
    model: CRPulseMLP,
    *,
    request: Request,
    output_dir: Path,
    n_points: int = 121,
) -> Path:
    physics = build_physics(config)
    flat_200, _active = waveform_for_request(config, model, request)
    limit = max(config.robustness_max_mhz, request.robustness_mhz)
    shifts = jnp.linspace(-limit, limit, int(n_points), dtype=jnp.float64)
    score_fn = jax.jit(
        lambda flat: fidelities_for_shifts(
            flat,
            shifts,
            coupling_mhz=request.coupling_mhz,
            duration_ns=request.duration_ns,
            physics=physics,
            config=config,
        )
    )
    fidelities, leakages = score_fn(jnp.asarray(flat_200))
    shifts_khz = 1e3 * np.asarray(shifts)
    fidelities = np.asarray(fidelities)
    leakages = np.asarray(leakages)

    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True, constrained_layout=True)
    axes[0].semilogy(shifts_khz, np.maximum(1.0 - fidelities, 1e-12))
    axes[0].set_ylabel("process infidelity")
    axes[0].grid(True, alpha=0.25)
    axes[1].plot(shifts_khz, leakages)
    axes[1].set_ylabel("leakage")
    axes[1].set_xlabel("target-frame shift (kHz)")
    axes[1].grid(True, alpha=0.25)
    for ax in axes:
        ax.axvline(-1e3 * request.robustness_mhz, color="tab:red", ls="--")
        ax.axvline(+1e3 * request.robustness_mhz, color="tab:red", ls="--")
    fig.suptitle(
        f"Frozen CR NN pulse: T={request.duration_ns} ns, "
        f"S={1e3 * request.robustness_mhz:g} kHz, "
        f"Amax={request.amp_bound_mhz:g} MHz, J={request.coupling_mhz:g} MHz"
    )
    path = output_dir / "detuning_profile.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    np.savez_compressed(
        output_dir / "detuning_profile.npz",
        shifts_mhz=np.asarray(shifts),
        fidelities=fidelities,
        leakage=leakages,
        flat_200=flat_200,
    )
    return path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--robustness-khz", type=float, default=190.0)
    parser.add_argument("--amp-bound-mhz", type=float, default=50.0)
    parser.add_argument("--coupling-mhz", type=float, default=None)
    parser.add_argument(
        "--axis",
        choices=("all", "duration", "robustness", "amplitude", "coupling"),
        default="all",
    )
    parser.add_argument("--skip-detuning", action="store_true")
    parser.add_argument("--detuning-points", type=int, default=121)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config, model, metadata, resolved = load_model(args.checkpoint)
    coupling = (
        config.coupling_center_mhz
        if args.coupling_mhz is None
        else float(args.coupling_mhz)
    )
    reference = Request(
        duration_ns=int(args.duration),
        robustness_mhz=float(args.robustness_khz) * 1e-3,
        amp_bound_mhz=float(args.amp_bound_mhz),
        coupling_mhz=coupling,
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else resolved.parent.parent / "evaluation" / timestamp
    )
    output.mkdir(parents=True, exist_ok=True)
    axes = (
        ("duration", "robustness", "amplitude", "coupling")
        if args.axis == "all"
        else (args.axis,)
    )
    print(
        f"checkpoint={resolved} step={metadata['global_step']} output={output}",
        flush=True,
    )
    for axis in axes:
        paths = make_portrait(
            config,
            model,
            axis=axis,
            reference=reference,
            output_dir=output,
        )
        print(f"{axis}: {paths[0]} {paths[1]}", flush=True)
    if not args.skip_detuning:
        path = make_detuning_plot(
            config,
            model,
            request=reference,
            output_dir=output,
            n_points=args.detuning_points,
        )
        print(f"detuning: {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
