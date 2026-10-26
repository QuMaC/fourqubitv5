# Phase 2 — JAX pulse assembly (`pulses_jax.py`)

Instructions only. You type the code. Phase 1 is done (QuTiP vs dynamiqs \(F\) agrees on a **NumPy** timeline). This phase does **not** call `sesolve` or `jax.grad`. It only makes the map

```text
complex flat knobs  →  CR-half waveform  →  echoed timeline dict
```

stay on JAX arrays so a later backward pass can see it.

Parent tutorial: `DYNAMIQS_GRAPE_MIGRATION.md` §3.11, Phase 2 checklist.  
Sibling sheets: `PHASE_0_UPGRADE_AND_JAX_CONFIG.md`, `PHASE_1_FORWARD_ENGINE_AND_PARITY.md`, `OPX_AMPLITUDE_SCALES_AND_CR_CALIBRATION.md` (hardware volts vs sim MHz).

---

## 0. What I would have implemented, in order

| Step | File | What |
| --- | --- | --- |
| 1 | **new** `engine/pulses_jax.py` | load rise/fall templates once as `jnp` constants |
| 2 | same | `assemble_cr_half_jax` — `jnp.repeat`; `n_knobs` must divide `n_flat` |
| 3 | same | `echoed_timeline_jax(cr_plus, x_pi, ...)` — same layout as `_build_timeline_from_cr_half` |
| 4 | **new** `optimization/optimization_tests/test_pulses_jax.py` | `assert_allclose` vs NumPy on several knob vectors |

**Not in Phase 2:**

- do **not** edit `engine/pulses.py` `Timeline` (keep it for experiments / QuTiP / parity)
- do **not** write `fidelity_jax.py` (Phase 3)
- do **not** write `grape_cost` or `jax.grad` (Phase 4)
- do **not** change `cr_grape.py` to call the JAX assembler yet
- do **not** put waits / padding / `L_max` in unless you already need them (you do not)
- do **not** make Xπ a JAX knob. Xπ stays a constant waveform

When the test file prints exact match, Phase 2 is done.

---

## 1. Why this phase exists (x-ray)

### 1.1 What GRAPE already does (NumPy)

Every SciPy eval today:

```text
x  (real, length 2 * n_knobs)
  →  _x_to_knobs  →  flat_knobs  (complex, length n_knobs)
  →  assemble_cr_half_from_flat_knobs  →  cr_plus  (complex, length n_rise+n_flat+n_fall)
  →  CR_len_sweep._build_timeline_from_cr_half  →  dict of 3 arrays, length L
  →  _propagator_from_timeline  →  U
  →  process_fidelity  →  cost
```

Phase 1 only replaced the **last physics step** (evolve) when `engine="dynamiqs"`. The pulse is still built in NumPy. That is fine for **forward** parity. It is **not** fine for `jax.grad` w.r.t. `x`.

### 1.2 What “the tape” needs

Reverse-mode AD writes down every JAX op from `x` to the scalar \(F\). If you do this:

```python
knobs = jnp.array(...)           # JAX
wf = assemble_cr_half_from_flat_knobs(np.asarray(knobs), ...)  # NumPy
```

then `np.asarray` (or any NumPy `mean` / `concatenate` on a converted array) **cuts the tape**. JAX no longer knows how `wf[17]` depended on `knobs[3]`. The gradient of \(F\) w.r.t. the knobs is then missing the rise/fall scaling and the echo copies, or the call fails inside `jit`.

So Phase 2 is: **same numbers as NumPy, all `jnp`.**

### 1.3 Why you cannot “just use `jnp` inside `Timeline`”

**ALREADY THERE** in `engine/pulses.py`:

```python
def _grow(self, ch, length):
    if len(self._buf[ch]) < length:
        pad = np.zeros(length - len(self._buf[ch]))
        self._buf[ch] = np.concatenate([self._buf[ch], pad])
```

`jit` compiles **one shape**. Growing a buffer as you `add()` is a different program after each add. Also:

- `self._buf[channel][start:end] += wf` mutates a Python dict of arrays
- `if len(buf) < length` is a Python `if` on a changing length

A flag `use_jnp=True` on the same class does not fix the **grow-and-mutate API**. That is why a **second file**, not a switch on `Timeline`.

