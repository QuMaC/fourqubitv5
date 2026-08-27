"""
plotting.py
===========
Shared plotting for the two-qubit pulse-simulator experiments.

Everything visual lives here so ``cr_len_sweep`` and ``cr_pulse_evolution`` (and
any future experiment) draw the same Bloch spheres, use the same control on/off
colour conventions, and write figures to the same ``sim_media`` directory:

  - Bloch-sphere primitives (``draw_bloch_sphere`` / ``plot_bloch_path``),
  - control on/off colour + label conventions (``CTRL_COLORS`` / ``CTRL_LABELS``),
  - pulse-evolution figures driven by an ``evolve_timeline`` results dict
    (``plot_populations`` / ``plot_xyz`` / ``save_bloch_png`` / ``save_bloch_gif``),
  - CR length-sweep Bloch-trajectory figures driven by per-control X/Y/Z arrays
    (``save_bloch_trajectory_png`` / ``save_bloch_trajectory_gif``).

Filenames passed in bare (no directory component) are placed under ``MEDIA_DIR``.
"""

from __future__ import annotations

import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.ticker import FormatStrFormatter

# Control on/off conventions, shared across every experiment plot.
CTRL_COLORS = {0: "tab:blue", 1: "tab:red"}
CTRL_LABELS = {0: "Control off (|0⟩)", 1: "Control on (|1⟩)"}
COMP_LABELS = ("|00⟩", "|01⟩", "|10⟩", "|11⟩")

# All generated figures / JSON dumps land here (two_qubit_simulator/sim_media).
MEDIA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sim_media"
)


def _media_path(filename):
    """Place a bare filename under MEDIA_DIR; leave paths with a directory as-is."""
    if os.path.dirname(filename):
        return filename
    return os.path.join(MEDIA_DIR, filename)


def _date_tag() -> str:
    return datetime.now().strftime("%d%m%Y")


# ---------------------------------------------------------------------------
# Bloch-sphere primitives
# ---------------------------------------------------------------------------
def draw_bloch_sphere(ax, wireframe_alpha=0.18, elev=22, azim=-58):
    """Unit Bloch sphere wireframe and axis arrows on a 3D axes.

    Matplotlib ``view_init`` angles (degrees): ``elev`` tilts the camera;
    ``azim`` rotates about the Bloch Z axis.
    """
    u = np.linspace(0, 2 * np.pi, 36)
    v = np.linspace(0, np.pi, 18)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, color="0.65", alpha=wireframe_alpha, linewidth=0.4, rstride=2, cstride=2)
    for vec, label in zip(
        [(1, 0, 0), (0, 1, 0), (0, 0, 1)],
        ["X", "Y", "Z"],
    ):
        ax.quiver(0, 0, 0, *vec, color="0.35", arrow_length_ratio=0.08, linewidth=0.9, alpha=0.85)
        ax.text(*(1.12 * np.asarray(vec)), label, color="0.35", fontsize=8)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_zlim(-1.05, 1.05)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


def plot_bloch_path(ax, xs, ys, zs, color, up_to=None, show_markers=True):
    """Plot a Bloch trajectory up to index up_to (inclusive)."""
    n = len(xs) if up_to is None else min(up_to + 1, len(xs))
    if n == 0:
        return
    ax.plot(xs[:n], ys[:n], zs[:n], color=color, lw=2.0, alpha=0.9)
    if show_markers and n > 0:
        ax.scatter(xs[0], ys[0], zs[0], color=color, s=28, marker="o", alpha=0.55, label="start")
        ax.scatter(xs[n - 1], ys[n - 1], zs[n - 1], color=color, s=42, marker="*", label="current")


def decimate_frame_indices(n_total: int, max_frames: int = 120) -> np.ndarray:
    """Evenly spaced frame indices, always including first and last."""
    if n_total <= 0:
        return np.array([], dtype=int)
    if max_frames <= 0:
        raise ValueError(f"max_frames must be positive, got {max_frames}")
    if n_total <= max_frames:
        return np.arange(n_total, dtype=int)
    return np.unique(np.round(np.linspace(0, n_total - 1, max_frames)).astype(int))


# ---------------------------------------------------------------------------
# Pulse-evolution figures (operate on an ``evolve_timeline`` results dict)
# ---------------------------------------------------------------------------
def plot_populations(results, filename=None, title=None):
    """Computational- and higher-level populations vs time (ctrl 0 / ctrl 1)."""
    filename = _media_path(filename or f"cr_pulse_evolution_populations_{_date_tag()}.png")
    times = results["times_ns"]
    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)

    for ax, ctrl in zip(axes, (0, 1)):
        data = results[f"control_{ctrl}"]
        color = CTRL_COLORS[ctrl]
        for k, label in enumerate(COMP_LABELS):
            ax.plot(times, data["comp_populations"][:, k], lw=1.6,
                    label=label, alpha=0.95)
        # Non-computational levels (e.g. |02⟩, |12⟩) when n_levels > 2.
        extra = []
        for j, lab in enumerate(data["level_labels"]):
            if lab not in COMP_LABELS:
                extra.append((j, lab))
        for j, lab in extra:
            ax.plot(times, data["level_populations"][:, j], lw=1.0,
                    ls="--", alpha=0.55, label=lab)
        ax.set_ylabel("Population")
        ax.set_ylim(-0.02, 1.05)
        ax.set_title(CTRL_LABELS[ctrl], color=color, fontsize=10)
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
                    color=CTRL_COLORS[ctrl],
                    lw=1.6,
                    label=CTRL_LABELS[ctrl],
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
    frame_indices = decimate_frame_indices(n_total, max_gif_frames)
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
        draw_bloch_sphere(ax)
        ax.set_title(CTRL_LABELS[ctrl], color=CTRL_COLORS[ctrl], fontsize=11)
        xs, ys, zs = trajectories[ctrl]
        color = CTRL_COLORS[ctrl]
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
        color = CTRL_COLORS[ctrl]
        draw_bloch_sphere(ax)
        plot_bloch_path(ax, xs, ys, zs, color=color, show_markers=False)
        ax.scatter(xs[0], ys[0], zs[0], color=color, s=36, marker="o", alpha=0.55, label="start")
        ax.scatter(xs[-1], ys[-1], zs[-1], color=color, s=64, marker="*", label="end")
        ax.set_title(CTRL_LABELS[ctrl], color=color, fontsize=11)

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


