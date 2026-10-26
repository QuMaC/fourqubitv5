# Phase 0: create the package and bootstrap dynamiqs/JAX

Instructions only. You type the code.

Parent guide: `SIX_QUBIT_DYNAMIQS_ROADMAP.md`.

This phase deliberately follows the role of the existing 2Q Phase 0. It makes
the future engine module importable and configures JAX before any engine arrays
are created.

---

## 0. Scope

Phase 0 is:

1. creating a package layout similar to `two_qubit_simulator`
2. adding package marker files
3. adding shared constants
4. creating the n-qubit dynamiqs engine module as a runtime bootstrap
5. enabling float64 and complex128 at engine import
6. confirming six-qutrit operator support

Phase 0 is not:

- defining `Qubit`
- defining `DriveLine`
- defining `CouplingEdge`
- defining `NQubitSimulatorBase`
- defining the simulator class
- building a Hamiltonian
- creating a timeline
- calling `sesolve`
- loading an NPZ file
- editing the 2Q package
- requiring a GPU

Phase 1 adds the classes and physics methods.

---

## 1. Existing 2Q pattern being copied

The current 2Q package separates:

```text
two_qubit_simulator/
    base_classes/
        device_base.py
    engine/
        constants.py
        pulses.py
        two_q_pulse_sim_dynamiqs.py
    experiments/
    optimization/
```

The new package begins as:

```text
n_qubit_simulator/
    base_classes/
    engine/
    experiments/
    analysis/
    tests/
    documentation/
```

The 6Q validator has `analysis/` instead of `optimization/` because pulse
optimization remains in the 2Q package.

---

## 2. Check the environment

The environment observed while writing this guide was:

| Item | Value |
| --- | --- |
| dynamiqs | 0.3.4 |
| JAX | 0.6.2 |
| backend | CPU |
| visible GPU | none |
| x64 before engine import | false |

CPU is valid for Phase 0 and Phase 1.

Run:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import dynamiqs as dq
import jax

print("dynamiqs", dq.__version__)
print("jax", jax.__version__)
print("backend", jax.default_backend())
print("devices", jax.devices())
print("x64 before engine import", jax.config.read("jax_enable_x64"))

assert hasattr(dq, "set_precision")
assert hasattr(dq, "set_progress_meter")
assert hasattr(dq.gradient, "BackwardCheckpointed")
assert len(jax.devices()) >= 1
print("environment ok")
PY
```

Do not install CUDA JAX in this phase.

---

## 3. Create the directory structure

From `fourqubitv5/`, run:

```bash
mkdir -p HM/simulator/n_qubit_simulator/base_classes
mkdir -p HM/simulator/n_qubit_simulator/engine
mkdir -p HM/simulator/n_qubit_simulator/experiments
mkdir -p HM/simulator/n_qubit_simulator/analysis
mkdir -p HM/simulator/n_qubit_simulator/tests
```

The documentation directory and `guides/` already exist.

Create package marker files:

```bash
touch HM/simulator/n_qubit_simulator/__init__.py
touch HM/simulator/n_qubit_simulator/base_classes/__init__.py
touch HM/simulator/n_qubit_simulator/engine/__init__.py
touch HM/simulator/n_qubit_simulator/experiments/__init__.py
touch HM/simulator/n_qubit_simulator/analysis/__init__.py
touch HM/simulator/n_qubit_simulator/tests/__init__.py
```

Leave all six marker files empty.

Do not import the future engine from the top-level `__init__.py`. Importing a
data helper should not allocate six-qutrit operators or initialize a solver.

### 3.1 Check the scaffold

Run:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from pathlib import Path

root = Path("HM/simulator/n_qubit_simulator")
required = [
    root / "__init__.py",
    root / "base_classes" / "__init__.py",
    root / "engine" / "__init__.py",
    root / "experiments" / "__init__.py",
    root / "analysis" / "__init__.py",
    root / "tests" / "__init__.py",
    root / "documentation" / "guides"
    / "SIX_QUBIT_DYNAMIQS_ROADMAP.md",
    root / "documentation" / "guides"
    / "PHASE_0_SCAFFOLD_RUNTIME_AND_CONTRACTS.md",
    root / "documentation" / "guides"
    / "PHASE_1_CLOSED_SYSTEM_ENGINE.md",
]
missing = [str(path) for path in required if not path.is_file()]
assert not missing, f"missing files: {missing}"
print("scaffold ok")
PY
```

---

## 4. Add engine constants

Create:

```text
HM/simulator/n_qubit_simulator/engine/constants.py
```

Add:

```python
"""Shared numerical conventions for the n-qubit simulator."""

from math import pi

TWOPI = 2.0 * pi
DT_SAMPLE_NS = 1.0
```

Why use `math.pi` here:

- the constants remain ordinary Python floats
- importing constants does not create JAX arrays
- runtime precision remains the engine module's responsibility

