# Two-qubit dynamiqs engine and GRAPE — a tutorial for the person who has not read their own code

This file is the migration guide. It is meant to be read in order. Six-qubit work is out of scope. The goal is a **2-qubit simulator** you can run as QuTiP or dynamiqs with a switch, then GRAPE that can take derivatives through dynamiqs.

You already have the switch for *which class gets constructed*:

```python
# base_classes/device_base.py
engine = kwargs.get("engine", "qutip")   # default is still QuTiP
```

`engine="qutip"` → `TwoQubitPulseSimulator`  
`engine="dynamiqs"` → `TwoQubitPulseSimulatorDynamiqs`

That switch does **not** yet mean GRAPE is differentiable or fast. GRAPE still builds the propagator by looping QuTiP basis kets through `run_shot`. This document is about making the dynamiqs side real, then wiring GRAPE to it.

Convention in this file:

- **Existing** = code already in the repo (often written by an AI assistant).
- **New** = what you should write next.
- If a snippet is a **replacement**, it is labelled `REPLACE THIS`.
- If it is **new**, it is labelled `ADD THIS`.
- If it is **already in your file**, it is labelled `ALREADY THERE`.

---

## 0. Upgrade dynamiqs first

Your env currently has **dynamiqs 0.3.3**. Current stable docs use different names:


| 0.3.3 (what you have)                                    | Current stable docs                               |
| -------------------------------------------------------- | ------------------------------------------------- |
| `dq.gradient.Autograd`                                   | `dq.gradient.Direct`                              |
| `dq.gradient.CheckpointAutograd`                         | `dq.gradient.BackwardCheckpointed`                |
| `dq.gradient.ForwardAutograd`                            | `dq.gradient.Forward`                             |
| `dq.sesolve(..., options=dq.Options(save_states=False))` | `dq.sesolve(..., save_states=False)` as a keyword |


You said we can redo against the latest package. Do that **before** writing GRAPE autodiff, so you do not learn the old names.

```bash
pip install -U dynamiqs
python -c "import dynamiqs as dq; print(dq.__version__)"
```

This tutorial uses **current stable names**: `Direct`, `BackwardCheckpointed`, and `sesolve(..., save_states=False, progress_meter=False)`.

If a snippet fails to import, print `dq.__version__` and look at `dir(dq.gradient)`.

---

## 1. What your code actually does today (read this even if you never opened the files)

### 1.1 Two transmons, not two qubits

Each device is a transmon with `n_levels=3` (states `|0>`, `|1>`, `|2>`). Two of them → Hilbert space size `3×3 = 9`. A vector with 9 complex numbers is one state of the pair.

The four **computational** states (the actual qubit subspace) are:

```
|control, target>     index in the 9-vector
|0,0>                 0
|0,1>                 1
|1,0>                 3     (because target has 3 levels: 1*3 + 0)
|1,1>                 4
```

That list is `comp_idx = [0, 1, 3, 4]` in both engines.

Naming in the device layer (this is easy to mix up):

- Lab qubits are often **Q1 and Q2** (`qubit_pair=[1, 2]`).
- Inside the engine they are **index 0 and index 1**.
- Index 0 = control = Q1. Index 1 = target = Q2.
- Channels: `q1_drive` (self-drive on control), `q2_drive` (self-drive on target), `cr_drive` (cross-resonance on control, at the target frequency).

### 1.2 A “timeline” is just three arrays of envelopes

`pulses.py` `Timeline` builds a dict:

```python
{
  "q1_drive": array of complex numbers, one per nanosecond,
  "q2_drive": ...,
  "cr_drive": ...,
}
```

Each complex number is `I + i Q` in MHz (Rabi-rate units). Hardware holds that value constant for `dt_sample_ns` (GRAPE uses 1 ns).

Echoed CR from `cr_len_sweep.py` `_build_timeline_from_cr_half`:

1. Play `+u` on `cr_drive`
2. Play an Xπ on the echo channel (`q1_drive`)
3. Play `−u` on `cr_drive`
4. Play another Xπ

GRAPE only optimizes the **flat top of one CR half** `u`. Rise/fall are lab templates. Xπ is a fixed calibrated pulse.

### 1.3 How QuTiP turns a timeline into a gate (`two_q_pulse_sim.py`)

**ALREADY THERE** — this is the loop that actually runs today for GRAPE:

```python
# two_q_pulse_sim.py, run_shot
for k in range(L):                          # each 1 ns sample
    samples = {nm: timeline[nm][k] ...}     # envelope is CONSTANT this ns
    for s in range(self.n_sub):             # e.g. n_sub=2 or 14
        t_mid_ns = (k + (s + 0.5) / n_sub) * dt_sample_ns
        H = self._hamiltonian_at(t_mid_ns, samples)
        psi = (-1j * H * dt_sub_us).expm() * psi
```

Read that twice.

- The **envelope** (the pulse you optimize) is **not** sampled `n_sub` times. It is frozen for the whole 1 ns.
- `n_sub` only re-evaluates the **time-dependent phases** in H: coupling oscillating at ~100 MHz, CR carrier beating, etc.
- Each substep treats H as a constant matrix and does `expm(-i H Δt)`.

If `n_sub=2` and `dt=1 ns`, you take two 0.5 ns matrix exponentials per ns.  
If `n_sub=14`, you take fourteen ~0.071 ns exponentials per ns. Envelope still changes only once per ns.

That is why a bigger `n_sub` can change seed fidelity: you are resolving the 100 MHz oscillation better, not making a finer pulse.

### 1.4 How GRAPE uses this

`cr_grape.py` / `cr_grape_robust.py`:

1. Turn real vector `x` (I,Q,I,Q,…) into complex knobs.
2. `assemble_cr_half_from_flat_knobs` → one CR-half waveform.
3. `_build_timeline_from_cr_half` → full echoed timeline.
4. `_propagator_from_timeline` → 9×9 unitary `U`.
5. Process fidelity of `U` vs ZX90 on the 4×4 computational block.
6. SciPy L-BFGS-B **without a Jacobian**, so SciPy estimates the gradient by finite differences: bump each of the ~122 real knobs, rerun the whole gate.

Robust GRAPE does step 4–5 **twice** today, with the target frequency shifted `+zz/2` and `-zz/2` on two experiment objects. The dynamiqs target is **one** object and `set_target_frame` with a length-2 array (§3.5).

### 1.5 What the dynamiqs engine does today (`two_q_pulse_sim_dynamiqs.py`)

It builds the **same Hamiltonian physics**, then calls `dq.sesolve` / `dq.sepropagator` instead of the `expm` loop.

Important: GRAPE does **not** call `run_propagator` on that class. It calls `CR_len_sweep._propagator_from_timeline`, which does this:

