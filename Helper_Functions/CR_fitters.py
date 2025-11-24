import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import leastsq, curve_fit
import copy

pi = np.pi

plt.rc('pgf', texsystem='pdflatex')
plt.rcParams.update({
    "pgf.texsystem": "pdflatex",
    "font.family": "serif",
    #     "font.serif": ["CMU serif"],                    # use latex default serif font
    'pgf.rcfonts': False,
    'figure.figsize': [6.5, 4.5],
    'font.size': 14,
    # 'lines.linewidth' : 1.5,
    'axes.linewidth': 1.1,
    'xtick.major.size': 5,
    'xtick.minor.size': 3,
    'ytick.major.size': 5,
    'ytick.minor.size': 3
})
plt.rc('axes', unicode_minus=False)


def fit_cos(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = np.array(tt)
    yy = np.array(yy)
    ff = np.fft.fftfreq(len(tt), (tt[1] - tt[0]))  # assume uniform spacing
    Fyy = abs(np.fft.fft(yy))
    guess_freq = abs(ff[np.argmax(Fyy[1:]) + 1])  # excluding the zero frequency "peak", which is related to offset
    guess_amp = np.std(yy) * 2. ** 0.5
    guess_offset = np.mean(yy)
    guess = np.array([guess_amp, 2. * pi * guess_freq, 0, guess_offset])

    def cosfunc(t, A, w, p, c):  return A * np.cos(w * t + p) + c

    try:
        popt, pcov = curve_fit(cosfunc, tt, yy, p0=guess, maxfev=2000)
    except RuntimeError:
        print('Fitting crashed')
        popt = guess
        pcov = [0,0]

    A, w, p, c = popt
    f = w / (2. * pi)
    fitfunc = lambda t: A * np.cos(w * t + p) + c

    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1. / f, "fitfunc": fitfunc,
            "maxcov": np.max(pcov), "rawres": (guess, popt, pcov)}


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
        d_in = 1000

        par_init = [ox_in, oy_in, del_in, d_in]

        # print(f'ox, oy, del, d = {par_init}')

    else:
        par_init = init_vals

    best, cov, info, message, ier = leastsq(diff_bloch_functions,
                                            par_init, args=(x, y, z, tlist),
                                            full_output=True,
                                            ftol=1.49012e-10)

    # print(" Best-Fit Parameters: ",  best)

    return best


def CR_Hamiltonian_tomography(exp_vals, tlist, bloch_params=False, init_vals=None):
    z_vals, y_vals, x_vals = exp_vals[0], exp_vals[1], exp_vals[2]

    if init_vals is None:

        C0 = fit_bloch_params(x_vals[0], y_vals[0], z_vals[0], tlist)
        C1 = fit_bloch_params(x_vals[1], y_vals[1], z_vals[1], tlist)
    else:
        C0 = fit_bloch_params(x_vals[0], y_vals[0], z_vals[0], tlist, init_vals[0])
        C1 = fit_bloch_params(x_vals[1], y_vals[1], z_vals[1], tlist, init_vals[1])

    int_strengths = []
    for i in range(3):
        int_strengths.append((C0[i] - C1[i]) / (4 * np.pi))
        int_strengths.append((C0[i] + C1[i]) / (4 * np.pi))

    if bloch_params is True:
        return int_strengths, [C0, C1]

    return int_strengths


def bloch_functions(tlist, omegax, omegay, delta, d):
    vals = np.zeros((3, tlist.size))
    B = (omegax ** 2 + omegay ** 2 + delta ** 2) ** 0.5
    for i in range(tlist.size):
        t = tlist[i]
        vals[2][i] = np.exp(-t / d) * (-omegax * delta * (1 - np.cos(B * t)) + omegay * B * np.sin(B * t)) / B ** 2
        vals[1][i] = np.exp(-t / d) * (-omegay * delta * (1 - np.cos(B * t)) - omegax * B * np.sin(B * t)) / B ** 2
        vals[0][i] = np.exp(-t / d) * (
                    delta ** 2 + (omegax ** 2 + omegay ** 2) * np.cos(B * t)) / B ** 2  # Check minus sign

    return vals


def normalize_data(Cdata1, off, norm):
    for i in range(3):
        for j in range(2):
            Cdata = copy.copy(Cdata1)
            data = Cdata[i][j]
            data = data - off
            data = data / norm
            Cdata[i][j] = data

    for i in range(2):
        sgn = np.sign(Cdata[0][i][0])
        for j in range(3):
            Cdata[j][i] = sgn * Cdata[j][i]

    #     Cdata[2][0] = -Cdata[2][0]  #Look into this manual correction
    #     Cdata[2][1] = -Cdata[2][1]  #Look into this manual correction

    return Cdata


def rabi_fit(t, A, f, d, p, c):
    '''
        Parameter order = (time, Amplitude, frequency, decay, phase, offset)
    '''

    return A * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p) + c