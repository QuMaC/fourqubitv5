import numpy as np
import time
from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from qualang_tools.results import progress_counter, fetching_tool
import pyvisa as visa
from scipy import signal as sgn
from qualang_tools.plot import interrupt_on_close
from scipy.signal import find_peaks
import statistics as st
import matplotlib
from Helper_Functions.spectro_helper import *
import sys
import pyvisa as visa
import json

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

n_avgs = 1e3  # SNR dependent, this is an upper bound
n_samples = 2000  # no. of samples
anharm = 12  # MHz
update_config = False
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
q_no = 6


def q_spectro(q_no, avgs, f_min, f_max, q_amp, df):
    # global qe, qe12, rr
    qe = f"q{q_no}"
    qe12 = f"q12_{q_no}"
    rr = f"rr{q_no}"
    out = adc_mapping[rr]
    f_LO = q_LO[f"{q_no}"]
    # freqs = np.linspace(f_min, f_max, n_sample)
    # freqs = np.arange(f_min, f_max, n_sample)
    # df = freqs[2] - freqs[1]
    # freqs = np.arange(f_min, f_max, df)

    with program() as qubit_spec:
        n = declare(int)
        I = declare(fixed)
        I_st = declare_stream()
        Q = declare(fixed)
        Q_st = declare_stream()
        f = declare(int)
        n_st = declare_stream()

        with for_(n, 0, n < avgs, n + 1):
            with for_(f, f_min, f < f_max, f + df):
                reset_frame(qe)
                reset_frame(qe12)
                wait(20000, qe)
                play_X180(qe)
                align(qe, qe12)
                update_frequency(qe12, f)
                play("const" * amp(q_amp), qe12, duration=20000)
                align(rr, qe12)
                measure("readout", rr, None,
                        demod.full("integW_cos", I, out),
                        demod.full("integW_minus_sin", Q, out))

                # measure_macro(qe, rr, out, I, Q, pi_12=True)
                save(I, I_st)
                save(Q, Q_st)
            save(n, n_st)

        with stream_processing():
            I_st.buffer(len(freqs)).average().save('I')
            Q_st.buffer(len(freqs)).average().save('Q')
            n_st.save("iteration")

    return qubit_spec, f_LO, freqs


######################################
# Open Communication with the Server #
######################################
f_min, f_max = -1*0.8*(q_IF[str(q_no)] + 150e6)/1e6, 0.8*(q_IF[str(q_no)] - 150e6)/1e6  # in MHz

if f_min > f_max:
    t = f_max
    f_max = f_min
    f_min = t

init_flag = 1
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

with open('../Configuration_Files/System_Parameters/external_bandwidth.json','r') as f:
    ext_bw = json.load(f)
    f.close()
if q_no < 5:
    power_scale = abs(np.round((4.9296223/ext_bw[f'{q_no}']), 5) * 2)

else:
    power_scale = abs(np.round((2.9296223 / ext_bw[f'{q_no}']), 5) * 1)

if q_no > 6:
    power_scale = power_scale * 3

a_min = np.round(0.05 * 1.5, 4)
a_max = np.round(0.4 * 1.5, 4)
amp_range = [a_min*power_scale, min(min(a_max, 0.8)*power_scale, 1.0)]
check_by2_line = 0


