"""
An experiment to calibrate the DRAG coefficient: drag_coef
This protocol is described in Reed's thesis (Fig. 5.8) https://rsl.yale.edu/sites/default/files/files/RSL_Theses/reed.pdf
This protocol was also cited in: https://doi.org/10.1103/PRXQuantum.2.040202
"""
from qm.qua import *
from qm import QuantumMachinesManager
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import fetching_tool, progress_counter

from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.macros import *
import json
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
from qm import SimulationConfig
from qualang_tools.loops import from_array
from scipy.optimize import curve_fit

from qualang_tools.units import unit
u = unit()

simulate = False

type = ""

q_no = 6
qe = f"q{q_no}"
rr = f"rr{q_no}"
con = f"con{dac_mapping[qe][0]}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]

pi_12 = True
drag = True
pulse_type = ""
if drag:
    pulse_type = f"{type}d_"

# Set the drag_dict = 1.0 in the configuration
# drag_coef = 1
drag_coef = eval(f"{type}drag_dict")[f"{q_no}"]
n_avg = 1e4  # DRAG averaging for better calibration

# ----------------------------
# Time-Rabi to find the levels
# ----------------------------

t_min_ns = pi_len_ns[f"{q_no}"]
t_max_ns = 6*1200
dt_ns = 4*6 # minimum 4ns
n_avg_rabi = 300
rabi_pi_amp = 1.0  # 0.1

t_min = int(t_min_ns/4) # in clocks
t_max = int(t_max_ns/4)
dt = int(dt_ns/4)
t_list = np.arange(t_min, t_max, dt)

rep_rate_clk = 250000
wait_rr = 16

with program() as rabi:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    t = declare(int)

    with for_(n, 0, n < n_avg_rabi, n + 1):
        with for_(t, t_min, t < t_max + 0.1, t + dt):
            wait(rep_rate_clk - t - wait_rr - ro_len)
            # play("const"*amp(rabi_pi_amp), qe, t)
            play(f"{pulse_type}X180", qe, t)
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('I')
        Q_st.buffer(len(t_list)).average().save('Q')


qmm = QuantumMachinesManager(qm_ip)

# ------------------------
#       Execute on the OPX
# ------------------------
qm1 = qmm.open_qm(config)

job = qm1.execute(rabi)
# Get results from QUA program
results = fetching_tool(job, data_list=["I", "Q"], mode="live")

# Live plotting
t_list = 4 * t_list
fig = plt.figure()
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

while results.is_processing():
    # Fetch results
    I, Q = results.fetch_all()
    sig = I + 1j * Q

    plt.cla()
    plt.plot(t_list, Q, marker='.', label="Q")
    plt.plot(t_list, I, marker='.', label="I")
    plt.xlabel("Time (ns)")
    plt.ylabel("Rabi Amplitude")
    plt.title(f"Time Rabi on Qubit {q_no}")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.pause(0.25)
    plt.show()

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

qm1.close()

# ############
# # analysis #
# ############
sig = I + 1j*Q

def rabi_fit(t, A, f, d, p, c):

    return A * np.exp(-t/d) * np.sin(2*np.pi*f*t + p) + c

pars, cov = curve_fit(f=rabi_fit, xdata=t_list, ydata=I, p0=[3e-3,0.01,100,0, 1e-5], bounds=(-np.inf, np.inf), maxfev=2000)
# init_pars = p0 = [A, f, d, p, c]

print('######################### \n### Fitted Parameters ### \n######################### ')
print(f"Rabi frequency = {np.round(1e3*pars[1],2)} MHz")
print(f"Pi pulse = {np.round(0.5/pars[1],3)} ns")
print(f"Rabi amplitude = {pars[0]}")
print(f"Rabi decay constant = {pars[2]*1e-3} us")

I_eq = pars[4]
rabi_amp = abs(pars[0])
I_g = I_eq - rabi_amp
I_e = I_eq + rabi_amp

print("##########")
print(f"Rabi DC offset = {I_eq}")
print(f"Rabi amp = {rabi_amp}")
print(f"In arbitrary units \n Ground state [-1] = {I_g} \n Equator [0] = {I_eq} \n Excited state [+1] = {I_e}")



###################
# The QUA program #
###################

