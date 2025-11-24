# from qm.QuantumMachinesManager import QuantumMachinesManager
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
from Helper_Functions.analysis_functions import *
from Helper_Functions.macros import *

save_data = False
###################
# The QUA program #
###################
t_min_ns = 16
t_max_ns = 500
dt_ns = 4 #minimum 4ns

t_min = int(t_min_ns/4)
t_max = int(t_max_ns/4)
dt = int(dt_ns/4)
t_list = np.arange(t_min, t_max, dt)

q_no = 4
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]

wait_init = 125000
wait_t = 4

O = "Y180"#"X180"
with program() as rabi:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    t = declare(int)

    with for_(n, 0, n < 1000, n + 1):
        with for_(t, t_min, t < t_max, t + dt):

            wait(wait_init)
            play(O, qe, t)
            # frame_rotation_2pi(0.25, qe)
            # Hadamard(qe)
            wait(wait_t, qe)
            align(qe, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", I, out),
                    demod.full("integW_minus_sin", Q, out))
            save(I, I_st)
            save(Q, Q_st)

            align(qe,rr)
            # reset_frame(qe)
            wait(wait_init,qe)
            play(O, qe, t)
            # frame_rotation_2pi(0.25, qe)
            # Hadamard(qe)
            wait(wait_t, qe)
            play("X90", qe)
            wait(wait_t, qe)
            align(qe, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", I, out),
                    demod.full("integW_minus_sin", Q, out))
            save(I, I_st)
            save(Q, Q_st)

            align(qe, rr)
            # reset_frame(qe)
            wait(wait_init, qe)
            play(O, qe, t)
            # frame_rotation_2pi(0.25, qe)
            # Hadamard(qe)
            wait(wait_t, qe)
            play("mY90", qe)
            wait(wait_t, qe)
            align(qe, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", I, out),
                    demod.full("integW_minus_sin", Q, out))
            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(t_list),3).average().save('I')
        Q_st.buffer(len(t_list),3).average().save('Q')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)


#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(rabi)
res_handles = job.result_handles
I_handle = job.result_handles.get("I")
Q_handle = job.result_handles.get("Q")

#job.result_handles.wait_for_all_values()

t_list = 4*t_list
I_handle.wait_for_values(1)
Q_handle.wait_for_values(1)

plt.ion()
plt.rcParams["figure.figsize"] = (15, 10)
fig, ax = plt.subplots(2, sharex=True,gridspec_kw = {'height_ratios':[3,1]})
fig.suptitle("Rabi Tomography", fontsize=15)
axbig = fig.add_subplot(111, frameon=False)
axbig.set_xlabel("Time (ns)", labelpad=20, fontsize=15)
axbig.set_ylabel("Amplitude", labelpad=50, fontsize=15)
axbig.set_xticks([])
axbig.set_yticks([])
lines = []
labels = ["Z","Y","X"]
for j in range(3):
    lines.append(ax[0].plot(t_list, 0.0001 * np.random.rand(len(t_list)), marker=".", label=labels[j])[0])  # Returns a tuple of line objects, thus the [0]
ax[0].set_title(" Rabi Oscillations ")
# ax[i,j].set_ylabel("Amplitude")
ax[0].grid()
ax[0].legend(loc='upper right')

fig.set_tight_layout(True)
plt.show()

# =======================================================


# Start data collection and plotting =====================
while res_handles.is_processing():

    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()

    # plot control qubits

    # plot target qubits
    for i in range(0, 3):
        lines[i].set_ydata(I[:, i])
    ax[0].relim()
    ax[0].autoscale_view()

    fig.set_tight_layout(True)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.25)

I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

Rabi_data = []
for i in range(3):
    Rabi_data.append(I[:,i])
Rabi_data = np.array(Rabi_data)
#
# # ############
# # # analysis #
# # ############
# m = 2 #0 for Z, 1 for Y, 2 for X
# pars, cov = curve_fit(f=rabi_fit, xdata=t_list, ydata=Rabi_data[m], p0=[0.1,0.0035,100,0, 1e-5],
#                         bounds=(-np.inf, np.inf), maxfev=2000)
#
# amp, off = pars[0], pars[4]
#
# #Normalizing the raw datas
# for i in range(3):
#     Rabi_data[i] = (Rabi_data[i] - off)/amp
#
# sgn = np.sign(Rabi_data[m][0])
# for i in range(3):
#     Rabi_data[i] = Rabi_data[i]*sgn
#
# #Fitting bloch equations to the normlized data
# z, y, x = Rabi_data[0], Rabi_data[1], Rabi_data[2]
# ivals = None
# best = fit_bloch_params(x, y, z, t_list, init_vals=ivals)
# fit = bloch_functions(t_list, *best)
#
# #Plotting results
# labels = ["Z","Y","X"]
# colors = ["r", "b", "g"]
#
# plt.figure()
# for i in range(3):
#     plt.plot(t_list,Rabi_data[i],".", label = labels[i], color = colors[i])
#     plt.plot(t_list,fit[i], color=colors[i])
# plt.grid()
# plt.ylim(-1.1,1.1)
# plt.title(f"Rabi : Tomography ; Operation {O}")
# plt.xlabel("Time (ns)")
# plt.ylabel("Amplitude")
# plt.axvline(52)
# plt.legend()
# plt.show()
#
# plt.figure()
# r_dat, r_fit = 0,0
# for i in range(3):
#     r_dat += Rabi_data[i]**2
#     r_fit += fit[i] ** 2
# plt.plot(t_list,r_dat,".", label = labels[i], color = colors[i])
# plt.plot(t_list,r_fit, color=colors[i])
# plt.grid()
# plt.title(f"Rabi : Bloch Vector; Operation {O}")
# plt.xlabel("Time (ns)")
# plt.ylabel("Bloch Length")
# plt.legend()
# plt.show()