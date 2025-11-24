import json
from qm.qua import *
from qm import SimulationConfig
from qm import QuantumMachinesManager
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.plot import interrupt_on_close
from Helper_Functions.macros import measure_macro, cooldown, BB1_X180, play_cmd_t, BB1_Y180, BB1_mX90, BB1_mY90, BB1_Y90, BB1_X90, KNILL_X180, UCP5b_X180, UCP5b_Y180
from Helper_Functions.analysis_functions import *
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
import copy


simulate = False
save_data = True
pi_12 = False

config_1 = copy.deepcopy(config)
##################
# The QUA program #
##################
q_no = 4
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]
pi_len_config = pi_len_ns[f"{q_no}"]

t_min_ns = 100
t_max_ns = 500
dt_ns = 4 #minimum 4ns
rabi_amp = 1
n_avg = 1000

t_min = int(t_min_ns/4)
t_max = int(t_max_ns/4)
dt = int(dt_ns/4)
t_list = np.arange(t_min, t_max, dt)
dem = 3.123e-05

if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000
wait_rr = 16
flg1 = True

def main_gate(qe,t):
    if flg1:
        UCP5b_Y180(qe)
        # KNILL_X180(qe)
        # KNILL_X180(qe)
    else:
        # play_X180(qe)
        play_Y180(qe)
        # play("I", qe)

    # play_X180(qe, t=t)
    # play_cmd_t("X180", qe, t, BB_flg=flg1)

with program() as rabi:

    n = declare(int)
    I = declare(fixed)
    Q = declare(fixed)
    I_st = declare_stream()
    Q_st = declare_stream()
    I_st_x = declare_stream()
    Q_st_x = declare_stream()
    I_st_y = declare_stream()
    Q_st_y = declare_stream()
    t = declare(int)
    n_st = declare_stream()





    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t < t_max, t + dt):
            # reset_phase(rr)
            if simulate:
                assign(t, 100)

            cooldown(time=rep_rate_clk, active_reset=False,
                     qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)
            reset_frame(qe)
            wait(4, qe)
            # play("grft"*amp(rabi_amp), qe, t)
            # play_X180(qe, a=amp(rabi_amp), t=t)
            # play_X180(qe, t=t)
            main_gate(qe, t)

            reset_if_phase(rr)
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)
            save(I, I_st)
            save(Q, Q_st)

            cooldown(time=rep_rate_clk, active_reset=False,
                     qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)

            reset_frame(qe)
            wait(4, qe)
            main_gate(qe, t)

            play_X90(qe)
            reset_if_phase(rr)
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)
            save(I, I_st_x)
            save(Q, Q_st_x)

            cooldown(time=rep_rate_clk, active_reset=False,
                     qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)
            reset_frame(qe)
            wait(4, qe)
            # play_X180(qe, t=t)
            main_gate(qe, t)

            play_Y90(qe)
            reset_if_phase(rr)
            measure_macro(qe, rr, out, I, Q, pi_12=pi_12)
            save(I, I_st_y)
            save(Q, Q_st_y)


        save(n, n_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('Iz')
        Q_st.buffer(len(t_list)).average().save('Qz')
        I_st_x.buffer(len(t_list)).average().save('Ix')
        Q_st_x.buffer(len(t_list)).average().save('Qx')
        I_st_y.buffer(len(t_list)).average().save('Iy')
        Q_st_y.buffer(len(t_list)).average().save('Qy')
        n_st.save("iteration")

####################
# Simulate Program #
####################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

if simulate:
    job = qmm.simulate(config, rabi, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    # samples.con1.plot()
    samples.con3.plot()

    raise Halted()

##################################
#       Execute on the OPX       #
##################################
qm = qmm.open_qm(config)
job = qm.execute(rabi)
results = fetching_tool(job, data_list=["Ix", "Qx", "Iy", "Qy", "Iz", "Qz", "iteration"], mode="live")

t_list = 4*t_list
fig, axs = plt.subplots(3, 1, sharex=True)
interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

exception_flag = 0

while results.is_processing():

    Ix, Qx, Iy, Qy, Iz, Qz, iteration = results.fetch_all()
    progress_counter(iteration, n_avg, start_time=results.get_start_time())

    try:
        res_Iz = fit_cos(t_list, Iz)
        res_Qz = fit_cos(t_list, Qz)
        res_Ix = fit_cos(t_list, Ix)
        res_Qx = fit_cos(t_list, Qx)
        res_Iy = fit_cos(t_list, Iy)
        res_Qy = fit_cos(t_list, Qy)
        exception_flag = 0
    except:
        exception_flag = 1
        print("Maximum iterations reached for fitting")
        res_Iz = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }
        res_Qz = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }
        res_Ix = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }
        res_Qx = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }
        res_Iy = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }
        res_Qy = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }

    dataz = {"Iz": [Iz, res_Iz], "Qz": [Qz, res_Qz]}
    datax = {"Ix": [Ix, res_Ix], "Qx": [Qx, res_Qx]}
    datay = {"Iy": [Iy, res_Iy], "Qy": [Qy, res_Qy]}

    data = [dataz, datax, datay]
    # pi_time = res_Iz["period"] / 2

    if exception_flag == 0:

        for i, ax in enumerate(axs.flat):

            ax.cla()
            data_label = list(data[i].keys())[0]
            plot_data = data[i][data_label]
            fit_func = plot_data[1]["fitfunc"]
            ax.plot(t_list, plot_data[0], marker='.', label=data_label)
            ax.plot(t_list, fit_func(t_list), label=data_label + "_Fit")
            ax.set(xlabel="Time (ns)", ylabel="Rabi Amplitude")
            ax.legend()
            ax.grid()
            ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

        fig.suptitle(f"Tomography for BB1 pulse testing. BB = {flg1}")
        plt.tight_layout()
        plt.pause(0.25)
    else:
        print('Exception while fitting')

