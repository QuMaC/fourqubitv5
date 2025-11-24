from helper_functionsv2 import *
from qualang_tools.units import unit
import json
u = unit()

import matplotlib
matplotlib.use('Qt5Agg')

path = r"E:\Experiments\2023-03-23 Ringv1_4Q"
#=======================Frequencies==========================================
Line1_Line3 = False #False => Line1
Line2_Line4 = False #False => Line2
#Use for enabling temporary set for measuring 4 qubit setup using only two lines/quantum elements

qe_list = ["q1", "q2",
           "rr1", "rr2",
           "cr_c1t2"]

CrossKerr = {"1" : 0.236 * u.MHz,              #Calculate and update later using simulation/ conditional Ramsey
      "2" : 0.230 * u.MHz,
      "3" : 0.230 * u.MHz,
      "4" : 0 * u.MHz,
      }

q_LO = {"1" : 6 * u.GHz, #4.95
      "2" : 5 * u.GHz,
      "3" : 5 * u.GHz,
      "4" : 5 * u.GHz,
      }

q_IF = {"1" : 50 * u.MHz + CrossKerr["1"], #212.734
      "2" : 7.99379 * u.MHz + CrossKerr["2"], #7.99
      "3" : 170.891 * u.MHz + CrossKerr["3"],
      "4" : -19.9 * u.MHz + CrossKerr["4"],
      }

rr_LO = {"1" : 7.36737 * u.GHz,  #7.36769
      "2" : 7.407946 * u.GHz, #7.40805
      "3" : 7.341449 * u.GHz,
      "4" : 7.439580 * u.GHz,
      }

rr_IF = {"1" : 20 * u.MHz,
      "2" : 20 * u.MHz,
      "3" : 20 * u.MHz,
      "4" : 20 * u.MHz,
      }

#======================Readout Parameters===========================================

tof = {"1" : 300,
      "2" : 300,
      "3" : 300,
      "4" : 300,
      }

ro_len_clk = {"1" : 500,
      "2" : 500,
      "3" : 500,
      "4" : 500,
      }

ro_amp = {"1" : 0.1,
      "2" : 0.13,
      "3" : 0.1,
      "4" : 0.1,
      }

integ_len_clk = {"1" : 500,
      "2" : 500,
      "3" : 500,
      "4" : 500,
      }

optimal_readout_phase = { "rr1" : 163*(np.pi/180),
                          "rr2" : 330.3*(-np.pi/180),
                          "rr3" : 156.7*(-np.pi/180),
                          "rr4" : 150*(np.pi/180),
                          }
#==================Control Parameters===============================================

pi_rise_grft_ns = 10
pi_len_ns = {"1" : 52,
        "2" : 52,
        "3" : 52,
        "4" : 52,
        }

piby2_rise_grft_ns = 10
piby2_len_ns = {"1" : 52,
        "2" : 52,
        "3" : 52,
        "4" : 52,
        }

cr_tail_ns = 16
cr_len_ns = {"c1t2" : 100,                 #CR gate length except 16ns rise and 16ns fall
        "2" : 100,
        "3" : 100,
        "4" : 100,
        }

# cr_amp = {"cr_c1t2" : 1.0, "cr_ac_c1t2" : -0.03}
# cr_phase = {"cr_c1t2" :  0.118118118118118, "cr_ac_c1t2" : 0.03403403403403403}

cr_amp = {"cr_c1t2" : 1.0, "cr_ac_c1t2" : 0.03} #-0.03
cr_phase = {"cr_c1t2" :  0.08708708708708708, "cr_ac_c1t2" : 0.03303303303303303}

calib_vals = {"q3" : {"amin" : 0.21, "amax" : 0.28, "da" : 0.0005, "n_pulses" : 7},
              "q2" : {"amin" : 0.75, "amax" : 1.0, "da" :0.001, "n_pulses" : 7}}

