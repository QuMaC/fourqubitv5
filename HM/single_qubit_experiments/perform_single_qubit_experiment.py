from HM.single_qubit_experiments.qubit_spectroscopy import perform_qubit_spectroscopy
from HM.single_qubit_experiments.vna_resonator_spectroscopy import perform_vna_resonator_spectroscopy
from HM.single_qubit_experiments.mixer_offset_calibration import perform_complete_mixer_offset_calibration
from HM.single_qubit_experiments.mixer_sideband_calibration import perform_complete_mixer_sideband_calibration
from HM.single_qubit_experiments.rabi_amp import perform_rabi_amp
_default_vna_resonator_spectroscopy_kwargs = {
    "turn_off_LOs": True,
    "update_config": True,
    "save_data": True,
    "f_search_start": 7.0e9,
    "f_search_stop": 7.75e9,
    "zoom_half_span": 15e6,
    "low_power": -30,
    "n_avgs": 100,
    "if_bw": 1e3,
    # "n_points": 2001,
    # "cmd_delay": 3.0,

}
_default_qubit_spectroscopy_kwargs = {
    "n_avgs": 1000,
    "n_samples": 2000,
    "f_min_MHz": -400,
    "f_max_MHz": 400,
    "update_config": True,
    "save_data": True,
}
_default_mixer_offset_calibration_kwargs = {
    "save_data": True,
}
_default_mixer_sideband_calibration_kwargs = {
    "save_data": True,
}
def perform_single_qubit_experiment(q_no: int, rr_no: int = None, **kwargs):
    
    for expt in kwargs.get("experiments", []):
        if expt == "vna_res_spec":
            vna_resonator_spectroscopy_kwargs = kwargs.get("vna_resonator_spectroscopy_kwargs", _default_vna_resonator_spectroscopy_kwargs)
            perform_vna_resonator_spectroscopy(q_no, rr_no, **vna_resonator_spectroscopy_kwargs)
        elif expt == "qubit_spec":
            qubit_spec_kwargs = kwargs.get("qubit_spec_kwargs", _default_qubit_spectroscopy_kwargs)
            perform_qubit_spectroscopy(q_no, rr_no, **qubit_spec_kwargs)

        elif expt == "rabi_amp":
            rabi_amp_kwargs = kwargs.get("rabi_amp_kwargs", _default_rabi_amp_kwargs)
            perform_rabi_amp(q_no, rr_no, **rabi_amp_kwargs)
        elif expt == "mixer_offset_calibration":
            mixer_offset_calibration_kwargs = kwargs.get("mixer_offset_calibration_kwargs", _default_mixer_offset_calibration_kwargs)
            perform_complete_mixer_offset_calibration(q_no, rr_no, **mixer_offset_calibration_kwargs)
        elif expt == "mixer_sideband_calibration":
            mixer_sideband_calibration_kwargs = kwargs.get("mixer_sideband_calibration_kwargs", _default_mixer_sideband_calibration_kwargs)
            perform_complete_mixer_sideband_calibration(q_no, rr_no, **mixer_sideband_calibration_kwargs)
        else:
            raise ValueError(f"Invalid experiment: {expt}")




if __name__ == "__main__":
    import time
    expt_kwargs = {
        "experiments": [
            # "vna_res_spec",
            # "qubit_spec",
            "mixer_offset_calibration",
            "mixer_sideband_calibration",
        ],
        "qubit_spec_kwargs": _default_qubit_spectroscopy_kwargs,
        "vna_resonator_spectroscopy_kwargs": _default_vna_resonator_spectroscopy_kwargs,
    }
    qubit_nos = [
        1,
        2,
        3,
        4,	
        5,
        6,
    ]

    time_started = time.time()
    for q_no in qubit_nos:
        perform_single_qubit_experiment(q_no, **expt_kwargs)












    ##### Timekeeping
    time_ended = time.time()
    elapsed = time_ended - time_started
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = elapsed % 60
    print(f"Total time for the entire set of qubits taken: {hours}h {minutes}m {seconds:.1f}s")