# Phase 1: build the 2Q-aligned six-qutrit engine

Instructions only. You type the code.

Finish Phase 0 first. Its final output must include:

```text
PHASE 0 OK
```

Parent guide: `SIX_QUBIT_DYNAMIQS_ROADMAP.md`.

This phase follows the existing 2Q architecture closely:

```text
base_classes/device_base.py
    -> engine/timelines.py
    -> engine/n_q_pulse_sim_dynamiqs.py
    -> experiments/closed_system_smoke.py
```

---

## 0. Scope

Phase 1 is:

1. adding `Qubit` and `DriveLine` records similar to the 2Q records
2. adding `CouplingEdge` because one scalar \(J\) cannot represent nine edges
3. adding `NQubitSimulatorBase` with construction-time qubit selection
4. adding one fixed-channel `Timeline`
5. completing `NQubitPulseSimulatorDynamiqs`
6. building operators as engine attributes
7. deriving every phase from `Qubit.frame_MHz`
8. building drift, coupling, and drive terms
9. evolving \(|100000\rangle\) with `sesolve`
10. returning only the final QArray

Phase 1 is not:

- loading an optimized waveform
- reproducing the 2Q result
- disabling spectator edges
- adding a full propagator
- adding reduced states or fidelity
- adding a separate frame class
- adding a separate operator class
- adding a result wrapper
- adding gradients
- adding noise

---

## 1. Files changed

| Step | File | Action |
| --- | --- | --- |
| 1 | `base_classes/device_base.py` | create device records and base |
| 2 | `engine/timelines.py` | create fixed global timeline |
| 3 | `engine/n_q_pulse_sim_dynamiqs.py` | extend Phase 0 bootstrap with engine |
| 4 | `experiments/closed_system_smoke.py` | create final-state smoke test |

Do one step and run its check before continuing.

---

## 2. Step 1: device records and base class

Create:

```text
HM/simulator/n_qubit_simulator/base_classes/device_base.py
```

### 2.1 Why `CouplingEdge` is new

The existing 2Q base passes:

```python
J_MHz: float
```

to its engine. There is exactly one physical pair, so no edge record is
necessary.

The 6Q graph has nine pairs. Each pair needs:

- two endpoints
- one \(J\)
- enabled state
- calibration status
- provenance

A list of `CouplingEdge` records is the minimal generalization.

The endpoint names are `qubit_i` and `qubit_j`, not control and target.
Exchange coupling is undirected. CR orientation is represented separately by
the `DriveLine` name, physical drive target, and carrier.

### 2.2 ADD the complete `device_base.py`

