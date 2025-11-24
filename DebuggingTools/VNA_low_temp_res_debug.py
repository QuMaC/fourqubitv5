import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.optimize import curve_fit
from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.instrument_helperfunctions import *
from datetime import datetime
import pyvisa as visa
import time
import scipy as sp


q_no = 5

turn_off = 0

test_name =r'\Cu_cavity_'
if q_no <= 6:
    test_name = fr"\Ring{qubit_to_ring_map[q_no][0]}_Input{qubit_to_ring_map[q_no][1]}Output{qubit_to_ring_map[q_no][2]}"


check_USB_switch_status()

switch_to_vna(keyer(f"q{q_no}", dac_mapping))

kHz = 1e3
MHz = 1e6
GHz = 1e9

cmd_delay = 4

now = datetime.now()
current_date = now.strftime("%y-%m-%d")

test_name = test_name + "_" + current_date + r'\\'

low_power = -30
high_power = -10

auto_punch_out = 0
manual_punch_out = 0

init_center_freq = 4.5e9
init_span = 7e9

update_config_dicts = 0


def setupXaxis(f_center, f_span, n_points, active_channel=1):
    kna.write(f":SENS{active_channel}:FREQ:CENT {f_center}")
    time.sleep(0.2)
    kna.write(f":SENS{active_channel}:FREQ:SPAN {f_span}")
    time.sleep(0.2)
    kna.write(f":SENS{active_channel}:SWE:POIN {n_points}")
    time.sleep(0.2)
    #     kna.write(f":SENS{active_channel}:SWE:TYPE LIN")
    #     time.sleep(1)

    x_array = np.linspace(f_center - f_span / 2, f_center + f_span / 2, n_points)

    return x_array


def setupMeasurement(s_ij="S21", meas_format="COMP", active_channel=1):
    # Supply all arguments in correct units

    kna.write(f":CALC{active_channel}:MEAS{active_channel}:PAR {s_ij};")
    time.sleep(0.5)
    kna.write(f":CALC{active_channel}:MEAS{active_channel}:FORM {meas_format};")
    time.sleep(0.5)


def setupAveraging(active_channel, n_avgs, IF_bw):
    kna.write(f":SENS{active_channel}:BWID {IF_bw}")
    time.sleep(0.5)
    kna.write(f":SENS{active_channel}:AVER ON")
    time.sleep(0.5)
    kna.write(f":SENS{active_channel}:AVER:COUN {n_avgs}")
    time.sleep(0.5)


# def setPower_getRealImag(power_dBm, wait_time, active_channel=1):
#     kna.write(f":SOUR{active_channel}:POW {power_dBm}")
#     time.sleep(wait_time)
#     kna.write(f":CALC{active_channel}:MEAS{active_channel}:DATA:FDAT?")
#     ydata_str = kna.read()
#     ydata_temp = ydata_str.split(",")
#     y_data = np.array([float(d) for d in ydata_temp])
#     y_data = y_data.reshape(n_points, 2)
#     y_data = y_data.transpose()

# real, imag = y_data
#
# return real, imag


# def setPower(power_dBm, wait_time, active_channel=1):

#     kna.write(f":SOUR{active_channel}:POW {power_dBm}")
#     time.sleep(0.5)
#     power=kna.read()

#     return real, imag

def save_data(data, fname, path=r"D:\BLUEFORS setup\2024-05-11 Cooldown\\"):
    data = np.transpose(data)

    np.savetxt(path + fname, data)


# def getRealImag(active_channel=1):
#     kna.write(f":CALC{active_channel}:MEAS{active_channel}:DATA:FDAT?")
#     ydata_str = kna.read()
#     ydata_temp = ydata_str.split(",")
#     y_data = np.array([float(d) for d in ydata_temp])
#     y_data = y_data.reshape(n_points, 2)
#     y_data = y_data.transpose()
#
#     real, imag = y_data
#
#     return real, imag


def lorentzian(x, c, gam, a, y0):
    return y0 + (2 * a / np.pi) * gam / (4 * (x - c) ** 2 + gam ** 2)