while True:
    iq_flag = 0  # 0 is I and 1 is Q
    if init_flag == 1:
        data = []
        for amp1 in amp_range:
            amp1 = np.round(amp1,4)
            if amp1 < 0.2:
                check_by2_line = 0
            else:
                check_by2_line = 1
            # freqs = np.linspace(f_min * u.MHz, f_max * u.MHz, n_samples)
            freqs = np.arange(f_min * u.MHz, f_max * u.MHz, (f_max - f_min) * u.MHz // n_samples)
            qubit_spec, _, _ = q_spectro(q_no=q_no, avgs=n_avgs, f_min=f_min * u.MHz, f_max=f_max * u.MHz,
                                         q_amp=amp1, df=(f_max - f_min) * u.MHz // n_samples)
            qm = qmm.open_qm(config)
            job = qm.execute(qubit_spec)
            res_handles = job.result_handles

            fig, axs = plt.subplots(2, 1, sharex=True)
            results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")
            interrupt_on_close(fig, job)

            while res_handles.is_processing():
                I, Q, iteration = results.fetch_all()

                data1 = {"I": I, "Q": Q}
                for i, ax in enumerate(axs.flat):
                    ax.cla()
                    data_label = list(data1.keys())[i]
                    plot_data = data1[data_label]
                    ax.plot(freqs * 1e-6, plot_data, marker='.', label=data_label)
                    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
                    ax.set(xlabel="Freq (MHz)", ylabel="Quadrature Amplitude")
                    ax.legend()
                    ax.grid()

                plt.pause(1)
                plt.tight_layout()
                fig.suptitle(f"Spectroscopy power = {amp1} Qubit = {q_no}")

                I_n = normalize(I)
                Q_n = normalize(Q)
                snr_i, _ = S2N_1(I_n)
                snr_q, _ = S2N_1(Q_n)

                print(f"SNR_I = {snr_i} and SNR_Q = {snr_q}")

                if amp1 < 0.2:
                    if snr_i > 0.6 or snr_q > 0.6:
                        job.halt()
                else:
                    if snr_i > 1 or snr_q > 1:
                        job.halt()

            data.append([I, Q])

        peak_list = []

        dat_index_arr = []
        for data_i in data:
            dat_index = check_I_or_Q(data_i, alpha1=0.5)
            if dat_index is not None:
                dat_index_arr.append(dat_index)

        dat_index = np.bincount(dat_index_arr).argmax()

        for data_i in data:
            if dat_index is not None:
                flg, fltd, w_size = does_signal_exist1(data_i[dat_index], alpha=0.5)
                normed = np.roll(normalize(fltd[w_size:-w_size + 1]), w_size // 2)
                if check_by2_line == 1:
                    peaks, _ = find_peaks(x=normed, height=0.4, prominence=0.2)
                else:
                    peaks, _ = find_peaks(x=normed, height=0.4, prominence=0.2)
                peak_list.append(freqs[peaks] * 1e-6)
            else:
                peak_list.append([])

        poss_qubits = np.array([])
        p_arr = []
        p_arr_02 = []

        poss_02by2 = np.array([])

        if check_by2_line == 1:
            for fr in peak_list:
                temp_list = fr
                temp_set = []
                temp_02 = []
                flag_less_peaks = 0
                if len(temp_list) <= 2:
                    poss_qubits = np.append(poss_qubits, max(temp_list))
                    temp_set.append(max(temp_list))
                    if len(temp_list) == 2:
                        temp_02.append(min(temp_list))
                    flag_less_peaks = 1
                else:
                    while len(temp_list) > 2:
                        a, b = closest_pair(temp_list, 140)  # 140 = half of anharmonicity
                        print(f'(a,b) = ({a},{b})')
                        if b - a < 150:  # 150 = half of maximum possible anharmonicity
                            temp_set.append(b)
                            temp_02.append(a)
                        rem_id = np.where(temp_list == b)[0][0]
                        temp_list = np.delete(temp_list, rem_id)
                        rem_id = np.where(temp_list == a)[0][0]
                        temp_list = np.delete(temp_list, rem_id)
                    poss_qubits = np.append(poss_qubits, temp_set)
                    poss_02by2 = np.append(poss_02by2, temp_02)
                p_arr.append(temp_set)
                p_arr_02.append(temp_02)

            det_list = []
            det_index = []

            for q in range(len(p_arr[0])):
                det_count = 0
                for i in range(len(p_arr[1:])):
                    val, _ = find_nearest(p_arr[i + 1], p_arr[0][q])
                    if abs(val - p_arr[0][q]) < 5:
                        det_count += 1
                    det_index.append([q, i + 1])
                if check_by2_line == 1:
                    if det_count >= 2:
                        det_list.append(p_arr[0][q])

            det_index1 = np.transpose(np.array(det_index))
            print(det_index1)

            if det_index1.size != 0:
                indices = set(det_index1[0])

            else:
                indices = None

            if indices is not None:
                qubits = np.array(p_arr[det_index[0][0]])[list(indices)]
                # if len(p_arr_02) > 0:
                #     twoby2_lines = np.array(p_arr_02[det_index[0][1]])[list(indices)]
                emp_flg = [1 if len(i) > 0 else 0 for i in p_arr_02]
                if np.sum(emp_flg) > 0:
                    twoby2_lines = np.array(p_arr_02[det_index[0][1]])[list(indices)]
                else:
                    twoby2_lines = False
            else:
                print('No qubits found')
                break
                # return data

        else:
            qubits = peak_list[0]

        if len(qubits) > 1:

            print(f'qubits seen = ({qubits})')
            print('Possibly multiple qubits observed')
            print('Re-running power sweep over lower power')
            raise Warning('For debugging. Terminated')
            temp_a = amp_range[0]
            amp_range = [temp_a / 1.5]
            # f_center = np.mean()
            f_min = np.min(qubits) - 20
            f_max = np.max(qubits) + 20
            check_by2_line = 0
            if temp_a < 0.01:
                print('Looks like some other issue. Basically single individual peak with a corresponding 02/2 '
                      'line not visible')
                print('Returning possible qubits')
                # return qubits
                break
        else:
            print(f'qubits seen = {qubits}')
            if twoby2_lines:
                print(f'Anharmonicity = {2 * (qubits - twoby2_lines)}')
            else:
                print('02/2 not found')
            init_flag = 0
            f_center = qubits[0]
            f_min = f_center - 20
            f_max = f_center + 20
            amp1 = a_min
            check_by2_line = 0
            count_for_debug = 0
            quad = dat_index

    else:
        count_for_debug += 1

        print(f'f_min_start = {f_min}')
        print(f'f_max_start = {f_max}')

        if f_max - f_min < 0.8:
            # return peak_list
            break

        # freqs = np.linspace(f_min * u.MHz, f_max * u.MHz, n_samples // 5)
        freqs = np.arange(f_min * u.MHz, f_max * u.MHz, (f_max - f_min) * u.MHz * 5 // n_samples)

        peak_list_prev = peak_list

        qubit_spec1, _, _ = q_spectro(q_no=q_no, avgs=n_avgs, f_min=f_min * u.MHz, f_max=f_max * u.MHz,
                                      q_amp=amp1, df=(f_max - f_min) * 5 * u.MHz // n_samples)

        qm.close()
        time.sleep(1)
        qm = qmm.open_qm(config)
        job1 = qm.execute(qubit_spec1)
        res_handles = job1.result_handles

        fig, axs = plt.subplots(2, 1, sharex=True)
        res_handles.get("I").wait_for_values(1)

        results = fetching_tool(job1, data_list=["I", "Q", "iteration"], mode="live")
        interrupt_on_close(fig, job1)

        while res_handles.is_processing():
            I, Q, iteration = results.fetch_all()

            data1 = {"I": I, "Q": Q}
            for i, ax in enumerate(axs.flat):
                ax.cla()
                data_label = list(data1.keys())[i]
                plot_data = data1[data_label]
                ax.plot(freqs * 1e-6, plot_data, marker='.', label=data_label)
                ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
                ax.set(xlabel="Freq (MHz)", ylabel="Quadrature Amplitude")
                ax.legend()
                ax.grid()

            I_n = normalize(I)
            Q_n = normalize(Q)
            snr_i, _ = S2N_1(I_n)
            snr_q, _ = S2N_1(Q_n)
            print(f"SNR_I = {snr_i} and SNR_Q = {snr_q}")

            plt.pause(1)
            plt.tight_layout()
            fig.suptitle(f"Spectroscopy power = {amp1} Qubit = {q_no}")

            if quad == 0:
                if snr_i > 2:
                    job1.halt()
            else:
                if snr_q > 2:
                    job1.halt()

        I = job1.result_handles.get("I").fetch_all()
        Q = job1.result_handles.get("Q").fetch_all()
        data = [[I, Q]]
        peak_list = []

        # dat_index_arr = []
        # for data_i in data:
        #     dat_index = check_I_or_Q(data_i, alpha1=0.5)
        #     if dat_index is not None:
        #         dat_index_arr.append(dat_index)
        #
        # dat_index = np.bincount(dat_index_arr).argmax()

        for data_i in data:
            # if dat_index is not None:
            flg, fltd, w_size = does_signal_exist1(data_i[quad], alpha=0.5, win_s=30)
            normed = normalize(fltd[w_size:-w_size + 1])
            peaks, props = find_peaks(x=normed, height=0.5, prominence=0.5)
            peak_list.append(freqs[peaks + w_size // 2] * 1e-6)
            # else:
            #     peak_list.append([])

        if len(peak_list[0]) > 0:
            f_center = freqs[peaks[(props['peak_heights']).argmax()] + w_size // 2]
            print(f'expected qubit at {f_center * 1e-6}')
            # if count_for_debug == 1:
            # raise Warning('Debug term')
        else:
            print('asd')
            amp1 = amp1 * 2
            continue

        # time.sleep(2)
        init_flag = 0

        f_range = (f_max - f_min) / 3
        f_min = f_center * 1e-6 - f_range / 2
        f_max = f_center * 1e-6 + f_range / 2
        amp1 = amp1 / 5 #10

        print(f'f_min = {f_min}')
        print(f'f_max = {f_max}')

        # return peak_list_prev
print(f'qubit IF = {f_center * 1e-6:.6f} MHz')
if twoby2_lines:
    print(f'Anharmonicty = {2 * (f_center * 1e-6 - twoby2_lines)[0]:.3f} MHz')
else:
    print('02/2 not found')
print('Fin')

if update_config:
    dac_key = keyer(f'q{q_no}', dac_mapping)[0]
    rm = visa.ResourceManager()

    q_LO_rns = rm.open_resource(LO_IP_dict['q_LO'][dac_key])
    # rr_LO_rns = rm.open_resource(LO_IP_dict['rr_LO'][dac_key])

    LO_freq = q_LO_rns.query_ascii_values('SOUR:FREQ:CW?')[0] / 1e9
    # rr_LO_freq = rr_LO_rns.query_ascii_values('SOUR:FREQ:CW?')[0] / 1e9


    with open('../Configuration_Files/System_Parameters/q_IF.json', 'r') as f:
        q_IF_dict = json.load(f)
        f.close()

    q_IF_dict[str(q_no)] = f_center / 1e6

    with open('../Configuration_Files/System_Parameters/q_IF.json', 'w') as f:
        json.dump(q_IF_dict, f, indent=6)
        f.close()

    with open('../Configuration_Files/System_Parameters/q_LO.json', 'r') as f:
        LO_dict = json.load(f)
        f.close()

    LO_dict[str(q_no)] = LO_freq

    with open('../Configuration_Files/System_Parameters/q_LO.json', 'w') as f:
        json.dump(LO_dict, f, indent=6)
        f.close()

    # with open('../Configuration_Files/System_Parameters/rr_LO.json', 'r') as f:
    #     rr_LO_dict = json.load(f)
    #     f.close()

    # rr_LO_dict[str(q_no)] = rr_LO_freq
    #
    # with open('../Configuration_Files/System_Parameters/rr_LO.json', 'w') as f:
    #     json.dump(rr_LO_dict, f, indent=6)
    #     f.close()

    with open('../Configuration_Files/System_Parameters/anharmonicities.json', 'r') as f:
        dets = json.load(f)
        f.close()

    dets[str(q_no)] = 2 * (f_center * 1e-6 - twoby2_lines)[0]

    with open('../Configuration_Files/System_Parameters/anharmonicities.json', 'w') as f:
        json.dump(dets, f, indent=6)
        f.close()