```python
"""Device records and shared setup for n-qubit simulator experiments."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from HM.simulator.n_qubit_simulator.engine.constants import DT_SAMPLE_NS


_REPO_ROOT = Path(__file__).resolve().parents[4]
_SYSTEM_PARAMETERS = _REPO_ROOT / "Configuration_Files" / "System_Parameters"


def _load_json(filename: str) -> dict:
    with (_SYSTEM_PARAMETERS / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


@dataclass
class Qubit:
    """One truncated transmon.

    `frame_MHz` is its rotating-frame frequency. The initial value equals the
    calibrated qubit frequency.
    """

    qubit_id: int
    anharm_MHz: float
    frame_MHz: float
    n_levels: int = 3
    f_qubit_MHz: float | None = None
    frequency_source: str = ""
    anharmonicity_source: str = ""


@dataclass(frozen=True)
class DriveLine:
    """A physical drive target and fixed carrier frequency."""

    name: str
    target_qubit_id: int
    carrier_MHz: float


@dataclass
class CouplingEdge:
    """One undirected exchange edge in the transmon graph."""

    name: str
    qubit_i: int
    qubit_j: int
    J_MHz: float
    is_calibrated: bool
    parameter_source: str
    enabled: bool = True


class NQubitSimulatorBase:
    """Build a selected subset of physical Q1 through Q6."""

    def __init__(
        self,
        *,
        qubit_ids: tuple[int, ...] = (1, 2, 3, 4, 5, 6),
        n_levels: int = 3,
        dt_sample_ns: float = DT_SAMPLE_NS,
    ) -> None:
        requested_ids = tuple(int(qubit_id) for qubit_id in qubit_ids)
        if not requested_ids:
            raise ValueError("select at least one qubit")
        if len(set(requested_ids)) != len(requested_ids):
            raise ValueError(f"qubit_ids contains duplicates: {requested_ids}")
        unknown = set(requested_ids) - set(range(1, 7))
        if unknown:
            raise ValueError(
                f"available physical qubits are 1 through 6; "
                f"got unknown ids {sorted(unknown)}"
            )

        # Tensor-product order is canonical and does not depend on caller order.
        self.qubit_ids = tuple(sorted(requested_ids))
        self.n_levels = int(n_levels)
        self.dt_sample_ns = float(dt_sample_ns)
        self.qubits = self.build_qubits()
        self.coupling_edges = self.build_coupling_edges()
        self.drive_lines = self.build_drive_lines()
        self._validate_device()

        from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
            NQubitPulseSimulatorDynamiqs,
        )

        self.simulator = NQubitPulseSimulatorDynamiqs(
            qubits=self.qubits,
            coupling_edges=self.coupling_edges,
            drive_lines=self.drive_lines,
            dt_sample_ns=self.dt_sample_ns,
        )
        self.channels = list(self.simulator.channel_names)

    def build_qubits(self) -> list[Qubit]:
        """Return selected qubits in canonical tensor-product order."""

        frequency_data = _load_json("fq_vals.json")["fq_vals"]
        anharmonicity_data = _load_json("anharmonicities.json")

        return [
            Qubit(
                qubit_id=qubit_id,
                anharm_MHz=-abs(float(anharmonicity_data[str(qubit_id)])),
                frame_MHz=float(frequency_data[str(qubit_id)]),
                n_levels=self.n_levels,
                f_qubit_MHz=float(frequency_data[str(qubit_id)]),
                frequency_source=f"fq_vals.json:{qubit_id}",
                anharmonicity_source=f"anharmonicities.json:{qubit_id}",
            )
            for qubit_id in self.qubit_ids
        ]

    def build_coupling_edges(self) -> list[CouplingEdge]:
        """Return all nine enabled odd-to-even exchange edges."""

        coupling_data = _load_json("coupling_vals.json")
        c1_t2_J = float(coupling_data["c1_t2"]["J_mhz"])

        all_edges = [
            CouplingEdge(
                "c1_t2",
                1,
                2,
                float(coupling_data["c1_t2"]["J_mhz"]),
                True,
                "coupling_vals.json:c1_t2",
            ),
            CouplingEdge(
                "c1_t4",
                1,
                4,
                float(coupling_data["c1_t4"]["J_mhz"]),
                True,
                "coupling_vals.json:c1_t4",
            ),
            CouplingEdge(
                "c1_t6", 1, 6, c1_t2_J, False, "synthetic_copy:c1_t2"
            ),
            CouplingEdge(
                "c3_t2",
                3,
                2,
                float(coupling_data["c3_t2"]["J_mhz"]),
                True,
                "coupling_vals.json:c3_t2",
            ),
            CouplingEdge(
                "c3_t4", 3, 4, c1_t2_J, False, "synthetic_copy:c1_t2"
            ),
            CouplingEdge(
                "c3_t6", 3, 6, c1_t2_J, False, "synthetic_copy:c1_t2"
            ),
            CouplingEdge(
                "c5_t2", 5, 2, c1_t2_J, False, "synthetic_copy:c1_t2"
            ),
            CouplingEdge(
                "c5_t4", 5, 4, c1_t2_J, False, "synthetic_copy:c1_t2"
            ),
            CouplingEdge(
                "c5_t6", 5, 6, c1_t2_J, False, "synthetic_copy:c1_t2"
            ),
        ]
        selected = set(self.qubit_ids)
        return [
            edge
            for edge in all_edges
            if edge.qubit_i in selected and edge.qubit_j in selected
        ]

    def build_drive_lines(self) -> list[DriveLine]:
        """Build self and CR lines contained in the selected subsystem."""

        frequency = {
            qubit.qubit_id: float(qubit.f_qubit_MHz)
            for qubit in self.qubits
        }

        self_drives = [
            DriveLine(
                name=f"q{qubit_id}_drive",
                target_qubit_id=qubit_id,
                carrier_MHz=frequency[qubit_id],
            )
            for qubit_id in self.qubit_ids
        ]

        cr_orientations = (
            (1, 2),
            (1, 4),
            (1, 6),
            (3, 2),
            (3, 4),
            (3, 6),
            (5, 2),
            (5, 4),
            (5, 6),
        )
        cr_drives = [
            DriveLine(
                name=f"cr_c{control_id}_t{target_id}",
                target_qubit_id=control_id,
                carrier_MHz=frequency[target_id],
            )
            for control_id, target_id in cr_orientations
            if control_id in frequency and target_id in frequency
        ]
        return self_drives + cr_drives

    def _validate_device(self) -> None:
        qubit_ids = tuple(qubit.qubit_id for qubit in self.qubits)
        if qubit_ids != self.qubit_ids:
            raise ValueError(
                f"built qubit order {qubit_ids} does not match "
                f"canonical selection {self.qubit_ids}"
            )
        if any(qubit.n_levels != self.n_levels for qubit in self.qubits):
            raise ValueError("all Phase 1 transmons must use the same truncation")
        if self.n_levels != 3:
            raise ValueError("Phase 1 requires n_levels=3")

        valid_ids = set(qubit_ids)
        edge_names = [edge.name for edge in self.coupling_edges]
        if len(set(edge_names)) != len(edge_names):
            raise ValueError("coupling edge names must be unique")
        for edge in self.coupling_edges:
            if edge.qubit_i not in valid_ids or edge.qubit_j not in valid_ids:
                raise ValueError(f"edge {edge.name} references an unknown qubit")
            if edge.qubit_i == edge.qubit_j:
                raise ValueError(f"edge {edge.name} is a self-edge")
            if edge.J_MHz < 0.0:
                raise ValueError(f"edge {edge.name} has negative J")
            if not edge.is_calibrated and not edge.parameter_source.startswith(
                "synthetic_copy:"
            ):
                raise ValueError(
                    f"edge {edge.name} lacks synthetic provenance"
                )

        line_names = [line.name for line in self.drive_lines]
        if len(set(line_names)) != len(line_names):
            raise ValueError("drive line names must be unique")
        expected_line_count = len(self.qubits) + len(self.coupling_edges)
        if len(self.drive_lines) != expected_line_count:
            raise ValueError(
                f"expected {expected_line_count} selected drive lines, "
                f"got {len(self.drive_lines)}"
            )
        if any(line.target_qubit_id not in valid_ids for line in self.drive_lines):
            raise ValueError("a drive line references an unknown qubit")
```

