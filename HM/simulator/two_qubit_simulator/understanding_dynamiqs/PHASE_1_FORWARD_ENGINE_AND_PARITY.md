# Phase 1 — JAX-pure forward engine + QuTiP parity

Instructions only. You type the code. Finish Phase 0 first (`PHASE_0_UPGRADE_AND_JAX_CONFIG.md` prints `PHASE 0 OK`).

Parent tutorial: `DYNAMIQS_GRAPE_MIGRATION.md` §3.4, §3.5, §3.8–3.10, Phase 1 checklist.

This is the phase where dynamiqs stops being “a class that exists” and starts being “the thing GRAPE will call.” You still **do not** call `jax.grad`. You get one number: process fidelity of a seed echoed-CR pulse, from both engines, on the **same** timeline.

---

## 0. What I would have implemented, in order

If I were committing this myself, I would do **exactly** these edits, in this order, and stop at the parity script until F is close.


| Step | File                                                            | What                                                                                 |
| ---- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 1    | `engine/two_q_pulse_sim_dynamiqs.py`                            | `dq.destroy(*dims)` instead of `kron`                                                |
| 2    | same                                                            | `set_target_frame`; `__init__` uses it                                               |
| 3    | `engine/two_q_pulse_sim.py`                                     | same method, **scalar only**                                                         |
| 4    | dynamiqs `_build_hamiltonian`                                   | delete the zero-channel `if` (no comments left)                                      |
| 5    | dynamiqs `_drive_hamiltonian`                                   | `sample_index` = `floor` then `clip` (not `int32` then `floor`)                      |
| 6    | dynamiqs `__init__` + `sesolve` / `sepropagator`                | `Tsit5(..., max_steps=1_000_000)` and store `BackwardCheckpointed`; pass `gradient=` |
| 7    | `experiments/cr_len_sweep.py`                                   | `_propagator_from_timeline` dispatches to `run_propagator` if it exists              |
| 8    | **new** `optimization/optimization_tests/engine_parity_seed.py` | one timeline, two engines, print                                                     |


**Not in Phase 1:** `pulses_jax.py`, `fidelity_jax.py`, `grape_cost`, SciPy `jac=`, robust length-2 `set_target_frame` in the optimizer, `mesolve`, GPU.

**Optional 1b, only after parity is green:** `evolve_comp` (4 computational kets). Do not write it before you trust full U.

---

## 1. Why this phase exists (logic, not vibes)

Today GRAPE does this even when `engine="dynamiqs"`:

```python
# cr_len_sweep._propagator_from_timeline  — ALREADY THERE
psi0 = qt.basis(sim.dims, [c, t])   # QuTiP ket
psi = sim.run_shot(timeline, psi0=psi0)
U[:, col] = psi.full().flatten()
```

Nine Python loops, nine `run_shot`s. Dynamiqs `run_propagator` (`dq.sepropagator`, one 9×9 U) is never called. So “I set engine dynamiqs” does not mean “GRAPE uses sepropagator.”

Phase 1 does three jobs:

1. **Clean the Hamiltonian builder** so it is the same physics as QuTiP, and so later `jit`/`grad` will not explode (`destroy`, always-add drives, `set_target_frame` as the only writer of \Delta).
2. **Point the experiment at `run_propagator`** when the simulator has that method.
3. **Prove** QuTiP `n_sub=14` and dynamiqs Tsit5 give close U / F on one echoed seed. If they do not, you do not start Phase 2. You debug units.

`np.asarray` on the propagator is **still allowed** here. Parity is a Python script comparing two NumPy matrices. Removing `np.asarray` is Phase 4 (`jax.grad`). If you remove it now, the parity script has to learn QArrays for no reason.

---

## 2. Files you will touch

```text
engine/two_q_pulse_sim_dynamiqs.py          # most of the work
engine/two_q_pulse_sim.py                   # set_target_frame only
experiments/cr_len_sweep.py                 # 4-line dispatch
optimization/optimization_tests/engine_parity_seed.py   # NEW file
```

Do not edit `device_base.py`. Do not edit `cr_grape.py`. Lab frames stay scalars at construction.

---

## 3. Step 1 — operators: `dq.destroy(*self.dims)`

### 3.1 What is there now

**ALREADY THERE** in `_build_operators`:

