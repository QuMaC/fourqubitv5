from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
from Helper_Functions.macros import *

save_data = False
simulate = False
###################
# The QUA program #
###################

N_shots = 25000
wait_init = 250000
wait_rr = 8


c_no, t_no = 5, 4
qe_c = f"q{c_no}"
rr_c = f"rr{c_no}"
out_c = adc_mapping[rr_c]
qe_t = f"q{t_no}"
rr_t = f"rr{t_no}"
out_t = adc_mapping[rr_t]

AC_flag = False

qe_cr = f"cr_c{c_no}t{t_no}"
qe_ac = f"cr_ac_c{c_no}t{t_no}"

p_cr = cr_phase[qe_cr]
p_ac = cr_phase[qe_ac]

qe_list_local = [qe_c, qe_t, qe_cr, qe_ac]

dem1 = demarcations[str(t_no)]
dem2 = demarcations[str(c_no)]

if simulate:
    wait_init = 100


with program() as Bell_state:

    n = declare(int)
    I1 = declare(fixed)
    I2 = declare(fixed)
    bool1 = declare(bool)
    bool2 = declare(bool)
    Q_dummy = declare(fixed)

    I1_st = declare_stream()
    bool1_st = declare_stream()
    I2_st = declare_stream()
    bool2_st = declare_stream()

    # for elem in cr_elems:
    #     frame_rotation_2pi(cr_phase[elem], elem)

    # frame_rotation_2pi(p_cr, qe_cr)
    # frame_rotation_2pi(p_ac, qe_ac)

    with for_(n, 0, n < N_shots, n + 1):

        # wait(wait_init)
        cooldown(time=wait_init)
        # reset_phase(rr_t)
        # reset_phase(rr_c)
        align(*qe_list_local)
        # play("X180", qe_c)
        # play("X180", qe_t)

        Hadamard(qe_c)
        align(qe_c, qe_cr)
        CNOT_macro(qe_c, qe_t, AC_flag)
        # CNOT_macro(qe_c, qe_t, AC_flag)
        # align()

        # CNOT_macro(qe_c, qe_t)

        measure_macro(qe_t, rr_t, out_t, I1, Q_dummy, pi_12=True)
        measure_macro(qe_c, rr_c, out_c, I2, Q_dummy, pi_12=True)
        assign(bool1, I1 > dem1)
        assign(bool2, I2 > dem2)

        save(I1, I1_st)
        save(I2, I2_st)
        save(bool1, bool1_st)
        save(bool2, bool2_st)

    with stream_processing():

        I1_st.save_all('I1')
        I2_st.save_all('I2')

        bool1_st.save_all('bool1')
        bool2_st.save_all('bool2')


######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

##############
# Simualtion #
##############

if simulate :
    job = qmm.simulate(config, Bell_state, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
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
try:
    qm = qmm.open_qm(config)
    job = qm.execute(Bell_state)
except:
    # print('job aint happening')
    raise Warning('job aint happening')
res_handles = job.result_handles
I1_handle = job.result_handles.get("I1")
I2_handle = job.result_handles.get("I2")
bool1_handle = job.result_handles.get("bool1")
bool2_handle = job.result_handles.get("bool2")

job.result_handles.wait_for_all_values()

I1 = I1_handle.fetch_all()
I2 = I2_handle.fetch_all()
bool1 = bool1_handle.fetch_all()
bool2 = bool2_handle.fetch_all()

stats = []
for i in range(N_shots):

    stats.append([bool1[i], bool2[i]])


def plot_correlations(stats):

    c00, c01, c10, c11 = 0, 0, 0, 0

    for m in stats:

        if not m[0][0] and not m[1][0]:
            c00 += 1
        elif not m[0][0] and m[1][0]:
            c01 +=1
        elif m[0][0] and not m[1][0]:
            c10 += 1
        elif m[0][0] and m[1][0]:
            c11 += 1

    tot_c = c00 + c01 + c10 + c11
    c00, c01, c10, c11 = c00/tot_c, c01/tot_c, c10/tot_c, c11/tot_c

    plt.figure()
    plt.imshow(np.array([[c00, c01], [c10, c11]]))
    plt.xticks([0, 1])
    plt.yticks([0, 1])
    plt.ylabel("Control")
    plt.xlabel("Target")
    plt.text(0, 0, f"{100 * c00:.1f}%", ha="center", va="center", color="k")
    plt.text(1, 0, f"{100 * c01:.1f}%", ha="center", va="center", color="w")
    plt.text(0, 1, f"{100 * c10:.1f}%", ha="center", va="center", color="w")
    plt.text(1, 1, f"{100 * c11:.1f}%", ha="center", va="center", color="k")
    plt.title(f"Quantum Correlations : Total points = {tot_c}")
    plt.show(block=False)


plot_correlations(stats)