amp_scale = {"1" : {"X180": 0.340070035017, "Y180": 0.340070035017, "X90": 0.167371185592, "Y90": 0.167371185592 },
        "2" : {"X180": 0.855047523761881, "Y180": 0.8541470735367684, "X90":   0.4136568284142071, "Y90":   0.4137818909454727 },
        "3" : {"X180":  0.24757878939, "Y180": 0.24767633816908455, "X90": 0.12328289144572285, "Y90": 0.12328664332166082 },
        "4" : {"X180": 0.19783391, "Y180": 0.19783391, "X90": 0.09891695, "Y90": 0.09891695 },
        }

#==================Mixer Parameters===============================================
dac_mapping = {"q1" : [1,[5,6]], "q2" : [1,[3,4]], "q3" : [2,[1,2]], "q4" : [2,[3,4]],
               "rr1" : [1,[7,8]], "rr2" : [1,[9,10]], "rr3" : [2,[7,8]], "rr4" : [2,[9,10]],
               "cr_c1t2" : [1,[1,2]], }

### DC Offsets
with open('Calibrations/dc_offsets.json') as f:
    dc_offsets = json.load(f)

### List of Mixers
mixers = {}
for qe in qe_list:
    mixers[qe] = "mixer_" + qe

### IQ Imbalance Correction Matrices
with open('Calibrations/iq_imbalance.json') as f:
    iq_imbalance = json.load(f)

mixer_corrections = {}
for qe in qe_list:
    a = iq_imbalance[qe]["a"]
    p = iq_imbalance[qe]["p"]
    mixer_corrections[qe] = IQ_imbalance(a,p)


### ADC Offets
adc_offset = {"1" : {"1" : -0.0230, "2" : 0.1922 },
              "2" : {"1" : 0.0, "2" : 0.0},}

#======================== Temporary setup for checking a 4 qubit experiment using only two lines/quantum elements===================

if Line1_Line3:

    CrossKerr["1"] = CrossKerr["3"]

    q_LO["1"] = q_LO["3"]
    rr_LO["1"] = rr_LO["3"]

    q_IF["1"] = q_IF["3"]
    rr_IF["1"] = rr_IF["3"]

    ro_amp["1"] = ro_amp["3"]
    amp_scale["1"] = amp_scale["3"]

    optimal_readout_phase["rr1"] = optimal_readout_phase["rr3"]

if Line2_Line4:

    CrossKerr["2"] = CrossKerr["4"]

    q_LO["2"] = q_LO["4"]
    rr_LO["2"] = rr_LO["4"]

    q_IF["2"] = q_IF["4"]
    rr_IF["2"] = rr_IF["4"]

    ro_amp["2"] = ro_amp["4"]
    amp_scale["2"] = amp_scale["4"]

    optimal_readout_phase["rr2"] = optimal_readout_phase["rr4"]

CrossKerr["2"] = CrossKerr["1"]

#========================QM Config Starts Here=========================================

