"""Calibrated c1t2 flat-top on Q1, Q2, Q3, scored like the 2Q simulator.

``C1T2FlatFidelity`` is the experiment class. It subclasses
``NQubitSimulatorBase`` the way ``CR_len_sweep`` subclasses
``TwoQubitSimulatorBase``: the instance is the chip, it stores the pulse
parameters, builds the timeline, and calls its own simulator.

The pulse is the robust-GRAPE seed: 21 MHz flat, 122 ns hold, 16 ns lab rise
and fall, 61 flat knobs, one link sample, echoed with the calibrated Q1 Xπ.
Q1 and Q2 use 4 levels. Q3 uses 3. The target is ZX(-pi/2).

The score is the 2Q process fidelity. A global phase drops out. Local Z is
left in. There is no virtual-Z fit. For a Q3 state that is not a bare level,
the computational block is the overlap with that same Q3 state.

Run from fourqubitv5:

    python -m HM.simulator.n_qubit_simulator.experiments.gaussian_flattop_fidelity
"""

from __future__ import annotations

import dynamiqs as dq
import numpy as np
import jax.numpy as jnp
from dynamiqs import method as dq_method

from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
)
from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    echoed_c1t2_timeline,
    embed_c1t2_timeline,
)
from HM.simulator.two_qubit_simulator.base_classes.device_base import (
    TwoQubitSimulatorBase,
)
from HM.simulator.two_qubit_simulator.optimization.cr_qpt import (
    calibrated_flat_half,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    embed_in_full,
    gate_metrics,
)


COMPUTATIONAL = ((0, 0), (0, 1), (1, 0), (1, 1))
_COMP_EMBED = [0, 1, 2, 3]
_PLUS = "plus"


