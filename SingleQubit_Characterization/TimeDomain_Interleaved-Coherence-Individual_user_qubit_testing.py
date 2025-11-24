from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from qualang_tools.results import progress_counter, fetching_tool
from Helper_Functions.analysis_functions import *
from qualang_tools.plot import interrupt_on_close
from Helper_Functions.macros import *


# %%
def coh_fit(t, A, d, c):
    return A * np.exp(-t / d) + c


def ramsey_fit(t, A, f, d, p, c):
    return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c


# %%

n_iter = 1
plot_final = True  # Set as true to obtain final plots with data and fit lines
save_data = True  # Set as true for automatic data saving
time_stamp = True  # Set as true to include time stamp in saved files
active_reset = False  # Set as true for resetting qubit with feedback

q_no = 2
qubit_IF = q_IF[str(q_no)]
qe = f"q{q_no}"
rr = f"rr{q_no}"
dem = demarcations[str(q_no)]
out = adc_mapping[rr]
ro_len = ro_len_clk[str(q_no)]
ZZ_shift = CrossKerr[str(q_no)] * 1e-6
qubit_IF_orig = qubit_IF
# qubit_IF_orig = -228.64 * u.MHz
###################
# The QUA program #
###################
with open('./coherence_redo.json', 'w') as f:
    json.dump({'redo': 0}, f, indent=6)

with open('../Configuration_Files/Pulse_Calibrations/coherence_time_limits.json', 'r') as coh_times_file:
    time_limits = json.load(coh_times_file)
    coh_times_file.close()

t_min = time_limits[str(q_no)]['t_min'] // 4
t_max = time_limits[str(q_no)]['t_max'] // 4
# dt = time_limits[str(q_no)]['dt'] // 4

points = 312

# t_min = 16 // 4
# t_max = 75000 // 4  # actual tmax will be twice this
# dt = 30//4  # actual step size is twice this to keep ramsey and t1 steps consistent with echo #150//4 # total 312 steps

# with open('./Pulse_Calibrations/ramsey_time_limits.json', 'r') as ram_file:
#     time_limits1 = json.load(ram_file)
#     ram_file.close()

# dt = 240 // 4#time_limits1[str(q_no)]['dt'] // 4
dt = (t_max - t_min)//points

# t_min = 16//4
# t_max = 20000//4  #actual tmax will be twice this
# dt = 50//4 #actual step size is twice this to keep ramsey and t1 steps consistent with echo #150//4
det = 0.2  # MHz


t_list = np.arange(t_min, t_max, dt)
# t_list = np.linspace(t_min, t_max, 450, dtype=int, endpoint=False)
# dt = t_list[1] - t_list[0]
t_list_us = 8e-3 * t_list  # to convert to us with factor two as above

rep_rate_clk = 250000
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
piby2_len = piby2_len_ns[str(q_no)]

n_avg = 1000

with program() as coherence:
    n = declare(int)
    Ir = declare(fixed)
    Ir_st = declare_stream()
    Qr = declare(fixed)
    Qr_st = declare_stream()
    Ie = declare(fixed)
    Ie_st = declare_stream()
    Qe = declare(fixed)
    Qe_st = declare_stream()
    It = declare(fixed)
    It_st = declare_stream()
    Qt = declare(fixed)
    Qt_st = declare_stream()
    I_ar = declare(fixed)
    Q_ar = declare(fixed)
    t = declare(int)
    n_st = declare_stream()

    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t < t_max, t + dt):
        # with for_each_(t, t_list):
            align(qe, rr)
            update_frequency(qe, qubit_IF_orig)
            align(qe, rr)
            cooldown(time=rep_rate_clk, active_reset=active_reset, qe=qe, qe_12=None, rr=rr, out=out, I=I_ar, Q=Q_ar,
                     pi_12=False, dem=dem)
            # reset_phase(rr)
            play_X90(qe)
            wait(t, qe)
            play_X180(qe)
            wait(t, qe)
            play_X90(qe)
            align(qe, rr)
            wait(wait_rr, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", Ie, out),
                    demod.full("integW_minus_sin", Qe, out))

            save(Ie, Ie_st)
            save(Qe, Qe_st)

            align(qe, rr)
            cooldown(time=rep_rate_clk, active_reset=active_reset, qe=qe, qe_12=None, rr=rr, out=out, I=I_ar, Q=Q_ar,
                     pi_12=False, dem=dem)
            # reset_phase(rr)
            play_X180(qe)
            wait(2 * t, qe)
            align(qe, rr)
            wait(wait_rr, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", It, out),
                    demod.full("integW_minus_sin", Qt, out))
            save(It, It_st)
            save(Qt, Qt_st)

            align(qe, rr)
            cooldown(time=rep_rate_clk, active_reset=active_reset, qe=qe, qe_12=None, rr=rr, out=out, I=I_ar, Q=Q_ar,
                     pi_12=False, dem=dem)
            # reset_phase(rr)
            update_frequency(qe, qubit_IF + det * 1e6)
            play_X90(qe)
            wait(2 * t, qe)
            play_X90(qe)
            align(qe, rr)
            wait(wait_rr, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", Ir, out),
                    demod.full("integW_minus_sin", Qr, out))

            save(Ir, Ir_st)
            save(Qr, Qr_st)
        save(n, n_st)

    with stream_processing():
        Ir_st.buffer(len(t_list)).average().save('Ir')
        Qr_st.buffer(len(t_list)).average().save('Qr')
        Ie_st.buffer(len(t_list)).average().save('Ie')
        Qe_st.buffer(len(t_list)).average().save('Qe')
        It_st.buffer(len(t_list)).average().save('It')
        Qt_st.buffer(len(t_list)).average().save('Qt')
        n_st.save("iteration")

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
job = qm.execute(coherence)
res_handles = job.result_handles

