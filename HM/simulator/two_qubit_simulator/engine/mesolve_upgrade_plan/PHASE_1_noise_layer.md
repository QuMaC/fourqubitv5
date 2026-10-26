# Phase 1: noise layer - rates, collapse operators, `Qubit` fields

**Goal.** Turn `T1_us` / `T2_us` into collapse operators, correctly, and prove it
on a single qubit. Also decide where the numbers come from.

**Why it is its own phase.** The only hard part of this whole upgrade is the
rate arithmetic, and it fails *silently*: a stray `2*pi` or a missing factor of 2
in the dephasing operator produces a perfectly well-shaped, perfectly
convergent, completely wrong answer. Every fidelity number in Phases 3-5 is
downstream of these four lines. So they get pinned numerically, on a single
qubit, before any two-qubit machinery exists to hide behind.

**Does not touch** `two_q_pulse_sim_dynamiqs.py`. Phase 1 writes the functions;
Phase 2 calls them.

Depends on Phase 0 only for Q1 (`jump_ops=[]` behaviour), and only for the test.

---

## 1. New module: `engine/noise_ops_jax.py`

Physics and operators only. **No JSON, no config, no `Qubit` import.** Where
numbers come from is section 2's problem; this module just turns two floats into
operators.

```python
def coherence_rates(T1_us: float, T2_us: float) -> tuple[float, float]:
    """(gamma_1, gamma_phi) in us^-1.

    gamma_1   = 1 / T1_us
    gamma_phi = 1 / T2_us - 1 / (2 * T1_us)

    Raises ValueError if T1_us <= 0, T2_us <= 0, or T2_us > 2 * T1_us
    (the last implies gamma_phi < 0, which is unphysical). Do not clamp.
    """


def qubit_jump_ops(
    a_q,                      # annihilation op for this qubit, full register dim
    T1_us: float | None,
    T2_us: float | None,
) -> list:
    """Static QArrays for one qubit. Empty list if both are None.

    L_relax = sqrt(gamma_1)       * a_q
    L_deph  = sqrt(2 * gamma_phi) * (a_q^dag @ a_q)

    Omit L_deph when gamma_phi == 0 exactly, rather than appending a zero
    operator. Allow T1 alone (pure relaxation) and T2 alone is an error -
    gamma_phi is undefined without T1.
    """


def build_jump_ops(
    a_ops: list,              # [a0, a1], already kron'd to the register dim
    T1_us: list,              # per qubit, entries may be None
    T2_us: list,
) -> list:
    """Concatenate per-qubit operators. Returns [] when nobody has coherence
    numbers, which is the switch that makes the open-system path reproduce the
    closed-system answer exactly."""
```

### Two things to get right

**No `TWOPI`.** Every other rate in this engine is angular - `H_drift` carries
`TWOPI * 0.5 * anharm_MHz`, the coupling carries `TWOPI * J_MHz`. Decay rates
are not angular frequencies. `gamma_1 = 1 / T1_us` and nothing else. Since
`tsave` is already in microseconds (`dt_sample_us = dt_sample_ns * 1e-3`), the
units are consistent with no conversion at all. A stray `2*pi` is a 6.28x error
that shape checks cannot see.

**`sqrt(2 * gamma_phi)` on `n`, not `sqrt(gamma_phi)`.** With the dissipator
convention `D[L]rho = L rho L^dag - 0.5 * {L^dag L, rho}` and `L = sqrt(g) n`,
the off-diagonal element `rho_01` decays at `g / 2`. So the pure-dephasing time
is `2 / g`, and getting `1 / T2 = 1 / (2 * T1) + gamma_phi` requires
`g = 2 * gamma_phi`. Section 3's test pins this rather than trusting the
algebra.

Use the ladder operator `a`, not `|0><1|`. In a 3-level transmon that gives
`Gamma(2->1) = 2 * Gamma(1->0)` for free and makes `|2>` population decay -
physically right, and it changes what "leakage" means (see D4 in
`00_OVERVIEW.md`).

