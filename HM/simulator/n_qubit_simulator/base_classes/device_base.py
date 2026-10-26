"""Device records and shared setup for n-qubit simulator experiments."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from HM.simulator.n_qubit_simulator.engine.constants import DT_SAMPLE_NS


_REPO_ROOT = Path(__file__).resolve().parents[4]
_SYSTEM_PARAMETERS = _REPO_ROOT / "Configuration_Files" / "System_Parameters"
_PAPER_CROSS_KERR = Path(__file__).with_name("paper_cross_kerr_khz.json")
_PAPER_DEVICE = Path(__file__).with_name("paper_device.json")
# Edges that keep the J in coupling_vals.json. Every other edge is fitted to
# the paper's cross-Kerr shift at the paper's Table I frequencies.
_LAB_COUPLING_EDGES = ("c1_t2",)
_LAB_QUBIT_IDS = (1, 2)


def _load_json(filename: str) -> dict:
    with (_SYSTEM_PARAMETERS / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


def _load_paper_device() -> dict:
    with _PAPER_DEVICE.open(encoding="utf-8") as handle:
        return json.load(handle)


def pair_cross_kerr_MHz(
    f_i_MHz: float,
    anharm_i_MHz: float,
    f_j_MHz: float,
    anharm_j_MHz: float,
    J_MHz: float,
    n_levels: int = 5,
) -> float:
    """Static ZZ shift E11 - E10 - E01 + E00 of two coupled transmons."""

    lowering = np.diag(np.sqrt(np.arange(1, n_levels)), 1)
    eye = np.eye(n_levels)
    number = lowering.T @ lowering
    a_i = np.kron(lowering, eye)
    a_j = np.kron(eye, lowering)
    n_i = np.kron(number, eye)
    n_j = np.kron(eye, number)
    H = (
        f_i_MHz * n_i
        + 0.5 * anharm_i_MHz * (n_i @ n_i - n_i)
        + f_j_MHz * n_j
        + 0.5 * anharm_j_MHz * (n_j @ n_j - n_j)
        + J_MHz * (a_i.T @ a_j + a_j.T @ a_i)
    )
    energies, vectors = np.linalg.eigh(H)

    def level(occ_i: int, occ_j: int) -> float:
        bare = occ_i * n_levels + occ_j
        return float(energies[np.argmax(np.abs(vectors[bare, :]) ** 2)])

    return level(1, 1) - level(1, 0) - level(0, 1) + level(0, 0)


def fit_exchange_MHz(
    f_i_MHz: float,
    anharm_i_MHz: float,
    f_j_MHz: float,
    anharm_j_MHz: float,
    cross_kerr_MHz: float,
    J_max_MHz: float = 10.0,
) -> float:
    """Return the J whose static ZZ magnitude equals ``cross_kerr_MHz``."""

    target = abs(float(cross_kerr_MHz))

    def residual(J_MHz: float) -> float:
        shift = pair_cross_kerr_MHz(
            f_i_MHz, anharm_i_MHz, f_j_MHz, anharm_j_MHz, J_MHz
        )
        return abs(shift) - target

    if residual(J_max_MHz) < 0.0:
        raise ValueError(
            f"no J below {J_max_MHz} MHz reaches a {1e3 * target:.1f} kHz shift"
        )
    return float(brentq(residual, 1e-6, J_max_MHz, xtol=1e-12))


@dataclass
class Qubit:
    """One truncated transmon.

    `frame_MHz` is its rotating-frame frequency. The initial value equals the
    calibrated qubit frequency.
    """

    qubit_id: int
    anharm_MHz: float
    frame_MHz: float
    n_levels: int = 3
    f_qubit_MHz: float | None = None
    frequency_source: str = ""
    anharmonicity_source: str = ""


@dataclass(frozen=True)
class DriveLine:
    """A physical drive target and fixed carrier frequency."""

    name: str
    target_qubit_id: int
    carrier_MHz: float


@dataclass
class CouplingEdge:
    """One undirected exchange edge in the transmon graph."""

    name: str
    qubit_i: int
    qubit_j: int
    J_MHz: float
    is_calibrated: bool
    parameter_source: str
    enabled: bool = True


class NQubitSimulatorBase:
    """Build a selected subset of physical Q1 through Q6."""

    def __init__(
        self,
        *,
        qubit_ids: tuple[int, ...] = (1, 2, 3, 4, 5, 6),
        n_levels: int = 3,
        levels_by_qubit: dict[int, int] | None = None,
        dt_sample_ns: float = DT_SAMPLE_NS,
    ) -> None:
        requested_ids = tuple(int(qubit_id) for qubit_id in qubit_ids)
        if not requested_ids:
            raise ValueError("select at least one qubit")
        if len(set(requested_ids)) != len(requested_ids):
            raise ValueError(f"qubit_ids contains duplicates: {requested_ids}")
        unknown = set(requested_ids) - set(range(1, 7))
        if unknown:
            raise ValueError(
                f"available physical qubits are 1 through 6; "
                f"got unknown ids {sorted(unknown)}"
            )

        # Tensor-product order is canonical and does not depend on caller order.
        self.qubit_ids = tuple(sorted(requested_ids))
        self.n_levels = int(n_levels)
        if self.n_levels < 2:
            raise ValueError("n_levels must be at least 2")

        overrides = {} if levels_by_qubit is None else dict(levels_by_qubit)
        unknown_override = set(overrides) - set(self.qubit_ids)
        if unknown_override:
            raise ValueError(
                f"levels_by_qubit names qubits that are not selected: "
                f"{sorted(unknown_override)}"
            )
        self.levels_by_qubit = {}
        for qubit_id, n_local in overrides.items():
            n_local = int(n_local)
            if n_local < 2:
                raise ValueError(
                    f"Q{int(qubit_id)} needs at least 2 levels, got {n_local}"
                )
            self.levels_by_qubit[int(qubit_id)] = n_local

        self.dt_sample_ns = float(dt_sample_ns)
        self.qubits = self.build_qubits()
        self.coupling_edges = self.build_coupling_edges()
        self.drive_lines = self.build_drive_lines()
        self._validate_device()

        from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
            NQubitPulseSimulatorDynamiqs,
        )

        self.simulator = NQubitPulseSimulatorDynamiqs(
            qubits=self.qubits,
            coupling_edges=self.coupling_edges,
            drive_lines=self.drive_lines,
            dt_sample_ns=self.dt_sample_ns,
        )
        self.channels = list(self.simulator.channel_names)

    def build_qubits(self) -> list[Qubit]:
        """Return selected qubits in canonical tensor-product order.

        Q1 and Q2 keep the lab frequencies and anharmonicities. Q3 through Q6
        take the paper Table I values, with frequencies shifted by the Q1
        lab-minus-paper offset so paper detunings relative to Q1 are kept.
        """

        frequency_data = _load_json("fq_vals.json")["fq_vals"]
        anharmonicity_data = _load_json("anharmonicities.json")
        paper = _load_paper_device()
        paper_freq = {
            int(qubit_id): float(frequency)
            for qubit_id, frequency in paper["frequency_MHz"].items()
        }
        paper_anharm = {
            int(qubit_id): -abs(float(anharm))
            for qubit_id, anharm in paper["anharmonicity_MHz"].items()
        }
        offset_MHz = float(frequency_data["1"]) - paper_freq[1]

        qubits = []
        for qubit_id in self.qubit_ids:
            if qubit_id in _LAB_QUBIT_IDS:
                f_MHz = float(frequency_data[str(qubit_id)])
                anharm_MHz = -abs(float(anharmonicity_data[str(qubit_id)]))
                frequency_source = f"fq_vals.json:{qubit_id}"
                anharmonicity_source = f"anharmonicities.json:{qubit_id}"
            else:
                f_MHz = paper_freq[qubit_id] + offset_MHz
                anharm_MHz = paper_anharm[qubit_id]
                frequency_source = f"paper_table_i+q1_offset:{qubit_id}"
                anharmonicity_source = f"paper_table_i:{qubit_id}"
            qubits.append(
                Qubit(
                    qubit_id=qubit_id,
                    anharm_MHz=anharm_MHz,
                    frame_MHz=f_MHz,
                    n_levels=self.levels_by_qubit.get(qubit_id, self.n_levels),
                    f_qubit_MHz=f_MHz,
                    frequency_source=frequency_source,
                    anharmonicity_source=anharmonicity_source,
                )
            )
        return qubits

    def build_coupling_edges(self) -> list[CouplingEdge]:
        """Return the odd-to-even exchange edges inside the selection.

        ``c1_t2`` keeps its lab J. Every other edge gets the J that reproduces
        the paper's cross-Kerr shift at the paper's Table I frequencies and
        anharmonicities.
        """

        coupling_data = _load_json("coupling_vals.json")
        paper = _load_paper_device()
        paper_freq = {
            int(qubit_id): float(frequency)
            for qubit_id, frequency in paper["frequency_MHz"].items()
        }
        paper_anharm = {
            int(qubit_id): -abs(float(anharm))
            for qubit_id, anharm in paper["anharmonicity_MHz"].items()
        }
        with _PAPER_CROSS_KERR.open(encoding="utf-8") as handle:
            paper_khz = json.load(handle)["nearest_neighbour_khz"]

        selected = set(self.qubit_ids)
        edges = []
        for control_id in (1, 3, 5):
            for target_id in (2, 4, 6):
                if control_id not in selected or target_id not in selected:
                    continue
                name = f"c{control_id}_t{target_id}"
                if name in _LAB_COUPLING_EDGES:
                    edges.append(
                        CouplingEdge(
                            name,
                            control_id,
                            target_id,
                            float(coupling_data[name]["J_mhz"]),
                            True,
                            f"coupling_vals.json:{name}",
                        )
                    )
                    continue
                J_MHz = fit_exchange_MHz(
                    paper_freq[control_id],
                    paper_anharm[control_id],
                    paper_freq[target_id],
                    paper_anharm[target_id],
                    1e-3 * float(paper_khz[name]),
                )
                edges.append(
                    CouplingEdge(
                        name,
                        control_id,
                        target_id,
                        J_MHz,
                        False,
                        f"paper_zz_fit:{name}",
                    )
                )
        return edges

    def build_drive_lines(self) -> list[DriveLine]:
        """Build self and CR lines contained in the selected subsystem."""

        frequency = {
            qubit.qubit_id: float(qubit.f_qubit_MHz)
            for qubit in self.qubits
        }

        self_drives = [
            DriveLine(
                name=f"q{qubit_id}_drive",
                target_qubit_id=qubit_id,
                carrier_MHz=frequency[qubit_id],
            )
            for qubit_id in self.qubit_ids
        ]

        cr_orientations = (
            (1, 2),
            (1, 4),
            (1, 6),
            (3, 2),
            (3, 4),
            (3, 6),
            (5, 2),
            (5, 4),
            (5, 6),
        )
        cr_drives = [
            DriveLine(
                name=f"cr_c{control_id}_t{target_id}",
                target_qubit_id=control_id,
                carrier_MHz=frequency[target_id],
            )
            for control_id, target_id in cr_orientations
            if control_id in frequency and target_id in frequency
        ]
        return self_drives + cr_drives

    def _validate_device(self) -> None:
        qubit_ids = tuple(qubit.qubit_id for qubit in self.qubits)
        if qubit_ids != self.qubit_ids:
            raise ValueError(
                f"built qubit order {qubit_ids} does not match "
                f"canonical selection {self.qubit_ids}"
            )
        for qubit in self.qubits:
            expected = self.levels_by_qubit.get(qubit.qubit_id, self.n_levels)
            if qubit.n_levels != expected:
                raise ValueError(
                    f"Q{qubit.qubit_id} has {qubit.n_levels} levels, "
                    f"expected {expected}"
                )
            if qubit.n_levels < 2:
                raise ValueError(
                    f"Q{qubit.qubit_id} needs at least 2 levels"
                )

        valid_ids = set(qubit_ids)
        edge_names = [edge.name for edge in self.coupling_edges]
        if len(set(edge_names)) != len(edge_names):
            raise ValueError("coupling edge names must be unique")
        for edge in self.coupling_edges:
            if edge.qubit_i not in valid_ids or edge.qubit_j not in valid_ids:
                raise ValueError(f"edge {edge.name} references an unknown qubit")
            if edge.qubit_i == edge.qubit_j:
                raise ValueError(f"edge {edge.name} is a self-edge")
            if edge.J_MHz < 0.0:
                raise ValueError(f"edge {edge.name} has negative J")
            if not edge.is_calibrated and not edge.parameter_source.startswith(
                ("synthetic_copy:", "paper_zz_fit:")
            ):
                raise ValueError(
                    f"edge {edge.name} has no provenance for its J"
                )

        line_names = [line.name for line in self.drive_lines]
        if len(set(line_names)) != len(line_names):
            raise ValueError("drive line names must be unique")
        expected_line_count = len(self.qubits) + len(self.coupling_edges)
        if len(self.drive_lines) != expected_line_count:
            raise ValueError(
                f"expected {expected_line_count} selected drive lines, "
                f"got {len(self.drive_lines)}"
            )
        if any(line.target_qubit_id not in valid_ids for line in self.drive_lines):
            raise ValueError("a drive line references an unknown qubit")