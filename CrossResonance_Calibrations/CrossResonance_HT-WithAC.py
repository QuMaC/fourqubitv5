import sys
from qm import SimulationConfig
from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
#matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import *

simulate = False
save_data = True
time_stamp = False
pi_12 = False
Echo = True
###################
# The QUA program #
###################

t_min_ns = 16
t_max_ns = 1000
dt_ns = 4 #minimum 4ns

t_min = int(t_min_ns/4)
t_max = int(t_max_ns/4)
dt = int(dt_ns/4)
t_list = np.arange(t_min, t_max, dt)

c_no, t_no = 3, 6

qe_c = f"q{c_no}"
rr_c = f"rr{c_no}"
out_c = adc_mapping[rr_c]
qe_t = f"q{t_no}"
rr_t = f"rr{t_no}"
out_t = adc_mapping[rr_t]

cr_elem = f"cr_c{c_no}t{t_no}"
cr_ac_elem = f"cr_ac_c{c_no}t{t_no}"

wait_init = 125000
wait_t = 4
wait_rr = 16
pi_amp = amp_scale[str(t_no)]["X180"]

if simulate: wait_init = 100


def twoqubit_CR_ham_tomo_withAC(control: int, target_pulse, cr_elem, cr_ac_elem, a_cr, a_ac, echo: bool):
    '''
    ### Pulse protocol:

    - Put control in 1 or 0 based on bool(control).
    - Send a cross resonance pulse of length 't' on cross resonance element (cr_c1t2) with or without echo.
    - Send target_pulse on Target qubit.
    - Measurement pulse on taget and control.
    - save data on 4 streams.

    ### Requirements:
    - 4 streams : I_t_st,Q_t_st,I_c_st,Q_c_st
    - 5 variables : It,Qt,Ic,Qc and time 't' that is looped over
    '''
    # start
    align(rr_t, qe_t)
    wait(wait_init, qe_t)
    # play("X", qe_t)             #Initializes Target in 1 ; Comment out for normal HT
    # wait(wait_t,qe_t)
    align(qe_t, qe_c)

    # set control to zero or one
    with if_(control == 1):
        play_X180(qe_c)
    with else_():
        play("I", qe_c)
    align(cr_elem, qe_c)

    # do either simple CR or echo CR
    with if_(echo == False):
        align(cr_elem, cr_ac_elem)
        play_flat_top(cr_elem, a_cr, 2 * t)
        play_flat_top(cr_ac_elem, a_ac, 2 * t)
    with else_():
        align(cr_elem, cr_ac_elem)
        play_flat_top(cr_elem, a_cr, t)
        play_flat_top(cr_ac_elem, a_ac, t)
        align(qe_c, cr_elem)
        wait(wait_t, qe_c)
        play_X180(qe_c)
        wait(wait_t, qe_c)
        align(cr_elem, qe_c)
        align(cr_elem, cr_ac_elem)
        play_flat_top(cr_elem, -a_cr, t)
        play_flat_top(cr_ac_elem, -a_ac, t)
        align(cr_elem, qe_c)
        wait(wait_t, qe_c)
        play_X180(qe_c)

    align(cr_elem, qe_t)
    wait(wait_t, qe_t)
    # play target pulse
    play(target_pulse, qe_t)

    # # finally perform readouts
    measure_macro(qe_t, rr_t, out_t, It, Qt, pi_12=pi_12)
    measure_macro(qe_t, rr_c, out_c, Ic, Qc, pi_12=pi_12)
    save(It, I_t_st)
    save(Qt, Q_t_st)
    save(Ic, I_c_st)
    save(Qc, Q_c_st)

a_cr, p_cr = cr_amp[cr_elem],  cr_phase[cr_elem]
a_ac, p_ac = cr_amp[cr_ac_elem], cr_phase[cr_ac_elem]

