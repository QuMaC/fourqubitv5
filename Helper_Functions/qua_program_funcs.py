from qm import SimulationConfig
from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.macros import *
from matplotlib import pyplot as plt


def HT_setPhase(qmm, cr_elem, p, t_min, t_max, dt, n_avg, wait_init, wait_t, wait_rr,
                qe_c, qe_t, pi_12, simulate, echo_p, a_cr):
    t_list = np.arange(t_min, t_max, dt)

    rr_c = f'rr{qe_c[-1]}'
    rr_t = f'rr{qe_t[-1]}'

    out_c = adc_mapping[rr_c]
    out_t = adc_mapping[rr_t]

    Echo = echo_p
    pi_12_in = pi_12

    def twoqubit_CR_ham_tomo_v2(cr_elem, control: int, target_pulse,
                                wait_t, wait_rr,
                                a, echo1, pi_12_in):
        '''
        ### Pulse protocol:

        - Put control in 1 or 0 based on bool(control).
        - Send a cross resonance pulse of length 't' on cross resonance element (qubit_cr) with or without echo.
        - Send target_pulse on Target qubit.
        - Measurement pulse on target and control.
        - Save data on 4 streams.

        ### Requirements:
        - 4 streams : I_t_st, Q_t_st, I_c_st, Q_c_st
        - 5 variables : It, Qt, Ic, Qc and time 't' that is looped over
        '''

        # start
        # reset_phase(rr_t)
        # reset_phase(rr_c)

        echo = declare(bool, value=echo1)

        wait_t = int(wait_t)
        wait_rr = int(wait_rr)

        # align(rr_t, qe_t)
        # align()
        # wait(wait_init, qe_t)
        cooldown(time=wait_init, qe = [qe_c, qe_t, cr_elem, rr_t, rr_c])
        align(qe_t, qe_c, cr_elem, rr_t, rr_c)
        # align()
        # set control to zero or one
        with if_(control == 1):
            play_X180(qe_c)
        with else_():
            play("I", qe_c)
        wait(wait_t, qe_c)
        # cooldown(time=wait_t, qe=qe_c)
        align(cr_elem, qe_c)

        frame_rotation_2pi(p, cr_elem)

        # do either simple CR or echo CR
        with if_(echo == False):
            play_flat_top(cr_elem, a, 2 * t)
        with else_():
            play_flat_top(cr_elem, a, t)
            align(qe_c, cr_elem)
            wait(wait_t, qe_c)
            play_X180(qe_c)
            align(cr_elem, qe_c)
            wait(wait_t, cr_elem)
            play_flat_top(cr_elem, -a, t)
            align(cr_elem, qe_c)
            wait(wait_t, qe_c)
            play_X180(qe_c, a=-1)

        reset_frame(cr_elem)
        # align(cr_elem, qe_t)
        align(cr_elem, qe_c, qe_t)
        wait(wait_t, qe_t)
        # play target pulse
        play(target_pulse, qe_t)
        wait(wait_rr, qe_t)

        # # finally perform readouts

        # measure("readout", rr_t, None,
        #     demod.full("integW_cos", It, out_t),
        #     demod.full("integW_minus_sin", Qt, out_t))
        measure_macro(qe_t, rr_t, out_t, It, Qt, pi_12=pi_12_in)
        # align(qe_t, rr_c)
        # measure("readout", rr_c, None,
        #     demod.full("integW_cos", Ic, out_c),
        #     demod.full("integW_minus_sin", Qc, out_c))
        measure_macro(qe_c, rr_c, out_c, Ic, Qc, pi_12=pi_12_in)

        save(It, I_t_st)
        save(Qt, Q_t_st)
        save(Ic, I_c_st)
        save(Qc, Q_c_st)

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

        # reset_frame(cr_elem)  ## checking if this changes things

        with for_(n, 0, n < n_avg, n + 1):
            with for_(t, t_min, t < t_max, t + dt):
                if simulate:
                    t = 100

                # wait(wait_init, qe_t)
                cooldown(time=wait_init)
                # reset_phase(rr_t)
                play("const" * amp(0.25), qe_t, t)
                wait(4, qe_t)
                measure_macro(qe_t, rr_t, out_t, Irabi, Qrabi, pi_12=pi_12)

                save(Irabi, I_rabi_st)
                save(Qrabi, Q_rabi_st)

                # play C0TI, get C0Z
                twoqubit_CR_ham_tomo_v2(cr_elem, 0, "I", wait_t, wait_rr, a_cr, Echo, pi_12)

                # play C0TX/2, get C0Y
                twoqubit_CR_ham_tomo_v2(cr_elem, 0, "X90", wait_t, wait_rr, a_cr, Echo, pi_12)

                # play C0T-Y/2, get C0X
                twoqubit_CR_ham_tomo_v2(cr_elem, 0, "mY90", wait_t, wait_rr, a_cr, Echo, pi_12)

                # playing C1TI, get C1Z
                twoqubit_CR_ham_tomo_v2(cr_elem, 1, "I", wait_t, wait_rr, a_cr, Echo, pi_12)

                # playing C1TX/2, get C1Y
                twoqubit_CR_ham_tomo_v2(cr_elem, 1, "X90", wait_t, wait_rr, a_cr, Echo, pi_12)

                # playing C1T-Y/2, get C1X
                twoqubit_CR_ham_tomo_v2(cr_elem, 1, "mY90", wait_t, wait_rr, a_cr, Echo, pi_12)
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

    job = qm.execute(CR_tomo)

    return job


