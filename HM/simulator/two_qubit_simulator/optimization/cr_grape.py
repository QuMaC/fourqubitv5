"""GRAPE-style optimization for echoed CR gates on the two-qubit pulse simulator.

Only the flat-top knobs of one CR half are optimized.  Rise and fall use the lab
``rise_arr`` / ``fall_arr`` templates, rescaled to meet the first/last
``n_link_samples`` flat samples (default 8; see ``assemble_cr_half_from_flat_knobs``).
sequence is ``+u → Xπ → −u → Xπ``.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any
import matplotlib

# Headless / long batch runs: TkAgg GC can abort with Tcl_AsyncDelete.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import jax
import jax.numpy as jnp
from scipy.optimize import minimize
from tqdm import tqdm

from HM.simulator.two_qubit_simulator.engine.pulses import (
    assemble_cr_half_from_flat_knobs,
    expand_samples_held_nsub,
    scale_sample_index,
    seed_flat_knobs_from_calibrated_cr,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import _templates_1ns
from HM.simulator.two_qubit_simulator.optimization.grape_cost_jax import(
    GrapeStatics,
    grape_cost
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    average_gate_fidelity,
    embed_in_full,
    gate_metrics,
    leakage_from_comp,
    process_fidelity,
    zx_target_unitary,
)

DEFAULT_CR_PULSE_PARAMS = {
    "amp_mhz": -32.0,
    "t_rise_ns": 16,
    "phase_rad": 2.724,
}


def _default_target_gate(amp_mhz: float) -> str:
    return "zx_m90" if float(amp_mhz) < 0 else "zx_90"


def _knobs_to_x(flat_knobs: np.ndarray) -> np.ndarray:
    flat_knobs = np.asarray(flat_knobs, dtype=complex).reshape(-1)
    return np.column_stack([flat_knobs.real, flat_knobs.imag]).ravel()


def _x_to_knobs(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float).reshape(-1)
    if x.size % 2:
        raise ValueError("control vector must have even length (I/Q pairs)")
    pairs = x.reshape(-1, 2)
    return pairs[:, 0] + 1j * pairs[:, 1]


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return _to_jsonable(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    return value


def cr_half_duration_ns(flat_len_ns: float, t_rise_ns: float | int) -> float:
    t_rise = int(round(float(t_rise_ns)))
    from Helper_Functions.helper_functionsv2 import fall_arr, rise_arr

    n_rise = len(rise_arr(t_rise))
    n_fall = len(fall_arr(t_rise))
    return float(n_rise + flat_len_ns + n_fall)


def echoed_gate_duration_ns(
    flat_len_ns: float,
    t_rise_ns: float | int,
    x_pi_len_ns: float,
) -> float:
    return float(2 * cr_half_duration_ns(flat_len_ns, t_rise_ns) + 2 * x_pi_len_ns)


@dataclass
class CRGrapeConfig:
    """User-facing GRAPE configuration."""

    flat_len_ns: float = 122.0
    n_flat_knobs: int = 61
    seed_amp_mhz: float = -21.0
    seed_phase_rad: float = 2.724
    t_rise_ns: int = 16
    n_link_samples: int = 8
    target_gate: str | None = None
    amp_bound_mhz: float = 48.0
    leakage_weight: float = 0.0
    maxiter: int = 80
    qubit_pair: list[int] = field(default_factory=lambda: [1, 2])
    n_levels: int = 3
    optimize: bool = True
    log_every_eval: bool = False
    show_progress: bool = True
    results_dir: str | None = None
    use_jax_grad: bool = False
    """if true, use jax for gradient computation, l-bfgs-b or Adam"""
    optimizer: str = "lbfgs"
    """lbfgs-b or Adam"""
    adam_lr: float = 0.02
    adam_steps: int = 200

    """ used only when optimizer = 'adam'"""

    evolution: str = "comp"
    """comp or full, comp is for computational subspace and full is for full dimension space"""

    def resolved_target_gate(self) -> str:
        if self.target_gate is not None:
            return str(self.target_gate)
        return _default_target_gate(self.seed_amp_mhz)


def _build_grape_statics(opt: "CRGrapeOptimizer") -> GrapeStatics:
    cfg = opt.config
    sim = opt.exp.simulator
    rise, fall = _templates_1ns(int(cfg.t_rise_ns))
    n_flat = int(round(float(cfg.flat_len_ns) / float(opt.exp.dt_sample_ns)))
    if n_flat % int(cfg.n_flat_knobs) != 0:
        raise ValueError(
            f"n_flat={n_flat} must be divisible by n_flat_knobs={cfg.n_flat_knobs}"
        )
    if abs(float(opt.exp.dt_sample_ns) - 1.0) > 1e-12:
        raise ValueError("JAX GRAPE locks dt_sample_ns=1.0")

    return GrapeStatics(
        rise=rise,
        fall=fall,
        n_flat=n_flat,
        n_link_samples=int(cfg.n_link_samples),
        x_pi=jnp.asarray(opt._x_pi),
        U_target_full=jnp.asarray(opt.u_target_full),
        U_target_comp=jnp.asarray(opt.u_target_comp),
        comp_indices=tuple(sim.comp_idx),
        channel_names=("q1_drive", "q2_drive", "cr_drive"),
        evolution=str(cfg.evolution),
        leakage_weight=float(cfg.leakage_weight),
    )

@dataclass
class GrapeResult:
    """Outcome of a GRAPE run."""

    config: CRGrapeConfig
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
    exp: CR_len_sweep | None = None

    @property
    def total_echoed_duration_ns(self) -> float:
        assert self.exp is not None
        x_pi_len = self.exp.x_pi_pulse_params["length_ns"]
        return echoed_gate_duration_ns(
            self.config.flat_len_ns,
            self.config.t_rise_ns,
            x_pi_len,
        )

    def save(self, directory: str | None = None) -> dict[str, str]:
        directory = directory or self.config.results_dir or _default_results_dir()
        os.makedirs(directory, exist_ok=True)

        json_path = os.path.join(directory, "cr_grape_result.json")
        npz_path = os.path.join(directory, "cr_grape_pulse.npz")
        conv_png = os.path.join(directory, "cr_grape_convergence.png")
        wf_png = os.path.join(directory, "cr_grape_waveform.png")

        dt = self.exp.dt_sample_ns if self.exp else 1.0
        t_half = np.arange(len(self.cr_half_opt), dtype=float) * dt

        payload = _to_jsonable(
            {
                "config": asdict(self.config),
                "total_echoed_duration_ns": self.total_echoed_duration_ns,
                "half_slices": {
                    k: {"start": v[0], "stop": v[1]} for k, v in self.half_slices.items()
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
        if not self.history:
            return
        iters = [h["iteration"] for h in self.history]
        f_proc = [h["process_fidelity"] for h in self.history]
        leakage = [h["leakage"] for h in self.history]

        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        axes[0].plot(iters, f_proc, "o-", ms=4, lw=1.2, color="tab:cyan")
        axes[0].axhline(self.seed_metrics["process_fidelity"], color="0.5", ls="--", lw=1,
                        label=f"seed F={self.seed_metrics['process_fidelity']:.4f}")
        axes[0].set_ylabel("process F")
        axes[0].set_ylim(0, 1.02)
        axes[0].grid(alpha=0.35)
        axes[0].legend(fontsize=8)

        axes[1].plot(iters, leakage, "o-", ms=4, lw=1.2, color="tab:red")
        axes[1].set_xlabel("optimizer iteration")
        axes[1].set_ylabel("leakage")
        axes[1].grid(alpha=0.35)

        gate = self.config.resolved_target_gate()
        axes[0].set_title(
            f"GRAPE convergence  |  target={gate}  |  flat={self.config.flat_len_ns:.0f} ns  "
            f"|  knobs={self.config.n_flat_knobs}"
        )
        plt.tight_layout()
        plt.savefig(out_png, dpi=160)
        plt.close(fig)

    def plot_waveform(self, out_png: str) -> None:
        dt = self.exp.dt_sample_ns if self.exp else 1.0
        n_sub = int(self.exp.simulator.n_sub) if self.exp else 2
        rs, re = self.half_slices["rise"]
        fs, fe = self.half_slices["flat"]
        ds, de = self.half_slices["fall"]

        t, seed_exp = expand_samples_held_nsub(self.cr_half_seed, dt, n_sub)
        _, opt_exp = expand_samples_held_nsub(self.cr_half_opt, dt, n_sub)
        rs_e, re_e = scale_sample_index(rs, n_sub), scale_sample_index(re, n_sub)
        fs_e, fe_e = scale_sample_index(fs, n_sub), scale_sample_index(fe, n_sub)
        ds_e, de_e = scale_sample_index(ds, n_sub), scale_sample_index(de, n_sub)

        fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
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
        axes[0].set_title(
            "CR half envelope: seed vs optimized "
            f"(shaded: rise / flat / fall; each sample held ×{n_sub})"
        )
        fig.text(0.99, 0.01, "blue=rise  orange=flat  purple=fall", ha="right", va="bottom",
                 fontsize=8, color="0.35")
        plt.tight_layout()
        plt.savefig(out_png, dpi=160)
        plt.close(fig)


def _default_results_dir() -> str:
    return os.path.join(
        os.path.dirname(__file__), "optimization_tests", "results"
    )


def _build_default_exp(config: CRGrapeConfig) -> CR_len_sweep:
    cr_pulse_params = {
        **DEFAULT_CR_PULSE_PARAMS,
        "amp_mhz": config.seed_amp_mhz,
        "phase_rad": config.seed_phase_rad,
        "t_rise_ns": config.t_rise_ns,
    }
    return CR_len_sweep(
        qubit_pair=list(config.qubit_pair),
        echoed_cr=True,
        n_levels=config.n_levels,
        cr_pulse_params=cr_pulse_params,
    )


class CRGrapeOptimizer:
    """Optimize flat-top CR knobs against process fidelity."""

    def __init__(
        self,
        config: CRGrapeConfig,
        exp: CR_len_sweep | None = None,
    ):
        self.config = config
        self.exp = exp or _build_default_exp(config)
        if not self.exp.echoed_cr:
            raise ValueError("CRGrapeOptimizer requires echoed_cr=True")

        self.flat_knobs_seed = seed_flat_knobs_from_calibrated_cr(
            n_flat_knobs=config.n_flat_knobs,
            flat_len_ns=config.flat_len_ns,
            amp_mhz=config.seed_amp_mhz,
            phase_rad=config.seed_phase_rad,
            t_rise_ns=config.t_rise_ns,
            dt_ns=self.exp.dt_sample_ns,
        )
        self.cr_half_seed, self.half_slices = assemble_cr_half_from_flat_knobs(
            self.flat_knobs_seed,
            flat_len_ns=config.flat_len_ns,
            t_rise_ns=config.t_rise_ns,
            dt_ns=self.exp.dt_sample_ns,
            n_link_samples=config.n_link_samples,
        )
        self._x_pi = self.exp.build_x_pi()

        if config.target_gate is not None:
            self.target_gate = str(config.target_gate)
        else:
            u_seed = self.propagate(self.flat_knobs_seed)
            self.target_gate = str(gate_metrics(u_seed, gate="best_zx")["zx_gate"])

        dim = self.exp.simulator.dim
        u_target_comp = zx_target_unitary(self.target_gate)
        self.u_target_full = embed_in_full(
            u_target_comp, dim=dim, comp_indices=self.exp.simulator.comp_idx
        )
        self.u_target_comp = u_target_comp

        ### Jax grape statics
        self._jax_statics : GrapeStatics | None = None
        self._cost_vg = None  # jitted (x,) -> (cost, grad)

        eng = getattr(self.exp, "engine", None) or getattr(
            self.exp.simulator, "__class__", type("x", (), {})
        ).__name__
        # Prefer an explicit flag on the experiment:
        is_dynamiqs = type(self.exp.simulator).__name__.endswith("Dynamiqs")

        if config.use_jax_grad:
            if not is_dynamiqs:
                raise ValueError(
                    "use_jax_grad=True requires CR_len_sweep(..., engine='dynamiqs')"
                )
            if config.optimizer not in ("lbfgs", "adam"):
                raise ValueError(f"unknown optimizer {config.optimizer!r}")
            self._jax_statics = _build_grape_statics(self)
            sim = self.exp.simulator
            statics = self._jax_statics

            def _cost_only(x):
                return grape_cost(x, sim, statics)

            # jit after first definition; first call compiles (slow once)
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
            dt_ns=self.exp.dt_sample_ns,
            n_link_samples=self.config.n_link_samples,
        )
        if slices != self.half_slices:
            self.half_slices = slices
        return wf

    def propagate(self, flat_knobs: np.ndarray) -> np.ndarray:
        cr_plus = self.assemble_half(flat_knobs)
        timeline = self.exp._build_timeline_from_cr_half(cr_plus, x_pi=self._x_pi)
        return self.exp._propagator_from_timeline(timeline)

    def metrics(self, U: np.ndarray) -> dict:
        m = gate_metrics(U, gate=self.target_gate)
        m["process_fidelity_zx_90"] = process_fidelity(
            U,
            embed_in_full(zx_target_unitary("zx_90"), dim=U.shape[0]),
        )
        m["process_fidelity_zx_m90"] = process_fidelity(
            U,
            embed_in_full(zx_target_unitary("zx_m90"), dim=U.shape[0]),
        )
        return m

    def cost_from_knobs(self, flat_knobs: np.ndarray) -> tuple[float, dict]:
        t0 = time.perf_counter()
        U = self.propagate(flat_knobs)
        f_proc = process_fidelity(U, self.u_target_full)
        leakage = leakage_from_comp(U)
        f_avg = average_gate_fidelity(U, self.u_target_comp)
        cost = -(f_proc - self.config.leakage_weight * leakage)
        elapsed = time.perf_counter() - t0
        metrics = {
            "process_fidelity": float(f_proc),
            "average_gate_fidelity": float(f_avg),
            "leakage": float(leakage),
            "cost": float(cost),
            "target_gate": self.target_gate,
            "elapsed_s": float(elapsed),
            "u_max_mhz": float(np.max(np.abs(flat_knobs))),
        }
        m_full = self.metrics(U)
        metrics["process_fidelity_zx_90"] = float(m_full["process_fidelity_zx_90"])
        metrics["process_fidelity_zx_m90"] = float(m_full["process_fidelity_zx_m90"])
        return cost, metrics

    def _cost_x(self, x: np.ndarray) -> float:
        knobs = _x_to_knobs(x)
        cost, metrics = self.cost_from_knobs(knobs)
        metrics["eval"] = len(self.eval_history)
        self.eval_history.append(metrics)
        self._last_eval_metrics = metrics
        if self._pbar is not None:
            evals_this_iter = len(self.eval_history) - self._eval_at_iter_start
            if evals_this_iter <= self._n_reals + 1:
                phase = "gradient"
            else:
                phase = "line search"
            self._pbar.set_description(f"GRAPE iter {self._iteration} [{phase}]")
            self._pbar.set_postfix(
                eval_total=len(self.eval_history),
                eval_iter=evals_this_iter,
                F=f"{metrics['process_fidelity']:.4f}",
                sec=f"{metrics['elapsed_s']:.1f}",
                refresh=True,
            )
        elif self.config.log_every_eval:
            print(
                f"  eval {metrics['eval']:4d}  F={metrics['process_fidelity']:.5f}  "
                f"leak={metrics['leakage']:.5f}  cost={cost:.5f}"
            )
        return cost

    def _cost_and_grad(self, x: np.ndarray) -> tuple[float, np.ndarray]:
        """ so scipy would end up caling the evolution twice if we had
        minimize(self._cost_x, jac=self._jac_x), instead we can pass 
        minimize(fun, x0, jac=True) but fun would have to return both cost and gradient"""
        t0 = time.perf_counter()
        x_j = jnp.asarray(x, dtype=jnp.float64)
        c, g = self._cost_vg(x_j)
        c_f = float(c)
        g_np = np.asarray(g, dtype=float)
        elapsed = time.perf_counter() - t0

        # Lightweight log for eval_history (no second ODE if you skip rich metrics)
        knobs = _x_to_knobs(x)
        metrics = {
            "process_fidelity": float(-c_f) if self.config.leakage_weight == 0.0 else float("nan"),
            # When leakage_weight==0, cost = -F, so F = -cost.
            "average_gate_fidelity": float("nan"),
            "leakage": float("nan"),
            "cost": c_f,
            "target_gate": self.target_gate,
            "elapsed_s": float(elapsed),
            "u_max_mhz": float(np.max(np.abs(knobs))),
            "eval": len(self.eval_history),
            "backend": "jax_ad",
        }
        # Optional: fill rich metrics only every N evals — see section 7.
        self.eval_history.append(metrics)
        self._last_eval_metrics = metrics

        if self._pbar is not None:
            evals_this_iter = len(self.eval_history) - self._eval_at_iter_start
            self._pbar.set_description(f"GRAPE iter {self._iteration} [jax]")
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
            # One NumPy-style forward for logging only (no grad)
            knobs = _x_to_knobs(x)
            _, metrics = self.cost_from_knobs(knobs)
            metrics["eval"] = len(self.eval_history)
            self._last_eval_metrics = metrics
        if self._last_eval_metrics is None:
            return
        if self._last_eval_metrics is None:
            return
        row = {"iteration": self._iteration, **_last_eval_metrics_copy(self._last_eval_metrics)}
        self.history.append(row)
        if self._pbar is not None:
            self._pbar.update(1)
            self._pbar.set_description(f"GRAPE iter {self._iteration + 1}")
            self._pbar.set_postfix(
                F=f"{row['process_fidelity']:.4f}",
                leak=f"{row['leakage']:.4f}",
                evals=len(self.eval_history),
                refresh=True,
            )
        else:
            print(
                f"iter {self._iteration:3d}  F={row['process_fidelity']:.5f}  "
                f"F_zx90={row['process_fidelity_zx_90']:.5f}  "
                f"F_zxm90={row['process_fidelity_zx_m90']:.5f}  "
                f"leak={row['leakage']:.5f}"
            )
        self._iteration += 1
        self._eval_at_iter_start = len(self.eval_history)

    def _run_adam(
        self, x0: np.ndarray, bounds: list[tuple[float, float]]
    ) -> np.ndarray:
        """Run Adam optimization"""
        import optax

        lo = np.array([b[0] for b in bounds], dtype=float)
        hi = np.array([b[1] for b in bounds], dtype=float)

        x = jnp.asarray(x0, dtype=jnp.float64)
        opt = optax.adam(self.config.adam_lr)
        opt_state = opt.init(x)

        print(
            f"\nStarting Adam: steps={self.config.adam_steps}, lr={self.config.adam_lr}"
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

        history_every = max(1, self.config.adam_steps//20)
        for i in range(1, int(self.config.adam_steps)):
            x, opt_state, c = step(x, opt_state)
            if i%history_every == 0 or i == self.config.adam_steps-1:
                knobs = _x_to_knobs(np.asarray(x))
                _, metrics = self.cost_from_knobs(knobs)
                metrics["eval"] = len(self.eval_history)
                metrics["cost"] = float(c)
                self.eval_history.append(metrics)
                self.history.append({
                    "iteration": i,
                    **_last_eval_metrics_copy(metrics)
                })
                print(
                    f"  step {i:4d}  cost={float(c):.8f}  "
                    f"F={metrics['process_fidelity']:.5f}"
                )
        return _x_to_knobs(np.asarray(x))

    def evaluate_seed(self) -> dict:
        _, metrics = self.cost_from_knobs(self.flat_knobs_seed)
        return metrics

    def run(self) -> GrapeResult:
        print(f"Target gate: {self.target_gate}  (fixed for entire optimization)")
        seed_metrics = self.evaluate_seed()
        print("Seed metrics:")
        _print_metrics(seed_metrics)

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
                if self.config.use_jax_grad: #this defaults to lbfgs-b
                    maxfun = int(self.config.maxiter*30)
                    fun = self._cost_and_grad
                    jac = True
                    print(
                        f"\nStarting L-BFGS-B + JAX AD: {self.config.n_flat_knobs} knobs "
                        f"({x0.size} reals), maxiter={self.config.maxiter}, maxfun={maxfun}"
                    )
                    print("  Compiling / first value_and_grad may take several minutes...")
                    _ = self._cost_and_grad(x0) #warm compile before minimize?
                else:  
                    
                    
                    maxfun = int(self.config.maxiter * (50 + 2 * self.config.n_flat_knobs))
                    fun = self._cost_x
                    jac = None
                    print(
                        f"\nStarting L-BFGS-B (FD grad): {self.config.n_flat_knobs} knobs "
                        f"({x0.size} reals), maxiter={self.config.maxiter}, maxfun={maxfun}"
                    )

                    

                    print(
                        f"  Each scipy iter ≈ {self._n_reals + 1}+ evals "
                        f"(~{self._n_reals + 1} for finite-diff gradient, then line search). "
                        f"Iter 0 can take many minutes — watch eval_iter in the bar."
                    )


                    self._eval_at_iter_start = len(self.eval_history)
                    if self.config.show_progress:
                        self._pbar = tqdm(
                            total=self.config.maxiter,
                            desc="GRAPE",
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
        _print_metrics(final_metrics)

        return GrapeResult(
            config=self.config,
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
            exp=self.exp,
        )


def _last_eval_metrics_copy(metrics: dict) -> dict:
    return {k: v for k, v in metrics.items() if k != "eval"}


def _print_metrics(m: dict) -> None:
    print(
        f"  target={m.get('target_gate', '?')}  "
        f"F_proc={m['process_fidelity']:.5f}  "
        f"F_avg={m['average_gate_fidelity']:.5f}  "
        f"F_zx90={m.get('process_fidelity_zx_90', float('nan')):.5f}  "
        f"F_zxm90={m.get('process_fidelity_zx_m90', float('nan')):.5f}  "
        f"leakage={m['leakage']:.5f}"
    )


def optimize_echoed_cr_grape(
    flat_len_ns: float = 184.0,
    n_flat_knobs: int = 46,
    seed_amp_mhz: float = -32.0,
    seed_phase_rad: float = 2.724,
    t_rise_ns: int = 16,
    n_link_samples: int = 8,
    target_gate: str | None = None,
    amp_bound_mhz: float = 48.0,
    leakage_weight: float = 0.0,
    maxiter: int = 80,
    qubit_pair: list[int] | None = None,
    n_levels: int = 3,
    optimize: bool = True,
    log_every_eval: bool = False,
    exp: CR_len_sweep | None = None,
    results_dir: str | None = None,
    save: bool = True,
    use_jax_grad: bool = False,
    optimizer: str = "lbfgs",
    adam_lr: float = 0.02,
    adam_steps: int = 200,
    evolution: str = "comp",
) -> GrapeResult:
    """User-facing entry point for echoed CR GRAPE.

    Parameters
    ----------
    flat_len_ns
        Flat-top duration of **one** CR half (|R| min default: 184 ns).
    n_flat_knobs
        Number of piecewise-constant complex knobs on the flat top.
    exp
        Optional pre-built ``CR_len_sweep`` (custom qubit pair, J, n_levels, …).
        Default builds the standard Q1–Q2 echoed CR experiment from lab JSONs.
    optimize
        If False, evaluate seed fidelity only (Phase 0 check).
    """
    config = CRGrapeConfig(
        flat_len_ns=flat_len_ns,
        n_flat_knobs=n_flat_knobs,
        seed_amp_mhz=seed_amp_mhz,
        seed_phase_rad=seed_phase_rad,
        t_rise_ns=t_rise_ns,
        n_link_samples=n_link_samples,
        target_gate=target_gate,
        amp_bound_mhz=amp_bound_mhz,
        leakage_weight=leakage_weight,
        maxiter=maxiter,
        qubit_pair=qubit_pair or [1, 2],
        n_levels=n_levels,
        optimize=optimize,
        log_every_eval=log_every_eval,
        results_dir=results_dir,
        use_jax_grad=use_jax_grad,
        optimizer=optimizer,
        adam_lr=adam_lr,
        adam_steps=adam_steps,
        evolution=evolution,
    )
    optimizer = CRGrapeOptimizer(config, exp=exp)
    result = optimizer.run()
    if save:
        result.save(config.results_dir)
    return result


@dataclass
class LoopedGrapeConfig:
    """Configuration for repeated GRAPE runs from the same seed."""

    grape_config: CRGrapeConfig
    n_cycles: int = 30
    save_individual_cycles: bool = True
    checkpoint_after_each_cycle: bool = True
    results_dir: str | None = None


@dataclass
class LoopedGrapeResult:
    """Outcome of multiple independent GRAPE runs from an identical seed."""

    config: LoopedGrapeConfig
    results: list[GrapeResult]

    @property
    def n_cycles(self) -> int:
        return len(self.results)

    @property
    def cr_halves_opt(self) -> np.ndarray:
        """Stacked optimized CR-half waveforms, shape ``(n_cycles, n_samples)``."""
        return np.stack([r.cr_half_opt for r in self.results], axis=0)

    @property
    def cr_half_avg(self) -> np.ndarray:
        return np.mean(self.cr_halves_opt, axis=0)

    @property
    def flat_knobs_stack(self) -> np.ndarray:
        return np.stack([r.flat_knobs_opt for r in self.results], axis=0)

    @property
    def flat_knobs_avg(self) -> np.ndarray:
        return np.mean(self.flat_knobs_stack, axis=0)

    def metrics_table(self, *, include_average: bool = True) -> list[dict]:
        rows = []
        for i, r in enumerate(self.results, start=1):
            m = dict(r.final_metrics)
            m["cycle"] = i
            m["label"] = f"cycle_{i:02d}"
            rows.append(m)
        if include_average and rows:
            avg = {
                "cycle": "avg",
                "label": "average",
                "process_fidelity": float(np.mean([r["process_fidelity"] for r in rows])),
                "average_gate_fidelity": float(
                    np.mean([r["average_gate_fidelity"] for r in rows])
                ),
                "process_fidelity_zx_90": float(
                    np.mean([r["process_fidelity_zx_90"] for r in rows])
                ),
                "process_fidelity_zx_m90": float(
                    np.mean([r["process_fidelity_zx_m90"] for r in rows])
                ),
                "leakage": float(np.mean([r["leakage"] for r in rows])),
                "target_gate": rows[0]["target_gate"],
            }
            rows.append(avg)
        return rows

    def print_fidelity_table(self, *, include_average: bool = True) -> None:
        rows = self.metrics_table(include_average=include_average)
        header = (
            f"{'cycle':>5}  {'target':>7}  {'F_proc':>8}  {'F_avg':>8}  "
            f"{'F_zx90':>8}  {'F_zxm90':>8}  {'leakage':>8}"
        )
        print("\n" + header)
        print("-" * len(header))
        for row in rows:
            cycle = row["cycle"]
            cycle_s = f"{cycle:>5}" if isinstance(cycle, int) else f"{cycle:>5}"
            print(
                f"{cycle_s}  "
                f"{row.get('target_gate', '?'):>7}  "
                f"{row['process_fidelity']:8.5f}  "
                f"{row['average_gate_fidelity']:8.5f}  "
                f"{row['process_fidelity_zx_90']:8.5f}  "
                f"{row['process_fidelity_zx_m90']:8.5f}  "
                f"{row['leakage']:8.5f}"
            )
        print()

    def plot_all_waveforms(self, out_png: str) -> None:
        if not self.results:
            return
        exp = self.results[0].exp
        dt = exp.dt_sample_ns if exp else 1.0
        n_sub = int(exp.simulator.n_sub) if exp else 2
        ref = self.results[0]
        rs, re = ref.half_slices["rise"]
        fs, fe = ref.half_slices["flat"]
        ds, de = ref.half_slices["fall"]
        t, _ = expand_samples_held_nsub(ref.cr_half_opt, dt, n_sub)
        rs_e, re_e = scale_sample_index(rs, n_sub), scale_sample_index(re, n_sub)
        fs_e, fe_e = scale_sample_index(fs, n_sub), scale_sample_index(fe, n_sub)
        ds_e, de_e = scale_sample_index(ds, n_sub), scale_sample_index(de, n_sub)

        fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
        cmap = plt.cm.viridis(np.linspace(0.15, 0.85, self.n_cycles))

        for ax, component in zip(axes, ("I", "Q")):
            for i, (r, color) in enumerate(zip(self.results, cmap)):
                y0 = r.cr_half_opt.real if component == "I" else r.cr_half_opt.imag
                _, y = expand_samples_held_nsub(y0, dt, n_sub)
                ax.plot(
                    t, y, color=color, lw=0.9, alpha=0.55,
                    label=f"cycle {i + 1}" if i < 3 or i == self.n_cycles - 1 else None,
                )
            avg0 = (
                self.cr_half_avg.real if component == "I" else self.cr_half_avg.imag
            )
            _, avg_y = expand_samples_held_nsub(avg0, dt, n_sub)
            ax.plot(t, avg_y, color="black", lw=2.2, ls="-", label="average", zorder=5)
            ax.axvspan(t[rs_e], t[re_e - 1] if re_e > rs_e else t[rs_e], color="tab:blue", alpha=0.06)
            ax.axvspan(t[fs_e], t[fe_e - 1] if fe_e > fs_e else t[fs_e], color="tab:orange", alpha=0.06)
            ax.axvspan(t[ds_e], t[de_e - 1] if de_e > ds_e else t[ds_e], color="tab:purple", alpha=0.06)
            ax.set_ylabel(f"{component} (MHz)")
            ax.grid(alpha=0.35)
            ax.legend(fontsize=7, loc="upper right", ncol=2)

        axes[1].set_xlabel(
            f"time within one CR half (ns)  |  held at n_sub={n_sub}  "
            f"(dt_sub={dt / n_sub:g} ns)"
        )
        axes[0].set_title(
            f"Looped GRAPE — {self.n_cycles} cycle(s) + average "
            f"(each sample held ×{n_sub})"
        )
        plt.tight_layout()
        plt.savefig(out_png, dpi=160)
        plt.close(fig)

    def _resolved_directory(self, directory: str | None) -> str:
        directory = (
            directory
            or self.config.results_dir
            or self.config.grape_config.results_dir
            or _default_results_dir()
        )
        os.makedirs(directory, exist_ok=True)
        return directory

    def save_cycle_npz(self, cycle: int, result: GrapeResult, directory: str | None = None) -> str:
        """Save one completed cycle immediately (crash-safe unit of work)."""
        directory = self._resolved_directory(directory)
        cycles_dir = os.path.join(directory, "cycles")
        os.makedirs(cycles_dir, exist_ok=True)

        dt = result.exp.dt_sample_ns if result.exp else 1.0
        t_half = np.arange(result.cr_half_opt.size, dtype=float) * dt
        cycle_npz = os.path.join(cycles_dir, f"cr_grape_cycle_{cycle:02d}.npz")
        np.savez(
            cycle_npz,
            t_ns=t_half,
            cycle=cycle,
            flat_knobs_opt=result.flat_knobs_opt,
            cr_half_opt_I=result.cr_half_opt.real,
            cr_half_opt_Q=result.cr_half_opt.imag,
            process_fidelity=result.final_metrics["process_fidelity"],
            average_gate_fidelity=result.final_metrics["average_gate_fidelity"],
            leakage=result.final_metrics["leakage"],
        )
        return cycle_npz

    def save(
        self,
        directory: str | None = None,
        *,
        status: str = "complete",
        quiet: bool = False,
    ) -> dict[str, str]:
        """Write combined artifacts for all completed cycles so far."""
        if not self.results:
            return {}
        directory = self._resolved_directory(directory)

        json_path = os.path.join(directory, "cr_grape_looped_result.json")
        npz_path = os.path.join(directory, "cr_grape_looped_all.npz")
        wf_png = os.path.join(directory, "cr_grape_looped_waveforms.png")

        ref = self.results[0]
        dt = ref.exp.dt_sample_ns if ref.exp else 1.0
        t_half = np.arange(ref.cr_half_opt.size, dtype=float) * dt

        halves = self.cr_halves_opt
        halves_with_avg = np.vstack([halves, self.cr_half_avg[np.newaxis, :]])
        knobs_with_avg = np.vstack(
            [self.flat_knobs_stack, self.flat_knobs_avg[np.newaxis, :]]
        )

        payload = _to_jsonable(
            {
                "status": status,
                "completed_cycles": self.n_cycles,
                "target_cycles": self.config.n_cycles,
                "looped_config": {
                    "n_cycles": self.config.n_cycles,
                    "grape_config": asdict(self.config.grape_config),
                },
                "metrics_table": self.metrics_table(),
                "half_slices": {
                    k: {"start": v[0], "stop": v[1]}
                    for k, v in ref.half_slices.items()
                },
            }
        )
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        np.savez(
            npz_path,
            t_ns=t_half,
            n_cycles=self.n_cycles,
            cr_half_opt_I=halves_with_avg.real,
            cr_half_opt_Q=halves_with_avg.imag,
            flat_knobs_opt_real=knobs_with_avg.real,
            flat_knobs_opt_imag=knobs_with_avg.imag,
            is_average=np.array(
                [False] * self.n_cycles + [True], dtype=bool
            ),
            rise_start=ref.half_slices["rise"][0],
            flat_start=ref.half_slices["flat"][0],
            flat_stop=ref.half_slices["flat"][1],
            fall_start=ref.half_slices["fall"][0],
        )

        paths = {"json": json_path, "npz": npz_path, "waveform_png": wf_png}

        if self.config.save_individual_cycles:
            cycles_dir = os.path.join(directory, "cycles")
            os.makedirs(cycles_dir, exist_ok=True)
            for i, r in enumerate(self.results, start=1):
                cycle_npz = os.path.join(cycles_dir, f"cr_grape_cycle_{i:02d}.npz")
                if os.path.exists(cycle_npz):
                    paths[f"cycle_{i:02d}_npz"] = cycle_npz
                    continue
                saved = self.save_cycle_npz(i, r, directory)
                paths[f"cycle_{i:02d}_npz"] = saved

        self.plot_all_waveforms(wf_png)
        if not quiet:
            for p in paths.values():
                print(f"Saved {p}")
        return paths

    def save_checkpoint(
        self,
        directory: str | None = None,
        *,
        completed_cycle: int | None = None,
    ) -> dict[str, str]:
        """Persist partial progress after a cycle finishes."""
        status = (
            "complete"
            if self.n_cycles >= self.config.n_cycles
            else "in_progress"
        )
        paths = self.save(directory, status=status, quiet=True)
        if completed_cycle is not None:
            m = self.results[-1].final_metrics
            print(
                f"Checkpoint cycle {completed_cycle}/{self.config.n_cycles}  "
                f"F_proc={m['process_fidelity']:.5f}  "
                f"leakage={m['leakage']:.5f}  "
                f"-> {paths.get('json', '?')}"
            )
        return paths


def run_looped_grape(
    n_cycles: int = 30,
    grape_config: CRGrapeConfig | None = None,
    exp: CR_len_sweep | None = None,
    save_individual_cycles: bool = True,
    checkpoint_after_each_cycle: bool = True,
    results_dir: str | None = None,
    save: bool = True,
    **grape_kwargs,
) -> LoopedGrapeResult:
    """Run ``n_cycles`` independent GRAPE optimizations from the same seed.

    Each cycle builds a fresh ``CRGrapeOptimizer`` (same config / seed params).
    Results are summarized in a terminal fidelity table, overlaid I/Q plot, and
    a combined ``.npz`` whose last row is the waveform average.
    """
    if grape_config is None:
        grape_config = CRGrapeConfig(**grape_kwargs)
    if results_dir is not None:
        grape_config.results_dir = results_dir

    loop_config = LoopedGrapeConfig(
        grape_config=grape_config,
        n_cycles=n_cycles,
        save_individual_cycles=save_individual_cycles,
        checkpoint_after_each_cycle=checkpoint_after_each_cycle,
        results_dir=results_dir,
    )

    print(
        f"Looped GRAPE: {n_cycles} cycles from identical seed  "
        f"(flat={grape_config.flat_len_ns:.0f} ns, knobs={grape_config.n_flat_knobs})"
    )
    if save and checkpoint_after_each_cycle:
        print("Checkpointing after each cycle -> results survive interruption.")

    results: list[GrapeResult] = []
    for cycle in range(1, n_cycles + 1):
        print(f"\n{'=' * 60}\nCycle {cycle}/{n_cycles}\n{'=' * 60}")
        optimizer = CRGrapeOptimizer(grape_config, exp=exp)
        result = optimizer.run()
        results.append(result)

        if save and checkpoint_after_each_cycle:
            partial = LoopedGrapeResult(config=loop_config, results=list(results))
            if save_individual_cycles:
                partial.save_cycle_npz(cycle, result, results_dir)
            partial.save_checkpoint(results_dir, completed_cycle=cycle)

    looped = LoopedGrapeResult(config=loop_config, results=results)
    looped.print_fidelity_table()
    if save and not checkpoint_after_each_cycle:
        looped.save(results_dir)
    elif save:
        looped.save(results_dir, status="complete")
    return looped