class C1T2FlatFidelity(NQubitSimulatorBase):
    """Q1, Q2, Q3 chip playing the calibrated c1t2 flat-top."""

    def __init__(
        self,
        *,
        enable_c3_t2: bool = True,
        q3_state: str | int = 0,
        amp_mhz: float = 21.0,
        phase_rad: float = 0.0,
        t_rise_ns: int = 16,
        flat_len_ns: float = 122.0,
        n_flat_knobs: int = 61,
        n_link_samples: int = 1,
        n_active_levels: int = 4,
        target_gate: str = "zx_m90",
    ) -> None:
        super().__init__(
            qubit_ids=(1, 2, 3),
            n_levels=3,
            levels_by_qubit={1: n_active_levels, 2: n_active_levels},
            dt_sample_ns=1.0,
        )
        self.cr_pulse_params = {
            "amp_mhz": float(amp_mhz),
            "phase_rad": float(phase_rad),
            "t_rise_ns": int(t_rise_ns),
            "flat_len_ns": float(flat_len_ns),
            "n_flat_knobs": int(n_flat_knobs),
            "n_link_samples": int(n_link_samples),
        }
        self.n_active_levels = int(n_active_levels)
        self.target_gate = target_gate
        self.q3_state = self._normalize_q3_state(q3_state)
        self.set_edges(
            ("c1_t2", "c3_t2") if enable_c3_t2 else ("c1_t2",)
        )
        self.simulator._integrator_method = dq_method.Tsit5(
            atol=1e-12, rtol=1e-12, max_steps=1_000_000
        )

    @staticmethod
    def _normalize_q3_state(q3_state: str | int) -> str | int:
        if q3_state in (0, 1, "0", "1"):
            return int(q3_state)
        if q3_state in (_PLUS, "+", "0+1"):
            return _PLUS
        raise ValueError(
            f"q3_state must be 0, 1, or {_PLUS!r}, got {q3_state!r}"
        )

    def set_edges(self, enabled_names) -> None:
        enabled_names = set(enabled_names)
        unknown = enabled_names - {edge.name for edge in self.simulator.coupling_edges}
        if unknown:
            raise KeyError(f"chip has no edges {sorted(unknown)}")
        for edge in self.simulator.coupling_edges:
            edge.enabled = edge.name in enabled_names

    def build_pair_timeline(self) -> dict[str, np.ndarray]:
        """Echoed flat-top on q1_drive, q2_drive, and cr_drive."""

        params = self.cr_pulse_params
        half = calibrated_flat_half(
            amp_mhz=params["amp_mhz"],
            phase_rad=params["phase_rad"],
            t_rise_ns=params["t_rise_ns"],
            flat_len_ns=params["flat_len_ns"],
            n_flat_knobs=params["n_flat_knobs"],
            n_link_samples=params["n_link_samples"],
            dt_ns=self.dt_sample_ns,
        )
        timeline = echoed_c1t2_timeline(jnp.asarray(half))
        return {name: np.asarray(waveform) for name, waveform in timeline.items()}

    def build_timeline(self) -> dict:
        return embed_c1t2_timeline(
            {
                name: jnp.asarray(waveform)
                for name, waveform in self.build_pair_timeline().items()
            },
            self.simulator.channel_names,
        )

    def _q3_amplitude(self, occupation: int) -> complex:
        if self.q3_state == _PLUS:
            if occupation in (0, 1):
                return 1.0 / np.sqrt(2.0)
            return 0.0
        return 1.0 if occupation == int(self.q3_state) else 0.0

    def initial_batch(self) -> np.ndarray:
        """Four Q1-Q2 computational states, each tensored with the Q3 state."""

        sim = self.simulator
        psi0 = np.zeros((4, sim.dim, 1), dtype=np.complex128)
        for column, (control, target) in enumerate(COMPUTATIONAL):
            for occupation in range(sim.dims[2]):
                amplitude = self._q3_amplitude(occupation)
                if amplitude == 0.0:
                    continue
                index = sim.basis_index((control, target, occupation))
                psi0[column, index, 0] = amplitude
        return psi0

    def _projected_amplitude(self, state: np.ndarray, control: int, target: int) -> complex:
        sim = self.simulator
        amplitude = 0.0j
        for occupation in range(sim.dims[2]):
            weight = self._q3_amplitude(occupation)
            if weight == 0.0:
                continue
            index = sim.basis_index((control, target, occupation))
            amplitude += np.conj(weight) * state[index]
        return amplitude

    def computational_block(self, finals: np.ndarray) -> np.ndarray:
        """4x4 map that stays in the prepared Q3 state and the Q1-Q2 subspace."""

        block = np.empty((4, 4), dtype=complex)
        for column in range(4):
            for row, (control, target) in enumerate(COMPUTATIONAL):
                block[row, column] = self._projected_amplitude(
                    finals[column], control, target
                )
        return block

    def population_outside_q3_state(self, finals: np.ndarray) -> float:
        """Mean population that left the prepared Q3 state, any Q1-Q2 level."""

        sim = self.simulator
        n0, n1, n2 = sim.dims
        outside = []
        for column in range(4):
            kept = 0.0
            for control in range(n0):
                for target in range(n1):
                    kept += abs(
                        self._projected_amplitude(finals[column], control, target)
                    ) ** 2
            outside.append(1.0 - kept)
        return float(np.mean(outside))

    def evolve(self) -> np.ndarray:
        sim = self.simulator
        timeline = self.build_timeline()
        psi0 = dq.asqarray(jnp.asarray(self.initial_batch()), dims=sim.dims)
        final = sim.run_shot_batch(timeline, psi0)
        return np.asarray(dq.to_jax(final)).reshape(4, sim.dim)

    def score(self) -> dict:
        finals = self.evolve()
        block = self.computational_block(finals)
        metrics = gate_metrics(
            embed_in_full(block, dim=4, comp_indices=_COMP_EMBED),
            gate=self.target_gate,
            comp_indices=_COMP_EMBED,
        )
        return {
            "zx_gate": self.target_gate,
            "process_fidelity": float(metrics["process_fidelity"]),
            "average_gate_fidelity": float(metrics["average_gate_fidelity"]),
            "leakage": float(metrics["leakage"]),
            "q3_left": self.population_outside_q3_state(finals),
            "block": block,
        }


def _local_pauli(dims: tuple[int, ...], position: int, which: str) -> np.ndarray:
    """X, Y, or Z on levels 0 and 1 of one qubit, identity elsewhere."""

    factors = []
    for index, dim in enumerate(dims):
        if index != position:
            factors.append(np.eye(dim, dtype=complex))
            continue
        matrix = np.zeros((dim, dim), dtype=complex)
        if which == "X":
            matrix[0, 1] = matrix[1, 0] = 1.0
        elif which == "Y":
            matrix[0, 1] = -1j
            matrix[1, 0] = 1j
        elif which == "Z":
            matrix[0, 0] = 1.0
            matrix[1, 1] = -1.0
        else:
            raise ValueError(which)
        factors.append(matrix)
    operator = factors[0]
    for factor in factors[1:]:
        operator = np.kron(operator, factor)
    return operator


