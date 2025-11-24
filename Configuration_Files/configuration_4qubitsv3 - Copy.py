from Configuration_Files.config_builder import *
from Configuration_Files.config_dictionaries import *
import matplotlib
from Helper_Functions.instrumentlib import RhodeandSchwarz_SGS100A


def setup_RF_Source(rf_ip, rf_f, rf_p):
    rf = RhodeandSchwarz_SGS100A(rf_ip)
    rf.set_freq_Hz(rf_f)
    rf.set_power_dB(rf_p)
    rf.output_on()
    rf.close_connection()


u = unit()
matplotlib.use('Qt5Agg')

ExpName = r"/2025-05-17 Ringv1-INDIQTa08,02-6Qubits-Shifted02"
qm_ip = "192.168.0.106"
cluster_name = "Proteox_main"
# cluster_name = "BLUEFORS setup"

if cluster_name == "Proteox_main":
    path = r"D:\Experiments"
else:
    path = r"D:\BLUEFORS setup"

TOF_testing = False
initialize_RF_sources = False

qubit_to_ring_map = {1: [7, 1, 25],
                     2: [9, 2, 26],
                     3: [11, 3, 27],
                     4: [1, 4, 28],
                     5: [3, 5, 29],
                     6: [5, 6, 30],
                     }

sw_ip = '192.168.0.118:80'
sl_to_fridge = '11509250001'
sl_from_fridge = '11509250002'
sl_5_6 = '11502170036'

sl_list = [sl_from_fridge, sl_to_fridge, sl_5_6]

vna_opx_switch_map = {'112': {sl_list[0]: {'A': 0, 'D': 1, 'C': 0}, sl_list[1]: {'A': 0, 'D': 1, 'C': 0}, sl_list[2]: {'B': 1}},
                      '134': {sl_list[0]: {'A': 1, 'D': 1, 'C': 0}, sl_list[1]: {'A': 1, 'D': 1, 'C': 0}, sl_list[2]: {'B': 1}},
                      '212': {sl_list[0]: {'B': 0, 'D': 0, 'C': 0}, sl_list[1]: {'B': 0, 'D': 0, 'C': 0}, sl_list[2]: {'B': 1}},
                      '234': {sl_list[0]: {'B': 1, 'D': 0, 'C': 0}, sl_list[1]: {'B': 1, 'D': 0, 'C': 0}, sl_list[2]: {'B': 1}},
                      '312': {sl_list[0]: {'C': 1}, sl_list[1]: {'C': 1}, sl_list[2]: {'A': 1, 'B': 0, 'C': 0, 'D': 1}},
                      '334': {sl_list[0]: {'C': 1}, sl_list[1]: {'C': 1}, sl_list[2]: {'A': 0, 'B': 0, 'C': 0, 'D': 0}},
                      'off': {sl_list[0]: {'C': 1}, sl_list[1]: {'C': 1}, sl_list[2]: {'A': 0, 'B': 1, 'C': 1, 'D': 0}},
                      }

switches = {"112": [0, 0, 0, 0],
            "156": [0, 0, 0, 0],
            "134": [1, 0, 0, 0],
            "1910": [1, 0, 0, 0],
            "212": [0, 0, 1, 0],
            "278": [0, 0, 1, 0],
            "234": [0, 1, 1, 0],
            "2910": [0, 1, 1, 0],
            "312": [0, 0, 0, 1, 0],
            "378": [0, 0, 0, 1, 0],
            "334": [0, 0, 0, 1, 1],
            "3910": [0, 0, 0, 1, 1],
            }

# ====================== DAC, ADC Mapping ========================================
if cluster_name == 'Proteox_main':
    dac_mapping = {"q1": [1, [1, 2]], "q2": [1, [3, 4]], "q3": [2, [2, 1]], "q4": [2, [4, 3]],
                   "q5": [3, [1, 2]], "q6": [3, [3, 4]], "q7": [3, [1, 2]], "q8": [3, [1, 2]],
                   "rr1": [1, [5, 6]], "rr2": [1, [9, 10]], "rr3": [2, [8, 7]], "rr4": [2, [9, 10]],
                   "rr5": [3, [7, 8]], "rr6": [3, [9, 10]], "rr7": [3, [7, 8]], "rr8": [3, [7, 8]],
                   }

# if cluster_name == 'Proteox_main':      # temp
#     dac_mapping = {"q1": [3, [1, 2]], "q2": [3, [3, 4]], "q3": [3, [1, 2]], "q4": [3, [3, 4]], "q5": [3, [1, 2]],
#                    "q6": [3, [3, 4]], "q7": [3, [1, 2]], "q8": [3, [1, 2]],
#                    "rr1": [3, [7, 8]], "rr2": [3, [9, 10]], "rr3": [3, [7, 8]], "rr4": [3, [9, 10]], "rr5": [3, [7, 8]],
#                    "rr6": [3, [9, 10]], "rr7": [3, [7, 8]], "rr8": [3, [7, 8]],
#                    "cr_c2t1": [1, [3, 4]], "cr_c4t1": [2, [3, 4]], "cr_c2t3": [1, [3, 4]], "cr_c4t3": [2, [3, 4]]}
else:
    dac_mapping = {"q1": [3, [1, 2]], "q2": [3, [3, 4]], "q3": [1, [1, 2]], "q4": [1, [3, 4]],
                   "rr1": [3, [7, 8]], "rr2": [3, [9, 10]], "rr3": [1, [7, 8]], "rr4": [1, [9, 10]],
                   }

