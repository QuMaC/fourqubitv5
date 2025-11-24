from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import measure_macro, cooldown

simulate = False
save_data = False
###################
# The QUA program #
###################
t_min = 4//4   #ns
t_max = 50000//4
dt = 50//4 #steps of 4ns
t_list = np.arange(t_min, t_max, dt)

q_no = 6
qubit_IF = q_IF[str(q_no)]
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(q_no)]
ZZ_shift = CrossKerr[str(q_no)]*1e-6


if simulate:
    rep_rate_clk = 100
else:
    rep_rate_clk = 250000

dem = demarcations[str(q_no)]
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
piby2_len = piby2_len_ns[str(q_no)]


with program() as ramsey:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    t = declare(int)

    with for_(n, 0, n < 10000, n + 1):
        with for_(t, t_min, t < t_max, t + dt):
            # if simulate:
            #     assign(t, 100)

            # wait(rep_rate_clk - t - 2*piby2_len - wait_rr - ro_len, qe)
            cooldown(time=rep_rate_clk, active_reset=False,
                     qe=qe, qe_12=qe_12, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)
            play_X180(qe)
            # play("const" * amp(0.05), qe)
            wait(t, qe)
            measure_macro(qe, rr, out, I, Q, pi_12=False)

            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('I')
        Q_st.buffer(len(t_list)).average().save('Q')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip,cluster_name=cluster_name)

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
plt.title("Ramsey")
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)

plot_no = 1
while res_handles.is_processing():

    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    sig = I + 1j*Q
    plt.clf()
    # plt.plot(4e-3*t_list, Q, marker=".", label="Q")
    plt.plot(4e-3*t_list, I, marker=".", label="I")
    plt.xlabel("Time (us)")
    plt.ylabel("Amplitude")
    # plt.title("Ramsey N = {0}".format(plot_no*20))
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.grid()
    plt.legend()
    plt.pause(1)
    plot_no+=1


I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

t_list_us = 4e-3*t_list


def t1_fit(t, A, d, c):

    return A * np.exp(-t/d) + c


pars, cov = curve_fit(f=t1_fit, xdata=t_list_us, ydata=I, p0=[1e-3, 5, 0], bounds=(-np.inf, np.inf), maxfev=10000)


print('#########################')
print('### Fitted Parameters ###')
print('#########################')
print("T1 time = {0} us".format(pars[1]))
# print('Covariance Matrix')
# print(cov)

t1 = np.round(pars[1], 2)

plt.figure()
plt.plot(t_list_us, I, ".")
plt.plot(t_list_us, t1_fit(t_list_us,*pars))
plt.xlabel('t (us)')
plt.ylabel("Amplitude")
plt.title("T1 : T1 = {0} us".format(t1))
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
plt.grid()
plt.show()

if save_data:
    file_saver_(np.transpose([t_list_us, np.abs(sig), I, Q]),file_name=__file__, master_folder=ExpName, header_string="Time (us), MAgnitude, I, Q")
