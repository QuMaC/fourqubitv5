import json
import sys

from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import *
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.plot import interrupt_on_close
from Helper_Functions.analysis_functions import *
import os

# pars, cov = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=I, p0=[1e-3,det + ZZ_shift,1,0, 1e-4], bounds=(-np.inf, np.inf), maxfev=10000)

matplotlib.use('Qt5Agg')

simulate = False
save_data = True

with open('./ramsey_redo.json', 'w') as f:
    json.dump({'redo': 0}, f, indent=6)

q_no = int(sys.argv[1])

###################
# The QUA program #
###################

# if os.path.getsize('./Pulse_Calibrations/ramsey_time_limits.json') > 2:
#     with open('./Pulse_Calibrations/ramsey_time_limits.json', 'r') as ram_times_file:
#         time_limits = json.load(ram_times_file)
#         ram_times_file.close()
#     t_min = (time_limits[str(q_no)]['t_min'] // 4)
#     t_max = (time_limits[str(q_no)]['t_max'] // 4)
#     dt = (time_limits[str(q_no)]['dt'] // 4)
# else:

with open('../Configuration_Files/Pulse_Calibrations/ramsey_time_limits.json', 'r') as ram_times_file:
    time_limits = json.load(ram_times_file)
    ram_times_file.close()
t_min = 16 // 4  # ns
t_max = 30000 // 4

if str(q_no) in time_limits.keys():
    dt = time_limits[str(q_no)]['dt'] // 4  #
else:
    dt = time_limits[list(time_limits.keys())[0]]['dt'] // 4

# time_limits = {}
times = {'t_min': t_min * 4, 't_max': t_max * 4, 'dt': dt * 4}
time_limits[str(q_no)] = times

with open('../Configuration_Files/Pulse_Calibrations/ramsey_time_limits.json', 'w') as ram_times_file:
    json.dump(time_limits, ram_times_file, indent=6)

t_min = 16 // 4  # ns
t_max = 30000 // 4
dt = 100 // 4  #

t_list = np.arange(t_min, t_max, dt)
t_list_us = t_list*4e-3
qubit_IF = q_IF[str(q_no)]
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(q_no)]
ZZ_shift = CrossKerr[str(q_no)] * 1e-6
n_avg = 1000

bare_det = float(sys.argv[2])  # in MHz

det = bare_det - ZZ_shift

if simulate:
    rep_rate_clk = 100
else:
    rep_rate_clk = 250000

dem = demarcations[str(q_no)]
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
piby2_len = piby2_len_ns[str(q_no)]

