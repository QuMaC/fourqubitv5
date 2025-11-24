from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import fetching_tool, progress_counter

from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import measure_macro

simulate = False
save_data = True
pi_12 = False
###################
# The QUA program #
###################
t_min = 4
t_max = 1000//4
dt = 4
t_list = np.arange(t_min, t_max, dt)

q_no_t_set = [1, 2, 3, 4, 6]
q_no_c_list_set = [[2, 4, 6],
                   [1, 3]]

for q_no_t in q_no_t_set:

    qubit_IF = q_IF[str(q_no_t)]
    det = 2.5  # in MHz

    qe_t = f"q{q_no_t}"
    rr_t = f"rr{q_no_t}"
    out_t = adc_mapping[rr_t]

    q_no_c_list = q_no_c_list_set[np.mod(q_no_t, 2) - 1]
    q_c_index = {}
    n_c_qubits = len(q_no_c_list)
    qe_c_list, rr_c_list, out_c_list = [], [], []

    for q_c_i in q_no_c_list:
        q_c_index[f"{q_c_i}"] = q_no_c_list.index(q_c_i)
        qe_c_list.append(f"q{q_c_i}")
        rr_c_list.append(f"rr{q_c_i}")
        out_c_list.append(adc_mapping[f"rr{q_c_i}"])

    perms_c_list = [np.binary_repr(i, width=n_c_qubits) for i in np.arange(2**n_c_qubits)]
    n_c_perms = len(perms_c_list)

    # con = f"con{dac_mapping[qe][0]}"
    wait_init = 25000
    n_avg = 4000
    if simulate:
        wait_init = 100

    with program() as ramsey:

        n = declare(int)
        n_st = declare_stream()
        t = declare(int)

        for perms_c_i in perms_c_list:

            vars()[f"It_{perms_c_i}"] = declare(fixed)
            vars()[f"Qt_{perms_c_i}"] = declare(fixed)
            vars()[f"It_{perms_c_i}_st"] = declare_stream()
            vars()[f"Qt_{perms_c_i}_st"] = declare_stream()

            for q_c_i in q_no_c_list:

                vars()[f"Ic_q{q_c_i}_{perms_c_i}"] = declare(fixed)
                vars()[f"Qc_q{q_c_i}_{perms_c_i}"] = declare(fixed)
                vars()[f"Ic_q{q_c_i}_{perms_c_i}_st"] = declare_stream()
                vars()[f"Qc_q{q_c_i}_{perms_c_i}_st"] = declare_stream()

        update_frequency(qe_t, qubit_IF + det*1e6)
        with for_(n, 0, n < n_avg, n + 1):
            with for_(t, t_min, t < t_max, t + dt):

                if simulate:
                    t = 100

                # Considering all control permutations
                for perms_c_i in perms_c_list:
                    wait(wait_init)

                    for q_c_i in q_no_c_list:
                        state_c = perms_c_i[q_c_index[f'{q_c_i}']]
                        if int(state_c):
                            play("X180", qe_c_list[q_c_index[f"{q_c_i}"]])

                    align()

                    play_X90(qe_t)
                    wait(t, qe_t)
                    play_X90(qe_t)

                    # Measurements
                    measure_macro(qe_t, rr_t, out_t,
                                  eval(f"It_{perms_c_i}"), eval(f"Qt_{perms_c_i}"),
                                  pi_12=pi_12)

                    for q_c_i in q_no_c_list:
                        measure_macro(qe_c_list[q_c_index[f"{q_c_i}"]], rr_c_list[q_c_index[f"{q_c_i}"]],
                                      out_c_list[q_c_index[f"{q_c_i}"]],
                                      eval(f"Ic_q{q_c_i}_{perms_c_i}"), eval(f"Qc_q{q_c_i}_{perms_c_i}"),
                                      pi_12=pi_12)

                    # Data acquisition
                    save(eval(f"It_{perms_c_i}"), eval(f"It_{perms_c_i}_st"))
                    save(eval(f"Qt_{perms_c_i}"), eval(f"Qt_{perms_c_i}_st"))

                    for q_c_i in q_no_c_list:
                        save(eval(f"Ic_q{q_c_i}_{perms_c_i}"), eval(f"Ic_q{q_c_i}_{perms_c_i}_st"))
                        save(eval(f"Qc_q{q_c_i}_{perms_c_i}"), eval(f"Qc_q{q_c_i}_{perms_c_i}_st"))
            save(n, n_st)

        with stream_processing():
            for perms_c_i in perms_c_list:

                eval(f"It_{perms_c_i}_st").buffer(len(t_list)).average().save(f'It_{perms_c_i}')
                eval(f"Qt_{perms_c_i}_st").buffer(len(t_list)).average().save(f'Qt_{perms_c_i}')

                for q_c_i in q_no_c_list:

                    eval(f"Ic_q{q_c_i}_{perms_c_i}_st").buffer(len(t_list)).average().save(f'Ic_q{q_c_i}_{perms_c_i}')
                    eval(f"Qc_q{q_c_i}_{perms_c_i}_st").buffer(len(t_list)).average().save(f'Qc_q{q_c_i}_{perms_c_i}')

            n_st.save("Iteration")

    ######################################
    # Open Communication with the Server #
    ######################################
    qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

    ####################
    # Simulate Program #
    ####################
    if simulate:
        job = qmm.simulate(config, ramsey, SimulationConfig(int(10000)))
        # get DAC and digital samples
        samples = job.get_simulated_samples()
        # plot all ports:
        samples.con1.plot()
        samples.con2.plot()
        plt.legend("")

        raise Halted()

    #############
    # execution #
    #############
    qm = qmm.open_qm(config)
    job = qm.execute(ramsey)

    data_list = ["Iteration"]
    for perms_c_i in perms_c_list:

        data_list.append(f"It_{perms_c_i}")
        data_list.append(f"Qt_{perms_c_i}")

        for q_c_i in q_no_c_list:

            data_list.append(f"Ic_q{q_c_i}_{perms_c_i}")
            data_list.append(f"Qc_q{q_c_i}_{perms_c_i}")

    # Get results from QUA program
    results = fetching_tool(job, data_list=data_list, mode="live")

    # Live plotting
    plt.ion()
    fig, ax = plt.subplots(1 + n_c_qubits)
    interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

    fig.suptitle(f"Conditional Ramsey with Controls Q{q_no_c_list}")
    lines = []
    titles = [f"Target Q{q_no_t}"]
    for q_c_i in q_no_c_list:
        titles.append(f"Control Q{q_c_i}")

    for i in range(1 + n_c_qubits):

        for perms_c_i in perms_c_list:
            lines.append(ax[i].plot(4e-3 * t_list, [0]*len(t_list),
                                    marker=".", label=f"{perms_c_i}")[0])

        ax[i].set_title(titles[i])
        ax[i].set_ylabel("Signal")
        ax[i].grid()
        ax[i].legend()

    ax[-1].set_xlabel("Time (us)") # Bottom plot has X axis label

    while results.is_processing():
        # Fetch results
        res_list = results.fetch_all()

        iter = res_list[0]

        for i in range(n_c_perms): # 0 to 7

            vars()[f"It_{perms_c_list[i]}"] = res_list[8*i + 1] # 9, 17
            vars()[f"Qt_{perms_c_list[i]}"] = res_list[8*i + 2]

            for j in range(n_c_qubits): # 0 to 2

                vars()[f"Ic_q{q_no_c_list[j]}_{perms_c_list[i]}"] = res_list[8*i + 2*j + 3]
                vars()[f"Qc_q{q_no_c_list[j]}_{perms_c_list[i]}"] = res_list[8*i + 2*j + 4]

        # Progress bar
        progress_counter(iter, n_avg, start_time=results.get_start_time())

        for j in range(1 + n_c_qubits):

            if j: # j = 1, 2, 3

                for i in range(n_c_perms): # 0 to 7
                    lines[8*j + i].set_ydata(eval(f"Ic_q{q_no_c_list[j-1]}_{perms_c_list[i]}"))

                ax[j].relim()
                ax[j].autoscale_view()
                fig.set_tight_layout(True)
                fig.canvas.draw()
                fig.canvas.flush_events()

            else: # j = 0

                for i in range(n_c_perms): # 0 to 7
                    lines[8*j + i].set_ydata(eval(f"It_{perms_c_list[i]}"))

                ax[j].relim()
                ax[j].autoscale_view()
                fig.set_tight_layout(True)
                fig.canvas.draw()
                fig.canvas.flush_events()
        plt.show()
        plt.pause(1)

    t_list_us = 4e-3 * t_list

    def ramsey_fit(t, A, f, d, p, c):

        return A * np.exp(-t/d) * np.sin(2*np.pi*f*t + p) + c


    for perms_c_i in perms_c_list:
        # print(perms_c_i)
        vars()[f"pars_{perms_c_i}"], vars()[f"cov_{perms_c_i}"] = curve_fit(f=ramsey_fit, xdata=t_list_us,
                                                                            ydata=eval(f"It_{perms_c_i}"),
                                                                            p0=[1e-3, det, 1, 0, -1e-4],
                                                                            bounds=(-np.inf, np.inf), maxfev=2000)
        # print(eval(f"pars_{perms_c_i}"), eval(f"It_{perms_c_i}") == eval("It_000"))

    print('#########################')
    print('### Fitted Parameters ###')
    print('#########################')

    det_perms_list = []
    plt.figure()
    plt.suptitle(f"Conditional Ramsey | Controls Q{q_no_c_list} Target Q{q_no_t}")

    for i in range(n_c_perms):

        print(f"Ramsey frequency {perms_c_list[i]} = {eval(f'pars_{perms_c_list[i]}')[1]} MHz")
        print(f"Ramsey time {perms_c_list[i]} = {eval(f'pars_{perms_c_list[i]}')[2]} us")
        # Detuning in kHz
        vars()[f"det_{perms_c_list[i]}"] = 1e3 * np.abs(np.round(np.abs(eval(f"pars_000")[1]) -
                                                           np.abs(eval(f"pars_{perms_c_list[i]}")[1]), 4))
        print(f"Detuning = {eval(f'det_{perms_c_list[i]}')} kHz")
        det_perms_list.append(eval(f"det_{perms_c_list[i]}"))

        plt.plot(t_list_us, eval(f"It_{perms_c_list[i]}"), "^", color=f"C{i}")
        plt.plot(t_list_us, ramsey_fit(t_list_us, *eval(f"pars_{perms_c_list[i]}")),
                 label=f"{perms_c_list[i]}", color=f"C{i}")

    plt.xlabel('t (us)')
    plt.ylabel('Signal')
    plt.title(f"Max shift = {np.max(det_perms_list)} kHz")
    plt.legend()
    plt.grid()
    plt.show()

    if save_data:
        for j in range(1 + n_c_qubits):

            if j: # j = 1, 2, 3
                header_list_c = "Time(us)"
                file_data_list_c = [t_list_us]
                for i in range(n_c_perms): # 0 to 7
                    header_list_c += f", {f'Ic_q{q_no_c_list[j-1]}_{perms_c_list[i]}'}"
                    header_list_c += f", {f'Qc_q{q_no_c_list[j-1]}_{perms_c_list[i]}'}"
                    file_data_list_c.append(eval(f"Ic_q{q_no_c_list[j-1]}_{perms_c_list[i]}"))
                    file_data_list_c.append(eval(f"Qc_q{q_no_c_list[j-1]}_{perms_c_list[i]}"))

                file_saver_(np.transpose(file_data_list_c), file_name=__file__,
                            suffix=f"CQ{q_no_c_list}TQ{q_no_t}_Control_Q{q_no_c_list[j-1]}",
                            master_folder=ExpName, header_string=header_list_c)

            else: # j = 0
                header_list_t = "Time(us)"
                file_data_list_t = [t_list_us]
                for i in range(n_c_perms): # 0 to 7
                    header_list_t += f", {f'It_{perms_c_list[i]}'}, {f'Qt_{perms_c_list[i]}'}"
                    file_data_list_t.append(eval(f"It_{perms_c_list[i]}"))
                    file_data_list_t.append(eval(f"Qt_{perms_c_list[i]}"))

                file_saver_(np.transpose(file_data_list_t), file_name=__file__,
                            suffix=f"CQ{q_no_c_list}TQ{q_no_t}_Target_Q{q_no_t}",
                            master_folder=ExpName, header_string=header_list_t)
