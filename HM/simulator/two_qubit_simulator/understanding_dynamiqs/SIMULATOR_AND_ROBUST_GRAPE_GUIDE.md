# Two-Qubit Simulator and Robust CR GRAPE Guide

## Purpose and scope

This document explains the pulse-level two-qubit simulator in
`HM/simulator/two_qubit_simulator`, with particular emphasis on echoed
cross-resonance (CR) gates, GRAPE pulse optimization, robust optimization over
frequency shifts, numerical tolerances, and optimizer settings.

The simulator answers the following question:

> Given a calibrated two-transmon model and a complex drive envelope, what
> state or gate does that envelope produce in the ideal closed system?

The current implementation includes:

- A two-transmon Duffing-oscillator model.
- QuTiP and dynamiqs simulation backends.
- Complex \(I+iQ\) pulse envelopes.
- Standard echoed-CR GRAPE.
- Robust GRAPE over multiple target-frequency shifts.
- JAX automatic differentiation.
- SciPy L-BFGS-B and Optax Adam or Adan optimization.
- Process fidelity, average gate fidelity, and leakage diagnostics.
- JSON, NPZ, and PNG result output.

The current implementation does not include:

- \(T_1\) relaxation or \(T_2\) dephasing.
- Lindblad master-equation evolution.
- Measured readout confusion matrices.
- An explicit measured static \(ZZ\) Hamiltonian term.
- OPX FIR/IIR filtering or analog-output bandwidth.
- Automatic conversion from MHz Rabi-rate envelopes to OPX voltage samples.

## Code map

The simulator is organized into the following layers:

```text
Configuration_Files/*.json
        |
        v
base_classes/device_base.py
        |
        +--> engine/two_q_pulse_sim.py
        |        QuTiP fixed-step evolution
        |
        +--> engine/two_q_pulse_sim_dynamiqs.py
                 dynamiqs adaptive evolution and JAX batching

engine/pulses.py and engine/pulses_jax.py
        |
        v
experiments/cr_len_sweep.py and cr_pulse_evolution.py
        |
        v
optimization/fidelity.py and fidelity_jax.py
        |
        v
optimization/grape_cost_jax.py
        |
        +--> optimization/cr_grape.py
        |        standard single-frame GRAPE
        |
        +--> optimization/cr_grape_robust.py
                 robust multi-frame GRAPE
```

Important entry points are:

- `experiments/cr_len_sweep.py`: CR duration sweeps, effective interaction
  extraction, and echoed-CR timeline construction.
- `experiments/cr_pulse_evolution.py`: state trajectories and arbitrary NPZ
  waveform evolution.
- `optimization/cr_grape.py`: standard echoed-CR GRAPE.
- `optimization/cr_grape_robust.py`: robust GRAPE over target-frequency shifts.
- `optimization/optimization_tests/cr_grape_robust_test.py`: editable driver
  for a current robust optimization run.
- `optimization/optimization_tests/cr_grape_robust_zz_sweep.py`: systematic
  robustness sweeps.

## 1. Device construction and parameter sources

### 1.1 Two transmons

The device consists of a control transmon and a target transmon. Each is
represented by:

- Anharmonicity \(\alpha_q\) in MHz.
- Rotating-frame frequency in MHz.
- Truncation level \(n_{\mathrm{levels}}\).
- Bare calibrated qubit frequency for reference.

The default truncation is three levels per transmon. This produces a joint
Hilbert-space dimension

\[
d = n_0 n_1 = 3 \times 3 = 9.
\]

