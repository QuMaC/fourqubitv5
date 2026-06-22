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
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import qutip as qt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.ticker import FormatStrFormatter

from HM.simulator.two_qubit_simulator.engine.pulses import Timeline
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import (
    CR_len_sweep,
    MEDIA_DIR,
    _CTRL_COLORS,
    _CTRL_LABELS,
    _draw_bloch_sphere,
    _media_path,
    _plot_bloch_path,
    pauli_on_levels,
)

_COMP_LABELS = ("|00⟩", "|01⟩", "|10⟩", "|11⟩")


def _date_tag() -> str:
    return datetime.now().strftime("%d%m%Y")


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


def _decimate_frame_indices(n_total: int, max_frames: int = 120) -> np.ndarray:
    """Evenly spaced frame indices, always including first and last."""
    if n_total <= 0:
        return np.array([], dtype=int)
    if max_frames <= 0:
        raise ValueError(f"max_frames must be positive, got {max_frames}")
    if n_total <= max_frames:
        return np.arange(n_total, dtype=int)
    return np.unique(np.round(np.linspace(0, n_total - 1, max_frames)).astype(int))


def plot_populations(results, filename=None, title=None):
    """Computational- and higher-level populations vs time (ctrl 0 / ctrl 1)."""
    filename = _media_path(filename or f"cr_pulse_evolution_populations_{_date_tag()}.png")
    times = results["times_ns"]
    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)

    for ax, ctrl in zip(axes, (0, 1)):
        data = results[f"control_{ctrl}"]
        color = _CTRL_COLORS[ctrl]
        for k, label in enumerate(_COMP_LABELS):
            ax.plot(times, data["comp_populations"][:, k], lw=1.6,
                    label=label, alpha=0.95)
        # Non-computational levels (e.g. |02⟩, |12⟩) when n_levels > 2.
        extra = []
        for j, lab in enumerate(data["level_labels"]):
            if lab not in _COMP_LABELS:
                extra.append((j, lab))
        for j, lab in extra:
            ax.plot(times, data["level_populations"][:, j], lw=1.0,
                    ls="--", alpha=0.55, label=lab)
        ax.set_ylabel("Population")
        ax.set_ylim(-0.02, 1.05)
        ax.set_title(_CTRL_LABELS[ctrl], color=color, fontsize=10)
        ax.grid(alpha=0.35)
        ax.legend(loc="upper right", fontsize=7, ncol=2)

    axes[-1].set_xlabel("Time (ns)")
    fig.suptitle(title or "Two-qubit state populations during pulse", fontsize=11)
    plt.tight_layout()
    fig.savefig(filename, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {filename}")
    return filename


def plot_xyz(results, filename=None, title=None, qubit="both"):
    """Pauli ⟨X⟩, ⟨Y⟩, ⟨Z⟩ vs time for control and/or target qubit."""
    filename = _media_path(filename or f"cr_pulse_evolution_xyz_{_date_tag()}.png")
    times = results["times_ns"]
    qubits = ("ctrl", "tgt") if qubit == "both" else (qubit,)
    n_rows = len(qubits)
    fig, axes = plt.subplots(n_rows, 3, figsize=(10, 3.2 * n_rows), sharex=True)
    if n_rows == 1:
        axes = np.asarray([axes])

    qubit_titles = {"ctrl": "Control qubit", "tgt": "Target qubit"}
    for row, q in enumerate(qubits):
        for col, comp in enumerate(("X", "Y", "Z")):
            ax = axes[row, col]
            key = f"{q}_{comp}"
            for ctrl in (0, 1):
                ax.plot(
                    times,
                    results[f"control_{ctrl}"][key],
                    color=_CTRL_COLORS[ctrl],
                    lw=1.6,
                    label=_CTRL_LABELS[ctrl],
                )
            ax.set_ylabel(f"⟨{comp}⟩")
            ax.set_ylim(-1.1, 1.1)
            ax.axhline(0, color="k", lw=0.4, alpha=0.3)
            ax.yaxis.set_major_formatter(FormatStrFormatter("%.2g"))
            ax.grid(alpha=0.35)
            if row == 0:
                ax.set_title(comp)
            if col == 0:
                ax.text(
                    -0.12, 0.5, qubit_titles[q], transform=ax.transAxes,
                    rotation=90, va="center", ha="center", fontsize=10,
                )
            if row == 0 and col == 2:
                ax.legend(loc="upper right", fontsize=7)

    axes[-1, 1].set_xlabel("Time (ns)")
    fig.suptitle(title or "Single-qubit Pauli expectations during pulse", fontsize=11)
    plt.tight_layout()
    fig.savefig(filename, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {filename}")
    return filename


def save_bloch_gif(
    results,
    filename=None,
    *,
    qubit="tgt",
    fps=12,
    max_gif_frames=120,
    title=None,
):
    """Animated 2x1 Bloch trajectories (ctrl off | ctrl on) during the pulse."""
    filename = _media_path(filename or f"cr_pulse_evolution_bloch_{_date_tag()}.gif")
    times = results["times_ns"]
    n_total = len(times)
    frame_indices = _decimate_frame_indices(n_total, max_gif_frames)
    n_frames = len(frame_indices)
    prefix = f"{qubit}_"

    trajectories = {}
    for ctrl in (0, 1):
        data = results[f"control_{ctrl}"]
        trajectories[ctrl] = (
            data[f"{prefix}X"],
            data[f"{prefix}Y"],
            data[f"{prefix}Z"],
        )

    fig, axes = plt.subplots(2, 1, figsize=(6, 10), subplot_kw={"projection": "3d"})
    path_artists = []
    for ax, ctrl in zip(axes, (0, 1)):
        _draw_bloch_sphere(ax)
        ax.set_title(_CTRL_LABELS[ctrl], color=_CTRL_COLORS[ctrl], fontsize=11)
        xs, ys, zs = trajectories[ctrl]
        color = _CTRL_COLORS[ctrl]
        (line,) = ax.plot([], [], [], color=color, lw=2.0, alpha=0.9)
        start = ax.scatter([], [], [], color=color, s=36, marker="o", alpha=0.55)
        current = ax.scatter([], [], [], color=color, s=64, marker="*")
        time_text = ax.text2D(0.02, 0.02, "", transform=ax.transAxes, fontsize=9, color=color)
        path_artists.append((line, start, current, time_text, xs, ys, zs))

    qubit_name = "Target" if qubit == "tgt" else "Control"
    fig.suptitle(
        title or f"{qubit_name} Bloch trajectories during pulse",
        fontsize=12, y=0.98,
    )

    def _update(anim_idx):
        artists = []
        data_idx = int(frame_indices[anim_idx])
        t_ns = float(times[data_idx])
        for line, start, current, time_text, xs, ys, zs in path_artists:
            n = data_idx + 1
            line.set_data(xs[:n], ys[:n])
            line.set_3d_properties(zs[:n])
            start._offsets3d = ([xs[0]], [ys[0]], [zs[0]])
            current._offsets3d = ([xs[data_idx]], [ys[data_idx]], [zs[data_idx]])
            time_text.set_text(f"t = {t_ns:.1f} ns")
            artists.extend([line, start, current, time_text])
        return artists

    anim = FuncAnimation(fig, _update, frames=n_frames, interval=1000 / fps, blit=False)
    writer = PillowWriter(fps=fps)
    anim.save(filename, writer=writer)
    plt.close(fig)
    if n_frames < n_total:
        print(
            f"Saved {filename} ({n_frames} frames @ {fps} fps, "
            f"decimated from {n_total} time steps)"
        )
    else:
        print(f"Saved {filename} ({n_frames} frames @ {fps} fps)")
    return filename


def save_bloch_png(results, filename=None, qubit="tgt", title=None):
    """Static 2×1 Bloch trajectories at full pulse duration."""
    filename = _media_path(filename or f"cr_pulse_evolution_bloch_{_date_tag()}.png")
    prefix = f"{qubit}_"
    fig, axes = plt.subplots(2, 1, figsize=(6, 10), subplot_kw={"projection": "3d"})
    t_end = results["total_duration_ns"]

    for ax, ctrl in zip(axes, (0, 1)):
        data = results[f"control_{ctrl}"]
        xs, ys, zs = data[f"{prefix}X"], data[f"{prefix}Y"], data[f"{prefix}Z"]
        color = _CTRL_COLORS[ctrl]
        _draw_bloch_sphere(ax)
        _plot_bloch_path(ax, xs, ys, zs, color=color, show_markers=False)
        ax.scatter(xs[0], ys[0], zs[0], color=color, s=36, marker="o", alpha=0.55, label="start")
        ax.scatter(xs[-1], ys[-1], zs[-1], color=color, s=64, marker="*", label="end")
        ax.set_title(_CTRL_LABELS[ctrl], color=color, fontsize=11)

    qubit_name = "Target" if qubit == "tgt" else "Control"
    fig.suptitle(
        title or f"{qubit_name} Bloch trajectories (0–{t_end:.0f} ns)",
        fontsize=12, y=0.98,
    )
    plt.tight_layout()
    fig.savefig(filename, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {filename}")
    return filename


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
    """Build a CR (or echoed-CR) timeline and run ``evolve_timeline`` on it."""

    def __init__(self, qubit_pair=(1, 2), flat_len_ns=None, **kwargs):
        kwargs.setdefault("dt_sample_ns", 1)
        kwargs.setdefault("n_sub", 2)
        super().__init__(qubit_pair=qubit_pair, len_list=None, **kwargs)
        self.flat_len_ns = flat_len_ns
        self.bloch_gif_fps = int(kwargs.get("bloch_gif_fps", 12))
        self.max_gif_frames = int(kwargs.get("max_gif_frames", 120))
        self.file_tag = kwargs.get("file_tag", "")
        os.makedirs(MEDIA_DIR, exist_ok=True)

    def build_timeline(self, flat_len_ns=None) -> dict[str, np.ndarray]:
        """Return a finalized timeline for the configured CR pulse."""
        if flat_len_ns is None:
            flat_len_ns = self.flat_len_ns
        if flat_len_ns is None:
            raise ValueError("flat_len_ns must be set on the instance or passed here")
        x_pi = self.build_x_pi() if self.echoed_cr else None
        return self._build_timeline(float(flat_len_ns), x_pi=x_pi)

    def run(
        self,
        timeline: Timeline | dict[str, np.ndarray] | None = None,
        *,
        flat_len_ns=None,
        plot=True,
        save_json=True,
    ):
        """Evolve one timeline (built from CR params if ``timeline`` is omitted)."""
        if timeline is None:
            timeline = self.build_timeline(flat_len_ns=flat_len_ns)
        else:
            timeline = finalize_timeline(timeline)

        print(f"Timeline duration: {_timeline_length(timeline) * self.dt_sample_ns:.1f} ns"
              f"  |  dt = {self.dt_sample_ns:g} ns  |  echoed = {self.echoed_cr}")
        self.results = evolve_timeline(self.simulator, timeline, dt_sample_ns=self.dt_sample_ns)
        self.results["metadata"] = {
            "q_pair": self.q_pair,
            "echoed_cr": self.echoed_cr,
            "cr_pulse_params": self.cr_pulse_params,
            "x_pi_pulse_params": self.x_pi_pulse_params,
            "flat_len_ns": flat_len_ns if flat_len_ns is not None else self.flat_len_ns,
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


if __name__ == "__main__":
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
        flat_len_ns=80.0,
        cr_pulse_params=cr_pulse_params,
        echoed_cr=echoed_cr,
        n_levels=n_levels,
        n_sub=2,
        file_tag=file_tag,
    )