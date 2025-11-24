import os
from matplotlib import pyplot as plt
from Configuration_Files.configuration_4qubitsv3 import *
import csv
import logging

logger = logging.getLogger(__name__)

matplotlib.use('Qt5Agg')
from Helper_Functions.analysis_functions import *


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

q_no = 4


init_path = "D:/Experiments/"

exp_rabi = 'TimeDomain_Rabi_user_in'

date = '25-08-19' ## yy-mm-dd

fin_path = init_path + ExpName + '/' + exp_rabi + '/' + date + f'_q{q_no}' + '/'

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

fit_flg = False

try:
    with open(fin_path + 'fit_data.json', 'r') as f:
        fit_data = json.load(f)
        fit_flg = True
        f.close()
except FileNotFoundError:
    logger.warning(f"No fit_data.json found in {fin_path!r}. Skipping.")


if not fit_flg:
    res_I = fit_cos(time, I)
    res_Q = fit_cos(time, Q)
    del res_I['fitfunc']
    del res_Q['fitfunc']
    del res_I['rawres']
    del res_Q['rawres']
    fit_data = {'fit_data_I': res_I, 'fit_data_Q': res_Q}

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


Power_rabi_file = 'PulseCalib_Power-Rabi_user_qubit'

fin_path = init_path + ExpName + '/' + Power_rabi_file + '/' + date + f'_q{q_no}' + '/'

files = os.listdir(fin_path)
#
# fit_flg = False
# with open(fin_path + './fit_data.json', 'r') as f:
#     power_fit_data = json.load(f)
#     fit_flg = True
#     f.close()

def para_fit(x, temp4, temp3, temp2, temp1, temp0):
    return temp4 * x ** 4 + temp3 * x ** 3 + temp2 * x ** 2 + temp1 * x + temp0

fit_flg = False

try:
    with open(fin_path + './fit_data.json', 'r') as f:
        power_fit_data = json.load(f)
        fit_flg = True
        f.close()
except FileNotFoundError:
    logger.warning(f"No fit_data.json found in {fin_path!r}. Skipping.")


    # res_I = fit_cos(time, I)
    # res_Q = fit_cos(time, Q)
    # del res_I['fitfunc']
    # del res_Q['fitfunc']
    # del res_I['rawres']
    # del res_Q['rawres']
    # fit_data = {'fit_data_I': res_I, 'fit_data_Q': res_Q}

for keys in ["X180", "X90", "Y180", "Y90"]:

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

    if not fit_flg:
        para_fit_val = np.polyfit(amp, p_I, 4)

        amp_arr = np.linspace(min(amp), max(amp), 2000)

        find_amp = para_fit(amp_arr, *para_fit_val)

        pi_amp = amp_arr[np.argmax(find_amp)]

        fit_data1 = {
            'power0': para_fit_val[0],
            'power1': para_fit_val[1],
            'power2': para_fit_val[2],
            'power3': para_fit_val[3],
            'power4': para_fit_val[4],
            'gate_amp': pi_amp
        }
        vals = fit_data1



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


exp_coh = 'TimeDomain_Interleaved-Coherence-Individual_user_qubit'

fin_path = init_path + ExpName + '/' + exp_coh + '/' + date + f'_q{q_no}' + '/'

try:
    files = os.listdir(fin_path)
except FileNotFoundError:
    raise Warning('File/Dir not found')


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

fit_flg = False

try:
    with open(fin_path + './fit_data.json', 'r') as f:
        coherence_fits = json.load(f)
        fit_flg = True
        f.close()
except FileNotFoundError:
    logger.warning(f"No fit_data.json found in {fin_path!r}. Skipping.")

if not fit_flg:

    res_I, pcov_i, init_i = ramsey_fitting(time, Ramsey_I)  # A, tau, offset, freq, phi

    T1_init = exp_init(time, T1_I)

    # T1_p0 = [T1_init[1], T1_init[0], T1_init[2]]

    echo_init = exp_init(time, echo_I)

    # echo_p0 = [echo_init[1], echo_init[0], echo_init[2]]

    pars_e, cov_e = curve_fit(f=coh_fit, xdata=time, ydata=echo_I, p0=echo_init, bounds=(-np.inf, np.inf),
                              maxfev=2000)
    pars_t, cov_t = curve_fit(f=coh_fit, xdata=time, ydata=T1_I, p0=T1_init, bounds=(-np.inf, np.inf),
                              maxfev=2000)

    coherence_fits = {'ramsey': {'amp': res_I[0],
                       'freq': res_I[3],
                       'decay': res_I[1],
                       'phase': res_I[4],
                       'offset': res_I[2],
                       },
            'echo': {
                'amp': pars_e[0],
                'decay': pars_e[1],
                'offset': pars_e[2],
            },
            'T1': {
                'amp': pars_t[0],
                'decay': pars_t[1],
                'offset': pars_t[2],
            },
            }

# with open(fin_path + './fit_data.json', 'r') as f:
#     coherence_fits = json.load(f)
#     f.close()



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
plt.show(block=False)
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






from scipy import signal
sos = signal.butter(10, 10, 'lowpass', fs=1/(time[1]-time[0]), output='sos')