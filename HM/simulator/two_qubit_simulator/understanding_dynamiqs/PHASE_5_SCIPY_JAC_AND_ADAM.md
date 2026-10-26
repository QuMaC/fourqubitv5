# Phase 5 — SciPy `jac=` (and optional Adam)

Instructions only. You type the code. Phase 4 is done in substance:

- `evolve_comp` matches propagator columns  
- `grape_cost` matches NumPy / full-`U` cost  
- `jax.value_and_grad(grape_cost)` returns a sensible gradient (~1% vs adaptive-ODE FD)

This phase does **not** invent new physics. It plugs that gradient into the optimizer you already have, so L-BFGS-B stops finite-differencing 92 knobs.

Parent: `DYNAMIQS_GRAPE_MIGRATION.md` §3.15, Phase 5 checklist.  
Siblings: `PHASE_0` … `PHASE_4_GRAPE_COST_AND_GRAD.md`.

**Not in Phase 5:** robust length-2 frames (`PHASE_6`), transfer functions, GPU, rewriting QuTiP GRAPE to JAX.

---

## 0. Decisions locked


| #   | Decision                                                                                                                                                                     |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Keep **QuTiP GRAPE** working (NumPy cost, SciPy FD) when `engine="qutip"`.                                                                                                   |
| 2   | Dynamiqs path uses Phase 4 `grape_cost` + AD when you opt in.                                                                                                                |
| 3   | Prefer SciPy `jac=True` with a function that returns `(cost, grad)` — **one** `value_and_grad` per eval, not separate `_cost_x` + `_jac_x` (that would double the ODE work). |
| 4   | Rich metrics (F_zx90, leakage plots, tqdm) stay on a **non-differentiated** forward (`cost_from_knobs` / `propagate`), mainly in `callback`.                                 |
| 5   | `optimizer: "lbfgs"` or `"adam"`; default `"lbfgs"`. Adam requires `use_jax_grad=True`.                                                                                      |
| 6   | Shrink `maxfun` formula: drop the `2 * n_flat_knobs` FD tax.                                                                                                                 |


---

## 1. What I would have implemented, in order


| Step | File                                                              | What                                                                                                      |
| ---- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 1    | `optimization/cr_grape.py`                                        | `CRGrapeConfig`: `use_jax_grad`, `optimizer`, `adam_lr`, `adam_steps`                                     |
| 2    | same                                                              | `CRGrapeOptimizer.__init`__: if dynamiqs + `use_jax_grad`, build `GrapeStatics` + jitted `value_and_grad` |
| 3    | same                                                              | `_cost_and_grad_x` → `(float, ndarray)`; wire `minimize(..., jac=True)`                                   |
| 4    | same                                                              | Fix `maxfun`; progress text no longer says “finite-diff gradient” on the JAX path                         |
| 5    | same                                                              | Optional `_run_adam` branch                                                                               |
| 6    | `optimize_echoed_cr_grape`                                        | Pass new kwargs through                                                                                   |
| 7    | **new** `optimization/optimization_tests/test_grape_scipy_jac.py` | Short run: eval count ≪ FD; F does not crash; seed→a few iters                                            |


When the smoke test prints `PHASE 5 OK`, stop.

---

## 2. Why this phase exists (x-ray)

### 2.1 What SciPy does today (no `jac`)

```text
each L-BFGS iteration
  ≈ (2 * n_reals + 1) calls to _cost_x     ← finite-diff gradient
  + a few more for line search
```

With 46 complex knobs → 92 reals → **~185 ODE propagations per iteration** just for the gradient, before line search. That is why a bar sitting on “iter 0” for ages is normal.

### 2.2 What SciPy does with AD

```text
each need for (cost, grad)
  → one value_and_grad(grape_cost)     ← ~2× one forward (forward + reverse)
  + line search may call a few more costs
```

Roughly **~2 physics forwards per gradient**, not ~185. Same L-BFGS math; different ∂C/∂x source.

### 2.3 What must not break

