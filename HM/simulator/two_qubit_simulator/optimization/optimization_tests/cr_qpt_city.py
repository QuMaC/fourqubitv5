"""City plots of the echoed-CR process (unitary and chi).

Edit the knobs and run this file with the qumac-env interpreter, from ``fourqubitv5``
so that ``HM`` and ``Configuration_Files`` import.

``WHICH`` picks the picture. Every matrix is always written to ``*_qpt.npz``,
so a later run with ``REPLOT_ONLY = True`` redraws without evolving again.

``WITH_SEED`` propagates ``cr_half_seed_I/Q`` from the same npz (the flat-top)
as well as the optimized half.

``SHIFTS_MHZ = None`` uses the shifts stored in the npz (spectator branches).
``SHIFTS_MHZ = [0.0]`` stays on the calibrated frame: flat-top, then optimized.
"""

from __future__ import annotations

import os

from HM.simulator.two_qubit_simulator.optimization.cr_qpt import plot_qpt, run_qpt

# ---------------------------------------------------------------------------
# Knobs
# ---------------------------------------------------------------------------

NPZ_PATH = os.path.join(
    os.path.dirname(__file__),
    "results",
    "robust_lp350mhz",
    "cr_grape_robust_zz0p15MHz_mms_l0p3_20261003_191251.npz",
)

# Include the unoptimized half stored in the npz.
WITH_SEED = True

# None -> shifts_mhz from the npz. [0.0] -> no spectator detuning.
SHIFTS_MHZ = None

# unitary | unitary_diff | chi | chi_diff | all
WHICH = "chi"

# Color reaches full dark at this |z|. None saturates at the largest bar that
# is at least 4x below the peak, so the ZX peaks stay dark and the error bars
# use the whole shade range. color_gamma < 1 lifts the smaller bars (0.5 = sqrt).
COLOR_CUTOFF = None
COLOR_GAMMA = 0.5

ENGINE = "dynamiqs"
# None -> target_gate from the sibling json, else the better ZX on the optimized pulse.
TARGET_GATE = None

REPLOT_ONLY = False
OUT_DIR = None  # None -> next to the pulse npz


def _qpt_path(pulse_npz: str, out_dir: str | None) -> str:
    directory = out_dir or os.path.dirname(os.path.abspath(pulse_npz))
    stem = os.path.splitext(os.path.basename(pulse_npz))[0]
    return os.path.join(directory, f"{stem}_qpt.npz")


def main() -> None:
    if REPLOT_ONLY:
        saved = _qpt_path(NPZ_PATH, OUT_DIR)
        plot_qpt(
            saved,
            which=WHICH,
            out_dir=OUT_DIR,
            color_cutoff=COLOR_CUTOFF,
            color_gamma=COLOR_GAMMA,
        )
        return
    run_qpt(
        NPZ_PATH,
        with_seed=WITH_SEED,
        shifts_mhz=SHIFTS_MHZ,
        which=WHICH,
        engine=ENGINE,
        target_gate=TARGET_GATE,
        out_dir=OUT_DIR,
        plot=True,
        color_cutoff=COLOR_CUTOFF,
        color_gamma=COLOR_GAMMA,
    )


if __name__ == "__main__":
    main()