### 2.3 What matches the 2Q base

- `Qubit` owns `anharm_MHz`, `frame_MHz`, and `n_levels`.
- `DriveLine` owns a channel name, physical target, and carrier.
- The base builds qubits, drives, and the simulator.
- Experiments receive `self.simulator` and `self.channels`.

### 2.4 What is intentionally different

- Physical qubit IDs are explicit.
- Couplings are a list of edges instead of one scalar.
- `qubit_ids` selects the Hilbert-space factors at construction.
- Readout confusion matrices are deferred.
- No engine switch is needed yet because the 6Q backend is dynamiqs only.

Qubit selection and edge selection are different operations:

```python
# Build only Q1, Q2, Q4, and Q6. Joint dimension is 81.
base = NQubitSimulatorBase(qubit_ids=(1, 2, 6, 4))

# Keep those four qubits, but disable one retained interaction.
edge = next(
    edge
    for edge in base.simulator.coupling_edges
    if edge.name == "c1_t6"
)
edge.enabled = False
```

Changing `qubit_ids` requires constructing a new base and engine. Changing an
edge's `enabled` field does not change Hilbert-space dimension.

The Phase 1 physical catalog is deliberately limited to IDs 1 through 6. The
engine accepts a variable-length qubit list, but its dense embedded operators
are not a practical route to 12 qutrits. Do not remove the ID check and assume
that the resulting model will scale.

### 2.5 Check the device base

Run:

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)

base = NQubitSimulatorBase()
subset = NQubitSimulatorBase(qubit_ids=(1, 2, 6, 4))
synthetic = [
    edge.name for edge in base.coupling_edges if not edge.is_calibrated
]

print("qubits", [qubit.qubit_id for qubit in base.qubits])
print("dims", base.simulator.dims)
print("dimension", base.simulator.dim)
print("edges", len(base.coupling_edges))
print("channels", len(base.channels))
print("synthetic", synthetic)
print(
    "Q6 calibration review",
    base.qubits[5].anharm_MHz,
    base.qubits[5].anharmonicity_source,
)

assert base.simulator.dims == (3,) * 6
assert base.simulator.dim == 729
assert len(base.coupling_edges) == 9
assert len(base.channels) == 15
assert subset.qubit_ids == (1, 2, 4, 6)
assert subset.simulator.dims == (3,) * 4
assert subset.simulator.dim == 81
assert [
    (edge.qubit_i, edge.qubit_j)
    for edge in subset.coupling_edges
] == [(1, 2), (1, 4), (1, 6)]
assert subset.channels == [
    "q1_drive",
    "q2_drive",
    "q4_drive",
    "q6_drive",
    "cr_c1_t2",
    "cr_c1_t4",
    "cr_c1_t6",
]
assert synthetic == [
    "c1_t6",
    "c3_t4",
    "c3_t6",
    "c5_t2",
    "c5_t4",
    "c5_t6",
]
print("device base ok")
PY
```

This check imports the Phase 0 engine file. It will fail until the Phase 1
engine class is added. Therefore, type `device_base.py`, then continue directly
to Step 2 and Step 3 before running this complete base check.

To check only the records before Step 3, temporarily run:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)

base = object.__new__(NQubitSimulatorBase)
base.qubit_ids = (1, 2, 3, 4, 5, 6)
base.n_levels = 3
base.dt_sample_ns = 1.0
base.qubits = base.build_qubits()
base.coupling_edges = base.build_coupling_edges()
base.drive_lines = base.build_drive_lines()
base._validate_device()

assert len(base.qubits) == 6
assert len(base.coupling_edges) == 9
assert len(base.drive_lines) == 15
print("device records ok")
PY
```

---

## 3. Step 2: global timeline

Create:

```text
HM/simulator/n_qubit_simulator/engine/timelines.py
```

The existing 2Q `Timeline` owns one buffer per channel. Use the same concept,
but allocate the final shape at construction so every selected channel always
exists. The default six-qubit selection has 15 channels.

### 3.1 ADD the complete `timelines.py`