```python
# experiments/cr_len_sweep.py  — ALREADY THERE
psi0 = qt.basis(sim.dims, [c, t])   # QuTiP ket, even if engine is dynamiqs
psi = sim.run_shot(timeline, psi0=psi0)
U[:, col] = psi.full().flatten()
```

So `engine="dynamiqs"` still:

- builds 9 QuTiP kets,
- evolves them one by one,
- copies each result to NumPy.

The dynamiqs `run_propagator` method exists and is unused by GRAPE.

---

## 2. Glossary (the words that made the last tutorial unreadable)

Read this section before any later section. Every later “tape / pytree / traced” refers here.

### JAX vs NumPy, in one paragraph

`numpy` (`np`) runs **right now**, in Python, on CPU. You can `if` on a value, grow arrays, print, whatever.

`jax.numpy` (`jnp`) looks like NumPy but is designed so JAX can:

1. **compile** a function once (`jax.jit`) and run it fast later,
2. **differentiate** it (`jax.grad` / `jax.value_and_grad`).

For (1) and (2) to work, JAX must see a closed world of array operations. The moment you do `np.asarray(jax_array)` or `float(jax_array)` in the middle, JAX can no longer see through that step.

### “The tape”

When you call `jax.grad(f)(x)`, JAX runs `f` and **writes down every operation** (add, matmul, `sesolve`, …) in a list. That list is the **tape** (like a recording). Then it plays the recording **backwards** to get `df/dx`.

If in the middle of `f` you do `np.asarray(U)` or `U.tolist()`, that recording **stops**. JAX has a number, but it has forgotten *how* that number depended on `x`. That is “the tape ends.”

It is not about speed. A NumPy add can be fast. It is about **whether JAX is allowed to see the operation**. Speed is a later bonus of `jit`.

### “Traced”

Inside `jax.jit` / `jax.grad`, a value that depends on the *input* is **traced**. It is a placeholder, not a concrete Python float.

You cannot do this:

```python
if eps_arr[0] > 0:    # BAD inside jit if eps_arr depends on knobs
    ...
```

because `if` needs a real True/False, and JAX only has a placeholder. That error is `ConcretizationTypeError`: “you asked me to make a concrete Python decision from a traced value.”

Things that **do not** depend on knobs (pulse length in samples, number of knobs, channel names) can stay ordinary Python. Those are **static**. JAX compiles a separate program for each static shape.

### “Pytree”

JAX walks nested containers of arrays: dicts, lists, tuples, dataclasses. That nested object is a **pytree**.

A dynamiqs Hamiltonian `H = H_drift + H_coupling + H_q1 + H_q2 + H_cr` is a pytree: a sum of several time-dependent pieces.

If one call has 5 terms and the next call has 4 terms (because you `continue`d a zero channel), JAX sees a **different tree**. It cannot reuse the compiled program. It **retraces** (compiles again). During `grad`, a tree that changes with the data is even worse: the tape’s structure would depend on the data.

That is why “always add every drive channel, even if the envelope is all zeros.” Zero envelope is a valid drive. Skipping it changes the tree.

### “Closes over” / “closure”

A function **closes over** a variable if it uses a variable that was not passed in as an argument.

```python
delta = 100.0

def f(t):
    return jnp.exp(1j * delta * t)   # f "closes over" delta
```

`f` captured `delta` from outside. If `delta` is a Python float sitting on `self`, then `f` always uses that one float. Changing `self.delta_qq_MHz` later only helps if you **rebuild** `f`. You cannot batch two deltas through one captured Python float.

Your dynamiqs engine **does** rebuild `f` every `run_propagator` / `run_shot` (`_build_hamiltonian` → `_coupling_hamiltonian`). So `sim.set_target_frame(...)` then propagate **does** pick up the new value. There is no stale-lambda bug.

If `delta` (or the target frame it is derived from) is a JAX array of shape `(2,)`, `f(t)` returns two values at once. That is batching. The array is stored on `self` by `set_target_frame`; `run_propagator(timeline)` does not take frequencies as arguments.

### `dq.modulated`

Dynamiqs needs `H(t)`, not just a static matrix. Three ways:


| Function                    | Meaning                                    | Example                        |
| --------------------------- | ------------------------------------------ | ------------------------------ |
| `dq.pwc(times, values, op)` | `H(t) = values[k] * op` for `t` in bin `k` | envelope constant on 1 ns bins |
| `dq.modulated(f, op)`       | `H(t) = f(t) * op`                         | `f(t) = exp(i 2π Δ t)`         |
| `dq.timecallable(f)`        | `H(t) = f(t)` as a full matrix             | anything                       |


**Envelope indexing** means: inside `f(t)`, look up which 1 ns bin `t` is in, and read `eps_arr[that_bin]`. Your dynamiqs engine already does that in `_drive_hamiltonian`. The envelope is still piecewise constant. The carrier `exp(-i 2π δ t)` is continuous.

### `dq.pwc` vs that lookup

They are the same physics for the envelope. `pwc` is the official piecewise-constant type. Your lookup-inside-`modulated` is a homemade piecewise-constant, multiplied by a continuous carrier, in one `f(t)`.

You **cannot** write `dq.pwc(...) * dq.modulated(...)` in dynamiqs  — `*` on two time-dependent objects multiplies the **operators**, not the two time functions. That is why the AI wrote one combined `modulated`.

### Forward vs backward (and “forward only”)

- **Forward** = compute the number: given knobs, what is fidelity?
- **Backward** = compute the gradient: given knobs, how does fidelity change if I wiggle each knob?

“Make the engine JAX-pure, forward only” means: first make `knobs → fidelity` work with JAX arrays and `sesolve`, **without** calling `jax.grad` yet. If the forward number is wrong, the gradient is garbage.

### `sesolve` vs `sepropagator`

- `sesolve(H, psi0, tsave)`: start from one (or many) kets, return the evolved kets. Output shape follows `psi0`.
- `sepropagator(H, tsave)`: start from the identity matrix, return the full unitary `U` of size `n×n` (here 9×9).

Both solve the same Schrödinger equation. Propagator is “evolve every basis ket at once, packed as a matrix.”

### Jacobian

The **Jacobian** of a scalar cost `c(x)` with `x` a vector is just the **gradient**: a vector `g` with `g_i = dc/dx_i`.

SciPy L-BFGS-B:

- without `jac=...`: SciPy **approximates** `g` by finite differences (slow, many extra simulations),
- with `jac=...`: you **give** SciPy `g`. Then each iteration is one cost + one gradient.

### Kernel

A **kernel** here means “one compiled GPU/CPU program.”  
“One kernel for two detunings and four kets” means dynamiqs runs those eight evolutions **in one batched `sesolve` call**, not eight Python `for` loops.

### Cartesian batching

