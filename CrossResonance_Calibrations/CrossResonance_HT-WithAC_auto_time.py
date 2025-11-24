from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
from Helper_Functions.macros import *
from qualang_tools.plot import interrupt_on_close
import os
from qualang_tools.results import progress_counter, fetching_tool
from Helper_Functions.CR_fitters import *
from Helper_Functions.qua_program_funcs import *



simulate = False
save_data = True
time_stamp = False

update_calib = False
###################
# The QUA program #
###################

t_min_ns = 16
t_max_ns = 1000
dt_ns = 4  # minimum 4ns
t_min = int(t_min_ns / 4)
t_max = int(t_max_ns / 4)
dt = int(dt_ns / 4)
t_list = np.arange(t_min, t_max, dt)

c_no, t_no = 5, 2



qe_c = f"q{c_no}"
rr_c = f"rr{c_no}"
out_c = adc_mapping[rr_c]
qe_t = f"q{t_no}"
rr_t = f"rr{t_no}"
out_t = adc_mapping[rr_t]
pi_12 = True

cr_elem = f"cr_c{c_no}t{t_no}"
cr_ac_elem = f"cr_ac_c{c_no}t{t_no}"
p_cr = cr_phase[cr_elem]
a_cr = cr_amp[cr_elem]

a_ac = cr_amp[cr_ac_elem]

pi_amp = amp_scale[str(t_no)]["X180"]

wait_init = 250000
wait_t = 4
wait_rr = 16

n_avg = 200

echo_p = True

if simulate:
    wait_init = 100

echo_time_delta = 0

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

#############
# execution #
#############

