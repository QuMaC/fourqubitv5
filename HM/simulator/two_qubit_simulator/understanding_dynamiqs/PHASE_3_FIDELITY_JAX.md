# Phase 3 — JAX process fidelity (`fidelity_jax.py`)

Instructions only. You type the code. Phase 2 is done (`test_pulses_jax.py` matches NumPy at `atol=1e-14`). This phase does **not** call `sesolve` or `jax.grad`. It only makes the map

```text
9×9 propagator U   +   9×9 target U_t   →   scalar F
```

stay on JAX arrays so a later backward pass can see it.

Parent tutorial: `DYNAMIQS_GRAPE_MIGRATION.md` §3.12, §3.14, Phase 3 checklist.  
Sibling sheets: `PHASE_0_UPGRADE_AND_JAX_CONFIG.md`, `PHASE_1_FORWARD_ENGINE_AND_PARITY.md`, `PHASE_2_PULSES_JAX.md`.

---

## 0. What I would have implemented, in order


| Step | File                                                           | What                                                                                   |
| ---- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 1    | **new** `optimization/fidelity_jax.py`                         | `comp_projector_jax`, `comp_block_jax`                                                 |
| 2    | same                                                           | `process_fidelity_jax` — same formula as `fidelity.process_fidelity`, **no `float()`** |
| 3    | same                                                           | `average_gate_fidelity_jax`, `leakage_from_comp_jax` (same file, still no `float()`)   |
| 4    | **new** `optimization/optimization_tests/test_fidelity_jax.py` | compare to NumPy on synthetic U and one parity `U`                                     |


**Not in Phase 3:**

- do **not** write `grape_cost` or `jax.grad` (Phase 4)
- do **not** write `evolve_comp` (optional 1b / Phase 4)
- do **not** port `gate_metrics` / `best_zx_gate_metrics` (Python `if` over two targets; logging only)
- do **not** port `embed_in_full` / `zx_90_unitary` (constants; keep using NumPy, then `jnp.asarray` once)
- do **not** port `combine_robust_fidelities` (lives in the robust file, Phase 6)
- do **not** change `cr_grape.py` to call the JAX fidelity yet
- do **not** edit `optimization/fidelity.py`

When the test file prints `PHASE 3 OK`, this phase is done.

---

## 1. Why this phase exists (x-ray)

### 1.1 What GRAPE already does (NumPy)

Every SciPy eval today, last two lines:

```text
U  = _propagator_from_timeline(timeline)     # 9×9, NumPy (or np.asarray of dynamiqs)
F  = process_fidelity(U, self.u_target_full) # Python float
cost = -F
```

`self.u_target_full` is built **once** in the optimizer constructor:

```python
u_target_comp = zx_target_unitary(self.target_gate)          # 4×4
self.u_target_full = embed_in_full(u_target_comp, dim=9, ...) # 9×9
```

That target does **not** depend on knobs. It is a constant. Phase 3 does not rebuild ZX matrices in JAX. It only rebuilds the **score**.

### 1.2 What “the tape” needs

Phase 4 will do `jax.grad` of `cost(x) = -F(U(x))`. If you do this:

```python
U = sim.run_propagator(timeline)          # JAX (later)
F = process_fidelity(np.asarray(U), Ut)   # NumPy + float()
```

then `np.asarray` and `float()` **cut the tape**. JAX no longer knows how `F` depended on `U[3,4]`, so it cannot know how `F` depended on knob 0.

So Phase 3 is: **same number as NumPy `process_fidelity`, all `jnp`, return a 0-d array not a Python float.**

### 1.3 What you do **not** put on the tape

`gate_metrics`, `best_zx`, “is this ZX+90 or ZX−90?” are **logging**. SciPy’s `callback` can keep calling NumPy `fidelity.py` on `np.asarray(U)`. That is a printout, not a gradient.

`zx_90_unitary()` / `embed_in_full` run **once** at optimizer init. Constants. `jnp.asarray` them into `statics` in Phase 4. Do not rewrite Gaussian-free 4×4 matrices in JAX for sport.

