import copy
import os
import sys
import threading
import numpy as np
import json
import subprocess
from matplotlib import pyplot as plt
from Configuration_Files.configuration_4qubitsv3 import *
from datetime import datetime
import csv

matplotlib.use('Qt5Agg')
from Helper_Functions.analysis_functions import *
from Helper_Functions.helper_functionsv2 import bulk_switch
from inputimeout import inputimeout, TimeoutOccurred
import subprocess

q_no = 5
do_mixer_calib = 1
qe = f'q{q_no}'


def get_input(input_list):
    """Thread target function to get user input."""
    user_input = input("Enter something: ")
    input_list.append(user_input)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


def coh_fit(t, A, d, c):
    return A * np.exp(-t / d) + c


####    Experiment starts

## Switch config for spectrum analyser
# qe_sw = f'q1'
qe_sw = qe
bulk_switch(qe=keyer(qe, dac_mapping), ip=sw_ip, switches=switches)

init_path = "./Scripts/"

tof = 'Calibration_TimeOfFlight_userin_auto_check'

try:
    subprocess.run(f'python {init_path + tof}.py {q_no}', check=True)
    # print('Disabling loopback. Some bug')
except:
    print('Exception occurred. Check')
    sys.exit()

conn_flag = 0

if os.path.exists('./loopback_tof.json'):
    with open('./loopback_tof.json', 'r') as f:
        flg = json.load(f)
        if flg[str(q_no)]['loopback']:
            conn_flag = 1
        else:
            conn_flag = 0
else:
    conn_flag = 0

if conn_flag:
    user_input = 1
    pass
else:
    print('Autoloopback shows failure. Proceed?')
    input_list = []
    input_thread = threading.Thread(target=get_input, args=(input_list,))
    input_thread.start()
    input_thread.join(timeout=10)
    if input_thread.is_alive():
        print('Next time, please decide in 10 seconds. For now....')
        user_input = 1
    else:
        user_input = input_list[0]

# time.sleep(10)

if user_input != '0':
    print('....Proceeding as if there are no issues')
else:
    print('Ok. Stopping')
    sys.exit()

init_path = "D:/Experiments/"

exp_rabi = 'TimeDomain_Rabi_user_in'

script_folder_path = './Scripts/'

now = datetime.now()
current_date = now.strftime("%y-%m-%d")

fin_path = init_path + ExpName + '/' + exp_rabi + '/' + current_date + f'_q{q_no}' + '/'

try:
    subprocess.run(f'python {script_folder_path + exp_rabi}.py {q_no}', check=True)
except:
    print('Exception occurred. Check')
    sys.exit()

###     Add plots

rabi_file = os.listdir(fin_path)[-1]

rabi_data = []

with open(fin_path + rabi_file) as rabi:
    file = csv.reader(rabi)
    for row in file:
        rabi_data.append(row)

rabi_data = np.transpose(rabi_data[1:])

time = np.array(rabi_data[0], dtype=float)
I = np.array(rabi_data[1], dtype=float)
Q = np.array(rabi_data[2], dtype=float)

with open('./Rabi_data_auto.json', 'r') as f:
    fit_data = json.load(f)
    f.close()

I_fit = [rabi_fit(i, fit_data['fit_data_I']['amp'], fit_data['fit_data_I']['freq'], 1e6,
                  fit_data['fit_data_I']['phase'] + np.pi / 2, fit_data['fit_data_I']['offset']) for i in time]

Q_fit = [rabi_fit(i, fit_data['fit_data_Q']['amp'], fit_data['fit_data_Q']['freq'], 1e6,
                  fit_data['fit_data_Q']['phase'] + np.pi / 2, fit_data['fit_data_Q']['offset']) for i in time]

plt.ion()
fig, axs = plt.subplots(2, 1, sharex=True)

data = {"I": [I, fit_data['fit_data_I']], "Q": [Q, fit_data['fit_data_Q']]}

for i, ax in enumerate(axs.flat):
    ax.cla()
    data_label = list(data.keys())[i]
    plot_data = data[data_label]
    ax.plot(time, plot_data[0], marker='.', label=data_label)
    if data_label == 'I':
        ax.plot(time, I_fit, label=data_label + "_Fit")
    else:
        ax.plot(time, Q_fit, label=data_label + "_Fit")
    ax.set(xlabel="Time (ns)", ylabel="Rabi Amplitude")
    ax.legend()
    ax.grid()
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

