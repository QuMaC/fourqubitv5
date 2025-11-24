from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from Helper_Functions.macros import *
import matplotlib
#matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from qualang_tools.analysis.discriminator import two_state_discriminator
# from qm import generate_qua_script

save_data = True

# rr_amp = 1.0
# integ_len = 4000
# update_config_rr(config, q_no, rr_no, rr_amp, integ_len)

q_no = 3
pi12 = True
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
chunk_size = 20 # In no. of clck cycles (units of 4ns)
integ_len = integ_len_clk[str(q_no)]
# integ_len = config[f'q{q_no}_ro_pulse']['length'] // 4
arr_size = int(integ_len/chunk_size)
integ_lens = np.arange(4*chunk_size, 4*integ_len + 2*chunk_size, 4*chunk_size)
n_runs = 1e4


# ro_amp = ro_amp[str(q_no)]
a_min = 0.01
a_max = 0.28
da = 0.01
amps = np.arange(a_min, a_max + da/2, da)
n_amps = amps.size
# Set ro_amp to 1.0 in config
rep_rate_clk = 250000
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
ro_len = ro_len_clk[str(q_no)]
###################
# The QUA program #
###################

dem = -1.742e-3
a_rr = 1.0

with program() as IQ_blobs:

    n = declare(int)
    a = declare(fixed)
    I0 = declare(fixed, size=arr_size)
    I0_st = declare_stream()
    Q0 = declare(fixed, size=arr_size)
    Q0_st = declare_stream()
    I1 = declare(fixed, size=arr_size)
    I1_st = declare_stream()
    Q1 = declare(fixed, size=arr_size)
    Q1_st = declare_stream()

    with for_(a, a_min, a < a_max + da / 2, a + da):
        with for_(n, 0, n < n_runs, n + 1):

            wait(rep_rate_clk, qe)
            play("I", qe)
            align(qe, rr)
            if pi12:
                align(qe, qe_12)
                play_X180(qe_12)
                align(qe_12, rr)
            wait(wait_rr, rr)
            measure("readout" * amp(a), rr, None,
                    demod.accumulated("integW_cos", I0, chunk_size, out),
                    demod.accumulated("integW_minus_sin", Q0, chunk_size, out))
            for i in range(arr_size):
                save(I0[i], I0_st)
                save(Q0[i], Q0_st)

            align(rr, qe)
            wait(rep_rate_clk, qe)
            play_X180(qe)
            align(qe, rr)
            if pi12:
                align(qe, qe_12)
                play_X180(qe_12)
                align(qe_12, rr)
            wait(wait_rr, rr)
            measure("readout" * amp(a), rr, None,
                    demod.accumulated("integW_cos", I1, chunk_size, out),
                    demod.accumulated("integW_minus_sin", Q1, chunk_size, out))
            for i in range(arr_size):
                save(I1[i], I1_st)
                save(Q1[i], Q1_st)

    with stream_processing():
        I0_st.save_all('I0')
        Q0_st.save_all('Q0')
        I1_st.save_all('I1')
        Q1_st.save_all('Q1')

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
qm = qmm.open_qm(config)
job = qm.execute(IQ_blobs)

I0_handle = job.result_handles.get("I0")
Q0_handle = job.result_handles.get("Q0")
I1_handle = job.result_handles.get("I1")
Q1_handle = job.result_handles.get("Q1")
job.result_handles.wait_for_all_values()

n_runs = int(n_runs)
arr_size = int(arr_size)
# I0 = I0_handle.fetch(slice(0, arr_size*n_runs))["value"]
# I1 = I1_handle.fetch(slice(0, arr_size*n_runs))["value"]
# Q0 = Q0_handle.fetch(slice(0, arr_size*n_runs))["value"]
# Q1 = Q1_handle.fetch(slice(0, arr_size*n_runs))["value"]
#
# I0_2d = np.transpose(I0.reshape(n_runs, arr_size))
# I1_2d = np.transpose(I1.reshape(n_runs, arr_size))
# Q0_2d = np.transpose(Q0.reshape(n_runs, arr_size))
# Q1_2d = np.transpose(Q1.reshape(n_runs, arr_size))

