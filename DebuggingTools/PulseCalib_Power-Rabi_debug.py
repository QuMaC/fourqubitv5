from qm import SimulationConfig
# from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import json
from Helper_Functions.macros import *
import matplotlib

matplotlib.use('Qt5Agg')

simulate = False

##################
# The QUA program #
###################
q_no = 2
q_spec = 1

qe_s = f"q{q_spec}"
qe = f"q{q_no}"
rr = f"rr{q_no}"
rr_s = f"rr{q_spec}"
out = adc_mapping[rr]
out_s = adc_mapping[rr_s]
ro_len = ro_len_clk[str(q_no)]
calib_Y = False
# con = f"con{dac_mapping[qe][0]}"
# "Pi" for calibrating Pi pulses and "Piby2" for calibrating Pi/2 pulses
# First calibrate Pi pulse and then don't change the amplitude ranges For calibrating Pi/2 pulse

##  Load calibrated values

# f = open('../Configuration_Files/Pulse_Calibrations/calib_vals.json','r')
# calib_vals = json.load(f)
# f.close()



a_min = 0.01
a_max = 0.99
da = 0.01
n_pulses = 1

amps = np.arange(a_min, a_max + da / 2, da)
peak = True  # if excited state is a peak or trough
operation = "grft"
# operation = "const"
amp_guess = 0.8

c = 1
pul_len = pi_len_ns[str(q_no)]


if simulate:
    rep_rate_clk = 100
else:
    rep_rate_clk = 250000
wait_rr = 16
wait_q = 4

with program() as power_rabi:
    n = declare(int)
    i = declare(int)
    N = declare(int)
    # N = n_pulses  # number of pulses
    I = declare(fixed)
    Is = declare(fixed)
    assign(N, n_pulses)
    I_st = declare_stream()
    Is_st = declare_stream()
    Q = declare(fixed)
    Qs = declare(fixed)
    Q_st = declare_stream()
    Qs_st = declare_stream()
    a = declare(fixed)

    if calib_Y:
        frame_rotation(0.25, qe)

    with for_(n, 0, n < 1200, n + 1):
        with for_(a, a_min, a < a_max + da / 2, a + da):

            if simulate:
                wait(rep_rate_clk, qe)

            else:
                wait(rep_rate_clk - n_pulses * (pul_len + c * wait_q) - wait_rr - ro_len, qe)

            with for_(i, 0, i < N, i + 1):
                play(operation * amp(a), qe)
                wait(wait_q, qe)
            align(qe, rr, qe_s, rr_s)
            measure_macro(qe, rr, out, I, Q, pi_12=False)
            wait(400, rr_s)
            align(qe, rr, qe_s, rr_s)
            measure_macro(qe_s, rr_s, out_s, Is, Qs, pi_12=False)
            save(I, I_st)
            save(Q, Q_st)
            save(Is, Is_st)
            save(Qs, Qs_st)

    with stream_processing():
        I_st.buffer(len(amps)).average().save('I')
        Q_st.buffer(len(amps)).average().save('Q')
        Is_st.buffer(len(amps)).average().save('Is')
        Qs_st.buffer(len(amps)).average().save('Qs')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
if simulate:
    job = qmm.simulate(config, power_rabi, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    sim_output = getattr(samples, con)
    sim_output.plot()
    plt.legend("")

    raise Halted()

#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(power_rabi)
res_handles = job.result_handles
I_handle = job.result_handles.get("I")
Q_handle = job.result_handles.get("Q")
Is_handle = job.result_handles.get("Is")
Qs_handle = job.result_handles.get("Qs")
# job.result_handles.wait_for_all_values()

plt.ion()
fig, ax = plt.subplots(2)
# plt.title("Power Rabi")
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)

fig.suptitle(f"Power Rabi on {qe} with readout on both {qe} and {qe_s}")
lines = []
tc = ["Rabi", "spectator"]
q_no = [qe[-1], qe_s[-1]]

for i in range(2):
    lines.append(ax[i].plot(amps, [0] * len(amps), marker=".", label="0")[0])  # Returns a tuple of line objects, thus the comma
    # lines.append(ax[i].plot(4e-3 * t_list, [0]*len(t_list), marker=".", label="1")[0])  # Returns a tuple of line objects, thus the comma
    ax[i].set_title(tc[i] + f" Q{q_no[i]}")
    ax[i].set_ylabel("Rabi Amplitude")
    ax[i].grid()
    ax[i].legend()

ax[1].set_xlabel("Amplitude")

while res_handles.is_processing():
    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    Is = Is_handle.fetch_all()
    Qs = Qs_handle.fetch_all()
    # sig = I + 1j * Q
    I_data = [I, Is]

    for i in range(1):
        lines[2 * i].set_ydata(I_data[2 * i])
        lines[2 * i + 1].set_ydata(I_data[2 * i + 1])
        ax[i].relim()
        ax[i + 1].relim()
        ax[i].autoscale_view()
        ax[i + 1].autoscale_view()
        fig.set_tight_layout(True)
        fig.canvas.draw()
        fig.canvas.flush_events()

    plt.pause(1)
    # plt.clf()
    # plt.plot(amps, I)
    # plt.xlabel("Pulse Amplitude")
    # plt.ylabel("Rabi Amplitude")
    # plt.grid()
    # plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    # plt.pause(0.25)
#
# I = job.result_handles.get("I").fetch_all()
# Q = job.result_handles.get("Q").fetch_all()
#
#
# ############
# # analysis #
# ############
# def rabi_fit(t, A, f, d, p, c):
#
#     return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c
#
#
# pars, cov = curve_fit(f=rabi_fit, xdata=amps, ydata=I, p0=[5e-4, c * n_pulses * amp_guess, 300, 0, 1e-5],
#                       bounds=(-np.inf, np.inf), maxfev=5000)
#
# amp_arr = np.linspace(a_min, a_max, 2000)
# find_amp = rabi_fit(amp_arr, *pars)
# if peak:
#     pi_amp = amp_arr[np.argmax(find_amp)]
# else:
#     pi_amp = amp_arr[np.argmin(find_amp)]
#
# print('#########################')
# print('### Fitted Parameters ###')
# print('#########################')
# print("Rabi frequency = {0} per amp".format(np.round(pars[1], 2)))
# print("{0} pulse amplitude = {1}".format(calib, pi_amp))
# # print("Pi pulse amplitude = {0}".format(N*0.5/pars[1]))
# # print('Covariance Matrix')
# # print(cov)
#
# plt.figure()
# plt.plot(amps, I, ".", label="I")
# plt.plot(amps, rabi_fit(amps, *pars))
# plt.xlabel("Drive Amplitude")
# plt.ylabel("Rabi Amplitude")
# plt.title(f"Power Rabi : {calib} amp = {pi_amp} ; N = {n_pulses}")
# plt.axvline(pi_amp)
# plt.legend()
# plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
# plt.grid()
# plt.show()
#
