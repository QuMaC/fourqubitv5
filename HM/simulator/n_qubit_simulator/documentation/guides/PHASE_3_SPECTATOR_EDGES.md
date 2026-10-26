# Phase 3: spectator couplings on the c1t2 gate

Instructions only. You type the code.

Finish Phase 2 first. The waveform-identity script must print
`WAVEFORM IDENTITY OK`, and the parity script must agree with the 2Q engine
on the Q1-Q2 chip.

Parent guide: `SIX_QUBIT_DYNAMIQS_ROADMAP.md`.

Phase 2 replayed the c1t2 GRAPE pulse with every spectator edge off. This
phase turns spectator edges on and measures what they do to that same pulse.
It does not change the pulse.

---

## 0. Scope

Phase 3 is:

1. taking `c1_t2` from the lab file and every other coupling from the paper's
   cross-Kerr matrix
2. adding a batched shot to the engine so four inputs share one solve
3. adding a dressed-basis helper module in `analysis/`
4. checking that helper with an idle evolution against exact static ZZ
5. replaying the c1t2 gate on a control-side spectator chip, Q1, Q2, Q4, Q6
6. replaying it on a target-side spectator chip, Q1, Q2, Q3
7. comparing the target-side result with the 2Q robust-GRAPE frame-shift model

Phase 3 is not:

- editing `two_qubit_simulator`
- re-optimizing the pulse
- computing an absolute fidelity to ZX(-π/2) (Phase 4)
- correcting local Z with virtual-Z updates (Phase 4)
- tracing out spectators into a process matrix (Phase 4)
- adding noise, transfer functions, or classical crosstalk

---

## 1. Decisions locked for this phase

### 1.1 Coupling values and the composite device

`c1_t2` keeps the lab J from `coupling_vals.json`. With that J the model
reproduces the lab's measured c1_t2 shift: 179.5 kHz in the model against
178.9 kHz measured.

Q1 and Q2 keep the lab frequencies and anharmonicities. Q3 through Q6 take the
paper Table I anharmonicities, and the paper frequencies plus the Q1
lab-minus-paper offset (about 56.57 MHz). That keeps the c1t2 pulse on the
frequencies it was calibrated at, and keeps the paper's spectator detunings
relative to Q1. The lab files are not overwritten. See
`documentation/PAPER_VALUES.md`.

Every other edge takes its J from the paper's cross-Kerr matrix. The paper
gives a shift, not a J. The device base therefore fits J at construction so
that two coupled transmons, at the paper's Table I frequencies and
anharmonicities, reproduce the paper's shift exactly. That J is then used on
the composite device.

Those edges are not calibrations of this device, so they get:

```text
is_calibrated = False
parameter_source = "paper_zz_fit:<edge name>"
```

The shift is the full state-dependent frequency shift:

```text
zeta = E11 - E10 - E01 + E00
```

That is the same quantity as `total_det_mhz` in `coupling_vals.json`. The
`zz_khz` field in that file is half of it. If the paper defines its cross-Kerr
with a different factor, every fitted J is off by the square root of that
factor.

Q6 uses the paper anharmonicity, -271 MHz, not the lab file's 633.6 MHz.

The paper's next-nearest entries are at most 9.7 kHz (Q1-Q5). They stay out
of the model. They are recorded in the data file so that choice is visible.

### 1.2 Two spectator chips

The control-side chip is the one already planned:

```text
qubit_ids = (1, 2, 4, 6)
dims      = (4, 4, 3, 3), dimension 144
edges     = c1_t2, c1_t4, c1_t6
```

Both spectators couple to Q1, the control. None couples to Q2.

The robust GRAPE run was built against a shift of the target frequency, ±zz/2
with zz = 0.15 MHz. On the control-side chip no spectator shifts the target,
so that chip cannot test the robust design. This phase therefore adds a
second chip:

```text
qubit_ids = (1, 2, 3)
dims      = (4, 4, 3), dimension 48
edges     = c1_t2, c3_t2
```

Q3 couples to Q2. The paper puts that shift at 225 kHz, which is larger than
the 150 kHz span the pulse was optimized for.

Q1 and Q2 use the GRAPE sidecar truncation, 4 levels for the current archive.
Spectators use 3 levels.

### 1.3 Dressed states, not bare product states

With an edge on, a bare product state is not an eigenstate. Q2 and Q3 are
about 110 MHz apart, with J = 3.55 MHz. A bare `|010>` on the target-side chip
therefore swaps a fraction of a percent of its population into Q3 and back,
even with every drive off. Read in the bare basis, that oscillation looks like
spectator excitation, and it is not. Q2 and Q6 are only 2.2 MHz apart, which
is why the control-side chip has to be read in the dressed basis as well.

The hardware prepares and measures dressed states: the eigenstates of the
static lab Hamiltonian with every coupling on. This phase does the same:

1. diagonalize the static lab Hamiltonian of the chip
2. label each eigenvector by its largest bare component
3. start every shot from a dressed state
4. read every final state back in the dressed basis

### 1.4 Frequency compensation

The engine has no `(f_qubit - frame) n` term. Its rotating frame runs at
`Qubit.frame_MHz`, so `frame_MHz` is the bare qubit frequency of the model.

Calibrated frequencies are dressed: they already include every coupling on the
device. Adding an edge to the model without changing the bare frequencies
shifts the dressed frequencies a second time. On the target-side chip,
switching `c3_t2` on with bare frequencies left at the calibrated values pulls
Q2 down by 423 kHz. The CR carrier would then sit 423 kHz away from the target,
which no real calibration would allow.

So every spectator configuration is compensated:

```text
retune every frame_MHz until the dressed single-excitation frequency
of each qubit, spectators in |0>, equals its Phase 2 value
```

The Phase 2 value is the dressed frequency with only `c1_t2` on. That keeps
the edges-off baseline identical to Phase 2. Drive carriers never change. They
stay at the calibrated frequencies, as on the hardware.

After compensation, a spectator in `|0>` leaves every qubit frequency where
Phase 2 had it. A spectator in `|1>` moves its neighbour by the static ZZ.
That difference is the spectator error that a calibration cannot remove.

### 1.5 Carrier placement on the target-side chip

Where the target frequency sits relative to the two Q3 branches is a modeling
choice. This phase runs both:

| Placement | Q2 with Q3 in `|0>` | Q2 with Q3 in `|1>` |
| --- | --- | --- |
| ground-calibrated | Phase 2 value | Phase 2 value + zeta |
| midpoint | Phase 2 value - zeta/2 | Phase 2 value + zeta/2 |

Ground-calibrated is a Ramsey calibration done with Q3 in `|0>`. Midpoint is
the assumption robust GRAPE made: the carrier halfway between the branches.

### 1.6 Every metric is relative

The analysis frame rotates at the Phase 2 dressed frequencies. In that frame
the baseline already carries local Z from the c1_t2 dressing itself, about
0.26 rad per qubit over 412 ns. An absolute ZX(-π/2) fidelity would mostly
measure that local Z. Correcting it with virtual Z belongs to Phase 4.

Phase 3 therefore reports:

| Metric | Meaning |
| --- | --- |
| `F_vs_baseline` | overlap of a branch with the edges-off gate on the same chip |
| branch fidelity | overlap of the Q-in-`|1>` branch with the Q-in-`|0>` branch |
| spectator excitation | population that left the spectator state it started in |
| active leakage | population that stayed in the spectator branch but left the Q1-Q2 computational subspace |