def HT_setPhase_local_phase(qmm, cr_elem, p, t_min, t_max, dt, n_avg, wait_init, wait_t, wait_rr,
                            qe_c, qe_t, pi_12, simulate, echo_p, a_cr):
    t_list = np.arange(t_min, t_max, dt)

    rr_c = f'rr{qe_c[-1]}'
    rr_t = f'rr{qe_t[-1]}'

    out_c = adc_mapping[rr_c]
    out_t = adc_mapping[rr_t]

    Echo = echo_p
    pi_12_in = pi_12

    def twoqubit_CR_ham_tomo_v2(cr_elem, control: int, target_pulse,
                                wait_t, wait_rr,
                                a, echo1, pi_12_in):
        '''
        ### Pulse protocol:

        - Put control in 1 or 0 based on bool(control).
        - Send a cross resonance pulse of length 't' on cross resonance element (qubit_cr) with or without echo.
        - Send target_pulse on Target qubit.
        - Measurement pulse on target and control.
        - Save data on 4 streams.

        ### Requirements:
        - 4 streams : I_t_st, Q_t_st, I_c_st, Q_c_st
        - 5 variables : It, Qt, Ic, Qc and time 't' that is looped over
        '''

        # start
        # reset_phase(rr_t)
        # reset_phase(rr_c)

        echo = declare(bool, value=echo1)

        wait_t = int(wait_t)
        wait_rr = int(wait_rr)

        # align(rr_t, qe_t)
        align()
        # wait(wait_init, qe_t)
        cooldown(time=wait_init)
        align(qe_t, qe_c)
        # align()
        # set control to zero or one
        with if_(control == 1):
            play_X180(qe_c)
        with else_():
            play("I", qe_c)
        wait(wait_t, qe_c)
        # cooldown(time=wait_t, qe=qe_c)
        align(cr_elem, qe_c)
        frame_rotation_2pi(p, cr_elem)

        # do either simple CR or echo CR
        with if_(echo == False):
            play_flat_top(cr_elem, a, 2 * t)
        with else_():
            play_flat_top(cr_elem, a, t)
            align(qe_c, cr_elem)
            wait(wait_t, qe_c)
            play_X180(qe_c)
            align(cr_elem, qe_c)
            wait(wait_t, cr_elem)
            play_flat_top(cr_elem, -a, t)
            align(cr_elem, qe_c)
            wait(wait_t, qe_c)
            play_X180(qe_c)

        reset_frame(cr_elem)

        # align(cr_elem, qe_t)
        align()
        wait(wait_t, qe_t)
        # play target pulse
        play(target_pulse, qe_t)
        wait(wait_rr, qe_t)

        # # finally perform readouts

        # measure("readout", rr_t, None,
        #     demod.full("integW_cos", It, out_t),
        #     demod.full("integW_minus_sin", Qt, out_t))
        measure_macro(qe_t, rr_t, out_t, It, Qt, pi_12=pi_12_in)
        # align(qe_t, rr_c)
        # measure("readout", rr_c, None,
        #     demod.full("integW_cos", Ic, out_c),
        #     demod.full("integW_minus_sin", Qc, out_c))
        measure_macro(qe_c, rr_c, out_c, Ic, Qc, pi_12=pi_12_in)

        save(It, I_t_st)
        save(Qt, Q_t_st)
        save(Ic, I_c_st)
        save(Qc, Q_c_st)

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

        reset_frame(cr_elem)  ## checking if this changes things

        # frame_rotation_2pi(p, cr_elem)
        with for_(n, 0, n < n_avg, n + 1):
            with for_(t, t_min, t < t_max, t + dt):
                if simulate:
                    t = 100

                # wait(wait_init, qe_t)
                reset_frame(cr_elem)  ## checking if this changes things
                cooldown(time=wait_init)
                # reset_phase(rr_t)
                play("const" * amp(0.25), qe_t, t)
                wait(4, qe_t)
                measure_macro(qe_t, rr_t, out_t, Irabi, Qrabi, pi_12=pi_12)

                save(Irabi, I_rabi_st)
                save(Qrabi, Q_rabi_st)

                # play C0TI, get C0Z
                twoqubit_CR_ham_tomo_v2(cr_elem, 0, "I", wait_t, wait_rr, a_cr, Echo, pi_12)

                # play C0TX/2, get C0Y
                twoqubit_CR_ham_tomo_v2(cr_elem, 0, "X90", wait_t, wait_rr, a_cr, Echo, pi_12)

                # play C0T-Y/2, get C0X
                twoqubit_CR_ham_tomo_v2(cr_elem, 0, "mY90", wait_t, wait_rr, a_cr, Echo, pi_12)

                # playing C1TI, get C1Z
                twoqubit_CR_ham_tomo_v2(cr_elem, 1, "I", wait_t, wait_rr, a_cr, Echo, pi_12)

                # playing C1TX/2, get C1Y
                twoqubit_CR_ham_tomo_v2(cr_elem, 1, "X90", wait_t, wait_rr, a_cr, Echo, pi_12)

                # playing C1T-Y/2, get C1X
                twoqubit_CR_ham_tomo_v2(cr_elem, 1, "mY90", wait_t, wait_rr, a_cr, Echo, pi_12)
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

    job = qm.execute(CR_tomo)

    return job