- `engine="qutip"` + old `minimize` without jac (FD).  
- `optimize=False` seed-only path.  
- Saving `GrapeResult`, plots, looped GRAPE.  
- Callback still shows F / leak (from a metrics forward, not from `grad`).

---

## 3. Files you will touch

```text
optimization/cr_grape.py                 # main work
optimization/grape_cost_jax.py           # already done (Phase 4); only import
optimization/optimization_tests/test_grape_scipy_jac.py   # NEW
```

Optional: `pip install optax` in `qumac-env` before the Adam section.

Do **not** edit QuTiP engine. Do **not** change `fidelity.py` formulas.

---

## 3.5 Where every piece goes (read this before typing)

Your standing rule for these MDs: **say exactly where to insert**, not only what the code is. Map:


| Piece                                          | Where in `cr_grape.py`                                                                                                          |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Config fields (`use_jax_grad`, …)              | Inside `CRGrapeConfig` dataclass, with the other fields                                                                         |
| `_build_grape_statics`                         | **Module-level** function, **above** `class CRGrapeOptimizer` (same area as `_build_default_exp`)                               |
| JAX init block (`_jax_statics`, `_cost_vg`, …) | Inside `CRGrapeOptimizer.__init__`, **immediately after** `self.u_target_comp = u_target_comp`, **before** `self.history = ...` |
| `_cost_and_grad_x`                             | **Class method.** Insert **immediately after** the existing `_cost_x` method ends, **before** `_callback`                       |
| `_callback` edit                               | **Edit in place** the existing `_callback` (do not add a second one)                                                            |
| `_run_adam`                                    | **Class method.** Insert **immediately after** `_callback` ends, **before** `evaluate_seed`                                     |
| `run()` branch                                 | **Edit in place** the existing `if self.config.optimize:` block inside `run`                                                    |
| `optimize_echoed_cr_grape` kwargs              | **Edit in place** that function + the `CRGrapeConfig(...)` call inside it                                                       |
| Smoke test                                     | **New file** `optimization/optimization_tests/test_grape_scipy_jac.py`                                                          |


Class method order after you are done should look like:

```text
assemble_half
propagate
metrics
cost_from_knobs
_cost_x                 # existing FD / NumPy
_cost_and_grad_x        # NEW — insert here
_callback               # existing; edit for jax metrics
_run_adam               # NEW — insert here
evaluate_seed
run                     # edit optimize branch
```

---

## 4. Step 1 — config knobs

**ADD** to `CRGrapeConfig`:

```python
@dataclass
class CRGrapeConfig:
    # ... existing fields ...
    use_jax_grad: bool = False
    """If True, require dynamiqs engine and use grape_cost + AD for L-BFGS/Adam."""

    optimizer: str = "lbfgs"
    """'lbfgs' (SciPy L-BFGS-B) or 'adam' (Optax). Adam ignored unless use_jax_grad."""

    adam_lr: float = 1e-2
    adam_steps: int = 200
    """Used only when optimizer='adam'."""

    evolution: str = "comp"
    """Passed into GrapeStatics: 'comp' | 'full'. Default evolve_comp."""
```

### 4.1 Syntax / logic

`**use_jax_grad=False` by default**  
Old scripts keep FD QuTiP/dynamiqs-NumPy behaviour. Opt in explicitly.

**Dynamiqs without `use_jax_grad`**  
Still allowed: Phase 1 parity path / NumPy timeline + `run_propagator` + SciPy FD. Slower, but valid.

`**use_jax_grad=True` + `engine="qutip"**`  
`raise ValueError` in `__init__`. QuTiP has no tape.

`**optimizer="adam"` + `use_jax_grad=False**`  
`raise ValueError`. Adam needs the JAX gradient.

---

## 5. Step 2 — build JAX statics once in `__init__`

**WHERE (imports):** Top of `cr_grape.py`, with the other imports.

```python
import jax
import jax.numpy as jnp

from HM.simulator.two_qubit_simulator.engine.pulses_jax import _templates_1ns
from HM.simulator.two_qubit_simulator.optimization.grape_cost_jax import (
    GrapeStatics,
    grape_cost,
)
```