results = fetching_tool(job, data_list=["Ir", "Qr", "Ie", "Qe", "It", "Qt", "iteration"], mode="live")

t_list = 4 * t_list
limit_check = 0

fig, axs = plt.subplots()
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

coh_list = []
exception_flag = 0

with open('../Configuration_Files/Pulse_Calibrations/upper_bound_coherence.json') as f:
    bound_dict = json.load(f)
    upper = 3 * bound_dict['T1_upper']
    f.close()

bnds = ([0, 0, -np.inf, 0, -np.inf], [np.inf, upper, np.inf, np.inf, np.inf])
bnds_et = ([0, 0, -np.inf], [np.inf, upper, np.inf])

while results.is_processing():

    # Ir = Ir_handle.fetch_all()
    # Qr = Qr_handle.fetch_all()
    # Ie = Ie_handle.fetch_all()
    # Qe = Qe_handle.fetch_all()
    # It = It_handle.fetch_all()
    # Qt = Qt_handle.fetch_all()

    Ir, Qr, Ie, Qe, It, Qt, iteration = results.fetch_all()
    progress_counter(iteration, n_avg, start_time=results.get_start_time())

    axs.cla()
    axs.plot(t_list_us, It, label="T1")
    axs.plot(t_list_us, Ie, label="Echo")
    axs.plot(t_list_us, Ir, label="Ramsey")
    axs.set(xlabel="Time (us)", ylabel="Amplitude")
    axs.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    fig.suptitle("Coherence Measurement")
    axs.grid()
    axs.legend()

    plt.tight_layout()
    plt.pause(0.2)

    snr, _ = S2N(It)
    # print(snr)
    no_time_flag = 0
    too_much_time = 0
    if snr > 5:
        if limit_check == 0:

            limit_check = 1

            try:
                pars_e1, cov_e = curve_fit(f=coh_fit, xdata=t_list_us, ydata=Ie, p0=[1e-3, 20, 1e-5],
                                           bounds=bnds_et, maxfev=2000)
                pars_t1, cov_t = curve_fit(f=coh_fit, xdata=t_list_us, ydata=It, p0=[1e-3, 5, 1e-5],
                                           bounds=bnds_et, maxfev=2000)
                exception_flag = 0
            except RuntimeError:
                print('Exception')
                exception_flag = 1

            # print(f'T1 ext = {pars_e1[1]}')
            # print(f'T_max = {t_max}')

            if t_max < 0.5 * pars_e1[1] or t_max < 0.5 * pars_t1[1]:
                print('Insufficient time')
                no_time_flag = 1
            elif t_max > 3 * pars_e1[1] or t_max > 3 * pars_t1[1]:
                print('Too much time')
                too_much_time = 1
            if (no_time_flag == 1):# or (too_much_time == 1):
                with open('./coherence_redo.json', 'w') as f:
                    json.dump({'redo': 1}, f, indent=6)
                    f.close()
                with open('../Configuration_Files/Pulse_Calibrations/coherence_time_limits.json', 'w') as f:
                    max_time = pars_e1[1]
                    if max_time < pars_t1[1]:
                        max_time = pars_t1[1]
                        exception_flag = 1

                    time_limits[str(q_no)]['t_max'] = max_time * 1000
                    # time_limits[str(q_no)]['dt'] = 2*max_time // 800
                    json.dump(time_limits, f, indent=6)
                    f.close()
                    job.halt()
            if too_much_time == 1:
                with open('../Configuration_Files/Pulse_Calibrations/coherence_time_limits.json', 'w') as f:
                    max_time = pars_e1[1]
                    if max_time < pars_t1[1]:
                        max_time = pars_t1[1]
                        # exception_flag = 1

                    time_limits[str(q_no)]['t_max'] = max_time * 1000
                    # time_limits[str(q_no)]['dt'] = 2*max_time // 800
                    json.dump(time_limits, f, indent=6)

                print(f"Estimated T1 is {pars_t1[1]} us")
                print(f"Estimated echo is {pars_e1[1]} us")
                job.halt()
            else:
                with open('./coherence_redo.json', 'w') as f:
                    json.dump({'redo': 0}, f, indent=6)
                    f.close()

        else:
            limit_check = 0

        if snr > 15:
            job.halt()

