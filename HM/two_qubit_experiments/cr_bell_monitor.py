"""
CR + Bell long-run monitor.

Each iteration:
  1) CR local-phase sweep (optional guarded write to ``cr_phase.json``)
  2) Bell-state correlations with ``precal=True`` (``ro_fidelity`` on both qubits)
  3) Append history JSON + overwrite dashboard PNG

Run from repo root::

    python -m HM.two_qubit_experiments.cr_bell_monitor --control 1 --target 4 -n 3

Or import::

    from HM.two_qubit_experiments.cr_bell_monitor import perform_cr_bell_monitor
    perform_cr_bell_monitor(1, 4, iterations=5, sleep_s=60.0)
"""
import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np

from HM.two_qubit_experiments.bell_state_correlations import perform_bell_state_correlations
from HM.two_qubit_experiments.cr_local_phase_sweep import perform_cr_local_phase_sweep
from HM.two_qubit_experiments.two_qubit_base import TwoQubitExperiment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class CRBellStateMonitor(TwoQubitExperiment):
    """
    Mega workflow per iteration:
      1) CR local-phase calibration
      2) Guarded CR-phase dictionary update
      3) Bell-state run with precalibration enabled
      4) Append metrics to JSON and overwrite dashboard PNG
    """

    def __init__(self, q_list: List[int], **kwargs):
        super().__init__(q_list=q_list, expt_name="cr_bell_monitor", **kwargs)
        self.iterations = int(kwargs.get("iterations", 5))
        self.sleep_s = float(kwargs.get("sleep_s", 0.0))
        self.save_data = bool(kwargs.get("save_data", True))
        self.save_plot = bool(kwargs.get("save_plot", True))
        self.show_plot = bool(kwargs.get("show_plot", True))
        self.stop_on_cr_update_fail = bool(kwargs.get("stop_on_cr_update_fail", True))

        self.cr_kwargs = dict(kwargs.get("cr_kwargs", {}))
        self.bell_kwargs = dict(kwargs.get("bell_kwargs", {}))
        self.bell_kwargs["precal"] = True

        self.log_json_path = str(self.path_to_save) + f"_q{self.q_control_no}_q{self.q_target_no}_history.json"
        self.dashboard_png_path = str(self.path_to_save) + f"_q{self.q_control_no}_q{self.q_target_no}_dashboard.png"

        self.results = {
            "control_q": self.q_control_no,
            "target_q": self.q_target_no,
            "cr_elem": self.cr_elem,
            "params": {
                "iterations": self.iterations,
                "sleep_s": self.sleep_s,
                "stop_on_cr_update_fail": self.stop_on_cr_update_fail,
                "cr_kwargs": self.cr_kwargs,
                "bell_kwargs": self.bell_kwargs,
            },
            "history": [],
            "artifacts": [],
        }

    def _read_current_cr_phase(self):
        phase_path = Path(self.config_files_path) / "Pulse_Calibrations" / "cr_phase.json"
        with open(phase_path, "r") as fptr:
            phase_dict = json.load(fptr)
        return float(phase_dict[self.cr_elem])

    def _append_and_save_history(self, row):
        self.results["history"].append(row)
        if self.save_data:
            self.save_json(self.results, self.log_json_path)
            if self.log_json_path not in self.results["artifacts"]:
                self.results["artifacts"].append(self.log_json_path)

    def _update_dashboard(self):
        hist = self.results["history"]
        if len(hist) == 0:
            return
        x = np.arange(1, len(hist) + 1)
        cr_phase = np.array([h.get("cr_phase", np.nan) for h in hist], dtype=float)
        bell_fid = np.array([h.get("bell_state_fidelity", np.nan) for h in hist], dtype=float)
        ro_ctrl = np.array([h.get("ro_fidelity_control", np.nan) for h in hist], dtype=float)
        ro_tgt = np.array([h.get("ro_fidelity_target", np.nan) for h in hist], dtype=float)

        fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
        axes[0].plot(x, cr_phase, "o-", label="CR phase (cycles)")
        axes[0].set_ylabel("CR phase")
        axes[0].grid(True)
        axes[0].legend(loc="best")

        axes[1].plot(x, 100.0 * bell_fid, "o-", color="purple", label="Bell state fidelity (%)")
        axes[1].set_ylabel("Bell fid (%)")
        axes[1].grid(True)
        axes[1].legend(loc="best")

        axes[2].plot(x, ro_ctrl, "o-", label=f"RO fidelity q{self.q_control_no} (%)")
        axes[2].plot(x, ro_tgt, "o-", label=f"RO fidelity q{self.q_target_no} (%)")
        axes[2].set_ylabel("RO fid (%)")
        axes[2].set_xlabel("Iteration")
        axes[2].grid(True)
        axes[2].legend(loc="best")

        fig.suptitle(f"CR/Bell monitor q{self.q_control_no}->q{self.q_target_no}")
        fig.tight_layout()

        if self.save_plot:
            fig.savefig(self.dashboard_png_path, bbox_inches="tight")
            if self.dashboard_png_path not in self.results["artifacts"]:
                self.results["artifacts"].append(self.dashboard_png_path)
        if self.show_plot:
            plt.show(block=False)
        else:
            plt.close(fig)

    def _build_row(self, iteration_idx, cr_exp, bell_exp):
        cr_summary = cr_exp.results.get("summary", {})
        cr_update = cr_summary.get("calibration_update", {})
        bell_counts = bell_exp.results.get("correlations", {}).get("counts", {})
        precal = bell_exp.results.get("precalibration", {})

        row = {
            "iteration": int(iteration_idx),
            "timestamp": self.get_timestamp_str(),
            "cr_phase": float(cr_summary.get("optimal_phase", np.nan)),
            "cr_update_fail_flag": bool(cr_update.get("update_fail_flag", False)),
            "cr_update_applied": bool(cr_update.get("applied", False)),
            "cr_update_old_phase": float(cr_update.get("old_phase", np.nan)),
            "cr_update_new_phase": float(cr_update.get("new_phase", np.nan)),
            "bell_state_fidelity": float(bell_counts.get("state_fidelity_to_ideal_00_11", np.nan)),
            "bell_coincidence_00_11": float(bell_counts.get("coincidence_00_11", np.nan)),
            "ro_fidelity_control": float(precal.get(f"q{self.q_control_no}", {}).get("fidelity_percent", np.nan)),
            "ro_fidelity_target": float(precal.get(f"q{self.q_target_no}", {}).get("fidelity_percent", np.nan)),
            "cr_summary": cr_summary,
            "bell_summary": {
                "counts": bell_counts,
                "params": bell_exp.results.get("params", {}),
            },
        }
        return row

    def run(self):
        for i in range(1, self.iterations + 1):
            logger.info("CR/Bell monitor iteration %s/%s", i, self.iterations)
            current_phase = self._read_current_cr_phase()
            cr_kwargs_local = dict(self.cr_kwargs)
            cr_kwargs_local.setdefault("update_calib", True)
            cr_kwargs_local.setdefault("save_data", self.save_data)
            cr_kwargs_local.setdefault("save_plot", self.save_plot)
            cr_kwargs_local.setdefault("show_plot", False)
            cr_kwargs_local.setdefault("plot_live", False)
            cr_kwargs_local.setdefault("query_LOs", False)
            cr_kwargs_local.setdefault("refresh_qm_config", True)
            cr_kwargs_local["initial_phase"] = current_phase

            cr_exp = perform_cr_local_phase_sweep(
                self.q_control_no,
                self.q_target_no,
                **cr_kwargs_local,
            )
            cr_update = cr_exp.results.get("summary", {}).get("calibration_update", {})
            if bool(cr_update.get("update_fail_flag", False)) and self.stop_on_cr_update_fail:
                fail_row = {
                    "iteration": int(i),
                    "timestamp": self.get_timestamp_str(),
                    "error": "cr_update_fail_flag",
                    "cr_phase": float(cr_exp.results.get("summary", {}).get("optimal_phase", np.nan)),
                    "cr_summary": cr_exp.results.get("summary", {}),
                }
                self._append_and_save_history(fail_row)
                self._update_dashboard()
                logger.warning("Stopping monitor due to CR update fail flag.")
                break

            bell_kwargs_local = dict(self.bell_kwargs)
            bell_kwargs_local.setdefault("save_data", self.save_data)
            bell_kwargs_local.setdefault("save_plot", self.save_plot)
            bell_kwargs_local.setdefault("show_plot", False)
            bell_kwargs_local.setdefault("query_LOs", False)
            bell_kwargs_local.setdefault("refresh_qm_config", True)
            bell_exp = perform_bell_state_correlations(
                self.q_control_no,
                self.q_target_no,
                **bell_kwargs_local,
            )

            row = self._build_row(i, cr_exp, bell_exp)
            self._append_and_save_history(row)
            self._update_dashboard()
            if i < self.iterations and self.sleep_s > 0:
                logger.info("Sleeping %.1fs before next iteration", self.sleep_s)
                time.sleep(self.sleep_s)

        logger.info("Monitor finished. History: %s", self.log_json_path)
        return self.results


