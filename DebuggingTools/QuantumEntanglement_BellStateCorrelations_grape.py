"""
GRAPE-enabled copy of QuantumEntanglement_BellStateCorrelations.py.

Toggle USE_GRAPE = True to swap the calibrated flat-top echoed CR for the
GRAPE-optimized waveform stored at GRAPE_PULSE_PATH. Everything else
(N_shots, demarcations, readout, plotting) is identical to the original.
"""
from qm import SimulationConfig
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from matplotlib import pyplot as plt
from Helper_Functions.macros import *

# -------- GRAPE switch --------
USE_GRAPE = False
GRAPE_PULSE_PATH = (
    r"D:\QUA\Master_Scripts\fourqubitv5_Hari\HM\Thesis\grape\grape_pulse_T440ns.json"
)
# ------------------------------

save_data = False
simulate = False
###################
# The QUA program #
###################

N_shots = 25000
wait_init = 250000
wait_rr = 8


c_no, t_no = 1, 2
qe_c = f"q{c_no}"
rr_c = f"rr{c_no}"
out_c = adc_mapping[rr_c]
qe_t = f"q{t_no}"
rr_t = f"rr{t_no}"
out_t = adc_mapping[rr_t]

AC_flag = False

qe_cr = f"cr_c{c_no}t{t_no}"
qe_ac = f"cr_ac_c{c_no}t{t_no}"

p_cr = cr_phase[qe_cr]
p_ac = cr_phase[qe_ac]

qe_list_local = [qe_c, qe_t, qe_cr, qe_ac]

dem1 = demarcations[str(t_no)]
dem2 = demarcations[str(c_no)]

if simulate:
    wait_init = 100

# -------- GRAPE registration --------
if USE_GRAPE:
    from HM.Thesis.grape.qm_grape_helpers import (
        register_grape_cr_pulse,
        CNOT_macro_grape,
    )
    grape_meta = register_grape_cr_pulse(
        config, c_no=c_no, t_no=t_no, grape_json_path=GRAPE_PULSE_PATH,
    )
    print("[GRAPE] registered pulse:")
    print(f"    pair       : {grape_meta['pair_key']}")
    print(f"    T_total    : {grape_meta['T_total_ns']} ns")
    print(f"    T_per_cr   : {grape_meta['T_per_cr_ns']} ns")
    print(f"    F_unitary  : {grape_meta['meta']['F_grape_unitary']:.5f}")
    print(f"    K_DCT      : {grape_meta['meta']['K_dct']}")
    print(f"    BW         : {grape_meta['meta']['bandwidth_MHz']:.2f} MHz")

    def _CNOT(qe_c_, qe_t_, AC_flag_):
        if AC_flag_:
            raise NotImplementedError("USE_GRAPE only supports AC_flag=False")
        CNOT_macro_grape(qe_c_, qe_t_)

else:
    def _CNOT(qe_c_, qe_t_, AC_flag_):
        CNOT_macro(qe_c_, qe_t_, AC_flag_)
# ------------------------------------


with program() as Bell_state:

    n = declare(int)
    I1 = declare(fixed)
    I2 = declare(fixed)
    bool1 = declare(bool)
    bool2 = declare(bool)
    Q_dummy = declare(fixed)

    I1_st = declare_stream()
    bool1_st = declare_stream()
    I2_st = declare_stream()
    bool2_st = declare_stream()

    with for_(n, 0, n < N_shots, n + 1):

        cooldown(time=wait_init)
        align(*qe_list_local)

        Hadamard(qe_c)
        align(qe_c, qe_cr)
        _CNOT(qe_c, qe_t, AC_flag)

        measure_macro(qe_t, rr_t, out_t, I1, Q_dummy, pi_12=True)
        measure_macro(qe_c, rr_c, out_c, I2, Q_dummy, pi_12=True)
        assign(bool1, I1 > dem1)
        assign(bool2, I2 > dem2)

        save(I1, I1_st)
        save(I2, I2_st)
        save(bool1, bool1_st)
        save(bool2, bool2_st)

    with stream_processing():

        I1_st.save_all('I1')
        I2_st.save_all('I2')

        bool1_st.save_all('bool1')
        bool2_st.save_all('bool2')


######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

##############
# Simualtion #
##############

if simulate:
    job = qmm.simulate(config, Bell_state, SimulationConfig(int(10000)))
    samples = job.get_simulated_samples()
    qe_t_I = dac_mapping[f'{qe_t}'][1][0]
    qe_t_Q = dac_mapping[f'{qe_t}'][1][1]
    qe_c_I = dac_mapping[f'{qe_c}'][1][0]
    qe_c_Q = dac_mapping[f'{qe_c}'][1][1]
    rr_c_I = dac_mapping[f'rr{qe_c[-1]}'][1][0]
    rr_c_Q = dac_mapping[f'rr{qe_c[-1]}'][1][1]
    rr_t_I = dac_mapping[f'rr{qe_t[-1]}'][1][0]
    rr_t_Q = dac_mapping[f'rr{qe_t[-1]}'][1][1]
    con_ctrl = dac_mapping[f'{qe_c}'][0]
    con_tgt = dac_mapping[f'{qe_t}'][0]
    con_ctrl = f'con{con_ctrl}'
    con_tgt = f'con{con_tgt}'
    control_I = getattr(samples, con_ctrl).analog[f'{qe_c_I}']
    control_Q = getattr(samples, con_ctrl).analog[f'{qe_c_Q}']
    target_I = getattr(samples, con_tgt).analog[f'{qe_t_I}']
    target_Q = getattr(samples, con_tgt).analog[f'{qe_t_Q}']
    rd_c_I = getattr(samples, con_ctrl).analog[f'{rr_c_I}']
    rd_c_Q = getattr(samples, con_ctrl).analog[f'{rr_c_Q}']
    rd_t_I = getattr(samples, con_tgt).analog[f'{rr_t_I}']
    rd_t_Q = getattr(samples, con_tgt).analog[f'{rr_t_Q}']
    stark_I = getattr(samples, 'con3').analog['5']
    stark_Q = getattr(samples, 'con3').analog['6']
    plt.figure()
    plt.plot(control_I, label='control_I')
    plt.plot(control_Q, label='control_Q')
    plt.plot(target_I, label='target_I')
    plt.plot(target_Q, label='target_Q')
    plt.plot(rd_c_I, label='rd_c_I')
    plt.plot(rd_c_Q, label='rd_c_Q')
    plt.plot(rd_t_I, label='rd_t_I')
    plt.plot(rd_t_Q, label='rd_t_Q')
    plt.plot(stark_I, label='stark_I')
    plt.plot(stark_Q, label='stark_Q')
    plt.grid()
    plt.legend()

    plt.show(block=False)

    raise Halted()

