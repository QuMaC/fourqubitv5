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
from Helper_Functions.macros import *

save_data = True
rescale = True
update_pars = True
simulate = False
pi12 = False
q_no = 4
qe = f"q{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
nshots = 10000





qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
ro_len = ro_len_clk[str(q_no)]
### Dict import for plot:
integ_len = integ_len_clk[f"{q_no}"]
ro_amplitude = ro_amp[f"{q_no}"]
###################
# The QUA program #
###################

dem = 3.123e-05
a_rr = 1.0
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

    with for_(n, 0, n < nshots, n + 1):
        reset_frame(qe, rr)
        cooldown(time=rep_rate_clk, active_reset=False,
                 qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=pi12, dem=dem)

        # wait(rep_rate_clk, qe)
        play("I", qe)
        # align(qe, rr)
        # wait(wait_rr, rr)
        # measure("readout" * amp(a_rr), rr, None,
        #         demod.full("integW_cos", I0, out),
        #         demod.full("integW_minus_sin", Q0, out))
        measure_macro(qe, rr, out, I0, Q0, pi_12=False)
        save(I0, I0_st)
        save(Q0, Q0_st)

        align()

        reset_frame(qe, rr)
        cooldown(time=rep_rate_clk, active_reset=False,
                 qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=pi12, dem=dem)

        # wait(rep_rate_clk, qe)
        play_X180(qe)
        # play("grft" * amp(0.15), qe, 22)
        # align(qe, rr)
        # wait(wait_rr, rr)
        # measure("readout" * amp(a_rr), rr, None,
        #         demod.full("integW_cos", I1, out),
        #         demod.full("integW_minus_sin", Q1, out))
        measure_macro(qe, rr, out, I1, Q1, pi_12=False)
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
    plt.show(block=True)


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

if rescale:
    I0 = 1e6 * I0/ ro_len
    Q0 = 1e6 * Q0/ ro_len
    I1 = 1e6 * I1/ ro_len
    Q1 = 1e6 * Q1/ ro_len

angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(I0, Q0, I1, Q1, b_print=True, b_plot=True)

plt.text(
    0.98, 0.98,
    f"Qubit {q_no}\n"
    f"fid: {fidelity:.2f}\n"
    f"ro amp {ro_amplitude}\n"
    f"ro len {ro_len}\n"
    f"int len {integ_len}",
    transform=plt.gca().transAxes,
    va="top", ha="left",
    fontsize=9,
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none")
)
plt.tight_layout()
plt.show(block= True)
# plt.savefig(f"IQ_blobs_verbose_{q_no}.png")
# print(f"IQ_blobs_verbose_{q_no}.png saved")

print(f"Ig, Ie = {np.mean(I0)}, {np.mean(I1)}")
print(f"Qg, Qe = {np.mean(Q0)}, {np.mean(Q1)}")

if update_pars:
    with open('../Configuration_Files/Readout_Settings/optimal_readout_phase.json', 'r') as f:
        rdout_phases = json.load(f)
        f.close()

    n_angle = rdout_phases[f'rr{q_no}'] + (-1 * angle * 180 / np.pi)

    rdout_phases[f'rr{q_no}'] = np.round(n_angle%360, 3)

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
                master_folder=ExpName, header_string="I0, Q0, I1, Q1")