def ext_BW(freq, ydata, plot=False):
    ymin = np.min(ydata)
    ymax = np.max(ydata)

    # initial guess
    left_index = np.where(ydata > 0.5 * (ymax + ymin))[0][0]  # FWHM
    right_index = np.where(ydata > 0.5 * (ymax + ymin))[0][-1]  # FWHM
    BW_g = freq[right_index] - freq[left_index]
    wc_g = freq[np.argmax(ydata)]
    a_g = 0.5 * np.pi * (ymax - ymin) * BW_g
    y0_g = ymin

    res, cov = curve_fit(lorentzian, freq, ydata, [wc_g, BW_g, a_g, y0_g])

    f0, bw = res[0], res[1]
    f0_err, bw_err = np.sqrt(cov[0, 0]), np.sqrt(cov[1, 1])

    a, y0 = res[2], res[3]
    a_err, y0_err = np.sqrt(cov[2, 2]), np.sqrt(cov[3, 3])

    H = 2 * a / (np.pi * bw)
    H_err = H * (a_err / a + bw_err / bw)
    y_xc = H + y0
    y_xc_err = H_err + y0_err

    r = (y0 - y_xc) / (y0 + y_xc)
    r_err = r * (y0_err + y_xc_err) * (1 / (-y0 + y_xc) + 1 / (-y0 - y_xc))

    kint = bw / (1 + r)
    kext = bw * r / (1 + r)

    kint_err = kint * (bw_err / bw + r_err / (r + 1))
    kext_err = bw_err + kint_err

    Qint = f0 / kint
    Qext = f0 / kext

    Qint_err = Qint * (f0_err / f0 + kint_err / kint)
    Qext_err = Qext * (f0_err / f0 + kext_err / kext)

    f0 = np.round(f0 * 1e-9, 10)
    f0_err = np.round(f0_err * 1e-9, 10)
    bw = np.round(bw * 1e-9, 10)
    bw_err = np.round(bw_err * 1e-9, 10)
    kint = np.round(kint * 1e-9, 10)
    kext = np.round(kext * 1e-9, 10)
    kint_err = np.round(kint_err * 1e-9, 10)
    kext_err = np.round(kext_err * 1e-9, 10)

    if plot:
        # plt.figure()
        fig, ax = plt.subplots()
        ax.plot(freq * 1e-9, ydata, label="Data")
        ax.plot(freq * 1e-9, lorentzian(freq, res[0], res[1], res[2], res[3]), c='r', label="Fit")
        text_str = f'Cavity Frequency = {f0:.6f} GHz' + f'\nTotal Bandwidth = {1e3 * bw:.3f} MHz'
        text_str = text_str + f'\nInternal Bandwidth = {kint * 1e3:.3f} MHz' + f'\nExternal Bandwidth = {1e3 * kext:.3f} MHz'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, text_str, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)
        ax.set(xlabel='Frequency (GHz)', ylabel='Measured ReS11')

        # ax.xlabel("Frequency (GHz)")
        # ax.ylabel("Measured ReS11")

        ax.grid()
        plt.legend()
        plt.tight_layout()
        plt.show()
        print("Cavity Frequency = {0} GHz; Total Bandwidth = {1} MHz".format(np.round(f0, 6), np.round(1e3 * bw, 3)))
        print("Internal Bandwidth = {0} MHz; External Bandwidth = {1} MHz".format(np.round(1e3 * kint, 3),
                                                                                  np.round(1e3 * kext, 3)))

    out1 = [(f0, f0_err), (1e3 * kint, 1e3 * kint_err), (1e3 * kext, 1e3 * kext_err)]
    out2 = [(Qint, Qint_err), (Qext, Qext_err)]

    if plot:
        return out1, out2, res, np.sqrt(np.diag(cov)), fig
    else:
        return out1, out2, res, np.sqrt(np.diag(cov))


# ip = "TCPIP0::DESKTOP-OME9GKM::hislip_PXI10_CHASSIS1_SLOT1_INDEX0::INSTR"
ip = "TCPIP0::192.168.0.27::inst0::INSTR"
rm = visa.ResourceManager()
kna = rm.open_resource(ip)

############### Steps to check
#   Low power at -40 dBm with averaging
#   Adjust electrical delay and offset for 5 - 8 GHz span
#   Check logmag
#   find cavity in between 6.5 - 8 GHz
#   center
#   span at 100 MHz
#   get complex at low power
#   move power to punchout zone
#   get complex
#   fit lorentzian on real part of both
#   save images and dat to app folder


setupAveraging(1, 200, 1e3)

setupMeasurement()
kna.write("OUTP ON")

