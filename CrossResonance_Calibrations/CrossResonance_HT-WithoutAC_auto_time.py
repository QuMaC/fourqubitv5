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

simulate = False
save_data = True
time_stamp = False
Echo = True
update_calib = False
###################
# The QUA program #
###################

t_min_ns = 16
t_max_ns = 1000
dt_ns = 4  # minimum 4ns
t_min = int(t_min_ns / 4)
t_max = int(t_max_ns / 4)
dt = int(dt_ns / 4)
t_list = np.arange(t_min, t_max, dt)

c_no, t_no = 5, 2

qe_c = f"q{c_no}"
rr_c = f"rr{c_no}"
out_c = adc_mapping[rr_c]
qe_t = f"q{t_no}"
rr_t = f"rr{t_no}"
out_t = adc_mapping[rr_t]
pi_12 = True

cr_elem = f"cr_c{c_no}t{t_no}"
p_cr = cr_phase[cr_elem]
a_cr = cr_amp[cr_elem]

wait_init = 250000
wait_t = 4
wait_rr = 16

n_avg = 200

echo_p = True

if simulate:
    wait_init = 100

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

#############
# execution #
#############
job = HT_setPhase(qmm, cr_elem, p_cr, t_min, t_max, dt, n_avg, wait_init, wait_t,
                  wait_rr, qe_c, qe_t, pi_12, simulate, echo_p, a_cr)

results = fetching_tool(job, data_list=["I_t_avg", "Q_t_avg", "I_c_avg",
                                            "Q_c_avg", "I_rabi_avg", "Q_rabi_avg",
                                            "iteration"], mode="live")

# res_handles = job.result_handles
# It_handle = job.result_handles.get("I_t_avg")
# Qt_handle = job.result_handles.get("Q_t_avg")
# Ic_handle = job.result_handles.get("I_c_avg")
# Qc_handle = job.result_handles.get("Q_c_avg")
# Irabi_handle = job.result_handles.get("I_rabi_avg")
# Qrabi_handle = job.result_handles.get("Q_rabi_avg")
#
# # job.result_handles.wait_for_all_values()
#
# It_handle.wait_for_values(1)
# Qt_handle.wait_for_values(1)
# Ic_handle.wait_for_values(1)
# Qc_handle.wait_for_values(1)
# Irabi_handle.wait_for_values(1)
# Qrabi_handle.wait_for_values(1)

# ========== PLOT INIT SETTINGS===================
t_list_ns = 2 * 4 * t_list
plt.ion()
plt.rcParams["figure.figsize"] = (15, 10)
fig, ax = plt.subplots(3, 3, sharex=True, sharey='row')
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
# fig,ax = plt.subplots(3,3,sharex=True)
fig.suptitle("Cross Resonance Tomography", fontsize=15)
axbig = fig.add_subplot(111, frameon=False)
axbig.set_xlabel("Time (us)", labelpad=20, fontsize=15)
axbig.set_ylabel("Amplitude", labelpad=50, fontsize=15)
axbig.set_xticks([])
axbig.set_yticks([])
lines = []
tc = ["Control 0", "Control 1"]
labels = ["Z", "Y", "X"]
for i in range(2):
    # ax[i,0].set_xlabel("Time (us)")
    for j in range(3):
        lines.append(ax[i, j].plot(1e-3 * t_list_ns, 0.0001 * np.random.rand(len(t_list_ns)), marker=".", label='I')[
                         0])  # Returns a tuple of line objects, thus the [0]
        lines.append(ax[i, j].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
        ax[i, j].set_title(tc[i] + "  Target : " + labels[j])
        # ax[i,j].set_ylabel("Amplitude")
        ax[i, j].grid()
        ax[i, j].legend(loc='upper right')

for i in range(2):
    lines.append(ax[2, i].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='I')[0])
    lines.append(ax[2, i].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
    ax[2, i].set_title(f"Control {i}")
    # ax[2,i].set_ylabel("Amplitude")
    ax[2, i].grid()
    ax[2, i].legend(loc='upper right')

lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='I')[0])
lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label='Q')[0])
ax[2, 2].set_title("Target Rabi")
ax[2, 2].grid()
ax[2, 2].legend(loc='upper right')
fig.set_tight_layout(True)
fig.set_tight_layout(True)
plt.show()

# =======================================================


