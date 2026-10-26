# Phase 6 — Robust GRAPE as batched target frame

**Status: DONE** (2026-08-23). Code is in-tree; smoke printed `PHASE 6 OK` / `ADAM WIRED OK`.

Phase 5 done in substance:

- SciPy `minimize(..., jac=True)` with `_cost_and_grad`
- Optional Adam via optax
- Smoke: L-BFGS + JAX jac reaches F≈0.998 with `PGTOL` in ≪ FD evals

This phase does **not** invent new pulse knobs. It makes **one** dynamiqs experiment evolve the **same** echoed-CR pulse at **two** target frames (`±s`) in one batched solve, then combines `F_a` and `F_b` into one scalar for AD + L-BFGS (default) or Adam (opt-in).

Parent: `DYNAMIQS_GRAPE_MIGRATION.md` §3.5, §3.16, Phase 6 checklist.  
Siblings: `PHASE_0` … `PHASE_5_SCIPY_JAC_AND_ADAM.md`.  
Existing QuTiP robust: `optimization/cr_grape_robust.py` (two experiments + FD) — **kept working**.

**Not in Phase 6:** GPU, 6-qubit, deleting QuTiP robust, transfer functions, rewriting Phase 5 single-frame GRAPE, `evolution="full"` on the robust JAX path.

---

## 0. Decisions locked


| #   | Decision |
| --- | --- |
| 1   | Dynamiqs robust = **one** `CR_len_sweep`, then **once** `set_target_frame(lab_f1 + [+s, -s])`. |
| 2   | QuTiP robust keeps **two** experiments + `_apply_target_freq_shift` until you delete it on purpose. |
| 3   | Shifts are fixed for the run. **Never** call `set_target_frame` inside every cost eval. |
| 4   | Cost scalar = `-(F_comb - w * leak_comb)` with the same `fidelity_metric` choices as NumPy robust. |
| 5   | Prefer **new** `grape_cost_robust` (+ JAX combine) so Phase 5 `grape_cost` stays a scalar-Δ path. |
| 6   | Optimizer wiring mirrors Phase 5: `use_jax_grad` + SciPy `jac=True` (**L-BFGS default**). **Adam wired** via `optimizer="adam"` (same `_cost_vg`; not default). |
| 7   | Flat I/Q bounds stay `amp_bound_mhz=48.0` (same as single-frame). |
| 8   | Robust JAX path locks `evolution="comp"`. |


---

## 1. What was implemented (order)


| Step | File | What | Status |
| ---- | --- | --- | --- |
| 1 | `engine/two_q_pulse_sim_dynamiqs.py` | Harden `set_target_frame` for length-2 `jnp`; doc `evolve_comp` batch shapes | done |
| 2 | `optimization/grape_cost_jax.py` | `combine_robust_fidelities_jax` + `grape_cost_robust` | done |
| 3 | `optimization/cr_grape_robust.py` | Config flags; one exp + frames; `_cost_vg` + `jac=True`; `_cost_from_knobs_batched` | done |
| 4 | same | `_run_adam` + `run()` branch (`optimizer="adam"`) | done |
| 5 | `optimize_robust_cr_grape` | Pass `use_jax_grad`, `optimizer`, `adam_lr`, `adam_steps`, `evolution` | done |
| 6 | **new** `optimization/optimization_tests/test_grape_robust_jax.py` | Batch F vs sequential; short L-BFGS smoke | done |


---

## 2. Why this phase exists (x-ray)

### 2.1 What QuTiP robust does today

```text
build exp_a with frame1 + s_a
build exp_b with frame1 + s_b
each cost eval:
  U_a = propagate(exp_a, knobs)
  U_b = propagate(exp_b, knobs)
  F_comb = combine(F_a, F_b)
```

Correct physics. With FD: roughly **2 × (2 n_reals + 1)** full gates per L-BFGS gradient — twice the Phase 5 pain.

### 2.2 What Phase 6 does

```text
one exp, lab chip
sim.set_target_frame(f1 + jnp.array([s_a, s_b]))   # once in __init__
each cost eval:
  one evolve_comp(timeline)   # H batched → psi shape (2, 4, dim, 1)
  F_a, F_b from batch axis
  F_comb = combine_jax(...)
  cost = -(F_comb - w * leak)
```

