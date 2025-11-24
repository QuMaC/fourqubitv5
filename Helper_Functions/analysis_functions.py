import json

import numpy as np
import scipy.signal
from scipy.optimize import curve_fit, leastsq
import copy
from Helper_Functions.spectro_helper import smooth_filter

pi = np.pi

def ramsey_exp_init(time, data):
    t = time
    yy = data
    N = len(yy)
    dt = t[1] - t[0]
    F = np.fft.fftfreq(N, d=dt)
    X = np.fft.fft(yy, N) * (2 / N)

    X_p = copy.deepcopy(X)

    X_p[0] = 0

    X_p = X_p[1:len(X_p) // 2]
    F = F[1:len(F) // 2]

    peak_freq_index = (np.where(np.abs(X_p) == max(np.abs(X_p))))

    amp = max(np.abs(X_p))

    freq_est1 = F[peak_freq_index[0][0]]

    c_init = (max(yy) + min(yy)) / 2

    y_norm = (data - c_init) * (1 / amp)

    y_demod = y_norm * (np.cos(2 * np.pi * freq_est1 * time))

    win_s = int(np.ceil(1/(freq_est1*dt)))//2
    # print(win_s)
    window_size = win_s
    fil_sig = smooth_filter(y_demod, window_size)

    t_time = time[win_s-1:]

    y_fin = fil_sig[win_s-1:]

    tau_est, amp, off = exp_init(t_time, y_fin)

    return tau_est


def exp_init(time_data, data):
    ''''
        Returns a decent initial fit for exponential fit
        Return: tau, amplitude, offset
    '''

    win_s = 10

    window_size = int(max(len(data) // 100, win_s))

    fil_sig = smooth_filter(data, window_size)

    trim_sig = fil_sig[win_s:-win_s]

    trim_time = time_data[win_s: -win_s]

    y_i = np.mean(trim_sig[:10])

    y_f = np.mean(trim_sig[-10:-1])

    y_p = (trim_sig - y_f) / (y_i - y_f)

    neg_id = np.where(y_p < 0.5)[0][0]

    y_p = y_p[:neg_id]

    t_time = trim_time[:neg_id]

    log_yp = np.log(y_p)

    # print(len(log_yp))

    # print(neg_id)
    # print(len(t_time))
    # print(len(log_yp))

    coeffs = np.polyfit(t_time, log_yp, 1)

    tau_est = np.abs(1 / coeffs[0])

    return np.mean(data[:10]) - np.mean(data[-10:-1]), tau_est, np.mean(data[-10:-1])


def fft_func(tt, yy):
    tt = np.array(tt)
    yy = np.array(yy)
    ff = np.fft.fftfreq(len(tt), (tt[1] - tt[0]))  # assume uniform spacing
    Fyy = abs(np.fft.fft(yy))
    F_yy = Fyy[1:len(Fyy) // 2]
    F_ff = ff[1:len(Fyy) // 2]
    index = np.where(F_yy == np.max(F_yy))[0][0]

    return F_ff, F_yy


################################################# Hamiltonian Tomography ###################################################
def fit_cos(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = np.array(tt)
    yy = np.array(yy)
    ff = np.fft.fftfreq(len(tt), (tt[1] - tt[0]))  # assume uniform spacing
    Fyy = abs(np.fft.fft(yy))
    F_yy = Fyy[1:len(Fyy) // 2]
    F_ff = ff[1:len(Fyy) // 2]
    index = np.where(F_yy == np.max(F_yy))[0][0]
    guess_freq = F_ff[
        index]  # abs(ff[np.argmax(Fyy) + 1])  # excluding the zero frequency "peak", which is related to offset
    guess_amp = Fyy[index]  # np.std(yy) * 2. ** 0.5
    guess_offset = np.mean(yy)
    guess = np.array([guess_amp, 2. * pi * guess_freq, 0, guess_offset])

    def cosfunc(t, A, w, p, c):  return A * np.cos(w * t + p) + c

    popt, pcov = curve_fit(cosfunc, tt, yy, p0=guess)
    A, w, p, c = popt
    f = w / (2. * pi)
    fitfunc = lambda t: A * np.cos(w * t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1. / f, "fitfunc": fitfunc,
            "maxcov": np.max(pcov), "rawres": (guess, popt, pcov)}


def fit_exp(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''

    def expfunc(t, A, d, c):  return A * np.exp(-t / d) + c

    popt, pcov = curve_fit(expfunc, tt, yy, p0=[1, 10e3, 0], bounds=(-np.inf, np.inf), maxfev=2000)
    A, d, c = popt
    fitfunc = lambda t: expfunc(t, A, d, c)
    return {"amp": A, "decay": d, "offset": c, "fitfunc": fitfunc,
            "maxcov": np.max(pcov)}


def ramsey_fitting(tt, yy, init=False):
    t = tt

    N = len(yy)
    dt = t[1] - t[0]
    F = np.fft.fftfreq(N, d=dt)
    X = np.fft.fft(yy, N) * (2 / N)

    X_p = copy.deepcopy(X)

    X_p[0] = 0

    X_p = X_p[1:len(X_p) // 2]
    F = F[1:len(F) // 2]

    peak_freq_index = (np.where(np.abs(X_p) == max(np.abs(X_p))))

    amp = max(np.abs(X_p))

    freq_est1 = F[peak_freq_index[0][0]]

    c_init = (max(yy) + min(yy)) / 2

    with open('../Configuration_Files/Pulse_Calibrations/upper_bound_coherence.json') as f:
        bound_dict = json.load(f)
        upper = 3 * bound_dict['T1_upper']
        f.close()

    # peaks = scipy.signal.find_peaks(yy, distance=int(len(yy) / peak_freq_index[0][0])//2)
    #
    # yy_peaks = np.array(yy)[peaks[0]]
    #
    # yy_peaks = yy_peaks - c_init

    # raise Exception

    if init:
        tau_init = ramsey_exp_init(tt, yy)
    else:
        tau_init = 10

    bnds = ([0, 0, -np.inf, 0, -np.pi], [np.inf, max(upper, 3*tau_init), np.inf, np.inf, np.pi])

    popt, pcov = curve_fit(ramsey_fit, xdata=tt, ydata=yy, p0=[amp, tau_init, c_init, freq_est1, np.pi / 2], maxfev=2000,
                           bounds=bnds)

    return popt, pcov, [amp, tau_init, c_init, freq_est1, 0]


def ramsey_fit(t, A, tau, c, freq, phi):
    return A * np.exp(-t / tau) * np.sin(2 * np.pi * freq * t + phi) + c


def bloch_functions(tlist, omegax, omegay, delta, d):
    vals = np.zeros((3, tlist.size))

    B = (omegax ** 2 + omegay ** 2 + delta ** 2) ** 0.5
    for i in range(tlist.size):
        t = tlist[i]
        vals[2][i] = np.exp(-t / d) * (-omegax * delta * (1 - np.cos(B * t)) + omegay * B * np.sin(B * t)) / B ** 2
        vals[1][i] = np.exp(-t / d) * (-omegay * delta * (1 - np.cos(B * t)) - omegax * B * np.sin(B * t)) / B ** 2
        vals[0][i] = np.exp(-t / d) * (delta ** 2 + (omegax ** 2 + omegay ** 2) * np.cos(B * t)) / B ** 2

    return vals


def fit_bloch_params(x, y, z, tlist, init_vals=None):
    def diff_bloch_functions(pars, x, y, z, t):
        omegax = pars[0]
        omegay = pars[1]
        delta = pars[2]
        d = pars[3]
        B = (omegax ** 2 + omegay ** 2 + delta ** 2) ** 0.5

        diff1 = x - np.exp(-t / d) * (-omegax * delta * (1 - np.cos(B * t)) + omegay * B * np.sin(B * t)) / B ** 2
        diff2 = y - np.exp(-t / d) * (-omegay * delta * (1 - np.cos(B * t)) - omegax * B * np.sin(B * t)) / B ** 2
        diff3 = z - np.exp(-t / d) * (delta ** 2 + (omegax ** 2 + omegay ** 2) * np.cos(B * t)) / B ** 2

        return np.concatenate((diff1, diff2, diff3))

    # initial values

    if init_vals is None:
        init_cal = fit_cos(tlist, z)
        B_in = init_cal["omega"]
        del_in = np.sqrt(abs(init_cal["offset"] * B_in ** 2))
        ox_in = np.sqrt(0.5 * (B_in ** 2 - del_in ** 2))
        oy_in = np.sqrt(0.5 * (B_in ** 2 - del_in ** 2))
        d_in = 10000

        par_init = [ox_in, oy_in, del_in, d_in]

    else:
        par_init = init_vals

    best, cov, info, message, ier = leastsq(diff_bloch_functions,
                                            par_init, args=(x, y, z, tlist),
                                            full_output=True,
                                            ftol=1.49012e-10)

    # print(" Best-Fit Parameters: ",  best)

    return best


def rabi_fit(t, A, f, d, p, c):
    return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c


def para_fit(x, temp4, temp3, temp2, temp1, temp0):
    return temp4 * x ** 4 + temp3 * x ** 3 + temp2 * x ** 2 + temp1 * x + temp0


################################## Randomized Benchmarking #################################################################
def power_law(m, a, b, p):
    return a * (p ** m) + b


def fit_RB(x_data, y_data, ivals=[-1e-5, 0, 0.9], nqubits=1):
    from scipy.optimize import curve_fit
    pars, cov = curve_fit(f=power_law, xdata=x_data, ydata=y_data, p0=ivals, bounds=(-np.inf, np.inf), maxfev=2000)

    stdevs = np.sqrt(np.diag(cov))

    print('#########################')
    print('### Fitted Parameters ###')
    print('#########################')
    print(f'A = {pars[0]:.3} ({stdevs[0]:.1}), B = {pars[1]:.3} ({stdevs[1]:.1}), p = {pars[2]:.3} ({stdevs[2]:.1})')
    print('Covariance Matrix')
    print(cov)

    one_minus_p = 1 - pars[2]
    r_c = one_minus_p * (1 - 1 / 2 ** nqubits)
    r_g = r_c / 1.875
    r_c_std = stdevs[2] * (1 - 1 / 2 ** nqubits)
    r_g_std = r_c_std / 1.875

    print('#########################')
    print('### Useful Parameters ###')
    print('#########################')
    print(f'1-p = {np.format_float_scientific(one_minus_p, precision=2)} ({stdevs[2]:.1}), '
          f'r_c = {np.format_float_scientific(r_c, precision=2)} ({r_c_std:.1}), '
          f'r_g = {np.format_float_scientific(r_g, precision=2)}  ({r_g_std:.1})')

    return pars
