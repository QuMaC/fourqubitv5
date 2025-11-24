from qm.qua import *
import numpy as np
from Configuration_Files.configuration_4qubitsv3 import cr_amp, cr_len_ns, optimal_readout_phase, grft_arr_gen
from Configuration_Files.config_dictionaries import *
import sympy as sym
import sys
from scipy.signal.windows import gaussian
import requests
import time


def play_X180(qe, a=None, t=None):
    if a is None:
        a = 1

    if t is None:
        play('d_X180' * amp(a), qe)
    else:
        play('d_X180' * amp(a), qe, t)


def play_X90(qe, a=None, t=None):
    if a is None:
        a = 1

    if t is None:
        play('d_X90' * amp(a), qe)
    else:
        play('d_X90' * amp(a), qe, t)


def play_Y180(qe, a=None, t=None):
    if a is None:
        a = 1

    if t is None:
        play('d_Y180' * amp(a), qe)
    else:
        play('d_Y180' * amp(a), qe, t)


def play_Y90(qe, a=None, t=None):
    if a is None:
        a = 1

    if t is None:
        play('d_Y90' * amp(a), qe)
    else:
        play('d_Y90' * amp(a), qe, t)


def play_mX90(qe, a=None, t=None):
    if a is None:
        a = 1

    if t is None:
        play('d_mX90' * amp(a), qe)
    else:
        play('d_mX90' * amp(a), qe, t)


def play_mY90(qe, a=None, t=None):
    if a is None:
        a = 1

    if t is None:
        play('d_mY90' * amp(a), qe)
    else:
        play('d_mY90' * amp(a), qe, t)


def play_flat_top(qe, a, t=5):
    play("rise" * amp(a), qe)
    play("const" * amp(a), qe, duration=t)
    # play("grft" * amp(a), qe, duration=t)## trial #TODO
    play("fall" * amp(a), qe)


def cooldown(time=250000, active_reset=False, qe=None, qe_12=None, rr=None, out=None, I=None, Q=None, pi_12=False,
             dem=None):
    # print(qe)
    if active_reset:

        measure_macro(qe, rr, out, I, Q, pi_12=pi_12)
        if pi_12:
            align(rr, qe_12)
            play("X180", qe_12, condition=I > dem)
            align(qe_12, qe)
            play("X180", qe, condition=I > dem)

        else:
            align(rr, qe)
            play("X180", qe, condition=I > dem)

    else:
        # reset_frame('q6')
        # if qe == 'q6':
        #     # play("const"*amp(stark_amp['6']), 'stark_6')
        #     play(ramp(0.0027*0.4), 'stark_6', duration=80)
        # if qe:
        #     wait(time, qe)

        # if qe != 'q7':
            # play(ramp(0.0027 * 0.0), 'stark_6', duration=80)
        if type(qe) == list:
            wait(time, *qe)
        elif type(qe) == str:
            wait(time, qe)
        else:
            wait(time)



def BB1_X180(qe):
    ''''
        Make sure you align before and after if necessary. No alignment inside
        Last pulse inside is: play(pulse_type, qe)
    '''

    phi = np.arccos(-0.25) / (2 * np.pi)

    # phi_in = declare(fixed)
    # phi_in1 = declare(fixed)
    # phi_in2 = declare(fixed)
    # phi_in3 = declare(fixed)
    # assign(phi_in, phi)
    # assign(phi_in1, 2 * phi)
    # assign(phi_in2, -2 * phi)
    # assign(phi_in3, -1 * phi)

    frame_rotation_2pi(phi, qe)
    play("d_X180", qe)
    frame_rotation_2pi(2 * phi, qe)
    play("d_X360", qe)
    frame_rotation_2pi(-2 * phi, qe)
    play("d_X180", qe)
    frame_rotation_2pi(-1 * phi, qe)
    play("d_X180", qe)


def UCP5b_Y180(qe):
    frame_rotation_2pi(-0.25, qe)
    UCP5b_X180(qe)
    frame_rotation_2pi(0.25, qe)


def CPMG_90(pulse_type, qe):
    play(pulse_type, qe)
    UCP5b_X180(qe)
    wait(12, qe)  # Might have to remove or tune this
    UCP5b_X180(qe)