Leakage weight in `CRGrapeConfig` is **0.0** today, so the cost is just `-F`. Still port `leakage_from_comp_jax`: it is five lines, and the NumPy cost already subtracts `leakage_weight * leakage` if you ever turn it on.

---

## 2. X-ray of the existing NumPy score

File: `optimization/fidelity.py`.

Read `process_fidelity` until you can recode it on paper. The JAX file is that function with `jnp` and without `float()`.

### 2.1 The Hilbert space picture (why 9 and why 4)

Two qutrits, `n_levels=3`. The engine state is **9-dimensional**. Computational subspace is **4-dimensional**:

```text
index   ket
  0     |0,0>     ← computational
  1     |0,1>     ← computational
  2     |0,2>     leakage (target |2>)
  3     |1,0>     ← computational
  4     |1,1>     ← computational
  5     |1,2>
  6     |2,0>
  7     |2,1>
  8     |2,2>
```

That list is `comp_idx = [0, 1, 3, 4]` (`DEFAULT_COMP_INDICES`). Same in both engines.

`U_full` is 9×9. **Column `j` is “what happens to basis ket `j`.”** Row `i` is the amplitude of ket `i` in that output.

The 4×4 **computational block** is the submatrix on those rows and columns:

```text
U_comp[a, b] = ⟨comp_a| U |comp_b⟩ = U_full[comp_idx[a], comp_idx[b]]
```

If you swap row/column (or stack evolved kets as rows instead of columns) you score U^\dagger and GRAPE will chase ZX†. Section 2.5 is the check.

### 2.2 Process fidelity (what GRAPE maximizes)

**ALREADY THERE:**

```python
P = comp_projector(dim, comp_indices)          # 9×9, 1 on the four comp diagonals
M = U_target_full.conj().T @ P @ U_full @ P
return float(abs(np.trace(M))**2 / d**2)       # d = 4
```

**In words:**

1. `P` is the projector onto `{|00>,|01>,|10>,|11>}`. `P v` zeros every leakage amplitude.
2. `P U P` keeps only “comp in → comp out.” Leakage in or out is dropped from the overlap.
3. `U_t† (P U P)` is “how much of the target did we do on that subspace.”
4. `tr(...)` sums the four diagonal overlaps. `abs(tr)² / 16` is Nielsen’s **process fidelity** of two unitaries on a `d=4` space (here the subspace).

If `U` is exactly the embedded target, `tr = 4`, `F = 1`. If the two 4×4 blocks are orthogonal in the Hilbert–Schmidt sense, `F = 0`.

**Why `abs` not `real`:** `tr` is complex. Process fidelity uses the modulus. `abs(z)**2` is `z * conj(z)` and is real.

**Why `/ d**2`:** Hilbert–Schmidt inner product of two `d×d` unitaries is at most `d`, so `|tr|² / d²` sits in `[0, 1]` when both are unitary on the subspace.

### 2.3 Equivalent 4×4 form (same number for GRAPE targets)

GRAPE’s `U_target_full` is `embed_in_full(zx_m90, dim=9)`: the 4×4 ZX lives on `comp_idx`, **identity on leakage**. For that family of targets,

```text
tr(U_t_full† P U P)  =  tr(U_t_comp† U_comp)
F = |tr(U_t_comp† U_comp)|² / 16
```

You may compute either way. Matching NumPy exactly is easiest if you keep the `P` sandwich: then any 9×9 target NumPy accepts, JAX accepts.

### 2.4 Average gate fidelity and leakage (logging / optional cost)

Average gate fidelity (Nielsen) from the **4×4 block** and a **4×4** target:

```python
overlap = np.trace(U_target_comp.conj().T @ U_comp)
F_avg = (abs(overlap)**2 + d) / (d * (d + 1))
```

This is **not** the GRAPE cost. Cost uses process fidelity. Port it anyway so the file is a 1–1 of the linear algebra.