```python
"""Fixed-shape pulse timelines for the n-qubit simulator."""

from __future__ import annotations

from collections.abc import Sequence

from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
    _configure_jax,
)

import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.engine.constants import DT_SAMPLE_NS


class Timeline:
    """One equal-length complex JAX buffer per registered channel."""

    def __init__(
        self,
        channels: Sequence[str],
        *,
        n_samples: int,
        dt_ns: float = DT_SAMPLE_NS,
    ) -> None:
        self.channels = tuple(channels)
        self.n_samples = int(n_samples)
        self.dt_ns = float(dt_ns)

        if not self.channels:
            raise ValueError("timeline requires at least one channel")
        if len(set(self.channels)) != len(self.channels):
            raise ValueError("timeline channel names must be unique")
        if self.n_samples <= 0:
            raise ValueError("n_samples must be positive")
        if self.dt_ns <= 0.0:
            raise ValueError("dt_ns must be positive")

        self._buf = {
            channel: jnp.zeros(self.n_samples, dtype=jnp.complex128)
            for channel in self.channels
        }

    @property
    def duration_us(self) -> float:
        return self.n_samples * self.dt_ns * 1e-3

    def add(
        self,
        channel: str,
        start_ns: float,
        waveform,
    ) -> None:
        """Add a waveform to one channel without changing buffer shape."""

        if channel not in self._buf:
            raise KeyError(f"unknown timeline channel {channel!r}")
        start_float = float(start_ns) / self.dt_ns
        start = int(round(start_float))
        if abs(start_float - start) > 1e-9:
            raise ValueError("start_ns must align with the timeline sample grid")

        values = jnp.asarray(waveform, dtype=jnp.complex128).reshape(-1)
        stop = start + int(values.shape[0])
        if start < 0 or stop > self.n_samples:
            raise ValueError(
                f"waveform interval [{start}, {stop}) is outside "
                f"{self.n_samples} samples"
            )
        self._buf[channel] = self._buf[channel].at[start:stop].add(values)

    def finalize(self) -> dict[str, jnp.ndarray]:
        """Return all channels in their fixed registry order."""
        return {channel: self._buf[channel] for channel in self.channels}
```

### 3.2 Why this is similar but not identical to the 2Q timeline

The 2Q `Timeline` grows buffers as pulses are added. The 6Q validator knows the
replayed gate duration before propagation, so it allocates the final shape
immediately.

This gives:

- the familiar channel-buffer API
- no missing idle channels
- no shape changes
- JAX complex128 arrays

Importing `_configure_jax` before `jax.numpy` ensures that importing the
timeline module directly still enables double precision. The import does not
construct an engine or allocate six-qutrit operators.

### 3.3 Check the timeline

Run:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.engine.timelines import Timeline

channels = ("q1_drive", "q2_drive", "cr_c1_t2")
timeline = Timeline(channels, n_samples=20, dt_ns=1.0)
timeline.add("q1_drive", 3.0, jnp.asarray([1.0 + 0.5j, 2.0 - 0.5j]))
data = timeline.finalize()

assert tuple(data) == channels
assert all(values.shape == (20,) for values in data.values())
assert all(values.dtype == jnp.complex128 for values in data.values())
assert data["q1_drive"][3] == 1.0 + 0.5j
assert data["q1_drive"][4] == 2.0 - 0.5j
assert jnp.all(data["q2_drive"] == 0.0)
assert abs(timeline.duration_us - 0.020) < 1e-15
print("timeline ok")
PY
```

---

## 4. Step 3: complete the dynamiqs engine

Open the Phase 0 file:

```text
HM/simulator/n_qubit_simulator/engine/n_q_pulse_sim_dynamiqs.py
```

Keep `_configure_jax()` at the top. Replace the complete Phase 0 file with the
following Phase 1 version.

### 4.1 REPLACE with the complete engine

```python
"""Dynamiqs/JAX pulse-level engine for an n-transmon device."""

from __future__ import annotations

from typing import TYPE_CHECKING

import dynamiqs as dq


def _configure_jax() -> None:
    """Set process-wide dynamiqs/JAX defaults before engine arrays exist."""
    dq.set_precision("double")
    dq.set_progress_meter(False)


_configure_jax()

import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.engine.constants import (
    DT_SAMPLE_NS,
    TWOPI,
)

if TYPE_CHECKING:
    from HM.simulator.n_qubit_simulator.base_classes.device_base import (
        CouplingEdge,
        DriveLine,
        Qubit,
    )


