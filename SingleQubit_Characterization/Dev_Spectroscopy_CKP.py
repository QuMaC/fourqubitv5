from qm import LoopbackInterface, SimulationConfig
from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from scipy import signal as sgn
# import statistics as st
import pandas as pd

save_data = False

###################
# The QUA program #
###################
q_no = 1
qe = f"q{q_no}"
rr = f"rr{q_no}"
# rr="rr1"
out = adc_mapping[rr]

fq_LO = q_LO[qe[-1]]
fr_LO = rr_LO[qe[-1]]

fq_min = q_IF[f"{q_no}"] - 20 * u.MHz #-91.8
fq_max = q_IF[f"{q_no}"] + 10 * u.MHz # -91.4
dfq = 0.5 * u.MHz

rr_IF_val = rr_IF[f"{q_no}"]
q_IF_val = q_IF[f"{q_no}"]
frr_min = rr_IF[f"{q_no}"] - 10 * u.MHz #-91.8
frr_max = rr_IF[f"{q_no}"] + 10 * u.MHz # -91.4
dfrr = 0.1 * u.MHz

q_amp = 0.03
a_stark = 0.8
stark_len = 5000#20000
pi_len = pi_len_ns[f"{q_no}"]
a_rr = 1.0  #Keep 1.0 for measurement amplitude as specified in config ; Use to scale that amplitude
rep_rate_clk = 250000

freqs_q = np.arange(fq_min, fq_max, dfq)
freqs_rr = np.arange(frr_min, frr_max, dfrr)

def CKP_pulse_seq(I, Q, I_st, Q_st, init_pulse="I"):

    wait(rep_rate_clk, qe)
    play(init_pulse, qe)
    update_frequency(qe, fq)
    update_frequency(rr, frr)
    align(qe, rr)
    play("readout" * amp(a_stark), rr, duration=stark_len)
    wait(stark_len // 8, qe)
    play_X180(qe)
    align(qe, rr)
    update_frequency(rr, rr_IF_val)
    update_frequency(qe, q_IF_val)
    wait(250, rr)
    measure("readout" * amp(a_rr), rr, None,
            demod.full("integW_cos", I, out),
            demod.full("integW_minus_sin", Q, out))
    save(I, I_st)
    save(Q, Q_st)


with program() as qubit_spec:

    n = declare(int)
    I = declare(fixed)
    Q = declare(fixed)
    I0_st = declare_stream()
    Q0_st = declare_stream()
    I1_st = declare_stream()
    Q1_st = declare_stream()
    fq = declare(int)
    frr = declare(int)

    with for_(n, 0, n < 10000, n + 1):
        with for_(fq, fq_min, fq < fq_max, fq + dfq):
            with for_(frr, frr_min, frr < frr_max, frr + dfrr):

                CKP_pulse_seq(I, Q, I0_st, Q0_st, init_pulse="I")
                CKP_pulse_seq(I, Q, I1_st, Q1_st, init_pulse="X180")

    with stream_processing():
        I0_st.buffer(len(freqs_rr)).buffer(len(freqs_q)).average().save('I0')
        Q0_st.buffer(len(freqs_rr)).buffer(len(freqs_q)).average().save('Q0')
        I1_st.buffer(len(freqs_rr)).buffer(len(freqs_q)).average().save('I1')
        Q1_st.buffer(len(freqs_rr)).buffer(len(freqs_q)).average().save('Q1')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
simulate = False
if simulate:
    simulation_config = SimulationConfig(
        duration=200000,
        simulation_interface=LoopbackInterface([("con1", 9, "con1", 1), ("con1", 10, "con1", 2)]))
    job = qmm.simulate(config, qubit_spec, simulation_config)
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()
    raise Halted()

#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(qubit_spec)
res_handles = job.result_handles
I0_handle = job.result_handles.get("I0")
Q0_handle = job.result_handles.get("Q0")
I1_handle = job.result_handles.get("I1")
Q1_handle = job.result_handles.get("Q1")
#job.result_handles.wait_for_all_values()

plt.figure()
plt.title("Qubit Spectroscopy")
I0_handle.wait_for_values(1)
Q0_handle.wait_for_values(1)
I1_handle.wait_for_values(1)
Q1_handle.wait_for_values(1)
while res_handles.is_processing():

    I0 = I0_handle.fetch_all()
    I1 = I1_handle.fetch_all()

    plt.cla()
    plt.pcolor(1e-6*(freqs_rr), 1e-6*(freqs_q), I0, label="I0")
    plt.title("CKP")
    plt.ylabel("Qubit Frequency")
    plt.xlabel("Readout Frequency")
    # plt.plot(1e-6*(freqs), Q, label="Q")
    plt.tight_layout()
    plt.pause(0.1)

I0 = I0_handle.fetch_all()
I1 = I1_handle.fetch_all()

############
# analysis #
############

# max_index = pd.Series(I).idxmax()
# print("Maximum Index position:", max_index)

freqs_q_GHz = 1e-9*(fq_LO + freqs_q)
freqs_rr_GHz = 1e-9*(fr_LO + freqs_rr)


data_I0 = np.transpose(I0)
data_I1 = np.transpose(I1)
data_x = np.transpose(freqs_rr_GHz)
data_y = np.transpose(freqs_q_GHz)

if save_data :

    file_saver_(I0, file_name=__file__, suffix= qe + "_init0", master_folder= ExpName, time_stamp=False)
    file_saver_(I1, file_name=__file__, suffix=qe + "_init1", master_folder=ExpName, time_stamp=False)
    file_saver_(data_x, file_name=__file__, suffix=qe + "_xaxis", master_folder=ExpName,
                header_string="Frequency (GHz), Frequency (GHz)", time_stamp=False)
    file_saver_(data_y, file_name=__file__, suffix=qe + "_yaxis", master_folder=ExpName,
                header_string="Frequency (GHz), Frequency (GHz)", time_stamp=False)
    # file_saver_(data, file_name=__file__, suffix=qe+f"vol_{flux}V", master_folder=ExpName, header_string="Frequency (GHz), I, Q")