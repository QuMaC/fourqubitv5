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
matplotlib.use('Qt5Agg')
import copy
from datetime import datetime
import json


simulate = True
save_data = False

now = datetime.now()
current_date = now.strftime("%y-%m-%d")

fin_path = 'TimeDomain_Rabi_user_in' + "/" + current_date + '/'



config_1 = copy.deepcopy(config)
###################
# The QUA program #
###################
q_no = 6
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]
pi_len_config = pi_len_ns[f"{q_no}"]

t_min_ns = 16
t_max_ns = 1000
dt_ns = 4 #minimum 4ns
rabi_amp = 0.4
n_avg = 100000

t_min = int(t_min_ns/4)
t_max = int(t_max_ns/4)
dt = int(dt_ns/4)
t_list = np.arange(t_min, t_max, dt)
dem = 3.123e-05

mixer_sat_pwr = 1
mixer_sat_comp = 1
mixer_sat_pwr_piby2 = 1

if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000
wait_rr = 16

with program() as rabi:

    n = declare(int)
    I = declare(fixed)
    Q = declare(fixed)
    I_st = declare_stream()
    Q_st = declare_stream()
    t = declare(int)
    n_st = declare_stream()

    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t < t_max, t + dt):

            if simulate:
                assign(t, 100)

            cooldown(time=rep_rate_clk, active_reset=False,
                     qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)
            # reset_phase(rr)
            play("grft"*amp(rabi_amp), qe, t)
            measure_macro(qe, rr, out, I, Q, pi_12=False)
            save(I, I_st)
            save(Q, Q_st)
        save(n, n_st)

    with stream_processing():
        I_st.buffer(len(t_list)).average().save('I')
        Q_st.buffer(len(t_list)).average().save('Q')
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
    plt.show(block=False)

    raise Halted()

##################################
#       Execute on the OPX       #
##################################
qm = qmm.open_qm(config)
job = qm.execute(rabi)
results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

t_list = 4*t_list
fig, axs = plt.subplots(2, 1, sharex=True)
interrupt_on_close(fig, job)  #  Interrupts the job when closing the figure

exception_flag = 0

while results.is_processing():

    I, Q, iteration = results.fetch_all()
    progress_counter(iteration, n_avg, start_time=results.get_start_time())

    try:
        res_I = fit_cos(t_list[20:], I[20:])
        res_Q = fit_cos(t_list[20:], Q[20:])
        exception_flag = 0
    except RuntimeError:
        exception_flag = 1
        print("Maximum iterations reached for fitting")
        res_I = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }
        res_Q = {"amp": 0, "omega": 0, "phase": 0, "offset": 0, "freq": 0, "period": 0, }


    data = {"I": [I, res_I], "Q": [Q, res_Q]}
    pi_time_i = res_I["period"] / 2
    pi_time_q = res_Q["period"] / 2

    if exception_flag == 0:
        for i, ax in enumerate(axs.flat):

            ax.cla()
            data_label = list(data.keys())[i]
            plot_data = data[data_label]
            fit_func = plot_data[1]["fitfunc"]
            ax.plot(t_list, plot_data[0], marker='.', label=data_label)
            ax.plot(t_list, fit_func(t_list), label=data_label + "_Fit")
            ax.set(xlabel="Time (ns)", ylabel="Rabi Amplitude")
            ax.legend()
            ax.grid()
            ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
            snr_i, _ = S2N(I)
            snr_q, _ = S2N(Q)

            # print(f'SNR_I = {snr_i} and SNR_Q = {snr_q}')

            if snr_i > 15 or snr_q > 15:
                job.halt()

        if snr_i > snr_q:
            fig.suptitle(f"Time Rabi : Pi time = {pi_time_i:.2f} ns  for amp = {rabi_amp}")
        else:
            fig.suptitle(f"Time Rabi : Pi time = {pi_time_q:.2f} ns  for amp = {rabi_amp}")

        plt.tight_layout()
        plt.pause(0.25)
        plt.show(block=False)
    else:
        print('Exception while fitting')