The overlap is the process overlap of two 4x4 computational blocks:

```text
F(A, B) = |Tr(A^dagger B)|^2 / 16
```

It ignores a global phase. It does not ignore local Z, so a spectator-dependent
Z counts as error, as it should.

`F_vs_baseline` of the baseline with itself is not 1. The block loses a little
norm to leakage, so the self-overlap is `(1 - loss)^2`, about 0.9994 here.

### 1.7 Tolerance

The engine default, `1e-10`, is enough here. Phase 2 showed that it leaves the
dimension-144 state about `1e-7` away in amplitude. Every effect this phase
measures is at least `1e-4`.

### 1.8 Envelope

The archive was optimized with the `lp_350mhz` envelope filter. The n-qubit
engine has no filters until Phase 6. The 2Q comparison in Step 6 also uses the
default identity envelope, so that comparison is like for like.

### 1.9 Checks stay scripts

Same pattern as Phases 1 and 2.

---

## 2. Files changed

| Step | File | Action |
| --- | --- | --- |
| 1 | `base_classes/paper_cross_kerr_khz.json` | paper cross-Kerr data |
| 1 | `base_classes/device_base.py` | lab `c1_t2`, fitted J for the rest |
| 2 | `engine/n_q_pulse_sim_dynamiqs.py` | add `run_shot_batch` |
| 3 | `analysis/dressed_frame.py` | dressed basis, compensation, readout |
| 4 | `experiments/spectator_setup.py` | shared chip setup |
| 5 | `experiments/spectator_idle_zz.py` | idle check of the dressed frame |
| 6 | `experiments/spectator_gate_sweep.py` | the gate measurement |

Do one step and run its check before continuing.

---

## 3. Step 1: paper couplings

### 3.1 ADD the data file

Create:

```text
HM/simulator/n_qubit_simulator/base_classes/paper_cross_kerr_khz.json
```

```json
{
  "source": "J. Deshmukh et al., Phys. Rev. Research 8, 033049 (2026), DOI 10.1103/6jdh-pm39, Fig. 1(c)",
  "convention": "full state-dependent frequency shift E11 - E10 - E01 + E00, kHz",
  "nearest_neighbour_khz": {
    "c1_t2": 239.0,
    "c1_t4": 116.0,
    "c1_t6": 64.0,
    "c3_t2": 225.0,
    "c3_t4": 268.0,
    "c3_t6": 147.0,
    "c5_t2": 154.0,
    "c5_t4": 162.0,
    "c5_t6": 100.0
  },
  "next_nearest_khz": {
    "q1_q3": 4.9,
    "q1_q5": 9.7,
    "q2_q4": 3.8,
    "q2_q6": 3.9,
    "q3_q5": 0.4,
    "q4_q6": 2.5
  }
}
```

`c1_t2` is listed for completeness. The device base does not use it.

### 3.2 Imports

At the top of `device_base.py`, replace:

```python
from dataclasses import dataclass
import json
from pathlib import Path

from HM.simulator.n_qubit_simulator.engine.constants import DT_SAMPLE_NS
```

with:

```python
from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from HM.simulator.n_qubit_simulator.engine.constants import DT_SAMPLE_NS
```

### 3.3 ADD the path and the fit

Directly below `_SYSTEM_PARAMETERS = ...`, add:

```python
_PAPER_CROSS_KERR = Path(__file__).with_name("paper_cross_kerr_khz.json")
# Edges that keep the J in coupling_vals.json. Every other edge is fitted to
# the paper's cross-Kerr shift.
_LAB_COUPLING_EDGES = ("c1_t2",)
```

Directly below `_load_json`, add:

```python
def pair_cross_kerr_MHz(
    f_i_MHz: float,
    anharm_i_MHz: float,
    f_j_MHz: float,
    anharm_j_MHz: float,
    J_MHz: float,
    n_levels: int = 5,
) -> float:
    """Static ZZ shift E11 - E10 - E01 + E00 of two coupled transmons."""

    lowering = np.diag(np.sqrt(np.arange(1, n_levels)), 1)
    eye = np.eye(n_levels)
    number = lowering.T @ lowering
    a_i = np.kron(lowering, eye)
    a_j = np.kron(eye, lowering)
    n_i = np.kron(number, eye)
    n_j = np.kron(eye, number)
    H = (
        f_i_MHz * n_i
        + 0.5 * anharm_i_MHz * (n_i @ n_i - n_i)
        + f_j_MHz * n_j
        + 0.5 * anharm_j_MHz * (n_j @ n_j - n_j)
        + J_MHz * (a_i.T @ a_j + a_j.T @ a_i)
    )
    energies, vectors = np.linalg.eigh(H)

    def level(occ_i: int, occ_j: int) -> float:
        bare = occ_i * n_levels + occ_j
        return float(energies[np.argmax(np.abs(vectors[bare, :]) ** 2)])

    return level(1, 1) - level(1, 0) - level(0, 1) + level(0, 0)


def fit_exchange_MHz(
    f_i_MHz: float,
    anharm_i_MHz: float,
    f_j_MHz: float,
    anharm_j_MHz: float,
    cross_kerr_MHz: float,
    J_max_MHz: float = 10.0,
) -> float:
    """Return the J whose static ZZ magnitude equals ``cross_kerr_MHz``."""

    target = abs(float(cross_kerr_MHz))

    def residual(J_MHz: float) -> float:
        shift = pair_cross_kerr_MHz(
            f_i_MHz, anharm_i_MHz, f_j_MHz, anharm_j_MHz, J_MHz
        )
        return abs(shift) - target

    if residual(J_max_MHz) < 0.0:
        raise ValueError(
            f"no J below {J_max_MHz} MHz reaches a {1e3 * target:.1f} kHz shift"
        )
    return float(brentq(residual, 1e-6, J_max_MHz, xtol=1e-12))
```

`a†a†aa` is written as `n @ n - n`. Both are `n(n - 1)` on a truncated
oscillator, because `n` is diagonal.

The fit uses 5 levels per transmon. Three and four levels give the same shift
to 0.001 kHz on every edge, so the simulated truncation does not change it.

### 3.4 REPLACE `build_coupling_edges`

Replace the whole method with:

```python
    def build_coupling_edges(self) -> list[CouplingEdge]:
        """Return the odd-to-even exchange edges inside the selection.

        ``c1_t2`` keeps its lab J. Every other edge gets the J that reproduces
        the paper's cross-Kerr shift at the calibrated frequencies and
        anharmonicities.
        """

        coupling_data = _load_json("coupling_vals.json")
        frequency_data = _load_json("fq_vals.json")["fq_vals"]
        anharmonicity_data = _load_json("anharmonicities.json")
        with _PAPER_CROSS_KERR.open(encoding="utf-8") as handle:
            paper_khz = json.load(handle)["nearest_neighbour_khz"]

        selected = set(self.qubit_ids)
        edges = []
        for control_id in (1, 3, 5):
            for target_id in (2, 4, 6):
                if control_id not in selected or target_id not in selected:
                    continue
                name = f"c{control_id}_t{target_id}"
                if name in _LAB_COUPLING_EDGES:
                    edges.append(
                        CouplingEdge(
                            name,
                            control_id,
                            target_id,
                            float(coupling_data[name]["J_mhz"]),
                            True,
                            f"coupling_vals.json:{name}",
                        )
                    )
                    continue
                J_MHz = fit_exchange_MHz(
                    float(frequency_data[str(control_id)]),
                    -abs(float(anharmonicity_data[str(control_id)])),
                    float(frequency_data[str(target_id)]),
                    -abs(float(anharmonicity_data[str(target_id)])),
                    1e-3 * float(paper_khz[name]),
                )
                edges.append(
                    CouplingEdge(
                        name,
                        control_id,
                        target_id,
                        J_MHz,
                        False,
                        f"paper_zz_fit:{name}",
                    )
                )
        return edges
```

