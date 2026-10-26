"""Figures and numbers for the n-qubit simulator tutorial PDF.

Every number quoted in n_qubit_simulator_tutorial.tex comes from this script.
It writes PDF figures to ./figures and the numbers to ./tutorial_numbers.json.

Run from fourqubitv5:

    python HM/simulator/n_qubit_simulator/documentation/tutorial/make_tutorial_figures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import dynamiqs as dq
import jax.numpy as jnp
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import numpy as np
from dynamiqs import method as dq_method

from HM.simulator.n_qubit_simulator.analysis.dressed_frame import (
    dressed_basis,
    single_excitation_MHz,
    static_zz_MHz,
)
from HM.simulator.n_qubit_simulator.base_classes.device_base import (
    NQubitSimulatorBase,
    pair_cross_kerr_MHz,
)
from HM.simulator.n_qubit_simulator.engine.pulses_jax import _templates_1ns
from HM.simulator.n_qubit_simulator.experiments.gaussian_flattop_fidelity import (
    C1T2FlatFidelity,
)


OUT_DIR = Path(__file__).resolve().parent / "figures"
NUMBERS_PATH = Path(__file__).resolve().parent / "tutorial_numbers.json"
NUMBERS: dict = {}

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "mathtext.fontset": "cm",
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "font.size": 9,
        "axes.titlesize": 9,
        "axes.labelsize": 9,
        "legend.fontsize": 7.5,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
    }
)

SEGMENTS = (
    (0, 154, "CR(+)", "#dbe9f6"),
    (154, 206, "Xπ on Q1", "#fbe3d6"),
    (206, 360, "CR(-)", "#dbe9f6"),
    (360, 412, "Xπ on Q1", "#fbe3d6"),
)


_SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _sub(value) -> str:
    return str(value).translate(_SUBSCRIPTS)


def save(fig, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote figures/{name}.pdf")


def shade_segments(ax, t_max: float | None = None, labels: bool = True) -> None:
    for start, stop, label, color in SEGMENTS:
        if t_max is not None and start >= t_max:
            continue
        ax.axvspan(start, stop if t_max is None else min(stop, t_max), color=color, lw=0, zorder=0)
        if labels:
            ax.text(
                0.5 * (start + (stop if t_max is None else min(stop, t_max))),
                1.02,
                label,
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="bottom",
                fontsize=7,
            )


def set_tolerance(sim, tol: float = 1e-10) -> None:
    sim._integrator_method = dq_method.Tsit5(atol=tol, rtol=tol, max_steps=4_000_000)


def solve_saved(sim, timeline: dict, psi0: np.ndarray, times_ns: np.ndarray) -> np.ndarray:
    """Evolve a batch ``psi0`` of shape (n_states, dim). Returns (n_times, n_states, dim)."""

    batch = dq.asqarray(jnp.asarray(psi0[:, :, None]), dims=sim.dims)
    result = dq.sesolve(
        sim.hamiltonian(timeline),
        batch,
        jnp.asarray(np.asarray(times_ns, dtype=float) * 1e-3),
        method=sim._integrator_method,
        gradient=None,
        options=dq.Options(save_states=True, progress_meter=False),
    )
    states = np.asarray(dq.to_jax(result.states))[..., 0]
    n_states, n_times = psi0.shape[0], len(times_ns)
    if states.shape[:2] == (n_states, n_times) and n_states != n_times:
        states = np.moveaxis(states, 0, 1)
    return states.reshape(n_times, n_states, sim.dim)


def reduced_bloch(states: np.ndarray, dims: tuple[int, ...], position: int) -> dict:
    """Bloch components of one qubit on its levels 0 and 1. ``states`` is (n_times, dim)."""

    n_times = states.shape[0]
    psi = states.reshape((n_times,) + tuple(dims))
    psi = np.moveaxis(psi, position + 1, 1).reshape(n_times, dims[position], -1)
    rho = np.einsum("tik,tjk->tij", psi, psi.conj())
    rho01 = rho[:, 0, 1]
    return {
        "X": 2.0 * rho01.real,
        "Y": -2.0 * rho01.imag,
        "Z": (rho[:, 0, 0] - rho[:, 1, 1]).real,
        "rho01": rho01,
    }


def ket(sim, terms) -> np.ndarray:
    psi = np.zeros(sim.dim, dtype=complex)
    for occupations, amplitude in terms:
        psi[sim.basis_index(tuple(occupations))] += amplitude
    return psi / np.linalg.norm(psi)


def empty_timeline(sim, n_samples: int) -> dict:
    return {name: np.zeros(n_samples, dtype=complex) for name in sim.channel_names}


def flat_top(amp_MHz: float, flat_ns: int, rise_ns: int = 16) -> np.ndarray:
    """Same shape as the c1t2 CR half with every flat knob equal to ``amp_MHz``."""

    if rise_ns == 0:
        return np.full(int(flat_ns), amp_MHz, dtype=complex)
    rise, fall = (np.asarray(x, dtype=float) for x in _templates_1ns(rise_ns))
    return np.concatenate(
        [rise / rise[-1] * amp_MHz, np.full(int(flat_ns), amp_MHz), fall / fall[0] * amp_MHz]
    ).astype(complex)


def transmon_dressed_bloch(amp_MHz: float, detuning_MHz: float, anharm_MHz: float, n_levels: int = 4):
    """Bloch vectors of the drive-dressed states that connect to |0> and |1>.

    One transmon in the frame of the drive. ``detuning_MHz`` is carrier minus
    qubit frequency, so the qubit sits at -detuning in this frame.
    """

    n = np.diag(np.arange(n_levels, dtype=float))
    a = np.diag(np.sqrt(np.arange(1, n_levels, dtype=float)), 1)
    H = -detuning_MHz * n + 0.5 * anharm_MHz * (n @ n - n) + 0.5 * amp_MHz * (a + a.T)
    energies, vectors = np.linalg.eigh(H)
    out = {}
    for level in (0, 1, 2):
        k = np.argmax(np.abs(vectors[level, :]) ** 2)
        column = vectors[:, k]
        rho01 = column[0] * np.conj(column[1])
        out[level] = {
            "X": 2.0 * rho01.real,
            "Y": -2.0 * rho01.imag,
            "Z": abs(column[0]) ** 2 - abs(column[1]) ** 2,
            "amp": 2.0 * abs(rho01),
            "energy_MHz": float(energies[k]),
        }
    return out


# ==========================================================================
# Device numbers and the frequency map
# ==========================================================================


def device_numbers() -> None:
    base = NQubitSimulatorBase(n_levels=2)
    freq = {q.qubit_id: q.f_qubit_MHz for q in base.qubits}
    anharm = {q.qubit_id: q.anharm_MHz for q in base.qubits}
    NUMBERS["qubits"] = {
        q.qubit_id: {
            "f_MHz": q.f_qubit_MHz,
            "anharm_MHz": q.anharm_MHz,
            "frequency_source": q.frequency_source,
            "anharmonicity_source": q.anharmonicity_source,
        }
        for q in base.qubits
    }
    edges = {}
    for edge in base.coupling_edges:
        i, j = edge.qubit_i, edge.qubit_j
        zz = pair_cross_kerr_MHz(freq[i], anharm[i], freq[j], anharm[j], edge.J_MHz)
        edges[edge.name] = {
            "i": i,
            "j": j,
            "J_MHz": edge.J_MHz,
            "detuning_MHz": freq[i] - freq[j],
            "zz_kHz_model": 1e3 * zz,
            "source": edge.parameter_source,
        }
    NUMBERS["edges"] = edges
    NUMBERS["drive_lines"] = {
        name: {"target": line.target_qubit_id, "carrier_MHz": line.carrier_MHz}
        for name, line in base.simulator.drive_lines.items()
    }
    print("qubits")
    for qid, entry in NUMBERS["qubits"].items():
        print(f"  Q{qid} f {entry['f_MHz']:.6f}  anharm {entry['anharm_MHz']:+.1f}  {entry['frequency_source']}")
    print("edges")
    for name, entry in edges.items():
        print(
            f"  {name}  J {entry['J_MHz']:.4f}  det {entry['detuning_MHz']:+.3f}  "
            f"ZZ {entry['zz_kHz_model']:+.1f} kHz  {entry['source']}"
        )

    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    colors = {1: "tab:blue", 2: "tab:red", 3: "tab:green", 4: "tab:purple", 5: "tab:brown", 6: "tab:orange"}
    for row, qid in enumerate((1, 2, 3, 4, 5, 6)):
        y = 6 - row
        if qid in (1, 2, 3):
            ax.axhspan(y - 0.42, y + 0.42, color="#f2f2f2", lw=0, zorder=0)
        f01 = freq[qid]
        f12 = freq[qid] + anharm[qid]
        ax.plot([f01, f01], [y - 0.32, y + 0.32], color=colors[qid], lw=2.2)
        ax.plot([f12, f12], [y - 0.32, y + 0.32], color=colors[qid], lw=1.4, ls="--")
        ax.text(f01 + 4, y + 0.18, f"f{_sub(qid)}={f01:.1f}", fontsize=6.5, color=colors[qid], va="center")
        ax.text(f12 + 4, y + 0.18, f"f{_sub(qid)}+α{_sub(qid)}", fontsize=6.5, color=colors[qid], va="center")
    ax.annotate(
        "CR tone on Q1\nat f₂",
        xy=(freq[2], 6.0),
        xytext=(freq[2] - 120, 6.25),
        fontsize=6.5,
        arrowprops={"arrowstyle": "->", "lw": 0.8},
        va="center",
    )
    ax.plot([freq[2]], [6.0], marker="*", color="k", ms=8, zorder=5)
    ax.set_yticks([6, 5, 4, 3, 2, 1], [f"Q{q}" for q in (1, 2, 3, 4, 5, 6)])
    ax.set_xlabel("frequency (MHz)")
    ax.set_xlim(4580, 5175)
    ax.set_ylim(0.4, 6.6)
    ax.grid(axis="x", alpha=0.25)
    ax.set_title("0-1 transitions (solid) and 1-2 transitions (dashed) of the model chip; Q1, Q2, Q3 shaded")
    save(fig, "frequency_map")


# ==========================================================================
# Timeline and Hamiltonian structure
# ==========================================================================


def timeline_figure() -> None:
    chip = C1T2FlatFidelity(enable_c3_t2=True, q3_state=0)
    timeline = chip.build_timeline()
    t = np.arange(len(timeline["cr_c1_t2"]))
    cr = np.asarray(timeline["cr_c1_t2"])
    q1 = np.asarray(timeline["q1_drive"])
    rise = cr[:16].real
    NUMBERS["timeline"] = {
        "length_ns": int(t.size),
        "cr_half_ns": 154,
        "x_pi_ns": 52,
        "cr_amp_MHz": float(np.max(np.abs(cr))),
        "x_pi_peak_MHz": float(np.max(np.abs(q1))),
        "x_pi_drag_peak_MHz": float(np.max(np.abs(q1.imag))),
        "x_pi_area_MHz_us": float(np.sum(q1[154:206].real) * 1e-3),
        "rise_samples_MHz": [float(x) for x in rise],
        "cr_half_area_MHz_us": float(np.sum(cr[:154].real) * 1e-3),
    }

    fig = plt.figure(figsize=(6.8, 4.4))
    grid = fig.add_gridspec(2, 2, height_ratios=(1.25, 1.0), hspace=0.55, wspace=0.28)
    ax = fig.add_subplot(grid[0, :])
    shade_segments(ax)
    ax.step(t, cr.real, where="post", color="tab:blue", lw=1.1, label="cr_c1_t2, Re ε (tone at f₂, on Q1)")
    ax.step(t, q1.real, where="post", color="tab:red", lw=1.1, label="q1_drive, Re ε (tone at f₁)")
    ax.step(t, q1.imag, where="post", color="tab:orange", lw=1.0, label="q1_drive, Im ε (DRAG)")
    ax.axhline(0, color="0.5", lw=0.5)
    ax.set_xlim(0, 412)
    ax.set_xlabel("time (ns)")
    ax.set_ylabel("ε(t) (MHz)")
    ax.legend(loc="lower left", frameon=False, ncol=1)

    ax2 = fig.add_subplot(grid[1, 0])
    ax2.step(t[:26], cr[:26].real, where="post", color="tab:blue", lw=1.2)
    ax2.plot(t[:26] + 0.5, cr[:26].real, "o", color="tab:blue", ms=2.5)
    ax2.set_xlim(0, 25)
    ax2.set_xlabel("time (ns)")
    ax2.set_ylabel("MHz")
    ax2.set_title("CR rise: 16 samples, 1 ns sample-and-hold")
    ax2.grid(alpha=0.25)

    ax3 = fig.add_subplot(grid[1, 1])
    ax3.step(t[150:210], q1[150:210].real, where="post", color="tab:red", lw=1.2, label="Re (X)")
    ax3.step(t[150:210], q1[150:210].imag, where="post", color="tab:orange", lw=1.2, label="Im (DRAG)")
    ax3.set_xlim(150, 210)
    ax3.set_xlabel("time (ns)")
    ax3.set_title("first Xπ echo on Q1: 52 ns")
    ax3.legend(frameon=False, loc="upper right")
    ax3.grid(alpha=0.25)
    save(fig, "timeline")


def hamiltonian_structure_figure() -> None:
    chip = C1T2FlatFidelity(enable_c3_t2=True, q3_state=0)
    sim = chip.simulator
    a = [np.asarray(dq.to_jax(op)) for op in sim.a]
    drift = np.asarray(dq.to_jax(sim.H_drift))
    category = np.zeros((sim.dim, sim.dim), dtype=int)
    category[np.abs(drift) > 1e-12] = 1
    position = {q.qubit_id: p for p, q in enumerate(sim.qubits)}
    for code, name in ((2, "c1_t2"), (3, "c3_t2")):
        edge = next(e for e in sim.coupling_edges if e.name == name)
        hop = a[position[edge.qubit_i]].conj().T @ a[position[edge.qubit_j]]
        category[np.abs(hop + hop.conj().T) > 1e-12] = code
    for code, qid in ((4, 1), (5, 2), (6, 3)):
        op = a[position[qid]]
        category[np.abs(op + op.conj().T) > 1e-12] = code

    colors = ["white", "0.35", "tab:blue", "tab:orange", "tab:red", "tab:green", "tab:purple"]
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    ax.imshow(category, cmap=ListedColormap(colors), vmin=-0.5, vmax=6.5, interpolation="nearest")
    for boundary in (12, 24, 36):
        ax.axhline(boundary - 0.5, color="0.6", lw=0.6)
        ax.axvline(boundary - 0.5, color="0.6", lw=0.6)
    comp = [sim.basis_index((c, t, 0)) for c, t in ((0, 0), (0, 1), (1, 0), (1, 1))]
    ax.set_xticks(comp, [f"{i}" for i in comp])
    ax.set_yticks(comp, [f"{i}" for i in comp])
    ax.set_xlabel("column index (computational states with Q3 in 0 are ticked)")
    ax.set_ylabel("row index")
    ax.set_title("Nonzero pattern of the 48 x 48 Hamiltonian, dims (Q1, Q2, Q3) = (4, 4, 3)\ngrey lines: blocks of fixed Q1 occupation")
    handles = [
        Patch(color=colors[1], label="drift: (α/2) a†² a² (diagonal)"),
        Patch(color=colors[2], label="exchange c1_t2: a₁† a₂ + h.c."),
        Patch(color=colors[3], label="exchange c3_t2: a₃† a₂ + h.c."),
        Patch(color=colors[4], label=r"drives on Q1 (q1_drive, cr_c1_t2)"),
        Patch(color=colors[5], label=r"drive on Q2 (q2_drive)"),
        Patch(color=colors[6], label=r"drives on Q3 (q3_drive, cr_c3_t2)"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
    save(fig, "hamiltonian_structure")


# ==========================================================================
# Static ZZ physics
# ==========================================================================


def zz_numbers_and_figure() -> None:
    J12, a1, a2 = 3.216328, -271.2, -266.4
    f1, f2 = 5087.614585, 4983.462676
    delta = f1 - f2

    def perturbative(J, d, alpha_i, alpha_j):
        return 2 * J**2 * (alpha_i + alpha_j) / ((d + alpha_i) * (d - alpha_j))

    exact_c1t2 = pair_cross_kerr_MHz(f1, a1, f2, a2, J12)
    J32, a3, f3 = NUMBERS["edges"]["c3_t2"]["J_MHz"], -268.0, NUMBERS["qubits"][3]["f_MHz"]
    exact_c3t2 = pair_cross_kerr_MHz(f3, a3, f2, a2, J32)
    NUMBERS["zz"] = {
        "c1_t2_exact_kHz": 1e3 * exact_c1t2,
        "c1_t2_perturbative_kHz": 1e3 * perturbative(J12, delta, a1, a2),
        "c3_t2_exact_kHz": 1e3 * exact_c3t2,
        "c3_t2_perturbative_kHz": 1e3 * perturbative(J32, f3 - f2, a3, a2),
        "c1_t2_exact_kHz_q2_positive_anharm": 1e3 * pair_cross_kerr_MHz(f1, a1, f2, -a2, J12),
        "c1_t2_perturbative_kHz_q2_positive_anharm": 1e3 * perturbative(J12, delta, a1, -a2),
        "single_excitation_shift_q2_by_q3_kHz": 1e3 * J32**2 / (f2 - f3),
        "single_excitation_shift_q2_by_q1_kHz": 1e3 * J12**2 / (f2 - f1),
    }

    chip = C1T2FlatFidelity(enable_c3_t2=False, q3_state=0)
    off = single_excitation_MHz(chip.simulator, dressed_basis(chip.simulator))
    chip.set_edges(("c1_t2", "c3_t2"))
    basis_on = dressed_basis(chip.simulator)
    on = single_excitation_MHz(chip.simulator, basis_on)
    NUMBERS["zz"]["chip_dressed_shift_kHz"] = {qid: 1e3 * (on[qid] - off[qid]) for qid in on}
    NUMBERS["zz"]["chip_zz_kHz"] = {
        "q1_q2": 1e3 * static_zz_MHz(chip.simulator, basis_on, 1, 2),
        "q2_q3": 1e3 * static_zz_MHz(chip.simulator, basis_on, 2, 3),
        "q1_q3": 1e3 * static_zz_MHz(chip.simulator, basis_on, 1, 3),
    }
    NUMBERS["zz"]["chip_min_overlap"] = basis_on.min_overlap
    print("zz", json.dumps(NUMBERS["zz"], indent=1))

    deltas = np.linspace(-420, 420, 1681)
    deltas = deltas[np.abs(deltas) > 6]
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    for alpha_j, color, label in ((a2, "tab:blue", "α₂ = −266.4 MHz (transmon)"), (-a2, "tab:green", "α₂ = +266.4 MHz (opposite sign)")):
        exact = np.array([1e3 * pair_cross_kerr_MHz(f2 + d, a1, f2, alpha_j, J12) for d in deltas])
        pert = 1e3 * perturbative(J12, deltas, a1, alpha_j)
        ax.plot(deltas, exact, color=color, lw=1.4, label=label + ", exact")
        ax.plot(deltas, pert, color=color, lw=0.9, ls="--", label="perturbative formula")
    ax.plot([delta], [1e3 * exact_c1t2], "ko", ms=4)
    ax.annotate(
        f"c1_t2: {1e3 * exact_c1t2:.1f} kHz",
        xy=(delta, 1e3 * exact_c1t2),
        xytext=(delta - 200, 3.0e3),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    for x in (-a1, a2):
        ax.axvline(x, color="0.6", lw=0.6, ls=":")
    ax.set_yscale("symlog", linthresh=10)
    ax.set_ylim(-3e4, 3e4)
    ax.set_xlabel("Δ = f₁ − f₂ (MHz)")
    ax.set_ylabel("static ζ (kHz, symlog)")
    ax.set_title("Static ZZ of two transmons, J = 3.216 MHz, α₁ = −271.2 MHz")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    save(fig, "zz_vs_detuning")


def cr_rate_numbers() -> None:
    J, omega, delta = 3.216328, 21.0, 5087.614585 - 4983.462676
    rows = {}
    for label, alpha1 in (("negative", -271.2), ("positive", 271.2)):
        nu_zx = -J * omega * alpha1 / (delta * (delta + alpha1))
        nu_ix = -J * omega / (delta + alpha1)
        rows[label] = {
            "nu_ZX_MHz": nu_zx,
            "nu_IX_MHz": nu_ix,
            "t_quarter_turn_ns": 1e3 / (4 * abs(nu_zx)),
        }
    cr = np.array(NUMBERS["timeline"]["rise_samples_MHz"])
    flat_equivalent_half = 122 + 2 * cr.sum() / omega
    NUMBERS["cr_rate"] = {
        "leading_order": rows,
        "flat_equivalent_ns_per_half": float(flat_equivalent_half),
        "flat_equivalent_ns_total": float(2 * flat_equivalent_half),
    }
    print("cr rate", json.dumps(NUMBERS["cr_rate"], indent=1))


# ==========================================================================
# Micro-oscillations
# ==========================================================================


def micro_q1_frames() -> None:
    """Q1 Bloch components in its own frame and in the frame of the CR tone."""

    chip = C1T2FlatFidelity(enable_c3_t2=True, q3_state=0)
    sim = chip.simulator
    set_tolerance(sim, 1e-10)
    timeline = chip.build_timeline()
    times = np.arange(0.0, 412.0 + 1e-9, 0.25)
    psi0 = np.stack([ket(sim, [((0, 0, 0), 1.0)]), ket(sim, [((1, 0, 0), 1.0)])])
    states = solve_saved(sim, timeline, psi0, times)

    f1 = sim.qubits[0].frame_MHz
    carrier = sim.drive_lines["cr_c1_t2"].carrier_MHz
    detuning = carrier - f1
    omega_t = np.real(np.asarray(timeline["cr_c1_t2"]))[np.clip(np.floor(times).astype(int), 0, 411)]
    theory = [transmon_dressed_bloch(w, detuning, sim.qubits[0].anharm_MHz, 4) for w in omega_t]
    theta = np.arctan(21.0 / abs(detuning))
    NUMBERS["micro"] = {
        "cr_detuning_MHz": detuning,
        "omega_MHz": 21.0,
        "theta_rad": float(theta),
        "sin_theta": float(np.sin(theta)),
        "cos_theta": float(np.cos(theta)),
        "generalized_rabi_MHz": float(np.hypot(21.0, detuning)),
        "period_ns": float(1e3 / abs(detuning)),
        "dressed_0": transmon_dressed_bloch(21.0, detuning, sim.qubits[0].anharm_MHz, 4)[0],
        "dressed_1": transmon_dressed_bloch(21.0, detuning, sim.qubits[0].anharm_MHz, 4)[1],
    }

    window = times <= 160.0
    fig, axes = plt.subplots(3, 2, figsize=(6.8, 5.4), sharex=True)
    for column, frame in enumerate(("qubit", "drive")):
        for b, (label, color) in enumerate((("Q1 starts in |0>", "tab:blue"), ("Q1 starts in |1>", "tab:red"))):
            bloch = reduced_bloch(states[:, b, :], sim.dims, 0)
            rho01 = bloch["rho01"]
            if frame == "drive":
                rho01 = rho01 * np.exp(-2j * np.pi * detuning * times * 1e-3)
            comps = {"X": 2 * rho01.real, "Y": -2 * rho01.imag, "Z": bloch["Z"]}
            for row, which in enumerate(("X", "Y", "Z")):
                ax = axes[row, column]
                ax.plot(times[window], comps[which][window], color=color, lw=0.8, label=label)
                level_theory = np.array([entry[b][which] for entry in theory])
                if frame == "drive" or which == "Z":
                    ax.plot(times[window], level_theory[window], color="k", lw=0.7, ls="--")
                else:
                    amp = np.array([entry[b]["amp"] for entry in theory])
                    ax.plot(times[window], amp[window], color="0.4", lw=0.6, ls=":")
                    ax.plot(times[window], -amp[window], color="0.4", lw=0.6, ls=":")
        for row, which in enumerate(("X", "Y", "Z")):
            ax = axes[row, column]
            ax.axvspan(154, 160, color="#fbe3d6", lw=0)
            ax.grid(alpha=0.25)
            if which == "Z":
                ax.set_ylim(-1.08, 1.08)
            else:
                ax.set_ylim(-0.3, 0.3)
            if column == 0:
                ax.set_ylabel(f"Q1  {which}")
        axes[0, column].set_title(
            "frame rotating at f₁ (what the simulator stores)" if frame == "qubit" else "frame rotating at the CR tone f₂"
        )
        axes[2, column].set_xlabel("time (ns)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.suptitle(
        "CR(+) half of the c1t2 gate. Dashed: drive-dressed eigenstate of the 4-level Q1. Dotted: its amplitude.",
        fontsize=8.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    legend = fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.955))
    for line in legend.get_lines():
        line.set_linewidth(2.0)
    save(fig, "micro_q1_frames")

    flat = (times > 40) & (times < 130)
    for b in (0, 1):
        bloch = reduced_bloch(states[:, b, :], sim.dims, 0)
        rho_d = bloch["rho01"] * np.exp(-2j * np.pi * detuning * times * 1e-3)
        NUMBERS["micro"][f"sim_level{b}"] = {
            "amp_mean": float(np.mean(2 * np.abs(bloch["rho01"][flat]))),
            "Xd_mean": float(np.mean(2 * rho_d.real[flat])),
            "Xd_ripple": float(np.ptp(2 * rho_d.real[flat])),
            "Z_mean": float(np.mean(bloch["Z"][flat])),
            "Z_ripple": float(np.ptp(bloch["Z"][flat])),
        }
    print("micro", json.dumps(NUMBERS["micro"], indent=1, default=float))


def micro_spectrum() -> None:
    """Long CR tone, no echo. Spectra of the three coherences in their own frames."""

    chip = C1T2FlatFidelity(enable_c3_t2=True, q3_state=0)
    sim = chip.simulator
    set_tolerance(sim, 1e-10)
    pulse = flat_top(21.0, 2000)
    timeline = empty_timeline(sim, pulse.size)
    timeline["cr_c1_t2"] = pulse
    times = np.arange(0.0, pulse.size + 1e-9, 0.5)
    psi0 = ket(sim, [((0, 0, 0), 1.0)])[None, :]
    states = solve_saved(sim, timeline, psi0, times)[:, 0, :]

    f = {q.qubit_id: q.frame_MHz for q in sim.qubits}
    detuning = f[2] - f[1]
    dressed = transmon_dressed_bloch(21.0, detuning, sim.qubits[0].anharm_MHz, 4)
    splitting = dressed[1]["energy_MHz"] - dressed[0]["energy_MHz"]
    predicted = {
        "Q1 coherence": {"f₂−f₁": (detuning, -60)},
        "Q1 Z": {r"dressed splitting": (splitting, 6)},
        "Q2 coherence": {"f₁−f₂": (f[1] - f[2], -62), "f₃−f₂": (f[3] - f[2], 6)},
        "Q3 coherence": {"f₂−f₃": (f[2] - f[3], -60)},
    }
    window = (times > 100) & (times < 1980)
    fig, axes = plt.subplots(4, 1, figsize=(6.4, 6.2), sharex=True)
    peaks = {}
    n_pad = 1 << 16
    freqs = np.fft.fftshift(np.fft.fftfreq(n_pad, d=0.5e-3))
    for row, key in enumerate(predicted):
        position = int(key[1]) - 1
        bloch = reduced_bloch(states, sim.dims, position)
        if key == "Q1 Z":
            signal = bloch["Z"][window] - bloch["Z"][window].mean()
        elif key == "Q2 coherence":
            signal = bloch["rho01"][window]
        else:
            signal = bloch["rho01"][window] - bloch["rho01"][window].mean()
        spectrum = np.fft.fftshift(np.fft.fft(signal * np.hanning(signal.size), n_pad))
        magnitude = np.abs(spectrum) / np.abs(spectrum).max()
        ax = axes[row]
        ax.semilogy(freqs, magnitude, color="k", lw=0.8)
        for label, (value, offset) in predicted[key].items():
            ax.axvline(value, color="tab:red", lw=0.8, ls="--")
            ax.text(value + offset, 0.05, label + f"\n{value:+.2f}", color="tab:red", fontsize=6.5)
        ax.set_ylim(1e-5, 3)
        ax.set_xlim(-250, 250)
        ax.set_ylabel(key, fontsize=8)
        ax.grid(alpha=0.25)
        band = (np.abs(freqs) > 20) if key != "Q1 Z" else (freqs > 20)
        peaks[key] = float(freqs[band][np.argmax(magnitude[band])])
    axes[0].set_title("2 us flat CR tone on Q1 at f₂, start in |000>. Spectra in each qubit's own frame (normalized)")
    axes[3].set_xlabel("frequency (MHz)")
    fig.tight_layout()
    save(fig, "micro_spectrum")
    NUMBERS["micro"]["spectrum_peak_away_from_zero_MHz"] = peaks
    NUMBERS["micro"]["dressed_splitting_MHz"] = float(splitting)
    print("spectrum peaks", peaks, "dressed splitting", splitting)


def micro_q2_echo() -> None:
    """Q2 kinks during the echo pulses, when Q1 passes through a superposition."""

    chip = C1T2FlatFidelity(enable_c3_t2=True, q3_state=0)
    sim = chip.simulator
    set_tolerance(sim, 1e-10)
    timeline = chip.build_timeline()
    times = np.arange(0.0, 412.0 + 1e-9, 0.25)
    psi0 = np.stack([ket(sim, [((0, 0, 0), 1.0)]), ket(sim, [((1, 0, 0), 1.0)])])
    states = solve_saved(sim, timeline, psi0, times)
    d12 = sim.qubits[0].frame_MHz - sim.qubits[1].frame_MHz

    fig, axes = plt.subplots(2, 2, figsize=(6.8, 3.9), sharex=True)
    window = (times >= 140) & (times <= 222)
    echo = (times >= 158) & (times <= 202)
    frequencies = {}
    for b, (label, color) in enumerate((("Q1 starts in |0>", "tab:blue"), ("Q1 starts in |1>", "tab:red"))):
        q1 = reduced_bloch(states[:, b, :], sim.dims, 0)
        q2 = reduced_bloch(states[:, b, :], sim.dims, 1)
        axes[0, 0].plot(times[window], q2["X"][window], color=color, lw=0.9, label=label)
        axes[0, 1].plot(times[window], q2["Z"][window], color=color, lw=0.9)
        axes[1, 0].plot(times[window], q1["Z"][window], color=color, lw=0.9)
        axes[1, 1].plot(times[window], np.sqrt(1 - np.clip(q1["Z"][window], -1, 1) ** 2), color=color, lw=0.9)
        signal = q2["rho01"][echo]
        trend = np.polyval(np.polyfit(times[echo], signal.real, 3), times[echo]) + 1j * np.polyval(np.polyfit(times[echo], signal.imag, 3), times[echo])
        n_pad = 1 << 15
        spectrum = np.abs(np.fft.fft((signal - trend) * np.hanning(signal.size), n_pad))
        freqs = np.fft.fftfreq(n_pad, d=0.25e-3)
        band = np.abs(freqs) > 30
        frequencies[b] = float(freqs[band][np.argmax(spectrum[band])])
    titles = (("Q2  X", "Q2  Z"), ("Q1  Z", "Q1 distance from the poles √(1−Z²)"))
    for r in range(2):
        for c in range(2):
            ax = axes[r, c]
            ax.axvspan(154, 206, color="#fbe3d6", lw=0, zorder=0)
            ax.set_title(titles[r][c], fontsize=8)
            ax.grid(alpha=0.25)
    for ax in axes[1]:
        ax.set_xlabel("time (ns)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.suptitle("First Xπ echo (shaded). Q2 wiggles at f₁−f₂ = %.2f MHz while Q1 sits away from its poles" % d12, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    legend = fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0))
    for line in legend.get_lines():
        line.set_linewidth(2.0)
    save(fig, "micro_q2_echo")
    NUMBERS["micro"]["q2_echo_ripple_MHz"] = frequencies
    print("q2 echo ripple frequency", frequencies)


def micro_exchange_circle() -> None:
    """No pulses. Q2 in |+>, Q3 in |0>: Q3 traces a small circle at f3 - f2."""

    chip = C1T2FlatFidelity(enable_c3_t2=True, q3_state=0)
    sim = chip.simulator
    set_tolerance(sim, 1e-11)
    n_samples = 60
    times = np.arange(0.0, n_samples + 1e-9, 0.1)
    psi0 = ket(sim, [((0, 0, 0), 1.0), ((0, 1, 0), 1.0)])[None, :]
    on = reduced_bloch(solve_saved(sim, empty_timeline(sim, n_samples), psi0, times)[:, 0, :], sim.dims, 2)
    chip.set_edges(("c1_t2",))
    off = reduced_bloch(solve_saved(sim, empty_timeline(sim, n_samples), psi0, times)[:, 0, :], sim.dims, 2)

    edge = NUMBERS["edges"]["c3_t2"]
    J = edge["J_MHz"]
    d32 = sim.qubits[2].frame_MHz - sim.qubits[1].frame_MHz
    eps = J / d32
    two_rho = eps * (1.0 - np.exp(-2j * np.pi * d32 * times * 1e-3))
    theory = {"X": two_rho.real, "Y": -two_rho.imag}
    NUMBERS["micro"]["exchange"] = {
        "J_MHz": J,
        "detuning_MHz": d32,
        "J_over_detuning": eps,
        "sim_X_max": float(on["X"].max()),
        "sim_Y_ptp": float(np.ptp(on["Y"])),
        "theory_X_max": float(2 * eps),
        "max_abs_dev_from_first_order": float(
            max(np.max(np.abs(on["X"] - theory["X"])), np.max(np.abs(on["Y"] - theory["Y"])))
        ),
    }

    fig = plt.figure(figsize=(6.8, 2.7))
    grid = fig.add_gridspec(1, 3, width_ratios=(1.4, 1.4, 1.0), wspace=0.42)
    for column, which in enumerate(("X", "Y")):
        ax = fig.add_subplot(grid[0, column])
        ax.plot(times, on[which], color="tab:green", lw=1.2, label="c3_t2 on")
        ax.plot(times, theory[which], color="k", lw=0.8, ls="--", label="first-order formula")
        ax.plot(times, off[which], color="0.5", lw=1.0, label="c3_t2 off")
        ax.set_xlabel("time (ns)")
        ax.set_ylabel(f"Q3  {which}")
        ax.grid(alpha=0.25)
        if column == 0:
            handles, labels = ax.get_legend_handles_labels()
    legend = fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.04))
    for line in legend.get_lines():
        line.set_linewidth(2.0)
    ax = fig.add_subplot(grid[0, 2])
    ax.plot(on["X"], on["Y"], color="tab:green", lw=1.0)
    ax.plot(theory["X"], theory["Y"], color="k", lw=0.7, ls="--")
    ax.set_aspect("equal")
    ax.set_xlabel("Q3 X")
    ax.set_ylabel("Q3 Y")
    ax.set_title(f"radius J/Δ = {eps:.4f}", fontsize=8)
    ax.grid(alpha=0.25)
    fig.suptitle("No pulse at all. Start in Q1 |0>, Q2 (|0>+|1>)/√2, Q3 |0>. Q3 ripples at f₃−f₂ = %.2f MHz" % d32, fontsize=8.5)
    save(fig, "micro_exchange_circle")
    print("exchange", NUMBERS["micro"]["exchange"])


def _q1_alone():
    base = NQubitSimulatorBase(qubit_ids=(1, 2), n_levels=4, dt_sample_ns=1.0)
    sim = base.simulator
    for edge in sim.coupling_edges:
        edge.enabled = False
    set_tolerance(sim, 1e-10)
    return sim


def micro_ramp() -> None:
    """Sudden versus 16 ns ramp: the drive-frame Bloch vector of a lone Q1."""

    sim = _q1_alone()
    detuning = sim.drive_lines["cr_c1_t2"].carrier_MHz - sim.qubits[0].frame_MHz
    psi0 = ket(sim, [((0, 0), 1.0)])[None, :]
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.6), sharey=False)
    results = {}
    for rise, color, label in ((0, "tab:orange", "square turn-on"), (16, "tab:blue", "16 ns c1t2 rise")):
        pulse = flat_top(21.0, 120, rise_ns=rise)
        timeline = empty_timeline(sim, pulse.size + 20)
        timeline["cr_c1_t2"][: pulse.size] = pulse
        times = np.arange(0.0, pulse.size + 20 + 1e-9, 0.1)
        bloch = reduced_bloch(solve_saved(sim, timeline, psi0, times)[:, 0, :], sim.dims, 0)
        xd = 2 * (bloch["rho01"] * np.exp(-2j * np.pi * detuning * times * 1e-3)).real
        axes[0].plot(times, bloch["Z"], color=color, lw=1.0, label=label)
        axes[1].plot(times, xd, color=color, lw=1.0, label=label)
        flat = (times > rise + 10) & (times < rise + 110)
        results[label] = {"Z_min": float(bloch["Z"][flat].min()), "Z_ptp": float(np.ptp(bloch["Z"][flat])), "Xd_ptp": float(np.ptp(xd[flat]))}
    theta = np.arctan(21.0 / abs(detuning))
    axes[0].axhline(np.cos(theta), color="k", ls="--", lw=0.7)
    axes[0].axhline(np.cos(2 * theta), color="k", ls=":", lw=0.7)
    axes[0].text(150, np.cos(theta) + 0.003, "cos θ", fontsize=7, ha="right", va="bottom")
    axes[0].text(150, np.cos(2 * theta) + 0.003, "cos 2θ", fontsize=7, ha="right", va="bottom")
    axes[1].axhline(-np.sin(theta), color="k", ls="--", lw=0.7)
    axes[0].set_ylim(np.cos(2 * theta) - 0.012, 1.006)
    axes[0].set_ylabel("Q1  Z")
    axes[1].set_ylabel("Q1  X in the drive frame")
    for ax in axes:
        ax.set_xlabel("time (ns)")
        ax.grid(alpha=0.25)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle("Lone Q1 (couplings off), CR tone 21 MHz at f₂: sudden turn-on nutates, a smooth ramp follows the dressed state", fontsize=8.5)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.01))
    save(fig, "micro_ramp")
    NUMBERS["micro"]["ramp"] = results
    print("ramp", results)


def micro_amplitude_scan() -> None:
    """Oscillation amplitude versus drive strength and versus detuning."""

    sim = _q1_alone()
    anharm = sim.qubits[0].anharm_MHz
    carrier = sim.drive_lines["cr_c1_t2"].carrier_MHz
    f1 = sim.qubits[0].frame_MHz
    psi0 = np.stack([ket(sim, [((0, 0), 1.0)]), ket(sim, [((1, 0), 1.0)])])
    # sesolve starts at times[0], so t = 0 must be the first saved time.
    times = np.concatenate([[0.0], np.arange(56.0, 116.0 + 1e-9, 1.0)])

    def measure(amp, detuning):
        sim.qubits[0].frame_MHz = carrier - detuning
        pulse = flat_top(amp, 100)
        timeline = empty_timeline(sim, pulse.size)
        timeline["cr_c1_t2"] = pulse
        states = solve_saved(sim, timeline, psi0, times)[1:]
        return [float(np.mean(2 * np.abs(reduced_bloch(states[:, b, :], sim.dims, 0)["rho01"]))) for b in (0, 1)]

    amps = np.array([2, 5, 8, 11, 14, 17, 21, 25, 30, 35, 40, 46, 52, 60], dtype=float)
    detuning0 = carrier - f1
    sim_amp = np.array([measure(w, detuning0) for w in amps])
    detunings = np.array([-220, -190, -160, -130, -104.151909, -80, -60, -45, 45, 60, 80, 110, 150, 190, 230], dtype=float)
    sim_det = np.array([measure(21.0, d) for d in detunings])
    sim.qubits[0].frame_MHz = f1

    fine_amp = np.linspace(0.5, 62, 300)
    fine_det = np.concatenate([np.linspace(-235, -38, 200), np.linspace(38, 240, 200)])
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.8))
    ax = axes[0]
    ax.plot(fine_amp, fine_amp / np.hypot(fine_amp, detuning0), color="0.3", lw=0.9, ls=":", label="two-level sin θ")
    for b, color in ((0, "tab:blue"), (1, "tab:red")):
        exact = [transmon_dressed_bloch(w, detuning0, anharm, 4)[b]["amp"] for w in fine_amp]
        ax.plot(fine_amp, exact, color=color, lw=1.0, label=f"dressed state of |{b}>, 4 levels")
        ax.plot(amps, sim_amp[:, b], "o", color=color, ms=3, label=f"simulation, Q1 starts in |{b}>")
    ax.axvline(21.0, color="0.6", lw=0.6, ls="--")
    ax.set_xlabel("CR amplitude Ω (MHz)")
    ax.set_ylabel("oscillation amplitude 2|ρ₀₁|")
    ax.set_title("δ = f₂ − f₁ = %.2f MHz" % detuning0)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=6.3, loc="upper left")
    ax = axes[1]
    for segment in (fine_det[fine_det < 0], fine_det[fine_det > 0]):
        ax.plot(segment, 21.0 / np.hypot(21.0, segment), color="0.3", lw=0.9, ls=":")
        for b, color in ((0, "tab:blue"), (1, "tab:red")):
            exact = [transmon_dressed_bloch(21.0, d, anharm, 4)[b]["amp"] for d in segment]
            ax.plot(segment, exact, color=color, lw=1.0)
    for b, color in ((0, "tab:blue"), (1, "tab:red")):
        ax.plot(detunings, sim_det[:, b], "o", color=color, ms=3)
    ax.axvline(detuning0, color="0.6", lw=0.6, ls="--")
    ax.axvline(anharm, color="tab:red", lw=0.6, ls=":")
    ax.text(anharm + 4, 0.42, r"1-2 resonance", color="tab:red", fontsize=6.5, rotation=90, va="top")
    ax.axvline(anharm / 2, color="tab:blue", lw=0.6, ls=":")
    ax.text(anharm / 2 - 4, 0.48, "two-photon 0-2 at α₁/2", color="tab:blue", fontsize=6.5, rotation=90, va="top", ha="right")
    ax.set_xlabel("detuning δ = carrier − f₁ (MHz)")
    ax.set_title("Ω = 21 MHz")
    ax.set_ylim(0, 0.5)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    save(fig, "micro_amplitude_scan")
    NUMBERS["micro"]["scan"] = {
        "amps_MHz": amps.tolist(),
        "sim_amp": sim_amp.tolist(),
        "detunings_MHz": detunings.tolist(),
        "sim_det": sim_det.tolist(),
        "max_dev_from_dressed": float(
            max(
                max(abs(sim_amp[k, b] - transmon_dressed_bloch(w, detuning0, anharm, 4)[b]["amp"]) for k, w in enumerate(amps) for b in (0, 1)),
                max(abs(sim_det[k, b] - transmon_dressed_bloch(21.0, d, anharm, 4)[b]["amp"]) for k, d in enumerate(detunings) for b in (0, 1)),
            )
        ),
    }
    print("scan max deviation from dressed-state theory", NUMBERS["micro"]["scan"]["max_dev_from_dressed"])


def main() -> None:
    device_numbers()
    timeline_figure()
    hamiltonian_structure_figure()
    zz_numbers_and_figure()
    cr_rate_numbers()
    micro_q1_frames()
    micro_spectrum()
    micro_q2_echo()
    micro_exchange_circle()
    micro_ramp()
    micro_amplitude_scan()
    NUMBERS_PATH.write_text(json.dumps(NUMBERS, indent=1, default=float))
    print(f"wrote {NUMBERS_PATH.name}")
    print("TUTORIAL FIGURES OK")


if __name__ == "__main__":
    main()