# ---------------------------------------------------------------------------
# CR length-sweep Bloch-trajectory figures (operate on per-control X/Y/Z arrays)
# ---------------------------------------------------------------------------
def bloch_trajectory_arrays(results):
    """Target-qubit Bloch components (X, Y, Z) per control state from a
    ``CR_len_sweep`` results dict (``results[ctrl]['X'|'Y'|'Z']``)."""
    trajectories = {}
    for ctrl in (0, 1):
        trajectories[ctrl] = (
            np.asarray(results[ctrl]["X"], dtype=float),
            np.asarray(results[ctrl]["Y"], dtype=float),
            np.asarray(results[ctrl]["Z"], dtype=float),
        )
    return trajectories


def save_bloch_trajectory_png(trajectories, tlist, filename, *, elev=22, azim=-58):
    """Static 2x1 PNG of net Bloch trajectories vs sweep duration (ctrl off | on).

    ``trajectories`` is the ``{ctrl: (xs, ys, zs)}`` dict from
    ``bloch_trajectory_arrays``.
    """
    fig, axes = plt.subplots(2, 1, figsize=(6, 10), subplot_kw={"projection": "3d"})
    for ax, ctrl in zip(axes, (0, 1)):
        xs, ys, zs = trajectories[ctrl]
        color = CTRL_COLORS[ctrl]
        draw_bloch_sphere(ax, elev=elev, azim=azim)
        plot_bloch_path(ax, xs, ys, zs, color=color, show_markers=False)
        ax.scatter(xs[0], ys[0], zs[0], color=color, s=36, marker="o", alpha=0.55, label="start")
        ax.scatter(xs[-1], ys[-1], zs[-1], color=color, s=64, marker="*", label="end")
        ax.set_title(CTRL_LABELS[ctrl], color=color, fontsize=11)

    fig.suptitle(
        f"Target Bloch trajectories vs CR duration (0–{tlist[-1]:.0f} ns)",
        fontsize=12,
        y=0.98,
    )
    plt.tight_layout()
    fig.savefig(filename, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {filename}")
    return filename


def save_bloch_trajectory_gif(trajectories, tlist, filename, *, fps=12, elev=22, azim=-58):
    """Animated 2x1 GIF of the traversed Bloch paths vs sweep duration (ctrl off | on).

    ``trajectories`` is the ``{ctrl: (xs, ys, zs)}`` dict from
    ``bloch_trajectory_arrays``.
    """
    n_frames = len(tlist)

    fig, axes = plt.subplots(2, 1, figsize=(6, 10), subplot_kw={"projection": "3d"})
    path_artists = []
    for ax, ctrl in zip(axes, (0, 1)):
        draw_bloch_sphere(ax, elev=elev, azim=azim)
        ax.set_title(CTRL_LABELS[ctrl], color=CTRL_COLORS[ctrl], fontsize=11)
        xs, ys, zs = trajectories[ctrl]
        color = CTRL_COLORS[ctrl]
        (line,) = ax.plot([], [], [], color=color, lw=2.0, alpha=0.9)
        start = ax.scatter([], [], [], color=color, s=36, marker="o", alpha=0.55)
        current = ax.scatter([], [], [], color=color, s=64, marker="*")
        duration_text = ax.text2D(0.02, 0.02, "", transform=ax.transAxes, fontsize=9, color=color)
        path_artists.append((line, start, current, duration_text, xs, ys, zs, color))

    fig.suptitle("Target Bloch trajectories vs CR duration", fontsize=12, y=0.98)

    def _update(frame_idx):
        artists = []
        duration_ns = float(tlist[frame_idx])
        for line, start, current, duration_text, xs, ys, zs, color in path_artists:
            n = frame_idx + 1
            line.set_data(xs[:n], ys[:n])
            line.set_3d_properties(zs[:n])
            start._offsets3d = ([xs[0]], [ys[0]], [zs[0]])
            current._offsets3d = ([xs[n - 1]], [ys[n - 1]], [zs[n - 1]])
            duration_text.set_text(f"t = {duration_ns:.0f} ns")
            artists.extend([line, start, current, duration_text])
        return artists

    anim = FuncAnimation(fig, _update, frames=n_frames, interval=1000 / fps, blit=False)
    writer = PillowWriter(fps=fps)
    anim.save(filename, writer=writer)
    plt.close(fig)
    print(f"Saved {filename} ({n_frames} frames @ {fps} fps)")
    return filename