best_qubit_T1 = 40 * u.us
cooldown_time = int(5 * best_qubit_T1 // 4) # in clock cycles

a_min = -1.0
a_max = 1.0
da = 0.01
amps = np.arange(a_min, a_max + da / 2, da)  # + da/2 to add a_max to amplitudes

with program() as drag:
    n = declare(int)
    n_st = declare_stream()
    a = declare(fixed)
    I = declare(fixed)
    Q = declare(fixed)
    I1_st = declare_stream()
    Q1_st = declare_stream()
    I2_st = declare_stream()
    Q2_st = declare_stream()

    with for_(n, 0, n < n_avg, n + 1):
        with for_(*from_array(a, amps)):
            play(f"{type}d_X180" * amp(1, 0, 0, a), qe)
            play(f"{type}d_Y90" * amp(a, 0, 0, 1), qe)

            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

            save(I, I1_st)
            save(Q, Q1_st)
            wait(cooldown_time, rr)
            align()

            play(f"{type}d_Y180" * amp(a, 0, 0, 1), qe)
            play(f"{type}d_X90" * amp(1, 0, 0, a), qe)

            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

            save(I, I2_st)
            save(Q, Q2_st)
            wait(cooldown_time, rr)
        save(n, n_st)
    
    with stream_processing():
        I1_st.buffer(len(amps)).average().save("I1")
        Q1_st.buffer(len(amps)).average().save("Q1")
        I2_st.buffer(len(amps)).average().save("I2")
        Q2_st.buffer(len(amps)).average().save("Q2")
        n_st.save("Iteration")

#####################################
#  Open Communication with the QOP  #
#####################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

if simulate:
    simulation_config = SimulationConfig(duration=1000)  # in clock cycles
    job = qmm.simulate(config, drag, simulation_config)
    samples = job.get_simulated_samples()
    # plot all ports:
    sim_output = getattr(samples, con)
    sim_output.plot()
    plt.legend("")
    plt.show()
    raise(Halted)

qm2 = qmm.open_qm(config)

job = qm2.execute(drag)
# Get results from QUA program
results = fetching_tool(job, data_list=["I1", "I2", "Iteration"], mode="live")

# Live plotting
fig = plt.figure()
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

while results.is_processing():
    # Fetch results
    I1, I2, iter = results.fetch_all()

    # Rescale results
    I1 = np.array(I1)
    I2 = np.array(I2)
    I_pair = np.array([I1, I2])
    z_pair = (I_pair - I_eq) / rabi_amp
    state_pair = (z_pair + 1) / 2

    # Progress bar
    progress_counter(iter, n_avg, start_time=results.get_start_time())
    # Plot results
    plt.cla()
    plt.plot(amps * drag_coef, state_pair[0], label="x180y90")
    plt.plot(amps * drag_coef, state_pair[1], label="y180x90")
    plt.xlabel("DRAG coefficient")
    plt.ylabel("State probability")
    plt.legend()
    plt.tight_layout()
    plt.pause(0.5)
    plt.show()

# Fetch results
I1, I2, iter = results.fetch_all()

# Rescale results
I1 = np.array(I1)
I2 = np.array(I2)
I_pair = np.array([I1, I2])
z_pair = (I_pair - I_eq) / rabi_amp
state_pair = (z_pair + 1) / 2

qm2.close()

# Analysis

def linear_fit(x, m, c):
    return m * x + c

pars1, cov1 = curve_fit(f=linear_fit, xdata=amps, ydata=state_pair[0], p0=[-0.4, 0.5], bounds=(-np.inf, np.inf), maxfev=2000)
pars2, cov2 = curve_fit(f=linear_fit, xdata=amps, ydata=state_pair[1], p0=[0.4, 0.5], bounds=(-np.inf, np.inf), maxfev=2000)

opt_drag_coef = np.round((pars1[1] - pars2[1])/(pars2[0] - pars1[0]), 5)

print(f"The optimal DRAG coefficient is {opt_drag_coef}")

plt.figure()

plt.plot(amps * drag_coef, state_pair[0])
plt.plot(amps * drag_coef, state_pair[1])
plt.plot(amps * drag_coef, linear_fit(amps, *pars1), label="x180y90")
plt.plot(amps * drag_coef, linear_fit(amps, *pars2), label="y180x90")
plt.axhline(y=0.5, linestyle="--")
plt.axvline(x=opt_drag_coef, linestyle="--")

plt.xlabel("DRAG Coefficient")
plt.ylabel("State probability")
plt.title(f"Q{q_no} DRAG alpha = {opt_drag_coef}")
plt.legend()

plt.tight_layout()
plt.show()

drag_file = open(f'./Pulse_Calibrations/{type}drag_dict.json', 'r+')

drag_dict = json.load(drag_file)

drag_dict[str(q_no)] = opt_drag_coef

drag_file.close()

drag_file = open(f'./Pulse_Calibrations/{type}drag_dict.json', 'w')
json.dump(drag_dict, drag_file, indent=6)
drag_file.close()