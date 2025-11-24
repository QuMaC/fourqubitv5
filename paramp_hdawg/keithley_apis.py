#%%
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time
import os


#%%
def set_V_read_I(keithley, V, I_c=1E-1):
    
    keithley.write(f"SOUR:VOLT:MODE FIXED\n SOUR:VOLT {V}")
    keithley.write(f"SENS:CURR:PROT {I_c}")
    keithley.write("TRIG:COUN 1")
    keithley.write("FORM:ELEM CURR")
    keithley.write("OUTP ON")
    keithley.write("READ?")
    I_read = keithley.read()
    
    return float(I_read)

def reset(keithley):
    keithley.write("*RST")
    set_V_read_I(keithley, 0, 0.1)

def rampdown_V(keithley, V_init, V_fin, step=0.01, t_wait=1, verbose=False):
    
    import time
    step = step if V_fin - V_init == 0 else np.sign(V_fin - V_init) * np.abs(step)
    V_list = np.round(np.arange(V_init, V_fin + step * 0.5, step), 3) 
    
    for V in V_list:
        I_read = set_V_read_I(keithley, V)
        time.sleep(t_wait)
        if verbose:
            print(I_read, V)
    return I_read

def init_code_paramp(keithley, I_c = 0.05):

    keithley.write("*RST")
    keithley.write("SOUR:FUNC VOLT")
    keithley.write("SOUR:VOLT:RANG 20")
    keithley.write("SENS:FUNC \"CURR\"")
    keithley.write(f"SOURce:VOLT:ILIM {I_c}")
    

def ch_op_on(keithley, ch = None, en = 0):

    if en == 1:
        keithley.write("OUTP ON")
    else:
        keithley.write("OUTP OFF")

def get_ch_op_state(keithley,ch = None):

    keithley.write("OUTP?")
    time.sleep(1)
    status = keithley.read()
    time.sleep(1)

    return int(status[:-1])

def read_output(keithley,ch = None):

    keithley.write("SOUR:VOLT?")
    time.sleep(1)
    status = keithley.read()
    time.sleep(1)

    return float(status[:-1])

def set_output(keithley,ch = None,val = 0):
    
    keithley.write(f"SOUR:VOLT {val}")

def ramp_V_hdawg(daq, ch, V_fin, V_init=None, step=0.01, t_wait=1, verbose=False):

    if V_init is None:
        V_init = read_output(daq)
        print(f'V_init automatically taken from current setting of {V_init}')


    st = get_ch_op_state(daq, ch)

    if st == 0:
        set_output(daq, ch, 0)
        V_init = 0
        print('Output off. Turning on output')
        ch_op_on(daq, ch, 1)
    
    import time

    if V_fin == V_init:
        return
    
    print(f'values {V_init}, {V_fin}, {step}, {abs(V_fin-V_init)}')

    if step > np.abs(V_fin - V_init):
        step = (V_fin - V_init)*0.5

    step = np.sign(V_fin - V_init)*np.abs(step)
    nums = abs((V_fin-V_init+step)/step)
    V_list = np.linspace(V_init, V_fin, num = int(np.round(nums,0)))
    # V_list = np.round(np.arange(V_init, V_fin, step),3) 
    
    for V in V_list:
        set_output(daq, ch, V)
        V_now = read_output(daq)

        print(V_now)
        time.sleep(t_wait)   

    print(f'Current')
# %%

def change_current(board,curr,DAC_no,Tile):
    curr = int(curr*1000)
    # DAC_no = 3
    # Tile = 1
    wait_in_sec = 0

    board.comm_query(f"SetDACVOP {Tile} {DAC_no} {curr}",wait_in_sec = wait_in_sec)  

    return 0

#%%

