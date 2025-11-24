from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import fetching_tool, progress_counter
from Helper_Functions.analysis_functions import fit_cos
from Configuration_Files.configuration_4qubitsv3 import *
import json
from Helper_Functions.macros import *
from matplotlib import pyplot as plt
from qualang_tools.analysis.discriminator import two_state_discriminator
from scipy.optimize import curve_fit

qmm = QuantumMachinesManager(host=qm_ip, cluster_name=cluster_name)
q_no = 5
qubit_IF = q_IF[str(q_no)]
ZZ_shift = CrossKerr[str(q_no)] * 1e-6

qe = f"q{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]

ro_len = ro_len_clk[str(q_no)]
rep_rate_clk = 250000
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]

pi_12 = False
drag = True
type = ""
pulse_type = ""
if drag:
    pulse_type = f"{type}d_"

save_data = True
discriminate = False
simulate = False
lsb = False

scale = 0.1

ro_len = ro_len_clk[str(q_no)]
###################
# The QUA program #
###################

# ---------------
det = 0.0  # in MHz
n_avg = 1e4
wait_init = 250000  # in clocks ~ 1 ms

# combi_pulse = True


# I_eq = rabi_levels[f'{q_no}']['I_eq']
# rabi_amp = rabi_levels[f'{q_no}']['rabi_amp']

############## Define the pulses inside functions. Helpful for combi-pulses ##############
def play_X180(qe):
    UCP5b_X180(qe)
    # BB1_X180(qe)
    # play("d_X180", qe)


def play_Y180(qe):
    UCP5b_Y180(qe)
    # BB1_Y180(qe)
    # play("d_Y180", qe)


def play_X90(qe):
    BB1_X90(qe)
    # play("d_X90", qe)


def play_Y90(qe):
    BB1_Y90(qe)
    # play("d_Y90", qe)




# All XY sequences. The sequence names must match corresponding operation in the config
sequence = [  # based on https://rsl.yale.edu/sites/default/files/physreva.82.pdf-optimized_driving_0.pdf
    ("I", "I"),
    (f"{pulse_type}X180", f"{pulse_type}X180"),
    (f"{pulse_type}Y180", f"{pulse_type}Y180"),
    (f"{pulse_type}X180", f"{pulse_type}Y180"),
    (f"{pulse_type}Y180", f"{pulse_type}X180"),
    (f"{pulse_type}X90", "I"),
    (f"{pulse_type}Y90", "I"),
    (f"{pulse_type}X90", f"{pulse_type}Y90"),
    (f"{pulse_type}Y90", f"{pulse_type}X90"),
    (f"{pulse_type}X90", f"{pulse_type}Y180"),
    (f"{pulse_type}Y90", f"{pulse_type}X180"),
    (f"{pulse_type}X180", f"{pulse_type}Y90"),
    (f"{pulse_type}Y180", f"{pulse_type}X90"),
    (f"{pulse_type}X90", f"{pulse_type}X180"),
    (f"{pulse_type}X180", f"{pulse_type}X90"),
    (f"{pulse_type}Y90", f"{pulse_type}Y180"),
    (f"{pulse_type}Y180", f"{pulse_type}Y90"),
    (f"{pulse_type}X180", "I"),
    (f"{pulse_type}Y180", "I"),
    (f"{pulse_type}X90", f"{pulse_type}X90"),
    (f"{pulse_type}Y90", f"{pulse_type}Y90"),
]


# Pulses are all pair-wise combinations of I, X180, Y180, X90, Y90
label_seq = [  # for aesthetic purposes
    "IdId",
    "XpXp",
    "YpYp",
    "XpYp",
    "YpXp",
    "X9Id",
    "Y9Id",
    "X9Y9",
    "Y9X9",
    "X9Yp",
    "Y9Xp",
    "XpY9",
    "YpX9",
    "X9Xp",
    "XpX9",
    "Y9Yp",
    "YpY9",
    "XpId",
    "YpId",
    "X9X9",
    "Y9Y9"
]