Leakage, mean over the four computational **input** columns:

```python
# U_comp is 4×4
# column b: how much of |comp_b> stayed in the subspace
comp_weight = sum over rows |U_comp[a, b]|²
leakage = mean(1 - comp_weight)
```

`axis=0` in NumPy is “sum over rows, keep columns.” Same in JAX.

### 2.5 The transpose trap

`U_ij = ⟨comp_i | ψ_j⟩` with `ψ_j` = evolution of computational ket `j`.

If you later (Phase 4) evolve four kets and stack them as a `(4, 9)` array `psi` with `psi[j, :]` = ket `j`:

```python
idx = jnp.asarray(comp_indices)          # [0, 1, 3, 4]
U_comp = psi[:, idx].T                   # shape (4, 4)
# U_comp[i, j] = psi[j, comp_i] = ⟨comp_i|ψ_j⟩
```

If you forget `.T` you score the transpose. Test in this phase: `F(U, U_t)` and `F(U.T, U_t)` must **not** be forced equal when `U_t` is **not** symmetric.

**Caveat:** ZX±90 (and identity) are complex-symmetric, so `F(U, U_t) = F(U.T, U_t)` for those targets. That does **not** mean the transpose trap is harmless in Phase 4 — there you build `U_comp` from four kets, and a wrong layout is still ZX† vs ZX for a signed target once the pulse is near the gate. For the Phase 3 assert, use a **random nonsymmetric** `U_t`.

Phase 3 tests use a full 9×9 `U`, so you cannot make the ket-stacking mistake yet. Read it now so Phase 4 does not.

---

## 3. JAX rules for this file (short)


| Do                                             | Do not                                                    |
| ---------------------------------------------- | --------------------------------------------------------- |
| `jnp.abs`, `jnp.trace`, `jnp.matmul` / `@`     | `float(F)`                                                |
| return a **0-d** array, shape `()`             | `jnp.array([F])` shape `(1,)` — `jax.grad` wants a scalar |
| `comp_indices` as a Python tuple/list (static) | traced integer indices that change length                 |
| `U.conj().T`                                   | `np.conj` on a JAX array                                  |
| `atol=1e-14` vs NumPy                          | `atol=0` (same 1 ULP story as Phase 2)                    |


`**float(F)`:** turns a tracer into a Python float. That is the whole bug this phase exists to avoid. NumPy does it because SciPy wants a `float`. JAX cost must **not**.

`**jax.grad` of a shape `(1,)` array** is not what you want. `process_fidelity_jax` must look like `F = (abs(tr)**2) / (d*d)` with no extra `[None]`.

**x64:** do **not** put `jax.config.update` in `fidelity_jax.py`. Phase 0 owns that (`dq.set_precision("double")` in the dynamiqs engine). Phase 2 also set it in `pulses_jax.py`. The **test** should import one of those first (see §7). `dtype=complex128` on `jnp.asarray(U)` is then honoured.

---

## 4. Step 1 — file header + projector + block

**ADD** `optimization/fidelity_jax.py`:

```python
"""Process fidelity (and cousins) on JAX arrays.

Same formulas as optimization/fidelity.py. Returns 0-d jnp arrays, never Python floats.
"""
from __future__ import annotations

import jax.numpy as jnp

from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    DEFAULT_COMP_INDICES,
    COMP_DIM,
)


def _idx(comp_indices: list[int] | tuple[int, ...] | None) -> jnp.ndarray:
    """Static computational indices as a 1-d int array."""
    if comp_indices is None:
        comp_indices = DEFAULT_COMP_INDICES
    return jnp.asarray(comp_indices, dtype=jnp.int64)


def comp_projector_jax(
    dim: int,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """P, shape (dim, dim). Ones on the computational diagonal."""
    dim = int(dim)
    idx = _idx(comp_indices)
    # .at[idx, idx].set(1) writes the diagonal entries P[0,0], P[1,1], P[3,3], P[4,4]
    # not an outer product. That is what we want.
    P = jnp.zeros((dim, dim), dtype=jnp.complex128)
    return P.at[idx, idx].set(1.0)


def comp_block_jax(
    U_full: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """4×4 computational block. U_comp[a,b] = U_full[comp_a, comp_b]."""
    idx = _idx(comp_indices)
    # idx[:, None] is a column; idx is a row. Advanced indexing → outer pair of indices.
    # Same as NumPy U_full[np.ix_(comp_indices, comp_indices)].
    return U_full[idx[:, None], idx]
```