class NQubitPulseSimulatorDynamiqs:
    """Global timeline in, final joint state out."""

    def __init__(
        self,
        qubits: list[Qubit],
        coupling_edges: list[CouplingEdge],
        drive_lines: list[DriveLine],
        *,
        dt_sample_ns: float = DT_SAMPLE_NS,
        integrator_tol: float = 1e-10,
        integrator_max_steps: int = 1_000_000,
    ) -> None:
        if not qubits:
            raise ValueError("at least one qubit is required")

        self.qubits = list(qubits)
        self.coupling_edges = list(coupling_edges)
        self.drive_lines = {line.name: line for line in drive_lines}
        self.channel_names = tuple(self.drive_lines)
        self.dt_sample_ns = float(dt_sample_ns)
        self.dt_sample_us = self.dt_sample_ns * 1e-3
        self.dims = tuple(qubit.n_levels for qubit in self.qubits)

        self.dim = 1
        for local_dim in self.dims:
            self.dim *= local_dim

        self._qubit_position = {
            qubit.qubit_id: position
            for position, qubit in enumerate(self.qubits)
        }
        if len(self._qubit_position) != len(self.qubits):
            raise ValueError("qubit IDs must be unique")

        self._integrator_method = dq.method.Tsit5(
            atol=integrator_tol,
            rtol=integrator_tol,
            max_steps=integrator_max_steps,
        )
        self._sesolve_options = dq.Options(
            save_states=False,
            progress_meter=False,
        )
        self._build_operators()

    def _position(self, qubit_id: int) -> int:
        try:
            return self._qubit_position[qubit_id]
        except KeyError as exc:
            raise KeyError(f"engine has no Q{qubit_id}") from exc

    def _build_operators(self) -> None:
        """Build all local operators and the static drift once."""

        self.a = list(dq.destroy(*self.dims))
        self.ad = [operator.dag() for operator in self.a]

        H_drift = 0.0 * (self.ad[0] @ self.a[0])
        for position, qubit in enumerate(self.qubits):
            H_drift = H_drift + (
                0.5
                * TWOPI
                * qubit.anharm_MHz
                * (
                    self.ad[position]
                    @ self.ad[position]
                    @ self.a[position]
                    @ self.a[position]
                )
            )
        self.H_drift = H_drift

        self._drive_ops = {}
        for name, line in self.drive_lines.items():
            position = self._position(line.target_qubit_id)
            self._drive_ops[name] = (
                0.5 * TWOPI * self.ad[position],
                0.5 * TWOPI * self.a[position],
            )

    def _validate_timeline(self, timeline: dict) -> int:
        expected = set(self.channel_names)
        actual = set(timeline)
        missing = expected - actual
        extra = actual - expected
        if missing or extra:
            raise KeyError(
                f"timeline mismatch, missing={sorted(missing)}, "
                f"extra={sorted(extra)}"
            )

        lengths = {name: len(timeline[name]) for name in self.channel_names}
        if len(set(lengths.values())) != 1:
            raise ValueError(f"timeline channel lengths differ: {lengths}")
        length = next(iter(lengths.values()))
        if length <= 0:
            raise ValueError("timeline must contain at least one sample")
        return int(length)

    def _coupling_hamiltonian(self):
        """Build all enabled rotating-frame exchange terms."""

        H = 0.0 * self.H_drift
        for edge in self.coupling_edges:
            if not edge.enabled:
                continue

            i = self._position(edge.qubit_i)
            j = self._position(edge.qubit_j)
            delta_MHz = (
                self.qubits[i].frame_MHz
                - self.qubits[j].frame_MHz
            )
            forward_operator = self.ad[i] @ self.a[j]
            backward_operator = forward_operator.dag()
            scale = TWOPI * edge.J_MHz

            forward = dq.modulated(
                lambda t, delta=delta_MHz: jnp.exp(
                    1j * TWOPI * delta * t
                ),
                scale * forward_operator,
            )
            backward = dq.modulated(
                lambda t, delta=delta_MHz: jnp.exp(
                    -1j * TWOPI * delta * t
                ),
                scale * backward_operator,
            )
            H = H + forward + backward
        return H

    def _drive_hamiltonian(
        self,
        name: str,
        envelope: jnp.ndarray,
        discontinuity_ts: jnp.ndarray,
    ):
        """Build one piecewise-envelope drive with continuous carrier phase."""

        line = self.drive_lines[name]
        position = self._position(line.target_qubit_id)
        delta_MHz = line.carrier_MHz - self.qubits[position].frame_MHz
        ad_operator, a_operator = self._drive_ops[name]
        n_samples = envelope.shape[0]
        dt_us = self.dt_sample_us

        def sample_index(t):
            index = jnp.floor(t / dt_us).astype(jnp.int32)
            return jnp.clip(index, 0, n_samples - 1)

        def coefficient_adjoint(t):
            epsilon = envelope[sample_index(t)]
            return epsilon * jnp.exp(-1j * TWOPI * delta_MHz * t)

        def coefficient_lowering(t):
            epsilon = envelope[sample_index(t)]
            return jnp.conj(epsilon) * jnp.exp(
                1j * TWOPI * delta_MHz * t
            )

        return (
            dq.modulated(
                coefficient_adjoint,
                ad_operator,
                discontinuity_ts=discontinuity_ts,
            )
            + dq.modulated(
                coefficient_lowering,
                a_operator,
                discontinuity_ts=discontinuity_ts,
            )
        )

    def _build_hamiltonian(self, timeline: dict):
        length = self._validate_timeline(timeline)
        discontinuity_ts = jnp.linspace(
            0.0,
            length * self.dt_sample_us,
            length + 1,
        )

        H = self.H_drift + self._coupling_hamiltonian()
        for name in self.channel_names:
            envelope = jnp.asarray(
                timeline[name],
                dtype=jnp.complex128,
            )
            H = H + self._drive_hamiltonian(
                name,
                envelope,
                discontinuity_ts,
            )
        return H

    def hamiltonian(self, timeline: dict):
        """Public Hamiltonian builder used by validation experiments."""
        return self._build_hamiltonian(timeline)

    def run_shot(
        self,
        timeline: dict,
        psi0=None,
    ):
        """Evolve one joint ket and return only the final dynamiqs QArray."""

        length = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        if psi0 is None:
            psi0 = dq.basis(self.dims, (0,) * len(self.dims))
        if psi0.shape != (self.dim, 1):
            raise ValueError(
                f"psi0 has shape {psi0.shape}, expected {(self.dim, 1)}"
            )

        tsave = jnp.asarray(
            [0.0, length * self.dt_sample_us],
            dtype=jnp.float64,
        )
        result = dq.sesolve(
            H,
            psi0,
            tsave,
            method=self._integrator_method,
            gradient=None,
            options=self._sesolve_options,
        )
        return result.final_state

    def measure_state_norm(self, state) -> float:
        """Return the norm of one ket as a Python float."""
        vector = dq.to_jax(state).reshape(-1)
        return float(jnp.vdot(vector, vector).real)

    def basis_index(self, occupations: tuple[int, ...]) -> int:
        """Return the flattened row-major tensor-product basis index."""
        if len(occupations) != len(self.dims):
            raise ValueError("occupation count does not match subsystem count")
        index = 0
        for occupation, local_dim in zip(occupations, self.dims):
            if not 0 <= occupation < local_dim:
                raise ValueError(
                    f"occupation {occupation} is outside dimension {local_dim}"
                )
            index = index * local_dim + occupation
        return index