if exception_flag == 0:

    I, Q, iteration = results.fetch_all()
    # ############
    # # analysis #
    # ############
    res_I = fit_cos(t_list, I)
    res_Q = fit_cos(t_list, Q)
    if snr_i > snr_q:
        pi_len = res_I["period"] / 2
        rabi_plot_amp = res_I["amp"]
        # decay_const = res_I["d"]
        fit_func = res_I["fitfunc"]
    else:
        pi_len = res_Q["period"] / 2
        rabi_plot_amp = res_Q["amp"]
        # decay_const = res_I["d"]
        fit_func = res_Q["fitfunc"]

    print('######################### \n### Fitted Parameters ### \n######################### ')
    # print("Rabi frequency = {0} MHz".format(np.round(1e3*pars[1],2)))
    print(f"Pi pulse = {pi_len:.2f} ns")
    print(f"Rabi plot amplitude = {abs(rabi_plot_amp)}")
    # print(f"Rabi decay constant = {abs(decay_const):.2f} us")
    print(f"Guess amp for Power Rabi = {rabi_amp*(pi_len/pi_len_config):.3f}")

    plt.figure()
    if snr_i > snr_q:
        plt.plot(t_list, I, ".")
    else:
        plt.plot(t_list, Q, ".")
    plt.plot(t_list, fit_func(t_list))
    plt.xlabel("Time (ns)")
    plt.ylabel("Rabi Amplitude")
    plt.title(f"Time Rabi : Pi pulse = {pi_len:.2f} ns ; Guess amp= {rabi_amp*(pi_len/pi_len_config):.3f}")
    plt.grid()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.show(block=False)

    qm.close()

    with open('../Configuration_Files/Pulse_Calibrations/amp_scale.json','r') as f:
        amp_scale = json.load(f)
        f.close()

    slow_flag = 0

    if rabi_amp*(pi_len/pi_len_config) > 0.4:
        mixer_sat_pwr = 1.1
    if rabi_amp * (pi_len / pi_len_config) > 0.7:
        mixer_sat_pwr_piby2 = 1.1

    if rabi_amp*(pi_len/pi_len_config) < 1:
        amp_scale[f'{q_no}']['X180'] = rabi_amp * (pi_len/pi_len_config) * 1 * mixer_sat_pwr
        amp_scale[f'{q_no}']['Y180'] = rabi_amp * (pi_len / pi_len_config) * 1 * mixer_sat_pwr
        amp_scale[f'{q_no}']['X90'] = rabi_amp * (pi_len / pi_len_config) * (0.5) * 1 * mixer_sat_pwr_piby2
        amp_scale[f'{q_no}']['Y90'] = rabi_amp * (pi_len / pi_len_config) * (0.5) * 1 * mixer_sat_pwr_piby2
    else:
        slow_flag = 1

        amp_scale[f'{q_no}']['X180'] = rabi_amp
        amp_scale[f'{q_no}']['Y180'] = rabi_amp
        amp_scale[f'{q_no}']['X90'] = rabi_amp / 2
        amp_scale[f'{q_no}']['X90'] = rabi_amp / 2


        print(f'Rabi too slow for q_amp = {rabi_amp}. Changing pulse width appropriately')
        with open('./Pulse_Calibrations/pi_len_ns.json','r') as f:
            pi_vals = json.load(f)
            f.close()

        with open('../Configuration_Files/Pulse_Calibrations/piby2_len_ns.json','r') as f:
            piby2_vals = json.load(f)
            f.close()

        pi_vals[f'{q_no}'] = int(((rabi_amp * pi_len // 4) + 1) * 4) * 3
        piby2_vals[f'{q_no}'] = int(((rabi_amp * pi_len // 4) + 1) * 4) * 3

        with open('../Configuration_Files/Pulse_Calibrations/pi_len_ns.json', 'w') as f:
            json.dump(pi_vals,f,indent=6)
            f.close()

        with open('../Configuration_Files/Pulse_Calibrations/piby2_len_ns.json', 'w') as f:
            json.dump(piby2_vals,f,indent=6)
            f.close()



    with open('../Configuration_Files/Pulse_Calibrations/amp_scale.json', 'w') as f:
        json.dump(amp_scale, f, indent=6)
        f.close()

    with open('../Configuration_Files/Pulse_Calibrations/calib_vals.json','r') as calib_vals_file:
        calib_vals = json.load(calib_vals_file)
        calib_vals_file.close()

    calib_vals[f'{q_no}']['amin'] = amp_scale[f'{q_no}']['X180'] * 0.85
    if amp_scale[f'{q_no}']['X180'] * 1.15 > 1:
        calib_vals[f'{q_no}']['amax'] = 1
    else:
        calib_vals[f'{q_no}']['amax'] = amp_scale[f'{q_no}']['X180'] * 1.15

    calib_vals[f'{q_no}']['da'] = rabi_amp*(pi_len/pi_len_config) * 0.3/100
    if slow_flag == 0:
        calib_vals[f'{q_no}']['n_pulses'] = 5
    else:
        calib_vals[f'{q_no}']['n_pulses'] = 7

    with open('../Configuration_Files/Pulse_Calibrations/calib_vals.json', 'w') as calib_vals_file:
        json.dump(calib_vals, calib_vals_file, indent = 6)
        calib_vals_file.close()

    with open('./Rabi_data_auto.json', 'w') as rabi_data_fit:
        del res_I['fitfunc']
        del res_Q['fitfunc']
        del res_I['rawres']
        del res_Q['rawres']
        fit_data = {'fit_data_I': res_I, 'fit_data_Q': res_Q}
        json.dump(fit_data, rabi_data_fit, indent=6)

    if save_data:
        file_saver_qubit_(np.transpose([t_list, I, Q]), file_name=__file__,
                    master_folder=ExpName, header_string="Time (in ns), Magnitude, I, Q", qubit = qe)



    print('Last Line')

else:
    print('Exception while fitting')