One compiled kernel. AD through `F_comb`. SciPy L-BFGS-B with `jac=True` (default), or Optax Adam.

### 2.3 Physics reminder (do not “batch the CR carrier”)

ZZ = shift of the **target** rotating frame. Coupling \(\Delta = f_0 - f_1\) changes. CR envelope on the control line is unchanged. Echoed CR leaves `q2_drive` idle; still install **frame1** (not only a hand-rolled `delta`) so drive detunings stay consistent if that channel is ever on.

---

## 3. Expected shapes (memorize)

2 qutrits → `dim = 9`. Computational batch = 4 kets. Robust = 2 frames.


| Object | Shape |
| --- | --- |
| `frame1` / `delta_qq_MHz` after set | `(2,)` |
| `H(t)` batch (conceptually) | leading axis 2 |
| `psi0` in `evolve_comp` | `(4, 9, 1)` |
| `psi = evolve_comp(...)` with length-2 Δ | **`(2, 4, 9, 1)`** (verified) |
| `U_comp` per frame | `(4, 4)` |
| `F_a`, `F_b`, `F_comb` | scalars `()` |


If `set_target_frame` is still a lab float, `psi` stays `(4, 9, 1)` — Phase 5 behavior.

---

## 3.5 Where every piece lives


| Piece | Where |
| --- | --- |
| Hardened `set_target_frame` | `two_q_pulse_sim_dynamiqs.py` |
| `evolve_comp` docstring (batch shapes) | Same file |
| `combine_robust_fidelities_jax` | `grape_cost_jax.py` (above `grape_cost_robust`) |
| `grape_cost_robust` | Same file, after `grape_cost` |
| Config: `use_jax_grad`, `optimizer`, `adam_*`, `evolution` | `RobustCRGrapeConfig` |
| `_build_lab_exp`, `_build_robust_grape_statics` | module level in `cr_grape_robust.py` |
| One dynamiqs exp + batched frames | `RobustCRGrapeOptimizer.__init__` when `use_jax_grad` |
| Batched rich metrics | `_cost_from_knobs_batched` (via `cost_from_knobs`) |
| `_cost_and_grad` / `_run_adam` / `run()` | Same class |
| Smoke | `optimization_tests/test_grape_robust_jax.py` |


Class method order on the robust optimizer (JAX path):

```text
cost_from_knobs          # dispatches to batched when use_jax_grad
_cost_from_knobs_batched # Fa/Fb/Fc metrics, no grad
_cost_x                  # QuTiP / FD path
_cost_and_grad           # SciPy jac=True
_callback                # JAX: refresh rich metrics via cost_from_knobs
_run_adam                # Optax; same _cost_vg
evaluate_seed / run
```

---

## 4. Engine: length-2 frames (as shipped)

**WHERE:** `engine/two_q_pulse_sim_dynamiqs.py`, `set_target_frame`.

```python
    def set_target_frame(self, frame1):
        """Install target rotating-frame frequency (float or length-2 jax array).

        Lab GRAPE: pass a Python float.
        Robust GRAPE: pass lab_f1 + jnp.asarray([+s, -s]) once before optimize.
        """
        if hasattr(frame1, "shape") and getattr(frame1, "ndim", 0) > 0:
            frame1 = jnp.asarray(frame1, dtype=jnp.float64)
            if frame1.shape != (2,):
                raise ValueError(
                    f"batched set_target_frame expects shape (2,), got {frame1.shape}"
                )
        else:
            frame1 = float(frame1)

        self.qubits[1].frame_MHz = frame1
        self.delta_qq_MHz = jnp.asarray(self.qubits[0].frame_MHz) - frame1
```

**`evolve_comp` returns:**

```text
(4, dim, 1) if delta_qq is scalar
(2, 4, dim, 1) if delta_qq has shape (2,)   # robust — verified in smoke
```

Axis order is **detuning × ket** (not ket × detuning). No transpose needed in `grape_cost_robust`.

---

## 5. JAX combine + `grape_cost_robust` (as shipped)

**WHERE:** `optimization/grape_cost_jax.py` (`import jax` at top).

- `combine_robust_fidelities_jax` — mirror of NumPy combine; **no** `float()`; shape `()`.
- `grape_cost_robust` — assemble → `echoed_timeline_jax` → `evolve_comp` → `vmap` fidelity/leak over leading axis → combine → `-(F_comb - w * leak)`.

