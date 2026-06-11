"""
cr_phase_sweep.py
=================
Sweep the relative phase of the CR drive and, at each phase, run the full
CR length sweep from ``cr_len_sweep.py``. The phase enters as a complex
amplitude on the CR envelope (``amp_mhz * exp(i*phase)``), which rotates the
in-plane interaction components (ZX, ZY) and (IX, IY) by the same angle while
leaving ZZ / IZ untouched.

Outputs
-------
1. avg-X plot:    duration-averaged <X> on the target vs phase, separately for
                  control |0> and |1>, with the lowest-avg-X phase marked.
2. trace overlay: XYZ traces vs duration, one line per phase (colormap).
3. heatmaps:      duration x phase maps of <X>, <Y>, <Z> per control state.
4. JSON dump of the full phase x length dataset for later analysis.
"""

import json

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from HM.simulator.two_qubit_simulator.experiments.cr_len_sweep import CR_len_sweep

PI_TICKS = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
PI_TICK_LABELS = ["0", r"$\pi/2$", r"$\pi$", r"$3\pi/2$", r"$2\pi$"]


class CR_phase_sweep:
    def __init__(self, qubit_pair=[1, 2], phase_list=None, len_list=None, **kwargs):
        if phase_list is None:
            phase_list = np.linspace(0.0, 2 * np.pi, 13)
        self.phase_list = np.asarray(phase_list, dtype=float)

        if len_list is None:
            len_list = np.arange(0, 2000, 50)
        self.len_list = np.asarray(len_list, dtype=float)

        self.avg_x_plot_filename = kwargs.pop("avg_x_plot_filename", "cr_phase_sweep_avg_x_16ns.png")
        self.traces_plot_filename = kwargs.pop("traces_plot_filename", "cr_phase_sweep_traces_16ns.png")
        self.heatmap_plot_filename = kwargs.pop("heatmap_plot_filename", "cr_phase_sweep_heatmap_16ns.png")
        self.trace_filename = kwargs.pop("trace_filename", "cr_phase_sweep_trace_16ns.json")

        # one CR_len_sweep instance reused for every phase point
        self.exp = CR_len_sweep(qubit_pair=qubit_pair, len_list=self.len_list, **kwargs)
        self.results = None

    # -- sweep ----------------------------------------------------------------
    def run_simulation(self):
        per_phase = []
        for i, phase in enumerate(self.phase_list):
            print(f"\n=== Phase {i + 1}/{len(self.phase_list)}: {phase:.4f} rad ===")
            res = self.exp.run_simulation(len_list=self.len_list, phase_rad=float(phase))
            per_phase.append({
                "phase_rad": float(phase),
                0: {c: np.asarray(res[0][c], dtype=float) for c in "XYZ"},
                1: {c: np.asarray(res[1][c], dtype=float) for c in "XYZ"},
                "R_mag": np.asarray(res["R_mag"], dtype=float),
            })

        self.results = {
            "phase_list": self.phase_list,
            "total_durations": np.asarray(self.exp.results["total_durations"], dtype=float),
            "per_phase": per_phase,
        }
        return self.results

    # -- analysis ---------------------------------------------------------------
    def _avg_x_vs_phase(self):
        """Duration-averaged <X> per control state, one value per phase."""
        avg_x = {0: [], 1: []}
        for entry in self.results["per_phase"]:
            for ctrl in [0, 1]:
                avg_x[ctrl].append(float(np.mean(entry[ctrl]["X"])))
        return {ctrl: np.asarray(v) for ctrl, v in avg_x.items()}

    def analyze_and_plot(self):
        phases = self.results["phase_list"]
        durations = self.results["total_durations"]
        per_phase = self.results["per_phase"]

        avg_x = self._avg_x_vs_phase()
        min_info = {}
        for ctrl in [0, 1]:
            idx = int(np.argmin(avg_x[ctrl]))
            min_info[ctrl] = {
                "index": idx,
                "phase_rad": float(phases[idx]),
                "avg_x": float(avg_x[ctrl][idx]),
            }
            print(f"Control {ctrl}: lowest avg <X> = {min_info[ctrl]['avg_x']:.6f} "
                  f"at phase = {min_info[ctrl]['phase_rad']:.4f} rad "
                  f"({np.degrees(min_info[ctrl]['phase_rad']):.1f} deg)")
        self.min_info = min_info

        # ---- plot 1: avg <X> vs phase -------------------------------------
        fig1, ax = plt.subplots(figsize=(8, 5))
        colors = {0: "tab:blue", 1: "tab:red"}
        for ctrl in [0, 1]:
            ax.plot(phases, avg_x[ctrl], "o-", color=colors[ctrl],
                    label=f"Control {ctrl}")
            ax.plot(min_info[ctrl]["phase_rad"], min_info[ctrl]["avg_x"], "*",
                    color=colors[ctrl], ms=16,
                    label=f"min ctrl {ctrl}: {min_info[ctrl]['avg_x']:.4f} "
                          f"@ {min_info[ctrl]['phase_rad']:.3f} rad")
            ax.axvline(min_info[ctrl]["phase_rad"], color=colors[ctrl],
                       ls="--", lw=1.0, alpha=0.5)
        ax.set_xlabel("CR drive phase (rad)")
        ax.set_ylabel("duration-averaged <X> target")
        ax.set_xticks(PI_TICKS)
        ax.set_xticklabels(PI_TICK_LABELS)
        ax.grid(alpha=0.4)
        ax.legend(fontsize=8)
        ax.set_title(f"Avg <X> vs CR phase  |  CR_amp = {self.exp.cr_pulse_params['amp_mhz']} MHz"
                     f"  |  echoed = {self.exp.echoed_cr}")
        fig1.tight_layout()
        fig1.savefig(self.avg_x_plot_filename, dpi=160)
        print(f"Saved {self.avg_x_plot_filename}")

        # ---- plot 2: XYZ + |R| traces colored by phase ----------------------
        cmap = plt.get_cmap("viridis")
        norm = Normalize(vmin=phases.min(), vmax=phases.max())
        fig2, axes2 = plt.subplots(4, 2, figsize=(11, 10), sharex=True)
        for col, ctrl in enumerate([0, 1]):
            for row, comp in enumerate(["X", "Y", "Z"]):
                ax = axes2[row, col]
                for entry in per_phase:
                    ax.plot(durations, entry[ctrl][comp],
                            color=cmap(norm(entry["phase_rad"])), lw=1.2, alpha=0.85)
                ax.set_ylim(-1.1, 1.1)
                ax.axhline(0, color="k", lw=0.5, alpha=0.3)
                ax.grid(alpha=0.3)
                if col == 0:
                    ax.set_ylabel(f"<{comp}> target")
                if row == 0:
                    ax.set_title(f"Control |{ctrl}>")
        # |R| is a joint (pair) quantity; shown in both columns for alignment.
        for col in [0, 1]:
            ax = axes2[3, col]
            for entry in per_phase:
                ax.plot(durations, entry["R_mag"],
                        color=cmap(norm(entry["phase_rad"])), lw=1.2, alpha=0.85)
            ax.set_ylim(0.0, 2.0)
            ax.grid(alpha=0.3)
            ax.set_xlabel("Total CR pulse duration (ns)")
            if col == 0:
                ax.set_ylabel("|R|")
        cbar = fig2.colorbar(ScalarMappable(norm=norm, cmap=cmap),
                             ax=axes2, fraction=0.025, pad=0.02)
        cbar.set_label("CR drive phase (rad)")
        cbar.set_ticks(PI_TICKS)
        cbar.set_ticklabels(PI_TICK_LABELS)
        fig2.suptitle("Target Bloch components and |R| vs duration, colored by CR phase")
        fig2.savefig(self.traces_plot_filename, dpi=160)
        print(f"Saved {self.traces_plot_filename}")

        # ---- plot 3: heatmaps (duration x phase), incl. |R| -----------------
        fig3, axes3 = plt.subplots(4, 2, figsize=(11, 10), sharex=True, sharey=True)
        for col, ctrl in enumerate([0, 1]):
            for row, comp in enumerate(["X", "Y", "Z"]):
                ax = axes3[row, col]
                grid = np.array([entry[ctrl][comp] for entry in per_phase])
                mesh = ax.pcolormesh(durations, phases, grid,
                                     cmap="RdBu_r", vmin=-1.0, vmax=1.0,
                                     shading="nearest")
                if col == 0:
                    ax.set_ylabel(f"<{comp}>\nphase (rad)")
                    ax.set_yticks(PI_TICKS)
                    ax.set_yticklabels(PI_TICK_LABELS)
                if row == 0:
                    ax.set_title(f"Control |{ctrl}>")
        # |R| row: joint quantity, own 0..2 color scale, duplicated for alignment.
        r_grid = np.array([entry["R_mag"] for entry in per_phase])
        for col in [0, 1]:
            ax = axes3[3, col]
            mesh_r = ax.pcolormesh(durations, phases, r_grid,
                                   cmap="viridis", vmin=0.0, vmax=2.0,
                                   shading="nearest")
            ax.set_xlabel("Total CR pulse duration (ns)")
            if col == 0:
                ax.set_ylabel("|R|\nphase (rad)")
                ax.set_yticks(PI_TICKS)
                ax.set_yticklabels(PI_TICK_LABELS)
        cbar = fig3.colorbar(mesh, ax=axes3[:3, :], fraction=0.025, pad=0.02)
        cbar.set_label("expectation value")
        cbar_r = fig3.colorbar(mesh_r, ax=axes3[3, :], fraction=0.08, pad=0.02)
        cbar_r.set_label("|R|")
        fig3.suptitle("Target Bloch components and |R|: duration x CR phase")
        fig3.savefig(self.heatmap_plot_filename, dpi=160)
        print(f"Saved {self.heatmap_plot_filename}")

        # ---- JSON export ----------------------------------------------------
        trace = {
            "metadata": {
                "q_pair": self.exp.q_pair,
                "echoed_cr": self.exp.echoed_cr,
                "echo_qubit": self.exp.echo_qubit,
                "dt_sample_ns": self.exp.dt_sample_ns,
                "n_sub": self.exp.simulator.n_sub,
                "cr_pulse_params": self.exp.cr_pulse_params,
                "x_pi_pulse_params": self.exp.x_pi_pulse_params,
                "f_rabi_per_opx1": self.exp.f_rabi_per_opx1,
                "avg_x_minimum": min_info,
            },
            "phase_list_rad": phases,
            "total_durations_ns": durations,
            "avg_x_vs_phase": {
                "control_0": avg_x[0],
                "control_1": avg_x[1],
            },
            "per_phase": [
                {
                    "phase_rad": entry["phase_rad"],
                    "control_0": {c: entry[0][c] for c in "XYZ"},
                    "control_1": {c: entry[1][c] for c in "XYZ"},
                    "R_mag": entry["R_mag"],
                }
                for entry in per_phase
            ],
        }
        with open(self.trace_filename, "w") as f:
            json.dump(CR_len_sweep._to_jsonable(trace), f, indent=2)
        print(f"Saved {self.trace_filename}")

        plt.show()
        return min_info

    def run(self):
        self.run_simulation()
        self.analyze_and_plot()
        return self.results


def perform_cr_phase_sweep(q_pair=[1, 2], phase_list=None, len_list=None, **kwargs):
    exp = CR_phase_sweep(qubit_pair=q_pair, phase_list=phase_list,
                         len_list=len_list, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    cr_pulse_params = {
        "amp_mhz": 32.0,
        "t_rise_ns": 16,
        "sigma_ns": 5,
        "t_flat_ns": None,
    }
    exp = perform_cr_phase_sweep(
        q_pair=[1, 2],
        phase_list=np.linspace(0.0, 2 * np.pi, 30),
        len_list=np.arange(0, 1000, 5),
        cr_pulse_params=cr_pulse_params,
        echoed_cr=True,
        parallel=True,
        max_workers=8,
        n_sub=2,
    )