```

### 4.2 Similarity with the 2Q dynamiqs engine

Both engines have:

- import-time `_configure_jax`
- `self.qubits`
- `self.drive_lines`
- `self.dims` and `self.dim`
- `self.a` and `self.ad`
- `self.H_drift`
- `_build_operators`
- `_drive_hamiltonian`
- `_build_hamiltonian`
- `run_shot`
- Tsit5

The main structural change is:

```text
2Q: self.J_MHz
NQ: self.coupling_edges
```

### 4.3 Why operators stay in the engine

The existing 2Q engine does not need an `OperatorSet` wrapper. Neither does the
first n-qubit engine.

Keeping:

```python
self.a
self.ad
self.H_drift
```

makes the code easier to compare line by line with the trusted 2Q engine.

### 4.4 Why frames stay on `Qubit`

The existing engine reads `qubit.frame_MHz`. The n-qubit engine does the same.

Every build derives:

```python
frame_i - frame_j
carrier - driven_qubit.frame_MHz
```

There is no cached `delta_ij` to become stale.

### 4.5 Check the complete base and engine

Now rerun the complete device-base check from Section 2.5.

Then run:

```bash
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import dynamiqs as dq

from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)

base = NQubitSimulatorBase()
sim = base.simulator

assert len(sim.a) == 6
assert len(sim.ad) == 6
assert all(operator.shape == (729, 729) for operator in sim.a)
assert all(operator.dims == (3,) * 6 for operator in sim.a)
assert sim.H_drift.shape == (729, 729)
assert sim.basis_index((0, 0, 0, 0, 0, 1)) == 1
assert sim.basis_index((0, 0, 0, 0, 1, 0)) == 3
assert sim.basis_index((1, 0, 0, 0, 0, 0)) == 243
assert sim._sesolve_options.save_states is False
assert dq.to_jax(sim.a[0]).dtype.name == "complex128"
print("engine structure ok")
PY
```

---

## 5. Step 4: closed-system smoke experiment

Create:

```text
HM/simulator/n_qubit_simulator/experiments/closed_system_smoke.py
```

This script performs two checks:

1. Hamiltonian Hermiticity with nonzero complex self-drive and CR envelopes.
2. Final-state evolution on an idle timeline from \(|100000\rangle\).

The nonzero probe is important. An all-zero timeline cannot detect a drive
conjugation error.

### 5.1 ADD the complete smoke experiment

```python
"""Phase 1 smoke test for the six-qutrit dynamiqs engine.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.closed_system_smoke
"""

from __future__ import annotations

import dynamiqs as dq
import jax
import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)
from HM.simulator.n_qubit_simulator.engine.constants import TWOPI
from HM.simulator.n_qubit_simulator.engine.timelines import Timeline


