"""
cr_pulse_evolution.py
=====================
Evolve a single pulse timeline sample-by-sample and record the full two-qubit
state trajectory for control |0⟩ (|00⟩) and control |1⟩ (|10⟩).

Core API (importable from other scripts)
----------------------------------------
``evolve_timeline(simulator, timeline)`` accepts a finalized timeline dict or a
``Timeline`` builder (``.finalize()`` is called internally). It returns
time-resolved observables plus the full state vector at every sample boundary.

CR convenience wrapper
----------------------
``CR_pulse_evolution`` builds a CR (or echoed-CR) timeline via the same pulse
machinery as ``cr_len_sweep``, then calls ``evolve_timeline``.

Outputs land in ``sim_media/`` with a ``ddmmyyyy`` date suffix on each filename.
"""

from __future__ import annotations

import json
import os

import numpy as np
import qutip as qt

from HM.simulator.two_qubit_simulator.engine.pulses import Timeline, load_waveform_npz
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import (
    CR_len_sweep,
    pauli_on_levels,
)
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
    """Return a channel -> envelope dict accepted by the pulse engines."""
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


def _pauli_ops(simulator):
    """Control- and target-qubit Pauli X/Y/Z on the joint Hilbert space."""
    n0, n1 = simulator.dims
    I0, I1 = qt.qeye(n0), qt.qeye(n1)
    ops = {}
    for which in ("X", "Y", "Z"):
        P0 = pauli_on_levels(which, n0)
        P1 = pauli_on_levels(which, n1)
        ops[f"ctrl_{which}"] = qt.tensor(P0, I1)
        ops[f"tgt_{which}"] = qt.tensor(I0, P1)
    return ops


def _observables_at_step(psi, simulator, pauli_ops):
    """Extract full-state and reduced observables from one ket."""
    vec = np.asarray(psi.full(), dtype=complex).reshape(-1)
    n0, n1 = simulator.dims
    comp_idx = list(simulator.comp_idx)

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
    """List of per-step dicts -> arrays keyed by observable name."""
    keys = [k for k in steps[0].keys() if k not in ("level_labels",)]
    out = {}
    complex_keys = {"state_vector", "comp_amplitudes"}
    for k in keys:
        if k in complex_keys:
            out[k] = np.stack([s[k] for s in steps], axis=0)
        elif k in ("comp_populations", "level_populations"):
            out[k] = np.stack([s[k] for s in steps], axis=0)
        else:
            out[k] = np.array([s[k] for s in steps], dtype=float)
    out["level_labels"] = steps[0]["level_labels"]
    return out


def evolve_timeline(
    simulator,
    timeline: Timeline | dict[str, np.ndarray],
    *,
    dt_sample_ns: float | None = None,
    ctrl_states: tuple[int, ...] = (0, 1),
    store_full_state_vector: bool = True,
):
    """Evolve one timeline for each control initial state; return time series.

    Parameters
    ----------
    simulator
        ``TwoQubitPulseSimulator`` (or dynamiqs wrapper with the same API).
    timeline
        ``Timeline`` builder or finalized ``dict[channel, complex envelope]``.
    dt_sample_ns
        Sample period in ns; defaults to ``simulator.dt_sample_ns``.
    ctrl_states
        Control-qubit initial states: 0 -> |00⟩, 1 -> |10⟩.
    store_full_state_vector
        When False, drop the raw Hilbert-space amplitudes from the return dict
        (populations and Pauli expectations are always kept).

    Returns
    -------
    dict with keys ``times_ns``, ``total_duration_ns``, ``dt_sample_ns``,
    ``n_samples``, and ``control_{0,1}`` sub-dicts of stacked observables.
    """
    tl = finalize_timeline(timeline)
    dt = float(simulator.dt_sample_ns if dt_sample_ns is None else dt_sample_ns)
    n_samples = _timeline_length(tl)
    times_ns = np.arange(n_samples + 1, dtype=float) * dt
    pauli_ops = _pauli_ops(simulator)
    comp_idx = list(simulator.comp_idx)

    ctrl_init = {
        0: qt.basis(simulator.dims, [0, 0]),
        1: qt.basis(simulator.dims, [1, 0]),
    }

    out = {
        "times_ns": times_ns,
        "total_duration_ns": float(times_ns[-1]),
        "dt_sample_ns": dt,
        "n_samples": n_samples,
        "comp_labels": [_COMP_LABELS[comp_idx.index(i)] if i in comp_idx else f"idx{i}"
                        for i in comp_idx],
        "comp_indices": comp_idx,
    }

    for ctrl in ctrl_states:
        if ctrl not in ctrl_init:
            raise ValueError(f"unsupported ctrl_state {ctrl!r}; expected 0 or 1")
        _, trajectory = simulator.run_shot(
            tl, psi0=ctrl_init[ctrl], store_trajectory=True
        )
        steps = [_observables_at_step(psi, simulator, pauli_ops) for psi in trajectory]
        stacked = _stack_observables(steps)
        if not store_full_state_vector:
            stacked.pop("state_vector", None)
        out[f"control_{ctrl}"] = stacked

    return out