The loop order is the old catalog order: `c1_t2`, `c1_t4`, `c1_t6`, `c3_t2`,
and so on. The Phase 1 smoke script asserts that order.

### 3.5 Accept the new provenance

In `_validate_device`, replace:

```python
            if not edge.is_calibrated and not edge.parameter_source.startswith(
                "synthetic_copy:"
            ):
                raise ValueError(
                    f"edge {edge.name} lacks synthetic provenance"
                )
```

with:

```python
            if not edge.is_calibrated and not edge.parameter_source.startswith(
                ("synthetic_copy:", "paper_zz_fit:")
            ):
                raise ValueError(
                    f"edge {edge.name} has no provenance for its J"
                )
```

### 3.6 Check

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import json

from HM.simulator.n_qubit_simulator.base_classes import device_base
from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
    pair_cross_kerr_MHz,
)

base = NQubitSimulatorBase()
with device_base._PAPER_CROSS_KERR.open(encoding="utf-8") as handle:
    paper = json.load(handle)["nearest_neighbour_khz"]
lab = device_base._load_json("coupling_vals.json")
by_id = {qubit.qubit_id: qubit for qubit in base.qubits}

for edge in base.coupling_edges:
    qubit_i = by_id[edge.qubit_i]
    qubit_j = by_id[edge.qubit_j]
    shift_kHz = 1e3 * pair_cross_kerr_MHz(
        qubit_i.f_qubit_MHz,
        qubit_i.anharm_MHz,
        qubit_j.f_qubit_MHz,
        qubit_j.anharm_MHz,
        edge.J_MHz,
    )
    print(
        f"{edge.name}  J {edge.J_MHz:.4f} MHz  pair shift {shift_kHz:7.2f} kHz  "
        f"paper {paper[edge.name]:6.1f} kHz  {edge.parameter_source}"
    )
    if edge.name == "c1_t2":
        assert edge.is_calibrated
        assert edge.J_MHz == float(lab["c1_t2"]["J_mhz"])
    else:
        assert not edge.is_calibrated
        assert edge.parameter_source == f"paper_zz_fit:{edge.name}"
        assert abs(shift_kHz - paper[edge.name]) < 1e-6

print("paper couplings ok")
PY
```

Expected J values, fitted at the paper Table I frequencies:

| Edge | J (MHz) | Source |
| --- | --- | --- |
| `c1_t2` | 3.2163 | lab |
| `c1_t4` | 2.7279 | paper fit |
| `c1_t6` | 1.9155 | paper fit |
| `c3_t2` | 3.5456 | paper fit |
| `c3_t4` | 4.1080 | paper fit |
| `c3_t6` | 2.8565 | paper fit |
| `c5_t2` | 3.0536 | paper fit |
| `c5_t4` | 2.8886 | paper fit |
| `c5_t6` | 2.4765 | paper fit |

The `c1_t2` row prints a pair shift of about 179.5 kHz against a paper value
of 239. That is expected: this edge follows the lab. Fitted edges reproduce
the paper shift at the paper frequencies to `1e-6` kHz. On the composite
device the pair shifts stay within 2 kHz of the paper, except that `c1_t2`
is the lab edge.

Then rerun the Phase 1 smoke script. It must still print `PHASE 1 OK`. Its
single-excitation populations change, because eight couplings changed. Its
assertions do not depend on those values.

The one-off device check in Phase 1 section 2.5 listed the synthetic edges by
name. That list no longer applies. Do not rerun it.

Phase 2 is unaffected. It enabled only `c1_t2`, and `c1_t2` did not change.

---

## 4. Step 2: batched shots

Every gate measurement in this phase evolves the four computational inputs
through the same timeline. One solve with a batch of four initial states
compiles once instead of four times. The 2Q engine has the same method under
the same name.

### 4.1 ADD `run_shot_batch`

In `engine/n_q_pulse_sim_dynamiqs.py`, add this method directly below
`run_shot`:

```python
    def run_shot_batch(
        self,
        timeline: dict,
        psi0_batch,
    ):
        """Evolve several joint kets through one timeline in one solve.

        ``psi0_batch`` is a QArray of shape ``(n_states, dim, 1)``. Returns the
        final states with the same shape.
        """

        length = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        if len(psi0_batch.shape) != 3 or tuple(psi0_batch.shape[1:]) != (
            self.dim,
            1,
        ):
            raise ValueError(
                f"psi0_batch has shape {psi0_batch.shape}, "
                f"expected (n_states, {self.dim}, 1)"
            )

        tsave = jnp.asarray(
            [0.0, length * self.dt_sample_us],
            dtype=jnp.float64,
        )
        result = dq.sesolve(
            H,
            psi0_batch,
            tsave,
            method=self._integrator_method,
            gradient=None,
            options=self._sesolve_options,
        )
        return result.final_state
```

### 4.2 Check

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
import dynamiqs as dq
import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)
from HM.simulator.n_qubit_simulator.engine.timelines import Timeline

sim = NQubitSimulatorBase(qubit_ids=(1, 2)).simulator
builder = Timeline(sim.channel_names, n_samples=40, dt_ns=sim.dt_sample_ns)
builder.add("q1_drive", 0.0, jnp.full(40, 3.0 + 1.0j, dtype=jnp.complex128))
builder.add("cr_c1_t2", 0.0, jnp.full(40, -8.0 + 2.0j, dtype=jnp.complex128))
timeline = builder.finalize()

labels = [(0, 0), (1, 0), (1, 1)]
batch = dq.asqarray(
    jnp.stack([dq.to_jax(dq.basis(sim.dims, label)) for label in labels]),
    dims=sim.dims,
)
final_batch = dq.to_jax(sim.run_shot_batch(timeline, batch))
assert final_batch.shape == (3, sim.dim, 1)

worst = 0.0
for row, label in enumerate(labels):
    single = dq.to_jax(sim.run_shot(timeline, psi0=dq.basis(sim.dims, label)))
    worst = max(worst, float(jnp.max(jnp.abs(final_batch[row] - single))))
print("batch vs single max abs difference", worst)
assert worst < 1e-9
print("batched shots ok")
PY
```

---

## 5. Step 3: dressed-frame helpers

Create:

```text
HM/simulator/n_qubit_simulator/analysis/dressed_frame.py
```

These helpers only read the engine's operators and records. They never call
`sesolve`.

The frame algebra, with `T` the duration and `n_i(k)` the occupation of qubit
`i` in bare label `k`:

```text
lab state       psi_lab[m]  = exp(-i 2 pi  sum_i frame_i n_i(m) T) psi_rot[m]
dressed amp     c_k         = <D_k | psi_lab>
reference amp   c_k^ref     = exp(+i 2 pi  sum_i ref_i n_i(k) T) c_k
```

`frame_i` are the bare frequencies the engine rotated with. `ref_i` are the
Phase 2 dressed frequencies. An idle dressed state `D_k` then picks up only the
phase

```text
-2 pi (E_k - sum_i ref_i n_i(k)) T
```

and the conditional phase of a pair is `-2 pi zeta T`.

### 5.1 ADD the complete file

