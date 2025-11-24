from qm import SimulationConfig
from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
# matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import *

simulate = False

plot_final = True   # Set as true to obtain final plots with data and fit lines
save_data = True      # Set as true for automatic data saving
time_stamp = False     # Set as true to include time stamp in saved files
active_reset = False     # Set as true for resetting qubit with feedback
parallel_experiment = False  # Set as true if you want to play on all qe_s simultaneously
pi_12 = True

n_runs = 1
n_avg = 300
q_no_list = [3, 6]
qubit_IF = [q_IF[str(q_no)] for q_no in q_no_list]
qe = [f"q{q_no}" for q_no in q_no_list]
rr = [f"rr{q_no}" for q_no in q_no_list]
out = [adc_mapping[rr_i] for rr_i in rr]
qubit_IF_orig = qubit_IF

###################
# The QUA program #
###################
t_min = 16//4
t_max = 50000//4  #actual tmax will be twice this
dt = 140//4 #actual step size is twice this to keep ramsey and t1 steps consistent with echo #150//4
det = [0.1 - CrossKerr[str(q_no)]*1e-6 for q_no in q_no_list]  #MHz
t_list = np.arange(t_min, t_max, dt)
t_list_us = 8e-3*t_list #to convert to us with factor two as above

rep_rate_clk = 250000
wait_rr = 16

def do_echo(qe, rr, out, qubit_IF_orig, I, Q, I_st, Q_st, t):

    update_frequency(qe, qubit_IF_orig)
    align(qe, rr)
    wait(rep_rate_clk, qe)
    play_X90(qe)
    wait(t, qe)
    play_X180(qe)
    wait(t, qe)
    play_X90(qe)
    measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

    save(I, I_st)
    save(Q, Q_st)


def do_ramsey(qe, rr, out, qubit_IF, det, I, Q, I_st, Q_st, t):

    align(qe, rr)
    wait(rep_rate_clk, qe)
    update_frequency(qe, qubit_IF + det*1e6)
    play_X90(qe)
    wait(2*t, qe)
    play_X90(qe)
    measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

    save(I, I_st)
    save(Q, Q_st)


def do_T1(qe, rr, out, I, Q, I_st, Q_st, t):

    align(qe, rr)
    wait(rep_rate_clk, qe)
    play_X180(qe)
    wait(2*t, qe)
    measure_macro(qe, rr, out, I, Q, pi_12=pi_12)
    save(I, I_st)
    save(Q, Q_st)


with program() as coherence:

    n = declare(int)

    for q_no in q_no_list:
        vars()[f"I{q_no}"] = declare(fixed)
        vars()[f"Q{q_no}"] = declare(fixed)
        vars()[f"I{q_no}_st"] = declare_stream()
        vars()[f"Q{q_no}_st"] = declare_stream()
    t = declare(int)

    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t < t_max, t + dt):

            if simulate:
                assign(t, 100)

            for i, q_no in enumerate(q_no_list):
                do_ramsey(qe[i], rr[i], out[i], qubit_IF[i], det[i],
                          vars()[f"I{q_no}"], vars()[f"Q{q_no}"], vars()[f"I{q_no}_st"], vars()[f"Q{q_no}_st"], t)
                do_echo(qe[i], rr[i], out[i], qubit_IF_orig[i],
                          vars()[f"I{q_no}"], vars()[f"Q{q_no}"], vars()[f"I{q_no}_st"], vars()[f"Q{q_no}_st"], t)
                do_T1(qe[i], rr[i], out[i],
                          vars()[f"I{q_no}"], vars()[f"Q{q_no}"], vars()[f"I{q_no}_st"], vars()[f"Q{q_no}_st"], t)
                if not parallel_experiment:
                    if q_no != q_no_list[-1]:
                        align(rr[i], qe[i+1])

    with stream_processing():

        for q_no in q_no_list:
            vars()[f"I{q_no}_st"].buffer(len(t_list), 3).average().save(f'I{q_no}')
            vars()[f"Q{q_no}_st"].buffer(len(t_list), 3).average().save(f'Q{q_no}')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
import sys
class Halted(Exception) :
    def __init__(self): sys.tracebacklimit = 0
if hasattr(sys,'tracebacklimit'): del sys.tracebacklimit

