import numpy as np
from qm import QuantumMachinesManager
from Helper_Functions.helper_functionsv2 import S2N
from qm import SimulationConfig
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
from qualang_tools.plot import interrupt_on_close
from Helper_Functions.macros import *
from qualang_tools.results import progress_counter, fetching_tool
from Helper_Functions.CR_fitters import *
from Helper_Functions.qua_program_funcs import *
from Helper_Functions.analysis_functions import *

matplotlib.use('Qt5Agg')
import os
import copy
from datetime import datetime
import json

simulate = False
save_data = False
time_stamp = False
pi_12 = True
plot_rabi = False
plot_local = True
update_calib = False
###################
# The QUA program #
###################

t_min_ns = 4
t_max_ns = 1000
dt_ns = 4  # minimum 4ns

ivals = None
t_min = int(t_min_ns / 4)
t_max = int(t_max_ns / 4)
dt = int(dt_ns / 4)
t_list = np.arange(t_min, t_max, dt)

c_no, t_no = 1, 4

CR_data = []

qe_c = f"q{c_no}"
rr_c = f"rr{c_no}"
out_c = adc_mapping[rr_c]
qe_t = f"q{t_no}"
rr_t = f"rr{t_no}"
out_t = adc_mapping[rr_t]

cr_elem = f"cr_c{c_no}t{t_no}"
cr_ac_elem = f"cr_ac_c{c_no}t{t_no}"
# p_list = [0]


echo_p = False

wait_init = 250000
wait_t = 4
wait_rr = 16

n_avg = 200

acc_ac_phase = 0
acc_ac_phase_arr = []
str_phase = 1
str_ac_phase = 1
# p = 0
p1 = cr_phase[cr_elem]
p = p1 - cr_phase[cr_ac_elem]
acc_ac_phase = p
max_trials = 7
trial_cnt = 0
acc_phase = 0

if simulate: wait_init = 100

a_cr = cr_amp[cr_elem]

# ######################################
# # Open Communication with the Server #
# ######################################

#############
# execution #
#############
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