#############
# execution #
#############
try:
    qm = qmm.open_qm(config)
    job = qm.execute(Bell_state)
except:
    raise Warning('job aint happening')
res_handles = job.result_handles
I1_handle = job.result_handles.get("I1")
I2_handle = job.result_handles.get("I2")
bool1_handle = job.result_handles.get("bool1")
bool2_handle = job.result_handles.get("bool2")

job.result_handles.wait_for_all_values()

I1 = I1_handle.fetch_all()
I2 = I2_handle.fetch_all()
bool1 = bool1_handle.fetch_all()
bool2 = bool2_handle.fetch_all()

stats = []
for i in range(N_shots):
    stats.append([bool1[i], bool2[i]])


def plot_correlations(stats):

    c00, c01, c10, c11 = 0, 0, 0, 0

    for m in stats:

        if not m[0][0] and not m[1][0]:
            c00 += 1
        elif not m[0][0] and m[1][0]:
            c01 += 1
        elif m[0][0] and not m[1][0]:
            c10 += 1
        elif m[0][0] and m[1][0]:
            c11 += 1

    tot_c = c00 + c01 + c10 + c11
    c00, c01, c10, c11 = c00 / tot_c, c01 / tot_c, c10 / tot_c, c11 / tot_c

    # --- Fidelity to ideal |Phi+> = (|00> + |11>) / sqrt(2) ---
    # Diagonal Bell-state fidelity (correlator-only bound; tight if dephasing
    # only): F_diag = P(00) + P(11). Strictly this is a measurement-basis-only
    # estimate; a full Bell tomography (XX/YY/ZZ) is needed for the Z2-corrected
    # state fidelity. We also report the classical fidelity to the ideal
    # measured distribution {00:0.5, 01:0, 10:0, 11:0.5}:
    #     F_class = sum_k sqrt(p_meas[k] * p_ideal[k]) ** 2
    #             = (sqrt(c00 * 0.5) + sqrt(c11 * 0.5)) ** 2
    #             = 0.5 * (sqrt(c00) + sqrt(c11)) ** 2
    F_diag = c00 + c11
    F_class = 0.5 * (np.sqrt(c00) + np.sqrt(c11)) ** 2
    coincidence = c00 + c11
    parity = c00 + c11 - c01 - c10

    label = "GRAPE" if USE_GRAPE else "calibrated flat-top"
    print()
    print("=" * 60)
    print(f"Bell-state correlations  q{c_no} (control)  q{t_no} (target)  [{label}]")
    print("=" * 60)
    print(f"  N_shots                          : {tot_c}")
    print(f"  P(00), P(01), P(10), P(11)       : "
          f"{c00:.4f}, {c01:.4f}, {c10:.4f}, {c11:.4f}")
    print(f"  P(00)+P(11)  (coincidence)       : {coincidence*100:.2f} %")
    print(f"  ZZ parity                        : {parity:+.4f}")
    print(f"  Diagonal Bell fidelity F_diag    : {F_diag*100:.2f} %")
    print(f"  Classical fidelity to ideal Phi+ : {F_class*100:.2f} %")
    if USE_GRAPE:
        print(f"  GRAPE simulator-predicted F_unitary "
              f": {grape_meta['meta']['F_grape_unitary']*100:.2f} % "
              f"(from {grape_meta['meta']['datetime']})")
    print("=" * 60)
    print()

    suffix = " (GRAPE)" if USE_GRAPE else ""
    plt.figure()
    plt.imshow(np.array([[c00, c01], [c10, c11]]))
    plt.xticks([0, 1])
    plt.yticks([0, 1])
    plt.ylabel("Control")
    plt.xlabel("Target")
    plt.text(0, 0, f"{100 * c00:.1f}%", ha="center", va="center", color="k")
    plt.text(1, 0, f"{100 * c01:.1f}%", ha="center", va="center", color="w")
    plt.text(0, 1, f"{100 * c10:.1f}%", ha="center", va="center", color="w")
    plt.text(1, 1, f"{100 * c11:.1f}%", ha="center", va="center", color="k")
    plt.title(f"Quantum Correlations{suffix}: N={tot_c}, "
              f"F_diag = {F_diag*100:.2f}%")
    plt.show(block=True)


plot_correlations(stats)
