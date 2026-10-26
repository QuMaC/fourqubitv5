# Robust echoed-CR neural pulse generator

The physics, the locked choices, how the sweeps become plots, and what to do
next are in `GUIDE.md`. `GUIDE.pdf` is the same text with the equations
rendered. This file is the command list.

This package trains one neural network through the differentiable dynamiqs
simulator. It does not learn from a dataset of GRAPE pulses.

## Locked physics and I/O

The normalized network input is

\[
x=(T_P,S,A_{\max},J_{12}).
\]

- \(T_P\): flat duration, one of 80, 90, ..., 200 ns.
- \(S\): requested target-frame half-width from 0 to 0.300 MHz.
- \(A_{\max}\): bound on each raw I and Q DAC sample, 30 to 100 MHz.
- \(J_{12}\): pair coupling, 2.216328 to 4.216328 MHz.

The network is five hidden layers of 1024 ReLU units. It emits 400 real
numbers, interpreted as I and Q for 200 complex, 1 ns flat-top samples. The
requested duration selects a centered crop. The existing 16 ns rise and fall
templates are attached with `n_link_samples=8`, followed by the existing echo
and X-pi templates. The complete timeline is filtered by
`bessel4_350mhz`.

For each request, the same waveform is evolved at target-frame shifts
\(-S\) and \(+S\). The score is the existing robust-GRAPE metric

\[
F_{\mathrm{comb}}=\frac{F_-+F_+}{2}-0.3|F_--F_+|.
\]

The target is ZX-90 and each transmon has four levels. Frequencies and
anharmonicities stay fixed at c1t2 values.

## Local wiring smoke test

Run this from the repository root in the existing environment:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.train \
  --tiny-smoke \
  --fixed-duration 80 \
  --output-dir /tmp/cr_nn_tiny_smoke
```

This uses a small 2 by 32 MLP but runs the real four-level Bessel physics,
gradient, Adan update, log, and checkpoint path.

The production-architecture smoke test keeps the full 5 by 1024 MLP:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.train \
  --smoke \
  --fixed-duration 80 \
  --output-dir results/cr_nn_gpu_smoke
```

## Pause and resume

Training writes atomic checkpoints under `OUTPUT/checkpoints`.

To pause cleanly, either press `Ctrl+C` once or create the sentinel:

```bash
touch OUTPUT/PAUSE
```

The current ODE/gradient step is allowed to finish. The trainer then saves the
model, Adan state, PRNG key, duration schedule, and global step before exiting.
Pressing `Ctrl+C` a second time interrupts immediately and saves the last
completed step.

Resume and extend the total step target with:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.train \
  --resume OUTPUT \
  --steps 20000 \
  --output-dir OUTPUT
```

## RTX 4070 on a Windows lab PC

Use Ubuntu 24.04 under WSL2. Native Windows CUDA JAX is not supported.

In an Administrator PowerShell:

```powershell
wsl --install -d Ubuntu-24.04
wsl --update
```

Install the current NVIDIA Windows driver and restart. Do not install a Linux
NVIDIA driver inside WSL. The Windows driver exposes the GPU to WSL.

Inside Ubuntu:

```bash
nvidia-smi
sudo apt update
sudo apt install -y git python3-venv build-essential
git clone YOUR_REPOSITORY_URL ~/src/fourqubitv5
cd ~/src/fourqubitv5
./setup_cr_nn_wsl_gpu.sh
source .venv-cr-nn/bin/activate
```

Keep the repository in the WSL filesystem, such as `~/src`, rather than under
`/mnt/c`.

Before a long run:

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export JAX_COMPILATION_CACHE_DIR="$HOME/.cache/jax-cr-nn"
sudo sysctl -w vm.max_map_count=1048576
```

Start with the production smoke test. Then try batch sizes 1, 2, and 4. Use
the largest size that leaves memory headroom:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.train \
  --steps 10000 \
  --batch-size 2 \
  --checkpoint-every 100 \
  --log-every 10 \
  --output-dir results/cr_nn_run_01
```

For a long Windows run, disable automatic sleep. A `tmux` session is also
recommended:

```bash
sudo apt install -y tmux
tmux new -s crnn
```

## Evaluation

Generate all four waveform portraits and a dense detuning profile:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.evaluate \
  results/cr_nn_run_01 \
  --output-dir results/cr_nn_run_01/evaluation
```

The portraits sweep:

- duration: 80 to 200 ns in steps of 10 ns;
- \(S\): 0 to 300 kHz;
- \(A_{\max}\): 30 to 100 MHz in steps of 5 MHz;
- \(J_{12}\): 2.216328 to 4.216328 MHz in steps of 0.1 MHz.

Each portrait contains raw flat-top I/Q and the full CR-drive timeline seen
through the Bessel filter.

Compare one network output with direct robust GRAPE initialized from that
output:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.cr_nn.compare_grape \
  results/cr_nn_run_01 \
  --output-dir results/cr_nn_run_01/grape_reference \
  --duration 120 \
  --robustness-khz 190 \
  --amp-bound-mhz 50 \
  --maxiter 50
```

Checkpoints and generated result directories should not be committed to git.
