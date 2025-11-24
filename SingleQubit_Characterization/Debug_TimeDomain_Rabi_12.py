from qm.qua import *
from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import cooldown, measure_macro

simulate = False
save_data = False
###################
# The QUA program #
###################
t_min_ns = 24
t_max_ns = 1000
dt_ns = 4  # minimum 4ns

t_min = int(t_min_ns / 4)
t_max = int(t_max_ns / 4)
dt = int(dt_ns / 4)
t_list = np.arange(t_min, t_max, dt)

q_no = 6
pi_init = True
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]

# qe_list = ["q1", "q2", "rr1", "rr2"]

if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000
wait_rr = 16

with program() as rabi:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    t = declare(int)

    with for_(n, 0, n < 5000, n + 1):
        with for_(t, t_min, t < t_max, t + dt):

            if simulate:
                assign(t, 100)

            # wait(rep_rate_clk)
            cooldown(time=rep_rate_clk, active_reset=False, qe=qe)
            if pi_init:
                play_X180(qe)
                align(qe, qe_12)
                align('stark_6', qe)
                ramp_to_zero('stark_6')
                align('stark_6', qe_12)
            play("grft" * amp(0.125), qe_12, t)

            align(qe_12, rr)
            wait(wait_rr, rr)

            measure_macro(qe, rr, out, I, Q, pi_12=False)
            # measure("readout", rr, None,
            #         demod.full("integW_cos", I, out),
            #         demod.full("integW_minus_sin", Q, out))
            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('I')
        Q_st.buffer(len(t_list)).average().save('Q')

####################
# Simulate Program #
####################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
if simulate:
    job = qmm.simulate(config, rabi, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con3.plot()
    plt.show(block=False)
    # samples.con2.plot()

    raise Halted()

##################################
#       Execute on the OPX       #
##################################
qm = qmm.open_qm(config)
job = qm.execute(rabi)
res_handles = job.result_handles
I_handle = job.result_handles.get("I")
Q_handle = job.result_handles.get("Q")
# job.result_handles.wait_for_all_values()

t_list = 4 * t_list
plt.figure()
plt.title("Rabi 1-2")
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)
while res_handles.is_processing():
    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    sig = I + 1j * Q
    plt.clf()
    plt.plot(t_list, Q, marker='.', label="Q")
    plt.plot(t_list, I, marker='.',label="I")
    plt.xlabel("Time (ns)")
    plt.ylabel("Rabi Amplitude")
    plt.title("Time Rabi 1-2")
    plt.legend()
    plt.grid()
    # plt.ylim((-0.00015, 0))
    plt.pause(0.25)
    plt.show(block=False)

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

# ############
# # analysis #
# ############
sig = I + 1j * Q


def rabi_fit(t, A, f, d, p, c):
    return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c


pars, cov = curve_fit(f=rabi_fit, xdata=t_list, ydata=I, p0=[3e-3, 0.01, 100, 0, 1e-5], bounds=(-np.inf, np.inf),
                      maxfev=2000)

print('######################### \n### Fitted Parameters ### \n######################### ')
print("Rabi frequency = {0} MHz".format(np.round(1e3 * pars[1], 2)))
print("Pi pulse = {0} ns".format(np.round(0.5 / pars[1], 3)))
print("Rabi amplitude = {0}".format(pars[0]))
print("Rabi decay constant = {0} us".format(pars[2] * 1e-3))

plt.figure()
plt.plot(t_list, I, ".")
plt.plot(t_list, rabi_fit(t_list, *pars))
plt.xlabel("Time (ns)")
plt.ylabel("Rabi Amplitude")
plt.title("Time Rabi")
plt.grid()
plt.show(block=False)

if save_data:
    file_saver_(np.transpose([t_list, np.abs(sig), I, Q]), file_name=__file__,
                master_folder=ExpName, header_string="Frequency (GHz), Magnitude, I, Q")
