# Six-Qubit dynamiqs simulator overview

## Status

This is a planning document.

Read and revise this overview before using the Phase 0 and Phase 1
implementation guides. Those guides will be updated only after the
architecture in this document is approved.

---

## 1. Goal

Use two separate simulation layers:

1. The existing 2Q dynamiqs/JAX simulator optimizes CR pulses efficiently.
2. A new n-qubit dynamiqs/JAX simulator validates those pulses with explicit
   spectators and configurable connectivity.

The new package is a validator first. It does not replace the 2Q optimizer.

The data flow is:

```text
2Q CR optimizer
    |
    | optimized NPZ waveform
    v
6Q pulse embedding
    |
    | selected CR and echo channels
    v
global n-qubit timeline
    |
    v
frame-consistent Hamiltonian
    |
    v
dynamiqs sesolve
    |
    v
active-pair, spectator, leakage, and fidelity analysis
```

---

## 2. Relationship with the existing 2Q package

The new package should look and feel like the existing simulator:

```text
HM/simulator/two_qubit_simulator/
    base_classes/
        device_base.py
    engine/
        constants.py
        pulses.py
        two_q_pulse_sim_dynamiqs.py
    experiments/
    optimization/
```

The new structure is:

```text
HM/simulator/n_qubit_simulator/
    __init__.py
    base_classes/
        __init__.py
        device_base.py
    engine/
        __init__.py
        constants.py
        timelines.py
        pulses_jax.py
        n_q_pulse_sim_dynamiqs.py
        pulse_embedding.py
    experiments/
        __init__.py
        closed_system_smoke.py
        pair_validation.py
        spectator_state_sweep.py
        leakage_validation.py
    analysis/
        __init__.py
        metrics.py
    tests/
        __init__.py
    documentation/
        guides/
            SIX_QUBIT_DYNAMIQS_ROADMAP.md
            PHASE_0_SCAFFOLD_RUNTIME_AND_CONTRACTS.md
            PHASE_1_CLOSED_SYSTEM_ENGINE.md
```

The n-qubit package uses `analysis/` instead of `optimization/` because pulse
optimization remains in the 2Q package.

Do not generalize the 2Q classes in place. Keep the current 2Q optimizer and
its QuTiP reference path intact.

---

## 3. Main design principle

Mirror the 2Q architecture while generalizing only the assumptions that do not
work for multiple qubits.

The first version uses these principal types:

```text
Qubit
DriveLine
CouplingEdge
NQubitSimulatorBase
Timeline
NQubitPulseSimulatorDynamiqs
```

Do not introduce separate first-version classes for:

```text
DeviceSpec
FrameSet
OperatorSet
FinalStateResult
```

Operators, frames, Hamiltonian terms, dimensions, and solver options remain
attributes or methods of the simulator, matching the existing 2Q engine.

---

## 4. Core classes

### 4.1 `Qubit`

This follows the existing 2Q `Qubit` dataclass.

It stores:

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

The initial frame frequency equals the calibrated qubit frequency.

The object uses a physical qubit ID so selected subsets do not have to rename
Q4 as local qubit 2.

### 4.2 `DriveLine`

This follows the existing 2Q drive-line concept.

```python
@dataclass(frozen=True)
class DriveLine:
    name: str
    target_qubit_id: int
    carrier_MHz: float
```

`target_qubit_id` is the physical qubit on which the annihilation and creation
operators act.

For a self drive:

```text
q4_drive
physical target: Q4
carrier: Q4 frequency
```

For a CR drive:

```text
cr_c1_t2
physical target: Q1
carrier: Q2 frequency
```

### 4.3 `CouplingEdge`

The existing 2Q engine has only one scalar `J_MHz`. The n-qubit engine needs a
record for every connected pair:

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

`qubit_i` and `qubit_j` are neutral endpoint names. Exchange coupling is
undirected.

The label `c1_t2` records the calibration and CR orientation used by the
device configuration, but the exchange Hamiltonian connects Q1 and Q2
symmetrically.

### 4.4 `NQubitSimulatorBase`

This follows the role of `TwoQubitSimulatorBase`.

It:

- selects physical qubits
- loads qubit parameters
- assigns local level counts
- filters the coupling graph
- creates self and CR drive lines
- constructs `NQubitPulseSimulatorDynamiqs`
- exposes the engine and channel names to experiments

### 4.5 Timelines and pulse assembly

The dynamiqs path is the canon. Do not copy the QuTiP/NumPy grow-as-you-add
`Timeline` as the main n-qubit design.

