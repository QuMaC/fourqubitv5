"""
intro_to_integration.py: Demonstrate usage of the integration in the measure statement
Author: Gal Winer - Quantum Machines
Created: 31/12/2020
Revised by Tomer Feld - Quantum Machines
Revision date: 24/04/2022
"""

from qm import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig, LoopbackInterface
from Configuration_Files.configuration_4qubitsv3 import *
import matplotlib.pyplot as plt

# Open communication with the server.
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

q_no = 7
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]
pi_len_config = pi_len_ns[f"{q_no}"]

rr_I = dac_mapping[rr][1][0]
rr_Q = dac_mapping[rr][1][0]

avgs = 1000



con = f'con{dac_mapping[qe][0]}'

# Sliced demodulation parameters
num_segments = 25
seg_length = ro_len // (4 * num_segments)

# Moving window demodulation parameters
samples_per_chunk = 25
chunks_per_window = 3
arr_size = 10


time_factor = 0.25

config["integration_weights"][f"new_dummy_cos{q_no}"] = {}
config["integration_weights"][f"new_dummy_cos{q_no}_mw"] = {}
config["integration_weights"][f"new_dummy_minusSin{q_no}"] = {}
config["integration_weights"][f"new_dummy_minusSin{q_no}_mw"] = {}




config["integration_weights"][f"new_dummy_cos{q_no}"]["cosine"] = [
    (np.cos(optimal_readout_phase[f"rr{q_no}"]), int(ro_len))]

config["integration_weights"][f"new_dummy_cos{q_no}"]["sine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(ro_len))]

config["integration_weights"][f"new_dummy_minusSin{q_no}"]["cosine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(ro_len))]

config["integration_weights"][f"new_dummy_minusSin{q_no}"]["sine"] = [
    (-np.cos(optimal_readout_phase[f"rr{q_no}"]), int(ro_len))]

config["integration_weights"][f"new_dummy_cos{q_no}_mw"]["cosine"] = [
    (np.cos(optimal_readout_phase[f"rr{q_no}"]), int(samples_per_chunk)*4*arr_size)]

config["integration_weights"][f"new_dummy_cos{q_no}_mw"]["sine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(samples_per_chunk)*4*arr_size)]

config["integration_weights"][f"new_dummy_minusSin{q_no}_mw"]["cosine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(samples_per_chunk)*4*arr_size)]

config["integration_weights"][f"new_dummy_minusSin{q_no}_mw"]["sine"] = [
    (-np.cos(optimal_readout_phase[f"rr{q_no}"]), int(samples_per_chunk)*4*arr_size)]

config["pulses"][f"q{q_no}_ro_pulse"]["integration_weights"]['new_dummy_cos'] = f"new_dummy_cos{q_no}"
config["pulses"][f"q{q_no}_ro_pulse"]["integration_weights"]['new_dummy_minusSin'] = f"new_dummy_minusSin{q_no}"

config["pulses"][f"q{q_no}_ro_pulse"]["integration_weights"]['new_dummy_cos_mw'] = f"new_dummy_cos{q_no}_mw"

with program() as measureProg:
    ind = declare(int)
    I = declare(fixed)

    int_stream = declare_stream()
    acc_int_stream = declare_stream()
    mov_int_stream = declare_stream()
    raw_adc = declare_stream(adc_trace=True)

    sliced_demod_res = declare(fixed, size=int(num_segments))
    acc_demod_res = declare(fixed, size=int(num_segments))
    mov_demod_res = declare(fixed, size=arr_size)

    # with for_(n, 0, n < av, n + 1):

    measure("readout", rr, raw_adc, demod.full("integW_cos", I, out))
    save(I, "full")

    reset_phase(rr)
    measure("readout", rr, None, demod.sliced("new_dummy_cos", sliced_demod_res, seg_length, out))
    with for_(ind, 0, ind < num_segments, ind + 1):  # save a QUA array
        save(sliced_demod_res[ind], int_stream)

    reset_phase(rr)
    measure("readout", rr, None, demod.accumulated("new_dummy_cos", acc_demod_res, seg_length, out))
    with for_(ind, 0, ind < num_segments, ind + 1):  # save a QUA array
        save(acc_demod_res[ind], acc_int_stream)

    measure(
        "readout",
        rr,
        None,
        demod.moving_window("new_dummy_cos_mw", mov_demod_res, samples_per_chunk, chunks_per_window, element_output=out)
    )
    with for_(ind, 0, ind < num_segments, ind + 1):
        save(mov_demod_res[ind], mov_int_stream)

    with stream_processing():
        int_stream.save_all("demod_sliced")
        acc_int_stream.save_all("demod_acc")
        mov_int_stream.save_all("demod_mov")
        raw_adc.input1().save("raw_input")

# job = qmm.simulate(
#     config,
#     measureProg,
#     SimulationConfig(int(6*ro_len), simulation_interface=LoopbackInterface([(con, rr_I, con, int(out[-1]))]))
# )

qm = qmm.open_qm(config)
job = qm.execute(measureProg)

res = job.result_handles
full = res.full.fetch_all()["value"]
print(f"Result of full demodulation: {full}")
sliced = res.demod_sliced.fetch_all()["value"]
print(f"Result of sliced demodulation in {num_segments} segments:{sliced}")

[f, (ax1, ax2)] = plt.subplots(nrows=1, ncols=2)
ax1.plot(res.demod_sliced.fetch_all(), "o-")
ax1.set_title("sliced demod")
ax1.set_xlabel("slice number")

ax2.plot(res.demod_acc.fetch_all(), "o-")
ax2.set_title("acc demodulation")
ax2.set_xlabel("slice number")
plt.show(block=False)

plt.figure()
plt.plot(res.raw_input.fetch_all() / 2**12)
plt.xlabel("t[ns]")
plt.ylabel("output [V]")
plt.title("Raw output")
plt.show(block=False)

plt.figure()
plt.plot(res.demod_mov.fetch_all()["value"] / 2**12, "o-")
plt.xlabel("sample number")
plt.title("moving windows")
plt.show(block=False)