The dissipator is invariant under `a -> exp(i theta) a`, so these operators are
**static in the rotating frame**. No frame bookkeeping, no interaction with
`set_target_frame`, no time dependence.

---

## 2. `base_classes/device_base.py`

### 2a. `Qubit` gains three fields

Insert after `f_qubit_MHz`, before `ro_fidelity_matrix`. All have defaults, so
every existing call site and the entire QuTiP path are untouched:

```python
T1_us: float | None = None
T2_us: float | None = None
T2_kind: str = "echo"      # "echo" -> T2e, "star" -> T2*
```

`None` means noiseless. `T2_us` holds the *already selected* value; `T2_kind`
records which measurement it came from, for provenance in the Phase 4 score
output. Do not store both T2e and T2\* on the qubit - one source of truth.

### 2b. Where the numbers come from

Resolution order, highest priority first:

1. explicit `T1_us` / `T2_us` kwargs on `TwoQubitSimulatorBase`
2. `_measured_coherence(q_no, T2_kind)` lookup
3. `None` -> noiseless

```python
def _measured_coherence(q_no: int, T2_kind: str = "echo") -> tuple[float | None, float | None]:
    """Read Configuration_Files/System_Parameters/coherence_vals.json if it
    exists. Returns (T1_us, T2_us) with T2 picked by T2_kind ("echo" ->
    "T2e_us", "star" -> "T2star_us"), or (None, None) if the file or the
    qubit's entry is absent.

    Inert today: that file does not exist yet. Schema is pinned in
    00_OVERVIEW.md D5 so populating it later needs no code change here.
    Must not raise on a missing file - a missing file means noiseless.
    """
```

`TwoQubitSimulatorBase.__init__` accepts `T1_us`, `T2_us`, `T2_kind` kwargs.
Each of `T1_us` / `T2_us` may be a scalar (applies to both qubits) or a length-2
list (per qubit, in `q_pair` order). `build_qubits` stamps the resolved values
onto each `Qubit`.

`CR_len_sweep.__init__` already forwards `**kwargs` to
`super().__init__(qubit_pair=qubit_pair, **kwargs)`, so no change is needed
there - the kwargs reach `TwoQubitSimulatorBase` for free.

Applying one qubit's measured numbers to both qubits (which is what today's
unlabelled legacy data forces, see D6) is an approximation. Record the resolved
per-qubit values so Phase 4 can print them; do not let it be implicit.

---

## 3. Test: `optimization_tests/test_noise_ops_jax.py`

Single qubit, hand-built operators, no `CR_len_sweep`, no GRAPE. Should run in
seconds. Follow the print-and-assert style of `test_grape_robust_jax.py`
(prints the numbers, asserts, prints an OK banner, `__main__` block at the
bottom calling each test).

Use `T1_us = 39.44`, `T2_us = 4.61` (the T2e from the November 2025 legacy fit)
so the test doubles as a sanity check on realistic values.

### `test_rate_arithmetic`

Pure arithmetic, no ODE.

- `coherence_rates(39.44, 4.61)` returns `gamma_1 = 1/39.44` and
  `gamma_phi = 1/4.61 - 1/(2*39.44)`, both to `1e-12`.
- `coherence_rates(10.0, 20.0)` gives `gamma_phi == 0.0` exactly
  (`T2 = 2*T1`, the pure-relaxation limit).
- `coherence_rates(10.0, 25.0)` raises `ValueError`.
- `coherence_rates(-1.0, 5.0)` and `coherence_rates(10.0, 0.0)` raise.

### `test_jump_op_structure`

- `qubit_jump_ops(a, None, None) == []`.
- With both set, returns 2 operators; the first is proportional to `a`, the
  second to `a^dag a` and diagonal.
- `qubit_jump_ops(a, 10.0, 20.0)` returns 1 operator (dephasing omitted at
  `gamma_phi == 0`), not 2 with a zero.