Follow the 2Q JAX pattern:

- know the total length before assembly
- allocate fixed-shape complex128 arrays
- keep every selected channel present
- represent idle channels as explicit zeros
- finalize the timeline in the experiment layer

The engine consumes only a finished dictionary:

```python
timeline: dict[str, jnp.ndarray]
```

Experiments may either:

1. build that dictionary locally with n-qubit pulse helpers, or
2. load an optimized 2Q NPZ and embed it onto selected n-qubit channels

Either way, finalization happens before `run_shot`.

### 4.6 `NQubitPulseSimulatorDynamiqs`

This follows `TwoQubitPulseSimulatorDynamiqs`.

It owns:

```text
self.qubits
self.coupling_edges
self.drive_lines
self.channel_names
self.dims
self.dim
self.a
self.ad
self.H_drift
self._integrator_method
self._sesolve_options
```

The initial public API is:

```python
sim.hamiltonian(timeline)
sim.run_shot(timeline, psi0)
sim.measure_state_norm(state)
sim.basis_index(occupations)
```

No six-qubit full propagator is part of the initial API.

---

## 5. Three independent controls

The design has three separate controls.

### 5.1 Which qubits exist

`qubit_ids` selects the Hilbert-space factors when constructing the base:

```python
base = NQubitSimulatorBase(
    qubit_ids=(1, 2, 4, 6),
)
```

Excluded qubits:

- have no Hilbert-space factor
- have no local operators
- have no drift term
- have no coupling edges
- have no drive channels

Changing `qubit_ids` requires constructing a new base and engine.

### 5.2 Which couplings are active

Each retained edge has:

```python
edge.enabled = True
```

Setting:

```python
edge.enabled = False
```

omits that exchange term when the Hamiltonian is built.

The endpoint qubits remain in the Hilbert space. Their other couplings, drift,
and drive channels remain available.

This is useful for gradually enabling spectators:

```text
active pair only
active pair plus one spectator edge
active pair plus several spectator edges
full selected connectivity
```

### 5.3 Which drives are active

Every registered drive channel remains in the finalized timeline.

An idle line contains an explicit zero array. A line is active only when its
timeline envelope is nonzero.

Disabling a coupling edge does not remove or disable a drive line.

---

## 6. Qubit selection and ordering

### 6.1 Default selection

The default uses all six calibrated physical IDs:

```python
NQubitSimulatorBase()
```

This is equivalent to:

```python
NQubitSimulatorBase(
    qubit_ids=(1, 2, 3, 4, 5, 6),
)
```

### 6.2 Subset selection

Any nonempty subset of Q1 through Q6 may be selected:

```python
NQubitSimulatorBase(
    qubit_ids=(1, 2, 6, 4),
)
```

Subsystem order is canonicalized by ascending physical ID:

```text
requested: Q1, Q2, Q6, Q4
actual tensor order: Q1, Q2, Q4, Q6
```

Canonical ordering prevents basis indices from changing merely because a
caller listed the same qubits in a different order.

### 6.3 Example selected graph

For Q1, Q2, Q4, and Q6:

```text
qubit order:
    Q1, Q2, Q4, Q6

retained exchange edges:
    Q1-Q2
    Q1-Q4
    Q1-Q6

self-drive channels:
    q1_drive
    q2_drive
    q4_drive
    q6_drive

CR channels:
    cr_c1_t2
    cr_c1_t4
    cr_c1_t6
```

There are seven channels in this selected model.

### 6.4 Selection validation

Rules:

- selection cannot be empty
- duplicate IDs are rejected
- the initial physical catalog accepts only Q1 through Q6
- output order is ascending physical ID
- an edge is retained only if both endpoints are selected
- a CR line is retained only if its control and carrier-reference qubits are
  selected

---

## 7. Per-qubit level selection

### 7.1 Default level count

`n_levels` sets one default for every selected qubit:

```python
NQubitSimulatorBase(
    qubit_ids=(1, 2, 4, 6),
    n_levels=3,
)
```

This produces:

```text
Q1: 3
Q2: 3
Q4: 3
Q6: 3

dims = (3, 3, 3, 3)
```

### 7.2 Individual overrides

`levels_by_qubit` overrides the default for selected qubits:

```python
NQubitSimulatorBase(
    qubit_ids=(1, 2, 4, 6),
    n_levels=3,
    levels_by_qubit={
        1: 4,
        2: 4,
    },
)
```

This produces:

```text
canonical qubit order: Q1, Q2, Q4, Q6
dims: (4, 4, 3, 3)
dimension: 144
```

The active pair can therefore use four levels while spectators remain
qutrits.

### 7.3 Override rules

- `n_levels` must be an integer of at least 2
- every override value must be an integer of at least 2
- every override key must be present in `qubit_ids`
- unspecified selected qubits use `n_levels`
- dimensions follow canonical qubit order

The intended API is:

```python
NQubitSimulatorBase(
    qubit_ids=(1, 2, 3, 4, 5, 6),
    n_levels=3,
    levels_by_qubit=None,
)
```

---

## 8. Hilbert-space scaling

For selected local dimensions n_i,

```text
d = product over i of n_i
```

Important examples:

```text
six two-level qubits:
    dims = (2, 2, 2, 2, 2, 2)
    d = 64

six qutrits:
    dims = (3, 3, 3, 3, 3, 3)
    d = 729

two four-level active qubits plus four qutrit spectators:
    dims = (4, 4, 3, 3, 3, 3)
    d = 1296

six four-level transmons:
    dims = (4, 4, 4, 4, 4, 4)
    d = 4096
```

A state vector is not the main dense-memory problem. Embedded operators and
Hamiltonian matrices scale as d^2.

For six four-level transmons, one dense complex128 operator is approximately
256 MiB. The engine requires several local operators, coupling terms, drive
terms, and solver work buffers. This configuration creates substantial CPU and
GPU memory pressure.

The recommended order is:

1. begin with six qutrits
2. use selected subsets for debugging
3. use four levels only on the active pair when needed
4. attempt six four-level transmons only after profiling memory

---

## 9. Twelve-qubit boundary

The class and engine interfaces are n-qubit in structure, but the first
physical catalog contains only Q1 through Q6.

Adding 12 physical qubits would first require:

- frequencies for all 12
- anharmonicities for all 12
- a 12-qubit connectivity graph
- calibrated or explicitly synthetic coupling values
- self-drive and CR carrier definitions
- parameter provenance

The dense engine is also not practical for 12 qutrits:

```text
d = 3^12 = 531441
```

One dense complex128 operator would require approximately 4.5 TB. A GPU does
not remove this exponential growth.

A practical 12-qubit implementation would require a different computational
representation, such as:

- sparse local operators
- matrix-free Hamiltonian application
- symmetry-sector reduction
- tensor-network evolution

Twelve qutrits are therefore outside the scope of the first dense dynamiqs
engine.

---

## 10. Device parameters

### 10.1 Qubit calibration source

Load directly from:

```text
Configuration_Files/System_Parameters/fq_vals.json
Configuration_Files/System_Parameters/anharmonicities.json
```

Store anharmonicity as:

```python
anharm_MHz = -abs(source_value)
```

Keep source labels on each `Qubit`.

The current Q6 anharmonicity magnitude is unusually large and must remain
visible as a calibration-review item. Do not silently replace it.

### 10.2 Coupling graph

The full six-qubit catalog contains:

```text
c1_t2  c1_t4  c1_t6
c3_t2  c3_t4  c3_t6
c5_t2  c5_t4  c5_t6
```

From Phase 3 on, `c1_t2` keeps the measured J in `coupling_vals.json`. With
that J the model reproduces the lab's measured c1_t2 shift, 179.5 kHz against
178.9 kHz.

Every other edge, including `c1_t4` and `c3_t2`, takes its J from the paper's
cross-Kerr matrix in `base_classes/paper_cross_kerr_khz.json`. The device base
fits J at construction so that two coupled transmons, at the calibrated
frequencies and anharmonicities, reproduce the paper's shift. Those edges are
labeled:

```python
is_calibrated=False
parameter_source="paper_zz_fit:<edge name>"
```

The paper's matrix confirms the nine-edge graph: its nine large entries are
exactly the odd-to-even pairs, and every next-nearest pair is at most 9.7 kHz.

The stored lab J for `c1_t4` and `c3_t2` does not reproduce the ZZ measured on
those same edges (125.6 against 174.5 kHz, and 133.9 against 194.6 kHz). That
is one reason the paper is used for them.

Phases 1 and 2 used `synthetic_copy:c1_t2` for six edges. That label is still
accepted by the validator, but no edge uses it now.

### 10.3 Edge filtering

Build the full catalog first, then retain an edge only when both endpoint IDs
belong to the selected qubit set.

Do not invent a coupling between selected qubits merely because both are
present. Only declared graph edges are retained.

---