```python
n0, n1 = self.dims
a0_local, a1_local = dq.destroy(n0), dq.destroy(n1)
I0, I1 = jnp.eye(n0), jnp.eye(n1)

a0 = jnp.kron(dq.to_jax(a0_local), I1)
a1 = jnp.kron(I0, dq.to_jax(a1_local))
self.a = [a0, a1]
self.ad = [op.conj().T for op in self.a]
```

**Syntax:**

- `dq.destroy(3)` → annihilation operator on **one** 3-level system, dynamiqs `QArray` 3×3.
- `dq.to_jax(...)` → strip to a raw JAX 3×3 so `jnp.kron` will accept it (`kron` does not take QArrays).
- `jnp.kron(a0_local, I1)` → a \otimes I on the 9-dimensional joint space.
- `op.conj().T` → a^\dagger for a dense JAX matrix (`@` later is matmul, not kron).

The **9×9 numbers are correct**. You lose `dims=(3,3)` metadata: dynamiqs then sees a 9-level blob. GRAPE does not need `ptrace`, so that did not bite you. It is just four lines of “I reimplemented `dq.destroy(3, 3)`.”

### 3.2 What to type instead

**REPLACE** the block above (from `a0_local, ...` through `self.ad = ...`) with:

```python
        n0, n1 = self.dims
        a0, a1 = dq.destroy(*self.dims)
        self.a = [a0, a1]
        self.ad = [a.dag() for a in self.a]
```

**Syntax:**

- `*self.dims` unpacks `[3, 3]` into `dq.destroy(3, 3)`.
- `dq.destroy(n0, n1)` returns **two** QArrays already embedded: a\otimes I and I\otimes a, with `dims=(n0, n1)`.
- `.dag()` is dynamiqs for conjugate transpose (same as QuTiP `.dag()`). On a JAX ndarray you used `.conj().T`; on a QArray you use `.dag()`.

Leave the rest of `_build_operators` as it is: drift loop, `coupling_op`, `_drive_ops`. `@` still means matmul. `TWOPI * 0.5 * qb.anharm_MHz * ad@ad@a@a` is still (\alpha/2) a^{\dagger}a^{\dagger}aa in angular MHz.

`dq.asqarray(...)` around those products is redundant if they are already QArrays, but **leave it**. Harmless. Do not also rewrite drift in this step; one behavior change at a time.

**Logic:** rotating frame is unchanged. Drift is still **only anharmonicity**. Frequencies still live in `frame_MHz` and in `exp(i 2\pi \Delta t)`, not on the diagonal.

---

## 4. Step 2 — `set_target_frame` on the dynamiqs engine

### 4.1 Why a method, not a new `run_propagator` argument

Coupling reads `self.delta_qq_MHz`. Drives read `self.qubits[dl.target].frame_MHz`. Those two must not disagree. Today `__init__` does:

```python
self.delta_qq_MHz = self.qubits[0].frame_MHz - self.qubits[1].frame_MHz
```

and nothing updates both together later. Robust GRAPE currently pokes them by hand on two objects. Phase 1 installs **one writer**. You will not pass a length-2 array in the parity script. You only make the method exist and use it for the lab scalar.

### 4.2 ADD the method on `TwoQubitPulseSimulatorDynamiqs`

Put it **after** `__init__` (or after `_build_operators`). I would put it immediately after `__init__`, before `_build_operators`, so “how frames get onto the object” is next to construction.

**ADD THIS:**

```python
    def set_target_frame(self, frame1):
        """Install the target rotating-frame frequency.

        ``frame1`` is the lab scalar (float) at construction, or later a
        jax array of shape (n,) for batched ZZ worlds. Coupling detuning
        is always derived: delta_qq = frame_control - frame_target.
        Drive detuning for q2_drive is carrier - frame1, so it tracks this
        too. cr_drive targets the control and does not read frame1.
        """
        self.qubits[1].frame_MHz = frame1
        self.delta_qq_MHz = self.qubits[0].frame_MHz - frame1
```

**Syntax:** no type annotation on purpose. A float and a `jnp.ndarray` both support `-`. If `frame1` has shape `(2,)`, `delta_qq_MHz` becomes shape `(2,)`. `_coupling_hamiltonian` already does `delta = self.delta_qq_MHz` and `jnp.exp(1j * TWOPI * delta * t)` — broadcasting then batches H. You do **not** change `_coupling_hamiltonian` in Phase 1.

