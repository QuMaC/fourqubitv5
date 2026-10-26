# Phase 4 — Differentiable GRAPE cost (`grape_cost` + FD vs AD)

Instructions only. You type the code. Phases 0–3 are done:

- Phase 0: x64 / `BackwardCheckpointed` at import  
- Phase 1: dynamiqs forward + QuTiP parity on a **NumPy** timeline  
- Phase 2: `pulses_jax` bit-matches NumPy  
- Phase 3: `process_fidelity_jax` bit-matches NumPy

This phase does **call** `jax.grad` / `jax.value_and_grad`. It does **not** plug SciPy `jac=` (Phase 5). It does **not** do robust length-2 frames (Phase 6).

Parent tutorial: `DYNAMIQS_GRAPE_MIGRATION.md` §3.12–3.14, Phase 4 checklist.  
Siblings: `PHASE_0_…`, `PHASE_1_…`, `PHASE_2_…`, `PHASE_3_…`.

---

## 0. Decisions locked for this phase (your answers)


| #   | Decision                                                                                                                                                                                            |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Keep **both** evolutions: full `U` (`sepropagator`) and **4 computational kets** (`evolve_comp`). Switch with a flag. **Default = `"comp"`** (the new path).                                        |
| 2   | `grape_cost` is a **free function** + a `GrapeStatics` bucket (not methods on `CRGrapeOptimizer`). Easier to `jit` / test. Phase 5 wires it into SciPy.                                             |
| 3   | Cost is `-(F - leakage_weight * leakage)` with `**leakage_weight = 0.0`** by default (same as today’s `CRGrapeConfig`). Knob exists so you can turn leakage on later without rewriting the formula. |


Also in this phase (not deferred): **write `evolve_comp`**.

---

## 1. What I would have implemented, in order


| Step | File                                                             | What                                                                                 |
| ---- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 1    | `engine/two_q_pulse_sim_dynamiqs.py`                             | `evolve_comp(timeline)` → JAX `(4, dim, 1)`, **no** `np.asarray`                     |
| 2    | same                                                             | `run_propagator(..., return_numpy=True)` — parity keeps NumPy; GRAPE can ask for JAX |
| 3    | `optimization/fidelity_jax.py`                                   | `u_comp_from_psi_jax`, `process_fidelity_comp_jax`, `leakage_from_psi_jax`           |
| 4    | **new** `optimization/grape_cost_jax.py`                         | `GrapeStatics`, `grape_cost(x, sim, statics)`                                        |
| 5    | **new** `optimization/optimization_tests/test_grape_cost_jax.py` | F matches NumPy path; FD vs AD on 3 indices                                          |


**Not in Phase 4:**

- do **not** set SciPy `jac=` / change `minimize` (Phase 5)  
- do **not** length-2 `set_target_frame` or `combine_robust` (Phase 6)  
- do **not** break QuTiP GRAPE  
- do **not** rewrite `CRGrapeOptimizer.run()` to call JAX yet (optional smoke call in the test only)  
- do **not** GPU

When the test prints `PHASE 4 OK` and AD ≈ FD, stop.

---

## 2. Why this phase exists (x-ray)

### 2.1 The chain that must stay on one tape

```text
x  (real, length 2 * n_knobs)
  →  knobs = x[0::2] + 1j * x[1::2]
  →  assemble_cr_half_jax  →  cr_plus
  →  echoed_timeline_jax   →  dict of 3 jnp arrays, length L
  →  evolve_comp  (default)  OR  run_propagator (flag "full")
  →  F = process_fidelity_jax / process_fidelity_comp_jax
  →  leak = leakage_…_jax
  →  cost = -(F - w * leak)     # w = 0.0 by default
```

Every arrow must be JAX (or dynamiqs ops that register with `jax.grad`). One `np.asarray` / `float()` in the middle and the gradient of `cost` w.r.t. `x` is wrong or raises.

### 2.2 What “FD vs AD” proves

- **AD** (`jax.value_and_grad`): one forward + one reverse through the ODE. Gradient for **all** knobs.  
- **FD** (central difference on one coordinate): two full forwards per checked index.

If three coordinates agree (~`1e-4`–`1e-5`relative), the tape is connected through pulse → H → sesolve → F. If index`0`matches and`17` does not, assembly stretch is wrong for later knobs.

