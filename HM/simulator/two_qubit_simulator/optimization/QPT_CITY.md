# Reading the echoed-CR city plots

The figures written by `cr_qpt.py` / `optimization_tests/cr_qpt_city.py` are city plots of the gate, in the same layout as Qiskit's `plot_state_city`: real part on the left (blue), imaginary part on the right (red).

The code builds the chi matrix with Qiskit's normalization. Qiskit itself is not imported. The numbers were checked against `qiskit.quantum_info.Chi`.

## What one figure is

Each png is one pulse at one target-frame shift.

| Filename piece | Meaning |
|---|---|
| `flat` | `cr_half_seed_I/Q` from the GRAPE npz, the flat-top |
| `opt` | `cr_half_opt_I/Q`, the optimized pulse |
| `m0p075`, `0p075` | target-frame shift in MHz (`m` is a minus sign) |
| `chi` | 16×16 process matrix |
| `unitary` | 4×4 computational unitary |
| `*_diff` | that matrix minus the ideal \(ZX\) |

The two shifts stored in a robust npz are the two spectator branches (target moved by \(\pm zz/2\)). The npz does not record which sign is spectator \(\lvert 0\rangle\). The panel title is the shift in MHz.

`F_proc` in the title is the process fidelity of that same case to the locked target (`zx_m90` or `zx_90` from the sibling json). It is the fidelity GRAPE was scoring. It is invariant under a global phase. It is not invariant under local \(Z\).

## Axes

The floor axes are the basis labels of the matrix. The vertical axis is one complex entry of that matrix. It is dimensionless. It is not MHz, not radians, and not a probability.

For a `chi` plot the labels are the two-qubit Paulis in Qiskit order

\[
\mathrm{II},\;\mathrm{IX},\;\mathrm{IY},\;\mathrm{IZ},\;\mathrm{XI},\;\ldots,\;\mathrm{ZZ}.
\]

The rightmost letter is qubit 0, which in this simulator is the **target**. The leftmost letter is the **control**. So `ZX` means \(Z\) on the control and \(X\) on the target, the CR interaction. Row label is the first index of \(\chi_{ij}\), column label is the second.

For a `unitary` plot the labels are the computational basis `00, 01, 10, 11` in that same order (control, then target). The vertical axis is \(\mathrm{Re}\,U_{ij}\) or \(\mathrm{Im}\,U_{ij}\).

## Qiskit normalization

The channel is

\[
\mathcal{E}(\rho) = \frac{1}{4}\sum_{ij}\chi_{ij}\, P_i\rho P_j,
\]

with \(P\in\{I,X,Y,Z\}^{\otimes 2}\) the ordinary Pauli matrices, not divided by anything. The \(1/4\) is there because \(\mathrm{Tr}(P_i P_j)=4\,\delta_{ij}\): the Paulis are orthogonal, not orthonormal. Qiskit leaves them bare and puts \(1/2^n\) outside the sum. For two qubits that factor is \(1/4\), so every \(\chi_{ij}\) is four times larger than the convention in which the identity channel is the number 1 sitting on `II`.

Expand the unitary in the same basis,

\[
U = \sum_k c_k P_k, \qquad c_k = \frac{1}{4}\mathrm{Tr}(P_k U), \qquad \sum_k \lvert c_k\rvert^2 = 1.
\]

Qiskit's matrix is \(\chi_{mn} = 4\, c_m c_n^*\). The diagonal entry is the Pauli weight,

\[
\chi_{kk} = 4\lvert c_k\rvert^2.
\]

For a unitary with no leakage the diagonal sums to 4. A bar of height \(h\) on the diagonal means that Pauli has weight \(h/4\).

\(ZX(-\pi/2) = (I + i\, ZX)/\sqrt{2}\) has \(c_I = 1/\sqrt{2}\) and \(c_{ZX} = i/\sqrt{2}\). Each weight is \(1/2\), so each diagonal bar is \(4\times 1/2 = 2\), and the cross terms are

\[
\chi_{\mathrm{ZX},\mathrm{II}} = +2i, \qquad \chi_{\mathrm{II},\mathrm{ZX}} = -2i.
\]

