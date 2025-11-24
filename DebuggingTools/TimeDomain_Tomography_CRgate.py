from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import *
from Helper_Functions.analysis_functions import *

simulate = False
save_data = True
pi_12 = True
update_pars = False

###################
# The QUA program #
###################
t_min = 16 // 4  # ns
t_max = 10000 // 4
dt = 16 // 4  # steps of 4ns
t_list = np.arange(t_min, t_max, dt)


# t_min = 16//4   #ns
# t_max = 17500//4
# dt = 60//4 #steps of 4ns
# t_list = np.arange(t_min, t_max, dt)

def ZX_macro_local_echo_AC(qe_cr, qe_ac, qe_c, qe_t):
    a_cr = cr_amp[qe_cr]
    a_ac = cr_amp[qe_ac]
    t = cr_len_ns[qe_cr] // 4

    tby2 = t // 2

    p_c_cos = np.cos(cr_control_phase[qe_cr] * 2 * np.pi)
    p_c_sin = np.sin(cr_control_phase[qe_cr] * 2 * np.pi)

    # align(qe_cr, qe_c, qe_t)
    # play_flat_top(qe_cr, a_cr, tby2)
    # align(qe_c, qe_cr)
    # wait(4, qe_c)
    # play_X180(qe_c)
    # align(qe_c, qe_cr)
    # play_flat_top(qe_cr, -a_cr, tby2)
    # align(qe_c, qe_cr)
    # wait(4, qe_c)
    # play_X180(qe_c, a=-1)

    #
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
    # fast_frame_rotation(p_c_cos, p_c_sin, qe_c)
    align(qe_cr, qe_c, qe_t, qe_ac)
    # frame_rotation_2pi(0*cr_control_phase[qe_cr], qe_c)
    wait(4)


# p_min = 0
# p_max = 2
# dp = 0.01
# p_list = np.arange(p_min, p_max, dp)

# q_no = 5
c_no, t_no = 5, 6
qubit_IF = q_IF[str(t_no)]
qe = f"q{c_no}"

qe_12 = f"q12_{c_no}"
rr = f"rr{c_no}"
if c_no in control_qubits:
    qe_cr = f"cr_c{c_no}t{t_no}"
    qe_ac = f"cr_ac_c{c_no}t{t_no}"
else:
    qe_cr = f"cr_c{t_no}t{c_no}"
    qe_ac = f"cr_ac_c{t_no}t{c_no}"

qe_c, qe_t = f"q{c_no}", f"q{t_no}"
rr_c, rr_t = f"rr{c_no}", f"rr{t_no}"

qe = qe_t
rr = rr_t

out = adc_mapping[rr]
ro_len = ro_len_clk[qe[-1]]
ZZ_shift = CrossKerr[qe[-1]] * 1e-6

det_bare = 1
det = det_bare - ZZ_shift  # in MHz

if simulate:
    rep_rate_clk = 100
else:
    rep_rate_clk = 250000

dem = demarcations[qe[-1]]
wait_rr = 16
pi_len = pi_len_ns[qe[-1]]
piby2_len = piby2_len_ns[qe[-1]]

with program() as ramsey:
    n = declare(int)
    Ix = declare(fixed)
    Ix_st = declare_stream()
    Qx = declare(fixed)
    Qx_st = declare_stream()
    Iy = declare(fixed)
    Iy_st = declare_stream()
    Qy = declare(fixed)
    Qy_st = declare_stream()
    Iz = declare(fixed)
    Iz_st = declare_stream()
    Qz = declare(fixed)
    Qz_st = declare_stream()
    t = declare(int)
    p = declare(float)

    # update_frequency(qe_t, qubit_IF + det * u.MHz)

    with for_(n, 0, n < 1000, n + 1):
        with for_(t, t_min, t < t_max, t + dt):
            # frame_rotation_2pi(-0.46, qe_c)
            # with for_(p, p_min, p < p_max, p + dp):
            if simulate:
                assign(t, 100)

            reset_frame(qe_cr, qe_ac, qe_c, qe_t)
            # reset_frame(rr)
            cooldown(time=rep_rate_clk)

            # CNOT_macro(qe_c, qe_t, AC_flg=True)
            align()
            measure_macro(qe, rr, out, Iz, Qz, pi_12=pi_12)

            save(Iz, Iz_st)
            save(Qz, Qz_st)

            align()

            cooldown(time=rep_rate_clk)

            # CNOT_macro(qe_c, qe_t, AC_flg=True)
            align()
            play_X90(qe)
            align()
            measure_macro(qe, rr, out, Iy, Qy, pi_12=pi_12)

            save(Iy, Iy_st)
            save(Qy, Qy_st)


            # CNOT_macro(qe_c, qe_t, AC_flg=True)
            align()
            play_mY90(qe)
            align()
            measure_macro(qe, rr, out, Ix, Qx, pi_12=pi_12)

            save(Ix, Ix_st)
            save(Qx, Qx_st)

    with stream_processing():
        Ix_st.buffer(len(t_list)).average().save('Ix')
        Qx_st.buffer(len(t_list)).average().save('Qx')
        Iy_st.buffer(len(t_list)).average().save('Iy')
        Qy_st.buffer(len(t_list)).average().save('Qy')
        Iz_st.buffer(len(t_list)).average().save('Iz')
        Qz_st.buffer(len(t_list)).average().save('Qz')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