If `H` has a batch axis of length 2 (two detunings) and `psi0` has a batch axis of length 4 (four starting states), **cartesian** means “do the grid of all pairs”: 2×4 = 8 evolutions.

Non-cartesian would mean “zip them”: H[i] with psi0[i] only, which is not what we want.

### `ptrace`

**Partial trace**: throw away some subsystems and keep the reduced density matrix of the rest. Example: two qutrits, keep only qutrit 1.

I mentioned `ptrace` as a *future* reason to keep dynamiqs `dims=(3,3)` instead of a flat `(9,)`. **You do not need ptrace for 2-qubit GRAPE.** Ignore it until you actually want a reduced state. I should not have led with it.

---

## 3. Your questions, answered

### 3.1 Can I switch Optax Adam vs SciPy L-BFGS-B? What is faster / more accurate?

Yes. Put a config field `optimizer: "lbfgs" | "adam"` and branch in `run()`. Both should call the **same** JAX `cost` / `value_and_grad`. The switch is only “who updates the knobs.”


|                              | SciPy L-BFGS-B                                                                                                        | Optax Adam                                                                                                 |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| What it is                   | Quasi-Newton. Builds an approximate Hessian from gradients.                                                           | First-order. Uses a running average of gradients (the same family as training neural nets).                |
| Bounds                       | Native (`bounds=`). You already clip amp to ±48 MHz.                                                                  | You add a clip yourself.                                                                                   |
| Typical evals                | Few iterations if the gradient is good. Each iteration is one cost + one grad + a short line search.                  | Many small steps. You pick `learning_rate` and `epochs`.                                                   |
| Accuracy of the **optimum**  | Often **better** for this problem (smooth pulse, ~100 parameters, box bounds). L-BFGS is the usual GRAPE second step. | Can reach similar fidelity with tuning; easier to stall or overshoot if the learning rate is wrong.        |
| Accuracy of the **gradient** | Same, if both use `jax.value_and_grad`. The optimizer does not compute the physics gradient.                          | Same.                                                                                                      |
| Speed per iteration          | One reverse-mode gradient (same as Adam) plus line search (a few extra forwards).                                     | One gradient per step, no line search.                                                                     |
| Speed to a good pulse        | On ~100 bounded pulse knobs, **L-BFGS with JAX gradients is usually fewer simulations to a high F**.                  | Adam can be fine; the dynamiqs Kerr example uses it because it is simple, not because it is more accurate. |
| What you have now            | L-BFGS-B **without** `jac`, so it is slow for a different reason: finite differences.                                 | Not used.                                                                                                  |


**Finite-difference L-BFGS (today)** -vs **JAX-gradient L-BFGS (target)** vs **Adam**:

- Today: ~`2 * n_reals + 1`**full gate simulations per iteration** just to estimate`g`, then more for line search. For 61 complex knobs that is ~123+ simulations per iteration, and robust GRAPE doubles it.
- JAX + L-BFGS: **1** forward simulation + **1** backward pass per gradient, then a few forwards for line search.
- JAX + Adam: **1** forward + **1** backward per step, no line search, but you may need hundreds of steps.

Recommendation: implement **both**, default `**lbfgs`**. Use Adam if L-BFGS misbehaves or you want to match dynamiqs examples.

```python
# ADD THIS — sketch only
if config.optimizer == "lbfgs":
    scipy.optimize.minimize(cost_np, x0, jac=jac_np, method="L-BFGS-B", bounds=bounds, ...)
elif config.optimizer == "adam":
    opt = optax.adam(config.learning_rate)
    ...
```

SciPy is not “slower because it is SciPy.” SciPy is a thin CPU loop around *your* cost. The time is inside `sesolve`. Giving SciPy a Jacobian makes SciPy call that cost far fewer times. That is the speedup.

### 3.2 “Expm will refuse it” — what that means, and both paths

Dynamiqs has a method literally named `dq.method.Expm`. It does the same *kind* of thing as your QuTiP loop: `U = exp(-i H Δt)` on pieces of time where H is **constant**.

The dynamiqs source checks: is this Hamiltonian a constant or a `dq.pwc` (or a sum of those)? If **any** piece is `dq.modulated` (a continuous `f(t)`), it raises:

```text
Method `Expm` requires a constant or piecewise constant Hamiltonian.
```

Your dynamiqs engine **already uses** `dq.modulated` for:

- coupling `exp(±i 2π Δ t)`,
- drives `eps[i(t)] * exp(±i 2π δ t)`.

So if you passed `method=dq.method.Expm()` into `sesolve` **on the current H**, dynamiqs would error. That is “refuse.” It is not that matrix exponentials are wrong physics. It is that **this H is not piecewise-constant as a dynamiqs type**, so that particular solver will not take it.

Your engine already chose `Tsit5` (an ODE solver). Tsit5 is happy with `modulated`. Tsit5 takes many internal time steps, automatically, to follow the 100 MHz oscillation. That is why `**n_sub` is unused** in the dynamiqs file: Tsit5 does not have an `n_sub`. It picks its own steps. The envelope is still piecewise constant because `sample_index(t)` holds `eps` for a whole 1 ns, and `discontinuity_ts` tells the ODE “stop at every 1 ns edge so you do not step across a jump.”

#### Path A — Tsit5 (continuous phases, PWC envelope)

```
envelope:  stair-steps every 1 ns     (your pulse)
phases:    smooth in t                (coupling, carriers)
stepping:  Tsit5 adaptive ODE
n_sub:     ignored
```

This is “use dynamiqs as designed.” Numbers will be **close** to QuTiP-with-large-`n_sub`, not bit-identical to QuTiP-with-`n_sub=2`.

#### Path B — Expm (everything frozen on a sub-grid, like QuTiP)

You rebuild H so dynamiqs sees only `pwc` / constants:

For each substep `s` of each sample `k`, evaluate the **same** `_hamiltonian_at(t_mid)` formula QuTiP uses, store that matrix (or store the scalar prefactors on each operator), and feed `dq.pwc`.

Then `dq.method.Expm` is legal. `n_sub=14` means 14 PWC bins per ns, exactly like QuTiP.

#### How hard is enabling both?

Medium, not huge, if you split “what are the operators” from “how do we step time.”

```
_build_operators()          # shared
_prefactors_at(t, samples)  # shared physics: J e^{iΔt}, eps e^{-iδt}, ...

Path A: wrap those prefactors in dq.modulated / lookup, Tsit5
Path B: evaluate prefactors on the n_sub grid, dq.pwc, Expm
```

Config:

```python
engine="dynamiqs"
dynamiqs_stepper="tsit5"   # Path A
# or
dynamiqs_stepper="expm"    # Path B, uses n_sub
```

Path B is more work in the Hamiltonian builder (you must emit PWC values). Path A is closer to the file you already have. **Do Path A first**, add Path B if the parity test vs QuTiP at `n_sub=14` is not close enough for you.