### 2.3 Why default is `evolve_comp`, not full `U`

Same process fidelity. Fewer Schrödinger solves (4 vs 9). Layout matches how you think about computational inputs. Full `U` stays as the **flag** for debugging / matching Phase 1 parity tooling.

```text
statics.evolution = "comp"   # DEFAULT — evolve_comp
statics.evolution = "full"   # run_propagator, score 9×9
```

---

## 3. Files you will touch

```text
engine/two_q_pulse_sim_dynamiqs.py          # evolve_comp + return_numpy on run_propagator
optimization/fidelity_jax.py                # 4-ket scoring helpers
optimization/grape_cost_jax.py              # NEW
optimization/optimization_tests/test_grape_cost_jax.py   # NEW
```

Optional one-liner later: fix `CHANNEL_NAMES` in `pulses_jax.py` to a **tuple** if it is still a set (Phase 2 leftover). Dict key order must be stable for pytrees.

Do **not** edit `cr_grape.py`’s SciPy loop yet.

---

## 4. Step 1 — `evolve_comp` on the dynamiqs engine

**File:** `engine/two_q_pulse_sim_dynamiqs.py`  
**Where:** after `run_propagator` / near `run_shot_batch`.

### 4.1 What it does

Evolve the four computational basis states

```text
|00>, |01>, |10>, |11>   ↔   indices self.comp_idx = [0, 1, 3, 4]
```

in **one** `dq.sesolve` call (batched `psi0`). Each state is still length `dim=9`. Return **JAX**, not NumPy.

### 4.2 Code to ADD

```python
def evolve_comp(self, timeline: dict) -> jnp.ndarray:
    """Evolve computational basis kets |00>,|01>,|10>,|11> in one sesolve.

    Returns jax array shape (4, dim, 1).
    No np.asarray — keep on the tape for jax.grad.
    """
    L = self._validate_timeline(timeline)
    H = self._build_hamiltonian(timeline)

    # psi0[j, :, 0] = |comp_j>  (column vector)
    psi0 = jnp.zeros((4, self.dim, 1), dtype=jnp.complex128)
    for j, idx in enumerate(self.comp_idx):
        # Python ints: unrolled at trace time. Legal in jit.
        psi0 = psi0.at[j, int(idx), 0].set(1.0)

    y0 = dq.asqarray(psi0)
    tsave = jnp.array([0.0, L * self.dt_sample_us])

    result = dq.sesolve(
        H,
        y0,
        tsave,
        method=self._integrator_method,
        gradient=self.gradient,          # BackwardCheckpointed from __init__
        options=self._sesolve_options,
    )
    # Prefer final_state: shape (4, dim, 1). Avoid guessing states axes.
    psi = dq.to_jax(result.final_state)
    return psi
```

### 4.3 Syntax / logic notes (read these)

`**psi0.at[j, idx, 0].set(1.0)**`  
JAX arrays are immutable. This returns a **new** array with that entry set. A Python `psi0[j, idx, 0] = 1` fails under `jit` / tracers.

`**for j, idx in enumerate(self.comp_idx)`**  
`comp_idx` is a Python list of four ints, fixed for the sim. The loop unrolls. That is fine.

`**dq.asqarray(psi0)**`  
Turns the batched ket array into a dynamiqs QArray. Shape `(4, dim, 1)` means “4 initial states.”

`**gradient=self.gradient**`  
Your class stores `self.gradient = dq.gradient.BackwardCheckpointed()` (Phase 1). Same object as `run_shot` / `run_propagator`. Without this, `jax.grad` through `sesolve` will not reverse-mode correctly.

`**result.final_state**`  
Dynamiqs documents `final_state` shape `(..., n, 1)`. For `psi0` shape `(4, dim, 1)` that is `(4, dim, 1)`.  

If your dynamiqs build ever lacks `final_state`, fall back to:

```python
psi = dq.to_jax(result.states[:, -1])   # (4, dim, 1) when ntsave=2
```

Print `result.states.shape` **once** if unsure. With `tsave = [0, T]` and default `save_states=True`, states are `(4, 2, dim, 1)` → last time is `[:, -1]`.

`**dq.to_jax(...)`**  
QArray → `jnp.ndarray`. Still JAX. **Do not** wrap with `np.asarray` here.

