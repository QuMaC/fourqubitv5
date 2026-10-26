# Phase 2: c1t2 waveform identity, then physics parity

Instructions only. You type the code.

Finish Phase 1 first. Its final output must include:

```text
PHASE 1 OK
```

Parent guide: `SIX_QUBIT_DYNAMIQS_ROADMAP.md`.

This phase replays one saved c1t2 GRAPE waveform. It does not optimize a pulse,
and it does not turn spectator couplings on.

---

## 0. Scope

Phase 2 is:

1. letting `levels_by_qubit` override the default truncation
2. copying the 2Q JAX CR-half and echoed-timeline assembly
3. copying the Q1 Xπ echo builder used by that assembly
4. loading `cr_half_opt_I` and `cr_half_opt_Q` from one NPZ
5. reading truncation and assembly lengths from the sibling JSON
6. embedding `cr_drive` onto `cr_c1_t2`, with every other channel explicit zeros
7. proving those samples mach the trusted 2Q assembler
8. evolving the same timeline on a Q1-Q2 chip
9. evolving it again on Q1, Q2, Q4, Q6 with Q4 and Q6 in `|0>` and spectator edges off
10. comparing both final states with a lab-frame 2Q dynamiqs replay

Phase 2 is not:

- editing `two_qubit_simulator`
- importing `pulses_jax.py` from the 2Q package inside `engine/`
- enabling `c1_t4` or `c1_t6`
- sweeping spectator states
- replaying the robust-GRAPE detuning batch
- computing a process fidelity or a reduced density matrix
- building a full propagator
- adding noise, transfer functions, or classical crosstalk

There is no GRAPE `.npz` inside this repository. The path at the bottom of
`two_qubit_simulator/experiments/cr_pulse_evolution.py` points at another
machine. Before the physics step, set `C1T2_NPZ_PATH` to an archive you
actually have, together with the `.json` saved beside it.

---

## 1. Decisions locked for this phase

### 1.1 Two comparisons, in this order

Waveform identity comes first. Physics parity comes second. If the samples
differ, do not call `sesolve`.

### 1.2 The assembler copy keeps the 2Q channel name

`engine/pulses_jax.py` still writes a channel named `cr_drive`.
`engine/c1t2_schedule.py` renames that buffer to `cr_c1_t2` when it builds
the n-qubit dictionary. The sequence math stays:

```text
+u on cr_drive, Xπ on q1_drive, -u on cr_drive, Xπ on q1_drive
```

`q2_drive` is idle in that echoed sequence. Spectator drives stay zero after
embedding.

### 1.3 Production code does not import the 2Q assembler

`engine/` must not import `HM.simulator.two_qubit_simulator`.

The waveform-identity script and the parity script may import the trusted
assembler and `TwoQubitSimulatorBase`. Those imports are the comparison, not
the implementation.

### 1.4 Parity truncation follows the sidecar

`RobustCRGrapeConfig.n_levels` defaults to 3, and the saved JSON is the
record of the run you are replaying. The active pair uses that integer.

Spectators stay at 3 levels. The object

```python
NQubitSimulatorBase(
    qubit_ids=(1, 2, 4, 6),
    n_levels=3,
    levels_by_qubit={1: 4, 2: 4},
)
```

is a constructor check in Step 1. It becomes the physics chip only when the
sidecar itself says `n_levels` is 4. A 4-level evolution is a different
Hilbert space from a 3-level GRAPE result, so it is not a valid comparison
partner for a 3-level archive.

### 1.5 Spectator pattern

Use `qubit_ids=(1, 2, 4, 6)`. Canonical order is Q1, Q2, Q4, Q6.

After construction, set:

```python
edge.enabled = {edge.qubit_i, edge.qubit_j} == {1, 2}
```

On this chip that leaves `c1_t2` enabled and disables `c1_t4` and `c1_t6`.
`CouplingEdge` is mutable, and the engine reads `enabled` when it builds the
coupling Hamiltonian for a shot. The same edge objects live in
`base.coupling_edges` and `simulator.coupling_edges`. Change the flag in
place. Do not rebuild the simulator.

Initial spectator occupations are 0. Spectator channels are the explicit
zeros from the embedding step.

### 1.6 Lab frame only

The archive stores one envelope. Robust GRAPE may have scored that envelope
at several target-frequency shifts. Phase 2 replays it once, at the calibrated
lab detuning. Do not pass a batch of frames into the 2Q reference.

### 1.7 Why the two frames can still agree

The 2Q base puts Q1 at frame `0` and Q2 at frame `-(f1 - f2)`. The n-qubit
base stores the calibrated frequencies directly. The detunings that enter the
Hamiltonian are the same:


| Term           | 2Q            | n-qubit   |
| -------------- | ------------- | --------- |
| Q1 self-drive  | `0 - 0`       | `f1 - f1` |
| Q2 self-drive  | `(-Δ) - (-Δ)` | `f2 - f2` |
| CR drive on Q1 | `(-Δ) - 0`    | `f2 - f1` |
| Coupling phase | `0 - (-Δ)`    | `f1 - f2` |


with `Δ = f1 - f2`. Both engines use `a1† a2` for the forward coupling and
the same `0.5 * 2π * anharmonicity * a† a† a a` drift. The pass test is an
elementwise amplitude difference, with no global-phase alignment.

### 1.8 Checks stay scripts

Same pattern as Phase 1. No new formal test package in this phase.

---

## 2. Files changed


| Step | File                                    | Action                             |
| ---- | --------------------------------------- | ---------------------------------- |
| 1    | `base_classes/device_base.py`           | add `levels_by_qubit`              |
| 2    | `engine/pulses_jax.py`                  | duplicate the 2Q JAX assembler     |
| 3    | `engine/c1t2_schedule.py`               | load NPZ, build Xπ, embed channels |
| 4    | `experiments/c1t2_waveform_identity.py` | sample equality, no `sesolve`      |
| 5    | `experiments/c1t2_parity.py`            | lab-frame state comparison         |


