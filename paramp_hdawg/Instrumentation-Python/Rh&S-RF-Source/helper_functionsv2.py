import numpy as np
import sys
from scipy.signal import gaussian


#Code to allow halting the program if simulating
class Halted(Exception) :
    def __init__(self): sys.tracebacklimit = 0
if hasattr(sys,'tracebacklimit'): del sys.tracebacklimit
# use as raise Halted()


def IQ_imbalance(g, phi):
    c = np.cos(phi)
    s = np.sin(phi)
    N = 1 / ((1-g**2)*(2*c**2-1))
    return [float(N * x) for x in [(1-g)*c, (1+g)*s, (1-g)*s, (1+g)*c]]

def file_saver_(data,header_string="",suffix="",delimiter=",",master_folder="ExpName",init_path="E:/Experiments"):
    '''
    saves data as a file -> init_path/masterfolder/exp_type/date/file-time.csv

    Arguments : 
    'init_path' -> prefix path like "E:/Experiments"
    'exp_type' -> example "Spectroscopy"
    'master_folder" -> example "2qubit_RB_experiment"
    'header_string' -> string to passed on as header to store useful parameters about exp.
    '''
    from datetime import datetime
    import os
    now = datetime.now()
    current_date = now.strftime("%y-%m-%d")
    current_time = now.strftime("%H-%M-%S")
    #Create relevant Folders
    master_path = init_path+"/"+master_folder
    exp_type = __file__.split("/")[0]
    os.makedirs(master_path+"/"+exp_type+"/"+current_date,exist_ok=True)
    final_path = master_path+"/"+exp_type+"/"+current_date

    #Create file and save DATA
    filename = __file__.split("/")[-1][:-3]+f"-{suffix}-"+current_time+".csv"
    np.savetxt(final_path+"/"+filename,data,delimiter=delimiter,header=header_string)

    return print("File saved as: ",final_path+"/"+filename)

def integration_weight_update(b,config,integ_len_clk):
    w_plus_cos = [(np.cos(b),  integ_len_clk*4)]
    w_minus_cos = [(-np.cos(b),  integ_len_clk*4)]
    w_plus_sin = [(np.sin(b),  integ_len_clk*4)]
    w_minus_sin = [(-np.sin(b),  integ_len_clk*4)]
    config['integration_weights']['integW_cos']['cosine'] = w_plus_cos
    config['integration_weights']['integW_cos']['sine'] = w_minus_sin
    config['integration_weights']['integW_sin']['cosine'] = w_plus_sin
    config['integration_weights']['integW_sin']['sine'] = w_plus_cos
    config['integration_weights']['integW_minus_sin']['cosine'] = w_minus_sin
    config['integration_weights']['integW_minus_sin']['sine'] = w_minus_cos
    return 1

def grft_pulse(pi_len_ns, pi_rise_ns):
    risefall = [float(arg) for arg in gaussian(2 * pi_rise_ns, 2 * pi_rise_ns // 6)]
    pulse = []
    for i in range(pi_len_ns):
        if i < pi_rise_ns:
            # pulse.append(risefall[i])
            pulse.append(1)
        elif i >= pi_len_ns - pi_rise_ns:
            # pulse.append(risefall[i - pi_len_ns + 2 * pi_rise_ns])
            pulse.append(1)
        else:
            pulse.append(1)

    return np.array(pulse)

def grft_arr_gen(arguments,scales=[1]):
    scaling = np.prod(scales)*0.4
    slist = [float(arg) for arg in scaling * grft_pulse(*arguments)]
    return slist

def gauss_arr_gen(arguments,scales=[1]):
    scaling = np.prod(scales)*0.4
    slist = [float(arg) for arg in scaling * gaussian(*arguments)]
    return slist

def rise_arr(rise_ns):

    risefall = [float(0.4*arg) for arg in gaussian(2 * rise_ns, 2 * rise_ns // 6)]
    l = int(len(risefall)/2)
    rise = risefall[:l]

    return rise


def fall_arr(rise_ns):
    risefall = [float(0.4*arg) for arg in gaussian(2 * rise_ns, 2 * rise_ns // 6)]
    l = int(len(risefall) / 2)
    fall = risefall[l:]

    return fall