With `n_sub=14` you care about resolving ~100 MHz. Path A’s Tsit5 with `atol=rtol=1e-9` is *meant* to resolve that. Path B with `n_sub=14` is the QuTiP-identical discretization.

### 3.3 `n_sub` does not sample the envelope — how does dynamiqs work then?

Picture one nanosecond, envelope value `A`, `n_sub=14`.

```
time (ns):  0.00                    1.00
envelope:   AAAAAAAAAAAAAAAAAAAAAAAAAA     ← constant (the pulse)
coupling:   ~sin(2π·100 MHz·t)              ← wiggles ~10 times per 100 ns,
                                              ~0.1 cycle in this 1 ns
```

**QuTiP:** 14 snapshots of the wiggling coupling, 14 `expm`s, envelope `A` every time.

**Dynamiqs Tsit5:** still envelope `A` for the whole ns (`sample_index`). Inside the ns, Tsit5 may take 3 steps or 30 steps. You do not pick 14. You pick tolerances.

**Dynamiqs Expm Path B:** you *do* pick 14, same as QuTiP.

So: wanting `n_sub=14` is a statement about **integrating the oscillation**, not about a 1/14 ns pulse grid. Your OPX pulse is still 1 ns samples.

If you only use Path A, expose `n_sub` on the dynamiqs engine as unused (or delete it) and put the accuracy knobs on `Tsit5(atol=..., rtol=..., max_steps=...)`. If you want the number 14 to mean something, you need Path B.

### 3.4 Kron, `dq.to_jax`, `@`, dims — what the AI wrote and whether it is wrong

**ALREADY THERE** in `two_q_pulse_sim_dynamiqs.py`:

```python
a0_local, a1_local = dq.destroy(n0), dq.destroy(n1)   # 3×3 and 3×3
I0, I1 = jnp.eye(n0), jnp.eye(n1)
a0 = jnp.kron(dq.to_jax(a0_local), I1)                 # 9×9 jax array
a1 = jnp.kron(I0, dq.to_jax(a1_local))
```

What each call is:

- `dq.destroy(3)` = annihilation operator on **one** qutrit, dynamiqs `QArray` 3×3.
- `dq.to_jax(...)` = convert that QArray to a raw JAX array, because `jnp.kron` does not accept QArrays.
- `jnp.kron(a, I)` = “a on the first factor, identity on the second” → 9×9.
- `@` is **matrix multiply**, not kron. `ad @ a` is `a† a`. Kron is `jnp.kron` or `dq.tensor`.

The 9×9 numbers are **correct**. This is not storing “nine entries.” It stores a 9×9 matrix (81 numbers), which is the right size.

What you **lose** is metadata. A dynamiqs QArray from `dq.destroy(3, 3)` knows `dims=(3, 3)`: “this 9×9 is two qutrits.” After `jnp.kron` + `dq.asqarray`, dynamiqs often sees `dims=(9,)`: “this is one 9-level blob.”

For 2-qubit GRAPE (evolve, fidelity on `comp_idx`) **that metadata does not matter**. The matrices are the same.

`dq.destroy(3, 3)` already returns `(a⊗I, I⊗a)` as QArrays with `dims=(3,3)`. That is the one-line version of what the AI did in four lines. Prefer it because it is shorter and keeps `dims`. Not because kron is numerically wrong.

```python
# REPLACE THIS (the kron block)
a0, a1 = dq.destroy(*self.dims)
self.a = [a0, a1]
self.ad = [a.dag() for a in self.a]
```

Rotating frame: **unchanged**. Drift is still only anharmonicity. Frames live in `Qubit.frame_MHz` and in the `exp(i 2π Δ t)` of coupling and drives. Operator construction does not put qubit frequencies on the diagonal; that was already the design in the QuTiP engine comments.

### 3.5 Robust GRAPE: who owns ±s, and `set_target_frame`

**ALREADY THERE** (QuTiP / current robust path):

```python
def _apply_target_freq_shift(exp, shift_mhz):
    sim.qubits[1].frame_MHz = ... + shift_mhz
    sim.delta_qq_MHz = sim.qubits[0].frame_MHz - sim.qubits[1].frame_MHz
```

Robust GRAPE today builds **two** `CR_len_sweep` objects, shifts each by a **scalar**, simulates each. That is correct Python. It is not a batched dynamiqs kernel.

ZZ is a **shift of the target rotating frame**. Drift is still only anharmonicity; there is no extra diagonal term. The shift shows up as:

- `delta_qq = frame0 - frame1` (coupling phase),
- `q2_drive` detuning `= carrier - frame1` (only if that channel is on).

`cr_drive` targets the control, so it does **not** read `frame1`. Echoed CR leaves `q2_drive` idle, so the coupling Δ is the piece that must be batched. Still install the **frame**, and derive Δ, so a later T1/spec/`q2_drive` pulse stays consistent.

#### Shared init stays a lab scalar (both engines)

`engine="dynamiqs"` already picks a **different simulator class**. It does **not** get different constructor arguments for frames.

```
CR_len_sweep / device_base __init__
  → build_qubits()           # lab floats on Qubit
  → TwoQubitPulseSimulator*  # same kwargs either engine
```

Do **not** put a JAX array in `device_base` or in the experiment constructor. QuTiP would break, and every Rabi/CR sweep would inherit a GRAPE concept.

#### One writer on the engine: `set_target_frame`

**ADD THIS** on both engines (QuTiP: scalar only; dynamiqs: scalar or `jnp` array):

```python
def set_target_frame(self, frame1):
    """Install target rotating-frame frequency (float or jax array)."""
    self.qubits[1].frame_MHz = frame1
    self.delta_qq_MHz = self.qubits[0].frame_MHz - self.qubits[1].frame_MHz
```

Engine `__init__` (not the experiment class) should use that same writer for the lab value:

```python
self.qubits = list(qubits)
self.set_target_frame(self.qubits[1].frame_MHz)  # still a float from JSON
```

Callers who want a shift or a batch do it **after init, before the first propagate**, on the simulator they already have:

```python
exp = CR_len_sweep(..., engine="dynamiqs")          # lab chip, either engine
f1 = exp.simulator.qubits[1].frame_MHz
exp.simulator.set_target_frame(f1 + jnp.array([+s, -s]))
# then only sim.run_propagator(timeline)
```

`run_propagator` stays **timeline only**. It reads `self` (frames, `delta_qq`, `J`, operators). The `dq.modulated` lambdas close over whatever `delta` / `frame` are at **that** Hamiltonian build. Set once; every later cost eval only passes the pulse.

#### Who calls `set_target_frame`


