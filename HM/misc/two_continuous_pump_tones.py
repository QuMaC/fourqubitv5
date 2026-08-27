import time

from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import config, qm_ip, cluster_name

element1 = "q1"
element2 = "q2"

 
freq1_Hz = 0
freq2_Hz = 0
 
amp1 = 0.1
amp2 = 0.1
 
phase1_turns = 0.0
phase2_turns = 0.0

chunk_duration_ns = 100_000_000

with program() as two_pumps:
    n = declare(int)

    update_frequency(element1, freq1_Hz)
    update_frequency(element2, freq2_Hz)

    frame_rotation_2pi(phase1_turns, element1)
    frame_rotation_2pi(phase2_turns, element2)

    with for_(n, 0, n >= 0, n + 1):
        align(element1, element2)
        play("const" * amp(amp1), element1, duration=chunk_duration_ns)
        play("const" * amp(amp2), element2, duration=chunk_duration_ns)

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
qm = qmm.open_qm(config)
job = qm.execute(two_pumps)

print(f"Two pumps: {element1} (f={freq1_Hz} Hz, a={amp1}, φ={phase1_turns}) | {element2} (f={freq2_Hz} Hz, a={amp2}, φ={phase2_turns})")
print("Stop with Ctrl+C.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    job.halt()
    print("Job halted.")
finally:
    qm.close()