# All XY macro generating the pulse sequences from a python list.
def run_allXY(pulses, amp_scaling, wait_init, qe, rr, out):
    """
    Generate a QUA sequence based on the two operations written in pulses. Used to generate the all XY program.
    **Example:** I, Q = allXY(['I', 'Y90'])

    :param pulses: tuple containing a particular set of operations to play. The pulse names must match corresponding
        operations in the config except for the identity operation that must be called 'I'.
    :return: two QUA variables for the 'I' and 'Q' quadratures measured after the sequence.
    """
    I_xy = declare(fixed)
    Q_xy = declare(fixed)

    wait(wait_init, qe)
    play(pulses[0] * amp(amp_scaling[0]), qe)
    wait(4, qe)  # added delay to reduce reflections
    play(pulses[1] * amp(amp_scaling[1]), qe)
    measure_macro(qe, rr, out, I_xy, Q_xy, pi_12=pi_12)

    return I_xy, Q_xy

def run_allXY_new(pulses, amp_scaling, wait_init, qe, rr, out):
    """
    Generate a QUA sequence based on the two operations written in pulses. Used to generate the all XY program.
    **Example:** I, Q = allXY(['I', 'Y90'])

    :param pulses: tuple containing a particular set of operations to play. The pulse names must match corresponding
        operations in the config except for the identity operation that must be called 'I'.
    :return: two QUA variables for the 'I' and 'Q' quadratures measured after the sequence.
    """
    I_xy = declare(fixed)
    Q_xy = declare(fixed)

    wait(wait_init, qe)
    # play(pulses[0] * amp(amp_scaling[0]), qe)
    if 'X180' in pulses[0]:
        play_X180(qe)
    elif 'X90' in pulses[0]:
        play_X90(qe)
    elif 'Y180' in pulses[0]:
        play_Y180(qe)
    elif 'Y90' in pulses[0]:
        play_Y90(qe)

    wait(20, qe)  # added delay to reduce reflections
    # play(pulses[1] * amp(amp_scaling[1]), qe)
    if 'X180' in pulses[1]:
        play_X180(qe)
    elif 'X90' in pulses[1]:
        play_X90(qe)
    elif 'Y180' in pulses[1]:
        play_Y180(qe)
    elif 'Y90' in pulses[1]:
        play_Y90(qe)

    measure_macro(qe, rr, out, I_xy, Q_xy, pi_12=pi_12)

    return I_xy, Q_xy


###################
# The QUA program #
###################
def qua_allxy(opt_amp_dict, n_avg, wait_init, qe, rr, out):
    with program() as ALLXY:
        n = declare(int)
        n_st = declare_stream()

        Ixy_st = [declare_stream() for _ in range(21)]
        Qxy_st = [declare_stream() for _ in range(21)]

        update_frequency(qe, qubit_IF + det * u.MHz)
        with for_(n, 0, n < n_avg, n + 1):
            reset_frame(qe)
            wait(16, qe)

            for i in range(len(sequence)):
                # Scale the pulse amplitudes in the sequences
                pulses = sequence[i]
                amp_scaling = [opt_amp_dict[pulses[0]], opt_amp_dict[pulses[1]]]
                Ixy, Qxy = run_allXY_new(pulses, amp_scaling, wait_init, qe, rr, out)
                save(Ixy, Ixy_st[i])
                save(Qxy, Qxy_st[i])
            save(n, n_st)

        with stream_processing():

            for j in range(21):
                Ixy_st[j].average().save(f"Ixy_{j}")
                Qxy_st[j].average().save(f"Qxy_{j}")
            n_st.save("iteration")
    return ALLXY


opt_amp_dict = {"I": 1,
                f"{pulse_type}X180": 1,
                f"{pulse_type}Y180": 1,
                f"{pulse_type}X90": 1,
                f"{pulse_type}Y90": 1}


# Rabi :(((

# ----------------------------
# Time-Rabi to find the levels
# ----------------------------

def rabi_fit(t, A, f, d, p, c):
    return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c


t_min_ns = pi_len_ns[f"{q_no}"]
t_max_ns = 3 * 1200
dt_ns = 4 * 3  # minimum 4ns
n_avg_rabi = 300
rabi_pi_amp = 0.1