| Layer                          | Role                                                                                     |
| ------------------------------ | ---------------------------------------------------------------------------------------- |
| `device_base` / `build_qubits` | Lab chip. One f per qubit. Never JAX.                                                    |
| Engine `__init__`              | `set_target_frame(lab float)` so `delta_qq` is not a second formula.                     |
| `run_propagator`               | `timeline` → U. No frequency argument.                                                   |
| Robust GRAPE                   | Owns \pm s (`config.resolved_shifts()`). One call after building **one** `CR_len_sweep`. |
| Spec / T1 / RB later           | Same method, their numbers. One line per experiment, not a new implementation.           |


Put the robust call **once** in `RobustCRGrapeOptimizer.__init__` (dynamiqs branch) so test scripts do not each poke frames. QuTiP robust can keep two objects + `_apply_target_freq_shift` until you delete it.

You do **not** recode coupling math in every script. You call `set_target_frame`. Ten experiments that need a shift → ten call sites, one method.

#### Batching is the same setter with a length-2 array

```python
# ADD THIS idea — still inside set_target_frame / _coupling_hamiltonian reading self
# after set_target_frame(f1 + jnp.array([+s, -s])):
#   frame1 shape (2,), delta_qq shape (2,)
fwd = dq.modulated(lambda t: jnp.exp(1j * TWOPI * delta * t), op)
# f(t) returns shape (2,), so H has a batch of 2 Hamiltonians
```

Same pulse, two target frames, one `sesolve`. Do not build two `CR_len_sweep`s on the dynamiqs GRAPE path.

Do not call `set_target_frame` inside `cost` every eval. Shifts are fixed for the optimize. Mutating `self` every eval is the old footgun (forget to set back). Init-once is enough; a later `run_propagator(timeline, frame1=...)` override is optional and not needed for GRAPE.

### 3.6 Precision / device: not at the top of every script

Do **not** paste `dq.set_precision("double")` into every test file.

**ADD THIS** once, inside the dynamiqs engine module (import runs once per process):

```python
# top of two_q_pulse_sim_dynamiqs.py, after import dynamiqs
import dynamiqs as dq

def _configure_jax():
    dq.set_precision("double")
    dq.set_progress_meter(False)

_configure_jax()
```

When `device_base` does `engine="dynamiqs"`, it imports this file, and JAX is configured. QuTiP-only scripts never import it.

Optional later: `DQ_DEVICE=gpu` environment variable read in `_configure_jax`. Skip GPU for now.

`jax_enable_x64` in the class `__init__` (already there) is the same idea, but it is easy to create arrays before the constructor. Module-level once is cleaner. Keep it **idempotent** (calling twice is fine).

### 3.7 “Forward only” in Phase 1

Phase 1 = get the **same kind of number you already plot** (process fidelity of a seed pulse) out of dynamiqs, as JAX arrays, **without** `jax.grad`.

You are not optimizing yet. You are asking: “If I pass this timeline in, is F ≈ the QuTiP F?”

### 3.8 Phase 1.2 again (batched target **frame**, derived `delta`)

`_coupling_hamiltonian(self)` currently reads `self.delta_qq_MHz` (one float). Keep reading `self` — do **not** add `delta=` to `run_propagator`.

After `set_target_frame`, `self.delta_qq_MHz` is already a scalar or shape `(n_batch,)`. The modulated lambda just uses it:

```python
def _coupling_hamiltonian(self):
    delta_mhz = self.delta_qq_MHz   # float or jax array from set_target_frame
    j = TWOPI * self.J_MHz
    fwd = dq.modulated(
        lambda t: jnp.exp(1j * TWOPI * delta_mhz * t),
        j * self.coupling_op,
    )
    bwd = dq.modulated(
        lambda t: jnp.exp(-1j * TWOPI * delta_mhz * t),
        j * self.coupling_op_dag,
    )
    return fwd + bwd
```

`_drive_hamiltonian` already does `carrier - self.qubits[dl.target].frame_MHz`. If `frame1` is length 2, `q2_drive` batches automatically. Leave that.

Units: `t` from dynamiqs is the same unit as `tsave`. Your engine uses **microseconds**. `delta_mhz * t_us` matches QuTiP’s `delta_mhz * t_ns * 1e-3`.

If `delta_mhz` is a length-2 array, you get two Hamiltonians stacked. That *is* the two ZZ cases. The public API that created that array is `set_target_frame`, not a new `run_propagator` argument.

### 3.9 Phase 1.3 — `sample_index` is **already in your file**

This is not a new invention. **ALREADY THERE:**

```python
def sample_index(t: float) -> jnp.ndarray:
    return jnp.minimum(jnp.int32(t / dt_us), n_eps - 1)
```

Meaning: `t` is time in µs. `dt_us` is 0.001 if `dt_sample_ns=1`. `t / dt_us` is which 1 ns bin you are in. `int32` truncates toward zero. `minimum(..., n_eps-1)` stops you running off the end of the array at the last instant.

I suggested a clearer version (same idea):

```python
# REPLACE the body of sample_index if you want it more readable
def sample_index(t):
    i = jnp.floor(t / dt_us).astype(jnp.int32)
    return jnp.clip(i, 0, n_eps - 1)
```

`floor` vs `int32` truncation differs for negative `t`. Your `tsave` starts at 0, so both are fine.

The **real** bug in `_build_hamiltonian` is this **ALREADY THERE** block:

```python
eps_arr = jnp.array(timeline[name], dtype=complex)
if jnp.all(eps_arr == 0):
    continue
```

Under `jax.grad`, `eps_arr` depends on knobs → traced → `if` explodes. Also, skipping a channel removes a term from `H`’s pytree.

**REPLACE** by always adding the drive, even if it is zeros. And use `jnp.asarray(..., dtype=jnp.complex128)` so you do not go through NumPy’s `complex` dtype helper in a traced region.

`discontinuity_ts = jnp.linspace(0.0, L * dt_us, L + 1)` is **ALREADY THERE**. Keep it. Those times are the 1 ns edges. Diffrax (the ODE library under Tsit5) will stop and restart at each edge so it does not interpolate across an envelope jump.

### 3.10 Phase 1.4 — will `_propagator_from_timeline` still be QuTiP?

Today: **yes, the loop is QuTiP kets**, even when `sim` is dynamiqs, because `qt.basis` + `run_shot`.

What I want you to write:

```python
# REPLACE the body of CR_len_sweep._propagator_from_timeline
def _propagator_from_timeline(self, timeline):
    sim = self.simulator
    if hasattr(sim, "run_propagator"):
        return sim.run_propagator(timeline)   # dynamiqs path: one sepropagator
    # existing qutip loop stays for TwoQubitPulseSimulator
    ...
```

“Existing QuTiP loop” = the `for c in range(n0): for t in range(n1): qt.basis ...` that is already in the file. Leave it as the **else** branch so `engine="qutip"` does not break.

