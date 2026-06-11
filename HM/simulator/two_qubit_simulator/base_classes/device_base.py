"""
device_base.py
==============
Device description + shared scaffolding for the two-qubit pulse-level
simulation experiments (Rabi, CR length sweep, ...).

``Qubit`` and ``DriveLine`` describe the device the engine simulates; the
engine itself (``engine/two_q_pulse_sim.py``) is deliberately ignorant of
where those numbers come from.

Every experiment builds the same set of objects from the lab calibration JSONs
for a given qubit pair: the two qutrits, the three drive lines (q1 self-drive,
q2 self-drive and the CR drive), the readout confusion matrices and the
``TwoQubitPulseSimulator`` itself. That common setup used to be copy-pasted into
each experiment class; it now lives here so the experiment classes only have to
add their own pulse parameters and sweep logic.
"""

from dataclasses import dataclass, field

import numpy as np

from Configuration_Files.config_dictionaries import *
from HM.simulator.two_qubit_simulator.engine.constants import DT_SAMPLE_NS


# ---------------------------------------------------------------------------
# Device description objects (consumed by the engines)
# ---------------------------------------------------------------------------
@dataclass
class Qubit:
    """A transmon. frame_MHz is the rotating-frame frequency = its own
    frequency. Only differences between qubits' frame_MHz ever matter, so the
    absolute value is a free choice of reference."""
    anharm_MHz: float          # negative, e.g. -330.0
    frame_MHz: float
    n_levels: int = 3
    f_qubit_MHz: float = None
    ro_fidelity_matrix: np.ndarray = field(
        default_factory=lambda: np.array([[1.0, 0.0], [0.0, 1.0]]))


@dataclass
class DriveLine:
    """A (physical line, carrier) pair. `target` is the index of the qubit the
    line physically drives. `carrier_MHz` is the frequency the line's envelope
    rides on. The detuning seen in the target's frame is carrier - frame."""
    name: str
    target: int                # 0 (control) or 1 (target)
    carrier_MHz: float


def _resolve_engine(engine: str):
    """Import the requested engine class lazily, so that e.g. a missing
    dynamiqs/jax install doesn't break the qutip path (and vice versa)."""
    if engine == "qutip":
        from HM.simulator.two_qubit_simulator.engine.two_q_pulse_sim import (
            TwoQubitPulseSimulator,
        )
        return TwoQubitPulseSimulator
    if engine == "dynamiqs":
        from HM.simulator.two_qubit_simulator.engine.two_q_pulse_sim_dynamiqs import (
            TwoQubitPulseSimulatorDynamiqs,
        )
        return TwoQubitPulseSimulatorDynamiqs
    raise ValueError(f"unknown engine {engine!r}; expected 'qutip' or 'dynamiqs'")


class TwoQubitSimulatorBase:
    """Base class wiring up a two-qubit pulse simulator for a qubit pair.

    Subclasses should call ``super().__init__(qubit_pair, **kwargs)`` and then
    set up whatever pulse parameters / sweep arrays their experiment needs.

    Shared kwargs:
        engine (str):          simulation backend, 'qutip' or 'dynamiqs'. Default 'qutip'.
        echoed_cr (bool):      flag carried by the CR experiments. Default False.
        nshots (int):          shots used when sampling measurement counts. Default 8192.
        dt_sample_ns (float):  simulation clock in ns. Default 4 (OPX clock).
    """

    def __init__(self, qubit_pair=[1, 2], **kwargs):
        self.q_pair = qubit_pair
        self.engine = kwargs.get("engine", "qutip")
        self.echoed_cr = kwargs.get("echoed_cr", False)
        self.dt_sample_ns = float(kwargs.get("dt_sample_ns", DT_SAMPLE_NS))
        self.n_sub = int(kwargs.get("n_sub", 8))
        self.drive_lines = self.build_drive_lines(self.q_pair)
        self.qubits = self.build_qubits(self.q_pair)
        self.confusion_matrices = self.build_confusion_matrices(self.q_pair)
        self.J_MHz = coupling_vals[f"c{self.q_pair[0]}_t{self.q_pair[1]}"]["J_mhz"]
        self.nshots = int(kwargs.get("nshots", 8192))
        simulator_cls = _resolve_engine(self.engine)
        self.simulator = simulator_cls(
            qubits=self.qubits,
            J_MHz=self.J_MHz,
            drive_lines=self.drive_lines,
            confusion_matrices=self.confusion_matrices,
            dt_sample_ns=self.dt_sample_ns,
            n_sub=self.n_sub,
        )
        self.channels = list[str](self.simulator.drive_lines)

    def delta_qq_MHz(self, q_pair):
        """Qubit-qubit detuning f_control - f_target in MHz."""
        return fq_vals["fq_vals"][f"{q_pair[0]}"] - fq_vals["fq_vals"][f"{q_pair[1]}"]

    def build_drive_lines(self, q_pair):
        DELTA_QQ_MHZ = self.delta_qq_MHz(q_pair)
        return [
            DriveLine(name="q1_drive", target=0, carrier_MHz=0.0),
            DriveLine(name="q2_drive", target=1, carrier_MHz=-DELTA_QQ_MHZ),
            DriveLine(name="cr_drive", target=0, carrier_MHz=-DELTA_QQ_MHZ),
        ]

    def build_qubits(self, q_pair):
        DELTA_QQ_MHZ = self.delta_qq_MHz(q_pair)
        ALPHA1_MHZ = anharmonicities[f"{q_pair[0]}"]
        ALPHA2_MHZ = anharmonicities[f"{q_pair[1]}"]
        return [
            Qubit(anharm_MHz=ALPHA1_MHZ, frame_MHz=0, n_levels=3,
                  f_qubit_MHz=fq_vals["fq_vals"][f"{q_pair[0]}"],
                  ro_fidelity_matrix=np.array([[1.0, 0.0], [0.0, 1.0]])),
            Qubit(anharm_MHz=ALPHA2_MHZ, frame_MHz=-DELTA_QQ_MHZ, n_levels=3,
                  f_qubit_MHz=fq_vals["fq_vals"][f"{q_pair[1]}"],
                  ro_fidelity_matrix=np.array([[1.0, 0.0], [0.0, 1.0]])),
        ]

    def build_confusion_matrices(self, q_pair):
        return [
            np.array([[1.0, 0.0], [0.0, 1.0]]),
            np.array([[1.0, 0.0], [0.0, 1.0]]),
        ]