t_min = int(t_min_ns / 4)  # in clocks
t_max = int(t_max_ns / 4)
dt = int(dt_ns / 4)
t_list = np.arange(t_min, t_max, dt)

with program() as rabi:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    t = declare(int)
    n_st = declare_stream()

    with for_(n, 0, n < n_avg_rabi, n + 1):
        with for_(t, t_min, t < t_max + 0.1, t + dt):
            wait(rep_rate_clk - t - wait_rr - ro_len)
            # play("const"*amp(rabi_pi_amp), qe, t)
            play(f"{pulse_type}X180"*amp(scale), qe, t)
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)

            save(I, I_st)
            save(Q, Q_st)
        save(n, n_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('I')
        Q_st.buffer(len(t_list)).average().save('Q')
        n_st.save("iteration")

# ------------------------
#       Execute on the OPX
# ------------------------
qm1 = qmm.open_qm(config)

job = qm1.execute(rabi)
# Get results from QUA program
results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

# Live plotting
t_list = 4 * t_list
fig = plt.figure()
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

while results.is_processing():
    # Fetch results
    I, Q, iteration = results.fetch_all()
    progress_counter(iteration, n_avg, start_time=results.get_start_time())
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
sig = I + 1j * Q

try:
    res_I = fit_cos(t_list[20:], I[20:])
        # curve_fit(f=rabi_fit, xdata=t_list, ydata=I, p0=[3e-3, 0.02, 100, 0, 1e-5], bounds=(-np.inf, np.inf),
        #                   maxfev=2000)
except RuntimeError:
    res_I = fit_cos(t_list[20:], I[20:])
    # pars, cov = curve_fit(f=rabi_fit, xdata=t_list, ydata=I, p0=[3e-3, 0.01, 500, 0, 1e-5], bounds=(-np.inf, np.inf),
    #                       maxfev=2000)
# init_pars = p0 = [A, f, d, p, c]
#
# print('######################### \n### Fitted Parameters ### \n######################### ')
# print(f"Rabi frequency = {np.round(1e3*pars[1],2)} MHz")
# print(f"Pi pulse = {np.round(0.5/pars[1],3)} ns")
# print(f"Rabi amplitude = {pars[0]}")
# print(f"Rabi decay constant = {pars[2]*1e-3} us")




I_eq = res_I['offset']
rabi_amp = abs(res_I['amp'])
I_g = I_eq - rabi_amp
I_e = I_eq + rabi_amp

# print("##########")
# print(f"Rabi DC offset = {I_eq}")
# print(f"Rabi amp = {rabi_amp}")
# print(f"In arbitrary units \n Ground state [-1] = {I_g} \n Equator [0] = {I_eq} \n Excited state [+1] = {I_e}")


# Done with Rabi :)))


# I_g = I_eq - rabi_amp
# I_e = I_eq + rabi_amp

ideal_set_z = [-1] * 5 + [0] * 12 + [1] * 4
ideal_set_I = [I_g] * 5 + [I_eq] * 12 + [I_e] * 4

qm = qmm.open_qm(config)
job = qm.execute(qua_allxy(opt_amp_dict, n_avg, wait_init, qe, rr, out))

data_list = []
for j in range(21):
    data_list.append(f"Ixy_{j}")
    data_list.append(f"Qxy_{j}")
data_list.append("iteration")

# Get results from QUA program
results = fetching_tool(job, data_list=data_list, mode="live")

# Live plotting
plt.ion()
fig, ax = plt.subplots(2)
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

fig.suptitle(f'ALLXY Diagnosis on Q{q_no}')
lines = []
Iz = ["I", "z"]
cols = ["red", "blue"]
ideal_sets = [ideal_set_I, ideal_set_z]

for i in range(2):

    lines.append(ax[i].plot([0] * 21, marker='o', linestyle=':', markersize=5, c=cols[i])[0])
    if i > 0:
        lines.append(
            ax[i].plot(ideal_sets[i], marker='x', linestyle='--', linewidth=0.1, markersize=2, c=cols[-i - 1])[0])

    ax[i].set_title(Iz[i])
    ax[i].set_ylabel(f"{Iz[i]} Amplitude")
    ax[i].grid()
    ax[i].legend()

ax[0].set_xticks(ticks=range(21), labels=[str(el) for el in label_seq], rotation=90)
ax[1].set_xticks(ticks=range(21), labels=[str(el) for el in label_seq], rotation=90)
ax[1].set_xlabel('XY Pairs')

while results.is_processing():

    res_list = results.fetch_all()
    iteration = res_list[-1]
    res_list = res_list[:-1]

    progress_counter(iteration, n_avg, start_time=results.get_start_time())


    Ixy = []
    Qxy = []

    for j in range(21):
        Ixy.append(res_list[2 * j])
        Qxy.append(res_list[2 * j + 1])

    I_xy = np.array(Ixy)
    Q_xy = np.array(Qxy)

    z_g, z_eq, z_e = -1.0, 0.0, 1.0
    z_xy = (I_xy - I_eq) / rabi_amp

    data = [I_xy, z_xy]
    refs = [I_g, I_eq, I_e, z_g, z_eq, z_e]

    for i in range(2):
        lines[2 * i].set_ydata(data[i])

        # ax[i].axhline(y=refs[3*i], color=cols[-i-1], linewidth=0.1, linestyle='--')
        # ax[i].axhline(y=refs[3*i+1], color=cols[-i-1], linewidth=0.1, linestyle='--')
        # ax[i].axhline(y=refs[3*i+2], color=cols[-i-1], linewidth=0.1, linestyle='--')

        ax[i].relim()
        ax[i].autoscale_view()
        fig.set_tight_layout(True)
        fig.canvas.draw()
        fig.canvas.flush_events()
    plt.show()
    plt.pause(1)

res_list = results.fetch_all()

qm.close()

Ixy = []
Qxy = []

for j in range(21):
    Ixy.append(res_list[2 * j])
    Qxy.append(res_list[2 * j + 1])

I_xy = np.array(Ixy)
Q_xy = np.array(Qxy)

z_g, z_eq, z_e = -1.0, 0.0, 1.0
z_xy = (I_xy - I_eq) / rabi_amp

plt.figure()
plt.plot(I_xy, marker='o', linestyle=':', markersize=5, c='red')
plt.plot(ideal_set_I, marker='x', linestyle='--', linewidth=0.1, markersize=2, c='blue')

# plt.axhline(y=I_g, color='b', linewidth=0.1, linestyle='--')
# plt.axhline(y=I_eq, color='b', linewidth=0.1, linestyle='--')
# plt.axhline(y=I_e, color='b', linewidth=0.1, linestyle='--')

plt.xticks(ticks=range(21), labels=[str(el) for el in label_seq], rotation=90)

plt.xlabel('XY Pairs')
plt.ylabel('I quadrature [a.u.]')
plt.title(f"All XY Calibration on Qubit {q_no}")
plt.grid()
plt.tight_layout()
plt.show()

plt.figure()
plt.plot(z_xy, marker='o', linestyle=':', markersize=5, c='blue')
plt.plot(ideal_set_z, marker='x', linestyle='--', linewidth=0.1, markersize=2, c='red')

# plt.axhline(y=z_g, color='r', linewidth=0.1, linestyle='--')
# plt.axhline(y=z_eq, color='r', linewidth=0.1, linestyle='--')
# plt.axhline(y=z_e, color='r', linewidth=0.1, linestyle='--')

plt.xticks(ticks=range(21), labels=[str(el) for el in label_seq], rotation=90)

plt.xlabel('XY Pairs')
plt.ylabel('Z Projection')
plt.title(f"All XY Calibration on Qubit {q_no}")
plt.grid()
plt.tight_layout()
plt.show()

if save_data is True:
    file_saver_(I_xy, file_name=__file__,
                master_folder=ExpName, header_string="I_values", suffix="with_DRAG", time_stamp=True)
    file_saver_(z_xy, file_name=__file__,
                master_folder=ExpName, header_string="Prob_values", suffix="prob_with_DRAG", time_stamp=True)