### 4.1 Syntax notes

`**P.at[idx, idx].set(1.0)`:** JAX arrays are immutable. You cannot write `P[i,i] = 1`. `.at[...].set(...)` returns a **new** array. `idx` is the same 1-d vector on both axes, so this sets the **diagonal** at those locations.

`**idx[:, None]`:** `idx` shape `(4,)`. `idx[:, None]` shape `(4, 1)`. Combined with `idx` shape `(4,)`, JAX broadcasts to all pairs `(idx[a], idx[b])`. Result shape `(4, 4)`.

This is **not** `U_full[idx][:, idx]` if you are being careful about copies, but for a 2-d matrix both give the same 4×4. Prefer the one-shot `U_full[idx[:, None], idx]`.

`**jnp.int64` on indices:** with x64 on, this is the natural index dtype. It is a constant (not a knob).

**Import `DEFAULT_COMP_INDICES` from NumPy `fidelity.py`:** one source of truth. Do not type `[0, 1, 3, 4]` in two files.

---

## 5. Step 2 — `process_fidelity_jax`

**ADD** to `fidelity_jax.py`:

```python
def process_fidelity_jax(
    U_full: jnp.ndarray,
    U_target_full: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Nielsen process fidelity on the computational subspace.

    U_full, U_target_full: (dim, dim) complex
    returns: 0-d real array (float64), shape ()
    """
    U_full = jnp.asarray(U_full)
    U_target_full = jnp.asarray(U_target_full)
    idx = _idx(comp_indices)
    d = int(idx.shape[0])
    dim = int(U_full.shape[0])

    P = comp_projector_jax(dim, comp_indices)
    M = U_target_full.conj().T @ P @ U_full @ P
    # jnp.abs on a complex 0-d array is the modulus. Do not use Python abs() out of habit;
    # it often works on 0-d jax arrays, but jnp.abs is the taped op.
    F = jnp.abs(jnp.trace(M)) ** 2 / (d * d)
    return F
```

### 5.1 Syntax notes

`**U_target_full.conj().T`:** conjugate transpose. For a 2-d matrix `.T` is enough. (Later, batched `(n_delta, 9, 9)` would use `jnp.conjugate(U).mT` or `vmap`. Phase 3 is one 9×9.)

`**@`:** `jnp.matmul`. Three of them. All stay on the tape. `P` is a constant, so JAX will treat ∂F/∂U through `P @ · @ P` as “only the 4×4 block matters,” which is the physics.

`**jnp.trace(M)`:** sum of the 9 diagonal entries. Leakage diagonal of `M` is 0 because of `P`, so this is the same as `tr` of the 4×4.

`**/ (d * d)`:** `d` is Python `4`. Dividing a traced scalar by 16 is fine. Do **not** `float()` the result.

**No `if U_target_full.shape != (dim, dim)` inside a jitted call with a traced check.** Shapes are static (`9`). If you want a guard, do it in Python on `int(U_full.shape[0])` before `jit`, or skip it: the test will fail loudly if you pass 4×4 by mistake.

**Return `F` not `F.real`:** `abs(z)**2` is already real (up to 1e-16 imaginary noise). If you ever see a tiny imaginary part, `jnp.real(F)` is ok; `float(F)` is not.

### 5.2 Optional 4×4 one-liner (not required)

If you want to see they match for embedded targets:

```python
def process_fidelity_comp_jax(U_comp, U_target_comp) -> jnp.ndarray:
    d = int(U_comp.shape[0])
    overlap = jnp.trace(U_target_comp.conj().T @ U_comp)
    return jnp.abs(overlap) ** 2 / (d * d)
```

