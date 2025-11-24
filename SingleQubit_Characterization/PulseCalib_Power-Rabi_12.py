from qm import SimulationConfig
from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.macros import *
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')

simulate = False

###################
# The QUA program #
##################
q_no = 5
qe = f"q{q_no}"
qe12 = f"q12_{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(q_no)]
calib = "Pi"
calib = "Piby2"
calib_Y = False
# "Pi" for calibrating Pi pulses and "Piby2" for calibrating Pi/2 pulses
# First calibrate Pi pulse and then don't change the amplitude ranges For calibrating Pi/2 pulse

a_min = 0.20226363181590795 * 0.9
a_max = 0.20226363181590795 * 1.1
da = 0.001
n_pulses = 5

# a_min = 0.01
# a_max = 0.99
# da = 0.01
# n_pulses = 1

if calib == "Piby2":
    a_min = a_min / 2
    a_max = a_max / 2
    da = da / 2

amps = np.arange(a_min, a_max + da / 2, da)
peak = True  # if excited state is a peak or trough
operation = "grft"
amp_guess = 0.3

if calib == "Pi":
    c = 1
    pul_len = pi_len_ns[str(q_no)]
if calib == "Piby2":
    c = 2  # Factor for computing initial guess for decaying sinusoid fit
    pul_len = piby2_len_ns[str(q_no)]

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
    # N = n_pulses # number of pulses
    I = declare(fixed)
    assign(N, n_pulses)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    a = declare(fixed)

    if calib_Y:
        frame_rotation(0.25, qe)

    with for_(n, 0, n < 1000, n + 1):
        with for_(a, a_min, a < a_max + da / 2, a + da):
            cooldown(time=rep_rate_clk, active_reset=False, qe=qe)

            # reset_frame(qe)
            # reset_frame(qe12)
            # reset_frame(rr)

            play_X180(qe)
            # wait(wait_q, qe)
            align(qe, qe12)

            with for_(i, 0, i < N, i + 1):
                play(operation * amp(a), qe12)
                wait(wait_q, qe12)
                if calib == "Piby2":
                    play(operation * amp(a), qe12)
                    wait(wait_q, qe12)
            align(qe12, rr)
            wait(wait_rr, rr)
            measure_macro(qe12, rr, out, I, Q, pi_12=False)
            # measure("readout", rr, None,
            #         demod.full("integW_cos", I, out),
            #         demod.full("integW_minus_sin", Q, out))
            save(I, I_st)
            save(Q, Q_st)


    with stream_processing():
        I_st.buffer(len(amps)).average().save('I')
        Q_st.buffer(len(amps)).average().save('Q')

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
    samples.con3.plot()
    plt.show(block=False)
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
# job.result_handles.wait_for_all_values()

plt.figure()
plt.title("Power Rabi 1-2")
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)
while res_handles.is_processing():
    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    sig = I + 1j * Q
    plt.clf()
    plt.plot(amps, I)
    plt.xlabel("Pulse Amplitude")
    plt.ylabel("Rabi Amplitude")
    plt.grid()
    plt.pause(0.25)

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()


############
# analysis #
############
def rabi_fit(t, A, f, d, p, c):
    return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c


pars, cov = curve_fit(f=rabi_fit, xdata=amps, ydata=I, p0=[5e-4, c * n_pulses * amp_guess, 300, 0, 1e-4],
                      bounds=(-np.inf, np.inf), maxfev=2000)

amp_arr = np.linspace(a_min, a_max, 2000)
find_amp = rabi_fit(amp_arr, *pars)
if peak:
    pi_amp = amp_arr[np.argmax(find_amp)]
else:
    pi_amp = amp_arr[np.argmin(find_amp)]

print('#########################')
print('### Fitted Parameters ###')
print('#########################')
print("Rabi frequency = {0} per amp".format(np.round(pars[1], 2)))
print("{0} pulse amplitude = {1}".format(calib, pi_amp))
# print("Pi pulse amplitude = {0}".format(N*0.5/pars[1]))
# print('Covariance Matrix')
# print(cov)

plt.figure()
plt.plot(amps, I, ".", label="I")
plt.plot(amps, rabi_fit(amps, *pars))
plt.xlabel("Drive Amplitude")
plt.ylabel("Rabi Amplitude")
plt.title(f"Power Rabi 1-2 : {calib} amp = {pi_amp} ; N = {n_pulses}")
plt.axvline(pi_amp)
plt.legend()
plt.grid()
plt.show(block=False)
