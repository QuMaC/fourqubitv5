# Phase 0: dynamiqs open-system API probe

**Goal.** Answer six empirical questions about `dq.mesolve` / `dq.mepropagator`
that the rest of the plan silently assumes. No production code, no new modules
in `engine/` or `optimization/`.

**Why it is its own phase.** Every downstream phase branches on these answers.
Phase 6 of the closed-system migration lost time to an axis-order surprise in
`evolve_comp` (the defensive `psi.shape != (2, 4, dim, 1)` check in
`grape_cost_robust` is the scar tissue). Cheaper to find out in a 40-line script
than inside a jitted cost function.

**Deliverable.** One throwaway script plus a findings table appended to this
file. The script can be deleted afterwards; the table cannot.

---

## Setup

File: `engine/mesolve_upgrade_plan/probe_open_api.py`

Run with:

```
/home/hm/IITB/TIFR/Software/envs/qumac-env/bin/python \
  HM/simulator/two_qubit_simulator/engine/mesolve_upgrade_plan/probe_open_api.py
```

Keep it self-contained: build a plain 2-level or 3-level single-qubit system
with hand-written operators. Do **not** import `CR_len_sweep` or the engine.
This phase is about dynamiqs' behaviour, not ours, and a 9x9 CR pulse would just
make failures slower to reproduce.

---

## Q1. Does `mesolve` accept an empty `jump_ops` list?

Phase 2's noiseless-parity test needs the open-system code path to run with
decoherence switched off and reproduce the `sesolve` answer exactly. That only
works if `jump_ops=[]` is legal.

```python
res = dq.mesolve(H, [], rho0, tsave, method=..., options=...)
```

Record: works / raises (and the exact exception).

If it raises, the fallback is a single zero operator
`dq.asqarray(jnp.zeros((dim, dim)))`. Check that this is accepted **and** that
it does not slow the solve down materially, since the parity test will use it on
every run.

## Q2. Does batched `rho0` work, and what shape comes back?

Pass a stack of `n = 16` density matrices, shape `(16, dim, dim)`.

```python
rho0 = dq.asqarray(rho_stack)          # (16, dim, dim)
res  = dq.mesolve(H, jump_ops, rho0, tsave, ...)
print(dq.to_jax(res.states).shape)
print(dq.to_jax(res.final_state).shape)
```

Record the shape of both `res.states` and `res.final_state`. Note that
`evolve_comp` currently uses `result.final_state` while `run_shot` uses
`result.states[-1]`; confirm which one is safe here.

## Q3. Axis order when a batched Hamiltonian meets a batched `rho0`

**The important one.** The robust path installs a length-2 frame via
`set_target_frame`, which makes `delta_qq_MHz` shape `(2,)` inside the
`dq.modulated` coefficient closures, giving a batched `H`. Combined with 16
batched inputs, the result is either `(2, 16, dim, dim)` or `(16, 2, dim, dim)`.

Reproduce the batched-`H` mechanism the same way the engine does - a
`dq.modulated` whose coefficient function returns a length-2 array - rather than
by stacking Hamiltonian matrices, because those are not the same code path.

```python
delta = jnp.asarray([+0.1, -0.1])
Hb = H0 + dq.modulated(lambda t: jnp.exp(1j * TWOPI * delta * t), op)
res = dq.mesolve(Hb, jump_ops, rho0_16, tsave, ...)
print(dq.to_jax(res.final_state).shape)
```

Record the exact shape. Phase 2 asserts on it; do not let Phase 2 guess.

## Q4. `mepropagator` method and gradient arguments

Its `method` defaults to `None`, unlike `mesolve`'s `Tsit5()`. Check that the
engine's existing `self._integrator_method`
(`dq_method.Tsit5(atol=1e-10, rtol=1e-10, max_steps=1_000_000)`) is accepted,
and that `gradient=dq.gradient.BackwardCheckpointed()` is accepted too (7a does
not need gradients, but knowing saves a guess later).

Also record the returned superoperator shape for `dim = 9`: expect
`(81, 81)`, possibly with a leading time axis.

## Q5. Superoperator vectorization convention

Decide whether `mepropagator`'s output acts on row-stacked or column-stacked
vectorized density matrices. Use a **deliberately non-symmetric** unitary so the
two conventions give different answers (a symmetric one cannot discriminate).

Method: with no jump operators, evolve under a constant `H` for time `T`, so the
channel is exactly `rho -> U rho U^dag` with `U = expm(-i H T)`. Then check
which of these matches:

```
S ?= kron(U, U.conj())        # row-major / vec-by-rows
S ?= kron(U.conj(), U)        # column-major / vec-by-columns
```

and independently verify by applying `S` to a vectorized non-symmetric `rho` and
comparing against `U rho U^dag` under each `reshape` order.

Record which one holds. Better still, record it as the definition of a tiny
helper pair (`vec`, `unvec`) that Phase 2 uses everywhere, so the convention is
captured in one place rather than assumed at every call site.

## Q6. Timing and memory, for the Phase 5 go/no-go

On this machine (CPU, `dim = 9`), time a single solve over a realistic gate
duration (~300 ns total, `dt = 1 ns`, so `tsave` spanning `0.3 us`):

| Case | State size | Measure |
| --- | --- | --- |
| `sesolve`, 4 kets, batched frames | `2 * 4 * 9` | wall time (baseline, already known) |
| `mesolve`, 16 rhos, no frame batch | `16 * 81` | wall time |
| `mesolve`, 16 rhos, `(2,)` frame batch | `2 * 16 * 81` | wall time |
| `mepropagator`, no frame batch | `81 * 81` | wall time |

Also record peak RSS if easy. The `2 * 16 * 81` number is the one that decides
whether Phase 5 (7b) is viable at all, or whether it has to fall back to a
`flat_len_ns` sweep instead. Do not use a jitted `value_and_grad` here - raw
solve time is enough to make the call, and jitting is what has been segfaulting.

---

## Findings

Fill this in from the probe output. This table is the phase's real deliverable.

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| Q1 | `jump_ops=[]` accepted? | | |
| Q2 | batched `rho0` output shape | | `states` vs `final_state` |
| Q3 | axis order, batched H + 16 rhos | | the one Phase 2 asserts |
| Q4 | `mepropagator` method / gradient / shape | | |
| Q5 | vectorization convention | | `kron(U, U*)` or `kron(U*, U)` |
| Q6 | timings | | decides Phase 5 viability |

---

## Done when

- [ ] `probe_open_api.py` runs to completion in the `qumac-env` interpreter.
- [ ] All six rows of the findings table are filled in with observed values,
      not expected ones.
- [ ] Q3's answer is written as a concrete tuple, e.g. `(2, 16, 9, 9)`.
- [ ] Q5's answer is written as a `vec` / `unvec` pair that Phase 2 can copy.
- [ ] Q6's `2 * 16 * 81` timing is recorded, with an explicit
      viable / not-viable call on Phase 5 next to it.
- [ ] Any surprise gets a row in the risk register in `00_OVERVIEW.md`.

## Not in scope

No changes to `two_q_pulse_sim_dynamiqs.py`, `device_base.py`, or anything under
`optimization/`. If the probe makes you want to change the engine, write it down
and do it in Phase 2.