plt.show(block=False)
plt.pause(2)

# fig.canvas.draw()  # Draw the updates
# plt.gcf().canvas.flush_events()  # Flush the GUI events

############    Mixer calibs

if do_mixer_calib == 1:

    offset = 'Calibration_Mixer_Offset_SA_user_in'
    sideband = 'Calibration_Mixer_Sideband_SA_user_in'

    try:
        subprocess.run(f'python {script_folder_path + offset}.py q{q_no}', check=True)
    except:
        print('Exception occurred. Check')
        sys.exit()

    try:
        subprocess.run(f'python {script_folder_path + offset}.py rr{q_no}', check=True)
    except:
        print('Exception occurred. Check')
        sys.exit()

    try:
        subprocess.run(f'python {script_folder_path + sideband}.py q{q_no}', check=True)
    except:
        print('Exception occurred. Check')
        sys.exit()

    try:
        subprocess.run(f'python {script_folder_path + sideband}.py rr{q_no}', check=True)
    except:
        print('Exception occurred. Check')
        sys.exit()

    with open('./offset_sideband_values.json', 'r') as f:
        vals = json.load(f)
        f.close()

    rel_keys = [f'q{q_no}', f'rr{q_no}']

    for key in rel_keys:
        print(f"LO leakage of {key} is {vals[key]['offset']}")
        print(f"Reject Band power of {key} is {vals[key]['sideband']}")

### IQ angle adjustor

try:
    subprocess.run(f'python ./Scripts/Calibration_IQ-blobs_auto.py {q_no}', check=True)
except:
    print('Exception occurred. Check')
    sys.exit()

### End IQ angle adjustor


### Power Rabi initial
Power_rabi_file = 'PulseCalib_Power-Rabi_user_qubit'

try:
    subprocess.run(f'python {script_folder_path + Power_rabi_file}.py {q_no}', check=True)
except:
    print('Exception occurred. Check')
    sys.exit()

fin_path = init_path + ExpName + '/' + Power_rabi_file + '/' + current_date + f'_q{q_no}' + '/'

if not os.path.exists(fin_path):
    print('data folder doesnt exist')
    os.makedirs(fin_path)
    exit()

files = os.listdir(fin_path)

# piby2_files = []
# pi_files = []
#
# for file in files:
#     if '90' in file:
#         piby2_files.append(file)
#     else:
#         pi_files.append(file)
#
# piby2_file = piby2_files[-1]
# pi_file = pi_files[-1]
#
# pi_data = []
#
# with open(fin_path + pi_file, 'r') as f:
#     file = csv.reader(f)
#     for row in file:
#         pi_data.append(row)
#     f.close()
#
# pi_data = np.transpose(pi_data[1:])
#
# amp = np.array(pi_data[0], dtype=float)
# p_I = np.array(pi_data[1], dtype=float)

with open('./power_rabi_fit.json', 'r') as f:
    power_fit_data = json.load(f)
    f.close()

z_peaks = []

for keys, vals in power_fit_data.items():

    data = []

    data_files = [file for file in files if keys in file]
    data_file = data_files[-1]

    with open(fin_path + data_file, 'r') as f:
        file = csv.reader(f)
        for row in file:
            data.append(row)
        f.close()

    data = np.transpose(data[1:])

    amp = np.array(data[0], dtype=float)
    p_I = np.array(data[1], dtype=float)

    p_fit_pi = []
    for i in vals.keys():
        if i != 'gate_amp':
            p_fit_pi.append(vals[i])

    I_fit = para_fit(amp, *p_fit_pi)

    z_peaks.append(max(I_fit))

    pi_amp = vals['gate_amp']
    plt.figure()
    plt.plot(amp, p_I)
    plt.plot(amp, I_fit)
    plt.xlabel("Drive Amplitude")
    plt.ylabel("Rabi Amplitude")
    plt.title(f"Power Rabi : {keys} amp = {pi_amp}")
    plt.axvline(pi_amp)
    plt.legend()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.grid()
    plt.show(block=False)
    plt.pause(1)

peaks_mean = np.mean(z_peaks)
#
# for p in z_peaks:
#     if abs(p/peaks_mean) < 0.5 or abs(p/peaks_mean) > 1.5:
#         raise Warning('Qubit Frequency incorrect')
#

