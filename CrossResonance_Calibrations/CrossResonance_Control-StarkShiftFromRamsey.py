from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
from Helper_Functions.macros import *
from qualang_tools.plot import interrupt_on_close
import os
from qualang_tools.results import progress_counter, fetching_tool
from Helper_Functions.CR_fitters import *
from Helper_Functions.qua_program_funcs import *

save_data = False
###################
# The QUA program #
###################
p_min = 0
p_max = 2
dp = 0.01
p_list = np.arange(p_min, p_max, dp)

c_no, t_no = 1, 2

qe_c = f"q{c_no}"
rr_c = f"rr{c_no}"
out_c = adc_mapping[rr_c]
qe_t = f"q{t_no}"
rr_t = f"rr{t_no}"
out_t = adc_mapping[rr_t]
pi_12 = False

qe = qe_c
rr = rr_c
out = out_c

cr_elem = f"cr_c{c_no}t{t_no}"
cr_ac_elem = f"cr_ac_c{c_no}t{t_no}"
p_cr = cr_phase[cr_elem]
a_cr = cr_amp[cr_elem]

wait_init = 250000

wait_t = 4
wait_rr = 8

with program() as ramsey:
    n = declare(int)
    I0 = declare(fixed)
    I0_st = declare_stream()
    Q0 = declare(fixed)
    Q0_st = declare_stream()
    I1 = declare(fixed)
    I1_st = declare_stream()
    Q1 = declare(fixed)
    Q1_st = declare_stream()
    p = declare(float)

    frame_rotation_2pi(p_cr, cr_elem)
    # frame_rotation_2pi(p_ac, "q_ac")
    # update_frequency(qe, qubit_IF + det*1e6)
    with for_(n, 0, n < 1000, n + 1):
        with for_(p, p_min, p < p_max, p + dp):
            reset_frame(qe)
            align(rr_c, qe)
            wait(wait_init, qe)
            play_X90(qe)
            wait(wait_t, qe)
            align(qe, cr_elem)
            # play("const"*amp(1.0), "qubit_cr",24)
            # ZXby2_echo_noAC(cr_elem, qe_c, qe_t)
            ZXby2_echo_AC(cr_elem, cr_ac_elem, qe_c, qe_t)
            wait(wait_t, qe)
            frame_rotation_2pi(p, qe)
            play_X90(qe)
            align(qe, rr)
            wait(wait_rr, rr)
            # measure("readout" * amp(0.2), rr, None,
            #         demod.full("integW_cos", I0, out),
            #         demod.full("integW_minus_sin", Q0, out))
            measure_macro(qe, rr, out, I0, Q0, pi_12=False)
            save(I0, I0_st)
            save(Q0, Q0_st)

            align(rr, qe)
            reset_frame(qe)
            wait(wait_init, qe)
            play_X90(qe)
            frame_rotation_2pi(p, qe)
            play_X90(qe)
            align(qe, rr)
            wait(wait_rr, rr)
            # measure("readout" * amp(0.2), rr, None,
            #         demod.full("integW_cos", I1, out),
            #         demod.full("integW_minus_sin", Q1, out))
            measure_macro(qe, rr, out, I1, Q1, pi_12=False)
            save(I1, I1_st)
            save(Q1, Q1_st)

    with stream_processing():
        I0_st.buffer(len(p_list)).average().save('I0')
        Q0_st.buffer(len(p_list)).average().save('Q0')
        I1_st.buffer(len(p_list)).average().save('I1')
        Q1_st.buffer(len(p_list)).average().save('Q1')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
# simulation_config = SimulationConfig(
#     duration=200000,
#     simulation_interface=LoopbackInterface([("con1", 9, "con1", 1), ("con1", 10, "con1", 2)]))
# job = qmm.simulate(config, rr_spec, simulation_config)

#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(ramsey)
res_handles = job.result_handles
I0_handle = job.result_handles.get("I0")
Q0_handle = job.result_handles.get("Q0")
I1_handle = job.result_handles.get("I1")
Q1_handle = job.result_handles.get("Q1")
# job.result_handles.wait_for_all_values()

