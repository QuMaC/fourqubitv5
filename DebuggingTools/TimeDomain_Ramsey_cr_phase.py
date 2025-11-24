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
# t_min = 16//4   #ns
# t_max = 10000//4
# dt = 16//4 #steps of 4ns
# t_list = np.arange(t_min, t_max, dt)

# t_min = 16//4   #ns
# t_max = 17500//4
# dt = 60//4 #steps of 4ns
# t_list = np.arange(t_min, t_max, dt)

def ZX_macro_local_echo_AC(qe_cr, qe_ac, qe_c, qe_t):
    a_cr = cr_amp[qe_cr]
    a_ac = cr_amp[qe_ac]
    t = cr_len_ns[qe_cr] // 4

    tby2 = t // 2

    # p_c_cos = np.cos(cr_control_phase[qe_cr] * 2 * np.pi)
    # p_c_sin = np.sin(cr_control_phase[qe_cr] * 2 * np.pi)

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


p_min = 0
p_max = 2
dp = 0.01
p_list = np.arange(p_min, p_max, dp)

# q_no = 5
c_no, t_no = 5, 2
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

qe = qe_c
rr = rr_c

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
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    t = declare(int)
    p = declare(float)
    ph = declare(float)

    # update_frequency(qe_t, qubit_IF + det * u.MHz)

    with for_(n, 0, n < 1000, n + 1):
        # with for_(t, t_min, t < t_max, t + dt):
        # frame_rotation_2pi(-0.46, qe_c)
        with for_(p, p_min, p < p_max, p + dp):
            if simulate:
                assign(t, 100)

            reset_frame(qe_cr, qe_ac, qe, rr)
            # reset_frame(rr)
            cooldown(time=rep_rate_clk)

            play_X90(qe)
            # align(qe_cr, qe_ac, qe_c, qe_t)
            # wait(4)
            ZXby2_echo_AC(qe_cr, qe_ac, qe_c, qe_t)
            # wait(232)
            if qe == qe_c:
                assign(ph, p + cr_control_phase[qe_cr])
                frame_rotation_2pi(ph, qe)
            else:
                assign(ph, p + cr_target_phase[qe_cr])
                frame_rotation_2pi(ph, qe)

            play_X90(qe)
            # Hadamard(qe)
            align()
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(p_list)).average().save('I')
        Q_st.buffer(len(p_list)).average().save('Q')

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
I_handle = job.result_handles.get("I")
Q_handle = job.result_handles.get("Q")
# job.result_handles.wait_for_all_values()

plt.figure()
plt.title("Ramsey")
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)

plot_no = 1
while res_handles.is_processing():
    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    sig = I + 1j * Q
    plt.clf()
    # plt.plot(4e-3*p_list, Q, marker=".", label="Q")
    plt.plot(p_list, I, marker=".", label="I")
    plt.xlabel("phase")
    plt.ylabel("Ramsey Amplitude")
    plt.title("Ramsey N = {0}".format(plot_no * 20))
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.grid()
    plt.legend()
    plt.pause(1)
    plot_no += 1

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

p_list_us = p_list


def ramsey_fit_phase(t, A, f, ph, c):
    return A * np.sin(t * 2 * np.pi * f + ph) + c


res_I, pcov_i, init_i = ramsey_fitting(p_list_us, I)  # A, tau, offset, freq, phi

pars = [res_I[0], init_i[-2], res_I[4], res_I[2]]

#
# pars, cov = curve_fit(f=ramsey_fit_phase, xdata=p_list_us, ydata=I, p0=[(max(I) - min(I)) / 2, 1, np.pi / 2, np.mean(I)],
#                       bounds=(-np.inf, np.inf), maxfev=10000)

ram_p = np.round(pars[2], 5)

print('#########################')
print('### Fitted Parameters ###')
print('#########################')
print(f"Ramsey phase = {ram_p:.3f}")
# print('Covariance Matrix')
# print(cov)

plt.figure()
plt.plot(p_list_us, I, ".")
plt.plot(p_list_us, ramsey_fit_phase(p_list_us, *pars))
plt.xlabel('phase')
plt.ylabel("Ramsey Amplitude")
plt.title(f"Ramsey phase = {ram_p:.3f} MHz")
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
plt.grid()
plt.show(block=False)

if save_data:
    file_saver_(np.transpose([p_list_us, I, Q]), file_name=__file__, suffix=qe, master_folder=ExpName,
                header_string="Time (us), MAgnitude, I, Q")
