from qm import SimulationConfig
import json
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from Helper_Functions.macros import *
from matplotlib import pyplot as plt
import sys

###################
# The QUA program #
###################
simulate = False
rr_no = int(sys.argv[1])
rr = f"rr{rr_no}"
ro_len = ro_len_clk[str(rr_no)]
rep_rate_clk = 250000 # 1 ms
tof_if = 12 * u.MHz

with open('./loopback_tof.json','w') as f:
    json.dump({str(rr_no): {'loopback': 0}}, f, indent=6)
    f.close()

# rep_rate_clk = 10000 # 1 ms

# config['elements'][rr]['intermediate_frequency'] = tof_if
#
# tof_dict = {}
# for key in config['mixers'][f'mixer_{rr}'][0].keys():
#     if key == 'intermediate_frequency':
#         tof_dict[key] = tof_if
#     else:
#         tof_dict[key] = config['mixers']['mixer_rr1'][0][key]
#
# config['mixers'][f'mixer_{rr}'].append(tof_dict)
#
# config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "arbitrary",
#                                                   "samples": grft_arr_gen((ro_len_clk[str(rr_no)] * 4, 200)
#                                                     )}
rr_amp = 1
integ_len = ro_len
update_config_rr(config, rr_no, rr_no, rr_amp, integ_len)

with program() as tof_cal:

    n = declare(int)
    adc_st = declare_stream(adc_trace=True)
    update_frequency(rr, tof_if)
    with for_(n, 0, n < 500, n+1):

        reset_phase(rr)
        wait(rep_rate_clk - ro_len, rr)
        update_frequency(rr, tof_if)
        measure("readout", rr, adc_st)


    with stream_processing():
        adc_st.input1().average().save("adc1")
        adc_st.input2().average().save("adc2")

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################

if simulate:
    simulation_config = SimulationConfig(
        duration=2000,
        simulation_interface=LoopbackInterface([("con1", 9, "con1", 1), ("con1", 10, "con1", 2)]))
    job = qmm.simulate(config, tof_cal, simulation_config)
    job.result_handles.wait_for_all_values()
    adc1 = job.result_handles.get("adc1").fetch_all()
    adc2 = job.result_handles.get("adc2").fetch_all()

    raise Halted()

#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(tof_cal)
res_handles = job.result_handles
adc1_handle = res_handles.get("adc1")
adc2_handle = res_handles.get("adc2")
res_handles.wait_for_all_values()
adc1 = job.result_handles.get("adc1").fetch_all()
adc2 = job.result_handles.get("adc2").fetch_all()

############
# analysis #
############
adc1_offset = -np.mean(adc1)*2**-12
adc2_offset = -np.mean(adc2)*2**-12

con = f"con{dac_mapping[rr][0]}"

with open('../Configuration_Files/Calibrations/adc_offsets.json') as f:
    adc_offsets = json.load(f)

adc_offsets[con]["1"] = adc_offsets[con]["1"] + adc1_offset
adc_offsets[con]["2"] = adc_offsets[con]["2"] + adc2_offset

with open('../Configuration_Files/Calibrations/adc_offsets.json', "w") as outfile:
    json.dump(adc_offsets, outfile, indent=4)

plt.figure()
plt.title('time-of-flight calibration analysis')
plt.plot(adc1)
plt.plot(adc2)
plt.legend(
    [f"adc1: offset = {adc1_offset:.4f}",
     f"adc2: offset = {adc2_offset:.4f}"])
plt.show(block=False)

i = len(adc1)//3
e = 2*len(adc1)//3

Y_1 = np.fft.fft(adc1[i:e])*(2/len(adc1[i:e]))
Y_2 = np.fft.fft(adc2[i:e])*(2/len(adc2[i:e]))

X = np.fft.fftfreq(n=len(adc1[i:e]),d=1e-9)

Y_1 = Y_1[1:len(Y_1)//2]
Y_2 = Y_2[1:len(Y_2)//2]
X = X[1:len(X)//2]

a = np.where(np.abs(Y_1) == np.max(np.abs(Y_1)))[0][0]
b = np.where(np.abs(Y_2) == np.max(np.abs(Y_2)))[0][0]

max_amp_1 = np.abs(Y_1)[a]
max_amp_2 = np.abs(Y_2)[b]

print(f'max amp 1 {max_amp_1}')
print(f'max amp 2 {max_amp_2}')

with open('./loopback_tof.json','w') as f:
    if max_amp_1 > 3 or max_amp_2 > 3:
        json.dump({str(rr_no): {'loopback': 1}},f,indent=6)
        print("Loopback Successful")
    else:
        json.dump({str(rr_no): {'loopback': 0}},f,indent=6)
        print("Loopback Failed, or try manually")

#
# with open('./report.txt','a') as f:
#
#
#
#
#
#