#
# p_fit_pi = []
# for i in power_fit_data['Pi'].keys():
#     if i != 'gate_amp':
#         p_fit_pi.append(power_fit_data['Pi'][i])
#
#
#
# I_fit = para_fit(amp, *p_fit_pi)
#
# pi_amp = power_fit_data['Pi']['gate_amp']
# plt.figure()
# plt.plot(amp, p_I)
# plt.plot(amp, I_fit)
# plt.xlabel("Drive Amplitude")
# plt.ylabel("Rabi Amplitude")
# plt.title(f"Power Rabi : Pi amp = {pi_amp}")
# plt.axvline(pi_amp)
# plt.legend()
# plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
# plt.grid()
# plt.show(block=False)
# plt.pause(1)
#
# piby2_data = []
#
# with open(fin_path + piby2_file, 'r') as f:
#     file = csv.reader(f)
#     for row in file:
#         piby2_data.append(row)
#     f.close()
#
# piby2_data = np.transpose(piby2_data[1:])
#
# amp = np.array(piby2_data[0], dtype=float)
# p_I = np.array(piby2_data[1], dtype=float)
#
# # with open('./power_rabi_fit.json', 'r') as f:
# #     power_fit_data = json.load(f)
# #     f.close()
#
# p_fit_piby2 = []
# for i in power_fit_data['Piby2'].keys():
#     if i != 'gate_amp':
#         p_fit_piby2.append(power_fit_data['Piby2'][i])
#
#
# I_fit = para_fit(amp, *p_fit_piby2)
#
# pi_amp = power_fit_data['Piby2']['gate_amp']
#
# plt.figure()
# plt.plot(amp, p_I)
# plt.plot(amp, I_fit)
# plt.xlabel("Drive Amplitude")
# plt.ylabel("Rabi Amplitude")
# plt.title(f"Power Rabi : Piby2 amp = {pi_amp}")
# plt.axvline(pi_amp)
# plt.legend()
# plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
# plt.grid()
# plt.show(block=False)
# plt.pause(1)

### Ramsey

exp_ramsey = 'TimeDomain_Ramsey_user_in_det_rem_time_limit'

fin_path = init_path + ExpName + '/' + exp_ramsey + '/' + current_date + f'_q{q_no}' + '/'

if not os.path.exists(fin_path):
    os.makedirs(fin_path)

try:
    subprocess.run(f'python {script_folder_path + exp_ramsey}.py {q_no} 1', check=True)
except:
    print('Exception occurred. Check')
    sys.exit()

####### Plotting

ramsey_file = os.listdir(fin_path)[-1]

ramsey_data = []

with open(fin_path + ramsey_file) as ramsey:
    file = csv.reader(ramsey)
    for row in file:
        ramsey_data.append(row)

ramsey_data = np.transpose(ramsey_data[1:])

time = np.array(ramsey_data[0], dtype=float)
I = np.array(ramsey_data[1], dtype=float)

with open('./ramsey_fits.json', 'r') as f:
    ramsey_fit_data = json.load(f)
    f.close()

I_fit = [ramsey_fit(i, ramsey_fit_data['amp'], ramsey_fit_data['tau'], ramsey_fit_data['offset'],
                    ramsey_fit_data['freq'], ramsey_fit_data['phase'], ) for i in time]

plt.figure()
plt.plot(time, I, ".")
plt.plot(time, I_fit)
plt.xlabel('t (ns)')
plt.ylabel("Ramsey Amplitude")
plt.title(
    f"Ramsey : Ramsey time = {ramsey_fit_data['tau']:.2f} us; Ramsey frequency = {ramsey_fit_data['freq']:.2f} MHz")
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
plt.grid()
plt.show(block=False)
plt.pause(1)

with open('ramsey_redo.json', 'r') as f:
    redo = json.load(f)
    f.close()
    if redo['redo'] == 1:
        print('Repeating Ramsey')
        try:
            subprocess.run(f'python {script_folder_path + exp_ramsey}.py {q_no} 1', check=True)
        except:
            print('Exception occurred. Check')
            sys.exit()

with open('ramsey_cache_json.json', 'r') as f:
    det_measured = json.load(f)
    f.close()

print(f'Observed De-tuning: {det_measured["det"]}')

detuned = 0

