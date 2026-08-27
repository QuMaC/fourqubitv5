import logging
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from termcolor import cprint
from Configuration_Files.config_dictionaries import u, dc_offsets
from Helper_Functions.auto_mixer_tools_visa import KeysightXSeries, _DEFAULT_ADDRESS
import json
import pyvisa as visa
from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from qm import QuantumMachinesManager
from qm.qua import program, infinite_loop_, play, amp
from Helper_Functions.helper_functionsv2 import bulk_switch, keyer, IQ_imbalance
import time
from scipy.optimize import minimize
SLEEP_TIME = 2

logger = logging.getLogger(__name__)

class MixerSidebandCalibration(SingleQubitExperiment):
    def __init__(self, q_no: int, rr_no: int = None, expt_element: str = "qubit", **kwargs):

        super().__init__(q_no, rr_no, expt_name=f"mixer_sideband_calibration_{expt_element}", 
        query_LOs=kwargs.pop("query_LOs", True),
        **kwargs)

        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        self.qm = self._qmm.open_qm(self.config)

        self.keysight_xseries = KeysightXSeries(_DEFAULT_ADDRESS, self.qm)
        self.span_in_MHz = kwargs.get("span_in_MHz", 50)
        self.bandwidth_in_KHz = kwargs.get("bandwidth_in_KHz", 5)
        self.sweep_points = kwargs.get("sweep_points", 501)
        self.leakage_threshold = kwargs.get("leakage_threshold", -90)
        self.leakage_target = kwargs.get("leakage_target", -90)
        self.fatol = kwargs.get("fatol", 1)
        self.maxiter = kwargs.get("maxiter", 50)
        self.calibration_files_path = kwargs.get("calibration_files_path", self.config_files_path + "/Calibrations")
        self.iteration_data = {
            "intermediate_x": [],
            "intermediate_fun": [],
        }
        self.initial_simplex = kwargs.get("initial_simplex", np.array([[0.19, 0.19], [0.19, -0.19], [-0.19, 0]]))
        self.save_data = kwargs.get("save_data", False)
        # self.save_plot = kwargs.get("save_plot", True)
        self.rm = visa.ResourceManager()
        if expt_element == "qubit":
            self.qe = f"q{self.q_no}"
            self.qe_amp = self.X180_amp
            self.qe_lo_val_in_Hz = self.q_lo_val_MHz*1e6
            self.qe_if_val_in_Hz = self.q_if_val_in_MHz*1e6
        elif expt_element == "resonator":
            self.qe = f"rr{self.rr_no}"
            self.qe_amp = self.ro_amp
            self.qe_lo_val_in_Hz = self.rr_lo_val_MHz*1e6
            self.qe_if_val_in_Hz = self.rr_if_val_in_MHz*1e6

        elif expt_element == "qubit12":
            self.qe = f"q12_{self.q_no}"
            # self.qe_amp = self.X180_amp
            raise NotImplementedError("Qubit 12 sideband calibration is not implemented yet")
            #TODO: need to expand this to control target and qe12

        else:
            raise ValueError(f"Invalid experiment type: {expt_element}")
        
        self.iq_imbalance_pair = self.iq_imbalance_dict[self.qe]
        self.analysis_freq_in_Hz = self.qe_lo_val_in_Hz - self.qe_if_val_in_Hz



    def _build_program(self):
        with program() as mixer_sideband_calibration_program:
            with infinite_loop_():
                play("const" * amp(self.qe_amp), self.qe)
        
        self.program = mixer_sideband_calibration_program
        return mixer_sideband_calibration_program
    
    def _callback(self, *, intermediate_result):
        print("intermediate_fun", intermediate_result.fun)
        print("intermediate_x", intermediate_result.x)

        self.iteration_data["intermediate_x"].append([intermediate_result.x[0], intermediate_result.x[1]])
        self.iteration_data["intermediate_fun"].append(intermediate_result.fun)

    def _set_iq_imbalance_get_leakage(self, imbalance_arr, verbose=True):
        a_imb, p_imb = imbalance_arr
        mixer_str = "mixer_" + self.qe
        assert int(self.qe_lo_val_in_Hz) > 1e9, f"LO frequency is too low: {self.qe_lo_val_in_Hz}"
        assert int(abs(self.qe_if_val_in_Hz)) > 1e6, f"IF frequency is too low: {abs(self.qe_if_val_in_Hz)}"
        self.qm.set_mixer_correction(mixer_str, int(self.qe_if_val_in_Hz), int(self.qe_lo_val_in_Hz), IQ_imbalance(a_imb, p_imb))
        time.sleep(SLEEP_TIME)
        leakage = self.keysight_xseries.query_marker(1)
        if verbose:
            print("Current leakage is {0} dBm".format(leakage))
        if leakage < self.leakage_threshold:
            return 0  # return low constant values so that the optimization loop quits
        return abs(leakage - self.leakage_target)

    
    def run_experiment(self):
        try:
            bulk_switch(qe=keyer(self.qe, self.dac_mapping), ip=self.sw_ip, switches=self.switches)
        except:
            print('Switch not accessible for some reason')
        
        self._build_program()
        job = self.qm.execute(self.program)
        self.keysight_xseries.set_bandwidth(self.bandwidth_in_KHz)
        self.keysight_xseries.set_sweep_points(self.sweep_points)
        self.keysight_xseries.set_center_freq(self.analysis_freq_in_Hz)
        self.keysight_xseries.set_span(self.span_in_MHz)
        self.keysight_xseries.active_marker(1)
        self.keysight_xseries.set_marker_freq(1, self.analysis_freq_in_Hz)

        inital_values = [self.iq_imbalance_pair["a"], self.iq_imbalance_pair["p"]]
        init_abs = [0.3 - abs(inital_values[0]), 0.3 - abs(inital_values[1])]
        if init_abs[0] < 0.05:
            inital_values = [self.iq_imbalance_pair["a"]*0.5, self.iq_imbalance_pair["p"]]
        if init_abs[1] < 0.05:
            inital_values = [self.iq_imbalance_pair["a"], self.iq_imbalance_pair["p"]*0.5]
        bnds = ((-0.3, 0.3), (-0.3, 0.3))
        initial_simplex = self.initial_simplex
        initial_simplex[0, :] = [0.19, 0.19]
        initial_simplex[1, :] = [0.19, -0.19]
        initial_simplex[2, :] = [-0.19, 0]
        self.res = minimize(self._set_iq_imbalance_get_leakage,
                       x0=np.array(inital_values),
                       method="Nelder-Mead",
                       bounds=bnds,
                       callback=self._callback,
                       options={
                        "fatol": self.fatol,
                       "maxiter": self.maxiter,
                       }
                       )
        if self.res.nit >= self.maxiter:
            cprint(f"Warning: Optimization hit maximum iterations ({self.maxiter}) for {self.qe}.", "black", on_color="on_red", attrs=["bold"])
        self.final_value = self.keysight_xseries.query_marker(1)
        print(f"Final leakage for {self.qe} is {self.final_value} dBm")
        element_freq = self.qe_lo_val_in_Hz + self.qe_if_val_in_Hz
        self.keysight_xseries.set_center_freq(element_freq)
        self.keysight_xseries.set_marker_freq(1, element_freq)
        self.upconverted_sideband_power = self.keysight_xseries.query_marker(1)
        print(f"Upconverted sideband power for {self.qe} is {self.upconverted_sideband_power} dBm")
        print(f"Calibrated IQ imbalance tuple is {self.res.x}")

    def update_config_dicts(self):
        import os
        a, p = self.res.x
        self.iq_imbalance_dict[self.qe]["a"] = a
        self.iq_imbalance_dict[self.qe]["p"] = p
        with open(self.config_files_path + "/Calibrations/" + "/iq_imbalance.json", "w") as f:
            json.dump(self.iq_imbalance_dict, f, indent=4)

        if os.path.isfile(self.single_qubit_experiments_path + "/cached_jsons/" + "/offset_sideband_values.json"):
            with open(self.single_qubit_experiments_path + "/cached_jsons/" + "/offset_sideband_values.json", "r") as f:
                offset_sideband_values = json.load(f)
            offset_sideband_values[self.qe]["sideband"] = self.final_value
            with open(self.single_qubit_experiments_path + "/cached_jsons/" + "/offset_sideband_values.json", "w") as f:
                json.dump(offset_sideband_values, f, indent=4)
        else:
            offset_sideband_values = {self.qe: {"sideband": self.final_value, "offset": 0}}
            with open(self.single_qubit_experiments_path + "/cached_jsons/" + "/offset_sideband_values.json", "w") as f:
                json.dump(offset_sideband_values, f, indent=4)

        
    def save_experiment_data(self):
        result = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "final_value": self.final_value,
            "res": self.res.x,
            "iteration_data": self.iteration_data,
        }
        json_path = str(self.path_to_save) + f"_q{self.q_no}.json"
        self.save_json(result, json_path)
        return result
    

    def run(self):
        t0 = time.time()
        cprint(f"Running mixer sideband calibration for {self.qe}", "black", on_color="on_green", attrs=["bold"])
        cprint(f"Starting time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", "black", on_color="on_green", attrs=["bold"])
        try:
            self.run_experiment()
            self.update_config_dicts()
            if self.save_data:
                self.save_experiment_data()
            else:
                cprint(f"Data not saved", "red")
        finally:
            if self._qmm is not None:
                try:
                    self._qmm.close()
                except Exception:
                    pass
        elapsed = time.time() - t0
        print(f"Total time: {int(elapsed // 60)}m {elapsed % 60:.1f}s")
        return self.final_value


    

def perform_complete_mixer_sideband_calibration(q_no: int, rr_no: int = None, **kwargs):

    #qubit:
    expt_element = "qubit"
    mixer_sideband_calibration_qubit = MixerSidebandCalibration(q_no, rr_no, expt_element, **kwargs)
    result_qubit = mixer_sideband_calibration_qubit.run()

    #resonator:
    expt_element = "resonator"
    mixer_sideband_calibration_resonator = MixerSidebandCalibration(q_no, rr_no, expt_element, **kwargs)
    result_resonator = mixer_sideband_calibration_resonator.run()
    result = {
        "qubit": result_qubit,
        "resonator": result_resonator,
    }
    return result


if __name__ == "__main__":
    q_no = 1
    rr_no = 1
    result = perform_complete_mixer_sideband_calibration(q_no, rr_no)
    print(result)
        
        