The `Qubit`, `DriveLine`, and engine-selection definitions are in
[device_base.py, lines 30-66](../base_classes/device_base.py#L30-L66):

```python
@dataclass
class Qubit:
    anharm_MHz: float
    frame_MHz: float
    n_levels: int = 3
    f_qubit_MHz: float = None

@dataclass
class DriveLine:
    name: str
    target: int
    carrier_MHz: float

def _resolve_engine(engine: str):
    if engine == "qutip":
        ...
    if engine == "dynamiqs":
        ...
```

### 1.2 Calibration files

The device values are loaded through
[config_dictionaries.py, lines 50-68](../../../../Configuration_Files/config_dictionaries.py#L50-L68):

```python
with open(path_global + '/Configuration_Files/System_Parameters/coupling_vals.json') as f:
    coupling_vals = json.load(f)

with open(path_global + '/Configuration_Files/System_Parameters/anharmonicities.json') as f:
    anharmonicities = json.load(f)

with open(path_global + '/Configuration_Files/System_Parameters/fq_vals.json') as f:
    fq_vals = json.load(f)

with open(path_global + '/Configuration_Files/System_Parameters/CrossKerr.json') as f:
    CrossKerr = json.load(f)
```

The simulator currently uses:

- `fq_vals.json` for the control-target detuning.
- `anharmonicities.json` for \(\alpha_0\) and \(\alpha_1\).
- `coupling_vals.json` for the exchange coupling \(J\).
- pulse-calibration JSON files indirectly when constructing the calibrated
  \(X_\pi\) echo pulse and CR seed.

The simulator does not currently use the measured `zz_khz` entry as an
explicit \(ZZ\) Hamiltonian coefficient. Robust simulations instead shift the
target rotating frame.

### 1.3 Drive lines and frames

Three logical drive lines are built:

1. `q1_drive`: drives the control at the control frequency.
2. `q2_drive`: drives the target at the target frequency.
3. `cr_drive`: drives the control at the target frequency.

The corresponding code is
[device_base.py, lines 108-134](../base_classes/device_base.py#L108-L134):

```python
def delta_qq_MHz(self, q_pair):
    return fq_vals["fq_vals"][f"{q_pair[0]}"] - fq_vals["fq_vals"][f"{q_pair[1]}"]

def build_drive_lines(self, q_pair):
    DELTA_QQ_MHZ = self.delta_qq_MHz(q_pair)
    return [
        DriveLine(name="q1_drive", target=0, carrier_MHz=0.0),
        DriveLine(name="q2_drive", target=1, carrier_MHz=-DELTA_QQ_MHZ),
        DriveLine(name="cr_drive", target=0, carrier_MHz=-DELTA_QQ_MHZ),
    ]
```

The control frame is set to zero and the target frame is set to
\(-\Delta_{qq}\). Only frequency differences enter the dynamics.

## 2. Hilbert space and basis ordering

The joint space is ordered as

\[
\mathcal{H}
=
\mathcal{H}_{\mathrm{control}}
\otimes
\mathcal{H}_{\mathrm{target}}.
\]

For equal transmon truncation \(n\), a joint basis index is

\[
i = n\,i_{\mathrm{control}} + i_{\mathrm{target}}.
\]

For \(n=3\), the ordering begins as

\[
|00\rangle,\ |01\rangle,\ |02\rangle,\
|10\rangle,\ |11\rangle,\ |12\rangle,\ldots
\]

The computational-subspace indices are therefore

\[
\mathcal{I}_{\mathrm{comp}}=[0,1,n,n+1].
\]

For qutrits this becomes \([0,1,3,4]\).

The QuTiP engine constructs this indexing in
[two_q_pulse_sim.py, lines 118-143](../engine/two_q_pulse_sim.py#L118-L143):

```python
n0, n1 = self.dims
I0, I1 = qt.qeye(n0), qt.qeye(n1)
d0, d1 = qt.destroy(n0), qt.destroy(n1)
self.a = [qt.tensor(d0, I1), qt.tensor(I0, d1)]
self.ad = [op.dag() for op in self.a]

self.comp_idx = [0, 1, n1, n1 + 1]
```

## 3. Hamiltonian

### 3.1 Static Duffing terms

Each transmon is modeled as a truncated Duffing oscillator. Since each qubit
is in its own rotating frame, the bare-frequency terms rotate away. The static
part is

\[
H_{\mathrm{drift}}
=
\sum_{q=0}^{1}
\frac{2\pi\alpha_q}{2}
a_q^{\dagger}a_q^{\dagger}a_q a_q.
\]

Equivalently, this gives \(\alpha_q n_q(n_q-1)/2\) before the \(2\pi\)
conversion to angular units.

The implementation is
[two_q_pulse_sim.py, lines 127-133](../engine/two_q_pulse_sim.py#L127-L133):

```python
H = 0
for q, qb in enumerate(self.qubits):
    H += (
        TWOPI * 0.5 * qb.anharm_MHz
        * self.ad[q] * self.ad[q] * self.a[q] * self.a[q]
    )
self.H_drift = H
```

### 3.2 Exchange coupling

The transmons are coupled by an exchange term. In the two rotating frames it
becomes time-dependent:

\[
H_{\mathrm{coup}}(t)
=
2\pi J
\left[
a_0^\dagger a_1 e^{+i2\pi\Delta t}
+
a_1^\dagger a_0 e^{-i2\pi\Delta t}
\right],
\]

where

\[
\Delta
=
f_{\mathrm{frame},0}-f_{\mathrm{frame},1}.
\]

In the QuTiP backend this is evaluated directly at each substep:
[two_q_pulse_sim.py, lines 159-164](../engine/two_q_pulse_sim.py#L159-L164).

```python
ph = TWOPI * self.delta_qq_MHz * t_ns * 1e-3
H = H + TWOPI * self.J_MHz * (
    self.coupling_op * np.exp(1j * ph)
    + self.coupling_op_dag * np.exp(-1j * ph)
)
```

The factor \(10^{-3}\) converts ns to microseconds because MHz is inverse
microseconds.

### 3.3 Drive Hamiltonian

For a drive line \(l\), let:

- \(\epsilon_l(t)=I_l(t)+iQ_l(t)\) be the complex envelope in MHz.
- \(q_l\) be the physical target of the line.
- \(\delta_l=f_{\mathrm{carrier},l}-f_{\mathrm{frame},q_l}\).

The drive term is

\[
H_{\mathrm{drive},l}(t)
=
\pi
\left[
\epsilon_l(t)e^{-i2\pi\delta_l t}a_{q_l}^\dagger
+
\epsilon_l^*(t)e^{+i2\pi\delta_l t}a_{q_l}
\right].
\]

The implementation is
[two_q_pulse_sim.py, lines 166-179](../engine/two_q_pulse_sim.py#L166-L179):

```python
for name, eps in samples.items():
    if eps == 0.0:
        continue
    dl = self.drive_lines[name]
    delta = dl.carrier_MHz - self.qubits[dl.target].frame_MHz
    eps_eff = eps * np.exp(-1j * TWOPI * delta * t_ns * 1e-3)
    q = dl.target
    H = H + TWOPI * 0.5 * (
        eps_eff * self.ad[q] + np.conj(eps_eff) * self.a[q]
    )
```

### 3.4 Full closed-system model

The complete simulated Hamiltonian is

\[
H(t)
=
H_{\mathrm{drift}}
+
H_{\mathrm{coup}}(t)
+
\sum_l H_{\mathrm{drive},l}(t).
\]

There are currently no collapse operators, density matrices, or dissipative
terms in the active engine.

## 4. Why CR dynamics emerge

The `cr_drive` physically acts on the control transmon but uses the target
carrier frequency. It is therefore detuned from the control. In combination
with the exchange coupling \(J\), this produces a control-state-dependent
rotation of the target.

The simulator does not insert a \(ZX\) interaction by hand. Instead, the
effective interaction emerges from:

- The control-target detuning.
- The exchange coupling.
- Transmon anharmonicities.
- The off-resonant drive of the control at the target frequency.
- The pulse amplitude and phase.

After propagation, `cr_len_sweep.py` projects the full unitary into the
computational subspace and extracts effective Pauli coefficients using a
matrix logarithm. The extracted terms are:

\[
ZX,\ IX,\ ZY,\ IY,\ ZZ,\ IZ.
\]

See
[cr_len_sweep.py, lines 262-283](../experiments/cr_len_sweep.py#L262-L283):

```python
U_comp = U_full[np.ix_(comp_indices, comp_indices)]
Up, _ = sla.polar(U_comp)
T_us = float(T_total_ns) * 1e-3
H_eff_rad_per_us = 1j * sla.logm(Up) / T_us
H_eff = 0.5 * (H_eff_rad_per_us + H_eff_rad_per_us.conj().T)

for lab in ("ZX", "IX", "ZY", "IY", "ZZ", "IZ"):
    c_P = np.trace(_PAULI4[lab] @ H_eff) / 4.0
    omega_P_rad_per_us = 2.0 * c_P
    out[lab] = float(np.real(omega_P_rad_per_us / (2 * np.pi)))
```

The polar decomposition removes the nonunitary component introduced by
projecting a leaking full-space unitary into the computational subspace.

## 5. Pulse representation

### 5.1 Timeline

A simulator timeline is a dictionary

```python
{
    "q1_drive": complex_array,
    "q2_drive": complex_array,
    "cr_drive": complex_array,
}
```

Each entry is a complex envelope

\[
\epsilon[k] = I[k] + iQ[k]
\]

in MHz. All arrays have equal length and share the same sample interval
`dt_sample_ns`.

This convention is documented in
[pulses.py, lines 1-7](../engine/pulses.py#L1-L7).

### 5.2 CR half-pulse

GRAPE does not optimize every part of the CR pulse independently. It optimizes
complex knobs in the flat region, while retaining calibrated rise and fall
templates.

For knobs \(u_j=I_j+iQ_j\):

1. Each knob is held for a fixed number of 1 ns samples.
2. The rise is scaled to meet the mean of the first `n_link_samples`.
3. The fall is scaled to meet the mean of the last `n_link_samples`.
4. Rise, flat, and fall are concatenated.

The NumPy implementation is
[pulses.py, lines 100-179](../engine/pulses.py#L100-L179).

The JAX implementation is
[pulses_jax.py, lines 31-76](../engine/pulses_jax.py#L31-L76):

```python
flat = _expand_knobs_to_flat(knobs, n_flat)

n_link = max(1, min(int(n_link_samples), n_flat))
u_rise_end = jnp.mean(flat[:n_link])
u_fall_start = jnp.mean(flat[-n_link:])

rise_part = (rise / rise[-1]) * u_rise_end
fall_part = (fall / fall[0]) * u_fall_start

wf = jnp.concatenate([
    rise_part.astype(knobs.dtype),
    flat,
    fall_part.astype(knobs.dtype),
])
```

The JAX path requires `n_flat` to be divisible by `n_flat_knobs`. For example:

- `flat_len_ns=122`, `n_flat_knobs=61` gives two samples per knob.
- `flat_len_ns=122`, `n_flat_knobs=122` gives one sample per knob.

### 5.3 Echoed CR sequence

The optimized CR half \(u\) is assembled into

\[
+u \rightarrow X_\pi \rightarrow -u \rightarrow X_\pi.
\]

The implementation is
[pulses_jax.py, lines 79-115](../engine/pulses_jax.py#L79-L115):

```python
cr_drive = jnp.concatenate([cr_plus, zeroes_x, -cr_plus, zeroes_x])
echo = jnp.concatenate([zeroes_cr, x_pi, zeroes_cr, x_pi])

for name in channel_names:
    if name == "cr_drive":
        out[name] = cr_drive
    elif name == echo_channel:
        out[name] = echo
    else:
        out[name] = idle
```

The echo pulse is applied through `q1_drive` by default.

## 6. Simulation backends

### 6.1 QuTiP fixed-step backend

The QuTiP backend treats each envelope sample as constant and divides it into
`n_sub` smaller propagation intervals:

\[
|\psi(t+\delta t)\rangle
=
\exp[-iH(t+\delta t/2)\delta t]|\psi(t)\rangle.
\]

The propagation code is
[two_q_pulse_sim.py, lines 183-236](../engine/two_q_pulse_sim.py#L183-L236):

```python
dt_sub_us = (self.dt_sample_ns / self.n_sub) * 1e-3

for k in range(L):
    samples = {nm: timeline[nm][k] for nm in names}
    for s in range(self.n_sub):
        t_mid_ns = (k + (s + 0.5) / self.n_sub) * self.dt_sample_ns
        H = self._hamiltonian_at(t_mid_ns, samples)
        psi = (-1j * H * dt_sub_us).expm() * psi
```

There is no ODE tolerance in this backend. Numerical accuracy is controlled
by:

- `dt_sample_ns`.
- `n_sub`.
- The resulting substep \(\delta t=dt_{\mathrm{sample}}/n_{\mathrm{sub}}\).

The shared base defaults are:

- `dt_sample_ns=4` ns.
- `n_sub=8`.
- Effective fixed substep \(0.5\) ns.

Specific experiments can override both values.

### 6.2 dynamiqs adaptive backend

The dynamiqs backend represents the same Hamiltonian with time-dependent
`dq.modulated` operators and evolves it with `dq.sesolve` or
`dq.sepropagator`.

Its integrator configuration is in
[two_q_pulse_sim_dynamiqs.py, lines 70-112](../engine/two_q_pulse_sim_dynamiqs.py#L70-L112):

```python
integrator_tol: float = 1e-10,
integrator_max_steps: int = 1_000_000,
...
self._integrator_method = dq_method.Tsit5(
    atol=integrator_tol,
    rtol=integrator_tol,
    max_steps=integrator_max_steps,
)
self.gradient = dq.gradient.BackwardCheckpointed()
```

The numerical integration settings are therefore:

- Absolute tolerance: `atol=1e-10`.
- Relative tolerance: `rtol=1e-10`.
- Maximum adaptive steps: `1_000_000`.
- Precision: double precision.
- Integrator: Tsitouras 5/4 Runge-Kutta, exposed as `Tsit5`.
- Gradient strategy: backward checkpointing.

The `n_sub` option is retained for API compatibility but is unused by
dynamiqs. Its accuracy is governed by the adaptive integrator instead.

### 6.3 Sample grids

The legacy default of 4 ns corresponds to the QUA instruction clock. The OPX+
arbitrary-waveform envelope has a 1 ns sample grid.

The JAX GRAPE path explicitly requires

\[
dt_{\mathrm{sample}}=1\ \mathrm{ns}.
\]

The check is in
[cr_grape.py, lines 249-259](../optimization/cr_grape.py#L249-L259):

```python
n_flat = int(round(float(cfg.flat_len_ns) / float(opt.exp.dt_sample_ns)))
if n_flat % int(cfg.n_flat_knobs) != 0:
    raise ValueError(...)
if abs(float(opt.exp.dt_sample_ns) - 1.0) > 1e-12:
    raise ValueError("JAX GRAPE locks dt_sample_ns=1.0")
```

## 7. Fidelity and leakage

### 7.1 Target gates

The primary targets are

\[
ZX_{+\pi/2}
=
\exp\left(-i\frac{\pi}{4}ZX\right)
\]

and

\[
ZX_{-\pi/2}
=
\exp\left(+i\frac{\pi}{4}ZX\right).
\]

Their explicit computational-space matrices are defined in
[fidelity.py, lines 18-40](../optimization/fidelity.py#L18-L40).

If the target sign is not supplied, the seed pulse is evaluated against both
signs and the better sign is fixed for the entire optimization. It is not
allowed to change sign from one optimizer iteration to another.

### 7.2 Computational-space propagator

For JAX optimization, the simulator evolves the four computational input
states:

\[
|00\rangle,\quad |01\rangle,\quad |10\rangle,\quad |11\rangle.
\]

Their final states become columns of \(U_{\mathrm{comp}}\). This avoids
propagating every basis state in the full Hilbert space.

See
[fidelity_jax.py, lines 99-122](../optimization/fidelity_jax.py#L99-L122):

```python
def u_comp_from_psi_jax(psi, comp_indices=None):
    if psi.ndim == 3:
        psi = psi[..., 0]
    idx = _idx(comp_indices)
    return psi[:, idx].T

def process_fidelity_comp_jax(U_comp, U_target_comp):
    d = int(U_comp.shape[0])
    overlap = jnp.trace(U_target_comp.conj().T @ U_comp)
    return jnp.abs(overlap) ** 2 / (d * d)
```

### 7.3 Process fidelity

For full-space propagation, the process fidelity is

\[
F_{\mathrm{proc}}
=
\frac{
\left|
\operatorname{Tr}
\left(
U_{\mathrm{target}}^\dagger PUP
\right)
\right|^2
}{d^2},
\]

where \(P\) projects onto the computational subspace and \(d=4\).

For direct computational-space propagation this reduces to

\[
F_{\mathrm{proc}}
=
\frac{
\left|
\operatorname{Tr}
\left(
U_{\mathrm{target,comp}}^\dagger U_{\mathrm{comp}}
\right)
\right|^2
}{16}.
\]

### 7.4 Average gate fidelity

The reported average gate fidelity is

\[
F_{\mathrm{avg}}
=
\frac{
\left|
\operatorname{Tr}
\left(
U_{\mathrm{target,comp}}^\dagger U_{\mathrm{comp}}
\right)
\right|^2+d
}{d(d+1)}.
\]

This is implemented in
[fidelity.py, lines 115-135](../optimization/fidelity.py#L115-L135).

### 7.5 Leakage

For computational input column \(j\), leakage is

\[
L_j
=
1-\sum_{i\in\mathcal{I}_{\mathrm{comp}}}|U_{ij}|^2.
\]

The reported leakage is the mean over the four computational inputs:

\[
L=\frac{1}{4}\sum_{j=1}^{4}L_j.
\]

See
[fidelity.py, lines 137-149](../optimization/fidelity.py#L137-L149).

## 8. Standard GRAPE

### 8.1 What is optimized

For `n_flat_knobs=N`, the optimization variable contains \(2N\) real numbers:

\[
\mathbf{x}
=
(I_0,Q_0,I_1,Q_1,\ldots,I_{N-1},Q_{N-1}).
\]

These are converted to complex knobs

\[
u_j=I_j+iQ_j.
\]

Only the flat-top knobs are optimized. Rise, fall, echo pulses, device
parameters, gate duration, and the target gate remain fixed during one run.

### 8.2 Standard objective

The standard differentiable cost is

\[
C(\mathbf{x})
=
-\left(
F_{\mathrm{proc}}(\mathbf{x})
-w_L L(\mathbf{x})
\right).
\]

The implementation is
[grape_cost_jax.py, lines 50-95](../optimization/grape_cost_jax.py#L50-L95):

```python
psi = sim.evolve_comp(timeline)
U_comp = u_comp_from_psi_jax(psi, statics.comp_indices)
F = process_fidelity_comp_jax(
    U_comp=U_comp,
    U_target_comp=statics.U_target_comp,
)
leak = leakage_from_psi_jax(psi, statics.comp_indices)

return -(F - statics.leakage_weight * leak)
```

The default is `leakage_weight=0.0`. Therefore leakage is normally reported
but not penalized unless the standard GRAPE configuration explicitly changes
this value.

### 8.3 Gradient routes

Standard GRAPE supports two gradient routes:

1. Finite differences:
   - Usually QuTiP.
   - SciPy estimates the gradient by repeatedly evaluating the cost.
   - One gradient evaluation requires roughly \(2N+1\) propagations.

2. JAX automatic differentiation:
   - Requires dynamiqs.
   - The full pulse-to-fidelity calculation is differentiated.
   - `jax.jit(jax.value_and_grad(...))` returns cost and gradient together.

The JAX setup is in
[cr_grape.py, lines 502-538](../optimization/cr_grape.py#L502-L538):

```python
if config.use_jax_grad:
    if not is_dynamiqs:
        raise ValueError(
            "use_jax_grad=True requires CR_len_sweep(..., engine='dynamiqs')"
        )

    def _cost_only(x):
        xq = quantize_amp_x_ste_jax(x, amp_step)
        return grape_cost(xq, sim, statics)

    self._cost_vg = jax.jit(jax.value_and_grad(_cost_only))
```

## 9. Robust GRAPE

### 9.1 Purpose

A pulse optimized at one exact target frequency can perform poorly when the
target transition shifts. Such shifts can arise from:

- Spectator-induced \(ZZ\) interactions.
- Calibration drift.
- Frequency-estimation uncertainty.
- Slow device drift.

Robust GRAPE optimizes one waveform against several target-frequency cases at
the same time.

### 9.2 Frequency-shift model

For shifts \(\delta_i\), the target frame is replaced by

\[
f_{\mathrm{frame},1}^{(i)}
=
f_{\mathrm{frame},1}^{\mathrm{lab}}+\delta_i.
\]

The CR carrier is not shifted. Therefore, each case sees a different
drive-target detuning.

If `shifts_mhz` is not supplied, the robust configuration constructs

\[
\delta_1=-\frac{\Delta_{ZZ}}{2},
\qquad
\delta_2=+\frac{\Delta_{ZZ}}{2}.
\]

Thus `zz_shift_mhz` denotes the full span between the two default cases, not
the magnitude of each endpoint.

This behavior is defined in
[cr_grape_robust.py, lines 223-263](../optimization/cr_grape_robust.py#L223-L263):

```python
zz_shift_mhz: float = 0.3
shifts_mhz: list[float] | None = None

def resolved_shifts(self) -> list[float]:
    if self.shifts_mhz is not None:
        return [float(v) for v in self.shifts_mhz]
    half = 0.5 * float(self.zz_shift_mhz)
    return [-half, half]
```

This is a frame-shift robustness model. It is not identical to inserting a
separate static \(ZZ\) operator into the Hamiltonian.

### 9.3 Batched dynamiqs evolution

The JAX path installs every target frame in one array:

[cr_grape_robust.py, lines 737-762](../optimization/cr_grape_robust.py#L737-L762):

```python
f1 = float(np.asarray(sim.qubits[1].frame_MHz).reshape(()))
sim.set_target_frame(
    f1 + jnp.asarray(self.shifts, dtype=jnp.float64)
)

def _cost_only(x):
    xq = quantize_amp_x_ste_jax(x, amp_step)
    return grape_cost_robust(
        xq,
        sim,
        statics,
        fidelity_metric=metric,
        weights=weights,
        spread_penalty_lambda=lam,
    )

self._cost_vg = jax.jit(jax.value_and_grad(_cost_only))
```

The propagated states have shape

\[
(N_{\mathrm{shifts}},4,d,1).
\]

JAX then vectorizes fidelity and leakage evaluation over the first axis. See
[grape_cost_jax.py, lines 158-185](../optimization/grape_cost_jax.py#L158-L185).

### 9.4 Robust fidelity objectives

Let \(F_i\) be the process fidelity at shift \(\delta_i\), and let normalized
nonnegative weights satisfy

\[
\sum_i w_i=1.
\]

Three combined metrics are implemented.

#### Weighted arithmetic mean

\[
F_{\mathrm{comb}}
=
\sum_i w_iF_i.
\]

This maximizes average performance across the selected cases.

#### Weighted geometric mean

\[
F_{\mathrm{comb}}
=
\exp\left(
\sum_i w_i\log F_i
\right).
\]

This penalizes a low-performing case more strongly than an arithmetic mean.

#### Mean minus spread

\[
F_{\mathrm{comb}}
=
\sum_i w_iF_i
-\lambda
\left(
\max_i F_i-\min_i F_i
\right).
\]

This rewards high mean fidelity while directly discouraging unequal
performance across the shift range.

The JAX implementation is
[grape_cost_jax.py, lines 98-125](../optimization/grape_cost_jax.py#L98-L125):

```python
if metric == "weighted_mean":
    return jnp.sum(w * f)
if metric == "geometric_mean":
    return jnp.exp(jnp.sum(w * jnp.log(jnp.maximum(f, 1e-30))))
if metric == "mean_minus_spread":
    spread = jnp.max(f) - jnp.min(f)
    return jnp.sum(w * f) - spread_penalty_lambda * spread
```

The robust cost is

\[
C_{\mathrm{robust}}=-F_{\mathrm{comb}}.
\]

Although robust runs report leakage, the current robust configuration fixes
the leakage weight to zero. Leakage is therefore diagnostic rather than part
of the optimized objective.

## 10. Optimizers

### 10.1 SciPy L-BFGS-B

L-BFGS-B is the default optimizer in both standard and robust library
configurations.

It is well suited to this problem because:

- The parameter count can be moderately large.
- It uses a limited-memory inverse-Hessian approximation.
- It supports independent bounds on every \(I\) and \(Q\) component.
- It can consume exact JAX gradients or estimate finite-difference gradients.

The bounds are constructed as

```python
bound = float(self.config.amp_bound_mhz)
bounds = [(-bound, bound)] * x0.size
```

from
[cr_grape_robust.py, lines 1098-1107](../optimization/cr_grape_robust.py#L1098-L1107).

The bound applies separately to \(I_j\) and \(Q_j\):

\[
-A_{\max}\le I_j,Q_j\le A_{\max}.
\]

It does not directly impose

\[
|u_j|\le A_{\max}.
\]

Consequently, if both components reach their bounds, the complex magnitude
can reach \(\sqrt{2}A_{\max}\).

### 10.2 L-BFGS-B optimizer tolerances

The explicit SciPy options are
[cr_grape_robust.py, lines 1147-1160](../optimization/cr_grape_robust.py#L1147-L1160):

```python
scipy_result = minimize(
    fun,
    x0,
    method="L-BFGS-B",
    jac=jac,
    bounds=bounds,
    callback=self._callback,
    options={
        "maxiter": self.config.maxiter,
        "maxfun": maxfun,
        "ftol": 1e-15,
    },
)
```

The project therefore explicitly sets:

- Function-reduction tolerance: `ftol=1e-15`.
- Maximum iterations: `maxiter` from the run configuration.
- Maximum cost evaluations: `maxfun`, calculated from the gradient route.

The project does not explicitly set `gtol`. The installed SciPy default
therefore controls projected-gradient termination.

The meaning of `ftol` is a relative cost-reduction stopping criterion. The
value \(10^{-15}\) is intentionally very tight. In practice, a run can stop
because of:

- The relative function-reduction criterion.
- The SciPy default projected-gradient criterion.
- `maxiter`.
- `maxfun`.
- Line-search failure or another SciPy termination condition.

Always retain the saved optimizer message when interpreting convergence.

### 10.3 L-BFGS-B evaluation limits

With a JAX gradient:

\[
\mathrm{maxfun}=30\,\mathrm{maxiter}.
\]

With finite-difference gradients:

\[
\mathrm{maxfun}
=
\mathrm{maxiter}
\left(
50+2N_{\mathrm{knobs}}
\right).
\]

These formulas are implemented in
[cr_grape_robust.py, lines 1110-1129](../optimization/cr_grape_robust.py#L1110-L1129).

Finite differences become expensive because there are \(2N_{\mathrm{knobs}}\)
real optimization variables, and each robust cost evaluation propagates every
frequency-shift case.

### 10.4 Optax Adam

Adam is available when `use_jax_grad=True`. It uses the same JAX cost and
gradient as JAX L-BFGS-B.

The relevant controls are:

- `adam_lr`: learning rate.
- `adam_steps`: fixed number of updates.
- `adam_log_every`: result-history sampling interval.

Adam does not currently have a convergence tolerance or early-stopping test.
It always executes the configured number of steps unless interrupted or an
error occurs.

### 10.5 Optax Adan

Adan is also available through Optax. It uses the same configuration fields as
Adam, including the field name `adam_lr`.

The optimizer construction is in
[cr_grape.py, lines 133-148](../optimization/cr_grape.py#L133-L148):

```python
def _optax_solver(name: str, learning_rate: float):
    import optax

    if name == "adam":
        return optax.adam(learning_rate)
    if name == "adan":
        return optax.adan(learning_rate, weight_decay=0.0)
```

Weight decay is explicitly disabled for Adan because pulse amplitudes are
physical control variables, not neural-network weights.

As with Adam, Adan uses a fixed step count rather than a tolerance-based
stopping condition.

### 10.6 First-order update constraints

After every Adam or Adan update:

1. Parameters are clipped to their \(I/Q\) bounds.
2. If amplitude quantization is enabled, parameters are rounded to the
   amplitude grid.

See
[cr_grape_robust.py, lines 1030-1039](../optimization/cr_grape_robust.py#L1030-L1039):

```python
c, g = self._cost_vg(x)
updates, opt_state = opt.update(g, opt_state, x)
x = optax.apply_updates(x, updates)
x = jnp.clip(x, lo, hi)
if amp_step is not None:
    step_mhz = jnp.asarray(amp_step, dtype=x.dtype)
    x = jnp.round(x / step_mhz) * step_mhz
```

## 11. Amplitude quantization

If `amp_step_khz` is set, the \(I\) and \(Q\) components are quantized
independently.

For a requested step \(s_{\mathrm{kHz}}\), the MHz step is

\[
s_{\mathrm{MHz}}=10^{-3}s_{\mathrm{kHz}}.
\]

For example:

\[
0.55\ \mathrm{kHz}=0.00055\ \mathrm{MHz}.
\]

The forward JAX calculation uses rounded amplitudes, while its backward
gradient uses a straight-through estimator. Conceptually:

\[
Q(x)=s\,\mathrm{round}(x/s)
\]

in the forward pass, but

\[
\frac{\partial Q}{\partial x}\approx 1
\]

in the backward pass.

This keeps gradient optimization possible despite the discrete forward
amplitudes. It is an amplitude grid in simulated MHz units. It is not yet a
complete model of OPX voltage-DAC quantization.

## 12. Library defaults versus current driver settings

It is important to distinguish reusable library defaults from settings in a
particular experiment script.

### 12.1 Standard GRAPE library defaults

From
[cr_grape.py, lines 209-241](../optimization/cr_grape.py#L209-L241):

- Flat length: 122 ns.
- Flat knobs: 61.
- Amplitude bound: 48 MHz per \(I/Q\) component.
- Leakage weight: 0.
- Maximum L-BFGS-B iterations: 80.
- Transmon levels: 3.
- JAX gradient: disabled by default.
- Optimizer: L-BFGS-B.
- Adam or Adan learning rate: 0.02.
- Adam or Adan steps: 200.
- Evolution mode: computational-subspace propagation.

### 12.2 Robust GRAPE library defaults

From
[cr_grape_robust.py, lines 212-254](../optimization/cr_grape_robust.py#L212-L254):

- Flat length: 122 ns.
- Flat knobs: 61.
- Seed amplitude: 21 MHz.
- Default full ZZ span: 0.3 MHz.
- Default cases: \(-0.15\) and \(+0.15\) MHz.
- Default robust metric: weighted mean.
- Spread penalty: 0.3.
- Amplitude bound: 48 MHz per \(I/Q\) component.
- Maximum L-BFGS-B iterations: 360.
- Transmon levels: 3.
- `n_sub`: 16, but unused on the dynamiqs path.
- JAX gradient: disabled in the reusable dataclass default.
- Optimizer: L-BFGS-B.
- Adam or Adan learning rate: 0.02.
- Adam or Adan steps: 200.

### 12.3 Current `cr_grape_robust_test.py` settings

At the time this guide was written, the editable driver
[cr_grape_robust_test.py, lines 20-75](../optimization/optimization_tests/cr_grape_robust_test.py#L20-L75)
uses:

- dynamiqs and JAX gradients enabled.
- Flat length: 122 ns.
- Flat knobs: 122, giving one flat knob per ns.
- Full shift span: 0.15 MHz.
- Default endpoints: \(-0.075\) and \(+0.075\) MHz.
- Metric: mean minus spread.
- Spread penalty: 0.3.
- Target gate: `zx_m90`.
- Amplitude bound: 48 MHz per \(I/Q\) component.
- Amplitude grid: 0.55 kHz.
- `MAXITER=300`, relevant only when L-BFGS-B is selected.
- Optimizer: Adan.
- Learning rate: 0.04.
- First-order steps: 360.
- Transmon levels: 4.
- Warm start disabled.

These are experiment-specific values and should not be described as universal
defaults.

## 13. Robust optimization workflow

The robust JAX workflow is:

```text
Load calibrated qubit and pulse values
        |
        v
Build two-transmon dynamiqs simulator
        |
        v
Create calibrated or NPZ warm-start flat knobs
        |
        v
Assemble rise + flat + fall CR half
        |
        v
Build +u, X_pi, -u, X_pi echoed timeline
        |
        v
Install N target-frame shifts
        |
        v
Propagate four computational inputs for all N shifts
        |
        v
Compute F_i and leakage_i for every shift
        |
        v
Combine F_i into one robust objective
        |
        v
Differentiate cost with JAX
        |
        v
Update with L-BFGS-B, Adam, or Adan
        |
        v
Save JSON, NPZ, convergence plot, and waveform plot
```

The main driver constructs its configuration in
[cr_grape_robust_test.py, lines 99-143](../optimization/optimization_tests/cr_grape_robust_test.py#L99-L143):

```python
config = RobustCRGrapeConfig(
    flat_len_ns=FLAT_LEN_NS,
    n_flat_knobs=N_FLAT_KNOBS,
    zz_shift_mhz=ZZ_SHIFT_MHZ,
    shifts_mhz=SHIFTS_MHZ,
    weights=WEIGHTS,
    fidelity_metric=FIDELITY_METRIC,
    spread_penalty_lambda=SPREAD_PENALTY_LAMBDA,
    target_gate=TARGET_GATE,
    amp_bound_mhz=AMP_BOUND_MHZ,
    amp_step_khz=AMP_STEP_KHZ,
    maxiter=MAXITER,
    n_levels=N_LEVELS,
    use_jax_grad=USE_JAX_GRAD,
    optimizer=OPTIMIZER,
    adam_lr=ADAM_LR,
    adam_steps=ADAM_STEPS,
)

optimizer = RobustCRGrapeOptimizer(config, flat_knobs_seed=flat_knobs_seed)
result = optimizer.run()
result.save(RESULTS_DIR)
```

## 14. Warm starts and sweeps

### 14.1 Calibrated seed

Without a saved NPZ seed, the flat knobs are initialized from the configured
CR amplitude and phase:

\[
u_j=A_{\mathrm{seed}}e^{i\phi_{\mathrm{seed}}}.
\]

The rise and fall are then attached using the calibrated templates.

### 14.2 NPZ warm start

A saved result contains `flat_knobs_opt`. A later run can load these optimized
knobs and use them as its next seed.

This is useful for:

- Increasing the robust ZZ span gradually.
- Comparing optimizers from the same initial pulse.
- Continuing a partially completed sweep.
- Testing nearby parameter values.

### 14.3 Warm-chain interpretation

In a warm ZZ sweep, the solution at one span becomes the seed at the next
span. Therefore the points are not statistically independent. A warm chain
tests continuation of one solution branch, while flat-seed runs test repeated
optimization from the same baseline.

Both are useful, but they answer different questions and should be labeled
separately in reported results.

## 15. Outputs

A robust result saves:

- A JSON file containing configuration, seed metrics, final metrics, optimizer
  history, shifts, weights, and target gate.
- An NPZ file containing seed and optimized complex knobs and assembled
  waveforms.
- A convergence PNG.
- A waveform PNG.

The result naming includes the ZZ span, robust metric, and timestamp. Saving is
implemented in
[cr_grape_robust.py, lines 320-400](../optimization/cr_grape_robust.py#L320-L400).

When interpreting a result, record at least:

- Git commit or workspace date.
- Exact driver script.
- Backend.
- Number of transmon levels.
- Shift list and weights.
- Robust metric.
- Optimizer.
- Integrator tolerance.
- Optimizer limits or first-order step count.
- Seed source.
- Quantization step.
- Final per-shift fidelities.
- Combined fidelity.
- Fidelity spread.
- Leakage.
- SciPy termination message, when applicable.

## 16. Validation scripts

The current validation is script-based rather than a unified pytest suite.
Relevant checks include:

- `optimization/optimization_tests/test_pulses_jax.py`: JAX and NumPy pulse
  assembly parity.
- `optimization/optimization_tests/test_fidelity_jax.py`: JAX and NumPy
  fidelity parity.
- `optimization/optimization_tests/test_grape_cost_jax.py`: differentiable
  cost checks.
- `optimization/optimization_tests/test_grape_scipy_jac.py`: JAX gradient use
  through SciPy.
- `optimization/optimization_tests/test_grape_robust_jax.py`: robust batched
  shape and parity checks.
- `optimization/optimization_tests/engine_parity_seed.py`: QuTiP and dynamiqs
  comparison for the same seed.

These tests establish software parity, but they do not establish agreement
between the ideal simulator and measured hardware.

## 17. Running the main robust driver

From the repository root:

```bash
PYTHONPATH=. python -u HM/simulator/two_qubit_simulator/optimization/optimization_tests/cr_grape_robust_test.py
```

For long JAX runs, the scripts may use:

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
```

The simulator requirements currently pin dynamiqs, JAX, QuTiP, and SciPy in
[requirements-hm-sim.txt](../../../../requirements-hm-sim.txt). The file does
not currently pin `optax`, although Adam and Adan import it at runtime. The
active environment must therefore provide Optax separately when those
optimizers are selected.

## 18. Interpretation cautions

### 18.1 Robust shifts are not an explicit \(ZZ\) Hamiltonian

The frame-shift model captures target-frequency displacement while retaining a
fixed CR carrier. It is appropriate for studying detuning robustness, but it
does not reproduce every dynamical effect of an explicit spectator or
multi-qubit \(ZZ\) interaction.

### 18.2 Process fidelity contains leakage sensitivity

The computational block is not unitary when population leaks. Its overlap with
the target is consequently reduced. Leakage is also reported separately to
make this failure mode visible.

### 18.3 Tight optimizer tolerance does not guarantee physical accuracy

`ftol=1e-15` only controls optimizer termination. It does not account for:

- Calibration uncertainty.
- Hamiltonian-model error.
- Missing dissipation.
- Missing electronics filtering.
- Drift during experiments.
- Inaccurate MHz-to-voltage conversion.

A numerically converged waveform can still fail on hardware.

### 18.4 More levels improve physical coverage but increase cost

Three levels capture the leading \(|2\rangle\) leakage. Four levels can reveal
additional leakage and Stark effects but increase the joint dimension from
\(9\) to \(16\). Results obtained with different truncations should be labeled
and compared.

### 18.5 First-order optimizers are step-limited

Adam and Adan currently have no automatic convergence test. Their final result
depends strongly on:

- Learning rate.
- Number of steps.
- Seed.
- Amplitude clipping.
- Quantization.

Convergence plots should be inspected rather than assuming that the last step
is optimal.

## 19. Current modeling boundary

The present simulator models:

\[
\text{ideal digital envelope}
\longrightarrow
\text{closed-system transmon evolution}
\longrightarrow
\text{gate fidelity}.
\]

A hardware-complete model would need:

\[
\begin{aligned}
\text{optimized envelope}
&\longrightarrow \text{OPX amplitude scaling and quantization}\\
&\longrightarrow \text{digital FIR/IIR response}\\
&\longrightarrow \text{analog bandwidth and mixer response}\\
&\longrightarrow \text{open-system transmon evolution}\\
&\longrightarrow \text{readout model}.
\end{aligned}
\]

The active simulator currently begins after most of the electronics chain and
ends before realistic readout.

## 20. Result placeholders

### 20.1 QuTiP and dynamiqs parity

**Configuration:**  

**Waveform or seed:**  

**QuTiP settings:**  

**dynamiqs settings:**  

**State or fidelity discrepancy:**  

**Conclusion:**  

### 20.2 Standard GRAPE

**Target gate:**  

**Seed pulse:**  

**Optimizer:**  

**Gradient route:**  

**Initial process fidelity:**  

**Final process fidelity:**  

**Initial leakage:**  

**Final leakage:**  

**Termination message:**  

**Result files:**  

**Interpretation:**  

### 20.3 Robust GRAPE

**Target gate:**  

**Shift list and weights:**  

**Robust metric:**  

**Seed source:**  

**Optimizer and settings:**  

**Amplitude bound and quantization:**  

**Per-shift seed fidelities:**  

**Per-shift final fidelities:**  

**Combined seed fidelity:**  

**Combined final fidelity:**  

**Final fidelity spread:**  

**Final leakage:**  

**Result files:**  

**Interpretation:**  

### 20.4 Warm-start ZZ sweep

**Sweep range:**  

**Step size:**  

**Flat-seed or warm-chain:**  

**Optimizer settings:**  

**Best span and fidelity:**  

**Failure or convergence points:**  

**Result files:**  

**Interpretation:**  

### 20.5 OPX quantization study

**Amplitude step:**  

**Continuous-waveform fidelity:**  

**Quantized-waveform fidelity:**  

**Maximum waveform difference:**  

**Hardware conversion assumptions:**  

**Result files:**  

**Interpretation:**  