def main() -> None:
    base = NQubitSimulatorBase(n_levels=3, dt_sample_ns=1.0)
    sim = base.simulator

    print("backend", jax.default_backend())
    print("devices", jax.devices())
    print("dims", sim.dims)
    print("dimension", sim.dim)
    print("edges", len(sim.coupling_edges))
    print("channels", len(sim.channel_names))
    print(
        "synthetic edges",
        [
            edge.name
            for edge in sim.coupling_edges
            if not edge.is_calibrated
        ],
    )
    print(
        "CALIBRATION REVIEW: Q6 anharmonicity",
        sim.qubits[5].anharm_MHz,
        "MHz from",
        sim.qubits[5].anharmonicity_source,
    )

    expected_edges = (
        ("c1_t2", 1, 2),
        ("c1_t4", 1, 4),
        ("c1_t6", 1, 6),
        ("c3_t2", 3, 2),
        ("c3_t4", 3, 4),
        ("c3_t6", 3, 6),
        ("c5_t2", 5, 2),
        ("c5_t4", 5, 4),
        ("c5_t6", 5, 6),
    )
    actual_edges = tuple(
        (edge.name, edge.qubit_i, edge.qubit_j)
        for edge in sim.coupling_edges
    )
    expected_channels = (
        "q1_drive",
        "q2_drive",
        "q3_drive",
        "q4_drive",
        "q5_drive",
        "q6_drive",
        "cr_c1_t2",
        "cr_c1_t4",
        "cr_c1_t6",
        "cr_c3_t2",
        "cr_c3_t4",
        "cr_c3_t6",
        "cr_c5_t2",
        "cr_c5_t4",
        "cr_c5_t6",
    )
    assert actual_edges == expected_edges
    assert sim.channel_names == expected_channels
    assert sim.drive_lines["cr_c1_t2"].target_qubit_id == 1
    assert (
        sim.drive_lines["cr_c1_t2"].carrier_MHz
        == sim.qubits[1].f_qubit_MHz
    )

    idle_builder = Timeline(
        sim.channel_names,
        n_samples=20,
        dt_ns=sim.dt_sample_ns,
    )
    idle_timeline = idle_builder.finalize()

    probe_builder = Timeline(
        sim.channel_names,
        n_samples=20,
        dt_ns=sim.dt_sample_ns,
    )
    probe_builder.add(
        "q1_drive",
        0.0,
        jnp.full(20, 0.25 + 0.10j, dtype=jnp.complex128),
    )
    probe_builder.add(
        "cr_c1_t2",
        0.0,
        jnp.full(20, -0.40 + 0.30j, dtype=jnp.complex128),
    )
    probe_timeline = probe_builder.finalize()

    for label, timeline in (
        ("idle", idle_timeline),
        ("complex-drive", probe_timeline),
    ):
        H = sim.hamiltonian(timeline)
        for t_us in (0.0, 0.0030, 0.0035, 0.0070, 0.0075, 0.020):
            matrix = dq.to_jax(H(t_us))
            error = jnp.max(jnp.abs(matrix - matrix.conj().T))
            print(
                "timeline",
                label,
                "t_us",
                t_us,
                "Hermiticity error",
                float(error),
            )
            assert matrix.shape == (729, 729)
            assert float(error) < 1e-10

    probe_time_us = 0.0073
    probe_matrix = dq.to_jax(
        sim.hamiltonian(probe_timeline)(probe_time_us)
    )
    vacuum_index = sim.basis_index((0, 0, 0, 0, 0, 0))
    q1_index = sim.basis_index((1, 0, 0, 0, 0, 0))
    q2_index = sim.basis_index((0, 1, 0, 0, 0, 0))

    c1_t2 = next(
        edge for edge in sim.coupling_edges if edge.name == "c1_t2"
    )
    coupling_delta_MHz = (
        sim.qubits[0].frame_MHz - sim.qubits[1].frame_MHz
    )
    expected_q1_from_q2 = (
        TWOPI
        * c1_t2.J_MHz
        * jnp.exp(
            1j * TWOPI * coupling_delta_MHz * probe_time_us
        )
    )
    observed_q1_from_q2 = probe_matrix[q1_index, q2_index]
    print("Q2 to Q1 coupling element", observed_q1_from_q2)
    assert jnp.allclose(
        observed_q1_from_q2,
        expected_q1_from_q2,
        rtol=1e-10,
        atol=1e-10,
    )

    self_epsilon = 0.25 + 0.10j
    cr_epsilon = -0.40 + 0.30j
    cr_delta_MHz = (
        sim.drive_lines["cr_c1_t2"].carrier_MHz
        - sim.qubits[0].frame_MHz
    )
    expected_q1_from_vacuum = 0.5 * TWOPI * (
        self_epsilon
        + cr_epsilon
        * jnp.exp(-1j * TWOPI * cr_delta_MHz * probe_time_us)
    )
    observed_q1_from_vacuum = probe_matrix[q1_index, vacuum_index]
    print("vacuum to Q1 drive element", observed_q1_from_vacuum)
    assert jnp.allclose(
        observed_q1_from_vacuum,
        expected_q1_from_vacuum,
        rtol=1e-10,
        atol=1e-10,
    )

    initial_occupations = (1, 0, 0, 0, 0, 0)
    psi0 = dq.basis(sim.dims, initial_occupations)
    final_state = sim.run_shot(idle_timeline, psi0=psi0)
    norm = sim.measure_state_norm(final_state)
    vector = dq.to_jax(final_state).reshape(-1)

    populations = {}
    for qubit_position, qubit in enumerate(sim.qubits):
        occupations = tuple(
            1 if position == qubit_position else 0
            for position in range(6)
        )
        index = sim.basis_index(occupations)
        populations[f"Q{qubit.qubit_id}"] = float(
            jnp.abs(vector[index]) ** 2
        )

    print("final state shape", final_state.shape)
    print("final norm", norm)
    print("single-excitation populations", populations)
    print("single-excitation population sum", sum(populations.values()))

    assert sim.dims == (3,) * 6
    assert sim.dim == 729
    assert len(sim.coupling_edges) == 9
    assert len(sim.channel_names) == 15
    assert final_state.shape == (729, 1)
    assert abs(norm - 1.0) < 1e-8
    assert abs(sum(populations.values()) - 1.0) < 1e-8
    assert sim._sesolve_options.save_states is False

    print("PHASE 1 OK")