# Start data collection and plotting =====================
while results.is_processing():

    I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg, iteration = results.fetch_all()

    progress_counter(iteration, n_avg, start_time=results.get_start_time())

    # It = It_handle.fetch_all()
    # Qt = Qt_handle.fetch_all()
    # Ic = Ic_handle.fetch_all()
    # Qc = Qc_handle.fetch_all()
    # Irabi = Irabi_handle.fetch_all()
    # Qrabi = Qrabi_handle.fetch_all()

    It = I_t_avg
    Qt = Q_t_avg
    Ic = I_c_avg
    Qc = Q_c_avg
    Irabi = I_rabi_avg
    Qrabi = Q_rabi_avg

    # plot control qubits
    Ic0 = np.average(Ic[:, 0].reshape(len(t_list), 3), axis=1)
    Qc0 = np.average(Qc[:, 0].reshape(len(t_list), 3), axis=1)
    Ic1 = np.average(Ic[:, 1].reshape(len(t_list), 3), axis=1)
    Qc1 = np.average(Qc[:, 1].reshape(len(t_list), 3), axis=1)
    lines[12].set_ydata(Ic0)
    lines[13].set_ydata(Ic0)
    lines[14].set_ydata(Ic1)
    lines[15].set_ydata(Ic1)
    lines[16].set_ydata(Irabi)
    lines[17].set_ydata(Qrabi)

    # plot target qubits
    for i in range(0, 6):
        lines[2 * i].set_ydata(It[:, i])
        lines[2 * i + 1].set_ydata(Qt[:, i])

    for i in range(3):
        for j in range(3):
            ax[i, j].relim()
            ax[i, j].autoscale_view()

    snr_i, _ = S2N(I_rabi_avg)

    if snr_i > 100:
        job.halt()


    fig.set_tight_layout(True)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.2)

It = job.result_handles.get("I_t_avg").fetch_all()
Qt = job.result_handles.get("Q_t_avg").fetch_all()
Ic = job.result_handles.get("I_c_avg").fetch_all()
Qc = job.result_handles.get("Q_c_avg").fetch_all()
Ic0 = np.average(Ic[:, 0].reshape(len(t_list), 3), axis=1)
Qc0 = np.average(Qc[:, 0].reshape(len(t_list), 3), axis=1)
Ic1 = np.average(Ic[:, 1].reshape(len(t_list), 3), axis=1)
Qc1 = np.average(Qc[:, 1].reshape(len(t_list), 3), axis=1)
Irabi = job.result_handles.get("I_rabi_avg").fetch_all()
Qrabi = job.result_handles.get("Q_rabi_avg").fetch_all()

t_list_ns_data = t_list_ns.reshape(len(t_list_ns), 1)
Ic0, Ic1 = Ic0.reshape(len(Ic0), 1), Ic1.reshape(len(Ic1), 1)
Qc0, Qc1 = Qc0.reshape(len(Qc0), 1), Qc1.reshape(len(Qc1), 1)

Qtarget_data = np.hstack((t_list_ns_data, Qt))
Itarget_data = np.hstack((t_list_ns_data, It))

Icontrol_data = np.hstack((t_list_ns_data, Ic0, Ic1))
Qcontrol_data = np.hstack((t_list_ns_data, Qc0, Qc1))

# ############
# # analysis #
# ############