config = {

    "version": 1,

    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                1: {"offset": dc_offsets["con1"]["1"]},  # q1_I
                2: {"offset": dc_offsets["con1"]["2"]},  # q1_Q
                3: {"offset": dc_offsets["con1"]["3"]},  # q2_I
                4: {"offset": dc_offsets["con1"]["4"]},  # q2_Q
                5: {"offset": dc_offsets["con1"]["5"]},
                6: {"offset": dc_offsets["con1"]["6"]},
                7: {"offset": dc_offsets["con1"]["7"]},  # rr1_I
                8: {"offset": dc_offsets["con1"]["8"]},  # rr1_Q
                9: {"offset": dc_offsets["con1"]["9"]},  # rr2_I
                10: {"offset": dc_offsets["con1"]["10"]},  # rr2_Q
            },
            "digital_outputs": {},
            "analog_inputs": {
                1: {"offset": adc_offset["1"]["1"], 'gain_db': 14},  # adc q1
                2: {"offset": adc_offset["1"]["2"] , 'gain_db': 14},  # adc q2
            },
        },

        "con2": {
            "type": "opx1",
            "analog_outputs": {
                1: {"offset": dc_offsets["con2"]["1"]},  # q3_I
                2: {"offset": dc_offsets["con2"]["2"]},  # q3_Q
                3: {"offset": dc_offsets["con2"]["3"]},  # q4_I
                4: {"offset": dc_offsets["con2"]["4"]},  # q4_Q
                5: {"offset": dc_offsets["con2"]["5"]},
                6: {"offset": dc_offsets["con2"]["6"]},
                7: {"offset": dc_offsets["con2"]["7"]},  # rr3_I
                8: {"offset": dc_offsets["con2"]["8"]},  # rr3_Q
                9: {"offset": dc_offsets["con2"]["9"]},  # rr4_I
                10: {"offset": dc_offsets["con2"]["10"]},  # rr4_Q
            },
            "digital_outputs": {},
            "analog_inputs": {
                1: {"offset": adc_offset["2"]["1"], 'gain_db': 0},  # adc q3
                2: {"offset": adc_offset["2"]["2"], 'gain_db': 0},  # adc q4
            },
        },

    },

    "elements": {

        "q1": {
            "mixInputs": {
                "I": ("con1", 5),
                "Q": ("con1", 6),
                "lo_frequency": q_LO["1"],
                "mixer": mixers["q1"],
            },
            "intermediate_frequency": q_IF["1"],
            "operations": {
                "test_pulse": "q1_const_pulse_IQ",
                "const": "q1_const_pulse_IQ",
                "grft" : "q1_grft",
                "X180": "q1_X180",
                "X90": "q1_X90",
                "mX90": "q1_mX90",
                "Y180": "q1_Y180",
                "Y90": "q1_Y90",
                "mY90": "q1_mY90",
                "I": "zero",
            },

        },

        "rr1": {
            "mixInputs": {
                "I": ("con1", 7),
                "Q": ("con1", 8),
                "lo_frequency": rr_LO["1"],
                "mixer": mixers["rr1"],
            },
            "intermediate_frequency": rr_IF["1"],
            "outputs": {
                "out1": ("con1", 1),
                "out2": ("con1", 2),
            },
            "time_of_flight": tof["1"],
            "smearing": 0,
            "operations": {
                "const": "q1_const_pulse_IQ",
                "readout": "q1_ro_pulse",
            }
        },

        "q2": {
            "mixInputs": {
                "I": ("con1", 3),
                "Q": ("con1", 4),
                "lo_frequency": q_LO["2"],
                "mixer": mixers["q2"],
            },
            "intermediate_frequency": q_IF["2"],
            "operations": {
                "test_pulse": "q2_const_pulse_IQ",
                "const": "q2_const_pulse_IQ",
                "grft" : "q2_grft",
                "X180": "q2_X180",
                "X90": "q2_X90",
                "mX90": "q2_mX90",
                "Y180": "q2_Y180",
                "Y90": "q2_Y90",
                "mY90": "q2_mY90",
                "I": "zero",
            },

        },

        "rr2": {
            "mixInputs": {
                "I": ("con1", 9),
                "Q": ("con1", 10),
                "lo_frequency": rr_LO["2"],
                "mixer": mixers["rr2"],
            },
            "intermediate_frequency": rr_IF["2"],
            "outputs": {
                "out1": ("con1", 1),
                "out2": ("con1", 2),
            },
            "time_of_flight": tof["2"],
            "smearing": 0,
            "operations": {
                "const": "q2_const_pulse_IQ",
                "readout": "q2_ro_pulse",
            }
        },

        "cr_c1t2": {
                    "mixInputs": {
                        "I": ("con1", 1),
                        "Q": ("con1", 2),
                        "lo_frequency": q_LO["1"],
                        "mixer": mixers["cr_c1t2"],
                    },
                    "intermediate_frequency": q_IF["2"] ,
                    "operations": {
                        "test_pulse": "q2_const_pulse_IQ",
                        "grft" : "q1_grft",
                        "const": "c1t2_const_pulse_IQ",
                        "rise": "rise_pulse",
                        "fall": "fall_pulse",
                    },
        },

        "cr_ac_c1t2": {
            "mixInputs": {
                "I": ("con1", 3),
                "Q": ("con1", 4),
                "lo_frequency": q_LO["2"],
                "mixer": mixers["q2"],
            },
            "intermediate_frequency": q_IF["2"],
            "operations": {
                "I": "zero",
                "grft" : "q2_grft",
                "const": "c1t2_const_pulse_IQ",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
    },

    "pulses": {

        "zero": {
            "operation": "control",
            "length": pi_len_ns["1"],
            "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
        },

        "q1_const_pulse_IQ": {
            "operation": "control",
            "length": pi_len_ns["1"],
            "waveforms": {"I": "q1_const_wf", "Q": "zero_wf"},
        },

        "q1_grft": {
            "operation": "control",
            "length": pi_len_ns["1"] ,
            "waveforms": {"I": "q1_grft_wf", "Q": "zero_wf"},
        },

        "q1_X180": {
            "operation": "control",
            "length": pi_len_ns["1"],
            "waveforms": {"I": "q1_X180_I_wf", "Q": "zero_wf"},
        },

        "q1_Y180": {
            "operation": "control",
            "length": pi_len_ns["1"],
            "waveforms": {"I": "zero_wf", "Q": "q1_Y180_Q_wf"},
        },

        "q1_X90": {
                    "operation": "control",
                    "length": piby2_len_ns["1"],
                    "waveforms": {"I": "q1_X90_I_wf", "Q": "zero_wf"},
                },

        "q1_Y90": {
                    "operation": "control",
                    "length": piby2_len_ns["1"],
                    "waveforms": {"I": "zero_wf", "Q": "q1_Y90_Q_wf"},
                },
        "q1_mX90": {
                    "operation": "control",
                    "length": piby2_len_ns["1"],
                    "waveforms": {"I": "q1_mX90_I_wf", "Q": "zero_wf"},
                        },

        "q1_mY90": {
                    "operation": "control",
                    "length": piby2_len_ns["1"],
                    "waveforms": {"I": "zero_wf", "Q": "q1_mY90_Q_wf"},
                },

        "q1_ro_pulse": {
            "operation": "measurement",
            "length": ro_len_clk["1"] * 4,
            "waveforms": {"I": "q1_ro_wf", "Q": "zero_wf"},
            "integration_weights": {
                "integW_cos": "integW_cos_rr1",
                "integW_sin": "integW_sin_rr1",
                "integW_minus_sin": "integW_minus_sin_rr1"
            },
            "digital_marker": "ON",
        },

        "q2_const_pulse_IQ": {
            "operation": "control",
            "length": pi_len_ns["2"],
            "waveforms": {"I": "q2_const_wf", "Q": "zero_wf"},
        },

        "q2_grft": {
            "operation": "control",
            "length": pi_len_ns["2"],
            "waveforms": {"I": "q2_grft_wf", "Q": "zero_wf"},
        },

        "q2_X180": {
            "operation": "control",
            "length": pi_len_ns["2"],
            "waveforms": {"I": "q2_X180_I_wf", "Q": "zero_wf"},
        },

        "q2_Y180": {
            "operation": "control",
            "length": pi_len_ns["2"],
            "waveforms": {"I": "zero_wf", "Q": "q2_Y180_Q_wf"},
        },

        "q2_X90": {
            "operation": "control",
            "length": piby2_len_ns["2"],
            "waveforms": {"I": "q2_X90_I_wf", "Q": "zero_wf"},
        },

        "q2_Y90": {
            "operation": "control",
            "length": piby2_len_ns["2"],
            "waveforms": {"I": "zero_wf", "Q": "q2_Y90_Q_wf"},
        },
        "q2_mX90": {
            "operation": "control",
            "length": piby2_len_ns["2"],
            "waveforms": {"I": "q2_mX90_I_wf", "Q": "zero_wf"},
        },

        "q2_mY90": {
            "operation": "control",
            "length": piby2_len_ns["2"],
            "waveforms": {"I": "zero_wf", "Q": "q2_mY90_Q_wf"},
        },

        "q2_ro_pulse": {
            "operation": "measurement",
            "length": ro_len_clk["2"] * 4,
            "waveforms": {"I": "q2_ro_wf", "Q": "zero_wf"},
            "integration_weights": {
                "integW_cos": "integW_cos_rr2",
                "integW_sin": "integW_sin_rr2",
                "integW_minus_sin": "integW_minus_sin_rr2"
            },
            "digital_marker": "ON",
        },

        "c1t2_const_pulse_IQ": {
            "operation": "control",
            "length": cr_len_ns["c1t2"],
            "waveforms": {"I": "const_wf", "Q": "zero_wf"},
        },

        "rise_pulse" : {
            "operation": "control",
            "length": cr_tail_ns,
            "waveforms": {"I": "rise_wf", "Q": "zero_wf"},
        },

        "fall_pulse" : {
            "operation": "control",
            "length": cr_tail_ns,
            "waveforms": {"I": "fall_wf", "Q": "zero_wf"},
        }
    },

    "waveforms": {
        "zero_wf": {"type": "constant", "sample": 0.0},
        "const_wf": {"type": "constant", "sample": 0.4},
        #QUBIT1
        "q1_const_wf": {"type": "constant", "sample": 0.4},
        "q1_ro_wf": {"type": "constant", "sample": 0.4*ro_amp["1"]},
        "q1_grft_wf": {"type": "arbitrary", "samples": grft_arr_gen((pi_len_ns["1"],pi_rise_grft_ns))},
        "q1_X180_I_wf": {"type": "arbitrary",
                         "samples":  grft_arr_gen((pi_len_ns["1"],pi_rise_grft_ns),[amp_scale["1"]["X180"]])},
        "q1_Y180_Q_wf": {"type": "arbitrary",
                         "samples": grft_arr_gen((pi_len_ns["1"], pi_rise_grft_ns), [amp_scale["1"]["Y180"]])},
        "q1_X90_I_wf": {"type": "arbitrary",
                         "samples":  grft_arr_gen((pi_len_ns["1"],pi_rise_grft_ns),[amp_scale["1"]["X90"]])},
        "q1_Y90_Q_wf": {"type": "arbitrary",
                         "samples": grft_arr_gen((pi_len_ns["1"], pi_rise_grft_ns), [amp_scale["1"]["Y90"]])},
        "q1_mX90_I_wf": {"type": "arbitrary",
                         "samples":  grft_arr_gen((pi_len_ns["1"],pi_rise_grft_ns),[-amp_scale["1"]["X90"]])},
        "q1_mY90_Q_wf": {"type": "arbitrary",
                         "samples": grft_arr_gen((pi_len_ns["1"], pi_rise_grft_ns), [-amp_scale["1"]["Y90"]])},
        #QUBIT1
        "q2_const_wf": {"type": "constant", "sample": 0.4},
        "q2_ro_wf": {"type": "constant", "sample": 0.4*ro_amp["2"]},
        "q2_grft_wf": {"type": "arbitrary", "samples": grft_arr_gen((pi_len_ns["2"],pi_rise_grft_ns))},
        "q2_X180_I_wf": {"type": "arbitrary",
                         "samples":  grft_arr_gen((pi_len_ns["2"],pi_rise_grft_ns),[amp_scale["2"]["X180"]])},
        "q2_Y180_Q_wf": {"type": "arbitrary",
                         "samples": grft_arr_gen((pi_len_ns["2"], pi_rise_grft_ns), [amp_scale["2"]["Y180"]])},
        "q2_X90_I_wf": {"type": "arbitrary",
                         "samples":  grft_arr_gen((pi_len_ns["2"],pi_rise_grft_ns),[amp_scale["2"]["X90"]])},
        "q2_Y90_Q_wf": {"type": "arbitrary",
                         "samples": grft_arr_gen((pi_len_ns["2"], pi_rise_grft_ns), [amp_scale["2"]["Y90"]])},
        "q2_mX90_I_wf": {"type": "arbitrary",
                         "samples":  grft_arr_gen((pi_len_ns["2"],pi_rise_grft_ns),[-amp_scale["2"]["X90"]])},
        "q2_mY90_Q_wf": {"type": "arbitrary",
                         "samples": grft_arr_gen((pi_len_ns["2"], pi_rise_grft_ns), [-amp_scale["2"]["Y90"]])},

        "rise_wf": {"type": "arbitrary", "samples": rise_arr(cr_tail_ns)},
        "fall_wf": {"type": "arbitrary", "samples": fall_arr(cr_tail_ns)},
    },

    "digital_waveforms": {
        "ON": {"samples": [(1, 0)]}},

    "integration_weights": {
        "integW_cos_rr1": {
            "cosine": [(np.cos(optimal_readout_phase["rr1"]),  integ_len_clk["1"]*4)],
            "sine": [(-np.sin(optimal_readout_phase["rr1"]),  integ_len_clk["1"]*4)],
        },
        "integW_sin_rr1": {
            "cosine": [(np.sin(optimal_readout_phase["rr1"]),  integ_len_clk["1"]*4)],
            "sine": [(np.cos(optimal_readout_phase["rr1"]),  integ_len_clk["1"]*4)],
        },
        "integW_minus_sin_rr1": {
            "cosine": [(-np.sin(optimal_readout_phase["rr1"]),  integ_len_clk["1"]*4)],
            "sine": [(-np.cos(optimal_readout_phase["rr1"]),  integ_len_clk["1"]*4)],
        },

        "integW_cos_rr2": {
            "cosine": [(np.cos(optimal_readout_phase["rr2"]), integ_len_clk["2"] * 4)],
            "sine": [(-np.sin(optimal_readout_phase["rr2"]), integ_len_clk["2"] * 4)],
        },
        "integW_sin_rr2": {
            "cosine": [(np.sin(optimal_readout_phase["rr2"]), integ_len_clk["2"] * 4)],
            "sine": [(np.cos(optimal_readout_phase["rr2"]), integ_len_clk["2"] * 4)],
        },
        "integW_minus_sin_rr2": {
            "cosine": [(-np.sin(optimal_readout_phase["rr2"]), integ_len_clk["2"] * 4)],
            "sine": [(-np.cos(optimal_readout_phase["rr2"]), integ_len_clk["2"] * 4)],
        }
    },

    "mixers": {
        "mixer_q1": [{"intermediate_frequency": q_IF["1"], "lo_frequency": q_LO["1"], "correction": mixer_corrections["q1"]}],
        "mixer_rr1": [{"intermediate_frequency": rr_IF["1"], "lo_frequency": rr_LO["1"], "correction": mixer_corrections["rr1"]}],
        "mixer_q2": [{"intermediate_frequency": q_IF["2"], "lo_frequency": q_LO["2"], "correction": mixer_corrections["q2"]}],
        "mixer_rr2": [{"intermediate_frequency": rr_IF["2"], "lo_frequency": rr_LO["2"], "correction": mixer_corrections["rr2"]}],
        "mixer_cr_c1t2": [{"intermediate_frequency": q_IF["2"], "lo_frequency": q_LO["1"], "correction": mixer_corrections["cr_c1t2"]}],
    }
}
