import numpy as np
import json
from Configuration_Files.configuration_4qubitsv3 import *

# define qubit ordering
qubits = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6']
n = len(qubits)

# initialize detuning matrix with NaN for missing entries
detuning = np.full((n, n), np.nan)
couplings = np.full((n, n), np.nan)

# data: (control, target, detuning_kHz)
measurements = [
    ('q3','q2',  73.4),
    ('q2','q3',  93.3),
    ('q1','q2',  90.8),
    ('q2','q1',  92.2),
    ('q5','q2',  48.3),
    ('q2','q5',  62.4),
    ('q5','q4',  50.1),
    ('q4','q5',  49.4),
    ('q5','q6', 212.2),
    ('q6','q5', 187.2),
    ('q3','q6', 543.0),
    ('q6','q3', 526.9),
    ('q1','q6',1298.1),
    ('q6','q1',1235.1),
    ('q1','q4', 66.1),
    ('q4','q1', 54.4),
    ('q3','q4', 65.7),
    ('q4','q3', 65.8),
]

# fill the matrix
for ctrl, tgt, d in measurements:
    i = qubits.index(ctrl)
    j = qubits.index(tgt)
    detuning[i, j] = d


for c1 in [1, 3, 5]:
    for t1 in [2, 4, 6]:
        for dummy in range(2):
            if dummy%2 != 0:
                k = t1
                t = c1
                c = k
            else:
                t = t1
                c = c1

            print(f"control = {c}, target = {t}")

            f_shift = detuning[c-1, t-1] * 1e3

            ZZ = f_shift / 2

            with open('../Configuration_Files/System_Parameters/anharmonicities.json', 'r') as f:
                anhs = json.load(f)
                f.close()

            qc_f = q_LO[str(c)] + q_IF[str(c)]
            qt_f = q_LO[str(t)] + q_IF[str(t)]

            d1, d2 = -anhs[str(c)], -anhs[str(t)]
            del12 = 1e-6 * (qc_f - qt_f)

            J_sq = -ZZ * (del12 + d1) * (d2 - del12) / (d1 + d2)
            if J_sq > 0:
                J = np.sqrt(J_sq)
            else:
                J = np.sqrt(-1 * J_sq)

            couplings[c-1, t-1] = np.round(J, 3) / 1e3

            # print(f'Coupling between  is {J * 1e-3:.3f} MHz')