Do one step and run its check before continuing. Step 4 needs an NPZ path.
Steps 1 through 3 do not.

---

## 3. Step 1: per-qubit truncation

Phase 1 forces every selected qubit to `n_levels`, and it rejects any value
other than 3. Keep the default at 3. Add an override map.

### 3.1 Replace the constructor signature and the level setup

In `NQubitSimulatorBase.__init__`, use:

```python
    def __init__(
        self,
        *,
        qubit_ids: tuple[int, ...] = (1, 2, 3, 4, 5, 6),
        n_levels: int = 3,
        levels_by_qubit: dict[int, int] | None = None,
        dt_sample_ns: float = DT_SAMPLE_NS,
    ) -> None:
```

Immediately after `self.qubit_ids = tuple(sorted(requested_ids))`, replace
the single `self.n_levels = int(n_levels)` assignment with:

```python
        self.n_levels = int(n_levels)
        if self.n_levels < 2:
            raise ValueError("n_levels must be at least 2")

        overrides = {} if levels_by_qubit is None else dict(levels_by_qubit)
        unknown_override = set(overrides) - set(self.qubit_ids)
        if unknown_override:
            raise ValueError(
                f"levels_by_qubit names qubits that are not selected: "
                f"{sorted(unknown_override)}"
            )
        self.levels_by_qubit = {}
        for qubit_id, n_local in overrides.items():
            n_local = int(n_local)
            if n_local < 2:
                raise ValueError(
                    f"Q{int(qubit_id)} needs at least 2 levels, got {n_local}"
                )
            self.levels_by_qubit[int(qubit_id)] = n_local

        self.dt_sample_ns = float(dt_sample_ns)
```

Keep the rest of the constructor as it is.

### 3.2 Use the override in `build_qubits`

Change the `n_levels=` argument of `Qubit(...)` to:

```python
                n_levels=self.levels_by_qubit.get(qubit_id, self.n_levels),
```

### 3.3 Replace the Phase 1 truncation checks

In `_validate_device`, delete these two checks:

```python
        if any(qubit.n_levels != self.n_levels for qubit in self.qubits):
            raise ValueError("all Phase 1 transmons must use the same truncation")
        if self.n_levels != 3:
            raise ValueError("Phase 1 requires n_levels=3")
```

Put this in their place:

```python
        for qubit in self.qubits:
            expected = self.levels_by_qubit.get(qubit.qubit_id, self.n_levels)
            if qubit.n_levels != expected:
                raise ValueError(
                    f"Q{qubit.qubit_id} has {qubit.n_levels} levels, "
                    f"expected {expected}"
                )
            if qubit.n_levels < 2:
                raise ValueError(
                    f"Q{qubit.qubit_id} needs at least 2 levels"
                )
```

The engine already builds `dq.destroy(*dims)` from `qubit.n_levels`. Do not
change `n_q_pulse_sim_dynamiqs.py` in this step.

### 3.4 Check

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)

default = NQubitSimulatorBase()
mixed = NQubitSimulatorBase(
    qubit_ids=(1, 2, 6, 4),
    n_levels=3,
    levels_by_qubit={1: 4, 2: 4},
)

assert default.simulator.dims == (3, 3, 3, 3, 3, 3)
assert default.simulator.dim == 729
assert mixed.qubit_ids == (1, 2, 4, 6)
assert mixed.simulator.dims == (4, 4, 3, 3)
assert mixed.simulator.dim == 144
assert [qubit.n_levels for qubit in mixed.qubits] == [4, 4, 3, 3]
print("mixed truncation ok", mixed.simulator.dims, mixed.simulator.dim)
PY
```

Then rerun the Phase 1 smoke script. It must still print `PHASE 1 OK`.

---

## 4. Step 2: duplicate the JAX assembler

Create:

```text
HM/simulator/n_qubit_simulator/engine/pulses_jax.py
```

This is a copy of `two_qubit_simulator/engine/pulses_jax.py` with two
differences:

1. Do not call `jax.config.update`. Importing the n-qubit engine module
  already runs `dq.set_precision("double")`. A later x64 toggle can fail
   once any JAX array exists.
2. Import that engine module before `jax.numpy`, for the same reason
  `timelines.py` does.

Keep `CHANNEL_NAMES`, the `cr_drive` string, `jnp.repeat`, and the echo
layout. `n_flat` must be divisible by the knob count, which is the rule the
2Q JAX assembler already enforces. The robust default (`122` ns, `61` knobs)
satisfies it.

### 4.1 ADD the complete file

```python
"""JAX CR-half and echoed-timeline assembly.

Sequence math is a deliberate copy of
two_qubit_simulator/engine/pulses_jax.py. Channel names stay q1_drive,
q2_drive, and cr_drive. The n-qubit registry rename happens later, in
c1t2_schedule.py.
"""

from __future__ import annotations

from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
    _configure_jax,
)

import jax.numpy as jnp
import numpy as np

from Helper_Functions.helper_functionsv2 import fall_arr, rise_arr


CHANNEL_NAMES = ("q1_drive", "q2_drive", "cr_drive")
DEFAULT_ECHO_CHANNEL = "q1_drive"


def _templates_1ns(t_rise_ns: int) -> tuple[jnp.ndarray, jnp.ndarray]:
    t_rise_ns = int(t_rise_ns)
    rise = jnp.asarray(np.asarray(rise_arr(t_rise_ns)), dtype=np.float64)
    fall = jnp.asarray(np.asarray(fall_arr(t_rise_ns)), dtype=np.float64)
    return rise, fall


