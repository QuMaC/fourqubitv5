
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
from Helper_Functions.helper_functionsv2 import bulk_switch, keyer
import time
from scipy.optimize import minimize


logger = logging.getLogger(__name__)

class MixerOffsetCalibration(SingleQubitExperiment):
    def __init__(self, q_no: int, rr_no: int = None, expt_element: str = "qubit", **kwargs):

        super().__init__(q_no, rr_no, expt_name=f"mixer_offset_calibration_{expt_element}", 
        query_LOs=kwargs.pop("query_LOs", True),
        **kwargs)

        self._qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)
        self.qm = self._qmm.open_qm(self.config)

        self.keysight_xseries = KeysightXSeries(_DEFAULT_ADDRESS, self.qm)
        self.qe_freq_dict = self._get_qe_freq_dict()
        self.span_in_MHz = kwargs.get("span_in_MHz", 50)
        self.bandwidth_in_KHz = kwargs.get("bandwidth_in_KHz", 5)
        self.sweep_points = kwargs.get("sweep_points", 501)
        self.leakage_threshold = kwargs.get("leakage_threshold", -100)
        self.leakage_target = kwargs.get("leakage_target", -99)
        self.fatol = kwargs.get("fatol", 1)
        self.maxiter = kwargs.get("maxiter", 50)
        self.calibration_files_path = kwargs.get("calibration_files_path", self.config_files_path + "/Calibrations")
        self.iteration_data = {
            "intermediate_x": [],
            "intermediate_fun": [],
        }
        self.initial_simplex = kwargs.get("initial_simplex", np.array([[0, -0.2], [0.2, 0.2], [-0.2, 0.2]]))
        self.save_data = kwargs.get("save_data", False)
        self.save_plot = kwargs.get("save_plot", True)
        self.rm = visa.ResourceManager()
        if expt_element == "qubit":
            self.qe = f"q{self.q_no}"
        elif expt_element == "resonator":
            self.qe = f"rr{self.rr_no}"
        else:
            raise ValueError(f"Invalid experiment type: {expt_element}")

        




    def _get_qe_freq_dict(self):
        qe_freq_dict = {}
        for i in range(1, 9):
            qe_freq_dict[f"q{i}"] = [self.q_lo_dict[f"{i}"], self.dac_mapping[f"q{i}"]]
            qe_freq_dict[f"rr{i}"] = [self.rr_lo_dict[f"{i}"], self.dac_mapping[f"rr{i}"]]
        print(qe_freq_dict)
        return qe_freq_dict

    def _build_program(self):
        with program() as mixer_offset_calibration_program:
            with infinite_loop_():
                play("const" * amp(0.0), self.qe)
        
        self.program = mixer_offset_calibration_program
        return mixer_offset_calibration_program


    def _callback(self, *, intermediate_result):
        print("intermediate_fun", intermediate_result.fun)
        print("intermediate_x", intermediate_result.x)

        self.iteration_data["intermediate_x"].append([intermediate_result.x[0], intermediate_result.x[1]])
        self.iteration_data["intermediate_fun"].append(intermediate_result.fun)

    def _set_dc_offset_get_leakage(self, offset_arr, verbose=True):
        I_offset, Q_offset = offset_arr[0], offset_arr[1]
        self.qm.set_output_dc_offset_by_element(self.qe, "I", I_offset)
        self.qm.set_output_dc_offset_by_element(self.qe, "Q", Q_offset)
        time.sleep(2)
        leakage = self.keysight_xseries.query_marker(1)
        if verbose:
            print(f"Current leakage is {leakage} dBm")
        if leakage < self.leakage_threshold:
            return 0
        return abs(leakage - self.leakage_target) # -99 dBm good target, this is the diff between leakage and the target

    
    def plot_iteration_data(self):
        plt.figure(figsize=(10, 5))
        self.iteration_data["intermediate_x"] = np.array(self.iteration_data["intermediate_x"])
        plt.plot(self.iteration_data["intermediate_x"][:, 0] , self.iteration_data["intermediate_fun"], "o-")
        plt.plot(self.iteration_data["intermediate_x"][:, 1], self.iteration_data["intermediate_fun"], "o-")

        plt.xlabel("DC Offset")
        plt.ylabel("Leakage")
        plt.title("Iteration Data")

        file_path = str(self.path_to_save) + f"_q{self.q_no}_iteration_data.png"
        plt.savefig(file_path)
        cprint(f"Iteration data saved to {file_path}", "green")


    def run_experiment(self):
        try:
            bulk_switch(qe=keyer(self.qe, self.dac_mapping), ip=self.sw_ip, switches=self.switches)
        except:
            print('Switch not accessible for some reason')

        self._build_program()
        job = self.qm.execute(self.program)
        central_freq, qe_ch = self.qe_freq_dict[self.qe]
        self.keysight_xseries.set_bandwidth(self.bandwidth_in_KHz)
        self.keysight_xseries.set_sweep_points(self.sweep_points)
        self.keysight_xseries.set_center_freq(central_freq)
        self.keysight_xseries.set_span(self.span_in_MHz)
        self.keysight_xseries.active_marker(1)
        self.keysight_xseries.set_marker_freq(1, central_freq)


        #initialization of the optimization
        self.dacs = self.dac_mapping[self.qe][-1]
        self.controller_idx = self.dac_mapping[self.qe][0]
        self.dc_offsets = dc_offsets

        inital_values = [self.dc_offsets[f'con{self.controller_idx}'][f'{self.dacs[0]}'], self.dc_offsets[f'con{self.controller_idx}'][f'{self.dacs[1]}']]
        bnds = ((-0.3, 0.3), (-0.3, 0.3))       
        initial_simplex = self.initial_simplex
        initial_simplex[0, :] = [0, -0.2]
        initial_simplex[1, :] = [0.2, 0.2]
        initial_simplex[2, :] = [-0.2, 0.2]

        self.res = minimize(
            self._set_dc_offset_get_leakage,
            x0=np.array(inital_values),
            args=self.qe,
            method="Nelder-Mead",
            bounds=bnds,
            callback=self._callback,
            options={
                "fatol": self.fatol,
                "maxiter": self.maxiter,
                # "initial_simplex": initial_simplex
            }
        )
        if self.res.nit >= self.maxiter:
            cprint(f"Warning: Optimization hit maximum iterations ({self.maxiter}) for {self.qe}.", "black", on_color="on_red", attrs=["bold"])

        self.final_value = self.keysight_xseries.query_marker(1)
        print(f"Final leakage is {self.final_value} dBm")
        print(f"Calibrated mixer offsets for {self.qe} are {self.res.x}")
        if self.save_plot:
            self.plot_iteration_data()
        


    def update_config_dicts(self):
        self.dc_offsets[f"con{self.controller_idx}"][f"{self.dacs[0]}"] = self.res.x[0]
        self.dc_offsets[f"con{self.controller_idx}"][f"{self.dacs[1]}"] = self.res.x[1]
        with open(self.calibration_files_path + "/dc_offsets.json", 'w') as f:
            json.dump(self.dc_offsets, f, indent=6)
        f.close()

        #caching offset sideband values
        #### 
        import os
        if os.path.isfile(self.single_qubit_experiments_path +"/cached_jsons/"  + "/offset_sideband_values.json"):
            with open(self.single_qubit_experiments_path +"/cached_jsons/"  + "/offset_sideband_values.json", 'r') as f:
                offset_sideband_values = json.load(f)
                f.close()
        else:
            print(f"No offset sideband values found for {self.qe}, creating new entry")
            offset_sideband_values = {self.qe: {"offset": 0, "sideband": 0}}

        offset_sideband_values[self.qe] = {"offset": self.final_value, "sideband": 0}
        with open(self.single_qubit_experiments_path +"/cached_jsons/"  + "/offset_sideband_values.json", 'w') as f:
            json.dump(offset_sideband_values, f, indent=6)
        f.close()
  
    def save_experiment_data(self):
        self.iteration_data = np.array(self.iteration_data)
        result = {
            "q_no": self.q_no,
            "rr_no": self.rr_no,
            "final_value": self.final_value,
            "res": self.res.x,
            "iteration_data": self.iteration_data.tolist(),
        }
        json_path = str(self.path_to_save) + f"_q{self.q_no}.json"
        self.save_json(result, json_path)
        return result




    
    def run(self):
        t0 = time.time()
        result = {}
        cprint(f"Running mixer offset calibration for {self.qe}", "black", on_color="on_green", attrs=["bold"])
        cprint(f"Starting time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", "black", on_color="on_green", attrs=["bold"])
        try:
            self.run_experiment()
            self.update_config_dicts()
            if self.save_data:
                result = self.save_experiment_data()
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
        
        #I should probably return the result here

        return self.final_value



def perform_complete_mixer_offset_calibration(q_no: int, rr_no: int = None, **kwargs):
    #qubit:'
    expt_element = "qubit"
    mixer_offset_calibration_qubit = MixerOffsetCalibration(q_no, rr_no, expt_element, **kwargs)
    result_qubit = mixer_offset_calibration_qubit.run()

    #resonator:
    expt_element = "resonator"

    mixer_offset_calibration_resonator = MixerOffsetCalibration(q_no, rr_no, expt_element, **kwargs)
    result_resonator = mixer_offset_calibration_resonator.run()

    result = {
        "qubit": result_qubit,
        "resonator": result_resonator,
    
    }
    return result



if __name__ == "__main__":
    q_no = 1
    rr_no = 1
    save_plot = False
    result = perform_complete_mixer_offset_calibration(q_no, rr_no, save_plot=save_plot)
    print(result)
    


        





