def UCP5b_X180(qe):
    ''''
        Make sure you align before and after if necessary. No alignment inside
        Last pulse inside is: play(pulse_type, qe)
    '''

    phi1 = 11 / 12
    phi2 = -0.75

    # phi_in1 = declare(fixed)
    # phi_in2 = declare(fixed)
    # phi_in3 = declare(fixed)
    # phi_in4 = declare(fixed)
    #
    # assign(phi_in1, phi1)
    # assign(phi_in2, phi2)
    # assign(phi_in3, phi3)
    # assign(phi_in4, -1 * phi3)

    play("d_X180", qe)
    frame_rotation_2pi(phi1, qe)
    play("d_X180", qe)
    frame_rotation_2pi(phi2, qe)
    play("d_X180", qe)
    frame_rotation_2pi(-1 * phi2, qe)
    play("d_X180", qe)
    frame_rotation_2pi(-1 * phi1, qe)
    play("d_X180", qe)


def KNILL_Y180(qe):
    frame_rotation_2pi(0.25)
    KNILL_X180(qe)
    frame_rotation_2pi(-0.25)


def KNILL_X180(qe):
    ''''
        Make sure you align before and after if necessary. No alignment inside
        Last pulse inside is: play(pulse_type, qe)
    '''

    phi1 = 1 / 12  # (np.pi/6) / (2*np.pi)
    phi2 = 0.25  # (np.pi/2) / (2*np.pi)
    # phi3 = -1/6#(-1*np.pi/3) / (2*np.pi)

    # phi_in1 = declare(fixed)
    # phi_in2 = declare(fixed)
    # phi_in3 = declare(fixed)
    # phi_in4 = declare(fixed)
    # phi_in6 = declare(fixed)
    #
    # assign(phi_in1, phi1)
    # assign(phi_in2, -1 * phi1)
    # assign(phi_in3, phi2)
    # assign(phi_in4, -1 * phi2)
    # assign(phi_in6, -2 * phi1)

    frame_rotation_2pi(phi1, qe)
    play_X180(qe)
    frame_rotation_2pi(-1 * phi1, qe)
    play_X180(qe)
    frame_rotation_2pi(phi2, qe)
    play_X180(qe)
    frame_rotation_2pi(-1 * phi2, qe)
    play_X180(qe)
    frame_rotation_2pi(phi1, qe)
    play_X180(qe)
    frame_rotation_2pi(-2 * phi1, qe)


def BB1_X90(qe):
    ''''
        Make sure you align before and after if necessary. No alignment inside
        Last pulse inside is: play(pulse_type, qe)
    '''

    phi = np.arccos(-0.125) / (2 * np.pi)

    # phi_in = declare(fixed)
    # phi_in1 = declare(fixed)
    # phi_in2 = declare(fixed)
    # phi_in3 = declare(fixed)
    # assign(phi_in, phi)
    # assign(phi_in1, 2 * phi)
    # assign(phi_in2, -2 * phi)
    # assign(phi_in3, -1 * phi)

    frame_rotation_2pi(phi, qe)
    play("d_X180", qe)
    frame_rotation_2pi(2 * phi, qe)
    play("d_X360", qe)
    frame_rotation_2pi(-2 * phi, qe)
    play("d_X180", qe)
    frame_rotation_2pi(-1 * phi, qe)
    play("d_X90", qe)


def BB1_mX90(qe):
    ''''
        Make sure you align before and after if necessary. No alignment inside
        Last pulse inside is: play(pulse_type, qe)
    '''

    phi = np.arccos(0.125) / (2 * np.pi)

    # phi_in = declare(fixed)
    # phi_in1 = declare(fixed)
    # phi_in2 = declare(fixed)
    # phi_in3 = declare(fixed)
    # assign(phi_in, phi)
    # assign(phi_in1, 2 * phi)
    # assign(phi_in2, -2 * phi)
    # assign(phi_in3, -1 * phi)

    frame_rotation_2pi(phi, qe)
    play("d_X180", qe)
    frame_rotation_2pi(2 * phi, qe)
    play("d_X360", qe)
    frame_rotation_2pi(-2 * phi, qe)
    play("d_X180", qe)
    frame_rotation_2pi(-1 * phi, qe)
    play("d_mX90", qe)