def _expand_knobs_to_flat(knobs: jnp.ndarray, n_flat: int) -> jnp.ndarray:
    """Hold each knob for k = n_flat // n_knobs samples.

    n_knobs must divide n_flat.
    """

    n_knobs = int(knobs.shape[0])
    n_flat = int(n_flat)
    if n_knobs < 1 or n_flat < 1:
        raise ValueError("n_knobs and n_flat must be at least 1")
    if n_flat % n_knobs != 0:
        raise ValueError("n_knobs must divide n_flat")
    return jnp.repeat(knobs, n_flat // n_knobs)


def assemble_cr_half_jax(
    knobs: jnp.ndarray,
    *,
    rise: jnp.ndarray,
    fall: jnp.ndarray,
    n_flat: int,
    n_link_samples: int,
) -> tuple[jnp.ndarray, dict[str, tuple[int, int]]]:
    knobs = jnp.asarray(knobs).reshape(-1)
    flat = _expand_knobs_to_flat(knobs, n_flat)

    n_link = max(1, min(int(n_link_samples), n_flat))
    u_rise_end = jnp.mean(flat[:n_link])
    u_fall_start = jnp.mean(flat[-n_link:])

    rise_end = rise[-1]
    fall_start = fall[0]
    rise_part = (rise / rise_end) * u_rise_end
    fall_part = (fall / fall_start) * u_fall_start
    waveform = jnp.concatenate(
        [
            rise_part.astype(knobs.dtype),
            flat,
            fall_part.astype(knobs.dtype),
        ]
    )

    n_rise = int(rise.shape[0])
    n_fall = int(fall.shape[0])
    slices = {
        "rise": (0, n_rise),
        "flat": (n_rise, n_rise + int(n_flat)),
        "fall": (n_rise + int(n_flat), n_rise + int(n_flat) + n_fall),
    }
    return waveform, slices


def echoed_timeline_jax(
    cr_plus: jnp.ndarray,
    x_pi: jnp.ndarray,
    *,
    channel_names: tuple[str, ...] = CHANNEL_NAMES,
    echo_channel: str = DEFAULT_ECHO_CHANNEL,
) -> dict[str, jnp.ndarray]:
    cr_plus = jnp.asarray(cr_plus).reshape(-1)
    x_pi = jnp.asarray(x_pi).reshape(-1)
    n_cr = int(cr_plus.shape[0])
    n_x = int(x_pi.shape[0])

    zeroes_cr = jnp.zeros((n_cr,), dtype=cr_plus.dtype)
    zeroes_x = jnp.zeros((n_x,), dtype=cr_plus.dtype)
    cr_drive = jnp.concatenate([cr_plus, zeroes_x, -cr_plus, zeroes_x])
    echo = jnp.concatenate([zeroes_cr, x_pi, zeroes_cr, x_pi])
    length = int(cr_drive.shape[0])
    idle = jnp.zeros((length,), dtype=cr_plus.dtype)

    if echo_channel not in channel_names:
        raise ValueError(
            f"echo_channel {echo_channel} not in channel_names {channel_names}"
        )

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

`_configure_jax` is imported for its module side effect. Do not call it again.

### 4.2 Check

This check imports the 2Q assembler on purpose.

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import numpy as np
import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.engine.pulses_jax import (
    _templates_1ns as templates_nq,
    assemble_cr_half_jax as assemble_nq,
    echoed_timeline_jax as echoed_nq,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    _templates_1ns as templates_2q,
    assemble_cr_half_jax as assemble_2q,
    echoed_timeline_jax as echoed_2q,
)

rise_nq, fall_nq = templates_nq(16)
rise_2q, fall_2q = templates_2q(16)
assert jnp.allclose(rise_nq, rise_2q)
assert jnp.allclose(fall_nq, fall_2q)

rng = np.random.default_rng(0)
x_pi = jnp.asarray(rng.normal(size=7) + 1j * rng.normal(size=7))
for n_knobs, n_flat in ((61, 122), (46, 184), (1, 184)):
    knobs = jnp.asarray(
        rng.normal(size=n_knobs) + 1j * rng.normal(size=n_knobs)
    )
    wf_nq, slices_nq = assemble_nq(
        knobs, rise=rise_nq, fall=fall_nq, n_flat=n_flat, n_link_samples=8
    )
    wf_2q, slices_2q = assemble_2q(
        knobs, rise=rise_2q, fall=fall_2q, n_flat=n_flat, n_link_samples=8
    )
    assert slices_nq == slices_2q
    assert jnp.allclose(wf_nq, wf_2q, rtol=0.0, atol=0.0)
    tl_nq = echoed_nq(wf_nq, x_pi)
    tl_2q = echoed_2q(wf_2q, x_pi)
    assert set(tl_nq) == {"q1_drive", "q2_drive", "cr_drive"}
    for name in tl_nq:
        assert jnp.allclose(tl_nq[name], tl_2q[name], rtol=0.0, atol=0.0)
    half = int(wf_nq.shape[0])
    echo_len = int(x_pi.shape[0])
    assert jnp.allclose(tl_nq["cr_drive"][:half], wf_nq)
    assert jnp.allclose(tl_nq["cr_drive"][half + echo_len: 2 * half + echo_len], -wf_nq)

print("assembler copy ok")
PY
```

---

## 5. Step 3: load, echo, and embed

Create:

```text
HM/simulator/n_qubit_simulator/engine/c1t2_schedule.py
```

This file owns everything that is specific to the saved c1t2 gate:

- the NPZ keys `cr_half_opt_I`, `cr_half_opt_Q`, `flat_knobs_opt`, and `t_ns`
- the sibling JSON fields used to rebuild that half
- the Q1 DRAG-GRFT Xπ, copied from `two_qubit_simulator/engine/pulses.py`
- the rename `cr_drive` to `cr_c1_t2`

### 5.1 ADD the complete file

```python
"""Saved c1t2 GRAPE half to a finalized n-qubit timeline dictionary."""

from __future__ import annotations

import json
from pathlib import Path

import jax.numpy as jnp
import numpy as np

from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
    _configure_jax,
)
from HM.simulator.n_qubit_simulator.engine.pulses_jax import (
    _templates_1ns,
    assemble_cr_half_jax,
    echoed_timeline_jax,
)