A perfect \(ZX(+\pi/2)\) flips the sign of those imaginary corners. That is the whole ideal city plot: four bars of height 2, and zeros everywhere else.

| Panel | Ideal \(ZX(-\pi/2)\) |
|---|---|
| Real | \(+2\) at `II,II` and `ZX,ZX` |
| Imaginary | \(+2\) at `ZX,II` and \(-2\) at `II,ZX` |

Height 4 would be a pure Pauli (the identity channel, or a full \(X\), \(Y\), or \(Z\) rotation by \(\pi\)). Height 2 on two Paulis is an equal superposition, which is what a \(\pi/2\) rotation is.

## How to read the errors

Anything that is not those four bars is coherent error in the computational subspace.

- A real diagonal bar on `ZY,ZY` of height \(h\) means weight \(h/4\) on \(ZY\) instead of \(ZX\). That is the CR axis tilted from \(X\) toward \(Y\).
- An imaginary bar on `II,ZY` or `ZY,II` is the same tilt showing up as coherence between \(I\) and \(ZY\), the partner of the ideal `II`/`ZX` corners.
- `IX`, `IY`, `XI`, `YI` are single-qubit errors. `ZZ`, `IZ`, `ZI` are phase errors. Because the plot is in the lab frame, a \(Z\) that a virtual-\(Z\) update could remove is still drawn.
- Off-diagonal bars between two Paulis are coherence between those components of \(U\). They come in conjugate pairs: \(\chi_{ji} = \chi_{ij}^*\).

The four tall bars near height 2 are the gate. Compare them to 2, and compare `II,II` with `ZX,ZX`. If `II,II` is 1.73 and `ZX,ZX` is 2.23, the rotation angle is a bit past \(\pi/2\): more weight has moved from \(I\) onto \(ZX\). The missing weight, if the diagonal no longer sums to 4, is leakage out of the computational subspace. On these pulses the leakage is about \(10^{-3}\), so the diagonal sum is very close to 4 and the visible extras (`ZY`, `IY`, …) are the error budget.

## Color is not a second copy of the height

Blue is always the real part and red is always the imaginary part. Darkness is a stretched scale so the bars of height 2 do not wash out the errors.

By default the color reaches full dark at the largest entry that is at least four times below the peak, and below that cutoff the shade follows \(\sqrt{\lvert z\rvert}\). The line under the figure states the cutoff and the height of the tallest bar. On the flat-top at \(-0.075\,\mathrm{MHz}\) that line is "full dark for \(\lvert z\rvert \ge 0.191\)" while the tallest bar is 2.23. A dark short bar and a dark tall bar are not the same size. Read the height off the vertical axis.

`COLOR_CUTOFF` and `COLOR_GAMMA` in `cr_qpt_city.py` change only this scale. A smaller cutoff, or a smaller gamma, spreads the tiniest bars across more of the shade range. Set `REPLOT_ONLY = True` and rerun. Nothing is re-evolved.

## Phase convention

Only a global phase is removed, chosen so that \(\mathrm{Tr}(U_{ZX}^\dagger U)\) is real and positive. Local \(Z\) on the control or the target is left as the simulator produced it. A spectator-dependent phase therefore stays in the picture. The same \(ZX\) target is used for every panel in a run, so a sign change between shifts is visible rather than absorbed into a new target.

## Files and how to redraw

From `fourqubitv5`, with the qumac-env interpreter:

```bash
python -m HM.simulator.two_qubit_simulator.optimization.optimization_tests.cr_qpt_city
```

Knobs live at the top of `optimization_tests/cr_qpt_city.py`.

- `WHICH`: `chi`, `unitary`, `chi_diff`, `unitary_diff`, or `all`.
- `WITH_SEED`: also propagate the flat-top stored in the same npz.
- `SHIFTS_MHZ = None` uses the shifts in the npz. `SHIFTS_MHZ = [0.0]` is the calibrated frame only.
- `REPLOT_ONLY = True` redraws from the saved `*_qpt.npz`.

`*_qpt.npz` holds every matrix. `*_qpt.json` holds the fidelities, leakage, and the global phase that was removed.