I0 = I0_handle.fetch_all()["value"]
Q0 = Q0_handle.fetch_all()["value"]
I1 = I1_handle.fetch_all()["value"]
Q1 = Q1_handle.fetch_all()["value"]

def reshape(A, n_amps, n_runs, arr_size):

    A_reshaped = A.reshape(n_amps, n_runs, arr_size)
    A_reshaped_transpose = []
    for i, a in enumerate(A_reshaped):
        A_reshaped_transpose.append(np.transpose(a))

    A_reshaped_transpose = np.array(A_reshaped_transpose)


    return A_reshaped_transpose

def get_fidelity(I0, Q0, I1, Q1):

    angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(I0, Q0, I1, Q1,
                                                                         b_print=False, b_plot=False)
    return fidelity

def get_fidelity_list(I0_2d, Q0_2d, I1_2d, Q1_2d):

    fidelity_list = []
    for i in range(arr_size):
        fid = get_fidelity(I0_2d[i], Q0_2d[i], I1_2d[i], Q1_2d[i])
        fidelity_list.append(fid)
    return fidelity_list


I0_3d = reshape(I0, n_amps, n_runs, arr_size)
Q0_3d = reshape(Q0, n_amps, n_runs, arr_size)
I1_3d = reshape(I1, n_amps, n_runs, arr_size)
Q1_3d = reshape(Q1, n_amps, n_runs, arr_size)

fid_list_arr = []
for i, a in enumerate(amps):

    I0_2d, Q0_2d = I0_3d[i], Q0_3d[i]
    I1_2d, Q1_2d = I1_3d[i], Q1_3d[i]

    a = np.round(a, 3)
    if save_data is True:
        file_saver_(I0_2d, file_name=__file__, suffix=f"I02d_Amp_{a}_q{q_no}", master_folder=ExpName, time_stamp=False, init_path="E:/Experiments")
        file_saver_(Q0_2d, file_name=__file__, suffix=f"Q02d_Amp_{a}_q{q_no}", master_folder=ExpName, time_stamp=False, init_path="E:/Experiments")
        file_saver_(I1_2d, file_name=__file__, suffix=f"I12d_Amp_{a}_q{q_no}", master_folder=ExpName, time_stamp=False, init_path="E:/Experiments")
        file_saver_(Q1_2d, file_name=__file__, suffix=f"Q12d_Amp_{a}_q{q_no}", master_folder=ExpName, time_stamp=False, init_path="E:/Experiments")

    fidelity_list = get_fidelity_list(I0_2d, Q0_2d, I1_2d, Q1_2d)
    fid_list_arr.append(fidelity_list)

fid_list_arr = np.array(fid_list_arr)
fid_list_2d = fid_list_arr.reshape(n_amps, arr_size)

plt.figure()
for arr in fid_list_2d:
    plt.plot(arr)

if save_data is True:
    file_saver_(fid_list_2d, file_name=__file__, suffix=f"Fidelity_AmpIntLen_2dSweep_q{q_no}", master_folder=ExpName, time_stamp=False, init_path="E:/Experiments")

import seaborn as sns

ax = plt.figure(figsize=(15, 10))
cmap = ['RdBu_r', 'YlGnBu', 'BuPu']
ax = sns.heatmap(fid_list_2d, annot=False,
                 xticklabels=np.round(1e-3*integ_lens, 2), yticklabels=np.round(amps, 4),
                 cmap=cmap[0], vmin=50, vmax=100)
ax.set(xlabel="Integration Length (us)", ylabel="Readout Amplitude (a.u.)", title="Readout Fidelity Optimisation")
ax.highlight = [[46, 42], [34, 10]]
plt.show()