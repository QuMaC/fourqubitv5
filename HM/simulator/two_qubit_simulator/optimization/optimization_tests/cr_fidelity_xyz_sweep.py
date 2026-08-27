

from __future__ import annotations

import json
import os

import matplotlib.pyplot as plt
import numpy as np
import qutip as qt
from matplotlib.ticker import FormatStrFormatter
from tqdm import tqdm

from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import (
    CR_len_sweep,
    pauli_on_levels,
)
from HM.simulator.two_qubit_simulator.optimization.fidelity import gate_metrics

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

CR_PULSE_PARAMS = {"amp_mhz": 32.0, "t_rise_ns": 16, "phase_rad": 0}
REFERENCE_FLAT_LENS_NS = [184, 244, 272]
SWEEP_FLAT_LEN_NS = {"start": 0, "stop": 600, "step": 4}


def to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return to_jsonable(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    return value


def total_echoed_duration_ns(exp: CR_len_sweep, flat_len_ns: float) -> float:
    t_rise = exp.cr_pulse_params["t_rise_ns"]
    x_pi_len = exp.x_pi_pulse_params["length_ns"]
    return float(2 * (2 * t_rise + flat_len_ns) + 2 * x_pi_len)


def measure_xyz(exp: CR_len_sweep, x_pi, flat_len_ns: float) -> tuple[dict, float]:
    """Target-qubit ⟨X⟩, ⟨Y⟩, ⟨Z⟩ for |00⟩ and |10⟩ inputs."""
    n0, n1 = exp.simulator.dims
    I0 = qt.qeye(n0)
    X_op = qt.tensor(I0, pauli_on_levels("X", n1))
    Y_op = qt.tensor(I0, pauli_on_levels("Y", n1))
    Z_op = qt.tensor(I0, pauli_on_levels("Z", n1))
    psi00 = qt.basis(exp.simulator.dims, [0, 0])
    psi10 = qt.basis(exp.simulator.dims, [1, 0])

    timeline = exp._build_timeline(length=float(flat_len_ns), x_pi=x_pi)
    out = {}
    for ctrl, psi0 in [(0, psi00), (1, psi10)]:
        psi = exp.simulator.run_shot(timeline, psi0=psi0)
        out[str(ctrl)] = {
            "X": float(qt.expect(X_op, psi)),
            "Y": float(qt.expect(Y_op, psi)),
            "Z": float(qt.expect(Z_op, psi)),
        }
    r_mag = float(
        np.sqrt(
            (out["0"]["X"] + out["1"]["X"]) ** 2
            + (out["0"]["Y"] + out["1"]["Y"]) ** 2
            + (out["0"]["Z"] + out["1"]["Z"]) ** 2
        )
    )
    return out, r_mag


def evaluate_flat_len(exp: CR_len_sweep, x_pi, flat_len_ns: float) -> dict:
    flat_len_f = float(flat_len_ns)
    expectations, r_mag = measure_xyz(exp, x_pi, flat_len_f)
    timeline = exp._build_timeline(length=flat_len_f, x_pi=x_pi)
    U = exp._propagator_from_timeline(timeline)
    metrics = gate_metrics(U, gate="best_zx")
    return {
        "flat_len_ns": flat_len_f,
        "total_echoed_duration_ns": total_echoed_duration_ns(exp, flat_len_f),
        "expectations": expectations,
        "R_mag": r_mag,
        **metrics,
    }


def _format_row(row: dict) -> str:
    return (
        f"flat={row['flat_len_ns']:.0f} ns  "
        f"total={row['total_echoed_duration_ns']:.0f} ns  "
        f"|R|={row['R_mag']:.4f}  "
        f"zx={row.get('zx_gate', '?')}  "
        f"F_proc={row['process_fidelity']:.4f}  "
        f"F_zx90={row.get('process_fidelity_zx_90', float('nan')):.4f}  "
        f"F_zxm90={row.get('process_fidelity_zx_m90', float('nan')):.4f}  "
        f"leakage={row['leakage']:.4f}"
    )


def plot_results(rows: list[dict], out_png: str, f_best_row: dict | None) -> None:
    tlist = np.array([r["total_echoed_duration_ns"] for r in rows])
    r_mag = np.array([r["R_mag"] for r in rows])
    f_proc = np.array([r["process_fidelity"] for r in rows])
    f_zx90 = np.array([r.get("process_fidelity_zx_90", np.nan) for r in rows])
    f_zxm90 = np.array([r.get("process_fidelity_zx_m90", np.nan) for r in rows])

    r_min_row = min(rows, key=lambda r: r["R_mag"])

    fig, axes = plt.subplots(5, 1, figsize=(9, 10), sharex=True)
    labels = ["X", "Y", "Z"]
    colors = {0: "tab:blue", 1: "tab:red"}
    ctrl_labels = {0: "Control off (|00⟩)", 1: "Control on (|10⟩)"}

    for ax, comp in zip(axes[:3], labels):
        for ctrl in (0, 1):
            vals = [r["expectations"][str(ctrl)][comp] for r in rows]
            ax.plot(
                tlist,
                vals,
                "o-",
                ms=3,
                lw=1.2,
                color=colors[ctrl],
                label=ctrl_labels[ctrl],
            )
        ax.axvline(r_min_row["total_echoed_duration_ns"], color="tab:purple", ls="--", lw=1.0, alpha=0.7)
        if f_best_row is not None:
            ax.axvline(f_best_row["total_echoed_duration_ns"], color="tab:orange", ls=":", lw=1.2, alpha=0.8)
        ax.set_ylabel(f"<{comp}> target")
        ax.set_ylim(-1.1, 1.1)
        ax.axhline(0, color="k", lw=0.5, alpha=0.3)
        ax.grid(alpha=0.35)
        ax.legend(loc="upper right", fontsize=8)

    ax_r = axes[3]
    ax_r.plot(tlist, r_mag, "o-", color="tab:green", ms=3, lw=1.2, label="|R|")
    ax_r.plot(
        r_min_row["total_echoed_duration_ns"],
        r_min_row["R_mag"],
        "o",
        color="tab:purple",
        ms=8,
        label=f"min |R|={r_min_row['R_mag']:.3f} @ {r_min_row['total_echoed_duration_ns']:.0f} ns",
    )
    ax_r.axvline(r_min_row["total_echoed_duration_ns"], color="tab:purple", ls="--", lw=1.0, alpha=0.7)
    if f_best_row is not None:
        ax_r.axvline(
            f_best_row["total_echoed_duration_ns"],
            color="tab:orange",
            ls=":",
            lw=1.2,
            alpha=0.8,
            label=f"max F @ {f_best_row['total_echoed_duration_ns']:.0f} ns",
        )
    ax_r.set_ylabel("|R|")
    ax_r.set_ylim(0, max(1.5, r_mag.max() * 1.1))
    ax_r.grid(alpha=0.35)
    ax_r.legend(loc="upper right", fontsize=8)

    ax_f = axes[4]
    ax_f.plot(tlist, f_proc, "o-", color="tab:cyan", ms=3, lw=1.2, label="F best ZX")
    ax_f.plot(tlist, f_zx90, "o-", color="0.65", ms=2, lw=1.0, alpha=0.7, label="F vs zx_90")
    ax_f.plot(tlist, f_zxm90, "o-", color="0.45", ms=2, lw=1.0, alpha=0.7, label="F vs zx_m90")
    r_min_zx = r_min_row.get("zx_gate", "?")
    ax_f.plot(
        r_min_row["total_echoed_duration_ns"],
        r_min_row["process_fidelity"],
        "o",
        color="tab:purple",
        ms=8,
        label=(
            f"F at min |R|={r_min_row['process_fidelity']:.3f} "
            f"({r_min_zx}, flat={r_min_row['flat_len_ns']:.0f} ns)"
        ),
    )
    ax_f.axvline(
        r_min_row["total_echoed_duration_ns"],
        color="tab:purple",
        ls="--",
        lw=1.0,
        alpha=0.7,
    )
    if f_best_row is not None:
        zx = f_best_row.get("zx_gate", "?")
        ax_f.plot(
            f_best_row["total_echoed_duration_ns"],
            f_best_row["process_fidelity"],
            "o",
            color="tab:orange",
            ms=8,
            label=(
                f"max F={f_best_row['process_fidelity']:.3f} "
                f"({zx}, flat={f_best_row['flat_len_ns']:.0f} ns)"
            ),
        )
        ax_f.axvline(
            f_best_row["total_echoed_duration_ns"],
            color="tab:orange",
            ls=":",
            lw=1.2,
            alpha=0.8,
        )
    ax_f.set_ylabel("process F")
    ax_f.set_xlabel("Total echoed CR duration (ns)")
    ax_f.set_ylim(0, 1.05)
    ax_f.grid(alpha=0.35)
    ax_f.legend(loc="upper right", fontsize=8)

    for ax in axes:
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2g"))

    title = (
        f"CR XYZ + |R| + F vs duration  |  amp={CR_PULSE_PARAMS['amp_mhz']} MHz  "
        f"phase={CR_PULSE_PARAMS['phase_rad']} rad  echoed"
    )
    axes[0].set_title(title)
    fig.text(
        0.99,
        0.01,
        "purple: min |R| + F there   orange: max process F (best_zx)",
        ha="right",
        va="bottom",
        fontsize=8,
        color="0.35",
    )
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"Saved {out_png}")