**Logic:** this **is** shifting the target frequency. There is no extra diagonal \omega |1\rangle\langle1|. Do not also invent a second `delta` that disagrees with `frame0 - frame1`.

Do not import JAX in this method. If the caller passes a jax array, subtraction uses jax because of how the array types work. If they pass a float, you get a float.

### 4.3 REPLACE the `__init__` line that sets `delta_qq`

**ALREADY THERE:**

```python
        self.dim = self.dims[0] * self.dims[1]
        self.delta_qq_MHz = self.qubits[0].frame_MHz - self.qubits[1].frame_MHz
        self.comp_idx = [0, 1, self.dims[1], self.dims[1] + 1]
```

**REPLACE** the middle line with a call (keep `dim` and `comp_idx`):

```python
        self.dim = self.dims[0] * self.dims[1]
        self.set_target_frame(self.qubits[1].frame_MHz)
        self.comp_idx = [0, 1, self.dims[1], self.dims[1] + 1]
```

**Logic:** `build_qubits` already put `frame_MHz=-DELTA` on qubit 1. You pass that same float into the writer. After this, `self.delta_qq_MHz` is still the lab detuning. Parity must print the same \Delta on both engines.

`self.qubits` must already be assigned (`self.qubits = list(qubits)` is above this). Do not call `set_target_frame` before that.

---

## 5. Step 3 — same method on the QuTiP engine (scalar only)

Same physics, so the name exists on both simulators. QuTiP `_hamiltonian_at` cannot batch. If you stuff a length-2 array into `frame_MHz`, `np.exp(1j * TWOPI * delta * t)` becomes a length-2 array and QuTiP `Qobj` arithmetic dies.

**ADD** on `TwoQubitPulseSimulator` in `two_q_pulse_sim.py`, next to where `delta_qq` is currently set. I would add the method on the class, then **replace** the assignment inside `_build_operators`.

**ADD THIS** method (e.g. just before `_build_operators`):

```python
    def set_target_frame(self, frame1):
        """Install a scalar target rotating-frame frequency (MHz).

        Arrays are rejected: this engine has no Hamiltonian batch axis.
        """
        frame1_arr = np.asarray(frame1)
        if frame1_arr.ndim > 0 and frame1_arr.size != 1:
            raise TypeError(
                "QuTiP engine set_target_frame expects a scalar; "
                f"got shape {frame1_arr.shape}. Use engine='dynamiqs' to batch."
            )
        self.qubits[1].frame_MHz = float(frame1_arr)
        self.delta_qq_MHz = float(self.qubits[0].frame_MHz) - self.qubits[1].frame_MHz
```

**REPLACE** inside `_build_operators` this **ALREADY THERE** line:

```python
        self.delta_qq_MHz = self.qubits[0].frame_MHz - self.qubits[1].frame_MHz
```

with:

```python
        self.set_target_frame(self.qubits[1].frame_MHz)
```

`float(frame1_arr)` on a 0-d array is the Python float. `ndim > 0 and size != 1` catches shape `(2,)`. A 0-d jax/numpy scalar still works.

Parity uses lab scalars on both engines, so this method is just “same API.” Robust QuTiP can later call `set_target_frame(f1 + s)` instead of `_apply_target_freq_shift` if you want; **do not** change `cr_grape_robust.py` in Phase 1.

---

## 6. Step 4 — always add drive channels (delete the skip)

### 6.1 What is wrong

**ALREADY THERE** (you may have commented it; delete it either way):

```python
            eps_arr = jnp.array(timeline[name], dtype=complex)
            # if jnp.all(eps_arr == 0):
            #     continue+
            H = H + self._drive_hamiltonian(name, eps_arr, discontinuity_ts)
```

or the live version:

```python
            if jnp.all(eps_arr == 0):
                continue
```

**Logic:**

- Under `jax.grad`, `eps_arr` depends on knobs → **traced**. `if traced: continue` is a Python branch on a placeholder → `ConcretizationTypeError`.
- Even in forward mode, skipping a channel **removes a term from the Hamiltonian pytree**. One call has 5 pieces, the next has 4. `jit` retraces. Zero envelope is a valid drive: H_\text{drive}=0.

QuTiP still skipping `if eps == 0.0` inside `_hamiltonian_at` is fine: that is a Python float per sample, not a traced array, and QuTiP is not jitted. Do not “fix” QuTiP in Phase 1.