def BB1_Y180(qe):
    ''''
        Make sure you align before and after if necessary. No alignment inside
        Last pulse inside is: play(pulse_type, qe)
    '''
    # phi = np.arccos(-0.375) / (2 * np.pi)
    #
    # # phi_in = declare(fixed)
    # # phi_in1 = declare(fixed)
    # # phi_in2 = declare(fixed)
    # # phi_in3 = declare(fixed)
    # # assign(phi_in, phi)
    # # assign(phi_in1, 2 * phi)
    # # assign(phi_in2, -2 * phi)
    # # assign(phi_in3, -1 * phi)
    #
    # frame_rotation_2pi(phi, qe)
    # play("d_X180", qe)
    # frame_rotation_2pi(2*phi, qe)
    # play("d_X360", qe)
    # frame_rotation_2pi(-2*phi, qe)
    # play("d_X180", qe)
    # frame_rotation_2pi(-1*phi, qe)
    # play("d_Y180", qe)
    frame_rotation_2pi(-0.25, qe)
    BB1_X180(qe)
    frame_rotation_2pi(0.25, qe)


def BB1_Y90(qe):
    '''
        Make sure you align before and after if necessary. No alignment inside
        Last pulse inside is: play(pulse_type, qe)
    '''
    # phi = np.arccos(-0.25) / (2 * np.pi)

    # phi_in = declare(fixed)
    # phi_in1 = declare(fixed)
    # phi_in2 = declare(fixed)
    # phi_in3 = declare(fixed)
    # assign(phi_in, phi)
    # assign(phi_in1, 2 * phi)
    # assign(phi_in2, -2 * phi)
    # assign(phi_in3, -1 * phi)

    # frame_rotation_2pi(phi, qe)
    # play("d_X180", qe)
    # frame_rotation_2pi(2*phi, qe)
    # play("d_X360", qe)
    # frame_rotation_2pi(-2*phi, qe)
    # play("d_X180", qe)
    # frame_rotation_2pi(-1*phi, qe)
    # play("d_Y90", qe)
    frame_rotation_2pi(-0.25, qe)
    BB1_X90(qe)
    frame_rotation_2pi(0.25, qe)
    # frame_rotation_2pi(-0.25, qe)
    # BB1_X90(qe)
    # frame_rotation_2pi(0.25, qe)


def BB1_mY90(qe):
    ''''
        Make sure you align before and after if necessary. No alignment inside
        Last pulse inside is: play(pulse_type, qe)
    '''
    # phi = np.arccos(0) / (2 * np.pi)

    # phi_in = declare(fixed)
    # phi_in1 = declare(fixed)
    # phi_in2 = declare(fixed)
    # phi_in3 = declare(fixed)
    # assign(phi_in, phi)
    # assign(phi_in1, 2 * phi)
    # assign(phi_in2, -2 * phi)
    # assign(phi_in3, -1 * phi)

    # frame_rotation_2pi(phi, qe)
    # play("d_X180", qe)
    # frame_rotation_2pi(2*phi, qe)
    # play("d_X360", qe)
    # frame_rotation_2pi(-2*phi, qe)
    # play("d_X180", qe)
    # frame_rotation_2pi(-1*phi, qe)
    #
    # play("d_mY90", qe)
    frame_rotation_2pi(-0.25, qe)
    BB1_mX90(qe)
    frame_rotation_2pi(0.25, qe)


# def play_cmd_t(pulse_type, qe, t, BB_flg):
#     ''''
#         Make sure you align before and after if necessary. No alignment inside
#         Last pulse inside is: play(pulse_type, qe)
#     '''
#     flg = declare(bool)
#     assign(flg, BB_flg)
#     phi = 0
#     phi_in = declare(fixed)
#     phi_in1 = declare(fixed)
#     phi_in2 = declare(fixed)
#     assign(phi_in, phi)
#     assign(phi_in1, 3 * phi)
#     assign(phi_in2, -3 * phi)
#     if "180" in pulse_type:
#         phi = np.arccos(-0.375) / (2 * np.pi)
#         assign(phi_in, phi)
#         assign(phi_in1, 3 * phi)
#         assign(phi_in2, -3 * phi)
#     elif "90" in pulse_type:
#         phi = np.arccos(-0.375) / (2 * np.pi)
#         assign(phi_in, phi)
#         assign(phi_in1, 2 * phi)
#         assign(phi_in2, -2 * phi)
#     with if_(flg):
#         frame_rotation_2pi(phi_in, qe)
#         play_Y180(qe)
#         frame_rotation_2pi(phi_in1, qe)
#         play("Y360", qe)
#         frame_rotation_2pi(phi_in2, qe)
#         play_Y180(qe)
#         # frame_rotation_2pi(phi_in2, qe)
#         play(pulse_type, qe, t)
#     with else_():
#         play(pulse_type, qe, t)

