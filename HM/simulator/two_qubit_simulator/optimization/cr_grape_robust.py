"""Robust (multi-detuning) GRAPE for echoed CR gates.

One CR-half pulse is optimized so it works well at *N* target-qubit
frequencies at once (e.g. the target shifted by a spectator's ZZ interaction).
Frequencies are modelled by shifting the target qubit's ``frame_MHz``;
``shifts_mhz`` may be any list of length ``N >= 1``. If omitted, the default
pair is ``+/- zz_shift_mhz / 2``.

Combined fidelity metrics (set ``fidelity_metric`` in the config or test script):

- ``weighted_mean``: ``sum_i w_i F_i`` (default equal weights)
- ``geometric_mean``: ``exp(sum_i w_i log F_i)``
- ``mean_minus_spread``: weighted mean minus ``lambda * (max F - min F)``

The optimized pulse, seed, per-case convergence, and combined/per-case
fidelities are saved (NPZ mirrors ``cr_grape.py`` + robust extras, filename
carries a timestamp and the ZZ span).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Sequence
import matplotlib

# Headless / long batch runs: TkAgg GC can abort with Tcl_AsyncDelete.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from tqdm import tqdm

import jax
import jax.numpy as jnp

from HM.simulator.two_qubit_simulator.engine.pulses import (
    assemble_cr_half_from_flat_knobs,
    expand_samples_held_nsub,
    scale_sample_index,
    seed_flat_knobs_from_calibrated_cr,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    assemble_cr_half_jax,
    echoed_timeline_jax,
    _templates_1ns,
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    DEFAULT_CR_PULSE_PARAMS,
    _knobs_to_x,
    _to_jsonable,
    _x_to_knobs,
    echoed_gate_duration_ns,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    average_gate_fidelity,
    embed_in_full,
    gate_metrics,
    leakage_from_comp,
    process_fidelity,
    zx_target_unitary,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    leakage_from_psi_jax,
    process_fidelity_comp_jax,
    u_comp_from_psi_jax,
)
from HM.simulator.two_qubit_simulator.optimization.grape_cost_jax import (
    GrapeStatics,
    combine_robust_fidelities_jax,
    grape_cost_robust,
)


# ---------------------------------------------------------------------------
# Physical knob: shift the target qubit frequency (models a ZZ shift)
# ---------------------------------------------------------------------------
def _apply_target_freq_shift(exp: CR_len_sweep, shift_mhz: float) -> CR_len_sweep:
    """Shift the target qubit (q2) frequency by ``shift_mhz`` in place.

    The CR drive carrier stays where it was calibrated, so the drive becomes
    detuned from the moved target exactly as a ZZ shift would do. Only the
    target frame and the cached qubit-qubit detuning need updating; the drift
    Hamiltonian carries only anharmonicities, so no operator rebuild is needed.
    """
    sim = exp.simulator
    sim.qubits[1].frame_MHz = float(sim.qubits[1].frame_MHz) + float(shift_mhz)
    sim.delta_qq_MHz = sim.qubits[0].frame_MHz - sim.qubits[1].frame_MHz
    return exp


def _fmt_mhz(x: float) -> str:
    """Filesystem-safe MHz tag, e.g. 0.2 -> '0p2', -0.1 -> 'm0p1'."""
    return f"{float(x):.4g}".replace("-", "m").replace(".", "p")


def _default_results_dir() -> str:
    return os.path.join(
        os.path.dirname(__file__), "optimization_tests", "results", "robust"
    )


FidelityMetric = Literal["weighted_mean", "geometric_mean", "mean_minus_spread"]

FIDELITY_METRICS: dict[FidelityMetric, str] = {
    "weighted_mean": "Weighted arithmetic mean over N detunings: sum_i w_i F_i",
    "geometric_mean": "Weighted geometric mean: exp(sum_i w_i log F_i)",
    "mean_minus_spread": (
        "Weighted mean minus spread: sum_i w_i F_i - lambda*(max F - min F)"
    ),
}


def combine_robust_fidelities(
    fidelities: Sequence[float],
    metric: FidelityMetric,
    weights: Sequence[float] | None = None,
    spread_penalty_lambda: float = 0.3,
) -> float:
    """Combine N per-detuning process fidelities into one scalar objective.

    Spread for ``mean_minus_spread`` is ``max(F)-min(F)`` (equals ``|F_a-F_b|``
    when N=2).
    """
    f = np.asarray(list(fidelities), dtype=float).reshape(-1)
    if f.size < 1:
        raise ValueError("fidelities must be non-empty")
    if weights is None:
        w = np.full(f.size, 1.0 / f.size, dtype=float)
    else:
        w = np.asarray(weights, dtype=float).reshape(-1)
        if w.size != f.size or np.any(w < 0):
            raise ValueError(
                f"weights must be {f.size} non-negative numbers "
                f"(got size {w.size})"
            )
        total = float(w.sum())
        if total <= 0:
            w = np.full(f.size, 1.0 / f.size, dtype=float)
        else:
            w = w / total
    if metric == "weighted_mean":
        return float(np.sum(w * f))
    if metric == "geometric_mean":
        return float(np.exp(np.sum(w * np.log(np.maximum(f, 1e-30)))))
    if metric == "mean_minus_spread":
        spread = float(np.max(f) - np.min(f)) if f.size >= 2 else 0.0
        return float(np.sum(w * f) - spread_penalty_lambda * spread)
    raise ValueError(
        f"Unknown fidelity_metric {metric!r}; "
        f"choose one of {list(FIDELITY_METRICS)}"
    )


def _fidelity_spread(fidelities: Sequence[float]) -> float:
    f = np.asarray(list(fidelities), dtype=float).reshape(-1)
    if f.size < 2:
        return 0.0
    return float(np.max(f) - np.min(f))


def _legacy_ab_fields(fs: Sequence[float], leaks: Sequence[float], avgs: Sequence[float]) -> dict:
    """Keep process_fidelity_a/b keys for N>=2 callers / old plot scripts."""
    out: dict = {
        "process_fidelities": [float(v) for v in fs],
        "leakages": [float(v) for v in leaks],
        "average_gate_fidelities": [float(v) for v in avgs],
        "process_fidelity_a": float(fs[0]) if len(fs) >= 1 else float("nan"),
        "process_fidelity_b": float(fs[1]) if len(fs) >= 2 else float("nan"),
        "leakage_a": float(leaks[0]) if len(leaks) >= 1 else float("nan"),
        "leakage_b": float(leaks[1]) if len(leaks) >= 2 else float("nan"),
        "average_gate_fidelity_a": float(avgs[0]) if len(avgs) >= 1 else float("nan"),
        "average_gate_fidelity_b": float(avgs[1]) if len(avgs) >= 2 else float("nan"),
    }
    return out


def fidelity_metric_label(metric: FidelityMetric) -> str:
    if metric == "weighted_mean":
        return "F_combined (weighted mean)"
    if metric == "geometric_mean":
        return "F_combined (geometric mean)"
    return "F_combined (mean - spread penalty)"


def _metric_tag(metric: FidelityMetric, spread_penalty_lambda: float) -> str:
    if metric == "weighted_mean":
        return "wmean"
    if metric == "geometric_mean":
        return "gmean"
    lam = _fmt_mhz(spread_penalty_lambda)
    return f"mms_l{lam}"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass
class RobustCRGrapeConfig:
    """Configuration for multi-detuning (robust) echoed CR GRAPE."""

    flat_len_ns: float = 122
    n_flat_knobs: int = 61
    seed_amp_mhz: float = 21.0
    seed_phase_rad: float = 0.0
    t_rise_ns: int = 16
    n_link_samples: int = 8

    # Target-frequency spread. ``shifts_mhz`` (any N>=1 list) takes priority;
    # otherwise the two cases are +/- zz_shift_mhz / 2.
    zz_shift_mhz: float = 0.3
    shifts_mhz: list[float] | None = None
    weights: Sequence[float] | None = None
    """Per-shift weights (length N). None → equal 1/N."""
    fidelity_metric: FidelityMetric = "weighted_mean"
    spread_penalty_lambda: float = 0.3

    target_gate: str | None = None
    amp_bound_mhz: float = 48.0
    maxiter: int = 360
    qubit_pair: list[int] = field(default_factory=lambda: [1, 2])
    n_levels: int = 3
    n_sub: int = 16
    optimize: bool = True
    show_progress: bool = True
    log_every_eval: bool = False
    results_dir: str | None = None
    use_jax_grad: bool = False
    """If True, one dynamiqs exp + batched frames + SciPy jac=True."""
    optimizer: str = "lbfgs"
    """lbfgs (default) or adam; adam requires use_jax_grad=True."""
    adam_lr: float = 0.02
    adam_steps: int = 200
    """Used only when optimizer='adam'."""
    evolution: str = "comp"
    """comp only for JAX robust path."""

    def resolved_shifts(self) -> list[float]:
        if self.shifts_mhz is not None:
            s = [float(v) for v in self.shifts_mhz]
            if len(s) < 1:
                raise ValueError("shifts_mhz must have at least one entry")
            return s
        half = 0.5 * float(self.zz_shift_mhz)
        return [-half, half]

    def resolved_weights(self) -> tuple[float, ...]:
        n = len(self.resolved_shifts())
        if self.weights is None:
            return tuple(1.0 / n for _ in range(n))
        w = np.asarray(self.weights, dtype=float).reshape(-1)
        if w.size != n or np.any(w < 0):
            raise ValueError(
                f"weights must be {n} non-negative numbers "
                f"(got size {w.size})"
            )
        total = float(w.sum())
        if total <= 0:
            return tuple(1.0 / n for _ in range(n))
        return tuple(float(v / total) for v in w)

    def zz_span_mhz(self) -> float:
        s = self.resolved_shifts()
        return float(max(s) - min(s))

    def resolved_fidelity_metric(self) -> FidelityMetric:
        metric = self.fidelity_metric
        if metric not in FIDELITY_METRICS:
            raise ValueError(
                f"Unknown fidelity_metric {metric!r}; "
                f"choose one of {list(FIDELITY_METRICS)}"
            )
        return metric


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
@dataclass
class RobustGrapeResult:
    """Outcome of a robust (multi-detuning) GRAPE run."""

    config: RobustCRGrapeConfig
    shifts_mhz: list[float]
    weights: tuple[float, ...]
    target_gate: str
    flat_knobs_seed: np.ndarray
    flat_knobs_opt: np.ndarray
    cr_half_seed: np.ndarray
    cr_half_opt: np.ndarray
    half_slices: dict[str, tuple[int, int]]
    seed_metrics: dict
    final_metrics: dict
    history: list[dict]
    eval_history: list[dict]
    scipy_result: Any = None
    exps: list[CR_len_sweep] | None = None

    @property
    def total_echoed_duration_ns(self) -> float:
        assert self.exps is not None
        x_pi_len = self.exps[0].x_pi_pulse_params["length_ns"]
        return echoed_gate_duration_ns(
            self.config.flat_len_ns, self.config.t_rise_ns, x_pi_len
        )

    def _basename(self) -> str:
        ts = time.strftime("%Y%m%d_%H%M%S")
        zz = _fmt_mhz(self.config.zz_span_mhz())
        metric = _metric_tag(
            self.config.resolved_fidelity_metric(),
            self.config.spread_penalty_lambda,
        )
        return f"cr_grape_robust_zz{zz}MHz_{metric}_{ts}"

    def save(self, directory: str | None = None) -> dict[str, str]:
        directory = directory or self.config.results_dir or _default_results_dir()
        os.makedirs(directory, exist_ok=True)

        base = self._basename()
        json_path = os.path.join(directory, f"{base}.json")
        npz_path = os.path.join(directory, f"{base}.npz")
        conv_png = os.path.join(directory, f"{base}_convergence.png")
        wf_png = os.path.join(directory, f"{base}_waveform.png")

        dt = self.exps[0].dt_sample_ns if self.exps else 1.0
        t_half = np.arange(len(self.cr_half_opt), dtype=float) * dt

        payload = _to_jsonable(
            {
                "config": asdict(self.config),
                "shifts_mhz": self.shifts_mhz,
                "weights": list(self.weights),
                "target_gate": self.target_gate,
                "total_echoed_duration_ns": self.total_echoed_duration_ns,
                "half_slices": {
                    k: {"start": v[0], "stop": v[1]}
                    for k, v in self.half_slices.items()
                },
                "seed_metrics": self.seed_metrics,
                "final_metrics": self.final_metrics,
                "history": self.history,
                "eval_history": self.eval_history if self.config.log_every_eval else None,
            }
        )
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        np.savez(
            npz_path,
            t_ns=t_half,
            flat_knobs_seed=self.flat_knobs_seed,
            flat_knobs_opt=self.flat_knobs_opt,
            cr_half_seed_I=self.cr_half_seed.real,
            cr_half_seed_Q=self.cr_half_seed.imag,
            cr_half_opt_I=self.cr_half_opt.real,
            cr_half_opt_Q=self.cr_half_opt.imag,
            rise_start=self.half_slices["rise"][0],
            flat_start=self.half_slices["flat"][0],
            flat_stop=self.half_slices["flat"][1],
            fall_start=self.half_slices["fall"][0],
            shifts_mhz=np.asarray(self.shifts_mhz, dtype=float),
            weights=np.asarray(self.weights, dtype=float),
            zz_span_mhz=float(self.config.zz_span_mhz()),
            seed_process_fidelities=np.asarray(
                self.seed_metrics.get(
                    "process_fidelities",
                    [
                        self.seed_metrics.get("process_fidelity_a", np.nan),
                        self.seed_metrics.get("process_fidelity_b", np.nan),
                    ],
                ),
                dtype=float,
            ),
            final_process_fidelities=np.asarray(
                self.final_metrics.get(
                    "process_fidelities",
                    [
                        self.final_metrics.get("process_fidelity_a", np.nan),
                        self.final_metrics.get("process_fidelity_b", np.nan),
                    ],
                ),
                dtype=float,
            ),
            seed_F_a=float(self.seed_metrics.get("process_fidelity_a", np.nan)),
            seed_F_b=float(self.seed_metrics.get("process_fidelity_b", np.nan)),
            seed_F_combined=float(self.seed_metrics["process_fidelity"]),
            final_F_a=float(self.final_metrics.get("process_fidelity_a", np.nan)),
            final_F_b=float(self.final_metrics.get("process_fidelity_b", np.nan)),
            final_F_combined=float(self.final_metrics["process_fidelity"]),
        )

        self.plot_convergence(conv_png)
        self.plot_waveform(wf_png)

        paths = {
            "json": json_path,
            "npz": npz_path,
            "convergence_png": conv_png,
            "waveform_png": wf_png,
        }
        for p in paths.values():
            print(f"Saved {p}")
        return paths

    def plot_convergence(self, out_png: str) -> None:
        # Prepend the seed as iteration 0 so the curves start from the seed.
        iters = [0] + [h["iteration"] + 1 for h in self.history]
        n = len(self.shifts_mhz)
        per_case = []
        for i in range(n):
            key = "process_fidelities"
            seed_fs = self.seed_metrics.get(key)
            if seed_fs is not None and len(seed_fs) > i:
                seed_fi = float(seed_fs[i])
            elif i == 0:
                seed_fi = float(self.seed_metrics.get("process_fidelity_a", np.nan))
            elif i == 1:
                seed_fi = float(self.seed_metrics.get("process_fidelity_b", np.nan))
            else:
                seed_fi = float("nan")
            hist_fi = []
            for h in self.history:
                hfs = h.get(key)
                if hfs is not None and len(hfs) > i:
                    hist_fi.append(float(hfs[i]))
                elif i == 0:
                    hist_fi.append(float(h.get("process_fidelity_a", np.nan)))
                elif i == 1:
                    hist_fi.append(float(h.get("process_fidelity_b", np.nan)))
                else:
                    hist_fi.append(float("nan"))
            per_case.append([seed_fi] + hist_fi)

        f_c = [self.seed_metrics["process_fidelity"]] + [
            h["process_fidelity"] for h in self.history
        ]

        fig, ax = plt.subplots(figsize=(9, 5.5))
        cmap = plt.cm.tab10
        markers = ["o", "s", "^", "D", "v", "P", "X", "*"]
        for i, (shift, curve) in enumerate(zip(self.shifts_mhz, per_case)):
            ax.plot(
                iters,
                curve,
                markers[i % len(markers)] + "-",
                ms=4,
                lw=1.3,
                color=cmap(i % 10),
                label=f"F[{i}] (shift {shift:+.4g} MHz)",
            )
        metric = self.config.resolved_fidelity_metric()
        ax.plot(
            iters,
            f_c,
            "k-",
            ms=4,
            lw=1.6,
            marker="*",
            label=fidelity_metric_label(metric),
        )
        ax.set_xlabel("optimizer iteration (0 = seed)")
        ax.set_ylabel("process fidelity")
        all_f = [v for curve in per_case for v in curve] + f_c
        lo, hi = min(all_f), max(all_f)
        pad = max((hi - lo) * 0.08, 1e-4)
        ax.set_ylim(lo - pad, min(1.0005, hi + pad))
        ax.grid(alpha=0.35)
        ax.legend(fontsize=9, loc="lower right")
        metric_desc = FIDELITY_METRICS[metric]
        ax.set_title(
            f"Robust GRAPE convergence  |  target={self.target_gate}  |  "
            f"ZZ span={self.config.zz_span_mhz():.4g} MHz  |  "
            f"N={len(self.shifts_mhz)}  flat={self.config.flat_len_ns:.0f} ns  "
            f"knobs={self.config.n_flat_knobs}\n"
            f"metric={metric}  ({metric_desc})"
        )
        plt.tight_layout()
        plt.savefig(out_png, dpi=160)
        plt.close(fig)

    def plot_waveform(self, out_png: str) -> None:
        dt = self.exps[0].dt_sample_ns if self.exps else 1.0
        n_sub = int(self.exps[0].simulator.n_sub) if self.exps else 2
        rs, re = self.half_slices["rise"]
        fs, fe = self.half_slices["flat"]
        ds, de = self.half_slices["fall"]

        t, seed_exp = expand_samples_held_nsub(self.cr_half_seed, dt, n_sub)
        _, opt_exp = expand_samples_held_nsub(self.cr_half_opt, dt, n_sub)
        rs_e, re_e = scale_sample_index(rs, n_sub), scale_sample_index(re, n_sub)
        fs_e, fe_e = scale_sample_index(fs, n_sub), scale_sample_index(fe, n_sub)
        ds_e, de_e = scale_sample_index(ds, n_sub), scale_sample_index(de, n_sub)

        fig, axes = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
        for ax, key in zip(axes, ("I", "Q")):
            seed_y = seed_exp.real if key == "I" else seed_exp.imag
            opt_y = opt_exp.real if key == "I" else opt_exp.imag
            ax.plot(t, seed_y, color="0.65", lw=1.2, ls="--", label=f"seed {key} (MHz)")
            ax.plot(t, opt_y, color="tab:green", lw=1.6, label=f"opt {key} (MHz)")
            ax.axvspan(t[rs_e], t[re_e - 1] if re_e > rs_e else t[rs_e], color="tab:blue", alpha=0.08)
            ax.axvspan(t[fs_e], t[fe_e - 1] if fe_e > fs_e else t[fs_e], color="tab:orange", alpha=0.08)
            ax.axvspan(t[ds_e], t[de_e - 1] if de_e > ds_e else t[ds_e], color="tab:purple", alpha=0.08)
            ax.set_ylabel(f"{key} (MHz)")
            ax.grid(alpha=0.35)
            ax.legend(fontsize=8, loc="upper right")

        axes[1].set_xlabel(
            f"time within one CR half (ns)  |  held at n_sub={n_sub}  "
            f"(dt_sub={dt / n_sub:g} ns)"
        )
        s = self.seed_metrics
        f = self.final_metrics

        def _fi_line(m: dict, label: str) -> str:
            fs = m.get("process_fidelities")
            if not fs:
                fs = [
                    m.get("process_fidelity_a", float("nan")),
                    m.get("process_fidelity_b", float("nan")),
                ]
            parts = [
                f"F[{i}]({sh:+.4g})={fi:.5f}"
                for i, (sh, fi) in enumerate(zip(self.shifts_mhz, fs))
            ]
            return f"{label}: F_comb={m['process_fidelity']:.5f}   " + "   ".join(parts)

        summary = (
            f"target={self.target_gate}   ZZ span={self.config.zz_span_mhz():.4g} MHz  "
            f"N={len(self.shifts_mhz)}\n"
            f"{_fi_line(s, 'seed')}\n"
            f"{_fi_line(f, 'final')}"
        )
        axes[0].set_title(
            "Robust CR half: seed vs optimized "
            f"(shaded: rise / flat / fall; each sample held ×{n_sub})"
        )
        fig.text(0.01, 0.005, summary, ha="left", va="bottom", fontsize=8,
                 family="monospace", color="0.15")
        fig.text(0.99, 0.005, "blue=rise  orange=flat  purple=fall", ha="right",
                 va="bottom", fontsize=8, color="0.45")
        plt.tight_layout(rect=(0, 0.09, 1, 1))
        plt.savefig(out_png, dpi=160)
        plt.close(fig)


# ---------------------------------------------------------------------------
# Optimizer
# ---------------------------------------------------------------------------
def _build_shifted_exp(config: RobustCRGrapeConfig, shift_mhz: float) -> CR_len_sweep:
    cr_pulse_params = {
        **DEFAULT_CR_PULSE_PARAMS,
        "amp_mhz": config.seed_amp_mhz,
        "phase_rad": config.seed_phase_rad,
        "t_rise_ns": config.t_rise_ns,
    }
    exp = CR_len_sweep(
        qubit_pair=list(config.qubit_pair),
        echoed_cr=True,
        n_levels=config.n_levels,
        n_sub=int(config.n_sub),
        cr_pulse_params=cr_pulse_params,
    )
    return _apply_target_freq_shift(exp, shift_mhz)


def _build_lab_exp(config: RobustCRGrapeConfig) -> CR_len_sweep:
    """Single unshifted dynamiqs experiment. Caller installs batched frames."""
    cr_pulse_params = {
        **DEFAULT_CR_PULSE_PARAMS,
        "amp_mhz": config.seed_amp_mhz,
        "phase_rad": config.seed_phase_rad,
        "t_rise_ns": config.t_rise_ns,
    }
    return CR_len_sweep(
        qubit_pair=list(config.qubit_pair),
        echoed_cr=True,
        n_levels=int(config.n_levels),
        engine="dynamiqs",
        n_sub=int(config.n_sub),
        cr_pulse_params=cr_pulse_params,
    )


def _build_robust_grape_statics(opt: "RobustCRGrapeOptimizer") -> GrapeStatics:
    cfg = opt.config
    sim = opt.exps[0].simulator
    rise, fall = _templates_1ns(int(cfg.t_rise_ns))
    n_flat = int(round(float(cfg.flat_len_ns) / float(opt.dt)))
    if n_flat % int(cfg.n_flat_knobs) != 0:
        raise ValueError(
            f"n_flat={n_flat} must be divisible by n_flat_knobs={cfg.n_flat_knobs}"
        )
    if abs(float(opt.dt) - 1.0) > 1e-12:
        raise ValueError("JAX robust GRAPE locks dt_sample_ns=1.0")
    return GrapeStatics(
        rise=rise,
        fall=fall,
        n_flat=n_flat,
        n_link_samples=int(cfg.n_link_samples),
        x_pi=jnp.asarray(opt._x_pi[0]),
        U_target_full=jnp.asarray(opt.u_target_full),
        U_target_comp=jnp.asarray(opt.u_target_comp),
        comp_indices=tuple(sim.comp_idx),
        channel_names=("q1_drive", "q2_drive", "cr_drive"),
        evolution=str(cfg.evolution),
        leakage_weight=0.0,
    )


class RobustCRGrapeOptimizer:
    """Optimize one CR-half pulse against a combined two-detuning fidelity."""

    def __init__(
        self,
        config: RobustCRGrapeConfig,
        exps: list[CR_len_sweep] | None = None,
        flat_knobs_seed: np.ndarray | None = None,
    ):
        self.config = config
        self.shifts = config.resolved_shifts()
        self.weights = config.resolved_weights()
        self.fidelity_metric = config.resolved_fidelity_metric()
        self._jax_statics: GrapeStatics | None = None
        self._cost_vg = None

        if config.use_jax_grad:
            if exps is not None:
                raise ValueError(
                    "use_jax_grad=True builds its own single dynamiqs experiment; "
                    "do not pass exps="
                )
            if config.optimizer not in ("lbfgs", "adam"):
                raise ValueError(
                    f"unknown robust optimizer {config.optimizer!r}; "
                    "use 'lbfgs' or 'adam'"
                )
            if str(config.evolution) != "comp":
                raise ValueError("robust JAX path locks evolution='comp'")
            self.exps = [_build_lab_exp(config)]
            sim = self.exps[0].simulator
            if type(sim).__name__ != "TwoQubitPulseSimulatorDynamiqs":
                raise ValueError(
                    "use_jax_grad=True requires dynamiqs engine "
                    f"(got {type(sim).__name__})"
                )
        elif exps is not None:
            if len(exps) != len(self.shifts):
                raise ValueError(
                    f"exps must have length {len(self.shifts)} "
                    f"(one per shift); got {len(exps)}"
                )
            self.exps = list(exps)
        else:
            self.exps = [_build_shifted_exp(config, s) for s in self.shifts]

        for e in self.exps:
            if not e.echoed_cr:
                raise ValueError("RobustCRGrapeOptimizer requires echoed_cr=True")

        self.dt = self.exps[0].dt_sample_ns

        if flat_knobs_seed is not None:
            knobs = np.asarray(flat_knobs_seed, dtype=complex).reshape(-1)
            if knobs.size != config.n_flat_knobs:
                raise ValueError(
                    f"flat_knobs_seed length {knobs.size} != "
                    f"n_flat_knobs={config.n_flat_knobs}"
                )
            self.flat_knobs_seed = knobs
        else:
            self.flat_knobs_seed = seed_flat_knobs_from_calibrated_cr(
                n_flat_knobs=config.n_flat_knobs,
                flat_len_ns=config.flat_len_ns,
                amp_mhz=config.seed_amp_mhz,
                phase_rad=config.seed_phase_rad,
                t_rise_ns=config.t_rise_ns,
                dt_ns=self.dt,
            )
        self.cr_half_seed, self.half_slices = assemble_cr_half_from_flat_knobs(
            self.flat_knobs_seed,
            flat_len_ns=config.flat_len_ns,
            t_rise_ns=config.t_rise_ns,
            dt_ns=self.dt,
            n_link_samples=config.n_link_samples,
        )
        self._x_pi = [e.build_x_pi() for e in self.exps]

        if config.target_gate is not None:
            self.target_gate = str(config.target_gate)
        else:
            # Lab / first-exp frame still scalar here on the JAX path (batch set below).
            u_seed_a = self._propagate_one(0, self.flat_knobs_seed)
            self.target_gate = str(gate_metrics(u_seed_a, gate="best_zx")["zx_gate"])

        dim = self.exps[0].simulator.dim
        comp_idx = self.exps[0].simulator.comp_idx
        self.u_target_comp = zx_target_unitary(self.target_gate)
        self.u_target_full = embed_in_full(
            self.u_target_comp, dim=dim, comp_indices=comp_idx
        )

        if config.use_jax_grad:
            sim = self.exps[0].simulator
            f1 = float(np.asarray(sim.qubits[1].frame_MHz).reshape(()))
            sim.set_target_frame(
                f1 + jnp.asarray(self.shifts, dtype=jnp.float64)
            )
            self._jax_statics = _build_robust_grape_statics(self)
            statics = self._jax_statics
            metric = self.fidelity_metric
            weights = self.weights
            lam = float(config.spread_penalty_lambda)

            def _cost_only(x):
                return grape_cost_robust(
                    x,
                    sim,
                    statics,
                    fidelity_metric=metric,
                    weights=weights,
                    spread_penalty_lambda=lam,
                )

            self._cost_vg = jax.jit(jax.value_and_grad(_cost_only))

        self.history: list[dict] = []
        self.eval_history: list[dict] = []
        self._iteration = 0
        self._last_eval_metrics: dict | None = None
        self._pbar: tqdm | None = None
        self._n_reals = 2 * config.n_flat_knobs
        self._eval_at_iter_start = 0

    def assemble_half(self, flat_knobs: np.ndarray) -> np.ndarray:
        wf, slices = assemble_cr_half_from_flat_knobs(
            flat_knobs,
            flat_len_ns=self.config.flat_len_ns,
            t_rise_ns=self.config.t_rise_ns,
            dt_ns=self.dt,
            n_link_samples=self.config.n_link_samples,
        )
        if slices != self.half_slices:
            self.half_slices = slices
        return wf

    def _propagate_one(self, exp_index: int, flat_knobs: np.ndarray) -> np.ndarray:
        cr_plus = self.assemble_half(flat_knobs)
        exp = self.exps[exp_index]
        timeline = exp._build_timeline_from_cr_half(cr_plus, x_pi=self._x_pi[exp_index])
        return exp._propagator_from_timeline(timeline)

    def cost_from_knobs(self, flat_knobs: np.ndarray) -> tuple[float, dict]:
        if self.config.use_jax_grad:
            return self._cost_from_knobs_batched(flat_knobs)

        t0 = time.perf_counter()
        cr_plus = self.assemble_half(flat_knobs)

        per_case = []
        for i, exp in enumerate(self.exps):
            timeline = exp._build_timeline_from_cr_half(cr_plus, x_pi=self._x_pi[i])
            U = exp._propagator_from_timeline(timeline)
            per_case.append(
                {
                    "process_fidelity": float(process_fidelity(U, self.u_target_full)),
                    "average_gate_fidelity": float(
                        average_gate_fidelity(U, self.u_target_comp)
                    ),
                    "leakage": float(leakage_from_comp(U)),
                }
            )

        fs = [c["process_fidelity"] for c in per_case]
        leaks = [c["leakage"] for c in per_case]
        avgs = [c["average_gate_fidelity"] for c in per_case]
        f_combined = combine_robust_fidelities(
            fs,
            self.fidelity_metric,
            weights=self.weights,
            spread_penalty_lambda=self.config.spread_penalty_lambda,
        )
        w = np.asarray(self.weights, dtype=float)
        leak_combined = float(np.sum(w * np.asarray(leaks, dtype=float)))
        cost = -f_combined
        elapsed = time.perf_counter() - t0

        metrics = {
            "process_fidelity": float(f_combined),
            "fidelity_spread": _fidelity_spread(fs),
            "fidelity_metric": self.fidelity_metric,
            "spread_penalty_lambda": float(self.config.spread_penalty_lambda),
            "leakage": float(leak_combined),
            "cost": float(cost),
            "target_gate": self.target_gate,
            "elapsed_s": float(elapsed),
            "u_max_mhz": float(np.max(np.abs(flat_knobs))),
            **_legacy_ab_fields(fs, leaks, avgs),
        }
        return cost, metrics

    def _cost_from_knobs_batched(self, flat_knobs: np.ndarray) -> tuple[float, dict]:
        """Rich metrics for JAX robust path (one batched evolve_comp, no grad)."""
        t0 = time.perf_counter()
        sim = self.exps[0].simulator
        statics = self._jax_statics
        assert statics is not None
        n = len(self.shifts)

        knobs_j = jnp.asarray(flat_knobs, dtype=jnp.complex128).reshape(-1)
        cr_plus, _ = assemble_cr_half_jax(
            knobs_j,
            rise=statics.rise,
            fall=statics.fall,
            n_flat=int(statics.n_flat),
            n_link_samples=int(statics.n_link_samples),
        )
        timeline = echoed_timeline_jax(
            cr_plus,
            statics.x_pi,
            channel_names=statics.channel_names,
            echo_channel=statics.echo_channel,
        )
        psi = sim.evolve_comp(timeline)
        if psi.ndim != 4 or psi.shape[0] != n or psi.shape[1] != 4:
            raise ValueError(
                f"batched metrics expected psi ({n}, 4, dim, 1), got {psi.shape}"
            )

        Fs = []
        leaks = []
        for i in range(n):
            U_comp = u_comp_from_psi_jax(psi[i], statics.comp_indices)
            Fs.append(
                float(
                    process_fidelity_comp_jax(
                        U_comp=U_comp, U_target_comp=statics.U_target_comp
                    )
                )
            )
            leaks.append(float(leakage_from_psi_jax(psi[i], statics.comp_indices)))

        f_combined = float(
            combine_robust_fidelities_jax(
                jnp.asarray(Fs),
                metric=self.fidelity_metric,
                weights=self.weights,
                spread_penalty_lambda=float(self.config.spread_penalty_lambda),
            )
        )
        w = np.asarray(self.weights, dtype=float)
        leak_combined = float(np.sum(w * np.asarray(leaks, dtype=float)))
        cost = -f_combined
        elapsed = time.perf_counter() - t0
        avgs = [float("nan")] * n
        metrics = {
            "process_fidelity": f_combined,
            "fidelity_spread": _fidelity_spread(Fs),
            "fidelity_metric": self.fidelity_metric,
            "spread_penalty_lambda": float(self.config.spread_penalty_lambda),
            "leakage": leak_combined,
            "cost": cost,
            "target_gate": self.target_gate,
            "elapsed_s": float(elapsed),
            "u_max_mhz": float(np.max(np.abs(flat_knobs))),
            "backend": "jax_batched",
            **_legacy_ab_fields(Fs, leaks, avgs),
        }
        return cost, metrics

    def _cost_x(self, x: np.ndarray) -> float:
        knobs = _x_to_knobs(x)
        cost, metrics = self.cost_from_knobs(knobs)
        metrics["eval"] = len(self.eval_history)
        self.eval_history.append(metrics)
        self._last_eval_metrics = metrics
        if self._pbar is not None:
            evals_this_iter = len(self.eval_history) - self._eval_at_iter_start
            phase = "gradient" if evals_this_iter <= self._n_reals + 1 else "line search"
            self._pbar.set_description(f"robust GRAPE iter {self._iteration} [{phase}]")
            self._pbar.set_postfix(
                Fc=f"{metrics['process_fidelity']:.4f}",
                spread=f"{metrics.get('fidelity_spread', float('nan')):.4f}",
                eval_iter=evals_this_iter,
                sec=f"{metrics['elapsed_s']:.1f}",
                refresh=True,
            )
        elif self.config.log_every_eval:
            print(
                f"  eval {metrics['eval']:4d}  Fc={metrics['process_fidelity']:.5f}  "
                f"spread={metrics.get('fidelity_spread', float('nan')):.5f}"
            )
        return cost

    def _cost_and_grad(self, x: np.ndarray) -> tuple[float, np.ndarray]:
        """JAX AD path for SciPy (jac=True)."""
        t0 = time.perf_counter()
        x_j = jnp.asarray(x, dtype=jnp.float64)
        c, g = self._cost_vg(x_j)
        c_f = float(c)
        g_np = np.asarray(g, dtype=float)
        elapsed = time.perf_counter() - t0
        knobs = _x_to_knobs(x)
        metrics = {
            "process_fidelity": float(-c_f),
            "process_fidelities": [],
            "process_fidelity_a": float("nan"),
            "process_fidelity_b": float("nan"),
            "fidelity_spread": float("nan"),
            "fidelity_metric": self.fidelity_metric,
            "spread_penalty_lambda": float(self.config.spread_penalty_lambda),
            "average_gate_fidelity_a": float("nan"),
            "average_gate_fidelity_b": float("nan"),
            "leakage_a": float("nan"),
            "leakage_b": float("nan"),
            "leakage": float("nan"),
            "cost": c_f,
            "target_gate": self.target_gate,
            "elapsed_s": float(elapsed),
            "u_max_mhz": float(np.max(np.abs(knobs))),
            "eval": len(self.eval_history),
            "backend": "jax_ad",
        }
        self.eval_history.append(metrics)
        self._last_eval_metrics = metrics
        if self._pbar is not None:
            evals_this_iter = len(self.eval_history) - self._eval_at_iter_start
            self._pbar.set_description(f"robust GRAPE iter {self._iteration} [jax]")
            self._pbar.set_postfix(
                eval_total=len(self.eval_history),
                eval_iter=evals_this_iter,
                cost=f"{c_f:.4f}",
                sec=f"{elapsed:.1f}",
                refresh=True,
            )
        elif self.config.log_every_eval:
            print(f"  eval {metrics['eval']:4d}  cost={c_f:.5f}  ({elapsed:.1f}s)")
        return c_f, g_np

    def _callback(self, x: np.ndarray) -> None:
        if self.config.use_jax_grad:
            knobs = _x_to_knobs(x)
            _, metrics = self.cost_from_knobs(knobs)
            metrics["eval"] = len(self.eval_history)
            self._last_eval_metrics = metrics
        if self._last_eval_metrics is None:
            return
        row = {"iteration": self._iteration,
               **{k: v for k, v in self._last_eval_metrics.items() if k != "eval"}}
        self.history.append(row)
        if self._pbar is not None:
            self._pbar.update(1)
            self._pbar.set_description(f"robust GRAPE iter {self._iteration + 1}")
            self._pbar.set_postfix(
                Fc=f"{row['process_fidelity']:.4f}",
                spread=f"{row.get('fidelity_spread', float('nan')):.4f}",
                evals=len(self.eval_history),
                refresh=True,
            )
        else:
            print(
                f"iter {self._iteration:3d}  Fc={row['process_fidelity']:.5f}  "
                f"spread={row.get('fidelity_spread', float('nan')):.5f}  "
                f"leak={row['leakage']:.5f}"
            )
        self._iteration += 1
        self._eval_at_iter_start = len(self.eval_history)

    def _run_adam(
        self, x0: np.ndarray, bounds: list[tuple[float, float]]
    ) -> np.ndarray:
        """Optax Adam on the same batched robust cost as L-BFGS (Phase 5 mirror)."""
        import optax

        lo = np.array([b[0] for b in bounds], dtype=float)
        hi = np.array([b[1] for b in bounds], dtype=float)

        x = jnp.asarray(x0, dtype=jnp.float64)
        opt = optax.adam(self.config.adam_lr)
        opt_state = opt.init(x)

        print(
            f"\nStarting Adam (robust batch): steps={self.config.adam_steps}, "
            f"lr={self.config.adam_lr}"
        )
        print("  Compiling first step...")

        @jax.jit
        def step(x, opt_state):
            c, g = self._cost_vg(x)
            updates, opt_state = opt.update(g, opt_state, x)
            x = optax.apply_updates(x, updates)
            x = jnp.clip(x, lo, hi)
            return x, opt_state, c

        x, opt_state, c = step(x, opt_state)
        print(f"step 0 cost={float(c):.8f}")

        history_every = max(1, int(self.config.adam_steps) // 20)
        for i in range(1, int(self.config.adam_steps)):
            x, opt_state, c = step(x, opt_state)
            if i % history_every == 0 or i == int(self.config.adam_steps) - 1:
                knobs = _x_to_knobs(np.asarray(x))
                _, metrics = self.cost_from_knobs(knobs)
                metrics["eval"] = len(self.eval_history)
                metrics["cost"] = float(c)
                self.eval_history.append(metrics)
                self.history.append(
                    {
                        "iteration": i,
                        **{k: v for k, v in metrics.items() if k != "eval"},
                    }
                )
                print(
                    f"  step {i:4d}  cost={float(c):.8f}  "
                    f"Fc={metrics['process_fidelity']:.5f}  "
                    f"spread={metrics.get('fidelity_spread', float('nan')):.5f}"
                )
        return _x_to_knobs(np.asarray(x))

    def evaluate_seed(self) -> dict:
        _, metrics = self.cost_from_knobs(self.flat_knobs_seed)
        return metrics

    def run(self) -> RobustGrapeResult:
        shifts_s = ", ".join(f"{s:+.4g}" for s in self.shifts)
        weights_s = ", ".join(f"{w:.3f}" for w in self.weights)
        print("Fidelity metrics available:")
        for key, desc in FIDELITY_METRICS.items():
            marker = " <-- selected" if key == self.fidelity_metric else ""
            print(f"  {key:18s}  {desc}{marker}")
        print(
            f"\nTarget gate: {self.target_gate}  (fixed)  |  "
            f"N={len(self.shifts)} shifts = [{shifts_s}] MHz  |  "
            f"weights = ({weights_s})  |  metric = {self.fidelity_metric}"
        )
        if self.fidelity_metric == "mean_minus_spread":
            print(f"  spread_penalty_lambda = {self.config.spread_penalty_lambda:.4g}")
        seed_metrics = self.evaluate_seed()
        print("Seed metrics:")
        _print_metrics(seed_metrics, self.shifts)

        flat_knobs_opt = self.flat_knobs_seed.copy()
        scipy_result = None

        if self.config.optimize:
            x0 = _knobs_to_x(self.flat_knobs_seed)
            bound = float(self.config.amp_bound_mhz)
            bounds = [(-bound, bound)] * x0.size

            if self.config.use_jax_grad and self.config.optimizer == "adam":
                flat_knobs_opt = self._run_adam(x0, bounds)
                scipy_result = None
            else:
                if self.config.optimizer == "adam":
                    raise ValueError(
                        "optimizer='adam' requires use_jax_grad=True "
                        "(robust Adam uses the batched dynamiqs cost)"
                    )
                if self.config.use_jax_grad:
                    maxfun = int(self.config.maxiter * 30)
                    fun = self._cost_and_grad
                    jac = True
                    print(
                        f"\nStarting L-BFGS-B + JAX AD (robust batch): "
                        f"{self.config.n_flat_knobs} knobs ({x0.size} reals), "
                        f"maxiter={self.config.maxiter}, maxfun={maxfun}"
                    )
                    print(
                        "  Compiling / first value_and_grad may take several minutes..."
                    )
                    _ = self._cost_and_grad(x0)
                else:
                    maxfun = int(
                        self.config.maxiter * (50 + 2 * self.config.n_flat_knobs)
                    )
                    fun = self._cost_x
                    jac = None
                    print(
                        f"\nStarting L-BFGS-B (FD): {self.config.n_flat_knobs} flat knobs "
                        f"({x0.size} reals), maxiter={self.config.maxiter}, maxfun={maxfun}"
                    )
                    print(
                        f"  Each scipy iter ~ {self._n_reals + 1}+ evals, and each eval "
                        f"propagates BOTH detunings (~2x the single-case cost)."
                    )

                self._eval_at_iter_start = len(self.eval_history)
                if self.config.show_progress:
                    self._pbar = tqdm(
                        total=self.config.maxiter,
                        desc="robust GRAPE",
                        unit="iter",
                        dynamic_ncols=True,
                    )
                try:
                    scipy_result = minimize(
                        fun,
                        x0,
                        method="L-BFGS-B",
                        jac=jac,
                        bounds=bounds,
                        callback=self._callback,
                        options={
                            "maxiter": self.config.maxiter,
                            "maxfun": maxfun,
                            "ftol": 1e-15,
                        },
                    )
                finally:
                    if self._pbar is not None:
                        self._pbar.close()
                        self._pbar = None
                flat_knobs_opt = _x_to_knobs(scipy_result.x)
                print(f"\nOptimizer message: {scipy_result.message}")
        else:
            print("\noptimize=False: seed metrics only (no L-BFGS-B).")

        _, final_metrics = self.cost_from_knobs(flat_knobs_opt)
        cr_half_opt = self.assemble_half(flat_knobs_opt)

        print("\nFinal metrics:")
        _print_metrics(final_metrics, self.shifts)

        return RobustGrapeResult(
            config=self.config,
            shifts_mhz=list(self.shifts),
            weights=self.weights,
            target_gate=self.target_gate,
            flat_knobs_seed=self.flat_knobs_seed.copy(),
            flat_knobs_opt=flat_knobs_opt,
            cr_half_seed=self.cr_half_seed.copy(),
            cr_half_opt=cr_half_opt,
            half_slices=self.half_slices,
            seed_metrics=seed_metrics,
            final_metrics=final_metrics,
            history=list(self.history),
            eval_history=list(self.eval_history),
            scipy_result=scipy_result,
            exps=self.exps,
        )


def _print_metrics(m: dict, shifts: list[float]) -> None:
    fs = m.get("process_fidelities")
    if not fs:
        fs = [
            m.get("process_fidelity_a", float("nan")),
            m.get("process_fidelity_b", float("nan")),
        ]
    spread = m.get("fidelity_spread", _fidelity_spread(fs))
    parts = "  ".join(
        f"F[{i}]({sh:+.4g})={fi:.5f}"
        for i, (sh, fi) in enumerate(zip(shifts, fs))
    )
    print(
        f"  target={m.get('target_gate', '?')}  "
        f"F_comb={m['process_fidelity']:.5f}  "
        f"{parts}  "
        f"spread={spread:.5f}  "
        f"leak={m['leakage']:.5f}"
    )


def optimize_robust_cr_grape(
    zz_shift_mhz: float = 0.2,
    shifts_mhz: list[float] | None = None,
    weights: Sequence[float] | None = None,
    fidelity_metric: FidelityMetric = "weighted_mean",
    spread_penalty_lambda: float = 0.3,
    flat_len_ns: float = 84.0,
    n_flat_knobs: int = 46,
    seed_amp_mhz: float = 32.0,
    seed_phase_rad: float = 0.0,
    t_rise_ns: int = 16,
    n_link_samples: int = 8,
    target_gate: str | None = None,
    amp_bound_mhz: float = 48.0,
    maxiter: int = 80,
    qubit_pair: list[int] | None = None,
    n_levels: int = 3,
    n_sub: int = 2,
    optimize: bool = True,
    log_every_eval: bool = False,
    exps: list[CR_len_sweep] | None = None,
    results_dir: str | None = None,
    save: bool = True,
    use_jax_grad: bool = False,
    optimizer: str = "lbfgs",
    adam_lr: float = 0.02,
    adam_steps: int = 200,
    evolution: str = "comp",
) -> RobustGrapeResult:
    """User-facing entry point for robust (multi-detuning) echoed CR GRAPE.

    Target frequencies are ``+/- zz_shift_mhz/2`` unless an explicit
    ``shifts_mhz`` list of any length ``N >= 1`` is given. Combined fidelity
    is set by ``fidelity_metric`` (see ``FIDELITY_METRICS``). Weights default
    to equal ``1/N``.

    Set ``use_jax_grad=True`` for one dynamiqs experiment with batched frames
    and SciPy ``jac=True`` (L-BFGS) or ``optimizer='adam'`` (optax).
    """
    config = RobustCRGrapeConfig(
        flat_len_ns=flat_len_ns,
        n_flat_knobs=n_flat_knobs,
        seed_amp_mhz=seed_amp_mhz,
        seed_phase_rad=seed_phase_rad,
        t_rise_ns=t_rise_ns,
        n_link_samples=n_link_samples,
        zz_shift_mhz=zz_shift_mhz,
        shifts_mhz=shifts_mhz,
        weights=weights,
        fidelity_metric=fidelity_metric,
        spread_penalty_lambda=spread_penalty_lambda,
        target_gate=target_gate,
        amp_bound_mhz=amp_bound_mhz,
        maxiter=maxiter,
        qubit_pair=qubit_pair or [1, 2],
        n_levels=n_levels,
        n_sub=n_sub,
        optimize=optimize,
        log_every_eval=log_every_eval,
        results_dir=results_dir,
        use_jax_grad=use_jax_grad,
        optimizer=optimizer,
        adam_lr=adam_lr,
        adam_steps=adam_steps,
        evolution=evolution,
    )
    opt = RobustCRGrapeOptimizer(config, exps=exps)
    result = opt.run()
    if save:
        result.save(config.results_dir)
    return result