### 6.2 What to type

**REPLACE** the loop body in `_build_hamiltonian` with:

```python
        H = self.H_drift + self._coupling_hamiltonian()
        for name in self.channel_names:
            eps_arr = jnp.asarray(timeline[name], dtype=jnp.complex128)
            H = H + self._drive_hamiltonian(name, eps_arr, discontinuity_ts)
        return H
```

Do **not** keep `if name not in timeline: continue` on the dynamiqs path. It is true that this branch is a **Python** dict-keys check, not a traced numeric `if`, so it would not immediately break JAX. But it still lets the Hamiltonian tree change across calls depending on which channels were present. The cleaner rule for the JAX engine is stronger:

> every timeline must contain **all** channels in `self.channel_names`, and idle channels are represented by explicit zero arrays.

That makes the Hamiltonian structure literally the same every call.

### 6.3 Why you are allowed to require all channels

For the code paths you actually use, the timeline already behaves this way.

- `Timeline.finalize()` in `engine/pulses.py` pads **every** channel to the same common length and returns the whole dict.
- `CR_len_sweep._build_timeline(...)` and `_build_timeline_from_cr_half(...)` both build timelines through `Timeline(...)`, then call `finalize()`.

So even if only `cr_drive` and `q1_drive` receive pulses, `q2_drive` is still present as a zero array. That means deleting the membership check does **not** remove needed functionality for echoed CR. It only turns an optional convention into an explicit requirement.

### 6.4 What this implies for future code

If later you hand-build a timeline dict yourself, you must include all channels, e.g.

```python
timeline = {
    "q1_drive": q1_arr,
    "q2_drive": jnp.zeros(L, dtype=jnp.complex128),
    "cr_drive": cr_arr,
}
```

Do not rely on “missing key means idle” on the dynamiqs path anymore. Missing key should now be treated as a caller bug, not something `_build_hamiltonian` silently patches over.

**Syntax:** `jnp.asarray(..., dtype=jnp.complex128)` not `dtype=complex`. Python’s `complex` is a dtype helper that can go through NumPy. `complex128` matches Phase 0 double precision.

`discontinuity_ts = jnp.linspace(0.0, L * self.dt_sample_us, L + 1)` stays. Those are the 1 ns (or `dt_sample`) edges. Tsit5 restarts there so it does not step across an envelope jump.

---

## 7. Step 5 — `sample_index`: floor, then clip

### 7.1 What it is doing

Tsit5 asks for H(t) at arbitrary t in **µs**. The envelope is a staircase, one complex number per sample. `sample_index(t)` is “which stair.”

Let `dt_us = dt_sample_ns * 1e-3` (GRAPE: `0.001`). `eps_arr` length `n_eps = L`.

- `t / dt_us` → how many samples have elapsed (float).
- `floor` → bin k covering [k\mathrm{dt}, (k+1)\mathrm{dt}).
- `clip(..., 0, n_eps-1)` → legal index. Upper clamp: at t=T=L\cdot\mathrm{dt} the division equals L, off the end of a length-L array. Lower clamp: ODE may probe t slightly below 0.

### 7.2 A bug to not ship

If you already wrote this, **fix it**:

```python
i = jnp.floor(jnp.int32(t / dt_us)).astype(jnp.int32)  # WRONG
```

`int32` **first** truncates toward zero, then `floor` of an integer does nothing. You wanted floor of the **float**. For t\ge 0 truncation toward zero equals floor, so you might not notice. For t<0, `int32(-0.3)` is `0`, `floor(-0.3)` is `-1` then clip to `0`. Write floor first.

**REPLACE** `sample_index` with:

```python
        def sample_index(t: float) -> jnp.ndarray:
            i = jnp.floor(t / dt_us).astype(jnp.int32)
            return jnp.clip(i, 0, n_eps - 1)
```

`coeff_ad` / `coeff_a` stay: envelope from `eps_arr[sample_index(t)]`, times `exp(\pm i 2\pi \delta t)` with \delta = `carrier - frame`. Envelope piecewise constant; carrier continuous. That is Path A.

Do **not** switch to `dq.pwc` in Phase 1. You cannot write `pwc * modulated` in dynamiqs (`*` multiplies operators). Combined `modulated` is already the right type.

---

## 8. Step 6 — Tsit5 `max_steps` and store `BackwardCheckpointed`