**WHERE (`_build_grape_statics`):** Module-level function, **above** `class CRGrapeOptimizer` (near `_build_default_exp`). Not a method.

```python
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
```

**In `CRGrapeOptimizer.__init__`, after targets exist:**

**WHERE:** After `self.u_target_comp = u_target_comp`, **before** `self.history = []` (and the other bookkeeping fields).

```python
        self._jax_statics: GrapeStatics | None = None
        self._cost_vg = None  # jitted (x,) -> (cost, grad)

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
```

### 5.1 Syntax notes

**Detect dynamiqs**  
Cleanest long-term: `self.exp.engine == "dynamiqs"` if that attribute exists on `CR_len_sweep` / device base. Class-name check works today. Pick one; be consistent.

**Close over `sim` and `statics`**  
Same as Phase 4 test. `statics` is frozen; `sim` holds frames. Do not put `sim` inside `x`.

**When to build statics**  
After `self.target_gate`, `self.u_target_`*, `self._x_pi` exist. Order matters.

`**jax.jit(jax.value_and_grad(_cost_only))`**  
Returns a function `(x,) -> (cost, grad)`. Both are JAX arrays. SciPy needs NumPy/`float` at the boundary — convert in `_cost_and_grad_x`.

**First compile**  
First `self._cost_vg(x0)` can take minutes on CPU. Print a one-liner before the first call: `"Compiling JAX cost+grad (first call)..."`.

---

## 6. Step 3 — SciPy boundary: `(cost, grad)` in one call

### 6.1 Why not separate `_cost_x` and `_jac_x`?

If you pass:

```python
minimize(self._cost_x, x0, jac=self._jac_x, ...)
```

SciPy often calls **both**. Each call runs a full ODE (+ reverse for jac). You pay **~2×** what you need.

SciPy allows:

```python
minimize(fun, x0, jac=True, ...)
# fun(x) must return (f, g)
```

### 6.2 ADD `_cost_and_grad_x` — insert location

**WHERE:** Inside `class CRGrapeOptimizer`, **immediately after** the full existing `_cost_x` method, **immediately before** `def _callback`.

In your file right now that means: after the `return cost` of `_cost_x` (around line 496), before `def _callback` (around line 498).

Do **not** replace `_cost_x`. Keep `_cost_x` for the FD / QuTiP path. Only **add** the new method between `_cost_x` and `_callback`.

```python
    def _cost_and_grad_x(self, x: np.ndarray) -> tuple[float, np.ndarray]:
        """JAX AD path for SciPy (jac=True)."""
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
```

`_cost_x` stays as it already is in the file (NumPy / FD). Do not paste a stub over it.

### 6.3 Syntax notes

`**F = -cost` when `leakage_weight == 0`**  
True for both NumPy and JAX cost formulas you use. Safe for the progress bar. If `leakage_weight ≠ 0`, either run a metrics forward or leave F as nan until callback.

`**dtype=jnp.float64`**  
Match x64. SciPy passes float64 `x`.

**Do not `jax.grad` inside `_cost_and_grad_x` without using the jitted `value_and_grad`**  
You already compiled `_cost_vg`. Call it.

**Bounds**  
L-BFGS-B still gets `bounds=[(-amp, amp)] * n`. AD does not remove box constraints.

---

## 7. Step 4 — callback metrics (non-AD forward)

`jax.value_and_grad` only returns a scalar (+ grad). Your plots want `process_fidelity_zx_90`, leakage, etc.

**WHERE:** Edit the **existing** `_callback` method in place (still after `_cost_and_grad_x`, before `evaluate_seed`). Do not create a second `_callback`.

At the **top** of `_callback`, before the usual history append, add the JAX metrics refresh:

```python
    def _callback(self, x: np.ndarray) -> None:
        if self.config.use_jax_grad:
            # One NumPy-style forward for logging only (no grad)
            knobs = _x_to_knobs(x)
            _, metrics = self.cost_from_knobs(knobs)
            metrics["eval"] = len(self.eval_history)
            self._last_eval_metrics = metrics
        if self._last_eval_metrics is None:
            return
        # ... keep the rest of your existing _callback body unchanged ...
```