def main() -> None:
    exp = CR_len_sweep(
        qubit_pair=[1, 2],
        echoed_cr=True,
        n_levels=3,
        cr_pulse_params=CR_PULSE_PARAMS,
    )
    x_pi = exp.build_x_pi()

    sweep_lengths = np.arange(
        SWEEP_FLAT_LEN_NS["start"],
        SWEEP_FLAT_LEN_NS["stop"] + SWEEP_FLAT_LEN_NS["step"] / 2,
        SWEEP_FLAT_LEN_NS["step"],
        dtype=float,
    )
    all_lengths = sorted(set(list(REFERENCE_FLAT_LENS_NS) + list(sweep_lengths)))

    rows: list[dict] = []
    print("Reference points:")
    for flat_len in REFERENCE_FLAT_LENS_NS:
        row = evaluate_flat_len(exp, x_pi, flat_len)
        rows.append(row)
        print(f"  {_format_row(row)}")

    print(
        f"\nSweeping flat_len {sweep_lengths[0]:.0f}–{sweep_lengths[-1]:.0f} ns "
        f"(step {SWEEP_FLAT_LEN_NS['step']:.0f}):"
    )
    for flat_len in tqdm(all_lengths, desc="CR length sweep"):
        if any(r["flat_len_ns"] == float(flat_len) for r in rows):
            continue
        rows.append(evaluate_flat_len(exp, x_pi, flat_len))

    rows.sort(key=lambda r: r["flat_len_ns"])
    r_min = min(rows, key=lambda r: r["R_mag"])
    f_best = max(rows, key=lambda r: float(r["process_fidelity"]))

    print(f"\n|R| minimum:\n  {_format_row(r_min)}")
    print(f"\nBest process fidelity (best_zx):\n  {_format_row(f_best)}")

    json_path = os.path.join(RESULTS_DIR, "cr_fidelity_xyz_sweep.json")
    payload = to_jsonable(
        {
            "cr_pulse_params": CR_PULSE_PARAMS,
            "fidelity_gate": "best_zx",
            "reference_flat_lens_ns": REFERENCE_FLAT_LENS_NS,
            "sweep_flat_len_ns": SWEEP_FLAT_LEN_NS,
            "results": rows,
            "r_min": r_min,
            "f_best": f_best,
        }
    )
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved {json_path}")

    png_path = os.path.join(RESULTS_DIR, "cr_fidelity_xyz_sweep.png")
    plot_results(rows, png_path, f_best_row=f_best)


if __name__ == "__main__":
    main()