if exception_flag == 0:
    Ix, Qx, Iy, Qy, Iz, Qz, iteration = results.fetch_all()
    # ############
    # # analysis #
    # ############
    res_I = fit_cos(t_list, Iy)
    res_Q = fit_cos(t_list, Qz)
    pi_len = res_I["period"] / 2
    rabi_plot_amp = res_I["amp"]
    # decay_const = res_I["d"]
    fit_func = res_I["fitfunc"]
    rabi_freq = res_I["freq"]


    print('######################### \n### Fitted Parameters ### \n######################### ')
    # print("Rabi frequency = {0} MHz".format(np.round(1e3*pars[1],2)))
    print(f"Pi pulse = {pi_len:.2f} ns")
    print(f"Rabi plot amplitude = {abs(rabi_plot_amp)}")
    # print(f"Rabi decay constant = {abs(decay_const):.2f} us")
    print(f"Guess amp for Power Rabi = {rabi_amp*(pi_len/pi_len_config):.3f}")
    print(f"Rabi frequency = {1e3*rabi_freq:.3f} MHz")

    plt.figure()
    plt.plot(t_list, Iy, ".")
    plt.plot(t_list, fit_func(t_list))
    plt.xlabel("Time (ns)")
    plt.ylabel("Rabi Amplitude")
    plt.title(f"Time Rabi : Pi pulse = {pi_len:.2f} ns ; Guess amp= {rabi_amp*(pi_len/pi_len_config):.3f}")
    plt.grid()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.show()

    # calib_vals_file = open('Pulse_Calibrations/calib_vals.json','r')
    # calib_vals = json.load(calib_vals_file)
    # calib_vals_file.close()
    #
    # calib_vals[f'{q_no}']['amin'] = rabi_amp*(pi_len/pi_len_config) * 0.8
    # calib_vals[f'{q_no}']['amax'] = rabi_amp*(pi_len/pi_len_config) * 1.2
    # calib_vals[f'{q_no}']['da'] = 0.0001
    # calib_vals[f'{q_no}']['n_pulses'] = 5
    #
    # calib_vals_file = open('Pulse_Calibrations/calib_vals.json','w')
    # json.dump(calib_vals, calib_vals_file, indent = 6)
    # calib_vals_file.close()

    if save_data:
        file_saver_(np.transpose([t_list, I, Q]), file_name=__file__,
                    master_folder=ExpName, header_string="Frequency (GHz), Magnitude, I, Q")

else:
    print('Exception while fitting')