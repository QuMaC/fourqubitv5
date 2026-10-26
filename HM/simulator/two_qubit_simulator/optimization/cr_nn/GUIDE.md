# Guide to the echoed-CR neural pulse

This note is for the next person who will train and use the network in
`optimization/cr_nn/`. The short command list is in `README.md`. This file
explains the physics, the choices that are already locked, what the code
does today, and how the plots should be read.

The code lives on branch `feature/cr-neural-pulse`. A network has been wired
and smoke-tested on a laptop CPU. It has not yet been trained on the lab GPU,
so there is no finished pulse to load onto the experiment.

## The job

We want one echoed cross-resonance (CR) gate on the pair c1t2: control Q1,
target Q2, target gate ZX−90. The microwave waveform has to keep doing that
gate when the target frequency is a little wrong, because spectator qubits
shift it and we do not know their state when we ask for the pulse.

The network is a fast way to emit that waveform for a requested duration,
robustness width, amplitude ceiling, and coupling. It is trained by
differentiating the Schrödinger equation. It is not trained on a library of
old GRAPE pulses, and it is not PPO.

Two papers sit in the background, and this project is not a copy of either.

- Kiermeyer et al., arXiv:2606.24507, train a network that emits a pulse for a
  requested rotation angle, duration, detuning window, and amplitude-error
  window. Their physics is a closed-form two-level spin. Their robustness
  grid (many detunings and amplitude errors) is inside the loss. Those
  errors are not network inputs.
- Deshmukh et al., Phys. Rev. Research 8, 033049 (2026), measure this
  six-qubit chip. Fig. 1(c) is the cross-Kerr matrix. Fig. 2 shows that three
  spectators split one qubit into eight frequencies, with a full spread of
  about 0.3 to 0.6 MHz. The qubits are operated at the mean of that spread.

## What a spectator does in this simulator

The two-qubit engine does not contain Q3, Q4, Q5, or Q6. A spectator in a
computational state shifts the target frequency. In the code that shift is a
change of the target rotating frame, installed with `set_target_frame`. The
CR carrier stays put. Shifting the target frame is not the same operation as
shifting the carrier.

For c1t2 the partner is Q1, so Q1 is not a spectator. From the Q2 row of
Fig. 1(c) the large spectator cells are Q2–Q3 = 225 kHz and Q2–Q5 = 154 kHz.
Those two bits make four frequencies. Measured from their mean they sit near

\[-190,\ -36,\ +36,\ +190~\mathrm{kHz}.\]

Q4 and Q6 only move Q2 by about 4 kHz, so they are not extra hills. Q4 does
move Q3 by 268 kHz, but that shift is not passed on to Q2. Pairwise cross-Kerr
adds. A 0.27 MHz change in a ~110 MHz Q2–Q3 detuning only corrects the 225 kHz
step by a fraction of a kilohertz.

The first network does not put those four frequencies into the cost. It uses
the same rule as current robust GRAPE: one requested half-width \(S\), and the
loss scores the waveform at the two bounds \(-S\) and \(+S\). \(S\) runs from
0 to 300 kHz so the portrait covers the whole Fig. 2 axis, past the
c1t2 outer bars at about \(\pm 190\) kHz.

Being good at \(\pm S\) does not by itself prove the gate is good at every
frequency between them. After training, `evaluate.py` draws that continuous
curve. The red lines on that plot are the two bounds the optimizer was told
about. The curve between them is a test, not a promise.

## What you type, and what you never type

Train and inference use the same four numbers:

\[x = (T_P,\ S,\ A_{\max},\ J_{12}).\]

| Symbol | Meaning | Range in this net |
|---|---|---|
| \(T_P\) | Flat-top length | 80, 90, ..., 200 ns |
| \(S\) | How far from the mean the pulse must still work | 0 to 300 kHz |
| \(A_{\max}\) | Largest allowed I or Q sample | 30 to 100 MHz |
| \(J_{12}\) | Coupling of this pair | 3.216 ± 1 MHz |

\(S\) is a request, like the paper's detuning-window width \(\Delta\delta\).
It is not "the detuning that happened this shot." This shot's detuning is
unknown, including when the spectators are in superposition, so it is never
an input. The loss is what averages over it, and in this first version that
average is only the two endpoints.