with program() as CR_tomo:
    n = declare(int)
    I_c_st = declare_stream()
    Q_c_st = declare_stream()
    Q_t_st = declare_stream()
    I_t_st = declare_stream()
    Ic = declare(float)
    Qc = declare(float)
    Qt = declare(float)
    It = declare(float)
    Qrabi = declare(float)
    Irabi = declare(float)
    Q_rabi_st = declare_stream()
    I_rabi_st = declare_stream()
    t = declare(int)

    frame_rotation_2pi(p_cr, cr_elem)
    frame_rotation_2pi(p_ac, cr_ac_elem)
    # update_frequency(cr_elem, q_IF["4"])   #For checking coherent errors
    # update_frequency(cr_ac_elem, q_IF["4"])   #For checking coherent errors
    with for_(n, 0, n < 2000, n + 1):
        with for_(t, t_min, t < t_max, t + dt):

            if simulate:
                assign(t, 100)

            wait(wait_init, qe_t)
            play("const"*amp(pi_amp), qe_t, t)
            wait(4, qe_t)
            measure_macro(qe_t, rr_t, out_t, Irabi, Qrabi, pi_12=pi_12)
            save(Irabi, I_rabi_st)
            save(Qrabi, Q_rabi_st)

            # play C0TI, get C0Z
            twoqubit_CR_ham_tomo_withAC(0, "I", cr_elem, cr_ac_elem, a_cr, a_ac, Echo)

            # play C0TX/2, get C0Y
            twoqubit_CR_ham_tomo_withAC(0, "X90", cr_elem, cr_ac_elem, a_cr, a_ac, Echo)

            # play C0T-Y/2, get C0X
            twoqubit_CR_ham_tomo_withAC(0, "mY90", cr_elem, cr_ac_elem, a_cr, a_ac, Echo)

            # playing C1TI, get C1Z
            twoqubit_CR_ham_tomo_withAC(1, "I", cr_elem, cr_ac_elem, a_cr, a_ac, Echo)

            # playing C1TX/2, get C1Y
            twoqubit_CR_ham_tomo_withAC(1, "X90", cr_elem, cr_ac_elem, a_cr, a_ac, Echo)

            # playing C1T-Y/2, get C1X
            twoqubit_CR_ham_tomo_withAC(1, "mY90", cr_elem, cr_ac_elem, a_cr, a_ac, Echo)


    with stream_processing():

        #saves [[I_C0_t0,I_C1_t0],[I_C0_t1,I_C1_t1]]
        I_c_st.buffer(3*len(t_list), 2).average().save("I_c_avg")
        Q_c_st.buffer(3*len(t_list), 2).average().save("Q_c_avg")

        #saves [[I_C0Z_t0, I_C0Y_t0, I_C0X_t0, I_C1Z_t0, I_C1Y_t0, I_C1X_t0], [_t1array]]
        I_t_st.buffer(len(t_list), 6).average().save("I_t_avg")
        Q_t_st.buffer(len(t_list), 6).average().save("Q_t_avg")

        I_rabi_st.buffer(len(t_list)).average().save("I_rabi_avg")
        Q_rabi_st.buffer(len(t_list)).average().save("Q_rabi_avg")


# ######################################
# # Open Communication with the Server #
# ######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)


##############
# Simualtion #
##############

if simulate :
    job = qmm.simulate(config, CR_tomo, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()
    plt.legend("")

    raise Halted()
#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(CR_tomo)
res_handles = job.result_handles
It_handle = job.result_handles.get("I_t_avg")
Qt_handle = job.result_handles.get("Q_t_avg")
Ic_handle = job.result_handles.get("I_c_avg")
Qc_handle = job.result_handles.get("Q_c_avg")
Irabi_handle = job.result_handles.get("I_rabi_avg")
Qrabi_handle = job.result_handles.get("Q_rabi_avg")

#job.result_handles.wait_for_all_values()

It_handle.wait_for_values(1)
Qt_handle.wait_for_values(1)
Ic_handle.wait_for_values(1)
Qc_handle.wait_for_values(1)
Irabi_handle.wait_for_values(1)
Qrabi_handle.wait_for_values(1)


#========== PLOT INIT SETTINGS===================
t_list_ns = 2*4*t_list
plt.ion()
plt.rcParams["figure.figsize"] = (15,10)
fig,ax = plt.subplots(3,3,sharex=True,sharey='row')
fig.suptitle("Cross Resonance Tomography",fontsize=15)
axbig = fig.add_subplot(111, frameon=False)
axbig.set_xlabel("Time (us)",labelpad=20,fontsize=15)
axbig.set_ylabel("Amplitude",labelpad=50,fontsize=15)
axbig.set_xticks([])
axbig.set_yticks([])
lines = []
tc = ["Control 0", "Control 1"]
labels = ["Z","Y","X"]
for i in range(2):
    # ax[i,0].set_xlabel("Time (us)")
    for j in range(3):
        lines.append(ax[i,j].plot(1e-3 * t_list_ns, 0.0001*np.random.rand(len(t_list_ns)), marker=".", label='I')[0])  # Returns a tuple of line objects, thus the [0]
        lines.append(ax[i,j].plot(1e-3 * t_list_ns, [0]*len(t_list_ns), marker=".", label='Q')[0])
        ax[i,j].set_title(tc[i] + "  Target : " + labels[j])
        # ax[i,j].set_ylabel("Amplitude")
        ax[i,j].grid()
        ax[i,j].legend(loc='upper right')

for i in range(2):
    lines.append(ax[2,i].plot(1e-3 * t_list_ns, [0]*len(t_list_ns), marker=".", label='I')[0])
    lines.append(ax[2,i].plot(1e-3 * t_list_ns, [0]*len(t_list_ns), marker=".", label='Q')[0])
    ax[2,i].set_title(f"Control {i}")
    # ax[2,i].set_ylabel("Amplitude")
    ax[2,i].grid()
    ax[2,i].legend(loc='upper right')

lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='I')[0])
lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
ax[2, 2].set_title("Target Rabi")
ax[2, 2].grid()
ax[2, 2].legend(loc='upper right')
fig.set_tight_layout(True)
fig.set_tight_layout(True)
plt.show()