# #
p = np.round(p_cr, 5)
if save_data is True:
    file_saver_qubit_(Itarget_data, file_name=__file__, master_folder=ExpName,
                      suffix=f"I_Control{c_no}_Target{t_no}_Phase_{p}_Echo_{Echo}", time_stamp=time_stamp)
    file_saver_qubit_(Qtarget_data, file_name=__file__, master_folder=ExpName,
                      suffix=f"Q_Control{c_no}_Target{t_no}_Phase_{p}_Echo_{Echo}", time_stamp=time_stamp)
    file_saver_qubit_(np.transpose([t_list_ns, Irabi, Qrabi]), file_name=__file__,
                      master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                      suffix=f"Rabi_Control{c_no}_Target{t_no}_Phase_{p}_Echo_{Echo}", time_stamp=time_stamp)
    file_saver_qubit_(Icontrol_data, file_name=__file__,
                      master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                      suffix=f"Icontrol_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)
    file_saver_qubit_(Qcontrol_data, file_name=__file__,
                      master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q",
                      suffix=f"Qcontrol_Control{c_no}_Target{t_no}_Phase_{p}", time_stamp=time_stamp)

############## CR len fitting ##############

t_data = Itarget_data.transpose()
t_data_r = [t_list_ns, Irabi, Qrabi]

time_list = t_data[0]

rabi_i = 1e3 * t_data_r[1]
C0data = 1e3 * t_data[1:4]
C1data = 1e3 * t_data[4:7]
Cdata1 = []
for i in range(3):
    data = [C0data[i], C1data[i]]
    Cdata1.append(data)

# pars, cov = curve_fit(f=rabi_fit, xdata=time_list, ydata=rabi_i, p0=[0.03, 0.0016, 100, 0, np.mean(rabi_i)],
#                       bounds=(-np.inf, np.inf), maxfev=2000)
res_I = fit_cos(time_list, rabi_i)
pars = [res_I['amp'], res_I['freq'], 0, res_I['phase'], res_I['offset']]
norm, off = pars[0], pars[4]


Cdata = normalize_data(Cdata1, off, norm)

p_init = [1, 0.8e-03, 4.39050031e+02, -1.17125957e-02,
          2.27866525e-02]

# pars0, cov0 = curve_fit(f=rabi_fit, xdata=time_list, ydata=Cdata[1][0], p0=p_init, bounds=(-np.inf, np.inf), maxfev=2000)
# pars1, cov1 = curve_fit(f=rabi_fit, xdata=time_list, ydata=Cdata[1][1], p0=p_init, bounds=(-np.inf, np.inf), maxfev=2000)

p0 = fit_cos(time_list, Cdata[1][0])
p1 = fit_cos(time_list, Cdata[1][1])

pars0 = [p0['amp'], p0['freq'], 11e6, p0['phase'], p0['offset']]  # A, f, d, p, c
pars1 = [p1['amp'], p1['freq'], 11e6, p1['phase'], p1['offset']]  # A, f, d, p, c

func_0 = p0['fitfunc']
func_1 = p1['fitfunc']

t_min, t_max = time_list[0], time_list[-1]
t_list_fine = np.linspace(t_min, t_max, 10000)
Y0 = func_0(t_list_fine)
Y1 = func_1(t_list_fine)


sep = np.abs(Y1[:5000] - Y0[:5000])
tgate = np.round(t_list_fine[np.argmax(sep)], 2)

# tgate = 160
r0, r1 = 0, 0
labels = ["Z", "Y", "X"]
colors = ["r", "b", "g"]
plt.figure()
for i in range(3):
    plt.plot(time_list, Cdata[i][0], "--", label=f'{labels[i]}0', color=colors[i])
    r0 += Cdata[i][0] ** 2

plt.plot(t_list_fine, Y0, linewidth=2.2)
plt.grid()
plt.title(f"Control 0 : $T_{{gate}}$ = {int(tgate)} ns")
plt.xlabel("Time (ns)")
plt.ylabel(r"$\langle z \rangle$")
plt.axvline(tgate)
plt.legend()
plt.ylim(-1, 1)
plt.show()

# plt.figure()
for i in range(3):
    plt.plot(time_list, Cdata[i][1], "-", label=f'{labels[i]}1', color=colors[i])
    r1 += Cdata[i][1] ** 2

plt.plot(t_list_fine, Y1, linewidth=2.2)
plt.grid()
plt.title(f"control {qe_c} and target {qe_t} Control 0 : $T_{{gate}}$ = {int(tgate)} ns")
plt.xlabel("Time (ns)")
plt.ylabel(r"$\langle z \rangle$")
plt.axvline(tgate)
plt.legend()
plt.ylim(-1, 1)
plt.show()
plt.grid()


if update_calib:
    with open('../Configuration_Files/Pulse_Calibrations/cr_len_ns.json', 'r') as f:
        cr_len_data = json.load(f)
        f.close()

    t_off = tgate%8

    if t_off <= 4 :
        tgate = tgate - t_off
    else:
        tgate = tgate - t_off + 8

    cr_len_data[cr_elem] = np.round(tgate)

    with open('../Configuration_Files/Pulse_Calibrations/cr_len_ns.json', 'w') as f:
        json.dump(cr_len_data, f, indent=6)
        f.close()