\(J_{12}\) is a device parameter of the pair you are driving. The lab value in
`coupling_vals.json` is 3.216328 MHz. The portrait asks what the pulse does
if that coupling moves by up to 1 MHz. The paper's "2.5 to 4 MHz" sentence is
a spread across nine different bonds, not a window on this one bond, so it is
not the axis we use.

The 239 kHz Q1–Q2 cell in Fig. 1(c) is the cross-Kerr of this same pair. It
is fixed once \(J_{12}\), the control–target detuning, and the anharmonicities
are fixed. It is not a second input.

Frozen inside the Hamiltonian, and therefore absent from \(x\):

- Control–target detuning, about 104.15 MHz on the lab c1t2 chips.
- Anharmonicities, about −271.2 MHz and −266.4 MHz.
- Target gate ZX−90. The Kiermeyer angle \(\beta\) is dropped because we are
  not building a family of rotations.
- Envelope `bessel4_350mhz`, 16 ns rise and fall, echo, and the \(X_\pi\) pulse.

The control–target detuning matters a great deal. Jay's Table II puts CR
poles at \(\Delta_{ct} = 0\), \(-\alpha_c/2\), and \(-\alpha_c\). We froze it
because this first net is for this pair only. A pulse from this net is not a
pulse for a different bond.

## What the network is allowed to change

It outputs only the flat top of one CR half: 200 complex samples at 1 ns,
stored as 400 real numbers (I then Q). A request for \(T_P = 120\) ns keeps
the center 120 samples and drops 40 samples from each side. Rise, fall, echo,
and \(X_\pi\) are pasted on afterwards by the same helpers GRAPE uses
(`assemble_cr_half_jax`, `echoed_timeline_jax`).

The rise and fall are lab templates. They are scaled so the rise ends at the
average of the first 8 flat samples and the fall starts at the average of the
last 8. The optimizer cannot invent a new ramp shape. A fidelity cost does
not grow ramps by itself.

The Bessel filter is a 4th-order low-pass with its 3 dB point at 350 MHz. It
rounds a one-sample step over about 1 ns. It does not replace the 16 ns
template. Every training and evaluation call uses this filter. The current
robust-GRAPE test file is often on a Butterworth filter; this network is not.

I and Q are kept inside \(\pm A_{\max}\) with a smooth tanh bound, so the
gradient does not die on the clip. At zero network output the I channel sits
on the calibrated seed, +21 MHz, provided that seed is inside the requested
ceiling. The smallest ceiling is 30 MHz, so the seed is always legal.

## The network itself

\[4 \rightarrow 1024 \rightarrow 1024 \rightarrow 1024 \rightarrow 1024 \rightarrow 1024 \rightarrow 400\]

Hidden layers use ReLU. The output layer is linear. That is about 4.61
million parameters. Kiermeyer et al. tried 512, 1024, and 2048 neurons, with
5 or 7 layers. Five layers matched seven. Their 5×1024 net (about 5.1 million
parameters, because they emit 900 phases) was nearly as good as 5×2048, and
slightly better at the strictest fidelity cut they published. We took 5×1024
because the transmon solver, not the matrix multiplies, dominates the runtime
and the GPU memory.

The optimizer is Adan, the same family they preferred over Adam, with learning
rate \(2\times 10^{-4}\) and no weight decay. Inputs are scaled to about
\([-1, 1]\) before they enter the first layer. Raw megahertz values would
otherwise sit on very different scales.

There is a smaller 2×32 network used only by `--tiny-smoke`. That is a wiring
test. It is not the model you interpret physically.

## One training step

1. Pick a flat length from the 13 allowed values. The order is a fixed shuffle
   so a resumed run continues the same rotation.
2. Draw \(S\), \(A_{\max}\), and \(J_{12}\) uniformly inside their ranges.
   Duration is discrete. The other three are continuous during training.
3. The network emits 200 complex samples. Crop to \(T_P\). Clip to
   \(A_{\max}\). Attach ramps, echo, and \(X_\pi\).
4. Evolve that one waveform twice, at target frames \(-S\) and \(+S\), with
   this draw's \(J_{12}\), through `sesolve` (Tsit5, double precision,
   checkpointed reverse-mode gradients). Hilbert space is \(4\times 4 = 16\).
5. Compute process fidelity of the computational block against ZX−90 at each
   bound. Combine them as robust GRAPE does:

\[F_{\mathrm{comb}} = \frac{F_{-}+F_{+}}{2} - 0.3\,|F_{-}-F_{+}|.\]

6. Loss is \(-F_{\mathrm{comb}}\). Leakage is logged and is not yet added to
   the loss (`leakage_weight = 0`).
7. Adan updates the weights. The waveform is not a free vector. Changing a
   weight changes the waveform for every request the network can see.

Different requests in one batch must share a duration, because the ODE length
changes with \(T_P\). A shorter gate is not padded with zeros out to 200 ns.
After the drive is over, the coupling and the anharmonic drift would keep
evolving, so padding would be a different experiment. The code compiles one
kernel per duration instead.

GRAPE is still in the tree and still works. It optimizes one waveform for one
fixed request. This network amortizes that problem across the four-dimensional
box. After training, a new request is one forward pass. `compare_grape.py`
can take one network waveform and keep optimizing it with L-BFGS, which is a
spot check, not how the portraits are made.

## How a sweep becomes a picture

Training does not march through a grid. The grids below are evaluation, after
a checkpoint exists. `evaluate.py` holds three inputs at a reference request
and varies the fourth. Each value is one forward pass and one row of a color
plot.

The default reference, unless you pass other flags, is \(T_P = 120\) ns,
\(S = 190\) kHz, \(A_{\max} = 50\) MHz, and \(J_{12} = 3.216328\) MHz.

| Portrait | What moves | What stays fixed | Rows |
|---|---|---|---|
| Duration | 80 to 200 ns, step 10 | \(S\), \(A_{\max}\), \(J_{12}\) | 13 |
| Robustness | \(S\) from 0 to 300 kHz, 31 points | duration, \(A_{\max}\), \(J_{12}\) | 31 |
| Amplitude | 30 to 100 MHz, step 5 | duration, \(S\), \(J_{12}\) | 15 |
| Coupling | 2.216 to 4.216 MHz, step 0.1 | duration, \(S\), \(A_{\max}\) | 21 |

Take the coupling portrait as the concrete example. Every row is asked for
the same 120 ns flat, the same \(\pm 190\) kHz robustness, and the same
50 MHz ceiling. Row \(J_{12} = 2.2\) MHz and row \(J_{12} = 4.2\) MHz are two
different waveforms because the Hamiltonian changed and the network was
trained to answer both requests. You do not re-run GRAPE between rows.

Each portrait is saved twice:

- `portrait_*_raw_flat.png`: the cropped flat-top I and Q, centered in the
  200-sample window. Inactive samples are blank.
- `portrait_*_bessel_timeline.png`: the CR-drive channel after ramps, echo
  sign flip, and the Bessel filter. This is closer to what `sesolve` drives
  with. The \(X_\pi\) pulses are on the echo channel, so they do not appear
  in this CR-drive image.

A fifth figure, `detuning_profile.png`, is not a family of waveforms. It
freezes one waveform and scans the target frame from \(-300\) to \(+300\) kHz.
Vertical lines mark \(\pm S\). Fidelity and leakage versus that scan are the
experimental question: does this one pulse survive the band, or only the two
endpoints?

Read a portrait in that order. First check the fidelity curve for a few rows
(a short \(S\), a mid \(S\), and \(S = 300\) kHz). Then look at whether I and
Q change smoothly down the color plot. A smooth change means the network
found one family of solutions. A sudden jump between neighboring rows means
it hopped between different waveform families, which independent GRAPE seeds
also do. The Kiermeyer networks were useful partly because shared weights
made neighboring requests land in the same family.

## What exists on disk

| File | Role |
|---|---|
| `config.py` | Locked ranges, target, and input scaling |
| `model.py` | MLP, amplitude bound, center crop |
| `sampling.py` | Duration rotation and continuous draws of \(S\), \(A_{\max}\), \(J_{12}\) |
| `cost.py` | Assemble, echo, two-frame `sesolve`, mean-minus-spread |
| `train.py` | Adan loop, logs, checkpoints |
| `checkpoint.py` | Atomic checkpoint publish and resume |
| `evaluate.py` | The four portraits and the detuning curve |
| `compare_grape.py` | L-BFGS refinement of one network pulse |
| `../optimization_tests/test_cr_nn_unit.py` | Shape, scaling, checkpoint tests |
| `../optimization_tests/test_cr_nn_physics.py` | Engine parity and a real gradient |
| `engine/two_q_pulse_sim_dynamiqs.py` | Optional traced \(J\) and target frame; old GRAPE calls omit them |

