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
qe = f"q{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(q_no)]
calib_Y = False
# con = f"con{dac_mapping[qe][0]}"
# "Pi" for calibrating Pi pulses and "Piby2" for calibrating Pi/2 pulses
# First calibrate Pi pulse and then don't change the amplitude ranges For calibrating Pi/2 pulse

##  Load calibrated values

# f = open('Pulse_Calibrations/calib_vals.json','r')
# calib_vals = json.load(f)
# f.close()

a_min = calib_vals[str(q_no)]["amin"]
a_max = calib_vals[str(q_no)]["amax"]
da = calib_vals[str(q_no)]["da"]
n_pulses = calib_vals[str(q_no)]["n_pulses"]


# phi_r = np.arange(phi*0.9, phi*1.1, phi/50)

a_min = 0.01
a_max = 0.99
da = 0.01
n_pulses = 1

for calib in ["Pi"]:
    if calib == "Pi":
        phi = np.arccos(-0.25) / (2 * np.pi)
    else:
        phi = np.arccos(-0.125) / (2 * np.pi)

    if calib == "Piby2":
        a_min = a_min / 2
        a_max = a_max / 2
        da = da / 2

    print(calib)
    print(a_max)

    amps = np.arange(a_min, a_max + da / 2, da)
    peak = True  # if excited state is a peak or trough
    # operation = "grft"

    # operation = "const"
    amp_guess = 0.8
    if calib == "Pi":
        operation = "X180"
        c = 1
        pul_len = pi_len_ns[str(q_no)]
    if calib == "Piby2":
        operation = "X90"
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
        N = n_pulses  # number of pulses
        I = declare(fixed)
        I_st = declare_stream()
        Q = declare(fixed)
        Q_st = declare_stream()
        a = declare(fixed)

        if calib_Y:
            frame_rotation(0.25, qe)

        with for_(n, 0, n < 1200, n + 1):

            if simulate:
                wait(rep_rate_clk, qe)

            else:
                wait(rep_rate_clk - N * (pul_len + c * wait_q) - wait_rr - ro_len, qe)

            frame_rotation_2pi(phi, qe)
            play(operation, qe)
            frame_rotation_2pi(3*phi, qe)
            play(operation, qe)
            play(operation, qe)
            frame_rotation_2pi(phi, qe)
            play(operation, qe)
            wait(wait_q, qe)

            measure_macro(qe, rr, out, I, Q, pi_12=False)
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
    # job.result_handles.wait_for_all_values()

    plt.figure()
    plt.title("Power Rabi")
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
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        plt.pause(0.25)

    I = job.result_handles.get("I").fetch_all()
    Q = job.result_handles.get("Q").fetch_all()


    ############
    # analysis #
    ############
    def rabi_fit(t, A, f, d, p, c):

        return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c


    pars, cov = curve_fit(f=rabi_fit, xdata=amps, ydata=I, p0=[5e-4, c * N * amp_guess, 300, 0, 1e-5],
                          bounds=(-np.inf, np.inf), maxfev=5000)

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
    plt.title(f"Power Rabi : {calib} amp = {pi_amp} ; N = {N}")
    plt.axvline(pi_amp)
    plt.legend()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.grid()
    plt.show()

    amp_file = open('../Configuration_Files/Pulse_Calibrations/amp_scale.json', 'r+')

    amp_scale = json.load(amp_file)

    # if calib == "Pi":
    #     amp_scale[str(q_no)]['X180'] = pi_amp
    #     amp_scale[str(q_no)]['Y180'] = pi_amp
    # elif calib == "Piby2":
    #     amp_scale[str(q_no)]['X90'] = pi_amp
    #     amp_scale[str(q_no)]['Y90'] = pi_amp
    #
    # json.dump(amp_scale,amp_file,indent=6)
    #
    # amp_file.close()