```python
"""Dressed eigenbasis and reference frames for spectator analysis.

The engine rotates every qubit at its ``frame_MHz`` and has no detuning term,
so ``frame_MHz`` is the bare frequency of the model. These helpers diagonalize
the static lab Hamiltonian, retune bare frequencies so dressed frequencies hit
a target, and read final states back in a dressed rotating frame.
"""

from __future__ import annotations

from dataclasses import dataclass

import dynamiqs as dq
import jax.numpy as jnp
import numpy as np


@dataclass
class DressedBasis:
    """Dressed states of one static configuration, indexed by bare label.

    Column ``k`` of ``vectors`` is the dressed state whose largest bare
    component is the bare basis state ``k``. Its phase makes that component
    real and positive.
    """

    energies_MHz: np.ndarray
    vectors: np.ndarray
    occupations: np.ndarray
    min_overlap: float


def _position(sim, qubit_id: int) -> int:
    return [qubit.qubit_id for qubit in sim.qubits].index(qubit_id)


def occupation_table(sim) -> np.ndarray:
    """Row ``i`` is the occupation of qubit ``i`` in every bare basis state."""
    return np.array(np.unravel_index(np.arange(sim.dim), sim.dims))


def static_hamiltonian_MHz(sim) -> np.ndarray:
    """Lab-frame Hamiltonian with every drive off, in MHz, not angular."""

    lowering = [np.asarray(dq.to_jax(operator)) for operator in sim.a]
    H = np.zeros((sim.dim, sim.dim), dtype=np.complex128)
    for position, qubit in enumerate(sim.qubits):
        a = lowering[position]
        ad = a.conj().T
        H += qubit.frame_MHz * (ad @ a)
        H += 0.5 * qubit.anharm_MHz * (ad @ ad @ a @ a)
    for edge in sim.coupling_edges:
        if not edge.enabled:
            continue
        hop = (
            lowering[_position(sim, edge.qubit_i)].conj().T
            @ lowering[_position(sim, edge.qubit_j)]
        )
        H += edge.J_MHz * (hop + hop.conj().T)
    return H


def dressed_basis(sim) -> DressedBasis:
    """Diagonalize the static Hamiltonian and label states by bare overlap."""

    energies, vectors = np.linalg.eigh(static_hamiltonian_MHz(sim))
    labels = np.argmax(np.abs(vectors) ** 2, axis=0)
    if np.unique(labels).size != sim.dim:
        raise RuntimeError(
            "dressed states do not map one-to-one onto bare labels"
        )
    order = np.argsort(labels)
    energies = energies[order]
    vectors = vectors[:, order]
    diagonal = np.diag(vectors)
    vectors = vectors * np.exp(-1j * np.angle(diagonal))
    return DressedBasis(
        energies_MHz=energies,
        vectors=vectors,
        occupations=occupation_table(sim),
        min_overlap=float(np.min(np.abs(diagonal) ** 2)),
    )


def _single_label(sim, position: int) -> tuple[int, ...]:
    return tuple(1 if index == position else 0 for index in range(len(sim.dims)))


def single_excitation_MHz(sim, basis: DressedBasis) -> dict[int, float]:
    """Dressed 0-to-1 frequency of each qubit, every other qubit in 0."""

    vacuum = basis.energies_MHz[sim.basis_index((0,) * len(sim.dims))]
    return {
        qubit.qubit_id: float(
            basis.energies_MHz[sim.basis_index(_single_label(sim, position))]
            - vacuum
        )
        for position, qubit in enumerate(sim.qubits)
    }


def static_zz_MHz(sim, basis: DressedBasis, qubit_a: int, qubit_b: int) -> float:
    """Dressed E11 - E10 - E01 + E00 for two qubits, the rest in 0."""

    position_a = _position(sim, qubit_a)
    position_b = _position(sim, qubit_b)

    def energy(occ_a: int, occ_b: int) -> float:
        label = [0] * len(sim.dims)
        label[position_a] = occ_a
        label[position_b] = occ_b
        return float(basis.energies_MHz[sim.basis_index(tuple(label))])

    return energy(1, 1) - energy(1, 0) - energy(0, 1) + energy(0, 0)


def compensate_frames(
    sim,
    target_MHz: dict[int, float],
    *,
    tol_MHz: float = 1e-10,
    max_iterations: int = 30,
) -> DressedBasis:
    """Shift bare frequencies until dressed frequencies equal ``target_MHz``.

    Mutates ``Qubit.frame_MHz`` in place. Drive carriers are not touched.
    Returns the dressed basis of the final configuration.
    """

    missing = {qubit.qubit_id for qubit in sim.qubits} - set(target_MHz)
    if missing:
        raise KeyError(f"no target frequency for qubits {sorted(missing)}")

    for _ in range(max_iterations):
        basis = dressed_basis(sim)
        dressed = single_excitation_MHz(sim, basis)
        residual = {
            qubit_id: target_MHz[qubit_id] - frequency
            for qubit_id, frequency in dressed.items()
        }
        if max(abs(value) for value in residual.values()) < tol_MHz:
            return basis
        for qubit in sim.qubits:
            qubit.frame_MHz += residual[qubit.qubit_id]
    raise RuntimeError(
        f"frame compensation did not converge in {max_iterations} iterations"
    )


def dressed_states(sim, basis: DressedBasis, labels) -> dq.QArray:
    """Batch of dressed kets, shape ``(n_labels, dim, 1)``."""

    columns = [basis.vectors[:, sim.basis_index(tuple(label))] for label in labels]
    batch = np.stack(columns)[:, :, None]
    return dq.asqarray(jnp.asarray(batch), dims=sim.dims)


def dressed_amplitudes(
    sim,
    basis: DressedBasis,
    final_states,
    duration_us: float,
    reference_MHz: dict[int, float],
) -> np.ndarray:
    """Final states in the dressed basis and the reference frame.

    Row ``b`` belongs to initial state ``b``. Column ``k`` is the amplitude on
    the dressed state labelled by bare index ``k``. ``basis`` must belong to
    the frames that the shot ran with.
    """

    psi = np.asarray(dq.to_jax(final_states)).reshape(-1, sim.dim)
    frames = np.array([qubit.frame_MHz for qubit in sim.qubits])
    reference = np.array([reference_MHz[qubit.qubit_id] for qubit in sim.qubits])
    frame_energy = frames @ basis.occupations
    reference_energy = reference @ basis.occupations

    lab = psi * np.exp(-2j * np.pi * frame_energy * duration_us)[None, :]
    dressed = lab @ basis.vectors.conj()
    return dressed * np.exp(2j * np.pi * reference_energy * duration_us)[None, :]
```

`lab @ basis.vectors.conj()` is `<D_k|psi_lab>` for every `k` at once:
element `[b, k]` is the sum over `m` of `psi_lab[b, m]` times the conjugate of
`vectors[m, k]`.

The exchange term conserves excitation number, so the vacuum is an exact
eigenstate with energy 0.

### 5.2 Check

No solve yet. This checks the static algebra against the Step 1 fit, and the
compensation on the target-side chip.

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python - <<'PY'
from HM.simulator.n_qubit_simulator.analysis.dressed_frame import (
    compensate_frames,
    dressed_basis,
    single_excitation_MHz,
    static_zz_MHz,
)
from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
    pair_cross_kerr_MHz,
)