I0_handle.wait_for_values(1)
Q0_handle.wait_for_values(1)
I1_handle.wait_for_values(1)
Q1_handle.wait_for_values(1)

plt.ion()
fig, ax = plt.subplots(1)

fig.suptitle("CR: Stark shift measurement")
lines = []

lines.append(ax.plot(p_list, [0] * len(p_list), marker=".", label="Stark Shift Q")[
                 0])  # Returns a tuple of line objects, thus the comma
lines.append(ax.plot(p_list, [0] * len(p_list), marker=".", label="Ramsey Q")[
                 0])  # Returns a tuple of line objects, thus the comma
lines.append(ax.plot(p_list, [0] * len(p_list), marker=".", label="Stark Shift I")[
                 0])  # Returns a tuple of line objects, thus the comma
lines.append(ax.plot(p_list, [0] * len(p_list), marker=".", label="Ramsey I")[
                 0])  # Returns a tuple of line objects, thus the comma
ax.set_ylabel("Ramsey Amplitude")
ax.grid()
ax.legend()

ax.set_xlabel("Phase (p*2pi)")

while res_handles.is_processing():

    I0 = I0_handle.fetch_all()
    Q0 = Q0_handle.fetch_all()
    I1 = I1_handle.fetch_all()
    Q1 = Q1_handle.fetch_all()
    Q = [Q0, Q1, I0, I1]
    for i in [1]:
        lines[2 * i].set_ydata(Q[2 * i])
        lines[2 * i + 1].set_ydata(Q[2 * i + 1])
        ax.relim()
        ax.autoscale_view()
        fig.set_tight_layout(True)
        fig.canvas.draw()
        fig.canvas.flush_events()

    plt.pause(1)

I0 = job.result_handles.get("I0").fetch_all()
Q0 = job.result_handles.get("Q0").fetch_all()
I1 = job.result_handles.get("I1").fetch_all()
Q1 = job.result_handles.get("Q1").fetch_all()

p_list_us = 4e-3 * p_list
if save_data is True:
    np.savetxt(
        "../../../Experiments/2022-06-24 Ringv1-Indiq7_CuCav_Ringv2v3/2022-06-28 Low_temp_Response/RingCavity_1.0/2022-07-02_ConditionalRamsey.txt",
        np.transpose([p_list_us, I0, Q0, I1, Q1]), delimiter="\t")

def ramsey_fit(t, A, f, d, p, c):

    return A * np.exp(-t/d) * np.sin(2*np.pi*f*t + p) + c


pars0, cov0 = curve_fit(f=ramsey_fit, xdata=p_list_us, ydata=Q0, p0=[1e-4,3.5,1,0, -1e-4], bounds=(-np.inf, np.inf), maxfev=2000)
pars1, cov1 = curve_fit(f=ramsey_fit, xdata=p_list_us, ydata=Q1, p0=[1e-4,0.1,1,0, -1e-4], bounds=(-np.inf, np.inf), maxfev=2000)
total_det =  np.abs(np.round(pars0[1] - pars1[1], 4))

print('#########################')
print('### Fitted Parameters ###')
print('#########################')
print("Ramsey frequency control 0 = {0} MHz".format(pars0[1]))
print("Ramsey time control 0 = {0} us".format(pars0[2]))
print("Ramsey frequency control 1 = {0} MHz".format(pars1[1]))
print("Ramsey time control 1 = {0} us".format(pars1[2]))
print("Total detuning = {0} kHz".format(1e3*total_det))
print("ZZ error = {0} MHz".format(0.5*total_det))

plt.figure()
plt.plot(p_list, Q0, "^", color="red")
plt.plot(p_list, ramsey_fit(p_list,*pars0), label="Control 0", color="red")
# plt.plot(t_list_us, Q1, "^", color="blue")
# plt.plot(t_list_us, ramsey_fit(t_list_us,*pars1), label="Control 1", color="blue")
plt.xlabel('t (us)')
plt.ylabel('Signal')
# plt.title("Conditional Ramsey : Target ; Total shift = {0} kHz".format(total_det))
plt.legend()
plt.grid()
plt.show()
