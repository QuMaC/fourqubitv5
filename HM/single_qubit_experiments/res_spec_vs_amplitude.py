import time
import json
from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from Configuration_Files.config_dictionaries import rr_IF, q_IF, rr_LO, q_LO, f
from HM.utilities.post_processing_utils import return_elec_delay
from HM.utilities.files_utils import save_json
import numpy as np
from Helper_Functions.macros import update_config_rr
from Helper_Functions.spectro_helper import smooth_filter
from qm.qua import program, declare, for_, update_frequency, fixed, declare_stream, wait, measure, save, stream_processing, demod
from qualang_tools.loops import from_array

from qm import QuantumMachinesManager, SimulationConfig, LoopbackInterface
import matplotlib.pyplot as plt
import logging
from termcolor import cprint
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class ResonatorSpectroscopyVsAmplitude(SingleQubitExperiment):
    def __init__(self, rr_no: int, q_no: int = None, **kwargs):
        super().__init__(q_no, rr_no, expt_name="res_spec_vs_amplitude", **kwargs)
        self.prev_rr_frequency = float(self.fr)
        self.readout_settings_path = self.config_files_path + '/Readout_Settings'
        self.prev_rr_amplitude = self.get_rr_amplitude(rr_no)



    def get_rr_amplitude(self, rr_no: int):
        with open(self.readout_settings_path + '/ro_amp.json', 'r') as f:
            self.ro_amp_dict = json.load(f)
        return self.ro_amp_dict[f"{rr_no}"]



    def run_experiment(self):
        pass

    def analyze_and_plot(self):
        pass

    def save_experiment_data(self):
        pass
