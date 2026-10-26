"""Slide figure: spectator ZZ on target q2, illustrated with spectator q3.

Left: TIFR 6-qubit coupling graph. The CR gate is on q1 (control) to
q2 (target). Spectator q3 is highlighted, with the q3-q2 edge emphasized.
Right: frequency-domain cartoon of the target. A dotted Gaussian marks
the bare q2 frequency. Two identical solid Gaussians are the q2 line
when that single spectator is in |0> or |1>.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib.gridspec import GridSpec


OUT_DIR = Path(__file__).resolve().parent
STEM = "zz_spectator_q3_on_q2"

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "Nimbus Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
    }
)

ANGLES = {
    5: 0.0,
    4: np.pi / 3,
    3: 2 * np.pi / 3,
    2: np.pi,
    1: 4 * np.pi / 3,
    6: 5 * np.pi / 3,
}
RADIUS = 1.0
POSITIONS = {
    q: (RADIUS * np.cos(theta), RADIUS * np.sin(theta))
    for q, theta in ANGLES.items()
}
EDGES = [(c, t) for c in (1, 3, 5) for t in (2, 4, 6)]

INK = "#111111"
ACCENT = "#2F5D8A"
ACCENT_FILL = "#3D6EA0"
CONTROL_FILL = "#D7E4F2"
CONTROL_EDGE = "#2B5C8A"
TARGET_FILL = "#F3E2E2"
TARGET_EDGE = "#8B3030"
GATE = "#2E8B57"
NODE_RADIUS = 0.205
LINEWIDTH = 1.45
TITLE_FONT = {"family": "STIXGeneral", "size": 13}
ROLE_FONT = {"family": "STIXGeneral", "size": 10}


def gaussian(x, center, width):
    return np.exp(-0.5 * ((x - center) / width) ** 2)


def _edge_style(i: int, j: int) -> tuple[str, float]:
    pair = {i, j}
    if pair == {1, 2}:
        return GATE, 2.55
    if pair == {2, 3}:
        return ACCENT, 2.35
    return INK, LINEWIDTH


def draw_device(ax) -> None:
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")

    for i, j in EDGES:
        x1, y1 = POSITIONS[i]
        x2, y2 = POSITIONS[j]
        color, lw = _edge_style(i, j)
        ax.plot(
            [x1, x2],
            [y1, y2],
            color=color,
            lw=lw,
            solid_capstyle="butt",
            zorder=1,
        )

    node_style = {
        1: (CONTROL_FILL, CONTROL_EDGE, 2.0, INK),
        2: (TARGET_FILL, TARGET_EDGE, 2.0, INK),
        3: (ACCENT_FILL, ACCENT, 2.0, "white"),
    }
    for q, (x, y) in POSITIONS.items():
        face, edge, lw, tcolor = node_style.get(q, ("white", INK, LINEWIDTH, INK))
        ax.add_patch(
            Circle(
                (x, y),
                NODE_RADIUS,
                facecolor=face,
                edgecolor=edge,
                lw=lw,
                zorder=2,
            )
        )
        ax.text(
            x,
            y - 0.008,
            rf"$q_{{{q}}}$",
            ha="center",
            va="center",
            fontsize=13,
            color=tcolor,
            zorder=3,
        )

    role_labels = {
        1: dict(text="control", xytext=(-0.22, -0.38), ha="center", va="top", color=CONTROL_EDGE),
        2: dict(text="target", xytext=(-0.46, 0.02), ha="right", va="center", color=TARGET_EDGE),
        3: dict(text="spectator", xytext=(-0.46, 0.10), ha="right", va="center", color=ACCENT),
    }
    for q, spec in role_labels.items():
        x, y = POSITIONS[q]
        ax.text(
            x + spec["xytext"][0],
            y + spec["xytext"][1],
            spec["text"],
            ha=spec["ha"],
            va=spec["va"],
            fontdict=ROLE_FONT,
            color=spec["color"],
            zorder=4,
        )

    mx = 0.5 * (POSITIONS[1][0] + POSITIONS[2][0])
    my = 0.5 * (POSITIONS[1][1] + POSITIONS[2][1])
    radial = np.hypot(mx, my)
    ax.text(
        mx + 0.28 * mx / radial,
        my + 0.28 * my / radial,
        r"$\mathrm{CR}$",
        ha="center",
        va="center",
        fontsize=11,
        color=GATE,
        zorder=4,
    )

    ax.set_xlim(-1.78, 1.42)
    ax.set_ylim(-1.78, 1.48)
    ax.set_title(
        r"(b)   CR gate $q_1 \to q_2$",
        fontdict=TITLE_FONT,
        color=INK,
        pad=8,
        loc="left",
    )


def draw_spectrum(ax) -> None:
    ax.set_facecolor("white")
    x = np.linspace(-1.35, 1.35, 2400)
    width = 0.048
    split = 0.62
    y_bare = gaussian(x, 0.0, width)
    y_left = gaussian(x, -split, width)
    y_right = gaussian(x, split, width)

    ax.fill_between(x, 0.0, y_left, color=ACCENT, alpha=0.18, linewidth=0, zorder=2)
    ax.fill_between(x, 0.0, y_right, color=ACCENT, alpha=0.18, linewidth=0, zorder=2)
    ax.plot(
        x,
        y_bare,
        color="#6A6A6A",
        lw=1.7,
        ls=(0, (1.15, 1.35)),
        zorder=3,
        label=r"bare $q_2$",
    )
    ax.plot(x, y_left, color=ACCENT, lw=2.0, zorder=4)
    ax.plot(x, y_right, color=ACCENT, lw=2.0, zorder=4)

    ax.axhline(0.0, color=INK, lw=1.05, zorder=1)
    ax.annotate(
        "",
        xy=(1.38, 0.0),
        xytext=(-1.38, 0.0),
        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.05, mutation_scale=10),
        zorder=1,
    )

    ax.text(
        0.0,
        -0.13,
        r"$\omega_{q_2}^{\mathrm{bare}}$",
        ha="center",
        va="top",
        fontsize=12,
        color="#555555",
    )
    ax.text(
        -split,
        -0.13,
        r"$q_3=|0\rangle$",
        ha="center",
        va="top",
        fontsize=12,
        color=ACCENT,
    )
    ax.text(
        split,
        -0.13,
        r"$q_3=|1\rangle$",
        ha="center",
        va="top",
        fontsize=12,
        color=ACCENT,
    )
    ax.text(
        1.38,
        -0.13,
        r"$\omega$",
        ha="right",
        va="top",
        fontsize=12,
        color=INK,
    )

    brace_y = 1.12
    ax.annotate(
        "",
        xy=(split, brace_y),
        xytext=(-split, brace_y),
        arrowprops=dict(
            arrowstyle="<|-|>",
            color=INK,
            lw=1.05,
            mutation_scale=9,
        ),
        zorder=5,
    )
    ax.text(
        0.0,
        brace_y + 0.07,
        r"$\zeta_{\mathrm{ZZ}}$",
        ha="center",
        va="bottom",
        fontsize=13,
        color=INK,
    )

    ax.set_xlim(-1.45, 1.48)
    ax.set_ylim(-0.42, 1.38)
    ax.axis("off")
    ax.set_title(
        r"(c)   Target $q_2$ with one spectator",
        fontdict=TITLE_FONT,
        color=INK,
        pad=8,
        loc="left",
    )


def draw_figure() -> plt.Figure:
    fig = plt.figure(figsize=(10.1, 4.25), facecolor="white")
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.08, 1.18], wspace=0.02)
    ax_dev = fig.add_subplot(gs[0, 0])
    ax_spec = fig.add_subplot(gs[0, 1])
    draw_device(ax_dev)
    draw_spectrum(ax_spec)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.08, top=0.88)
    return fig


def main() -> None:
    fig = draw_figure()
    for suffix in ("pdf", "svg", "png"):
        kwargs = {"bbox_inches": "tight", "facecolor": "white", "pad_inches": 0.06}
        if suffix == "png":
            kwargs["dpi"] = 400
        fig.savefig(OUT_DIR / f"{STEM}.{suffix}", **kwargs)
    plt.close(fig)


if __name__ == "__main__":
    main()
