from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from Helper_Functions.macros import *
from scipy.optimize import curve_fit
import sys
import pyvisa as visa

###################
# The QUA program #
###################

save_data = False
simulate = False
check_e_delay = True

rr_no = 3
q_no = rr_no
rr = f"rr{rr_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(rr_no)]
rep_rate_clk = 2500
ro_power = rr_LO_dBm        # in dBm

with open('../../fourqubitv3/System_Parameters/init_freqs.json', 'r') as f:
    init_dic = json.load(f)
    f.close()

# rr_LO = config["elements"][rr]["mixInputs"]["lo_frequency"]
# rr_LO = init_dic['rr_init'][f'{q_no}'] - 0.02     # in GHz

## Set readout LO

LO_control = 0

if LO_control == 1:
    rr_LO2 = init_dic['rr_init'][f'{q_no}'] - 0.02  # in GHz
    LO_ip = LO_IP_dict[f'rf_rr{rr_no}_ip']
    rr_LO1 = rr_LO2

    rm = visa.ResourceManager()
    rns_siggen = rm.open_resource(LO_ip)
    rns_siggen.write('OUTP:STAT OFF')
    rns_siggen.write(f'SOUR:FREQ:CW {rr_LO1} GHz')
    rns_siggen.write(f'SOUR:POW {ro_power}dBm')
    rns_siggen.write('OUTP:STAT ON')
else:
    rr_LO1 = rr_LO[f'{q_no}']*1e-9  # in GHz



f_min = -100e6
f_max = 100e6
df = 0.5e6


f_min = rr_IF[str(rr_no)] - 100*u.MHz
f_max = rr_IF[str(rr_no)] + 100*u.MHz
df = 1e6

rr_amp = 0.05
integ_len = 4000
update_config_rr(config, q_no, rr_no, rr_amp, integ_len)
# f_min = 20e6
# f_max = 60e6
# df = 0.1e6

# if check_e_delay:
#     f_min = -100e6
#     f_max = 300e6
#     df = 0.5e6

freq_list = np.arange(f_min, f_max, df)
zeros = np.where(freq_list == 0)[0]
if len(zeros):
    zero_i = zeros[0]

with program() as rr_spec:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    f = declare(int)

    with for_(n, 0, n < 2000, n + 1):
        with for_(f, f_min, f < f_max, f + df):

            update_frequency(rr, f)
            wait(rep_rate_clk - ro_len, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", I, out),
                    demod.full("integW_minus_sin", Q, out))

            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(freq_list)).average().save('I')
        Q_st.buffer(len(freq_list)).average().save('Q')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
if simulate:
    simulation_config = SimulationConfig(
        duration=200000,
        simulation_interface=LoopbackInterface([("con2", 7, "con2", 1), ("con2", 8, "con2", 2)]))
    job = qmm.simulate(config, rr_spec, simulation_config)
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con2.plot()
    raise Halted()

#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(rr_spec)
job.result_handles.wait_for_all_values()
I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

############
# analysis #
############

freq_list1 = rr_LO1 + 1e-9*(freq_list)
sig = I + 1j*Q
if len(zeros):
    freq_list1 = np.delete(freq_list1, zero_i)
    sig = np.delete(sig, zero_i)

e_delay = 0#elec_delay_ns[str(rr_no)]-1
p_offset = phase_offset_rad[str(rr_no)]
# if check_e_delay:
#     e_delay = elec_delay_ns[str(rr_no)]
#     p_offset = phase_offset_rad[str(rr_no)]

sig_corrected = sig*np.exp(1j*2*np.pi*freq_list1*e_delay + 1j*p_offset)
phase = np.angle(sig_corrected)
real = np.real(sig_corrected)
imag = np.imag(sig_corrected)

mag_data = np.abs(sig)

df1 = df*1e-9
ph_d = np.diff(phase)

e_delay_est = -1*np.median(ph_d)/(2*3.14159*df1)# + 20

cav_wid = 5*1e6