**Batched Δ (Phase 6):** if `set_target_frame` later stores a length-2 `delta`, `H` batches and `final_state` gains a leading axis `(n_delta, 4, dim, 1)`. **Do not test that in Phase 4.** Lab scalar only.

### 4.4 Sanity check (before grape_cost)

Same timeline as Phase 1 parity seed. Compare:

```python
U = sim.run_propagator(timeline)           # 9×9 NumPy
psi = np.asarray(sim.evolve_comp(timeline))  # (4, 9, 1)

for j, idx in enumerate(sim.comp_idx):
    # column idx of U is evolution of |idx>
    np.testing.assert_allclose(
        psi[j, :, 0],
        U[:, idx],
        atol=1e-8,
        rtol=1e-8,
    )
```

If this fails, stop. Do not build `grape_cost` on a wrong `evolve_comp`.

---

## 5. Step 2 — `run_propagator` that can stay on the tape

**ALREADY THERE** today:

```python
return np.asarray(dq.to_jax(result.final_propagator))
```

That **cuts** the tape. Parity / experiments want NumPy. GRAPE with `evolution="full"` wants JAX.

**CHANGE** to:

```python
def run_propagator(
    self,
    timeline: dict,
    *,
    return_numpy: bool = True,
):
    """Full Hilbert-space unitary via dq.sepropagator.

    return_numpy=True  (default): ndarray — parity, QuTiP-shaped callers
    return_numpy=False: jnp.ndarray — GRAPE autodiff path
    """
    L = self._validate_timeline(timeline)
    H = self._build_hamiltonian(timeline)
    tsave = jnp.array([0.0, L * self.dt_sample_us])
    result = dq.sepropagator(
        H,
        tsave,
        method=self._integrator_method,
        gradient=self.gradient,
        options=self._seprop_options,
    )
    U = dq.to_jax(result.final_propagator)
    if return_numpy:
        return np.asarray(U)
    return U
```

### 5.1 Syntax notes

**Keyword-only `return_numpy`**  
Same `*` idea as Phase 2: cannot accidentally pass a bool as a second positional.

**Default `True`**  
Existing callers (`_propagator_from_timeline`, parity script) keep working with no edits.

**GRAPE full path:**

```python
U = sim.run_propagator(timeline, return_numpy=False)
F = process_fidelity_jax(U, statics.U_target_full)
```

---

## 6. Step 3 — score four kets in `fidelity_jax.py`

Phase 3 scored a 9×9 `U`. With `evolve_comp` you have `psi` shape `(4, dim, 1)`. You must form the 4×4 block with the **correct** layout (Phase 3 §2.5 transpose trap).

### 6.1 ADD helpers

```python
def u_comp_from_psi_jax(
    psi: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Build 4×4 computational block from evolved kets.

    psi: shape (4, dim) or (4, dim, 1)
         psi[j] = U |comp_j>

    U_comp[i, j] = ⟨comp_i | ψ_j⟩ = psi[j, comp_i]
    """
    psi = jnp.asarray(psi)
    if psi.ndim == 3:
        psi = psi[..., 0]          # (4, dim, 1) → (4, dim)
    idx = _idx(comp_indices)
    # psi[:, idx] has shape (4, 4) with entries [j, i] = ⟨comp_i|ψ_j⟩
    # transpose → [i, j]
    return psi[:, idx].T


def process_fidelity_comp_jax(
    U_comp: jnp.ndarray,
    U_target_comp: jnp.ndarray,
) -> jnp.ndarray:
    """Process fidelity from 4×4 blocks. Returns shape ()."""
    U_comp = jnp.asarray(U_comp)
    U_target_comp = jnp.asarray(U_target_comp)
    d = int(U_comp.shape[0])
    overlap = jnp.trace(U_target_comp.conj().T @ U_comp)
    return jnp.abs(overlap) ** 2 / (d * d)


def leakage_from_psi_jax(
    psi: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Mean leakage of the four computational inputs. Shape ()."""
    U_comp = u_comp_from_psi_jax(psi, comp_indices)
    comp_weight = jnp.sum(jnp.abs(U_comp) ** 2, axis=0)
    return jnp.mean(1.0 - comp_weight)
```

### 6.2 Syntax notes