Experiments keep `Timeline`. JAX GRAPE gets functions that already know \(L\).

### 1.4 What is static vs what is a knob

For **one** GRAPE run these Python integers never change:

| Quantity | Typical | Role |
| --- | --- | --- |
| `dt_ns` | 1 | sample grid (`CR_len_sweep` sets `dt_sample_ns=1`) |
| `t_rise_ns` | 16 | lab rise/fall length |
| `n_rise`, `n_fall` | `len(rise_arr(16))` etc. | template lengths |
| `flat_len_ns` | 184 | flat duration |
| `n_flat` | `round(flat_len_ns / dt_ns)` | e.g. 184 samples |
| `n_knobs` | `n_flat_knobs` (e.g. 46) | **must divide `n_flat`** (`n_flat % n_knobs == 0`) |
| `n_link` | 8 | samples used to scale rise/fall |
| `n_x` | `len(x_pi)` | calibrated echo pulse |
| channel names | `q1_drive`, `q2_drive`, `cr_drive` | always all three |
| `echo_channel` | `q1_drive` | control Xπ for echoed CR |

**Traced (depends on `x`):** the complex `flat_knobs` (or the real `x` that unpacks to them), therefore `cr_plus`, therefore the `cr_drive` samples (and the rise/fall **scale**, because that scale is `mean(flat[:8])`).

Xπ samples do **not** depend on knobs. They are constants. Rise/fall **shapes** are constants; only their **complex scale** depends on knobs.

---

## 2. X-ray of the existing NumPy assembler

File: `engine/pulses.py`, function `assemble_cr_half_from_flat_knobs`.

Read this until you can recode it on paper. The JAX file is this function with `jnp`.

### 2.1 Inputs

```python
flat_knobs      # complex, length n_knobs  (what SciPy actually optimizes)
flat_len_ns     # float, e.g. 184
t_rise_ns       # 16
dt_ns           # 1 for GRAPE
n_link_samples  # 8
```

### 2.2 Lab templates (not knobs)

```python
from Helper_Functions.helper_functionsv2 import rise_arr, fall_arr
rise = np.asarray(rise_arr(t_rise_ns), dtype=float)  # real, length n_rise
fall = np.asarray(fall_arr(t_rise_ns), dtype=float)
```

`rise_arr` / `fall_arr` build a Gaussian of length `2 * rise_ns`, scale by `0.4` (OPX `AC_AMP_FACTOR`), then split in half. They are the **same** edges hardware uses. You do **not** reimplement the Gaussian in JAX. You call them **once in Python**, stash `jnp.asarray(rise)`.

If `dt_ns != 1`, NumPy does `rise[::step]`. For JAX GRAPE **lock `dt_ns == 1.0`** and `raise` otherwise. All current GRAPE configs use 1 ns. Supporting 4 ns in JAX is extra and unused.

### 2.3 Stretch knobs onto `n_flat` samples

**Rule:** `n_knobs` must divide `n_flat`. Then each knob is held for the same number of samples:

```text
assert n_flat % n_knobs == 0
k = n_flat // n_knobs
flat = jnp.repeat(knobs, k)
```

That is the whole expand. Examples you already use:

| `n_knobs` | `n_flat` | `k` |
| --- | --- | --- |
| 46 | 184 | 4 |
| 61 | 122 | 2 |
| 184 | 184 | 1 (one knob per ns) |
| 1 | 184 | 184 (constant flat = seed) |

If it does not divide (`3` knobs, `10` samples), `raise ValueError`. Do not invent an uneven split. NumPy `assemble_cr_half_from_flat_knobs` can stay general; JAX is stricter.

`jnp.repeat(knobs, k)` is legal in `jit` because `k` is a Python int. Shape of `flat` is always `(n_flat,)`.

### 2.4 Rise/fall scaled to the flat edges

**This block is the NumPy original** in `assemble_cr_half_from_flat_knobs`. You are reading it so you know the math. Phase 2 still uses **`jnp.mean` / `jnp.concatenate`** (section 6). Same formula, different namespace.

```python
n_link = max(1, min(int(n_link_samples), n_flat))
u_rise_end = np.mean(flat[:n_link])      # complex
u_fall_start = np.mean(flat[-n_link:])

rise_part = (rise / rise[-1]) * u_rise_end
fall_part = (fall / fall[0]) * u_fall_start

wf = np.concatenate([rise_part, flat, fall_part])
```

