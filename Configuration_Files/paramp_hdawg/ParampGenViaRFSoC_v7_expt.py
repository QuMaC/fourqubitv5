# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 10:38:37 2023

@author: RB

Check the DAC for ParaAmp signal generation
a) Generate two tones
b) Power in two tones to be within 1 dB
c) Tones to be as follows 
        fc = centre frequency between 7 to 8 GHz
        300 MHz <= fSB <= 600 MHz
        thus the two tones will be at fc +- fSB MHz
d) Additionally ...
        
Characterize the signal generated 

"""
#%% Import libraries and dependencies
# from RFSoC_config_25072023_dysl_v1 import *
from RFSoC_PARAMPconfig_08012024_dysl_v1 import *
# from ckt_to_samples_func_v1 import *
import time

# from gen_pulse_fn import gen_pulses

# import standard python libraries

import numpy as np
from matplotlib import pyplot as plt
# %

#%%

def change_current(curr,DAC_no,Tile):
    curr = int(curr*1000)
    # DAC_no = 3
    # Tile = 1

    board.comm_query(f"SetDACVOP {Tile} {DAC_no} {curr}",wait_in_sec = wait_in_sec)  

    return 0

#%%

def gen_pulses(fs_IF, N, f_c, f_sep,  Amp1_offset, Amp1):

    # f_c = 0

    f_1 =  f_c - (f_sep / 2.0) # Tone 1 (lower tone in zone 1)
    f_2 =  f_c + (f_sep / 2.0) # Tone 2 (upper tone in zone 2)

    # Amp2 = 0.5

    # NOTE: Dual tone generation about a central frequency by creating two SSB signals 
    tilde_k_1 = np.floor(N*f_1/fs_IF) # In the interest of minimum deviation in f_c
    tilde_k_2 = np.ceil(N*f_2/fs_IF) # In the interest of minimum deviation in f_c
    tilde_f_1 = fs_IF * tilde_k_1 / N
    tilde_f_2 = fs_IF * tilde_k_2 / N

    Amp2 = 1 * (1 - (Amp1 + Amp1_offset))
    sig1_I = Amp1 * np.cos(2 * np.pi *(tilde_f_1 / fs_IF) * np.arange(N)) + Amp1_offset 
    sig1_Q = Amp1 * np.sin(2 * np.pi *(tilde_f_1 / fs_IF) * np.arange(N)) + 0
    sig2_I = Amp2 * np.cos(2 * np.pi *(tilde_f_2 / fs_IF) * np.arange(N))
    sig2_Q = Amp2 * np.sin(2 * np.pi *(tilde_f_2 / fs_IF) * np.arange(N))
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

#%%

def DAC_prog(board, Type, Tile, Block, F_sample, DAC_current, Cavity_freqs, wave_data):
    # Calculate NCO Frequency
    NCOFreq = F_sample - Cavity_freqs
    # Update the Class object
    board.sys_config[f'DAC_TILE_{Tile}'][f'DAC_{Block}']['NCOFreq'] = NCOFreq
    # Program DAC
    board.program_DAC(DAC_number=Block, DAC_tile=Tile, wait_in_sec = 0.0)
    # Send Data
    board.DAC_BRAM_dataupload(wave_data, DAC_number=Block, DAC_tile=Tile, wait_in_sec = 0.0)

    print('DATA UPLOADED')

    return 0


#%% Configure the board

# # Create board object 
board = RFSoC_auxill("192.168.0.210",userconfig=None,debug=True,logging=False)

#%% USER AND BOARD PARAMETERS

# DUAL TONE PROPERTY DECLARATION
# IF PLAN
f_c = [0e6,0e6,0e6,0e6] # Centre Frequency declaration. 
f_sep = [300e6,800e6,800e6,800e6] # Frequency Separation of dual tones

# AMPLITUDE PLAN
Amp1_offset = [0,0,0,0] # DC Offset
Amp1 = [0.55,0.45,0.55,0.55]

# DAC CURRENT PLAN
DAC_currents = [32,32,32,32]       # currents in mA

# DAC TILE and BLOCK PLAN
Tiles = [1, 1, 1, 1]
Blocks = [0, 1, 2, 3]
Type = 1

# BOARD DAC FIFO SAMPLING RATES
F_sample = 8355.84 # MHz # RF sampling Frequency
Interpolation = 4 # 4: 2x inerpolation
fs_IF = F_sample*1e6/Interpolation # Sampling Frequency of IF
# BOARD DAC PROPERTIES (FOR DIRECT SETTING)
f_firstNyq = 1355.84 # MhZ
Cavity_freqs = [F_sample - f_firstNyq, F_sample - f_firstNyq, F_sample - f_firstNyq, F_sample - f_firstNyq] # 

# PYTHON CODE PARAMETERS
wait_in_sec = 0.0
# NUMBER OF SAMPLES IN I OR Q CHANNEL OF BRAM
N = 8192 * 1
# PREALLOCATION
wave_data = [0,0,0,0]

#%% SET CLOCK FOR BOARD

clk_file = "int_source.tcs"
# clk_file = "ext_source.tcs"
board.set_clock(clk_file, wait_in_sec = wait_in_sec)
# Set Sampling Frequency across DACs
command = f'SetClkDistribution 1 1 245.760000 {F_sample} 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample} 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample} 1 1 1 1 245.760000 1966.080000 1 0 1 1 245.760000 {F_sample} 1 0 1 1 245.760000 1966.080000 1 0'
board.comm_query(command, wait_in_sec = wait_in_sec)

#%% GENERATE DATA

for i in range(len(Blocks)):
    [wave_data[i],_,_] = gen_pulses(fs_IF, N, f_c[i], f_sep[i], Amp1_offset[i], Amp1[i])

#% PROGRAM DAC

for i in range(len(Blocks)):
    DAC_prog(board, Type, Tiles[i], Blocks[i], F_sample, DAC_currents[i], Cavity_freqs[i], wave_data[i])
    
#%% POST CALIBRATION STATUS CHECK / UPDATE

# change_current(32,0,1)
#%%    

# curr = int(25*1000)
# DAC_no = 3
# Tile = 1

# board.comm_query(f"SetDACVOP {Tile} {DAC_no} {curr}",wait_in_sec = wait_in_sec)    

