"""
rabi_amp_sim.py
===============
Power-Rabi (amplitude Rabi) simulation on a single qubit of the pair using the
calibrated DRAG ``d_X180`` pulse.

The pulse SHAPE is fixed (the same GRFT-DRAG envelope the OPX plays, built by
``drag_grft_pulse_waveforms``); only its amplitude is swept, from 0 -> 1 in OPX
amp-scale units. At ``amp == amp_scale[q]["X180"]`` the qubit experiences a pi
pulse, so P(excited) traces a cosine whose first maximum sits at that calibrated
X180 amplitude.

The OPX-amp -> MHz-Rabi-rate conversion is fixed by the X180 pi-rotation
condition (same derivation as HM/Thesis/grape/calibrate_amp_to_mhz.py), so the
result is physically anchored to the lab calibration rather than an arbitrary
amplitude.

The simulator runs at 1 ns resolution to match the arbitrary-waveform samples
from ``drag_grft_pulse_waveforms`` directly, with no downsampling step.
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.optimize import curve_fit

from Configuration_Files.config_dictionaries import *
from Helper_Functions.helper_functionsv2 import drag_grft_pulse_waveforms, grft_pulse
from HM.simulator.two_qubit_simulator.base_classes.device_base import TwoQubitSimulatorBase
from HM.simulator.two_qubit_simulator.engine.pulses import Timeline

AC_AMP_FACTOR = 0.4  # config_builder.py: grft_arr_gen scales every waveform by 0.4


class RabiAmpSim(TwoQubitSimulatorBase):
    def __init__(self, qubit_pair=[1, 2], amp_list=None, **kwargs):
        # 1 ns matches drag_grft_pulse_waveforms sample resolution; no resampling needed.
        kwargs.setdefault("dt_sample_ns", 1)
        super().__init__(qubit_pair=qubit_pair, **kwargs)

        # which physical qubit to drive (defaults to the control = q_pair[0])
        self.drive_qubit = int(kwargs.get("drive_qubit", self.q_pair[0]))
        if self.drive_qubit == self.q_pair[0]:
            self.drive_channel, self.drive_idx = "q1_drive", 0
        elif self.drive_qubit == self.q_pair[1]:
            self.drive_channel, self.drive_idx = "q2_drive", 1
        else:
            raise ValueError(
                f"drive_qubit {self.drive_qubit} is not in pair {self.q_pair}")

        # d_X180 pulse definition, pulled from the lab calibration JSONs for the
        # driven qubit. These reproduce exactly what config_builder.py plays.
        q = str(self.drive_qubit)
        _default_d_x180_params = {
            "amp_scale_x180": float(amp_scale[q]["X180"]),  # OPX amp for a pi pulse
            "length_ns": int(pi_len_ns[q]),
            "rise_ns": int(pi_rise_grft_ns),
            "alpha": float(drag_dict[q]["alpha"]),
            "det": float(drag_dict[q]["det"]),
            "anharm_hz": float(anharmonicities[q]) * 1e6,  # q_anh convention (positive)
        }
        self.d_x180_params = {**_default_d_x180_params,
                              **kwargs.get("d_x180_params", {})}
        print(f"d_X180 pulse params: {self.d_x180_params}")
        # exit()

        if amp_list is None:
            amp_list = np.linspace(0.0, 1.0, 101)
        self.amp_list = np.asarray(amp_list, dtype=float)

        # OPX-amp -> MHz Rabi-rate conversion. Defaults to the value fixed by the
        # X180 pi-rotation calibration, but can be overridden via the
        # `f_rabi_per_opx1` kwarg (e.g. to detune the sim from the calibration).
        override = kwargs.get("f_rabi_per_opx1", None)
        self.f_rabi_overridden = override is not None
        self.f_rabi_per_opx1 = (
            float(override) if self.f_rabi_overridden else self._calibrate_amp_to_mhz())
        self.results = None

    # -- pulse construction --------------------------------------------------
    def _calibrate_amp_to_mhz(self):
        """MHz Rabi rate per unit OPX waveform sample.

        Fixed by the X180 pi-rotation condition: with the engine's drive term
        H = 2*pi*0.5*(eps a^dag + h.c.), a pi rotation needs
        integral(eps dt) = 0.5 (MHz*us). The X180 waveform area in OPX*ns is
        AC_AMP_FACTOR * amp_scale_x180 * sum(grft_pulse), so the scale that maps
        OPX samples to MHz is 0.5 / (area * 1e-3). Matches calibrate_amp_to_mhz.py.
        """
        p = self.d_x180_params
        a_grft = float(np.sum(grft_pulse(p["length_ns"], p["rise_ns"])))
        a_wf_x180 = AC_AMP_FACTOR * p["amp_scale_x180"] * a_grft  # OPX-amp * ns
        return 0.5 / (a_wf_x180 * 1e-3)

    def build_d_x180(self, amp):
        """Complex drive envelope (MHz) for d_X180 at OPX `amp`, one sample per ns."""
        p = self.d_x180_params
        i_wf, q_wf = drag_grft_pulse_waveforms(
            amplitude=amp, length=p["length_ns"], rise=p["rise_ns"],
            anharmonicity=p["anharm_hz"], alpha=p["alpha"], detuning=p["det"],
        )
        return (np.asarray(i_wf) + 1j * np.asarray(q_wf)) * self.f_rabi_per_opx1

    # -- measurement ops -----------------------------------------------------
    def _measure_ops(self):
        """Marginal |1> (excited) and |2> (leakage) projectors on the driven qubit."""
        I3 = qt.qeye(3)
        proj_e = qt.basis(3, 1) * qt.basis(3, 1).dag()
        proj_leak = qt.basis(3, 2) * qt.basis(3, 2).dag()
        if self.drive_idx == 0:
            return qt.tensor(proj_e, I3), qt.tensor(proj_leak, I3)
        return qt.tensor(I3, proj_e), qt.tensor(I3, proj_leak)

    # -- sweep ---------------------------------------------------------------
    def run_simulation(self, amp_list=None):
        if amp_list is not None:
            self.amp_list = np.asarray(amp_list, dtype=float)

        src = "user-set" if self.f_rabi_overridden else "X180-calibrated"
        print(f"Power Rabi on q{self.drive_qubit} via '{self.drive_channel}'")
        print(f"  sim clock           = {self.dt_sample_ns:g} ns")
        print(f"  X180 calibrated amp = {self.d_x180_params['amp_scale_x180']:.4f}")
        print(f"  f_Rabi @ OPX amp 1  = {self.f_rabi_per_opx1:.3f} MHz ({src})")

        Pe_op, Pleak_op = self._measure_ops()
        psi0 = qt.basis(self.simulator.dims, [0, 0])

        p_excited, p_leak = [], []
        for amp in tqdm(self.amp_list, desc="Amp sweep"):
            tl = Timeline(self.channels, dt_ns=self.dt_sample_ns)
            tl.add(self.drive_channel, start_ns=0.0, waveform=self.build_d_x180(amp))
            psi = self.simulator.run_shot(tl.finalize(), psi0=psi0)
            p_excited.append(float(qt.expect(Pe_op, psi)))
            p_leak.append(float(qt.expect(Pleak_op, psi)))

        self.results = {
            "amp": self.amp_list,
            "p_excited": np.asarray(p_excited),
            "p_leak": np.asarray(p_leak),
        }
        return self.results

    # -- analysis ------------------------------------------------------------
    @staticmethod
    def _rabi_model(a, offset, contrast, period, phase):
        return offset - contrast * np.cos(2 * np.pi * a / period + phase)

    def analyze_and_plot(self, results_input=None, save=True):
        results = self.results if results_input is None else results_input
        amp = results["amp"]
        pe = results["p_excited"]
        pl = results["p_leak"]
        a_x180 = self.d_x180_params["amp_scale_x180"]

        pi_amp_fit, fit_curve = None, None
        try:
            p0 = [0.5, 0.5, 2 * a_x180, 0.0]
            popt, _ = curve_fit(self._rabi_model, amp, pe, p0=p0, maxfev=10000)
            a_dense = np.linspace(amp.min(), amp.max(), 1000)
            fit_curve = (a_dense, self._rabi_model(a_dense, *popt))
            pi_amp_fit = abs(popt[2]) / 2.0
            print(f"Fitted Rabi period = {abs(popt[2]):.4f} amp-units"
                  f"  ->  pi-amp = {pi_amp_fit:.4f}")
        except Exception as exc:  # keep the plot even if the fit struggles
            print(f"Rabi cosine fit failed: {exc}")
        print(f"Expected pi-amp (X180 calibration) = {a_x180:.4f}")

        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        axes[0].plot(amp, pe, "o", ms=4, color="tab:blue", label="P(excited) sim")
        if fit_curve is not None:
            axes[0].plot(*fit_curve, color="tab:blue", lw=2, alpha=0.6, label="cosine fit")
        axes[0].axvline(a_x180, color="k", ls="--", lw=1,
                        label=f"X180 cal amp = {a_x180:.3f}")
        # if pi_amp_fit is not None:
        #     axes[0].axvline(pi_amp_fit, color="tab:red", ls=":", lw=1.2,
        #                     label=f"fit pi-amp = {pi_amp_fit:.3f}")
        axes[0].set_ylabel(f"P(|1>) on q{self.drive_qubit}")
        axes[0].set_ylim(-0.05, 1.05)
        axes[0].grid(alpha=0.3)
        axes[0].legend(loc="upper right", fontsize=8)
        axes[0].set_title(
            f"Power Rabi (d_X180) on q{self.drive_qubit}  |  pair {self.q_pair}")

        axes[1].plot(amp, pl, "s", ms=4, color="tab:orange", label="P(|2>) leakage")
        axes[1].set_xlabel("d_X180 amplitude (OPX amp-scale units)")
        axes[1].set_ylabel("leakage")
        axes[1].grid(alpha=0.3)
        axes[1].legend(loc="upper right", fontsize=8)

        plt.tight_layout()
        if save:
            out = f"rabi_amp_sim_q{self.drive_qubit}.png"
            plt.savefig(out, dpi=120)
            print(f"Saved {out}")
        plt.show()
        return pi_amp_fit

    def run(self):
        self.run_simulation()
        self.analyze_and_plot()
        return self.results


def perform_rabi_amp_sim(qubit_pair=[1, 2], amp_list=None, **kwargs):
    exp = RabiAmpSim(qubit_pair=qubit_pair, amp_list=amp_list, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    # Example: run Rabi amp sim with a fixed d_X180 pulse length of 104 ns
    exp = perform_rabi_amp_sim(
        qubit_pair=[1, 2],
        amp_list=np.linspace(0.0, 1.0, 101),
        d_x180_params={
            "length_ns": 52,
        },
        f_rabi_per_opx1=55.541
    )
    # exp = perform_rabi_amp_sim(qubit_pair=[1, 2], amp_list=np.linspace(0.0, 1.0, 101))
    # exp = perform_rabi_amp_sim(qubit_pair=[1, 2], f_rabi_per_opx1=65.0, amp_list=np.linspace(0.0, 1.0, 101))