**Logic:**

- Templates are real envelopes in \([0, 0.4]\). `rise[-1]` is the last rise sample (should be near the Gaussian peak / flat join, **not** zero).
- Divide by that number so the template **ends at 1**, then multiply by `u_rise_end` so it **ends at the actual first-flat complex amplitude**.
- Fall is independent: join to the **last** `n_link` samples, not to the rise.
- If the first 8 knobs are not equal, `u_rise_end` is their **mean**. Continuity is at that mean, not at knob 0 alone.

**Why this must stay on the tape:** wiggling knob 0 changes `u_rise_end`, which scales **every** rise sample. If you bake rise in NumPy from the seed and then only JAX-update the flat, the gaussian will not track. That is the “seed plus NumPy pulse then assign `x`” idea that does not autodiff.

NumPy also has:

```python
if not np.allclose(rise_part[-1], u_rise_end):
    raise RuntimeError(...)
```

Those asserts use `float` / NumPy. **Do not put them inside the JAX function.** They will break tracers. Put them in the **test** against NumPy instead (if NumPy matches, continuity holds).

### 2.5 Return value

```python
slices = {
    "rise": (0, n_rise),
    "flat": (n_rise, n_rise + n_flat),
    "fall": (n_rise + n_flat, n_rise + n_flat + n_fall),
}
return wf, slices
```

`slices` is for plots. `sesolve` never reads it. JAX concatenate already **places** the knobs in the middle. You do not pass an index list into the engine.

---

## 3. X-ray of the existing echoed timeline

File: `experiments/cr_len_sweep.py`, `_build_timeline_from_cr_half`.

```python
cr_minus = -cr_plus
tl = Timeline(self.channels, dt_ns=self.dt_sample_ns)
t = tl.add("cr_drive", start_ns=0.0, waveform=cr_plus)
t = tl.add(self.echo_channel, start_ns=t, waveform=x_pi)
t = tl.add("cr_drive", start_ns=t, waveform=cr_minus)
tl.add(self.echo_channel, start_ns=t, waveform=x_pi)
return tl.finalize()
```

`self.channels` is `["q1_drive", "q2_drive", "cr_drive"]`. `finalize()` zero-pads **every** channel to the same \(L\). Echoed GRAPE: `echo_channel = "q1_drive"` (control Xπ). `q2_drive` is all zeros.

Picture, one sample = one array slot (`dt_ns=1`):

```text
time  →
cr_drive:   [  cr_plus  |  0000  |  -cr_plus  |  0000 ]
q1_drive:   [  000000   |  x_pi  |   000000   |  x_pi ]
q2_drive:   [  000000000000000000000000000000000000 ]
            <— n_cr —><— n_x —><—  n_cr   —><— n_x —>
```

Lengths:

```text
n_cr = len(cr_plus) = n_rise + n_flat + n_fall
n_x  = len(x_pi)
L    = 2 * n_cr + 2 * n_x
```

No growing. Allocate `L` and write blocks. That **is** the JAX version of `Timeline` for this one recipe.

**Sign of the second CR:** `cr_minus = -cr_plus` is elementwise. Same envelope, opposite complex amplitude. Echo identity: ZX adds, many IX-like terms cancel.

**Idle zeros:** Phase 1 dynamiqs engine requires all three keys. `q2_drive = zeros(L)` is mandatory, not optional.

---

## 4. Files you will touch

```text
engine/pulses_jax.py                                          # NEW
optimization/optimization_tests/test_pulses_jax.py            # NEW
```

Do not modify `pulses.py` except if you discover a NumPy bug (you should not). Do not import `pulses_jax` from `device_base`.

---

## 5. Step 1 — `pulses_jax.py` skeleton and templates

**ADD** `engine/pulses_jax.py`.

Templates must be loaded **outside** `jit`: `rise_arr` builds a Python list from `gaussian(...)`. That is not JAX.

**Type this file** (then fill the two functions in steps 2–3):

