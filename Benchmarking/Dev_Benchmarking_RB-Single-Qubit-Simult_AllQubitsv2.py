from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
from qm.qua import *
from scipy.optimize import curve_fit
from Helper_Functions.macros import measure_macro
from Helper_Functions.RB_helper_functions import *

n_iter = 1
n_qubits = 6
avgs = 200
wait_init = 250000
wait_t = 4
wait_rr = 8

time_stamp = True
simulate = True
lsb = False
pi_12 = True

max_circuit_depth = 400
delta_depth = 1  # must be 1!!
num_of_sequences = 10 #50
seed = 345323#   345324


q_no_list = [i+1 for i in range(n_qubits)]
q_no_list = [1]
n_qubits = len(q_no_list)
qe_list, rr_list, out_list = [], [], []
q_index = {}
for q_i in q_no_list:

    q_index[f"{q_i}"] = q_no_list.index(q_i)
    qe_list.append(f"q{q_i}")
    rr = f"rr{q_i}"
    rr_list.append(rr)
    out_list.append(adc_mapping[rr])


if simulate:
    wait_init = 100
    avgs = 3

with program() as rb:

    depth = declare(int)
    m = declare(int)
    n = declare(int)

    for i, q_i in enumerate(q_no_list):
        vars()[f"saved_gate_{i}"] = declare(int)

    I = declare(fixed, size=n_qubits)
    Q = declare(fixed, size=n_qubits)

    for q_i in q_no_list:
        vars()[f"I{q_i}_st"] = declare_stream()
        vars()[f"Q{q_i}_st"] = declare_stream()

    with for_(m, 0, m < num_of_sequences, m+1):

        for i, q_i in enumerate(q_no_list):
            vars()[f"sequence_list_{i}"], vars()[f"inv_gate_list_{i}"] = generate_sequence(max_circuit_depth, seed+i)

        with for_(depth, 1, depth <= max_circuit_depth, depth+delta_depth):

            with for_(n, 0, n < avgs, n+1):

                for i, q_i in enumerate(q_no_list):
                    assign(eval(f"saved_gate_{i}"), eval(f"sequence_list_{i}")[depth])
                    assign(eval(f"sequence_list_{i}")[depth], eval(f"inv_gate_list_{i}")[depth - 1])
                wait(wait_init)
                for q_i in q_no_list:

                    # reset_phase(rr_list[q_index[f"{q_i}"]])
                    # wait(wait_init, qe_list[q_index[f"{q_i}"]], rr_list[q_index[f"{q_i}"]])
                    play_sequence(qe_list[q_index[f"{q_i}"]], eval(f"sequence_list_{i}"), depth)

                for q_i in q_no_list:

                    measure_macro(qe_list[q_index[f"{q_i}"]], rr_list[q_index[f"{q_i}"]], out_list[q_index[f"{q_i}"]],
                                  I[q_index[f"{q_i}"]], Q[q_index[f"{q_i}"]], pi_12=True)
                    save(I[q_index[f"{q_i}"]], eval(f"I{q_i}_st"))
                    save(Q[q_index[f"{q_i}"]], eval(f"Q{q_i}_st"))

                assign(eval(f"sequence_list_{i}")[depth], eval(f"saved_gate_{i}"))

    with stream_processing():

        for q_i in q_no_list:
            eval(f"I{q_i}_st").buffer(avgs).map(FUNCTIONS.average()).buffer(num_of_sequences, max_circuit_depth).save(f"I{q_i}_avg")
            eval(f"Q{q_i}_st").buffer(avgs).map(FUNCTIONS.average()).buffer(num_of_sequences, max_circuit_depth).save(f"Q{q_i}_avg")


###########
# execute #
###########
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
qm = qmm.open_qm(config)

if simulate:
    job = qmm.simulate(config, rb, SimulationConfig(int(60000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()
    samples.con2.plot()
    plt.legend("")
    raise Halted()

rb_vals = []
for i in range(n_iter):
    job = qm.execute(rb, duration_limit=0, data_limit=0)

    ############
    # analysis #
    ############

    res_handles = job.result_handles
    res_handles.wait_for_all_values()

    avg_trace_values = []
    x = np.linspace(1, max_circuit_depth, max_circuit_depth)
    rb_vals_temp = []
    for q_i in q_no_list:

        vars()[f"I{q_i}value"] = getattr(res_handles, f"I{q_i}_avg").fetch_all()
        vars()[f"Q{q_i}value"] = getattr(res_handles, f"Q{q_i}_avg").fetch_all()

        avg_trace = np.average(eval(f"I{q_i}value"), axis=0)
        avg_trace_values.append(avg_trace)
        init_vals = [-6e-5, 6e-5, 0.99]

    #
        pars, cov = curve_fit(f=power_law, xdata=x, ydata=avg_trace, p0=init_vals,
                              bounds=(-np.inf, np.inf), maxfev=2000)
        stdevs = np.sqrt(np.diag(cov))
        one_minus_p = 1 - pars[2]
        r_c = one_minus_p * (1 - 1 / 2 ** 1)
        r_g = r_c / 1.875
        r_c_std = stdevs[2] * (1 - 1 / 2 ** 1)
        r_g_std = r_c_std / 1.875
        rb_vals_temp.append(r_c)

        fid = np.round(1e2*(1-r_c), 2)

        plt.figure()
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        plt.title(f"Simultaneus RB : Qubit {q_i} Fidelity = {fid}% ", fontsize=14)
        plt.ylabel("Voltage (a.u.)", fontsize=16)
        plt.xlabel("No. of Cliffords", fontsize=16)
        plt.plot(avg_trace, ".r", markersize=6, alpha=0.7) #plot averaged trace

        for j in range(eval(f"I{q_i}value").shape[0]):
            plt.plot(eval(f"I{q_i}value")[j], '.', alpha=0.4, markersize=3)  # plot individual traces in 4k colour

        plt.plot(x, power_law(x, *pars), '-r')
        plt.grid()
        plt.show()

        print(f'~~~~~~~~~~~~~~ FOR QUBIT {q_i} ~~~~~~~~~~~~~~~~~')
        print('#########################')
        print('### Fitted Parameters ###')
        print('#########################')
        print(f'A = {pars[0]:.3} ({stdevs[0]:.1}), B = {pars[1]:.3} ({stdevs[1]:.1}), p = {pars[2]:.3} ({stdevs[2]:.1})')
        print('Covariance Matrix')
        print(cov)



        print('#########################')
        print('### Useful Parameters ###')
        print('#########################')
        print(f'1-p = {np.format_float_scientific(one_minus_p, precision=2)} ({stdevs[2]:.1}), '
              f'r_c = {np.format_float_scientific(r_c, precision=2)} ({r_c_std:.1}), '
              f'r_g = {np.format_float_scientific(r_g, precision=2)}  ({r_g_std:.1})')

        file_saver_(np.transpose([x, avg_trace, power_law(x, *pars)]), file_name=__file__,
                 master_folder=ExpName, header_string="Simultanenous RB", suffix=f"{q_i}", time_stamp=time_stamp)

        file_saver_(np.transpose(eval(f"I{q_i}value")), file_name=__file__,
                    master_folder=ExpName, header_string="Simultanenous RB", suffix=f"{q_i}_Individual Traces", time_stamp=time_stamp)
    rb_vals.append(rb_vals_temp)
    file_saver_(np.transpose(rb_vals), file_name=__file__,
                master_folder=ExpName, header_string="Simultanenous RB", suffix=f"RB_vals", time_stamp=False)