Why 1 ns:

- saved GRAPE NPZ waveforms use a 1 ns grid
- strict c1t2 parity in Phase 2 must preserve that grid
- an OPX hardware timing model is deferred

Check:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from HM.simulator.n_qubit_simulator.engine.constants import (
    DT_SAMPLE_NS,
    TWOPI,
)

print("DT_SAMPLE_NS", DT_SAMPLE_NS)
print("TWOPI", TWOPI)
assert DT_SAMPLE_NS == 1.0
assert abs(TWOPI - 6.283185307179586) < 1e-15
print("constants ok")
PY
```

---

## 5. Create the engine bootstrap

Create:

```text
HM/simulator/n_qubit_simulator/engine/n_q_pulse_sim_dynamiqs.py
```

The file does not contain the simulator class yet. Phase 1 adds it below the
runtime configuration.

### 5.1 ADD the complete Phase 0 engine file

```python
"""Dynamiqs/JAX engine for an n-transmon pulse simulator.

Phase 0 contains only process-wide numerical configuration. Phase 1 adds
``NQubitPulseSimulatorDynamiqs`` without moving this configuration.
"""

from __future__ import annotations

import dynamiqs as dq


def _configure_jax() -> None:
    """Set process-wide dynamiqs/JAX defaults before engine arrays exist."""
    dq.set_precision("double")
    dq.set_progress_meter(False)


_configure_jax()
```

This follows the existing 2Q dynamiqs engine:

- configuration lives in the engine module
- configuration runs once when that module is imported
- double precision is not toggled in a class constructor
- GPU is not forced

Do not add:

```python
dq.set_device("gpu")
```

Do not add a second `runtime.py`.

---

## 6. Verify import-time precision

Use a fresh process:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
    _configure_jax,
)

import dynamiqs as dq
import jax
import jax.numpy as jnp

print("backend", jax.default_backend())
print("devices", jax.devices())
print("x64 after engine import", jax.config.read("jax_enable_x64"))

real_value = jnp.asarray(1.0)
complex_value = jnp.asarray(1.0 + 0.0j)
print("real dtype", real_value.dtype)
print("complex dtype", complex_value.dtype)

assert jax.config.read("jax_enable_x64") is True
assert real_value.dtype == jnp.float64
assert complex_value.dtype == jnp.complex128
assert hasattr(dq.gradient, "BackwardCheckpointed")
print("engine runtime ok")
PY
```

Required output:

```text
x64 after engine import True
real dtype float64
complex dtype complex128
engine runtime ok
```

The backend may be CPU or GPU.

---

## 7. Verify the six-qutrit primitive

The eventual engine will use the same `dq.destroy(*dims)` pattern that the 2Q
engine uses.

Run:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
    _configure_jax,
)

import dynamiqs as dq
import jax.numpy as jnp

dims = (3,) * 6
a = dq.destroy(*dims)
psi = dq.basis(dims, (1, 0, 0, 0, 0, 0))

print("operator count", len(a))
print("operator shape", a[0].shape)
print("operator dims", a[0].dims)
print("state shape", psi.shape)
print("state dims", psi.dims)

vector = dq.to_jax(psi).reshape(-1)
norm = jnp.vdot(vector, vector).real

assert len(a) == 6
assert all(operator.shape == (729, 729) for operator in a)
assert all(operator.dims == dims for operator in a)
assert psi.shape == (729, 1)
assert psi.dims == dims
assert dq.to_jax(a[0]).dtype == jnp.complex128
assert dq.to_jax(psi).dtype == jnp.complex128
assert jnp.allclose(norm, 1.0)
print("six-qutrit primitive ok")
PY
```

Do not write manual six-part Kronecker products.

---

## 8. Class decisions locked for Phase 1

Read this section before proceeding. Do not implement these classes in Phase 0.

### `Qubit`

Use the existing 2Q concept, extended with a physical ID and provenance:

```python
@dataclass
class Qubit:
    qubit_id: int
    anharm_MHz: float
    frame_MHz: float
    n_levels: int = 3
    f_qubit_MHz: float | None = None
    frequency_source: str = ""
    anharmonicity_source: str = ""
```

### `DriveLine`

Use:

```python
@dataclass
class DriveLine:
    name: str
    target_qubit_id: int
    carrier_MHz: float
```

`target_qubit_id` is the physical qubit acted on by the drive operator.

### `CouplingEdge`

Use:

```python
@dataclass
class CouplingEdge:
    name: str
    qubit_i: int
    qubit_j: int
    J_MHz: float
    is_calibrated: bool
    parameter_source: str
    enabled: bool = True