```python
"""JAX assembly of echoed-CR envelopes for autodiff GRAPE.

NumPy twin: engine/pulses.py assemble_cr_half_from_flat_knobs and
experiments/cr_len_sweep.py _build_timeline_from_cr_half.

dt_ns is locked to 1.0 (GRAPE sim clock). Rise/fall templates are loaded
once as jax constants; only knob values are traced.
"""
from __future__ import annotations

from functools import partial

import jax.numpy as jnp
import numpy as np

from Helper_Functions.helper_functionsv2 import fall_arr, rise_arr

CHANNEL_NAMES = ("q1_drive", "q2_drive", "cr_drive")
DEFAULT_ECHO_CHANNEL = "q1_drive"


def _templates_1ns(t_rise_ns: int) -> tuple[jnp.ndarray, jnp.ndarray]:
    t_rise_ns = int(t_rise_ns)
    rise = jnp.asarray(np.asarray(rise_arr(t_rise_ns), dtype=np.float64))
    fall = jnp.asarray(np.asarray(fall_arr(t_rise_ns), dtype=np.float64))
    return rise, fall
```

**Why NumPy then `jnp.asarray`:** `rise_arr` returns a Python list of floats. `np.asarray` once, then freeze as jax. After that, **never** call `rise_arr` inside the jitted cost.

**Why `float64`:** Phase 0 is double precision. Templates should match.

You can call `_templates_1ns` inside `assemble_cr_half_jax` with a Python `t_rise_ns`. First `jit` trace will bake the arrays in. Or load them in the test / optimizer `__init__` and pass them in. Passing them in is clearer:

```python
rise, fall = _templates_1ns(16)   # once, Python
assemble_cr_half_jax(knobs, rise=rise, fall=fall, n_flat=184, ...)
```

Both are fine. I would **pass them in** so the jitted function never imports Helper_Functions.

---

## 6. Step 2 — `assemble_cr_half_jax`

**ADD** to `pulses_jax.py`:

```python
def _expand_knobs_to_flat(knobs: jnp.ndarray, n_flat: int) -> jnp.ndarray:
    """Hold each knob for k = n_flat // n_knobs samples. n_knobs must divide n_flat."""
    n_knobs = int(knobs.shape[0])
    n_flat = int(n_flat)
    if n_knobs < 1 or n_flat < 1:
        raise ValueError("n_knobs and n_flat must be >= 1")
    if n_flat % n_knobs != 0:
        raise ValueError(
            f"n_knobs={n_knobs} must divide n_flat={n_flat}"
        )
    return jnp.repeat(knobs, n_flat // n_knobs)


def assemble_cr_half_jax(
    knobs: jnp.ndarray,
    *,
    rise: jnp.ndarray,
    fall: jnp.ndarray,
    n_flat: int,
    n_link_samples: int = 8,
) -> tuple[jnp.ndarray, dict[str, tuple[int, int]]]:
    """One CR-half envelope (MHz). Same contract as assemble_cr_half_from_flat_knobs.

    knobs: complex (n_knobs,)
    rise, fall: real templates at 1 ns (constants)
    n_flat: Python int, round(flat_len_ns / dt_ns)
    """
    knobs = jnp.asarray(knobs).reshape(-1)
    flat = _expand_knobs_to_flat(knobs, n_flat)

    n_link = max(1, min(int(n_link_samples), n_flat))
    u_rise_end = jnp.mean(flat[:n_link])
    u_fall_start = jnp.mean(flat[-n_link:])

    rise_end = rise[-1]
    fall_start = fall[0]
    rise_part = (rise / rise_end) * u_rise_end
    fall_part = (fall / fall_start) * u_fall_start

    wf = jnp.concatenate([rise_part.astype(knobs.dtype), flat, fall_part.astype(knobs.dtype)])

    n_rise = int(rise.shape[0])
    n_fall = int(fall.shape[0])
    slices = {
        "rise": (0, n_rise),
        "flat": (n_rise, n_rise + n_flat),
        "fall": (n_rise + n_flat, n_rise + n_flat + n_fall),
    }
    return wf, slices
```

### 6.1 Syntax notes (read these)

**`jnp.repeat(knobs, k)`:** `k` is a Python int (`n_flat // n_knobs`). Legal in `jit`. Same as writing each knob into `k` consecutive samples. The **values** change every eval; the **length** `n_flat` does not.