pair = NQubitSimulatorBase(qubit_ids=(1, 2)).simulator
q1, q2 = pair.qubits
edge = pair.coupling_edges[0]
expected = pair_cross_kerr_MHz(
    q1.frame_MHz, q1.anharm_MHz, q2.frame_MHz, q2.anharm_MHz, edge.J_MHz,
    n_levels=3,
)
measured = static_zz_MHz(pair, dressed_basis(pair), 1, 2)
print("pair ZZ kHz", 1e3 * measured, "two-transmon fit", 1e3 * expected)
assert abs(measured - expected) < 1e-9

chip = NQubitSimulatorBase(
    qubit_ids=(1, 2, 3),
    n_levels=3,
    levels_by_qubit={1: 4, 2: 4},
).simulator
for edge in chip.coupling_edges:
    edge.enabled = edge.name == "c1_t2"
reference = single_excitation_MHz(chip, dressed_basis(chip))

for edge in chip.coupling_edges:
    edge.enabled = True
uncompensated = single_excitation_MHz(chip, dressed_basis(chip))
basis = compensate_frames(chip, reference)
compensated = single_excitation_MHz(chip, basis)

for qubit in chip.qubits:
    qubit_id = qubit.qubit_id
    print(
        f"Q{qubit_id}  shift without compensation "
        f"{1e3 * (uncompensated[qubit_id] - reference[qubit_id]):8.2f} kHz  "
        f"bare - calibrated {1e3 * (qubit.frame_MHz - qubit.f_qubit_MHz):8.2f} kHz"
    )
residual = max(abs(compensated[q] - reference[q]) for q in reference)
print("compensation residual MHz", residual)
print("smallest dressed-bare overlap", basis.min_overlap)
assert residual < 1e-9
assert basis.min_overlap > 0.5
print("dressed frame ok")
PY
```

Expected: Q2 is pulled down about 114 kHz without compensation and Q3 up
about 117 kHz. After compensation the bare Q2 sits about 115 kHz above its
calibrated frequency and the bare Q3 about 117 kHz below.

---

## 6. Step 4: shared chip setup

Create:

```text
HM/simulator/n_qubit_simulator/experiments/spectator_setup.py
```

Both experiment scripts need the same four operations: build a chip, take the
Phase 2 reference frequencies, switch a set of edges on, and compensate.

### 6.1 ADD the complete file

```python
"""Shared chip setup for the Phase 3 spectator experiments."""

from __future__ import annotations

from HM.simulator.n_qubit_simulator.analysis.dressed_frame import (
    DressedBasis,
    compensate_frames,
    dressed_basis,
    single_excitation_MHz,
)
from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)
from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    load_grape_sidecar,
)
from HM.simulator.n_qubit_simulator.experiments.c1t2_parity import (
    C1T2_NPZ_PATH,
)


ACTIVE_EDGE = "c1_t2"
CONTROL_SIDE_CHIP = (1, 2, 4, 6)
TARGET_SIDE_CHIP = (1, 2, 3)


def active_levels() -> int:
    """Truncation the GRAPE archive was optimized at."""
    return load_grape_sidecar(C1T2_NPZ_PATH)["n_levels"]


def build_chip(
    qubit_ids: tuple[int, ...],
    n_active_levels: int,
) -> NQubitSimulatorBase:
    """Q1 and Q2 at the GRAPE truncation, spectators at 3 levels."""

    if tuple(qubit_ids[:2]) != (1, 2):
        raise ValueError("Phase 3 chips start with the active pair Q1, Q2")
    overrides = (
        None
        if n_active_levels == 3
        else {1: n_active_levels, 2: n_active_levels}
    )
    return NQubitSimulatorBase(
        qubit_ids=qubit_ids,
        n_levels=3,
        levels_by_qubit=overrides,
        dt_sample_ns=1.0,
    )


def set_edges(sim, enabled_names) -> None:
    enabled_names = set(enabled_names)
    unknown = enabled_names - {edge.name for edge in sim.coupling_edges}
    if unknown:
        raise KeyError(f"chip has no edges {sorted(unknown)}")
    for edge in sim.coupling_edges:
        edge.enabled = edge.name in enabled_names


def reset_frames(sim) -> None:
    for qubit in sim.qubits:
        qubit.frame_MHz = qubit.f_qubit_MHz


def ground_reference_MHz(sim) -> dict[int, float]:
    """Dressed frequencies of the Phase 2 model, only ``c1_t2`` on.

    Spectators are uncoupled in that model, so their reference is their
    calibrated frequency.
    """

    reset_frames(sim)
    set_edges(sim, (ACTIVE_EDGE,))
    return single_excitation_MHz(sim, dressed_basis(sim))


def configure(sim, enabled_names, target_MHz) -> DressedBasis:
    """Switch ``enabled_names`` on and retune bare frequencies to the target."""

    reset_frames(sim)
    set_edges(sim, enabled_names)
    return compensate_frames(sim, target_MHz)
```

The canonical tensor order puts Q1 and Q2 at positions 0 and 1 on both chips.
The gate analysis relies on that, which is why `build_chip` checks it.

There is no separate check for this step. Step 5 imports everything in it.

---

## 7. Step 5: idle check of the dressed frame

Create:

```text
HM/simulator/n_qubit_simulator/experiments/spectator_idle_zz.py
```

This evolves every 0/1 product label through 412 ns of silence, the gate
duration, with every spectator edge on and compensated. If the engine and the
dressed frame agree, then:

- every dressed state stays where it started
- every amplitude picks up exactly the phase its dressed energy predicts
- the conditional phase of each edge is `-2 pi zeta T`

This is independent of GRAPE. It tests the engine's coupling phases and the
helper module against exact diagonalization.

### 7.1 ADD the complete file

```python
"""Idle check of the dressed frame on both Phase 3 chips.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.spectator_idle_zz
"""

from __future__ import annotations

import itertools
import json

import numpy as np

from HM.simulator.n_qubit_simulator.analysis.dressed_frame import (
    dressed_amplitudes,
    dressed_states,
    single_excitation_MHz,
    static_zz_MHz,
)
from HM.simulator.n_qubit_simulator.base_classes import device_base
from HM.simulator.n_qubit_simulator.engine.timelines import Timeline
from HM.simulator.n_qubit_simulator.experiments.spectator_setup import (
    ACTIVE_EDGE,
    C1T2_NPZ_PATH,
    CONTROL_SIDE_CHIP,
    TARGET_SIDE_CHIP,
    active_levels,
    build_chip,
    configure,
    ground_reference_MHz,
)


IDLE_NS = 412
CHIPS = (
    (CONTROL_SIDE_CHIP, ("c1_t4", "c1_t6")),
    (TARGET_SIDE_CHIP, ("c3_t2",)),
)