def measure_macro_acc(qe, rr, out, I_d, Q_d, I_seg, Q_seg, rd_id, pi_12=False):
    wait_rr = 4
    qe12 = f"q12_{rr[-1]}"

    max_signal_sample = max_signal_section[qe[-1]]

    seg_length = ro_len_clk[rr[-1]] // (num_segment)

    assign(I_d, 0)
    assign(Q_d, 0)
    assign(rd_id, 0)

    if pi_12:
        align(qe, qe12)
        wait(4, qe12)
        # play_X180(qe12)
        play('X180', qe12)
        # if qe == 'q6':
        align('stark_6', qe12)
        ramp_to_zero('stark_6')
        wait(4, 'stark_6')
        align('stark_6', qe12)

        wait(wait_rr, rr)

        align(qe12, rr)
        wait(wait_rr, rr)

        # wait(4, qe12)
    else:
        if qe == 'q6' or qe == 'q12_6':
            if '12' not in qe:
                align('stark_6', qe)
                ramp_to_zero('stark_6')
                align('stark_6', rr)
            else:
                q_d = f'q{qe[-1]}'
                align('stark_6', qe)
                ramp_to_zero('stark_6')
                align('stark_6', rr)
            # align(qe, rr, 'stark_6')
            wait(wait_rr, rr)
        else:
            align(qe, rr)
            ##temp
        align('stark_6', qe)
        ramp_to_zero('stark_6')
        align('stark_6', rr)
        ##end temp
        wait(wait_rr, rr)

    # reset_phase(rr)
    # measure("readout", rr, None,
    # demod.full("integW_cos", I, out),
    # demod.full("integW_minus_sin", Q, out))

    measure("readout", rr, None,
            demod.accumulated("integW_cos", I_seg, seg_length, out),
            demod.accumulated("integW_minus_sin", Q_seg, seg_length, out))

    with for_(rd_id, max_signal_sample - acc_data_width // 2, rd_id < max_signal_sample - acc_data_width // 2 + 1,
              rd_id + 1):  # save a QUA array
        # save(I_seg[rd_id], I_data_st)
        assign(I_d, I_d + I_seg[rd_id])

    with for_(rd_id, max_signal_sample - acc_data_width // 2, rd_id < max_signal_sample - acc_data_width // 2 + 1,
              rd_id + 1):  # save a QUA array
        # save(Q_seg[rd_id], Q_data_st)
        assign(Q_d, Q_d + Q_seg[rd_id])


def measure_macro(qe, rr, out, I, Q, pi_12=False):
    wait_rr = 4
    qe12 = f"q12_{rr[-1]}"

    if pi_12:
        align(qe, qe12)
        wait(4, qe12)
        play('X180', qe12)
        # wait(4, qe12)
        # align('stark_6', qe12)
        # ramp_to_zero('stark_6')
        # wait(4, 'stark_6')
        # align('stark_6', qe12)

        wait(wait_rr, rr)

        align(qe12, rr)
        wait(wait_rr, rr)

        # wait(4, qe12)
    else:
        # if qe == 'q6' or qe == 'q12_6':
        #     if '12' not in qe:
        #         align('stark_6', qe)
        #         ramp_to_zero('stark_6')
        #         align('stark_6', rr)
        #     else:
        #         q_d = f'q{qe[-1]}'
        #         align('stark_6', qe)
        #         ramp_to_zero('stark_6')
        #         align('stark_6', rr)
        #     # align(qe, rr, 'stark_6')
        #     wait(wait_rr, rr)
        # else:
        align(qe, rr)
        # align('stark_6', qe)
        # ramp_to_zero('stark_6')
        # align('stark_6', rr)
        wait(wait_rr, rr)

    # reset_phase(rr)
    measure("readout", rr, None,
            demod.full("integW_cos", I, out),
            demod.full("integW_minus_sin", Q, out))

