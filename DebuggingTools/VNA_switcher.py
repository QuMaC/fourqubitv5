from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.instrument_helperfunctions import *
import pyvisa as visa
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

q_no = 6

turn_off = 0

# test_name = r'\Cu_cavity_'
# if q_no <= 6:
#     test_name = fr"\Ring{qubit_to_ring_map[q_no][0]}_Input{qubit_to_ring_map[q_no][1]}Output{qubit_to_ring_map[q_no][2]}"

check_USB_switch_status()

switch_to_vna(keyer(f"q{q_no}", dac_mapping))

# ip = "TCPIP0::192.168.0.27::inst0::INSTR"
# rm = visa.ResourceManager()
# kna = rm.open_resource(ip)

# f_data = np.array(kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))

# # g_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
#
#
# ######################
#
# plt.figure()
# plt.plot(f_data, g_data1, label = 'Ch 1')
# plt.plot(f_data, g_data2, label = 'Ch 2')
# plt.plot(f_data, g_data3, label = 'Ch 3')
# plt.plot(f_data, g_data4, label = 'Ch 4')
# plt.grid()
# plt.legend()
