import numpy as np


def smooth_filter(data, window):  # moving_average_numpy
    weights = np.repeat(1.0, window) / window
    k = np.convolve(data, weights, mode='full')
    return k


def does_signal_exist(sig, alpha=1):
    '''
    Checks for existence of trend. If yes, will return a filtered version
    :param sig: signal
    :param alpha: factor to tune threshold. Ultra-high value can make the function think noise is signal
    :return: flag for yes/no, filtered signal
    '''
    window_size = int(max(len(sig) // 100, 10))

    limit = np.sqrt(window_size) * alpha

    fil_sig = smooth_filter(sig, window_size)

    filt_std = np.std(fil_sig)

    sig_std = np.std(sig)

    return filt_std / sig_std < limit, fil_sig


def does_signal_exist1(sig, alpha=1, win_s=10):
    '''
    Checks for existence of trend. If yes, will return a filtered version
    :param sig: signal
    :param alpha: factor to tune threshold. Ultra-high value can make the function think noise is signal
    :return: flag for yes/no, filtered signal
    '''
    window_size = int(max(len(sig) // 100, win_s))

    limit = np.sqrt(window_size) * alpha

    fil_sig = smooth_filter(sig, window_size)

    filt_std = np.std(fil_sig[window_size-1:-window_size+1])

    sig_std = np.std(sig)

    return filt_std / sig_std < limit, fil_sig, window_size


def normalize(sig):
    '''
    Normalizes a signal. Inversions taken care of
    :param sig: Signal
    :return: normalized signal
    '''
    null = np.median(sig)

    sig1 = sig - null

    max_s = np.max(sig) - null

    min_s = np.min(sig) - null


    if abs(min_s) > abs(max_s):
        add_sign = -1
        scale = np.abs(np.min(sig1))
    else:
        add_sign = 1
        scale = np.abs(np.max(sig1))

    return add_sign * sig1 / scale


def S2N_1(norm_sig):  # normalized signal input
    window_size = int(max(len(norm_sig) // 100, 10))  # 10 works for 500 samples
    fil_sig = smooth_filter(norm_sig, window_size)[window_size-1:-window_size+1]
    prefix = np.zeros(window_size // 2)
    suffix = np.zeros(window_size // 2 - 1)

    signal = np.append(np.append(prefix, fil_sig), suffix)
    noise = norm_sig - signal
    noise_std = np.std(noise)
    fil_noise = [min(2 * np.abs(noise_std), np.abs(noise[i])) for i in range(len(noise))]

    P_signal = np.sum(np.square(signal))
    P_noise = np.sum(np.square(fil_noise))

    S2N = P_signal / P_noise
    return S2N, [signal, fil_noise]


def check_I_or_Q(signal, alpha1=1):
    """Input signal = [I,Q]. Returns which index is better"""
    I, Q = signal
    sig_I_flg, fltd_I, w_I = does_signal_exist1(I, alpha=alpha1)
    sig_Q_flg, fltd_Q, w_Q = does_signal_exist1(Q, alpha=alpha1)

    if sig_I_flg and not sig_Q_flg:
        return 0
    if sig_Q_flg and not sig_I_flg:
        return 1
    elif sig_Q_flg and sig_I_flg:
        span_I = np.abs(np.max(fltd_I[w_I:-w_I+1]) - np.min(fltd_I[w_I:-w_I+1]))
        span_Q = np.abs(np.max(fltd_Q[w_Q:-w_Q+1]) - np.min(fltd_Q[w_Q:-w_Q+1]))

        if span_I > span_Q:
            return 0
        else:
            return 1
    else:
        return None


def closest_pair(arr, target):
    # Sort the array
    arr.sort()
    n = len(arr)
    closest_diff = float('inf')
    closest_pair1 = (None, None)

    # Initialize two pointers
    i, j = 0, 1

    # Iterate while the second pointer is within the array
    while j < n:
        # Calculate the current difference
        current_diff = abs(arr[j] - arr[i] - target)

        # Update the closest pair if the current difference is smaller than the closest found so far
        if current_diff < closest_diff:
            closest_diff = current_diff
            closest_pair1 = (arr[i], arr[j])
            closest_pair1 = (min((arr[i], arr[j])), max((arr[i], arr[j])))

        # Move the pointers based on comparison
        if arr[j] - arr[i] < target:
            j += 1
        else:
            i += 1

        # Ensure i and j don't cross, and j always stays ahead
        if i == j:
            j += 1

    return closest_pair1


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx
