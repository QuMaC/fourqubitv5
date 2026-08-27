from qm import LoopbackInterface, SimulationConfig
from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from Helper_Functions.macros import *
save_data = False

###################
# The QUA program #
###################
q_no = 3
rr_no = q_no
qe = f"q{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]

f_LO = q_LO[qe[-1]]
f_min = -400* u.MHz
f_max = 400 * u.MHz
df = 0.5 * u.MHz
q_amp = 0.12
rr_amp = 0.35
integ_len = 1000
navgs = 520

freqs = np.arange(f_min, f_max, df)


update_config_rr(config, q_no, rr_no, rr_amp, integ_len)

with program() as qubit_spec:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    f = declare(int)

    with for_(n, 0, n < navgs, n + 1):
        with for_(f, f_min, f < f_max, f + df):
            wait(20000, qe, rr)
            # reset_phase(rr)
            update_frequency(qe, f)
            play("const"*amp(q_amp), qe, duration=4*integ_len)
            measure("readout", rr, None,
                    demod.full("integW_cos", I, out),
                    demod.full("integW_minus_sin", Q, out))
            save(I, I_st)
            save(Q, Q_st)
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
freqs_abs_GHz = 1e-9*(f_LO + freqs)
qm = qmm.open_qm(config)
job = qm.execute(qubit_spec)
res_handles = job.result_handles
I_handle = job.result_handles.get("I")
Q_handle = job.result_handles.get("Q")
# n_handle = job.result_handles.get("iteration")
#job.result_handles.wait_for_all_values()
prev_fq_if = q_IF[qe[-1]]*1e-6
plt.figure(figsize=(8, 6))
plt.title(f"Qubit Spectroscopy : Q{q_no}")
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)
while res_handles.is_processing():

    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    sig = I + 1j * Q
    plt.clf()
    #plt.plot(freqs, np.abs(sig))
    plt.plot(1e-6*(freqs), I, label="I")
    plt.title(f"Qubit Spectroscopy : Q{q_no}")
    plt.xlabel("Intermediate Frequency [MHz]")
    plt.ylabel("Quadrature Amplitude [a.u.]")
    plt.annotate(f"qamp: {q_amp}\nrramp: {rr_amp} integ_len: {integ_len} \ndf: {df*1e-6:.5f} MHz", 
                 xy=(0.62, 0.90), xycoords='axes fraction',
                 fontsize=10, bbox=dict(boxstyle="round", fc="w", alpha=0.3))
    plt.axvline(x=prev_fq_if, color='red', linestyle='--', label=f"Previous IF: {prev_fq_if:.5f} MHz" ,alpha=0.2)
    # plt.plot(1e-6*(freqs), Q, label="Q")
    plt.grid()
    plt.legend()
    plt.pause(1)
plt.savefig(f"Qubit_Spectroscopy_CW_{qe}_q_amp_{q_amp}_rr_amp_{rr_amp}_integ_len_{integ_len}_df_{df*1e-6:.5f}_MHz.png")
print(f"saved figure to Qubit_Spectroscopy_CW_{qe}_q_amp_{q_amp}_rr_amp_{rr_amp}_integ_len_{integ_len}_df_{df*1e-6:.5f}_MHz.png")
I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

############
# analysis #
############

# freqs = 1e-9*(f_LO + freqs)
# prev_fq_GHz = 1e-9*(f_LO + abs(prev_fq_if))
# plt.figure()
# plt.title(f'Qubit spectroscopy : Q{q_no}')
# plt.plot(freqs, I)
# plt.axvline(x=prev_fq_GHz, color='red', linestyle='--', label=f"Previous IF: {prev_fq_GHz:.5f} GHz" ,alpha=0.2)
# plt.xlabel("Frequency (GHz)")
# plt.grid()
# plt.show()

data = np.transpose([freqs, I,Q])

if save_data :
    file_saver_(data, file_name=__file__, suffix= qe, master_folder= ExpName,header_string="Frequency (GHz), I, Q")