**`jnp.mean(flat[:n_link])`:** `n_link` is Python. Slice `[:8]` is static. Mean of a traced array is a traced scalar. That is the scale that must stay JAX.

**`rise / rise_end`:** `rise` is a constant. `rise_end` is a constant. The quotient is a constant. Times `u_rise_end` (traced) scales the whole vector. JAX will give \(\partial \mathrm{wf}_\mathrm{rise}/\partial \mathrm{knob}_0 \neq 0\).

**Do not** `float(rise[-1])` here. Constants can stay 0-d jax arrays. `float(...)` on a tracer later would be a bug; doing it only on templates at load time is OK **in `_templates_1ns`**, not in this function.

**Do not** `raise` on `|rise[-1]| < 1e-12` inside a jitted call using a traced check. If you want a guard, do it once in Python after loading templates:

```python
rise, fall = _templates_1ns(16)
if abs(float(rise[-1])) < 1e-12 or abs(float(fall[0])) < 1e-12:
    raise ValueError("rise/fall template cannot anchor")
```

**dtype:** `knobs` should be `complex128`. `rise_part.astype(knobs.dtype)` matches the NumPy `rise_part.astype(complex)`.

### 6.2 Do not port the uneven NumPy loop

You do **not** need `searchsorted` or a Python `for i`. `jnp.repeat` is the whole expand.

NumPy still uses the general `//` loop. On every test case below it matches `repeat` because `n_knobs` divides `n_flat`. If you test `(3, 10)`, JAX should **raise**.

---

## 7. Step 3 — `echoed_timeline_jax`

**ADD** to `pulses_jax.py`:

```python
def echoed_timeline_jax(
    cr_plus: jnp.ndarray,
    x_pi: jnp.ndarray,
    *,
    channel_names: tuple[str, ...] = CHANNEL_NAMES,
    echo_channel: str = DEFAULT_ECHO_CHANNEL,
) -> dict[str, jnp.ndarray]:
    """Echoed CR: +u, Xπ, −u, Xπ. All channels present (idle = zeros).

    Same layout as CR_len_sweep._build_timeline_from_cr_half + Timeline.finalize.
    """
    cr_plus = jnp.asarray(cr_plus).reshape(-1)
    x_pi = jnp.asarray(x_pi).reshape(-1)
    n_cr = int(cr_plus.shape[0])
    n_x = int(x_pi.shape[0])
    zeros_cr = jnp.zeros((n_cr,), dtype=cr_plus.dtype)
    zeros_x = jnp.zeros((n_x,), dtype=cr_plus.dtype)

    cr_drive = jnp.concatenate([cr_plus, zeros_x, -cr_plus, zeros_x])
    echo = jnp.concatenate([zeros_cr, x_pi, zeros_cr, x_pi])
    L = int(cr_drive.shape[0])
    idle = jnp.zeros((L,), dtype=cr_plus.dtype)

    if echo_channel not in channel_names:
        raise KeyError(f"echo_channel {echo_channel!r} not in {channel_names}")

    out = {}
    for name in channel_names:
        if name == "cr_drive":
            out[name] = cr_drive
        elif name == echo_channel:
            out[name] = echo
        else:
            out[name] = idle
    return out
```

### 7.1 Syntax / layout

**`-cr_plus`:** JAX unary minus, same as NumPy. Second CR half.

**`zeros_cr` vs `zeros_x`:** first gap on `cr_drive` is **Xπ long**, not CR long. Mixing those lengths is the classic off-by-`n_x` bug.

**Dict of arrays:** JAX pytree. `jit` is happy if **keys and shapes** are the same every call. `channel_names` is a Python tuple, same order every time (`q1_drive`, `q2_drive`, `cr_drive`). Do not build the dict from `timeline.keys()` in random order.

**`echo_channel`:** Python string, static. GRAPE: `"q1_drive"`. If you ever echo on the target, pass `"q2_drive"`; then `q1_drive` is the idle zeros. The `for name in channel_names` handles that.

**`int(cr_plus.shape[0])`:** on a traced array inside `jit`, `.shape[0]` is still a concrete int if the length is static (it is: \(n_\mathrm{cr}\) is determined by templates + `n_flat`). If JAX ever treats it as a tracer, you passed a knob-dependent **length**, which Phase 2 forbids.

