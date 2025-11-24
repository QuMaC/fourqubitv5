import numpy as np
import json
from Configuration_Files.configuration_4qubitsv3 import *

with open('../Configuration_Files/System_Parameters/punchout_shifts.json', 'r') as f:
    punchouts = json.load(f)
    f.close()

with open('../Configuration_Files/System_Parameters/external_bandwidth.json', 'r') as f:
    ext_bws = json.load(f)
    f.close()

with open('../Configuration_Files/System_Parameters/internal_bandwidth.json', 'r') as f:
    int_bws = json.load(f)
    f.close()

with open('../Configuration_Files/System_Parameters/anharmonicities.json', 'r') as f:
    anhs = json.load(f)
    f.close()

# q_no = 1
#

q_c_coupling = {}
disp_shift = {}
purcell_T1 = {}

for q_no in [1, 2, 3, 4, 5, 6]:
# for q_no in [6]:

    f_c = rr_LO[str(q_no)] + rr_IF[str(q_no)]

    punchout = punchouts[str(q_no)] * 1e6

    bw = ext_bws[str(q_no)] + int_bws[str(q_no)]

    f_q = q_LO[str(q_no)] + q_IF[str(q_no)]

    d_q = anhs[str(q_no)] * 1e6

    k = (2 * np.pi * bw) * 1e6

    delta = f_c - f_q
    g = np.sqrt(delta * punchout)  #Needs 
    T_purcell = (1 / k) * (delta / g) ** 2
    chi = g ** 2 * (1 / (-delta) - 1 / (-delta - d_q))

    q_c_coupling[str(q_no)] = np.round(g * 1e-6, 5)
    disp_shift[str(q_no)] = np.round(chi * 1e-6, 5)
    purcell_T1[str(q_no)] = np.round(T_purcell * 1e6 * 1e-6, 5)

    print('-------------------------------------------------------------')
    print(f"Qubit-Cavity coupling for qubit {q_no} =  {g * 1e-6:.3f} MHz")
    print(f"Purcell T1 for qubit {q_no} = {T_purcell * 1e6:.3f} us")
    print(f"Dispersive Shift for qubit {q_no} = {chi * 1e-6:.3f} MHz")


print('-------------------------------------------------------------')
with open('../Configuration_Files/System_Parameters/qubit_cavity_couplings.json', 'w') as f:
    json.dump(q_c_coupling, f, indent=6)