def measure_macro_no_ramp(qe, rr, out, I, Q, pi_12=False):
    wait_rr = 4
    qe12 = f"q12_{rr[-1]}"

    if pi_12:
        align(qe, qe12)
        wait(4, qe12)
        play('X180', qe12)
        wait(4, qe12)
        align(qe12, rr)
        wait(wait_rr, rr)

        # wait(4, qe12)
    else:
        align(qe, rr)
        wait(wait_rr, rr)

    # reset_phase(rr)
    measure("readout", rr, None,
            demod.full("integW_cos", I, out),
            demod.full("integW_minus_sin", Q, out))


def play_I(qe):
    play('I', qe)

def update_config_rr(config, q_no, rr_no, a_rr, integ_len):
    config["pulses"][f"q{q_no}_ro_pulse"]["length"] = integ_len * 4
    config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "arbitrary",
                                              "samples": grft_arr_gen((integ_len * 4, 200),
                                                                      [a_rr])}

    config["integration_weights"][f"integW_cos_rr{rr_no}"]["cosine"] = [
        (np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len * 4)]
    config["integration_weights"][f"integW_cos_rr{rr_no}"]["sine"] = [
        (-np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len * 4)]

    config["integration_weights"][f"integW_sin_rr{rr_no}"]["cosine"] = [
        (np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len * 4)]
    config["integration_weights"][f"integW_sin_rr{rr_no}"]["sine"] = [
        (np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len * 4)]

    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"]["cosine"] = [
        (-np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len * 4)]
    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"]["sine"] = [
        (-np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len * 4)]


def Hadamard(qe):
    # frame_rotation_2pi(-0.5, qe)
    play_Y90(qe)
    play_X180(qe)
    # play_Y180(qe)


# def Hadamard(qe):
#
#     # frame_rotation_2pi(-0.5, qe)
#     play_X90(qe)
#     frame_rotation_2pi(-0.5, qe)
#     play_X90(qe)


def ZXby4(qe_cr, qe_c, a=1.0, t=28):
    tby2 = t // 2
    play_flat_top(qe_cr, a, tby2)
    align(qe_c, qe_cr)


def ZXby4_AC(qe_cr, qe_ac, qe_c, a_cr=1.0, a_ac=0.0, t=28):
    tby2 = t // 2
    align(qe_cr, qe_ac)
    play_flat_top(qe_cr, a_cr, tby2)
    play_flat_top(qe_ac, a_ac, tby2)
    align(qe_c, qe_cr, qe_ac)


def ZXby2_echo_noAC(qe_cr, qe_c, qe_t):
    a = cr_amp[qe_cr]
    t = cr_len_ns[qe_cr] // 4

    tby2 = t // 2

    align(qe_cr, qe_c, qe_t)

    # frame_rotation_2pi(cr_phase[qe_cr], qe_cr)

    frame_rotation_2pi(cr_phase[qe_cr], qe_cr)
    # frame_rotation_2pi(cr_phase[qe_ac], qe_ac)

    align(qe_cr, qe_c, qe_t)
    play_flat_top(qe_cr, a, tby2)
    align(qe_c, qe_cr)
    wait(4, qe_c)
    play_X180(qe_c)
    align(qe_c, qe_cr)
    play_flat_top(qe_cr, -a, tby2)
    align(qe_c, qe_cr)
    wait(4, qe_c)
    play_X180(qe_c, a=-1)
    reset_frame(qe_cr)