def xyz_trajectory(
    chip: C1T2FlatFidelity,
    *,
    stride_ns: int = 2,
) -> dict:
    """Bloch components of Q1, Q2, and Q3 for control in |0> and in |1>.

    Q2 starts in |0>. Q3 starts in the chip's prepared state. Expectations
    use X, Y, Z on the {|0>, |1>} subspace, so Z is +1 in |0> and -1 in |1>.
    """

    sim = chip.simulator
    timeline = chip.build_timeline()
    n_samples = len(next(iter(timeline.values())))
    times_ns = np.arange(0, n_samples + 1, int(stride_ns))
    if times_ns[-1] != n_samples:
        times_ns = np.append(times_ns, n_samples)

    psi0 = chip.initial_batch()
    # Columns of COMPUTATIONAL: 00, 01, 10, 11. Keep control |0> and |1>, target |0>.
    selected = psi0[[0, 2]]
    labels = ("Q1 in |0>", "Q1 in |1>")
    result = dq.sesolve(
        sim.hamiltonian(timeline),
        dq.asqarray(jnp.asarray(selected), dims=sim.dims),
        jnp.asarray(times_ns * sim.dt_sample_us),
        method=sim._integrator_method,
        gradient=None,
        options=dq.Options(save_states=True, progress_meter=False),
    )
    states = np.asarray(dq.to_jax(result.states))
    # dynamiqs stacks saved times first: (n_times, n_states, dim, 1).
    if states.shape[0] != times_ns.size:
        states = np.moveaxis(states, 0, 1)
    states = states.reshape(times_ns.size, selected.shape[0], sim.dim)

    curves = {}
    for position, qubit in enumerate(sim.qubits):
        curves[qubit.qubit_id] = {}
        for which in ("X", "Y", "Z"):
            operator = _local_pauli(sim.dims, position, which)
            curves[qubit.qubit_id][which] = np.einsum(
                "tbi,ij,tbj->bt", states.conj(), operator, states
            ).real
    q1 = np.asarray(timeline["q1_drive"])
    cr = np.asarray(timeline["cr_c1_t2"])
    return {
        "times_ns": times_ns,
        "labels": labels,
        "curves": curves,
        "echo_on": np.abs(q1) > 0.0,
        "cr_on": np.abs(cr) > 0.0,
        "q3_state": chip.q3_state,
    }


def save_xyz_figure(
    trajectory: dict,
    path,
    note: str = "",
    spectator_edge: str = "c3_t2 on",
) -> None:
    """Three rows of qubits, three columns of X, Y, Z."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    times = trajectory["times_ns"]
    labels = trajectory["labels"]
    colors = ("tab:blue", "tab:red")
    fig, axes = plt.subplots(3, 3, figsize=(10.5, 7.2), sharex=True, sharey=True)
    q3_name = {0: "|0>", 1: "|1>", "plus": "|+>"}.get(
        trajectory["q3_state"], str(trajectory["q3_state"])
    )
    for row, qubit_id in enumerate((1, 2, 3)):
        for column, which in enumerate(("X", "Y", "Z")):
            ax = axes[row, column]
            for series, label, color in zip(
                trajectory["curves"][qubit_id][which], labels, colors
            ):
                ax.plot(times, series, color=color, lw=1.2, label=label)
            ax.axhline(0.0, color="0.7", lw=0.6)
            ax.set_ylim(-1.05, 1.05)
            ax.grid(alpha=0.25)
            if row == 0:
                ax.set_title(which)
            if column == 0:
                ax.set_ylabel(f"Q{qubit_id}")
            if row == 2:
                ax.set_xlabel("time (ns)")
            if row == 0 and column == 2:
                ax.legend(loc="lower right", fontsize=8, frameon=False)
    fig.suptitle(
        f"c1t2 flat-top, {spectator_edge}, Q3 starts in {q3_name}, Q2 starts in |0>"
        + (f", {note}" if note else ""),
        fontsize=12,
    )
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)


def block_overlap(a: np.ndarray, b: np.ndarray) -> float:
    """|Tr(A† B)|² / 16. Same overlap the 2Q process fidelity uses."""

    return float(abs(np.trace(a.conj().T @ b)) ** 2 / 16.0)


def two_qubit_reference(
    pair_timeline: dict[str, np.ndarray],
    *,
    n_levels: int,
    dt_ns: float,
    envelope: str = "identity",
    target_gate: str = "zx_m90",
) -> dict:
    """Same samples on the 2Q engine. ``envelope`` is the 2Q drive filter."""

    base = TwoQubitSimulatorBase(
        qubit_pair=[1, 2],
        engine="dynamiqs",
        n_levels=n_levels,
        dt_sample_ns=dt_ns,
        envelope=envelope,
    )
    sim = base.simulator
    sim._integrator_method = dq_method.Tsit5(
        atol=1e-12, rtol=1e-12, max_steps=1_000_000
    )
    states = np.asarray(sim.evolve_comp(pair_timeline)).reshape(4, sim.dim)
    indices = [int(index) for index in sim.comp_idx]
    block = np.asarray(states[:, indices], dtype=complex).T
    metrics = gate_metrics(
        embed_in_full(block, dim=4, comp_indices=_COMP_EMBED),
        gate=target_gate,
        comp_indices=_COMP_EMBED,
    )
    return {
        "zx_gate": target_gate,
        "process_fidelity": float(metrics["process_fidelity"]),
        "average_gate_fidelity": float(metrics["average_gate_fidelity"]),
        "leakage": float(metrics["leakage"]),
        "block": block,
    }


def _print_score(name: str, score: dict) -> None:
    print(
        f"{name:32} {score['zx_gate']:7}  "
        f"F_proc {score['process_fidelity']:.6f}  "
        f"F_avg {score['average_gate_fidelity']:.6f}  "
        f"leakage {score['leakage']:.3e}"
    )


def main() -> None:
    chip = C1T2FlatFidelity(enable_c3_t2=False, q3_state=0)
    params = chip.cr_pulse_params
    pair_timeline = chip.build_pair_timeline()
    print(
        f"c1t2 flat-top echoed CR  amp {params['amp_mhz']:.1f} MHz  "
        f"rise {params['t_rise_ns']} ns  hold {params['flat_len_ns']:.0f} ns  "
        f"knobs {params['n_flat_knobs']}  link {params['n_link_samples']}  "
        f"levels {chip.n_active_levels}  "
        f"length {len(pair_timeline['cr_drive'])} ns  target {chip.target_gate}"
    )
    print("metric: 2Q process fidelity, global phase removed, local Z kept")
    print("comparison envelope: identity on both engines")

    reference = two_qubit_reference(
        pair_timeline,
        n_levels=chip.n_active_levels,
        dt_ns=chip.dt_sample_ns,
        target_gate=chip.target_gate,
    )
    _print_score("2Q Q1 Q2", reference)

    idle = chip.score()
    self_overlap = block_overlap(reference["block"], reference["block"])
    idle_overlap = block_overlap(reference["block"], idle["block"])
    block_error = float(np.max(np.abs(reference["block"] - idle["block"])))
    _print_score("Q1 Q2 Q3, c3_t2 off, Q3=|0>", idle)
    print(
        f"{'':32} overlap with 2Q block {idle_overlap:.6f}  "
        f"(2Q block with itself {self_overlap:.6f})  "
        f"max abs block difference {block_error:.3e}  "
        f"left Q3 state {idle['q3_left']:.3e}"
    )

    ground = C1T2FlatFidelity(enable_c3_t2=True, q3_state=0).score()
    _print_score("Q1 Q2 Q3, c3_t2 on, Q3=|0>", ground)
    print(
        f"{'':32} overlap with 2Q block "
        f"{block_overlap(reference['block'], ground['block']):.6f}  "
        f"(2Q block with itself {self_overlap:.6f})  "
        f"left Q3 state {ground['q3_left']:.3e}"
    )

    plus = C1T2FlatFidelity(enable_c3_t2=True, q3_state="plus").score()
    _print_score("Q1 Q2 Q3, c3_t2 on, Q3=|+>", plus)
    print(
        f"{'':32} overlap with 2Q block "
        f"{block_overlap(reference['block'], plus['block']):.6f}  "
        f"(2Q block with itself {self_overlap:.6f})  "
        f"left Q3 state {plus['q3_left']:.3e}"
    )
    print(
        f"{'':32} |+> = (|0> + |1>) / sqrt(2). "
        f"The block is the overlap with that same state."
    )

    filtered = two_qubit_reference(
        pair_timeline,
        n_levels=chip.n_active_levels,
        dt_ns=chip.dt_sample_ns,
        envelope="butterworth4_350mhz",
        target_gate=chip.target_gate,
    )
    city_f_proc = 0.991722
    _print_score("2Q Q1 Q2, butterworth", filtered)
    print(
        f"{'':32} city plot F_proc {city_f_proc:.6f}  "
        f"difference {filtered['process_fidelity'] - city_f_proc:+.3e}"
    )

    assert abs(reference["process_fidelity"] - idle["process_fidelity"]) < 1e-6
    assert block_error < 1e-6
    assert abs(filtered["process_fidelity"] - city_f_proc) < 1e-4
    print("C1T2 FLAT FIDELITY OK")


if __name__ == "__main__":
    main()