### 8.1 Integrator

**ALREADY THERE:**

```python
        self._integrator_method = dq_method.Tsit5(
            atol=integrator_tol,
            rtol=integrator_tol,
        )
```

Default `max_steps` on your dynamiqs 0.3.4 is **100000**. A ~100 MHz coupling over a few hundred ns, tolerances `1e-9`, can exceed that. Then Tsit5 errors “max steps reached” and you will think the Hamiltonian is wrong.

**REPLACE** with:

```python
        self._integrator_method = dq_method.Tsit5(
            atol=integrator_tol,
            rtol=integrator_tol,
            max_steps=1_000_000,
        )
        self._gradient = dq.gradient.BackwardCheckpointed()
```

You need `import dynamiqs as dq` (already there). `dq.gradient` is a submodule; Phase 0 already proved `BackwardCheckpointed` imports.

`n_sub` stays on the object, unused. Path A does not use it. QuTiP parity will still pass `n_sub=14`.

### 8.2 Pass `gradient=` into the three solvers

On 0.3.4, `sesolve` / `sepropagator` take `gradient=` as a keyword. If it is `None`, autodiff later uses a default. Setting it **now** does not run a backward pass. It only records *which* adjoint to use **when** someone later calls `jax.grad`. Forward numbers should be unchanged.

**REPLACE** each `dq.sesolve(...)` and `dq.sepropagator(...)` so they include `gradient=self._gradient`.

`run_shot` — **ALREADY THERE** call, add one keyword:

```python
        result = dq.sesolve(
            H,
            y0,
            tsave,
            method=self._integrator_method,
            gradient=self._gradient,
            options=self._sesolve_options,
        )
```

`run_propagator`:

```python
        result = dq.sepropagator(
            H,
            tsave,
            method=self._integrator_method,
            gradient=self._gradient,
            options=self._seprop_options,
        )
```

`run_shot_batch`: same `gradient=self._gradient` on its `sesolve`.

**Leave** `return np.asarray(dq.to_jax(result.final_propagator))`. Parity wants a NumPy 9×9. `jax.grad` will need a second path later; not now.

---

## 9. Step 7 — dispatch `_propagator_from_timeline`

File: `experiments/cr_len_sweep.py`.

**ALREADY THERE:**

```python
    def _propagator_from_timeline(self, timeline):
        """Assemble the joint Hilbert-space propagator by evolving each basis ket."""
        sim = self.simulator
        n0, n1 = sim.dims
        dim = n0 * n1
        U = np.zeros((dim, dim), dtype=complex)
        for c in range(n0):
            for t in range(n1):
                col = c * n1 + t
                psi0 = qt.basis(sim.dims, [c, t])
                psi = sim.run_shot(timeline, psi0=psi0)
                U[:, col] = psi.full().flatten()
        return U
```

QuTiP has no `run_propagator`. Dynamiqs does. `hasattr` is the switch. Do **not** add `run_propagator` to QuTiP in Phase 1 (you would have to write a 9-ket loop there anyway).

**REPLACE** the whole method with:

```python
    def _propagator_from_timeline(self, timeline):
        """Full Hilbert-space unitary for this experiment's engine.

        Dynamiqs: one ``sepropagator`` call (``sim.run_propagator``).
        QuTiP: evolve each basis ket with ``run_shot`` (no run_propagator).
        """
        sim = self.simulator
        run_U = getattr(sim, "run_propagator", None)
        if callable(run_U):
            return run_U(timeline)
        n0, n1 = sim.dims
        dim = n0 * n1
        U = np.zeros((dim, dim), dtype=complex)
        for c in range(n0):
            for t in range(n1):
                col = c * n1 + t
                psi0 = qt.basis(sim.dims, [c, t])
                psi = sim.run_shot(timeline, psi0=psi0)
                U[:, col] = psi.full().flatten()
        return U
```

**Syntax:** `getattr(sim, "run_propagator", None)` so a missing method is not an `AttributeError`. `callable` so you do not trip on a random attribute.

**Logic:** GRAPE, generator extraction, diagnose scripts all call this one method. After this, `engine="dynamiqs"` actually uses `sepropagator`. `engine="qutip"` is bit-identical to before.

Keep the `import qutip as qt` at the top of `cr_len_sweep.py`; the else branch still needs it.

---

## 10. Step 8 — parity script (type this whole file)

