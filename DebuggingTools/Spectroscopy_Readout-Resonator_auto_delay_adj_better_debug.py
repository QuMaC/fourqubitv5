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

rr_no = 1
q_no = rr_no
rr = f"rr{rr_no}"

q_c = 2
rr_c = f"rr{q_c}"

out = adc_mapping[rr]
ro_len = ro_len_clk[str(rr_no)]
rep_rate_clk = 250000
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

e_delay = 0  # elec_delay_ns[str(rr_no)]-1
p_offset = 0

f_offsets = [150, 30]

for f_offset in f_offsets:

    f_min = rr_IF[str(rr_no)] - f_offset*u.MHz
    f_max = rr_IF[str(rr_no)] + f_offset*u.MHz
    df = f_offset*u.MHz/100

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
                reset_frame(qe)
                reset_frame(rr)
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

    freq_list1 = rr_LO1 + 1e-9 * (freq_list)
    sig = I + 1j * Q
    if len(zeros):
        freq_list1 = np.delete(freq_list1, zero_i)
        sig = np.delete(sig, zero_i)

    phase = np.angle(sig)
    real = np.real(sig)
    imag = np.imag(sig)
    u_phase = np.unwrap(phase)

    # plt.figure()
    # plt.plot(freq_list1, u_phase)
    # plt.legend()
    # plt.xlabel("Frequency (GHz)")
    # plt.grid()
    # plt.show(block=False)


    if f_offset == max(f_offsets):

        sec1 = u_phase[0:len(u_phase)//3]
        sec2 = u_phase[len(u_phase) // 3: 2*len(u_phase) // 3]
        sec3 = u_phase[2*len(u_phase) // 3:]

        len_f = len(freq_list1)

        data1, cov1 = np.polyfit(freq_list1[0:len(u_phase)//3], sec1, 1, cov=True)
        data2, cov2 = np.polyfit(freq_list1[len(u_phase) // 3: 2*len(u_phase) // 3], sec2, 1, cov=True)
        data3, cov3 = np.polyfit(freq_list1[2*len(u_phase) // 3:], sec3, 1, cov=True)

        id = np.argmin([cov1[0][0], cov2[0][0], cov3[0][0]])

        slope = [data1[0], data2[0], data3[0]][id]

        e_delay = -slope / (2*np.pi)

        plt.figure()
        plt.plot(freq_list1, phase)
        plt.plot(freq_list1, u_phase)
        plt.plot(freq_list1[0:len(u_phase)//3], data1[0]*freq_list1[0:len(u_phase)//3] + data1[1])
        plt.plot(freq_list1[len(u_phase) // 3: 2*len(u_phase) // 3], data2[0]*freq_list1[len(u_phase) // 3: 2*len(u_phase) // 3] + data2[1])
        plt.plot(freq_list1[2*len(u_phase) // 3:], data3[0]*freq_list1[2*len(u_phase) // 3:] + data3[1])
        plt.legend()
        plt.xlabel("Frequency (GHz)")
        plt.grid()
        plt.show(block=False)

        sig_corrected1 = sig * np.exp(1j * 2 * np.pi * freq_list1 * e_delay)

        phase1 = np.angle(sig_corrected1)
        real1 = np.real(sig_corrected1)
        imag1 = np.imag(sig_corrected1)

        plt.figure()
        plt.plot(freq_list1, phase1)
        plt.legend()
        plt.xlabel("Frequency (GHz)")
        plt.title(f'Cavity Spectroscopy (Phase)')
        plt.grid()
        plt.show(block=False)

    else:

        sig_corrected = sig * np.exp(1j * 2 * np.pi * freq_list1 * e_delay)

        cav_wid = 10 * 1e6

        d_uph = np.diff(u_phase)

        cav_ph_id = np.argmax(np.abs(d_uph))

        cavity = freq_list1[cav_ph_id] # in GHz

        ph_offset = -1*(u_phase[cav_ph_id])

        sig_corrected1 = sig_corrected*np.exp(1j*1*ph_offset)

        phase1 = np.angle(sig_corrected1)
        real1 = np.real(sig_corrected1)
        imag1 = np.imag(sig_corrected1)

        ph_offset = ph_offset - phase1[cav_ph_id]

        ph_offset = (ph_offset%(2*np.pi)) - np.pi

        sig_corrected1 = sig_corrected * np.exp(1j * -1 * ph_offset)

        phase1 = np.angle(sig_corrected1)
        real1 = np.real(sig_corrected1)
        imag1 = np.imag(sig_corrected1)

        plt.figure()
        plt.plot(freq_list1, phase1)
        plt.legend()
        plt.xlabel("Frequency (GHz)")
        plt.title(f'Cavity Spectroscopy (Phase) : Cavity Frequency = {cavity} GHz')
        plt.axvline(x=cavity, linestyle = "--")
        plt.grid()
        plt.show(block=False)

data = np.transpose([freq_list1, phase1, real1, imag1, np.abs(sig)])

if save_data:
    file_saver_(data, file_name=__file__, suffix=f'{rr}', master_folder=ExpName,
                header_string="Frequency (GHz), Phase, Real, Imaginary, Magnitude")

print(f'E_delay = {e_delay}')
print(f'Phase offset = {ph_offset}')


print(f'Detected Readout Resonator Frequency is {cavity} GHz')