kna.write("SENS1:SWE:POIN 2001")
time.sleep(cmd_delay)
kna.write("CALC:MEAS:MATH:FUNC NORM")
time.sleep(cmd_delay)
kna.write("SENS:AVER:CLE")
time.sleep(cmd_delay)
kna.write("CALC1:MEAS1:FORM PHAS")
time.sleep(cmd_delay)
kna.write(f"DISP:MEAS:Y:AUTO")
time.sleep(cmd_delay * 0.5)
kna.write(f":SOUR1:POW {low_power}")
time.sleep(cmd_delay)


kna.write('CALC:MEAS:MATH:FUNC NORM')
time.sleep(cmd_delay*0.5)
kna.write("SENS1:FREQ:START 7e9")
time.sleep(cmd_delay)
kna.write("SENS1:FREQ:STOP 7.5e9")
time.sleep(cmd_delay)
kna.write("CALC1:MEAS1:CORR:EDEL:TIME 0NS")
time.sleep(cmd_delay)
kna.write("CALC:MEAS:OFFS:PHAS 0")
time.sleep(cmd_delay)
kna.write(f"CALC1:MEAS1:FORM UPH")
time.sleep(cmd_delay)
kna.write(f"DISP:MEAS:Y:AUTO")
time.sleep(cmd_delay * 0.5)
# for _ in range(2):
ph_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
time.sleep(cmd_delay)
f_data = np.array(kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))
time.sleep(cmd_delay)

df1 = f_data[1] - f_data[0]

len_f = len(f_data)

data1, cov1 = np.polyfit(f_data[:len_f//2], ph_data[:len_f//2], 1, cov=True)
data2, cov2 = np.polyfit(f_data[len_f//2:], ph_data[len_f//2:], 1, cov=True)
# ph_d = np.diff(ph_data)

if cov1[0][0] > cov2[0][0]:
    slope = data2[0]
else:
    slope = data1[0]

e_delay_ns = -slope * 1e9 / (360)

kna.write(f"CALC1:MEAS1:CORR:EDEL:TIME {e_delay_ns}NS")
time.sleep(cmd_delay)
kna.write(f"DISP:MEAS:Y:AUTO")
time.sleep(cmd_delay * 0.5)
kna.write("SENS1:FREQ:START 7e9")
time.sleep(cmd_delay)
kna.write("SENS1:FREQ:STOP 7.5e9")
time.sleep(cmd_delay)
kna.write(f"DISP:MEAS:Y:AUTO")
time.sleep(cmd_delay * 0.5)
## If possible, get better logic to find cavity
# kna.write(f"CALC1:MEAS1:FORM MLOG")
# time.sleep(cmd_delay)
# g_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
# time.sleep(cmd_delay)
# f_data = np.array(kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))
# time.sleep(cmd_delay)

# np.convolve(data, weights, mode='valid')
# check unwrapped phase
kna.write(f"CALC1:MEAS1:FORM UPH")
time.sleep(cmd_delay)
kna.write(f"DISP:MEAS:Y:AUTO")
time.sleep(cmd_delay*2)
kna.write(f"CALC1:MEAS1:FORM PHAS")
time.sleep(cmd_delay)
kna.write(f"CALC1:MEAS1:FORM UPH")
time.sleep(cmd_delay)
uph_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
time.sleep(cmd_delay)
f_data = np.array(kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))
# time.sleep(cmd_delay)


win = 30
weights = np.repeat(1.0, win) / win
# filt_uph_dat = np.convolve(uph_data, weights, mode='valid')

diff_uph = np.diff(uph_data)
filt_uph_diff_dat = np.convolve(diff_uph, weights, mode='same')
cav_ph_id = np.argmax(np.abs(filt_uph_diff_dat))
cavity = f_data[cav_ph_id]
#
# ind = np.argmin(g_data)
# cav = np.min(g_data)
#
# cavity = f_data[ind]

fl_low = cavity - 50e6
fl_high = cavity + 50e6

kna.write(f"SENS1:FREQ:START {fl_low}")
time.sleep(cmd_delay)
kna.write(f"SENS1:FREQ:STOP {fl_high}")
time.sleep(cmd_delay)

fl_low = cavity - 15e6
fl_high = cavity + 15e6

kna.write(f"SENS1:FREQ:START {fl_low}")
time.sleep(cmd_delay)
kna.write(f"SENS1:FREQ:STOP {fl_high}")
time.sleep(cmd_delay)

kna.write(f"CALC1:MEAS1:MARK:X {cavity}")

########Phase offset estimation

p_offset = 0
kna.write("CALC:MEAS:OFFS:PHAS 0")
time.sleep(cmd_delay)
kna.write(f"CALC1:MEAS1:FORM UPH")
time.sleep(cmd_delay)
kna.write(f"DISP:MEAS:Y:AUTO")
time.sleep(cmd_delay * 0.5)
ph_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
time.sleep(cmd_delay)
f_data = np.array(kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))
time.sleep(cmd_delay)
diff_uph = np.diff(ph_data)
filt_uph_diff_dat = np.convolve(diff_uph, weights, mode='same')
cav_ph_id = np.argmax(np.abs(filt_uph_diff_dat))
cavity = f_data[cav_ph_id]
kna.write(f"CALC1:MEAS1:MARK:X {cavity}")
time.sleep(cmd_delay)
u_ph_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))