def save_results_json(results, filename=None, include_state_vector=True):
    """Dump observables (and optionally full state vectors) to JSON."""
    filename = _media_path(filename or f"cr_pulse_evolution_{_date_tag()}.json")
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
        "populations": plot_populations(results, f"cr_pulse_evolution_populations{suffix}.png"),
        "xyz": plot_xyz(results, f"cr_pulse_evolution_xyz{suffix}.png"),
        "bloch_png": save_bloch_png(results, f"cr_pulse_evolution_bloch{suffix}.png", qubit=bloch_qubit),
        "bloch_gif": save_bloch_gif(
            results,
            f"cr_pulse_evolution_bloch{suffix}.gif",
            qubit=bloch_qubit,
            fps=gif_fps,
            max_gif_frames=max_gif_frames,
        ),
    }
    if save_json:
        paths["json"] = save_results_json(results, f"cr_pulse_evolution{suffix}.json")
    return paths


class CR_pulse_evolution(CR_len_sweep):
    """Build a CR (or echoed-CR) timeline and run ``evolve_timeline`` on it.

    A timeline can come from three places:
      * the analytic CR-pulse parameters (``build_timeline``), as before;
      * an arbitrary waveform loaded from an ``.npz`` file
        (``build_arb_timeline`` / the ``arb_npz_path`` option), e.g. a
        GRAPE-optimized pulse from ``optimization/cr_grape.py``;
      * an explicit ``timeline`` passed to ``run``.
    """

    # Recognized arb-pulse kwargs popped before delegating to CR_len_sweep.
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
        kwargs.setdefault("dt_sample_ns", 1)
        kwargs.setdefault("n_sub", 2)
        arb_opts = {name: kwargs.pop(name) for name in self._ARB_KWARGS if name in kwargs}
        super().__init__(qubit_pair=qubit_pair, len_list=None, **kwargs)
        self.flat_len_ns = flat_len_ns
        self.bloch_gif_fps = int(kwargs.get("bloch_gif_fps", 12))
        self.max_gif_frames = int(kwargs.get("max_gif_frames", 120))
        self.file_tag = kwargs.get("file_tag", "")

        # Arbitrary-waveform (npz) options.
        #   arb_mode "echoed_cr_half": treat the npz as one CR half (+u) and
        #       build the echoed sequence +u -> Xpi -> -u -> Xpi (requires
        #       echoed_cr=True). This matches how cr_grape.py dumps a pulse.
        #   arb_mode "single": place the loaded waveform directly on
        #       ``arb_channel`` as a single arb pulse starting at t=0.
        self.arb_npz_path = arb_opts.get("arb_npz_path")
        self.arb_mode = str(arb_opts.get("arb_mode", "echoed_cr_half"))
        self.arb_channel = str(arb_opts.get("arb_channel", "cr_drive"))
        self.arb_key = arb_opts.get("arb_key")
        self.arb_i_key = arb_opts.get("arb_i_key")
        self.arb_q_key = arb_opts.get("arb_q_key")
        self.arb_amp_scale = float(arb_opts.get("arb_amp_scale", 1.0))
        self.arb_phase_rad = float(arb_opts.get("arb_phase_rad", 0.0))
        os.makedirs(MEDIA_DIR, exist_ok=True)

    def build_timeline(self, flat_len_ns=None) -> dict[str, np.ndarray]:
        """Return a finalized timeline for the configured CR pulse."""
        if flat_len_ns is None:
            flat_len_ns = self.flat_len_ns
        if flat_len_ns is None:
            raise ValueError("flat_len_ns must be set on the instance or passed here")
        x_pi = self.build_x_pi() if self.echoed_cr else None
        return self._build_timeline(float(flat_len_ns), x_pi=x_pi)

    def build_arb_timeline(self, npz_path=None, *, mode=None) -> dict[str, np.ndarray]:
        """Build a timeline from an arbitrary waveform stored in an ``.npz`` file.

        Parameters
        ----------
        npz_path
            Path to the ``.npz`` waveform (defaults to ``self.arb_npz_path``).
        mode
            ``"echoed_cr_half"`` (default) builds the echoed sequence
            ``+u -> Xpi -> -u -> Xpi`` from the loaded CR half; ``"single"``
            places the waveform directly on ``self.arb_channel``.
        """
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
            return self._build_timeline_from_cr_half(cr_half, x_pi=self.build_x_pi())

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

    def run(
        self,
        timeline: Timeline | dict[str, np.ndarray] | None = None,
        *,
        flat_len_ns=None,
        plot=True,
        save_json=True,
    ):
        """Evolve one timeline.

        If ``timeline`` is omitted, the timeline is built from an arb npz
        waveform when ``arb_npz_path`` is set, otherwise from the CR-pulse
        parameters.
        """
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
        print(f"Timeline duration: {_timeline_length(timeline) * self.dt_sample_ns:.1f} ns"
              f"  |  dt = {self.dt_sample_ns:g} ns  |  echoed = {self.echoed_cr}"
              f"  |  source = {src}")
        self.results = evolve_timeline(self.simulator, timeline, dt_sample_ns=self.dt_sample_ns)
        self.results["metadata"] = {
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
            } if used_arb else None,
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


