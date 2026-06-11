"""
cr_fixed_len_phase_sweep.py
===========================
Sweep the relative phase of the CR drive at a FIXED pulse length and measure
the target's <X>, <Y>, <Z> (for control |0> and |1>) plus |R| at each phase.

This is the cheap, single-duration cut through the full phase x length sweep
(``cr_phase_len_sweep.py``): one timeline per phase instead of a whole length
sweep, so a fine phase grid runs in seconds-to-minutes.

The fixed length is the flat-top duration of each CR half (``t_flat_ns``);
it defaults to the calibrated value for the pair from cr_len_ns.json.
"""

import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
from tqdm import tqdm

from Configuration_Files.config_dictionaries import cr_len_ns
from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep

# major ticks every pi/4, labeled; minor grid every pi/12
PI_TICKS = [k * np.pi / 4 for k in range(9)]
PI_TICK_LABELS = ["0", r"$\pi/4$", r"$\pi/2$", r"$3\pi/4$", r"$\pi$",
                  r"$5\pi/4$", r"$3\pi/2$", r"$7\pi/4$", r"$2\pi$"]
PI_MINOR_TICKS = [k * np.pi / 12 for k in range(25)]


class CR_fixed_len_phase_sweep:
    def __init__(self, qubit_pair=[1, 2], phase_list=None, flat_len_ns=None, **kwargs):
        if phase_list is None:
            phase_list = np.linspace(0.0, 2 * np.pi, 73)  # 5 deg steps
        self.phase_list = np.asarray(phase_list, dtype=float)

        self.plot_filename = kwargs.pop("plot_filename", "cr_fixed_len_phase_sweep.png")
        self.trace_filename = kwargs.pop("trace_filename", "cr_fixed_len_phase_sweep.json")

        # CR_len_sweep provides the calibrated pulse construction, simulator
        # and parallel settings; we drive it one timeline at a time.
        self.exp = CR_len_sweep(qubit_pair=qubit_pair, len_list=[0.0], **kwargs)

        if flat_len_ns is None:
            key = f"cr_c{qubit_pair[0]}t{qubit_pair[1]}"
            flat_len_ns = float(cr_len_ns[key])
            print(f"flat_len_ns not given, using calibrated {key} = {flat_len_ns} ns")
        self.flat_len_ns = float(flat_len_ns)
        self.results = None

    # -- sweep ----------------------------------------------------------------
    def run_simulation(self):
        sim = self.exp.simulator
        n0, _ = sim.dims
        I0 = qt.qeye(n0)
        sx_2 = qt.Qobj(np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex))
        sy_2 = qt.Qobj(np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex))
        sz_2 = qt.Qobj(np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex))
        X_op = qt.tensor(I0, sx_2)
        Y_op = qt.tensor(I0, sy_2)
        Z_op = qt.tensor(I0, sz_2)
        psi00 = qt.basis(sim.dims, [0, 0])
        psi10 = qt.basis(sim.dims, [1, 0])

        print(f"Fixed CR flat-top length: {self.flat_len_ns} ns per half"
              f"  |  echoed = {self.exp.echoed_cr}")
        print(f"Phase sweep: {len(self.phase_list)} points,"
              f" {self.phase_list[0]:.3f} -> {self.phase_list[-1]:.3f} rad")

        # Timelines are built serially (cheap) because _build_timeline reads
        # the shared cr_pulse_params dict; only the shots run in parallel.
        x_pi = self.exp.build_x_pi() if self.exp.echoed_cr else None
        timelines = []
        for phase in self.phase_list:
            self.exp.cr_pulse_params["phase_rad"] = float(phase)
            timelines.append(self.exp._build_timeline(self.flat_len_ns, x_pi=x_pi))

        def simulate_phase(timeline):
            point = {}
            for ctrl_state, psi0 in [(0, psi00), (1, psi10)]:
                psi = sim.run_shot(timeline, psi0=psi0)
                point[ctrl_state] = {
                    "X": float(qt.expect(X_op, psi)),
                    "Y": float(qt.expect(Y_op, psi)),
                    "Z": float(qt.expect(Z_op, psi)),
                }
            return point

        if self.exp.parallel:
            max_workers = self.exp.max_workers
            if max_workers is None:
                import os
                max_workers = min(len(self.phase_list), os.cpu_count() or 1)
            max_workers = max(1, int(max_workers))
            print(f"Running phase sweep in parallel with {max_workers} workers")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                points = list(tqdm(executor.map(simulate_phase, timelines),
                                   total=len(timelines), desc="Phase Sweep"))
        else:
            points = [simulate_phase(tl) for tl in tqdm(timelines, desc="Phase Sweep")]

        self.results = {
            0: {c: np.array([p[0][c] for p in points]) for c in "XYZ"},
            1: {c: np.array([p[1][c] for p in points]) for c in "XYZ"},
        }
        self.results["R_mag"] = np.sqrt(
            (self.results[0]["X"] + self.results[1]["X"]) ** 2 +
            (self.results[0]["Y"] + self.results[1]["Y"]) ** 2 +
            (self.results[0]["Z"] + self.results[1]["Z"]) ** 2
        )
        return self.results

    @staticmethod
    def _find_crossings(phases, y0, y1):
        """Phases where the two curves cross, by linear interpolation between
        adjacent sweep points. Returns list of (phase, value) tuples."""
        diff = np.asarray(y0) - np.asarray(y1)
        crossings = []
        for i in range(len(diff) - 1):
            if diff[i] == 0.0:
                crossings.append((float(phases[i]), float(y0[i])))
            elif diff[i] * diff[i + 1] < 0:
                frac = diff[i] / (diff[i] - diff[i + 1])
                phi_c = phases[i] + frac * (phases[i + 1] - phases[i])
                val_c = y0[i] + frac * (y0[i + 1] - y0[i])
                crossings.append((float(phi_c), float(val_c)))
        if diff[-1] == 0.0:
            crossings.append((float(phases[-1]), float(y0[-1])))
        return crossings

    # -- plot -------------------------------------------------------------------
    def analyze_and_plot(self):
        phases = self.phase_list
        results = self.results
        r_mag = results["R_mag"]

        idx_min = int(np.argmin(r_mag))
        print(f"Minimum |R| = {r_mag[idx_min]:.6f} at phase = {phases[idx_min]:.4f} rad "
              f"({np.degrees(phases[idx_min]):.1f} deg)")

        x_crossings = self._find_crossings(phases, results[0]["X"], results[1]["X"])
        self.x_crossings = x_crossings
        if x_crossings:
            for phi_c, val_c in x_crossings:
                print(f"<X> ctrl0/ctrl1 overlap at phase = {phi_c:.4f} rad "
                      f"({np.degrees(phi_c):.1f} deg), <X> = {val_c:.4f}")
        else:
            print("No <X> ctrl0/ctrl1 crossings found in the swept phase range")

        fig, axes = plt.subplots(4, 1, figsize=(8, 9), sharex=True)
        colors = {0: "tab:blue", 1: "tab:red"}
        for ax, comp in zip(axes[:3], ["X", "Y", "Z"]):
            for ctrl in [0, 1]:
                ax.plot(phases, results[ctrl][comp], "o-", ms=4,
                        color=colors[ctrl], label=f"Control {ctrl}")
            ax.set_ylabel(f"<{comp}> target")
            ax.set_ylim(-1.1, 1.1)
            ax.axhline(0, color="k", lw=0.5, alpha=0.3)
            ax.grid(alpha=0.4)
            ax.grid(which="minor", alpha=0.15, linestyle=":")
        # highlight <X> overlap points on the X panel + vlines on all panels
        for k, (phi_c, val_c) in enumerate(x_crossings):
            axes[0].plot(phi_c, val_c, "*", color="k", ms=14, zorder=5,
                         label=f"<X> overlap @ {phi_c:.3f} rad" if k == 0 else None)
            for ax in axes:
                ax.axvline(phi_c, color="k", ls=":", lw=0.9, alpha=0.5)
        axes[0].legend(loc="upper right", fontsize=8)

        axes[3].plot(phases, r_mag, "o-", ms=4, color="tab:green", label="|R|")
        axes[3].plot(phases[idx_min], r_mag[idx_min], "o", color="tab:purple", ms=7,
                     label=f"min |R| = {r_mag[idx_min]:.4f} @ {phases[idx_min]:.3f} rad")
        axes[3].set_ylabel("|R|")
        axes[3].set_ylim(0.0, 2.0)
        axes[3].grid(alpha=0.4)
        axes[3].grid(which="minor", alpha=0.15, linestyle=":")
        axes[3].legend(loc="upper right", fontsize=8)
        axes[3].set_xlabel("CR drive phase (rad)")
        axes[3].set_xticks(PI_TICKS)
        axes[3].set_xticklabels(PI_TICK_LABELS)
        axes[3].set_xticks(PI_MINOR_TICKS, minor=True)

        axes[0].set_title(
            f"Phase sweep at fixed CR flat-top = {self.flat_len_ns:.0f} ns"
            f"  |  CR_amp = {self.exp.cr_pulse_params['amp_mhz']} MHz"
            f"  |  echoed = {self.exp.echoed_cr}")
        plt.tight_layout()
        plt.savefig(self.plot_filename, dpi=160)
        print(f"Saved {self.plot_filename}")

        trace = {
            "metadata": {
                "q_pair": self.exp.q_pair,
                "echoed_cr": self.exp.echoed_cr,
                "echo_qubit": self.exp.echo_qubit,
                "dt_sample_ns": self.exp.dt_sample_ns,
                "n_sub": self.exp.simulator.n_sub,
                "flat_len_ns": self.flat_len_ns,
                "cr_pulse_params": self.exp.cr_pulse_params,
                "x_pi_pulse_params": self.exp.x_pi_pulse_params,
                "f_rabi_per_opx1": self.exp.f_rabi_per_opx1,
                "min_r_mag": {
                    "index": idx_min,
                    "phase_rad": float(phases[idx_min]),
                    "r_mag": float(r_mag[idx_min]),
                },
                "x_overlap_points": [
                    {"phase_rad": phi_c, "x_value": val_c}
                    for phi_c, val_c in x_crossings
                ],
            },
            "phase_list_rad": phases,
            "control_0": {c: results[0][c] for c in "XYZ"},
            "control_1": {c: results[1][c] for c in "XYZ"},
            "R_mag": r_mag,
        }
        with open(self.trace_filename, "w") as f:
            json.dump(CR_len_sweep._to_jsonable(trace), f, indent=2)
        print(f"Saved {self.trace_filename}")

        plt.show()
        return self.results

    def run(self):
        self.run_simulation()
        self.analyze_and_plot()
        return self.results


def perform_cr_fixed_len_phase_sweep(q_pair=[1, 2], phase_list=None,
                                     flat_len_ns=None, **kwargs):
    exp = CR_fixed_len_phase_sweep(qubit_pair=q_pair, phase_list=phase_list,
                                   flat_len_ns=flat_len_ns, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    cr_pulse_params = {
        "amp_mhz": 32.0,
        "t_rise_ns": 16,
        "sigma_ns": 5,
        "t_flat_ns": None,
    }
    exp = perform_cr_fixed_len_phase_sweep(
        q_pair=[1, 2],
        phase_list=np.linspace(0.0, np.pi, 20),
        flat_len_ns=170,  # None -> calibrated cr_len_ns.json value for the pair
        cr_pulse_params=cr_pulse_params,
        echoed_cr=True,
        parallel=True,
        max_workers=8,
        n_sub=2,
    )
