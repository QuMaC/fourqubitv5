from scipy.signal import gaussian
from helper_functions import *

qubit_LO = 4e9
qubit_IF = 100e6
rr_LO = 7e9
rr_IF = 50e6
ro_len_clk = 500
integ_len_clk = 50#ro_len_clk
pi_len_ns = 100
pi_scale = 0.3706



config = {

    "version": 1,

    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                1: {"offset": -0.12142362252441788},  # qubit_I -0.0722 before amp 
                2: {"offset": -0.045400922535486665},  # qubit_Q  #leakage -105 dBm ; ON -39 dBm -0.0295 before amp
                9: {"offset": 0.467},  # rr_I 
                10: {"offset": 4},  # rr_Q   leakage -105 dBm ; ON -46 dBm
            },
            "digital_outputs": {},
            "analog_inputs": {
                1: {"offset": 0.1255, 'gain_db': 0},  # rr_I
                2: {"offset": -0.1499, 'gain_db': 0}  # rr_Q
            },
        },
    },

    "elements": {
        "qubit": {
            "mixInputs": {
                "I": ("con1", 1),
                "Q": ("con1", 2),
                "lo_frequency": qubit_LO,
                "mixer": "mixer_qubit",
            },
            "intermediate_frequency": qubit_IF,
            "operations": {
                "test_pulse": "const_pulse_IQ",
                "const": "const_pulse_IQ",
                "gauss": "gaussian_pulse",
                "X": "X",
                "X/2": "X/2",
                "-X/2": "-X/2",
                "Y": "Y",
                "Y/2": "Y/2",
                "-Y/2": "-Y/2",
            },
        },

        "rr": {
            "mixInputs": {
                "I": ("con1", 9),
                "Q": ("con1", 10),
                "lo_frequency": rr_LO,
                "mixer": "mixer_ro",
            },
            "intermediate_frequency": rr_IF,
            "outputs": {
                "out1": ("con1", 1),
                "out2": ("con1", 2),
            },
            "time_of_flight": 592, #300
            "smearing": 0,
            "operations": {
                "const": "const_pulse_IQ",
                "gauss": "gaussian_pulse",
                "readout": "ro_pulse",
            }
        },

    },

    "pulses": {

        "const_pulse_IQ": {
            "operation": "control",
            "length": 100,
            "waveforms": {"I": "const_wf", "Q": "zero_wf"},
        },

        "gaussian_pulse": {
            "operation": "control",
            "length": pi_len_ns,
            "waveforms": {"I": "gauss_wf", "Q": "zero_wf"},
        },

        "X": {
            "operation": "control",
            "length": pi_len_ns,
            "waveforms": {"I": "X_I_wf", "Q": "zero_wf"},
        },

         "Y": {
            "operation": "control",
            "length": pi_len_ns,
            "waveforms": {"I": "zero_wf", "Q": "Y_Q_wf"},
        },

        "X/2": {
                    "operation": "control",
                    "length": pi_len_ns,
                    "waveforms": {"I": "X/2_I_wf", "Q": "zero_wf"},
                },

        "Y/2": {
                    "operation": "control",
                    "length": pi_len_ns,
                    "waveforms": {"I": "zero_wf", "Q": "Y/2_Q_wf"},
                },
        "-X/2": {
                            "operation": "control",
                            "length": pi_len_ns,
                            "waveforms": {"I": "-X/2_I_wf", "Q": "zero_wf"},
                        },

        "-Y/2": {
                    "operation": "control",
                    "length": pi_len_ns,
                    "waveforms": {"I": "zero_wf", "Q": "-Y/2_Q_wf"},
                },
        

        "ro_pulse": {
            "operation": "measurement",
            "length": ro_len_clk * 4,
            "waveforms": {"I": "ro_wf", "Q": "zero_wf"},
            "integration_weights": {
                "integW_cos": "integW_cos",
                "integW_sin": "integW_sin",
                "integW_minus_sin": "integW_minus_sin"
            },
            "digital_marker": "ON",
        },

    },

    "waveforms": {
        "zero_wf": {"type": "constant", "sample": 0.0},
        "const_wf": {"type": "constant", "sample": 0.4},
        "ro_wf": {"type": "constant", "sample": 0.4},
        "gauss_wf": {"type": "arbitrary", "samples": [float(arg) for arg in 0.4 * gaussian(pi_len_ns, pi_len_ns//6)]},
        "X_I_wf": {"type": "arbitrary", "samples": [float(arg) for arg in 0.4 * pi_scale * gaussian(pi_len_ns, pi_len_ns//6)]},
        "Y_Q_wf": {"type": "arbitrary", "samples": [float(arg) for arg in 0.4 * pi_scale * gaussian(pi_len_ns, pi_len_ns//6)]},
        "X/2_I_wf": {"type": "arbitrary", "samples": [float(arg) for arg in 0.4 * 0.5 * pi_scale * gaussian(pi_len_ns, pi_len_ns//6)]},
        "-X/2_I_wf": {"type": "arbitrary", "samples": [float(arg) for arg in -0.4 * 0.5 * pi_scale * gaussian(pi_len_ns, pi_len_ns//6)]},
        "Y/2_Q_wf": {"type": "arbitrary", "samples": [float(arg) for arg in 0.4 * 0.5 * pi_scale * gaussian(pi_len_ns, pi_len_ns//6)]},
        "-Y/2_Q_wf": {"type": "arbitrary", "samples": [float(arg) for arg in -0.4 * 0.5 * pi_scale * gaussian(pi_len_ns, pi_len_ns//6)]}
    },

    "digital_waveforms": {
        "ON": {"samples": [(1, 0)]}},

    "integration_weights": {
        "integW_cos": {
            "cosine": [1.0] * integ_len_clk,
            "sine": [0.0] * integ_len_clk,
        },
        "integW_sin": {
            "cosine": [0.0] * integ_len_clk,
            "sine": [1.0] * integ_len_clk,
        },
        "integW_minus_sin": {
            "cosine": [0.0] * integ_len_clk,
            "sine": [-1.0] * integ_len_clk,
        }
    },

    "mixers": {
        "mixer_qubit": [{"intermediate_frequency": qubit_IF, "lo_frequency": qubit_LO, "correction": IQ_imbalance(0.03087066799715502,0.05494634281175763)}],
        "mixer_ro": [{"intermediate_frequency": rr_IF, "lo_frequency": rr_LO, "correction": IQ_imbalance(-0.0876483, -0.10233029)}],
    }
}

# IQ_imbalance(0.0172, 0.0122) reject band -79 dBm ; qubit band -0.3 dBm
#IQ_imbalance(0.0115, 0.0128) qubit before amp
#IQ_imbalance(-0.028, -0.088) rr before amp
#qm.set_mixer_correction('mixer_ro', int(rr_IF), int(rr_LO), IQ_imbalance(0.0115, 0.0128))
#qm.set_output_dc_offset_by_element("qubit", "I", -0.07225)
#Qubit - reject band : -102 dBm ; qubit band : -29.25 dBm
#Readout - reject band : -101 dBm ; readout band : -37.3 dBm