def perform_cr_pulse_evolution(q_pair=(1, 2), flat_len_ns=None, **kwargs):
    """One-shot CR pulse evolution with plots saved to sim_media."""
    exp = CR_pulse_evolution(qubit_pair=q_pair, flat_len_ns=flat_len_ns, **kwargs)
    exp.run()
    return exp


def perform_arb_pulse_evolution(
    arb_npz_path,
    q_pair=(1, 2),
    *,
    arb_mode="echoed_cr_half",
    echoed_cr=True,
    n_levels=3,
    **kwargs,
):
    """One-shot pulse evolution driven by an arbitrary waveform from an npz file.

    Loads ``arb_npz_path`` (e.g. a GRAPE-optimized CR pulse) and evolves it via
    the same machinery as ``perform_cr_pulse_evolution``. With the default
    ``arb_mode='echoed_cr_half'`` the npz is treated as one CR half and the
    echoed sequence ``+u -> Xpi -> -u -> Xpi`` is built around it.
    """
    exp = CR_pulse_evolution(
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
    # Set to a path to evolve a GRAPE-optimized (or any) waveform from an npz
    # file; leave as None to evolve the analytic CR pulse below.
    ARB_NPZ_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "optimization", "optimization_tests", "results", "cr_grape_pulse.npz",
    )
    ARB_NPZ_PATH =f'/home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5/HM/simulator/two_qubit_simulator/optimization/optimization_tests/results/robust/cr_grape_robust_zz0p1824MHz_20260702_213910.npz'
    if ARB_NPZ_PATH:
        n_levels = 3
        perform_arb_pulse_evolution(
            ARB_NPZ_PATH,
            q_pair=[1, 2],
            arb_mode="echoed_cr_half",
            echoed_cr=True,
            n_levels=n_levels,
            n_sub=2,
            file_tag=f"arb_grape_echoed_cr_n_levels_{n_levels}",
        )
    else:
        cr_pulse_params = {
            "amp_mhz": 32.0,
            "t_rise_ns": int(16),
            "phase_rad": 0,
        }
        echoed_cr = True
        n_levels = 3
        file_tag = (
            f"amp_{cr_pulse_params['amp_mhz']}_t_rise_{cr_pulse_params['t_rise_ns']}"
            f"_ph_{cr_pulse_params['phase_rad']}_echoed_cr_{echoed_cr}_n_levels_{n_levels}"
        )
        perform_cr_pulse_evolution(
            q_pair=[1, 2],
            flat_len_ns=84.0,
            cr_pulse_params=cr_pulse_params,
            echoed_cr=echoed_cr,
            n_levels=n_levels,
            n_sub=2,
            file_tag=file_tag,
        )