def HT_setACAmp(cr_elem, cr_ac_elem, a_ac, echo):
    def twoqubit_CR_ham_tomo_withAC(control: int, target_pulse, cr_elem, cr_ac_elem, a_ac, echo, simulate=False):
        '''
        ### Pulse protocol:

        - Put control in 1 or 0 based on bool(control).
        - Send a cross resonance pulse of length 't' on cross resonance element (cr_c1t2) with or without echo.
        - Send target_pulse on Target qubit.
        - Measurement pulse on taget and control.
        - save data on 4 streams.

        ### Requirements:
        - 4 streams : I_t_st,Q_t_st,I_c_st,Q_c_st
        - 5 variables : It,Qt,Ic,Qc and time 't' that is looped over
        '''
        # start

        echo = declare(bool, value=echo)


        # wait(wait_init, qe_t)
        align()
        cooldown(time=wait_init)

        # play("X", qe_t)             #Initializes Target in 1 ; Comment out for normal HT
        # wait(wait_t,qe_t)
        align(qe_t, qe_c)



        # set control to zero or one
        with if_(control == 1):
            play_X180(qe_c)
        with else_():
            play("I", qe_c)
        align(cr_elem, qe_c)



        # do either simple CR or echo CR
        with if_(echo == False):
            align(cr_elem, cr_ac_elem)
            play_flat_top(cr_elem, a_cr, 2 * t)
            play_flat_top(cr_ac_elem, a_ac, 2 * t)
        with else_():
            align(cr_elem, cr_ac_elem)
            play_flat_top(cr_elem, a_cr, t)
            play_flat_top(cr_ac_elem, a_ac, t)
            align(qe_c, cr_elem)
            wait(wait_t, qe_c)
            play_X180(qe_c)
            # wait(wait_t, qe_c)
            align(cr_elem, qe_c)
            align(cr_elem, cr_ac_elem)
            play_flat_top(cr_elem, -a_cr, t)
            play_flat_top(cr_ac_elem, -a_ac, t)
            align(cr_elem, qe_c)
            wait(wait_t, qe_c)
            play_X180(qe_c, a = -1)


        align(cr_elem, qe_t)
        wait(wait_t, qe_t)
        # play target pulse
        play(target_pulse, qe_t)

        # align()

        # # finally perform readouts
        measure_macro(qe_t, rr_t, out_t, It, Qt, pi_12=pi_12)
        measure_macro(qe_t, rr_c, out_c, Ic, Qc, pi_12=pi_12)
        save(It, I_t_st)
        save(Qt, Q_t_st)
        save(Ic, I_c_st)
        save(Qc, Q_c_st)

    Echo = echo
    a_cr, p_cr = cr_amp[cr_elem], cr_phase[cr_elem]
    p_ac = cr_phase[cr_ac_elem]

    with program() as CR_tomo:
        n = declare(int)
        I_c_st = declare_stream()
        Q_c_st = declare_stream()
        Q_t_st = declare_stream()
        I_t_st = declare_stream()
        Ic = declare(float)
        Qc = declare(float)
        Qt = declare(float)
        It = declare(float)
        Qrabi = declare(float)
        Irabi = declare(float)
        Q_rabi_st = declare_stream()
        I_rabi_st = declare_stream()
        t = declare(int)
        n_st = declare_stream()

        reset_frame([cr_elem, cr_ac_elem])

        frame_rotation_2pi(p_cr, cr_elem)
        frame_rotation_2pi(p_ac, cr_ac_elem)

        with for_(n, 0, n < 300, n + 1):
            with for_(t, t_min, t < t_max, t + dt):
                if simulate:
                    assign(t, 100)

                # wait(wait_init, qe_t)
                cooldown(time=wait_init)
                play("const" * amp(pi_amp), qe_t, t)
                measure_macro(qe_t, rr_t, out_t, Irabi, Qrabi, pi_12=pi_12)
                save(Irabi, I_rabi_st)
                save(Qrabi, Q_rabi_st)

                # wait(wait_init, qe_t)
                # cooldown(time=wait_init)
                # play C0TI, get C0Z
                twoqubit_CR_ham_tomo_withAC(0, "I", cr_elem, cr_ac_elem, a_ac, Echo)

                # play C0TX/2, get C0Y
                twoqubit_CR_ham_tomo_withAC(0, "X90", cr_elem, cr_ac_elem, a_ac, Echo)

                # play C0T-Y/2, get C0X
                twoqubit_CR_ham_tomo_withAC(0, "mY90", cr_elem, cr_ac_elem, a_ac, Echo)

                # playing C1TI, get C1Z
                twoqubit_CR_ham_tomo_withAC(1, "I", cr_elem, cr_ac_elem, a_ac, Echo)

                # playing C1TX/2, get C1Y
                twoqubit_CR_ham_tomo_withAC(1, "X90", cr_elem, cr_ac_elem, a_ac, Echo)

                # playing C1T-Y/2, get C1X
                twoqubit_CR_ham_tomo_withAC(1, "mY90", cr_elem, cr_ac_elem, a_ac, Echo)
            save(n, n_st)

        with stream_processing():
            # saves [[I_C0_t0,I_C1_t0],[I_C0_t1,I_C1_t1]]
            I_c_st.buffer(3 * len(t_list), 2).average().save("I_c_avg")
            Q_c_st.buffer(3 * len(t_list), 2).average().save("Q_c_avg")

            # saves [[I_C0Z_t0, I_C0Y_t0, I_C0X_t0, I_C1Z_t0, I_C1Y_t0, I_C1X_t0], [_t1array]]
            I_t_st.buffer(len(t_list), 6).average().save("I_t_avg")
            Q_t_st.buffer(len(t_list), 6).average().save("Q_t_avg")

            I_rabi_st.buffer(len(t_list)).average().save("I_rabi_avg")
            Q_rabi_st.buffer(len(t_list)).average().save("Q_rabi_avg")

            n_st.save("iteration")

    qm = qmm.open_qm(config)
    job = qm.execute(CR_tomo)

    ####################
    # Simulate Program #
    ####################
    if simulate:
        # qmm = QuantumMachinesManager()
        job = qmm.simulate(config, CR_tomo, SimulationConfig(int(30000)))
        # get DAC and digital samples
        samples = job.get_simulated_samples()
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
        # samples.con2.plot()

        raise Halted()


    return job