if simulate:
    job = qmm.simulate(config, coherence, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()

    raise Halted()

#############
# execution #
#############
qm = qmm.open_qm(config)

coh_list = [[] for q_no in q_no_list]
plt.figure()
for i in range(n_runs):

    print(f"Current Iteration Number : {i}")
    job = qm.execute(coherence)
    res_handles = job.result_handles
    for q_no in q_no_list:
        vars()[f"I{q_no}_handle"] = job.result_handles.get(f"I{q_no}")
        vars()[f"Q{q_no}_handle"] = job.result_handles.get(f"Q{q_no}")
    #job.result_handles.wait_for_all_values()
        vars()[f"I{q_no}_handle"].wait_for_values(1)
        vars()[f"Q{q_no}_handle"].wait_for_values(1)

    # I1_handle.wait_for_values(1)
    # Q1_handle.wait_for_values(1)
    # I2_handle.wait_for_values(1)
    # Q2_handle.wait_for_values(1)

    while res_handles.is_processing():

        plt.clf()
        for q_no in q_no_list:

            vars()[f"I{q_no}"] = vars()[f"I{q_no}_handle"].fetch_all()
            vars()[f"Q{q_no}"] = vars()[f"Q{q_no}_handle"].fetch_all()
            vars()[f"Ir{q_no}"] = vars()[f"I{q_no}"][:, 0]
            vars()[f"Qr{q_no}"] = vars()[f"Q{q_no}"][:, 0]
            vars()[f"Ie{q_no}"] = vars()[f"I{q_no}"][:, 1]
            vars()[f"Qe{q_no}"] = vars()[f"Q{q_no}"][:, 1]
            vars()[f"It{q_no}"] = vars()[f"I{q_no}"][:, 2]
            vars()[f"Qt{q_no}"] = vars()[f"Q{q_no}"][:, 2]

            plt.plot(t_list_us, vars()[f"It{q_no}"], label="T1")
            plt.plot(t_list_us, vars()[f"Ie{q_no}"], label="Echo")
            plt.plot(t_list_us, vars()[f"Ir{q_no}"], label="Ramsey")
        plt.xlabel("Time (us)")
        plt.ylabel(" Amplitude")
        plt.title("Coherence Measurement")
        plt.grid()
        plt.legend()
        plt.pause(0.2)

    for q_no in q_no_list:
        vars()[f"I{q_no}"] = vars()[f"I{q_no}_handle"].fetch_all()
        vars()[f"Q{q_no}"] = vars()[f"Q{q_no}_handle"].fetch_all()
        vars()[f"Ir{q_no}"] = vars()[f"I{q_no}"][:, 0]
        vars()[f"Qr{q_no}"] = vars()[f"Q{q_no}"][:, 0]
        vars()[f"Ie{q_no}"] = vars()[f"I{q_no}"][:, 1]
        vars()[f"Qe{q_no}"] = vars()[f"Q{q_no}"][:, 1]
        vars()[f"It{q_no}"] = vars()[f"I{q_no}"][:, 2]
        vars()[f"Qt{q_no}"] = vars()[f"Q{q_no}"][:, 2]

    def coh_fit(t, A, d, c):

        return A * np.exp(-t/d) + c

    def ramsey_fit(t, A, f, d, p, c):

        return A * np.exp(-t/d) * np.sin(2*np.pi*f*t + p) + c

    def coh_analysis(Ir, Ie, It, Qr, Qe, Qt, q_no, k, verbose=True, plot_final=True, save_data=False):

        pars_r, cov = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=Ir, p0=[1e-3, 0.1, 10, 0, 1e-5], bounds=(-np.inf, np.inf), maxfev=2000)
        pars_e, cov_e = curve_fit(f=coh_fit, xdata=t_list_us, ydata=Ie, p0=[1e-3, 10, 1e-5], bounds=(-np.inf, np.inf), maxfev=2000)
        pars_t, cov_t = curve_fit(f=coh_fit, xdata=t_list_us, ydata=It, p0=[1e-3, 10, 1e-5], bounds=(-np.inf, np.inf), maxfev=2000)

        ram_t = np.round(pars_r[2], 2)
        ram_f = np.round(pars_r[1], 5)
        echo_t = np.round(pars_e[1], 2)
        t1_t = np.round(pars_t[1], 2)
        print(k)
        coh_list[k].append([ram_f, ram_t, t1_t, echo_t])


        if verbose:
            print('#########################')
            print('### Fitted Parameters ###')
            print('#########################')
            print("Ramsey time = {0} us".format(ram_t))
            print("Echo time = {0} us".format(echo_t))
            print("T1 time = {0} us".format(t1_t))

        if plot_final:
            t_list_fit = 8e-3*np.linspace(t_min,t_max,2000)
            plt.figure()
            plt.plot(t_list_fit, ramsey_fit(t_list_fit, *pars_r), linestyle='--', linewidth=2, label = "Ramsey")
            plt.plot(t_list_us, Ir)
            plt.plot(t_list_fit, coh_fit(t_list_fit, *pars_e), linestyle='--', linewidth=2, label = "Echo")
            plt.plot(t_list_us, Ie)
            plt.plot(t_list_fit, coh_fit(t_list_fit, *pars_t), linestyle='--', linewidth=2, label = "T1")
            plt.plot(t_list_us, It)
            plt.xlabel('t (us)')
            plt.ylabel('Signal')
            plt.title(f"Coherence Qubit {q_no}:Ramsey = {ram_t} us , T1 = {t1_t} us , Echo = {echo_t} us")
            plt.grid()
            plt.legend()
            #plt.savefig("../../Experiments/2022-06-06_Cu&Al_Cavity_CoherenceTest/After_Recool/OvernightCoherence_Data/Coh_{0}.png".format(i))
            plt.show()

        if save_data:
            file_saver_(np.transpose([t_list_us, Ir, Qr]), file_name=__file__, suffix=f"Ramsey_{i}_QubitNo-{q_no}",
                        master_folder=ExpName, header_string="Time (us), I, Q", time_stamp=time_stamp)

            file_saver_(np.transpose([t_list_us, It, Qt]), file_name=__file__, suffix=f"T1_{i}_QubitNo-{q_no}",
                        master_folder=ExpName, header_string="Time (us), I, Q", time_stamp=time_stamp)

            file_saver_(np.transpose([t_list_us, Ie, Qe]), file_name=__file__, suffix=f"Echo_{i}_QubitNo-{q_no}",
                        master_folder=ExpName, header_string="Time (us), I, Q", time_stamp=time_stamp)

            file_saver_(coh_list[k], file_name=__file__, suffix=f"CoherenceVals_QubitNo-{q_no}",
                        master_folder=ExpName, header_string="Ramsey freq (MHz), Ramsey(us), T1(us), Echo(us)",
                        time_stamp=time_stamp)


    for k, q_no in enumerate(q_no_list):

        coh_analysis(vars()[f"Ir{q_no}"], vars()[f"Ie{q_no}"], vars()[f"It{q_no}"],
                     vars()[f"Qr{q_no}"], vars()[f"Qe{q_no}"], vars()[f"Qt{q_no}"],
                     q_no, k, verbose=True, plot_final=plot_final, save_data=save_data)