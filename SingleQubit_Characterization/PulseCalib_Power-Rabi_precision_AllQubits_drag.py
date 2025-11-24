import sys
from qualang_tools.plot import interrupt_on_close
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
from qualang_tools.results import progress_counter, fetching_tool

simulate = False
save_data = True
pi_12 = True

##################
# The QUA program #
###################
q_list = [1, 2, 3, 4, 5, 6]
q_list = [2, 5]


func_dict = {
    "X180": play_X180,
    "Y180": play_Y180,
    "X90": play_X90,
    "mX90": play_mX90,
    "Y90": play_Y90,
    "mY90": play_mY90,
    'I': play_I,
}

for q_no in q_list:
    qe = f"q{q_no}"
    rr = f"rr{q_no}"
    out = adc_mapping[rr]
    ro_len = ro_len_clk[str(q_no)]
    calib = "Pi"
    # calib = "Piby2"
    calib_Y = False
    # con = f"con{dac_mapping[qe][0]}"
    # "Pi" for calibrating Pi pulses and "Piby2" for calibrating Pi/2 pulses
    # First calibrate Pi pulse and then don't change the amplitude ranges For calibrating Pi/2 pulse

    ##  Load calibrated values

    f = open('../Configuration_Files/Pulse_Calibrations/amp_scale.json', 'r')
    calib_vals = json.load(f)
    f.close()

    I_data = {}
    fit_data = {}

    n_avg = 200

    a_min = calib_vals[str(q_no)]["X180"] * 0.97
    a_max = calib_vals[str(q_no)]["X180"] * 1.03
    da = calib_vals[str(q_no)]["X180"] * 0.06 / 1250
    n_pulses = 25  # Change this line to whatever u feel is right
    #
    # a_min = 0.01 #0.6
    # a_max = 0.99
    # da = 0.01 #0.001
    # n_pulses = 1 #5  #3

    # a_min = 0.01 #0.6
    # a_max = 0.6
    # da = 0.002 #0.001

    # n_pulses = 1  #3

    for calib in ["X180", "X90", "Y180", "Y90"]:
        # for calib in ["X90", "Y90"]:

        a_min = calib_vals[str(q_no)]["X180"] * 0.97
        a_max = calib_vals[str(q_no)]["X180"] * 1.03
        da = calib_vals[str(q_no)]["X180"] * 0.06 / 1250
        n_pulses = 25  # Change this line to whatever u feel is right

        if "90" in calib:
            a_min = calib_vals[str(q_no)]["X90"] * 0.97
            a_max = calib_vals[str(q_no)]["X90"] * 1.03
            da = calib_vals[str(q_no)]["X90"] * 0.06 / 1250

        a_min = 0.97
        a_max = 1.03
        da = 0.06/1250

        if "Y" in calib:
            calib_Y = True

        print(calib)
        # print(a_max)

        amps = np.arange(a_min, a_max + da / 2, da)
        peak = True  # if excited state is a peak or trough
        operation = "grft"
        operation = "d_" + calib

        amp_guess = (a_min + a_max) / 2
        if "180" in calib:
            c = 1
            pul_len = pi_len_ns[str(q_no)]

        if "90" in calib:
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
            n_st = declare_stream()

            if calib_Y:
                frame_rotation(0.25, qe)

            with for_(n, 0, n < n_avg, n + 1):
                with for_(a, a_min, a < a_max + da / 2, a + da):
                    cooldown(time=rep_rate_clk, active_reset=False,
                             qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=0)

                    reset_frame(qe)
                    wait(4, qe)

                    if simulate:
                        wait(rep_rate_clk, qe)

                    else:
                        wait(rep_rate_clk - N * (pul_len + c * wait_q) - wait_rr - ro_len, qe)

                    with for_(i, 0, i < N, i + 1):
                        # play(operation * amp(a), qe)
                        func_dict[calib](qe, a = a)
                        wait(wait_q, qe)
                        if "90" in calib:
                            # play(operation * amp(a), qe)
                            func_dict[calib](qe, a=a)
                            wait(wait_q, qe)

                    # align(qe, 'stark_6')
                    # ramp_to_zero('stark_6')
                    # align(qe, 'stark_6')


                    measure_macro_no_ramp(qe, rr, out, I, Q, pi_12=True)
                    save(I, I_st)
                    save(Q, Q_st)
                save(n, n_st)

            with stream_processing():
                I_st.buffer(len(amps)).average().save('I')
                Q_st.buffer(len(amps)).average().save('Q')
                n_st.save("iteration")

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
            sim_output = getattr(samples, con1)
            sim_output.plot()
            plt.legend("")

            raise Halted()

        #############
        # execution #
        #############
        qm = qmm.open_qm(config)
        job = qm.execute(power_rabi)
        # res_handles = job.result_handles
        results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")
        # I_handle = job.result_handles.get("I")
        # Q_handle = job.result_handles.get("Q")

        fig, axs = plt.subplots()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figureobs
        # job.result_handles.wait_for_all_values()

        # plt.figure()

        # I_handle.wait_for_values(1)
        # Q_handle.wait_for_values(1)
        while results.is_processing():
            #
            # I = I_handle.fetch_all()
            # Q = Q_handle.fetch_all()
            I, Q, iteration = results.fetch_all()
            progress_counter(iteration, n_avg, start_time=results.get_start_time())
            # sig = I + 1j * Q
            axs.cla()
            axs.plot(amps, I)
            axs.set(xlabel="Pulse Amplitude", ylabel="Rabi Amplitude")
            axs.grid()
            axs.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
            snr, _ = S2N(I)
            if snr > 15:
                job.halt()
            plt.pause(0.25)
            fig.suptitle(f"Power Rabi: {calib} qubit = {q_no}")
            plt.tight_layout()
            plt.pause(0.25)
            plt.show(block=False)

        plt.close(fig)
        I = job.result_handles.get("I").fetch_all()
        Q = job.result_handles.get("Q").fetch_all()

        bnds = ([0, 0, -np.pi, -np.inf], [np.inf, np.inf, np.pi, np.inf])


        ############
        # analysis #
        ############
        def rabi_fit(t, A, f, p, c):

            return A * np.sin(2 * np.pi * f * t + p) + c


        def para_fit(x, temp4, temp3, temp2, temp1, temp0):
            return temp4 * x ** 4 + temp3 * x ** 3 + temp2 * x ** 2 + temp1 * x + temp0


        para_fit_val = np.polyfit(amps, I, 4)

        # init_guess = []

        # pars, cov = curve_fit(f=rabi_fit, xdata=amps, ydata=I, p0=[5e-4, c * N * amp_guess, 0, 1e-5], bounds=bnds,
        #                       maxfev=5000)

        amp_arr = np.linspace(a_min, a_max, 2000)

        find_amp = para_fit(amp_arr, *para_fit_val)

        if peak:
            pi_amp = amp_arr[np.argmax(find_amp)]
        else:
            pi_amp = amp_arr[np.argmin(find_amp)]

        fit_data1 = {
            'power0': para_fit_val[0],
            'power1': para_fit_val[1],
            'power2': para_fit_val[2],
            'power3': para_fit_val[3],
            'power4': para_fit_val[4],
            'gate_amp': pi_amp
        }

        fit_data.update({calib: fit_data1})

        print('#########################')
        print('### Fitted Parameters ###')
        print('#########################')
        # print("Rabi frequency = {0} per amp".format(np.round(pars[1], 2)))
        print(f"{calib} pulse amplitude = {pi_amp}")
        # print("180 pulse amplitude = {0}".format(N*0.5/pars[1]))
        # print('Covariance Matrix')
        # print(cov)

        plt.figure()
        plt.plot(amps, I, ".", label="I")
        plt.plot(amps, para_fit(amps, *para_fit_val))
        plt.xlabel("Drive Amplitude")
        plt.ylabel("Rabi Amplitude")
        plt.title(f"qubit = {q_no} Power Rabi : {calib} amp = {pi_amp} ; N = {n_pulses}")
        plt.axvline(pi_amp)
        plt.legend()
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        plt.grid()
        plt.show(block=False)

        amp_file = open('../Configuration_Files/Pulse_Calibrations/amp_scale.json', 'r+')

        amp_scale = json.load(amp_file)

        amp_scale[str(q_no)][calib] = pi_amp * amp_scale[str(q_no)][calib]

        amp_file.close()

        amp_file = open('../Configuration_Files/Pulse_Calibrations/amp_scale.json', 'w')
        json.dump(amp_scale, amp_file, indent=6)
        amp_file.close()

        # I_data.update({calib: I})
        #
        # with open('../fourqubitv4 (Under Construction)/power_rabi_fit.json', 'w') as f:
        #     json.dump(fit_data, f, indent=6)
        #     f.close

        # with open('./power_rabi_data.json', 'w') as f:
        #     json.dump(fit_data,f,indent=6)
        #     f.close

        if save_data:
            data_name = __file__
            file_saver_qubit_(np.transpose([amps, I]), file_name=data_name, suffix=calib,
                              master_folder=ExpName, header_string="Amps, I", qubit=qe)
