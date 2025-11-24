from qm.qua import *
from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from Helper_Functions.analysis_functions import *
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.constants import h,k
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

qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]


temp_possible = True

qe_list = ["q1", "q2", "rr1", "rr2"]

if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000
wait_rr = 16

rabi_params = []

t_list = 4 * t_list
for pi_init in [True, False]:

    # pi_init = True

    with program() as rabi:
        n = declare(int)
        I = declare(fixed)
        I_st = declare_stream()
        Q = declare(fixed)
        Q_st = declare_stream()
        t = declare(int)

        with for_(n, 0, n < 1000, n + 1):
            with for_(t, t_min, t < t_max, t + dt):

                if simulate:
                    assign(t, 100)

                # wait(rep_rate_clk)
                cooldown(time=rep_rate_clk, active_reset=False, qe=qe)
                if pi_init:
                    play_X180(qe)
                    align(qe, qe_12)
                play("grft" * amp(0.125), qe_12, t)
                align(qe_12, rr)
                wait(wait_rr, rr)
                # measure("readout", rr, None,
                #         demod.full("integW_cos", I, out),
                #         demod.full("integW_minus_sin", Q, out))
                measure_macro(qe, rr, out, I, Q, pi_12=False)
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
        samples.con1.plot()
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


    plt.figure()
    plt.title("Rabi 1-2")
    I_handle.wait_for_values(1)
    Q_handle.wait_for_values(1)
    while res_handles.is_processing():
        I = I_handle.fetch_all()
        Q = Q_handle.fetch_all()
        sig = I + 1j * Q
        plt.clf()
        # plt.plot(t_list, Q, marker='.', label="Q")
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


    res_I = fit_cos(t_list[20:], I[20:])


    # pars, cov = curve_fit(f=rabi_fit, xdata=t_list, ydata=I, p0=[3e-3, 0.01, 100, 0, np.mean(I)], bounds=(-np.inf, np.inf),
    #                       maxfev=2000)

    rabi_params.append(res_I)

    print('######################### \n### Fitted Parameters ### \n######################### ')
    print("Rabi frequency = {0} MHz".format(np.round(1e3 * res_I['freq'], 2)))
    print("Pi pulse = {0} ns".format(np.round(0.5 / res_I['freq'], 3)))
    print("Rabi amplitude = {0}".format(res_I['amp']))
    # print("Rabi decay constant = {0} us".format(pars[2] * 1e-3))


    plt.figure()
    plt.plot(t_list, I, ".")
    plt.plot(t_list, res_I['fitfunc'](t_list))
    plt.xlabel("Time (ns)")
    plt.ylabel("Rabi Amplitude")
    plt.title("Time Rabi")
    plt.grid()
    plt.show(block=False)


    if save_data:
        file_saver_(np.transpose([t_list, np.abs(sig), I, Q]), file_name=__file__,
                    master_folder=ExpName, header_string="Frequency (GHz), Magnitude, I, Q")

# pars

# if abs(rabi_params[0]['freq'] / rabi_params[1]['freq']) > 3 or abs(rabi_params[0]['freq'] / rabi_params[1]['freq']) < 0.3333:
f, amps = fft_func(t_list[20:], I[20:])

f_rabi = np.where(f > rabi_params[0]['freq'])[0][0]

A0 = amps[f_rabi]/len(f)

f0 = q_LO[f'{q_no}'] + q_IF[f'{q_no}']

Api = abs(rabi_params[0]['amp'])

r = A0/(Api+A0)

T = -h*f0/(k*np.log(r))

print(f"Qubit {q_no} Temperature = {(np.round(T*1e3, 3))} mK")
