#%%
from hdawg_init import *
import zhinst

import numpy as np
import matplotlib.pyplot as plt
import time
import zhinst.core
from datetime import datetime
import pyvisa as visa
from datetime import datetime
import json

from RFSoC_PARAMPconfig_08012024_dysl_v1 import *


from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.instrument_helperfunctions import *


#%%

ip = "TCPIP0::192.168.0.27::inst0::INSTR"
rm = visa.ResourceManager()
kna = rm.open_resource(ip)


#%%

rr_range = [1, 2, 3, 4, 5, 6]

iters = 300

delay = 15 * 60

check_USB_switch_status()

switch_to_vna(keyer(f"q{q_no}", dac_mapping))

#%% Save with VNA data into file

gain_profile = (kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
time.sleep(4)
f_data = (kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))

gain_data = list(np.transpose([f_data, gain_profile]))

# save_data = {}
# save_data['DAC_currents'] = current
# save_data['tot_pwr'] = tot_pwr_adj
# save_data['Amp1'] = Amp1_adj
# save_data['DC_bias'] = offset

now = datetime.now()
current_date = now.strftime("%y-%m-%d")

file_name = f'paramp_gain_data_{current_date}_R{(2*rr+5)%12}'

# with open(f'./paramp_data_files/{file_name}.json','w') as f:
#     json.dump(save_data, f, indent = 6)
#     f.close()

np.savetxt(fname = f'./paramp_data_files/{file_name}.csv', X = gain_data)