**ADD** file:

`optimization/optimization_tests/engine_parity_seed.py`

Same timeline object (NumPy, from the QuTiP experiment’s pulse builder) fed to both engines. If you let each experiment build its own timeline, you could silently compare two different pulses.

Type this:

```python
"""Compare QuTiP vs dynamiqs on one echoed-CR seed timeline.

Phase 1 gate: stop and debug if |F_q - F_d| is ~0.01. Proceed to Phase 2
if max|Uq-Ud| is ~1e-3 to 1e-6 and F agrees at that level.

Run from fourqubitv5/ so HM imports:

    python -m HM.simulator.two_qubit_simulator.optimization.optimization_tests.engine_parity_seed
"""
from __future__ import annotations

import numpy as np

from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import DEFAULT_CR_PULSE_PARAMS
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    embed_in_full,
    leakage_from_comp,
    process_fidelity,
    zx_target_unitary,
)


def build_exp(engine: str, n_sub: int = 14) -> CR_len_sweep:
    return CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        n_sub=n_sub,
        engine=engine,
        cr_pulse_params={
            **DEFAULT_CR_PULSE_PARAMS,
            "amp_mhz": 21.0,
            "phase_rad": 0.0,
            "t_rise_ns": 16,
        },
    )


def main() -> None:
    flat_len_ns = 122.0
    exp_q = build_exp("qutip", n_sub=14)
    exp_d = build_exp("dynamiqs", n_sub=14)  # n_sub unused on Path A Tsit5

    print("delta_qq qutip   ", exp_q.simulator.delta_qq_MHz)
    print("delta_qq dynamiqs", exp_d.simulator.delta_qq_MHz)

    x_pi = exp_q.build_x_pi()
    timeline = exp_q._build_timeline(flat_len_ns, x_pi=x_pi)

    U_q = exp_q._propagator_from_timeline(timeline)
    U_d = exp_d._propagator_from_timeline(timeline)

    dim = U_q.shape[0]
    print("U shapes", U_q.shape, U_d.shape, "dim", dim)

    du = np.max(np.abs(U_q - U_d))
    print("max |Uq - Ud|", du)

    for name in ("zx_90", "zx_m90"):
        Ut = embed_in_full(zx_target_unitary(name), dim=dim)
        Fq = process_fidelity(U_q, Ut)
        Fd = process_fidelity(U_d, Ut)
        print(
            name,
            "F_q", Fq,
            "F_d", Fd,
            "|dF|", abs(Fq - Fd),
            "leak_q", leakage_from_comp(U_q),
            "leak_d", leakage_from_comp(U_d),
        )


if __name__ == "__main__":
    main()
```

**Why `amp_mhz=21`, `phase_rad=0`:** a simple on-axis CR so ZX vs ZY is not a phase puzzle. `DEFAULT_CR_PULSE_PARAMS` still supplies `t_rise_ns` etc.; you override amp/phase.

**Why `flat_len_ns=122`:** long enough to be a real gate, short enough that QuTiP `n_sub=14` finishes. Do not start with 400 ns.

**Why print both ZX90 and ZXm90:** seed sign/convention; you care that **the two engines agree with each other**, not that F=1.

**Why `n_sub=14` on dynamiqs:** ignored by Tsit5, but `CR_len_sweep` still stores it. Harmless. QuTiP **uses** it; that is the fair “well resolved oscillation” comparison (Path A vs QuTiP-fine).

**How to run** (from `fourqubitv5/` so `HM` is importable — same as your other tests):

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python -m \
  HM.simulator.two_qubit_simulator.optimization.optimization_tests.engine_parity_seed
```

If `optimization_tests` is not a package (`__init__.py` missing), either add an empty `__init__.py` there or run:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5
PYTHONPATH=. /home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python \
  HM/simulator/two_qubit_simulator/optimization/optimization_tests/engine_parity_seed.py
```

---

## 11. How to read the parity numbers

`delta_qq` on both lines **must match** (lab scalar, same pair). If they do not, `set_target_frame` / construction is wrong. Do not interpret F until they match.