#=======================================================


#Start data collection and plotting =====================
while res_handles.is_processing():

    It = It_handle.fetch_all()
    Qt = Qt_handle.fetch_all()
    Ic = Ic_handle.fetch_all()
    Qc = Qc_handle.fetch_all()
    Irabi = Irabi_handle.fetch_all()
    Qrabi = Qrabi_handle.fetch_all()

    #plot control qubits
    Ic0 = np.average(Ic[:, 0].reshape(len(t_list), 3), axis=1)
    Qc0 = np.average(Qc[:, 0].reshape(len(t_list), 3), axis=1)
    Ic1 = np.average(Ic[:, 1].reshape(len(t_list), 3), axis=1)
    Qc1 = np.average(Qc[:, 1].reshape(len(t_list), 3), axis=1)
    lines[12].set_ydata(Ic0)
    lines[13].set_ydata(Qc0)
    lines[14].set_ydata(Ic1)
    lines[15].set_ydata(Qc1)
    lines[16].set_ydata(Irabi)
    lines[17].set_ydata(Qrabi)

    #plot target qubits
    for i in range(0, 6):
        lines[2*i].set_ydata(It[:, i])
        lines[2*i+1].set_ydata(Qt[:, i])

    for i in range(3):
        for j in range(3):
            ax[i,j].relim()
            ax[i,j].autoscale_view()

    fig.set_tight_layout(True)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(1)

It = job.result_handles.get("I_t_avg").fetch_all()
Qt = job.result_handles.get("Q_t_avg").fetch_all()
Ic = job.result_handles.get("I_c_avg").fetch_all()
Qc = job.result_handles.get("Q_c_avg").fetch_all()
Ic0 = np.average(Ic[:, 0].reshape(len(t_list), 3), axis=1)
Qc0 = np.average(Qc[:, 0].reshape(len(t_list), 3), axis=1)
Ic1 = np.average(Ic[:, 1].reshape(len(t_list), 3), axis=1)
Qc1 = np.average(Qc[:, 1].reshape(len(t_list), 3), axis=1)
Irabi = job.result_handles.get("I_rabi_avg").fetch_all()
Qrabi = job.result_handles.get("Q_rabi_avg").fetch_all()

t_list_ns_data = t_list_ns.reshape(len(t_list_ns), 1)
Ic0, Ic1 = Ic0.reshape(len(Ic0), 1), Ic1.reshape(len(Ic1), 1)
Qc0, Qc1 = Qc0.reshape(len(Qc0), 1), Qc1.reshape(len(Qc1), 1)

Qtarget_data = np.hstack((t_list_ns_data, Qt))
Itarget_data = np.hstack((t_list_ns_data, It))

Icontrol_data = np.hstack((t_list_ns_data, Ic0, Ic1))
Qcontrol_data = np.hstack((t_list_ns_data, Qc0, Qc1))

# ############
# # analysis #
# ############


# #

if save_data is True:

    file_saver_qubit_(Itarget_data, file_name=__file__, master_folder=ExpName,
                      suffix=f"I_Control{c_no}_Target{t_no}_Phase_{p_cr}_Echo_{Echo}", time_stamp=time_stamp)
    file_saver_qubit_(Qtarget_data, file_name=__file__, master_folder=ExpName,
                      suffix=f"Q_Control{c_no}_Target{t_no}_Phase_{p_cr}_Echo_{Echo}", time_stamp=time_stamp)
    file_saver_qubit_(np.transpose([t_list_ns, Irabi, Qrabi]), file_name=__file__,
                      master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                      suffix=f"Rabi_Control{c_no}_Target{t_no}_Phase_{p_cr}_Echo_{Echo}", time_stamp=time_stamp)
    file_saver_qubit_(Icontrol_data, file_name=__file__,
                      master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                      suffix=f"Icontrol_Control{c_no}_Target{t_no}_Phase_{p_cr}", time_stamp=time_stamp)
    file_saver_qubit_(Qcontrol_data, file_name=__file__,
                      master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                      suffix=f"Qcontrol_Control{c_no}_Target{t_no}_Phase_{p_cr}", time_stamp=time_stamp)
