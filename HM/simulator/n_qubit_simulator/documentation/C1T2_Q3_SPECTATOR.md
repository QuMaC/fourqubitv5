# Q1, Q2, Q3 flat-top: what the fidelity is saying

The run is one echoed c1t2 gate on a three-qubit chip. Q3 is a spectator. Nothing is played on Q3.

## The pulse

The waveform is the calibrated c1t2 flat-top, the same seed the robust GRAPE runs start from.


| Knob           | Value                   |
| -------------- | ----------------------- |
| Flat amplitude | 21 MHz                  |
| Hold           | 122 ns                  |
| Rise and fall  | 16 ns, lab templates    |
| Flat knobs     | 61                      |
| Link samples   | 1                       |
| Echo           | calibrated Xπ on Q1     |
| Total length   | 412 ns                  |
| Active levels  | 4 on Q1 and Q2, 3 on Q3 |
| Target         | ZX(−π/2)                |


The driven channels are `q1_drive` and `cr_c1_t2`. `q2_drive`, `q3_drive`, and `cr_c3_t2` are zero for the whole gate.

## The three frequencies

| Qubit | Frequency | Anharmonicity | Where it comes from |
| --- | --- | --- | --- |
| Q1 | 5087.615 MHz | −271.2 MHz | lab |
| Q2 | 4983.463 MHz | −266.4 MHz | lab |
| Q3 | 5093.055 MHz | −268.0 MHz | paper, shifted by the Q1 lab offset |

| Pair | Detuning | Exchange J | In this run |
| --- | --- | --- | --- |
| Q1-Q2 | 104.152 MHz | 3.216 MHz | on, lab value |
| Q3-Q2 | 109.592 MHz | 3.546 MHz | on when `c3_t2` is on |
| Q3-Q1 | 5.440 MHz | none | Q1 and Q3 are not directly coupled |

## Why Q3 does not just sit there

Q3 is a spectator because no pulse is played on it. It is not decoupled. The interaction is the always-on exchange between Q3 and Q2,

```text
J (a3† a2 + a2† a3)
```

with J = 3.546 MHz and a detuning of 109.592 MHz. There is no drive in that term. Excitation on Q2 can mix with Q3 because those two share the coupling. The mix is small: J divided by the detuning is 0.032, so a bare Q2 excitation carries about 0.1% of Q3 character. That is why, starting from Q3 in `|0>`, only 0.5% of the population leaves `|0>`.

The 9.9% figure for `|+>` is a different thing. It is not 9.9% of the population jumping onto Q3 from the vacuum. Q3 was already half in `|0>` and half in `|1>`. Those two branches pick up different phases, because Q2's frequency depends on Q3. The conditional shift is the static ZZ, about 223 kHz. Over 412 ns that is a phase of 0.59 rad. The part of the superposition that dephases moves from `|+>` to `|->`. Both of those states are still inside Q3's `|0>` and `|1>`. The fidelity throws that amplitude away because it only keeps the overlap with the state you prepared.

## c3_t2 is a coupling, not a pulse

Turning `c3_t2` on adds the always-on exchange between Q3 and Q2 to the Hamiltonian. It is the same kind of term as the always-on exchange between Q1 and Q2. There is no envelope, no carrier, and no CR tone on that pair.

With that coupling present, the frequency of Q2 depends on whether Q3 is in `|0>` or `|1>`. The c1t2 pulse is unchanged. The gate it implements changes, because the target sits at a different frequency in the two cases.

## How the number is computed

The score is the same process fidelity the 2Q simulator uses. One global phase is removed. Local Z is left in. There is no virtual-Z fit.

```text
F = |Tr(U_target† U)|² / 16
```

`U_target` is ZX(−π/2) on the four computational states of Q1 and Q2. `U` is the piece of the final state that is still in the Q3 state you prepared, and still in the Q1-Q2 computational subspace. Population that leaves that Q3 state is missing from `U`, so it lowers `F`.

For a bare level, that piece is the amplitude still on that level. For a superposition, it is the overlap with that same superposition. The superposition used here is

```text
|+> = (|0> + |1>) / √2
```

## The three preparations

All three rows use the same pulse, with `c3_t2` on.


| Q3 at the start | Process fidelity | What the lost weight means |
| --- | --- | --- |
| ground | 0.968690 | 0.5% actually left the ground state |
| excited | 0.971776 | 0.7% actually left the excited state |
| plus | 0.887044 | 9.9% left plus, mostly into minus |


Each branch on its own is a good match to the target. The superposition is worse than either branch.

The two branches agree with each other at overlap 0.927, and they differ by a phase of 0.59 rad. That phase is the spectator ZZ accumulated over 412 ns.

## Why the superposition scores lower

Start Q3 in `|+>` and the state is an equal sum of the two branches. Each branch then picks up its own phase. Wherever those phases disagree, amplitude moves from `|+>` into

```text
|-> = (|0> - |1>) / √2
```

The fidelity keeps only the part that is still in `|+>`. The part that moved to `|->` is counted as lost. About 10% of the population leaves, which is most of the drop from 0.97 to 0.887.

The loss is larger when Q2 is excited, which is when the ZZ actually acts.


| Q1 Q2 input | Weight still in the prepared Q3 state |
| ----------- | ------------------------------------- |
| 00          | 0.949                                 |
| 01          | 0.854                                 |
| 10          | 0.929                                 |
| 11          | 0.869                                 |


So 0.887 is not a different pulse, and neither branch is a bad gate. It is the same c1t2 flat-top, with the two Q3 branches out of phase, and with the score counting only the amplitude that stayed in `|+>`.

## Bloch components through the gate

Z = +1 is `|0>`, Z = −1 is `|1>`. Blue is Q1 starting in `|0>`. Red is Q1 starting in `|1>`. Q2 starts in `|0>` in both traces. `c3_t2` is on.

Q3 starting in the ground state. Its Z stays near +1 and its X and Y stay near 0.

![XYZ with Q3 in the ground state](figures/c1t2_flat_xyz_q3_ground.png)

Q3 starting in plus. Its Z stays near 0, so it is still half `|0>` and half `|1>`. X falls from +1 and Y grows, which is the phase between those two branches.

![XYZ with Q3 in plus](figures/c1t2_flat_xyz_q3_plus.png)

## Where this lives

The experiment class is `C1T2FlatFidelity` in `experiments/gaussian_flattop_fidelity.py`. It subclasses `NQubitSimulatorBase`. The comparison that prints these numbers is

```bash
python -m HM.simulator.n_qubit_simulator.experiments.gaussian_flattop_fidelity
```

Run that from `fourqubitv5`.