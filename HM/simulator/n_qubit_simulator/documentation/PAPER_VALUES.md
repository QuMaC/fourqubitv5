# Values taken from the six-qubit paper

Every number in the n-qubit simulator that comes from this paper is listed
here, with where it comes from and where it is used. Anything not in this file
comes from the lab files in `Configuration_Files/System_Parameters/`.

## Source

J. Deshmukh, S. Das, B. Nambiar, M. Chand, K. V. Salunkhe, G. Umasankar,
A. Kamat, K. Bhowal, G. Agarwal, L. Bharadwaj, E. Chawla, P. Jain,
M. P. Patankar, and R. Vijay, "Coherent errors in a superconducting six-qubit
network with beyond-nearest-neighbor connectivity," Phys. Rev. Research 8,
033049 (2026). DOI: 10.1103/6jdh-pm39.

Data: Zenodo, DOI 10.5281/zenodo.15561172.

The supplemental material (Sec. I, coupling estimates from cross-Kerr) has not
been read. Its J estimates would replace the fits below if obtained.

## Status of each value

| Value | Paper location | Used in | Status |
| --- | --- | --- | --- |
| cross-Kerr shifts, nine connected pairs | Fig. 1(c) | Phase 3 J fit for every edge except `c1_t2` | used |
| cross-Kerr shifts, six disconnected pairs | Fig. 1(c) | recorded only | not used, at most 9.7 kHz |
| connectivity: each qubit couples at ±60° and 180° | Sec. II, Fig. 1(a) | confirms the nine odd-to-even edges | used as a check |
| qubit frequencies | Table I | Q3-Q6 in the n-qubit model, plus the J fit | used |
| anharmonicities | Table I | Q3-Q6 in the n-qubit model, plus the J fit | used |
| Q6 anharmonicity, -271 MHz | Table I | replacement for the lab's 633.6 MHz | used |
| T1, T2*, T2 | Table I | Phase 5 noise | recorded only |
| f0 and f_mean operating points | Sec. II | same idea as Phase 3's ground-calibrated and midpoint placements | interpretation only |
| CR pole conditions and the 25 MHz avoidance margin | Table II, Sec. III | Phase 3 interpretation | interpretation only |
| J of about 2.5 to 4 MHz on connected pairs | Sec. II | sanity range for fitted J | check only |
| uniform J = 3 MHz in their simulations | Sec. III | not used | recorded only |

`c1_t2` never uses the paper. It keeps the lab J from `coupling_vals.json`.

## What the paper does not give

| Missing | Needed by | Workaround |
| --- | --- | --- |
| J per pair | every phase with spectator edges | fit to the Fig. 1(c) shifts; Supplement Sec. I has estimates, not yet read |
| single-qubit pulse calibrations for Q3 to Q6 | Phase 4 simultaneous gates | assume, for example a copy of the Q1 calibration |
| CR calibrations for bonds other than Q1-Q2 | gates on other bonds | none; only "typical CR gate time 300 ns" |
| readout parameters and confusion matrices | not modeled | none needed |
| transfer functions and classical drive crosstalk | Phase 6 | another source |

Precision: frequencies are given to 0.01 MHz except Q5 (0.1 MHz).
Anharmonicities are whole MHz.

Ambiguity: Table I does not say whether each frequency is the value with every
other qubit in the ground state (f0) or the mean over spectator states
(f_mean). The text uses both. The spread is 0.3 to 0.6 MHz. Phase 3
compensation assumes f0.

Labeling: the lab's Q1-Q2 detuning, 104.15 MHz, matches the paper's
104.32 MHz, which supports the paper's Q1 and Q2 being the lab's Q1 and Q2.

## Fig. 1(c): cross-Kerr shifts (kHz)

Connected pairs:

| Edge | Shift |
| --- | --- |
| `c1_t2` | 239 |
| `c1_t4` | 116 |
| `c1_t6` | 64 |
| `c3_t2` | 225 |
| `c3_t4` | 268 |
| `c3_t6` | 147 |
| `c5_t2` | 154 |
| `c5_t4` | 162 |
| `c5_t6` | 100 |

Disconnected pairs: Q1-Q3 4.9, Q1-Q5 9.7, Q2-Q4 3.8, Q2-Q6 3.9, Q3-Q5 0.4,
Q4-Q6 2.5.

