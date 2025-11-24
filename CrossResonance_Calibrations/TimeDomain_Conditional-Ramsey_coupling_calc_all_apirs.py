import json

from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
from Helper_Functions.analysis_functions import ramsey_fitting

matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import *

simulate = False
save_data = True
pi_12 = False
###################
# The QUA program #
###################
t_min = 4
t_max = 5000 // 4
dt = 4
t_list = np.arange(t_min, t_max, dt)

tot_qubits = [1, 2, 3, 4, 5, 6]

tot_shifts = []
couplings = []

tgt_qubits = [i for i in tot_qubits if i not in control_qubits]

for c in control_qubits:

    for tgt in tgt_qubits:

        for fwd in [True, False]:

            if fwd:
                q_no_t, q_no_c = tgt, c
            else:
                q_no_t, q_no_c = c, tgt
            qubit_IF = q_IF[str(q_no_t)]
            det = 2.5  # in MHz
            qe_t = f"q{q_no_t}"
            rr_t = f"rr{q_no_t}"
            out_t = adc_mapping[rr_t]
            qe = qe_t

            qe12 = f"q12_{q_no}"
            dem = demarcations[str(q_no)]

            qe_c = f"q{q_no_c}"
            rr_c = f"rr{q_no_c}"
            out_c = adc_mapping[rr_c]

            # con = f"con{dac_mapping[qe][0]}"
            wait_init = 250000
            if simulate: wait_init = 100

            with program() as ramsey:
                n = declare(int)
                I0 = declare(fixed)
                I0_st = declare_stream()
                Q0 = declare(fixed)
                Q0_st = declare_stream()
                I0c = declare(fixed)
                I0c_st = declare_stream()
                Q0c = declare(fixed)
                Q0c_st = declare_stream()
                I1 = declare(fixed)
                I1_st = declare_stream()
                Q1 = declare(fixed)
                Q1_st = declare_stream()
                I1c = declare(fixed)
                I1c_st = declare_stream()
                Q1c = declare(fixed)
                Q1c_st = declare_stream()
                t = declare(int)

                update_frequency(qe_t, qubit_IF + det * 1e6)
                with for_(n, 0, n < 1500, n + 1):
                    with for_(t, t_min, t < t_max, t + dt):
                        if simulate: t = 100

                        cooldown(time=wait_init)
                        # cooldown(time=wait_init, active_reset=False, qe=qe_c)
                        # wait(wait_init)
                        play_X90(qe_t)
                        wait(t, qe_t)
                        play_X90(qe_t)
                        align()
                        measure_macro(qe_t, rr_t, out_t, I0, Q0, pi_12=pi_12)
                        measure_macro(qe_c, rr_c, out_c, I0c, Q0c, pi_12=pi_12)
                        save(I0, I0_st)
                        save(Q0, Q0_st)
                        save(I0c, I0c_st)
                        save(Q0c, Q0c_st)

                        align()
                        # wait(wait_init)
                        cooldown(time=wait_init)
                        # cooldown(time=wait_init, active_reset=False, qe=qe_c)
                        align(qe_t, qe_c)
                        play_X180(qe_c)
                        align(qe_c, qe_t)
                        play_X90(qe_t)
                        wait(t, qe_t)
                        play_X90(qe_t)
                        align()
                        measure_macro(qe_t, rr_t, out_t, I1, Q1, pi_12=pi_12)
                        measure_macro(qe_c, rr_c, out_c, I1c, Q1c, pi_12=pi_12)
                        save(I1, I1_st)
                        save(Q1, Q1_st)
                        save(I1c, I1c_st)
                        save(Q1c, Q1c_st)
                        # assign(ang, ang + 0.05)

                with stream_processing():
                    I0_st.buffer(len(t_list)).average().save('I0')
                    Q0_st.buffer(len(t_list)).average().save('Q0')
                    I0c_st.buffer(len(t_list)).average().save('I0c')
                    Q0c_st.buffer(len(t_list)).average().save('Q0c')
                    I1_st.buffer(len(t_list)).average().save('I1')
                    Q1_st.buffer(len(t_list)).average().save('Q1')
                    I1c_st.buffer(len(t_list)).average().save('I1c')
                    Q1c_st.buffer(len(t_list)).average().save('Q1c')

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
                # samples.con1.plot()
                # samples.con2.plot()
                # samples.con3.plot()
                # plt.show(block=False)
                # plt.legend("")
                qe_t_I = dac_mapping[f'{qe_t}'][1][0]
                qe_t_Q = dac_mapping[f'{qe_t}'][1][1]
                qe_c_I = dac_mapping[f'{qe_c}'][1][0]
                qe_c_Q = dac_mapping[f'{qe_c}'][1][1]
                rr_c_I = dac_mapping[f'rr{qe_c[-1]}'][1][0]
                rr_c_Q = dac_mapping[f'rr{qe_c[-1]}'][1][1]
                rr_t_I = dac_mapping[f'rr{qe_t[-1]}'][1][0]
                rr_t_Q = dac_mapping[f'rr{qe_t[-1]}'][1][1]
                con_ctrl = dac_mapping[f'{qe_c}'][0]
                con_tgt = dac_mapping[f'{qe_t}'][0]
                con_ctrl = f'con{con_ctrl}'
                con_tgt = f'con{con_tgt}'
                control_I = getattr(samples, con_ctrl).analog[f'{qe_c_I}']
                control_Q = getattr(samples, con_ctrl).analog[f'{qe_c_Q}']
                target_I = getattr(samples, con_tgt).analog[f'{qe_t_I}']
                target_Q = getattr(samples, con_tgt).analog[f'{qe_t_Q}']
                rd_c_I = getattr(samples, con_ctrl).analog[f'{rr_c_I}']
                rd_c_Q = getattr(samples, con_ctrl).analog[f'{rr_c_Q}']
                rd_t_I = getattr(samples, con_tgt).analog[f'{rr_t_I}']
                rd_t_Q = getattr(samples, con_tgt).analog[f'{rr_t_Q}']
                stark_I = getattr(samples, 'con3').analog['5']
                stark_Q = getattr(samples, 'con3').analog['6']
                # plot all ports:
                plt.figure()
                plt.plot(control_I, label='control_I')
                plt.plot(control_Q, label='control_Q')
                plt.plot(target_I, label='target_I')
                plt.plot(target_Q, label='target_Q')
                plt.plot(rd_c_I, label='rd_c_I')
                plt.plot(rd_c_Q, label='rd_c_Q')
                plt.plot(rd_t_I, label='rd_t_I')
                plt.plot(rd_t_Q, label='rd_t_Q')
                plt.plot(stark_I, label='stark_I')
                plt.plot(stark_Q, label='stark_Q')
                plt.grid()
                plt.legend()

                plt.show(block=False)

                raise Halted()

            #############
            # execution #
            #############
            qm = qmm.open_qm(config)
            job = qm.execute(ramsey)
            res_handles = job.result_handles
            I0_handle = job.result_handles.get("I0")
            Q0_handle = job.result_handles.get("Q0")
            I0c_handle = job.result_handles.get("I0c")
            Q0c_handle = job.result_handles.get("Q0c")
            I1_handle = job.result_handles.get("I1")
            Q1_handle = job.result_handles.get("Q1")
            I1c_handle = job.result_handles.get("I1c")
            Q1c_handle = job.result_handles.get("Q1c")
            # job.result_handles.wait_for_all_values()

            I0_handle.wait_for_values(1)
            Q0_handle.wait_for_values(1)
            I1_handle.wait_for_values(1)
            Q1_handle.wait_for_values(1)

            plt.ion()
            fig, ax = plt.subplots(2)

            fig.suptitle("Conditional Ramsey")
            lines = []
            tc = ["Target", "Control"]
            for i in range(2):
                lines.append(ax[i].plot(4e-3 * t_list, [0] * len(t_list), marker=".", label="0")[
                                 0])  # Returns a tuple of line objects, thus the comma
                lines.append(ax[i].plot(4e-3 * t_list, [0] * len(t_list), marker=".", label="1")[
                                 0])  # Returns a tuple of line objects, thus the comma
                ax[i].set_title(tc[i])
                ax[i].set_ylabel("Ramsey Amplitude")
                ax[i].grid()
                ax[i].legend()

            ax[1].set_xlabel("Time (us)")

            while res_handles.is_processing():

                I0 = I0_handle.fetch_all()
                Q0 = Q0_handle.fetch_all()
                I1 = I1_handle.fetch_all()
                Q1 = Q1_handle.fetch_all()
                I0c = I0c_handle.fetch_all()
                Q0c = Q0c_handle.fetch_all()
                I1c = I1c_handle.fetch_all()
                Q1c = Q1c_handle.fetch_all()
                I = [I0, I1, I0c, I1c]
                Q = [Q0, Q1, Q0c, Q1c]

                for i in range(2):
                    lines[2 * i].set_ydata(I[2 * i])
                    lines[2 * i + 1].set_ydata(I[2 * i + 1])
                    ax[i].relim()
                    ax[i].autoscale_view()
                    fig.set_tight_layout(True)
                    fig.canvas.draw()
                    fig.canvas.flush_events()

                plt.pause(1)

            I0 = job.result_handles.get("I0").fetch_all()
            Q0 = job.result_handles.get("Q0").fetch_all()
            I1 = job.result_handles.get("I1").fetch_all()
            Q1 = job.result_handles.get("Q1").fetch_all()

            t_list_us = 4e-3 * t_list


            def ramsey_fit(t, A, f, d, p, c):
                return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c

            #
            # pars0, cov0 = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=I0,
            #                         p0=[(max(I0) - min(I0)) / 2, det, 50, np.pi, np.mean(I0)], bounds=(-np.inf, np.inf),
            #                         maxfev=2000)
            # pars1, cov1 = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=I1,
            #                         p0=[(max(I1) - min(I1)) / 2, det * 0.9, 50, np.pi, np.mean(I1)],
            #                         bounds=(-np.inf, np.inf), maxfev=2000)

            res_0, pcov_0, init_0 = ramsey_fitting(t_list_us, I0)  # A, tau, offset, freq, phi
            res_1, pcov_1, init_1 = ramsey_fitting(t_list_us, I1)  # A, tau, offset, freq, phi

            pars0 = [res_0[0], res_0[3], res_0[1], res_0[4], res_0[2]]
            pars1 = [res_1[0], res_1[3], res_1[1], res_1[4], res_1[2]]

            total_det = np.abs(np.round(abs(pars0[1]) - abs(pars1[1]), 4))

            print('#########################')
            print('### Fitted Parameters ###')
            print('#########################')
            print(f"Ramsey frequency control {qe_c} 0 = {pars0[1]} MHz")
            print(f"Ramsey time control {qe_c} 0 = {pars0[2]} us")
            print(f"Ramsey frequency control {qe_c}  1 = {pars1[1]} MHz")
            print(f"Ramsey time control {qe_c} 1 = {pars1[2]} us")
            print(f"Total detuning {qe_c} {qe_t} pair = {1e3 * total_det} kHz")
            print(f"ZZ error = {0.5 * total_det} MHz")

            plt.figure()
            plt.plot(t_list_us, I0, "-*", color="red")
            plt.plot(t_list_us, ramsey_fit(t_list_us, *pars0), label="Control 0", color="red")
            plt.plot(t_list_us, I1, "--", color="blue")
            plt.plot(t_list_us, ramsey_fit(t_list_us, *pars1), label="Control 1", color="blue")
            plt.xlabel('t (us)')
            plt.ylabel('Signal')
            plt.title(
                f"Conditional Ramsey : Target ; Total shift = {1e3 * total_det:.2f} kHz Control: R{qubit_to_ring_map[q_no_c][0]} Target: R{qubit_to_ring_map[q_no_t][0]}")
            plt.legend()
            plt.grid()
            plt.show(block=False)

            plt.figure()
            plt.plot(t_list_us, I0c, "^", color="red", label="Control 0")
            plt.plot(t_list_us, I1c, "^", color="blue", label="Control 1")
            plt.xlabel('t (us)')
            plt.ylabel('Signal')
            plt.title(
                f"Conditional Ramsey : Control Control: R{qubit_to_ring_map[q_no_c][0]} Target: R{qubit_to_ring_map[q_no_t][0]}")
            plt.legend()
            plt.grid()
            plt.show(block=False)

            if save_data:
                file_saver_(np.transpose([t_list_us, I0, Q0, I1, Q1]), file_name=__file__,
                            suffix=f"Control_{qe_c}_Target_{qe_t}",
                            master_folder=ExpName, header_string="Time(us), I_0, Q_0, I_1, Q_1")

            # q_no_t, q_no_c = 6, 3
            qc_f = q_LO[str(q_no_c)] + q_IF[str(q_no_c)]
            qt_f = q_LO[str(q_no_t)] + q_IF[str(q_no_t)]

            f_shift = total_det * 1e6

            ZZ = f_shift / 2

            with open('../Configuration_Files/System_Parameters/anharmonicities.json', 'r') as f:
                anhs = json.load(f)
                f.close()

            # d1, d2 = -anhs[str(q_no_c)], -anhs[str(q_no_t)]
            d1 = (q12_IF[str(q_no_c)] - q_IF[str(q_no_c)]) * 1e-6
            d2 = (q12_IF[str(q_no_t)] - q_IF[str(q_no_t)]) * 1e-6

            del12 = 1e-6 * (qc_f - qt_f)

            J_sq = -ZZ * (del12 + d1) * (d2 - del12) / (d1 + d2)
            if J_sq > 0:
                J = np.sqrt(J_sq)
            else:
                J = np.sqrt(-1 * J_sq)

            print(f'Coupling is {J * 1e-3:.3f} MHz')

            tot_shifts.append([qe_c, qe_t, np.round(total_det*1e3, 3)])
            couplings.append([qe_c, qe_t, np.round(J*1e3, 3)])
