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
save_data = True
simulate =False

###################
# The QUA program #
###################
rr_no = 2
q_c = 1
q_no = rr_no
Pi12 = False
qe = f"q{rr_no}"
qe_c = f"q{q_c}"
qe12 = f"q12_{rr_no}"
rr = f"rr{rr_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(rr_no)]
rep_rate_clk = 250000
rr_LO = config["elements"][rr]["mixInputs"]["lo_frequency"]

f_min = rr_IF[str(rr_no)] - 10*u.MHz
f_max = rr_IF[str(rr_no)] + 10*u.MHz
df = 0.01e6
freq_list = np.arange(f_min, f_max, df)

rr_amp = ro_amp[str(rr_no)]
integ_len = 4000
update_config_rr(config, q_no, rr_no, rr_amp, integ_len)

a = 0
if Pi12:
    a = 1
# zero_i = np.where(freq_list == 0)[0][0]

with program() as rr_spec:
    n = declare(int)
    I0 = declare(fixed)
    I0_st = declare_stream()
    Q0 = declare(fixed)
    Q0_st = declare_stream()
    I1 = declare(fixed)
    I1_st = declare_stream()
    Q1 = declare(fixed)
    Q1_st = declare_stream()
    f = declare(int)

    with for_(n, 0, n < 200, n + 1):
        with for_(f, f_min, f < f_max, f + df):
            reset_frame(qe)
            update_frequency(rr, f)
            wait(rep_rate_clk - ro_len, rr)
            play("I", qe_c)
            align(qe_c, rr)
            wait(4, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", I0, out),
                    demod.full("integW_minus_sin", Q0, out))

            save(I0, I0_st)
            save(Q0, Q0_st)

            align(rr, qe)
            wait(rep_rate_clk - ro_len, qe)
            play_X180(qe_c)
            align(qe_c, rr)
            wait(4, rr)
            measure_macro(qe, rr, out, I1, Q1, pi_12=Pi12)
            # align(qe, qe12)
            # wait(4, qe12)
            # play_X180(qe12, a=amp(a))
            # align(qe12, rr)
            # wait(4, rr)
            # measure("readout", rr, None,
            #         demod.full("integW_cos", I1, out),
            #         demod.full("integW_minus_sin", Q1, out))

            save(I1, I1_st)
            save(Q1, Q1_st)



    with stream_processing():
        I0_st.buffer(len(freq_list)).average().save('I0')
        Q0_st.buffer(len(freq_list)).average().save('Q0')

        I1_st.buffer(len(freq_list)).average().save('I1')
        Q1_st.buffer(len(freq_list)).average().save('Q1')

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
        simulation_interface=LoopbackInterface([("con1", 9, "con1", 1), ("con1", 10, "con1", 2)]))
    job = qmm.simulate(config, rr_spec, simulation_config)
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()
    raise Halted()

#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(rr_spec)
job.result_handles.wait_for_all_values()
I0 = job.result_handles.get("I0").fetch_all()
Q0 = job.result_handles.get("Q0").fetch_all()
I1 = job.result_handles.get("I1").fetch_all()
Q1 = job.result_handles.get("Q1").fetch_all()

############
# analysis #
############
freq_list1 = 1e-9*(rr_LO + freq_list)
sig0 = I0 + 1j*Q0
sig1 = I1 + 1j*Q1
# freq_list = np.delete(freq_list, zero_i)
# sig0 = np.delete(sig0, zero_i)
# sig1 = np.delete(sig1, zero_i)

e_delay = elec_delay_ns[str(rr_no)]
p_offset = phase_offset_rad[str(rr_no)]
# p_offset = p_offset + 3.9

sig0_corrected = sig0*np.exp(1j*2*np.pi*freq_list1*e_delay + 1j*p_offset)
phase0 = np.angle(sig0_corrected)
real0 = np.real(sig0_corrected)
f0_res_i = np.argmin(abs(phase0))
f0_res = freq_list1[f0_res_i]

sig1_corrected = sig1*np.exp(1j*2*np.pi*freq_list1*e_delay + 1j*p_offset)
phase1 = np.angle(sig1_corrected)
real1 = np.real(sig1_corrected)
f1_res_i = np.argmin(abs(phase1))
f1_res = freq_list1[f1_res_i]
disp = np.round(1e6*abs(f0_res - f1_res)/2, 2)
f_op = np.round((f0_res + f1_res)/2, 6)


f0, f1 = freq_list1[np.argmin(abs(sig0))], freq_list1[np.argmin(abs(sig1))]
disp_mag = np.round(1e6*abs(f0 - f1)/2, 3)
f_op_mag = np.round(abs(f0 + f1)/2, 6)


plt.figure()
plt.title(f"Dispersive shift = {disp} kHz ; Best SNR at {f_op} GHz Phase")
plt.plot(freq_list1, phase0, label = "qubit 0", color="blue")
plt.plot(freq_list1, phase1, label = "qubit 1", color="red")
plt.xlabel("Frequency (GHz)")
plt.axvline(f0_res, linestyle="--", color="blue")
plt.axvline(f1_res, linestyle="--", color="red")
plt.grid()
plt.legend()
plt.show(block=False)

plt.figure()
plt.title(f"Dispersive shift = {disp} kHz ; Best SNR at {f_op} GHz Real Part")
plt.plot(freq_list1, real0, label = "qubit 0", color="blue")
plt.plot(freq_list1, real1, label = "qubit 2", color="red")
plt.xlabel("Frequency (GHz)")
plt.axvline(f0_res, linestyle="--", color="blue")
plt.axvline(f1_res, linestyle="--", color="red")
plt.grid()
plt.legend()
plt.show(block=False)

plt.figure()
plt.title(f"Dispersive shift = {disp_mag} kHz ; Best SNR at {f_op_mag} GHz Magnitude Plot")
plt.plot(freq_list1, abs(sig0), label = "qubit 0", color="blue")
plt.plot(freq_list1, abs(sig1), label = "qubit 1", color="red")
plt.xlabel("Frequency (GHz)")
plt.axvline(f0, linestyle="--", color="blue")
plt.axvline(f1, linestyle="--", color="red")
plt.grid()
plt.legend()
plt.show(block=False)



data0 = np.transpose([freq_list1, real0])
data1 = np.transpose([freq_list1, real1])

if save_data :
    file_saver_(data0, file_name=__file__, suffix=rr + "_Qubit0", master_folder=ExpName, header_string="Frequency (GHz), Magnitude")
    file_saver_(data1, file_name=__file__, suffix=rr + "_Qubit1", master_folder=ExpName, header_string="Frequency (GHz), Magnitude")
