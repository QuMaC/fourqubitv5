"""
Plot GRFT / DRAG waveform samples as built for the OPX (qubit 1).

Run from repo root:
    python HM/misc/plot_grft_q1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal.windows import gaussian

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Helper_Functions.helper_functionsv2 import (
    drag_grft_pulse_waveforms,
    grft_arr_gen,
    grft_der_arr_gen,
    grft_der_pulse,
    grft_pulse,
    rise_arr,
)

AC_AMP_FACTOR = 0.4  # config_builder.py
PI_RISE_GRFT_NS = 10  # config_dictionaries.py
CR_TAIL_NS = 16

Q_NO = "1"


def _load_json(rel: str):
    with open(REPO / rel, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    pi_len_ns = _load_json("Configuration_Files/Pulse_Calibrations/pi_len_ns.json")
    piby2_len_ns = _load_json("Configuration_Files/Pulse_Calibrations/piby2_len_ns.json")
    amp_scale = _load_json("Configuration_Files/Pulse_Calibrations/amp_scale.json")
    drag_dict = _load_json("Configuration_Files/Pulse_Calibrations/drag_dict.json")
    anharmonicities = _load_json("Configuration_Files/System_Parameters/anharmonicities.json")

    T_pi = int(pi_len_ns[Q_NO])
    T_piby2 = int(piby2_len_ns[Q_NO])
    pi_rise = PI_RISE_GRFT_NS
    a_x180 = float(amp_scale[Q_NO]["X180"])
    a_x90 = float(amp_scale[Q_NO]["X90"])
    alpha = float(drag_dict[Q_NO]["alpha"])
    # det = float(drag_dict[Q_NO]["det"])
    det = 0
    anharm_hz = float(anharmonicities[Q_NO]) * 1e6

    t_pi = np.arange(T_pi)
    t_piby2 = np.arange(T_piby2)

    shape = grft_pulse(T_pi, pi_rise)
    wf_unit = grft_arr_gen((T_pi, pi_rise), [1.0])
    wf_x180 = grft_arr_gen((T_pi, pi_rise), [a_x180])
    wf_x90 = grft_arr_gen((T_piby2, pi_rise), [a_x90])

    der_shape = grft_der_pulse(T_pi, pi_rise)
    der_x180 = grft_der_arr_gen((T_pi, pi_rise), [a_x180])

    risefall_window = np.array(gaussian(2 * pi_rise, 2 * pi_rise // 6), dtype=float)

    I_drag, Q_drag = drag_grft_pulse_waveforms(
        amplitude=a_x180,
        length=T_pi,
        rise=pi_rise,
        anharmonicity=anharm_hz,
        alpha=alpha,
        detuning=det,
    )
    I_drag = np.asarray(I_drag, dtype=float)
    Q_drag = np.asarray(Q_drag, dtype=float)

    cr_rise = np.asarray(rise_arr(CR_TAIL_NS), dtype=float)

    print(f"Q{Q_NO} pi_len_ns = {T_pi}, piby2_len_ns = {T_piby2}, pi_rise_grft_ns = {pi_rise}")
    print(f"amp_scale X180 = {a_x180:.6f}, X90 = {a_x90:.6f}")
    print(f"drag alpha = {alpha:.4f}, anharmonicity = {anharmonicities[Q_NO]} MHz -> {anharm_hz:.3e} Hz")
    print(f"grft_pulse: peak={shape.max():.4f}, sum={shape.sum():.4f} (ns)")
    print(f"grft_arr_gen X180: peak={np.real(wf_x180).max():.4f}, sum={np.real(wf_x180).sum():.4f}")
    print(f"d_X180 |z|: peak={np.hypot(I_drag, Q_drag).max():.4f}")

    fig, axes = plt.subplots(4, 1, figsize=(10, 11), sharex=False)

    ax = axes[0]
    ax.plot(np.arange(len(risefall_window)), risefall_window, "k--", alpha=0.5, label="scipy gaussian(20, σ=10//6)")
    ax.plot(t_pi, shape, "C0-o", ms=3, label="grft_pulse (unitless)")
    ax.axvline(pi_rise - 0.5, color="gray", ls=":", lw=1)
    ax.axvline(T_pi - pi_rise - 0.5, color="gray", ls=":", lw=1)
    ax.set_ylabel("amplitude")
    ax.set_title(f"Q{Q_NO}: normalized GRFT shape (rise={pi_rise} ns, flat={T_pi - 2 * pi_rise} ns)")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(t_pi, np.real(wf_unit), "C1-", label=f"grft_arr_gen(scale=1) = {AC_AMP_FACTOR}×shape")
    ax.plot(t_pi, np.real(wf_x180), "C2-", label=f"grft_arr_gen(scale=X180={a_x180:.4f})")
    ax.plot(t_piby2, np.real(wf_x90), "C3--", alpha=0.8, label=f"grft_arr_gen(scale=X90={a_x90:.4f})")
    ax.set_ylabel("OPX sample")
    ax.set_title("Samples sent to OPX (I channel, non-DRAG pulses)")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)

    ax = axes[2]
    ax.plot(t_pi, I_drag, "C0-", label="I (d_X180)")
    ax.plot(t_pi, Q_drag, "C1-", label="Q (DRAG)")
    ax.plot(t_pi, np.hypot(I_drag, Q_drag), "k:", alpha=0.7, label="|I+jQ|")
    ax.set_ylabel("OPX sample")
    ax.set_title("DRAG pulse drag_grft_pulse_waveforms (hardware play: d_X180)")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)

    ax = axes[3]
    ax.plot(t_pi, der_shape, "C4-", alpha=0.7, label="grft_der_pulse (unitless)")
    ax.plot(t_pi, np.real(der_x180), "C5-", label="grft_der_arr_gen(X180 scale)")
    ax.set_xlabel("time (ns), 1 sample = 1 ns")
    ax.set_ylabel("derivative scale")
    ax.set_title("DRAG derivative envelope")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)

    fig.tight_layout()

    fig2, ax2 = plt.subplots(figsize=(8, 3))
    ax2.plot(np.arange(len(cr_rise)), cr_rise, "C6-o", ms=4)
    ax2.set_xlabel("time (ns)")
    ax2.set_ylabel("OPX sample")
    ax2.set_title(f"CR rise_wf only (rise_arr, cr_tail_ns={CR_TAIL_NS}) — not the full π pulse")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()

    out = REPO / "HM" / "misc" / f"grft_samples_q{Q_NO}.png"
    out_cr = REPO / "HM" / "misc" / f"cr_rise_q{Q_NO}.png"
    fig.savefig(out, dpi=150)
    fig2.savefig(out_cr, dpi=150)
    print(f"Saved {out}")
    print(f"Saved {out_cr}")
    plt.show()


if __name__ == "__main__":
    main()