sup = max(u_ph_data)
inf = min(u_ph_data)

sgn = 0

ph_offset = (sup + inf)*0.5


# for i in range(3):
#
#     p_offset = (p_offset + ph_data[cav_ph_id])
#     print(p_offset)
#     kna.write(f"CALC:MEAS:OFFS:PHAS {p_offset}")
#     time.sleep(cmd_delay)
#     kna.write(f"DISP:MEAS:Y:AUTO")
#     time.sleep(cmd_delay*2)
#     kna.write(f"CALC1:MEAS1:FORM PHAS")
#     time.sleep(cmd_delay)
#     ph_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
#     time.sleep(cmd_delay)
#     f_data = np.array(kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))
#     time.sleep(cmd_delay)

kna.write(f"CALC:MEAS:OFFS:PHAS {p_offset}")
ph_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
time.sleep(cmd_delay)
f_data = np.array(kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))
time.sleep(cmd_delay)
diff_uph = np.diff(ph_data)
####    IIR filtering
filt_uph_diff_dat = np.convolve(diff_uph, weights, mode='same')
sos1 = sp.signal.butter(2, 150, 'lp', output='sos', fs=f_data[1]-f_data[0])
filt_ph_data_diff_iir = sp.signal.sosfilt(sos1, diff_uph)


