import copy
import os
import sys
import threading
import json
import subprocess
from Configuration_Files.configuration_4qubitsv3 import *
from datetime import datetime
import csv

n_qubits = 1
q_no_list = range(1, n_qubits+1)
q_no_list = [1]
calibrate_CR = False

offset = 'Calibration_Mixer_Offset_SA_user_in'
sideband = 'Calibration_Mixer_Sideband_SA_user_in'

for q_no in q_no_list:
    os.system(f'python {offset}.py q{q_no}')
    os.system(f'python {offset}.py rr{q_no}')
    os.system(f'python {sideband}.py q{q_no}')
    os.system(f'python {sideband}.py rr{q_no}')

    if calibrate_CR:
        if q_no in control_qubits:
            for t_no in connectivity[c_no]:
                os.system(f'python {sideband}.py cr_c{q_no}t{t_no}')

with open('../Configuration_Files/offset_sideband_values.json', 'r') as f:
    vals = json.load(f)
    f.close()

for key in vals.keys():
    print(f"For quantum element {key}")
    print(f"LO leakage is {vals[key]['offset']}")
    print(f"Reject Band power is {vals[key]['sideband']}")