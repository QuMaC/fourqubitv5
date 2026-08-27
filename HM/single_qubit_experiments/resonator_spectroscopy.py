from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib import pyplot as plt
from Helper_Functions.macros import update_config_rr
from Helper_Functions.helper_functionsv2 import file_saver_
from HM.utilities.files_utils import get_save_path
from termcolor import cprint


ExpName = "resonator_spectroscopy"
path_to_save = get_save_path(suffix=ExpName)
# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------
save_data = False
simulate = False

# Resonator to measure (1-indexed)
rr_no = 1
q_no = rr_no
rr = f"rr{rr_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(rr_no)]
rep_rate_clk = 2500

# Frequency sweep (Hz). Tune around your expected resonance.
f_min = -40e6
f_max = 20e6
df = 0.1e6

# Readout pulse
rr_amp = 0.005
integ_len = 4000
update_config_rr(config, q_no, rr_no, rr_amp, integ_len)

# Averages per frequency point
n_avg = 2000


freq_list = np.arange(f_min, f_max, df)
zeros = np.where(freq_list == 0)[0]
zero_i = zeros[0] if len(zeros) else None

# Get LO frequency for converting IF sweep to absolute frequency (GHz)
_val = rr_LO[f"{q_no}"]
rr_LO_GHz = float(getattr(_val, "magnitude", _val))
if rr_LO_GHz > 1e6:  # value in Hz
    rr_LO_GHz = rr_LO_GHz * 1e-9


with program() as rr_spec:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    f = declare(int)

    with for_(n, 0, n < n_avg, n + 1):
        with for_(f, f_min, f < f_max, f + df):
            update_frequency(rr, f)
            wait(rep_rate_clk - ro_len, rr)
            measure(
                "readout",
                rr,
                None,
                demod.full("integW_cos", I, out),
                demod.full("integW_minus_sin", Q, out),
            )
            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(freq_list)).average().save("I")
        Q_st.buffer(len(freq_list)).average().save("Q")

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

if simulate:
    simulation_config = SimulationConfig(
        duration=200000,
        simulation_interface=LoopbackInterface(
            [("con2", 7, "con2", 1), ("con2", 8, "con2", 2)]
        ),
    )
    job = qmm.simulate(config, rr_spec, simulation_config)
    job.get_simulated_samples().con2.plot()
    plt.show()
    sys.exit(0)

qm = qmm.open_qm(config)
job = qm.execute(rr_spec)
job.result_handles.wait_for_all_values()
I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()


freq_list_GHz = rr_LO_GHz + freq_list * 1e-9
sig = I + 1j * Q

if zero_i is not None:
    freq_list_GHz = np.delete(freq_list_GHz, zero_i)
    sig = np.delete(sig, zero_i)

# Optional: apply electrical delay and phase offset from calibration
e_delay_ns = elec_delay_ns.get(str(rr_no), 0)
p_offset_rad = phase_offset_rad.get(str(rr_no), 0.0)
sig_corrected = sig * np.exp(1j * 2 * np.pi * freq_list_GHz * e_delay_ns + 1j * p_offset_rad)

phase = np.angle(sig_corrected)
real_part = np.real(sig_corrected)
imag_part = np.imag(sig_corrected)
mag = np.abs(sig)

# Resonance: minimum of magnitude
f_res_idx = np.argmin(mag)
f_res_GHz = freq_list_GHz[f_res_idx]


fig, axes = plt.subplots(1, 3, figsize=(12, 4))

axes[0].plot(freq_list_GHz, phase)
axes[0].axvline(x=f_res_GHz, linestyle="--", color="gray")
axes[0].set_xlabel("Frequency (GHz)")
axes[0].set_ylabel("Phase (rad)")
axes[0].set_title(f"Resonator spectroscopy (phase): f_res = {f_res_GHz:.6f} GHz")
axes[0].grid(True)

axes[1].plot(freq_list_GHz, real_part, label="Real")
axes[1].plot(freq_list_GHz, imag_part, label="Imag")
axes[1].axvline(x=f_res_GHz, linestyle="--", color="gray")
axes[1].set_xlabel("Frequency (GHz)")
axes[1].set_ylabel("I/Q")
axes[1].set_title(f"Resonator spectroscopy (IQ): f_res = {f_res_GHz:.6f} GHz")
axes[1].legend()
axes[1].grid(True)

axes[2].plot(freq_list_GHz, mag)
axes[2].axvline(x=f_res_GHz, linestyle="--", color="gray")
axes[2].set_xlabel("Frequency (GHz)")
axes[2].set_ylabel("Magnitude")
axes[2].set_title(f"Resonator spectroscopy (magnitude): f_res = {f_res_GHz:.6f} GHz")
axes[2].grid(True)

plt.tight_layout()
plt.show(block=False)

plt.savefig(f"{path_to_save }.png")
cprint(f"file saved as: {path_to_save }.png", "green")
print(f"Detected readout resonator frequency: {f_res_GHz} GHz")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
if save_data:
    data = np.column_stack(
        (freq_list_GHz, phase, real_part, imag_part, mag)
    )
    file_saver_(
        data,
        file_name=__file__,
        suffix=rr,
        master_folder=ExpName,
        header_string="Frequency (GHz), Phase, Real, Imaginary, Magnitude",
    )