####### End Phase offset estimation
#
#
# kna.write(f"CALC1:MEAS1:FORM REAL")
# time.sleep(cmd_delay)
# kna.write(f"DISP:MEAS:Y:AUTO")
# # time.sleep(cmd_delay*0.5)
# time.sleep(10)
#
# r_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
# time.sleep(0.5)
#
# kna.write(f"CALC1:MEAS1:FORM IMAG")
# kna.write(f"DISP:MEAS:Y:AUTO")
# time.sleep(cmd_delay)
#
# i_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
# time.sleep(cmd_delay)
# ########### Cavity found, elec delay and phase offset adjusted till here, real imag part measured till here for init power
#
# # plt.figure()
# # plt.plot(f_data, r_data)
# # plt.xlabel("Frequency (Hz)")
# # plt.ylabel("Real S11")
# # plt.title('Real Part')
# # plt.grid()
#
# # f_r =
#
# meas_vals_l, q_vals_l, fit_param_l, fit_error_l, fig_lp = ext_BW(f_data, r_data, plot=True)
#
# if not os.path.isdir(path + ExpName + r"\Low Temperature Response" + test_name):
#     os.makedirs(path + ExpName + r"\Low Temperature Response" + test_name)
#
# path1 = path + ExpName + r"\Low Temperature Response" + test_name
# fname = path + ExpName + r"\Low Temperature Response" + test_name + f'{low_power}_dB.pdf'
# plt.savefig(fname=fname)
#
# # plt.figure()
# # plt.plot(f_data, i_data)
# # plt.xlabel("Frequency (Hz)")
# # plt.ylabel("Imag S11")
# # plt.title('Imag Part')
# # plt.grid()
#
# data = [f_data, r_data]
# power = low_power
#
# save_data(data, f"Real_{power}dBm", path=path1)
#
# data = [f_data, i_data]
# power = kna.query_ascii_values('SOUR:POW1:LEV?')
# # path1 = path + ExpName + r"\Low Temperature Response"+test_name
# save_data(data, f"Imag_{power}dBm", path=path1)
#
# ### Low power done
#
# ### Adding punchout calculator. Better to do this manually, as if some weird behaviour occurs, then it wont be caught.
# ### Assuming that punchout will be normal
#
# n_pow = -40
# pr_max = 6e9
# peak_freq = f_data[np.argmax(r_data)]
# kna.write(f"CALC1:MEAS1:FORM REAL")
# time.sleep(cmd_delay)
# kna.write(f"DISP:MEAS:Y:AUTO")
# time.sleep(cmd_delay * 0.5)
# stick = 0
# f_data = np.array(kna.query_ascii_values("CALC1:MEAS1:X:VAL?"))
# if auto_punch_out == 1 and manual_punch_out == 0:
#
#     while (abs(peak_freq - pr_max) > 0.5e6) and (stick == 0):
#         count = 0
#         print(f'Current power = {n_pow}')
#         pr_max = peak_freq
#         kna.write(f":SOUR1:POW {n_pow}")
#         time.sleep(cmd_delay * 5)
#         r_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
#         time.sleep(cmd_delay)
#         peak_freq = f_data[np.argmax(r_data)]
#         n_pow = n_pow + 5
#         print(f'Current peak = {peak_freq}')
#         if abs(peak_freq - pr_max) > 0.1e6:
#             count += 1
#         if count == 5:
#             stick = 1
#
#     punch_out_freq = cavity - peak_freq
#
#     high_power = n_pow
#
# if manual_punch_out == 1:
#
#     kna.write(f":SOUR1:POW {high_power}")
#     time.sleep(cmd_delay)
#
#     kna.write(f"CALC1:MEAS1:FORM REAL")
#     time.sleep(cmd_delay)
#     kna.write(f"DISP:MEAS:Y:AUTO")
#     time.sleep(cmd_delay * 0.5)
#     time.sleep(10)
#     r_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
#     time.sleep(cmd_delay)
#
#     kna.write(f"CALC1:MEAS1:FORM IMAG")
#     time.sleep(cmd_delay)
#     kna.write(f"DISP:MEAS:Y:AUTO")
#     time.sleep(cmd_delay * 0.5)
#     i_data = np.array(kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))
#     time.sleep(cmd_delay)
#
#     # plt.figure()
#     # plt.plot(f_data, r_data)
#     # plt.xlabel("Frequency (Hz)")
#     # plt.ylabel("Real S11")
#     # plt.title('Real Part')
#
#     meas_vals_r, q_vals_r, fit_param_r, fit_error_r, fig_hp = ext_BW(f_data, r_data, plot=True)
#
#     if not os.path.isdir(path + ExpName + r"\Low Temperature Response" + test_name):
#         os.makedirs(path + ExpName + r"\Low Temperature Response" + test_name)
#
#     path1 = path + ExpName + r"\Low Temperature Response" + test_name
#     fname = path + ExpName + r"\Low Temperature Response" + test_name + f'{high_power}_dB.pdf'
#     plt.savefig(fname=fname)
#
#     # plt.figure()
#     # plt.plot(f_data, i_data)
#     # plt.xlabel("Frequency (Hz)")
#     # plt.ylabel("Imag S11")
#     # plt.title('Imag Part')
#     # plt.grid()
#
#     data = [f_data, r_data]
#     power = kna.query_ascii_values('SOUR:POW1:LEV?')
#
#     save_data(data, f"Real_{power}dBm", path=path1)
#
#     data = [f_data, i_data]
#     power = high_power
#     # path1 = path + ExpName + r"\Low Temperature Response"+test_name
#     save_data(data, f"Imag_{power}dBm", path=path1)
#
# kna.write(f":SOUR1:POW {low_power}")
#
# kna.write("OUTP OFF")
#
# if update_config_dicts == 1:
#     dac_key = keyer(f'q{q_no}', dac_mapping)[0]
#     rr_LO_rns = rm.open_resource(LO_IP_dict['rr_LO'][dac_key])
#
#     rr_LO_rns.write(f'SOUR:FREQ:CW {meas_vals_l[0][0] - 0.02} GHz')
#
#     with open('./System_Parameters/rr_LO.json', 'r') as f:
#         rr_LO_dict = json.load(f)
#         f.close()
#
#     with open('./System_Parameters/rr_IF.json', 'r') as f:
#         rr_IF_dict = json.load(f)
#         f.close()
#
#     rr_LO_dict[str(q_no)] = meas_vals_l[0][0] - 0.02
#     rr_IF_dict[str(q_no)] = 20
#
#     with open('./System_Parameters/rr_LO.json', 'w') as f:
#         json.dump(rr_LO_dict, f, indent=6)
#         f.close()
#
#     with open('./System_Parameters/rr_IF.json', 'w') as f:
#         json.dump(rr_IF_dict, f, indent=6)
#         f.close()
#
#     rr_LO_rns.close()
#
#
# if turn_off == 1:
#     VNA_route_off()
