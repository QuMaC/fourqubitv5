from HM.simulator.two_qubit_simulator.engine.pulses import cr_rise_fall_flat_top
from Configuration_Files.config_dictionaries import *
from HM.simulator.two_qubit_simulator.engine.pulses import Timeline
from HM.simulator.two_qubit_simulator.base_classes.device_base import TwoQubitSimulatorBase
from Helper_Functions.CR_fitters import  CR_Hamiltonian_tomography, bloch_functions
import qutip as qt
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

class RabiLenSim(TwoQubitSimulatorBase):
    def __init__(self, qubit_pair = [1,2], len_list = None, **kwargs):
        super().__init__(qubit_pair=qubit_pair, **kwargs)
        self.len_list = len_list
        _default_rabi_pulse_params = {
            "amp_mhz": 65.0,
            "t_rise_ns": 16,
            "sigma_ns": 5,
            "t_flat_ns": None,
        }
        self.rabi_pulse_params = kwargs.get("rabi_pulse_params", _default_rabi_pulse_params)
