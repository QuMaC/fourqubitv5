"""
cr_pulse_evolution_crcopy.py
============================
CR pulse-evolution experiment backed by ``engine/CRcopy.py``.

This mirrors the output schema of ``cr_pulse_evolution.py`` (same plots / JSON
keys) but runs time evolution through ``CRcopy.processor`` instead of the newer
timeline-native engines.

Important modeling scope (current implementation)
-------------------------------------------------
- No explicit cancellation tone support.
- No explicit target-line drive while CR is active.
- Echoed CR is supported for the common control-line echo sequence
  ``+CR -> Xpi(control) -> -CR -> Xpi(control)``.

These constraints match the current use case where classical cross-talk /
cancellation tones are not enabled.
"""

from __future__ import annotations

import json
import os
from typing import Iterable

import numpy as np
import qutip as qt

from Configuration_Files.config_dictionaries import (
    amp_scale,
    anharmonicities,
    coupling_vals,
    cr_tail_ns,
    drag_dict,
    fq_vals,
    pi_len_ns,
    pi_rise_grft_ns,
)
from HM.simulator.two_qubit_simulator.engine.constants import TWOPI
from HM.simulator.two_qubit_simulator.engine.pulses import (
    Timeline,
    calibrate_f_rabi_per_opx1,
    cr_rise_fall_flat_top,
    drag_grft_envelope_mhz,
    load_waveform_npz,
)
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import pauli_on_levels
from HM.simulator.two_qubit_simulator.experiments.plotting import (
    COMP_LABELS as _COMP_LABELS,
    MEDIA_DIR,
    _date_tag,
    _media_path,
    plot_populations,
    plot_xyz,
    save_bloch_gif,
    save_bloch_png,
)

_CHANNELS = ("q1_drive", "q2_drive", "cr_drive")
_AMP_MHZ_TO_RAD_PER_NS = TWOPI * 1e-3
_TOL = 1e-12