`**psi[:, idx].T**`  
Mandatory. Without `.T` you score the transpose of the gate (chase ZX† once near optimum).  

Check against full `U`:

```python
U_comp_from_U = comp_block_jax(U)
U_comp_from_psi = u_comp_from_psi_jax(psi)
np.testing.assert_allclose(U_comp_from_psi, U_comp_from_U, atol=1e-8)
```

`**process_fidelity_comp_jax` vs 9×9 form**  
For GRAPE’s embedded ZX targets they agree:

```text
|tr(U_t_full† P U P)|²/16  =  |tr(U_t_comp† U_comp)|²/16
```

Use the 4×4 form on the `"comp"` path. Use Phase 3’s `process_fidelity_jax` on the `"full"` path.

**Leakage from psi**  
Same numbers as `leakage_from_comp_jax(U)` when `psi` matches `U`’s computational columns.

### 6.3 Optional: fix `dim: int(dim)` if still present

In `comp_projector_jax`, if you still have `dim: int(dim)` that is a **type annotation**, not an assignment. It should be `dim = int(dim)`. Phase 3 tests may have passed if `dim` was already an `int`. Fix it while you are in the file.

---

## 7. Step 4 — `GrapeStatics` and `grape_cost` 

**ADD** `optimization/grape_cost_jax.py`.

### 7.1 What is `statics`?

Everything the cost needs that **does not depend on `x`** (or is treated as fixed for one optimize):


| Field            | Example                              | Role                   |
| ---------------- | ------------------------------------ | ---------------------- |
| `rise`, `fall`   | from `_templates_1ns(16)`            | CR edges               |
| `n_flat`         | 184                                  | samples in flat        |
| `n_link_samples` | 8                                    | rise/fall scale window |
| `x_pi`           | from `exp.build_x_pi()`              | echo pulse (constant)  |
| `channel_names`  | `("q1_drive","q2_drive","cr_drive")` | timeline keys          |
| `echo_channel`   | `"q1_drive"`                         | where Xπ sits          |
| `U_target_full`  | embed ZX in 9×9                      | for `evolution="full"` |
| `U_target_comp`  | 4×4 ZX                               | for `evolution="comp"` |
| `comp_indices`   | `(0,1,3,4)`                          | subspace               |
| `evolution`      | `"comp"` or `"full"`                 | which engine path      |
| `leakage_weight` | `0.0`                                | cost knob              |


Frames / Δ live on `**sim**`, set once with `set_target_frame` before optimize. Not in `statics`.

### 7.2 Code

```python
"""Differentiable echoed-CR cost for dynamiqs GRAPE (Phase 4)."""
from __future__ import annotations

from dataclasses import dataclass

import jax.numpy as jnp

from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    CHANNEL_NAMES,
    DEFAULT_ECHO_CHANNEL,
    assemble_cr_half_jax,
    echoed_timeline_jax,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    leakage_from_comp_jax,
    leakage_from_psi_jax,
    process_fidelity_comp_jax,
    process_fidelity_jax,
    u_comp_from_psi_jax,
)


@dataclass(frozen=True)
class GrapeStatics:
    rise: jnp.ndarray
    fall: jnp.ndarray
    n_flat: int
    n_link_samples: int
    x_pi: jnp.ndarray
    U_target_full: jnp.ndarray
    U_target_comp: jnp.ndarray
    comp_indices: tuple[int, ...]
    channel_names: tuple[str, ...] = tuple(CHANNEL_NAMES) if isinstance(CHANNEL_NAMES, (list, tuple)) else ("q1_drive", "q2_drive", "cr_drive")
    echo_channel: str = DEFAULT_ECHO_CHANNEL
    evolution: str = "comp"          # "comp" | "full"  — DEFAULT is evolve_comp
    leakage_weight: float = 0.0      # same default as CRGrapeConfig


def _x_to_knobs_jax(x: jnp.ndarray) -> jnp.ndarray:
    """Real I/Q vector → complex knobs. Same layout as cr_grape._x_to_knobs."""
    x = jnp.asarray(x).reshape(-1)
    return x[0::2] + 1j * x[1::2]


def grape_cost(x: jnp.ndarray, sim, statics: GrapeStatics) -> jnp.ndarray:
    """Scalar cost = -(F - w * leakage). Shape ().

    sim: TwoQubitPulseSimulatorDynamiqs (closed over; frames already set)
    """
    knobs = _x_to_knobs_jax(x)
    cr_plus, _ = assemble_cr_half_jax(
        knobs,
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

    if statics.evolution == "comp":
        psi = sim.evolve_comp(timeline)
        U_comp = u_comp_from_psi_jax(psi, statics.comp_indices)
        F = process_fidelity_comp_jax(U_comp, statics.U_target_comp)
        leak = leakage_from_psi_jax(psi, statics.comp_indices)
    elif statics.evolution == "full":
        U = sim.run_propagator(timeline, return_numpy=False)
        F = process_fidelity_jax(U, statics.U_target_full, statics.comp_indices)
        leak = leakage_from_comp_jax(U, statics.comp_indices)
    else:
        raise ValueError(
            f"evolution must be 'comp' or 'full', got {statics.evolution!r}"
        )

    w = statics.leakage_weight
    # w is a Python float (static). F and leak are traced scalars shape ().
    return -(F - w * leak)
```

