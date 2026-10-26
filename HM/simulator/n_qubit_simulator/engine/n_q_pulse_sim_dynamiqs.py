"""Dynamiqs/JAX pulse-level engine for an n-transmon device."""

from __future__ import annotations

from typing import TYPE_CHECKING

import dynamiqs as dq


def _configure_jax() -> None:
    """Set process-wide dynamiqs/JAX defaults before engine arrays exist."""
    dq.set_precision("double")
    dq.set_progress_meter(False)


_configure_jax()

import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.engine.constants import (
    DT_SAMPLE_NS,
    TWOPI,
)

if TYPE_CHECKING:
    from HM.simulator.n_qubit_simulator.base_classes.device_base import (
        CouplingEdge,
        DriveLine,
        Qubit,
    )


class NQubitPulseSimulatorDynamiqs:
    """Global timeline in, final joint state out."""

    def __init__(
        self,
        qubits: list[Qubit],
        coupling_edges: list[CouplingEdge],
        drive_lines: list[DriveLine],
        *,
        dt_sample_ns: float = DT_SAMPLE_NS,
        integrator_tol: float = 1e-10,
        integrator_max_steps: int = 1_000_000,
    ) -> None:
        if not qubits:
            raise ValueError("at least one qubit is required")

        self.qubits = list(qubits)
        self.coupling_edges = list(coupling_edges)
        self.drive_lines = {line.name: line for line in drive_lines}
        self.channel_names = tuple(self.drive_lines)
        self.dt_sample_ns = float(dt_sample_ns)
        self.dt_sample_us = self.dt_sample_ns * 1e-3
        self.dims = tuple(qubit.n_levels for qubit in self.qubits)

        self.dim = 1
        for local_dim in self.dims:
            self.dim *= local_dim

        self._qubit_position = {
            qubit.qubit_id: position
            for position, qubit in enumerate(self.qubits)
        }
        if len(self._qubit_position) != len(self.qubits):
            raise ValueError("qubit IDs must be unique")

        self._integrator_method = dq.method.Tsit5(
            atol=integrator_tol,
            rtol=integrator_tol,
            max_steps=integrator_max_steps,
        )
        self._sesolve_options = dq.Options(
            save_states=False,
            progress_meter=False,
        )
        self._build_operators()

    def _position(self, qubit_id: int) -> int:
        try:
            return self._qubit_position[qubit_id]
        except KeyError as exc:
            raise KeyError(f"engine has no Q{qubit_id}") from exc

    def _build_operators(self) -> None:
        """Build all local operators and the static drift once."""

        self.a = list(dq.destroy(*self.dims))
        self.ad = [operator.dag() for operator in self.a]

        H_drift = 0.0 * (self.ad[0] @ self.a[0])
        for position, qubit in enumerate(self.qubits):
            H_drift = H_drift + (
                0.5
                * TWOPI
                * qubit.anharm_MHz
                * (
                    self.ad[position]
                    @ self.ad[position]
                    @ self.a[position]
                    @ self.a[position]
                )
            )
        self.H_drift = H_drift

        self._drive_ops = {}
        for name, line in self.drive_lines.items():
            position = self._position(line.target_qubit_id)
            self._drive_ops[name] = (
                0.5 * TWOPI * self.ad[position],
                0.5 * TWOPI * self.a[position],
            )

    def _validate_timeline(self, timeline: dict) -> int:
        expected = set(self.channel_names)
        actual = set(timeline)
        missing = expected - actual
        extra = actual - expected
        if missing or extra:
            raise KeyError(
                f"timeline mismatch, missing={sorted(missing)}, "
                f"extra={sorted(extra)}"
            )

        lengths = {name: len(timeline[name]) for name in self.channel_names}
        if len(set(lengths.values())) != 1:
            raise ValueError(f"timeline channel lengths differ: {lengths}")
        length = next(iter(lengths.values()))
        if length <= 0:
            raise ValueError("timeline must contain at least one sample")
        return int(length)

    def _coupling_hamiltonian(self):
        """Build all enabled rotating-frame exchange terms."""

        H = 0.0 * self.H_drift
        for edge in self.coupling_edges:
            if not edge.enabled:
                continue

            i = self._position(edge.qubit_i)
            j = self._position(edge.qubit_j)
            delta_MHz = (
                self.qubits[i].frame_MHz
                - self.qubits[j].frame_MHz
            )
            forward_operator = self.ad[i] @ self.a[j]
            backward_operator = forward_operator.dag()
            scale = TWOPI * edge.J_MHz

            forward = dq.modulated(
                lambda t, delta=delta_MHz: jnp.exp(
                    1j * TWOPI * delta * t
                ),
                scale * forward_operator,
            )
            backward = dq.modulated(
                lambda t, delta=delta_MHz: jnp.exp(
                    -1j * TWOPI * delta * t
                ),
                scale * backward_operator,
            )
            H = H + forward + backward
        return H

    def _drive_hamiltonian(
        self,
        name: str,
        envelope: jnp.ndarray,
        discontinuity_ts: jnp.ndarray,
    ):
        """Build one piecewise-envelope drive with continuous carrier phase."""

        line = self.drive_lines[name]
        position = self._position(line.target_qubit_id)
        delta_MHz = line.carrier_MHz - self.qubits[position].frame_MHz
        ad_operator, a_operator = self._drive_ops[name]
        n_samples = envelope.shape[0]
        dt_us = self.dt_sample_us

        def sample_index(t):
            index = jnp.floor(t / dt_us).astype(jnp.int32)
            return jnp.clip(index, 0, n_samples - 1)

        def coefficient_adjoint(t):
            epsilon = envelope[sample_index(t)]
            return epsilon * jnp.exp(-1j * TWOPI * delta_MHz * t)

        def coefficient_lowering(t):
            epsilon = envelope[sample_index(t)]
            return jnp.conj(epsilon) * jnp.exp(
                1j * TWOPI * delta_MHz * t
            )

        return (
            dq.modulated(
                coefficient_adjoint,
                ad_operator,
                discontinuity_ts=discontinuity_ts,
            )
            + dq.modulated(
                coefficient_lowering,
                a_operator,
                discontinuity_ts=discontinuity_ts,
            )
        )

    def _build_hamiltonian(self, timeline: dict):
        length = self._validate_timeline(timeline)
        discontinuity_ts = jnp.linspace(
            0.0,
            length * self.dt_sample_us,
            length + 1,
        )

        H = self.H_drift + self._coupling_hamiltonian()
        for name in self.channel_names:
            envelope = jnp.asarray(
                timeline[name],
                dtype=jnp.complex128,
            )
            H = H + self._drive_hamiltonian(
                name,
                envelope,
                discontinuity_ts,
            )
        return H

    def hamiltonian(self, timeline: dict):
        """Public Hamiltonian builder used by validation experiments."""
        return self._build_hamiltonian(timeline)

    def run_shot(
        self,
        timeline: dict,
        psi0=None,
    ):
        """Evolve one joint ket and return only the final dynamiqs QArray."""

        length = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        if psi0 is None:
            psi0 = dq.basis(self.dims, (0,) * len(self.dims))
        if psi0.shape != (self.dim, 1):
            raise ValueError(
                f"psi0 has shape {psi0.shape}, expected {(self.dim, 1)}"
            )

        tsave = jnp.asarray(
            [0.0, length * self.dt_sample_us],
            dtype=jnp.float64,
        )
        result = dq.sesolve(
            H,
            psi0,
            tsave,
            method=self._integrator_method,
            gradient=None,
            options=self._sesolve_options,
        )
        return result.final_state

    def run_shot_batch(
        self,
        timeline: dict,
        psi0_batch,
    ):
        """Evolve several joint kets through one timeline in one solve.

        ``psi0_batch`` is a QArray of shape ``(n_states, dim, 1)``. Returns the
        final states with the same shape.
        """

        length = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        if len(psi0_batch.shape) != 3 or tuple(psi0_batch.shape[1:]) != (
            self.dim,
            1,
        ):
            raise ValueError(
                f"psi0_batch has shape {psi0_batch.shape}, "
                f"expected (n_states, {self.dim}, 1)"
            )

        tsave = jnp.asarray(
            [0.0, length * self.dt_sample_us],
            dtype=jnp.float64,
        )
        result = dq.sesolve(
            H,
            psi0_batch,
            tsave,
            method=self._integrator_method,
            gradient=None,
            options=self._sesolve_options,
        )
        return result.final_state

    def measure_state_norm(self, state) -> float:
        """Return the norm of one ket as a Python float."""
        vector = dq.to_jax(state).reshape(-1)
        return float(jnp.vdot(vector, vector).real)

    def basis_index(self, occupations: tuple[int, ...]) -> int:
        """Return the flattened row-major tensor-product basis index."""
        if len(occupations) != len(self.dims):
            raise ValueError("occupation count does not match subsystem count")
        index = 0
        for occupation, local_dim in zip(occupations, self.dims):
            if not 0 <= occupation < local_dim:
                raise ValueError(
                    f"occupation {occupation} is outside dimension {local_dim}"
                )
            index = index * local_dim + occupation
        return index