print('acquistion loop done')
plt.close(fig)

try:
    pars_r, cov_r = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=Ir, p0=[1e-3, det + ZZ_shift, 10, 0, 1e-5],
                              bounds=(-np.inf, np.inf), maxfev=2000)
    pars_e, cov_e = curve_fit(f=coh_fit, xdata=t_list_us, ydata=Ie, p0=[1e-3, 20, 1e-5], bounds=(-np.inf, np.inf),
                              maxfev=2000)
    pars_t, cov_t = curve_fit(f=coh_fit, xdata=t_list_us, ydata=It, p0=[1e-3, 5, 1e-5], bounds=(-np.inf, np.inf),
                              maxfev=2000)

except RuntimeError:
    pars_r = [0, 0, 0, 0, 0]
    pars_e = [0, 0, 0]
    pars_t = [0, 0, 0]
    exception_flag = 1
# pars_r, cov_r = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=Ir, p0=[1e-3,det+ZZ_shift,10,0, 1e-5], bounds=(-np.inf, np.inf), maxfev=2000)
# pars_r, cov_r = curve_fit(f=ramsey_fit, xdata=t_list_us, ydata=Ir, p0=[1e-3, det + ZZ_shift+0.0, 10, 0, 1e-5], bounds=(-np.inf, np.inf), maxfev=2000)
# pars_e, cov_e = curve_fit(f=coh_fit, xdata=t_list_us, ydata=Ie, p0=[1e-3, 20, 1e-5], bounds=(-np.inf, np.inf), maxfev=2000)
# pars_t, cov_t = curve_fit(f=coh_fit, xdata=t_list_us, ydata=It, p0=[1e-3, 5, 1e-5], bounds=(-np.inf, np.inf), maxfev=2000)

