import time
from Configuration_Files.configuration_4qubitsv3 import *
from qm import SimulationConfig
import os
import numpy as np
from qm import QuantumMachinesManager
from Helper_Functions.macros import *
import matplotlib.pyplot as plt
from Helper_Functions.analysis_functions import fit_RB, power_law

###################
# The QUA program #
###################
save_data = True
simulate = False
pi_12 = True


def play_I(qf):
    play('I', qf)


func_dict = {
    "X": play_X180,
    "Y": play_Y180,
    "X/2": play_X90,
    "-X/2": play_mX90,
    "Y/2": play_Y90,
    "-Y/2": play_mY90,
    'I': play_I,
}

op_map = {"I": "I", "X": "X180", "Y": "d_Y180", "X/2": "d_X90", "-X/2": "d_mX90", "Y/2": "Y90", "-Y/2": "mY90"}


def TwoQ_RB_fixed_seq(op_list, cr_elem, cr_ac_elem, qe_c, qe_t, AC_flag=False):
    def play_seq(op_list, cr_elem, cr_ac_elem, qe_c, qe_t, AC_flag=AC_flag):

        for op in op_list:

            if op[0] == "CNOT":
                CNOT_macro(qe_c, qe_t, AC_flag)

            elif op[0] == "SWAP":
                SWAP_macro(qe_c, qe_t, AC_flag)

            elif op[0] == "iSWAP":
                iSWAP_macro(qe_c, qe_t, AC_flag)

            elif op[0] == "ZX/4":
                # align()
                align(cr_elem, qe_c, qe_t)
                if AC_flag:
                    ZXby4_AC(cr_elem, cr_ac_elem, qe_c, a_cr=cr_amp[cr_elem], a_ac=cr_amp[cr_ac_elem],
                             t=cr_len_ns[cr_elem] // 4)
                else:
                    ZXby4(cr_elem, qe_c, a=cr_amp[cr_elem], t=cr_len_ns[cr_elem] // 4)


            elif op[0] == "-ZX/4":
                # align()
                align(cr_elem, qe_c, qe_t)

                if AC_flag:
                    ZXby4_AC(cr_elem, cr_ac_elem, qe_c, a_cr=-cr_amp[cr_elem], a_ac=-cr_amp[cr_ac_elem],
                             t=cr_len_ns[cr_elem] // 4)
                else:
                    ZXby4(cr_elem, qe_c, a=-cr_amp[cr_elem], t=cr_len_ns[cr_elem] // 4)

            else:
                func_dict[op[0]](op[1])
                # play(op_map[op[0]], op[1])
                # if
                wait(4, op[1])

            # align()
            # align(qe_t, cr_elem, qe_c)

    wait_init = 62500
    wait_t = 4
    wait_rr = 16
    n_avg = 3000  # 3000
    if simulate is True:
        wait_init = 100
        n_avg = 3

    p_cr, p_ac = cr_phase[cr_elem], cr_phase[cr_ac_elem]
    with program() as twoQ_RB:
        n = declare(int)
        Qt = declare(fixed)
        It = declare(fixed)
        Qc = declare(fixed)
        Ic = declare(fixed)
        Qt_st = declare_stream()
        It_st = declare_stream()
        Qc_st = declare_stream()
        Ic_st = declare_stream()

        I0c = declare(fixed)
        Q0c = declare(fixed)
        I1c = declare(fixed)
        Q1c = declare(fixed)
        Q0c_st = declare_stream()
        I0c_st = declare_stream()
        Q1c_st = declare_stream()
        I1c_st = declare_stream()

        I0t = declare(fixed)
        Q0t = declare(fixed)
        I1t = declare(fixed)
        Q1t = declare(fixed)
        Q0t_st = declare_stream()
        I0t_st = declare_stream()
        Q1t_st = declare_stream()
        I1t_st = declare_stream()

        # frame_rotation_2pi(p_cr, cr_elem)
        # frame_rotation_2pi(p_ac, cr_ac_elem)

        with for_(n, 0, n < n_avg, n + 1):
            # wait(wait_init, qe_c)
            reset_frame(qe_c, qe_t, cr_elem, cr_ac_elem)
            cooldown(time=wait_init, qe=[qe_c, qe_t, cr_elem, cr_ac_elem, rr_t, rr_c])
            # align()
            measure_macro(qe_c, rr_c, out_c, I0c, Q0c, pi_12=pi_12)
            save(I0c, I0c_st)
            save(Q0c, Q0c_st)

            measure_macro(qe_t, rr_t, out_t, I0t, Q0t, pi_12=pi_12)
            save(I0t, I0t_st)
            save(Q0t, Q0t_st)

            align(qe_c, qe_t, cr_elem, cr_ac_elem, rr_t, rr_c)

            # wait(wait_init, qe_c, qe_t)
            cooldown(time=wait_init, qe=[qe_c, qe_t, cr_elem, cr_ac_elem, rr_t, rr_c])
            play_X180(qe_c)
            play_X180(qe_t)
            # align()
            measure_macro(qe_c, rr_c, out_c, I1c, Q1c, pi_12=pi_12)
            save(I1c, I1c_st)
            save(Q1c, Q1c_st)
            measure_macro(qe_t, rr_t, out_t, I1t, Q1t, pi_12=pi_12)
            save(I1t, I1t_st)
            save(Q1t, Q1t_st)

            align(qe_c, qe_t, cr_elem, cr_ac_elem, rr_t, rr_c)

            # wait(wait_init, qe_t)
            cooldown(time=wait_init, qe=[qe_c, qe_t, cr_elem, cr_ac_elem, rr_t, rr_c])
            play_seq(op_list, cr_elem, cr_ac_elem, qe_c, qe_t)
            align(qe_c, qe_t, cr_elem, cr_ac_elem, rr_t, rr_c)
            measure_macro(qe_t, rr_t, out_t, It, Qt, pi_12=pi_12)
            save(It, It_st)
            save(Qt, Qt_st)

            measure_macro(qe_c, rr_c, out_c, Ic, Qc, pi_12=pi_12)
            save(Ic, Ic_st)
            save(Qc, Qc_st)

        with stream_processing():
            # saves [[I_C0_t0,I_C1_t0],[I_C0_t1,I_C1_t1]]
            It_st.average().save("It_avg")
            Qt_st.average().save("Qt_avg")
            Ic_st.average().save("Ic_avg")
            Qc_st.average().save("Qc_avg")

            I0c_st.average().save("I0c_avg")
            Q0c_st.average().save("Q0c_avg")
            I1c_st.average().save("I1c_avg")
            Q1c_st.average().save("Q1c_avg")

            I0t_st.average().save("I0t_avg")
            Q0t_st.average().save("Q0t_avg")
            I1t_st.average().save("I1t_avg")
            Q1t_st.average().save("Q1t_avg")

    if simulate:
        job = qmm.simulate(config, twoQ_RB, SimulationConfig(int(12000)))
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

    # try:
    # compile_id = qm.compile(twoQ_RB)
    # pending_job = qm.queue.add_compiled(compile_id)
    # raise Warning('test block')
    # job = pending_job.wait_for_execution()
    job = qm.execute(twoQ_RB)
    # job.result_handles.wait_for_all_values()
    while job._is_job_running():
        time.sleep(1)
    It_f = job.result_handles.get("It_avg")
    Qt_f = job.result_handles.get("Qt_avg")
    Ic_f = job.result_handles.get("Ic_avg")
    Qc_f = job.result_handles.get("Qc_avg")

    I0c_f = job.result_handles.get("I0c_avg")
    I1c_f = job.result_handles.get("I1c_avg")
    I0t_f = job.result_handles.get("I0t_avg")
    I1t_f = job.result_handles.get("I1t_avg")
    time.sleep(0.5)
    It = It_f.fetch_all()
    Qt = Qt_f.fetch_all()
    Ic = Ic_f.fetch_all()
    Qc = Qc_f.fetch_all()

    I0c = I0c_f.fetch_all()
    I1c = I1c_f.fetch_all()
    I0t = I0t_f.fetch_all()
    I1t = I1t_f.fetch_all()

    return It, Qt, Ic, Qc, I0c, I1c, I0t, I1t


def op_list_from_seq(seq):
    gate_list = seq.split("_")

    op_list = []
    for gate_info in gate_list:

        q_i = gate_info[0]
        gate = gate_info[1:]
        if q_i == "1":
            q_i = str(c_no)

        elif q_i == "2":
            q_i = str(t_no)

        op_list.append([gate, f"q{q_i}"])

    return op_list


def normalize(Qc, Q1c, Q0c):
    Qc = (Qc - Q0c) / (Q1c - Q0c)
    Qc = 1 - 2 * Qc

    return Qc


#############
# execution #
#############
c_no, t_no = 5, 2

qe_c = f"q{c_no}"
rr_c = f"rr{c_no}"
out_c = adc_mapping[rr_c]
qe_t = f"q{t_no}"
rr_t = f"rr{t_no}"
out_t = adc_mapping[rr_t]
cr_elem = f"cr_c{c_no}t{t_no}"
cr_ac_elem = f"cr_ac_c{c_no}t{t_no}"
qe_list = [qe_c, qe_t, cr_elem, cr_ac_elem]
AC_flag = True

qe = qe_t

prob_list = []
prob_gate_seq = []

prob_list_in = []
prob_gate_seq_in = []

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
qmm.close_all_qms()
qm = qmm.open_qm(config)

test_gate = 'CNOT'

if test_gate == 'ZX':
    with open(f"../Configuration_Files/Resources/2Q_RB_Sequences/ZX_sequences/Standard.txt", 'r') as file:
        seq_list = file.readlines()

    with open(f"../Configuration_Files/Resources/2Q_RB_Sequences/ZX_sequences/Interleaved.txt", 'r') as file:
        in_seq_list = file.readlines()
else:
    with open(f"../Configuration_Files/Resources/2Q_RB_Sequences/CNOT_seq/Standard.txt", 'r') as file:
        seq_list = file.readlines()

    with open(f"../Configuration_Files/Resources/2Q_RB_Sequences/CNOT_seq/Interleaved.txt", 'r') as file:
        in_seq_list = file.readlines()

exp_seq, exp_in_seq = [], []
for seq, in_seq in zip(seq_list, in_seq_list):

    seq = seq.replace("\n", "")
    seq = seq.replace("1SWAP_", "1SWAP_1I_2I")
    cliff_seq = seq.split("\\")
    n_cliff = len(cliff_seq)

    if n_cliff > 15:
        continue

    in_seq = in_seq.replace("\n", "")
    in_seq = in_seq.replace("1SWAP_", "1SWAP_1I_2I")
    cliff_in_seq = in_seq.split("\\")

    exp_seq.append([n_cliff, cliff_seq])
    exp_in_seq.append([n_cliff, cliff_in_seq])

x_data, y1_data, y2_data = [], [], []
y1_in_data, y2_in_data = [], []
gc_val, ec_val, gt_val, et_val = [], [], [], []
nseq, nseq_count = 10, 0
for exp, exp_in in zip(exp_seq, exp_in_seq):

    if exp[0] == 2: nseq_count += 1
    if nseq_count > nseq: break

    x_data.append(exp[0])
    gate_seq = "_".join(exp[1])
    op_list = op_list_from_seq(gate_seq)
    try:
        It, Qt, Ic, Qc, I0c, I1c, I0t, I1t = TwoQ_RB_fixed_seq(op_list, cr_elem, cr_ac_elem, qe_c, qe_t, AC_flag)

        y1_data.append([It, Qt])
        y2_data.append([Ic, Qc])
        gc_val.append(I0c)
        ec_val.append(I1c)
        gt_val.append(I0t)
        et_val.append(I1t)
    except Exception as e:
        print(f"Exception at iteration {i}: {type(e).__name__}: {e}")

        import traceback

        traceback.print_exc()

        prob_list.append(exp[0])
        prob_gate_seq.append(exp[1])

    # Qc_n = normalize(Qc, Q1c, Q0c)
    # It_n = normalize(It, I1t, I0t)

    gate_seq = "_".join(exp_in[1])
    op_list = op_list_from_seq(gate_seq)
    # It, Qt, Ic, Qc, I0c, I1c, I0t, I1t = TwoQ_RB_fixed_seq(op_list, cr_elem, cr_ac_elem, qe_c, qe_t, AC_flag)
    try:
        It, Qt, Ic, Qc, I0c, I1c, I0t, I1t = TwoQ_RB_fixed_seq(op_list, cr_elem, cr_ac_elem, qe_c, qe_t, AC_flag)

        y1_in_data.append([It, Qt])
        y2_in_data.append([Ic, Qc])
        gc_val.append(I0c)
        ec_val.append(I1c)
        gt_val.append(I0t)
        et_val.append(I1t)
    except Exception as e:
        print(f"Exception at iteration {i}: {type(e).__name__}: {e}")

        import traceback

        traceback.print_exc()

        prob_list_in.append(exp[0])
        prob_gate_seq_in.append(exp[1])
    # Qc_n = normalize(Qc, Q1c, Q0c)
    # It_n = normalize(It, I1t, I0t)

gc_v, ec_v = sum(gc_val) / len(gc_val), sum(ec_val) / len(ec_val)
gt_v, et_v = sum(gt_val) / len(gt_val), sum(et_val) / len(et_val)

for i, x in enumerate(x_data):
    if i == 0: continue
    if x == x_data[0]:
        if x_data[i - 1] != x_data[0]:
            step = (x_data[i - 1] - x_data[0]) / (i - 1)
        n_el = i
        n_seq = int(len(x_data) / i)
        break

n_el = n_el - len(prob_list)
n_el_in = n_el - len(prob_list_in)

x_data = [i for i in x_data if i not in prob_list]
x_data_in = [i for i in x_data if i not in prob_list_in]

x_reshaped = np.array(x_data).reshape((n_seq, n_el))
x_reshaped_in = np.array(x_data_in).reshape((n_seq, n_el_in))

y1i = np.array([y1_data[i][0] for i in range(n_seq * n_el)])
y2i = np.array([y2_data[i][0] for i in range(n_seq * n_el)])
y1ini = np.array([y1_in_data[i][0] for i in range(n_seq * n_el_in)])
y2ini = np.array([y2_in_data[i][0] for i in range(n_seq * n_el_in)])

y1i_reshaped = y1i.reshape((n_seq, n_el))
y2i_reshaped = y2i.reshape((n_seq, n_el))
y1ini_reshaped = y1ini.reshape((n_seq, n_el_in))
y2ini_reshaped = y2ini.reshape((n_seq, n_el_in))

sort_i = np.argsort(x_data)
x_data_sorted = sorted(x_data)

sort_i_in = np.argsort(x_data_in)
x_data_sorted_in = sorted(x_data_in)

y1i = [y1_data[i][0] for i in sort_i]
y2i = [y2_data[i][0] for i in sort_i]
y1ini = [y1_in_data[i][0] for i in sort_i_in]
y2ini = [y2_in_data[i][0] for i in sort_i_in]

x_fit = x_reshaped[0]
x_fit = np.insert(x_fit, 0, 0)

x_fit_in = x_reshaped_in[0]
x_fit_in = np.insert(x_fit_in, 0, 0)

y2i_fit = np.average(y2i_reshaped, axis=0)
y2ini_fit = np.average(y2ini_reshaped, axis=0)
y2i_fit = np.insert(y2i_fit, 0, gc_v)
y2ini_fit = np.insert(y2ini_fit, 0, gc_v)
# y2q_fit = np.insert(y2q_fit,0,1)
# y2inq_fit=np.insert(y2inq_fit,0,1)

y1i_fit = np.average(y1i_reshaped, axis=0)
y1ini_fit = np.average(y1ini_reshaped, axis=0)
y1i_fit = np.insert(y1i_fit, 0, gt_v)
y1ini_fit = np.insert(y1ini_fit, 0, gt_v)
# y1i_fit = np.insert(y1i_fit,0,1)
# y1ini_fit=np.insert(y1ini_fit,0,1)

print("========================Readout : Target Qubit====================================================")
print("=====================STANDARD======================================================================")
pars1 = fit_RB(x_fit, y1i_fit, nqubits=2, ivals=[0.5, 0, 0.9])
print("=====================INTERLEAVED===================================================================")
pars1_in = fit_RB(x_fit_in, y1ini_fit, nqubits=2, ivals=[0.5, 0, 0.9])

print("========================Readout : Control Qubit====================================================")
print("=====================STANDARD======================================================================")
pars2 = fit_RB(x_fit, y2i_fit, nqubits=2, ivals=[-0.5, 0, 0.8])
print("=====================INTERLEAVED===================================================================")
pars2_in = fit_RB(x_fit_in, y2ini_fit, nqubits=2, ivals=[-0.5, 0, 0.8])

p_st_1, p_in_1 = pars1[-1], pars1_in[-1]
p_st_2, p_in_2 = pars2[-1], pars2_in[-1]

ZX_fid1 = np.round((1 - (2 ** 2 - 1) / 2 ** 2 * (1 - p_in_1 / p_st_1)) * 1e2, 2)
ZX_fid2 = np.round((1 - (2 ** 2 - 1) / 2 ** 2 * (1 - p_in_2 / p_st_2)) * 1e2, 2)

ZX_fid2_err = (2 ** 2 - 1) / 2 ** 2 * (abs(p_st_2 - p_in_2 / p_st_2) + 1 - p_st_2)
ZX_fid2_err = np.round((1 - ZX_fid2_err) * 1e2, 3)
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

plt.figure()
plt.plot(x_data_sorted, y1i, ".r", label="Standard")
plt.plot(x_fit, power_law(x_fit, *pars1), '-r')
plt.plot(x_data_sorted_in, y1ini, ".b", label="Interleaved")
plt.plot(x_fit_in, power_law(x_fit_in, *pars1_in), '-b')
plt.title(f"2Q RB: Readout Target  F({test_gate}) = {ZX_fid1}%")
plt.ylabel("Voltage (a.u.)")
plt.xlabel("No. of Cliffords")
plt.axhline(gt_v, linestyle='--', color="green")
plt.axhline(et_v, linestyle='--', color="orange")
# plt.axhline(1, linestyle='--', color="green")
# plt.axhline(-1, linestyle='--', color="orange")
# plt.ylim(-1.2, 1.2)
plt.legend()
plt.grid()
plt.show(block=False)
print(f"gt_v = {gt_v}, et_v = {et_v}")

plt.figure()
plt.plot(x_data_sorted, y2i, ".r", label="Standard")
plt.plot(x_fit, power_law(x_fit, *pars2), '-r')
plt.plot(x_data_sorted_in, y2ini, ".b", label="Interleaved")
plt.plot(x_fit_in, power_law(x_fit_in, *pars2_in), '-b')
plt.title(f"2Q RB: Readout Control  F({test_gate}) = {ZX_fid2}%")
plt.ylabel("Voltage (a.u.)")
plt.xlabel("No. of Cliffords")
plt.axhline(gc_v, linestyle='--', color="green")
plt.axhline(ec_v, linestyle='--', color="orange")
# plt.axhline(1, linestyle='--', color="green")
# plt.axhline(-1, linestyle='--', color="orange")
plt.legend()
plt.grid()
plt.show(block=False)
print(f"gc_v = {gc_v}, ec_v = {ec_v}")

if save_data is True:
    file_saver_qubit_(np.transpose([x_data_sorted, y1i]), file_name=__file__, master_folder=ExpName,
                      suffix=f"Standard_C_Control{c_no}_Target{t_no}", delimiter="\t")
    file_saver_qubit_(np.transpose([x_data_sorted_in, y1ini]), file_name=__file__, master_folder=ExpName,
                      suffix=f"Interleaved_C_Control{c_no}_Target{t_no}", delimiter="\t")
    file_saver_qubit_(np.transpose([x_fit, power_law(x_fit, *pars1)]), file_name=__file__, master_folder=ExpName,
                      suffix=f"Standard_Fit_C_Control{c_no}_Target{t_no}", delimiter="\t")
    file_saver_qubit_(np.transpose([x_fit_in, power_law(x_fit_in, *pars1_in)]), file_name=__file__,
                      master_folder=ExpName,
                      suffix=f"Interleaved_Fit_C_Control{c_no}_Target{t_no}", delimiter="\t")

    file_saver_qubit_(np.transpose([x_data_sorted, y2i]), file_name=__file__, master_folder=ExpName,
                      suffix=f"Standard_T_Control{c_no}_Target{t_no}", delimiter="\t")
    file_saver_qubit_(np.transpose([x_data_sorted_in, y2ini]), file_name=__file__, master_folder=ExpName,
                      suffix=f"Interleaved_T_Control{c_no}_Target{t_no}", delimiter="\t")
    file_saver_qubit_(np.transpose([x_fit, power_law(x_fit, *pars2)]), file_name=__file__, master_folder=ExpName,
                      suffix=f"Standard_Fit_T_Control{c_no}_Target{t_no}", delimiter="\t")
    file_saver_qubit_(np.transpose([x_fit_in, power_law(x_fit_in, *pars2_in)]), file_name=__file__,
                      master_folder=ExpName,
                      suffix=f"Interleaved_Fit_T_Control{c_no}_Target{t_no}", delimiter="\t")