```

The endpoint names are neutral. Exchange is undirected.

### `NQubitSimulatorBase`

This class builds the records and constructs the engine, following
`TwoQubitSimulatorBase`.

It accepts:

```python
NQubitSimulatorBase(
    qubit_ids=(1, 2, 3, 4, 5, 6),
    n_levels=3,
    dt_sample_ns=1.0,
)
```

The default includes all six physical qubits. A subset such as
`qubit_ids=(1, 2, 6, 4)` is canonicalized to subsystem order
`(1, 2, 4, 6)`. Excluded qubits are removed from the Hilbert space, and edges
and drive lines are filtered to the selected IDs.

Qubit selection happens at construction. It is not changed on a built engine.

### `NQubitPulseSimulatorDynamiqs`

This class owns operators, Hamiltonian methods, and solver configuration,
following `TwoQubitPulseSimulatorDynamiqs`.

Do not create:

- `DeviceSpec`
- `FrameSet`
- `OperatorSet`
- `FinalStateResult`

---

## 9. Physics conventions locked for Phase 1

### Basis order

Subsystem order is ascending physical qubit ID.

For the default six-qutrit selection:

```text
order: Q1, Q2, Q3, Q4, Q5, Q6
|000000> -> 0
|000001> -> 1
|000010> -> 3
|100000> -> 243
```

For `qubit_ids=(1, 2, 6, 4)`:

```text
canonical order: Q1, Q2, Q4, Q6
dimension: 81
```

### Frames

Initially:

```python
qubit.frame_MHz = qubit.f_qubit_MHz
```

The engine derives:

```python
coupling_delta_MHz = frame_i_MHz - frame_j_MHz
drive_delta_MHz = carrier_MHz - frame_of_driven_qubit_MHz
```

### Coupling graph

Use all nine edges:

```text
c1_t2  c1_t4  c1_t6
c3_t2  c3_t4  c3_t6
c5_t2  c5_t4  c5_t6
```

Retain measured \(J\) for c1_t2, c1_t4, and c3_t2. Copy c1_t2 only to
the remaining six, with explicit synthetic provenance. For a selected subset,
retain only edges whose two endpoints are selected.

### Timeline

The finalized timeline contains all 15 channels as equal-length complex128
arrays. Idle channels are explicit zeros.

### Save policy

Phase 1 uses:

```python
dq.Options(save_states=False, progress_meter=False)
```

and returns:

```python
result.final_state
```

---

## 10. Final Phase 0 check

Run:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from pathlib import Path

from HM.simulator.n_qubit_simulator.engine.constants import (
    DT_SAMPLE_NS,
    TWOPI,
)
from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
    _configure_jax,
)

import dynamiqs as dq
import jax
import jax.numpy as jnp

root = Path("HM/simulator/n_qubit_simulator")
for relative in (
    "__init__.py",
    "base_classes/__init__.py",
    "engine/__init__.py",
    "engine/constants.py",
    "engine/n_q_pulse_sim_dynamiqs.py",
    "experiments/__init__.py",
    "analysis/__init__.py",
    "tests/__init__.py",
):
    assert (root / relative).is_file(), relative

assert DT_SAMPLE_NS == 1.0
assert abs(TWOPI - 2.0 * 3.141592653589793) < 1e-15
assert jax.config.read("jax_enable_x64") is True
assert jnp.asarray(1.0).dtype == jnp.float64
assert jnp.asarray(1.0j).dtype == jnp.complex128
assert len(jax.devices()) >= 1
assert hasattr(dq.gradient, "BackwardCheckpointed")

dims = (3,) * 6
a = dq.destroy(*dims)
psi = dq.basis(dims, (1, 0, 0, 0, 0, 0))
assert len(a) == 6
assert a[0].shape == (729, 729)
assert a[0].dims == dims
assert psi.shape == (729, 1)

print("backend", jax.default_backend())
print("devices", jax.devices())
print("joint dimension", psi.shape[0])
print("PHASE 0 OK")
PY
```

---

## 11. Failure guide

### `HM` does not import

Run from:

```text
/home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5
```

### x64 remains false

Check that:

1. `_configure_jax()` is called at module scope.
2. The engine module is imported before creating JAX arrays.
3. You used a fresh Python process.

Do not scatter `jax.config.update` into later files.

### No GPU is visible

Continue on CPU. This is not a Phase 0 failure.

### Operator construction uses substantial memory

Six dense \(729\times729\) operators are much larger than two 9-dimensional
operators. Construct them once during the check and let the process exit.

---

## 12. Stop condition

Phase 0 is complete only when:

1. the 2Q-aligned package directories exist
2. package marker files exist
3. constants import without initializing JAX arrays
4. importing the engine module enables x64
5. float64 and complex128 are active
6. at least one JAX device is visible
7. six embedded qutrit operators have shape `(729, 729)`
8. the final script prints `PHASE 0 OK`

Then stop and return with the complete terminal output. Do not begin Phase 1
until Phase 0 has been checked.