### 7.3 Syntax notes (long — this is the heart)

`**@dataclass(frozen=True)**`  
Immutable bag of fields. Fine to close over in `jit` as long as arrays inside are JAX arrays / static Python ints. Frozen stops accidental `statics.n_flat = ...` mid-run.

`**CHANNEL_NAMES` may still be a set** in your `pulses_jax.py`. Sets are unordered. Force a tuple in `GrapeStatics` construction:

```python
channel_names=("q1_drive", "q2_drive", "cr_drive")
```

Better: change `CHANNEL_NAMES` in `pulses_jax.py` to that tuple once.

`**_x_to_knobs_jax**`  
`x[0::2]` = I (real parts), `x[1::2]` = Q. Same as NumPy `_x_to_knobs`. SciPy’s vector is this layout.

`**sim` as second argument**  
Not a pytree. You will usually wrap:

```python
def cost_only(x):
    return grape_cost(x, sim, statics)

c, g = jax.value_and_grad(cost_only)(x0)
```

Closing over `sim` and `statics` is normal. Do **not** put `sim` inside `x`.

**Python `if statics.evolution == "comp"`**  
`evolution` is a Python `str` on a frozen dataclass, **not** a traced array. The `if` is resolved at trace time. Both branches must be valid code; only one is compiled into a given `jit` specialization if `evolution` is treated as static (it is — Python string).

`**leakage_weight = 0.0`**  
Then `cost = -F` exactly. The `w * leak` term still exists so `jax.grad` would see leakage if you set `w = 0.1` later. With `w = 0`, that path is multiplied by zero (still fine).

**Return shape `()`**  
`jax.grad` requires a scalar. Do not return `(1,)` or a Python float.

**Do not `float(F)`**  
Same Phase 3 rule.

### 7.4 Building `statics` in Python (once per optimize / once in the test)

```python
from HM.simulator.two_qubit_simulator.engine.pulses_jax import _templates_1ns
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    embed_in_full,
    zx_target_unitary,
)

rise, fall = _templates_1ns(16)
U_t_comp = jnp.asarray(zx_target_unitary("zx_m90"))  # or config gate
U_t_full = jnp.asarray(embed_in_full(np.asarray(U_t_comp), dim=9))
x_pi = jnp.asarray(exp.build_x_pi())

statics = GrapeStatics(
    rise=rise,
    fall=fall,
    n_flat=184,                 # or 122 for parity-length seed
    n_link_samples=8,
    x_pi=x_pi,
    U_target_full=U_t_full,
    U_target_comp=U_t_comp,
    comp_indices=tuple(sim.comp_idx),
    channel_names=("q1_drive", "q2_drive", "cr_drive"),
    evolution="comp",           # DEFAULT
    leakage_weight=0.0,
)
```

`zx_target_unitary` / `embed_in_full` stay NumPy → `jnp.asarray` once. They are constants.

---

## 8. Step 5 — tests (`test_grape_cost_jax.py`)

**ADD** `optimization/optimization_tests/test_grape_cost_jax.py`.

### 8.1 What to prove

