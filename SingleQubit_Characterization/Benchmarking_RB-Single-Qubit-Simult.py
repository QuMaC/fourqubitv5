"""Run from this folder or anywhere: repo root is added to sys.path from __file__."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_rs = str(_REPO_ROOT)
if _rs not in sys.path:
    sys.path.insert(0, _rs)

from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
from matplotlib import pyplot as plt
from qm.qua import *
from scipy.optimize import curve_fit
import time

try:
    from tqdm.auto import tqdm
except ImportError:
    tqdm = None

from Helper_Functions.helper_functionsv2 import Halted, file_saver_
from Helper_Functions.macros import (
    measure_macro,
    play_X180,
    play_X90,
    play_Y180,
    play_Y90,
    play_mX90,
    play_mY90,
)

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

pi_12 = False
q1_no, q2_no = 1, 4

qe1 = f"q{q1_no}"
rr1 = f"rr{q1_no}"
out1 = adc_mapping[rr1]

qe2 = f"q{q2_no}"
rr2 = f"rr{q2_no}"
out2 = adc_mapping[rr2]

avgs= 200
wait_init = 250000
wait_t = 4
wait_rr = 8
dem1 = demarcations[str(q1_no)]
dem2 = demarcations[str(q2_no)]

simulate = False
lsb = False
# Progress bar while the OPX program runs (per-shot counter streamed to host).
SHOW_PROGRESS = True

_CAYLEY_CSV = _REPO_ROOT / "Configuration_Files" / "Resources" / "c1_cayley_table.csv"
_cayley_raw = np.genfromtxt(_CAYLEY_CSV, delimiter=",")
cayley_table = np.asarray(_cayley_raw[1:, 1:], dtype=np.int64)
inv_gates = [int(np.where(cayley_table[i, :] == 0)[0][0]) for i in range(24)]
max_circuit_depth = 400 #180
delta_depth = 1  # must be 1!!
num_of_sequences = 10 #50
seed = 345323#   345324

def generate_sequence():

    cayley = declare(int, value=cayley_table.flatten().tolist())
    inv_list = declare(int, value=inv_gates)
    current_state = declare(int)
    step = declare(int)
    sequence = declare(int, size=max_circuit_depth+1)
    inv_gate = declare(int, size=max_circuit_depth+1)
    i = declare(int)
    rand = Random(seed=seed)

    assign(current_state, 0)
    with for_(i, 0, i < max_circuit_depth, i+1):
        assign(step, rand.rand_int(24))
        assign(current_state, cayley[current_state*24+step])
        assign(sequence[i], step)
        assign(inv_gate[i], inv_list[current_state])

    return sequence, inv_gate

def play_sequence(qe, sequence_list, depth):
    i = declare(int)
    with for_(i, 0, i <= depth, i+1):

        with switch_(sequence_list[i], unsafe=True):

            with case_(0):
                play('I', qe)
            with case_(1):
                play_X180(qe)
            with case_(2):
                play_Y180(qe)
            with case_(3):
                play_Y180(qe)
                play_X180(qe)
            with case_(4):
                play_X90(qe)
                play_Y90(qe)
            with case_(5):
                play_X90(qe)
                play_mY90(qe)
            with case_(6):
                play_mX90(qe)
                play_Y90(qe)
            with case_(7):
                play_mX90(qe)
                play_mY90(qe)
            with case_(8):
                play_Y90(qe)
                play_X90(qe)
            with case_(9):
                play_Y90(qe)
                play_mX90(qe)
            with case_(10):
                play_mY90(qe)
                play_X90(qe)
            with case_(11):
                play_mY90(qe)
                play_mX90(qe)
            with case_(12):
                play_X90(qe)
            with case_(13):
                play_mX90(qe)
            with case_(14):
                play_Y90(qe)
            with case_(15):
                play_mY90(qe)
            with case_(16):
                play_mX90(qe)
                play_Y90(qe)
                play_X90(qe)
            with case_(17):
                play_mX90(qe)
                play_mY90(qe)
                play_X90(qe)
            with case_(18):
                play_X180(qe)
                play_Y90(qe)
            with case_(19):
                play_X180(qe)
                play_mY90(qe)
            with case_(20):
                play_Y180(qe)
                play_X90(qe)
            with case_(21):
                play_Y180(qe)
                play_mX90(qe)
            with case_(22):
                play_X90(qe)
                play_Y90(qe)
                play_X90(qe)
            with case_(23):
                play_mX90(qe)
                play_Y90(qe)
                play_mX90(qe)

        # wait(4, qe)

if simulate:
    wait_init = 100
    avgs = 3

_total_rb_shots = num_of_sequences * max_circuit_depth * avgs

with program() as rb:
    depth = declare(int)
    saved_gate = declare(int)
    m = declare(int)
    n = declare(int)
    shot_i = declare(int)
    shot_i_st = declare_stream()
    assign(shot_i, 0)
    res1 = declare(bool)
    res1_st = declare_stream()
    res2 = declare(bool)
    res2_st = declare_stream()

    I1 = declare(fixed)
    Q1 = declare(fixed)
    I1_st = declare_stream()
    Q1_st = declare_stream()

    I2 = declare(fixed)
    Q2 = declare(fixed)
    I2_st = declare_stream()
    Q2_st = declare_stream()

    with for_(m, 0, m < num_of_sequences, m+1):
        sequence_list, inv_gate_list = generate_sequence()

        with for_(depth, 1, depth <= max_circuit_depth, depth+delta_depth):

            with for_(n, 0, n < avgs, n+1):

                assign(saved_gate, sequence_list[depth])
                assign(sequence_list[depth], inv_gate_list[depth-1])

                # reset_phase(rr1)
                # reset_phase(rr2)
                wait(wait_init)

                play_sequence(qe1, sequence_list, depth)
                play_sequence(qe2, sequence_list, depth)

                measure_macro(qe1, rr1, out1, I1, Q1, pi_12=pi_12)
                assign(res1, I1 >  dem1)
                save(res1, res1_st)
                save(I1, I1_st)
                save(Q1, Q1_st)

                measure_macro(qe2, rr2, out2, I2, Q2, pi_12=pi_12)
                assign(res2, I2 > dem2)
                save(res2, res2_st)
                save(I2, I2_st)
                save(Q2, Q2_st)

                assign(sequence_list[depth], saved_gate)

                assign(shot_i, shot_i + 1)
                save(shot_i, shot_i_st)

    with stream_processing():
        shot_i_st.save_all("shot_progress")
        res1_st.boolean_to_int().buffer(avgs).map(FUNCTIONS.average()).buffer(num_of_sequences, max_circuit_depth).save('res1')
        res2_st.boolean_to_int().buffer(avgs).map(FUNCTIONS.average()).buffer(num_of_sequences, max_circuit_depth).save('res2')

        #res_st.buffer(avgs).average().buffer(num_of_sequences, max_circuit_depth).save('res')
        I1_st.buffer(avgs).map(FUNCTIONS.average()).buffer(num_of_sequences, max_circuit_depth).save("I1_avg")
        Q1_st.buffer(avgs).map(FUNCTIONS.average()).buffer(num_of_sequences, max_circuit_depth).save("Q1_avg")
        I2_st.buffer(avgs).map(FUNCTIONS.average()).buffer(num_of_sequences, max_circuit_depth).save("I2_avg")
        Q2_st.buffer(avgs).map(FUNCTIONS.average()).buffer(num_of_sequences, max_circuit_depth).save("Q2_avg")


###########
# execute #
###########
qm = qmm.open_qm(config)

if simulate:
    job = qmm.simulate(config, rb, SimulationConfig(int(60000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()
    plt.legend("")
    raise Halted()


def _progress_last(raw):
    if raw is None:
        return None
    if isinstance(raw, dict) and "value" in raw:
        raw = raw["value"]
    arr = np.asarray(raw).reshape(-1)
    if arr.size == 0:
        return None
    return int(arr[-1])


job = qm.execute(rb, duration_limit=0, data_limit=0)

if SHOW_PROGRESS:
    try:
        from qualang_tools.results import fetching_tool
    except ImportError:
        fetching_tool = None

    if fetching_tool is not None and tqdm is not None:
        results = fetching_tool(job, data_list=["shot_progress"], mode="live")
        pbar = tqdm(total=_total_rb_shots, desc="Simultaneous RB", unit="shot")
        try:
            while results.is_processing():
                shot_progress = results.fetch_all()[0]
                last = _progress_last(shot_progress)
                if last is not None:
                    pbar.n = min(last, _total_rb_shots)
                    pbar.refresh()
                else:
                    time.sleep(0.05)
        finally:
            pbar.close()
    elif tqdm is not None:
        pbar = tqdm(total=None, desc="Simultaneous RB (running…)", bar_format="{desc} [{elapsed}]")
        try:
            while job.result_handles.is_processing():
                time.sleep(0.25)
        finally:
            pbar.close()

res_handles = job.result_handles
res_handles.wait_for_all_values()

res1value = res_handles.res1.fetch_all()
res2value = res_handles.res2.fetch_all()

I1value = res_handles.I1_avg.fetch_all()
Q1value = res_handles.Q1_avg.fetch_all()
I2value = res_handles.I2_avg.fetch_all()
Q2value = res_handles.Q2_avg.fetch_all()

avg_trace_values=[] # to hold averages of the traces
bare_values = True

if bare_values:
    avg_trace_values.append(np.average(I1value, axis=0))
    avg_trace_values.append(np.average(I2value, axis=0))
    init_vals = [-6e-5,6e-5,0.99]

else:
    avg_trace_values.append(1-np.average(res1value, axis=0))
    avg_trace_values.append(1-np.average(res2value, axis=0))
    init_vals = [1, 0.5, 0.98]

def power_law(m, a, b, p):
    return a * (p ** m) + b

x = np.linspace(1, max_circuit_depth, max_circuit_depth)
labels = [q1_no, q2_no]

_fit_loop = tqdm(range(2), desc="Fit & save qubits") if tqdm else range(2)
for i in _fit_loop:

    pars, cov = curve_fit(f=power_law, xdata=x, ydata=avg_trace_values[i], p0=init_vals, bounds=(-np.inf, np.inf),
                          maxfev=2000)
    stdevs = np.sqrt(np.diag(cov))
    one_minus_p = 1 - pars[2]
    r_c = one_minus_p * (1 - 1 / 2 ** 1)
    r_g = r_c / 1.875
    r_c_std = stdevs[2] * (1 - 1 / 2 ** 1)
    r_g_std = r_c_std / 1.875

    fid = np.round(1e2*(1-r_c), 2)

    plt.figure()
    plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    plt.title(f"Simultaneus RB : Qubit {labels[i]} Fidelity = {fid}% ", fontsize=14)
    plt.ylabel("Voltage (a.u.)", fontsize=16)
    plt.xlabel("No. of Cliffords", fontsize=16)
    plt.plot(avg_trace_values[i],".r",markersize=6,alpha=0.7) #plot averaged trace

    if bare_values:
        if i == 0: Ivalue = I1value
        if i == 1: Ivalue = I2value
        for j in range(Ivalue.shape[0]):
            plt.plot(Ivalue[j], '.', alpha=0.4, markersize=3)  # plot individual traces in 4k colour

    else:
        if i==0 : resvalue = res1value
        if i==1: resvalue = res2value
        for j in range(resvalue.shape[0]):
            plt.plot(1-resvalue[j], '.',alpha=0.4,markersize=3) #plot individual traces in 4k colour

    plt.plot(x, power_law(x, *pars), '-r')
    plt.grid()
    plt.show()

    print(f'~~~~~~~~~~~~~~ FOR QUBIT {labels[i]} ~~~~~~~~~~~~~~~~~')
    print('#########################')
    print('### Fitted Parameters ###')
    print('#########################')
    print(f'A = {pars[0]:.3} ({stdevs[0]:.1}), B = {pars[1]:.3} ({stdevs[1]:.1}), p = {pars[2]:.3} ({stdevs[2]:.1})')
    print('Covariance Matrix')
    print(cov)



    print('#########################')
    print('### Useful Parameters ###')
    print('#########################')
    print(f'1-p = {np.format_float_scientific(one_minus_p, precision=2)} ({stdevs[2]:.1}), '
          f'r_c = {np.format_float_scientific(r_c, precision=2)} ({r_c_std:.1}), '
          f'r_g = {np.format_float_scientific(r_g, precision=2)}  ({r_g_std:.1})')

    file_saver_(np.transpose([x, avg_trace_values[i], power_law(x, *pars)]), file_name=__file__,
             master_folder=ExpName, header_string="Simultaenous RB", suffix=f"{i}")