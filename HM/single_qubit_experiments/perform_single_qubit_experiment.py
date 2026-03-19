from HM.single_qubit_experiments.qubit_spec import QubitSpectroscopy
from HM.single_qubit_experiments.vna_resonator_spectroscopy import VNASpectroscopy

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

def perform_single_qubit_experiment(q_no: int, rr_no: int = None, **kwargs):
    for expt in kwargs.get("experiments", []):
        if expt == "qubit_spec":
            qubit_spec_kwargs = kwargs.get("qubit_spec_kwargs", _default_qubit_spectroscopy_kwargs)
            qubit_spec = QubitSpectroscopy(q_no, rr_no, **qubit_spec_kwargs)
            qubit_spec.run_experiment()
        elif expt == "vna_resonator_spectroscopy":
            vna_resonator_spectroscopy_kwargs = kwargs.get("vna_resonator_spectroscopy_kwargs", _default_vna_resonator_spectroscopy_kwargs)
            vna_resonator_spectroscopy = VNASpectroscopy(q_no, rr_no, **vna_resonator_spectroscopy_kwargs)
            vna_resonator_spectroscopy.run_experiment()
        else:
            raise ValueError(f"Invalid experiment: {expt}")




if __name__ == "__main__":
    for q_no in range(1, 6):
        perform_single_qubit_experiment(q_no)