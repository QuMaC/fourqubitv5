"""Publication-style connectivity figure for the TIFR 6-qubit processor.

The hardware graph is the complete bipartite graph K_{3,3}: every
odd-numbered control qubit couples to every even-numbered target qubit.
Nodes are placed on a regular hexagon in device order q1 through q6,
matching the usual laboratory schematic (q5 at the right).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle


OUT_DIR = Path(__file__).resolve().parent
STEM = "six_qubit_connectivity"

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

# Standard polar convention: 0 at +x (right), counterclockwise.
# This reproduces the original layout with q1 at bottom-left (the original
# figure mislabeled that node as a second q4).
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
NODE_RADIUS = 0.205
LINEWIDTH = 1.45
TITLE_FONT = {
    "family": "STIXGeneral",
    "size": 15,
}


def draw_figure() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(4.35, 4.55), facecolor="white")
    ax.set_facecolor("white")
    ax.set_aspect("equal")
    ax.axis("off")

    for i, j in EDGES:
        x1, y1 = POSITIONS[i]
        x2, y2 = POSITIONS[j]
        ax.plot(
            [x1, x2],
            [y1, y2],
            color=INK,
            lw=LINEWIDTH,
            solid_capstyle="butt",
            zorder=1,
        )

    for q, (x, y) in POSITIONS.items():
        ax.add_patch(
            Circle(
                (x, y),
                NODE_RADIUS,
                facecolor="white",
                edgecolor=INK,
                lw=LINEWIDTH,
                zorder=2,
            )
        )
        ax.text(
            x,
            y - 0.008,
            rf"$q_{{{q}}}$",
            ha="center",
            va="center",
            fontsize=13.5,
            color=INK,
            zorder=3,
        )

    ax.set_xlim(-1.40, 1.40)
    ax.set_ylim(-1.40, 1.52)
    ax.set_title(
        "6-qubit system at TIFR",
        fontdict=TITLE_FONT,
        color=INK,
        pad=6,
    )

    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.91)
    return fig


def main() -> None:
    fig = draw_figure()
    for suffix in ("pdf", "svg", "png"):
        kwargs = {"bbox_inches": "tight", "facecolor": "white", "pad_inches": 0.05}
        if suffix == "png":
            kwargs["dpi"] = 450
        fig.savefig(OUT_DIR / f"{STEM}.{suffix}", **kwargs)
    plt.close(fig)


if __name__ == "__main__":
    main()
