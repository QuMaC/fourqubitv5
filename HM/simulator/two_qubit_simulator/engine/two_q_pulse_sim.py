"""
two_q_pulse_sim.py
==================
The bare two-qubit pulse-level engine: pulse schedule in, final state /
counts out. Nothing else lives here -- device description (``Qubit``,
``DriveLine``) is in ``base_classes/device_base.py``, envelope helpers and
the ``Timeline`` builder are in ``engine/pulses.py``, and experiment /
sweep scaffolding is under ``experiments/``.

QuTiP build
-----------
Operators and states are qutip.Qobj. Evolution is a fixed-step propagator:
each 4 ns OPX sample is split into n_sub finer steps, H is treated as
constant over each finer step, and the step is applied with Qobj.expm().
This is the scheme validate_simulator.py uses (it steps at the full 4 ns;
the sub-stepping is added here because the two-frame treatment puts a
~100 MHz oscillation on the coupling that a 4 ns step under-resolves).

qutip's ODE solver (sesolve) was tried first and fights that fast
oscillation -- it either errors out ("excess work") or silently
under-resolves. A fixed step below the known fastest timescale is both
simpler and more reliable, which is presumably why the lab's own script
does it that way. So qutip is used for the linear algebra (Qobj operators,
tensor products, expm, basis states), not the solver.

(For the eventual 6Q sim the dense expm becomes the bottleneck -- 3^6 = 729
dimensions -- and gets swapped for a sparse action-of-exponential on the
state vector. Noted, not solved here.)

Design
------
  - Each qubit lives in its OWN rotating frame at its own frequency. The static
    drift therefore carries only anharmonicities; the qubit frequency terms
    rotate away. Only frequency *differences* survive, so absolute frequencies
    are never needed -- only the detuning between the two qubits.
  - A "drive line" is a (physical line, carrier) pair, not a wire. Q1's physical
    line driving Q1 at its own frequency, and the same line driving Q1 at Q2's
    frequency (the CR drive), are two DriveLine objects: same target qubit,
    different carriers. Each contributes a control term that, in the target
    qubit's frame, oscillates at (carrier - frame).
  - The inter-qubit coupling J is therefore time-dependent in this frame: it
    oscillates at the qubit-qubit detuning Delta = frame_0 - frame_1.
  - No `eps` cross-drive patch. That term in validate_simulator.py was a fix
    for the single-frame shortcut; in the proper two-frame treatment the
    leakage of one drive onto the other emerges from J plus the modulation
    factors. If the Phase 2 regression passes without it, it was scaffolding.

Units
-----
Frequencies in MHz, time in ns. Hamiltonians are stored in angular units
(multiplied by 2*pi), matching validate_simulator.py, so a term evolving for
dt nanoseconds carries a factor dt * 1e-3 to convert to the us-scale rad.

Bit ordering
------------
Joint space is tensor(qutrit_control, qutrit_target). State index =
n_levels_target * i_control + i_target; the computational subspace is
[|00>, |01>, |10>, |11>]. In every counts dict the first character is the
control qubit (Q1), the second is the target (Q2).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import numpy as np
import qutip as qt

from HM.simulator.two_qubit_simulator.engine.constants import (
    DT_SAMPLE_NS,
    TWOPI,
)

if TYPE_CHECKING:
    from HM.simulator.two_qubit_simulator.base_classes.device_base import (
        DriveLine,
        Qubit,
    )


class TwoQubitPulseSimulator:
    """Pulse schedule in, counts out.

    run_shot(timeline)  -> final state (qutip.Qobj ket)
    measure(state)      -> counts dict + diagnostics
    """

    def __init__(self, qubits: Sequence[Qubit], J_MHz: float,
                 drive_lines: Sequence[DriveLine],
                 confusion_matrices: tuple[np.ndarray, np.ndarray],
                 n_sub: int = 8, dt_sample_ns: float = DT_SAMPLE_NS):
        assert len(qubits) == 2, "this throwaway sim is hard-wired to 2 qubits"
        self.qubits = list(qubits)
        self.J_MHz = J_MHz
        self.drive_lines = {dl.name: dl for dl in drive_lines}
        self.M1, self.M2 = confusion_matrices   # per-qubit 2x2 readout error
        self.n_sub = n_sub
        self.dt_sample_ns = dt_sample_ns
        self.dims = [q.n_levels for q in qubits] #both have to have the same dims right now. Not a logial restriction but lets keep it for now.
        self.dim = self.dims[0] * self.dims[1]
        self._build_operators()

    # -- static operator construction ---------------------------------------
    def _build_operators(self) -> None:
        n0, n1 = self.dims
        I0, I1 = qt.qeye(n0), qt.qeye(n1)

        # annihilation operators on the joint space, as Qobj
        d0, d1 = qt.destroy(n0), qt.destroy(n1)
        self.a = [qt.tensor(d0, I1), qt.tensor(I0, d1)]
        self.ad = [op.dag() for op in self.a]

        # static drift: ONLY anharmonicities. Each qubit is in its own frame,
        # so the bare frequency terms have rotated away. (alpha/2) a^dag a^dag a a.
        H = 0
        for q, qb in enumerate(self.qubits):
            H += (TWOPI * 0.5 * qb.anharm_MHz
                  * self.ad[q] * self.ad[q] * self.a[q] * self.a[q])
        self.H_drift = H

        # coupling building blocks: J (a0^dag a1 e^{i Delta t} + h.c.)
        self.coupling_op = self.ad[0] * self.a[1]          # a0^dag a1
        self.coupling_op_dag = self.coupling_op.dag()
        # qubit-qubit detuning IS the frame difference -- Delta falls out of
        # the frame choice, no need to pass it separately.
        self.delta_qq_MHz = self.qubits[0].frame_MHz - self.qubits[1].frame_MHz

        # computational subspace indices, ordered |00>,|01>,|10>,|11>
        self.comp_idx = [0, 1, n1, n1 + 1]

    # -- time-dependent Hamiltonian -----------------------------------------
    def _hamiltonian_at(self, t_ns: float,
                        samples: dict[str, complex]) -> qt.Qobj:
        """H(t) as a qutip.Qobj, in angular units (2*pi baked in).

        `samples` is the envelope value of each channel for the 4 ns sample
        the time t_ns falls in (the OPX output is piecewise-constant; only the
        frame modulation below varies within the sample).

        This is the same construction validate_simulator.py uses, generalised
        to two frames: the qubit-qubit detuning rides on the coupling instead
        of sitting as a static term on the control, and each drive line
        carries its own (carrier - frame) modulation.
        """
        H = self.H_drift

        # time-dependent coupling: oscillates at the qubit-qubit detuning
        ph = TWOPI * self.delta_qq_MHz * t_ns * 1e-3
        H = H + TWOPI * self.J_MHz * (self.coupling_op * np.exp(1j * ph)
                                      + self.coupling_op_dag * np.exp(-1j * ph))

        # drive lines: each contributes 0.5 (eps_eff a^dag + c.c.) on its
        # target qubit, with eps_eff = eps * exp(-i 2pi (carrier-frame) t).
        # For a self-drive (carrier == frame) the exponential is 1 and the
        # envelope acts statically. For the CR line (carrier == Q2 freq,
        # target == Q1) it rides the detuning -- that IS cross-resonance.
        for name, eps in samples.items():
            if eps == 0.0:
                continue
            dl = self.drive_lines[name]
            delta = dl.carrier_MHz - self.qubits[dl.target].frame_MHz
            eps_eff = eps * np.exp(-1j * TWOPI * delta * t_ns * 1e-3)
            q = dl.target
            H = H + TWOPI * 0.5 * (eps_eff * self.ad[q]
                                   + np.conj(eps_eff) * self.a[q])
        return H

    # -- evolution ----------------------------------------------------------
    def run_shot(self, timeline: dict[str, np.ndarray],
                 psi0: qt.Qobj | None = None,
                 store_trajectory: bool = False):
        """Evolve a state through one full timeline.

        Fixed-step propagator: each 4 ns sample is split into n_sub finer
        steps, and over each finer step H is treated as constant and applied
        via qutip's Qobj.expm(). This is the same scheme as
        validate_simulator.py (which steps at the full 4 ns); the sub-stepping
        is needed here because the frame modulation oscillates at the
        qubit-qubit detuning (~100 MHz, ~10 ns period), which a 4 ns step
        under-resolves. The ODE solver (sesolve) was tried and fights this
        fast oscillation -- a fixed step below the known fastest timescale is
        both simpler and more reliable here.

        timeline : dict channel_name -> complex envelope array (eps = I + iQ),
                   all channels the same length, on the dt_sample grid.
        psi0     : initial ket as a qutip.Qobj; defaults to |00>.
        Returns the final state (qutip.Qobj ket). If store_trajectory, also
        returns the list of states at every 4 ns sample boundary.
        """
        names = list(timeline.keys())
        if not names:
            raise ValueError("empty timeline")
        unknown = set(names) - set(self.drive_lines)
        if unknown:
            raise KeyError(f"timeline has channels with no DriveLine: {unknown}")
        L = len(timeline[names[0]])
        for nm in names:
            if len(timeline[nm]) != L:
                raise ValueError("all channels must be the same length")

        if psi0 is None:
            psi = qt.basis(self.dims, [0, 0])           # |00>
        else:
            psi = psi0.copy()

        dt_sub_us = (self.dt_sample_ns / self.n_sub) * 1e-3
        trajectory = [psi] if store_trajectory else None

        for k in range(L):
            # OPX output is constant over sample k...
            samples = {nm: timeline[nm][k] for nm in names}
            # ...but the frame modulation is not, so sub-step within the sample
            for s in range(self.n_sub):
                t_mid_ns = (k + (s + 0.5) / self.n_sub) * self.dt_sample_ns
                H = self._hamiltonian_at(t_mid_ns, samples)
                psi = (-1j * H * dt_sub_us).expm() * psi
            if store_trajectory:
                trajectory.append(psi)

        if store_trajectory:
            return psi, trajectory
        return psi

    # -- measurement --------------------------------------------------------
    def measure(self, psi: qt.Qobj, n_shots: int = 8192,
                apply_confusion: bool = True,
                rng: np.random.Generator | None = None
                ) -> tuple[dict[str, int], dict]:
        """Project to the computational subspace, optionally apply the two
        per-qubit confusion matrices, sample n_shots, return counts.

        Leakage out of the computational subspace is reported separately; the
        four computational populations are renormalised before sampling
        (hardware readout has no 'leaked' bin -- leaked population is simply
        misclassified, and for a Bell state it should be small anyway)."""
        rng = rng or np.random.default_rng()
        vec = psi.full().flatten()
        amps = vec[self.comp_idx]
        p_comp = np.abs(amps) ** 2
        leakage = 1.0 - p_comp.sum()
        p = p_comp / p_comp.sum()

        if apply_confusion:
            # joint readout error for independent qubits: M1 (x) M2.
            # ordering [00,01,10,11] matches index = 2*bit_control + bit_target.
            p = np.kron(self.M1, self.M2) @ p

        p = np.clip(p, 0.0, None)
        p /= p.sum()
        draws = rng.choice(4, size=n_shots, p=p)
        labels = ["00", "01", "10", "11"]
        counts = {lab: int(np.sum(draws == i)) for i, lab in enumerate(labels)}
        info = {
            "leakage": float(leakage),
            "probs_ideal": p_comp,          # before confusion
            "probs_measured": p,            # after confusion (if applied)
        }
        return counts, info