## 11. Rotating-frame contract

All selected qubits evolve as one joint state under one Hamiltonian.

Each `Qubit` owns one frame frequency:

```python
qubit.frame_MHz
```

Initially:

```python
qubit.frame_MHz = qubit.f_qubit_MHz
```

For exchange edge i,j:

```text
Δ_ij = ω_i - ω_j
```

The Hamiltonian term is:

```text
H_ij(t) = 2π J_ij [
    a_i† a_j exp(+i 2π Δ_ij t)
  + a_i a_j† exp(-i 2π Δ_ij t)
]
```

For a drive physically acting on qubit i:

```text
δ_l = f_carrier,l - ω_i
```

```text
H_l(t) = π [
    ε_l(t) exp(-i 2π δ_l t) a_i†
  + ε_l*(t) exp(+i 2π δ_l t) a_i
]
```

Do not store a separately mutable `delta_ij`. Derive every detuning from frames
and fixed carriers when building the Hamiltonian.

---

## 12. Timeline contract

A finalized timeline is:

```python
{
    "q1_drive": complex_jax_array,
    "q2_drive": complex_jax_array,
    "cr_c1_t2": complex_jax_array,
    # every other selected channel
}
```

Rules:

1. Every selected channel is present.
2. Every array has equal length.
3. Every array uses complex128 during validation.
4. Idle channels contain explicit zeros.
5. The complex envelope is I + iQ in MHz.
6. The initial validation grid is 1 ns.
7. Timeline shape is fixed before the engine sees it.
8. Experiments finalize timelines. The engine does not grow buffers.

The engine always adds every selected drive term, even when its envelope is
zero. This keeps the Hamiltonian structure fixed.

---

## 13. Solver and output policy

Use:

```python
dq.sesolve(...)
```

Do not use a full propagator for the initial six-qubit validation.

Default options:

```python
dq.Options(
    save_states=False,
    progress_meter=False,
)
```

The engine returns:

```python
result.final_state
```

Default policy:

- save final states
- save expectation values when time traces are needed
- do not save full state trajectories by default
- do not construct density matrices before the noise phase
- do not request full d x d propagators for ordinary validation

---

## 14. Package boundary with the 2Q optimizer

Keep this package unchanged:

```text
HM/simulator/two_qubit_simulator/
```

The new package must not import:

- `CRGrapeOptimizer`
- `RobustCRGrapeOptimizer`
- SciPy optimizer callbacks
- Optax optimizer state
- QuTiP simulator classes
- live 2Q pulse-assembly modules such as `pulses_jax.py`

### 14.1 Duplicate pulse assembly carefully

Do not make the 2Q package a live single source of truth for n-qubit pulse
code. Instead:

1. Copy the 2Q JAX CR-half and echoed-timeline assembly into
   `n_qubit_simulator/engine/pulses_jax.py`.
2. Adapt only channel naming for the selected n-qubit registry.
3. Keep the sequence math intentionally identical.
4. Prove identity with an equality test before physics comparisons.

The durable external bridge remains a saved NPZ waveform:

```text
2Q result NPZ
    -> n_qubit_simulator pulse load / reconstruct
    -> pulse_embedding onto selected channels
    -> finalized n-qubit timeline dict
    -> n-qubit engine
```

The bridge must preserve:

- sample spacing
- complex envelope units
- CR sign
- echo order
- active control and target IDs
- fixed carriers

Before comparing n-qubit and 2Q states, first assert that the reconstructed
channel samples match the trusted 2Q timeline sample-for-sample on the active
CR and echo channels.

---

## 15. Implementation phases

### Phase 0: scaffold and runtime bootstrap

Purpose:

- create the 2Q-aligned package directories
- add package marker files
- add `engine/constants.py`
- create the dynamiqs engine module
- configure x64 at engine-module import
- verify six-qutrit `dq.destroy(*dims)`

No classes or Hamiltonian yet.

Pass marker:

```text
PHASE 0 OK
```

### Phase 1: closed-system forward engine

Purpose:

- add `Qubit`, `DriveLine`, and `CouplingEdge`
- add selectable `qubit_ids`
- add default `n_levels` (Phase 1 keeps every selected qubit at this default)
- filter edges and drives to the selected subsystem
- add fixed-shape timeline helpers in the dynamiqs style
- build engine operators and Hamiltonian methods
- evolve one product state
- return only the final state

Required Phase 1 checks should cover:

