import json
from qm.qua import *
from qm import SimulationConfig
from qm.QuantumMachinesManager import QuantumMachinesManager
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.plot import interrupt_on_close
from macros import measure_macro, cooldown
from analysis_functions import *
from configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
import copy

simulate = False
save_data = True
pi_12 = False
normalize = True

config_1 = copy.deepcopy(config)
###################
# The QUA program #
###################
q_no = 4
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]

#04C
Ig, Ie = -2.3968283832073213e-06, 1.1652741879224777e-05
Qg, Qe = 3.064022153615952e-05, 3.075984731316566e-05

t_min_ns = 16
t_max_ns = 90000
dt_ns = 60  # minimum 4ns
n_avg = 100000

t_min = int(t_min_ns / 4)
t_max = int(t_max_ns / 4)
dt = int(dt_ns / 4)
t_list = np.arange(t_min, t_max, dt)
dem = 0

if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000
wait_rr = 16

with program() as rabi:
    n = declare(int)
    I1 = declare(fixed)
    Q1 = declare(fixed)
    I2 = declare(fixed)
    Q2 = declare(fixed)
    I12 = declare(fixed)
    Q12 = declare(fixed)
    I1_st = declare_stream()
    Q1_st = declare_stream()
    I2_st = declare_stream()
    Q2_st = declare_stream()
    I12_st = declare_stream()
    Q12_st = declare_stream()
    t = declare(int)
    n_st = declare_stream()

    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t < t_max, t + dt):

            if simulate:
                assign(t, 100)

            cooldown(time=rep_rate_clk, active_reset=False,
                     qe=qe, qe_12=None, rr=rr, out=out, I=I1, Q=Q1, pi_12=False, dem=dem)

            # play_X90(qe)
            measure_macro(qe, rr, out, I1, Q1, pi_12=pi_12)
            save(I1, I1_st)
            save(Q1, Q1_st)

            wait(t, rr)

            measure_macro(qe, rr, out, I2, Q2, pi_12=pi_12)
            save(I2, I2_st)
            save(Q2, Q2_st)

            if normalize:
                assign(I1, (I1 - Ig) / (Ie - Ig))
                assign(Q1, (Q1 - Qg) / (Qe - Qg))
                assign(I2, (I2 - Ig) / (Ie - Ig))
                assign(Q2, (Q2 - Qg) / (Qe - Qg))

            assign(I12, I1 * I2)
            assign(Q12, Q1 * Q2)
            save(I12, I12_st)
            save(Q12, Q12_st)
        save(n, n_st)

    with stream_processing():
        I1_st.buffer(len(t_list)).average().save('I1')
        Q1_st.buffer(len(t_list)).average().save('Q1')
        I2_st.buffer(len(t_list)).average().save('I2')
        Q2_st.buffer(len(t_list)).average().save('Q2')
        I12_st.buffer(len(t_list)).average().save('I12')
        Q12_st.buffer(len(t_list)).average().save('Q12')
        n_st.save("iteration")

####################
# Simulate Program #
####################
qmm = QuantumMachinesManager(host=qm_ip, cluster_name=cluster_name)

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
job = qm.execute(rabi)
results = fetching_tool(job, data_list=["I1", "Q1", "I2", "Q2",
                                        "I12", "Q12", "iteration"], mode="live")

t_list = 4 * t_list
fig, axs = plt.subplots(2, 1, sharex=True)
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

exception_flag = 0

while results.is_processing():

    I1, Q1, I2, Q2, I12, Q12, iteration = results.fetch_all()
    progress_counter(iteration, n_avg, start_time=results.get_start_time())

    try:
        res_I12 = fit_exp(t_list, I12)
        res_Q12 = fit_exp(t_list, Q12)
        exception_flag = 0
    except:
        exception_flag = 1
        print("Maximum iterations reached for fitting")
        res_I12 = {"amp": 0, "decay": 0, "offset": 0}
        res_Q12 = {"amp": 0, "decay": 0, "offset": 0}

    data = {"I12": [I12, res_I12], "Q12": [Q12, res_Q12]}
    decay_time = res_I12["decay"] * 1e-3

    if exception_flag == 0:
        for i, ax in enumerate(axs.flat):
            ax.cla()
            data_label = list(data.keys())[i]
            plot_data = data[data_label]
            fit_func = plot_data[1]["fitfunc"]
            ax.plot(t_list, plot_data[0], marker='.', label=data_label)
            ax.plot(t_list, fit_func(t_list), label=data_label + "_Fit")
            ax.set(xlabel="Time (ns)", ylabel="g(1)(t)")
            ax.legend()
            ax.grid()
            ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

        fig.suptitle(f"G1 Correlator : Decay time = {decay_time:.2f} us")
        plt.pause(0.25)
    else:
        print('Exception while fitting')

if exception_flag == 0:
    I1, Q1, I2, Q2, I12, Q12, iteration = results.fetch_all()
    # ############
    # # analysis #
    # ############
    res_I12 = fit_exp(t_list, I12)
    res_Q12 = fit_exp(t_list, Q12)
    exception_flag = 0
    decay_const = res_I12["decay"]*1e-3
    fit_func = res_I12["fitfunc"]
    Pe = fit_func(0)
    fq = q_LO[f"{q_no}"] + q_IF[f"{q_no}"]

    def qubit_temp(Pe, fq):

        from scipy.constants import h,k

        r = (1.0-Pe)/Pe
        T = h*fq/(k*np.log(r))
        T = np.round(T*1e3, 3)

        return T


    Tq = qubit_temp(Pe, fq)

    print('######################### \n### Fitted Parameters ### \n######################### ')
    # print("Rabi frequency = {0} MHz".format(np.round(1e3*pars[1],2)))
    print(f"Decay Time = {decay_const:.2f} us")
    print(f"Pe = {Pe:.6f}")
    print(f"Qubit Temperature = {Tq} mK")

    plt.figure()
    plt.plot(t_list, I12)
    plt.plot(t_list, fit_func(t_list))
    plt.xlabel("Time (ns)")
    plt.ylabel("g(1)(t)")
    plt.title(f"G1 Correlator : Decay time = {decay_time:.2f} us ; Pe = {fit_func(0):.6f}")
    plt.grid()
    plt.show()


    if save_data:
        file_saver_(np.transpose([t_list, I12, Q12]), file_name=__file__,
                    master_folder=ExpName, header_string="Time (ns), g1(t), g1(t)-badquad")

else:
    print('Exception while fitting')
