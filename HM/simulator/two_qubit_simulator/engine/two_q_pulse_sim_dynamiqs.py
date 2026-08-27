"""
two_q_pulse_sim_dynamiqs.py
===========================
Dynamiqs/JAX pulse-level engine for the same two-frame transmon model as
``two_q_pulse_sim.py``. Evolution is delegated to ``dq.sesolve`` (state) or
``dq.sepropagator`` (unitary) instead of a hand-rolled sub-step ``expm`` scan.

Hamiltonian structure
---------------------
  - Static drift: anharmonicities only (each qubit in its own frame).
  - Coupling: ``dq.modulated`` carrier phases at the qubit-qubit detuning.
  - Drives: OPX piecewise-constant envelopes indexed inside ``dq.modulated``
    callbacks (equivalent to ``dq.pwc`` envelope × ``dq.modulated`` carrier,
    which dynamiqs does not combine with ``*`` on distinct operators).

Units match the qutip engine: frequencies in MHz, Hamiltonian in angular units
(2π baked in), evolution time in µs (``t_us = t_ns * 1e-3``).

GPU / batching
--------------
Install ``jax[cuda]`` and the same code runs on GPU. ``run_propagator`` uses
``dq.sepropagator``; batched initial states in ``run_shot`` batch over the
Schödinger solves. Double precision is set at import
(``dq.set_precision("double")``), not per instance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

import dynamiqs as dq
from dynamiqs import method as dq_method
import jax.numpy as jnp
import numpy as np

from HM.simulator.two_qubit_simulator.engine.constants import DT_SAMPLE_NS, TWOPI

if TYPE_CHECKING:
    from HM.simulator.two_qubit_simulator.base_classes.device_base import (
        DriveLine,
        Qubit,
    )

def _configure_jax() -> None:
    dq.set_precision("double")
    dq.set_progress_meter(False)

_configure_jax()

class _DynamiqsState:
    """Thin wrapper so experiment code can call ``state.full()`` like QuTiP."""

    def __init__(self, vec: jnp.ndarray | np.ndarray) -> None:
        self._vec = np.asarray(jnp.asarray(vec), dtype=complex).reshape(-1, 1)

    def full(self) -> np.ndarray:
        return self._vec.copy()


class TwoQubitPulseSimulatorDynamiqs:
    """Pulse schedule in, final state out — dynamiqs backend.

    ``run_shot(timeline)``   -> ``_DynamiqsState`` (``.full()`` -> (dim, 1) ndarray)
    ``run_propagator(...)``  -> unitary as (dim, dim) ndarray
    ``measure(state)``         -> counts dict + diagnostics
    """

    def __init__(
        self,
        qubits: Sequence[Qubit],
        J_MHz: float,
        drive_lines: Sequence[DriveLine],
        confusion_matrices: tuple[np.ndarray, np.ndarray],
        n_sub: int = 8,
        dt_sample_ns: float = DT_SAMPLE_NS,
        enable_x64: bool = True,
        progress_meter: bool = False,
        integrator_tol: float = 1e-10,
        integrator_max_steps: int = 1_000_000,
    ):
        assert len(qubits) == 2, "this sim is hard-wired to 2 qubits"
        # Precision is set at import by _configure_jax() (dq.set_precision
        # "double"). Do not toggle jax_enable_x64 here: it is too late if any
        # JAX arrays already exist, and it fights the process-wide default.
        if not enable_x64:
            raise ValueError(
                "enable_x64=False is not supported; dynamiqs engine is always "
                "double precision (see _configure_jax). Omit this kwarg."
            )
        self.qubits = list(qubits)
        self.J_MHz = J_MHz
        self.drive_lines = {dl.name: dl for dl in drive_lines}
        self.M1, self.M2 = confusion_matrices
        self.n_sub = n_sub  # kept for API parity with the qutip engine; unused here
        self.dt_sample_ns = float(dt_sample_ns)
        self.dt_sample_us = self.dt_sample_ns * 1e-3
        self.dims = [q.n_levels for q in qubits]
        self.dim = self.dims[0] * self.dims[1]
        self.set_target_frame(self.qubits[1].frame_MHz)
        self.comp_idx = [0, 1, self.dims[1], self.dims[1] + 1]
        self.channel_names = list(self.drive_lines.keys())
        self._sesolve_options = dq.Options(progress_meter=progress_meter)
        self._seprop_options = dq.Options(
            progress_meter=progress_meter,
            save_propagators=False,
        )
        self._integrator_method = dq_method.Tsit5(
            atol=integrator_tol,
            rtol=integrator_tol,
            max_steps=integrator_max_steps,
        )
        self.gradient = dq.gradient.BackwardCheckpointed()
        self._build_operators()

    def set_target_frame(self, frame1):
        """Install target rotating-frame frequency (float or length-N jax array).

        Lab GRAPE: pass a Python float.
        Robust GRAPE: pass ``lab_f1 + jnp.asarray(shifts)`` once before optimize
        (any ``N >= 1``; coupling / drive coeffs then batch over that axis).
        """
        # Keep jax arrays as jax arrays so coupling / drive coeffs batch.
        if hasattr(frame1, "shape") and getattr(frame1, "ndim", 0) > 0:
            frame1 = jnp.asarray(frame1, dtype=jnp.float64).reshape(-1)
            if frame1.ndim != 1 or frame1.size < 1:
                raise ValueError(
                    f"batched set_target_frame expects shape (N,) with N>=1, "
                    f"got {getattr(frame1, 'shape', None)}"
                )
        else:
            frame1 = float(frame1)

        self.qubits[1].frame_MHz = frame1
        # frame0 stays a lab scalar; broadcast against length-N frame1
        self.delta_qq_MHz = jnp.asarray(self.qubits[0].frame_MHz) - frame1

    def _build_operators(self) -> None:
        n0, n1 = self.dims
        # a0_local, a1_local = dq.destroy(n0), dq.destroy(n1)
        # I0, I1 = jnp.eye(n0), jnp.eye(n1)

        # a0 = jnp.kron(dq.to_jax(a0_local), I1)
        # a1 = jnp.kron(I0, dq.to_jax(a1_local))
        # self.a = [a0, a1]
        # self.ad = [op.conj().T for op in self.a]
        a0, a1 = dq.destroy(*self.dims)
        self.a = [a0, a1]
        self.ad = [op.dag() for op in self.a]

        H_drift = jnp.zeros((self.dim, self.dim), dtype=complex)
        for q, qb in enumerate(self.qubits):
            H_drift = H_drift + (
                TWOPI * 0.5 * qb.anharm_MHz
                * self.ad[q] @ self.ad[q] @ self.a[q] @ self.a[q]
            )
        self.H_drift = dq.asqarray(H_drift)

        self.coupling_op = dq.asqarray(self.ad[0] @ self.a[1])
        self.coupling_op_dag = dq.asqarray(self.a[0] @ self.ad[1])

        self._drive_ops: dict[str, tuple[dq.QArray, dq.QArray]] = {}
        for name, dl in self.drive_lines.items():
            q = dl.target
            self._drive_ops[name] = (
                dq.asqarray(TWOPI * 0.5 * self.ad[q]),
                dq.asqarray(TWOPI * 0.5 * self.a[q]),
            )

    def _validate_timeline(self, timeline: dict[str, np.ndarray]) -> int:
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
        return L

    def _coupling_hamiltonian(self) -> dq.TimeQArray:
        delta = self.delta_qq_MHz
        j_scale = TWOPI * self.J_MHz
        fwd = dq.modulated(
            lambda t: jnp.exp(1j * TWOPI * delta * t),
            j_scale * self.coupling_op,
        )
        bwd = dq.modulated(
            lambda t: jnp.exp(-1j * TWOPI * delta * t),
            j_scale * self.coupling_op_dag,
        )
        return fwd + bwd

    def _drive_hamiltonian(
        self,
        name: str,
        eps_arr: jnp.ndarray,
        discontinuity_ts: jnp.ndarray,
    ) -> dq.TimeQArray:
        dl = self.drive_lines[name]
        delta = dl.carrier_MHz - self.qubits[dl.target].frame_MHz
        ad_op, a_op = self._drive_ops[name]
        n_eps = eps_arr.shape[0]
        dt_us = self.dt_sample_us

        def sample_index(t: float) -> jnp.ndarray:
            i = jnp.floor(t / dt_us).astype(jnp.int32)
            return jnp.clip(i, 0, n_eps - 1)

        def coeff_ad(t: float) -> jnp.ndarray:
            eps = eps_arr[sample_index(t)]
            return eps * jnp.exp(-1j * TWOPI * delta * t)

        def coeff_a(t: float) -> jnp.ndarray:
            eps = eps_arr[sample_index(t)]
            return jnp.conj(eps) * jnp.exp(1j * TWOPI * delta * t)

        ad_term = dq.modulated(
            coeff_ad,
            ad_op,
            discontinuity_ts=discontinuity_ts,
        )
        a_term = dq.modulated(
            coeff_a,
            a_op,
            discontinuity_ts=discontinuity_ts,
        )
        return ad_term + a_term

    def _build_hamiltonian(self, timeline: dict[str, np.ndarray]) -> dq.TimeQArray:
        L = self._validate_timeline(timeline)
        discontinuity_ts = jnp.linspace(0.0, L * self.dt_sample_us, L + 1)

        H = self.H_drift + self._coupling_hamiltonian()
        for name in self.channel_names:
            eps_arr = jnp.array(timeline[name], dtype=complex)
            # if jnp.all(eps_arr == 0):
            #     continue
            H = H + self._drive_hamiltonian(name, eps_arr, discontinuity_ts)
        return H

    def _initial_state(self, psi0: Any | None) -> dq.QArray:
        if psi0 is None:
            return dq.basis(self.dim, 0)
        if hasattr(psi0, "full"):
            vec = np.asarray(psi0.full(), dtype=complex).reshape(self.dim, 1)
        else:
            vec = np.asarray(psi0, dtype=complex).reshape(self.dim, 1)
        return dq.asqarray(jnp.array(vec))

    def _wrap_state(self, state: dq.QArray | jnp.ndarray) -> _DynamiqsState:
        if hasattr(state, "to_jax"):
            vec = dq.to_jax(state)
        else:
            vec = state
        return _DynamiqsState(vec)

    def run_shot(
        self,
        timeline: dict[str, np.ndarray],
        psi0: Any | None = None,
        store_trajectory: bool = False,
    ):
        """Evolve through one timeline via ``dq.sesolve``.

        Returns ``_DynamiqsState`` with ``.full()`` -> (dim, 1) complex ndarray.
        If ``store_trajectory``, also returns a list of states at each OPX sample
        boundary (including the initial state), matching the qutip engine.
        """
        L = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        y0 = self._initial_state(psi0)

        if store_trajectory:
            tsave = jnp.arange(L + 1) * self.dt_sample_us
        else:
            tsave = jnp.array([0.0, L * self.dt_sample_us])

        result = dq.sesolve(
            H,
            y0,
            tsave,
            method=self._integrator_method,
            gradient=self.gradient,
            options=self._sesolve_options,
        )
        psi_final = self._wrap_state(result.states[-1])

        if store_trajectory:
            trajectory = [self._wrap_state(s) for s in result.states]
            return psi_final, trajectory
        return psi_final

    def run_propagator(self, timeline: dict[str, np.ndarray], return_numpy: bool = True):
        """Full Hilbert-space unitary via ``dq.sepropagator`` (JIT/GPU-friendly)."""
        L = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        tsave = jnp.array([0.0, L * self.dt_sample_us])
        result = dq.sepropagator(
            H,
            tsave,
            method=self._integrator_method,
            gradient=self.gradient,
            options=self._seprop_options,
        )
        if return_numpy:
            return np.asarray(dq.to_jax(result.final_propagator))
        else:
            return dq.to_jax(result.final_propagator)

    def run_shot_batch(
        self,
        timeline: dict[str, np.ndarray],
        psi0_batch: jnp.ndarray | np.ndarray,
    ) -> np.ndarray:
        """Evolve a batch of initial states in one ``dq.sesolve`` call.

        ``psi0_batch`` has shape (n_states, dim) or (n_states, dim, 1).
        Returns (n_states, dim, 1) complex ndarray.
        """
        L = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        vecs = np.asarray(psi0_batch, dtype=complex)
        if vecs.ndim == 2:
            vecs = vecs[:, :, np.newaxis]
        y0 = dq.asqarray(jnp.array(vecs))
        tsave = jnp.array([0.0, L * self.dt_sample_us])
        result = dq.sesolve(
            H,
            y0,
            tsave,
            method=self._integrator_method,
            gradient=self.gradient,
            options=self._sesolve_options,
        )
        return np.asarray(dq.to_jax(result.states[:, -1]))

    def measure(
        self,
        psi: _DynamiqsState | Any,
        n_shots: int = 8192,
        apply_confusion: bool = True,
        rng: np.random.Generator | None = None,
    ) -> tuple[dict[str, int], dict]:
        """Project to the computational subspace, sample counts (same as qutip engine)."""
        rng = rng or np.random.default_rng()
        if isinstance(psi, _DynamiqsState):
            vec = psi.full().flatten()
        elif hasattr(psi, "full"):
            vec = np.asarray(psi.full()).flatten()
        else:
            vec = np.asarray(psi, dtype=complex).flatten()

        amps = vec[self.comp_idx]
        p_comp = np.abs(amps) ** 2
        leakage = 1.0 - p_comp.sum()
        p = p_comp / p_comp.sum()

        if apply_confusion:
            p = np.kron(self.M1, self.M2) @ p

        p = np.clip(p, 0.0, None)
        p /= p.sum()
        draws = rng.choice(4, size=n_shots, p=p)
        labels = ["00", "01", "10", "11"]
        counts = {lab: int(np.sum(draws == i)) for i, lab in enumerate(labels)}
        info = {
            "leakage": float(leakage),
            "probs_ideal": p_comp,
            "probs_measured": p,
        }
        return counts, info


    def evolve_comp(self, timeline: dict) -> jnp.ndarray:
        """Evolve computational basis kets ``00,01,10,11`` in one ``sesolve``.

        Returns a JAX array (keeps the AD tape; no ``np.asarray``):

        - ``(4, dim, 1)`` if ``delta_qq_MHz`` is a lab scalar
        - ``(N, 4, dim, 1)`` if ``delta_qq_MHz`` has shape ``(N,)`` (robust batch)
        """

        L = self._validate_timeline(timeline)
        H = self._build_hamiltonian(timeline)
        psi0 = jnp.zeros((4, self.dim, 1), dtype=jnp.complex128)

        for j, idx in enumerate(self.comp_idx):
            psi0 = psi0.at[j, int(idx), 0].set(1.0)

        y0 = dq.asqarray(psi0, dims=tuple(self.dims))

        tsave = jnp.array([0.0, L * self.dt_sample_us])
        result = dq.sesolve(
            H, 
            y0, 
            tsave, 
            method=self._integrator_method,
            gradient=self.gradient,
            options=self._sesolve_options,
        )
        
        psi = dq.to_jax(result.final_state)
        return psi