GRAPE Phase 4 can call this after building `U_comp` from four kets. Phase 3 tests the 9×9 wrapper against NumPy. You may add the 4×4 helper now; you do not have to.

---

## 6. Step 3 — average gate fidelity and leakage

**ADD** to `fidelity_jax.py`:

```python
def average_gate_fidelity_jax(
    U_full: jnp.ndarray,
    U_target_comp: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Average gate fidelity from the 4×4 block. U_target_comp is 4×4, not 9×9."""
    U_full = jnp.asarray(U_full)
    U_target_comp = jnp.asarray(U_target_comp)
    idx = _idx(comp_indices)
    d = int(idx.shape[0])
    U_comp = comp_block_jax(U_full, comp_indices)
    overlap = jnp.trace(U_target_comp.conj().T @ U_comp)
    return (jnp.abs(overlap) ** 2 + d) / (d * (d + 1))


def leakage_from_comp_jax(
    U_full: jnp.ndarray,
    comp_indices: list[int] | tuple[int, ...] | None = None,
) -> jnp.ndarray:
    """Mean leakage of the four computational input kets."""
    U_comp = comp_block_jax(jnp.asarray(U_full), comp_indices)
    # axis=0: sum over rows → one number per input column
    comp_weight = jnp.sum(jnp.abs(U_comp) ** 2, axis=0)
    return jnp.mean(1.0 - comp_weight)
```

### 6.1 Syntax notes

`**U_target_comp` is 4×4.** NumPy `average_gate_fidelity` is the same. Do not pass `u_target_full` here. GRAPE already stores both.

`**jnp.sum(..., axis=0)`:** four numbers, one per computational input. `jnp.mean` of those is a 0-d scalar. Good for `jax.grad` if leakage weight is ever nonzero.

`**jnp.abs(U_comp) ** 2`:** elementwise `|z|²`. Same as `U_comp * U_comp.conj()` then `real`.

---

## 7. Step 4 — tests

**ADD** `optimization/optimization_tests/test_fidelity_jax.py`.

x64 must be on **before** the first `jnp.asarray`. Importing the dynamiqs engine (Phase 0) or `pulses_jax` (Phase 2) does that. Do one of them at the top:

```python
"""Compare fidelity_jax to optimization/fidelity.py."""
from __future__ import annotations

import numpy as np
import jax
import jax.numpy as jnp

# Enables x64 via dq.set_precision("double") at import.
from HM.simulator.two_qubit_simulator.engine import two_q_pulse_sim_dynamiqs  # noqa: F401

from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    DEFAULT_COMP_INDICES,
    average_gate_fidelity,
    comp_block,
    embed_in_full,
    leakage_from_comp,
    process_fidelity,
    zx_target_unitary,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity_jax import (
    average_gate_fidelity_jax,
    comp_block_jax,
    leakage_from_comp_jax,
    process_fidelity_jax,
)

ATOL = 1e-14


def _random_matrix(dim: int, rng: np.random.Generator) -> np.ndarray:
    """Complex 9×9, not unitary. The formula does not require U to be unitary."""
    re = rng.normal(size=(dim, dim))
    im = rng.normal(size=(dim, dim))
    return (re + 1j * im) / np.sqrt(2)


def test_identity_is_one() -> None:
    dim = 9
    I = np.eye(dim, dtype=complex)
    Ut = embed_in_full(np.eye(4, dtype=complex), dim=dim)
    F = process_fidelity_jax(I, Ut)
    assert F.shape == ()
    np.testing.assert_allclose(np.asarray(F), 1.0, atol=ATOL, rtol=0)
    print("identity F", float(F))


def test_perfect_zx_is_one() -> None:
    dim = 9
    U_t_comp = zx_target_unitary("zx_m90")
    U = embed_in_full(U_t_comp, dim=dim)
    F = process_fidelity_jax(U, U)
    np.testing.assert_allclose(np.asarray(F), 1.0, atol=ATOL, rtol=0)
    print("perfect zx_m90 F", float(F))


def test_matches_numpy_random() -> None:
    rng = np.random.default_rng(0)
    dim = 9
    Ut = embed_in_full(zx_target_unitary("zx_m90"), dim=dim)
    U = _random_matrix(dim, rng)

    F_np = process_fidelity(U, Ut)
    F_jx = process_fidelity_jax(U, Ut)
    np.testing.assert_allclose(np.asarray(F_jx), F_np, atol=ATOL, rtol=ATOL)

    np.testing.assert_allclose(
        np.asarray(comp_block_jax(U)),
        comp_block(U),
        atol=ATOL,
        rtol=ATOL,
    )
    np.testing.assert_allclose(
        np.asarray(average_gate_fidelity_jax(U, zx_target_unitary("zx_m90"))),
        average_gate_fidelity(U, zx_target_unitary("zx_m90")),
        atol=ATOL,
        rtol=ATOL,
    )
    np.testing.assert_allclose(
        np.asarray(leakage_from_comp_jax(U)),
        leakage_from_comp(U),
        atol=ATOL,
        rtol=ATOL,
    )
    print("random U  F_np", F_np, "F_jx", float(F_jx))


def test_transpose_is_not_the_same() -> None:
    # ZX±90 is complex-symmetric (U_t = U_t.T), so F(U)=F(U.T) for that target.
    # Use a nonsymmetric random target to see the transpose trap.
    rng = np.random.default_rng(1)
    U = _random_matrix(9, rng)
    Ut = _random_matrix(9, rng)
    F = float(process_fidelity_jax(U, Ut))
    FT = float(process_fidelity_jax(U.T, Ut))
    assert abs(F - FT) > 1e-6
    print("F(U)", F, "F(U.T)", FT)


def test_matches_numpy_parity_seed() -> None:
    """One real propagator. Layout is whatever run_propagator already uses."""
    from HM.simulator.two_qubit_simulator.optimization.optimization_tests.engine_parity_seed import (
        FLAT_LEN_NS,
        build_exp,
    )

    exp = build_exp("dynamiqs", n_sub=14)
    x_pi = exp.build_x_pi()
    timeline = exp._build_timeline(FLAT_LEN_NS, x_pi=x_pi)
    U = np.asarray(exp._propagator_from_timeline(timeline))
    Ut = embed_in_full(zx_target_unitary("zx_m90"), dim=U.shape[0])

    F_np = process_fidelity(U, Ut)
    F_jx = process_fidelity_jax(U, Ut)
    np.testing.assert_allclose(np.asarray(F_jx), F_np, atol=ATOL, rtol=ATOL)
    print("parity seed F_np", F_np, "F_jx", float(F_jx))


def test_process_fidelity_under_jit() -> None:
    Ut = jnp.asarray(embed_in_full(zx_target_unitary("zx_m90"), dim=9))

    @jax.jit
    def F_of(U):
        return process_fidelity_jax(U, Ut)

    rng = np.random.default_rng(2)
    U0 = jnp.asarray(_random_matrix(9, rng))
    a = F_of(U0)
    b = F_of(U0 * 1.01)
    assert a.shape == ()
    assert b.shape == ()
    assert not np.allclose(np.asarray(a), np.asarray(b))
    print("jit F", float(a), a.dtype)


if __name__ == "__main__":
    test_identity_is_one()
    test_perfect_zx_is_one()
    test_matches_numpy_random()
    test_transpose_is_not_the_same()
    test_matches_numpy_parity_seed()
    test_process_fidelity_under_jit()
    print("PHASE 3 OK")
```

Run from `fourqubitv5/`:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python \
  HM/simulator/two_qubit_simulator/optimization/optimization_tests/test_fidelity_jax.py