_SOURCE_TO_DEST = {
    "q1_drive": "q1_drive",
    "q2_drive": "q2_drive",
    "cr_drive": "cr_c1_t2",
}


def load_grape_sidecar(npz_path: str) -> dict:
    """Read the JSON written next to a GRAPE ``.npz``."""

    json_path = Path(npz_path).with_suffix(".json")
    if not json_path.is_file():
        raise FileNotFoundError(
            f"expected sidecar {json_path}. The NPZ alone does not store "
            "n_levels or the rise and flat lengths."
        )
    with json_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    config = payload["config"]
    qubit_pair = tuple(int(qubit_id) for qubit_id in config["qubit_pair"])
    if qubit_pair != (1, 2):
        raise ValueError(
            f"Phase 2 parity is the c1t2 archive, got qubit_pair {qubit_pair}"
        )
    n_levels = int(config["n_levels"])
    if n_levels < 2:
        raise ValueError(f"sidecar n_levels must be at least 2, got {n_levels}")
    return {
        "n_levels": n_levels,
        "flat_len_ns": float(config["flat_len_ns"]),
        "t_rise_ns": int(config["t_rise_ns"]),
        "n_link_samples": int(config["n_link_samples"]),
        "n_flat_knobs": int(config["n_flat_knobs"]),
        "qubit_pair": qubit_pair,
        "json_path": str(json_path),
    }


def load_optimized_cr_half(npz_path: str) -> tuple[jnp.ndarray, jnp.ndarray]:
    """Return ``(cr_half, flat_knobs_opt)`` from the saved I/Q arrays."""

    with np.load(npz_path, allow_pickle=False) as data:
        required = ("cr_half_opt_I", "cr_half_opt_Q", "flat_knobs_opt", "t_ns")
        missing = [key for key in required if key not in data.files]
        if missing:
            raise KeyError(
                f"{npz_path} is missing {missing}; available {sorted(data.files)}"
            )
        real = np.asarray(data["cr_half_opt_I"], dtype=np.float64).reshape(-1)
        imag = np.asarray(data["cr_half_opt_Q"], dtype=np.float64).reshape(-1)
        knobs = np.asarray(data["flat_knobs_opt"]).reshape(-1)
        t_ns = np.asarray(data["t_ns"], dtype=np.float64).reshape(-1)

    if real.shape != imag.shape:
        raise ValueError("cr_half_opt_I and cr_half_opt_Q differ in length")
    if t_ns.shape != real.shape:
        raise ValueError("t_ns length does not match the saved CR half")
    if t_ns.size > 1 and float(np.max(np.abs(np.diff(t_ns) - 1.0))) > 1e-9:
        raise ValueError("Phase 2 expects the saved CR half on a 1 ns grid")

    waveform = jnp.asarray(real + 1j * imag)
    return waveform, jnp.asarray(knobs)


def rebuild_cr_half(knobs: jnp.ndarray, sidecar: dict) -> jnp.ndarray:
    """Assemble the half the same way the JAX GRAPE path does."""

    n_flat = int(round(sidecar["flat_len_ns"]))
    if int(knobs.shape[0]) != int(sidecar["n_flat_knobs"]):
        raise ValueError(
            f"flat_knobs_opt length {int(knobs.shape[0])} does not match "
            f"sidecar n_flat_knobs {sidecar['n_flat_knobs']}"
        )
    rise, fall = _templates_1ns(sidecar["t_rise_ns"])
    waveform, _slices = assemble_cr_half_jax(
        knobs,
        rise=rise,
        fall=fall,
        n_flat=n_flat,
        n_link_samples=sidecar["n_link_samples"],
    )
    return waveform


def calibrate_f_rabi_per_opx1(
    amp_scale_x180: float,
    length_ns: int,
    rise_ns: int,
) -> float:
    """MHz Rabi rate per unit OPX waveform sample, from the X180 calibration."""

    from Helper_Functions.helper_functionsv2 import grft_pulse

    ac_amp_factor = 0.4
    a_grft = float(np.sum(grft_pulse(length_ns, rise_ns)))
    a_wf_x180 = ac_amp_factor * amp_scale_x180 * a_grft
    return 0.5 / (a_wf_x180 * 1e-3)


def drag_grft_envelope_mhz(
    amplitude: float,
    length_ns: int,
    rise_ns: int,
    anharm_hz: float,
    alpha: float,
    detuning: float = 0.0,
    f_rabi_per_opx1: float = 1.0,
) -> np.ndarray:
    """Complex d_X180 envelope in MHz, one sample per ns."""

    from Helper_Functions.helper_functionsv2 import drag_grft_pulse_waveforms

    i_wf, q_wf = drag_grft_pulse_waveforms(
        amplitude=amplitude,
        length=length_ns,
        rise=rise_ns,
        anharmonicity=anharm_hz,
        alpha=alpha,
        detuning=detuning,
    )
    return (
        np.asarray(i_wf, dtype=complex) + 1j * np.asarray(q_wf, dtype=complex)
    ) * f_rabi_per_opx1


