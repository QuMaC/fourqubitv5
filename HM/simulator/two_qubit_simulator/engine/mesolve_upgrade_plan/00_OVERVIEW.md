# Mesolve upgrade: open-system CR GRAPE

Overall structure for adding Lindblad decoherence to the dynamiqs two-qubit
engine, scoring existing pulses against it (7a), and optimizing through it (7b).

This is **Phase 7** of `understanding_dynamiqs/DYNAMIQS_GRAPE_MIGRATION.md`, but
it is large enough to need its own numbering. Phases here are numbered 0-6 and
live in this folder. When the parent doc is updated at the end, all of this
collapses into one "Phase 7" section there.

---

## Numbering map

| This folder | Parent doc |
| --- | --- |
| Phase 0 - 6 (`PHASE_*.md`) | Phase 7 (single section, written at the end) |

Do not renumber the parent doc's Phases 1-6. They are the closed-system
migration and are finished.

---

## Phase list

| Phase | Title | Touches | Runs an ODE? |
| --- | --- | --- | --- |
| 0 | dynamiqs open-system API probe | throwaway script only | yes, tiny |
| 1 | Noise layer: rates, collapse operators, `Qubit` fields | `noise_ops_jax.py`, `device_base.py` | 1-qubit only |
| 2 | Engine open-system evolution | `two_q_pulse_sim_dynamiqs.py` | yes |
| 3 | Open-system fidelity | `fidelity_open_jax.py` | no (pure algebra) |
| 4 | 7a: error-budget scorer + retro-scoring | `open_system_score.py`, `cr_grape_robust.py` | yes, 4 solves per pulse |
| 5 | 7b: optimize through the Liouvillian | `grape_cost_jax.py`, `cr_grape_robust.py` | yes, on the AD tape |
| 6 | Docs + gate-duration sweep | parent doc, new run file | yes |

Each phase has a `PHASE_N_*.md` with an exact spec, a test with named
assertions, and a done-when checklist. Nothing in phase N+1 should be written
until phase N's checklist passes.

---

## Decisions fixed up front

These are settled now so that no phase has to re-litigate them.

### D1. Collapse operators

Per qubit `q`, with `T1_us` and `T2_us` in microseconds:

```
gamma_1   = 1 / T1_us                        # us^-1
gamma_phi = 1 / T2_us - 1 / (2 * T1_us)      # us^-1

L_relax = sqrt(gamma_1)       * a_q
L_deph  = sqrt(2 * gamma_phi) * n_q           # n_q = a_q^dag a_q
```

Two traps, both load-bearing:

- **No `TWOPI`.** Every other rate in this engine is angular (`TWOPI` baked
  into `H`). Decay rates are *not*. A stray `2*pi` here is a silent 6.28x
  error that no shape check catches. This is why Phase 1 exists on its own.
- **The `sqrt(2 * gamma_phi)` factor.** With `D[L]rho = L rho L^dag -
  0.5 {L^dag L, rho}` and `L = sqrt(g) n`, the off-diagonal `rho_01` decays at
  `g/2`. So pure-dephasing time `T_phi = 2/g`, i.e. `g = 2 * gamma_phi`, which
  makes `1/T2 = 1/(2*T1) + gamma_phi` come out right. Phase 1's test pins this
  numerically instead of trusting the algebra.

Using the ladder operator `a` rather than `|0><1|` gives
`Gamma(2->1) = 2 * Gamma(1->0)` for free (standard transmon assumption) and
makes `|2>` population decay, which is physically right but changes what
"leakage" means - see D4.

Raise on `T2_us > 2 * T1_us` (implies `gamma_phi < 0`, unphysical) rather than
clamping silently.

The dissipator is invariant under `a -> exp(i theta) a`, so these operators are
**static in the rotating frame**. They need no frame bookkeeping and do not
interact with `set_target_frame`. They pass to `dq.mesolve` as a plain list
alongside the existing `TimeQArray` Hamiltonian.

### D2. The 16 input states (this replaced a broken idea)

The first draft of this plan evolved a "Hermitian operator basis", which
includes traceless, non-positive elements like `(|0><1| + |1><0|)/2`. Those are
not density matrices and `dq.mesolve` may well reject them.

Use instead the **standard process-tomography set of 16 pure states**, every
one of which is a legitimate rank-1 density matrix (trace 1, positive):

| Group | Count | State |
| --- | --- | --- |
| computational | 4 | `\|j>` for `j` in 0..3 |
| real superposition | 6 | `(\|j> + \|k>)/sqrt(2)`, `j < k` |
| imaginary superposition | 6 | `(\|j> + i\|k>)/sqrt(2)`, `j < k` |