samp = int(cav_wid/df)
cavity_freq = np.where(mag_data == np.min(mag_data))[0][0]

sig_corrected2 = sig_corrected*np.exp(1j*2*np.pi*freq_list1*e_delay_est + 1j*p_offset)
ph2 = np.angle(sig_corrected2)

if cavity_freq - samp < 0:
    p_offset = -np.pi - ph2[cavity_freq + samp]
else:
    p_offset = np.pi - ph2[cavity_freq - samp]

# p_offset = phase_offset_rad[f"{rr_no}"]
sig_corrected = sig_corrected*np.exp(1j*2*np.pi*freq_list1*e_delay_est + 1j*p_offset)

phase1 = np.angle(sig_corrected)
real1 = np.real(sig_corrected)
imag1 = np.imag(sig_corrected)

f_res_i = np.argmin(np.abs(sig))
f_res = freq_list1[f_res_i]

plt.figure()
plt.plot(freq_list1, phase1)
plt.legend()
plt.xlabel("Frequency (GHz)")
plt.title(f'Cavity Spectroscopy (Phase) : Cavity Frequency = {f_res} GHz')
plt.axvline(x=f_res, linestyle = "--")
plt.grid()
plt.show(block=False)

if not check_e_delay:
    plt.figure()
    plt.plot(freq_list1, real1, label="Real")
    plt.plot(freq_list1, imag1, label="Imag")
    plt.title(f'Cavity Spectroscopy (Real) : Cavity Frequency = {f_res} GHz')
    plt.xlabel("Frequency (GHz)")
    plt.axvline(x=f_res, linestyle = "--")
    plt.grid()
    plt.legend()
    plt.show(block=False)

    plt.figure()
    plt.plot(freq_list1, np.abs(sig))
    plt.title(f'Cavity Spectroscopy (Magnitude) : Cavity Frequency = {f_res} GHz')
    plt.xlabel("Frequency (GHz)")
    plt.axvline(x=f_res, linestyle="--")
    plt.grid()
    plt.show(block=False)

data = np.transpose([freq_list1, phase1, real1, imag1, np.abs(sig)])

if save_data:
    file_saver_(data, file_name=__file__, suffix=f'{rr}', master_folder=ExpName,
                header_string="Frequency (GHz), Phase, Real, Imaginary, Magnitude")

print(f'Detected Readout Resonator Frequency is {f_res} GHz. Adjusting IF appropriately!!')
#
# with open('./System_Parameters/rr_IF.json','r') as f:
#     rr_IF_vals = json.load(f)
#     f.close()
#
# with open('./System_Parameters/rr_LO.json','r') as f:
#     rr_LO_m = json.load(f)
#     f.close()
#
# if LO_control == 0:
#
#     if_val_new = (f_res - rr_LO_m[f'{q_no}'])*1e3
#     rr_IF_vals[f'{q_no}'] = np.round(if_val_new)
#
# else:
#     LO_frequency = rns_siggen.query_ascii_values('SOUR:FREQ:CW?')[0]/1e9
#
#     if_val_new = (f_res - LO_frequency)*1e3
#     rr_IF_vals[f'{q_no}'] = np.round(if_val_new)
#
# with open('./System_Parameters/rr_IF.json','w') as f:
#     json.dump(rr_IF_vals,f,indent=6)
#     f.close()

# sig_corrected = sig_corrected*np.exp(1j*2*np.pi*freq_list1*0 + 1j*(p_offset+40))
#
# phase1 = np.angle(sig_corrected)
# real1 = np.real(sig_corrected)
# imag1 = np.imag(sig_corrected)
#
# f_res_i = np.argmin(np.abs(sig))
# f_res = freq_list1[f_res_i]
#
# plt.figure()
# plt.plot(freq_list1, phase1)
# plt.legend()
# plt.xlabel("Frequency (GHz)")
# plt.title(f'Cavity Spectroscopy (Phase) : Cavity Frequency = {f_res} GHz')
# plt.axvline(x=f_res, linestyle = "--")
# plt.grid()
# plt.show(block=False)
