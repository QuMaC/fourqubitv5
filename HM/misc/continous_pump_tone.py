"""
Continuous pump tone: OPX plays a constant-amplitude tone on a chosen element until the job is halted.
Run from project root: python -m HM.misc.continous_pump_tone
Stop with Ctrl+C (halts the job and closes the QM).
"""
import time

from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import config, qm_ip, cluster_name

# ---------------------------------------------------------------------------
# Options: set element and fixed amplitude
# ---------------------------------------------------------------------------
# Element to pump: any element that has "const" (e.g. "q1", "q2", "stark_6")
element = "q1"

# Fixed amplitude (0.0 to 1.0 typical; scale matches config const_wf base 0.4)
pump_amp = 0.1

# Duration per play in ns (long chunk to reduce loop overhead). 100 ms = 100_000_000 ns.
chunk_duration_ns = 100_000_000

# ---------------------------------------------------------------------------
# QUA program: play continuous tone until job is halted
# ---------------------------------------------------------------------------
with program() as continuous_pump:
    n = declare(int)
    # Infinite loop: condition n >= 0 is always true
    with for_(n, 0, n >= 0, n + 1):
        play("const" * amp(pump_amp), element, duration=chunk_duration_ns)


qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
qm = qmm.open_qm(config)
job = qm.execute(continuous_pump)

print(f"Continuous pump running: element={element}, amp={pump_amp}")
print("Stop with Ctrl+C to halt the job and close the QM.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    job.halt()
    print("Job halted.")
finally:
    qm.close()