# Drive-convention factor. CRcopy's drive term is pulse(t)*a + conj(pulse)*a^dag
# (no 1/2), whereas the envelopes here (and two_q_pulse_sim) use the standard
# 0.5*(eps*a^dag + conj(eps)*a) RWA convention where eps is the Rabi rate in MHz.
# Without this factor the calibrated X180 becomes a 2*pi (no-op) rotation and the
# CR drive is 2x too strong, so the same pulse parameters do NOT transfer.
_DRIVE_CONVENTION_FACTOR = 0.5


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return _to_jsonable(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def finalize_timeline(timeline: Timeline | dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Return a channel -> envelope dict."""
    if isinstance(timeline, Timeline):
        return timeline.finalize()
    if not isinstance(timeline, dict):
        raise TypeError(
            "timeline must be a Timeline builder or a finalized dict[str, ndarray]"
        )
    return timeline


def _timeline_length(timeline: dict[str, np.ndarray]) -> int:
    if not timeline:
        raise ValueError("empty timeline")
    lengths = {len(wf) for wf in timeline.values()}
    if len(lengths) != 1:
        raise ValueError(f"all channels must share length; got {lengths}")
    return lengths.pop()


def _pauli_ops(n0: int, n1: int):
    I0, I1 = qt.qeye(n0), qt.qeye(n1)
    ops = {}
    for which in ("X", "Y", "Z"):
        P0 = pauli_on_levels(which, n0)
        P1 = pauli_on_levels(which, n1)
        ops[f"ctrl_{which}"] = qt.tensor(P0, I1)
        ops[f"tgt_{which}"] = qt.tensor(I0, P1)
    return ops


def _observables_at_step(psi, n0: int, n1: int, comp_idx: list[int], pauli_ops):
    vec = np.asarray(psi.full(), dtype=complex).reshape(-1)

    comp_amps = vec[comp_idx]
    comp_pops = np.abs(comp_amps) ** 2

    level_pops = (np.abs(vec) ** 2).reshape(n0, n1)
    level_labels = [f"|{i}{j}⟩" for i in range(n0) for j in range(n1)]

    obs = {
        "state_vector": vec,
        "comp_amplitudes": comp_amps,
        "comp_populations": comp_pops,
        "level_populations": level_pops.reshape(-1),
        "level_labels": level_labels,
    }
    for key, op in pauli_ops.items():
        obs[key] = float(np.real(qt.expect(op, psi)))
    return obs


def _stack_observables(steps):
    keys = [k for k in steps[0].keys() if k not in ("level_labels",)]
    out = {}
    complex_keys = {"state_vector", "comp_amplitudes"}
    for key in keys:
        if key in complex_keys:
            out[key] = np.stack([s[key] for s in steps], axis=0)
        elif key in ("comp_populations", "level_populations"):
            out[key] = np.stack([s[key] for s in steps], axis=0)
        else:
            out[key] = np.array([s[key] for s in steps], dtype=float)
    out["level_labels"] = steps[0]["level_labels"]
    return out


def _combined_control_pulse(t, args):
    """Effective control-line pulse in the CRcopy drive frame.

    The CRcopy solver accepts one driven operator (control line) and one complex
    envelope. We combine the self-drive and CR carrier contributions into that
    one envelope in the chosen drive frame:

        eps_eff(t) = eps_q1[k] + eps_cr[k] * exp(+i * (w_cr - w_drive) * t)

    where k is the sample index for time t.
    """
    dt_ns = args["dt_ns"]
    n_samples = args["n_samples"]
    idx = int(np.floor(float(t) / dt_ns + 1e-12))
    if idx < 0:
        idx = 0
    if idx >= n_samples:
        idx = n_samples - 1

    eps_q1 = args["eps_q1"][idx]
    eps_cr = args["eps_cr"][idx]
    dw_cr = args["dw_cr"]
    return eps_q1 + eps_cr * np.exp(+1j * dw_cr * float(t))


def save_results_json(results, filename=None, include_state_vector=True):
    """Dump observables (and optionally full state vectors) to JSON."""
    filename = _media_path(filename or f"cr_pulse_evolution_crcopy_{_date_tag()}.json")
    payload = {
        "times_ns": results["times_ns"],
        "total_duration_ns": results["total_duration_ns"],
        "dt_sample_ns": results["dt_sample_ns"],
        "n_samples": results["n_samples"],
        "comp_labels": results["comp_labels"],
        "comp_indices": results["comp_indices"],
    }
    for ctrl in (0, 1):
        key = f"control_{ctrl}"
        if key not in results:
            continue
        data = results[key]
        block = {
            "comp_populations": data["comp_populations"],
            "comp_amplitudes": data["comp_amplitudes"],
            "level_populations": data["level_populations"],
            "level_labels": data["level_labels"],
        }
        for q in ("ctrl", "tgt"):
            for comp in ("X", "Y", "Z"):
                block[f"{q}_{comp}"] = data[f"{q}_{comp}"]
        if include_state_vector and "state_vector" in data:
            block["state_vector"] = data["state_vector"]
        payload[key] = block

    with open(filename, "w") as f:
        json.dump(_to_jsonable(payload), f, indent=2)
    print(f"Saved {filename}")
    return filename


def plot_and_save_all(
    results,
    *,
    tag="",
    save_json=True,
    bloch_qubit="tgt",
    gif_fps=12,
    max_gif_frames=120,
):
    """Write population, XYZ, Bloch PNG/GIF, and optional JSON to sim_media."""
    suffix = f"_{tag}_{_date_tag()}" if tag else f"_{_date_tag()}"
    paths = {
        "populations": plot_populations(
            results, f"cr_pulse_evolution_crcopy_populations{suffix}.png"
        ),
        "xyz": plot_xyz(results, f"cr_pulse_evolution_crcopy_xyz{suffix}.png"),
        "bloch_png": save_bloch_png(
            results, f"cr_pulse_evolution_crcopy_bloch{suffix}.png", qubit=bloch_qubit
        ),
        "bloch_gif": save_bloch_gif(
            results,
            f"cr_pulse_evolution_crcopy_bloch{suffix}.gif",
            qubit=bloch_qubit,
            fps=gif_fps,
            max_gif_frames=max_gif_frames,
        ),
    }
    if save_json:
        paths["json"] = save_results_json(
            results, f"cr_pulse_evolution_crcopy{suffix}.json"
        )
    return paths


class CR_pulse_evolution_CRcopy:
    """CR pulse evolution with ``CRcopy.processor``.

    The external API mirrors ``CR_pulse_evolution``:
      - ``build_timeline`` / ``build_arb_timeline``
      - ``run``
      - ``results`` + optional plots under ``sim_media``
    """

    _ARB_KWARGS = (
        "arb_npz_path",
        "arb_mode",
        "arb_channel",
        "arb_key",
        "arb_i_key",
        "arb_q_key",
        "arb_amp_scale",
        "arb_phase_rad",
    )

    def __init__(self, qubit_pair=(1, 2), flat_len_ns=None, **kwargs):
        self.q_pair = list(qubit_pair)
        if len(self.q_pair) != 2:
            raise ValueError(f"expected exactly two qubits, got {self.q_pair!r}")

        self.dt_sample_ns = float(kwargs.get("dt_sample_ns", 1.0))
        self.n_levels = int(kwargs.get("n_levels", 3))
        self.echoed_cr = bool(kwargs.get("echoed_cr", False))
        # Kept for config/API parity with the timeline-native scripts.
        self.n_sub = int(kwargs.get("n_sub", 2))

        self.flat_len_ns = flat_len_ns
        self.file_tag = kwargs.get("file_tag", "")
        self.bloch_gif_fps = int(kwargs.get("bloch_gif_fps", 12))
        self.max_gif_frames = int(kwargs.get("max_gif_frames", 120))

        self.echo_qubit = int(kwargs.get("echo_qubit", self.q_pair[0]))
        if self.echoed_cr and self.echo_qubit != self.q_pair[0]:
            raise ValueError(
                "CRcopy pulse-evolution currently supports echoed CR only when "
                "the echo Xpi is on the control qubit."
            )

        default_cr_pulse_params = {
            "amp_mhz": 65.0,
            "t_rise_ns": int(cr_tail_ns),
            "t_flat_ns": None,
            "phase_rad": 0.0,
        }
        self.cr_pulse_params = {
            **default_cr_pulse_params,
            **kwargs.get("cr_pulse_params", {}),
        }
        if "phase_rad" in kwargs:
            self.cr_pulse_params["phase_rad"] = float(kwargs["phase_rad"])

        q = str(self.q_pair[0])
        default_x_pi_params = {
            "amp_scale_x180": float(amp_scale[q]["X180"]),
            "length_ns": int(pi_len_ns[q]),
            "rise_ns": int(pi_rise_grft_ns),
            "alpha": float(drag_dict[q]["alpha"]),
            "det": float(drag_dict[q]["det"]),
            "anharm_hz": float(anharmonicities[q]) * 1e6,
        }
        self.x_pi_pulse_params = {
            **default_x_pi_params,
            **kwargs.get("x_pi_pulse_params", {}),
        }
        override = kwargs.get("f_rabi_per_opx1", None)
        self.f_rabi_overridden = override is not None
        self.f_rabi_per_opx1 = (
            float(override)
            if self.f_rabi_overridden
            else self._calibrate_x_pi_amp_to_mhz()
        )

        arb_opts = {name: kwargs.pop(name) for name in self._ARB_KWARGS if name in kwargs}
        self.arb_npz_path = arb_opts.get("arb_npz_path")
        self.arb_mode = str(arb_opts.get("arb_mode", "echoed_cr_half"))
        self.arb_channel = str(arb_opts.get("arb_channel", "cr_drive"))
        self.arb_key = arb_opts.get("arb_key")
        self.arb_i_key = arb_opts.get("arb_i_key")
        self.arb_q_key = arb_opts.get("arb_q_key")
        self.arb_amp_scale = float(arb_opts.get("arb_amp_scale", 1.0))
        self.arb_phase_rad = float(arb_opts.get("arb_phase_rad", 0.0))

        os.makedirs(MEDIA_DIR, exist_ok=True)

        self.channels = list(_CHANNELS)
        self.processor = self._build_processor()
        self.dims = [self.n_levels, self.n_levels]
        self.comp_idx = [0, 1, self.n_levels, self.n_levels + 1]
        self.results = None

    def _calibrate_x_pi_amp_to_mhz(self):
        p = self.x_pi_pulse_params
        return calibrate_f_rabi_per_opx1(
            p["amp_scale_x180"], p["length_ns"], p["rise_ns"]
        )

    def _build_processor(self):
        try:
            from HM.simulator.two_qubit_simulator.engine.CRcopy import (
                processor as crcopy_processor,
            )
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Failed to import CRcopy.processor. "
                "Make sure CRcopy dependencies are installed in this environment "
                "(notably 'sympy' and 'tabulate')."
            ) from exc

        c_label = str(self.q_pair[0])
        t_label = str(self.q_pair[1])

        pair_key = f"c{self.q_pair[0]}_t{self.q_pair[1]}"
        if pair_key in coupling_vals:
            J_MHz = float(coupling_vals[pair_key]["J_mhz"])
        else:
            rev_key = f"c{self.q_pair[1]}_t{self.q_pair[0]}"
            if rev_key not in coupling_vals:
                raise KeyError(
                    f"could not find coupling entry for {pair_key} (or {rev_key})"
                )
            J_MHz = float(coupling_vals[rev_key]["J_mhz"])

        f_ctrl_MHz = float(fq_vals["fq_vals"][c_label])
        f_tgt_MHz = float(fq_vals["fq_vals"][t_label])
        anh_ctrl_MHz = -abs(float(anharmonicities[c_label]))
        anh_tgt_MHz = -abs(float(anharmonicities[t_label]))

        self.J_MHz = J_MHz
        self.delta_qq_MHz = f_ctrl_MHz - f_tgt_MHz
        self._w_ctrl = _AMP_MHZ_TO_RAD_PER_NS * f_ctrl_MHz
        self._w_tgt = _AMP_MHZ_TO_RAD_PER_NS * f_tgt_MHz
        self._w_cr = self._w_tgt

        w = _AMP_MHZ_TO_RAD_PER_NS * np.array([f_ctrl_MHz, f_tgt_MHz], dtype=float)
        anh = _AMP_MHZ_TO_RAD_PER_NS * np.array([anh_ctrl_MHz, anh_tgt_MHz], dtype=float)
        J = np.array([[0.0, J_MHz], [J_MHz, 0.0]], dtype=float) * _AMP_MHZ_TO_RAD_PER_NS
        control_target = np.array([[0, 1], [0, 0]], dtype=int)

        pr = crcopy_processor(
            N=2,
            N_l=self.n_levels,
            w=w,
            anh=anh,
            J=J,
            control_target=control_target,
        )
        pr.schrodinger_progress_bar = None
        pr.progress_bar = None
        return pr

    def build_x_pi(self):
        """Calibrated complex d_X180 envelope (MHz) for the control qubit."""
        p = self.x_pi_pulse_params
        return drag_grft_envelope_mhz(
            amplitude=p["amp_scale_x180"],
            length_ns=p["length_ns"],
            rise_ns=p["rise_ns"],
            anharm_hz=p["anharm_hz"],
            alpha=p["alpha"],
            detuning=p["det"],
            f_rabi_per_opx1=self.f_rabi_per_opx1,
        )

    def build_timeline(self, flat_len_ns=None) -> dict[str, np.ndarray]:
        """Return a finalized timeline for the configured CR pulse."""
        if flat_len_ns is None:
            flat_len_ns = self.flat_len_ns
        if flat_len_ns is None:
            flat_len_ns = self.cr_pulse_params.get("t_flat_ns", None)
        if flat_len_ns is None:
            raise ValueError("flat_len_ns must be set on the instance or passed here")

        tl = Timeline(self.channels, dt_ns=self.dt_sample_ns)
        phase_rad = float(self.cr_pulse_params.get("phase_rad", 0.0))
        cr_amp = self.cr_pulse_params["amp_mhz"] * np.exp(1j * phase_rad)

        if self.echoed_cr:
            x_pi = self.build_x_pi()
            cr_plus = cr_rise_fall_flat_top(
                amp=cr_amp,
                t_flat_ns=flat_len_ns,
                t_rise_ns=self.cr_pulse_params["t_rise_ns"],
                dt_ns=self.dt_sample_ns,
            )
            cr_minus = cr_rise_fall_flat_top(
                amp=-cr_amp,
                t_flat_ns=flat_len_ns,
                t_rise_ns=self.cr_pulse_params["t_rise_ns"],
                dt_ns=self.dt_sample_ns,
            )
            t = tl.add("cr_drive", start_ns=0.0, waveform=cr_plus)
            t = tl.add("q1_drive", start_ns=t, waveform=x_pi)
            t = tl.add("cr_drive", start_ns=t, waveform=cr_minus)
            tl.add("q1_drive", start_ns=t, waveform=x_pi)
            return tl.finalize()

        cr = cr_rise_fall_flat_top(
            amp=cr_amp,
            t_flat_ns=flat_len_ns,
            t_rise_ns=self.cr_pulse_params["t_rise_ns"],
            dt_ns=self.dt_sample_ns,
        )
        tl.add("cr_drive", start_ns=0.0, waveform=cr)
        return tl.finalize()

    def build_arb_timeline(self, npz_path=None, *, mode=None) -> dict[str, np.ndarray]:
        """Build a timeline from an arbitrary waveform stored in an ``.npz`` file."""
        npz_path = npz_path or self.arb_npz_path
        if npz_path is None:
            raise ValueError("arb_npz_path must be set (or pass npz_path here)")
        mode = str(mode or self.arb_mode)

        if mode == "echoed_cr_half":
            if not self.echoed_cr:
                raise ValueError("arb_mode='echoed_cr_half' requires echoed_cr=True")
            cr_half = load_waveform_npz(
                npz_path, key=self.arb_key, i_key=self.arb_i_key, q_key=self.arb_q_key
            )
            if self.arb_amp_scale != 1.0 or self.arb_phase_rad != 0.0:
                cr_half = cr_half * (
                    self.arb_amp_scale * np.exp(1j * self.arb_phase_rad)
                )
            x_pi = self.build_x_pi()
            tl = Timeline(self.channels, dt_ns=self.dt_sample_ns)
            t = tl.add("cr_drive", start_ns=0.0, waveform=cr_half)
            t = tl.add("q1_drive", start_ns=t, waveform=x_pi)
            t = tl.add("cr_drive", start_ns=t, waveform=-cr_half)
            tl.add("q1_drive", start_ns=t, waveform=x_pi)
            return tl.finalize()

        if mode == "single":
            tl = Timeline(self.channels, dt_ns=self.dt_sample_ns)
            tl.add_arb(
                self.arb_channel,
                npz_path,
                start_ns=0.0,
                key=self.arb_key,
                i_key=self.arb_i_key,
                q_key=self.arb_q_key,
                amp_scale=self.arb_amp_scale,
                phase_rad=self.arb_phase_rad,
            )
            return tl.finalize()

        raise ValueError(
            f"unknown arb_mode {mode!r}; expected 'echoed_cr_half' or 'single'"
        )

    def _validate_ctrl_states(self, ctrl_states: Iterable[int]):
        out = []
        for ctrl in ctrl_states:
            if ctrl not in (0, 1):
                raise ValueError(f"unsupported ctrl_state {ctrl!r}; expected 0 or 1")
            out.append(int(ctrl))
        return tuple(out)

    def _timeline_to_solver_args(self, timeline: dict[str, np.ndarray]) -> dict:
        n_samples = _timeline_length(timeline)
        if n_samples <= 0:
            raise ValueError("timeline has zero samples")

        allowed = set(_CHANNELS)
        for ch, wf in timeline.items():
            if ch not in allowed and np.any(np.abs(wf) > _TOL):
                raise ValueError(
                    f"timeline channel {ch!r} is unsupported by CRcopy path"
                )

        q1 = np.asarray(
            timeline.get("q1_drive", np.zeros(n_samples, dtype=complex)),
            dtype=complex,
        )
        q2 = np.asarray(
            timeline.get("q2_drive", np.zeros(n_samples, dtype=complex)),
            dtype=complex,
        )
        cr = np.asarray(
            timeline.get("cr_drive", np.zeros(n_samples, dtype=complex)),
            dtype=complex,
        )

        if np.any(np.abs(q2) > _TOL):
            raise ValueError(
                "q2_drive is non-zero. This CRcopy experiment currently models only "
                "control-line drives (no explicit target-line/cancellation tones)."
            )

        drive_scale = _DRIVE_CONVENTION_FACTOR * _AMP_MHZ_TO_RAD_PER_NS
        return {
            "dt_ns": self.dt_sample_ns,
            "n_samples": n_samples,
            "eps_q1": drive_scale * q1,
            "eps_cr": drive_scale * cr,
            "dw_cr": self._w_cr - self._w_ctrl,
        }

    def evolve_timeline(
        self,
        timeline: Timeline | dict[str, np.ndarray],
        *,
        ctrl_states: tuple[int, ...] = (0, 1),
        store_full_state_vector: bool = True,
    ):
        """Evolve one timeline for each control initial state; return time series."""
        tl = finalize_timeline(timeline)
        n_samples = _timeline_length(tl)
        solver_args = self._timeline_to_solver_args(tl)
        times_ns = np.arange(n_samples + 1, dtype=float) * self.dt_sample_ns

        ctrl_states = self._validate_ctrl_states(ctrl_states)
        init_vectors = [(ctrl, 0) for ctrl in ctrl_states]
        key_map = {ctrl: "".join(str(v) for v in vec) for ctrl, vec in zip(ctrl_states, init_vectors)}

        trajectories = self.processor.get_out_vectors(
            ctrl=0,
            tgt=1,
            vectors=init_vectors,
            drive_frequency=self._w_ctrl,
            pulse_shape=_combined_control_pulse,
            t=times_ns,
            args=solver_args,
            return_evolution=True,
        )

        pauli_ops = _pauli_ops(self.dims[0], self.dims[1])
        out = {
            "times_ns": times_ns,
            "total_duration_ns": float(times_ns[-1]),
            "dt_sample_ns": self.dt_sample_ns,
            "n_samples": n_samples,
            "comp_labels": [
                _COMP_LABELS[self.comp_idx.index(i)] if i in self.comp_idx else f"idx{i}"
                for i in self.comp_idx
            ],
            "comp_indices": list(self.comp_idx),
        }

        for ctrl in ctrl_states:
            states = trajectories[key_map[ctrl]]
            steps = [
                _observables_at_step(
                    psi,
                    n0=self.dims[0],
                    n1=self.dims[1],
                    comp_idx=self.comp_idx,
                    pauli_ops=pauli_ops,
                )
                for psi in states
            ]
            stacked = _stack_observables(steps)
            if not store_full_state_vector:
                stacked.pop("state_vector", None)
            out[f"control_{ctrl}"] = stacked
        return out

    def run(
        self,
        timeline: Timeline | dict[str, np.ndarray] | None = None,
        *,
        flat_len_ns=None,
        plot=True,
        save_json=True,
    ):
        """Evolve one timeline and optionally write plots/JSON to ``sim_media``."""
        used_arb = False
        if timeline is None:
            if self.arb_npz_path is not None:
                timeline = self.build_arb_timeline()
                used_arb = True
            else:
                timeline = self.build_timeline(flat_len_ns=flat_len_ns)
        else:
            timeline = finalize_timeline(timeline)

        src = f"arb npz ({self.arb_mode})" if used_arb else "CR params"
        print(
            f"Timeline duration: {_timeline_length(timeline) * self.dt_sample_ns:.1f} ns"
            f"  |  dt = {self.dt_sample_ns:g} ns  |  echoed = {self.echoed_cr}"
            f"  |  source = {src}"
        )
        print(
            f"CRcopy frame: control @ {self._w_ctrl / _AMP_MHZ_TO_RAD_PER_NS:.6f} MHz, "
            f"CR carrier @ {self._w_cr / _AMP_MHZ_TO_RAD_PER_NS:.6f} MHz"
        )

        self.results = self.evolve_timeline(timeline)
        self.results["metadata"] = {
            "engine": "CRcopy.processor",
            "q_pair": self.q_pair,
            "echoed_cr": self.echoed_cr,
            "cr_pulse_params": self.cr_pulse_params,
            "x_pi_pulse_params": self.x_pi_pulse_params,
            "flat_len_ns": flat_len_ns if flat_len_ns is not None else self.flat_len_ns,
            "arb_pulse": {
                "npz_path": self.arb_npz_path,
                "mode": self.arb_mode,
                "channel": self.arb_channel,
                "amp_scale": self.arb_amp_scale,
                "phase_rad": self.arb_phase_rad,
            }
            if used_arb
            else None,
            "supports_cancellation_tone": False,
        }

        if plot:
            self.plot_paths = plot_and_save_all(
                self.results,
                tag=self.file_tag,
                save_json=save_json,
                gif_fps=self.bloch_gif_fps,
                max_gif_frames=self.max_gif_frames,
            )
        return self.results


def perform_crcopy_pulse_evolution(q_pair=(1, 2), flat_len_ns=None, **kwargs):
    """One-shot CR pulse evolution with CRcopy backend."""
    exp = CR_pulse_evolution_CRcopy(qubit_pair=q_pair, flat_len_ns=flat_len_ns, **kwargs)
    exp.run()
    return exp


def perform_crcopy_arb_pulse_evolution(
    arb_npz_path,
    q_pair=(1, 2),
    *,
    arb_mode="echoed_cr_half",
    echoed_cr=True,
    n_levels=3,
    **kwargs,
):
    """One-shot pulse evolution from an arbitrary waveform (CRcopy backend)."""
    exp = CR_pulse_evolution_CRcopy(
        qubit_pair=q_pair,
        arb_npz_path=arb_npz_path,
        arb_mode=arb_mode,
        echoed_cr=echoed_cr,
        n_levels=n_levels,
        **kwargs,
    )
    exp.run()
    return exp


if __name__ == "__main__":
    # Set to a path to evolve a GRAPE-optimized waveform from npz; leave None
    # to run the analytic CR pulse below.
    ARB_NPZ_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "optimization",
        "optimization_tests",
        "results",
        "cr_grape_pulse.npz",
    )
    ARB_NPZ_PATH = None
    if ARB_NPZ_PATH:
        n_levels = 3
        perform_crcopy_arb_pulse_evolution(
            ARB_NPZ_PATH,
            q_pair=[1, 2],
            arb_mode="echoed_cr_half",
            echoed_cr=True,
            n_levels=n_levels,
            n_sub=2,  # kept for parity with other scripts; unused by CRcopy path
            file_tag=f"arb_grape_echoed_cr_crcopy_n_levels_{n_levels}",
        )
    else:
        cr_pulse_params = {
            "amp_mhz": 80.0,
            "t_rise_ns": int(16),
            "phase_rad": 0,
        }
        echoed_cr = True
        n_levels = 3
        file_tag = (
            f"amp_{cr_pulse_params['amp_mhz']}_t_rise_{cr_pulse_params['t_rise_ns']}"
            f"_ph_{cr_pulse_params['phase_rad']}_echoed_cr_{echoed_cr}_n_levels_{n_levels}"
        )
        perform_crcopy_pulse_evolution(
            q_pair=[1, 2],
            flat_len_ns=80.0,
            cr_pulse_params=cr_pulse_params,
            echoed_cr=echoed_cr,
            n_levels=n_levels,
            n_sub=2,
            file_tag=file_tag,
        )