def perform_cr_bell_monitor(control_qubit: int, target_qubit: int, **kwargs) -> CRBellStateMonitor:
    exp = CRBellStateMonitor(q_list=[control_qubit, target_qubit], **kwargs)
    exp.run()
    return exp


def main():
    parser = argparse.ArgumentParser(
        description="Run CR local-phase sweep + Bell (with precal) in a loop; log JSON and dashboard PNG.",
    )
    parser.add_argument("--control", "-c", type=int, default=1, help="Control qubit index")
    parser.add_argument("--target", "-t", type=int, default=4, help="Target qubit index")
    parser.add_argument(
        "--iterations",
        "-n",
        type=int,
        default=400,
        help="Number of monitor cycles (default: 1 for a quick test)",
    )
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between iterations")
    parser.add_argument(
        "--continue-on-cr-fail",
        action="store_true",
        help="If CR phase guard blocks file update, still run Bell and continue (default: stop that iteration)",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not open interactive plot windows (still saves PNG if --save-plot)",
    )
    parser.add_argument("--no-save-data", action="store_true", help="Skip writing history JSON")
    parser.add_argument("--no-save-plot", action="store_true", help="Skip writing dashboard PNG")
    parser.add_argument(
        "--max-phase-delta",
        type=float,
        default=0.10,
        metavar="FRAC",
        help="Max relative CR phase change vs previous cal to apply (default: 0.1 = 10%%)",
    )
    parser.add_argument(
        "--n-shots",
        type=int,
        default=25_000,
        help="Bell experiment shots per iteration",
    )
    args = parser.parse_args()

    perform_cr_bell_monitor(
        control_qubit=args.control,
        target_qubit=args.target,
        iterations=args.iterations,
        sleep_s=args.sleep,
        save_data=not args.no_save_data,
        save_plot=not args.no_save_plot,
        show_plot=not args.no_show,
        stop_on_cr_update_fail=not args.continue_on_cr_fail,
        cr_kwargs={
            "max_phase_update_fraction": args.max_phase_delta,
        },
        bell_kwargs={
            "n_shots": args.n_shots,
        },
    )


if __name__ == "__main__":
    main()