- default six-qutrit model
- reordered subset input `(1, 2, 6, 4)`
- canonical subset order `(1, 2, 4, 6)`
- edge filtering
- channel filtering
- Hamiltonian Hermiticity
- coupling and drive phase signs
- state norm

Pass marker:

```text
PHASE 1 OK
```

### Phase 2: strict c1t2 parity

Detailed steps: `PHASE_2_C1T2_PARITY.md`.

Purpose:

- add `levels_by_qubit` overrides
- add n-qubit `pulses_jax.py` as a careful duplicate of the 2Q JAX assembler
- load one optimized c1t2 NPZ waveform and its sibling JSON
- reconstruct the echoed timeline locally
- equality-check active CR and echo samples against the trusted 2Q timeline
- replay that timeline on Q1 and Q2 only, at the sidecar truncation
- replay it again on Q1, Q2, Q4, Q6 with Q4 and Q6 in |0> and spectator edges off
- compare both final states with a lab-frame 2Q dynamiqs replay

The mixed-truncation constructor check is:

```python
NQubitSimulatorBase(
    qubit_ids=(1, 2, 4, 6),
    n_levels=3,
    levels_by_qubit={1: 4, 2: 4},
)
```

This gives order Q1, Q2, Q4, Q6, dims (4, 4, 3, 3), dimension 144.
That object is not the physics-parity chip unless the GRAPE sidecar itself
says `n_levels` is 4. The parity shot uses the sidecar truncation on Q1 and Q2.
Spectators stay at 3 levels.

On the spectator chip, disable every edge whose endpoints are not exactly
`{1, 2}`. For `qubit_ids=(1, 2, 4, 6)` that leaves `c1_t2` on and turns
`c1_t4` and `c1_t6` off. Do not enable those spectator edges until waveform
equality and both physics comparisons pass.

### Phase 3: incremental spectators

Detailed steps: `PHASE_3_SPECTATOR_EDGES.md`.

Two chips:

- control side, Q1, Q2, Q4, Q6: `c1_t4` alone, `c1_t6` alone, then both
- target side, Q1, Q2, Q3: `c3_t2`, which is the only way to test the
  robust-GRAPE assumption, because only a target-side spectator shifts the
  target

Spectators are run in |0> and |1>. Every shot starts and ends in the dressed
basis of the static Hamiltonian. Bare frequencies are retuned so each qubit's
spectator-|0> dressed frequency equals its Phase 2 value, while carriers stay
at the calibrated frequencies.

Reported, all relative to the edges-off Phase 2 gate:

- overlap of each spectator branch with the baseline
- overlap between spectator branches
- spectator excitation and active-pair leakage
- static ZZ of each edge, checked by an idle evolution
- the target-side branch overlap against the 2Q frame-shift model, for a
  ground-calibrated carrier and for the midpoint carrier robust GRAPE assumed

### Phase 4: complete closed-system analysis

Add `analysis/metrics.py` for:

- leakage by qubit
- spectator excitation by qubit
- active-pair observables
- reduced active-pair states
- conditional phases
- simultaneous gates
- computational spectator-state sweeps

For process-level validation:

1. choose a spectator state
2. evolve four active-pair computational inputs
3. trace out spectators
4. reconstruct the active-pair quantum channel
5. compare with ZX(±π/2)

A reduced state from one input is not a process matrix.

The comparison with ZX(±π/2) needs a frame decision first. In the dressed
frame Phase 3 uses, the c1t2 dressing alone puts about 0.26 rad of local Z on
each qubit over the 412 ns gate. An uncorrected ZX fidelity mostly measures
that local Z. Phase 4 must fit the virtual-Z corrections once, with spectators
in |0>, and keep them fixed for every other spectator state.

### Phase 5: noise

After closed-system parity works, add:

```text
L_1,i = sqrt(1 / T_1,i) * a_i
```

```text
L_φ,i = sqrt( 2 * (1/T_2,i - 1/(2 T_1,i)) ) * n_i
```

This phase uses `mesolve` and density matrices.

### Phase 6: OPX and line distortion

Do not implement transfer functions or classical crosstalk before
closed-system parity and spectator validation pass.

Keep the nominal `DriveLine` small and serializable. A future version may add
only a registry key:

```python
transfer_function_key: str = "identity"
```

The key resolves through a separate response registry:

```python
{
    "identity": identity_response,
    "dummy_lowpass": synthetic_lowpass,
    "q1_measured": measured_q1_response,
}
```

The default response is identity:

```text
ε_delivered[n] = ε_digital[n]
```

Filter the digital envelope before Hamiltonian construction:

```text
ε_delivered[n] = (h * ε_digital)[n]
```

Add:

1. low-pass approximation
2. configured FIR and IIR taps
3. measured transfer functions
4. classical port-specific crosstalk

Classical crosstalk is separate from `CouplingEdge`:

- `CouplingEdge` describes coherent quantum exchange between transmons.
- Classical crosstalk describes a control tone leaking onto an unintended
  physical qubit.

A future crosstalk record may use:

```python
@dataclass
class CrosstalkPath:
    source_channel: str
    victim_qubit_id: int
    complex_gain: complex
    transfer_function_key: str = "identity"
```

For source channel l leaking onto victim qubit q:

```text
ε_{l→q}(t) = c_ql * (h_ql * ε_l)(t)
```

The leaked tone retains the source channel's carrier frequency. For example,
leakage from `cr_c1_t2` onto Q3 still uses the Q2 carrier frequency. It must
not be merged into `q3_drive`, whose nominal carrier is Q3's frequency.

The future delivery pipeline is:

```text
digital timeline
    -> per-line transfer functions
    -> classical crosstalk paths
    -> delivered physical drive terms
    -> Hamiltonian
```

Filtering happens once before propagation, not repeatedly inside the
Hamiltonian callback.

---

## 16. Locked planning decisions

The following decisions are currently locked:

1. Keep 2Q optimization and n-qubit validation separate.
2. Mirror the 2Q folder and engine structure.
3. Use only the minimal first-version class set.
4. Represent exchange connectivity with `CouplingEdge`.
5. Use neutral coupling endpoints.
6. Keep the fixed nine-edge catalog. No arbitrary custom graph yet.
7. Select physical qubits at construction with `qubit_ids`.
8. Canonicalize tensor order by ascending physical ID.
9. Keep `CouplingEdge.enabled` independent from qubit selection.
10. Mutate `edge.enabled` directly. No setter method is required yet.
11. Keep drive activity independent through timeline envelopes.
12. Use `n_levels` as the default for every selected qubit.
13. Use `levels_by_qubit` for individual overrides.
14. First spectator chip: `qubit_ids=(1, 2, 4, 6)`. Mixed truncation `(4, 4, 3, 3)` is a constructor check. Physics parity uses the GRAPE sidecar `n_levels` on Q1 and Q2, with spectators at 3 levels.
15. Begin Phase 1 with dense closed-system `sesolve` and final-state-only output.
16. `c1_t2` uses the lab J. Every other edge uses a J fitted to the paper's cross-Kerr shift, labeled `paper_zz_fit`.
17. Defer noise, transfer functions, and classical crosstalk until later.
18. Treat the dynamiqs fixed-length pulse path as canon, not NumPy grow-as-you-add.
19. Experiments finalize timeline dictionaries. The engine only consumes them.
20. Duplicate 2Q JAX pulse assembly carefully inside n-qubit. Do not live-import it.
21. Prove waveform identity with an equality test before physics parity.
22. Phase 2 disables every coupling edge whose endpoints are not exactly `{1, 2}`. Spectators start in |0>.
23. Phase checks stay script-style. Calibration JSON is reloaded on every base construction.
24. Phase 3 adds a target-side chip, `qubit_ids=(1, 2, 3)`, next to the control-side chip.
25. Spectator analysis uses dressed states, with bare frequencies retuned so every spectator-|0> dressed frequency stays at its Phase 2 value. Carriers never move.
26. Phase 3 reports only metrics relative to the edges-off gate. Absolute ZX fidelity with virtual-Z correction is Phase 4.

---

## 17. Items still open for discussion

Every value taken from the paper (Deshmukh et al., Phys. Rev. Research 8, 033049 (2026)) is listed in `documentation/PAPER_VALUES.md`.

The n-qubit working model is locked there: lab Q1/Q2 and `c1_t2`, paper Table I for Q3-Q6 (frequencies plus the Q1 offset), and J fitted at the paper frequencies. The lab files are not overwritten.

Still open:

1. Whether the paper's device is the current device. The Q1-Q2 detuning matches to 0.2 MHz. Q5 and Q6 differ by about 200 MHz in the lab files. The simulator uses the paper placement for Q3-Q6 anyway.

---

## 18. First major milestone

> Replay one optimized c1t2 NPZ waveform in an n-qubit dynamiqs model,
> initialize selected spectators in |0>, disable spectator coupling
> edges, and reproduce the trusted 2Q dynamiqs result.

Only after this passes should spectator edges be enabled one at a time.