def build_q1_x_pi() -> jnp.ndarray:
    """Calibrated control Xπ used as the echoed-CR echo."""

    from Configuration_Files.config_dictionaries import (
        amp_scale,
        anharmonicities,
        drag_dict,
        pi_len_ns,
        pi_rise_grft_ns,
    )

    qubit_key = "1"
    amplitude = float(amp_scale[qubit_key]["X180"])
    length_ns = int(pi_len_ns[qubit_key])
    rise_ns = int(pi_rise_grft_ns)
    waveform = drag_grft_envelope_mhz(
        amplitude=amplitude,
        length_ns=length_ns,
        rise_ns=rise_ns,
        anharm_hz=float(anharmonicities[qubit_key]) * 1e6,
        alpha=float(drag_dict[qubit_key]["alpha"]),
        detuning=float(drag_dict[qubit_key]["det"]),
        f_rabi_per_opx1=calibrate_f_rabi_per_opx1(
            amplitude, length_ns, rise_ns
        ),
    )
    return jnp.asarray(waveform)


def echoed_c1t2_timeline(
    cr_plus: jnp.ndarray,
    x_pi: jnp.ndarray | None = None,
) -> dict[str, jnp.ndarray]:
    """Echoed pair timeline on ``q1_drive``, ``q2_drive``, and ``cr_drive``."""

    if x_pi is None:
        x_pi = build_q1_x_pi()
    return echoed_timeline_jax(cr_plus, x_pi)


def embed_c1t2_timeline(
    pair_timeline: dict[str, jnp.ndarray],
    channel_names,
) -> dict[str, jnp.ndarray]:
    """Place the pair timeline onto an n-qubit channel registry.

    ``cr_drive`` is written to ``cr_c1_t2``. Every channel that is not the
    Q1 drive, the Q2 drive, or ``cr_c1_t2`` stays an explicit zero buffer of
    the echoed length.
    """

    channel_names = tuple(channel_names)
    missing = [
        dest for dest in _SOURCE_TO_DEST.values() if dest not in channel_names
    ]
    if missing:
        raise KeyError(f"channel registry is missing {missing}")

    length = int(jnp.asarray(pair_timeline["cr_drive"]).shape[0])
    for source in _SOURCE_TO_DEST:
        source_length = int(jnp.asarray(pair_timeline[source]).shape[0])
        if source_length != length:
            raise ValueError(
                f"{source} has length {source_length}, expected {length}"
            )

    out = {
        name: jnp.zeros(length, dtype=jnp.complex128)
        for name in channel_names
    }
    for source, dest in _SOURCE_TO_DEST.items():
        out[dest] = jnp.asarray(pair_timeline[source], dtype=jnp.complex128)
    return out
```

### 5.2 Check the Xπ copy and the embed

This still does not need an NPZ.

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import numpy as np
import jax.numpy as jnp

from Configuration_Files.config_dictionaries import (
    amp_scale,
    anharmonicities,
    drag_dict,
    pi_len_ns,
    pi_rise_grft_ns,
)
from HM.simulator.two_qubit_simulator.engine.pulses import (
    calibrate_f_rabi_per_opx1,
    drag_grft_envelope_mhz,
)
from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    build_q1_x_pi,
    echoed_c1t2_timeline,
    embed_c1t2_timeline,
)

qubit_key = "1"
amplitude = float(amp_scale[qubit_key]["X180"])
length_ns = int(pi_len_ns[qubit_key])
rise_ns = int(pi_rise_grft_ns)
trusted = drag_grft_envelope_mhz(
    amplitude=amplitude,
    length_ns=length_ns,
    rise_ns=rise_ns,
    anharm_hz=float(anharmonicities[qubit_key]) * 1e6,
    alpha=float(drag_dict[qubit_key]["alpha"]),
    detuning=float(drag_dict[qubit_key]["det"]),
    f_rabi_per_opx1=calibrate_f_rabi_per_opx1(amplitude, length_ns, rise_ns),
)
local = build_q1_x_pi()
assert jnp.allclose(local, jnp.asarray(trusted), rtol=0.0, atol=0.0)

cr_plus = jnp.asarray([0.25 + 0.1j, -0.4 + 0.3j, 0.15 - 0.05j])
pair = echoed_c1t2_timeline(cr_plus, x_pi=local)
channels = (
    "q1_drive",
    "q2_drive",
    "q4_drive",
    "q6_drive",
    "cr_c1_t2",
    "cr_c1_t4",
    "cr_c1_t6",
)
embedded = embed_c1t2_timeline(pair, channels)
assert jnp.allclose(embedded["q1_drive"], pair["q1_drive"])
assert jnp.allclose(embedded["q2_drive"], pair["q2_drive"])
assert jnp.allclose(embedded["cr_c1_t2"], pair["cr_drive"])
for name in ("q4_drive", "q6_drive", "cr_c1_t4", "cr_c1_t6"):
    assert float(jnp.max(jnp.abs(embedded[name]))) == 0.0
print("echo and embed ok", int(local.shape[0]), int(pair["cr_drive"].shape[0]))
PY
```

---

## 6. Step 4: waveform identity on the real archive

Create:

```text
HM/simulator/n_qubit_simulator/experiments/c1t2_waveform_identity.py
```

Set `C1T2_NPZ_PATH` before running. Do not call `sesolve` in this file.

The saved half is the physics input. Rebuilding it from `flat_knobs_opt` is
the identity check. Both must agree before Step 5.

### 6.1 ADD the complete file