if exception_flag == 0 or no_time_flag == 0:

    ram_t = np.round(pars_r[2], 2)
    ram_f = np.round(pars_r[1], 5)
    echo_t = np.round(pars_e[1], 2)
    t1_t = np.round(pars_t[1], 2)
    coh_list.append([ram_f, ram_t, t1_t, echo_t])

    if t_max < 0.5 * pars_e[1] or t_max < 0.5 * pars_t[1]:
        print('Insufficient time')
        no_time_flag = 1
    elif t_max > 3 * pars_e[1] or t_max > 3 * pars_t[1]:
        print('Too much time')
        too_much_time = 1

    if (no_time_flag == 1):# or (too_much_time == 1):
        with open('./coherence_redo.json', 'w') as f:
            json.dump({'redo': 1}, f, indent=6)
            f.close()

    if (no_time_flag == 1):  # or (too_much_time == 1):
        with open('./coherence_redo.json', 'w') as f:
            json.dump({'redo': 1}, f, indent=6)
            f.close()
        with open('../Configuration_Files/Pulse_Calibrations/coherence_time_limits.json', 'w') as f:
            max_time = pars_e1[1]
            if max_time < pars_t1[1]:
                max_time = pars_t1[1]
                exception_flag = 1

            time_limits[str(q_no)]['t_max'] = max_time * 1000
            # time_limits[str(q_no)]['dt'] = 2*max_time // 800
            json.dump(time_limits, f, indent=6)

    if too_much_time == 1:
        with open('../Configuration_Files/Pulse_Calibrations/coherence_time_limits.json', 'w') as f:
            max_time = pars_e[1]
            if max_time < pars_t[1]:
                max_time = pars_t[1]
                # exception_flag = 1

            time_limits[str(q_no)]['t_max'] = max_time * 1000
            # time_limits[str(q_no)]['dt'] = 2*max_time // 800
            json.dump(time_limits, f, indent=6)
        print(f'Estimated T1 is {pars_t[1]} us')
        print(f'Estimated Echo is {pars_e[1]} us')

    fits = {'ramsey': {'amp': pars_r[0],
                       'freq': pars_r[1],
                       'decay': pars_r[2],
                       'phase': pars_r[3],
                       'offset': pars_r[4],
                       },
            'echo': {
                'amp': pars_e[0],
                'decay': pars_e[1],
                'offset': pars_e[2],
            },
            'T1': {
                'amp': pars_t[0],
                'decay': pars_t[1],
                'offset': pars_t[2],
            },
            }

    with open('./Coherence_fits.json', 'w') as f:
        json.dump(fits, f, indent=6)

    print('#########################')
    print('### Fitted Parameters ###')
    print('#########################')
    print("Ramsey frequency = {0} MHz".format(ram_f))
    print("Ramsey time = {0} us".format(ram_t))
    print("Echo time = {0} us".format(echo_t))
    print("T1 time = {0} us".format(t1_t))

    if plot_final:
        plt.figure()
        t_list_fit = 8e-3 * np.linspace(t_min, t_max, 2000)
        plt.plot(t_list_fit, coh_fit(t_list_fit, *pars_t), linestyle='--', linewidth=2, label="T1")
        plt.plot(t_list_us, It)
        plt.plot(t_list_fit, coh_fit(t_list_fit, *pars_e), linestyle='--', linewidth=2, label="Echo")
        plt.plot(t_list_us, Ie)
        plt.plot(t_list_fit, ramsey_fit(t_list_fit, *pars_r), linestyle='--', linewidth=2, label="Ramsey")
        plt.plot(t_list_us, Ir)
        plt.xlabel('t (us)')
        plt.ylabel('Signal')
        plt.title("Coherence :Ramsey = {0} us , T1 = {1} us , Echo = {2} us".format(ram_t, t1_t, echo_t))
        plt.grid()
        plt.legend()
        plt.show(block=False)

        plt.figure()
        t_list_fit = 8e-3 * np.linspace(t_min, t_max, 2000)
        plt.plot(t_list_fit, coh_fit(t_list_fit, *pars_t), linestyle='--', linewidth=2, label="T1")
        plt.plot(t_list_us, It)
        plt.plot(t_list_fit, coh_fit(t_list_fit, *pars_e), linestyle='--', linewidth=2, label="Echo")
        plt.plot(t_list_us, Ie)
        plt.xlabel('t (us)')
        plt.ylabel('Signal')
        plt.title("Coherence : T1 = {0} us , Echo = {1} us".format(t1_t, echo_t))
        plt.grid()
        plt.legend()
        plt.show(block=False)

    if save_data:
        file_saver_qubit_(np.transpose([t_list_us, Ir, Qr]), file_name=__file__, suffix=f"Ramsey_{qe}",
                          master_folder=ExpName, header_string="Time (us), I, Q", time_stamp=time_stamp, qubit=qe)

        file_saver_qubit_(np.transpose([t_list_us, It, Qt]), file_name=__file__, suffix=f"T1_{qe}",
                          master_folder=ExpName, header_string="Time (us), I, Q", time_stamp=time_stamp, qubit=qe)

        file_saver_qubit_(np.transpose([t_list_us, Ie, Qe]), file_name=__file__, suffix=f"Echo_{qe}",
                          master_folder=ExpName, header_string="Time (us), I, Q", time_stamp=time_stamp, qubit=qe)

        file_saver_qubit_(coh_list, file_name=__file__, suffix=f"CoherenceVals_{qe}",
                          master_folder=ExpName, header_string="Ramsey freq (MHz), Ramsey(us), T1(us), Echo(us)",
                          time_stamp=time_stamp, qubit=qe)

else:
    with open('./coherence_redo.json', 'w') as f:
        json.dump({'redo': 1}, f, indent=6)
        f.close()
    print('Exception somewhere, or redo coherence')