if np.abs((det_measured['det'] - 1) / 1) > 0.04:
    detuned = 1
    print('Estimating IF detuning')
    if_values_1 = [det_measured['det'] - 1, det_measured['det'] + 1]
    det_n = det_measured['det'] + 0.1
    try:
        subprocess.run(f'python {script_folder_path + exp_ramsey}.py {q_no} {det_n}', check=True)
    except:
        print('Exception occurred. Check')
        sys.exit()
    with open('ramsey_redo.json', 'r') as f:
        redo = json.load(f)
        f.close()
        if redo['redo'] == 1:
            print('Repeating Ramsey')
            try:
                subprocess.run(f'python {script_folder_path + exp_ramsey}.py {q_no} {det_n}', check=True)
            except:
                print('Exception occurred. Check')
                sys.exit()

    with open('ramsey_cache_json.json', 'r') as f:
        det_measured = json.load(f)
        f.close()

    if_values_2 = [det_measured['det'] - det_n, det_measured['det'] + det_n]

    if_val1 = copy.deepcopy(if_values_1)
    if_val2 = copy.deepcopy(if_values_2)

    for i in range(len(if_values_1)):
        if abs(if_values_1[i]) < 0.01:
            if_values_1[i] = 0.01 * np.sign(if_val1[i])

    for i in range(len(if_values_2)):
        if abs(if_values_2[i]) < 0.01:
            if_values_2[i] = 0.01 * np.sign(if_val2[i])

    comp = [abs(i - j) for i, j in zip(if_val1, if_val2)]

    id = np.argmin(comp)

    if_shift = -1 * if_val1[id]

    print(f'IF_shift = {if_shift}')

    with open('../Configuration_Files/System_Parameters/q_IF.json', 'r+') as f:
        q_if = json.load(f)
        p_if = q_if[str(q_no)]
        f.close()
    with open('../Configuration_Files/System_Parameters/q_IF.json', 'w') as f:
        q_if.update({str(q_no): p_if + if_shift})
        json.dump(q_if, f, indent=6)
        f.close()

else:
    detuned = 0

###     Repeat Power Rabi