```python
"""Prove the local c1t2 timeline matches the trusted 2Q assembler.

Run from fourqubitv5 after setting C1T2_NPZ_PATH:

    python -m HM.simulator.n_qubit_simulator.experiments.c1t2_waveform_identity
"""

from __future__ import annotations

import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    echoed_c1t2_timeline,
    embed_c1t2_timeline,
    load_grape_sidecar,
    load_optimized_cr_half,
    rebuild_cr_half,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    echoed_timeline_jax as echoed_timeline_2q,
)


# Fill this in with a local archive. The sibling .json must sit beside it.
C1T2_NPZ_PATH = ""


def main() -> None:
    if not C1T2_NPZ_PATH:
        raise SystemExit(
            "Set C1T2_NPZ_PATH in c1t2_waveform_identity.py to a local "
            "GRAPE .npz. The sibling .json must have the same stem."
        )

    sidecar = load_grape_sidecar(C1T2_NPZ_PATH)
    saved_half, knobs = load_optimized_cr_half(C1T2_NPZ_PATH)
    rebuilt = rebuild_cr_half(knobs, sidecar)
    half_error = float(jnp.max(jnp.abs(saved_half - rebuilt)))
    print("sidecar", sidecar["json_path"])
    print("n_levels", sidecar["n_levels"])
    print("flat_len_ns", sidecar["flat_len_ns"])
    print("half samples", int(saved_half.shape[0]))
    print("rebuilt half max abs error", half_error)
    assert half_error == 0.0 or half_error < 1e-12

    local_pair = echoed_c1t2_timeline(saved_half)
    n_half = int(saved_half.shape[0])
    n_echo = int((local_pair["q1_drive"].shape[0] - 2 * n_half) // 2)
    x_pi = local_pair["q1_drive"][n_half : n_half + n_echo]
    trusted_pair = echoed_timeline_2q(saved_half, x_pi)
    for name in ("q1_drive", "q2_drive", "cr_drive"):
        error = float(jnp.max(jnp.abs(local_pair[name] - trusted_pair[name])))
        print("pair channel", name, "max abs error", error)
        assert error < 1e-12

    channels = (
        "q1_drive",
        "q2_drive",
        "q4_drive",
        "q6_drive",
        "cr_c1_t2",
        "cr_c1_t4",
        "cr_c1_t6",
    )
    embedded = embed_c1t2_timeline(local_pair, channels)
    assert float(jnp.max(jnp.abs(embedded["cr_c1_t2"] - trusted_pair["cr_drive"]))) < 1e-12
    assert float(jnp.max(jnp.abs(embedded["q1_drive"] - trusted_pair["q1_drive"]))) < 1e-12
    assert float(jnp.max(jnp.abs(embedded["q2_drive"] - trusted_pair["q2_drive"]))) < 1e-12
    for name in ("q4_drive", "q6_drive", "cr_c1_t4", "cr_c1_t6"):
        assert float(jnp.max(jnp.abs(embedded[name]))) == 0.0

    print("WAVEFORM IDENTITY OK")


if __name__ == "__main__":
    main()
```

The Xπ slice above is only recovering the echo buffer that
`echoed_c1t2_timeline` already placed. Step 3 already compared that buffer
with the 2Q DRAG helper. This step compares the echoed layout.

### 6.2 Run

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python -m \
  HM.simulator.n_qubit_simulator.experiments.c1t2_waveform_identity
```

Required last line:

```text
WAVEFORM IDENTITY OK
```

If the rebuilt half does not match the saved half, stop. Do not start Step 5.
Report `rebuilt half max abs error` and the sidecar `n_flat_knobs`,
`flat_len_ns`, `t_rise_ns`, and `n_link_samples`.

---

## 7. Step 5: physics parity

Create:

```text
HM/simulator/n_qubit_simulator/experiments/c1t2_parity.py
```

Use the same `C1T2_NPZ_PATH` string as Step 4.

Two n-qubit chips:

```python
pair = NQubitSimulatorBase(
    qubit_ids=(1, 2),
    n_levels=sidecar["n_levels"],
    dt_sample_ns=1.0,
)
spectators = NQubitSimulatorBase(
    qubit_ids=(1, 2, 4, 6),
    n_levels=3,
    levels_by_qubit=(
        None
        if sidecar["n_levels"] == 3
        else {1: sidecar["n_levels"], 2: sidecar["n_levels"]}
    ),
    dt_sample_ns=1.0,
)
```

Disable spectator edges on the second chip before any shot:

```python
for edge in spectators.coupling_edges:
    edge.enabled = {edge.qubit_i, edge.qubit_j} == {1, 2}
```

The 2Q reference is:

```python
from HM.simulator.two_qubit_simulator.base_classes.device_base import (
    TwoQubitSimulatorBase,
)

reference = TwoQubitSimulatorBase(
    qubit_pair=[1, 2],
    engine="dynamiqs",
    n_levels=sidecar["n_levels"],
    dt_sample_ns=1.0,
)
```

Feed the reference the three-channel dictionary (`cr_drive`). Feed each
n-qubit engine the embedded dictionary (`cr_c1_t2`). Those active buffers
were already proved identical in Step 4. Check that identity again at the
start of this script, then evolve.

Initial states are every product state of the two active qudits, with
spectators in `|0>` on the larger chip. For sidecar `n_levels == 3` that is
9 shots per chip. For `n_levels == 4` it is 16.

Compare full pair-chip vectors with `reference.simulator.run_shot(...).full()`.
Compare the spectator-chip slice where Q4 and Q6 remain in `|0>` with that
same reference vector. Also require the population outside that slice to be
below `1e-8`.

Index convention, first qubit slowest:

```text
2Q index = occupation_q1 * n_levels + occupation_q2
n-qubit spectator index = that index * (n_q4 * n_q6)
```

`simulator.basis_index((c, t, 0, 0))` is the spectator-slice index.

Before evolving, assert:

- pair dimension equals `n_levels ** 2`
- spectator dims are `(n_levels, n_levels, 3, 3)`
- `c1_t2` is enabled on both chips
- `c1_t4` and `c1_t6` are disabled
- `c1_t2` `J_MHz` matches `reference.simulator.J_MHz`
- both anharmonicities match
- coupling detuning `frame_q1 - frame_q2` matches `reference.simulator.delta_qq_MHz`
- CR detuning `carrier - frame_q1` matches the 2Q `cr_drive` detuning
- `save_states` is false on both n-qubit engines

Pass criterion for every initial product state:

```text
max abs amplitude difference < 1e-8
spectator excitation < 1e-8
```

Print the worst difference. Do not loosen `1e-8` if a run misses it. Bring
the printed worst case back instead.

### 7.1 ADD the complete file

```python
"""Replay one c1t2 GRAPE archive on the n-qubit engine.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.c1t2_parity
"""

