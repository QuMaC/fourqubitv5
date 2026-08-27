import logging
import time
from pathlib import Path

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
from termcolor import cprint

from HM.single_qubit_experiments.ro_fidelity import validate_ro_point_with_ro_fidelity
from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class RoFidelityAmpLenGrid(SingleQubitExperiment):
    """
    Simple 2D grid runner that calls ro_fidelity at every (amp, integ_len) point.
    """

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="ro_fidelity_amp_len_grid",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )
        self.n_runs = int(kwargs.get("n_runs", 5_000))
        self.rep_rate_clk = int(kwargs.get("rep_rate_clk", 250_000))
        self.wait_rr = int(kwargs.get("wait_rr", 16))

        self.a_min = float(kwargs.get("a_min", 0.01))
        self.a_max = float(kwargs.get("a_max", 0.30))
        self.da = float(kwargs.get("da", 0.01))
        self.amps = np.arange(self.a_min, self.a_max + self.da / 2, self.da)
        if np.any(np.abs(self.amps) > 0.5):
            raise ValueError("All requested amplitudes must satisfy |amp| <= 0.5")

        t_array_clk = kwargs.get("t_array_clk", None)
        if t_array_clk is not None:
            t_array = np.asarray(t_array_clk, dtype=int).ravel()
            if t_array.size == 0 or np.any(t_array <= 0):
                raise ValueError("t_array_clk must contain strictly positive integers.")
            self.integration_lengths_clk = t_array
        else:
            self.integ_len_clk_min = int(kwargs.get("integ_len_clk_min", 50))
            self.integ_len_clk_max = int(kwargs.get("integ_len_clk_max", int(self.integ_len)))
            self.integ_len_clk_step = int(kwargs.get("integ_len_clk_step", 25))
            if self.integ_len_clk_step <= 0:
                raise ValueError("integ_len_clk_step must be > 0")
            self.integration_lengths_clk = np.arange(
                self.integ_len_clk_min,
                self.integ_len_clk_max + self.integ_len_clk_step,
                self.integ_len_clk_step,
                dtype=int,
            )
        if self.integration_lengths_clk.size == 0:
            raise ValueError("No integration lengths to scan.")

        # ro_len policy:
        # - "max": ro_len = max(base ro_len from config, integ_len) [default]
        # - "equal": ro_len = integ_len
        # - "fixed": use fixed_ro_len_clk
        self.ro_len_policy = str(kwargs.get("ro_len_policy", "max")).lower()
        self.fixed_ro_len_clk = kwargs.get("fixed_ro_len_clk", None)
        if self.ro_len_policy not in {"max", "equal", "fixed"}:
            raise ValueError("ro_len_policy must be one of: max, equal, fixed")
        if self.ro_len_policy == "fixed" and self.fixed_ro_len_clk is None:
            raise ValueError("fixed_ro_len_clk is required when ro_len_policy='fixed'")

        self.save_data = bool(kwargs.get("save_data", True))
        self.show_heatmap = bool(kwargs.get("show_heatmap", True))
        self.save_heatmap = bool(kwargs.get("save_heatmap", True))
        self.save_point_plots = bool(kwargs.get("save_point_plots", True))
        self.show_point_plots = bool(kwargs.get("show_point_plots", False))

        self.results = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "params": {
                "n_runs": self.n_runs,
                "rep_rate_clk": self.rep_rate_clk,
                "wait_rr": self.wait_rr,
                "a_min": self.a_min,
                "a_max": self.a_max,
                "da": self.da,
                "integration_lengths_clk": self.integration_lengths_clk,
                "ro_len_policy": self.ro_len_policy,
                "fixed_ro_len_clk": self.fixed_ro_len_clk,
            },
            "point_runs": [],
            "figures": [],
        }

    def _resolve_ro_len_clk(self, integ_len_clk: int) -> int:
        integ_len_clk = int(integ_len_clk)
        if self.ro_len_policy == "equal":
            return integ_len_clk
        if self.ro_len_policy == "fixed":
            return int(self.fixed_ro_len_clk)
        return int(max(int(self.ro_len), integ_len_clk))

    def run(self):
        t0 = time.time()
        n_amp = len(self.amps)
        n_len = len(self.integration_lengths_clk)
        fidelity_2d = np.full((n_amp, n_len), np.nan, dtype=float)
        best = None
        total = n_amp * n_len
        done = 0

        for ai, ro_amp in enumerate(self.amps):
            for li, integ_len_clk in enumerate(self.integration_lengths_clk):
                ro_len_clk = self._resolve_ro_len_clk(int(integ_len_clk))
                done += 1
                logger.info(
                    f"[{done}/{total}] q{self.q_no} rr{self.rr_no}: "
                    f"ro_amp={ro_amp:.4f}, integ_len={int(integ_len_clk)} clk, ro_len={ro_len_clk} clk"
                )
                run_info = {
                    "amp_index": int(ai),
                    "length_index": int(li),
                    "ro_amp": float(ro_amp),
                    "integration_length_clk": int(integ_len_clk),
                    "ro_len_clk": int(ro_len_clk),
                }
                try:
                    exp = validate_ro_point_with_ro_fidelity(
                        q_no=self.q_no,
                        rr_no=self.rr_no,
                        ro_amp=float(ro_amp),
                        ro_len_clk=int(ro_len_clk),
                        integ_len_clk=int(integ_len_clk),
                        n_runs=self.n_runs,
                        rep_rate_clk=self.rep_rate_clk,
                        wait_rr=self.wait_rr,
                        save_data=self.save_data,
                        save_plot=self.save_point_plots,
                        show_plot=self.show_point_plots,
                        query_LOs=False,
                    )
                    analysis = exp.results.get("analysis", {})
                    fidelity = float(analysis.get("fidelity_percent", np.nan))
                    fig_path = exp.results.get("figures", [None])[0] if exp.results.get("figures") else None
                    fidelity_2d[ai, li] = fidelity
                    run_info["fidelity_percent"] = fidelity
                    run_info["figure_path"] = fig_path
                    run_info["json_path"] = str(exp.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}.json"
                    if np.isfinite(fidelity) and (best is None or fidelity > best["fidelity_percent"]):
                        best = {
                            "amp_index": int(ai),
                            "length_index": int(li),
                            "ro_amp": float(ro_amp),
                            "integration_length_clk": int(integ_len_clk),
                            "ro_len_clk": int(ro_len_clk),
                            "fidelity_percent": float(fidelity),
                            "figure_path": fig_path,
                        }
                except Exception as exc:
                    run_info["error"] = str(exc)
                    logger.exception(
                        f"Point failed at ro_amp={ro_amp:.4f}, integ_len={int(integ_len_clk)} clk: {exc}"
                    )
                self.results["point_runs"].append(run_info)

        self.results["sweep"] = {
            "amps": self.amps,
            "integration_lengths_clk": self.integration_lengths_clk,
            "fidelity_percent_2d": fidelity_2d,
        }
        self.results["best_point"] = best

        fig, ax = plt.subplots(figsize=(9, 6))
        extent = [
            float(self.integration_lengths_clk[0]),
            float(self.integration_lengths_clk[-1]),
            float(self.amps[0]),
            float(self.amps[-1]),
        ]
        im = ax.imshow(
            fidelity_2d,
            aspect="auto",
            origin="lower",
            extent=extent,
            interpolation="nearest",
            cmap="viridis",
        )
        ax.set_xlabel("Integration length (clock cycles)")
        ax.set_ylabel("Readout amplitude")
        ax.set_title(f"RO fidelity map from ro_fidelity runs (q{self.q_no}, rr{self.rr_no})")
        if best is not None:
            ax.scatter(
                best["integration_length_clk"],
                best["ro_amp"],
                marker="x",
                s=120,
                color="white",
                label=f"Best {best['fidelity_percent']:.2f}%",
            )
            ax.legend(loc="lower right")
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label("Fidelity (%)")

        heatmap_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}_fidelity_map.png"
        if self.save_heatmap:
            fig.tight_layout()
            fig.savefig(heatmap_path, bbox_inches="tight")
            self.results["figures"].append(heatmap_path)
            cprint(f"Figure saved: {Path(heatmap_path).as_uri()}", "green")
        if self.show_heatmap:
            plt.show(block=False)
        else:
            plt.close(fig)

        if self.save_data:
            json_path = str(self.path_to_save) + f"_q{self.q_no}_rr{self.rr_no}.json"
            save_json(self.results, json_path)
            self.results["json_path"] = json_path
            cprint(f"Data saved: {Path(json_path).as_uri()}", "green")

        if best is not None:
            logger.info(
                f"Best point q{self.q_no} rr{self.rr_no}: "
                f"fidelity={best['fidelity_percent']:.2f}% at "
                f"ro_amp={best['ro_amp']:.4f}, integ_len={best['integration_length_clk']} clk, "
                f"ro_len={best['ro_len_clk']} clk"
            )
            logger.info(f"Best-point figure path: {best['figure_path']}")
        else:
            logger.warning("No successful point found in sweep.")

        elapsed = time.time() - t0
        logger.info(f"Total time: {int(elapsed // 60)}m {elapsed % 60:.1f}s")
        return self.results


def perform_ro_fidelity_amp_len_grid(q_no: int, rr_no: int = None, **kwargs):
    exp = RoFidelityAmpLenGrid(q_no=q_no, rr_no=rr_no, **kwargs)
    exp.run()
    return exp


if __name__ == "__main__":
    qubit_list = [
        1,
        2,
        3,
        4,
        6
    ]
    for qubit in qubit_list:
        exp = perform_ro_fidelity_amp_len_grid(
            q_no=qubit,
            n_runs=1000,
            a_min=0.02,
            a_max=0.49,
            da=0.01,
            t_array_clk=np.arange(100, 2000, 50),
            ro_len_policy="max",
            save_data=True,
            save_point_plots=True,
            show_point_plots=False,
            save_heatmap=True,
            show_heatmap=True,
        )
        best = exp.results.get("best_point")
        if best is not None:
            cprint(
                "Best-point IQ blob: "
                f"{best.get('figure_path')} "
                f"(fidelity={best.get('fidelity_percent'):.2f}%)",
                "cyan",
            )