After this change:

- `engine="qutip"` → still the 9-ket expm loop.
- `engine="dynamiqs"` → `TwoQubitPulseSimulatorDynamiqs.run_propagator` → `dq.sepropagator` → one 9×9 `U`.

That `U` is still a JAX/dynamiqs object internally; `run_propagator` today does `return np.asarray(dq.to_jax(...))` which is fine for **experiments and the parity script**. For **GRAPE autodiff** you must not `np.asarray` on the path that `jax.grad` sees. So later, add a flag or a second method that returns the QArray.

### 3.11 Phase 2 — can I just swap `np` for `jnp` in `pulses.py`? Do I need NumPy?

A global `cls` switch `np` ↔ `jnp` will **not** make `Timeline` JIT-safe.

**ALREADY THERE** — the problem:

```python
def _grow(self, ch, length):
    if len(self._buf[ch]) < length:
        pad = np.zeros(length - len(self._buf[ch]))
        self._buf[ch] = np.concatenate([self._buf[ch], pad])
```

JAX compiled functions need **fixed array shapes**. You cannot grow a buffer as pulses are added. `start = int(round(start_ns / dt))` is also a Python int from a time; that is OK if times are static (they are: 184 ns flat, 16 ns rise, fixed Xπ).

So:

- **Experiments + QuTiP GRAPE:** keep NumPy `Timeline`. It is the right tool.
- **JAX GRAPE:** a second function that **knows the final length in advance** and writes slices. That is `pulses_jax.py`, not a flag on `Timeline`.

“Always build jnp, convert to np before QuTiP”:

- QuTiP `Qobj` wants NumPy (or lists). Yes, you convert at that boundary.
- You do **not** need NumPy on the dynamiqs GRAPE path.
- Saving `.npz` / plotting: `np.asarray(jax_array)` at the **end** is correct. That is after the tape, on purpose.

Static lengths vs existing code:

Existing: `Timeline` starts at length 0 and grows as you `add()`. Final length is discovered at `finalize()`.

JAX version: you already know

```
n_cr = len(cr_plus)
n_x  = len(x_pi)
L    = 2 * n_cr + 2 * n_x
```

because the echoed sequence is fixed. You allocate `L` once. That is the same numbers `Timeline` would have produced; you just do not grow.

### 3.12 Phase 4 cost, line by line — what is `statics`?

`statics` is a bucket of **arrays that do not depend on the knobs** (or that we treat as fixed during one optimization): rise/fall templates, Xπ, target unitary, `comp_idx`.

Detunings / target frames are **not** passed into `grape_cost` every eval. They sit on `self` after `set_target_frame` (§3.5). If you are **not** doing robust GRAPE, that is the lab scalar. If you **are**, it is length 2:

```python
sim.set_target_frame(lab_frame1 + jnp.array([+s, -s]))  # once, before optimize
```

Sketch with comments (this is **new** code, not in the repo):

```python
def grape_cost(x, statics):
    # x: real vector, length 2 * n_knobs. Same layout as _knobs_to_x today.
    knobs = x[0::2] + 1j * x[1::2]

    # same math as assemble_cr_half_from_flat_knobs, but jnp
    cr_plus = assemble_cr_half_jax(knobs, statics)
timeline = echoed_timeline_jax(cr_plus, statics.x_pi, statics.channel_names)
    # same layout as _build_timeline_from_cr_half
    

    # evolve computational kets; H batched if self.delta_qq_MHz has a leading axis
    psi = sim.evolve_comp(timeline)
    # psi shape (n_delta, 4, 9, 1)   n_delta=2 for robust, 1 otherwise

    def F_of_one_delta(psi_one):
        return process_fidelity_jax(psi_one, statics.U_target, statics.comp_idx)

    F = jax.vmap(F_of_one_delta)(psi)   # shape (n_delta,)
    F_comb = combine_robust_jax(F[0], F[1], ...) if n_delta == 2 else F[0]
    return -F_comb
```

`jax.vmap` = “run this on each leading-index slice.” You could also skip `vmap` and write a 2-line loop if `n_delta` is 2 and static; `vmap` is the habit.

### 3.13 The finite-difference check and why `17` is hardcoded

You cannot trust `jax.grad` until you check it against a dumb estimate.

Finite difference for one coordinate `i`:

```
g_i ≈ [ C(x + eps e_i) - C(x - eps e_i) ] / (2 eps)
```

That is two extra full simulations per coordinate. Checking **all** 122 knobs is slow, so you check **three**:

```python
cost_and_grad = jax.jit(jax.value_and_grad(grape_cost))
c, g = cost_and_grad(x0)          # JAX's gradient vector, length 122

eps = 1e-6
for i in [0, 1, 17]:              # three arbitrary knobs: first I, first Q, and some later one
    e = jnp.zeros_like(x0).at[i].set(eps)
    fd = (grape_cost(x0 + e) - grape_cost(x0 - e)) / (2 * eps)
    print(i, float(g[i]), float(fd), float(abs(g[i] - fd)))
```

`17` is not physics. It is “don’t only test index 0.” Pick any interior index. If those three match to ~1e-5 relative, you are good. If index 0 matches and 17 does not, you have a bug in assembly (knob i maps to the wrong samples).

`.at[i].set(eps)` is JAX’s way to write `e[i] = eps` without mutating.

### 3.14 Four kets in 9D; sesolve vs sepropagator; one forward one backward

The **state** is always 9-dimensional. `|00>` is a 9-vector with a 1 at index 0. You never evolve a 4-vector.

Process fidelity (your `fidelity.py`) only looks at how those **four** computational basis states move, and only at the **four** computational amplitudes of each result. The five leaked basis states `|2,0>`, `|0,2>`, … as *inputs* do not enter `P @ U @ P`.

So you evolve **4 kets**, each of length **9**. Leakage is visible: if `|00>` leaks to `|2,0>`, that amplitude sits at some index not in `comp_idx`, and `leakage_from_comp` sees that the 4×4 block is not unitary.

`sepropagator` would evolve **all 9** inputs (the full `U`). Same physics, wasted work. For 2 qutrits it is cheap (9 vs 4). Prefer 4 anyway so the code matches the cost.

**One forward, one backward:**

- Forward: run the compiled `sesolve`, get `F`.
- Backward: play the tape in reverse, get `dF/dx` for **all** knobs in one go.

Reverse-mode AD cost is roughly “another forward,” **not** “another forward per knob.” That is the whole reason to use JAX. Finite difference is one forward **per knob**.

### 3.15 Phase 5 — plugging into SciPy, Jacobian, metrics, `maxfun`

**Plug into SciPy** = keep

```python
scipy.optimize.minimize(..., method="L-BFGS-B")
```

