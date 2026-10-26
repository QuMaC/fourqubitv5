# Phase 0 — Upgrade dynamiqs and configure JAX once

This is the **only** file you need open to implement Phase 0. The big tutorial (`DYNAMIQS_GRAPE_MIGRATION.md`) is background. Here you will change **one Python file** and run **a few terminal checks**. You will not touch GRAPE, pulses, or `set_target_frame` yet.

Parent guide: `DYNAMIQS_GRAPE_MIGRATION.md` §0, §3.6, Phase 0 checklist.

---

## 0. What Phase 0 is, and what it is not

**Is:** make sure the process that will later run `sesolve` / `jax.grad` is using

1. a dynamiqs version whose **gradient class names** match the docs we write against,
2. **double precision** (`float64` / `complex128`), same idea as QuTiP’s default,
3. that configuration happening **once, at import**, before any JAX arrays exist.

**Is not:**

- not making GRAPE faster,
- not wiring `jax.grad`,
- not changing the Hamiltonian,
- not adding `set_target_frame`,
- not writing `pulses_jax.py`,
- not a parity test vs QuTiP (that is Phase 1).

If you skip Phase 0 and later call `dq.gradient.BackwardCheckpointed`, two things can go wrong:

- **NameError / AttributeError** if you are still on an old dynamiqs that called it `CheckpointAutograd`.
- **Silent float32** if JAX arrays were created before `jax_enable_x64` was turned on. Then QuTiP (float64) and dynamiqs (float32) disagree on \(F\) and you will debug “units” for a day.

That is why this is step zero.

---

## 1. Where you are right now (read this before typing)

Checked in `envs/qumac-env` when this note was written:

| Thing | Value |
| --- | --- |
| Package | `dynamiqs 0.3.4` (this **is** current PyPI stable) |
| JAX | `0.6.2` |
| `dq.gradient` names | `Direct`, `BackwardCheckpointed`, `Forward` (already the **new** names) |
| `dq.set_precision` | exists |
| `dq.set_progress_meter` | exists |
| `dq.set_device` | exists (`'cpu'`, `'gpu'`, `'tpu'`) — **do not use GPU in Phase 0** |

The parent tutorial’s table that says “you have 0.3.3 / `CheckpointAutograd`” is **stale**. You already have the new names. Phase 0 is still required because of **when** precision is set, not because you must rename gradient classes.

**ALREADY THERE** in `engine/two_q_pulse_sim_dynamiqs.py`, inside `TwoQubitPulseSimulatorDynamiqs.__init__`:

```python
if enable_x64:
    jax.config.update("jax_enable_x64", True)
```

That is the right *idea* (double precision) in the wrong *place* (the constructor).

### Why the constructor is the wrong place

JAX’s rule, from their docs and from `dq.set_precision`’s own docstring:

> `dq.set_precision("double")` is equivalent to `jax.config.update("jax_enable_x64", True)`.

And JAX’s rule on that flag:

> It must be set **before** JAX allocates any arrays. Arrays created earlier stay `float32`. Turning the flag on later does not promote them.

Timeline of a typical script today:

```text
1. import jax / some other library     ← might already make float32 arrays
2. CR_len_sweep(..., engine="dynamiqs")
3. device_base lazy-imports two_q_pulse_sim_dynamiqs.py
4. TwoQubitPulseSimulatorDynamiqs.__init__
5.     jax.config.update("jax_enable_x64", True)   ← possibly TOO LATE
6.     _build_operators()  ← first arrays this class makes; these are x64 IF step 5 ran in time
```

If step 1 already created JAX arrays, step 5 is too late for those, and you can get a mix of dtypes. Even if you are lucky today, the next notebook that does `jnp.zeros(3)` before constructing the sim will bite you.

**Module import** of `two_q_pulse_sim_dynamiqs.py` is the earliest moment **this package** can set the flag, and it runs once per process. `device_base._resolve_engine` only imports this file when `engine="dynamiqs"`, so QuTiP-only scripts never pay for it. That is the design.

`dq.set_precision("double")` is the dynamiqs spelling of the same flag. Prefer it so you are not mixing two ways to say x64.

---

## 2. Files you will touch

| Path | Action |
| --- | --- |
| `HM/simulator/two_qubit_simulator/engine/two_q_pulse_sim_dynamiqs.py` | **ADD** `_configure_jax()` at import; **REPLACE** the `jax.config.update` in `__init__` |
| nothing else | no GRAPE, no `device_base`, no tests folder yet |

Optional, not required: a tiny scratch script to verify imports. You can run the checks from the terminal instead.

---

## 3. Terminal work first (upgrade / confirm)

Use the same env you actually run simulations in (`qumac-env`). Do not upgrade a random system Python.

```bash
# from anywhere; use the env's python
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python -c \
  "import dynamiqs as dq, jax; print(dq.__version__, jax.__version__)"
```