with program() as ramsey:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    t = declare(int)
    n_st = declare_stream()

    update_frequency(qe, qubit_IF + det * u.MHz)
    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t < t_max, t + dt):
            if simulate:
                assign(t, 100)

            cooldown(time=rep_rate_clk, active_reset=False,
                     qe=qe, qe_12=qe_12, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)
            play_X90(qe)
            # wait(t, qe) #Echo debug
            # play_X180(qe)
            wait(t, qe)
            play_X90(qe)
            measure_macro(qe, rr, out, I, Q, pi_12=False)

            save(I, I_st)
            save(Q, Q_st)
        save(n, n_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('I')
        Q_st.buffer(len(t_list)).average().save('Q')
        n_st.save("iteration")

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
if simulate:
    qmm = QuantumMachinesManager()
    job = qmm.simulate(config, ramsey, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()

    raise Halted()
#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(ramsey)
res_handles = job.result_handles
# I_handle = job.result_handles.get("I")
# Q_handle = job.result_handles.get("Q")

results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

t_list = 4 * t_list
fig, axs = plt.subplots(2, 1, sharex=True)
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

exception_flag = 0

# job.result_handles.wait_for_all_values()

# plt.figure()
# plt.title("Ramsey")
# I_handle.wait_for_values(1)
# Q_handle.wait_for_values(1)

flag_max_time_low = 0
flag_max_time_high = 0
flag_dt_low = 0
flag_dt_high = 0

tau_array = []
freq_array = []

t_max_us = max(t_list_us)
dt_us = t_list_us[1] - t_list_us[0]

dt_c = copy.copy(dt_us*1e3)

plot_no = 1
while res_handles.is_processing():

    I, Q, iteration = results.fetch_all()
    progress_counter(iteration, n_avg, start_time=results.get_start_time())

    try:
        res_I, pcov_i, init_i = ramsey_fitting(t_list_us, I)  # A, tau, offset, freq, phi
        res_Q, pcov_q, init_q = ramsey_fitting(t_list_us, Q)
        # if 0 < res_I[1] < t_max_us:
        tau_array.append(res_I[1])
        freq_array.append(res_I[3])
        exception_flag = 0
    except RuntimeError:
        exception_flag = 1
        print("Maximum iterations reached for fitting")
        res_I = [0, 0, 0, 0, 0]
        res_Q = [0, 0, 0, 0, 0]

    data = {"I": [I, res_I], "Q": [Q, res_Q]}

    if exception_flag == 0:
        for i, ax in enumerate(axs.flat):

            ax.cla()
            data_label = list(data.keys())[i]
            plot_data = data[data_label]
            fit_data_I = [ramsey_fit(i, res_I[0], res_I[1], res_I[2], res_I[3], res_I[4]) for i in t_list_us]
            fit_data_Q = [ramsey_fit(i, res_Q[0], res_Q[1], res_Q[2], res_Q[3], res_Q[4]) for i in t_list_us]

            # fit_func = plot_data[1]["fitfunc"]
            ax.plot(t_list_us, plot_data[0], marker='.', label=data_label)
            if data_label == 'I':
                ax.plot(t_list_us, fit_data_I, label=data_label + "_Fit")
            else:
                ax.plot(t_list_us, fit_data_Q, label=data_label + "_Fit")
            ax.set(xlabel="Time (us)", ylabel="Ramsey Amplitude")
            ax.legend()
            ax.grid()
            ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
            snr, temp = S2N(I)
            # print(snr)
            if snr > 5:

                guess_t = np.median(tau_array)

                if np.isnan(guess_t):
                    guess_t = 3*t_max_us

                Y = np.fft.fft(I) * (2 / len(I))
                Y_m = Y[1:len(Y) // 2]
                X = np.fft.fftfreq((len(Y)), d=t_list_us[1] - t_list_us[0])
                X_m = X[1:len(Y) // 2]
                guess_freq = X_m[np.where(np.abs(Y_m) == np.max(np.abs(Y_m)))[0][0]]

                print(f'guess tau = {guess_t}')
                print(f'guess freq = {guess_freq}')

                # if flag_max_time_low == 0:
                    # if (t_max_us < 2.5 * guess_t):
                    #     flag_max_time_low = 1
                    #     t_max_p = t_max_us
                    #     if t_min < 2.5 * guess_t * 1e3:
                    #         t_max_c = 2.5 * guess_t * 1e3
                    #     else:
                    #         t_max_c = t_min + 500
                    #     print(f'new max time = {t_max_c}')
                    #     print('insuff time')
                    # else:
                    #     flag_max_time_low = 0
                    #     # t_max_c = copy.deepcopy(t_max_us*1e3)

                # if flag_max_time_high == 0:
                #     if (t_max_us > 15 * guess_t):
                #         flag_max_time_high = 1
                #         t_max_p = t_max_us
                #         t_max_c = 2 * guess_t * 1e3
                #         print(f'new max time = {t_max_c}')
                #         print('too much time')
                #     else:
                #         flag_max_time_high = 0
                #         # t_max_c = copy.deepcopy(t_max_us*1e3)

                # if dt < (1/80) * abs((1/res_I[3])):
                if flag_dt_low == 0:
                    if dt_us < 1 / (50 * guess_freq):
                        flag_dt_low = 1
                        # print(f'dt_us {dt_us}')
                        dt_p = copy.deepcopy(dt_us)
                        dt_us1 = 1/(40 * guess_freq)
                        dt_c = int(dt_us1*1e3) - 4
                        if dt_c < 16:
                            dt_c = 16
                        print('meshing too fine')
                    else:
                        flag_dt_low = 0

                if flag_dt_high == 0:
                    if (dt_us > 1 / (3 * guess_freq)) and (flag_dt_low == 0):
                        # print(f'dt_us {dt_us}')
                        # print(f'low flag = {flag_dt_low}')
                        flag_dt_high = 1
                        dt_p = copy.deepcopy(dt_us)
                        dt_us1 = (1 / 8) * (1 / guess_freq)
                        dt_c = int(dt_us1*1e3) + 1
                        if dt_c < 16:
                            dt_c = 16
                        print('meshing too coarse')
                    else:
                        flag_dt_high = 0

                if (flag_dt_high == 1 or flag_dt_low == 1):
                    # with open('./Pulse_Calibrations/ramsey_time_limits.json', 'w') as f:
                    #     # if (flag_max_time_high == 1) or (flag_max_time_low == 1):
                    #     #     time_limits[str(q_no)]['t_max'] = t_max_c
                    #     time_limits[str(q_no)]['dt'] = dt_c
                    #     json.dump(time_limits, f, indent=6)
                    #     f.close()

                    with open('./ramsey_redo.json', 'w') as f:
                        json.dump({'redo': 1}, f, indent=6)

                    job.halt()
                else:
                    with open('./ramsey_redo.json', 'w') as f:
                        json.dump({'redo': 0}, f, indent=6)

                if snr > 10:
                    job.halt()

        fig.suptitle(f"Time Ramsey : Ramsey time = {res_I[1]:.2f} us  Ramsey Freq = {(res_I[3]):.2f}"
                     f" Applied detuning: {bare_det} MHz")
        plt.tight_layout()
        plt.pause(0.25)
        plt.show(block=False)
    else:
        print('Exception while fitting')

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

fit_list = {'amp': res_I[0],
            'tau': res_I[1],
            'offset': res_I[2],
            'freq': res_I[3],
            'phase': res_I[4],
            }

guess_t = res_I[1]
guess_freq = res_I[3]
#
# if (t_max_us < 2.5 * guess_t):
#     flag_max_time_low = 1
#     t_max_p = t_max_us
#     if t_min < 2.5 * guess_t * 1e3:
#         t_max_c = 2.5 * guess_t * 1e3
#     else:
#         t_max_c = t_min + 500
#     print(f'new max time = {t_max_c}')
#     print('insuff time')
# else:
#     flag_max_time_low = 0
#     # t_max_c = copy.deepcopy(t_max_us*1e3)

# if flag_max_time_high == 0:
#     if (t_max_us > 15 * guess_t):
#         flag_max_time_high = 1
#         t_max_p = t_max_us
#         t_max_c = 2 * guess_t * 1e3
#         print(f'new max time = {t_max_c}')
#         print('too much time')
#     else:
#         flag_max_time_high = 0
#         # t_max_c = copy.deepcopy(t_max_us*1e3)

# if dt < (1/80) * abs((1/res_I[3])):

# dt_c = dt

if flag_dt_low == 0:
    if dt_us < 1 / (50 * guess_freq):
        flag_dt_low = 1
        # print(f'dt_us {dt_us}')
        dt_p = copy.deepcopy(dt_us)
        dt_us1 = 1 / (20 * guess_freq)
        dt_c = int(dt_us1 * 1e3) - 4
        if dt_c < 16:
            dt_c = 16
        print('meshing too fine')
    else:
        flag_dt_low = 0

if flag_dt_high == 0:
    if (dt_us > 1 / (3 * guess_freq)) and (flag_dt_low == 0):
        # print(f'dt_us {dt_us}')
        # print(f'low flag = {flag_dt_low}')
        flag_dt_high = 1
        dt_p = copy.deepcopy(dt_us)
        dt_us1 = (1 / 8) * (1 / guess_freq)
        dt_c = int(dt_us1 * 1e3) + 1
        if dt_c < 16:
            dt_c = 16
        print('meshing too coarse')
    else:
        flag_dt_high = 0

if (flag_dt_high == 1 or flag_dt_low == 1):
    # with open('./Pulse_Calibrations/ramsey_time_limits.json', 'w') as f:
    #     if (flag_max_time_high == 1) or    (flag_max_time_low == 1):
    #         time_limits[str(q_no)]['t_max'] = t_max_c
    #     time_limits[str(q_no)]['dt'] = dt_c
    #     json.dump(time_limits, f, indent=6)
    #     f.close()

    with open('./ramsey_redo.json', 'w') as f:
        json.dump({'redo': 1}, f, indent=6)



fit_data_I = [ramsey_fit(i, res_I[0], res_I[1], res_I[2], res_I[3], res_I[4]) for i in t_list_us]

print('#########################')
print('### Fitted Parameters ###')
print('#########################')
print("Ramsey frequency = {0} MHz".format(res_I[3]))
print("Ramsey time = {0} us".format(res_I[1]))
# print('Covariance Matrix')
# print(cov)

ram_t = np.round(res_I[1], 2)
ram_f = np.round(res_I[3], 5)

plt.figure()
plt.plot(t_list_us, I, "-.")
plt.plot(t_list_us, fit_data_I)
plt.xlabel('t (us)')
plt.ylabel("Ramsey Amplitude")
plt.title(f"Ramsey : Ramsey time = {res_I[1]:.2f} us; Ramsey frequency = {res_I[3]:.2f} MHz")
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
plt.grid()
plt.show(block=False)

if save_data:
    file_saver_qubit_(np.transpose([t_list_us, I]), file_name=__file__, suffix=qe, master_folder=ExpName,
                      header_string="Time (us), I", qubit=qe)

with open('ramsey_cache_json.json', 'w') as f:
    json.dump({'det': ram_f}, f)
    f.close()

with open('ramsey_fits.json', 'w') as f:
    json.dump(fit_list, f, indent=6)
    f.close()

with open('../Configuration_Files/Pulse_Calibrations/ramsey_time_limits.json', 'r') as f:
    time_limits = json.load(f)
    f.close()

with open('../Configuration_Files/Pulse_Calibrations/ramsey_time_limits.json', 'w') as f:
    times = {}
    times['t_max'] = res_I[1] * 2 * 5 * 1000
    times['dt'] = dt_c
    times['t_min'] = t_min * 4
    time_limits[str(q_no)] = times
    json.dump(time_limits, f, indent=6)
    f.close()
