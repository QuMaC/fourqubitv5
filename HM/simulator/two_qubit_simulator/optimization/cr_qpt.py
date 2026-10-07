"""Process tomography of an echoed CR pulse, plotted as a Qiskit-style cityscape.

The pulse file is a GRAPE ``.npz`` (simple or robust) with ``cr_half_opt_I/Q``
and, when present, ``cr_half_seed_I/Q``. Each half is embedded in the echoed
sequence ``+u -> Xpi -> -u -> Xpi`` and propagated on the two-qubit simulator.

What is saved, per case (flat-top and/or optimized, at each target-frame shift):

- the 4x4 computational unitary, with only a global phase removed
- the 16x16 chi matrix of that block (Qiskit's Pauli basis, qubit 0 = target)
- process fidelity, average gate fidelity, and leakage against one locked ZX target

Local Z rotations are left in the lab frame. A spectator-dependent phase therefore
stays visible. The global phase of each propagator is chosen so that
``Tr(U_target^dag U)`` is real and positive.

``which`` selects the picture, at run time or later from the saved ``*_qpt.npz``:

- ``unitary``       4x4 computational unitary
- ``unitary_diff``  that unitary minus the ideal ZX
- ``chi``           16x16 process matrix
- ``chi_diff``      that chi matrix minus the ideal ZX chi
- ``all``           every one of the above

Qiskit is not required. The city plot follows ``plot_state_city``: real bars in
midnight blue, imaginary bars in crimson, basis labels on both floor axes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from HM.simulator.two_qubit_simulator.optimization.fidelity import (
    gate_metrics,
    zx_target_unitary,
)

WHICH_CHOICES = ("unitary", "unitary_diff", "chi", "chi_diff", "all")
COMP_LABELS = ("00", "01", "10", "11")
_CITY_COLORS = ("midnightblue", "crimson")


def pauli_labels(n_qubits: int = 2) -> list[str]:
    """Qiskit Pauli-basis order. The rightmost character is qubit 0 (the target)."""
    one = ("I", "X", "Y", "Z")
    labels = list(one)
    for _ in range(n_qubits - 1):
        labels = [left + right for left in one for right in labels]
    return labels


PAULI_LABELS = tuple(pauli_labels(2))


def chi_from_unitary(U: np.ndarray) -> np.ndarray:
    """Chi matrix of one Kraus operator, in Qiskit's Pauli basis.

    ``U`` is the computational block. When leakage makes it non-unitary the
    channel is completely positive and not trace-preserving, and ``Tr(chi) < 1``.
    """
    U = np.asarray(U, dtype=complex)
    if U.ndim != 2 or U.shape[0] != U.shape[1]:
        raise ValueError(f"U must be square, got {U.shape}")
    dim = U.shape[0]
    n_qubits = int(round(np.log2(dim)))
    if 2**n_qubits != dim:
        raise ValueError(f"chi is defined on a qubit space, got dimension {dim}")
    vec = np.ravel(U, order="F")
    choi = np.outer(vec, np.conj(vec))
    return _transform_to_pauli(choi, n_qubits)


def fix_global_phase(U: np.ndarray, U_target: np.ndarray) -> tuple[np.ndarray, float]:
    """Return ``e^{iφ} U`` so that ``Tr(U_target^dag U)`` is real and non-negative.

    The returned angle is φ in radians. Local unitary factors are not removed.
    """
    U = np.asarray(U, dtype=complex)
    overlap = np.trace(np.asarray(U_target, dtype=complex).conj().T @ U)
    if abs(overlap) < 1e-18:
        return U.copy(), 0.0
    phase = -float(np.angle(overlap))
    return U * np.exp(1j * phase), phase


def plot_city(
    matrix: np.ndarray,
    labels: list[str] | tuple[str, ...],
    title: str,
    out_png: str,
    symbol: str,
    fidelity: float | None = None,
    color_cutoff: float | None = None,
    color_gamma: float = 0.5,
    zlim: tuple[float, float] | None = None,
) -> str:
    """Real/imaginary 3d bar plot in the style of Qiskit's ``plot_state_city``.

    The vertical axis is the real or imaginary part of one matrix entry.
    For ``chi`` that entry is chi_ij in Qiskit's normalization,
    E(rho) = (1/2^n) sum_ij chi_ij P_i rho P_j, so an ideal two-qubit Pauli
    term has height 4 and ZX(+/- pi/2) has height 2 on the II/ZX block.
    For ``unitary`` the entry is U_ij in the computational basis 00, 01, 10, 11.

    Bar color stays blue for the real part and red for the imaginary part.
    Darkness follows ``|z| ** color_gamma`` and saturates at ``color_cutoff``.
    ``color_cutoff=None`` saturates at the largest bar that is at least 4 times
    below the peak, so the dominant terms stay fully dark and the error bars
    use the whole light-to-dark range.

    ``zlim`` replaces the per-figure vertical range. A flat-top / optimized pair
    passes the same limits, taken from whichever matrix extends further.
    """
    data = np.asarray(matrix, dtype=complex)
    if data.ndim != 2 or data.shape[0] != data.shape[1]:
        raise ValueError(f"city plot expects a square matrix, got {data.shape}")
    n = data.shape[0]
    if len(labels) != n:
        raise ValueError(f"expected {n} labels, got {len(labels)}")

    real = np.real(data)
    imag = np.imag(data)
    fig_in = 8.0 if n <= 4 else 13.0
    font = 12 if n <= 4 else 8
    fig = plt.figure(figsize=(2.05 * fig_in, fig_in), facecolor="w")
    ax_real = fig.add_subplot(1, 2, 1, projection="3d")
    ax_imag = fig.add_subplot(1, 2, 2, projection="3d")

    grid = np.arange(n)
    xpos, ypos = np.meshgrid(grid + 0.25, grid + 0.25)
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = np.zeros(n * n)
    dx = np.full(n * n, 0.5)
    dy = dx.copy()

    if zlim is None:
        zmin, zmax = _city_zlim([data])
    else:
        zmin, zmax = float(zlim[0]), float(zlim[1])
    peak, sat = _color_saturation(real, imag, color_cutoff)
    if color_gamma <= 0:
        raise ValueError(f"color_gamma must be positive, got {color_gamma}")

    panels = (
        (ax_real, real.ravel(), _CITY_COLORS[0], "Real"),
        (ax_imag, imag.ravel(), _CITY_COLORS[1], "Imaginary"),
    )
    # Figure is large (about 16 to 26 inches wide), so point sizes have to
    # scale with it or the headings look small when the png is viewed.
    panel_title_size = 36 if n <= 4 else 42
    zlabel_size = 26 if n <= 4 else 30
    for ax, height, color, name in panels:
        _city_bars(
            ax, xpos, ypos, zpos, dx, dy, height, color, zmin, zmax, n, sat, color_gamma
        )
        ax.set_title(f"{name} Amplitude ({symbol})", fontsize=panel_title_size, pad=18)
        z_part = "Re" if name == "Real" else "Im"
        ax.set_zlabel(f"{z_part}({symbol})", fontsize=zlabel_size, labelpad=22)
        ax.set_xticks(np.arange(0.5, n + 0.5, 1))
        ax.set_yticks(np.arange(0.5, n + 0.5, 1))
        x_rot = 45 if n <= 4 else 90
        y_rot = -22 if n <= 4 else 0
        ax.set_xticklabels(list(labels), fontsize=font, rotation=x_rot, ha="right", va="top")
        ax.set_yticklabels(list(labels), fontsize=font, rotation=y_rot, ha="left", va="center")
        ax.set_zlim(zmin, zmax)
        ax.set_box_aspect((4, 4, 3))
        ax.tick_params(axis="z", labelsize=max(font + 4, 14), pad=6)
        ax.tick_params(axis="x", pad=0)
        ax.tick_params(axis="y", pad=0)

    heading = title if fidelity is None else f"{title}     F_proc = {fidelity:.6f}"
    fig.suptitle(heading, fontsize=32 if n <= 4 else 36)
    fig.text(
        0.5,
        0.01,
        f"color |z|^{color_gamma:g}, full dark for |z| ≥ {sat:.3g}   (tallest bar {peak:.3g})",
        ha="center",
        va="bottom",
        fontsize=16 if n <= 4 else 20,
        color="0.25",
    )
    fig.subplots_adjust(left=0.0, right=1.0, bottom=0.06, top=0.80, wspace=0.0)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)) or ".", exist_ok=True)
    fig.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out_png


def plot_qpt(
    qpt_npz: str,
    which: str = "chi",
    out_dir: str | None = None,
    *,
    color_cutoff: float | None = None,
    color_gamma: float = 0.5,
) -> list[str]:
    """Draw city plots from a saved ``*_qpt.npz`` without re-evolving the pulse."""
    which = _resolve_which(which)
    record = _load_qpt_npz(qpt_npz)
    directory = Path(out_dir) if out_dir else Path(qpt_npz).parent
    directory.mkdir(parents=True, exist_ok=True)
    stem = Path(qpt_npz).stem
    if stem.endswith("_qpt"):
        stem = stem[: -len("_qpt")]

    keys = list(WHICH_CHOICES[:-1]) if which == "all" else [which]
    paths: list[str] = []
    for key in keys:
        groups: dict[float, list[dict]] = {}
        for case in record["cases"]:
            groups.setdefault(float(case["shift_mhz"]), []).append(case)
        for shift, group in groups.items():
            matrices = [_select_matrix(key, case, record)[0] for case in group]
            # One vertical scale for every pulse at this shift (flat-top and
            # optimized). The wider of the two sets the limits.
            zlim = _city_zlim(matrices)
            for case in group:
                matrix, labels, symbol = _select_matrix(key, case, record)
                title = f"{case['title']}    {key}"
                tag = _fmt_mhz(shift)
                out_png = directory / f"{stem}_qpt_{key}_{case['pulse']}_{tag}.png"
                plot_city(
                    matrix,
                    labels,
                    title,
                    str(out_png),
                    symbol,
                    fidelity=case.get("process_fidelity"),
                    color_cutoff=color_cutoff,
                    color_gamma=color_gamma,
                    zlim=zlim,
                )
                paths.append(str(out_png))
                print(f"Saved {out_png}")
    return paths


def run_qpt(
    npz_path: str,
    *,
    with_seed: bool = True,
    shifts_mhz: list[float] | None = None,
    which: str = "chi",
    engine: str = "dynamiqs",
    target_gate: str | None = None,
    n_levels: int | None = None,
    n_sub: int | None = None,
    qubit_pair: list[int] | None = None,
    envelope: str | None = None,
    out_dir: str | None = None,
    plot: bool = True,
    color_cutoff: float | None = None,
    color_gamma: float = 0.5,
) -> dict:
    """Evolve the echoed CR pulse and save unitary, chi, and (optionally) city plots.

    Parameters
    ----------
    npz_path
        GRAPE result. The optimized half is ``cr_half_opt_I/Q``.
    with_seed
        Also propagate ``cr_half_seed_I/Q`` from that same file (the flat-top).
    shifts_mhz
        Target-frame shifts in MHz, the same list robust GRAPE stores.
        ``None`` uses ``shifts_mhz`` from the npz. Pass ``[0.0]`` for the
        calibrated frame only (before and after, no spectator detuning).
    which
        One of ``unitary``, ``unitary_diff``, ``chi``, ``chi_diff``, ``all``.
    """
    which = _resolve_which(which)
    loaded = load_grape_npz(npz_path)
    if with_seed and loaded["seed"] is None:
        raise KeyError(
            f"{npz_path} has no cr_half_seed_I/Q; set with_seed=False or pass a "
            "GRAPE npz that stored the flat-top."
        )

    meta = loaded["meta"]
    cfg = (meta or {}).get("config") or {}
    settings = {
        "engine": engine,
        "n_levels": int(n_levels if n_levels is not None else cfg.get("n_levels", 3)),
        "n_sub": int(n_sub if n_sub is not None else cfg.get("n_sub", 16)),
        "qubit_pair": list(qubit_pair if qubit_pair is not None else cfg.get("qubit_pair", [1, 2])),
        "envelope": envelope if envelope is not None else str(cfg.get("envelope", "identity")),
        "seed_amp_mhz": float(cfg.get("seed_amp_mhz", 21.0)),
        "seed_phase_rad": float(cfg.get("seed_phase_rad", 0.0)),
        "t_rise_ns": int(cfg.get("t_rise_ns", 16)),
    }
    shifts = _resolve_shifts(shifts_mhz, loaded["shifts_mhz"])
    pulses: list[tuple[str, np.ndarray]] = []
    if with_seed:
        pulses.append(("flat", loaded["seed"]))
    pulses.append(("opt", loaded["opt"]))

    exp, lab_frame = _make_experiment(settings)
    x_pi = exp.build_x_pi()
    comp_idx = list(exp.simulator.comp_idx)

    raw_cases: list[dict] = []
    for pulse_name, half in pulses:
        for shift in shifts:
            exp.simulator.set_target_frame(lab_frame + float(shift))
            timeline = exp._build_timeline_from_cr_half(half, x_pi=x_pi)
            U_full = np.asarray(exp._propagator_from_timeline(timeline))
            U_comp = U_full[np.ix_(comp_idx, comp_idx)].astype(complex)
            raw_cases.append(
                {
                    "pulse": pulse_name,
                    "shift_mhz": float(shift),
                    "U_raw": U_comp,
                    "U_full": U_full,
                }
            )
            print(
                f"evolved {pulse_name:4s}  shift {shift:+.4g} MHz  "
                f"dim {U_full.shape[0]}"
            )
    exp.simulator.set_target_frame(lab_frame)

    locked_gate = target_gate or _target_from_meta(meta)
    if locked_gate is None:
        locked_gate = _infer_target_gate(raw_cases, comp_idx)
        print(f"target_gate inferred from the optimized pulse: {locked_gate}")
    else:
        print(f"target_gate: {locked_gate}")
    U_target = zx_target_unitary(locked_gate)
    chi_target = chi_from_unitary(U_target)

    cases: list[dict] = []
    for raw in raw_cases:
        U_phased, phase = fix_global_phase(raw["U_raw"], U_target)
        metrics = gate_metrics(raw["U_full"], gate=locked_gate, comp_indices=comp_idx)
        title = _case_title(raw["pulse"], raw["shift_mhz"], shifts)
        case = {
            "pulse": raw["pulse"],
            "shift_mhz": raw["shift_mhz"],
            "title": title,
            "U_comp": U_phased,
            "chi": chi_from_unitary(U_phased),
            "global_phase_rad": phase,
            "process_fidelity": float(metrics["process_fidelity"]),
            "average_gate_fidelity": float(metrics["average_gate_fidelity"]),
            "leakage": float(metrics["leakage"]),
        }
        cases.append(case)
        print(
            f"  {title}:  F_proc={case['process_fidelity']:.6f}  "
            f"F_avg={case['average_gate_fidelity']:.6f}  "
            f"leak={case['leakage']:.3e}  "
            f"global_phase={phase:+.4f} rad"
        )

    out_directory = Path(out_dir) if out_dir else Path(loaded["path"]).parent
    out_directory.mkdir(parents=True, exist_ok=True)
    stem = Path(loaded["path"]).stem
    qpt_path = out_directory / f"{stem}_qpt.npz"
    summary_path = out_directory / f"{stem}_qpt.json"
    _save_qpt(qpt_path, cases, U_target, chi_target, locked_gate, settings, loaded["path"], shifts)
    _save_summary(summary_path, cases, locked_gate, settings, loaded["path"], shifts)
    print(f"Saved {qpt_path}")
    print(f"Saved {summary_path}")

    pngs: list[str] = []
    if plot:
        pngs = plot_qpt(
            str(qpt_path),
            which=which,
            out_dir=str(out_directory),
            color_cutoff=color_cutoff,
            color_gamma=color_gamma,
        )
    return {
        "qpt_npz": str(qpt_path),
        "summary_json": str(summary_path),
        "pngs": pngs,
        "target_gate": locked_gate,
        "cases": cases,
    }


def load_grape_npz(npz_path: str) -> dict:
    """Read the optimized half, the flat-top half, and the stored shifts."""
    path = os.path.abspath(npz_path)
    with np.load(path, allow_pickle=False) as data:
        available = set(data.files)
        missing = [k for k in ("cr_half_opt_I", "cr_half_opt_Q") if k not in available]
        if missing:
            raise KeyError(
                f"Missing {missing} in {path}. Available keys: {sorted(available)}"
            )
        opt = np.asarray(data["cr_half_opt_I"], dtype=float) + 1j * np.asarray(
            data["cr_half_opt_Q"], dtype=float
        )
        seed = None
        if "cr_half_seed_I" in available and "cr_half_seed_Q" in available:
            seed = np.asarray(data["cr_half_seed_I"], dtype=float) + 1j * np.asarray(
                data["cr_half_seed_Q"], dtype=float
            )
        shifts = None
        if "shifts_mhz" in available:
            shifts = [float(v) for v in np.asarray(data["shifts_mhz"], dtype=float).reshape(-1)]
    return {
        "path": path,
        "opt": np.asarray(opt, dtype=complex).reshape(-1),
        "seed": None if seed is None else np.asarray(seed, dtype=complex).reshape(-1),
        "shifts_mhz": shifts,
        "meta": _load_sibling_json(path),
    }


def _transform_to_pauli(data: np.ndarray, n_qubits: int) -> np.ndarray:
    """Qiskit ``_transform_to_pauli``: Choi (or superop) to the Pauli basis.

    The single-qubit change-of-basis rows are the column-stacked Paulis
    I, X, Y, Z, and the result is divided by ``2**n``.
    """
    basis = np.array(
        [[1, 0, 0, 1], [0, 1, 1, 0], [0, -1j, 1j, 0], [1, 0, 0, -1]],
        dtype=complex,
    )
    cob = basis
    for _ in range(n_qubits - 1):
        dim = int(np.sqrt(len(cob)))
        cob = np.reshape(
            np.transpose(
                np.reshape(np.kron(basis, cob), (4, dim * dim, 2, 2, dim, dim)),
                (0, 1, 2, 4, 3, 5),
            ),
            (4 * dim * dim, 4 * dim * dim),
        )
    return (cob @ data @ cob.conj().T) / 2**n_qubits


def _city_zlim(matrices: list[np.ndarray]) -> tuple[float, float]:
    """Shared vertical range. Zero stays inside, and the furthest bar wins."""
    pieces = []
    for matrix in matrices:
        data = np.asarray(matrix)
        if np.iscomplexobj(data):
            pieces.append(np.real(data).ravel())
            pieces.append(np.imag(data).ravel())
        else:
            pieces.append(np.asarray(data, dtype=float).ravel())
    vals = np.concatenate(pieces) if pieces else np.zeros(1)
    zmin = float(min(float(np.min(vals)), 0.0))
    zmax = float(max(float(np.max(vals)), 0.0))
    if zmax - zmin < 1e-9:
        zmax = zmin + 1.0
    return zmin, zmax


def _color_saturation(
    real: np.ndarray,
    imag: np.ndarray,
    cutoff: float | None,
    dominant_ratio: float = 4.0,
) -> tuple[float, float]:
    """Return ``(peak, saturation level)`` for the shared color scale.

    The saturation level is where the color reaches full darkness. By default
    that is the largest entry at least ``dominant_ratio`` below the peak, so
    the few tall process terms do not set the shade of the error bars.
    """
    mag = np.concatenate([np.abs(np.asarray(real, dtype=float)).ravel(),
                          np.abs(np.asarray(imag, dtype=float)).ravel()])
    peak = float(max(np.max(mag) if mag.size else 0.0, 1e-15))
    if cutoff is not None:
        return peak, max(float(cutoff), 1e-15)
    kept = mag[mag > 1e-8]
    errors = kept[kept < peak / dominant_ratio]
    if errors.size == 0:
        return peak, peak
    return peak, max(float(errors.max()), 1e-15)


def _magnitude_rgba(height: np.ndarray, base: str, sat: float, gamma: float) -> np.ndarray:
    """Pale tint at zero, the base hue once ``|z|`` reaches ``sat``.

    ``gamma < 1`` lifts the small bars relative to a linear ramp.
    """
    base_rgb = np.asarray(mcolors.to_rgb(base), dtype=float)
    light_rgb = 0.88 * np.ones(3) + 0.12 * base_rgb
    weight = np.clip(np.abs(np.asarray(height, dtype=float)) / sat, 0.0, 1.0) ** gamma
    rgb = light_rgb * (1.0 - weight)[:, None] + base_rgb * weight[:, None]
    alpha = np.full((rgb.shape[0], 1), 0.95)
    return np.concatenate([rgb, alpha], axis=1)


def _city_bars(
    ax, xpos, ypos, zpos, dx, dy, height, color, zmin, zmax, n, sat: float, gamma: float
) -> None:
    # Exact zeros are the complement of the process. Drawing all of them on a
    # 16x16 chi matrix hides the nonzero bars under a carpet of squares.
    height = np.asarray(height, dtype=float)
    keep = np.abs(height) > 1e-8
    if not np.any(keep):
        return
    xpos, ypos, zpos = xpos[keep], ypos[keep], zpos[keep]
    dx, dy, height = dx[keep], dy[keep], height[keep]
    rgba = _magnitude_rgba(height, color, sat, gamma)
    negative = height < 0
    positive = ~negative
    # shade=False keeps the face color equal to the magnitude scale.
    edge = (0.15, 0.15, 0.15, 0.25)
    if np.any(negative):
        ax.bar3d(
            xpos[negative],
            ypos[negative],
            zpos[negative],
            dx[negative],
            dy[negative],
            height[negative],
            color=rgba[negative],
            shade=False,
            edgecolor=edge,
            linewidth=0.15,
        )
    if zmin < 0.0 < zmax:
        verts = [[(0, 0, 0), (n, 0, 0), (n, n, 0), (0, n, 0)]]
        plane = Poly3DCollection(verts, alpha=0.12, facecolor="0.25", linewidths=0)
        ax.add_collection3d(plane)
    if np.any(positive):
        ax.bar3d(
            xpos[positive],
            ypos[positive],
            zpos[positive],
            dx[positive],
            dy[positive],
            height[positive],
            color=rgba[positive],
            shade=False,
            edgecolor=edge,
            linewidth=0.15,
        )


def _make_experiment(settings: dict):
    from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep

    kwargs = dict(
        qubit_pair=list(settings["qubit_pair"]),
        echoed_cr=True,
        n_levels=int(settings["n_levels"]),
        n_sub=int(settings["n_sub"]),
        engine=settings["engine"],
        dt_sample_ns=1.0,
        cr_pulse_params={
            "amp_mhz": settings["seed_amp_mhz"],
            "phase_rad": settings["seed_phase_rad"],
            "t_rise_ns": settings["t_rise_ns"],
        },
    )
    if settings["engine"] == "dynamiqs":
        kwargs["envelope"] = settings["envelope"]
    elif settings["envelope"] not in (None, "identity"):
        raise ValueError(
            f"envelope {settings['envelope']!r} is applied by the dynamiqs engine; "
            f"engine={settings['engine']!r} would drop it"
        )
    exp = CR_len_sweep(**kwargs)
    lab_frame = float(np.asarray(exp.simulator.qubits[1].frame_MHz).reshape(()))
    return exp, lab_frame


def _resolve_which(which: str) -> str:
    key = str(which).strip().lower()
    if key not in WHICH_CHOICES:
        raise ValueError(f"which must be one of {WHICH_CHOICES}, got {which!r}")
    return key


def _resolve_shifts(shifts_mhz: list[float] | None, stored: list[float] | None) -> list[float]:
    if shifts_mhz is None:
        if stored:
            return [float(v) for v in stored]
        return [0.0]
    shifts = [float(v) for v in shifts_mhz]
    if not shifts:
        raise ValueError("shifts_mhz must contain at least one value; use [0.0] for no detuning")
    return shifts


def _target_from_meta(meta: dict | None) -> str | None:
    if not meta:
        return None
    gate = meta.get("target_gate")
    if gate:
        return str(gate)
    cfg_gate = (meta.get("config") or {}).get("target_gate")
    if cfg_gate:
        return str(cfg_gate)
    return None


def _infer_target_gate(raw_cases: list[dict], comp_idx: list[int]) -> str:
    """Lock ZX(+pi/2) or ZX(-pi/2) from the optimized pulse closest to zero shift."""
    opt_cases = [c for c in raw_cases if c["pulse"] == "opt"] or raw_cases
    ref = min(opt_cases, key=lambda c: abs(c["shift_mhz"]))
    scored = gate_metrics(ref["U_full"], gate="best_zx", comp_indices=comp_idx)
    return str(scored["zx_gate"])


def _case_title(pulse: str, shift: float, shifts: list[float]) -> str:
    name = "flat-top" if pulse == "flat" else "optimized"
    if len(shifts) == 1 and abs(shifts[0]) < 1e-15:
        return name
    return f"{name}, shift {shift:+.4g} MHz"


def _fmt_mhz(x: float) -> str:
    return f"{float(x):.4g}".replace("-", "m").replace(".", "p").replace("+", "")


def _load_sibling_json(npz_path: str) -> dict | None:
    json_path = Path(npz_path).with_suffix(".json")
    if not json_path.is_file():
        return None
    with open(json_path, encoding="utf-8") as handle:
        meta = json.load(handle)
    if not isinstance(meta, dict):
        return None
    return meta


def _select_matrix(which: str, case: dict, record: dict):
    if which == "unitary":
        return case["U_comp"], record["comp_labels"], "U"
    if which == "unitary_diff":
        return case["U_comp"] - record["U_target"], record["comp_labels"], "U - U_ZX"
    if which == "chi":
        return case["chi"], record["pauli_labels"], "chi"
    if which == "chi_diff":
        return case["chi"] - record["chi_target"], record["pauli_labels"], "chi - chi_ZX"
    raise ValueError(f"unknown which {which!r}")


def _save_qpt(path, cases, U_target, chi_target, target_gate, settings, pulse_npz, shifts) -> None:
    np.savez(
        path,
        U_comp=np.stack([c["U_comp"] for c in cases], axis=0),
        chi=np.stack([c["chi"] for c in cases], axis=0),
        U_target=np.asarray(U_target, dtype=complex),
        chi_target=np.asarray(chi_target, dtype=complex),
        shift_mhz=np.asarray([c["shift_mhz"] for c in cases], dtype=float),
        global_phase_rad=np.asarray([c["global_phase_rad"] for c in cases], dtype=float),
        process_fidelity=np.asarray([c["process_fidelity"] for c in cases], dtype=float),
        average_gate_fidelity=np.asarray(
            [c["average_gate_fidelity"] for c in cases], dtype=float
        ),
        leakage=np.asarray([c["leakage"] for c in cases], dtype=float),
        pulse=np.asarray([c["pulse"] for c in cases]),
        title=np.asarray([c["title"] for c in cases]),
        comp_labels=np.asarray(COMP_LABELS),
        pauli_labels=np.asarray(PAULI_LABELS),
        target_gate=np.asarray(target_gate),
        engine=np.asarray(settings["engine"]),
        envelope=np.asarray(settings["envelope"]),
        n_levels=np.asarray(settings["n_levels"]),
        shifts_mhz=np.asarray(shifts, dtype=float),
        pulse_npz=np.asarray(pulse_npz),
        gauge=np.asarray("global_phase"),
    )


def _save_summary(path, cases, target_gate, settings, pulse_npz, shifts) -> None:
    payload = {
        "pulse_npz": pulse_npz,
        "target_gate": target_gate,
        "gauge": "global_phase",
        "engine": settings["engine"],
        "envelope": settings["envelope"],
        "n_levels": settings["n_levels"],
        "shifts_mhz": shifts,
        "plot_keys": list(WHICH_CHOICES),
        "cases": [
            {
                "pulse": c["pulse"],
                "shift_mhz": c["shift_mhz"],
                "title": c["title"],
                "process_fidelity": c["process_fidelity"],
                "average_gate_fidelity": c["average_gate_fidelity"],
                "leakage": c["leakage"],
                "global_phase_rad": c["global_phase_rad"],
            }
            for c in cases
        ],
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _load_qpt_npz(path: str) -> dict:
    with np.load(path, allow_pickle=False) as data:
        pulses = [str(v) for v in np.asarray(data["pulse"]).reshape(-1)]
        titles = [str(v) for v in np.asarray(data["title"]).reshape(-1)]
        shifts = np.asarray(data["shift_mhz"], dtype=float).reshape(-1)
        U_comp = np.asarray(data["U_comp"], dtype=complex)
        chi = np.asarray(data["chi"], dtype=complex)
        if "process_fidelity" in data.files:
            fidelity = np.asarray(data["process_fidelity"], dtype=float).reshape(-1)
        else:
            fidelity = np.full(pulses.__len__(), np.nan)
        n = pulses.__len__()
        if U_comp.shape[0] != n or chi.shape[0] != n or shifts.shape[0] != n:
            raise ValueError(f"inconsistent case count in {path}")
        cases = [
            {
                "pulse": pulses[i],
                "title": titles[i],
                "shift_mhz": float(shifts[i]),
                "U_comp": U_comp[i],
                "chi": chi[i],
                "process_fidelity": None if not np.isfinite(fidelity[i]) else float(fidelity[i]),
            }
            for i in range(n)
        ]
        comp_labels = (
            [str(v) for v in np.asarray(data["comp_labels"]).reshape(-1)]
            if "comp_labels" in data.files
            else list(COMP_LABELS)
        )
        pauli = (
            [str(v) for v in np.asarray(data["pauli_labels"]).reshape(-1)]
            if "pauli_labels" in data.files
            else list(PAULI_LABELS)
        )
        return {
            "cases": cases,
            "U_target": np.asarray(data["U_target"], dtype=complex),
            "chi_target": np.asarray(data["chi_target"], dtype=complex),
            "comp_labels": comp_labels,
            "pauli_labels": pauli,
        }