if cluster_name == 'Proteox_main':
    adc_mapping = {"rr1": "out1", "rr2": "out2", "rr3": "out1", "rr4": "out2", "rr5": "out1", "rr6": "out2",
                   "rr7": "out1", "rr8": "out1"}
    # adc_mapping = {"rr1": "out1", "rr2": "out2", "rr3": "out1", "rr4": "out1", "rr5": "out1", "rr6": "out2"}
else:
    adc_mapping = {"rr1": "out1", "rr2": "out2", "rr3": "out1", "rr4": "out2", "rr5": "out1", "rr6": "out2"}

# For TOF Testing
if TOF_testing:

    from Readout_Settings.tof_calib_settings import rr_IF, ro_amp

    for rr_i in rr_IF:
        rr_IF[rr_i] = rr_IF[rr_i] * u.MHz

# ======================= Setting up RF sources with above parameters =========================
# LO_IP_dict = {"rr_1": "TCPIP0::192.168.0.105::inst0::INSTR",
#               "rr_2": "TCPIP0::192.168.0.114::inst0::INSTR",
#               'rf_rr34_ip': "TCPIP0::192.168.0.200::inst0::INSTR",
#               'rf_q12_ip': "TCPIP0::192.168.0.104::inst0::INSTR",
#               'rf_q34_ip': "TCPIP0::192.168.0.103::inst0::INSTR",
#               }

if cluster_name == 'Proteox_main':
    LO_IP_dict = {'q_LO': {'1': "TCPIP0::192.168.0.104::inst0::INSTR",
                           '2': "TCPIP0::192.168.0.111::inst0::INSTR",
                           '3': "TCPIP0::192.168.0.113::inst0::INSTR",
                           },
                  'rr_LO': {'1': "TCPIP0::192.168.0.105::inst0::INSTR",
                            '2': "TCPIP0::192.168.0.114::inst0::INSTR",
                            '3': "TCPIP0::192.168.0.200::inst0::INSTR",
                            }
                  }
else:
    LO_IP_dict = {'q_LO': {'1': "TCPIP0::192.168.0.109::inst0::INSTR",
                           },
                  'rr_LO': {'1': "TCPIP0::192.168.0.200::inst0::INSTR",
                            }
                  }

rr_LO_dBm = 21
q_LO_dBm = 17

# if initialize_RF_sources:  ## Modify for all 7 qubits
#     setup_RF_Source(LO_IP_dict['rf_rr1_ip'], rr_LO["1"], rr_LO_dBm)
#     setup_RF_Source(LO_IP_dict['rf_rr2_ip'], rr_LO["2"], rr_LO_dBm)
#     setup_RF_Source(LO_IP_dict['rf_rr34_ip'], rr_LO["3"], rr_LO_dBm)
#     setup_RF_Source(LO_IP_dict['rf_q12_ip'], q_LO["1"], q_LO_dBm)

# ======================== QM Config Starts Here =========================================

config = {

    "version": 1,
}

if cluster_name == 'Proteox_main':
    n_controllers = 3
    n_qubits = 8
else:
    n_controllers = 1
    n_qubits = 2

for i in range(1, n_controllers + 1):
    config = config_add_controller(config, i, dc_offsets, adc_offsets, gain_dict)

config = config_add_common_elements(config)

q_anh = {}

for keys, vals in q_LO.items():
    q_anh[keys] = q12_IF[str(i)] - q_IF[str(i)]

for i in range(1, n_qubits + 1):
    q_no = i
    rr_no = i

    config = config_add_elements_q_rr(config, q_no, rr_no, dac_mapping, q_LO, q_IF, rr_LO, rr_IF, pi_len_ns,
                                      piby2_len_ns, pi_rise_grft_ns, amp_scale,
                                      mixers, mixer_corrections, ro_amp, ro_len_clk, tof, integ_len_clk,
                                      optimal_readout_phase, smearing=0)

    config = config_add_drag_grft(config, q_no, q_anh, pi_len_ns,
                                  piby2_len_ns, pi_rise_grft_ns, amp_scale, drag_dict)

config = config_add_rise_fall(config, cr_tail_ns)

# Check CR config elements
cr_elems = []
for c_no in control_qubits:
    for t_no in connectivity[c_no]:
        cr_elems.append(f"cr_c{c_no}t{t_no}")

if cluster_name == 'Proteox_main':
    for c_no in control_qubits:
        for t_no in connectivity[c_no]:
            dac_mapping[f"cr_c{c_no}t{t_no}"] = dac_mapping[f"q{c_no}"]
            config = config_add_crgate(config, c_no, t_no, dac_mapping, q_LO, q_IF, mixers, mixer_corrections)


# Add quantum elements for 1-2 transition
for i in range(1, n_qubits + 1):
    q_no = i
    config = config_add_q12(config, q_no, dac_mapping, q_LO, q12_IF,
                            pi_12_len_ns, piby2_12_len_ns, pi_rise_grft_ns, amp_12_scale, mixers, mixer_corrections)

# Add quantum elements for stark tone
for i in range(1, n_qubits + 1):
    q_no = i
    config = config_add_tonestark(config, q_no, dac_mapping, q_LO, q_IF, stark_IF, stark_amp, mixers, mixer_corrections)