The paper defines the shift as the magnitude of the Z⊗Z component, measured
by conditional Ramsey: the frequency shift of one qubit when the other is
excited. That is the same quantity as `total_det_mhz` in `coupling_vals.json`
and the `E11 - E10 - E01 + E00` the simulator computes.

## Table I: the paper's device

| Qubit | Frequency (GHz) | Anharmonicity (MHz) | T1 (µs) | T2* (µs) | T2 (µs) |
| --- | --- | --- | --- | --- | --- |
| Q1 | 5.03104 | -271 | 44 | 35 | 40 |
| Q2 | 4.92672 | -269 | 30 | 21 | 42 |
| Q3 | 5.03648 | -268 | 25 | 11 | 27 |
| Q4 | 4.96960 | -269 | 37 | 28 | 30 |
| Q5 | 4.8378 | -280 | 1.6 | 2.2 | 2 |
| Q6 | 4.92466 | -271 | 57 | 26 | 28 |

## Where the paper and the lab files disagree

The paper's frequencies are not the lab's current frequencies:

| Qubit | Paper (MHz) | Lab `fq_vals.json` (MHz) | Lab minus paper (MHz) |
| --- | --- | --- | --- |
| Q1 | 5031.04 | 5087.61 | 56.6 |
| Q2 | 4926.72 | 4983.46 | 56.7 |
| Q3 | 5036.48 | 5018.15 | -18.3 |
| Q4 | 4969.60 | 4961.93 | -7.7 |
| Q5 | 4837.80 | 5022.23 | 184.4 |
| Q6 | 4924.66 | 5135.89 | 211.2 |

The Q1-Q2 detuning is almost the same in both, 104.32 MHz in the paper and
104.15 MHz in the lab. Every other detuning on the Phase 3 chips is
different: Q1-Q4 is 61.4 MHz in the paper and 125.7 MHz in the lab, Q2-Q3 is
109.8 MHz and 34.7 MHz, Q1-Q6 is 106.4 MHz and -48.3 MHz.

The `c1_t2` shift also disagrees, 239 kHz in the paper against 178.9 kHz in
the lab, at nearly the same detuning. So the `c1_t2` coupling itself differs
between the two configurations. The paper attributes coupling variability to
the manual placement of the transmon chips in the 3D cavity.

## Locked working model

The n-qubit simulator does not overwrite the lab files. It builds this
composite:

| Quantity | Source |
| --- | --- |
| Q1, Q2 frequency | lab `fq_vals.json` |
| Q1, Q2 anharmonicity | lab `anharmonicities.json` |
| Q3-Q6 frequency | paper Table I plus (lab Q1 minus paper Q1) |
| Q3-Q6 anharmonicity | paper Table I |
| `c1_t2` J | lab `coupling_vals.json` |
| other eight J | fit to Fig. 1(c) at paper Table I frequencies and anharmonicities |

The Q1 offset is about 56.57 MHz. Adding it to Q3 through Q6 keeps the paper's
detunings relative to Q1. Q1 and Q2 stay at the frequencies the c1t2 pulse was
calibrated at.

J is fitted at the paper's frequencies, then used as-is. Simulated spectator
shifts are then close to the paper's, because J and the detunings match the
paper. They are not copies of the paper: Q1 and Q2 keep lab anharmonicities,
and Q2 is 0.17 MHz off the paper-plus-offset value.

## Consequence for the Phase 3 fit

The coupling J is the transferable quantity, because it is set by geometry.
The shift is not: it depends strongly on detuning.

The procedure in the working model is:

1. fit J to each paper shift at the paper's Table I frequencies and
   anharmonicities
2. carry that J onto the composite device above
3. treat the simulated shifts as predictions, compared against the paper
   values as a sanity check, not as a fit target at the lab frequencies

The two-transmon formula
`zeta = 2 J^2 (alpha_1 + alpha_2) / ((Delta + alpha_1)(alpha_2 - Delta))`
reproduces the exact `c1_t2` shift to 0.1 kHz at 104 MHz. The code uses the
exact two-transmon diagonalization, not this formula.

## Whether the paper's device is the current device

Not established. Matching Q1-Q2 detunings suggest the same Q1 and Q2 chips.
Q5 and Q6 differ by about 200 MHz, which suggests different chips there. If
the chips or their placement changed, even J does not transfer exactly, and
the paper's values remain estimates for every edge except the ones the lab
measures.