1. `evolve_comp` columns match `run_propagator` columns at `comp_idx`.
2. `grape_cost` with `evolution="comp"` and `"full"` give the same scalar (within ODE tol).
3. That scalar matches NumPy `CRGrapeOptimizer`-style cost on the same knobs (within ~`1e-5`–`1e-6` on F).
4. `jax.value_and_grad` vs central FD on indices `[0, 1, 17]` (or `min(17, n-1)`).
5. Optional: `jax.jit(value_and_grad)` runs twice.

### 8.2 Full test sketch

```python
"""Phase 4: grape_cost FD vs AD + evolve_comp parity."""
from __future__ import annotations

import numpy as np
import jax
import jax.numpy as jnp

from HM.simulator.two_qubit_simulator.engine import two_q_pulse_sim_dynamiqs  # noqa: F401
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    _templates_1ns,
    assemble_cr_half_jax,
    echoed_timeline_jax,
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import (
    DEFAULT_CR_PULSE_PARAMS,
    _knobs_to_x,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    embed_in_full,
    process_fidelity,
    zx_target_unitary,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    u_comp_from_psi_jax,
)
from HM.simulator.two_qubit_simulator.optimization.grape_cost_jax import (
    GrapeStatics,
    grape_cost,
)

# Use a length that matches a real GRAPE config and divides knobs cleanly.
FLAT_LEN_NS = 184.0
N_KNOBS = 46
T_RISE = 16
N_LINK = 8
ATOL_U = 1e-7
ATOL_F = 1e-6
ATOL_GRAD_REL = 5e-4   # ODE + FD eps; tighten if your machine is clean


def _build_exp() -> CR_len_sweep:
    return CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        engine="dynamiqs",
        n_sub=14,
        cr_pulse_params={
            **DEFAULT_CR_PULSE_PARAMS,
            "amp_mhz": -32.0,
            "phase_rad": 0.0,
            "t_rise_ns": T_RISE,
        },
    )


def _seed_knobs() -> np.ndarray:
    """Constant complex amp (one value repeated) — like a flat seed."""
    return np.full(N_KNOBS, 21.0 + 0.0j, dtype=complex)


def _make_statics(exp, sim, evolution: str) -> GrapeStatics:
    rise, fall = _templates_1ns(T_RISE)
    gate = "zx_m90"
    U_comp = zx_target_unitary(gate)
    return GrapeStatics(
        rise=rise,
        fall=fall,
        n_flat=int(round(FLAT_LEN_NS)),
        n_link_samples=N_LINK,
        x_pi=jnp.asarray(exp.build_x_pi()),
        U_target_full=jnp.asarray(embed_in_full(U_comp, dim=sim.dim)),
        U_target_comp=jnp.asarray(U_comp),
        comp_indices=tuple(sim.comp_idx),
        channel_names=("q1_drive", "q2_drive", "cr_drive"),
        evolution=evolution,
        leakage_weight=0.0,
    )


def test_evolve_comp_matches_propagator_columns() -> None:
    exp = _build_exp()
    sim = exp.simulator
    rise, fall = _templates_1ns(T_RISE)
    knobs = _seed_knobs()
    cr_plus, _ = assemble_cr_half_jax(
        knobs, rise=rise, fall=fall, n_flat=int(FLAT_LEN_NS), n_link_samples=N_LINK
    )
    timeline = echoed_timeline_jax(
        cr_plus, exp.build_x_pi(), channel_names=("q1_drive", "q2_drive", "cr_drive")
    )
    # NumPy dict for engine validate (values can be jnp; asarray inside H build)
    tl = {k: np.asarray(v) for k, v in timeline.items()}

    U = sim.run_propagator(tl, return_numpy=True)
    psi = np.asarray(sim.evolve_comp(tl))
    assert psi.shape == (4, sim.dim, 1)
    for j, idx in enumerate(sim.comp_idx):
        np.testing.assert_allclose(psi[j, :, 0], U[:, idx], atol=ATOL_U, rtol=ATOL_U)
        print("ket", j, "idx", idx, "max|d|", np.max(np.abs(psi[j, :, 0] - U[:, idx])))
    # layout check
    U_comp_U = U[np.ix_(sim.comp_idx, sim.comp_idx)]
    U_comp_psi = np.asarray(u_comp_from_psi_jax(psi, tuple(sim.comp_idx)))
    np.testing.assert_allclose(U_comp_psi, U_comp_U, atol=ATOL_U, rtol=ATOL_U)
    print("evolve_comp vs U columns ok")


def test_cost_comp_matches_full_and_numpy() -> None:
    exp = _build_exp()
    sim = exp.simulator
    knobs = _seed_knobs()
    x = jnp.asarray(_knobs_to_x(knobs))

    st_comp = _make_statics(exp, sim, "comp")
    st_full = _make_statics(exp, sim, "full")

    c_comp = float(grape_cost(x, sim, st_comp))
    c_full = float(grape_cost(x, sim, st_full))
    print("cost comp", c_comp, "cost full", c_full)
    np.testing.assert_allclose(c_comp, c_full, atol=ATOL_F, rtol=ATOL_F)

    # NumPy reference: build timeline NumPy path + process_fidelity
    from HM.simulator.two_qubit_simulator.engine.pulses import (
        assemble_cr_half_from_flat_knobs,
    )
    cr_np, _ = assemble_cr_half_from_flat_knobs(
        knobs, flat_len_ns=FLAT_LEN_NS, t_rise_ns=T_RISE, dt_ns=1.0, n_link_samples=N_LINK
    )
    tl_np = exp._build_timeline_from_cr_half(cr_np, x_pi=exp.build_x_pi())
    U_np = exp._propagator_from_timeline(tl_np)
    Ut = embed_in_full(zx_target_unitary("zx_m90"), dim=U_np.shape[0])
    F_np = process_fidelity(U_np, Ut)
    c_np = -F_np
    print("cost numpy", c_np, "F_np", F_np)
    np.testing.assert_allclose(c_comp, c_np, atol=1e-5, rtol=1e-5)


def test_fd_vs_ad() -> None:
    exp = _build_exp()
    sim = exp.simulator
    knobs = _seed_knobs()
    x0 = jnp.asarray(_knobs_to_x(knobs))
    statics = _make_statics(exp, sim, "comp")

    def cost_only(x):
        return grape_cost(x, sim, statics)

    # First without jit — easier to debug
    c, g = jax.value_and_grad(cost_only)(x0)
    print("AD cost", float(c), "||g||", float(jnp.linalg.norm(g)))

    eps = 1e-6
    n = int(x0.shape[0])
    indices = [0, 1, min(17, n - 1)]
    for i in indices:
        e = jnp.zeros_like(x0).at[i].set(eps)
        fd = (cost_only(x0 + e) - cost_only(x0 - e)) / (2 * eps)
        gi = float(g[i])
        fdi = float(fd)
        rel = abs(gi - fdi) / max(1e-8, abs(fdi))
        print(f"idx {i:3d}  AD={gi:+.6e}  FD={fdi:+.6e}  |d|={abs(gi-fdi):.3e}  rel={rel:.3e}")
        assert rel < ATOL_GRAD_REL or abs(gi - fdi) < 1e-5

    # Optional jit smoke
    cost_vg = jax.jit(jax.value_and_grad(cost_only))
    c2, g2 = cost_vg(x0)
    c3, g3 = cost_vg(x0 * 1.0)  # second call uses cache
    np.testing.assert_allclose(float(c2), float(c), atol=1e-10)
    print("jit value_and_grad ok", float(c2), g2.shape)


if __name__ == "__main__":
    test_evolve_comp_matches_propagator_columns()
    test_cost_comp_matches_full_and_numpy()
    test_fd_vs_ad()
    print("PHASE 4 OK")
```