```

`**float(F)` in the test print:** allowed. That is after the JAX function returned. The function itself must not `float()`.

**Parity seed test** constructs a dynamiqs experiment (slow-ish first JIT of Tsit5). That is the same `U` Phase 1 already trusted. You are not testing `sesolve` quality; you are testing that JAX `F` on that `U` equals NumPy `F`.

---

## 8. What failure looks like

**Fail — `F` is a numpy float, jit ConcretizationTypeError:** you `float(trace)` or `float(F)` inside `process_fidelity_jax`.

**Fail — `jax.grad` later complains about non-scalar:** you returned shape `(1,)`. Check `F.shape == ()` in the test.

**Fail — `F ≈ 1` on the identity test but random U disagrees at `1e-2`:** you used `U[idx, :][:, idx]` wrong, or `.T` without `.conj()`, or `d` instead of `d**2`.

**Fail — identity is not 1:** projector is an outer product (`P.at[idx[:, None], idx]`) instead of the diagonal `.at[idx, idx]`. Then `P` is all-ones on the 4×4 block, not a projector.

**Fail — `F(U)` equals `F(U.T)` with a nonsymmetric random `U_t`:** your `comp_block` symmetrised the matrix, or you used `U + U.T`. Equal under a ZX target is expected (§2.5).

**Fail — x64 warning, disagreement at `1e-6`:** the test did not import the dynamiqs engine / `pulses_jax` first. Same lesson as Phase 2.

**Fail — parity seed `F_jx` is 0.0 and NumPy is ~0.7:** `U` came in as an object / QArray and `jnp.asarray` did not copy the numbers. `np.asarray(U)` first, then pass to JAX (the test already does this).

**Pass:** `PHASE 3 OK`. Identity and perfect ZX print `1`. Random and parity lines show `F_np` and `F_jx` agreeing. With a nonsymmetric `U_t`, `F(U)` and `F(U.T)` differ. `jit F` is `float64`, shape `()`.

---

## 9. How this slots into Phase 4 (do not write it yet)

```python
# Phase 4, not now:
knobs = x[0::2] + 1j * x[1::2]
cr_plus, _ = assemble_cr_half_jax(knobs, rise=..., fall=..., n_flat=...)
timeline = echoed_timeline_jax(cr_plus, x_pi)
U = sim.run_propagator(timeline)                 # stay JAX, no np.asarray
F = process_fidelity_jax(U, U_target_full)       # this file
return -F                                        # shape ()
```

or, with four kets (cheaper, same F if you index columns correctly):

```python
psi = sim.evolve_comp(timeline)     # (4, 9) or (4, 9, 1)
U_comp = psi[:, idx].T              # see §2.5
F = process_fidelity_comp_jax(U_comp, U_target_comp)
```

Phase 4 decides sepropagator vs 4 kets. Phase 3 only proves the scalar `F` is the NumPy scalar.

`jax.grad` of `process_fidelity_jax` w.r.t. `U` is a useful smoke test you may do **in the test file** if you are curious (`jax.grad(lambda U: process_fidelity_jax(U, Ut))(U0)` should be a 9×9). You do **not** need it to pass Phase 3. Do not wire SciPy `jac=` yet.

---

## 10. What the module looks like when you are done

```text
fidelity_jax.py
    _idx, comp_projector_jax, comp_block_jax
    process_fidelity_jax(U_full, U_target_full) -> shape ()
    average_gate_fidelity_jax, leakage_from_comp_jax

fidelity.py                         # UNCHANGED
cr_grape.py process_fidelity        # UNCHANGED (still NumPy)
```

---

## 11. Stop condition

Phase 3 is **done** when:

1. `test_fidelity_jax.py` prints `PHASE 3 OK`.
2. `process_fidelity_jax` matches NumPy at `atol=1e-14` on a random 9×9 and on the parity-seed `U`.
3. Identity and embedded ZX self-fidelity are 1.
4. Return shape is `()`.
5. `jax.jit` of `process_fidelity_jax` runs twice with different `U`.

Then stop. Do not open `grape_cost` until that is true. Phase 4 is a later MD.