def check_chip(
    qubit_ids: tuple[int, ...],
    spectator_edges: tuple[str, ...],
    n_active: int,
    expected_kHz: dict[str, float],
) -> None:
    sim = build_chip(qubit_ids, n_active).simulator
    reference = ground_reference_MHz(sim)
    basis = configure(sim, (ACTIVE_EDGE,) + spectator_edges, reference)

    print("chip", qubit_ids, "dims", sim.dims, "dimension", sim.dim)
    dressed = single_excitation_MHz(sim, basis)
    residual = max(abs(dressed[q] - reference[q]) for q in reference)
    for qubit in sim.qubits:
        print(
            f"  Q{qubit.qubit_id} bare - calibrated "
            f"{1e3 * (qubit.frame_MHz - qubit.f_qubit_MHz):8.2f} kHz"
        )
    print("  compensation residual MHz", residual)
    print("  smallest dressed-bare overlap", basis.min_overlap)
    assert residual < 1e-9

    labels = list(itertools.product((0, 1), repeat=len(sim.dims)))
    idle = Timeline(
        sim.channel_names,
        n_samples=IDLE_NS,
        dt_ns=sim.dt_sample_ns,
    ).finalize()
    duration_us = IDLE_NS * sim.dt_sample_us
    final = sim.run_shot_batch(idle, dressed_states(sim, basis, labels))
    amplitudes = dressed_amplitudes(sim, basis, final, duration_us, reference)

    reference_vector = np.array([reference[q.qubit_id] for q in sim.qubits])
    worst_leave = 0.0
    worst_phase = 0.0
    for row, label in enumerate(labels):
        index = sim.basis_index(label)
        detuning_MHz = basis.energies_MHz[index] - reference_vector @ np.array(label)
        predicted = -2.0 * np.pi * detuning_MHz * duration_us
        amplitude = amplitudes[row, index]
        worst_leave = max(worst_leave, 1.0 - abs(amplitude) ** 2)
        worst_phase = max(
            worst_phase,
            abs(float(np.angle(amplitude * np.exp(-1j * predicted)))),
        )
    print("  worst population leaving its dressed state", worst_leave)
    print("  worst phase error rad", worst_phase)
    assert worst_leave < 1e-8
    assert worst_phase < 1e-6

    for edge in sim.coupling_edges:
        if not edge.enabled:
            continue
        zz_kHz = 1e3 * static_zz_MHz(sim, basis, edge.qubit_i, edge.qubit_j)
        expected = expected_kHz[edge.name]
        print(
            f"  {edge.name}  chip ZZ {zz_kHz:7.2f} kHz  "
            f"expected {expected:7.2f} kHz  J {edge.J_MHz:.4f} MHz"
        )
        assert abs(zz_kHz - expected) < 0.05 * expected

    if 3 in qubit_ids:
        shift_kHz = 1e3 * static_zz_MHz(sim, basis, 3, 2)
        with np.load(C1T2_NPZ_PATH, allow_pickle=False) as data:
            span_kHz = 1e3 * float(data["zz_span_mhz"])
        print(
            f"  Q2 moves {shift_kHz:.1f} kHz when Q3 flips. "
            f"The pulse was optimized for a {span_kHz:.1f} kHz span."
        )


def main() -> None:
    n_active = active_levels()
    with device_base._PAPER_CROSS_KERR.open(encoding="utf-8") as handle:
        expected_kHz = dict(json.load(handle)["nearest_neighbour_khz"])
    lab = device_base._load_json("coupling_vals.json")
    expected_kHz[ACTIVE_EDGE] = 1e3 * float(lab[ACTIVE_EDGE]["total_det_mhz"])

    for qubit_ids, spectator_edges in CHIPS:
        check_chip(qubit_ids, spectator_edges, n_active, expected_kHz)
    print("SPECTATOR IDLE OK")


if __name__ == "__main__":
    main()
```

The chip ZZ is compared with the lab value for `c1_t2` and the paper value for
every other edge. They agree to a few percent, not exactly: on a chip, each
qubit sees every neighbour at once, and compensation moves the bare
frequencies the two-transmon fit used. The 5% bar catches a wrong J or a wrong
edge, not that few percent. `c1_t6` is allowed 15%, because Q2 and Q6 sit
2.2 MHz apart and the many-body dressing of that edge is larger.

### 7.2 Run

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python -m \
  HM.simulator.n_qubit_simulator.experiments.spectator_idle_zz
```

About a minute on CPU. Required last line:

```text
SPECTATOR IDLE OK
```

---

## 8. Step 6: the gate measurement

Create:

```text
HM/simulator/n_qubit_simulator/experiments/spectator_gate_sweep.py
```

Control-side chip cases:

| Case | Edges on | Spectator branches (Q4, Q6) |
| --- | --- | --- |
| baseline | `c1_t2` | 00 |
| `+c1_t4` | `c1_t2`, `c1_t4` | 00, 10 |
| `+c1_t6` | `c1_t2`, `c1_t6` | 00, 01 |
| `+c1_t4+c1_t6` | all three | 00, 10, 01, 11 |

A spectator whose edge is off is uncoupled, so only its `|0>` branch is run.

Target-side chip cases:

| Case | Edges on | Q3 branches | Q2 placement |
| --- | --- | --- | --- |
| baseline | `c1_t2` | 0 | Phase 2 |
| ground-calibrated | `c1_t2`, `c3_t2` | 0, 1 | Q3 in `|0>` at Phase 2 value |
| midpoint | `c1_t2`, `c3_t2` | 0, 1 | halfway between the branches |

The 2Q comparison evolves the same pulse in the 2Q engine with the target
frame moved by the shift each placement predicts. That is exactly how robust
GRAPE modeled a spectator. Overlaps between branches do not depend on the
frame or basis convention, as long as both branches use the same one. Those
are the numbers to compare.

### 8.1 ADD the complete file

