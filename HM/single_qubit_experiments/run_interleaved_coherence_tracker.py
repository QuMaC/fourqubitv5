import time

from HM.single_qubit_experiments.interleaved_coherence import run_interleaved_coherence_tracking


if __name__ == "__main__":
    qubit_list = [1, 2, 3, 4, 5, 6]
    rr_map = {
        # 1: 1,
        # 2: 2,
    }

    tracking_kwargs = {
        "run_forever": True,
        # "max_cycles": 10,  # Use with run_forever=False for finite runs.
        "sleep_between_cycles_s": 10.0,
        "continue_on_error": True,
        "save_every_cycle": True,
        # "save_root": r"D:\QUA\Master_Scripts\fourqubitv5_Hari\HM\data_misc",
    }

    interleaved_kwargs = {
        "n_avgs": 60,
        "detuning_mhz": 0.1,
        "save_data": True,
        "min_avg_bound": 200,
        "plot_live": False,
    }

    t0 = time.time()
    summary = run_interleaved_coherence_tracking(
        qubit_list=qubit_list,
        rr_map=rr_map if rr_map else None,
        **tracking_kwargs,
        **interleaved_kwargs,
    )

    elapsed = time.time() - t0
    print(
        f"Tracking finished after {elapsed / 3600:.2f} h. "
        f"Saved JSON: {summary['output_files']['json']} | "
        f"Saved plot: {summary['output_files']['plot']}"
    )
