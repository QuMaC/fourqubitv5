"""Refine one CR NN output with direct robust GRAPE and compare waveforms."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import jax
import jax.numpy as jnp
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

from .cost import build_physics, request_metrics_from_flat
from .evaluate import Request, load_model, waveform_for_request


def _active_to_x(active: np.ndarray) -> np.ndarray:
    active = np.asarray(active, dtype=complex).reshape(-1)
    return np.column_stack([active.real, active.imag]).reshape(-1)


def _x_to_flat_200(x, *, duration_ns: int, max_flat_samples: int):
    x = jnp.asarray(x, dtype=jnp.float64).reshape(-1)
    active = x[0::2] + 1j * x[1::2]
    duration = int(duration_ns)
    if active.shape[0] != duration:
        raise ValueError(f"expected {duration} complex controls, got {active.shape[0]}")
    start = (int(max_flat_samples) - duration) // 2
    return jnp.zeros(max_flat_samples, dtype=jnp.complex128).at[
        start : start + duration
    ].set(active)


def compare(
    checkpoint: str | Path,
    *,
    request: Request,
    output_dir: str | Path,
    maxiter: int = 50,
) -> Path:
    config, model, metadata, resolved = load_model(checkpoint)
    physics = build_physics(config)
    flat_200_nn, active_nn = waveform_for_request(config, model, request)

    def objective(x):
        flat_200 = _x_to_flat_200(
            x,
            duration_ns=request.duration_ns,
            max_flat_samples=config.max_flat_samples,
        )
        metrics = request_metrics_from_flat(
            flat_200,
            coupling_mhz=request.coupling_mhz,
            robustness_mhz=request.robustness_mhz,
            duration_ns=request.duration_ns,
            physics=physics,
            config=config,
        )
        return metrics.loss

    objective_vg = jax.jit(jax.value_and_grad(objective))

    def scipy_fun(x):
        value, grad = objective_vg(jnp.asarray(x, dtype=jnp.float64))
        return float(value), np.asarray(grad, dtype=float)

    x0 = _active_to_x(active_nn)
    bound = float(request.amp_bound_mhz)
    result = minimize(
        scipy_fun,
        x0,
        method="L-BFGS-B",
        jac=True,
        bounds=[(-bound, bound)] * x0.size,
        options={"maxiter": int(maxiter), "ftol": 1e-10, "gtol": 1e-8},
    )
    active_grape = np.asarray(result.x[0::2] + 1j * result.x[1::2])
    start = (config.max_flat_samples - request.duration_ns) // 2
    flat_200_grape = np.zeros(config.max_flat_samples, dtype=complex)
    flat_200_grape[start : start + request.duration_ns] = active_grape

    nn_metrics = request_metrics_from_flat(
        jnp.asarray(flat_200_nn),
        coupling_mhz=request.coupling_mhz,
        robustness_mhz=request.robustness_mhz,
        duration_ns=request.duration_ns,
        physics=physics,
        config=config,
    )
    grape_metrics = request_metrics_from_flat(
        jnp.asarray(flat_200_grape),
        coupling_mhz=request.coupling_mhz,
        robustness_mhz=request.robustness_mhz,
        duration_ns=request.duration_ns,
        physics=physics,
        config=config,
    )

    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    path = output / "nn_vs_grape.png"
    time_ns = np.arange(request.duration_ns, dtype=float)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, constrained_layout=True)
    axes[0].plot(time_ns, active_nn.real, label="NN")
    axes[0].plot(time_ns, active_grape.real, label="GRAPE", alpha=0.8)
    axes[0].set_ylabel("I (MHz)")
    axes[0].legend()
    axes[1].plot(time_ns, active_nn.imag, label="NN")
    axes[1].plot(time_ns, active_grape.imag, label="GRAPE", alpha=0.8)
    axes[1].set_ylabel("Q (MHz)")
    axes[1].set_xlabel("flat-top time (ns)")
    fig.suptitle(
        f"NN F={float(nn_metrics.fidelity_combined):.8f}; "
        f"GRAPE F={float(grape_metrics.fidelity_combined):.8f}; "
        f"step={metadata['global_step']}; success={result.success}"
    )
    fig.savefig(path, dpi=180)
    plt.close(fig)

    np.savez_compressed(
        output / "nn_vs_grape.npz",
        checkpoint=np.asarray(str(resolved)),
        request=np.asarray(
            [
                request.duration_ns,
                request.robustness_mhz,
                request.amp_bound_mhz,
                request.coupling_mhz,
            ]
        ),
        nn_flat=active_nn,
        grape_flat=active_grape,
        nn_fidelity=float(nn_metrics.fidelity_combined),
        grape_fidelity=float(grape_metrics.fidelity_combined),
        scipy_success=bool(result.success),
        scipy_message=np.asarray(str(result.message)),
        scipy_nit=int(result.nit),
    )
    return path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--robustness-khz", type=float, default=190.0)
    parser.add_argument("--amp-bound-mhz", type=float, default=50.0)
    parser.add_argument("--coupling-mhz", type=float, default=None)
    parser.add_argument("--maxiter", type=int, default=50)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config, _model, _metadata, _resolved = load_model(args.checkpoint)
    request = Request(
        duration_ns=args.duration,
        robustness_mhz=1e-3 * args.robustness_khz,
        amp_bound_mhz=args.amp_bound_mhz,
        coupling_mhz=(
            config.coupling_center_mhz
            if args.coupling_mhz is None
            else args.coupling_mhz
        ),
    )
    path = compare(
        args.checkpoint,
        request=request,
        output_dir=args.output_dir,
        maxiter=args.maxiter,
    )
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