but stop making SciPy guess the gradient.

**ALREADY THERE** (no jacobian):

```python
minimize(self._cost_x, x0, method="L-BFGS-B", bounds=bounds, callback=...,
         options={"maxiter": ..., "maxfun": maxfun, "ftol": 1e-10})
```

**ADD** `jac=`:

```python
minimize(self._cost_x, x0, jac=self._jac_x, method="L-BFGS-B", ...)
```

`_jac_x(x)` returns the gradient as a NumPy vector. Inside, it calls `jax.value_and_grad`. SciPy still runs on CPU Python; each time it needs `c` or `g` it calls you, and you run the jitted JAX function. That is not a slow extra layer worth worrying about.

**Metrics function:** your `_callback` today prints process fidelity, leakage, etc. `jax.value_and_grad` only differentiates a **scalar**. It does not return those extra numbers. So:

- Optimizer sees `cost` and `grad`.
- Every SciPy `callback` (once per L-BFGS iteration, not per finite-diff eval) you run `metrics_fn(x)` **without** `grad`: one extra forward, to fill the JSON/progress bar.

That extra forward is cheap compared to today’s 123 evals.

**Why `maxfun = maxiter * (50 + 2 * n_flat_knobs)` would “stop early” after you add `jac`:**

SciPy stops when **either** `maxiter` **or** `maxfun` (max number of **calls to `_cost_x`**) is hit.

Today each iteration calls `_cost_x` about `2*n_reals+1` times (gradient) plus line search. `maxfun` is sized for that.

With `jac=`, each iteration calls `_cost_x` maybe 1–20 times (line search only). You will **not** hit `maxfun` accidentally if you leave it large. The danger is the **opposite of what I said if you leave it large**: it is fine.

The failure mode I meant: if you **shrink** `maxfun` thinking “we need fewer evals” and set it to something like `maxiter`, line search can use several evals per iter and you stop with `ABNORMAL: maxfun exceeded` after 20 iterations even though `maxiter=80`.

Practical: with `jac=`, set `maxfun` to `maxiter * 30` or just omit it. Do not keep the `2 * n_flat_knobs` term; that term existed **only** to pay for finite differences.

`maxiter=80` still means “at most 80 L-BFGS steps.” That is unchanged.

**Optax later:** not because it is faster. Because L-BFGS + bounds matches what you already converged. Adam is a backup and a switch, as in §3.1.

### 3.16 Phase 6 — frames, CR carrier, cartesian shapes

Lab: CR tone is generated at **Q2’s frequency**. In the code that is `cr_drive` with `target=0` (it drives the control transmon) and `carrier_MHz = -DELTA_QQ` so that in the control’s rotating frame the CR envelope rides at the detuning. That carrier is **not** changed when you model ZZ. That is “CR carrier is fixed (lab).”

ZZ from a spectator is modelled as a **shift of the target’s frequency**. Install it with `set_target_frame(lab_frame1 + shifts)`, not by inventing a second `delta` that disagrees with `frame1`. Coupling `Δ = frame0 - frame1` changes. The CR **envelope** on the control line is the same.

Does that shift change `q2_drive`?  
`q2_drive` detuning = `carrier_q2 - frame_target`. If you moved `frame_target` and left `q2_drive`’s carrier equal to the old frame, a pulse on `q2_drive` would be off-resonant. Batching `frame1` (not only `delta_qq`) keeps that honest.

In **echoed CR**, `q2_drive` is **idle** (all zeros). The echo Xπ is on `q1_drive` (control). The CR drive coefficient does not pick up `frame1`. Don’t copy the qontrol notebook blindly and batch every drive detuning; `set_target_frame` already batches what this Hamiltonian reads from `self`.

Spectroscopy note: many spec scans vary a **drive carrier**, not the target rotating frame. Use `set_target_frame` only when the model is “qubit frequency moved.” A tone sweep is a different knob.

**Shapes** (2 qutrits, robust, 4 computational kets):

- `n = 9` = full Hilbert-space size, **not** “dimension of each qubit.” Each qubit is 3. `n = 3×3`.
- `H` shape `(2, 9, 9)`: 2 detunings, each a 9×9 matrix (time-dependent).
- `psi0` shape `(4, 9, 1)`: 4 starting kets. Each ket is 9×1 (a column). The last `1` is “column vector,” dynamiqs convention, same as QuTiP’s `(9, 1)`.
- cartesian batching: every pair (detuning, ket) → `final_state` shape `(2, 4, 9, 1)`.

One `sesolve` call, one compiled kernel, eight evolutions inside.

---

## 4. Enable / disable dynamiqs (2 qubits only)

Keep `engine` on `TwoQubitSimulatorBase`. Add the same field to GRAPE configs so test scripts can say:

```python
CR_len_sweep(..., engine="dynamiqs", n_sub=14)
# or
optimize_echoed_cr_grape(..., engine="dynamiqs", dynamiqs_stepper="tsit5")
```

Default remains `"qutip"` so old sweeps do not change.

Do not generalize `assert len(qubits)==2` away yet.

---

## 5. Implementation phases (2-qubit only)

Skip GPU and N-qubit. Parity test is the first thing to run.

### Phase 0 — upgrade and configure JAX

1. Upgrade dynamiqs.
2. `_configure_jax()` at import of `two_q_pulse_sim_dynamiqs.py` (§3.6).
3. Confirm `dq.gradient.BackwardCheckpointed` imports.

### Phase 1 — JAX-pure **forward** engine + parity

Work in `engine/two_q_pulse_sim_dynamiqs.py` and `experiments/cr_len_sweep.py`.

Checklist:

1. Replace kron block with `dq.destroy(*self.dims)` (§3.4). Drift / rotating frame unchanged.
2. `set_target_frame` on the engine; `__init__` calls it with the lab float. `_coupling_hamiltonian` still reads `self.delta_qq_MHz` (scalar or array) (§3.5, §3.8).
3. Delete `if jnp.all(eps_arr == 0): continue`.
4. Keep `sample_index` and `discontinuity_ts`.
5. `run_propagator` stays for full `U` (parity, tomography).
6. `_propagator_from_timeline` dispatches to `run_propagator` (§3.10).
7. Write and run the parity script below.
8. Optionally add `evolve_comp` (4 kets) after parity on full `U` agrees.

Integrator for Path A:

```python
self._integrator_method = dq.method.Tsit5(atol=1e-9, rtol=1e-9, max_steps=1_000_000)
self._gradient = dq.gradient.BackwardCheckpointed()
```

`n_sub=14` does not enter Path A. For a fair vs-QuTiP comparison, run QuTiP at `n_sub=14` (your preferred accuracy) against dynamiqs Tsit5. If they disagree more than you can tolerate, that is the argument for Path B.

#### Parity script (you asked for help building this)