You want dynamiqs **≥ 0.3.4** and the new gradient names. If you are already there, **do not** need to pip install. If you are behind:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/pip install -U dynamiqs
```

Then confirm the names Phase 1–5 will use:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import dynamiqs as dq
print("dynamiqs", dq.__version__)
print("gradients", [n for n in dir(dq.gradient) if n[0].isupper()])
assert hasattr(dq.gradient, "BackwardCheckpointed")
assert hasattr(dq.gradient, "Direct")
assert hasattr(dq.gradient, "Forward")
assert hasattr(dq, "set_precision")
g = dq.gradient.BackwardCheckpointed()
print("BackwardCheckpointed ok", g)
print("Tsit5", dq.method.Tsit5)
PY
```

If `assert hasattr(..., "BackwardCheckpointed")` fails, you are on the old API (`CheckpointAutograd`). Upgrade until this assert passes. **Do not** write GRAPE autodiff against the old names.

### What those three gradient classes mean (you do not use them in Phase 0)

You are only **importing** them so later code will compile. You do **not** pass `gradient=` into `sesolve` in Phase 0.

| Class | Role later |
| --- | --- |
| `Direct` | reverse-mode through the solver, no checkpointing; more memory |
| `BackwardCheckpointed` | reverse-mode with checkpoints; **this is what GRAPE will use** |
| `Forward` | forward-mode; good for few parameters, bad for 122 knobs |

Phase 0 success = `BackwardCheckpointed()` constructs without error. Wiring it into `sesolve(..., gradient=...)` is Phase 1 / 4.

### `sesolve` signature on 0.3.4 (so you are not misled by the parent tutorial)

On **your** install:

```text
dq.sesolve(H, psi0, tsave, *, exp_ops=None, method=Tsit5(), gradient=None, options=Options())
```

`save_states` is still a field of `dq.Options`, **not** a bare keyword of `sesolve`. The parent tutorial’s “current stable docs use `sesolve(..., save_states=False)` as a keyword” may describe a newer/dev API. **Follow what `inspect.signature(dq.sesolve)` prints in your env**, not a blog table.

Phase 0 does not change `sesolve` calls. Leave `options=self._sesolve_options` as it is.

---

## 4. Exact code to write in `two_q_pulse_sim_dynamiqs.py`

### 4.1 ADD — configure JAX at import

Put this **immediately after** the existing imports (`dynamiqs`, `jax`, `jnp`, `numpy`, `DT_SAMPLE_NS`, `TWOPI`), **before** `class _DynamiqsState`.

**ADD THIS:**

```python
def _configure_jax() -> None:
    """Set JAX/dynamiqs defaults once per process.

    Must run at import, before this module (or the caller) allocates JAX
    arrays. ``double`` is float64/complex128, matching QuTiP's default
    and the ``jax_enable_x64`` flag this class used to set in ``__init__``.

    Idempotent: dynamiqs/JAX do not mind this being called again.
    """
    dq.set_precision("double")
    dq.set_progress_meter(False)


_configure_jax()
```

**Why `set_progress_meter(False)` here:** Tsit5 can print a progress bar per `sesolve`. GRAPE will call `sesolve` hundreds of times. A bar per eval is unusable. You already pass `progress_meter=False` into `dq.Options` in `__init__`; the global default makes notebooks that call `dq.sesolve` directly equally quiet. Harmless if both are set.

**Why not `set_device("gpu")` here:** Phase 0 is CPU. GPU is a later env flag. Putting GPU in import would surprise a machine without CUDA.

**Why a function plus an immediate call:** so a test or notebook can do `from ...two_q_pulse_sim_dynamiqs import _configure_jax` and call it *before* creating arrays, if they imported `jax` first. The call at the bottom still runs on a normal `engine="dynamiqs"` import.

### 4.2 REPLACE — stop setting x64 in `__init__`

**ALREADY THERE:**

```python
        assert len(qubits) == 2, "this sim is hard-wired to 2 qubits"
        if enable_x64:
            jax.config.update("jax_enable_x64", True)
```

**REPLACE THIS** with:

```python
        assert len(qubits) == 2, "this sim is hard-wired to 2 qubits"
        # Precision is set at module import by _configure_jax() (dq.set_precision
        # "double"). Do not toggle jax_enable_x64 here: it is too late if any
        # JAX arrays already exist, and it fights the process-wide default.
        if not enable_x64:
            raise ValueError(
                "enable_x64=False is not supported; dynamiqs engine is always "
                "double precision (see _configure_jax). Omit this kwarg."
            )
```

**Why raise instead of silently ignoring `False`:** the kwarg still exists so old call sites that pass `enable_x64=True` (the default) keep working. If someone passes `False` thinking they will get a fast float32 GRAPE, they should get an error, not a constructor that claims to disable x64 while `_configure_jax` already turned it on.