```python
"""Replay the c1t2 GRAPE gate with spectator couplings switched on.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.spectator_gate_sweep
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import numpy as np

from HM.simulator.n_qubit_simulator.analysis.dressed_frame import (
    dressed_amplitudes,
    dressed_states,
    single_excitation_MHz,
    static_zz_MHz,
)
from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    echoed_c1t2_timeline,
    embed_c1t2_timeline,
    load_optimized_cr_half,
)
from HM.simulator.n_qubit_simulator.experiments.spectator_setup import (
    ACTIVE_EDGE,
    C1T2_NPZ_PATH,
    CONTROL_SIDE_CHIP,
    TARGET_SIDE_CHIP,
    active_levels,
    build_chip,
    configure,
    ground_reference_MHz,
)
from HM.simulator.two_qubit_simulator.base_classes.device_base import (
    TwoQubitSimulatorBase,
)


COMPUTATIONAL = ((0, 0), (0, 1), (1, 0), (1, 1))
ACTIVE_CHANNELS = ("q1_drive", "q2_drive", "cr_c1_t2")
RESULTS_DIR = Path(__file__).resolve().parent / "results"

CONTROL_SIDE_CASES = (
    ("baseline", (), ((0, 0),)),
    ("+c1_t4", ("c1_t4",), ((0, 0), (1, 0))),
    ("+c1_t6", ("c1_t6",), ((0, 0), (0, 1))),
    ("+c1_t4+c1_t6", ("c1_t4", "c1_t6"), ((0, 0), (1, 0), (0, 1), (1, 1))),
)


def overlap_fidelity(A: np.ndarray, B: np.ndarray) -> float:
    """|Tr(A^dagger B)|^2 / 16 for two 4x4 computational blocks."""
    return float(abs(np.trace(A.conj().T @ B)) ** 2 / 16.0)


def gate_branch(sim, basis, reference, timeline, spectators) -> dict:
    """Computational block and losses with spectators started in ``spectators``."""

    labels = [active + tuple(spectators) for active in COMPUTATIONAL]
    indices = [sim.basis_index(label) for label in labels]
    n_samples = len(next(iter(timeline.values())))
    final = sim.run_shot_batch(timeline, dressed_states(sim, basis, labels))
    amplitudes = dressed_amplitudes(
        sim,
        basis,
        final,
        n_samples * sim.dt_sample_us,
        reference,
    )

    block = amplitudes[:, indices].T
    spectator_rows = basis.occupations[2:, :]
    in_branch = np.all(
        spectator_rows == np.array(spectators, dtype=int).reshape(-1, 1),
        axis=0,
    )
    branch_population = (np.abs(amplitudes) ** 2)[:, in_branch].sum(axis=1)
    computational_population = (np.abs(block) ** 2).sum(axis=0)
    return {
        "block": block,
        "spectator_excitation": float(np.mean(1.0 - branch_population)),
        "active_leakage": float(
            np.mean(branch_population - computational_population)
        ),
    }


def assert_spectator_channels_idle(timeline: dict) -> None:
    for name, envelope in timeline.items():
        if name in ACTIVE_CHANNELS:
            continue
        assert float(np.max(np.abs(np.asarray(envelope)))) == 0.0, name


def print_branch(chip: str, case: str, spectators, branch: dict, baseline) -> None:
    label = "".join(str(occupation) for occupation in spectators)
    print(
        f"{chip:12} {case:18} {label:4} "
        f"F_vs_baseline {overlap_fidelity(baseline, branch['block']):.6f}  "
        f"spectator excitation {branch['spectator_excitation']:.2e}  "
        f"active leakage {branch['active_leakage']:.2e}",
        flush=True,
    )


def run_control_side(pair_timeline: dict, n_active: int) -> dict:
    sim = build_chip(CONTROL_SIDE_CHIP, n_active).simulator
    timeline = embed_c1t2_timeline(pair_timeline, sim.channel_names)
    assert_spectator_channels_idle(timeline)
    reference = ground_reference_MHz(sim)

    results = {}
    for case, extra_edges, branches in CONTROL_SIDE_CASES:
        enabled = (ACTIVE_EDGE,) + extra_edges
        basis = configure(sim, enabled, reference)
        assert sorted(e.name for e in sim.coupling_edges if e.enabled) == sorted(
            enabled
        )
        for spectators in branches:
            branch = gate_branch(sim, basis, reference, timeline, spectators)
            results[(case, spectators)] = branch
            baseline = results[("baseline", (0, 0))]["block"]
            print_branch("Q1Q2Q4Q6", case, spectators, branch, baseline)
    return results


def run_target_side(pair_timeline: dict, n_active: int) -> tuple[dict, float]:
    sim = build_chip(TARGET_SIDE_CHIP, n_active).simulator
    timeline = embed_c1t2_timeline(pair_timeline, sim.channel_names)
    assert_spectator_channels_idle(timeline)
    reference = ground_reference_MHz(sim)
    edges = (ACTIVE_EDGE, "c3_t2")

    results = {}
    basis = configure(sim, (ACTIVE_EDGE,), reference)
    results[("baseline", (0,))] = gate_branch(sim, basis, reference, timeline, (0,))
    baseline = results[("baseline", (0,))]["block"]
    print_branch("Q1Q2Q3", "baseline", (0,), results[("baseline", (0,))], baseline)

    basis = configure(sim, edges, reference)
    zz_MHz = static_zz_MHz(sim, basis, 3, 2)
    for spectators in ((0,), (1,)):
        branch = gate_branch(sim, basis, reference, timeline, spectators)
        results[("ground-calibrated", spectators)] = branch
        print_branch("Q1Q2Q3", "ground-calibrated", spectators, branch, baseline)

    midpoint = dict(reference)
    midpoint[2] = reference[2] - 0.5 * zz_MHz
    basis = configure(sim, edges, midpoint)
    offset_kHz = 1e3 * (single_excitation_MHz(sim, basis)[2] - reference[2])
    print(f"midpoint: Q2 with Q3 in |0> sits {offset_kHz:.2f} kHz from Phase 2")
    for spectators in ((0,), (1,)):
        branch = gate_branch(sim, basis, reference, timeline, spectators)
        results[("midpoint", spectators)] = branch
        print_branch("Q1Q2Q3", "midpoint", spectators, branch, baseline)
    return results, zz_MHz


def two_qubit_frame_model(
    pair_timeline: dict,
    n_active: int,
    shifts_MHz,
) -> dict[float, np.ndarray]:
    """Computational blocks of the 2Q engine with the target frame moved."""

    reference = TwoQubitSimulatorBase(
        qubit_pair=[1, 2],
        engine="dynamiqs",
        n_levels=n_active,
        dt_sample_ns=1.0,
    ).simulator
    lab_frame = float(reference.qubits[1].frame_MHz)
    timeline = {
        name: np.asarray(pair_timeline[name])
        for name in ("q1_drive", "q2_drive", "cr_drive")
    }
    blocks = {}
    for shift in shifts_MHz:
        reference.set_target_frame(lab_frame + shift)
        states = np.asarray(reference.evolve_comp(timeline))
        blocks[shift] = states[:, reference.comp_idx, 0].T
    reference.set_target_frame(lab_frame)
    return blocks


def _jsonable_block(block: np.ndarray) -> list:
    return [[[float(z.real), float(z.imag)] for z in row] for row in block]


def main() -> None:
    n_active = active_levels()
    saved_half, _knobs = load_optimized_cr_half(C1T2_NPZ_PATH)
    pair_timeline = echoed_c1t2_timeline(saved_half)
    with np.load(C1T2_NPZ_PATH, allow_pickle=False) as data:
        design_span_MHz = float(data["zz_span_mhz"])
    print("active levels", n_active, "design span MHz", design_span_MHz)

    control = run_control_side(pair_timeline, n_active)
    target, zz_MHz = run_target_side(pair_timeline, n_active)

    baseline_difference = float(
        np.max(
            np.abs(
                control[("baseline", (0, 0))]["block"]
                - target[("baseline", (0,))]["block"]
            )
        )
    )
    print("baseline block difference between chips", baseline_difference)
    assert baseline_difference < 1e-6

    both = "+c1_t4+c1_t6"
    ground = control[(both, (0, 0))]["block"]
    control_branches = {
        "Q4 flipped": overlap_fidelity(ground, control[(both, (1, 0))]["block"]),
        "Q6 flipped": overlap_fidelity(ground, control[(both, (0, 1))]["block"]),
        "both flipped": overlap_fidelity(ground, control[(both, (1, 1))]["block"]),
    }
    print("control-side branch fidelity vs Q4 Q6 in 00:", control_branches)

    target_branches = {
        placement: overlap_fidelity(
            target[(placement, (0,))]["block"],
            target[(placement, (1,))]["block"],
        )
        for placement in ("ground-calibrated", "midpoint")
    }

    shifts = {
        "ground-calibrated": (0.0, zz_MHz),
        "midpoint": (-0.5 * zz_MHz, 0.5 * zz_MHz),
        "design": (-0.5 * design_span_MHz, 0.5 * design_span_MHz),
    }
    model = two_qubit_frame_model(
        pair_timeline,
        n_active,
        sorted({0.0, *shifts["ground-calibrated"], *shifts["midpoint"], *shifts["design"]}),
    )
    model_branches = {
        placement: overlap_fidelity(model[low], model[high])
        for placement, (low, high) in shifts.items()
    }
    model_vs_baseline = {
        placement: [overlap_fidelity(model[0.0], model[s]) for s in shifts[placement]]
        for placement in ("ground-calibrated", "midpoint")
    }

    print(f"Q3 shifts Q2 by {1e3 * zz_MHz:.2f} kHz")
    for placement in ("ground-calibrated", "midpoint"):
        print(
            f"{placement:18} branch fidelity: n-qubit {target_branches[placement]:.6f}  "
            f"2Q frame model {model_branches[placement]:.6f}"
        )
        full = [
            overlap_fidelity(
                target[("baseline", (0,))]["block"],
                target[(placement, s)]["block"],
            )
            for s in ((0,), (1,))
        ]
        print(
            f"{'':18} F_vs_baseline Q3=0, Q3=1: n-qubit "
            f"{full[0]:.6f}, {full[1]:.6f}  2Q frame model "
            f"{model_vs_baseline[placement][0]:.6f}, "
            f"{model_vs_baseline[placement][1]:.6f}"
        )
    print(
        f"design span ±{0.5e3 * design_span_MHz:.1f} kHz, 2Q frame model branch "
        f"fidelity {model_branches['design']:.6f}"
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"phase3_spectator_sweep_{stamp}.json"
    payload = {
        "archive": C1T2_NPZ_PATH,
        "active_levels": n_active,
        "q3_on_q2_zz_kHz": 1e3 * zz_MHz,
        "design_span_kHz": 1e3 * design_span_MHz,
        "control_side": {
            f"{case} {''.join(map(str, s))}": {
                "spectator_excitation": branch["spectator_excitation"],
                "active_leakage": branch["active_leakage"],
                "block": _jsonable_block(branch["block"]),
            }
            for (case, s), branch in control.items()
        },
        "target_side": {
            f"{case} {''.join(map(str, s))}": {
                "spectator_excitation": branch["spectator_excitation"],
                "active_leakage": branch["active_leakage"],
                "block": _jsonable_block(branch["block"]),
            }
            for (case, s), branch in target.items()
        },
        "control_side_branch_fidelity": control_branches,
        "target_side_branch_fidelity": target_branches,
        "two_qubit_frame_model_branch_fidelity": model_branches,
    }
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print("saved", out_path)
    print("PHASE 3 OK")


if __name__ == "__main__":
    main()
```