**ADD** `optimization/optimization_tests/engine_parity_seed.py`

```python
"""Compare QuTiP vs dynamiqs on one echoed-CR seed timeline."""
import numpy as np

from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep
from HM.simulator.two_qubit_simulator.optimization.cr_grape import DEFAULT_CR_PULSE_PARAMS
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    process_fidelity,
    zx_target_unitary,
    embed_in_full,
    leakage_from_comp,
)

def build_exp(engine, n_sub=14):
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

def main():
    flat_len_ns = 122.0
    exp_q = build_exp("qutip", n_sub=14)
    exp_d = build_exp("dynamiqs", n_sub=14)  # n_sub unused on Path A

    x_pi = exp_q.build_x_pi()
    timeline = exp_q._build_timeline(flat_len_ns, x_pi=x_pi)

    U_q = exp_q._propagator_from_timeline(timeline)
    U_d = exp_d._propagator_from_timeline(timeline)

    dim = U_q.shape[0]
    Ut = embed_in_full(zx_target_unitary("zx_m90"), dim=dim)  # or zx_90; print both
    print("max |Uq - Ud|", np.max(np.abs(U_q - U_d)))
    print("F_q", process_fidelity(U_q, Ut), "leak", leakage_from_comp(U_q))
    print("F_d", process_fidelity(U_d, Ut), "leak", leakage_from_comp(U_d))

if __name__ == "__main__":
    main()
```

After you dispatch `_propagator_from_timeline`, this is a fair test.

What to expect:

- `max |Uq-Ud|` of `1e-3`–`1e-6` and `|F_q - F_d|` similarly small: Path A is good enough; proceed.
- `|F_q - F_d|` like `0.01`: bug (units, missing 2π, `t` in ns vs µs, wrong echo channel).
- Tiny `max |Uq-Ud|` only after Path B: then you know the gap was discretization, not a bug.

Print `exp_q.simulator.delta_qq_MHz` and `exp_d.simulator.delta_qq_MHz` if F disagrees; they must match.

### Phase 2 — JAX pulse assembly

**ADD** `engine/pulses_jax.py`. Do not switch `Timeline` to jnp.

Port, with tests against NumPy:

- `assemble_cr_half_from_flat_knobs`
- echoed layout of `_build_timeline_from_cr_half`

Load `rise_arr` / `fall_arr` once to `jnp` constants. `n_flat`, `n_knobs` static.

Test: `np.testing.assert_allclose(jax_wf, numpy_wf, atol=0, rtol=0)` on a few knob vectors (exact match; same arithmetic).

### Phase 3 — JAX fidelity

**ADD** `optimization/fidelity_jax.py`. Same formulas as `fidelity.py`, `jnp`, no `float()`.

Test against `process_fidelity(U_full, ...)` using `U` from the parity script.

Remember the 4×4 layout: `U_ij = ⟨comp_i|ψ_j⟩` with `ψ_j` the evolution of computational ket `j`. Get the transpose wrong and you optimize ZX†.

### Phase 4 — jitted cost + gradient check

Wire `grape_cost` (§3.12). `jax.jit(jax.value_and_grad(grape_cost))`. Run the three-index FD test (§3.13).

Do this on **one** detuning first (lab `set_target_frame`, scalar). Then robust (length-2 array).

### Phase 5 — SciPy `jac=` and an Adam switch

- `jac=self._jac_x` for L-BFGS-B.
- Relax `maxfun` (§3.15).
- `callback` still calls a non-differentiated `metrics_fn`.
- `optimizer="adam"` branch with Optax, same `grape_cost`.

Keep `engine="qutip"` GRAPE working until you are willing to break it.

### Phase 6 — robust as batched target frame (**DONE**)

See `PHASE_6_ROBUST_BATCHED_FRAME.md`. Stop building two `CR_len_sweep`s on the JAX path. One dynamiqs experiment, then **once**:

```python
sim = exp.simulator
sim.set_target_frame(sim.qubits[1].frame_MHz + jnp.asarray(self.shifts))
```

Use `evolve_comp` + `grape_cost_robust` (combine F_a, F_b from the batch axis; §3.5, §3.16). Default optimizer: L-BFGS + `jac=True`. Adam available via `optimizer="adam"` (same `_cost_vg`). Smoke: `optimization_tests/test_grape_robust_jax.py` → `PHASE 6 OK`.

QuTiP robust path keeps two objects + `_apply_target_freq_shift` until you delete it on purpose.

---

## 6. What the AI-written dynamiqs file is doing, line by line (so you have seen it)


| Piece                                               | Intent                            | Verdict                                                             |
| --------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------- |
| `jax_enable_x64` in `__init_`_                      | Double precision like QuTiP       | Move to module import                                               |
| `n_sub` stored, unused                              | API copy of QuTiP                 | Honest for Path A; used only in Path B                              |
| `Tsit5(atol=1e-9)`                                  | Tight ODE                         | Keep for Path A                                                     |
| kron + `to_jax`                                     | 9×9 annihilation ops              | Numerically OK; replace with `destroy(n0,n1)`                       |
| `_coupling_hamiltonian` `modulated`                 | J e^{±i 2π Δ t}                   | Correct physics; `delta` comes from `self` after `set_target_frame` |
| `_drive_hamiltonian` `sample_index` + `modulated`   | PWC envelope × continuous carrier | Correct; cannot use `pwc * modulated`                               |
| `if all(eps==0): continue`                          | Skip idle channels                | Wrong for JIT/grad; always add                                      |
| `run_shot` → `sesolve`                              | Evolve one (or batched) ket       | Fine for experiments                                                |
| `run_propagator` → `sepropagator` then `np.asarray` | Full U                            | Fine for parity; not for `jax.grad`                                 |
| `_DynamiqsState.full()` NumPy                       | QuTiP-shaped API                  | Fine outside GRAPE                                                  |
| GRAPE → `_propagator_from_timeline`                 | 9 QuTiP kets                      | This is why dynamiqs is not really used                             |


---

## 7. Order of work (checklist)

1. Upgrade dynamiqs; import `BackwardCheckpointed`.
2. Parity script + `_propagator_from_timeline` dispatch. **Stop here until F is close.**
3. Clean engine: `destroy(*dims)`, no zero-skip, `set_target_frame`.
4. `pulses_jax.py` equality tests.
5. `fidelity_jax.py` equality tests.
6. `grape_cost` + 3-knob FD vs AD.
7. L-BFGS `jac=` ; optional Adam switch.
8. Robust: one sim, `set_target_frame` with length-2 array; `grape_cost_robust`; L-BFGS default + Adam opt-in. (**DONE** — see `PHASE_6_ROBUST_BATCHED_FRAME.md`)

When you start coding, start at item 2. We can write that dispatch + parity script together next.