def ZXby2_echo_AC(qe_cr, qe_ac, qe_c, qe_t):
    a_cr = cr_amp[qe_cr]
    a_ac = cr_amp[qe_ac]
    t = cr_len_ns[qe_cr] // 4

    tby2 = t // 2


    # fast_frame_rotation(p_cr_cos, p_cr_sin, qe_cr)
    # fast_frame_rotation(p_ac_cos, p_ac_sin, qe_ac)

    # frame_rotation_2pi(cr_phase[qe_cr], qe_cr)
    # frame_rotation_2pi(cr_phase[qe_ac], qe_ac)

    # align(qe_cr, qe_ac)
    # play_flat_top(qe_cr, a_cr, tby2)
    # play_flat_top(qe_ac, a_ac, tby2)
    # align(qe_c, qe_cr)
    # wait(4, qe_c)
    # play_X180(qe_c)
    # wait(4, qe_c)
    # align(qe_c, qe_cr, qe_ac)
    # play_flat_top(qe_cr, -a_cr, tby2)
    # play_flat_top(qe_ac, -a_ac, tby2)
    # align(qe_c, qe_cr, qe_ac)
    # wait(4, qe_c)
    # play_X180(qe_c)

    align(qe_cr, qe_c, qe_t, qe_ac)

    frame_rotation_2pi(cr_phase[qe_cr], qe_cr)
    frame_rotation_2pi(cr_phase[qe_ac], qe_ac)
    play_flat_top(qe_cr, a_cr, tby2)
    play_flat_top(qe_ac, a_ac, tby2)
    align(qe_c, qe_cr)
    wait(4, qe_c)
    play_X180(qe_c)
    align(qe_c, qe_cr, qe_ac)
    play_flat_top(qe_cr, -a_cr, tby2)
    play_flat_top(qe_ac, -a_ac, tby2)
    align(qe_c, qe_cr)
    wait(4, qe_c)
    play_X180(qe_c, a=-1)
    reset_frame(qe_cr)
    reset_frame(qe_ac)
    # frame_rotation_2pi(cr_control_phase[qe_cr], qe_c)
    # wait(4, qe_c)
    # play_I(qe_c)
    # frame_rotation_2pi(cr_target_phase[qe_cr], qe_t)


def CNOT_macro(qe_c, qe_t, AC_flg=False):
    c, t = qe_c[-1], qe_t[-1]

    if int(c) in control_qubits:

        qe_cr = f"cr_c{c}t{t}"
        qe_ac = f"cr_ac_c{c}t{t}"

        frame_rotation_2pi(0.25, qe_c)
        if AC_flg:
            ZXby2_echo_AC(qe_cr, qe_ac, qe_c, qe_t)
        else:
            ZXby2_echo_noAC(qe_cr, qe_c, qe_t)
        #
        align(qe_cr, qe_t)
        wait(4, qe_t)
        play_mX90(qe_t)
        wait(4, qe_t)

    else:

        qe_cr = f"cr_c{t}t{c}"

        align(qe_cr, qe_c, qe_t)

        Hadamard(qe_c)
        Hadamard(qe_t)
        wait(4, qe_c)
        align(qe_cr, qe_c, qe_t)
        CNOT_macro(qe_t, qe_c)
        wait(4, qe_c)
        align(qe_cr, qe_c, qe_t)
        Hadamard(qe_c)
        Hadamard(qe_t)


def SWAP_macro(q1, q2, AC_flag=False):
    CNOT_macro(q1, q2, AC_flag)
    CNOT_macro(q2, q1, AC_flag)
    CNOT_macro(q1, q2, AC_flag)


def iSWAP_macro(q1, q2, AC_flag=False):
    # frame_rotation_2pi(-0.25, q1)
    # frame_rotation_2pi(-0.25, q2)
    # Hadamard(q1)
    # CNOT_macro(q1, q2)
    # CNOT_macro(q2, q1)
    # Hadamard(q2)

    CNOT_macro(q1, q2, AC_flag)
    CNOT_macro(q2, q1, AC_flag)
    play_X90(q2)  # switched X/2 to -X/2
    play_mY90(q2)  # switched Y/2 to -Y/2
    play_mX90(q2)  # switched -X/2 to X/2
    CNOT_macro(q1, q2, AC_flag)


def CZ_macro(fgge_elem, qe_t, qe_c):
    a_cz = 1.0
    t_cz = 600 // 4

    # align(qe_c, fgge_elem, qe_t)
    # play_X180(qe_c)
    align(qe_c, fgge_elem, qe_t)
    play("const" * amp(a_cz), fgge_elem, t_cz)
    align(qe_c, qe_t, fgge_elem)
    # frame_rotation_2pi(0.075, qe_c)
    frame_rotation_2pi(-0.5, qe_t)