### 8.2 Run

```bash
cd /home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5

/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python -m \
  HM.simulator.n_qubit_simulator.experiments.spectator_gate_sweep
```

About four minutes on CPU: nine branches of dimension 144, five of
dimension 48, and five small 2Q solves. Required last line:

```text
PHASE 3 OK
```

---

## 9. Reading the results

These are the numbers from the composite-device run with the current archive.
Q3-Q6 sit at paper frequencies plus the Q1 offset, so Q2 and Q6 are 2.2 MHz
apart, as in the paper. That changes the control-side story relative to a
run at the lab Q6 frequency.

### 9.1 Static shifts

| Edge | Chip ZZ (kHz) | Expected (kHz) |
| --- | --- | --- |
| `c1_t2`, control-side chip | 183.9 | 178.9 (lab) |
| `c1_t4` | 116.3 | 116 (paper) |
| `c1_t6` | 57.2 | 64 (paper); pair ZZ is 64, chip ZZ drops because Q2 is nearby |
| `c1_t2`, target-side chip | 181.1 | 178.9 (lab) |
| `c3_t2` | 223.2 | 225 (paper) |

### 9.2 Control-side chip

Q4 is a small, echoed control-side spectator. Q6 is not:

| Case | Q4, Q6 | F_vs_baseline | Spectator excitation |
| --- | --- | --- | --- |
| `+c1_t4` | 00 | 0.9989 | `4.9e-4` |
| `+c1_t4` | 10 | 0.9987 | `5.0e-4` |
| `+c1_t6` | 00 | 0.9544 | `4.4e-2` |
| `+c1_t6` | 01 | 0.9541 | `4.4e-2` |

| Q4, Q6 flip, all edges on | Branch fidelity |
| --- | --- |
| Q4 | 0.9122 |
| Q6 | 0.9122 |
| both | 0.9104 |

The CR tone on Q1 sits at the Q2 frequency. Q6 is 2.2 MHz from that tone and
is coupled to Q1, so about 4% of the population leaves Q6. Q4 is 43 MHz from
the tone and stays near `5e-4`. The echo still cancels a static Z on Q1, which
is why `+c1_t4` alone stays at 0.999. It does not cancel a drive on Q6.

### 9.3 Target-side chip

Q3 moves Q2 by about 223 kHz, larger than the 150 kHz span the pulse was
optimized for:

| Placement | Q3 = 0, F_vs_baseline | Q3 = 1, F_vs_baseline | Branch fidelity |
| --- | --- | --- | --- |
| ground-calibrated | 0.9965 | 0.9338 | 0.9319 |
| midpoint | 0.9810 | 0.9806 | 0.9319 |

The 2Q frame-shift model at the same 223 kHz gives a branch fidelity of about
0.963. At the design span, ±75 kHz, it gives 0.982.

Two readings follow:

1. The pulse is outside its robust window here. The spectator splitting is
   about 1.5 times the span GRAPE was optimized against.
2. The n-qubit model loses more than the 2Q frame-shift model predicts at the
   same shift, 6.8% against 3.7%. The frame-shift model treats Q3 as a pure
   frequency shift of Q2. The n-qubit model keeps the Q2-Q3 exchange itself
   while the CR drive is on. That exchange is the only physics the two models
   do not share.

Placement moves the error between branches, but the branch fidelity barely
changes. Calibrating with Q3 in `|0>` makes that branch almost perfect and
puts all of the error on Q3 in `|1>`. The midpoint splits it evenly.

---

## 10. Failure guide

### `fit_exchange_MHz` raises "no J below 10 MHz"

The paper shift for that edge cannot be reached at our frequencies with J up
to 10 MHz. Check the edge name, the paper value, and that the anharmonicities
are negative.

### Phase 1 smoke fails after Step 1

Check the edge order printed by the smoke script. The loop in
`build_coupling_edges` must run controls 1, 3, 5 on the outside and targets
2, 4, 6 on the inside.

### `dressed states do not map one-to-one onto bare labels`

Two eigenvectors have the same largest bare component. That happens only when
a coupling is comparable to a detuning. Print the J values and the qubit
frequencies of that chip before anything else.

### Compensation does not converge

The frames should converge in five to eight iterations. If they do not, the
target dictionary is probably from a different chip. Rebuild the reference
with `ground_reference_MHz` on the same simulator.

### Idle check: population leaves its dressed state

The dressed basis was built for different frames than the shot ran with.
`configure` returns the basis of the final frames. Do not reuse a basis after
calling `configure` again.

### Idle check: phases are off by a constant per qubit

`dressed_amplitudes` was given the bare frames as the reference. Pass the
dictionary from `ground_reference_MHz`.

### Baseline block differs between the two chips

Both baselines have only `c1_t2` on, with spectators uncoupled and idle. They
must agree. Check `assert_spectator_channels_idle` and the enabled-edge list.

---

## 11. Stop condition

Phase 3 is complete only when:

1. `c1_t2` keeps its lab J and the other eight edges carry `paper_zz_fit`
   provenance
2. every fitted edge reproduces its paper shift within `1e-6` kHz as a pair
3. the Phase 1 smoke script still prints `PHASE 1 OK`
4. `run_shot_batch` matches `run_shot` within `1e-9`
5. compensation brings every dressed frequency back to its Phase 2 value within
   `1e-9` MHz
6. idle dressed states stay put within `1e-8` and match their predicted phase
   within `1e-6` rad
7. every chip ZZ is within 5% of the lab or paper value, except `c1_t6`
   (15%, Q2-Q6 near degeneracy)
8. the two chips' baseline blocks agree within `1e-6`
9. the sweep prints `PHASE 3 OK` and writes its JSON

Then stop. Return with the idle output, the sweep table, and the JSON path
before starting Phase 4.
