import json
from qm.qua import *
from qm import SimulationConfig
from qm import QuantumMachinesManager
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.plot import interrupt_on_close
from Helper_Functions.macros import measure_macro, cooldown  # , play_cmd What's this?
from Helper_Functions.analysis_functions import *
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
import copy
import time

simulate = False
save_data = True
pi_12 = False

config_1 = copy.deepcopy(config)
##################
# The QUA program #
##################
q_no = 1
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]
pi_len_config = pi_len_ns[f"{q_no}"]

t_min_ns = 16
t_max_ns = 5000
dt_ns = 16  # minimum 4ns
rabi_amp = 0.1
n_avg = 300
n_runs = 100

t_min = int(t_min_ns / 4)
t_max = int(t_max_ns / 4)
dt = int(dt_ns / 4)
t_list = np.arange(t_min, t_max, dt)
dem = 3.123e-05

if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000
wait_rr = 16

with program() as rabi:
    n = declare(int)
    I = declare(fixed)
    Q = declare(fixed)
    I_st = declare_stream()
    Q_st = declare_stream()
    t = declare(int)
    n_st = declare_stream()

    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t < t_max, t + dt):
            # reset_frame(rr)
            if simulate:
                assign(t, 100)

            cooldown(time=rep_rate_clk, active_reset=False,
                     qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)

            play("grft" * amp(rabi_amp), qe, t)
            # play_X180(qe, a=amp(rabi_amp), t=t)
            # reset_frame(rr)
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)
            save(I, I_st)
            save(Q, Q_st)
        save(n, n_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('I')
        Q_st.buffer(len(t_list)).average().save('Q')
        n_st.save("iteration")

####################
# Simulate Program #
####################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

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
qm = qmm.open_qm(config)

zero_one_levels = []

start_time = [time.localtime()[3], time.localtime()[4], time.localtime()[5]]
print(start_time)
t0 = time.time_ns()

date_time = time.localtime()[3:6]

with open(f'./long_term_rabi/rabi_level_data_{q_no}_{date_time[0]}_{date_time[1]}_{date_time[2]}.csv', 'w') as f:
    w_data = ['Time', 'level_0', 'level_1', 'pi_time_est']
    f.write(",".join(map(str, w_data)) + "\n")
    f.close()

t_list = 4 * t_list

for i in range(n_runs):

    t_iter = time.time_ns()

    print(f'Current iteration = {i}')

    job = qm.execute(rabi)
    results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")


    fig, axs = plt.subplots(2, 1, sharex=True)
    interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

    exception_flag = 0

    while results.is_processing():

        I, Q, iteration = results.fetch_all()
        progress_counter(iteration, n_avg, start_time=results.get_start_time())

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

            fig.suptitle(f"Time Rabi : Pi time = {pi_time:.2f} ns  for amp = {rabi_amp}")
            plt.tight_layout()
            plt.pause(0.25)
        else:
            print('Exception while fitting')

    if exception_flag == 0:
        I, Q, iteration = results.fetch_all()
        # ############
        # # analysis #
        # ############
        res_I = fit_cos(t_list, I)
        res_Q = fit_cos(t_list, Q)
        pi_len = res_I["period"] / 2
        rabi_plot_amp = res_I["amp"]
        # decay_const = res_I["d"]
        fit_func = res_I["fitfunc"]
        rabi_freq = res_I["freq"]

        plt.close()

        print('######################### \n### Fitted Parameters ### \n######################### ')
        # print("Rabi frequency = {0} MHz".format(np.round(1e3*pars[1],2)))
        print(f"Pi pulse = {pi_len:.2f} ns")
        print(f"Rabi plot amplitude = {abs(rabi_plot_amp)}")
        # print(f"Rabi decay constant = {abs(decay_const):.2f} us")
        print(f"Guess amp for Power Rabi = {rabi_amp * (pi_len / pi_len_config):.3f}")
        print(f"Rabi frequency = {1e3 * rabi_freq:.3f} MHz")

        # plt.figure()
        # plt.plot(t_list, I, ".")
        # plt.plot(t_list, fit_func(t_list))
        # plt.xlabel("Time (ns)")
        # plt.ylabel("Rabi Amplitude")
        # plt.title(
        #     f"Q{q_no} Time Rabi : Pi pulse = {pi_len:.2f} ns ; Guess amp= {rabi_amp * (pi_len / pi_len_config):.3f}")
        # plt.grid()
        # plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        # plt.show()

        # calib_vals_file = open('Pulse_Calibrations/calib_vals.json','r')
        # calib_vals = json.load(calib_vals_file)
        # calib_vals_file.close()
        #
        # calib_vals[f'{q_no}']['amin'] = rabi_amp*(pi_len/pi_len_config) * 0.8
        # calib_vals[f'{q_no}']['amax'] = rabi_amp*(pi_len/pi_len_config) * 1.2
        # calib_vals[f'{q_no}']['da'] = 0.0001
        # calib_vals[f'{q_no}']['n_pulses'] = 5
        #
        # calib_vals_file = open('Pulse_Calibrations/calib_vals.json','w')
        # json.dump(calib_vals, calib_vals_file, indent = 6)
        # calib_vals_file.close()

        if save_data:
            file_saver_(np.transpose([t_list, I, Q]), file_name=__file__,
                        master_folder=ExpName, header_string="Frequency (GHz), Magnitude, I, Q")


    else:
        print('Exception while fitting')

    levels_0 = res_I['offset'] - abs(res_I['amp'])
    levels_1 = res_I['offset'] + abs(res_I['amp'])

    with open(f'./long_term_rabi/rabi_level_data_{q_no}_{date_time[0]}_{date_time[1]}_{date_time[2]}.csv', 'a') as f:
        w_data = [np.round((t_iter - t0)/1e9, 5), levels_0, levels_1, np.round(pi_time, 5)]
        f.write(",".join(map(str, w_data)) + "\n")
        f.close()

    # with open('../Configuration_Files/System_Parameters/01_levels.json','r') as f:
    #     levels = json.load(f)
    #     f.close()
    #
    # levels_01 = levels[qe]
    #
    # levels_01["0"] = res_I['offset'] - abs(res_I['amp'])
    # levels_01["1"] = res_I['offset'] + abs(res_I['amp'])
    #
    # levels[qe] = levels_01
    #
    # with open('../Configuration_Files/System_Parameters/01_levels.json','w') as f:
    #     json.dump(levels, f, indent=6)
    #     f.close()