**Keep `_callback` roughly as today**, but when on the JAX path refresh rich metrics **once per L-BFGS iteration** (callback fires once per iter, not per FD probe).

### 7.1 Logic


| Call                            | Frequency (AD path)  | Work                                         |
| ------------------------------- | -------------------- | -------------------------------------------- |
| `_cost_and_grad_x`              | every SciPy fun eval | 1× (fwd+bwd) JAX                             |
| `_callback` → `cost_from_knobs` | once per L-BFGS iter | 1× NumPy/dynamiqs forward for pretty metrics |


That extra forward per iter is cheap vs old FD.

**Consistency note:** `cost_from_knobs` still uses NumPy assemble + `_propagator_from_timeline`. Forward F should match JAX F at ~1e-5 (you already proved that). Logging can use either.

---

## 8. Step 5 — rewrite `run()` branch

**WHERE:** Inside `def run(self)`, edit the existing `if self.config.optimize:` block in place. Do not add a second `run`.

**REPLACE** that optimize block conceptually with:

```python
        if self.config.optimize:
            x0 = _knobs_to_x(self.flat_knobs_seed)
            bound = float(self.config.amp_bound_mhz)
            bounds = [(-bound, bound)] * x0.size

            if self.config.use_jax_grad and self.config.optimizer == "adam":
                flat_knobs_opt = self._run_adam(x0, bounds)
                scipy_result = None
            else:
                if self.config.use_jax_grad:
                    # AD: line search only — no 2*n_reals FD tax
                    maxfun = int(self.config.maxiter * 30)
                    fun = self._cost_and_grad_x
                    jac = True
                    print(
                        f"\nStarting L-BFGS-B + JAX AD: {self.config.n_flat_knobs} knobs "
                        f"({x0.size} reals), maxiter={self.config.maxiter}, maxfun={maxfun}"
                    )
                    print("  Compiling / first value_and_grad may take several minutes...")
                    _ = self._cost_and_grad_x(x0)  # warm compile before minimize
                else:
                    maxfun = int(
                        self.config.maxiter * (50 + 2 * self.config.n_flat_knobs)
                    )
                    fun = self._cost_x
                    jac = None
                    print(
                        f"\nStarting L-BFGS-B (FD grad): {self.config.n_flat_knobs} knobs "
                        f"({x0.size} reals), maxiter={self.config.maxiter}, maxfun={maxfun}"
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
                            "ftol": 1e-10,
                        },
                    )
                finally:
                    if self._pbar is not None:
                        self._pbar.close()
                        self._pbar = None
                flat_knobs_opt = _x_to_knobs(scipy_result.x)
                print(f"\nOptimizer message: {scipy_result.message}")
```

### 8.1 `maxfun` explained again


| Mode | Typical evals / iter         | `maxfun` formula                   |
| ---- | ---------------------------- | ---------------------------------- |
| FD   | ~`2*n_reals+1` + line search | `maxiter * (50 + 2*n_knobs)` (old) |
| AD   | ~1–20 (line search)          | `maxiter * 30` (new)               |


If you **keep** the old `maxfun` with AD, nothing bad happens (limit is just huge).  
If you **shrink** to `maxiter` itself, line search can trip `maxfun exceeded` early — that is the footgun.

Warm compile **before** `minimize` so tqdm iter 0 is not “silent compile forever.”

### 8.2 `jac=True` vs `jac=callable`

```python
minimize(fun, x0, jac=True, ...)   # fun returns (f, g)
minimize(fun, x0, jac=jac_fn, ...) # fun returns f; jac_fn returns g
```

Use the first on the JAX path.

---

## 9. Step 6 — optional Adam (`optimizer="adam"`)