from __future__ import annotations

import numpy as np
import dynamiqs as dq
import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)
from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    echoed_c1t2_timeline,
    embed_c1t2_timeline,
    load_grape_sidecar,
    load_optimized_cr_half,
    rebuild_cr_half,
)
from HM.simulator.two_qubit_simulator.base_classes.device_base import (
    TwoQubitSimulatorBase,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    echoed_timeline_jax as echoed_timeline_2q,
)


# Keep this identical to c1t2_waveform_identity.C1T2_NPZ_PATH.
C1T2_NPZ_PATH = ""

_AMPLITUDE_ATOL = 1e-8


def _numpy_basis(dims: tuple[int, ...], occupations: tuple[int, ...]) -> np.ndarray:
    if len(dims) != len(occupations):
        raise ValueError("occupation count does not match dims")
    dim = 1
    for local_dim in dims:
        dim *= int(local_dim)
    index = 0
    for occupation, local_dim in zip(occupations, dims):
        index = index * int(local_dim) + int(occupation)
    vector = np.zeros((dim, 1), dtype=np.complex128)
    vector[index, 0] = 1.0
    return vector


def _spectator_ground_slice(sim, state) -> np.ndarray:
    vector = np.asarray(dq.to_jax(state)).reshape(-1)
    n0, n1 = sim.dims[0], sim.dims[1]
    tail = 1
    for local_dim in sim.dims[2:]:
        tail *= int(local_dim)
    sliced = np.empty(n0 * n1, dtype=np.complex128)
    for control in range(n0):
        for target in range(n1):
            flat = control * n1 + target
            sliced[flat] = vector[flat * tail]
    return sliced


