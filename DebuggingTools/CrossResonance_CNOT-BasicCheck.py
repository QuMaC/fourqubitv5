from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from matplotlib import pyplot as plt
from Helper_Functions.macros import *

save_data = False
simulate = False

###################
# The QUA program #
###################

def CNOT_check_macro(U_c, U_t, pi_12, AC_flg = False):

    align(*qe_list_local)
    cooldown(time=wait_init)
    # wait(wait_init, qe_t)
    # reset_phase(rr_c)
    # reset_phase(rr_t)

    align(qe_t, qe_c)
    play(U_c, qe_c)
    wait(wait_t, qe_c)

    play(U_t, qe_t)
    wait(wait_t, qe_c)

    CNOT_macro(qe_c, qe_t, AC_flg)
    # iSWAP_macro(qe_c, qe_t)

    align()

    measure_macro(qe_t, rr_t, out_t, I, Q, pi_12=pi_12)
    measure_macro(qe_c, rr_c, out_c, I_c, Q_c, pi_12=pi_12)

    save(I, I_st)
    save(Q, Q_st)
    save(I_c, Ic_st)
    save(Q_c, Qc_st)

t_min_ns = 100
t_max_ns = 500
dt_ns = 4 #minimum 4ns

t_min = int(t_min_ns/4)
t_max = int(t_max_ns/4)
dt = int(dt_ns/4)
t_list = np.arange(t_min, t_max, dt)

c_no, t_no = 5, 2

AC_flg = True

qe_c, qe_t = f"q{c_no}", f"q{t_no}"
rr_c, rr_t = f"rr{c_no}", f"rr{t_no}"
out_c, out_t = adc_mapping[rr_c], adc_mapping[rr_t]
if c_no in control_qubits:
    qe_cr = f"cr_c{c_no}t{t_no}"
    qe_ac = f"cr_ac_c{c_no}t{t_no}"
else:
    qe_cr = f"cr_c{t_no}t{c_no}"
    qe_ac = f"cr_ac_c{t_no}t{c_no}"

qe_list_local = [qe_c, qe_t, qe_cr, qe_ac, rr_c, rr_t, 'stark_6']

wait_t = 4
wait_init = 125000
if simulate: wait_init = 100

pi_12 = True



p_cr = cr_phase[qe_cr]
with program() as CNOT_check:

    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    I_c = declare(fixed)
    Ic_st = declare_stream()
    Q_c = declare(fixed)
    Qc_st = declare_stream()
    Irabi_st = declare_stream()
    Qrabi_st = declare_stream()
    t = declare(int)


    # frame_rotation_2pi(cr_phase[qe_cr], qe_cr)
    # frame_rotation_2pi(cr_phase[qe_ac], qe_ac)


    with for_(n, 0, n < 2000, n + 1):
        with for_(t, t_min, t < t_max, t + dt):
            if simulate:
                assign(t, 100)

            # wait(wait_init, qe_t)
            reset_frame(qe_c)
            reset_frame(qe_t)
            reset_frame(qe_ac)
            reset_frame(qe_cr)
            cooldown(time=wait_init)
            # align(*qe_list_local)

            # reset_phase(rr_c)
            # reset_phase(rr_t)
            play_X180(qe_t, t=t)
            measure_macro(qe_t, rr_t, out_t, I, Q, pi_12=pi_12)
            save(I, Irabi_st)
            save(Q, Qrabi_st)


            ######################################################################

            CNOT_check_macro("I", "I", pi_12, AC_flg)

            ######################################################################

            CNOT_check_macro("X180", "I", pi_12, AC_flg)

            ######################################################################

            CNOT_check_macro("I", "X180", pi_12, AC_flg)

            ######################################################################

            CNOT_check_macro("X180", "X180", pi_12, AC_flg)

            ######################################################################

    with stream_processing():
        I_st.buffer(len(t_list), 4).average().save('I')
        Q_st.buffer(len(t_list), 4).average().save('Q')

        Ic_st.buffer(len(t_list), 4).average().save('I_c')
        Qc_st.buffer(len(t_list), 4).average().save('Q_c')

        Irabi_st.buffer(len(t_list)).average().save('I_r')
        Qrabi_st.buffer(len(t_list)).average().save('Q_r')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

##############
# Simualtion #
##############