`optax` is **not** in `qumac-env` right now. When you want Adam:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/pip install optax
```

### 9.1 ADD `_run_adam`

**WHERE:** Inside `class CRGrapeOptimizer`, **immediately after** `_callback` ends, **immediately before** `def evaluate_seed`.

```python
    def _run_adam(self, x0: np.ndarray, bounds: list[tuple[float, float]]) -> np.ndarray:
        import optax  # local import so QuTiP-only users need not install

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

        # warm
        x, opt_state, c = step(x, opt_state)
        print(f"  step 0  cost={float(c):.6f}")

        history_every = max(1, self.config.adam_steps // 20)
        for i in range(1, int(self.config.adam_steps)):
            x, opt_state, c = step(x, opt_state)
            if i % history_every == 0 or i == self.config.adam_steps - 1:
                knobs = _x_to_knobs(np.asarray(x))
                _, metrics = self.cost_from_knobs(knobs)
                metrics["eval"] = len(self.eval_history)
                metrics["cost"] = float(c)
                self.eval_history.append(metrics)
                self.history.append({"iteration": i, **_last_eval_metrics_copy(metrics)})
                print(
                    f"  step {i:4d}  cost={float(c):.6f}  "
                    f"F={metrics['process_fidelity']:.5f}"
                )
        return _x_to_knobs(np.asarray(x))
```

### 9.2 Syntax notes

`**optax.apply_updates**`  
Adam proposes `updates` (usually −lr·scaled grad). `x = x + updates` under the hood.

`**jnp.clip(x, lo, hi)**`  
Poor man’s box constraints. L-BFGS-B handles bounds more carefully; Adam + clip is good enough as a backup.

**Closing over `self._cost_vg` inside `jit`**  
Works if `_cost_vg` is already a jitted function. If JAX complains about `self`, build `step` with `cost_vg = self._cost_vg` as a local:

```python
        cost_vg = self._cost_vg

        @jax.jit
        def step(x, opt_state):
            c, g = cost_vg(x)
            ...
```

**Adam is not “faster GRAPE.”**  
It is a different update rule. Use it when L-BFGS stalls or for experimentation. Default stays L-BFGS.

---

## 10. Step 7 — wire the public API

**ADD** kwargs to `optimize_echoed_cr_grape`:

**WHERE:** Edit the existing `optimize_echoed_cr_grape` function at the bottom of `cr_grape.py` in place — signature + the `CRGrapeConfig(...)` construction inside it.

```python
def optimize_echoed_cr_grape(
    ...
    use_jax_grad: bool = False,
    optimizer: str = "lbfgs",
    adam_lr: float = 1e-2,
    adam_steps: int = 200,
    evolution: str = "comp",
    ...
):
    config = CRGrapeConfig(
        ...
        use_jax_grad=use_jax_grad,
        optimizer=optimizer,
        adam_lr=adam_lr,
        adam_steps=adam_steps,
        evolution=evolution,
    )
```

**Caller example (dynamiqs + AD):**

```python
exp = CR_len_sweep(
    qubit_pair=[1, 2],
    echoed_cr=True,
    n_levels=3,
    engine="dynamiqs",
    n_sub=14,
    cr_pulse_params={...},
)
result = optimize_echoed_cr_grape(
    flat_len_ns=184.0,
    n_flat_knobs=46,
    maxiter=20,              # short smoke
    use_jax_grad=True,
    optimizer="lbfgs",
    exp=exp,
    save=False,
)
```

---

## 11. Step 8 — smoke test

**ADD** `optimization/optimization_tests/test_grape_scipy_jac.py`:

```python
"""Phase 5: L-BFGS-B with jac=True uses far fewer evals than FD."""
from __future__ import annotations

import numpy as np

from HM.simulator.two_qubit_simulator.engine import two_q_pulse_sim_dynamiqs  # noqa: F401
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    CRGrapeConfig,
    CRGrapeOptimizer,
    DEFAULT_CR_PULSE_PARAMS,
)