### 7.2 What you are not writing

No `Timeline.add`. No `start_ns`. No `int(round(t / dt))`. Times are implied by concatenation order on a 1 ns grid.

No padding to `L_max`. Exact \(L\).

No waits. Insert `jnp.zeros(n_wait)` later if you need idle nanoseconds.

---

## 8. Step 4 — test file (this is the Phase 2 gate)

**ADD** `optimization/optimization_tests/test_pulses_jax.py`.

The test must use the **real** NumPy functions as ground truth, including knob stretch and `Timeline.finalize`.

```python
"""Bit-match pulses_jax against engine/pulses.py + CR_len_sweep layout."""
from __future__ import annotations

import numpy as np

from HM.simulator.two_qubit_simulator.engine.pulses import (
    assemble_cr_half_from_flat_knobs,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    CHANNEL_NAMES,
    _templates_1ns,
    assemble_cr_half_jax,
    echoed_timeline_jax,
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep


def _random_knobs(n_knobs: int, rng: np.random.Generator) -> np.ndarray:
    amp = rng.uniform(5.0, 30.0, size=n_knobs)
    phase = rng.uniform(-np.pi, np.pi, size=n_knobs)
    return amp * np.exp(1j * phase)


def test_assemble_matches_numpy() -> None:
    t_rise_ns = 16
    dt_ns = 1.0
    n_link = 8
    rise, fall = _templates_1ns(t_rise_ns)
    rng = np.random.default_rng(0)

    cases = [
        (46, 184.0),   # regular GRAPE default: 4 samples per knob
        (61, 122.0),   # robust-style: 2 samples per knob
        (184, 184.0),  # one knob per sample
        (1, 184.0),    # single complex amp (seed-like)
    ]
    for n_knobs, flat_len_ns in cases:
        knobs = _random_knobs(n_knobs, rng)
        wf_np, sl_np = assemble_cr_half_from_flat_knobs(
            knobs,
            flat_len_ns=flat_len_ns,
            t_rise_ns=t_rise_ns,
            dt_ns=dt_ns,
            n_link_samples=n_link,
        )
        n_flat = int(round(flat_len_ns / dt_ns))
        wf_jx, sl_jx = assemble_cr_half_jax(
            knobs,  # numpy in is ok; function jnp.asarray's
            rise=rise,
            fall=fall,
            n_flat=n_flat,
            n_link_samples=n_link,
        )
        np.testing.assert_allclose(np.asarray(wf_jx), wf_np, atol=0, rtol=0)
        assert sl_jx == sl_np
        print("assemble ok", n_knobs, n_flat, "len", wf_np.size)

    try:
        assemble_cr_half_jax(
            _random_knobs(3, rng),
            rise=rise,
            fall=fall,
            n_flat=10,
            n_link_samples=n_link,
        )
    except ValueError:
        print("uneven (3, 10) rejected ok")
    else:
        raise AssertionError("expected ValueError when n_knobs does not divide n_flat")


def test_echoed_timeline_matches_numpy() -> None:
    exp = CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        engine="qutip",
        n_sub=2,
    )
    x_pi = exp.build_x_pi()
    rng = np.random.default_rng(1)
    knobs = _random_knobs(46, rng)
    cr_plus, _ = assemble_cr_half_from_flat_knobs(
        knobs,
        flat_len_ns=184.0,
        t_rise_ns=16,
        dt_ns=1.0,
        n_link_samples=8,
    )
    tl_np = exp._build_timeline_from_cr_half(cr_plus, x_pi=x_pi)
    tl_jx = echoed_timeline_jax(cr_plus, x_pi, channel_names=tuple(exp.channels))

    assert set(tl_jx) == set(tl_np) == set(CHANNEL_NAMES)
    for name in CHANNEL_NAMES:
        np.testing.assert_allclose(
            np.asarray(tl_jx[name]), tl_np[name], atol=0, rtol=0
        )
        print(name, "len", tl_np[name].size, "maxabs", np.max(np.abs(tl_np[name])))
    assert tl_np["q2_drive"].shape == tl_np["cr_drive"].shape
    assert np.allclose(tl_np["q2_drive"], 0.0)


def test_assemble_under_jit() -> None:
    import jax

    rise, fall = _templates_1ns(16)
    n_flat = 184
    knobs0 = _random_knobs(46, np.random.default_rng(2))

    @jax.jit
    def wf_len(knobs):
        wf, _ = assemble_cr_half_jax(
            knobs, rise=rise, fall=fall, n_flat=n_flat, n_link_samples=8
        )
        return wf

    a = wf_len(jnp.asarray(knobs0))
    b = wf_len(jnp.asarray(knobs0 * 1.01))
    assert a.shape == b.shape
    assert not np.allclose(np.asarray(a), np.asarray(b))
    print("jit assemble ok", a.shape, a.dtype)


if __name__ == "__main__":
    test_assemble_matches_numpy()
    test_echoed_timeline_matches_numpy()
    test_assemble_under_jit()
    print("PHASE 2 OK")
```

