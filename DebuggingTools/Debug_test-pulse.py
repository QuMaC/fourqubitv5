import time
from qm.qua import *
from qm import SimulationConfig
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from Configuration_Files.auto_mixer_tools_visa import KeysightXSeries
import numpy as np
from scipy.optimize import curve_fit

simulate = False
change_SA_settings = True

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
qm = qmm.open_qm(config)
address = "TCPIP0::192.168.0.117::inst0::INSTR"
calib = KeysightXSeries(address, qm)

qe_freq = {}
for i in range(1, 9):
    qe_freq[f"q{i}"] = [q_LO[f"{i}"], q_IF[f"{i}"], f"mixer_q{i}"]
    qe_freq[f"rr{i}"] = [rr_LO[f"{i}"], rr_IF[f"{i}"], f"mixer_rr{i}"]

for c_no in control_qubits:
    for t_no in connectivity[c_no]:
        qe_freq[f"cr_c{c_no}t{t_no}"] = [q_LO[f"{c_no}"], q_IF[f"{t_no}"], f"mixer_cr_c{c_no}t{t_no}"]
        qe_freq[f"cr_ac_c{c_no}t{t_no}"] = [q_LO[f"{t_no}"], q_IF[f"{t_no}"], f"mixer_q{t_no}"]

qe = "stark_6"
qe = "q2"
# qe = "cr_c1t2"
if 'stark' in qe:
    qe = f'q{qe[-1]}'
    qe_LO, qe_IF, mixer = qe_freq[qe]
    qe_LO = stark_LO[qe[-1]]
    qe_IF = stark_IF[qe[-1]]
    qe = f'stark_{qe[-1]}'
else:
    qe_LO, qe_IF, mixer = qe_freq[qe]

center_freq = qe_LO + qe_IF  # rr_LO
span = 50
calib.set_marker_freq(1, center_freq)
if change_SA_settings:
    calib.set_bandwidth(5)
    calib.set_sweep_points(1001)

    calib.set_center_freq(center_freq)
    calib.set_span(span)
    calib.active_marker(1)
    calib.set_marker_freq(1, center_freq)
###################
# The QUA program #
###################

try:
    bulk_switch(qe=keyer(qe, dac_mapping), ip=sw_ip, switches=switches)
except:
    print('Switch not accessible for some reason')

with program() as mixtest:
    n = declare(int)
    with infinite_loop_():
        # reset_frame(qe)
        # play("readout", qe)
        # update_frequency(qe, q_IF[qe[-1]] + 1*1e6)
        play("const" * amp(1), qe)

if simulate:
    qmm = QuantumMachinesManager()
    job = qmm.simulate(config, mixtest, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con3.plot()
    # samples.con2.plot()

    raise Halted()

a_i, a_q = 0.000, 0.000  # NB010


def change_dc_offset(qe, a_i, a_q):
    qm.set_output_dc_offset_by_element(qe, "I", a_i)
    qm.set_output_dc_offset_by_element(qe, "Q", a_q)


# qm.set_mixer_correction(mixer, int(qe_IF), int(qe_LO), IQ_imbalance(0.1748, 0.101))  #NB003
job = qm.execute(mixtest)
time.sleep(2)
print("Upconverted sideband power is {0} dBm".format(calib.query_marker(1)))