Locks `statics.evolution == "comp"`. Soft shape check expects `(2, 4, dim, 1)`.

Phase 5 `grape_cost` left untouched (scalar Δ).

---

## 6. `RobustCRGrapeOptimizer` (as shipped)

### 6.1 Config knobs

```python
    use_jax_grad: bool = False
    """If True, one dynamiqs exp + batched frames + SciPy jac=True."""
    optimizer: str = "lbfgs"
    """lbfgs (default) or adam; adam requires use_jax_grad=True."""
    adam_lr: float = 0.02
    adam_steps: int = 200
    """Used only when optimizer='adam'."""
    evolution: str = "comp"
```

### 6.2 `__init__` — one experiment when JAX

When `use_jax_grad=True`:

1. Reject caller-supplied `exps=`.
2. `self.exps = [_build_lab_exp(config)]` (`engine="dynamiqs"`).
3. Resolve `target_gate` **before** batching frames (lab scalar still).
4. Then once: `sim.set_target_frame(f1 + jnp.asarray([sa, sb]))`.
5. Build `GrapeStatics` via `_build_robust_grape_statics`.
6. `self._cost_vg = jax.jit(jax.value_and_grad(_cost_only))` closing over metric/weights/λ.

When `use_jax_grad=False`: existing two-exp QuTiP/FD path unchanged.

### 6.3 Helpers

- `_build_lab_exp(config)` — unshifted dynamiqs `CR_len_sweep`.
- `_build_robust_grape_statics(opt)` — templates, `x_pi`, targets, `evolution`, etc.

### 6.4 Metrics / AD / callback

- `_cost_from_knobs_batched` — one `evolve_comp`, fill `process_fidelity` (= F_comb), `_a`/`_b`, leakages.
- `_cost_and_grad` — SciPy `jac=True` wrapper around `_cost_vg` (cheap eval log; rich Fa/Fb in callback).
- `_callback` on JAX path — refresh rich metrics via `cost_from_knobs` (batched).

### 6.5 `run()` branches

```text
use_jax_grad + optimizer == "adam"  → _run_adam (scipy_result=None)
use_jax_grad + optimizer == "lbfgs" → minimize(..., jac=True), warm compile once
use_jax_grad=False                  → existing FD minimize
optimizer == "adam" without JAX     → ValueError
```

L-BFGS `maxfun = maxiter * 30` on the JAX path.

### 6.6 Adam (wired; not default)

**WHERE:** `RobustCRGrapeOptimizer._run_adam`, immediately before `evaluate_seed`.  
Mirror of Phase 5: Optax Adam on the **same** `_cost_vg` (batched `grape_cost_robust`), clip I/Q to `amp_bound_mhz`, log Fa/Fb/Fc every `adam_steps // 20`.

Usage:

```python
RobustCRGrapeConfig(
    ...,
    use_jax_grad=True,
    optimizer="adam",
    adam_lr=0.02,
    adam_steps=200,
)
# or
optimize_robust_cr_grape(..., use_jax_grad=True, optimizer="adam", adam_steps=200)
```

Smoke (2 steps): seed F_comb≈0.98706 → ~0.98733; printed `ADAM WIRED OK`.

---

## 7. Smoke tests (as shipped)

**WHERE:** `optimization/optimization_tests/test_grape_robust_jax.py`

```bash
cd Hari_6_qubit/fourqubitv5
PYTHONPATH=. /path/to/envs/qumac-env/bin/python -u \
  HM/simulator/two_qubit_simulator/optimization/optimization_tests/test_grape_robust_jax.py
```

### 7.1 Shape + parity

- Seed echoed timeline; `set_target_frame(f1 + [+s, -s])`.
- Assert `psi.shape == (2, 4, 9, 1)`.
- Batch F vs sequential `set_target_frame(f1±s)` + full propagator: agree to ~`1e-10` (measured).
- Prints `PHASE 6 SHAPE+PARITY OK`.

### 7.2 L-BFGS + JAX jac smoke

- `maxiter=3`, `n_flat_knobs=61`, `zz_shift_mhz=0.2`, `target_gate="zx_90"`.
- Grad norm > 0 at seed.
- Measured: F_comb `0.98706 → 0.98772`, **7** AD evals, `STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT`.
- Prints `PHASE 6 OK`.