def main() -> None:
    if not C1T2_NPZ_PATH:
        raise SystemExit(
            "Set C1T2_NPZ_PATH in c1t2_parity.py to the same local GRAPE .npz "
            "used for waveform identity."
        )

    sidecar = load_grape_sidecar(C1T2_NPZ_PATH)
    n_levels = sidecar["n_levels"]
    saved_half, knobs = load_optimized_cr_half(C1T2_NPZ_PATH)
    rebuilt = rebuild_cr_half(knobs, sidecar)
    half_error = float(jnp.max(jnp.abs(saved_half - rebuilt)))
    print("rebuilt half max abs error", half_error)
    assert half_error < 1e-12

    pair_timeline = echoed_c1t2_timeline(saved_half)
    n_half = int(saved_half.shape[0])
    n_echo = int((pair_timeline["q1_drive"].shape[0] - 2 * n_half) // 2)
    x_pi = pair_timeline["q1_drive"][n_half : n_half + n_echo]
    trusted = echoed_timeline_2q(saved_half, x_pi)
    for name in ("q1_drive", "q2_drive", "cr_drive"):
        error = float(jnp.max(jnp.abs(pair_timeline[name] - trusted[name])))
        assert error < 1e-12

    reference_base = TwoQubitSimulatorBase(
        qubit_pair=[1, 2],
        engine="dynamiqs",
        n_levels=n_levels,
        dt_sample_ns=1.0,
    )
    reference = reference_base.simulator

    pair_base = NQubitSimulatorBase(
        qubit_ids=(1, 2),
        n_levels=n_levels,
        dt_sample_ns=1.0,
    )
    overrides = None if n_levels == 3 else {1: n_levels, 2: n_levels}
    spectator_base = NQubitSimulatorBase(
        qubit_ids=(1, 2, 4, 6),
        n_levels=3,
        levels_by_qubit=overrides,
        dt_sample_ns=1.0,
    )
    for edge in spectator_base.coupling_edges:
        edge.enabled = {edge.qubit_i, edge.qubit_j} == {1, 2}

    pair = pair_base.simulator
    spectators = spectator_base.simulator
    pair_embedded = embed_c1t2_timeline(pair_timeline, pair.channel_names)
    spectator_embedded = embed_c1t2_timeline(
        pair_timeline,
        spectators.channel_names,
    )

    assert pair.dims == (n_levels, n_levels)
    assert pair.dim == n_levels * n_levels
    assert spectators.dims == (n_levels, n_levels, 3, 3)
    assert spectators.dim == n_levels * n_levels * 9
    assert pair._sesolve_options.save_states is False
    assert spectators._sesolve_options.save_states is False

    enabled = sorted(
        edge.name for edge in spectator_base.coupling_edges if edge.enabled
    )
    disabled = sorted(
        edge.name for edge in spectator_base.coupling_edges if not edge.enabled
    )
    print("enabled edges", enabled)
    print("disabled edges", disabled)
    assert enabled == ["c1_t2"]
    assert disabled == ["c1_t4", "c1_t6"]

    c1_t2 = next(
        edge for edge in pair_base.coupling_edges if edge.name == "c1_t2"
    )
    assert abs(c1_t2.J_MHz - float(reference.J_MHz)) < 1e-9
    assert abs(pair.qubits[0].anharm_MHz - reference.qubits[0].anharm_MHz) < 1e-9
    assert abs(pair.qubits[1].anharm_MHz - reference.qubits[1].anharm_MHz) < 1e-9

    delta_nq = pair.qubits[0].frame_MHz - pair.qubits[1].frame_MHz
    delta_2q = float(np.asarray(reference.delta_qq_MHz))
    print("coupling detuning n-qubit", delta_nq, "2Q", delta_2q)
    assert abs(delta_nq - delta_2q) < 1e-6

    cr_delta_nq = (
        pair.drive_lines["cr_c1_t2"].carrier_MHz - pair.qubits[0].frame_MHz
    )
    cr_delta_2q = (
        reference.drive_lines["cr_drive"].carrier_MHz
        - float(reference.qubits[0].frame_MHz)
    )
    print("CR detuning n-qubit", cr_delta_nq, "2Q", cr_delta_2q)
    assert abs(cr_delta_nq - cr_delta_2q) < 1e-6

    reference_timeline = {
        name: np.asarray(pair_timeline[name])
        for name in ("q1_drive", "q2_drive", "cr_drive")
    }
    worst = 0.0
    worst_spectator = 0.0
    for control in range(n_levels):
        for target in range(n_levels):
            psi_ref = _numpy_basis((n_levels, n_levels), (control, target))
            out_ref = reference.run_shot(
                reference_timeline,
                psi0=psi_ref,
            ).full().reshape(-1)

            out_pair = np.asarray(
                dq.to_jax(
                    pair.run_shot(
                        pair_embedded,
                        psi0=dq.basis(pair.dims, (control, target)),
                    )
                )
            ).reshape(-1)
            out_spec = spectators.run_shot(
                spectator_embedded,
                psi0=dq.basis(spectators.dims, (control, target, 0, 0)),
            )
            sliced = _spectator_ground_slice(spectators, out_spec)
            spectator_population = 1.0 - float(np.sum(np.abs(sliced) ** 2))

            pair_error = float(np.max(np.abs(out_pair - out_ref)))
            slice_error = float(np.max(np.abs(sliced - out_ref)))
            worst = max(worst, pair_error, slice_error)
            worst_spectator = max(worst_spectator, spectator_population)
            print(
                "input",
                (control, target),
                "pair error",
                pair_error,
                "spectator-slice error",
                slice_error,
                "spectator population",
                spectator_population,
            )
            assert pair_error < _AMPLITUDE_ATOL
            assert slice_error < _AMPLITUDE_ATOL
            assert spectator_population < _AMPLITUDE_ATOL

    print("worst amplitude error", worst)
    print("worst spectator population", worst_spectator)
    print("PHASE 2 OK")


if __name__ == "__main__":
    main()
```

### 7.2 Run

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python -m \
  HM.simulator.n_qubit_simulator.experiments.c1t2_parity
```

The first shot compiles. Later product states reuse that compilation only if
the shapes stay fixed, which they do. A 3-level archive is 9 reference shots,
9 pair shots, and 9 spectator shots of dimension 81.

Required structural lines include:

```text
enabled edges ['c1_t2']
disabled edges ['c1_t4', 'c1_t6']
PHASE 2 OK
```

---

## 8. Failure guide

### Rebuilt half does not match `cr_half_opt_I/Q`

Stop before `sesolve`. Check that the sidecar next to the NPZ belongs to
that NPZ, and that `n_flat_knobs` divides `flat_len_ns` on the 1 ns grid.
The JAX copy uses `jnp.repeat`. An archive whose flat length is not divisible
by the knob count was not produced by this assembler.

### `SystemExit` asking for `C1T2_NPZ_PATH`

The repository does not contain the waveform. Point both scripts at a local
`.npz` whose sibling `.json` is in the same directory.

### Pair amplitudes disagree while detuning asserts passed

The samples and the rotating-frame detunings already match. Compare one
matrix element of the pair Hamiltonian at a single time, the same way Phase 1
checks the Q2-to-Q1 coupling element, before changing tolerances.

### Spectator-slice error is large while the pair chip matches

`c1_t4` or `c1_t6` is still enabled, or a spectator channel received a
nonzero envelope. Print `enabled` and the max abs value of `q4_drive`,
`q6_drive`, `cr_c1_t4`, and `cr_c1_t6`.

### Spectator population is large while the slice matches

The active amplitudes agree and the extra population is leakage into Q4 or
Q6. That means a spectator coupling or a spectator drive is on. Do not treat
a global phase as the explanation: the slice test is elementwise.

### `levels_by_qubit` names a qubit outside `qubit_ids`

Overrides apply only to qubits that are actually in the tensor product.
Select the qubit first.

### Phase 1 smoke fails after Step 1

The default constructor must still build six qutrits. `levels_by_qubit`
defaults to `None`, and `n_levels` still defaults to 3.

---

## 9. Stop condition

Phase 2 is complete only when:

1. the default constructor is still six qutrits, dimension 729
2. `(1, 2, 4, 6)` with `{1: 4, 2: 4}` has dims `(4, 4, 3, 3)` and dimension 144
3. the JAX assembler matches the 2Q assembler exactly on the Step 2 knob set
4. the local Q1 Xπ matches `drag_grft_envelope_mhz` exactly
5. embedding writes `cr_drive` onto `cr_c1_t2` and leaves spectator channels at 0
6. the saved CR half matches `rebuild_cr_half` within `1e-12`
7. the echoed pair timeline matches `echoed_timeline_jax` from the 2Q package
8. the pair chip at the sidecar `n_levels` matches the 2Q final state within `1e-8` for every active product state
9. the spectator chip matches that same state on the Q4=Q6=`|0>` slice within `1e-8`
10. spectator excitation stays below `1e-8`
11. the only enabled spectator-chip edge is `c1_t2`
12. the parity script prints `PHASE 2 OK`

Then stop. Return with the waveform-identity output and the parity output
before enabling any spectator edge.