`sesolve` still uses the installed device when those optional arguments are
left out, so older GRAPE scripts keep their behavior.

## How to train it

On the laptop, only the tiny smoke test is worth running. It checks that a
step, a checkpoint, and a resume work. It does not produce a pulse.

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.train \
  --tiny-smoke --fixed-duration 80 \
  --output-dir /tmp/cr_nn_tiny_smoke
```

The real model is an RTX 4070 job, from Ubuntu under WSL2 on the Windows lab
PC. Native Windows CUDA JAX is not supported. Install the Windows NVIDIA
driver, install Ubuntu 24.04 with `wsl --install -d Ubuntu-24.04`, and do not
install a Linux NVIDIA driver inside WSL. Clone into the Linux filesystem
(`~/src`, not `/mnt/c`), then:

```bash
git fetch origin
git switch --track origin/feature/cr-neural-pulse
./setup_cr_nn_wsl_gpu.sh
source .venv-cr-nn/bin/activate
```

`python -c "import jax; print(jax.default_backend(), jax.devices())"` must
print `gpu` and a `CudaDevice` before you spend a night on training.

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export JAX_COMPILATION_CACHE_DIR="$HOME/.cache/jax-cr-nn"
sudo sysctl -w vm.max_map_count=1048576

python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.train \
  --smoke --fixed-duration 80 \
  --output-dir results/cr_nn_gpu_smoke
```

If that two-step full-size smoke fits in memory, start the study. Try batch
sizes 1, 2, and 4, and keep the largest that leaves headroom. The default
step count in `CRNNConfig` is 10,000. That is a first budget, not a claim
that the fidelity has converged. Kiermeyer's two-level nets took about five
days each on an RTX 5090. This solver is a 16-dimensional transmon ODE, so
time the smoke test and scale from the seconds per step it prints. Do not
quote a total time before that measurement.

Pause with one Ctrl+C, or with `touch results/cr_nn_run_01/PAUSE`. The
current step finishes, then the run writes a checkpoint and exits. A second
Ctrl+C drops back to the last completed step. Resume with the same output
directory and a larger `--steps` if you want to continue past the old target:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.train \
  --resume results/cr_nn_run_01 \
  --steps 20000 \
  --output-dir results/cr_nn_run_01
```

The checkpoint stores the weights, the Adan state, the random-number key, the
duration order, whether a duration was fixed, and the global step. Resuming
does not start the optimizer over.

Then:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.evaluate \
  results/cr_nn_run_01 \
  --output-dir results/cr_nn_run_01/evaluation
```

## What to do next, in order

1. Run the GPU smoke test and record seconds per step and the largest batch
   that fits.
2. Train long enough that \(F_{\mathrm{comb}}\) at a mid-box request
   (\(T_P = 120\) ns, \(S = 150\) kHz, \(A_{\max} = 50\) MHz,
   \(J_{12} = 3.216\) MHz) is worth comparing with GRAPE. Watch
   `metrics.jsonl`. A tiny gradient with a bad fidelity means the step size
   or the initialization needs attention, not that the portraits are ready.
3. Make the four portraits and the detuning curve. For several \(S\), check
   whether fidelity stays high between \(-S\) and \(+S\), and whether it
   falls outside.
4. Run `compare_grape.py` at a few requests, including the lab coupling and
   one coupling near each end of the ±1 MHz window. The network is doing its
   job if one forward pass is close to a GRAPE run started from that pulse.
5. Only after that, decide whether the two-endpoint loss is enough. If the
   detuning curve dips between \(\pm S\), the next cost is a few extra frames
   inside the interval, or the four c1t2 spectator frequencies when
   \(S\) is large enough to contain them. That is a new training run.
6. Later inputs, each only if you will actually type them when you request a
   pulse: control–target detuning, control anharmonicity, and an amplitude-error
   window in the style of Kiermeyer's \(\Delta s\). Amplitude error is not in
   this net at all yet.

Do not put this shot's spectator state, or this shot's exact frequency, into
\(x\). That would train a lookup table for a number the experiment does not
have.
