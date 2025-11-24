#%%
from hdawg_init import *
import zhinst

import sys
import os

sys.path.append(os.path.abspath('../'))

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

rr_range = [1, 3, 4, 5, 6]

iters = 300

delay = 15 * 60

check_USB_switch_status()

recall_setting_path = ' "D:\\03022025_ring\\paramp_R'

for q in rr_range:
    var_name = f'cav_gain_list_R{(2*q+5)%12}'
    locals()[var_name] = []

#%% Save with VNA data into file

for it in range(iters):

    for rr in rr_range:

        ring_pos = (2*rr+5)%12

        print(f'Checking R{ring_pos}')

        var_name = f'cav_gain_list_R{ring_pos}'

        ## VNA switch

        switch_to_vna(keyer(f"q{rr}", dac_mapping))

        time.sleep(5)

        ## load settings 

        fin_path = recall_setting_path + f'{ring_pos}' + '.csa"'

        kna.write("MMEM:LOAD " + fin_path)

        time.sleep(5)

        ##
        gain_profile = (kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
        time.sleep(4)
        f_data = (kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))

        gain_data = list(np.transpose([f_data, gain_profile]))

        f_center = f_data[len(f_data)//2]

        f_cav = f_center + 20e6

        f_cav_id = np.argmin(np.abs(np.array(f_data)-f_cav))

        cav_gain = gain_profile[f_cav_id]

        cent_gain = gain_profile[f_data.index(f_center)]

        locals()[var_name].append([cent_gain, cav_gain])

        # save_data = {}
        # save_data['DAC_currents'] = current
        # save_data['tot_pwr'] = tot_pwr_adj
        # save_data['Amp1'] = Amp1_adj
        # save_data['DC_bias'] = offset

        now = datetime.now()
        current_date = now.strftime("%y-%m-%d")

        save_dir = f'./paramp_overnight/{current_date}'

        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)

        file_name = f'/paramp_gain_data_{current_date}_R{ring_pos}_{it}.csv'

        # with open(f'./paramp_data_files/{file_name}.json','w') as f:
        #     json.dump(save_data, f, indent = 6)
        #     f.close()

        np.savetxt(fname = save_dir + file_name, X = gain_data)

    time.sleep(delay)
# %%

cav_gain_1 = [i[1] for i in cav_gain_list_R7]
cav_gain_3 = [i[1] for i in cav_gain_list_R11]
cav_gain_4 = [i[1] for i in cav_gain_list_R1]
cav_gain_5 = [i[1] for i in cav_gain_list_R3]
cav_gain_6 = [i[1] for i in cav_gain_list_R5]
# %%


plt.figure()
save_dir = f'./paramp_overnight/{current_date}'
for rr in rr_range:
    ring_pos = (2*rr+5)%12
    plt.plot(locals()[f'cav_gain_{rr}'], label = f'RR{ring_pos}')
    np.savetxt(fname = save_dir + f'/RR{ring_pos}_gain-stability.csv', X = locals()[f'cav_gain_{rr}'])

plt.grid()
plt.legend()
plt.ylabel("Gain (dB)")
plt.xlabel("Run Number")
plt.title("Paramp gain at cavity frequency")


# %%
