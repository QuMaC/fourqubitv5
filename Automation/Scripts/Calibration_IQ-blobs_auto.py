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
import sys
import json

save_data = False
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
q_no = int(sys.argv[1])
# q_no = 4
qe = f"q{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]

rep_rate_clk = 250000
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
ro_len = ro_len_clk[str(q_no)]
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

    with for_(n, 0, n < 5000, n + 1):
        cooldown(time=rep_rate_clk, active_reset=False,
                 qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)
        # wait(rep_rate_clk, qe)
        # reset_phase(rr)
        play("I", qe)
        align(qe, rr)
        wait(wait_rr, rr)
        # measure("readout" * amp(a_rr), rr, None,
        #         demod.full("integW_cos", I0, out),
        #         demod.full("integW_minus_sin", Q0, out))
        measure_macro(qe, rr, out, I0, Q0, pi_12=False)
        save(I0, I0_st)
        save(Q0, Q0_st)

        align()
        cooldown(time=rep_rate_clk, active_reset=False,
                 qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=False, dem=dem)
        # wait(rep_rate_clk, qe)
        play_X180(qe)
        align(qe, rr)
        wait(wait_rr, rr)
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
job = qm.execute(IQ_blobs)

I0_handle = job.result_handles.get("I0")
Q0_handle = job.result_handles.get("Q0")
I1_handle = job.result_handles.get("I1")
Q1_handle = job.result_handles.get("Q1")
job.result_handles.wait_for_all_values()

I0 = I0_handle.fetch_all()["value"]  # /ro_len
Q0 = Q0_handle.fetch_all()["value"]  # /ro_len
I1 = I1_handle.fetch_all()["value"]  # /ro_len
Q1 = Q1_handle.fetch_all()["value"]  # /ro_len

angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(I0, Q0, I1, Q1, b_print=True, b_plot=False)

with open(path_global + '/Configuration_Files/Readout_Settings/optimal_readout_phase.json', 'r') as f:
    rdout_phases = json.load(f)
    f.close()

n_angle = rdout_phases[f'rr{q_no}'] + (-1 * angle * 180 / np.pi)

rdout_phases[f'rr{q_no}'] = n_angle

with open(path_global + '/Configuration_Files/Readout_Settings/optimal_readout_phase.json', 'w') as f:
    json.dump(rdout_phases, f, indent=6)
    f.close()

with open(path_global + '/Configuration_Files/Readout_Settings/demarcations.json', 'r') as f:
    demarks = json.load(f)
    f.close()

demarks[str(q_no)] = threshold

with open(path_global + '/Configuration_Files/Readout_Settings/demarcations.json', 'w') as f:
    json.dump(demarks, f, indent=6)
    f.close()

if save_data:
    file_saver_(np.transpose([I0, Q0, I1, Q1]), file_name=__file__,
                master_folder=ExpName, header_string="I0, Q0, I1, Q1")