for echo_p in [False, True]:

    job = HT_setACAmp(cr_elem, cr_ac_elem, a_ac, echo_p)

    results = fetching_tool(job, data_list=["I_t_avg", "Q_t_avg", "I_c_avg",
                                                "Q_c_avg", "I_rabi_avg", "Q_rabi_avg",
                                                "iteration"], mode="live")

    # ========== PLOT INIT SETTINGS===================
    t_list_ns = 2 * 4 * t_list
    plt.ion()
    plt.rcParams["figure.figsize"] = (15, 10)
    fig, ax = plt.subplots(3, 3, sharex=True, sharey='row')
    interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
    # fig,ax = plt.subplots(3,3,sharex=True)
    fig.suptitle("Cross Resonance Tomography", fontsize=15)
    axbig = fig.add_subplot(111, frameon=False)
    axbig.set_xlabel("Time (us)", labelpad=20, fontsize=15)
    axbig.set_ylabel("Amplitude", labelpad=50, fontsize=15)
    axbig.set_xticks([])
    axbig.set_yticks([])
    lines = []
    tc = ["Control 0", "Control 1"]
    labels = ["Z", "Y", "X"]
    for i in range(2):
        # ax[i,0].set_xlabel("Time (us)")
        for j in range(3):
            lines.append(ax[i, j].plot(1e-3 * t_list_ns, 0.0001 * np.random.rand(len(t_list_ns)), marker=".", label='I')[
                             0])  # Returns a tuple of line objects, thus the [0]
            lines.append(ax[i, j].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
            ax[i, j].set_title(tc[i] + "  Target : " + labels[j])
            # ax[i,j].set_ylabel("Amplitude")
            ax[i, j].grid()
            ax[i, j].legend(loc='upper right')

    for i in range(2):
        lines.append(ax[2, i].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='I')[0])
        lines.append(ax[2, i].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
        ax[2, i].set_title(f"Control {i}")
        # ax[2,i].set_ylabel("Amplitude")
        ax[2, i].grid()
        ax[2, i].legend(loc='upper right')

    lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='I')[0])
    lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
    ax[2, 2].set_title("Target Rabi")
    ax[2, 2].grid()
    ax[2, 2].legend(loc='upper right')
    fig.set_tight_layout(True)
    fig.set_tight_layout(True)
    plt.show()

    # =======================================================


    # Start data collection and plotting =====================
    while results.is_processing():

        I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg, iteration = results.fetch_all()

        progress_counter(iteration, n_avg, start_time=results.get_start_time())

        It = I_t_avg
        Qt = Q_t_avg
        Ic = I_c_avg
        Qc = Q_c_avg
        Irabi = I_rabi_avg
        Qrabi = Q_rabi_avg

        # plot control qubits
        Ic0 = np.average(Ic[:, 0].reshape(len(t_list), 3), axis=1)
        Qc0 = np.average(Qc[:, 0].reshape(len(t_list), 3), axis=1)
        Ic1 = np.average(Ic[:, 1].reshape(len(t_list), 3), axis=1)
        Qc1 = np.average(Qc[:, 1].reshape(len(t_list), 3), axis=1)
        lines[12].set_ydata(Ic0)
        lines[13].set_ydata(Ic0)
        lines[14].set_ydata(Ic1)
        lines[15].set_ydata(Ic1)
        lines[16].set_ydata(Irabi)
        lines[17].set_ydata(Qrabi)

        # plot target qubits
        for i in range(0, 6):
            lines[2 * i].set_ydata(It[:, i])
            lines[2 * i + 1].set_ydata(Qt[:, i])

        for i in range(3):
            for j in range(3):
                ax[i, j].relim()
                ax[i, j].autoscale_view()

        snr_i, _ = S2N(I_rabi_avg)

        if snr_i > 100:
            job.halt()


        fig.set_tight_layout(True)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.2)

    It = job.result_handles.get("I_t_avg").fetch_all()
    Qt = job.result_handles.get("Q_t_avg").fetch_all()
    Ic = job.result_handles.get("I_c_avg").fetch_all()
    Qc = job.result_handles.get("Q_c_avg").fetch_all()
    Ic0 = np.average(Ic[:, 0].reshape(len(t_list), 3), axis=1)
    Qc0 = np.average(Qc[:, 0].reshape(len(t_list), 3), axis=1)
    Ic1 = np.average(Ic[:, 1].reshape(len(t_list), 3), axis=1)
    Qc1 = np.average(Qc[:, 1].reshape(len(t_list), 3), axis=1)
    Irabi = job.result_handles.get("I_rabi_avg").fetch_all()
    Qrabi = job.result_handles.get("Q_rabi_avg").fetch_all()

    t_list_ns_data = t_list_ns.reshape(len(t_list_ns), 1)
    Ic0, Ic1 = Ic0.reshape(len(Ic0), 1), Ic1.reshape(len(Ic1), 1)
    Qc0, Qc1 = Qc0.reshape(len(Qc0), 1), Qc1.reshape(len(Qc1), 1)

    Qtarget_data = np.hstack((t_list_ns_data, Qt))
    Itarget_data = np.hstack((t_list_ns_data, It))

    Icontrol_data = np.hstack((t_list_ns_data, Ic0, Ic1))
    Qcontrol_data = np.hstack((t_list_ns_data, Qc0, Qc1))

    # ############
    # # analysis #
    # ############

    # #
    p = np.round(p_cr, 5)
    if save_data is True:
        file_saver_qubit_(Itarget_data, file_name=__file__, master_folder=ExpName,
                          suffix=f"I_Control{c_no}_Target{t_no}_Phase_{p}_Echo_{echo_p}", time_stamp=time_stamp)
        file_saver_qubit_(Qtarget_data, file_name=__file__, master_folder=ExpName,
                          suffix=f"Q_Control{c_no}_Target{t_no}_Phase_{p}_Echo_{echo_p}", time_stamp=time_stamp)
        file_saver_qubit_(np.transpose([t_list_ns, Irabi, Qrabi]), file_name=__file__,
                          master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                          suffix=f"Rabi_Control{c_no}_Target{t_no}_Phase_{p}_Echo_{echo_p}", time_stamp=time_stamp)
        file_saver_qubit_(Icontrol_data, file_name=__file__,
                          master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                          suffix=f"Icontrol_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)
        file_saver_qubit_(Qcontrol_data, file_name=__file__,
                          master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                          suffix=f"Qcontrol_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)

    ############## CR len fitting ##############

    #
    # pars, cov = curve_fit(f=rabi_fit, xdata=time_list, ydata=rabi_i, p0=[0.03, 0.0016, 100, 0, 1e-5],
    #                       bounds=(-np.inf, np.inf), maxfev=2000)
    # norm, off = pars[0], pars[4]
    #
    # Cdata = normalize_data(Cdata, off, norm)
    #
    # p_init = [1, 0.8e-03, 4.39050031e+02, -1.17125957e-02,
    #           2.27866525e-02]
    #
    # pars0, cov0 = curve_fit(f=rabi_fit, xdata=time_list, ydata=Cdata[1][0], p0=p_init, bounds=(-np.inf, np.inf), maxfev=2000)
    # pars1, cov1 = curve_fit(f=rabi_fit, xdata=time_list, ydata=Cdata[1][1], p0=p_init, bounds=(-np.inf, np.inf), maxfev=2000)

    if echo_p:

        t_data = Itarget_data.transpose()
        t_data_r = [t_list_ns, Irabi, Qrabi]

        time_list = t_data[0]

        rabi_i = 1e3 * t_data_r[1]
        C0data = 1e3 * t_data[1:4]
        C1data = 1e3 * t_data[4:7]
        Cdata1 = []
        for i in range(3):
            data = [C0data[i], C1data[i]]
            Cdata1.append(data)

        res_I = fit_cos(time_list, rabi_i)
        pars = [res_I['amp'], res_I['freq'], 0, res_I['phase'], res_I['offset']]
        norm, off = pars[0], pars[4]

        Cdata = normalize_data(Cdata1, off, norm)

        p0 = fit_cos(time_list, Cdata[1][0])
        p1 = fit_cos(time_list, Cdata[1][1])

        pars0 = [p0['amp'], p0['freq'], 11e6, p0['phase'], p0['offset']]    # A, f, d, p, c
        pars1 = [p1['amp'], p1['freq'], 11e6, p1['phase'], p1['offset']]    # A, f, d, p, c

        func_0 = p0['fitfunc']
        func_1 = p1['fitfunc']

        t_min, t_max = time_list[0], time_list[-1]
        t_list_fine = np.linspace(t_min, t_max, 10000)
        Y0 = func_0(t_list_fine)
        Y1 = func_1(t_list_fine)

        sep = np.abs(Y1[:5000] - Y0[:5000])
        tgate = np.round(t_list_fine[np.argmax(sep)], 2)

        # tgate = 160
        r0, r1 = 0, 0
        labels = ["Z", "Y", "X"]
        colors = ["r", "b", "g"]
        plt.figure()
        for i in range(3):
            plt.plot(time_list, Cdata[i][0], "--", label=f'{labels[i]}0', color=colors[i])
            r0 += Cdata[i][0] ** 2

        plt.plot(t_list_fine, Y0, linewidth=2.2)
        plt.grid()
        plt.title(f"Control 0 : $T_{{gate}}$ = {int(tgate)} ns")
        plt.xlabel("Time (ns)")
        plt.ylabel(r"$\langle z \rangle$")
        plt.axvline(tgate)
        plt.legend()
        plt.ylim(-1, 1)
        plt.show()

        # plt.figure()
        for i in range(3):
            plt.plot(time_list, Cdata[i][1], "-", label=f'{labels[i]}1', color=colors[i])
            r1 += Cdata[i][1] ** 2

        plt.plot(t_list_fine, Y1, linewidth=2.2)
        plt.grid()
        plt.title(f"control {qe_c} and target {qe_t} Control 0 : $T_{{gate}}$ = {int(tgate)} ns")
        plt.xlabel("Time (ns)")
        plt.ylabel(r"$\langle z \rangle$")
        plt.axvline(tgate)
        plt.legend()
        plt.ylim(-1, 1)
        plt.show()
        plt.grid()

    else:
        if not echo_p:
            t_data = Itarget_data.transpose()
            t_data_r = [t_list_ns, Irabi, Qrabi]

            time_list = t_data[0]

            rabi_i = 1e3 * t_data_r[1]


            res_I = fit_cos(time_list, rabi_i)
            pars = [res_I['amp'], res_I['freq'], 0, res_I['phase'], res_I['offset']]
            norm, off = pars[0], pars[4]
            # if plot_rabi:
            #     plt.figure()
            #     plt.plot(t_list, rabi_i)
            #     plt.plot(t_list, rabi_fit(t_list, *pars))
            #     plt.show()

            C0data = 1e3 * t_data[1:4]
            C1data = 1e3 * t_data[4:7]
            Cdata = []
            for i in range(3):
                data_t = [C0data[i], C1data[i]]
                Cdata.append(data_t)
            Cdata = normalize_data(Cdata, off, norm)

            # Calculate interaction strengths by fitting Bloch equations to CR data
            int_strengths, ivals = CR_Hamiltonian_tomography(Cdata, time_list, bloch_params=True, init_vals=None)
            int_strengths = np.array(int_strengths)  # labels = ["ZX", "IX", "ZY", "IY", "ZZ", "IZ"]
            # CR_data.append(1e3*int_strengths)

            print(f'Strengths are'
                  f'\n ZX = {int_strengths[0] * 1e3} MHz'
                  f'\n IX = {int_strengths[1] * 1e3} MHz'
                  f'\n ZY = {int_strengths[2] * 1e3} MHz'
                  f'\n IY = {int_strengths[3] * 1e3} MHz'
                  f'\n ZZ = {int_strengths[4] * 1e3} MHz'
                  f'\n IZ = {int_strengths[5] * 1e3} MHz'
                  )

            exp_vals = Cdata
            ox1, oy1, del1, d1 = ivals[0]
            ox2, oy2, del2, d2 = ivals[1]
            vals1 = bloch_functions(time_list, ox1, oy1, del1, d1)
            vals2 = bloch_functions(time_list, ox2, oy2, del2, d2)




    if update_calib:
        with open('../Configuration_Files/Pulse_Calibrations/cr_len_ns.json', 'r') as f:
            cr_len_data = json.load(f)
            f.close()

        t_off = tgate%8

        if t_off <= 4 :
            tgate = tgate - t_off
        else:
            tgate = tgate - t_off + 8

        cr_len_data[cr_elem] = np.round(tgate)

        if echo_p:
            if update_calib:
                with open('../Configuration_Files/Pulse_Calibrations/cr_len_ns.json', 'w') as f:
                    json.dump(cr_len_data, f, indent=6)
                    f.close()