You can leave `enable_x64: bool = True` in the signature. Default `True` plus “error if False” means every current caller is unchanged.

### 4.3 Do **not** add in Phase 0

Leave these for later phases. If you add them now you will mix “does import work?” with “does the Hamiltonian match QuTiP?”.

- `self._gradient = dq.gradient.BackwardCheckpointed()` — Phase 1 wiring, optional even then until `jax.grad`
- `dq.destroy(*self.dims)` instead of kron — Phase 1
- `set_target_frame` — Phase 1
- deleting `if jnp.all(eps_arr == 0)` — Phase 1
- `_propagator_from_timeline` dispatch — Phase 1
- `pulses_jax.py` — Phase 2

### 4.4 Optional docstring tweak (same file, top)

The module docstring still says:

```text
Enable ``jax_enable_x64`` via constructor kwarg for parity with double-precision QuTiP runs.
```

**REPLACE** that sentence with:

```text
Double precision is set at import (``dq.set_precision("double")``), not per instance.
```

Not required for the code to work. Stops you from teaching yourself the old story next month.

---

## 5. What the file should look like around the edit (orientation)

After the change, the top of `two_q_pulse_sim_dynamiqs.py` is conceptually:

```text
imports
    dynamiqs as dq
    jax, jax.numpy, numpy
    DT_SAMPLE_NS, TWOPI

_configure_jax()          # NEW: precision + quiet progress, once
    dq.set_precision("double")
    dq.set_progress_meter(False)

class _DynamiqsState:     # UNCHANGED
class TwoQubitPulseSimulatorDynamiqs:
    def __init__(...):
        assert two qubits
        reject enable_x64=False
        store qubits, J, drive_lines, ...
        delta_qq_MHz = frame0 - frame1     # still a scalar; Phase 1 adds set_target_frame
        Tsit5(...)
        _build_operators()                 # UNCHANGED in Phase 0
```

`_build_operators`, `_coupling_hamiltonian`, `run_shot`, `run_propagator` stay as they are. Phase 0 must not change physics.

---

## 6. How to verify Phase 0 (do this before calling Phase 0 done)

Run from a cwd where `HM` imports (same as you run CR experiments). Example:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import jax.numpy as jnp
from HM.simulator.two_qubit_simulator.engine.two_q_pulse_sim_dynamiqs import (
    _configure_jax,
    TwoQubitPulseSimulatorDynamiqs,
)
import dynamiqs as dq

# 1) names we will need later
assert hasattr(dq.gradient, "BackwardCheckpointed")
dq.gradient.BackwardCheckpointed()

# 2) precision: a new array should be float64
x = jnp.array(1.0)
print("array dtype", x.dtype)          # want float64
assert x.dtype == jnp.float64, x.dtype

# 3) constructing the class still works (needs a tiny fake device)
from HM.simulator.two_qubit_simulator.base_classes.device_base import Qubit, DriveLine
import numpy as np
qubits = [
    Qubit(anharm_MHz=-330.0, frame_MHz=0.0, n_levels=3),
    Qubit(anharm_MHz=-330.0, frame_MHz=-100.0, n_levels=3),
]
lines = [
    DriveLine("q1_drive", 0, 0.0),
    DriveLine("q2_drive", 1, -100.0),
    DriveLine("cr_drive", 0, -100.0),
]
I2 = np.eye(2)
sim = TwoQubitPulseSimulatorDynamiqs(
    qubits, J_MHz=5.0, drive_lines=lines,
    confusion_matrices=(I2, I2),
)
print("sim ok", sim.dim, sim.delta_qq_MHz)
print("PHASE 0 OK")
PY
```

**Pass:**

- `array dtype float64`
- `BackwardCheckpointed()` does not raise
- simulator constructs, `sim.dim == 9`

**Fail — dtype is float32:** `_configure_jax` did not run before `jnp.array`, or JAX was already initialized in single precision. Make sure the import of `two_q_pulse_sim_dynamiqs` happens **before** you create arrays (in the snippet above, the import is first; that is intentional).

**Fail — `enable_x64=False` still silently works:** you did not add the `raise`.

QuTiP-only sanity (optional): run any existing `engine="qutip"` script. It must **not** import the dynamiqs file, so Phase 0 cannot break it.

---

## 7. Why this is enough for Phase 0

Later phases assume:

- `import dynamiqs as dq` gives `dq.gradient.BackwardCheckpointed`
- every `jnp` array in the dynamiqs engine is `complex128` / `float64` unless you explicitly pick otherwise
- you do not sprinkle `jax.config.update` in test scripts

Phase 0 is exactly those assumptions, encoded in one import. When the check script prints `PHASE 0 OK`, stop. Open `PHASE_1_FORWARD_ENGINE_AND_PARITY.md` next (not written until you ask). Do not start `pulses_jax` or GRAPE autodiff with a float32 engine.