| What you see                                                        | Meaning                                                                            |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `max                                                                | Uq-Ud                                                                              |
|                                                                     | F_q-F_d                                                                            |
| U close only if you later build Path B Expm                         | Discretization gap, not a wiring bug. Decide then; do not start Path B in Phase 1. |
| dynamiqs “max steps”                                                | you forgot `max_steps=1_000_000`.                                                  |
| dynamiqs still 9× slower in a weird way and `qt.basis` in traceback | dispatch did not run; still the 9-ket loop.                                        |


Global phase: U_q-U_d can look large if one engine dumps a global phase. Process fidelity is phase-insensitive in the usual definition you already use. If `max|U|` is ugly but F agrees to 10^{-4}, print `np.max(np.abs(U_q * np.exp(-1j*phi) - U_d))` with `phi = np.angle((U_q.conj()*U_d).trace())` before panicking. If **both** `max|U|` and F disagree, it is not global phase.

---

## 12. Optional 1b — `evolve_comp` (only after parity is green)

GRAPE cost only needs 4 computational kets, not 9. After you trust `run_propagator`, add this on the dynamiqs class. **Do not** switch the parity script to it until full U agrees.

**ADD:**

```python
    def evolve_comp(self, timeline: dict[str, np.ndarray]) -> jnp.ndarray:
        """Evolve |00>,|01>,|10>,|11> in one sesolve.

        Returns jax array shape (4, dim, 1), or (n_delta, 4, dim, 1) if
        delta_qq / frame1 is batched. Leaves the result as JAX (no np.asarray)
        so a later grad path can use it. Parity/GRAPE-numpy can np.asarray
        at the call
```

 site.
        """
        L = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        psi0 = jnp.zeros((4, self.dim, 1), dtype=jnp.complex128)
        for i, idx in enumerate(self.comp_idx):
            psi0 = psi0.at[i, idx, 0].set(1.0)
        y0 = dq.asqarray(psi0)
        tsave = jnp.array([0.0, L * self.dt_sample_us])
        result = dq.sesolve(
            H,
            y0,
            tsave,
            method=self._integrator_method,
            gradient=self._gradient,
            options=self._sesolve_options,
        )
        return result.states[:, -1]

**Syntax:** `psi0.at[i, idx, 0].set(1.0)` is JAX’s “write without mutating.” A Python `psi0[i,idx]=1` on a traced array is illegal later; doing it right now means you do not rewrite this in Phase 4.

**Logic:** `comp_idx = [0, 1, n1, n1+1]` is |00\rangle,|01\rangle,|10\rangle,|11\rangle`in the flattened 9. Column vectors`(dim, 1)` match dynamiqs/QuTiP.

If `H` is batched (you called `set_target_frame` with shape `(2,)`), cartesian batching with `y0` shape `(4, dim, 1)` should yield states with a leading detuning axis. **Do not test that in Phase 1.** Parity uses lab scalars.

`result.states[:, -1]` — check the actual `states` layout if this errors (sometimes the time index is last). Print `result.states.shape` once. You want the **final** time, all 4 kets.

---

## 13. What you should see in the dynamiqs file when Phase 1 (without 1b) is done

Conceptual skeleton:

```text
_configure_jax()                    # Phase 0
class TwoQubitPulseSimulatorDynamiqs:
    __init__:
        reject enable_x64=False     # Phase 0
        set_target_frame(lab float) # Phase 1
        Tsit5(..., max_steps=1e6)
        _gradient = BackwardCheckpointed()
        _build_operators()
    set_target_frame(frame1)
    _build_operators:
        a0, a1 = dq.destroy(*dims)
        ad = dag
        H_drift anharmonicity only
    _coupling_hamiltonian:
        delta = self.delta_qq_MHz   # unchanged
        modulated exp(±i 2π delta t)
    _drive_hamiltonian:
        sample_index = floor + clip
        modulated eps[i(t)] * exp(±i 2π δ t)
    _build_hamiltonian:
        always add every channel in timeline
    run_shot / run_propagator / run_shot_batch:
        gradient=self._gradient
        run_propagator still np.asarray(U)
```

---

## 14. Stop condition

Phase 1 is **done** when:

1. Both `delta_qq` printouts match.
2. Dynamiqs path traceback (if you set a breakpoint) goes through `run_propagator` / `sepropagator`, not nine `qt.basis`.
3. F_q-F_d is in the 10^{-3}–10^{-6} ballpark, or you have a written reason it is discretization (and you still accept Path A).

Then stop. Do not open `pulses_jax.py` until that is true. Phase 2 is `PHASE_2_...` (next MD when you ask).