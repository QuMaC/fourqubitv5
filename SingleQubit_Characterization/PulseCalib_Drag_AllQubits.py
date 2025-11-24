"""
An experiment to calibrate the DRAG coefficient: drag_coef
This protocol is described in Reed's thesis (Fig. 5.8) https://rsl.yale.edu/sites/default/files/files/RSL_Theses/reed.pdf
This protocol was also cited in: https://doi.org/10.1103/PRXQuantum.2.040202
"""
from qm.qua import *
from qm import QuantumMachinesManager
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import fetching_tool, progress_counter

from Helper_Functions.analysis_functions import *
from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.macros import *
import json
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
from qm import SimulationConfig
from qualang_tools.loops import from_array
from scipy.optimize import curve_fit

from qualang_tools.units import unit

u = unit()

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

simulate = False
save_data = True
pi_12 = True
type = ""

n_avg = 1e4  # can go as high as 1e4 for extreme accuracy

if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000
wait_rr = 16
wait_q = 4

rabi_pulse = "grft"

# Time Rabi parameters
rabi_amp = 0.25  # was 0.5
n_avg_rabi = 400  # 1000
snr_rabi = 40

##################
# The QUA program #
###################
q_list = [1, 2, 3, 4, 5, 6]
q_list = [4, 5]
for q_no in q_list:
    qe = f"q{q_no}"
    rr = f"rr{q_no}"
    out = adc_mapping[rr]
    ro_len = ro_len_clk[str(q_no)]
    dem = demarcations[f"{q_no}"]
    con = f"con{dac_mapping[qe][0]}"

    # ----------------------------
    # Time-Rabi to find the levels
    # ----------------------------

    # Time Rabi parameters
    pi_len_config = eval(f"{type}pi_len_ns")[f"{q_no}"]
    t_min_ns = pi_len_config  # 16
    t_max_ns = 400
    dt_ns = 4  # minimum 4ns

    t_min = int(t_min_ns / 4)
    t_max = int(t_max_ns / 4)
    dt = int(dt_ns / 4)
    t_list = np.arange(t_min, t_max, dt)

    # --- Start of Time Rabi ---

    ###################
    # The QUA program #
    ###################

    with program() as rabi:

        n = declare(int)

        I = declare(fixed)
        Q = declare(fixed)
        I_st = declare_stream()
        Q_st = declare_stream()

        t = declare(int)
        n_st = declare_stream()

        with for_(n, 0, n < n_avg_rabi, n + 1):
            with for_(t, t_min, t < t_max, t + dt):
                if simulate:
                    assign(t, 100)

                cooldown(time=rep_rate_clk, active_reset=False,
                         qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)
                # reset_phase(rr)
                reset_frame(qe)
                wait(4)

                # play("grft"*amp(rabi_amp), qe, t)
                # play(f"{pulse_type}flat"*amp(rabi_amp), qe, t)
                play(rabi_pulse * amp(rabi_amp), qe, t)

                measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

                save(I, I_st)
                save(Q, Q_st)

            save(n, n_st)

        with stream_processing():
            I_st.buffer(len(t_list)).average().save('I')
            Q_st.buffer(len(t_list)).average().save('Q')

            n_st.save("Iteration")

    ####################
    # Simulate Program #
    ####################

    if simulate:
        job = qmm.simulate(config, rabi, SimulationConfig(int(10000)))
        # get DAC and digital samples
        samples = job.get_simulated_samples()
        # plot all ports:
        # samples.con1.plot()
        samples.con1.plot()

        raise Halted()

    ##################################
    #       Execute on the OPX       #
    ##################################
    qm_rabi = qmm.open_qm(config)
    job_rabi = qm_rabi.execute(rabi)
    results_rabi = fetching_tool(job_rabi, data_list=["Iteration", "I", "Q"], mode="live")

    t_list = 4 * t_list
    fig, axs = plt.subplots(2, 1, sharex=True)
    interrupt_on_close(fig, job_rabi)  # Interrupts the job when closing the figure

    exception_flag = 0

    while results_rabi.is_processing():

        iters, I, Q = results_rabi.fetch_all()
        progress_counter(iters, n_avg_rabi, start_time=results_rabi.get_start_time())
        snr, _ = S2N(I)

        try:
            res_I = fit_cos(t_list, I)
            res_Q = fit_cos(t_list, Q)

            exception_flag = 0
        except:
            exception_flag = 1
            print("Maximum iterations reached for fitting")
            res_I = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }
            res_Q = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }

        data = {"I": [I, res_I], "Q": [Q, res_Q]}
        pi_time = res_I["period"] / 2

        if exception_flag == 0:
            for i, ax in enumerate(axs.flat):
                ax.cla()
                data_label = list(data.keys())[i]
                plot_data = data[data_label]
                fit_func = plot_data[1]["fitfunc"]
                ax.plot(t_list, plot_data[0], marker='.', label=data_label)
                ax.plot(t_list, fit_func(t_list), label=data_label + "_Fit")
                ax.set(xlabel="Time (ns)", ylabel="Rabi Amplitude")
                ax.legend()
                ax.grid()
                ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

            # if snr > snr_rabi:
            #     job_rabi.halt()

            plt.title(f"Q{q_no} SNR = {snr}")
            fig.suptitle(f"Time Rabi : Pi time = {pi_time:.2f} ns  for amp = {rabi_amp}")
            plt.tight_layout()
            plt.pause(0.25)
        else:
            print('Exception while fitting')
    plt.close()

    if exception_flag == 0:
        pi_len = pi_time

        rabi_plot_amp = abs(res_I["amp"])
        I_eq = res_I["offset"]
        I_g = I_eq - rabi_plot_amp
        I_e = I_eq + rabi_plot_amp
        # decay_const = res_I["d"]
        fit_func = res_I["fitfunc"]

        print('######################### \n'
              f'Qubit {q_no} Parameters \n'
              '######################### ')
        # print("Rabi frequency = {0} MHz".format(np.round(1e3*pars[1],2)))
        print(f"Pi pulse = {pi_len:.2f} ns")
        print(f"Rabi plot amplitude = {abs(rabi_plot_amp)}")
        print(f"In arbitrary units: \n "
              f"Ground state [-1] = {I_g} \n "
              f"Equator [0] = {I_eq} \n "
              f"Excited state [+1] = {I_e}")
        # print(f"Rabi decay constant = {abs(decay_const):.2f} us")

        plt.figure()
        plt.plot(t_list, I, ".")
        plt.plot(t_list, fit_func(t_list))
        plt.xlabel("Time (ns)")
        plt.ylabel("Rabi Amplitude")
        plt.title(f"Q{q_no} Time Rabi : Pi pulse = {pi_len:.2f} ns")
        plt.grid()
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        plt.show(block=False)
        # plt.pause(1)
    else:
        print('Exception while fitting')

    # Done with Rabi :)))
    print("# Done with Rabi :)))")

    ###################
    # The QUA program #
    ###################

    best_qubit_T1 = 40 * u.us
    cooldown_time = int(5 * best_qubit_T1 // 4)  # in clock cycles

    a_min = -1.0
    a_max = 1.0
    da = 0.01
    amps = np.arange(a_min, a_max + da / 2, da)  # + da/2 to add a_max to amplitudes

    with program() as drag:
        n = declare(int)
        n_st = declare_stream()
        a = declare(fixed)
        I = declare(fixed)
        Q = declare(fixed)
        I1_st = declare_stream()
        Q1_st = declare_stream()
        I2_st = declare_stream()
        Q2_st = declare_stream()

        with for_(n, 0, n < n_avg, n + 1):
            with for_(*from_array(a, amps)):
                cooldown(time=rep_rate_clk)
                # reset_phase(rr)
                reset_frame(qe)
                wait(4)

                play(f"{type}d_X180" * amp(1, 0, 0, a), qe)
                play(f"{type}d_Y90" * amp(a, 0, 0, 1), qe)

                measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

                save(I, I1_st)
                save(Q, Q1_st)

                align()
                cooldown(time=rep_rate_clk)
                # wait(cooldown_time, rr)
                align()

                play(f"{type}d_Y180" * amp(a, 0, 0, 1), qe)
                play(f"{type}d_X90" * amp(1, 0, 0, a), qe)

                measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

                save(I, I2_st)
                save(Q, Q2_st)
                wait(cooldown_time, rr)
            save(n, n_st)

        with stream_processing():
            I1_st.buffer(len(amps)).average().save("I1")
            Q1_st.buffer(len(amps)).average().save("Q1")
            I2_st.buffer(len(amps)).average().save("I2")
            Q2_st.buffer(len(amps)).average().save("Q2")
            n_st.save("Iteration")

    #####################################
    #  Open Communication with the QOP  #
    #####################################
    qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

    if simulate:
        simulation_config = SimulationConfig(duration=1000)  # in clock cycles
        job = qmm.simulate(config, drag, simulation_config)
        samples = job.get_simulated_samples()
        # plot all ports:
        sim_output = getattr(samples, con)
        sim_output.plot()
        plt.legend("")
        plt.show(block=False)
        raise (Halted)

    qm2 = qmm.open_qm(config)

    job = qm2.execute(drag)
    # Get results from QUA program
    results = fetching_tool(job, data_list=["I1", "I2", "Iteration"], mode="live")

    # Live plotting
    fig = plt.figure()
    interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

    while results.is_processing():
        # Fetch results
        I1, I2, iters = results.fetch_all()

        # Rescale results
        I1 = np.array(I1)
        I2 = np.array(I2)
        I_pair = np.array([I1, I2])
        z_pair = (I_pair - I_eq) / rabi_plot_amp
        state_pair = (z_pair + 1) / 2

        # Progress bar
        progress_counter(iters, n_avg, start_time=results.get_start_time())
        # Plot results
        plt.cla()
        plt.plot(amps, state_pair[0], label="x180y90")
        plt.plot(amps, state_pair[1], label="y180x90")
        plt.xlabel("DRAG coefficient")
        plt.ylabel("State probability")
        plt.title(f"Q{q_no} DRAG calibration")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.pause(0.5)
        plt.show(block=False)
    plt.close()

    # Fetch results
    I1, I2, iter = results.fetch_all()

    # Rescale results
    I1 = np.array(I1)
    I2 = np.array(I2)
    I_pair = np.array([I1, I2])
    z_pair = (I_pair - I_eq) / rabi_amp
    state_pair = (z_pair + 1) / 2

    qm2.close()


    # Analysis

    def linear_fit(x, m, c):
        return m * x + c


    pars1, cov1 = curve_fit(f=linear_fit, xdata=amps, ydata=state_pair[0], p0=[-0.4, 0.5], bounds=(-np.inf, np.inf),
                            maxfev=2000)
    pars2, cov2 = curve_fit(f=linear_fit, xdata=amps, ydata=state_pair[1], p0=[0.4, 0.5], bounds=(-np.inf, np.inf),
                            maxfev=2000)

    opt_drag_coef = np.round((pars1[1] - pars2[1]) / (pars2[0] - pars1[0]), 4)

    print(f"The optimal DRAG coefficient is {opt_drag_coef}")

    plt.figure()

    plt.plot(amps, state_pair[0])
    plt.plot(amps, state_pair[1])
    plt.plot(amps, linear_fit(amps, *pars1), label="x180y90")
    plt.plot(amps, linear_fit(amps, *pars2), label="y180x90")
    plt.axhline(y=0.5, linestyle="--")
    plt.axvline(x=opt_drag_coef, linestyle="--")

    plt.xlabel("DRAG Coefficient")
    plt.ylabel("State probability")
    plt.title(f"Q{q_no} DRAG alpha = {opt_drag_coef}")
    plt.legend()

    plt.tight_layout()
    plt.show(block=False)

    drag_file = open(f'../Configuration_Files/Pulse_Calibrations/{type}drag_dict.json', 'r+')

    drag_dict = json.load(drag_file)

    drag_dict[str(q_no)]['alpha'] *= opt_drag_coef

    drag_file.close()

    drag_file = open(f'../Configuration_Files/Pulse_Calibrations/{type}drag_dict.json', 'w')
    json.dump(drag_dict, drag_file, indent=6)
    drag_file.close()

    if save_data:
        data_name = __file__
        file_saver_qubit_(np.transpose([amps, state_pair[0], state_pair[1]]), file_name=data_name,
                          master_folder=ExpName, header_string="Amps, x180y90, y180x90", qubit=qe,
                          suffix=f"Pulse {type}")