if simulate :
    job = qmm.simulate(config, CNOT_check, SimulationConfig(int(10000)))
    # get DAC and digital samples
    # samples = job.get_simulated_samples()
    # plot all ports:
    # samples.con1.plot()
    samples = job.get_simulated_samples()
    qe_t_I = dac_mapping[f'{qe_t}'][1][0]
    qe_t_Q = dac_mapping[f'{qe_t}'][1][1]
    qe_c_I = dac_mapping[f'{qe_c}'][1][0]
    qe_c_Q = dac_mapping[f'{qe_c}'][1][1]
    rr_c_I = dac_mapping[f'rr{qe_c[-1]}'][1][0]
    rr_c_Q = dac_mapping[f'rr{qe_c[-1]}'][1][1]
    rr_t_I = dac_mapping[f'rr{qe_t[-1]}'][1][0]
    rr_t_Q = dac_mapping[f'rr{qe_t[-1]}'][1][1]
    con_ctrl = dac_mapping[f'{qe_c}'][0]
    con_tgt = dac_mapping[f'{qe_t}'][0]
    con_ctrl = f'con{con_ctrl}'
    con_tgt = f'con{con_tgt}'
    control_I = getattr(samples, con_ctrl).analog[f'{qe_c_I}']
    control_Q = getattr(samples, con_ctrl).analog[f'{qe_c_Q}']
    target_I = getattr(samples, con_tgt).analog[f'{qe_t_I}']
    target_Q = getattr(samples, con_tgt).analog[f'{qe_t_Q}']
    rd_c_I = getattr(samples, con_ctrl).analog[f'{rr_c_I}']
    rd_c_Q = getattr(samples, con_ctrl).analog[f'{rr_c_Q}']
    rd_t_I = getattr(samples, con_tgt).analog[f'{rr_t_I}']
    rd_t_Q = getattr(samples, con_tgt).analog[f'{rr_t_Q}']
    stark_I = getattr(samples, con_tgt).analog['5']
    stark_Q = getattr(samples, con_tgt).analog['6']
    # plot all ports:
    plt.figure()
    plt.plot(control_I, label='control_I')
    plt.plot(control_Q, label='control_Q')
    plt.plot(target_I, label='target_I')
    plt.plot(target_Q, label='target_Q')
    plt.plot(rd_c_I, label='rd_c_I')
    plt.plot(rd_c_Q, label='rd_c_Q')
    plt.plot(rd_t_I, label='rd_t_I')
    plt.plot(rd_t_Q, label='rd_t_Q')
    plt.plot(stark_I, label='stark_I')
    plt.plot(stark_Q, label='stark_Q')
    plt.grid()
    plt.legend()
    plt.show(block=False)

    # plt.legend("")

    raise Halted()

#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(CNOT_check)
res_handles = job.result_handles
I_handle = job.result_handles.get("I")
Q_handle = job.result_handles.get("Q")
I_c_handle = job.result_handles.get("I_c")
Q_c_handle = job.result_handles.get("Q_c")
I_r_handle = job.result_handles.get("I_r")
Q_r_handle = job.result_handles.get("Q_r")
#job.result_handles.wait_for_all_values()

t_list = 4*t_list
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)
I_c_handle.wait_for_values(1)
Q_c_handle.wait_for_values(1)
I_r_handle.wait_for_values(1)
Q_r_handle.wait_for_values(1)


#========== PLOT INIT SETTINGS===================
plt.ion()
plt.rcParams["figure.figsize"] = (15,10)
fig,ax = plt.subplots(3,2,sharex=True)
fig.suptitle("CNOT Check",fontsize=15)
axbig = fig.add_subplot(111, frameon=False)
axbig.set_xlabel("Time (us)",labelpad=20,fontsize=15)
axbig.set_ylabel("Amplitude",labelpad=50,fontsize=15)
axbig.set_xticks([])
axbig.set_yticks([])
lines = []
labellist = ["Control 0", "Control 1"]
titlelist2 = [" Target 0", " Target 1"]
titlelist1 = [" I "," Control I "]

for i in range(2):
    for j in range(2):
        lines.append(ax[i, j].plot(1e-3 * t_list, 0.0001*np.random.rand(len(t_list)), marker=".", label='C0')[0])
        lines.append(ax[i, j].plot(1e-3 * t_list, 0.0001*np.random.rand(len(t_list)), marker=".", label='C1')[0])
        ax[i, j].set_title(titlelist2[i]+titlelist1[j])
        ax[i,j].grid()
        ax[i,j].legend(loc='upper right')


lines.append(ax[2, 0].plot(1e-3 * t_list, 0.0001 * np.random.rand(len(t_list)), marker=".",label='I')[0])
lines.append(ax[2, 1].plot(1e-3 * t_list, 0.0001 * np.random.rand(len(t_list)), marker=".",label='Q')[0])
for j in range(2):
    ax[2,j].set_title('Rabi'+titlelist1[j])
    ax[2, j].grid()
    ax[2, j].legend(loc='upper right')

fig.set_tight_layout(True)
plt.show()
###################################################


while res_handles.is_processing():

    #plot rabi
    I_r = I_r_handle.fetch_all()
    Q_r = Q_r_handle.fetch_all()

    Ic = I_c_handle.fetch_all()

    lines[8].set_ydata(I_r)
    lines[9].set_ydata(Q_r)


    #plot cnot tests
    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()

    lines[0].set_ydata(I[:,0])
    lines[1].set_ydata(I[:,1])
    lines[2].set_ydata(Ic[:,0])
    lines[3].set_ydata(Ic[:,1])
    lines[4].set_ydata(I[:,2])
    lines[5].set_ydata(I[:,3])
    lines[6].set_ydata(Ic[:,2])
    lines[7].set_ydata(Ic[:,3])


    for i in range(3):
        for j in range(2):
            ax[i, j].relim()
            ax[i, j].autoscale_view()

    fig.set_tight_layout(True)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.5)

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()
#
#
#
# ############
# # analysis #
# ############

#
if save_data is True:
    np.savetxt("../../../Experiments/2022-06-24 Ringv1-Indiq7_CuCav_Ringv2v3/2022-06-28 Low_temp_Response/RingCavity_1.0/Cross_Resonance/2022-07-12_RabiTarget_4.txt",
               np.transpose([t_list, I,Q]), delimiter="\t")