if detuned:

    Power_rabi_file = './PulseCalib_Power-Rabi_user_qubit'

    try:
        subprocess.run(f'python {script_folder_path + Power_rabi_file}.py {q_no}', check=True)
    except:
        print('Exception occurred. Check')
        sys.exit()

    fin_path = init_path + ExpName + '/' + Power_rabi_file + '/' + current_date + f'_q{q_no}' + '/'

    if not os.path.exists(fin_path):
        os.makedirs(fin_path)

    files = os.listdir(fin_path)

    # piby2_files = []
    # pi_files = []
    #
    # for file in files:
    #     if '90' in file:
    #         piby2_files.append(file)
    #     else:
    #         pi_files.append(file)
    #
    # piby2_file = piby2_files[-1]
    # pi_file = pi_files[-1]
    #
    # pi_data = []
    #
    # with open(fin_path + pi_file, 'r') as f:
    #     file = csv.reader(f)
    #     for row in file:
    #         pi_data.append(row)
    #     f.close()
    #
    # pi_data = np.transpose(pi_data[1:])
    #
    # amp = np.array(pi_data[0], dtype=float)
    # p_I = np.array(pi_data[1], dtype=float)

    with open('./power_rabi_fit.json', 'r') as f:
        power_fit_data = json.load(f)
        f.close()

    for keys, vals in power_fit_data.items():

        data = []

        data_files = [file for file in files if keys in file]
        data_file = data_files[-1]

        with open(fin_path + data_file, 'r') as f:
            file = csv.reader(f)
            for row in file:
                data.append(row)
            f.close()

        data = np.transpose(data[1:])

        amp = np.array(data[0], dtype=float)
        p_I = np.array(data[1], dtype=float)

        p_fit_pi = []
        for i in vals.keys():
            if i != 'gate_amp':
                p_fit_pi.append(vals[i])

        I_fit = para_fit(amp, *p_fit_pi)

        pi_amp = vals['gate_amp']
        plt.figure()
        plt.plot(amp, p_I)
        plt.plot(amp, I_fit)
        plt.xlabel("Drive Amplitude")
        plt.ylabel("Rabi Amplitude")
        plt.title(f"Power Rabi : {keys} amp = {pi_amp}")
        plt.axvline(pi_amp)
        plt.legend()
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        plt.grid()
        plt.show(block=False)
        plt.pause(1)

    # p_fit_pi = []
    # for i in power_fit_data['Pi'].keys():
    #     if i != 'gate_amp':
    #         p_fit_pi.append(power_fit_data['Pi'][i])
    #
    # I_fit = para_fit(amp, *p_fit_pi)
    #
    # pi_amp = power_fit_data['Pi']['gate_amp']
    #
    # plt.figure()
    # plt.plot(amp, p_I)
    # plt.plot(amp, I_fit)
    # plt.xlabel("Drive Amplitude")
    # plt.ylabel("Rabi Amplitude")
    # plt.title(f"Power Rabi : Pi amp = {pi_amp}")
    # plt.axvline(pi_amp)
    # plt.legend()
    # plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    # plt.grid()
    # plt.show(block=False)
    # plt.pause(1)
    #
    # piby2_data = []
    #
    # with open(fin_path + piby2_file, 'r') as f:
    #     file = csv.reader(f)
    #     for row in file:
    #         piby2_data.append(row)
    #     f.close()
    #
    # piby2_data = np.transpose(piby2_data[1:])
    #
    # amp = np.array(piby2_data[0], dtype=float)
    # p_I = np.array(piby2_data[1], dtype=float)
    #
    # with open('./power_rabi_fit.json', 'r') as f:
    #     power_fit_data = json.load(f)
    #     f.close()
    #
    # p_fit_piby2 = []
    # for i in power_fit_data['Piby2'].keys():
    #     if i != 'gate_amp':
    #         p_fit_piby2.append(power_fit_data['Piby2'][i])
    #
    # I_fit = para_fit(amp, *p_fit_piby2)
    #
    # pi_amp = power_fit_data['Piby2']['gate_amp']
    #
    # plt.figure()
    # plt.plot(amp, p_I)
    # plt.plot(amp, I_fit)
    # plt.xlabel("Drive Amplitude")
    # plt.ylabel("Rabi Amplitude")
    # plt.title(f"Power Rabi : Piby2 amp = {pi_amp}")
    # plt.axvline(pi_amp)
    # plt.legend()
    # plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    # plt.grid()
    # plt.show(block=False)
    # plt.pause(1)

### Full Coherence
print('Full Coherence')
exp_coh = 'TimeDomain_Interleaved-Coherence-Individual_user_qubit'

try:
    subprocess.run(f'python {script_folder_path + exp_coh}.py {q_no}', check=True)
except:
    print('Exception occurred. Check')
    sys.exit()

with open('./coherence_redo.json', 'r') as f:
    redo_coh = json.load(f)
    redo_coherence = redo_coh['redo']
    f.close()

if redo_coherence == 1:
    print('Max time not sufficient. Redoing Coherence')
    try:
        subprocess.run(f'python {script_folder_path + exp_coh}.py {q_no}', check=True)
    except:
        print('Exception occurred. Check')
        sys.exit()

now = datetime.now()
current_date = now.strftime("%y-%m-%d")

fin_path = init_path + ExpName + '/' + exp_coh + '/' + current_date + f'_q{q_no}' + '/'

if not os.path.exists(fin_path):
    os.makedirs(fin_path)

files = os.listdir(fin_path)

T1_files = []
Ramsey_files = []
Echo_files = []
coh_val_file = []

for file in files:
    if 'Echo' in file:
        Echo_files.append(file)
    elif 'T1' in file:
        T1_files.append(file)
    elif 'Ramsey' in file:
        Ramsey_files.append(file)
    else:
        coh_val_file.append(file)

echo_data_file = Echo_files[-1]
T1_data_file = T1_files[-1]
Ramsey_data_file = Ramsey_files[-1]

echo_data = []
T1_data = []
Ramsey_data = []

with open(fin_path + echo_data_file, 'r') as f:
    file = csv.reader(f)
    for row in file:
        echo_data.append(row)
    f.close()

with open(fin_path + T1_data_file, 'r') as f:
    file = csv.reader(f)
    for row in file:
        T1_data.append(row)
    f.close()

with open(fin_path + Ramsey_data_file, 'r') as f:
    file = csv.reader(f)
    for row in file:
        Ramsey_data.append(row)
    f.close()

