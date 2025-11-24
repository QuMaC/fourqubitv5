from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import measure_macro, cooldown, Hadamard

simulate = False
save_data = True
pi_12 = True
update_pars = False
###################
# The QUA program #
###################
# t_min = 16//4   #ns
# t_max = 10000//4
# dt = 16//4 #steps of 4ns
# t_list = np.arange(t_min, t_max, dt)

# t_min = 16//4   #ns
# t_max = 17500//4
# dt = 60//4 #steps of 4ns
# t_list = np.arange(t_min, t_max, dt)

p_min = 0
p_max = 2
dp = 0.01
p_list = np.arange(p_min, p_max, dp)

q_no = 5
qubit_IF = q_IF[str(q_no)]
qe = f"q{q_no}"
q_stark = f'stark_{q_no}'
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(q_no)]
ZZ_shift = CrossKerr[str(q_no)] * 1e-6

det_bare = 1
det = det_bare - ZZ_shift  # in MHz

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
    # t = declare(int)
    p = declare(float)

    # update_frequency(qe, qubit_IF + det * u.MHz)
    # frame_rotation_2pi(0.36, qe)
    with for_(n, 0, n < 1000, n + 1):

        with for_(p, p_min, p < p_max, p + dp):

            # if simulate:
            #     assign(t, 100)
            # reset_frame(qe)
            # reset_frame(rr)
            cooldown(time=rep_rate_clk)
            # play_X90(qe)
            Hadamard(qe)
            # align(qe, q_stark)
            # play('const'*amp(1), q_stark)
            # wait(t, qe)
            frame_rotation_2pi(p, qe)
            # ramp_to_zero(q_stark)
            # align(q_stark, qe)
            # play_X90(qe)
            Hadamard(qe)
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(p_list)).average().save('I')
        Q_st.buffer(len(p_list)).average().save('Q')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
if simulate:
    # qmm = QuantumMachinesManager()
    job = qmm.simulate(config, ramsey, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con3.plot()
    plt.show(block=False)
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
    sig = I + 1j * Q
    plt.clf()
    # plt.plot(4e-3*p_list, Q, marker=".", label="Q")
    plt.plot(p_list, I, marker=".", label="I")
    plt.xlabel("phase")
    plt.ylabel("Ramsey Amplitude")
    plt.title("Ramsey N = {0}".format(plot_no * 20))
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.grid()
    plt.legend()
    plt.pause(1)
    plot_no += 1

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

p_list_us = p_list


def ramsey_fit_phase(t, A, ph, c):
    return A * np.sin(t*2*np.pi + ph) + c


pars, cov = curve_fit(f=ramsey_fit_phase, xdata=p_list_us, ydata=I, p0=[(max(I) - min(I)) / 2, np.pi / 2, np.mean(I)],
                      bounds=(-np.inf, np.inf), maxfev=10000)

ram_p = np.round(pars[1], 5)

print('#########################')
print('### Fitted Parameters ###')
print('#########################')
print(f"Ramsey phase = {ram_p:.3f}")
# print('Covariance Matrix')
# print(cov)

plt.figure()
plt.plot(p_list_us, I, ".")
plt.plot(p_list_us, ramsey_fit_phase(p_list_us, *pars))
plt.xlabel('phase')
plt.ylabel("Ramsey Amplitude")
plt.title(f"Ramsey phase = {ram_p:.3f} MHz")
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
plt.grid()
plt.show(block=False)

if save_data:
    file_saver_(np.transpose([p_list_us, I, Q]), file_name=__file__, suffix=qe, master_folder=ExpName,
                header_string="Time (us), MAgnitude, I, Q")