All 16 map into the 9-dim full space via `comp_idx = [0, 1, 3, 4]`.

The channel's action on the basis operators `|j><k|` follows by linearity.
Writing `E_jj` etc. for the evolved-and-comp-projected images, and for `j < k`:

```
R_jk = 2 * E(plus_jk)  - E_jj - E_kk        # = E(|j><k|) + E(|k><j|)
M_jk = 2 * E(plusi_jk) - E_jj - E_kk        # = i*(E(|j><k|) - E(|k><j|))

E(|j><k|) = (R_jk + i * M_jk) / 2
E(|k><j|) = (R_jk - i * M_jk) / 2
```

Cost: 16 density matrices at 9x9 = 1296 complex numbers, versus 6561 for the
full 81x81 superoperator. Same answer on the computational subspace.

### D3. Fidelity definition (and why the parity test is exact)

One definition only. Process (entanglement) fidelity of channel `E` against
target unitary `U_t`, on the computational subspace, `d = 4`:

```
F_pro = (1/d^2) * sum_{j,k} < j | U_t^dag  E(|j><k|)  U_t | k >
```

where `E` includes the projection onto the computational block, so leakage
appears as a trace deficit exactly as it already does in the closed-system
code.

**This reduces algebraically to the existing expression.** For a closed but
leaky system, `E(rho) = V rho V^dag` with `V` the 4x4 comp block, and the sum
factorizes:

```
sum_{j,k} <j|U_t^dag V|j> <k|V^dag U_t|k> = tr(U_t^dag V) * tr(V^dag U_t)
                                          = |tr(U_t^dag V)|^2
```

so `F_pro = |tr(U_t^dag U_comp)|^2 / d^2`, which is
`process_fidelity_comp_jax` verbatim. The Phase 3 noiseless-parity test is
therefore an *exact identity*, not an approximation - if it fails, there is a
real bug (index order, projection, vectorization convention), never a modelling
difference. That is the whole reason this definition was chosen over average
gate fidelity.

Report `Re(F_pro)` and carry `Im(F_pro)` as an integrator health diagnostic.
`F_avg = (d * F_pro + 1) / (d + 1)` if an average gate fidelity is ever wanted;
do not mix the two in one field.

### D4. Open-system leakage

Once `a` is a jump operator, `|2>` population decays back down, so the
closed-system notion (`1 - comp weight`, monotonically accumulating) no longer
means the same thing. Define explicitly:

- `leakage_end` = `1 - tr(comp_block(rho_final))`, averaged over the 4
  computational inputs. Population outside the comp subspace *at the end of the
  gate*. This is the number that matters for a gate in a circuit.
- `population_loss` = `1 - tr(rho_final)` over the full 9x9. Must be ~0;
  a nonzero value means the integrator is losing trace and the tolerances are
  wrong. This is a diagnostic, not a physics result.

Report both. Never call `leakage_end` comparable to the closed-system leakage
number without saying so - they coincide only when `gamma_1 = 0`.

### D5. `coherence_vals.json` schema, pinned now

The loader hook is written in Phase 1 and is inert until this file exists. Fix
the schema now so populating it later needs no code change. It follows
`fq_vals.json` (timestamp wrapper + per-qubit dict) since provenance matters
more here than for anharmonicities:

```json
{
  "timestamp": "2026-08-26 14:00:00",
  "source": "HM/single_qubit_experiments/interleaved_coherence.py",
  "coherence_vals": {
    "1": {"T1_us": 39.44, "T2star_us": 1.84, "T2e_us": 4.61},
    "2": {"T1_us": 24.32, "T2star_us": 3.21, "T2e_us": 33.90}
  }
}
```

Location: `Configuration_Files/System_Parameters/coherence_vals.json`.
Wiring, when the file appears: one `json.load` in
`Configuration_Files/config_dictionaries.py` next to `anharmonicities`, no unit
scaling (values already in microseconds).

`InterleavedCoherence` already produces exactly these three numbers per qubit
(`results["fit"]["T1"]["decay_us"]`, `["ramsey"]["decay_us"]`,
`["echo"]["decay_us"]`), so a small promoter script can populate this file from
a saved run later. Out of scope here.

### D6. Which measured numbers, for now

The interleaved-coherence outputs live on the instrument machine under
`data_misc/{yy}/{mm}/{dd}/` (the save root in `single_qubit_base.py` line 96
resolves to a Windows path), so they are not on the Linux box. The only fitted
numbers here are legacy, unlabelled by qubit, and they disagree by 7x on T2e:

| Source | Modified | T1 us | T2* us | T2e us |
| --- | --- | --- | --- | --- |
| `Automation/Coherence_fits.json` | 2026-06-12 | 24.32 | 3.21 | 33.90 |
| `SingleQubit_Characterization/Coherence_fits.json` | 2025-11-26 | 39.44 | 1.84 | 4.61 |

Both go into the run file as named constants with one selected, so switching is
a one-line edit. **Applying one qubit's numbers to both qubits is an explicit
approximation** and must be recorded in the score output's provenance field, not
left implicit.

### D7. T2e vs T2\*, and what the budget does and does not double-count

`T2_kind` is a field on `Qubit`, `"echo"` (use T2e) or `"star"` (use T2*).
Default `"echo"`.

The reason: the `+/-ZZ` robust batch already sweeps a static detuning, which is
a coherent average over two Hamiltonians - it models the *quasi-static* part of
the low-frequency noise that makes T2\* short. A Markovian dephasing channel
built from T2\* would model that same noise a second time. So with the robust
batch on, T2e is the non-double-counting choice.

Consequence for the 7a budget: `err_coherent` already contains the ZZ spread,
and `err_deph` contains only the Markovian remainder. State this in the printed
budget. The two are not independent error channels and should not be quoted as
if they were.

---

## Risk register

| Risk | Where it bites | Mitigation |
| --- | --- | --- |
| Batch axis order under robust `(2,)` frame + 16 inputs | Phase 2 | Phase 0 probe. Phase 6 of the parent doc was already bitten by `(2,4,...)` vs `(4,2,...)`; `evolve_comp` still carries a defensive shape check because of it. Assert, never assume. |
| `dq.mesolve` may reject `jump_ops=[]` | Phase 2 noiseless parity | Phase 0 probe. Fallback is a zero operator, which costs time and a little accuracy. |
| Superoperator vectorization convention (row- vs column-stacking) | Phase 2 `run_superop` | Phase 0 probe with a deliberately non-symmetric unitary. Or sidestep entirely by only ever touching the superoperator through a helper calibrated by that probe. |
| 7b state is ~40x the closed-system size (`2*16*81` vs `2*4*9`) | Phase 5 | Off by default. Pre-flight print of state size and an estimated compile cost before `jax.jit`, given this machine has segfaulted twice on XLA compile spikes. |
| Integrator tolerance for a dissipative 81x81 may differ from the closed-system `1e-10` | Phases 2, 3 | Make tolerance an explicit knob; derive test tolerances from it rather than hardcoding `1e-10`. |

---

## Files, by phase

New:

| Path | Phase |
| --- | --- |
| `engine/mesolve_upgrade_plan/probe_open_api.py` (throwaway) | 0 |
| `engine/noise_ops_jax.py` | 1 |
| `optimization/fidelity_open_jax.py` | 3 |
| `optimization/open_system_score.py` | 4 |
| `optimization/optimization_tests/test_noise_ops_jax.py` | 1 |
| `optimization/optimization_tests/test_engine_open.py` | 2 |
| `optimization/optimization_tests/test_fidelity_open_jax.py` | 3 |
| `optimization/optimization_tests/test_open_score.py` | 4 |
| `optimization/optimization_tests/test_grape_open_jax.py` | 5 |
| `optimization/optimization_tests/cr_grape_robust_open.py` | 4, 6 |

Modified:

| Path | Phase |
| --- | --- |
| `base_classes/device_base.py` | 1 |
| `engine/two_q_pulse_sim_dynamiqs.py` | 2 |
| `optimization/grape_cost_jax.py` | 5 |
| `optimization/cr_grape_robust.py` | 4, 5 |
| `understanding_dynamiqs/DYNAMIQS_GRAPE_MIGRATION.md` | 6 |

---

## Environment

`dynamiqs 0.3.4` in `/home/hm/IITB/TIFR/Software/envs/qumac-env`. Both
`dq.mesolve` and `dq.mepropagator` exist:

```
mesolve(H, jump_ops, rho0, tsave, *, exp_ops=None, method=Tsit5(),
        gradient=None, options=Options())
mepropagator(H, jump_ops, tsave, *, method=None, gradient=None,
             options=Options())
```

Note `mepropagator`'s `method` defaults to `None`, not `Tsit5()` - so passing
the engine's existing `self._integrator_method` is a Phase 0 probe item.
