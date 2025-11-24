import os
from qm import QuantumMachinesManager
import time
from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.auto_mixer_tools_visa import KeysightXSeries
from qm.qua import *
from Helper_Functions.helper_functionsv2 import *
from Helper_Functions.macros import *
import json
import sys
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

rm = visa.ResourceManager()

cr_list = [elem for elem in config['elements'].keys() if 'cr' in elem]

for elem in cr_list:

    print(elem)

    q_no = elem
    qe = q_no
    q_n = int(q_no[4])

    with open('../Configuration_Files/Calibrations/iq_imbalance.json') as f:
        iq_imbalance = json.load(f)

    rm = visa.ResourceManager()
    LO_real = rm.open_resource(LO_IP_dict[f'q_LO'][f'{((q_n-1) // 2)+1}'])
    LO_val = LO_real.query_ascii_values('SOUR:FREQ:CW?')[0]


    # q_no = sys.argv[1]
    # qe = q_no
    # q_n = int(q_no[-1])

    # qe = q_no  # "rr1"  #RF switch A pos 1 => q2, rr2 else q1, rr1

    # LO_real = rm.open_resource(LO_IP_dict[f'{q_no[0:-1]}_LO'][f'{((q_n-1) // 2)+1}'])
    # LO_val = LO_real.query_ascii_values('SOUR:FREQ:CW?')[0]


    with program() as mixer_calibration_pulse:
        with infinite_loop_():
            # for qe_temp in qe_freq.keys():
            play("const" * amp(0.0), qe)

    try:
        bulk_switch(qe=keyer(qe, dac_mapping), ip=sw_ip, switches=switches)
    except:
        print('Switch not accessible for some reason')

    job = qm.execute(mixer_calibration_pulse)
    center_freq, qe_ch = qe_freq[qe]
    center_freq = LO_val
    span = 50
    calib.set_bandwidth(5)
    calib.set_sweep_points(501)

    calib.set_center_freq(center_freq)
    calib.set_span(span)
    calib.active_marker(1)
    calib.set_marker_freq(1, center_freq)


    # q=[]

    def callback(*, intermediate_result):
        print(intermediate_result.fun)
        print(intermediate_result.x)
        # q.append(intermediate_result.x)


    def set_dc_offset_get_leakage(offset_arr, qe, verbose=True):
        I_offset, Q_offset = offset_arr[0], offset_arr[1]

        qm.set_output_dc_offset_by_element(qe, "I", I_offset)
        qm.set_output_dc_offset_by_element(qe, "Q", Q_offset)

        time.sleep(2)

        leakage = calib.query_marker(1)
        if verbose:
            print("Current leakage is {0} dBm".format(leakage))

        if leakage < -100:
            return 0

        return abs(leakage + 99)  # -99 dBm good target


    from scipy.optimize import minimize

    dacs = dac_mapping[q_no][-1]
    contro = dac_mapping[q_no][0]

    init_vals = [dc_offsets[f'con{contro}'][f'{dacs[0]}'], dc_offsets[f'con{contro}'][f'{dacs[1]}']]


    bnds = ((-0.3, 0.3), (-0.3, 0.3))

    # xatol = 1e-4  # 1e-4 change in DC offset or gain/phase
    fatol = 1  # dB change tolerance
    maxiter = 50  # 50 iterations should be more than enough, but can be changed.
    initial_simplex = np.zeros([3, 2])
    # initial_simplex[0, :] = [0, 0]
    # initial_simplex[1, :] = [0, -0.2]
    # initial_simplex[2, :] = [-0.1, 0]
    #
    initial_simplex[0, :] = [0, -0.2]
    initial_simplex[1, :] = [0.2, 0.2]
    initial_simplex[2, :] = [-0.2, 0.2]

    # initial_simplex[0, :] = [0, -0.15]
    # initial_simplex[1, :] = [0.15, 0.15]
    # initial_simplex[2, :] = [-0.15, 0.15]

    res = minimize(set_dc_offset_get_leakage,
                   x0=np.array(init_vals),
                   args=qe,
                   method="Nelder-Mead",
                   bounds=bnds,
                   callback=callback,
                   # tol=0.1,
                   options={
                       # "xatol": xatol,
                       "fatol": fatol,
                       #                 "initial_simplex": initial_simplex,
                       "maxiter": maxiter,
                   }
                   )

    fin_val = calib.query_marker(1)

    print("Final leakage is {0} dBm".format(fin_val))
    print(f"Calibrated Mixer offsets for {qe} are {res.x}")

    if os.path.isfile('./offset_sideband_values.json'):
        with open('offset_sideband_values.json', 'r') as f:
            calib_numbers = json.load(f)
            f.close()
    else:
        calib_numbers = {q_no: {'offset': 0, 'sideband': 0}}

    calib_numbers.update({q_no: {"offset": fin_val, "sideband": 0}})

    with open('offset_sideband_values.json', 'w') as f:
        json.dump(calib_numbers, f, indent=6)
        f.close()

    with open('../Configuration_Files/Calibrations/dc_offsets.json') as f:
        dc_offsets = json.load(f)

    dc_offsets[f"con{qe_ch[0]}"][f"{qe_ch[1][0]}"] = res.x[0]
    dc_offsets[f"con{qe_ch[0]}"][f"{qe_ch[1][1]}"] = res.x[1]

    with open('../Configuration_Files/Calibrations/dc_offsets.json', "w") as outfile:
        json.dump(dc_offsets, outfile, indent=4)

    # calib.close()