def gen_pulses(fs_IF, N, f_c, f_sep,  Amp1_offset, Amp1, tot_pwr1, wait_in_sec = 0):

    # f_c = 0

    f_1 =  f_c - (f_sep / 2.0) # Tone 1 (lower tone in zone 1)
    f_2 =  f_c + (f_sep / 2.0) # Tone 2 (upper tone in zone 2)

    # Amp2 = 0.5

    # NOTE: Dual tone generation about a central frequency by creating two SSB signals 
    tilde_k_1 = np.floor(N*f_1/fs_IF) # In the interest of minimum deviation in f_c
    tilde_k_2 = np.ceil(N*f_2/fs_IF) # In the interest of minimum deviation in f_c
    tilde_f_1 = fs_IF * tilde_k_1 / N
    tilde_f_2 = fs_IF * tilde_k_2 / N

    Amp2 = (1 - (Amp1 + Amp1_offset))
    sig1_I = tot_pwr1 * Amp1 * np.cos(2 * np.pi *(tilde_f_1 / fs_IF) * np.arange(N)) + Amp1_offset 
    sig1_Q = tot_pwr1 * Amp1 * np.sin(2 * np.pi *(tilde_f_1 / fs_IF) * np.arange(N)) + 0
    sig2_I = tot_pwr1 * Amp2 * np.cos(2 * np.pi *(tilde_f_2 / fs_IF) * np.arange(N))
    sig2_Q = tot_pwr1 * Amp2 * np.sin(2 * np.pi *(tilde_f_2 / fs_IF) * np.arange(N))
    temp1 = sig1_I + sig2_I
    temp2 = sig1_Q + sig2_Q

    # DATA CHECKING FOR BRAM
    waveforms1 = {'ch1':{'I':[temp1], 'Q':[temp2]}}
    for dac1 in waveforms1:
        # check if number of pulses in both I and Q are same for all channels
        if len(waveforms1[dac1]["I"]) != len(waveforms1[dac1]["Q"]):
            raise ValueError(f"Number of PULSES in I and Q of channel {dac1} are not equal")
        pulse_I1, pulse_Q1 = waveforms1[dac1].values()
        # Loop through each pulse 
        for pulse_arr_I1, pulse_arr_Q1 in zip(pulse_I1, pulse_Q1):
            if len(pulse_arr_I1) != len(pulse_arr_Q1):
                raise ValueError(f"Number of SAMPLES in I pulse and Q pulse of channel {dac1} are not equal")

    wave_data = np.vstack((waveforms1['ch1']['I'],waveforms1['ch1']['Q']))
    wave_data = wave_data.flatten('F')
    wave_data = (wave_data * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) / 2 + (np.iinfo(np.int16).max + np.iinfo(np.int16).min) / 2).astype('int16')

    # # DATA CHECKING / PREPARATION FOR LVM FILE
    # tempI = sig1_I + sig2_I
    # tempQ = sig1_Q + sig2_Q
    # temp1 = (tempI * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) / 2 + (np.iinfo(np.int16).max + np.iinfo(np.int16).min) / 2).astype('int16')
    # temp2 = (tempQ * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) / 2 + (np.iinfo(np.int16).max + np.iinfo(np.int16).min) / 2).astype('int16')
    # Delta_X = '8.1380e-10'
    # NumOfSamples = len(temp1)

    return [wave_data,temp1,temp2]

def DAC_prog(board, Type, Tile, Block, F_sample, DAC_current, Cavity_freqs, wave_data, wait_in_sec = 0):
    # Calculate NCO Frequency
    curr = int(DAC_current*1000)
    NCOFreq = Cavity_freqs
    # Update the Class object
    board.sys_config[f'DAC_TILE_{Tile}'][f'DAC_{Block}']['NCOFreq'] = NCOFreq
    # Program DAC
    board.program_DAC(DAC_number=Block, DAC_tile=Tile, wait_in_sec = 0.0)
    # Send Data
    board.DAC_BRAM_dataupload(wave_data, DAC_number=Block, DAC_tile=Tile, wait_in_sec = 0.0)
    board.comm_query(f"SetDACVOP {Tile} {Block} {curr}",wait_in_sec = wait_in_sec)  

    print('DATA UPLOADED')

    return 0

def board_init(board,int_ext,F_sample, wait_in_sec=0):
    ## SET CLOCK FOR BOARD
    if (int_ext=='int'):
        clk_file = "int_source.tcs"
    elif(int_ext=='ext'):
        clk_file = "ext_source.tcs"

    board.set_clock(clk_file, wait_in_sec = wait_in_sec)
    # Set Sampling Frequency across DACs
    command = f'SetClkDistribution 1 1 245.760000 {F_sample} 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample} 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample} 1 1 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample} 1 0 1 1 245.760000 1966.080000 1 0'
    ## Format for DAC DACtile_0 DACtile_1 DACtile_2 DACtile_3
    board.comm_query(command, wait_in_sec = wait_in_sec)


def board_init_diff_sample(board,int_ext,F_sample, wait_in_sec=0):
    ## SET CLOCK FOR BOARD
    if (int_ext=='int'):
        clk_file = "int_source.tcs"
    elif(int_ext=='ext'):
        clk_file = "ext_source.tcs"

    board.set_clock(clk_file, wait_in_sec = wait_in_sec)
    # Set Sampling Frequency across DACs
    command = f'SetClkDistribution 1 1 245.760000 {F_sample[0]} 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample[1]} 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample[2]} 1 1 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample[3]} 1 0 1 1 245.760000 1966.080000 1 0'
    ## Format for DAC DACtile_0 DACtile_1 DACtile_2 DACtile_3
    board.comm_query(command, wait_in_sec = wait_in_sec)

def cavity_freq_extract(cavity_frequencies):
    tile_0 = []

    for i in range(1,5):
        tile_0.append(cavity_frequencies[f'rr{i}'])

    tile_1 = []

    for i in range(5,9):
        tile_1.append(cavity_frequencies[f'rr{i}'])

    return [tile_0,tile_1]    