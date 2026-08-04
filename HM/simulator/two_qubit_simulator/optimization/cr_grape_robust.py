"""Robust (two-detuning) GRAPE for echoed CR gates.

One CR-half pulse is optimized so it works well at *two* target-qubit
frequencies at once (e.g. the target shifted by a spectator's ZZ interaction).
The two frequencies are modelled by shifting the target qubit's ``frame_MHz``
by ``+shift`` / ``-shift`` (see ``_apply_target_freq_shift``); nothing in the
engine changes.

Combined fidelity metrics (set ``fidelity_metric`` in the config or test script):

- ``weighted_mean``: ``w_a * F_a + w_b * F_b`` (default weights 0.5, 0.5)
- ``geometric_mean``: ``sqrt(F_a * F_b)``
- ``mean_minus_spread``: ``w_a * F_a + w_b * F_b - lambda * |F_a - F_b|``

The optimized pulse, seed, per-case convergence, and combined/per-case
fidelities are saved (NPZ mirrors ``cr_grape.py`` + robust extras, filename
carries a timestamp and the ZZ shift).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from tqdm import tqdm

from HM.simulator.two_qubit_simulator.engine.pulses import (
    assemble_cr_half_from_flat_knobs,
    seed_flat_knobs_from_calibrated_cr,
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
    "weighted_mean": "Weighted arithmetic mean: w_a*F_a + w_b*F_b",
    "geometric_mean": "Geometric mean: sqrt(F_a * F_b)",
    "mean_minus_spread": (
        "Weighted mean minus spread penalty: w_a*F_a + w_b*F_b - lambda*|F_a-F_b|"
    ),
}


def combine_robust_fidelities(
    f_a: float,
    f_b: float,
    metric: FidelityMetric,
    weights: tuple[float, float] = (0.5, 0.5),
    spread_penalty_lambda: float = 0.3,
) -> float:
    """Combine per-detuning process fidelities into one scalar objective."""
    wa, wb = weights
    if metric == "weighted_mean":
        return float(wa * f_a + wb * f_b)
    if metric == "geometric_mean":
        return float(np.sqrt(max(f_a, 0.0) * max(f_b, 0.0)))
    if metric == "mean_minus_spread":
        weighted = wa * f_a + wb * f_b
        return float(weighted - spread_penalty_lambda * abs(f_a - f_b))
    raise ValueError(
        f"Unknown fidelity_metric {metric!r}; "
        f"choose one of {list(FIDELITY_METRICS)}"
    )


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
    """Configuration for two-detuning (robust) echoed CR GRAPE."""

    flat_len_ns: float = 84.0
    n_flat_knobs: int = 46
    seed_amp_mhz: float = 32.0
    seed_phase_rad: float = 0.0
    t_rise_ns: int = 16
    n_link_samples: int = 8

    # Target-frequency spread. ``shifts_mhz`` (an explicit pair) takes priority;
    # otherwise the two cases are +/- zz_shift_mhz / 2.
    zz_shift_mhz: float = 0.2
    shifts_mhz: list[float] | None = None
    weights: tuple[float, float] = (0.5, 0.5)
    fidelity_metric: FidelityMetric = "weighted_mean"
    spread_penalty_lambda: float = 0.3

    target_gate: str | None = None
    amp_bound_mhz: float = 48.0
    maxiter: int = 80
    qubit_pair: list[int] = field(default_factory=lambda: [1, 2])
    n_levels: int = 3
    optimize: bool = True
    show_progress: bool = True
    log_every_eval: bool = False
    results_dir: str | None = None

    def resolved_shifts(self) -> list[float]:
        if self.shifts_mhz is not None:
            s = [float(v) for v in self.shifts_mhz]
            if len(s) != 2:
                raise ValueError("shifts_mhz must have exactly two entries")
            return s
        half = 0.5 * float(self.zz_shift_mhz)
        return [-half, half]

    def resolved_weights(self) -> tuple[float, float]:
        w = np.asarray(self.weights, dtype=float)
        if w.size != 2 or np.any(w < 0):
            raise ValueError("weights must be two non-negative numbers")
        total = float(w.sum())
        if total <= 0:
            return (0.5, 0.5)
        return (float(w[0] / total), float(w[1] / total))

    def zz_span_mhz(self) -> float:
        s = self.resolved_shifts()
        return float(s[1] - s[0])

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
    """Outcome of a robust (two-detuning) GRAPE run."""

    config: RobustCRGrapeConfig
    shifts_mhz: list[float]
    weights: tuple[float, float]
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
            seed_F_a=float(self.seed_metrics["process_fidelity_a"]),
            seed_F_b=float(self.seed_metrics["process_fidelity_b"]),
            seed_F_combined=float(self.seed_metrics["process_fidelity"]),
            final_F_a=float(self.final_metrics["process_fidelity_a"]),
            final_F_b=float(self.final_metrics["process_fidelity_b"]),
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
        f_a = [self.seed_metrics["process_fidelity_a"]] + [
            h["process_fidelity_a"] for h in self.history
        ]
        f_b = [self.seed_metrics["process_fidelity_b"]] + [
            h["process_fidelity_b"] for h in self.history
        ]
        f_c = [self.seed_metrics["process_fidelity"]] + [
            h["process_fidelity"] for h in self.history
        ]

        fig, ax = plt.subplots(figsize=(9, 5.5))
        sa, sb = self.shifts_mhz
        ax.plot(iters, f_a, "o-", ms=4, lw=1.3, color="tab:blue",
                label=f"F_a (shift {sa:+.4g} MHz)")
        ax.plot(iters, f_b, "s-", ms=4, lw=1.3, color="tab:orange",
                label=f"F_b (shift {sb:+.4g} MHz)")
        metric = self.config.resolved_fidelity_metric()
        ax.plot(
            iters,
            f_c,
            "^-",
            ms=4,
            lw=1.6,
            color="black",
            label=fidelity_metric_label(metric),
        )
        ax.set_xlabel("optimizer iteration (0 = seed)")
        ax.set_ylabel("process fidelity")
        all_f = f_a + f_b + f_c
        lo, hi = min(all_f), max(all_f)
        pad = max((hi - lo) * 0.08, 1e-4)
        ax.set_ylim(lo - pad, min(1.0005, hi + pad))
        ax.grid(alpha=0.35)
        ax.legend(fontsize=9, loc="lower right")
        metric_desc = FIDELITY_METRICS[metric]
        ax.set_title(
            f"Robust GRAPE convergence  |  target={self.target_gate}  |  "
            f"ZZ span={self.config.zz_span_mhz():.4g} MHz  |  "
            f"flat={self.config.flat_len_ns:.0f} ns  knobs={self.config.n_flat_knobs}\n"
            f"metric={metric}  ({metric_desc})"
        )
        plt.tight_layout()
        plt.savefig(out_png, dpi=160)
        plt.close(fig)

    def plot_waveform(self, out_png: str) -> None:
        dt = self.exps[0].dt_sample_ns if self.exps else 1.0
        t = np.arange(len(self.cr_half_opt), dtype=float) * dt
        rs, re = self.half_slices["rise"]
        fs, fe = self.half_slices["flat"]
        ds, de = self.half_slices["fall"]

        fig, axes = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
        for ax, key in zip(axes, ("I", "Q")):
            seed_y = self.cr_half_seed.real if key == "I" else self.cr_half_seed.imag
            opt_y = self.cr_half_opt.real if key == "I" else self.cr_half_opt.imag
            ax.plot(t, seed_y, color="0.65", lw=1.2, ls="--", label=f"seed {key} (MHz)")
            ax.plot(t, opt_y, color="tab:green", lw=1.6, label=f"opt {key} (MHz)")
            ax.axvspan(t[rs], t[re - 1] if re > rs else t[rs], color="tab:blue", alpha=0.08)
            ax.axvspan(t[fs], t[fe - 1] if fe > fs else t[fs], color="tab:orange", alpha=0.08)
            ax.axvspan(t[ds], t[de - 1] if de > ds else t[ds], color="tab:purple", alpha=0.08)
            ax.set_ylabel(f"{key} (MHz)")
            ax.grid(alpha=0.35)
            ax.legend(fontsize=8, loc="upper right")

        axes[1].set_xlabel("time within one CR half (ns)")
        sa, sb = self.shifts_mhz
        s = self.seed_metrics
        f = self.final_metrics
        summary = (
            f"target={self.target_gate}   ZZ span={self.config.zz_span_mhz():.4g} MHz\n"
            f"seed:  F_comb={s['process_fidelity']:.5f}   "
            f"F_a({sa:+.4g})={s['process_fidelity_a']:.5f}   "
            f"F_b({sb:+.4g})={s['process_fidelity_b']:.5f}\n"
            f"final: F_comb={f['process_fidelity']:.5f}   "
            f"F_a({sa:+.4g})={f['process_fidelity_a']:.5f}   "
            f"F_b({sb:+.4g})={f['process_fidelity_b']:.5f}"
        )
        axes[0].set_title("Robust CR half: seed vs optimized (shaded: rise / flat / fall)")
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
        cr_pulse_params=cr_pulse_params,
    )
    return _apply_target_freq_shift(exp, shift_mhz)


class RobustCRGrapeOptimizer:
    """Optimize one CR-half pulse against a combined two-detuning fidelity."""

    def __init__(
        self,
        config: RobustCRGrapeConfig,
        exps: list[CR_len_sweep] | None = None,
    ):
        self.config = config
        self.shifts = config.resolved_shifts()
        self.weights = config.resolved_weights()
        self.fidelity_metric = config.resolved_fidelity_metric()

        if exps is not None:
            if len(exps) != 2:
                raise ValueError("exps must be a list of exactly two experiments")
            self.exps = list(exps)
        else:
            self.exps = [_build_shifted_exp(config, s) for s in self.shifts]
        for e in self.exps:
            if not e.echoed_cr:
                raise ValueError("RobustCRGrapeOptimizer requires echoed_cr=True")

        self.dt = self.exps[0].dt_sample_ns

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
            u_seed_a = self._propagate_one(0, self.flat_knobs_seed)
            self.target_gate = str(gate_metrics(u_seed_a, gate="best_zx")["zx_gate"])

        dim = self.exps[0].simulator.dim
        comp_idx = self.exps[0].simulator.comp_idx
        self.u_target_comp = zx_target_unitary(self.target_gate)
        self.u_target_full = embed_in_full(
            self.u_target_comp, dim=dim, comp_indices=comp_idx
        )

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

        f_a = per_case[0]["process_fidelity"]
        f_b = per_case[1]["process_fidelity"]
        f_combined = combine_robust_fidelities(
            f_a,
            f_b,
            self.fidelity_metric,
            weights=self.weights,
            spread_penalty_lambda=self.config.spread_penalty_lambda,
        )
        wa, wb = self.weights
        leak_combined = wa * per_case[0]["leakage"] + wb * per_case[1]["leakage"]
        cost = -f_combined
        elapsed = time.perf_counter() - t0

        metrics = {
            "process_fidelity": float(f_combined),
            "process_fidelity_a": float(f_a),
            "process_fidelity_b": float(f_b),
            "fidelity_spread": float(abs(f_a - f_b)),
            "fidelity_metric": self.fidelity_metric,
            "spread_penalty_lambda": float(self.config.spread_penalty_lambda),
            "average_gate_fidelity_a": per_case[0]["average_gate_fidelity"],
            "average_gate_fidelity_b": per_case[1]["average_gate_fidelity"],
            "leakage_a": per_case[0]["leakage"],
            "leakage_b": per_case[1]["leakage"],
            "leakage": float(leak_combined),
            "cost": float(cost),
            "target_gate": self.target_gate,
            "elapsed_s": float(elapsed),
            "u_max_mhz": float(np.max(np.abs(flat_knobs))),
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
                Fa=f"{metrics['process_fidelity_a']:.4f}",
                Fb=f"{metrics['process_fidelity_b']:.4f}",
                eval_iter=evals_this_iter,
                sec=f"{metrics['elapsed_s']:.1f}",
                refresh=True,
            )
        elif self.config.log_every_eval:
            print(
                f"  eval {metrics['eval']:4d}  Fc={metrics['process_fidelity']:.5f}  "
                f"Fa={metrics['process_fidelity_a']:.5f}  "
                f"Fb={metrics['process_fidelity_b']:.5f}"
            )
        return cost

    def _callback(self, x: np.ndarray) -> None:
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
                Fa=f"{row['process_fidelity_a']:.4f}",
                Fb=f"{row['process_fidelity_b']:.4f}",
                evals=len(self.eval_history),
                refresh=True,
            )
        else:
            print(
                f"iter {self._iteration:3d}  Fc={row['process_fidelity']:.5f}  "
                f"Fa={row['process_fidelity_a']:.5f}  "
                f"Fb={row['process_fidelity_b']:.5f}  leak={row['leakage']:.5f}"
            )
        self._iteration += 1
        self._eval_at_iter_start = len(self.eval_history)

    def evaluate_seed(self) -> dict:
        _, metrics = self.cost_from_knobs(self.flat_knobs_seed)
        return metrics

    def run(self) -> RobustGrapeResult:
        sa, sb = self.shifts
        wa, wb = self.weights
        print("Fidelity metrics available:")
        for key, desc in FIDELITY_METRICS.items():
            marker = " <-- selected" if key == self.fidelity_metric else ""
            print(f"  {key:18s}  {desc}{marker}")
        print(
            f"\nTarget gate: {self.target_gate}  (fixed)  |  "
            f"shifts = [{sa:+.4g}, {sb:+.4g}] MHz  |  weights = ({wa:.2f}, {wb:.2f})  |  "
            f"metric = {self.fidelity_metric}"
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
            print(
                f"\nStarting L-BFGS-B: {self.config.n_flat_knobs} flat knobs "
                f"({x0.size} reals), maxiter={self.config.maxiter}"
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
                    self._cost_x,
                    x0,
                    method="L-BFGS-B",
                    bounds=bounds,
                    callback=self._callback,
                    options={"maxiter": self.config.maxiter, "ftol": 1e-10},
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
    sa, sb = shifts
    spread = m.get("fidelity_spread", abs(m["process_fidelity_a"] - m["process_fidelity_b"]))
    print(
        f"  target={m.get('target_gate', '?')}  "
        f"F_comb={m['process_fidelity']:.5f}  "
        f"F_a({sa:+.4g})={m['process_fidelity_a']:.5f}  "
        f"F_b({sb:+.4g})={m['process_fidelity_b']:.5f}  "
        f"|dF|={spread:.5f}  "
        f"leak={m['leakage']:.5f}"
    )


def optimize_robust_cr_grape(
    zz_shift_mhz: float = 0.2,
    shifts_mhz: list[float] | None = None,
    weights: tuple[float, float] = (0.5, 0.5),
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
    optimize: bool = True,
    log_every_eval: bool = False,
    exps: list[CR_len_sweep] | None = None,
    results_dir: str | None = None,
    save: bool = True,
) -> RobustGrapeResult:
    """User-facing entry point for robust (two-detuning) echoed CR GRAPE.

    The two target frequencies are ``+/- zz_shift_mhz/2`` unless an explicit
    ``shifts_mhz`` pair is given. Combined fidelity is set by
    ``fidelity_metric`` (see ``FIDELITY_METRICS``).
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
        optimize=optimize,
        log_every_eval=log_every_eval,
        results_dir=results_dir,
    )
    optimizer = RobustCRGrapeOptimizer(config, exps=exps)
    result = optimizer.run()
    if save:
        result.save(config.results_dir)
    return result
