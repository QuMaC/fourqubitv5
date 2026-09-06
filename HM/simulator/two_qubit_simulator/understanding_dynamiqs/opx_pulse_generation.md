# OPX+ pulse generation and the dynamiqs simulation model

How Quantum Machines OPX+ turns QUA waveforms into analog output, what that implies for slew rate and filtering, and how our JAX / dynamiqs CR optimization stack maps onto the hardware.

**Related code**

| Component | Path |
|-----------|------|
| Dynamiqs pulse engine | `engine/two_q_pulse_sim_dynamiqs.py` |
| QuTiP pulse engine (4 ns grid) | `engine/two_q_pulse_sim.py` |
| JAX GRAPE optimizer | `optimization/cr_grape.py`, `optimization/cr_grape_robust.py` |
| Pulse assembly | `engine/pulses.py`, `engine/pulses_jax.py` |
| Lab QM config | `Configuration_Files/configuration_4qubitsv3.py` |

**External references**

- [QM Configuration](https://docs.quantum-machines.co/1.4.1/docs/Introduction/config/)
- [QUA Overview (play / modulation)](https://docs.quantum-machines.co/1.4.1/docs/Introduction/qua_overview/)
- [OPX hardware specs](https://docs.quantum-machines.co/1.3.0/docs/Hardware/OPX_hardware/)
- [Output filters (FIR / IIR)](https://docs.quantum-machines.co/1.4.1/docs/Guides/output_filter/)
- [OPX simulator](https://docs.quantum-machines.co/1.4.1/docs/Guides/simulator/)

---

## 1. Two time scales on OPX+

QM uses two different clocks. Confusing them breaks alignment between optimization and hardware.

| Layer | Resolution | Controls |
|-------|------------|----------|
| **QUA timing / PPU** | **4 ns** | `play()`, `wait()`, pulse `length`, program timing, integration-weight chunks |
| **Waveform envelope** | **1 ns** (1 GS/s) | Arbitrary waveform `samples[]`; list length equals pulse duration in ns |

Rules from the QM docs:

- Pulse `length` must be divisible by **4 ns**.
- Arbitrary waveform `samples` has **one entry per nanosecond** of pulse duration (e.g. a 184 ns pulse has 184 samples).
- Sample values on OPX+ are **volts** in \([-0.5, 0.5]\) V (direct output mode).

Example: a 184 ns CR flat-top has 184 envelope points at 1 ns spacing, but the total sequence timing still snaps to 4 ns boundaries in QUA.

---

## 2. OPX+ hardware limits

From QM product and hardware documentation:

| Parameter | OPX+ value |
|-----------|------------|
| DAC rate | **1 GS/s** (1 ns per sample) |
| Resolution | **16 bit** |
| Voltage range | **±0.5 V** (direct), 50 Ω |
| Analog bandwidth | **~350 MHz** (hardware spec) / **400 MHz** (product page) |

Quantization step (order of magnitude):

\[
\text{LSB} \approx \frac{1\,\text{V}_{pp}}{2^{16}} \approx 15\,\mu\text{V}
\]

Usually negligible for CR drive optimization.

**OPX+ vs OPX1000 LF-FEM:** OPX1000 DACs run at 2 GS/s and upsample 1 GS/s PPU output (`upsampling_mode`: `pulse` = zero-order hold, `mw` = 14-tap Dolph-Chebyshev). **OPX+ has no upsampling stage**; envelope samples go to the DAC at 1 GS/s (after optional digital filters). Do not import OPX1000 upsampling logic into an OPX+ model.

---

## 3. Signal chain (baseband / flux line)

For a `singleInput` element with `intermediate_frequency = 0`:

```
envelope samples s[i]     (1 ns, volts)
        |
        v
x amplitude A             (QUA play amp / scaling)
        |
        v
crosstalk matrix          (optional, per config)
        |
        v
digital FIR               (up to 44 taps, optional)
        |
        v
digital IIR               (up to 3 taps, optional)
        |
        v
16-bit DAC
        |
        v
fixed analog front-end    (~350-400 MHz low-pass)
        |
        v
+ DC offset               (per-port, additive)
        |
        v
BNC output
```

Digital output filters are **predistortion**: calibrated to cancel setup distortions (bias-tee high-pass, cable bounce, amplifier ringing). They are configured per port under `analog_outputs` → `filter` → `feedforward` / `feedback`. If your deployed config enables them, the dynamiqs model should include them or you optimize against a different plant than the hardware plays.

Filter latency on OPX+ (fixed, all ports on that controller):

| Configuration | Latency |
|---------------|---------|
| FIR only | 44 ns |
| FIR + 1 IIR | 48 ns |
| FIR + 2 IIR | 60 ns |
| FIR + 3 IIR | 72 ns |

---

## 4. Signal chain (microwave / CR drive on IQ mixer)

CR drives use mixer elements. The envelope is defined **before** IF modulation.

For I/Q inputs, QUA applies (schematically):

\[
\begin{pmatrix} \tilde{I}_i \\ \tilde{Q}_i \end{pmatrix}
=
A \cdot C_{ij}
\begin{pmatrix} I_i \\ Q_i \end{pmatrix}
\cdot
\begin{pmatrix} \cos(\omega_{IF} t + \phi_F) \\ \sin(\omega_{IF} t + \phi_F) \end{pmatrix}
\]

where \(A\) is amplitude scaling, \(C_{ij}\) is the mixer correction matrix, \(\omega_{IF}\) is `intermediate_frequency`, and \(\phi_F\) is the frame phase.

The dynamiqs engine does **not** replay this RF chain literally. It uses a **two-frame transmon model**: each drive line carries a piecewise-constant envelope and a carrier frequency in the qubit's rotating frame (`DriveLine` + `dq.modulated`). That is the right abstraction for gate optimization as long as the envelope fed to the Hamiltonian matches what the OPX intends at the mixer input (before or after line filtering, consistently).

---

## 5. Slew rate: what QM actually specifies

QM does **not** publish a fixed slew-rate limit in V/ns. There is no dedicated slew limiter in the documented chain.

Effective output shape is set by:

1. **Zero-order hold at 1 ns** (each digital sample held flat for 1 ns).
2. **Optional digital FIR/IIR** (user taps from calibration).
3. **Fixed analog reconstruction** (~350-400 MHz low-pass on the output stage).

### Order-of-magnitude estimate

For a full-scale step \(0 \to 0.5\) V with \(f_{3\text{dB}} \approx 350\) MHz:

\[
t_r \sim \frac{0.35}{f_{3\text{dB}}} \approx 1\,\text{ns}
\qquad\Rightarrow\qquad
\left|\frac{dV}{dt}\right|_{\max} \sim \frac{0.5\,\text{V}}{1\,\text{ns}} \approx 0.5\,\text{V/ns}
\]

This is **filter-limited**, not a hard cap. Small per-sample changes are much gentler than a full-scale step.

**Model as a linear filter, not a `dV/dt < X` saturator.**

---

## 6. How our dynamiqs stack represents pulses today

### 6.1 Dynamiqs engine (`two_q_pulse_sim_dynamiqs.py`)

- Drives enter as **piecewise-constant envelopes** indexed inside `dq.modulated` callbacks.
- Time grid: `dt_sample_ns` (JAX GRAPE uses **1.0 ns**; default constant in `engine/constants.py` is **4 ns** for the legacy QuTiP path).
- Carriers are qubit-frame frequencies, not OPX IF frequencies directly.
- Evolution: `dq.sesolve` / `dq.sepropagator` with Hamiltonian in angular units (MHz × \(2\pi\)), time in µs.

This matches **Tier 0** below: ideal 1 ns ZOH envelopes, no OPX output filtering.

### 6.2 JAX GRAPE (`cr_grape.py`)

- Locks `dt_sample_ns = 1.0` (matches OPX envelope grid).
- Optimizes flat-top knobs; rise/fall from lab templates via `assemble_cr_half_from_flat_knobs`.
- Echoed sequence: \(+u \to X_\pi \to -u \to X_\pi\).

### 6.3 Legacy QuTiP engine (`two_q_pulse_sim.py`)

- Default `DT_SAMPLE_NS = 4` (QUA clock, not envelope grid).
- Sub-steps each 4 ns sample into `n_sub` finer steps for stiff coupling terms.

For hardware-faithful CR optimization, prefer the **1 ns dynamiqs path**, not the 4 ns QuTiP default.

---

## 7. Modeling tiers (what to add next)

Use these tiers when passing assembled JAX pulses through an OPX-like filter before the Hamiltonian.

### Tier 0: Current dynamiqs model

Piecewise-constant envelope at **1 ns**. No DAC or analog effects.

- **Pros:** Fast, differentiable, matches digital intent.
- **Cons:** Optimistic rise/fall; ignores lab line distortion unless folded into calibration elsewhere.

### Tier 1: Minimum hardware-realistic (recommended first step)

1. ZOH at 1 ns (already implicit).
2. Fixed analog low-pass, e.g. \(H(s) = \omega_c / (s + \omega_c)\) with \(\omega_c = 2\pi \times 350\,\text{MHz}\).

In JAX: convolve the envelope with a short discrete impulse response of that filter at 1 ns, or apply as a smoothing step on the drive amplitude before `dq.modulated` indexing.

### Tier 2: Configured digital filters

Read `feedforward` / `feedback` from live `analog_outputs` in the QM config:

\[
y[n] = \sum_{k=0}^{K} b_k\, x[n-k] + \sum_{m=1}^{M} a_m\, y[n-m]
\]

Apply **before** the analog LP. Clip to \([-0.5, 0.5)\) V if modeling OPX saturation.

`qualang_tools.digital_filters.calc_filter_taps` derives taps from measured step responses.

### Tier 3: Ground truth validation

Run the same QUA program through `qmm.simulate()` and `get_simulated_samples()` with the real config. For OPX+, `analog_sampling_rate` is typically `1e9` (1 ns per sample). Compare to the analytic filter model and fit taps or bandwidth if needed.

---

## 8. Where to plug filtering into the optimization path

Conceptual insertion point:

```
assemble_cr_half_from_flat_knobs(...)
        |
        v
[NEW] opx_output_filter(envelope, port_config)   # Tier 1-2
        |
        v
grape_cost / dynamiqs propagation
        |
        v
fidelity
```

Requirements:

- Filter must be **JAX-differentiable** (linear FIR/IIR is fine).
- Apply the **same** filter in forward sim and GRAPE adjoint (or use a fixed filter and treat it as part of the plant).
- For microwave CR lines, decide whether the filter acts on the **envelope** (before `dq.modulated`) or on the **RF** signal; envelope filtering is usually enough for slowly varying CR shapes.

---

## 9. Checklist before trusting sim vs lab

- [ ] Confirm hardware is **OPX+** (not OPX1000 LF-FEM upsampling path).
- [ ] Confirm JAX optimizer uses **`dt_sample_ns = 1.0`**, not 4 ns.
- [ ] Check deployed config for **`filter`** keys on CR / qubit analog outputs.
- [ ] Note CR element **`intermediate_frequency`** and mixer corrections (affects RF, not envelope grid).
- [ ] Optional: compare one optimized waveform to **`get_simulated_samples()`** on the matching port.

---

## 10. Summary

| Question | Answer |
|----------|--------|
| Envelope sample spacing? | **1 ns** on OPX+ |
| QUA timing grid? | **4 ns** |
| Published slew rate? | **No**; use ~350 MHz LP + optional digital taps |
| What dynamiqs uses today? | **1 ns ZOH envelopes** (GRAPE path), no OPX filter |
| Next modeling step? | **Tier 1 LP** or **Tier 2 config FIR/IIR** before propagation |

The goal of the next implementation step is a small `opx_output_filter` (or equivalent) in the JAX path so optimized CR pulses see the same smoothing the hardware applies before they hit the transmon Hamiltonian.