### 8.3 Syntax notes for the FD test

`**jnp.zeros_like(x0).at[i].set(eps)**`  
Build a one-hot perturbation without mutating `x0`.

**Central difference**  
`(C(x+εe) - C(x-εe)) / (2ε)`. One-sided is noisier.

`**eps = 1e-6`**  
Typical for float64 costs of order 1. If FD is garbage, try `1e-5` or `1e-7`.

**Relative vs absolute**  
Near a flat direction, both AD and FD are ~0; use absolute floor `1e-5` as well as relative.

**First call is slow**  
Tsit5 + reverse-mode compile. Minutes possible on CPU the first time. Second `jit` call should be fast.

`**evolution="full"` in FD**  
Optional second loop. If `"comp"` AD matches FD and `"comp"` cost matches `"full"` cost, you do not need a second FD sweep.

### 8.4 Run

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python \
  HM/simulator/two_qubit_simulator/optimization/optimization_tests/test_grape_cost_jax.py
```

---

## 9. What failure looks like

**Fail — `evolve_comp` ≠ `U[:, idx]`**  
Wrong `comp_idx` fill, or `states` time axis wrong (`states[-1]` vs `states[:, -1]`). Print shapes.

**Fail — `U_comp` from psi ≠ `comp_block(U)`**  
Forgot `.T` in `u_comp_from_psi_jax`.

**Fail — `cost_comp` ≠ `cost_full` at `1e-2`**  
Different timelines (NumPy vs JAX pulse), or `return_numpy=True` on the full path cutting something inconsistently (should still match forward). Check you pass the **same** knobs and same `x_pi`.

**Fail — AD vs FD only on index 0**  
Stretch / assemble bug for later samples. Check `n_flat % n_knobs == 0` and `jnp.repeat`.

**Fail — `ConcretizationTypeError` inside cost**  
`float(F)`, Python `if` on a traced amplitude, or `int(knobs[0])`. Lengths must be Python ints from `statics`.

**Fail — `np.asarray` in the grad path**  
`run_propagator` without `return_numpy=False`, or `evolve_comp` wrapping NumPy.

**Fail — gradient all zeros**  
`gradient=` not passed to `sesolve` / `sepropagator`, or pulse cut before H (NumPy assemble).

**Fail — jit error closing over `sim`**  
Run `value_and_grad` **without** `jit` first. If that passes FD, Phase 4 is scientifically done; fix jit as a follow-up (sometimes needs `donate_argnums` / not jitting the first call). Document what you saw.

**Fail — x64 warning**  
Import dynamiqs engine (or `pulses_jax`) before first `jnp` array.

**Pass — `PHASE 4 OK`**  
Columns match; comp/full/numpy costs agree; three FD indices agree with AD.

---

## 10. How Phase 5 will use this (do not write it yet)

```python
# Phase 5 sketch
cost_vg = jax.jit(jax.value_and_grad(lambda x: grape_cost(x, sim, statics)))

