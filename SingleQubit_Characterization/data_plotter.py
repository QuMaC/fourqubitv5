import os
from matplotlib import pyplot as plt
from Configuration_Files.configuration_4qubitsv3 import *
import csv
from pathlib import Path
import re

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

def clean_name(name):
    # drop parenthetical content
    name = re.sub(r'\([^)]*\)', '', name)
    # remove non-alphanumeric characters, convert runs to single underscore
    name = re.sub(r'[^A-Za-z0-9]+', '_', name)
    # strip leading/trailing underscores
    name = name.strip('_')
    return name

def coh_fit(t, A, d, c):
    return A * np.exp(-t / d) + c



data_path = r'File saved as:  D:/Experiments//2025-06-07 Ringv1-INDIQTa08^J02-6Qubits-Shifted02_post_topup/TimeDomain_Interleaved-Coherence-Individual_user_qubit/25-06-28_q2/TimeDomain_Interleaved-Coherence-Individual_user_qubit-Ramsey_q1-00-05-57.csv'

fit_data_flg = False

jsons = list(Path('./').glob("*.json"))

data = []

with open(data_path, 'r') as rabi:
    file = csv.reader(rabi)
    for row in file:
        data.append(row)

headers = np.transpose(data[0])

test_data = np.transpose(data[1:])

cleaned = np.array([clean_name(n) for n in headers])

for i, head in enumerate(cleaned):
    locals()[head] = np.array(test_data[i], dtype=float)
    if 'ime' in head:
        time = locals()[head]

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
