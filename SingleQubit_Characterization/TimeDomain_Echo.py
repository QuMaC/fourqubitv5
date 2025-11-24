import json
from qm.qua import *
from qm import SimulationConfig
from qm import QuantumMachinesManager
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.plot import interrupt_on_close
from Helper_Functions.macros import measure_macro, cooldown
from Helper_Functions.analysis_functions import *
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
import copy

simulate = False
save_data = False
active_reset = False     # Set as true for resetting qubit with feedback
pi_12 = False

###################
# The QUA program #
###################
t_min = 4//4   #ns
t_max = 10000//4
dt = 32//4 #steps of 4ns
t_list = np.arange(t_min, t_max, dt)

q_no = 6
qubit_IF = q_IF[str(q_no)]
qe = f"q{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
det = 0 # in MHz
dem = 0

if simulate : rep_rate_clk = 100
else: rep_rate_clk = 250000

with program() as ramsey:

    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    I_ar = declare(fixed)
    Q_ar = declare(fixed)
    t = declare(int)

    with for_(n, 0, n < 1000, n + 1):
        with for_(t, t_min, t < t_max, t + dt):

            if simulate: assign(t, 100)

            cooldown(time=rep_rate_clk, active_reset=active_reset, qe=qe, qe_12=None, rr=rr, out=out, I=I_ar, Q=Q_ar,
                     pi_12=False, dem=dem)
            align(qe, rr)
            play_X90(qe)
            wait(t, qe)
            play_X180(qe)
            wait(t, qe)
            play_X90(qe)
            # align(qe, rr)
            # measure("readout", rr, None,
            #         demod.full("integW_cos", I, out),
            #         demod.full("integW_minus_sin", Q, out))
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)
            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('I')
        Q_st.buffer(len(t_list)).average().save('Q')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
if simulate:
    qmm = QuantumMachinesManager()
    job = qmm.simulate(config, ramsey, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()

    raise Halted()
#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(ramsey)
res_handles = job.result_handles
I_handle = job.result_handles.get("I")
Q_handle = job.result_handles.get("Q")
# job.result_handles.wait_for_all_values()

plt.figure()
plt.title("Echo")
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)

plot_no = 1
while res_handles.is_processing():

    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    sig = I + 1j * Q
    plt.clf()
    # plt.plot(4e-3*t_list, Q, marker=".", label="Q")
    plt.plot(8e-3 * t_list, I, marker=".", label="I")
    plt.xlabel("Time (us)")
    plt.ylabel("Echo Amplitude")
    plt.title("Echo N = {0}".format(plot_no*20))
    plt.grid()
    plt.legend()
    plt.pause(0.2)
    plot_no+=1


I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()
sig = I + 1j*Q

t_list_us = 8e-3*t_list


def ramsey_fit(t, A, f, d, p, c):

    return A * np.exp(-t/d) * np.sin(2*np.pi*f*t + p) + c


pars, cov = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=I, p0=[1e-3,det,1,0, 1e-4], bounds=(-np.inf, np.inf), maxfev=10000)


print('#########################')
print('### Fitted Parameters ###')
print('#########################')
print("Echo frequency = {0} MHz".format(pars[1]))
print("Echo time = {0} us".format(pars[2]))
# print('Covariance Matrix')
# print(cov)

ram_t = np.round(pars[2], 2)
ram_f = np.round(pars[1], 5)

plt.figure()
plt.plot(t_list_us, I, ".")
plt.plot(t_list_us, ramsey_fit(t_list_us,*pars))
plt.xlabel('t (us)')
plt.ylabel("Echo Amplitude")
plt.title("Echo : Echo time = {0} us; Echo frequency = {1} MHz".format(ram_t, ram_f))
plt.grid()
plt.show()

if save_data:
    file_saver_(np.transpose([t_list_us, np.abs(sig), I, Q]),file_name=__file__, master_folder=ExpName, header_string="Time (us), MAgnitude, I, Q")