**`atol=0, rtol=0`:** same arithmetic, not “close enough.” When knobs divide `n_flat`, `jnp.repeat` matches NumPy’s `//` loop. If this fails, you used a different hold or dtype.

**`engine="qutip"`** in the timeline test: only to build `x_pi` and call `_build_timeline_from_cr_half`. You are not testing `sesolve`.

Run from `fourqubitv5/`:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python \
  HM/simulator/two_qubit_simulator/optimization/optimization_tests/test_pulses_jax.py
```

**Pass:** `PHASE 2 OK`, all `assemble ok` lines, all three channels match.

**Fail — `ValueError` on `(46, 184)`:** you checked `n_knobs % n_flat` instead of `n_flat % n_knobs`.

**Fail — you wanted JAX to accept `(3, 10)`:** out of scope. Change `n_flat_knobs` so it divides `n_flat`.

**Fail — `q2_drive` missing:** you did not emit idle zeros.

**Fail — `jit` ConcretizationTypeError:** a Python `if` on a traced knob, or `int(knobs[0])`. `n_flat` / `n_knobs` must stay Python.

**Fail — shapes change between two `jit` calls:** you traced a length. `n_flat` must not come from `knobs.size` if that size is not static (it is static if knobs length is fixed by config).

---

## 9. How `x` will connect later (not this phase, but so you see the slot)

Phase 4 will do:

```python
knobs = x[0::2] + 1j * x[1::2]          # length n_knobs
cr_plus, _ = assemble_cr_half_jax(knobs, rise=..., fall=..., n_flat=...)
timeline = echoed_timeline_jax(cr_plus, x_pi)
U_or_psi = sim.run_propagator / evolve_comp(timeline)
```

`x[0::2]` is “every even entry = I.” `x[1::2]` = Q. Same as `_x_to_knobs`. The knobs **are** the stretched flat, not a searched list of indices. Concatenate puts them at samples `[n_rise : n_rise+n_flat]`.

You do **not** pass `x` into `pulses_jax` in Phase 2. Tests pass **complex** `knobs` like NumPy does.

---

## 10. What the module looks like when you are done

```text
pulses_jax.py
    CHANNEL_NAMES, DEFAULT_ECHO_CHANNEL
    _templates_1ns(t_rise_ns) -> rise, fall   # Python, once
    _expand_knobs_to_flat(knobs, n_flat)      # jnp.repeat; n_knobs | n_flat
    assemble_cr_half_jax(...) -> wf, slices
    echoed_timeline_jax(...) -> dict of jnp, length L, 3 keys

pulses.py Timeline                         # UNCHANGED
cr_grape.py assemble_half                  # UNCHANGED (still NumPy)
```

`cr_grape.py` switching to `assemble_cr_half_jax` is Phase 4. If you switch it now, SciPy finite-difference still works (JAX forward is a valid forward), but you have not been asked to do that yet. Keep the split: NumPy path lives, JAX path is tested equal.

---

## 11. Stop condition

Phase 2 is **done** when:

1. `test_pulses_jax.py` prints `PHASE 2 OK`.
2. NumPy and JAX waveforms match at `atol=0` for the four knob layouts, including 46→184 stretch.
3. Echoed dict has three channels, `q2_drive` all zeros, same \(L\) as `Timeline.finalize()`.
4. `jax.jit` of `assemble_cr_half_jax` runs twice with different knobs, same shape.

Then stop. Do not open `fidelity_jax.py` until that is true. Phase 3 is a later MD.