---

## 8. Pitfalls (still true)


| Pitfall | Fix |
| --- | --- |
| `set_target_frame` every eval | Once in `__init__` only |
| `float(F)` inside combine / cost | Breaks tape — use JAX ops |
| Assuming `psi.shape == (4, dim, 1)` after batching | Leading axis is 2 |
| Two dynamiqs exps + length-2 on both | One exp only |
| QuTiP `set_target_frame(array)` | QuTiP stays scalar; JAX path only |
| Forgetting warm compile | First `value_and_grad` is slow on CPU |
| Comparing `n_eval` to Adam logs | Log rows ≠ Adam steps |
| `evolution="full"` on robust JAX | Locked to `comp` |
| `optimizer="adam"` without `use_jax_grad` | Raises |


---

## 9. Amp bounds (yes, still ~48)

`amp_bound_mhz` default **48.0**: each real I/Q coordinate is clipped to **[-48, +48] MHz**. Seed in many tests is **|21| MHz**. Unchanged in Phase 6 (Adam uses the same clip).

---

## 10. Module map (done)

```text
two_q_pulse_sim_dynamiqs.py
    set_target_frame(float | shape (2,))
    evolve_comp → (4,dim,1) or (2,4,dim,1)

grape_cost_jax.py
    grape_cost                     # Phase 4/5 scalar Δ
    combine_robust_fidelities_jax
    grape_cost_robust              # Phase 6

cr_grape_robust.py
    RobustCRGrapeConfig.use_jax_grad, optimizer, adam_*, evolution
    _build_lab_exp / _build_robust_grape_statics
    RobustCRGrapeOptimizer
        one dynamiqs exp + batched frames when use_jax_grad
        _cost_from_knobs_batched / _cost_vg / _cost_and_grad
        _run_adam
        run() branches: lbfgs jac=True | adam | QuTiP FD
        QuTiP two-exp FD unchanged when use_jax_grad=False

optimization_tests/test_grape_robust_jax.py
    PHASE 6 SHAPE+PARITY OK
    PHASE 6 OK
```

---

## 11. Checklist (green)


| # | Item | Result |
| --- | --- | --- |
| 1 | `set_target_frame` shape `(2,)` | OK |
| 2 | `evolve_comp` leading batch axis 2 | `(2, 4, 9, 1)` |
| 3 | `grape_cost_robust` + `value_and_grad` finite, ‖g‖>0 | OK |
| 4 | Batch F ≈ sequential F | ~1e-10 |
| 5 | L-BFGS `use_jax_grad=True` smoke, `n_eval` ≪ FD | 7 evals / 3 iters |
| 6 | QuTiP / `use_jax_grad=False` path kept | unchanged code path |
| 7 | Adam opt-in wired | 2-step smoke OK |


---

## 12. Explicitly not doing (still)


| Temptation | Why not |
| --- | --- |
| Delete `cr_grape_robust` two-exp path | Keep QuTiP / FD fallback |
| Batch 10 ZZ points | Length 2 first; generalize later |
| GPU | Later |
| `evolution="full"` robust batch | Comp path verified; full-U later |
| Change Nielsen formulas | Same `fidelity_jax` |


Adam for robust is **no longer deferred** — it is wired, not default (decision 6).

---

## 13. How to run robust JAX day-to-day

**L-BFGS (default):**

```python
from HM.simulator.two_qubit_simulator.optimization.cr_grape_robust import (
    RobustCRGrapeConfig,
    RobustCRGrapeOptimizer,
)

cfg = RobustCRGrapeConfig(
    flat_len_ns=122.0,
    n_flat_knobs=61,
    seed_amp_mhz=-21.0,
    zz_shift_mhz=0.2,
    fidelity_metric="weighted_mean",
    maxiter=30,
    use_jax_grad=True,
    optimizer="lbfgs",
    evolution="comp",
    n_sub=14,
    target_gate="zx_90",
)
result = RobustCRGrapeOptimizer(cfg).run()
```

**Adam (opt-in):**

```python
cfg = RobustCRGrapeConfig(
    ...,
    use_jax_grad=True,
    optimizer="adam",
    adam_lr=0.02,
    adam_steps=200,
)
```
