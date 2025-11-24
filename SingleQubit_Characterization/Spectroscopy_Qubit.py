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

save_data = True
simulate = False
###################
# The QUA program #
##################
q_no = 4
qe = f"q{q_no}"
rr = f"rr{q_no}"
# rr="rr1"
out = adc_mapping[rr]

f_LO = q_LO[qe[-1]]

f_min = 260 * u.MHz#38.5 * u.MHz#132 * u.MHz #129.13 12.171
f_max = 270 * u.MHz#132.5 * u.MHz # -91.4

df = 0.01 * u.MHz
q_amp = 0.0005

a_rr = 1.0  #Keep 1.0 for measurement amplitude as specified in config ; Use to scale that amplitude
freqs = np.arange(f_min, f_max, df)

wait_time = 20000
pulse_duration = 20000
if simulate:
    wait_time = 100
    pulse_duration = 500

with program() as qubit_spec:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    f = declare(int)

    # play("stark", f"stark_{q_no}")
    # wait(10000, f"stark_{q_no}")
    with for_(n, 0, n < 10000, n + 1):
        with for_(f, f_min, f < f_max, f + df):
            # reset_phase(rr)         # added for testing remove asap
            wait(wait_time, qe)
            update_frequency(qe, f)
            play("const"*amp(q_amp), qe, duration=pulse_duration)
            align(rr, qe)
            measure("readout", rr, None,
                    demod.full("integW_cos", I, out),
                    demod.full("integW_minus_sin", Q, out))
            save(I, I_st)
            save(Q, Q_st)
    # align(rr, f"stark_{q_no}")
    # ramp_to_zero(f"stark_{q_no}")

    with stream_processing():
        I_st.buffer(len(freqs)).average().save('I')
        Q_st.buffer(len(freqs)).average().save('Q')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################

if simulate:
    # simulation_config = SimulationConfig(
    #     duration=200000,
    #     simulation_interface=LoopbackInterface([("con1", 9, "con1", 1), ("con1", 10, "con1", 2)]))
    job = qmm.simulate(config, qubit_spec, SimulationConfig(int(10000)))
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
I_handle = job.result_handles.get("I")
Q_handle = job.result_handles.get("Q")
#job.result_handles.wait_for_all_values()

plt.figure()
plt.title(f"Qubit Spectroscopy : Q{q_no}")
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)

freqs_GHz = 1e-9*(f_LO + freqs)
freqs_GHz = freqs
while res_handles.is_processing():

    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    sig = I + 1j * Q
    plt.clf()
    # plt.plot(1e-6*(freqs), np.abs(sig), label='mag')
    plt.plot(1e-6*(freqs_GHz), I, label="I")
    plt.title("Qubit Spectroscopy")
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Quadrature Amplitude [a.u.]")
    # plt.plot(1e-6*(freqs_GHz), Q, label="Q")
    plt.grid()
    plt.legend()
    plt.pause(1)

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

############
# analysis #
############

max_index = pd.Series(I).idxmax()
print("Maximum Index position:",max_index)



q_freq = freqs[max_index]
# q_fwhm = max(widths) * df * 1e-9  # in GHz

print(f'The qubit frequency is {q_freq} GHz.')
# print(f'The FWHM of the qubit peak is {1e3 * q_fwhm} MHz.')

flux=-36 #temp variable

# freqs = 1e-9*(f_LO + freqs)
plt.figure()
plt.title('Qubit spectroscopy')
# plt.plot(freqs, I)
plt.plot(freqs_GHz, Q)
plt.xlabel("Frequency (GHz)")
plt.grid()
plt.show()

data = np.transpose([freqs_GHz, I,Q])

if save_data :
    file_saver_(data, file_name=__file__, suffix= qe, master_folder= ExpName,header_string="Frequency (GHz), I, Q")
    # file_saver_(data, file_name=__file__, suffix=qe+f"vol_{flux}V", master_folder=ExpName, header_string="Frequency (GHz), I, Q")
