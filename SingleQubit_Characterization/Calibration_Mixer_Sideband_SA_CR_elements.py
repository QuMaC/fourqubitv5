import os
from qm import QuantumMachinesManager
import time
from Configuration_Files.configuration_4qubitsv3 import *
import sys
from Helper_Functions.auto_mixer_tools_visa import KeysightXSeries
from qm.qua import *
from Helper_Functions.macros import *
from scipy.optimize import minimize
import json
import pyvisa as visa

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
qm = qmm.open_qm(config)

address = "TCPIP0::192.168.0.117::inst0::INSTR"
calib = KeysightXSeries(address, qm)

qe_freq = {}
for i in range(1, n_qubits + 1):
    qe_freq[f"q{i}"] = [q_LO[f"{i}"], q_IF[f"{i}"], f"mixer_q{i}"]
    qe_freq[f"rr{i}"] = [rr_LO[f"{i}"], rr_IF[f"{i}"], f"mixer_rr{i}"]
    qe_freq[f"q12_{i}"] = [q_LO[f"{i}"], q12_IF[f"{i}"], f"mixer_q12_{i}"]

for c_no in control_qubits:
    for t_no in connectivity[c_no]:
        qe_freq[f"cr_c{c_no}t{t_no}"] = [q_LO[f"{c_no}"], q_IF[f"{t_no}"], f"mixer_cr_c{c_no}t{t_no}"]
        qe_freq[f"cr_ac_c{c_no}t{t_no}"] = [q_LO[f"{c_no}"], q_IF[f"{t_no}"], f"mixer_cr_ac_c{c_no}t{t_no}"]

cr_list = [elem for elem in config['elements'].keys() if 'cr' in elem]

for elem in cr_list:

    # if elem not in ['cr_c5t4', 'cr_ac_c5t4']:
    #     continue

    print(elem)

    q_no = elem
    qe = q_no
    if 'ac' in q_no:
        q_n = int(q_no[7])
    else:
        q_n = int(q_no[4])

    with open('../Configuration_Files/Calibrations/iq_imbalance.json') as f:
        iq_imbalance = json.load(f)

    rm = visa.ResourceManager()
    LO_real = rm.open_resource(LO_IP_dict[f'q_LO'][f'{((q_n-1) // 2)+1}'])
    LO_val = LO_real.query_ascii_values('SOUR:FREQ:CW?')[0]

    qe_LO, qe_IF, mixer = qe_freq[qe]
    qe_LO = LO_val
    center_freq = qe_LO - qe_IF  # rr_LO
    span = 50


    def callback(*, intermediate_result):
        print(intermediate_result.fun)
        print(intermediate_result.x)
        # calib.set_center_freq(qe_LO + qe_IF)
        # calib.set_span(span)
        # calib.active_marker(1)
        # calib.set_marker_freq(1, qe_LO + qe_IF)
        # print("power {0}".format(calib.query_marker(1)))
        # time.sleep(1)
        # calib.set_center_freq(center_freq)
        # calib.set_span(span)
        # calib.active_marker(1)
        # calib.set_marker_freq(1, center_freq)

        # q.append(intermediate_result.x)


    def set_IQ_imbalance_get_leakage(imbalance_arr, qe, qe_freq, verbose=True):
        a_imb, p_imb = imbalance_arr
        qe_LO, qe_IF, mixer = qe_freq[qe]
        qm.set_mixer_correction(mixer, int(qe_IF), int(qe_LO), IQ_imbalance(a_imb, p_imb))
        time.sleep(2)
        leakage = calib.query_marker(1)
        if verbose:
            print("Current leakage is {0} dBm".format(leakage))
        if leakage < -90:
            return 0  # return low constant values so that the optimization loop quits

        return abs(leakage + 90)



    calib_amp = cr_amp[qe]


    with program() as mixer_calibration_pulse:
        with infinite_loop_():
            play("const" * amp(calib_amp), qe)

    try:
        if 'ac' in qe:
            bulk_switch(qe=keyer(f'q{qe[9]}', dac_mapping), ip=sw_ip, switches=switches)
        else:
            bulk_switch(qe=keyer(f'q{qe[4]}', dac_mapping), ip=sw_ip, switches=switches)
    except:
        print('Switch not accessible for some reason')

    job = qm.execute(mixer_calibration_pulse)

    calib.set_bandwidth(5)
    calib.set_sweep_points(501)

    calib.set_center_freq(center_freq)
    calib.set_span(span)
    calib.active_marker(1)
    calib.set_marker_freq(1, center_freq)

    init_vals = [iq_imbalance[qe]["a"], iq_imbalance[qe]["p"]]


    init_abs = [0.3-abs(init_vals[0]), 0.3 - abs(init_vals[1])]

    if init_abs[0] < 0.05:
        init_vals = [iq_imbalance[qe]["a"]*0.5, iq_imbalance[qe]["p"]]

    if init_abs[1] < 0.05:
        init_vals = [init_vals[0], iq_imbalance[qe]["p"]*0.5]

    # lower_bound = -60
    bnds = ((-0.3, 0.3), (-0.3, 0.3))

    fatol = 1e-2  # 1e-4 change in DC offset or gain/phase
    # fatol = 3  # dB change tolerance
    maxiter = 50  # 50 iterations should be more than enough, but can be changed.
    initial_simplex = np.zeros([3, 2])

    # initial_simplex[0, :] = [0, -0.2]
    # initial_simplex[1, :] = [0.2, 0.2]
    # initial_simplex[2, :] = [-0.2, -0.2]
    initial_simplex[0, :] = [0.19, 0.19]
    initial_simplex[1, :] = [0.19, -0.19]
    initial_simplex[2, :] = [-0.19, 0]

    args = [qe, qe_freq]
    res = minimize(set_IQ_imbalance_get_leakage,
                   x0=np.array(init_vals),
                   args=(qe, qe_freq),
                   method="Nelder-Mead",
                   bounds=bnds,
                   callback=callback,
                   tol=1,
                   options={
                       # "xatol": xatol,
                       "fatol": fatol,
                       #                 "initial_simplex": initial_simplex,
                       "maxiter": maxiter,
                   }
                   )

    fin_val = calib.query_marker(1)
    print(f"For quantum element {qe}")
    print(f"Final reject band leakage is {fin_val} dBm")

    center_freq = qe_LO + qe_IF
    calib.set_center_freq(center_freq)
    calib.set_marker_freq(1, center_freq)
    print(f"Upconverted sideband power is {calib.query_marker(1)} dBm")
    print(f"Calibrated IQ imbalance tuple is {res.x}")

    # if os.path.isfile('./offset_sideband_values.json'):
    #     with open('offset_sideband_values.json', 'r') as f:
    #         calib_numbers = json.load(f)
    #         f.close()
    # else:
    #     calib_numbers = {q_no: {'offset': 0, 'sideband': 0}}
    #
    # calib_numbers[q_no]['sideband'] = fin_val
    #
    # with open('offset_sideband_values.json', 'w') as f:
    #     json.dump(calib_numbers, f, indent=6)
    #     f.close()

    a, p = res.x
    iq_imbalance[qe]["a"] = a
    iq_imbalance[qe]["p"] = p

    with open('../Configuration_Files/Calibrations/iq_imbalance.json', "w") as outfile:
        json.dump(iq_imbalance, outfile, indent=4)

    # calib.close()
    # qm.close()