- The dephasing operator's `[2,2]` entry is `2x` its `[1,1]` entry, confirming
  `n` and not a two-level projector.

### `test_t1_recovery`

3-level qubit, `H = 0` (or anharmonicity only - it commutes with `n` and must
not matter; asserting that it doesn't is a free extra check). Start in `|1>`,
`dq.mesolve` out to `3 * T1`, save ~40 points.

Extract without curve fitting, so the test has no fitter to blame:

```
p1(t)          = < 1 | rho(t) | 1 >
gamma_measured = -log(p1(t)) / t        # evaluated at t = T1_us
```

- `1 / gamma_measured` recovers `T1_us` to better than `1e-3` relative.
- Log-linearity: least-squares fit of `log(p1)` against `t` over all points has
  max residual `< 1e-6`, confirming it is a clean single exponential and not
  something that merely passes through the right point.
- `|2>` population stays `< 1e-12` (the ladder lowers, it does not raise).

The `1e-3` tolerance is loose on purpose relative to the integrator's `1e-10`:
it is not testing the ODE solver, it is testing that nobody wrote `2*pi/T1`
or `1/(2*T1)`. Either mistake misses by a factor of 2 or more.

### `test_t2_recovery`

Same system, start in `(|0> + |1>)/sqrt(2)`.

```
c(t)           = | < 0 | rho(t) | 1 > |
gamma_measured = -log(c(t) / c(0)) / t   # evaluated at t = T2_us
```

- `1 / gamma_measured` recovers `T2_us` to better than `1e-3` relative.
  **This is the assertion that pins the `sqrt(2 * gamma_phi)` convention** -
  with `sqrt(gamma_phi)` instead, the recovered T2 misses by roughly a factor
  of 2 and this fails loudly.
- Log-linearity residual `< 1e-6` as above.
- Cross-check the decomposition directly: with `gamma_phi` forced to zero
  (pass `T2_us = 2 * T1_us`), the recovered coherence decay rate equals
  `gamma_1 / 2` to `1e-3` relative. That isolates the relaxation contribution
  to T2 from the dephasing one, so a failure tells you which of the two
  operators is wrong.

### `test_device_defaults_unchanged`

- A `Qubit` built with no coherence kwargs has `T1_us is None` and
  `T2_us is None`.
- `build_jump_ops` over two such qubits returns `[]`.
- Constructing `CR_len_sweep(qubit_pair=[1, 2], engine="dynamiqs", ...)` with no
  coherence kwargs still works and its qubits carry `None` - i.e. nothing about
  the existing closed-system path changed.
- `_measured_coherence(1)` returns `(None, None)` and does not raise, with
  `coherence_vals.json` absent.
- Passing `T1_us=39.44, T2_us=4.61` through `CR_len_sweep(**kwargs)` lands on
  both `Qubit` objects; passing `T1_us=[39.44, 24.32]` lands per qubit in
  `q_pair` order.

---

## Done when

- [ ] `noise_ops_jax.py` exists with the three functions above and no config or
      JSON imports.
- [ ] `Qubit` has the three new fields; every existing construction site still
      works unchanged.
- [ ] `_measured_coherence` returns `(None, None)` quietly with no
      `coherence_vals.json` present.
- [ ] `test_noise_ops_jax.py` passes all five tests.
- [ ] `test_t2_recovery` has been *seen to fail* after deliberately changing
      `sqrt(2 * gamma_phi)` to `sqrt(gamma_phi)`, then restored. A convention
      test that has never failed is not yet known to be a test.
- [ ] The QuTiP path still runs: one existing closed-system test or run file
      executes unchanged.

## Not in scope

- `self.jump_ops` on the engine, `run_superop`, `evolve_comp_open` - Phase 2.
- Any fidelity, any 9x9 two-qubit solve, any GRAPE - Phases 3-5.
- Creating `coherence_vals.json` or a promoter script to populate it from
  interleaved-coherence output.
