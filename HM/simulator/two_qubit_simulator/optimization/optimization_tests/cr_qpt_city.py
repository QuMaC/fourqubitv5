"""City plots of the echoed-CR flat-top (unitary and chi).

Edit the knobs and run this file with the qumac-env interpreter, from ``fourqubitv5``
so that ``HM`` and ``Configuration_Files`` import.

The pulse is the calibrated flat-top from the robust-GRAPE knobs
(``CR_PULSE_PARAMS`` in ``cr_grape_robust_test.py``), not a saved optimization.

``WHICH`` picks the picture. Each matrix kind is one GIF, frames ordered from
the most negative target-frame shift to the most positive. Every matrix is
always written to ``*_qpt.npz``, so a later run with ``REPLOT_ONLY = True``
redraws without evolving again.
"""

from __future__ import annotations

import os

import numpy as np

from HM.simulator.two_qubit_simulator.optimization.cr_qpt import (
    calibrated_flat_half,
    plot_qpt,
    run_qpt,
)

# ---------------------------------------------------------------------------
# Knobs. Same flat-top as cr_grape_robust_test.py with USE_SEED_NPZ = False.
# ---------------------------------------------------------------------------

AMP_MHZ = 21.0
PHASE_RAD = 0.0
T_RISE_NS = 16
FLAT_LEN_NS = 122.0
N_FLAT_KNOBS = 61
N_LINK_SAMPLES = 1
ENVELOPE = "butterworth4_350mhz"
N_LEVELS = 4
N_SUB = 16
QUBIT_PAIR = [1, 2]
TARGET_GATE = "zx_m90"
STEM = "flat_amp21_len122"

# Target-frame detuning in MHz. 0 is the calibrated frame.
# -300 kHz to +300 kHz in steps of 25 kHz (0.025 MHz).
DETUNE_STEP_MHZ = 0.025
DETUNE_MIN_MHZ = -0.3
DETUNE_MAX_MHZ = 0.3
_N_SHIFTS = int(round((DETUNE_MAX_MHZ - DETUNE_MIN_MHZ) / DETUNE_STEP_MHZ)) + 1
SHIFTS_MHZ = np.linspace(DETUNE_MIN_MHZ, DETUNE_MAX_MHZ, _N_SHIFTS).round(6).tolist()

# How long each detuning stays on screen.
GIF_FRAME_MS = 500

# unitary (4x4) and chi (16x16), plus each minus the ideal ZX.
WHICH = "all"

# One vertical scale for the whole detuning series, set by the tallest bar.
SHARE_Z_ACROSS_SHIFTS = True

# Color reaches full dark at this |z|. None saturates at the largest bar that
# is at least 4x below the peak, so the ZX peaks stay dark and the error bars
# use the whole shade range. color_gamma < 1 lifts the smaller bars (0.5 = sqrt).
COLOR_CUTOFF = None
COLOR_GAMMA = 0.5

ENGINE = "dynamiqs"

REPLOT_ONLY = False
OUT_DIR = os.path.join(os.path.dirname(__file__), "results", "flat_detune_city")


def _qpt_path() -> str:
    return os.path.join(OUT_DIR, f"{STEM}_qpt.npz")


def main() -> None:
    if REPLOT_ONLY:
        plot_qpt(
            _qpt_path(),
            which=WHICH,
            out_dir=OUT_DIR,
            color_cutoff=COLOR_CUTOFF,
            color_gamma=COLOR_GAMMA,
            share_z_across_shifts=SHARE_Z_ACROSS_SHIFTS,
            frame_ms=GIF_FRAME_MS,
        )
        return
    half = calibrated_flat_half(
        amp_mhz=AMP_MHZ,
        phase_rad=PHASE_RAD,
        t_rise_ns=T_RISE_NS,
        flat_len_ns=FLAT_LEN_NS,
        n_flat_knobs=N_FLAT_KNOBS,
        n_link_samples=N_LINK_SAMPLES,
    )
    run_qpt(
        flat_half=half,
        stem=STEM,
        with_seed=True,
        with_opt=False,
        shifts_mhz=SHIFTS_MHZ,
        which=WHICH,
        engine=ENGINE,
        target_gate=TARGET_GATE,
        n_levels=N_LEVELS,
        n_sub=N_SUB,
        qubit_pair=QUBIT_PAIR,
        envelope=ENVELOPE,
        seed_amp_mhz=AMP_MHZ,
        seed_phase_rad=PHASE_RAD,
        t_rise_ns=T_RISE_NS,
        out_dir=OUT_DIR,
        plot=True,
        color_cutoff=COLOR_CUTOFF,
        color_gamma=COLOR_GAMMA,
        share_z_across_shifts=SHARE_Z_ACROSS_SHIFTS,
        frame_ms=GIF_FRAME_MS,
    )


if __name__ == "__main__":
    main()