echo_data = np.transpose(echo_data[1:])
T1_data = np.transpose(T1_data[1:])
Ramsey_data = np.transpose(Ramsey_data[1:])

time = np.array(echo_data[0], dtype=float)
echo_I = np.array(echo_data[1], dtype=float)
Ramsey_I = np.array(Ramsey_data[1], dtype=float)
T1_I = np.array(T1_data[1], dtype=float)

with open('./Coherence_fits.json', 'r') as f:
    coherence_fits = json.load(f)
    f.close()

echo_fit = [coh_fit(i, coherence_fits['echo']['amp'], coherence_fits['echo']['decay'],
                    coherence_fits['echo']['offset']) for i in time]
Ramsey_fit = [ramsey_fit(i, coherence_fits['ramsey']['amp'], coherence_fits['ramsey']['decay'],
                         coherence_fits['ramsey']['offset'], coherence_fits['ramsey']['freq'],
                         coherence_fits['ramsey']['phase']) for i in time]
T1_fit = [coh_fit(i, coherence_fits['T1']['amp'], coherence_fits['T1']['decay'],
                  coherence_fits['T1']['offset']) for i in time]

plt.figure()
plt.plot(time, T1_fit, linestyle='--', linewidth=2, label="T1")
plt.plot(time, T1_I)
plt.plot(time, echo_fit, linestyle='--', linewidth=2, label="Echo")
plt.plot(time, echo_I)
plt.plot(time, Ramsey_fit, linestyle='--', linewidth=2, label="Ramsey")
plt.plot(time, Ramsey_I)
plt.xlabel('t (us)')
plt.ylabel('Signal')
plt.title("Coherence :Ramsey = {:.2f} us , T1 = {:.2f} us , Echo = {:.2f} us".format(coherence_fits['ramsey']['decay'],
                                                                                     coherence_fits['T1']['decay'],
                                                                                     coherence_fits['echo']['decay']))
plt.grid()
plt.legend()
plt.show()
plt.pause(1)
#
plt.figure()
plt.plot(time, T1_fit, linestyle='--', linewidth=2, label="T1")
plt.plot(time, T1_I)
plt.plot(time, echo_fit, linestyle='--', linewidth=2, label="Echo")
plt.plot(time, echo_I)
plt.xlabel('t (us)')
plt.ylabel('Signal')
plt.title("Coherence : T1 = {:.2f} us , Echo = {:.2f} us".format(coherence_fits['T1']['decay'],
                                                                 coherence_fits['echo']['decay']))
plt.grid()
plt.legend()
plt.show(block=False)
plt.pause(1)

#### Final Ramsey (Since Ramsey and echo is vastly different, have to run independently)

exp_ramsey_coh = 'TimeDomain_Ramsey_user_in_det_for_coh'

try:
    subprocess.run(f'python {script_folder_path + exp_ramsey_coh}.py {q_no}', check=True)
except:
    print('Exception occurred. Check')
    sys.exit()

now = datetime.now()
current_date = now.strftime("%y-%m-%d")

fin_path = init_path + ExpName + '/' + exp_ramsey_coh + '/' + current_date + f'_q{q_no}' + '/'

ramsey_file = os.listdir(fin_path)[-1]

ramsey_data = []

with open(fin_path + ramsey_file) as ramsey:
    file = csv.reader(ramsey)
    for row in file:
        ramsey_data.append(row)

ramsey_data = np.transpose(ramsey_data[1:])

time = np.array(ramsey_data[0], dtype=float)
I = np.array(ramsey_data[1], dtype=float)

with open('./ramsey_fits.json', 'r') as f:
    ramsey_fit_data = json.load(f)
    f.close()

I_fit = [ramsey_fit(i, ramsey_fit_data['amp'], ramsey_fit_data['tau'], ramsey_fit_data['offset'],
                    ramsey_fit_data['freq'], ramsey_fit_data['phase'], ) for i in time]

plt.figure()
plt.plot(time, I, ".")
plt.plot(time, I_fit)
plt.xlabel('t (ns)')
plt.ylabel("Ramsey Amplitude")
plt.title(
    f"Ramsey : Ramsey time = {ramsey_fit_data['tau']:.2f} us; Ramsey frequency = {ramsey_fit_data['freq']:.2f} MHz")
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
plt.grid()
plt.show(block=False)
plt.pause(1)