if simulate:
    # qmm = QuantumMachinesManager()
    job = qmm.simulate(config, ramsey, SimulationConfig(int(10000)))
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
    plt.show(block=False)
    raise Halted()
#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(ramsey)
res_handles = job.result_handles
Ix_handle = job.result_handles.get("Ix")
Qx_handle = job.result_handles.get("Qx")
Iy_handle = job.result_handles.get("Iy")
Qy_handle = job.result_handles.get("Qy")
Iz_handle = job.result_handles.get("Iz")
Qz_handle = job.result_handles.get("Qz")
# job.result_handles.wait_for_all_values()

fig, ax = plt.subplots(3, 1, sharex=True, sharey='row')
# plt.title("Tomography")
Ix_handle.wait_for_values(1)
Qx_handle.wait_for_values(1)

plot_no = 1

with open('../Configuration_Files/System_Parameters/01_levels.json','r') as f:
    levels = json.load(f)
    f.close()

z_level = levels[qe]['0']
o_level = levels[qe]['1']
while res_handles.is_processing():
    Ix = Ix_handle.fetch_all()
    Qx = Qx_handle.fetch_all()
    Iy = Iy_handle.fetch_all()
    Qy = Qy_handle.fetch_all()
    Iz = Iz_handle.fetch_all()
    Qz = Qz_handle.fetch_all()
    # sig = I + 1j * Q
    # plt.clf()
    for a in ax:
        a.clear()

    ax[0].plot(t_list, Ix, label='Ix')
    ax[1].plot(t_list, Iy, label='Iy')
    ax[2].plot(t_list, Iz, label='Iz')
    ax[0].set_title("Ix")
    ax[1].set_title("Iy")
    ax[2].set_title("Iz")

    for a in ax:
        a.grid()
        a.legend(loc='upper right')
        a.axhline(z_level, color='red')
        a.axhline(o_level, color='blue')

    # plt.show(block=False)
    fig.canvas.draw()

    # # plt.plot(4e-3*p_list, Q, marker=".", label="Q")
    # plt.xlabel("time")
    # plt.ylabel("Ampl")
    # plt.title("Tomography")
    # # plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.grid()
    plt.legend()
    plt.pause(1)
    plot_no += 1

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

p_list_us = 4e-3*t_list

#
# def ramsey_fit_phase(t, A, f, ph, c):
#     return A * np.sin(t * 2 * np.pi * f + ph) + c
#
#
# res_I, pcov_i, init_i = ramsey_fitting(p_list_us, I)  # A, tau, offset, freq, phi
#
# pars = [res_I[0], init_i[-2], res_I[4], res_I[2]]
#
# #
# # pars, cov = curve_fit(f=ramsey_fit_phase, xdata=p_list_us, ydata=I, p0=[(max(I) - min(I)) / 2, 1, np.pi / 2, np.mean(I)],
# #                       bounds=(-np.inf, np.inf), maxfev=10000)
#
# ram_p = np.round(pars[2], 5)
#
# print('#########################')
# print('### Fitted Parameters ###')
# print('#########################')
# print(f"Ramsey phase = {ram_p:.3f}")
# # print('Covariance Matrix')
# # print(cov)
#
# plt.figure()
# plt.plot(p_list_us, I, ".")
# plt.plot(p_list_us, ramsey_fit_phase(p_list_us, *pars))
# plt.xlabel('phase')
# plt.ylabel("Ramsey Amplitude")
# plt.title(f"Ramsey phase = {ram_p:.3f} MHz")
# plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
# plt.grid()
# plt.show(block=False)
#
# if save_data:
#     file_saver_(np.transpose([p_list_us, I, Q]), file_name=__file__, suffix=qe, master_folder=ExpName,
#                 header_string="Time (us), MAgnitude, I, Q")
