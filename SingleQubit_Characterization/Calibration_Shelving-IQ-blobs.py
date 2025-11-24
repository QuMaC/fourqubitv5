from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
# matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from qualang_tools.analysis.discriminator import two_state_discriminator
from Helper_Functions.macros import cooldown, measure_macro

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

# q_list = [1, 2, 3, 4, 5]
q_list = [3]
for q_no in q_list:
    # q_no = 1
    qe = f"q{q_no}"
    qe_12 = f"q12_{q_no}"
    rr = f"rr{q_no}"
    out = adc_mapping[rr]
    # pi_12 = False
    save_data = True
    rescale = False
    update_pars = False
    simulate = False

    if simulate:
        rep_rate_clk = 300
    else:
        rep_rate_clk = 250000

    wait_rr = 16
    wait_q = 4
    pi_len = pi_len_ns[str(q_no)]
    ro_len = ro_len_clk[str(q_no)]
    ###################
    # The QUA program #
    ###################

    dem = demarcations[str(q_no)]
    a_rr = 1
    with program() as IQ_blobs:

        n = declare(int)
        I = declare(fixed)
        Q = declare(fixed)
        I0 = declare(fixed)
        I0_st = declare_stream()
        Q0 = declare(fixed)
        Q0_st = declare_stream()
        I1 = declare(fixed)
        I1_st = declare_stream()
        Q1 = declare(fixed)
        Q1_st = declare_stream()

        with for_(n, 0, n < 5000, n + 1):
            # wait(rep_rate_clk, qe)
            # reset_phase(rr)
            cooldown(time=rep_rate_clk, active_reset=False, qe=qe)
            play("I", qe)
            wait(wait_q, qe)
            align(qe, qe_12)
            play_X180(qe_12)
            align(qe_12, rr)
            wait(wait_rr, rr)
            reset_if_phase(rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", I0, out),
                    demod.full("integW_minus_sin", Q0, out))
            # measure_macro(qe, rr, out, I0, Q0, pi_12=True)
            save(I0, I0_st)
            save(Q0, Q0_st)

            align()
            # reset_phase(rr)
            cooldown(time=rep_rate_clk, active_reset=False, qe=qe, qe_12=qe_12, rr=rr, out=out, I=I, Q=Q, pi_12=False,
                     dem=dem)
            play_X180(qe)
            wait(wait_q, qe)
            align(qe, qe_12)
            play_X180(qe_12)
            align(qe_12, rr)
            wait(wait_rr, rr)
            reset_if_phase(rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", I1, out),
                    demod.full("integW_minus_sin", Q1, out))
            # measure_macro(qe, rr, out, I1, Q1, pi_12=True)
            save(I1, I1_st)
            save(Q1, Q1_st)

        with stream_processing():
            I0_st.save_all('I0')
            Q0_st.save_all('Q0')
            I1_st.save_all('I1')
            Q1_st.save_all('Q1')

    qm = qmm.open_qm(config)
    if simulate:
        job = qmm.simulate(config, IQ_blobs, SimulationConfig(int(10000)))
        # get DAC and digital samples
        samples = job.get_simulated_samples()
        # plot all ports:
        # samples.con1.plot()
        samples.con3.plot()
        plt.show(block=False)

        raise Halted()
    job = qm.execute(IQ_blobs)

    I0_handle = job.result_handles.get("I0")
    Q0_handle = job.result_handles.get("Q0")
    I1_handle = job.result_handles.get("I1")
    Q1_handle = job.result_handles.get("Q1")
    job.result_handles.wait_for_all_values()

    I0 = I0_handle.fetch_all()["value"]
    Q0 = Q0_handle.fetch_all()["value"]
    I1 = I1_handle.fetch_all()["value"]
    Q1 = Q1_handle.fetch_all()["value"]

    angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(I0, Q0, I1, Q1, b_print=True, b_plot=True)
    plt.title(f'Qubit = {q_no}')
    plt.show(block=False)

    if update_pars:
        with open('../Configuration_Files/Readout_Settings/optimal_readout_phase.json', 'r') as f:
            rdout_phases = json.load(f)
            f.close()

        n_angle = rdout_phases[f'rr{q_no}'] + (-1 * angle * 180 / np.pi)

        rdout_phases[f'rr{q_no}'] = np.round(n_angle % 360, 3)

        with open('../Configuration_Files/Readout_Settings/optimal_readout_phase.json', 'w') as f:
            json.dump(rdout_phases, f, indent=6)
            f.close()

        with open('../Configuration_Files/Readout_Settings/demarcations.json', 'r') as f:
            demarks = json.load(f)
            f.close()

        demarks[str(q_no)] = threshold

        with open('../Configuration_Files/Readout_Settings/demarcations.json', 'w') as f:
            json.dump(demarks, f, indent=6)
            f.close()

    if save_data:
        file_saver_(np.transpose([I0, Q0, I1, Q1]), file_name=__file__,
                    master_folder=ExpName, header_string="I0, Q0, I1, Q1", suffix=f"q{q_no}")
