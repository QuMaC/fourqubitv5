import numpy as np


def return_elec_delay(phase_data, freq_list_MHz):
    '''
    Returns the electronic delay (single scalar) in ns from phase vs frequency slope.
    d(phase)/d(freq) = -2*pi*delay_ns, so delay_ns = -median(dphase)/(2*pi*df).
    '''
    phase = np.angle(phase_data)
    df = np.diff(freq_list_MHz)
    ph_d = np.diff(phase)
    df_scalar = np.median(df)  # one value so e_delay_est is a scalar
    e_delay_est = -1 * np.median(ph_d) / (2 * np.pi * df_scalar)
    return float(e_delay_est)




def rotate_phase_data(phase_data, e_delay_est, ph_offset, freq_list_MHz):
    '''
    Rotates the data by the electronic delay and phase offset.
    '''
    return phase_data * np.exp(1j * 2 * np.pi * freq_list_MHz * e_delay_est + 1j * ph_offset)

