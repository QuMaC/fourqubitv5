from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import *
from Helper_Functions.analysis_functions import *

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
t_min = 16//4   #ns
t_max = 17500//4
dt = 60//4 #steps of 4ns
t_list = np.arange(t_min, t_max, dt)
#
# p_min = 0
# p_max = 2
# dp = 0.01
# p_list = np.arange(p_min, p_max, dp)

# q_no = 5
c_no, t_no = 3, 4

# qe = f"q{q_no}"
# q_stark = f'stark_{q_no}'
# qe_12 = f"q12_{q_no}"
# rr = f"rr{q_no}"
if c_no in control_qubits:
    qe_cr = f"cr_c{c_no}t{t_no}"
    qe_ac = f"cr_ac_c{c_no}t{t_no}"
else:
    qe_cr = f"cr_c{t_no}t{c_no}"
    qe_ac = f"cr_ac_c{t_no}t{c_no}"


qe_c, qe_t = f"q{c_no}", f"q{t_no}"
rr_c, rr_t = f"rr{c_no}", f"rr{t_no}"

qe = qe_t
rr = rr_t

qubit_IF = q_IF[qe[-1]]

out = adc_mapping[rr]
ro_len = ro_len_clk[qe[-1]]
ZZ_shift = CrossKerr[qe[-1]] * 1e-6

det_bare = 0.5
det = det_bare - ZZ_shift  # in MHz

if simulate:
    rep_rate_clk = 100
else:
    rep_rate_clk = 250000

dem = demarcations[qe[-1]]
wait_rr = 16
pi_len = pi_len_ns[qe[-1]]
piby2_len = piby2_len_ns[qe[-1]]


with program() as ramsey:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    t = declare(int)

    update_frequency(qe, qubit_IF + det * u.MHz)
    with for_(n, 0, n < 1000, n + 1):
        with for_(t, t_min, t < t_max, t + dt):
            if simulate:
                assign(t, 100)

            # reset_frame(rr)
            cooldown(time=rep_rate_clk)
            reset_frame(qe)
            # reset_frame(qe_cr)
            # play_X90(qe)
            play('X90', qe)

            ZXby2_echo_AC(qe_cr, qe_ac, qe_c, qe_t)
            wait(t, qe)
            # wait(284, qe_t)
            # Hadamard(qe)
            # align(qe, q_stark)
            # align()
            # play('const'*amp(1), q_stark)

            # ramp_to_zero(q_stark)
            # align(q_stark, qe)

            # ZXby2_echo_AC(qe_cr, qe_ac, qe_c, qe_t)
            # play_X90(qe)
            play('X90', qe)
            align()
            # Hadamard(qe)
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
    sig = I + 1j*Q
    plt.clf()
    # plt.plot(4e-3*t_list, Q, marker=".", label="Q")
    plt.plot(4e-3*t_list, I, marker=".", label="I")
    plt.xlabel("Time (us)")
    plt.ylabel("Ramsey Amplitude")
    plt.title("Ramsey N = {0}".format(plot_no*20))
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.grid()
    plt.legend()
    plt.pause(1)
    plot_no+=1


I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

t_list_us = 4e-3*t_list


def ramsey_fit(t, A, f, d, p, c):

    return A * np.exp(-t/d) * np.sin(2*np.pi*f*t + p) + c


res_I, pcov_i, init_i = ramsey_fitting(t_list_us, I)  # A, tau, offset, freq, phi

# pars, cov = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=I, p0=[1e-3, det + ZZ_shift, 1, np.pi/2, np.mean(I)], bounds=(-np.inf, np.inf), maxfev=10000)

ram_t = np.round(res_I[1], 2)
ram_f = np.round(res_I[3], 5)

pars = [res_I[0], res_I[3], res_I[1], res_I[4], res_I[2]]

print('#########################')
print('### Fitted Parameters ###')
print('#########################')
print(f"Ramsey frequency = {ram_f} MHz")
print(f"Ramsey time = {ram_t} us")
# print('Covariance Matrix')
# print(cov)

plt.figure()
plt.plot(t_list_us, I, ".")
plt.plot(t_list_us, ramsey_fit(t_list_us, *pars))
plt.xlabel('t (us)')
plt.ylabel("Ramsey Amplitude")
plt.title(f"Ramsey : Ramsey time = {ram_t:.2f} us; Ramsey frequency = {ram_f:.3f} MHz")
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
plt.grid()
plt.show(block=False)

if update_pars:
    del_f = det_bare - ram_f

    IF_file = open('../Configuration_Files/System_Parameters/q_IF.json', 'r+')

    q_IF_json = json.load(IF_file)
    IF_file.close()

    q_IF_json[str(q_no)] = np.round(q_IF_json[str(q_no)] + del_f, 3)
    IF_file = open('../Configuration_Files/System_Parameters/q_IF.json', 'r+')
    json.dump(q_IF_json, IF_file, indent=6)
    IF_file.close()

if save_data:
    file_saver_(np.transpose([t_list_us, I, Q]),file_name=__file__, suffix= qe, master_folder=ExpName, header_string="Time (us), MAgnitude, I, Q")
#
# with open('ramsey_cache_json.json','w') as f:
#     json.dump({'det': ram_f}, f)
#     f.close()