def _cost_x(x_np):
    c, _ = cost_vg(jnp.asarray(x_np))
    return float(c)

def _jac_x(x_np):
    _, g = cost_vg(jnp.asarray(x_np))
    return np.asarray(g)

minimize(_cost_x, x0, jac=_jac_x, method="L-BFGS-B", ...)
```

Metrics / tqdm callback stay on a **separate** non-differentiated forward (NumPy or `float(F)` after a no-grad eval). `value_and_grad` only returns the scalar + gradient.

---

## 11. Module map when you are done

```text
two_q_pulse_sim_dynamiqs.py
    evolve_comp(timeline) -> jnp (4, dim, 1)
    run_propagator(..., return_numpy=True|False)

fidelity_jax.py
    u_comp_from_psi_jax, process_fidelity_comp_jax, leakage_from_psi_jax
    (+ Phase 3 functions unchanged)

grape_cost_jax.py
    GrapeStatics(evolution="comp", leakage_weight=0.0, ...)
    grape_cost(x, sim, statics) -> shape ()

cr_grape.py                         # UNCHANGED SciPy loop
```

---

## 12. Stop condition

Phase 4 is **done** when:

1. `test_grape_cost_jax.py` prints `PHASE 4 OK`.
2. `evolve_comp` matches propagator columns at `comp_idx`.
3. `grape_cost` with `"comp"` and `"full"` agree; both agree with NumPy F at ~`1e-5`.
4. AD matches FD on three indices at the stated tolerance.
5. Default `evolution` is `"comp"`; `leakage_weight` defaults to `0.0`.

Then stop. Do not open SciPy `jac=` until that is true. Phase 5 is a later MD.

---

## 13. Suggested typing order (so you do not boil the ocean)

1. `evolve_comp` + column test only.
2. `return_numpy` on `run_propagator`.
3. `u_comp_from_psi_jax` + layout assert.
4. `grape_cost` forward (`float(grape_cost(...))`) vs NumPy.
5. `value_and_grad` without jit + FD.
6. `jit` if step 5 is green.

If you get stuck, stop at the last green step and paste the traceback — do not invent a second ODE path.