# for p in p_list:
while abs(str_ac_phase) > 0.05 and trial_cnt < max_trials:

    # print(abs(str_ac_phase) > 0.005)
    #
    # print(trial_cnt < max_trials)
    #
    # print(abs(str_ac_phase) > 0.005 and trial_cnt < max_trials)

    job = HT_setPhase(qmm, cr_elem, p, t_min, t_max, dt, n_avg, wait_init, wait_t,
                      wait_rr, qe_c, qe_t, pi_12, simulate, echo_p, a_cr)

    results = fetching_tool(job, data_list=["I_t_avg", "Q_t_avg", "I_c_avg",
                                            "Q_c_avg", "I_rabi_avg", "Q_rabi_avg",
                                            "iteration"], mode="live")
    # res_handles = job.result_handles
    # It_handle = job.result_handles.get("I_t_avg")
    # Qt_handle = job.result_handles.get("Q_t_avg")
    # Ic_handle = job.result_handles.get("I_c_avg")
    # Qc_handle = job.result_handles.get("Q_c_avg")
    # Irabi_handle = job.result_handles.get("I_rabi_avg")
    # Qrabi_handle = job.result_handles.get("Q_rabi_avg")

    # job.result_handles.wait_for_all_values()

    # It_handle.wait_for_values(1)
    # Qt_handle.wait_for_values(1)
    # Ic_handle.wait_for_values(1)
    # Qc_handle.wait_for_values(1)
    # Irabi_handle.wait_for_values(1)
    # Qrabi_handle.wait_for_values(1)

    # ========== PLOT INIT SETTINGS===================
    t_list_ns = 2 * 4 * t_list
    plt.ion()
    plt.rcParams["figure.figsize"] = (15, 10)
    fig, ax = plt.subplots(3, 3, sharex=True, sharey='row')
    interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
    fig.suptitle(f"Cross Resonance Tomography : Phase {p1} AC phase = {p}", fontsize=15)
    axbig = fig.add_subplot(111, frameon=False)
    axbig.set_xlabel("Time (us)", labelpad=20, fontsize=15)
    axbig.set_ylabel("Amplitude", labelpad=50, fontsize=15)
    axbig.set_xticks([])
    axbig.set_yticks([])
    lines = []
    tc = ["Control 0", "Control 1"]
    labels = ["Z", "Y", "X"]
    for i in range(2):
        # ax[i,0].set_xlabel("Time (us)")
        for j in range(3):
            lines.append(
                ax[i, j].plot(1e-3 * t_list_ns, 0.0001 * np.random.rand(len(t_list_ns)), marker=".", label='I')[
                    0])  # Returns a tuple of line objects, thus the [0]
            lines.append(ax[i, j].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
            ax[i, j].set_title(tc[i] + "  Target : " + labels[j])
            # ax[i,j].set_ylabel("Amplitude")
            ax[i, j].grid()
            ax[i, j].legend(loc='upper right')

    for i in range(2):
        lines.append(ax[2, i].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='I')[0])
        lines.append(ax[2, i].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
        ax[2, i].set_title(f"Control {i}")
        # ax[2,i].set_ylabel("Amplitude")
        ax[2, i].grid()
        ax[2, i].legend(loc='upper right')

    lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='I')[0])
    lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
    ax[2, 2].set_title("Target Rabi")
    ax[2, 2].grid()
    ax[2, 2].legend(loc='upper right')
    fig.set_tight_layout(True)
    fig.set_tight_layout(True)
    plt.show()

    # =======================================================

    # Start data collection and plotting =====================
    while results.is_processing():

        I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg, iteration = results.fetch_all()

        progress_counter(iteration, n_avg, start_time=results.get_start_time())
        # It = It_handle.fetch_all()
        # Qt = Qt_handle.fetch_all()
        # Ic = Ic_handle.fetch_all()
        # Qc = Qc_handle.fetch_all()
        # Irabi = Irabi_handle.fetch_all()
        # Qrabi = Qrabi_handle.fetch_all()

        It = I_t_avg
        Qt = Q_t_avg
        Ic = I_c_avg
        Qc = Q_c_avg
        Irabi = I_rabi_avg
        Qrabi = Q_rabi_avg

        # plot control qubits
        Ic0 = np.average(Ic[:, 0].reshape(len(t_list), 3), axis=1)
        Qc0 = np.average(Qc[:, 0].reshape(len(t_list), 3), axis=1)
        Ic1 = np.average(Ic[:, 1].reshape(len(t_list), 3), axis=1)
        Qc1 = np.average(Qc[:, 1].reshape(len(t_list), 3), axis=1)
        lines[12].set_ydata(Ic0)
        lines[13].set_ydata(Ic0)
        lines[14].set_ydata(Ic1)
        lines[15].set_ydata(Ic1)
        lines[16].set_ydata(Irabi)
        # lines[17].set_ydata(Qrabi)

        snr_i, _ = S2N(I_rabi_avg)

        if snr_i > 80:
            job.halt()

        # plot target qubits
        for i in range(0, 6):
            lines[2 * i].set_ydata(It[:, i])
            lines[2 * i + 1].set_ydata(Qt[:, i])

        for i in range(3):
            for j in range(3):
                ax[i, j].relim()
                ax[i, j].autoscale_view()

        fig.set_tight_layout(True)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.1)

    # It = job.result_handles.get("I_t_avg").fetch_all()
    # Qt = job.result_handles.get("Q_t_avg").fetch_all()
    # Ic = job.result_handles.get("I_c_avg").fetch_all()
    # Qc = job.result_handles.get("Q_c_avg").fetch_all()

    I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg, iteration = results.fetch_all()

    Ic0 = np.average(I_c_avg[:, 0].reshape(len(t_list), 3), axis=1)
    Qc0 = np.average(Q_c_avg[:, 0].reshape(len(t_list), 3), axis=1)
    Ic1 = np.average(I_c_avg[:, 1].reshape(len(t_list), 3), axis=1)
    Qc1 = np.average(Q_c_avg[:, 1].reshape(len(t_list), 3), axis=1)
    Irabi = I_rabi_avg
    Qrabi = Q_rabi_avg

    t_list_ns_data = t_list_ns.reshape(len(t_list_ns), 1)
    Ic0, Ic1 = Ic0.reshape(len(Ic0), 1), Ic1.reshape(len(Ic1), 1)
    Qc0, Qc1 = Qc0.reshape(len(Qc0), 1), Qc1.reshape(len(Qc1), 1)

    Qtarget_data = np.hstack((t_list_ns_data, Q_t_avg))
    Itarget_data = np.hstack((t_list_ns_data, I_t_avg))

    Icontrol_data = np.hstack((t_list_ns_data, Ic0, Ic1))
    Qcontrol_data = np.hstack((t_list_ns_data, Qc0, Qc1))

    # ############
    # # analysis #
    # ############

    p = np.round(p, 5)
    if save_data is True:
        file_saver_qubit_(Itarget_data, file_name=__file__, master_folder=ExpName,
                          suffix=f"I_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)
        file_saver_qubit_(Qtarget_data, file_name=__file__, master_folder=ExpName,
                          suffix=f"Q_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)
        file_saver_qubit_(np.transpose([t_list_ns, Irabi, Qrabi]), file_name=__file__,
                          master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                          suffix=f"Rabi_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)
        file_saver_qubit_(Icontrol_data, file_name=__file__,
                          master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                          suffix=f"Icontrol_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)
        file_saver_qubit_(Qcontrol_data, file_name=__file__,
                          master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                          suffix=f"Qcontrol_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)

    ############## CR fitting ##############

    t_data = Itarget_data.transpose()
    t_data_r = [t_list_ns, Irabi, Qrabi]

    time_list = t_data[0]

    rabi_i = 1e3 * t_data_r[1]

    if trial_cnt == 0:

        #
        # pars, cov = curve_fit(f=rabi_fit, xdata=time_list, ydata=rabi_i, p0=[0.03, 0.0001, 100, 0, 1e-5],
        # #                       bounds=(-np.inf, np.inf), maxfev=2000)
        res_I = fit_cos(time_list, rabi_i)
        pars = [res_I['amp'], res_I['freq'], 0, res_I['phase'], res_I['offset']]
        norm, off = pars[0], pars[4]
        if plot_rabi:
            plt.figure()
            plt.plot(t_list, rabi_i)
            plt.plot(t_list, rabi_fit(t_list, *pars))
            plt.show()

    C0data = 1e3 * t_data[1:4]
    C1data = 1e3 * t_data[4:7]
    Cdata = []
    for i in range(3):
        data_t = [C0data[i], C1data[i]]
        Cdata.append(data_t)
    Cdata = normalize_data(Cdata, off, norm)

    # Calculate interaction strengths by fitting Bloch equations to CR data
    int_strengths, ivals = CR_Hamiltonian_tomography(Cdata, time_list, bloch_params=True, init_vals=None)
    int_strengths = np.array(int_strengths)  # labels = ["ZX", "IX", "ZY", "IY", "ZZ", "IZ"]
    # CR_data.append(1e3*int_strengths)

    print(f'Strengths at {acc_ac_phase} are '
          f'\n ZX = {int_strengths[0] * 1e3} MHz'
          f'\n IX = {int_strengths[1] * 1e3} MHz'
          f'\n ZY = {int_strengths[2] * 1e3} MHz'
          f'\n IY = {int_strengths[3] * 1e3} MHz'
          f'\n ZZ = {int_strengths[4] * 1e3} MHz'
          f'\n IZ = {int_strengths[5] * 1e3} MHz'
          )

    exp_vals = Cdata
    ox1, oy1, del1, d1 = ivals[0]
    ox2, oy2, del2, d2 = ivals[1]
    vals1 = bloch_functions(time_list, ox1, oy1, del1, d1)
    vals2 = bloch_functions(time_list, ox2, oy2, del2, d2)

    str_phase = (np.arctan2(int_strengths[2], int_strengths[0])) * (1 / (2 * pi))

    str_ac_phase = (np.arctan2(int_strengths[3], int_strengths[1])) * (1 / (2 * pi))
    # str_ac_phase = int_strengths[3]*1e3*np.sign(int_strengths[3]*int_strengths[1])

    acc_ac_phase_arr.append(str_ac_phase)

    if str_phase > 1:
        str_phase = str_phase - 1
    elif str_phase < 0:
        str_phase = str_phase + 1

    if str_ac_phase > 1:
        str_ac_phase = str_ac_phase - 1
    elif str_ac_phase < 0:
        str_ac_phase = str_ac_phase + 1

    acc_phase += -1 * str_phase

    acc_ac_phase += -1 * str_ac_phase

    if acc_ac_phase > 1:
        acc_ac_phase = acc_ac_phase - 1
    elif acc_ac_phase < 0:
        acc_ac_phase = acc_ac_phase + 1

    colors = ["red", "blue", "green", "orange", "black", "magenta"]
    labels = ["Z", "Y", "X"]

    if plot_local:
        plt.figure()
        for i in range(3):
            plt.plot(time_list, vals1[i], color=colors[i], label=labels[i])
            plt.plot(time_list, Cdata[i][0], ".", color=colors[i])
        plt.grid()
        plt.title(f"Fitting Phase {p} : Control 0")
        plt.legend()
        plt.ylabel("Expectation Value")
        plt.xlabel("Time (ns)")
        plt.show()

        plt.figure()
        for i in range(3):
            plt.plot(time_list, vals2[i], color=colors[i], label=labels[i])
            plt.plot(time_list, Cdata[i][1], ".", color=colors[i])
        plt.grid()
        plt.title(f"Fitting Phase {p} : Control 1")
        plt.legend()
        plt.ylabel("Expectation Value")
        plt.xlabel("Time (ns)")
        plt.show()

    print(f'Current phase offset = {acc_ac_phase}')
    p = acc_ac_phase
    trial_cnt += 1

print(f'Optimal CR AC phase is {p1 - acc_ac_phase}')
print(f'Strengths at {acc_ac_phase} are '
      f'\n ZX = {int_strengths[0] * 1e3} MHz'
      f'\n IX = {int_strengths[1] * 1e3} MHz'
      f'\n ZY = {int_strengths[2] * 1e3} MHz'
      f'\n IY = {int_strengths[3] * 1e3} MHz'
      f'\n ZZ = {int_strengths[4] * 1e3} MHz'
      f'\n IZ = {int_strengths[5] * 1e3} MHz'
      )

if update_calib:
    with open('../Configuration_Files/Pulse_Calibrations/cr_phase.json', 'r') as f:
        cr_phase_data = json.load(f)
        f.close()

    t_phase = (p1 - acc_ac_phase) % 1

    if t_phase < 0:
        t_phase = t_phase + 1

    cr_phase_data[cr_ac_elem] = t_phase

    with open('../Configuration_Files/Pulse_Calibrations/cr_phase.json', 'w') as f:
        json.dump(cr_phase_data, f, indent=6)
        f.close()
