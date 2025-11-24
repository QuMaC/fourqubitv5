import json
from Helper_Functions.helper_functionsv2 import *
from qualang_tools.units import unit

path_global = r"D:\QUA\Master_Scripts\fourqubitv5 (Under Construction)"

u = unit()
n_qubits = 8
connectivity = {1: [2, 4, 6],
                3: [2, 4, 6],
                5: [2, 4, 6]
                }

control_qubits = list(connectivity.keys())

qe_list = [f"q{i}" for i in range(1, n_qubits+1)]
for i in range(1, n_qubits+1):
    qe_list.append(f"rr{i}")
    qe_list.append(f"q12_{i}")
    qe_list.append(f"stark_{i}")

for c_no in control_qubits:
    for t_no in connectivity[c_no]:
        qe_list.append(f"cr_c{c_no}t{t_no}")
        qe_list.append(f"cr_ac_c{c_no}t{t_no}")

pi_rise_grft_ns = 10
piby2_rise_grft_ns = 10
cr_tail_ns = 16


### Filter details
num_segment = 100
samples_per_chunk = 20
chunks_per_window = 3
arr_size = 10
acc_data_width = 8



# Cross-Kerr shifts dictionary
with open(path_global + '/Configuration_Files/System_Parameters/CrossKerr.json') as f:
    CrossKerr = json.load(f)

for q_i in CrossKerr:
    CrossKerr[q_i] = CrossKerr[q_i] * u.MHz

# Qubit LO dictionary
with open(path_global + '/Configuration_Files/System_Parameters/q_LO.json') as f:
    q_LO = json.load(f)

for q_i in q_LO:
    q_LO[q_i] = q_LO[q_i] * u.GHz

# Qubit IF dictionary
with open(path_global + '/Configuration_Files/System_Parameters/q_IF.json') as f:
    q_IF = json.load(f)

for q_i in q_IF:
    q_IF[q_i] = q_IF[q_i] * u.MHz + CrossKerr[q_i]

# Readout LO dictionary
with open(path_global + '/Configuration_Files/System_Parameters/rr_LO.json') as f:
    rr_LO = json.load(f)

for rr_i in rr_LO:
    rr_LO[rr_i] = rr_LO[rr_i] * u.GHz

# Readout IF dictionary
with open(path_global + '/Configuration_Files/System_Parameters/rr_IF.json') as f:
    rr_IF = json.load(f)

for rr_i in rr_IF:
    rr_IF[rr_i] = rr_IF[rr_i] * u.MHz

# ======================Readout Parameters===========================================

with open(path_global + '/Configuration_Files/Readout_Settings/tof.json') as f:
    tof = json.load(f)

with open(path_global + '/Configuration_Files/Readout_Settings/ro_amp.json') as f:
    ro_amp = json.load(f)

with open(path_global + '/Configuration_Files/Readout_Settings/ro_len_clk.json') as f:
    ro_len_clk = json.load(f)

with open(path_global + '/Configuration_Files/Readout_Settings/integ_len_clk.json') as f:
    integ_len_clk = json.load(f)

with open(path_global + '/Configuration_Files/Readout_Settings/optimal_readout_phase.json') as f:
    optimal_readout_phase = json.load(f)

with open(path_global + '/Configuration_Files/Readout_Settings/max_signal_section.json') as f:
    max_signal_section = json.load(f)

for rr_i in optimal_readout_phase.keys():
    optimal_readout_phase[rr_i] = optimal_readout_phase[rr_i]*(np.pi/180)

with open(path_global + '/Configuration_Files/Readout_Settings/demarcations.json') as f:
    demarcations = json.load(f)

with open(path_global + '/Configuration_Files/Readout_Settings/elec_delay_ns.json') as f:
    elec_delay_ns = json.load(f)

with open(path_global + '/Configuration_Files/Readout_Settings/phase_offset_rad.json') as f:
    phase_offset_rad = json.load(f)

# ==================Control Parameters===============================================

with open(path_global + '/Configuration_Files/Pulse_Calibrations/pi_len_ns.json') as f:
    pi_len_ns = json.load(f)


with open(path_global + '/Configuration_Files/Pulse_Calibrations/piby2_len_ns.json') as f:
    piby2_len_ns = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/calib_vals.json') as f:
    calib_vals = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/amp_scale.json') as f:
    amp_scale = json.load(f)


with open(path_global + '/Configuration_Files/Pulse_Calibrations/cr_len_ns.json') as f:
    cr_len_ns = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/cr_amp.json') as f:
    cr_amp = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/cr_phase.json') as f:
    cr_phase = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/cr_control_phase_correction.json') as f:
    cr_control_phase = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/cr_target_phase_correction.json') as f:
    cr_target_phase = json.load(f)

##
with open(path_global + '/Configuration_Files/Pulse_Calibrations/drag_dict.json') as f:
    drag_dict = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/stark_LO.json') as f:
    stark_LO = json.load(f)

for rr_i in stark_LO:
    stark_LO[rr_i] = stark_LO[rr_i] * u.GHz

# with open('./Pulse_Calibrations/amp_scale_rcp.json') as f:
#     amp_scale_rcp = json.load(f)
#
# with open('./Pulse_Calibrations/drag_dict_rcp.json') as f:
#     drag_dict_rcp = json.load(f)
##

# =================== Dictionaries for 1-2 transition =================================

with open(path_global + '/Configuration_Files/System_Parameters/q12_IF.json') as f:
    q12_IF = json.load(f)

for q_i in q12_IF:
    q12_IF[q_i] = q12_IF[q_i] * u.MHz

with open(path_global + '/Configuration_Files/Pulse_Calibrations/pi_12_len_ns.json') as f:
    pi_12_len_ns = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/piby2_12_len_ns.json') as f:
    piby2_12_len_ns = json.load(f)

with open(path_global + '/Configuration_Files/Pulse_Calibrations/amp_12_scale.json') as f:
    amp_12_scale = json.load(f)

# =================== Dictionaries for stark tones =================================
with open(path_global + '/Configuration_Files/Pulse_Calibrations/stark_IF.json') as f:
    stark_IF = json.load(f)
for q_i in stark_IF:
    stark_IF[q_i] = stark_IF[q_i] * u.MHz

with open(path_global + '/Configuration_Files/Pulse_Calibrations/stark_amp.json') as f:
    stark_amp = json.load(f)

# ==================Mixer Parameters ===============================================
# =================== DC Offsets ===============================================
with open(path_global + '/Configuration_Files/Calibrations/dc_offsets.json') as f:
    dc_offsets = json.load(f)

# ================ List of Mixers ===============================================
mixers = {}
for qe in qe_list:
    mixers[qe] = "mixer_" + qe

# ================ IQ Imbalance Correction Matrices ===============================================
with open(path_global + '/Configuration_Files/Calibrations/iq_imbalance.json') as f:
    iq_imbalance = json.load(f)

mixer_corrections = {}
for qe in qe_list:
    a = iq_imbalance[qe]["a"]
    p = iq_imbalance[qe]["p"]
    mixer_corrections[qe] = IQ_imbalance(a, p)

# ============== ADC Offets ===============================================
with open(path_global + '/Configuration_Files/Calibrations/adc_offsets.json') as f:
    adc_offsets = json.load(f)

# ============== ADC Offets ===============================================
with open(path_global + '/Configuration_Files/Calibrations/gain_dict.json') as f:
    gain_dict = json.load(f)