def test_jax_lbfgs_smoke() -> None:
    exp = CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        engine="dynamiqs",
        n_sub=14,
        cr_pulse_params={
            **DEFAULT_CR_PULSE_PARAMS,
            "amp_mhz": -32.0,
            "phase_rad": 0.0,
            "t_rise_ns": 16,
        },
    )
    cfg = CRGrapeConfig(
        flat_len_ns=184.0,
        n_flat_knobs=46,
        seed_amp_mhz=-32.0,
        seed_phase_rad=0.0,
        maxiter=3,                 # tiny
        use_jax_grad=True,
        optimizer="lbfgs",
        evolution="comp",
        show_progress=True,
        optimize=True,
    )
    opt = CRGrapeOptimizer(cfg, exp=exp)
    seed_F = opt.evaluate_seed()["process_fidelity"]
    result = opt.run()
    final_F = result.final_metrics["process_fidelity"]
    n_eval = len(result.eval_history)

    print("seed F", seed_F, "final F", final_F, "n_eval", n_eval)

    # FD would need ≳ 3 * (2*92+1) ≈ 555 evals minimum for 3 iters of pure FD grad.
    # AD should be far below that (warm + line searches).
    assert n_eval < 80, f"too many evals for AD path: {n_eval}"
    # Do not require F improved in 3 iters; only that the loop ran.
    assert result.scipy_result is not None
    print("PHASE 5 OK")


if __name__ == "__main__":
    test_jax_lbfgs_smoke()
```

### 11.1 What pass / fail means

**Pass:** `PHASE 5 OK`, `n_eval` small, SciPy returns a result, no tape errors.

**Fail — `n_eval` huge (~hundreds):** you still FD somehow (`use_jax_grad` not wired, or `jac` not set).

**Fail — `maxfun exceeded` at iter 5:** `maxfun` too small; use `maxiter * 30`.

**Fail — QuTiP + `use_jax_grad`:** should raise in `__init__` with a clear message.

**Fail — cost nan / grad nan:** compile / dims / `asqarray(..., dims=)` regression; revisit Phase 4.

**Fail — Adam `ImportError`:** install optax or skip Adam test.

Run:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python \
  HM/simulator/two_qubit_simulator/optimization/optimization_tests/test_grape_scipy_jac.py
```

First run: long compile. Second run in the same process: faster.

---

## 12. Progress-bar / eval counting semantics

Today’s tqdm assumes FD: “eval_iter ≈ n_reals for gradient phase.”

On the JAX path, rewrite descriptions to `[jax]` / `[line search]` without assuming 185 evals. Simple approach: stop splitting “gradient vs line search” phases when `use_jax_grad`; just show `cost` and `eval_total`.

---

## 13. What you are explicitly not doing


| Temptation                      | Why not in Phase 5                                      |
| ------------------------------- | ------------------------------------------------------- |
| Delete NumPy `cost_from_knobs`  | Still needed for QuTiP, seed metrics, callback richness |
| Force all GRAPE through JAX     | Default stays FD-safe                                   |
| Robust ±Δ in the same PR        | Phase 6                                                 |
| Prove FD vs AD to 1e-6 in SciPy | Already settled in Phase 4                              |
| GPU                             | Later                                                   |


---

## 14. Module map when done

```text
CRGrapeConfig
    use_jax_grad, optimizer, adam_*, evolution

CRGrapeOptimizer
    _jax_statics, _cost_vg
    _cost_and_grad_x   # AD → (f, g)
    _cost_x            # FD / NumPy (unchanged role)
    _run_adam          # optional
    run()              # branches

grape_cost_jax.py      # unchanged from Phase 4
```

---

## 15. Stop condition

Phase 5 is **done** when:

1. `test_grape_scipy_jac.py` prints `PHASE 5 OK`.
2. With `use_jax_grad=True`, `n_eval ≪` FD expectation for the same `maxiter`.
3. QuTiP / `use_jax_grad=False` still runs the old path.
4. (Optional) Adam runs a few steps after `pip install optax` without error.

Then stop. Phase 6 is robust batching + `F_comb`, a later MD.

---

## 16. Suggested typing order

1. Config fields + `__init__` guards + `_build_grape_statics`.
2. `_cost_vg` + `_cost_and_grad_x` + warm call in a tiny script (print cost/grad norm).
3. Wire `minimize(..., jac=True)` + new `maxfun`.
4. Callback rich metrics.
5. Smoke test.
6. Adam only if you care this week.

If step 2 works and step 3 fails, the bug is SciPy wiring, not physics.