if __name__ == "__main__":
    main()
```

### 5.2 Why the evolution timeline is idle

Phase 1 tests:

- the six-transmon drift
- all nine exchange edges
- state propagation
- basis ordering
- norm conservation

The nonzero drive is used only for Hamiltonian Hermiticity. Phase 2 will replay
the first meaningful CR waveform.

### 5.3 Run

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python -m \
  HM.simulator.n_qubit_simulator.experiments.closed_system_smoke
```

The first call may compile slowly on CPU.

Required structural output:

```text
dims (3, 3, 3, 3, 3, 3)
dimension 729
edges 9
channels 15
final state shape (729, 1)
final norm 1.0
PHASE 1 OK
```

Do not hardcode the individual populations. Their sum is the invariant.

---

## 6. Physics review

### 6.1 Drift

For each transmon:

\[
H_{\mathrm{anh},i}
=
\frac{2\pi\alpha_i}{2}
a_i^\dagger a_i^\dagger a_i a_i.
\]

There is no bare-frequency diagonal because every transmon has its own
rotating frame.

### 6.2 Exchange edge

For an edge between qubits \(i\) and \(j\):

\[
H_{ij}(t)
=
2\pi J_{ij}
\left[
a_i^\dagger a_j e^{i2\pi(\omega_i-\omega_j)t}
+
a_i a_j^\dagger e^{-i2\pi(\omega_i-\omega_j)t}
\right].
\]

The code uses:

```python
forward_operator = ad[i] @ a[j]
backward_operator = forward_operator.dag()
```

### 6.3 Drive

For a line physically driving qubit \(i\):

\[
H_l(t)
=
\pi
\left[
\epsilon(t)e^{-i2\pi(f_l-\omega_i)t}a_i^\dagger
+
\epsilon^*(t)e^{i2\pi(f_l-\omega_i)t}a_i
\right].
\]

For `cr_c1_t2`:

```text
drive operator: Q1
carrier: Q2 frequency
```

### 6.4 Time units

The engine uses:

```python
dt_sample_us = dt_sample_ns * 1e-3
```

With MHz frequencies and microsecond solver time, the phase is dimensionless.

---

## 7. Failure guide

### `NQubitPulseSimulatorDynamiqs` cannot be imported

Phase 0 contains only the bootstrap. Confirm that you replaced the whole file
with the Phase 1 version in Section 4.

### `TYPE_CHECKING` names fail at runtime

The annotations are postponed by:

```python
from __future__ import annotations
```

Do not remove that import.

### Hamiltonian is not Hermitian

Check:

- both exchange directions are present
- the backward operator is the adjoint
- drive coefficients use conjugate envelope and opposite phase
- both \(a^\dagger\) and \(a\) terms are present

### Timeline mismatch

Construct `Timeline` with:

```python
sim.channel_names
```

Do not handwrite a partial channel dictionary.

### Solver reaches maximum steps

Confirm:

```python
max_steps=1_000_000
```

Then verify units and phase frequencies before loosening tolerances.

### Norm is not conserved

Do not proceed. Check Hamiltonian Hermiticity, the initial-state shape, and
solver units.

### Process uses too much memory

Confirm `_build_operators()` runs once in `__init__`. Do not rebuild six dense
operators inside each edge or drive loop.

### Q6 anharmonicity appears anomalous

The current source value is \(-633.6\) MHz. Retain and report it. Do not
silently replace it during an architecture test.

---

## 8. Comparison with the removed over-abstract design

Phase 1 now intentionally has:

```text
Qubit
DriveLine
CouplingEdge
NQubitSimulatorBase
Timeline
NQubitPulseSimulatorDynamiqs
```

It no longer asks you to create:

```text
DeviceSpec
FrameSet
OperatorSet
FinalStateResult
device.py
operators.py
frames.py
hamiltonian.py
engine_dynamiqs.py
```

The physics did not become less structured. The same responsibilities now
live as methods and attributes on the engine, matching the 2Q implementation.

---

## 9. Stop condition

Phase 1 is complete only when:

1. `Qubit` and `DriveLine` match the existing concepts
2. `CouplingEdge` uses neutral physical endpoints
3. `NQubitSimulatorBase` canonicalizes selected physical IDs
4. the default selection builds six qutrits with dimension 729
5. `(1, 2, 6, 4)` builds ordered Q1, Q2, Q4, Q6 with dimension 81
6. coupling edges are filtered to selected endpoints without losing provenance
7. self and CR drive lines are filtered to the selected subsystem
8. the default engine owns six `(729, 729)` annihilation operators
9. `|100000>` maps to index 243 in the default six-qubit ordering
10. idle and complex-drive Hamiltonians are Hermitian
11. `run_shot` returns a final `(729, 1)` QArray for the default selection
12. state norm is conserved within \(10^{-8}\)
13. single-excitation population is conserved within \(10^{-8}\)
14. no trajectory or propagator is stored
15. the script prints `PHASE 1 OK`

Then stop. Return with all check outputs before beginning Phase 2.
