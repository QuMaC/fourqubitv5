# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 23:43:48 2023

@author: User
Details:    To Test 8 Ch implementations.
            RF Sampling Frequecy: 245.76 * 36 = 8847.36 MHz
            Interpolation Factor: 4x (is 8x in board)
            IF Sampling Frequency FIFO = 8847.36 / 8 = 1105.92 MHz 
            FPGA Clock Rate: IF Sampling Frequency FIFO / 8 = 138.24 MHz
            IF Sampling Frequency Ch = 276.48 MHz
            
            This is derived from CommandSeq_PYTHON_e1 for further tests and bug fixes.
            This is also the test bed for Simultaneous data acquisition
            
"""
import socket
import atexit
import sys
import time
import numpy as np
from datetime import datetime
from types import SimpleNamespace
import matplotlib.pyplot as plt
import pandas as pd # 28042023
import binascii

# import based on the sequence 
# import qiskitPulses_1 as QP
# import Rabi_1 as Rabi
# import Rabi_2 as Rabi_local
# address = 'C:/Users/User/Desktop/SINGULARITY BACKUP/ToPulses/Raghav/ToPulses'
# sys.path.append(address)
# import Pulses_trial1 as gatesSeq 

# from hardware_timing_config_v2 import *
import scipy

def cprint( fmt, fg=None, bg=None, style=None ):
    """
    Colour-printer.
        cprint( 'Hello!' )                                  # normal
        cprint( 'Hello!', fg='g' )                          # green
        cprint( 'Hello!', fg='r', bg='w', style='bx' )      # bold red blinking on white
    List of colours (for fg and bg):
        k   black
        r   red
        g   green
        y   yellow
        b   blue
        m   magenta
        c   cyan
        w   white
    List of styles:
        b   bold
        i   italic
        u   underline
        s   strikethrough
        x   blinking
        r   reverse
        y   fast blinking
        f   faint
        h   hide
    """

    COLCODE = {
        'k': 0, # black
        'r': 1, # red
        'g': 2, # green
        'y': 3, # yellow
        'b': 4, # blue
        'm': 5, # magenta
        'c': 6, # cyan
        'w': 7  # white
    }

    FMTCODE = {
        'b': 1, # bold
        'f': 2, # faint
        'i': 3, # italic
        'u': 4, # underline
        'x': 5, # blinking
        'y': 6, # fast blinking
        'r': 7, # reverse
        'h': 8, # hide
        's': 9, # strikethrough
    }

    # properties
    props = []
    if isinstance(style,str):
        props = [ FMTCODE[s] for s in style ]
    if isinstance(fg,str):
        props.append( 30 + COLCODE[fg] )
    if isinstance(bg,str):
        props.append( 40 + COLCODE[bg] )

    # display
    props = ';'.join([ str(x) for x in props ])
    if props:
        print( '\x1b[%sm%s\x1b[0m' % (props, fmt) )
    else:
        print( fmt )


#%
class Halted(Exception) :
    def __init__(self): sys.tracebacklimit = 0
if hasattr(sys,'tracebacklimit'): del sys.tracebacklimit
# use as raise Halted()

#% 
class ZCU216_RFSoC():

    def __init__(self, addr, data_port=8082, com_port = 8081, logging=True, debug=False):
        #set variables

        self.sys_config ={
                        'RFSoC': {
                            'clksource' : 'int',                #define clock source
                            'IF_interp' : 4,
                            'experiment_timings' : {
                                'control_period' : 40e-6,               # length of control sequences (sec)
                                'readout_period' : 5e-6,                # length of readout pulse (sec)
                                'readout_delay' : 25e-9 + 77e-9,                # delay between end of control and readout pulse begin
                                'marker_start' : 40e-6 + 70e-9,                 # Beginning of marker
                                'marker_width' : 50e-9,                 # width of the marker (sec)
                                'relax_time' : 1e-3,                    # relaxation time after readout
                                'time_of_flight' : 888e-9,              # time of flight for ADC to begin collectiong data
                                'ADC_base_read_timeoffset_1' : 4.000e-6,#4.000e-6,      # 
                                'ADC_base_read_timeoffset_2' : 10e-6,      # 
                                'ADC_readout_window' : 230e-9 # 300e-9 # 230e-9, # 5e-9 
                            }

                        },
                        
#% CONTROL DAC TILE 0 DAC TILE 0 DAC TILE 0 DAC TILE 0 DAC TILE 0 
                        'DAC_TILE_0' : {                           
                            'sample_freq' : 8355.84e6, # 9830.4e6, # 8847.36e6,                           
#% DAC 00
                            'DAC_0' : {
                                'name' : '0_228',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 0 ,                    # 0 1 2 3
                                'Block' : 0 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84,            # MHz (Upto 9830.4 MHz based on Zone etc) (8847.36 - 5048.7 ) + 50 
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
            
                            },
#% DAC 01
                            'DAC_1' : {
                                'name' : '1_228',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 0 ,                    # 0 1 2 3
                                'Block' : 1 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84 ,           # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
#% DAC 02
                            'DAC_2' : {
                                'name' : '2_228',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 0 ,                    # 0 1 2 3
                                'Block' : 2 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84 , # 705.00 ,            # MHz (Upto 9830.4 MHz based on Zone etc) # 1000 on 25042023
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
#% DAC 03                            
                            'DAC_3' : {
                                'name' : '3_228',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 0 ,                    # 0 1 2 3
                                'Block' : 3 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84 ,          # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
                        },
#% CONTROL DAC TILE 2 DAC TILE 2 DAC TILE 2 DAC TILE 2 DAC TILE 2
                        'DAC_TILE_2' : {                           
                            'sample_freq' : 8355.84e6, # 9830.4e6,  
#% DAC 20                          
                            'DAC_0' : {
                                'name' : '0_229',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 2 ,                    # 0 1 2 3
                                'Block' : 0 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84,            # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
            
                            },
#% DAC 21                        
                            'DAC_1' : {
                                'name' : '1_229',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 2 ,                    # 0 1 2 3
                                'Block' : 1 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84 ,            # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
#% DAC 22                        
                            'DAC_2' : {
                                'name' : '2_229',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 2 ,                    # 0 1 2 3
                                'Block' : 2 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84 ,            # MHz (Upto 9830.4 MHz based on Zone etc) # 1000 on 25042023
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
#% DAC 23                        
                            'DAC_3' : {
                                'name' : '3_229',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 2 ,                    # 0 1 2 3
                                'Block' : 3 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84 ,            # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
                        },
                        
#% READOUT DAC TILE 1 DAC TILE 1 DAC TILE 1 DAC TILE 1 DAC TILE 1 
                        'DAC_TILE_1' : {
                            'sample_freq' : 8355.84e6, # 9830.4e6, # 8847.36e6, 
#% DAC 10   
                            'DAC_0' : {
                                'name' : '0_230',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 1 ,                    # 0 1 2 3
                                'Block' : 0 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84,        # 3347.36, # 1411.420000,        # 100.000000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) (8847.36 - 7455.07)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power # 32  
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:                                 
                            },
#% DAC 11                            
                            'DAC_1' : {
                                'name' : '1_230',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 1 ,                    # 0 1 2 3
                                'Block' : 1 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84, # 1724.970000, # old 1392.29, # 2708.010000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) (8847.36 - 7455.07)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power # 32
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
            
                            },
#% DAC 12                            
                            'DAC_2' : {
                                'name' : '2_230',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 1 ,                    # 0 1 2 3
                                'Block' : 2 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84 ,       # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power # 32
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
#% DAC 13                            
                            'DAC_3' : {
                                'name' : '3_230',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 1 ,                    # 0 1 2 3
                                'Block' : 3 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84, # 2630.400000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) # 2708.010000 upto 25042023
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power # 32
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
                        },
                        
#% READOUT DAC TILE 3 DAC TILE 3 DAC TILE 3 DAC TILE 3 DAC TILE 3                         
                        'DAC_TILE_3' : {
                            'sample_freq' : 8355.84e6, # 9830.4e6, # 8847.36e6, 
#% DAC 30   
                            'DAC_0' : {
                                'name' : '0_231',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 3 ,                    # 0 1 2 3
                                'Block' : 0 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84, # 100.000000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) (8847.36 - 7455.07)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power     # 32  
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
#% DAC 31                            
                            'DAC_1' : {
                                'name' : '1_231',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 3 ,                    # 0 1 2 3
                                'Block' : 1 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84, # 1392.42, # old 1392.29, # 2708.010000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) (8847.36 - 7455.07)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power # 32
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
            
                            },
#% DAC 32                            
                            'DAC_2' : {
                                'name' : '2_231',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 3 ,                    # 0 1 2 3
                                'Block' : 2 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84 ,       # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power # 32
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
#% DAC 33                            
                            'DAC_3' : {
                                'name' : '3_231',
                                'Type' : 1 ,                    # ADC 0 DAC 1
                                'Tile' : 3 ,                    # 0 1 2 3
                                'Block' : 3 ,                   # 0 1 2 3
                                'MemType' : 1 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'DataPathMode' : 2 ,            # DUC 1/ IMR LP 2/ *IMR HP 3/ DUC Bypass 4
                                'NyquistZone' : 2 ,             # NyquistZone: (Zone 1:1 / Zone 2:2)
                                'InterpolationFactor' : 2 ,     # (1x to 40x)
                                'DigitalDataPathMask' : '0x1' , # DigitalDataPathMask: 0x1 0x2 0x4 0x8
                                'DataType' : '0x4' ,            # DataType: 1 C2C 2 R2C 4 C2R
                                'DataConverterMask' : '0x1' ,   # DataConverterMask: 0x1 0x2 0x4 0x8
                                'NCOFreq' : 1355.84, # 2630.400000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) # 2708.010000 upto 25042023
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 2 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB
                                'DAC_current' :  32 ,           # DAC output power # 32
                                'DecoderMode' : 2 ,             # 1 : Max SNR, 2: High Linearity
                                'InvSincFirEn' : 0              # 0: Disable InverSincFilter, 1:
                            },
                        },                        
                        
#% READOUT ADC TILE 0 ADC TILE 0 ADC TILE 0 ADC TILE 0 ADC TILE 0
                        'ADC_TILE_0' : {
                            'sample_freq' : 1966.08e6, 
#% ADC 00
                            'ADC_0' : {
                                'name' : '0_224',
                                'Type' : 0 ,                    # ADC 0 DAC 1
                                'Tile' : 0 ,                    # 0 1 2 3
                                'Block' : 0 ,                   # 0 1 2 3
                                'MemType' : 0 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'NCOFreq' : -428.380030,        #-428.380000,        # -398.24, # -428.3799999999999955, # -428.380000, #10002894,#-409.2500100 ,       # MHz (Upto 9830.4 MHz based on Zone etc) -409.25
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 3 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB                                  
                            },
#% ADC 01                            
                            'ADC_1' : {
                                'name' : '1_224',
                                'Type' : 0 ,                    # ADC 0 DAC 1
                                'Tile' : 0 ,                    # 0 1 2 3
                                'Block' : 1 ,                   # 0 1 2 3
                                'MemType' : 0 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'NCOFreq' : -428.380020,        #-428.380000, # -741.9300, # -741.930000 -741.930010002894, # -409.38, # -407.98, # -409.38, #-407.98, # -408.18, # -408.38, # -408.58, # -408.78 # -408.98, # -409.18, # -409.38, # -409.380010002894 , # old -409.250000, # 409.250020 -741.930000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) # -741.930010
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 3 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB  
                            },
#% ADC 02                            
                            'ADC_2' : {
                                'name' : '2_224',
                                'Type' : 0 ,                    # ADC 0 DAC 1
                                'Tile' : 0 ,                    # 0 1 2 3
                                'Block' : 2 ,                   # 0 1 2 3
                                'MemType' : 0 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'NCOFreq' : -041.930060 ,#-041.93 ,       # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 3 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB    


                            },
#% ADC 03                            
                            'ADC_3' : {
                                'name' : '3_224',
                                'Type' : 0 ,                    # ADC 0 DAC 1
                                'Tile' : 0 ,                    # 0 1 2 3
                                'Block' : 3 ,                   # 0 1 2 3
                                'MemType' : 0 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'NCOFreq' : -741.930040005788,#-741.930020005788, # -050.320000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) -741.930020 till 25042023 # -664.320060 
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 3 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB  
                            },
                        },

#% READOUT ADC TILE 1 ADC TILE 1 ADC TILE 1 ADC TILE 1 ADC TILE 1
                        'ADC_TILE_1' : {
                            'sample_freq' : 1966.08e6, 
#% ADC 10
                            'ADC_0' : {
                                'name' : '0_224',
                                'Type' : 0 ,                    # ADC 0 DAC 1
                                'Tile' : 1 ,                    # 0 1 2 3
                                'Block' : 0 ,                   # 0 1 2 3
                                'MemType' : 0 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'NCOFreq' : -041.930050 ,#-041.93 ,       # MHz (Upto 9830.4 MHz based on Zone etc) -409.25
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 3 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB                                  
                            },
#% ADC 11                            
                            'ADC_1' : {
                                'name' : '1_224',
                                'Type' : 0 ,                    # ADC 0 DAC 1
                                'Tile' : 1 ,                    # 0 1 2 3
                                'Block' : 1 ,                   # 0 1 2 3
                                'MemType' : 0 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'NCOFreq' : -432.160030,#-432.1600, # -432.160000, # -432.160030008682, # -409.38, # -407.98, # -409.38, #-407.98, # -408.18, # -408.38, # -408.58, # -408.78 # -408.98, # -409.18, # -409.38, # -409.380010002894 , # old -409.250000, # 409.250020 -741.930000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) # -741.930010
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 3 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB  
                            },
#% ADC 12                            
                            'ADC_2' : {
                                'name' : '2_224',
                                'Type' : 0 ,                    # ADC 0 DAC 1
                                'Tile' : 1 ,                    # 0 1 2 3
                                'Block' : 2 ,                   # 0 1 2 3
                                'MemType' : 0 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'NCOFreq' : -041.930070 ,#-041.93 ,       # MHz (Upto 9830.4 MHz based on Zone etc)
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 3 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB    


                            },
#% ADC 13                            
                            'ADC_3' : {
                                'name' : '3_224',
                                'Type' : 0 ,                    # ADC 0 DAC 1
                                'Tile' : 1 ,                    # 0 1 2 3
                                'Block' : 3 ,                   # 0 1 2 3
                                'MemType' : 0 ,                 # BRAM 1 / DDR 0 % For READ DAC
                                'NCOFreq' : -432.160040,#-432.1600, # -432.160000 -432.160040011576, # -050.320000 ,       # MHz (Upto 9830.4 MHz based on Zone etc) -741.930020 till 25042023 # -664.320060 
                                'NCOPhase' : 0.000000 ,         # Degree -90 to 90 
                                'EventSource' : 2 ,             # EventSource: 2 Tile 3 SYSREF 5 PL event
                                'MixerType' : 2 ,               # MixerType: 2 Fine
                                'CoarseMixFreq' : 0 ,           # CoarseMixFreq: 0 off
                                'MixerMode' : 3 ,               # MixerMode: 2 C2R 3 R2C
                                'FineMixerScale' : 1 ,          # FineMixerScale: 1 0dB  
                            },
                        },
            

                     }

#% ZCU216_RFSoC methods        
        #connection
        self.addr = addr
        self.data_port=data_port
        self.com_port = com_port
        # self.s_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s_dat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug = debug
        self.logging = logging
        # self.log_file = open(f'commandlog.txt', 'a')
        self.log_file = open('commandlog.txt', 'a')
        self.establish_connection()
        self.comm_query("Version")
        self.comm_query("RfdcVersion")
        # Status update
        print('RFSoC PARAMP CLASS')
        time.sleep(1)

        ##Exit
        # self.break_connection()
        # atexit.register(self.break_connection()) # for closing connection if anything crashes
        return

    def establish_connection(self):
        self.s_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_dat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 20062023
        self.s_com.settimeout(10)
        self.s_dat.settimeout(10)
        # 20062023
        self.s_com.connect((self.addr, self.com_port))
        self.s_dat.connect((self.addr, self.data_port))
        cprint("Connection Established.",'w','g','b')
    
    def break_connection(self):
        self.s_com.shutdown(socket.SHUT_RDWR)
        self.s_com.close()
        self.s_dat.shutdown(socket.SHUT_RDWR)
        self.s_dat.close()
        self.log_file.close()
        cprint("Connection Closed.",'r','g')

    def send_data(self,command, data,buffer=4096): # What data is this ? Answer: This is information of data size to be sent (in samples and in bytes)
        fcom = (command + '\r\n').encode('ascii')
        self.s_dat.send(fcom) 
        time.sleep(0.2)
        print('------------------------------COMMAND SENT----------------------------')
        # fcom = (str(data)[1:-1]).encode('ascii')
        fcom = (str(data)).encode('ascii')
        self.s_dat.send(data.tobytes())
        time.sleep(1)
        print('-----------------------------DATA SENT--------------------------------')
        answer=''
        while True:
            answer += self.s_dat.recv(buffer).decode()
            if "\n" in answer : break
        answer = answer[:-2]
        if self.debug : print(answer)
        if "ERROR" in answer : cprint(answer, fg='r', bg='w', style='bx')
        if self.logging :  self.log_file.write(f'{datetime.now().strftime("%m/%d/%Y %H:%M:%S    ")}{command}    Ans: {answer}\n')
           
        return answer
        # return
        
    def comm_query(self, command, buffer=4096, wait_in_sec = 0.75):
        fcom = (command + '\r\n').encode('ascii')
        self.s_com.send(fcom)
        time.sleep(wait_in_sec)
        answer=''
        while True:
            answer += self.s_com.recv(buffer).decode()
            if "\n" in answer : break
        answer = answer[:-2]
        if self.debug : print(answer)
        if "ERROR" in answer : cprint(answer, fg='r', bg='w', style='bx')
        if self.logging :  self.log_file.write(f'{datetime.now().strftime("%m/%d/%Y %H:%M:%S    ")}{command}    Ans: {answer}\n')           
        return answer
        # return

    def set_clock(self,tcsfile, wait_in_sec = 0.25):
        '''
        This function parses tcs files for clock settings and sets these clock settings on the board.
        Inputs:
        tcsfile -> path of the input clock settings file
        clk104 -> address of the chip. 2 for the big clock and 0 LM2594 ADC and 1 for LM2594 DAC
        '''
        opened_file = open(tcsfile,'r')
        lines = opened_file.readlines()
        settings = []
        for line in lines:
            if 'VALUE' in line[:5]:
                settings.append(line[:-1].split('='))

        cprint("TCS file read, beginning clock programming.",fg='g')
        self.comm_query('SetStartEndClkConfig 1', wait_in_sec = wait_in_sec)
        for entry in settings:
            tp = hex(int(entry[1]))[2:].zfill(6)  #read relevant value, convert to hex and pad it
            command = "rfclkWriteReg 0x0 0x{} 0x{} 0x{}".format(2, tp[:4], tp[4:])
            self.comm_query(command, wait_in_sec = wait_in_sec)
        self.comm_query('SetStartEndClkConfig 0', wait_in_sec = wait_in_sec)
        cprint("RFSoC clock settings programmed.",fg='g')

    def set_clock_dist(self, wait_in_sec = 0.0): #TODO : integrate function frequency_planner and change fs according to dictionary
        cprint('Setting clock distribution','b')
        # command = 'SetClkDistribution 1 1 245.760000 9093.120000 1 0 5 1 245.760000 1966.080000 1 0 1 1 245.760000 9830.400000 1 0 5 1 245.760000 1966.080000 1 0 1 1 245.760000 9830.400000 1 1 5 1 245.760000 1966.080000 1 1 1 1 245.760000 9830.400000 1 0 5 1 245.760000 1966.080000 1 0'
        # command = 'SetClkDistribution 1 1 245.760000 9830.400000 1 0 5 1 245.760000 1966.080000 1 0 1 1 245.760000 9830.400000 1 0 5 1 245.760000 1966.080000 1 0 1 1 245.760000 9830.400000 1 1 5 1 245.760000 1966.080000 1 1 1 1 245.760000 9830.400000 1 0 5 1 245.760000 1966.080000 1 0'
        # command = 'SetClkDistribution 1 1 245.760000 8847.360000 1 0 5 1 245.760000 1966.080000 1 0 1 1 245.760000 8847.360000 1 0 5 1 245.760000 1966.080000 1 0 1 1 245.760000 8847.360000 1 1 5 1 245.760000 1966.080000 1 1 1 1 245.760000 8847.360000 1 0 5 1 245.760000 1966.080000 1 0'
        # command = 'SetClkDistribution 1 1 245.760000 8847.360000 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 8847.360000 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 8847.360000 1 1 1 1 245.760000 1966.080000 1 0 1 1 245.760000 8847.360000 1 0 1 1 245.760000 1966.080000 1 0'
        command = 'SetClkDistribution 1 1 245.760000 8847.360000 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 8847.360000 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 8847.360000 1 1 1 1 245.760000 1966.080000 1 0 1 1 245.760000 8847.360000 1 0 1 1 245.760000 1966.080000 1 0'
        # command = 'SetClkDistribution 1 1 245.760000 9830.400000 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 9830.400000 1 0 1 1 245.760000 1966.080000 1 0 1 1 245.760000 9830.400000 1 1 1 1 245.760000 1966.080000 1 0 1 1 245.760000 9830.400000 1 0 1 1 245.760000 1966.080000 1 0'
        # Set DAC Tile 0 fs, ADC Tile 0 fs, DAC Tile 1 fs, ADC Tile 1 fs .....
        # 245.76 is the PLL Clock
        
        self.comm_query(command, wait_in_sec = wait_in_sec)

        # Sets clock to be distributed to each DAC and ADC tile from DAC Tile 2. 
        # set MixedMode clock Module argumetns -> Type, Tile
        self.comm_query("SetMMCM 1 0", wait_in_sec = wait_in_sec)
        self.comm_query("SetMMCM 1 1", wait_in_sec = wait_in_sec)
        self.comm_query("SetMMCM 1 2", wait_in_sec = wait_in_sec)
        self.comm_query("SetMMCM 1 3", wait_in_sec = wait_in_sec)
        self.comm_query("SetMMCM 0 0", wait_in_sec = wait_in_sec)
        self.comm_query("SetMMCM 0 1", wait_in_sec = wait_in_sec)
        self.comm_query("SetMMCM 0 2", wait_in_sec = wait_in_sec)
        self.comm_query("SetMMCM 0 3", wait_in_sec = wait_in_sec)

        cprint('Clock distribution programmed.',fg='g')
        return

    def set_timings(self,DAC_tile, SlotsPerMS = 25,wait_in_sec = 0.0): 
        cprint(f"Beginning programming of timing windows on DAC Tile {DAC_tile}.",fg='b')
        # DDR_bus_freq = self.sys_config[f"DAC_TILE_{DAC_tile}"]['sample_freq'] / (self.sys_config['RFSoC']['IF_interp']*2*4*2) # denominator -> interpolation factor x 2 IQ channels * 4 DACS * 2 mysterious
        DDR_bus_freq = self.sys_config[f"DAC_TILE_{DAC_tile}"]['sample_freq'] / (self.sys_config['RFSoC']['IF_interp']*2*4*2) # denominator -> interpolation factor x 2 IQ channels * 4 DACS * 2 mysterious
        timing = SimpleNamespace(**self.sys_config['RFSoC']['experiment_timings'])

        mark_start = int(DDR_bus_freq * timing.marker_start)
        mark_end = int(DDR_bus_freq * (timing.marker_start + timing.marker_width))
        print(f"Marker_Pulse {mark_start} {mark_end}")
        self.comm_query(f"Marker_Pulse {mark_start} {mark_end}", wait_in_sec = wait_in_sec)

        Board_DAC_fs = self.sys_config[f"DAC_TILE_{DAC_tile}"]['sample_freq'] # 8847.36e6 # 9830.4e6; 
        QuSlotWin = self.sys_config['RFSoC']['experiment_timings']['control_period'] # 40e-6;
        fs = Board_DAC_fs / 32 # 8x (for 4x interpolation) * 4 Channels per DDR
        QuSlotWin_N = int(round(QuSlotWin * fs / 16) * 16) * 4; # 
        control = (QuSlotWin_N // 8) - 1  # 5527 # 6143 # 5527 # (QuSlotWin_N // 8) - 1 # 8 I are streaming at every clock 
        print(f"Qubit {control}")
        self.comm_query(f"Qubit {control}", wait_in_sec = wait_in_sec)
        
        pulse_period = ((QuSlotWin_N // 8) * SlotsPerMS) - 1 # 138199 # 153599 # 138199 # ((QuSlotWin_N // 8) * 25) - 1 # 153599 # int(DDR_bus_freq * (timing.control_period + timing.readout_delay + timing.readout_period + timing.relax_time))  # TODO : Might need to change this in conditionals like ACtive reset
        print(f"Pulse_Period {pulse_period}")
        self.comm_query(f"Pulse_Period {pulse_period}", wait_in_sec = wait_in_sec)

        readout_start = int(DDR_bus_freq * (timing.control_period + timing.readout_delay))
        readout_stop = int(DDR_bus_freq * (timing.control_period + timing.readout_delay + timing.readout_period))
        print(f"Readout_Pulse {readout_start} {readout_stop}")
        self.comm_query(f"Readout_Pulse {readout_start} {readout_stop}", wait_in_sec = wait_in_sec)

        ADC_read_TOFdelay = int(DDR_bus_freq * timing.time_of_flight) # based on time of flight (time between start to read tx to start of read Rx)
        ADC_Enable_1_IR_delay = int(DDR_bus_freq * timing.ADC_base_read_timeoffset_1) # Impulse response delay based on filter design
        ADC_Enable_2_UR_delay = int(DDR_bus_freq * timing.ADC_base_read_timeoffset_2) # User defined delay (to read noise)
        ADC_base_delay_1 = readout_start + ADC_read_TOFdelay + ADC_Enable_1_IR_delay
        ADC_base_delay_2 = readout_start + ADC_read_TOFdelay + ADC_Enable_2_UR_delay
        ADC_window = int(DDR_bus_freq * timing.ADC_readout_window) # Window to capture single sample from the ADC processed data
        # ADC Enable 1
        print(f"ADC_Enable_one {ADC_base_delay_1} {ADC_window + ADC_base_delay_1}")
        self.comm_query(f"ADC_Enable_one {ADC_base_delay_1} {ADC_window + ADC_base_delay_1}", wait_in_sec = wait_in_sec)
        # ADC Enable 2
        print(f"ADC_Enable_two {ADC_base_delay_2} {ADC_window + ADC_base_delay_2}")
        self.comm_query(f"ADC_Enable_two {ADC_base_delay_2} {ADC_window + ADC_base_delay_2}", wait_in_sec = wait_in_sec)

        cprint(f"Experiment timing windows programmed for DAC Tile {DAC_tile}.",fg='g')

        return
    
    def set_timings_v1(self, DAC_tile, DAC_block, SlotsPerMS = 25,wait_in_sec = 0.0):
        cprint(f"Beginning programming of timing windows on DAC Tile {DAC_tile} and DAC Block {DAC_block}.",fg='b')
        DDR_bus_freq = self.sys_config[f"DAC_TILE_{DAC_tile}"]['sample_freq'] / (self.sys_config['RFSoC']['IF_interp']*2*4*2) # denominator -> interpolation factor x 2 IQ channels * 4 DACS * 2 mysterious
        timing = SimpleNamespace(**self.sys_config['RFSoC']['experiment_timings'])

        mark_start = int(DDR_bus_freq * timing.marker_start)
        mark_end = int(DDR_bus_freq * (timing.marker_start + timing.marker_width))
        print(f"Marker_Pulse {DAC_tile} {DAC_block} {mark_start} {mark_end}")
        self.comm_query(f"Marker_Pulse {DAC_tile} {DAC_block} {mark_start} {mark_end}", wait_in_sec = wait_in_sec)

        Board_DAC_fs = self.sys_config[f"DAC_TILE_{DAC_tile}"]['sample_freq'] # 8847.36e6 # 9830.4e6; 
        QuSlotWin = self.sys_config['RFSoC']['experiment_timings']['control_period'] # 40e-6;
        fs = Board_DAC_fs / 32 # 8x (for 4x interpolation) * 4 Channels per DDR
        QuSlotWin_N = int(round(QuSlotWin * fs / 16) * 16) * 4; # 
        control = (QuSlotWin_N // 8) - 1  # 5527 # 6143 # 5527 # (QuSlotWin_N // 8) - 1 # 8 I are streaming at every clock 
        print(f"Qubit {DAC_tile} {DAC_block} {control}")
        self.comm_query(f"Qubit {DAC_tile} {DAC_block} {control}", wait_in_sec = wait_in_sec)
        
        pulse_period = ((QuSlotWin_N // 8) * SlotsPerMS) - 1 # 138199 # 153599 # 138199 # ((QuSlotWin_N // 8) * 25) - 1 # 153599 # int(DDR_bus_freq * (timing.control_period + timing.readout_delay + timing.readout_period + timing.relax_time))  # TODO : Might need to change this in conditionals like ACtive reset
        print(f"Pulse_Period {DAC_tile} {DAC_block} {pulse_period}")
        self.comm_query(f"Pulse_Period {DAC_tile} {DAC_block} {pulse_period}", wait_in_sec = wait_in_sec)

        readout_start = int(DDR_bus_freq * (timing.control_period + timing.readout_delay))
        readout_stop = int(DDR_bus_freq * (timing.control_period + timing.readout_delay + timing.readout_period))
        print(f"Readout_Pulse {readout_start} {readout_stop}")
        self.comm_query(f"Readout_Pulse {DAC_tile} {DAC_block} {readout_start} {readout_stop}", wait_in_sec = wait_in_sec)

        ADC_read_TOFdelay = int(DDR_bus_freq * timing.time_of_flight) # based on time of flight (time between start to read tx to start of read Rx)
        ADC_Enable_1_IR_delay = int(DDR_bus_freq * timing.ADC_base_read_timeoffset_1) # Impulse response delay based on filter design
        ADC_Enable_2_UR_delay = int(DDR_bus_freq * timing.ADC_base_read_timeoffset_2) # User defined delay (to read noise)
        ADC_base_delay_1 = readout_start + ADC_read_TOFdelay + ADC_Enable_1_IR_delay
        ADC_base_delay_2 = readout_start + ADC_read_TOFdelay + ADC_Enable_2_UR_delay
        ADC_window = int(DDR_bus_freq * timing.ADC_readout_window) # Window to capture single sample from the ADC processed data
        # ADC Enable 1
        print(f"ADC_Enable_one {DAC_tile} {DAC_block} {ADC_base_delay_1} {ADC_window + ADC_base_delay_1}")
        self.comm_query(f"ADC_Enable_one {DAC_tile} {DAC_block} {ADC_base_delay_1} {ADC_window + ADC_base_delay_1}", wait_in_sec = wait_in_sec)
        # ADC Enable 2
        print(f"ADC_Enable_two {ADC_base_delay_2} {ADC_window + ADC_base_delay_2}")
        self.comm_query(f"ADC_Enable_two {DAC_tile} {DAC_block} {ADC_base_delay_2} {ADC_window + ADC_base_delay_2}", wait_in_sec = wait_in_sec)

        cprint(f"Experiment timing windows programmed for DAC Tile {DAC_tile} DAC Block {DAC_block}.",fg='g')
        
        return
    
    def DisableRTS(self): # added 23062023 to check power level fluctuation
        # DACs
        self.comm_query('SetDecoderMode 0 0 2') # High Linearity Setting
        self.comm_query('SetDecoderMode 0 1 2')
        self.comm_query('SetDecoderMode 0 2 2')
        self.comm_query('SetDecoderMode 0 3 2')
        
        self.comm_query('SetDecoderMode 1 0 2')
        self.comm_query('SetDecoderMode 1 1 2')
        self.comm_query('SetDecoderMode 1 2 2')
        self.comm_query('SetDecoderMode 1 3 2')
        
        self.comm_query('SetDecoderMode 2 0 2')
        self.comm_query('SetDecoderMode 2 1 2')
        self.comm_query('SetDecoderMode 2 2 2')
        self.comm_query('SetDecoderMode 2 3 2')
        
        self.comm_query('SetDecoderMode 3 0 2')
        self.comm_query('SetDecoderMode 3 1 2')
        self.comm_query('SetDecoderMode 3 2 2')
        self.comm_query('SetDecoderMode 3 3 2')
        # DACs
        self.comm_query('SetPwrMode 1 0 0 1 1')
        self.comm_query('SetPwrMode 1 0 1 1 1')
        self.comm_query('SetPwrMode 1 0 2 1 1')
        self.comm_query('SetPwrMode 1 0 3 1 1')
        
        self.comm_query('SetPwrMode 1 1 0 1 1')
        self.comm_query('SetPwrMode 1 1 1 1 1')
        self.comm_query('SetPwrMode 1 1 2 1 1')
        self.comm_query('SetPwrMode 1 1 3 1 1')
        
        self.comm_query('SetPwrMode 1 2 0 1 1')
        self.comm_query('SetPwrMode 1 2 1 1 1')
        self.comm_query('SetPwrMode 1 2 2 1 1')
        self.comm_query('SetPwrMode 1 2 3 1 1')
        
        self.comm_query('SetPwrMode 1 3 0 1 1')
        self.comm_query('SetPwrMode 1 3 1 1 1')
        self.comm_query('SetPwrMode 1 3 2 1 1')
        self.comm_query('SetPwrMode 1 3 3 1 1')
        # ADCs
        self.comm_query('SetPwrMode 0 0 0 1 1')
        self.comm_query('SetPwrMode 0 0 1 1 1')
        self.comm_query('SetPwrMode 0 0 2 1 1')
        self.comm_query('SetPwrMode 0 0 3 1 1')
        
        self.comm_query('SetPwrMode 0 1 0 1 1')
        self.comm_query('SetPwrMode 0 1 1 1 1')
        self.comm_query('SetPwrMode 0 1 2 1 1')
        self.comm_query('SetPwrMode 0 1 3 1 1')
        
        self.comm_query('SetPwrMode 0 2 0 1 1')
        self.comm_query('SetPwrMode 0 2 1 1 1')
        self.comm_query('SetPwrMode 0 2 2 1 1')
        self.comm_query('SetPwrMode 0 2 3 1 1')
        
        self.comm_query('SetPwrMode 0 3 0 1 1')
        self.comm_query('SetPwrMode 0 3 1 1 1')
        self.comm_query('SetPwrMode 0 3 2 1 1')
        self.comm_query('SetPwrMode 0 3 3 1 1')
        
        
        
    def program_DAC(self,DAC_number,DAC_tile=0,wait_in_sec = 0.0):
        dacset = SimpleNamespace(**self.sys_config[f'DAC_TILE_{DAC_tile}'][f'DAC_{DAC_number}'])
        cprint(f" Programming DAC {dacset.name} (DAC {DAC_number}, Tile {DAC_tile})...",fg='b')

        self.comm_query(f"SetMemType {dacset.Type} {dacset.Tile} {dacset.MemType}",wait_in_sec = wait_in_sec)              
        self.comm_query(f"SetDataPathMode {dacset.Tile} {dacset.Block} {dacset.DataPathMode}",wait_in_sec = wait_in_sec)  
        self.comm_query(f"SetMMCM {dacset.Type} {dacset.Tile}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetNyquistZone {dacset.Type} {dacset.Tile} {dacset.Block} {dacset.NyquistZone}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetupFIFO {dacset.Type} {dacset.Tile} {0}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetInterpolationFactor {dacset.Tile} {dacset.Block} {dacset.InterpolationFactor}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetMMCM {dacset.Type} {dacset.Tile}",wait_in_sec = wait_in_sec)
        self.comm_query(f"IntrClr {dacset.Type} {dacset.Tile} {dacset.Block} {'0xFFFFFFFF'}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetupFIFO {dacset.Type} {dacset.Tile} {1}",wait_in_sec = wait_in_sec)
        self.comm_query(f"MultiBand {dacset.Type} {dacset.Tile} {dacset.DigitalDataPathMask} {dacset.DataType} {dacset.DataConverterMask}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetMixerSettings {dacset.Type} {dacset.Tile} {dacset.Block} {'%.12g' % dacset.NCOFreq} {'%.12g' % dacset.NCOPhase} {dacset.EventSource} {dacset.MixerType} {dacset.CoarseMixFreq} {dacset.MixerMode} {dacset.FineMixerScale}",wait_in_sec = wait_in_sec)
        self.comm_query(f"ResetNCOPhase {dacset.Type} {dacset.Tile} {dacset.Block}",wait_in_sec = wait_in_sec)
        self.comm_query(f"UpdateEvent {dacset.Type} {dacset.Tile} {dacset.Block} {1}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetDACVOP {dacset.Tile} {dacset.Block} {dacset.DAC_current*1000}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetDecoderMode {dacset.Tile} {dacset.Block} {dacset.DecoderMode}",wait_in_sec = wait_in_sec)  # High Linearity vs SNR Optimised
        self.comm_query(f"SetInvSincFir {dacset.Tile} {dacset.Block} {dacset.InvSincFirEn}",wait_in_sec = wait_in_sec)

        cprint(f"DAC {dacset.name} (DAC {DAC_number}, Tile {DAC_tile}) settings programmed.",fg='g')
        return 
    
    def program_ADC(self,ADC_number,ADC_tile,wait_in_sec = 0.0):
        adcset = SimpleNamespace(**self.sys_config[f'ADC_TILE_{ADC_tile}'][f'ADC_{ADC_number}'])
        cprint(f"Programming ADC {adcset.name} (ADC {ADC_number}, Tile {ADC_tile})...",fg='b')

        self.comm_query(f"SetMemType {adcset.Type} {adcset.Tile} {adcset.MemType}",wait_in_sec = wait_in_sec)
        self.comm_query(f"SetMixerSettings {adcset.Type} {adcset.Tile} {adcset.Block} {'%.12g' % adcset.NCOFreq} {'%.12g' % adcset.NCOPhase} {adcset.EventSource} {adcset.MixerType} {adcset.CoarseMixFreq} {adcset.MixerMode} {adcset.FineMixerScale}",wait_in_sec = wait_in_sec)
        self.comm_query(f"ResetNCOPhase {adcset.Type} {adcset.Tile} {adcset.Block}",wait_in_sec = wait_in_sec)
        self.comm_query(f"UpdateEvent {adcset.Type} {adcset.Tile} {adcset.Block} {'1'}",wait_in_sec = wait_in_sec)

        cprint(f"ADC {adcset.name} (ADC {ADC_number}, Tile {ADC_tile}) settings programmed.",fg='g')

        return

    # def enable_MTS(self):

    #     for which in ["DAC","ADC"]:
    #         self.program_MTS(which)
    #         cprint(f"Enabling Multi-Tile sync for {which}. \n  DO NOT RUN THIS AGAIN UNTIL REBOOT.",'b')
    #         #Equivalent of EventSource_REF script below, sets the correct eventsource
    #         for i in range(4):
    #             for j in range(4):
    #                     try:
    #                         dacset = SimpleNamespace(**self.sys_config[f'{which}_TILE_{i}'][f'{which}_{j}'])
    #                         self.comm_query(f"SetMixerSettings {dacset.Type} {dacset.Tile} {dacset.Block} {'%.12g' % dacset.NCOFreq} {'%.12g' % dacset.NCOPhase} {3} {dacset.MixerType} {dacset.CoarseMixFreq} {dacset.MixerMode} {dacset.FineMixerScale}")
    #                     except (AttributeError,KeyError): continue

    #         cprint(f'Multi-Tile sync enabled for {which}.',fg='g')
        
    #     self.comm_query('User_Sync 1')
    #     time.sleep(20)
    #     self.comm_query("User_Sync 0")
    
    #     return
    
    def enable_MTS1(self, mtsIndDAC = 15, mtsIndADC = 15, wait_in_sec = 0.0):
        # mtsInd is one hot encoded. All DACs and ADCs which need to be setup for MTS are represented by a 1 else 0
        for which in ["DAC","ADC"]:
            if which == "DAC": mtsInd = mtsIndDAC
            elif which == "ADC" : mtsInd = mtsIndADC
            self.setup_MTS(which, mtsInd, wait_in_sec = wait_in_sec)
            cprint(f"Chosen {which} Tiles have MTS enabled", fg = 'r')
        # cprint(f"\nDO NOT RUN THIS AGAIN UNTIL REBOOT.",'b')
        cprint("\nDO NOT RUN THIS AGAIN UNTIL REBOOT.",'b')
        # Choose event source to be SYSREF for the chosen DACs and ADCs and set respective frequencies and phase, etc
        for which in ["DAC","ADC"]:
            if which == "DAC": mtsInd = mtsIndDAC
            elif which == "ADC" : mtsInd = mtsIndADC
            # NameSpaceDacSet = self.set_EventSource(which, mtsInd)
            self.set_EventSource(which, mtsInd, wait_in_sec = wait_in_sec)
        # Provide the User Sync Signal
        self.comm_query('User_Sync 1', wait_in_sec = wait_in_sec)
        print("User Sync ON")
        time.sleep(3) # 10 DONT REDUCE THIS TIME !!!
        self.comm_query("User_Sync 0", wait_in_sec = wait_in_sec)
        print("User Sync OFF")
            
        return # NameSpaceDacSet
    
    def setup_MTS(self, which, mtsInd = 15, mtsclk = 122880, wait_in_sec = 0.5):
        # should only be run once!!!!
        if which == "ADC" : tp = 0
        elif which == "DAC" : tp = 1
        
        self.comm_query(f"MTS_Setup {tp} {hex(mtsInd)}", wait_in_sec = wait_in_sec)
        print(f"MTS_Setup {tp} {hex(mtsInd)}")
        # time.sleep(wait_time)
        k = 1
        while bin(mtsInd)[-k] != 'b':
            if int(bin(mtsInd)[-k]) == 1:
                self.comm_query(f"SetMMCMFin {tp} {k-1} {mtsclk}", wait_in_sec = wait_in_sec)
                print(f"SetMMCMFin {tp} {k-1} {mtsclk}")
                # time.sleep(wait_time)
            k += 1
        self.comm_query(f"MultiConverter_Init {tp}", wait_in_sec = wait_in_sec)
        print(f"MultiConverter_Init {tp}")
        # time.sleep(wait_time)
        self.comm_query(f"MultiConverter_Sync {tp} {-1} {mtsInd}", wait_in_sec = wait_in_sec) 
        print(f"MultiConverter_Sync {tp} {-1} {mtsInd}")
        # time.sleep(wait_time)
        cprint(f"Chosen {which}s have MTS enabled", fg = 'r')

    def update_MTS1(self,mtsIndDAC,mtsIndADC, wait_in_sec = 0.5):
        for which in ["DAC","ADC"]:
            if which == "DAC": mtsInd = mtsIndDAC
            elif which == "ADC" : mtsInd = mtsIndADC
            # NameSpaceDacSet = self.set_EventSource(which, mtsInd)
            self.set_EventSource(which, mtsInd, wait_in_sec = wait_in_sec)
        # Provide the User Sync Signal
        self.comm_query('User_Sync 1', wait_in_sec = wait_in_sec)
        print("User Sync ON")
        time.sleep(3) # DONT REDUCE THIS TIME !!!
        self.comm_query("User_Sync 0", wait_in_sec = wait_in_sec)
        print("User Sync OFF")        
        
    def set_EventSource(self, which, mtsInd = 15, EventSource = 3, wait_in_sec = 0.5):
        
        k = 1
        while bin(mtsInd)[-k] != 'b': # iterate through the tiles
            if int(bin(mtsInd)[-k]) == 1: # if tile is selected for MTS
                for j in np.arange(4): # then iterate through the blocks
                    # try:
                        dacset = SimpleNamespace(**self.sys_config[f'{which}_TILE_{k-1}'][f'{which}_{j}'])
                        if len(dacset.__dict__) != 0: # Incase the dictionery is not defined
                            # print([f'{which}_TILE_{k-1}'][f'{which}_{j}'])
                            self.comm_query(f"SetMixerSettings {dacset.Type} {dacset.Tile} {dacset.Block} {'%.12g' % dacset.NCOFreq} {'%.12g' % dacset.NCOPhase} {EventSource} {dacset.MixerType} {dacset.CoarseMixFreq} {dacset.MixerMode} {dacset.FineMixerScale}", wait_in_sec = wait_in_sec)
                            print(f"SetMixerSettings {dacset.Type} {dacset.Tile} {dacset.Block} {'%.12g' % dacset.NCOFreq} {'%.12g' % dacset.NCOPhase} {EventSource} {dacset.MixerType} {dacset.CoarseMixFreq} {dacset.MixerMode} {dacset.FineMixerScale}")
                    # except (AttributeError,KeyError): continue
                    # except (KeyError): continue
                # time.sleep(wait_time)
            k += 1
        
        return # dacset
    
    # def program_MTS(self,which,wait_time=1):
        
    #     # shoould only be run once!!!!
    #     if which == "ADC" : tp = 0
    #     elif which == "DAC" : tp = 1

    #     self.comm_query(f"MTS_Setup {tp} {0x3}")
    #     time.sleep(wait_time)
    #     self.comm_query(f"SetMMCMFin {tp} {0} {122880}") # 122880 in Hz, fixed freq, PL CLK
    #     time.sleep(wait_time)
    #     self.comm_query(f"SetMMCMFin {tp} {1} {122880}")
    #     time.sleep(wait_time)
    #     self.comm_query(f"MultiConverter_Init {tp}")
    #     time.sleep(wait_time)
    #     self.comm_query(f"MultiConverter_Sync {tp} {-1} {3}")

    def anglecorr(self,angle):

        #ASK: Following were in EVENTSource_SYSREF, what can be generalized?
        # the frequencies below cna be changed (I think), and angle 
        #TODO : Program DACs and ADCs after MTS, add rdac and adc dictionary
        #TODO: Set frequemcies as per NCO frequencies set in dictionary
        self.comm_query(f'SetMixerSettings 1 1 0 2575.83 {angle} 3 2 0 2 1')
        self.comm_query(f'SetMixerSettings 1 1 2 2575.83 {angle} 3 2 0 2 1')
        self.comm_query(f'SetMixerSettings 0 0 0 {-609.750000}') #ASK: There's a space here, does it need to be there?
        self.comm_query(f'SetMixerSettings 0 0 2 {-609.750000}')

        # Trigger for MTS to  actaully start, and tile NCOs to restart
        self.comm_query(f"User_Sync {1}")
        time.sleep(3)
        self.comm_query(f"User_Sync {0}")

        ## Confirm SYNC
        self.comm_query(f'GetMixerSettings 1 1 {0}')
        self.comm_query(f'GetMixerSettings 1 1 {2}')
        self.comm_query(f'GetMixerSettings 0 0 {0}')
        self.comm_query(f'GetMixerSettings 0 0 {2}')

        return

    def DAC_control_dataupload_trigger(self, data, LocalMemTrigger, only_trigger_DAC = True, DAC_number = 3, DAC_tile=0 ):  #ASK: What is LocalMemTrigger, how to generalize it?
        """
        """
        cdacset = SimpleNamespace(**self.sys_config[f'DAC_TILE_{DAC_tile}'][f'DAC_{DAC_number}'])
        clksel=0
        
        self.comm_query(f"LocalMemInfo {cdacset.Type}")
        self.comm_query(f"LocalMemTrigger {cdacset.Type} {clksel} {0} {'0x0000'}")  # Number of samples would be /2 becuase MSB+LSB and /2 because (I,Q)
        self.comm_query(f"SetLocalMemSample {cdacset.Type} {cdacset.Tile} {cdacset.Block} {data.size//2}")
        time.sleep(2)
        if not only_trigger_DAC:
            self.send_data(f"WriteDataToMemory {cdacset.Tile} {cdacset.Block} {data.size} {1}", data) 
            time.sleep(2)
        self.comm_query(f"LocalMemTrigger {cdacset.Type} {clksel} {0} {LocalMemTrigger}")
        self.comm_query(f"LocalMemInfo {cdacset.Type}")
        # cprint(f"Control Data Sent. {cdacset.name} DAC active (DAC {DAC_number}, Tile {DAC_tile})",'g')
        cprint(f"Control Data Sent for DAC {DAC_number}, Tile {DAC_tile}",'g')
        return
    
    def DAC_control_dataupload(self, data, DDR_Num, only_trigger_DAC = True, DAC_number = 3, DAC_tile=0 ):  #ASK: What is LocalMemTrigger, how to generalize it?
        """
        """
        cdacset = SimpleNamespace(**self.sys_config[f'DAC_TILE_{DAC_tile}'][f'DAC_{DAC_number}'])
        clksel=0
        
        self.comm_query(f"LocalMemInfo {cdacset.Type}")
        if DDR_Num == 1:
            self.comm_query(f"LocalMemTrigger {cdacset.Type} {clksel} {0} {'0x0000'}")  # Number of samples would be /2 becuase MSB+LSB and /2 because (I,Q)
        elif DDR_Num == 2:
            self.comm_query(f"LocalMemTriggerDDR {cdacset.Type} {clksel} {0} {'0x0000'}")  # Number of samples would be /2 becuase MSB+LSB and /2 because (I,Q)
        else:
            print('Wrong DDR chosen please start over !!!!!')
        self.comm_query(f"SetLocalMemSample {cdacset.Type} {cdacset.Tile} {cdacset.Block} {data.size//2}")
        time.sleep(2)
        if not only_trigger_DAC:
            self.send_data(f"WriteDataToMemory {cdacset.Tile} {cdacset.Block} {data.size} {1}", data) 
            time.sleep(2)
        cprint(f"Control Data Sent for DAC {DAC_number}, Tile {DAC_tile}",'g')
        return

    def DAC_readout_enable(self,DAC_number=0, DAC_tile=1, wait_in_sec = 0.0):
        
        LMTstring = self.DACADC_LMTString(DAC_number, DAC_tile)
        
        rdacset = SimpleNamespace(**self.sys_config[f'DAC_TILE_{DAC_tile}'][f'DAC_{DAC_number}'])
        clksel = 0
        wvf = np.ones(256*16)   #256*16 = 4096 block size fixed for BRAM (Readout DACS)
        wvf = (wvf * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) / 2 + (np.iinfo(np.int16).max + np.iinfo(np.int16).min) / 2).astype('int16')

        wvf_I = wvf
        wvf_Q = wvf

        data = np.array([wvf_I, wvf_Q]).flatten('F')

        # MSB_LSB_data = np.vstack((data >> 8, data - ((data >> 8) << 8)))
        MSB_LSB_data = np.vstack((data - ((data >> 8) << 8), data >> 8))
        
        data = MSB_LSB_data.flatten("F").astype('uint8')

        cprint(f"Sending data to DAC {DAC_number}, Tile {DAC_tile}. ({rdacset.name})",'b')
        self.comm_query(f"LocalMemInfo {rdacset.Type}", wait_in_sec = wait_in_sec)
        self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {0} {'0x0000'}", wait_in_sec = wait_in_sec)
        self.comm_query(f"SetLocalMemSample {rdacset.Type} {rdacset.Tile} {rdacset.Block} {data.size//2}", wait_in_sec = wait_in_sec)
        time.sleep(0.25)
        self.send_data(f"WriteDataToMemory {rdacset.Tile} {rdacset.Block} {data.size} {1}", data)
        time.sleep(0)
        # self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {wvf.size} {'0xFFFF'}")
        # self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {wvf.size} {'0x00F0'}")
        # self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {wvf.size} {'0xF0F0'}")
        self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {0} {LMTstring}", wait_in_sec = wait_in_sec)
        time.sleep(0)
        self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {0} {0xF0F0}", wait_in_sec = wait_in_sec) # To ensure triggering
        self.comm_query(f"LocalMemInfo {rdacset.Type}", wait_in_sec = wait_in_sec)

        cprint(f"Data Sent. {rdacset.name} DAC active (DAC {DAC_number}, Tile {DAC_tile})",'g')
        return data
    
    def DAC_BRAM_dataupload(self, wave_data, DAC_number=0, DAC_tile=1, wait_in_sec = 0.0):
        
        LMTstring = self.DACADC_LMTString(DAC_number, DAC_tile)
        
        rdacset = SimpleNamespace(**self.sys_config[f'DAC_TILE_{DAC_tile}'][f'DAC_{DAC_number}'])
        clksel = 0

        data = wave_data # np.array([wvf_I, wvf_Q]).flatten('F')

        # MSB_LSB_data = np.vstack((data >> 8, data - ((data >> 8) << 8)))
        MSB_LSB_data = np.vstack((data - ((data >> 8) << 8), data >> 8))
        
        data = MSB_LSB_data.flatten("F").astype('uint8')

        cprint(f"Sending data to DAC {DAC_number}, Tile {DAC_tile}. ({rdacset.name})",'b')
        self.comm_query(f"LocalMemInfo {rdacset.Type}", wait_in_sec = wait_in_sec)
        self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {0} {'0x0000'}", wait_in_sec = wait_in_sec)
        self.comm_query(f"SetLocalMemSample {rdacset.Type} {rdacset.Tile} {rdacset.Block} {data.size//2}", wait_in_sec = wait_in_sec)
        time.sleep(0.25)
        self.send_data(f"WriteDataToMemory {rdacset.Tile} {rdacset.Block} {data.size} {1}", data)
        time.sleep(0.1)
        self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {0} {LMTstring}", wait_in_sec = wait_in_sec)
        time.sleep(0.1)
        self.comm_query(f"LocalMemTrigger {rdacset.Type} {clksel} {0} {0xFFFF}", wait_in_sec = wait_in_sec) # To ensure triggering
        self.comm_query(f"LocalMemInfo {rdacset.Type}", wait_in_sec = wait_in_sec)

        cprint(f"Data Sent. {rdacset.name} DAC active (DAC {DAC_number}, Tile {DAC_tile})",'g')
        return data
    
    def ADC_data_capture_DDR(self,ADC_tile,ADC_number,n_samples):
        '''
        n_samples is the (no of ensembles = EnsN X the experiments in sequence = SeqN)
        '''
        clksel=0
        adcset = SimpleNamespace(**self.sys_config[f'ADC_TILE_{ADC_tile}'][f'ADC_{ADC_number}'])
        BytesPerSample = 2
        SamplesPerFrame = 12
        datasize = int(((n_samples * SamplesPerFrame * BytesPerSample)//32)*32) # number of bytes to capture aligned to 16 samples
        # datasize = int(n_samples * SamplesPerFrame * BytesPerSample) # number of bytes to capture aligned to 16 samples
        # Commands to configure DMA
        self.comm_query(f"SetLocalMemSample {adcset.Type} {adcset.Tile} {adcset.Block} {datasize}")
        self.comm_query(f"LocalMemInfo {adcset.Type}")
        self.comm_query(f"LocalMemTrigger {adcset.Type} {clksel} {datasize} {'0x0001'}")
        fcom = (str(f"ReadDataFromMemory {adcset.Tile} {adcset.Block} {datasize} {0}") + '\r\n').encode('ascii')
        self.s_dat.send(fcom)
        cprint('Read DATA INSTRUCTION SENT', fg='r' )
        # Capture Data: create byte object, iterate through the byte object        
        ADC_samples = b'' # empty bytes object
        DeltaData = 1536 # 240 # Restore to 240 or small number if faults are observed 16052023
        k = 1
        # If datasize is smaller than DeltaData then raise value error here
        while k <= (datasize // DeltaData):
            dataHolder = self.s_dat.recv(DeltaData )
            ADC_samples += dataHolder
            k = k + 1            
        cprint('DATA CAPTURED IN BYTES OBJECT', fg='r' )
        
        SigI, SigQ = self.CustomFloatingPointFormat(ADC_samples)
        
        return SigI, SigQ
    
    def ADC_data_capture_PP(board,self,ADC_tile,ADC_number,n_samples,BufferSize = 1920): #Buffer size change 1920 for regular pingpong size and 3840 for twice pinpong size
        '''
        n_samples is the (no of ensembles = EnsN X the experiments in sequence = SeqN)
        Note: 24052023 :-
        PingPong application layer sends data in two packets 
        a) data of 1920 bytes in one send()
        b) \r\n i.e. 2 bytes in the next send()
    
        Here the recv() hence receives 1920 bytes in one iteration and 2 bytes in the next
        The 2 bytes has to be discarded anyway so an if: condition should do
        NumBuff has to be doubled
        '''
        # PingPongResidueBytes = 2 # This is because of '\n\r' appended in application layer 
        BytesPerSample = 2
        SamplesPerFrame = 12 # 6 I and 6 Q samples
        datasize = int(((n_samples * SamplesPerFrame * BytesPerSample)//32)*32) # number of bytes to capture aligned to 32 samples (Not needed for capture via PingPong Buffer)
        NumBuff = (datasize // BufferSize) + 1 # One buffer gets discarded later
        # send command for data capture via ping pong buffers
        fcom = (str(f"PingPong {NumBuff}") + '\r\n').encode('ascii')
        self.s_dat.send(fcom)
        # Capture Data: create byte object, iterate through the byte object        
        ADC_samples = b'' # empty bytes object
        DeltaData = BufferSize # bytes
        k = 1
        # If datasize is smaller than DeltaData then raise value error here
        while k <= (NumBuff*2): # Seems this has been changed in application for bit file D:/Darshit/Darshit_trial_bitfiles/D_200723_1516_V3C_w_PP.bit
        #while k <= (NumBuff*1):
            dataHolder = board.s_dat.recv(DeltaData)
            if len(dataHolder) == DeltaData: # Happens only if data has come via PingPong buffer
                ADC_samples += dataHolder
            # Progress
            if np.mod(k,50) == 0:
                print(f'Progress        {int(np.round(k/(NumBuff*2) * 100,0))} %')
            # Progress
            k = k + 1            
        cprint('DATA CAPTURED IN BYTES OBJECT', fg='r' )       
        # Formatting
        cprint('DATA FORMATTING AND CUSTOMISED DECODING', fg='b')
        # print(ADC_samples)
        SigI, SigQ = self.CustomFloatingPointFormat(ADC_samples)
        
        # return SigI, SigQ
        return SigI, SigQ, ADC_samples
    
    def CustomFloatingPointFormat(self,ADC_samples):
        # Data formatting and customised decoding        
        # Formatting
        ADC_samples1 = ADC_samples
        tempa = np.array(list(ADC_samples1)).reshape(2,len(ADC_samples1)//2, order='F')
        tempa = tempa.astype('uint16')
        tempa[1] = tempa[1] * 256
        tempDataformatted = np.add(tempa[0],tempa[1])
        # Customised decoding
        tempd = tempDataformatted 
        tempd_bin_list = [np.binary_repr(binstr, width = 16) for binstr in tempd]
        EXP = [int(binstr[1:6], 2) for binstr in tempd_bin_list]
        MANT = [int('0' + binstr[4:],2) if EXP[k]>=28 else int('1' + binstr[6:],2)/pow(2,10) for k, binstr in enumerate(tempd_bin_list)]
        EXP = [0 if ((n+12)>=40) else n+12 for n in EXP]
        SIGN = [int(binstr[0], 2) for binstr in tempd_bin_list]   
        SigIQ = [pow(-1,sign)*mant*pow(2,exp) for (sign,exp,mant) in zip(SIGN,EXP,MANT)]
        #% Separate out I and Q
        SigI = SigIQ[::2]
        SigQ = SigIQ[1::2]
        
        return SigI, SigQ
        
    
    def DataIntoChannelsAndEns(self, SigI, SigQ, SeqN, Ch, AlighN):  # Data into Channels and Ensemble
        # Separate data into chuncks of SeqN
        SigI_2D = [SigI[n:n+(Ch*SeqN)] for n in range(0,Ch*(len(SigI)//Ch),Ch*SeqN)]
        SigQ_2D = [SigQ[n:n+(Ch*SeqN)] for n in range(0,Ch*(len(SigQ)//Ch),Ch*SeqN)]
        # Take Ensemble average
        SigI_ens = np.array(SigI_2D[:-1]).sum(axis = 0) # Discard the last inhomogeneous array
        SigQ_ens = np.array(SigQ_2D[:-1]).sum(axis = 0) # Discard the last inhomogeneous array
        # Normalize
        SigI_ens = SigI_ens / (len(SigI_2D) - 1)
        SigQ_ens = SigQ_ens / (len(SigQ_2D) - 1)
        # Separate out the channels
        SigI_ch1 = SigI_ens[AlighN::Ch]
        SigQ_ch1 = SigQ_ens[AlighN::Ch]
        SigI_ch2 = SigI_ens[AlighN+1::Ch]
        SigQ_ch2 = SigQ_ens[AlighN+1::Ch]
        SigI_ch3 = SigI_ens[AlighN+2::Ch]
        SigQ_ch3 = SigQ_ens[AlighN+2::Ch]
        SigI_ch4 = SigI_ens[AlighN+3::Ch]
        SigQ_ch4 = SigQ_ens[AlighN+3::Ch]
        SigI_ch5 = SigI_ens[AlighN+4::Ch]
        SigQ_ch5 = SigQ_ens[AlighN+4::Ch]
        SigI_ch6 = SigI_ens[AlighN+5::Ch]
        SigQ_ch6 = SigQ_ens[AlighN+5::Ch]
        SigI_ch7 = SigI_ens[AlighN+6::Ch]
        SigQ_ch7 = SigQ_ens[AlighN+6::Ch]
        SigI_ch8 = SigI_ens[AlighN+7::Ch]
        SigQ_ch8 = SigQ_ens[AlighN+7::Ch]
        # Place data in a dictionery
        SigEnsCh =    {'ch1': {'I': SigI_ch1,
                            'Q': SigQ_ch1},
                       'ch2': {'I': SigI_ch2,
                            'Q': SigQ_ch2},
                       'ch3': {'I': SigI_ch3,
                            'Q': SigQ_ch3},
                       'ch4': {'I': SigI_ch4,
                            'Q': SigQ_ch4},
                       'ch5': {'I': SigI_ch5,
                            'Q': SigQ_ch5},
                       'ch6': {'I': SigI_ch6,
                            'Q': SigQ_ch6},
                       'ch7': {'I': SigI_ch7,
                            'Q': SigQ_ch7},
                       'ch8': {'I': SigI_ch8,
                            'Q': SigQ_ch8}
                        }
        
        return SigEnsCh
    
    def DataIntoChannelsAndEns_v1(self, SigI, SigQ, SeqN, Ch, AlighN, ADCen2 = False):  # Data into Channels and Ensemble
        # Separate data into chunks of SeqN
        # Note: ADCen2 if True then every alternate set of values holds local bias value
        if ADCen2 == True:
            ScaleFactor = 2 * Ch # ADC enable 2 is activated
        else: 
            ScaleFactor = 1 * Ch # ADC enable 2 is not activated
            
        SigI_2D_full = [SigI[n:n+(ScaleFactor*SeqN)] for n in range(0,ScaleFactor*(len(SigI)//ScaleFactor),ScaleFactor*SeqN)]
        SigQ_2D_full = [SigQ[n:n+(ScaleFactor*SeqN)] for n in range(0,ScaleFactor*(len(SigQ)//ScaleFactor),ScaleFactor*SeqN)]
        # Local Bias Correction
        SigI_2D_temp = [[np.array(SigArr[n:n+Ch])-np.array(SigArr[n+Ch:n+ScaleFactor]) for n in range(0,len(SigArr),ScaleFactor)] for SigArr in SigI_2D_full]
        SigI_2D = [list(np.ravel(SigArr)) for SigArr in SigI_2D_temp]
        SigQ_2D_temp = [[np.array(SigArr[n:n+Ch])-np.array(SigArr[n+Ch:n+ScaleFactor]) for n in range(0,len(SigArr),ScaleFactor)] for SigArr in SigQ_2D_full]
        SigQ_2D = [list(np.ravel(SigArr)) for SigArr in SigQ_2D_temp]
        # Take Ensemble average
        SigI_ens = np.array(SigI_2D[:-1]).sum(axis = 0) # Discard the last inhomogeneous array
        SigQ_ens = np.array(SigQ_2D[:-1]).sum(axis = 0) # Discard the last inhomogeneous array
        # Normalize
        SigI_ens = SigI_ens / (len(SigI_2D) - 1)
        SigQ_ens = SigQ_ens / (len(SigQ_2D) - 1)
        # Separate out the channels
        SigI_ch1 = SigI_ens[AlighN::Ch]
        SigQ_ch1 = SigQ_ens[AlighN::Ch]
        SigI_ch2 = SigI_ens[AlighN+1::Ch]
        SigQ_ch2 = SigQ_ens[AlighN+1::Ch]
        SigI_ch3 = SigI_ens[AlighN+2::Ch]
        SigQ_ch3 = SigQ_ens[AlighN+2::Ch]
        SigI_ch4 = SigI_ens[AlighN+3::Ch]
        SigQ_ch4 = SigQ_ens[AlighN+3::Ch]
        SigI_ch5 = SigI_ens[AlighN+4::Ch]
        SigQ_ch5 = SigQ_ens[AlighN+4::Ch]
        SigI_ch6 = SigI_ens[AlighN+5::Ch]
        SigQ_ch6 = SigQ_ens[AlighN+5::Ch]
        SigI_ch7 = SigI_ens[AlighN+6::Ch]
        SigQ_ch7 = SigQ_ens[AlighN+6::Ch]
        SigI_ch8 = SigI_ens[AlighN+7::Ch]
        SigQ_ch8 = SigQ_ens[AlighN+7::Ch]
        # Place data in a dictionery
        SigEnsCh =    {'ch1': {'I': SigI_ch1,
                            'Q': SigQ_ch1},
                       'ch2': {'I': SigI_ch2,
                            'Q': SigQ_ch2},
                       'ch3': {'I': SigI_ch3,
                            'Q': SigQ_ch3},
                       'ch4': {'I': SigI_ch4,
                            'Q': SigQ_ch4},
                       'ch5': {'I': SigI_ch5,
                            'Q': SigQ_ch5},
                       'ch6': {'I': SigI_ch6,
                            'Q': SigQ_ch6},
                       'ch7': {'I': SigI_ch7,
                            'Q': SigQ_ch7},
                       'ch8': {'I': SigI_ch8,
                            'Q': SigQ_ch8}
                        }
        
        return SigEnsCh
    
    def FidelityTestDataSep(self, SigI, SigQ, SeqN, Ch, roll=0, AlighN=0): # 22062023
        # Separate data into chunks of SeqN (List of lists)
        SigI_2D = [SigI[n:n+(Ch*SeqN)] for n in range(0,Ch*(len(SigI)//Ch),Ch*SeqN)]
        SigQ_2D = [SigQ[n:n+(Ch*SeqN)] for n in range(0,Ch*(len(SigQ)//Ch),Ch*SeqN)]
        # Separate out the channels (Channelwise List of List of arrays)
        SigI_FT = [[np.roll(np.array(SigI_temp[AlighN+k::Ch]),roll) for SigI_temp in SigI_2D] for k in range(Ch)]
        SigQ_FT = [[np.roll(np.array(SigQ_temp[AlighN+k::Ch]),roll) for SigQ_temp in SigQ_2D] for k in range(Ch)]
        # Flatten with the following rule
        # Note: Leave the Last Sequence, Leave Last sample of every sequence
        SigI_FT_flat = [[np.array(SigI_temp)[:-1]  for SigI_temp in SigI_FT[k][:-1]] for k in range(Ch)]
        SigQ_FT_flat = [[np.array(SigQ_temp)[:-1]  for SigQ_temp in SigQ_FT[k][:-1]] for k in range(Ch)]
        # SigI_FT_flat = [[np.array(SigI_temp)[:]  for SigI_temp in SigI_FT[k][:-1]] for k in range(Ch)]
        # SigQ_FT_flat = [[np.array(SigQ_temp)[:]  for SigQ_temp in SigQ_FT[k][:-1]] for k in range(Ch)]
        # 
        SigI_ch1 = np.ndarray.flatten(np.array(SigI_FT_flat[0]))
        SigQ_ch1 = np.ndarray.flatten(np.array(SigQ_FT_flat[0]))
        SigI_ch2 = np.ndarray.flatten(np.array(SigI_FT_flat[1]))
        SigQ_ch2 = np.ndarray.flatten(np.array(SigQ_FT_flat[1]))
        SigI_ch3 = np.ndarray.flatten(np.array(SigI_FT_flat[2]))
        SigQ_ch3 = np.ndarray.flatten(np.array(SigQ_FT_flat[2]))
        SigI_ch4 = np.ndarray.flatten(np.array(SigI_FT_flat[3]))
        SigQ_ch4 = np.ndarray.flatten(np.array(SigQ_FT_flat[3]))
        SigI_ch5 = np.ndarray.flatten(np.array(SigI_FT_flat[4]))
        SigQ_ch5 = np.ndarray.flatten(np.array(SigQ_FT_flat[4]))
        SigI_ch6 = np.ndarray.flatten(np.array(SigI_FT_flat[5]))
        SigQ_ch6 = np.ndarray.flatten(np.array(SigQ_FT_flat[5]))
        SigI_ch7 = np.ndarray.flatten(np.array(SigI_FT_flat[6]))
        SigQ_ch7 = np.ndarray.flatten(np.array(SigQ_FT_flat[6]))
        SigI_ch8 = np.ndarray.flatten(np.array(SigI_FT_flat[7]))
        SigQ_ch8 = np.ndarray.flatten(np.array(SigQ_FT_flat[7]))
        # Place data in a dictionery
        SigFTCh =    {'ch1': {'I': SigI_ch1,
                            'Q': SigQ_ch1},
                       'ch2': {'I': SigI_ch2,
                            'Q': SigQ_ch2},
                       'ch3': {'I': SigI_ch3,
                            'Q': SigQ_ch3},
                       'ch4': {'I': SigI_ch4,
                            'Q': SigQ_ch4},
                       'ch5': {'I': SigI_ch5,
                            'Q': SigQ_ch5},
                       'ch6': {'I': SigI_ch6,
                            'Q': SigQ_ch6},
                       'ch7': {'I': SigI_ch7,
                            'Q': SigQ_ch7},
                       'ch8': {'I': SigI_ch8,
                            'Q': SigQ_ch8}
                        }
        return SigFTCh 
        
    def FidelityTestDataPlot(self, SigFTCh, Ch = 8): # 22062023
        fig, axs = plt.subplots(4,2)
        for ax, ChNo in zip(axs.flat, np.arange(1,Ch+1)):
            SigI_ch, SigQ_ch = SigFTCh[f'ch{ChNo}'].values()
            ax.set_title(f'Qubit {ChNo}')
            # ax.scatter(SigI_ch[::2],SigQ_ch[::2],'.-')
            # ax.scatter(SigI_ch[1::2],SigQ_ch[1::2],'*-')    
            ax.scatter(SigI_ch[::2],SigQ_ch[::2],marker = '.')
            ax.scatter(SigI_ch[1::2],SigQ_ch[1::2],marker = '.')  
        
    def FidelityTestDataPlot_C(self, hn_ma, SigFTCh, lengthN, Ch = 8): # 23062023
        fig, axs = plt.subplots(4,2)
        for ax, ChNo in zip(axs.flat, np.arange(1,Ch+1)):
            SigI_ch, SigQ_ch = SigFTCh[f'ch{ChNo}'].values()
            # -----
            tReal = SigI_ch
            tImag = SigQ_ch
            tSig = tReal + 1j * tImag
            # hn_ma = (1/5)*np.ones(5,)
            mean_tSig = np.mean(tSig)
            movingAvg_tSig = scipy.signal.convolve(tSig, hn_ma, 'same')
            biascorrected_tSig = tSig - movingAvg_tSig + mean_tSig
            # plt.figure()
            # plt.scatter(np.real(biascorrected_tSig[10:-9]), np.imag(biascorrected_tSig[10:-9]), marker = '.')
            SigI_ch = np.real(biascorrected_tSig[lengthN:(-lengthN+1)])
            SigQ_ch = np.imag(biascorrected_tSig[lengthN:(-lengthN+1)])
            # -----
            ax.set_title(f'Qubit {ChNo}') 
            ax.scatter(SigI_ch[::2],SigQ_ch[::2],marker = '.')
            ax.scatter(SigI_ch[1::2],SigQ_ch[1::2],marker = '.')  
        
        
    
    def freqRespFilt(self, F_DAC = 2708.01, DacTile = 1, DacBlk = 1, F_ADC = -741.93, AdcTile = 0, AdcBlk = 1, FreqDevLim = 2.0, FreqJumps = 0.25 , SeqN = 100, EnsN = 2, Ch = 8, AlighN = 2):  
        
        F_centre = F_ADC # -741.93 # -409.38 # -409.38 # -623.66 MHz 
        F_Spots = F_centre + np.arange(-FreqDevLim, FreqDevLim + FreqJumps, FreqJumps) # MHz
        
        # Set the frequencies
        self.sys_config[f'DAC_TILE_{DacTile}'][f'DAC_{DacBlk}']['NCOFreq'] = F_DAC # 2708.01 # 1392.42 # 1342.42
        self.program_DAC(DAC_number = DacBlk, DAC_tile = DacTile)
        
        try:
            self.comm_query(f"LocalMemTrigger {1} {0} {0} {0x000F}")
        except (UnicodeDecodeError):
            pass
        self.comm_query(f"LocalMemTrigger {1} {0} {0} {0x000F}")
        
        
        # Data Collection lists
        FreqDevAndChPower = []
        
        for Iter, freq in enumerate(F_Spots):
            self.sys_config[f'ADC_TILE_{AdcTile}'][f'ADC_{AdcBlk}']['NCOFreq'] = freq
            self.program_ADC(ADC_number = AdcBlk, ADC_tile = AdcTile)
            # To flush out the sockets
            self.break_connection()
            time.sleep(2)
            self.establish_connection()
            time.sleep(1)
            # To flush out the sockets
            SigI, SigQ = self.ADC_data_capture_DDR(ADC_tile = 0, ADC_number = 0, n_samples = SeqN * EnsN)
            #% Separate data into channels and take ensemble average
            # AlighN = 2 #6 DDR #2 PINGPONG # May have to be changed from system to system
            SigEnsCh = self.DataIntoChannelsAndEns(SigI, SigQ, SeqN, Ch, AlighN)
            #% Plots for reference
            # limitsOfY = 4.5e8
            SigI_ch1, SigQ_ch1 = SigEnsCh['ch1'].values()
            # plt.figure()
            # plt.plot(SigI_ch1,'.-')
            # plt.plot(SigQ_ch1,'*-')
            # Measure Channel Power
            Sig_ch1_cplx = SigI_ch1 + 1j * SigQ_ch1
            Sig_ch1_sqnorm = pow(np.linalg.norm(Sig_ch1_cplx),2)
            Sig_ch1_pow = Sig_ch1_sqnorm / len(SigI_ch1)
            # Store Data
            FreqDevAndChPower.append([freq, Sig_ch1_pow])
            cprint(f"------------- Iteration {Iter} of {len(F_Spots)-1}")
            
        freqVect = [FreqDevAndChPower[k][0] for k in np.arange(len(FreqDevAndChPower))]
        ChPowVect = [FreqDevAndChPower[k][1] for k in np.arange(len(FreqDevAndChPower))]
        plt.figure()
        plt.plot(freqVect, 10 * np.log10(ChPowVect / np.max(ChPowVect)))
        plt.show()
        
        return freqVect, (10 * np.log10(ChPowVect / np.max(ChPowVect)))
    
    def freqRespFilt_v1(self, F_DAC = 2708.01, DacTile = 1, DacBlk = 1, F_ADC = -741.93, AdcTile = 0, AdcBlk = 1, FreqDevLim = 2.0, FreqJumps = 0.25 , SeqN = 100, EnsN = 2, Ch = 8, AlighN = 2):  
        # This function is specifically for 8 Ch bit files where data acquisition is via ping pong buffer only
        
        F_centre = F_ADC # -741.93 # -409.38 # -409.38 # -623.66 MHz 
        F_Spots = F_centre + np.arange(-FreqDevLim, FreqDevLim + FreqJumps, FreqJumps) # MHz
        
        # Set the frequencies
        self.sys_config[f'DAC_TILE_{DacTile}'][f'DAC_{DacBlk}']['NCOFreq'] = F_DAC # 2708.01 # 1392.42 # 1342.42
        self.program_DAC(DAC_number = DacBlk, DAC_tile = DacTile)
        
        try:
            self.comm_query(f"LocalMemTrigger {1} {0} {0} {0x000F}")
        except (UnicodeDecodeError):
            pass
        self.comm_query(f"LocalMemTrigger {1} {0} {0} {0x000F}")
        
        
        # Data Collection lists
        FreqDevAndChPower = []
        
        for Iter, freq in enumerate(F_Spots):
            self.sys_config[f'ADC_TILE_{AdcTile}'][f'ADC_{AdcBlk}']['NCOFreq'] = freq
            self.program_ADC(ADC_number = AdcBlk, ADC_tile = AdcTile)
            # To flush out the sockets
            self.break_connection()
            time.sleep(2)
            self.establish_connection()
            time.sleep(1)
            # To flush out the sockets
            SigI, SigQ = self.ADC_data_capture_DDR(ADC_tile = 0, ADC_number = 0, n_samples = SeqN * EnsN)
            #% Separate data into channels and take ensemble average
            # AlighN = 2 #6 DDR #2 PINGPONG # May have to be changed from system to system
            SigEnsCh = self.DataIntoChannelsAndEns(SigI, SigQ, SeqN, Ch, AlighN)
            #% Plots for reference
            # limitsOfY = 4.5e8
            SigI_ch1, SigQ_ch1 = SigEnsCh['ch1'].values()
            # plt.figure()
            # plt.plot(SigI_ch1,'.-')
            # plt.plot(SigQ_ch1,'*-')
            # Measure Channel Power
            Sig_ch1_cplx = SigI_ch1 + 1j * SigQ_ch1
            Sig_ch1_sqnorm = pow(np.linalg.norm(Sig_ch1_cplx),2)
            Sig_ch1_pow = Sig_ch1_sqnorm / len(SigI_ch1)
            # Store Data
            FreqDevAndChPower.append([freq, Sig_ch1_pow])
            cprint(f"------------- Iteration {Iter} of {len(F_Spots)-1}")
            
        freqVect = [FreqDevAndChPower[k][0] for k in np.arange(len(FreqDevAndChPower))]
        ChPowVect = [FreqDevAndChPower[k][1] for k in np.arange(len(FreqDevAndChPower))]
        plt.figure()
        plt.plot(freqVect, 10 * np.log10(ChPowVect / np.max(ChPowVect)))
        plt.show()
        
        return freqVect, (10 * np.log10(ChPowVect / np.max(ChPowVect)))
        
    def FreqInZoneOne(self, Rx_Freq, AdcTile = 0): # Same as FreqAmbiguity in MATLAB
        # freqADC = self.sys_config[f'ADC_TILE_{AdcTile}'][f'sample_freq'] / 1e6
        freqADC = self.sys_config[f'ADC_TILE_{AdcTile}']['sample_freq'] / 1e6
        freqADCby2 = freqADC * 0.5
        FreqZone = Rx_Freq // freqADCby2
        FreqRemainder = np.mod(Rx_Freq, freqADCby2)
        ADC_NCO_freq = FreqRemainder
        if np.mod(FreqZone,2) != 0:
            ADC_NCO_freq = ADC_NCO_freq - freqADCby2
        
        return np.around(ADC_NCO_freq,6)
    
    def FreqRespRFchannel(self, board, F_start_DAC = 4500.00, F_stop_DAC = 7500.00, F_steps = 100, DacTile = 1, DacBlk = 1,  AdcTile = 0, AdcBlk = 1, SeqN = 100, EnsN = 2, Ch = 8, AlighN = 2, limitsOfY = 8.0e8): 
        
        F_Spots_DAC_Zone1 =  (self.sys_config[f'DAC_TILE_{DacTile}']['sample_freq'] / 1e6 )- np.arange(F_start_DAC, F_stop_DAC, F_steps) # To be actually assigned to DACs
        F_DataPathmode = np.array([3 if freq > 2457.6 else 2 for freq in F_Spots_DAC_Zone1]) # 2457.6 is the forbidden crossover frequency (Also decides DataPathMode)
        F_Spots_DAC =  np.arange(F_start_DAC, F_stop_DAC, F_steps)# MHz
        F_Spots_ADC = np.array([board.FreqInZoneOne(freq) for freq in F_Spots_DAC])
    
        # Data Collection lists
        ChPower = []
    
        for Iter, freq in enumerate(zip(F_Spots_DAC_Zone1, F_Spots_ADC, F_DataPathmode)):
            self.sys_config[f'DAC_TILE_{DacTile}'][f'DAC_{DacBlk}']['NCOFreq'] = freq[0]
            self.sys_config[f'DAC_TILE_{DacTile}'][f'DAC_{DacBlk}']['DataPathMode'] = freq[2]
            self.program_DAC(DAC_number = DacBlk, DAC_tile = DacTile)
            self.sys_config[f'ADC_TILE_{AdcTile}'][f'ADC_{AdcBlk}']['NCOFreq'] = freq[1]
            self.program_ADC(ADC_number = AdcBlk, ADC_tile = AdcTile)
            # Trigger the DACs
            self.comm_query(f"LocalMemTrigger {1} {0} {0} {0x000F}")
            # # To flush out the sockets
            self.break_connection()
            time.sleep(2)
            self.establish_connection()
            time.sleep(1)
            # # To flush out the sockets
            SigI, SigQ, ADC_samples = self.ADC_data_capture_PP(board,ADC_tile = 0, ADC_number = 0, n_samples = SeqN * EnsN)
            # % Separate data into channels and take ensemble average
            SigEnsCh = self.DataIntoChannelsAndEns(SigI, SigQ, SeqN, Ch, AlighN)
            # % Plots for reference 
            SigI_ch1, SigQ_ch1 = SigEnsCh['ch1'].values()
            # plt.figure()
            # plt.plot(SigI_ch1,'.-')
            # plt.plot(SigQ_ch1,'*-')
            # Measure Channel Power
            Sig_ch1_cplx = SigI_ch1 + 1j * SigQ_ch1
            Sig_ch1_sqnorm = pow(np.linalg.norm(Sig_ch1_cplx),2)
            Sig_ch1_pow = Sig_ch1_sqnorm / len(SigI_ch1)
            # # Store Data
            ChPower.append([Sig_ch1_pow])
            cprint(f"------------- Iteration {Iter} of {len(F_Spots_DAC)-1}")
            
        plt.figure()
        plt.plot(F_Spots_DAC ,10 * np.log10(ChPower / np.max(ChPower)),'*-')
        plt.show()
        
    def FreqRespRFchannel_v1(self, board,waveforms, F_start_DAC = 4500.00, F_stop_DAC = 7500.00, F_steps = 100, DacTile = 1, DacBlk = 1,  AdcTile = 0, AdcBlk = 1, SeqN = 100, EnsN = 2, Ch = 8, AlighN = 0, QDacTile = 0, QDacBlk = 0, limitsOfY = 8.0e8): 
        
        # Save old nco characteristics of DAC ADC Pair to be involved in spectroscopy
        DAC_nco_details = board.sys_config[f'DAC_TILE_{DacTile}'][f'DAC_{DacBlk}']
        ADC_nco_details = board.sys_config[f'ADC_TILE_{AdcTile}'][f'ADC_{AdcBlk}']
        
        # Update the sweep characteristics
        F_Spots_DAC_Zone1 =  (self.sys_config[f'DAC_TILE_{DacTile}']['sample_freq'] / 1e6 )- np.arange(F_start_DAC, F_stop_DAC, F_steps) # To be actually assigned to DACs
        F_DataPathmode = np.array([3 if freq > 2457.6 else 2 for freq in F_Spots_DAC_Zone1]) # 2457.6 is the forbidden crossover frequency (Also decides DataPathMode)
        F_Spots_DAC =  np.arange(F_start_DAC, F_stop_DAC, F_steps)# MHz
        F_Spots_ADC = np.array([board.FreqInZoneOne(freq) for freq in F_Spots_DAC])
        
        # Radio Silence to Qubit 
        # waveforms1 = Rabi_local.MakeRabi(Amp = 1) # 0: Radio Silence # 1: Control Pulses Generated # Modify to give no signal to qubit (ideally qubit must be punched out)
        waveforms1 = waveforms
        # Prepare or process data prepared by qiskit pulses OR inhouse code
        cprint('DATA PREPARATION START: standby', fg = 'r')
        final_data1 = board.process_IQ_waveforms1(waveforms1, 0, 4) #### 2 #### 3
        final_data2 = board.process_IQ_waveforms1(waveforms1, 0, 4) #### 2 #### 3
        cprint('DATA PREPARATION COMPLETE !!!', fg = 'g')
        # Send data and triggers 
        trigger_and_acquire_1(board,SeqN,EnsN,final_data1,final_data2) # Doesnt Acquire only partially prepares triggers. 
    
        # Data Collection lists
        ChPower = []
    
        for Iter, freq in enumerate(zip(F_Spots_DAC_Zone1, F_Spots_ADC, F_DataPathmode)):
            # Set Frequency of DAC ADC pair
            self.sys_config[f'DAC_TILE_{DacTile}'][f'DAC_{DacBlk}']['NCOFreq'] = freq[0]
            self.sys_config[f'DAC_TILE_{DacTile}'][f'DAC_{DacBlk}']['DataPathMode'] = freq[2]
            self.program_DAC(DAC_number = DacBlk, DAC_tile = DacTile, wait_in_sec = 0.0)
            self.sys_config[f'ADC_TILE_{AdcTile}'][f'ADC_{AdcBlk}']['NCOFreq'] = freq[1]
            self.program_ADC(ADC_number = AdcBlk, ADC_tile = AdcTile, wait_in_sec = 0.0)
            # # To flush out the sockets
            self.break_connection()
            time.sleep(0.25)
            self.establish_connection()
            time.sleep(0.25)
            # # To flush out the sockets
            [SigEnsCh,SigI,SigQ] = only_acquire(board,SeqN,EnsN)
            # This will reset address in PingPong Buffers to 0th  
            board.comm_query(f"DAcquisition_en {0}", buffer=4096, wait_in_sec = 0.05)
            # % Plots for reference 
            SigI_ch1, SigQ_ch1 = SigEnsCh[f'ch{Ch}'].values()
            # plt.figure()
            # plt.plot(SigI_ch1,'.-')
            # plt.plot(SigQ_ch1,'*-')
            # Measure Channel Power
            Sig_ch1_cplx = SigI_ch1 + 1j * SigQ_ch1
            Sig_ch1_sqnorm = pow(np.linalg.norm(Sig_ch1_cplx),2)
            Sig_ch1_pow = Sig_ch1_sqnorm / len(SigI_ch1)
            # # Store Data
            ChPower.append([Sig_ch1_pow])
            cprint(f"------------- Iteration {Iter} of {len(F_Spots_DAC)-1}")
            
        plt.figure()
        plt.plot(F_Spots_DAC ,10 * np.log10(ChPower / np.max(ChPower)),'*-')
        plt.show()
        
        # Restore the frequencies and nco characteristics of DAC ADC Pair involved in spectroscopy
        board.sys_config[f'DAC_TILE_{DacTile}'][f'DAC_{DacBlk}'] = DAC_nco_details
        board.sys_config[f'ADC_TILE_{AdcTile}'][f'ADC_{AdcBlk}'] = ADC_nco_details
        
        return F_Spots_DAC, (10 * np.log10(ChPower / np.max(ChPower)))
        
        
    def DACADC_LMTString(self, DACorADCblk = 0, DACorADCtile = 0): # Tell teh DAC or ADC Tile and block and get the string '0x0001' etc
        
        DacNum = hex(int((16**DACorADCtile)*(2**DACorADCblk)))
        LMTstring = '0x' + DacNum[2:].zfill(4)
        
        return LMTstring
            
        

class RFSoC_auxill(ZCU216_RFSoC):

    def __init__(self,addr,userconfig, data_port=8082, com_port = 8081, logging=True, debug=False ) -> None:
        
        super().__init__(addr, data_port, com_port , logging, debug)
        self.user_config = {
                        'q1': {
                            'freq' : 4.7e9,
                            'read' : 7.4e9,
                            'DACTile' : 0
                        },

                        "q2": {
                            'freq' : 4.1e9,
                            'read' : 7.5e9,
                            'DACTile' : 1
                        }
        }

        if userconfig : self.user_config = userconfig
        return
    
    def change_NCO_freq_DAC(self,DAC_NCO,DAC_tile,DAC):

        tile = 'DAC_TILE_'+str(DAC_tile)

        dac = 'DAC_'+str(DAC)

        self.sys_config[tile][dac]['NCOFreq'] = DAC_NCO

        # self.program_DAC(DAC_number=DAC,DAC_tile=DAC_tile)

        # self.update_MTS1(mtsIndDAC = 15, mtsIndADC = 3)   #self,mtsIndDAC,mtsIndADC


        return None
    
    def change_NCO_freq_ADC(self,ADC_NCO,ADC_tile,ADC):

        tile = 'ADC_TILE_'+str(ADC_tile)

        adc = 'ADC_'+str(ADC)


        self.sys_config[tile][adc]['NCOFreq'] = ADC_NCO

        # self.program_ADC(ADC_number=ADC,ADC_tile=ADC_tile)

        # self.update_MTS1(mtsIndDAC = 15, mtsIndADC = 3)   #self,mtsIndDAC,mtsIndADC

        return 1


    def initialize_board_preset(self):

        #Frequency planning
        # self.frequency_planner(self.user_config)

        #update things in sys_config using userconfig

        #

        #set clocks
        # if self.sys_config['RFSoC']['clksource'] == 'int' : clk_file = './matlab/int_source.tcs'
        # elif self.sys_config['RFSoC']['clksource'] == 'ext' : clk_file = './matlab/ext_source.tcs'
        if self.sys_config['RFSoC']['clksource'] == 'int' : clk_file = 'int_source.tcs'
        elif self.sys_config['RFSoC']['clksource'] == 'ext' : clk_file = 'ext_source.tcs'
        self.set_clock(clk_file)
        self.set_clock_dist()

        # #set experiment timings
        self.set_timings(DAC_tile=0)
        self.set_timings(DAC_tile=1)

        # Turn on Readout
        self.program_DAC(DAC_number=0,DAC_tile=1)
        self.program_DAC(DAC_number=2,DAC_tile=1)
        #Turn on control DACs
        self.program_DAC(DAC_number=0,DAC_tile=0)
        self.program_DAC(DAC_number=2,DAC_tile=0)

        # Turn on ADCs
        # self.program_ADC(ADC_number=0,ADC_tile=0)
        # self.program_ADC(ADC_number=2,ADC_tile=0)
        self.program_ADC(ADC_number=1,ADC_tile=0)
        self.program_ADC(ADC_number=3,ADC_tile=0)

        #enable Multi-tilesync
        # self.enable_MTS(which='DAC')
        # self.enable_MTS(which='ADC')

        return

    def process_IQ_waveforms(self, waveforms, DAC_Tile, no_of_ctrl_DACs=4):
        '''
        INPUT:
        waveforms -> dict
                        {
                        0: {I: [[Pulse1],[Pulse2],[Pulse3]...],
                            Q: [[Pulse1],[Pulse2],[Pulse3]...]}

                        1: {I: [[Pulse1],[Pulse2],[Pulse3]...],
                            Q: [[Pulse1],[Pulse2],[Pulse3]...]}
                        }
        '''
        #CHECK : Does parallelization make this much more faster?
        #dim check and normalization check
        for dac in waveforms:
            if len(dac["I"]) != len(dac["Q"]):
                raise ValueError(f"Number of pulses do not match for DAC {dac} in channels I and Q.")
            for pulse_I,pulse_Q in zip(dac["I"],dac["Q"]):
                if len(pulse_I) != len(pulse_Q):
                    raise ValueError(f"Pulse sizes do not match for I and Q channels of DAC {dac}.")
                
                if (np.any(np.abs(pulse_I) > 1) or np.any(np.abs(pulse_Q) > 1) ):
                    raise ValueError(f"Pulses not normalised for DAC {dac}.")
                
        # pad with zeros according to tile sampling freq
        # DDR_freq = self.sys_config[f"DAC_TILE_{DAC_Tile}"]['sample_freq'] / (self.sys_config['RFSoC']['IF_interp']*2*4*2) # denominator -> interpolation factor x 2 IQ channels * 4 DACS * 2 mysterious
        DDR_freq = self.sys_config[f"DAC_TILE_{DAC_Tile}"]['sample_freq'] / (self.sys_config['RFSoC']['IF_interp']*2*4*1) # denominator -> interpolation factor x 2 IQ channels * 4 DACS * 2 mysterious
        ctrl_time = self.sys_config["RFSoC"]["experiment_timings"]["control_period"]
        ctrl_pts = int(ctrl_time*DDR_freq)
        for dac in waveforms:
            for pulse_I,pulse_Q in zip(dac["I"],dac["Q"]):
                pulse_I = ([0]*(ctrl_pts-len(pulse_I))).append(pulse_I)
                pulse_Q = ([0]*(ctrl_pts-len(pulse_Q))).append(pulse_Q)


        #scrambling
        descr_ind = 25
        for dac in waveforms:
            scr_pulse_I = [0 for i in dac["I"]]
            scr_pulse_Q = [0 for i in dac["Q"]]

            for i in range(len(dac["I"])):
                scr_pulse_I[(descr_ind*i)%len(dac["I"])] = dac["I"][i]
                scr_pulse_Q[(descr_ind*i)%len(dac["I"])] = dac["Q"][i]

            dac["I"] = scr_pulse_I
            dac["Q"] = scr_pulse_Q


        #add zeros for the DACs not present 
        dacs_in_input =  waveforms.keys
        ref_dac = waveforms[waveforms.keys[0]]
        for i in range(no_of_ctrl_DACs):
            if i in dacs_in_input : continue
            waveforms[i]["I"] =  [ [0]*len(j) for j in ref_dac["I"]]
            waveforms[i]["Q"] =  [ [0]*len(j) for j in ref_dac["Q"]]       

        #interleave
        wave_data = np.vstack((waveforms[0]['I'],waveforms[0]['Q']))
        for i in range(1,no_of_ctrl_DACs):
            wave_data = np.vstack((wave_data,waveforms[i]["I"],waveforms[i]["Q"]))
        wave_data = wave_data.flatten('F')


        # convert to int16
        wave_data = (wave_data * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) / 2 + (np.iinfo(np.int16).max + np.iinfo(np.int16).min) / 2).astype('int16')
        
        #convert to MSB LSB little endian
        final_data = [0] * wave_data.size
        for i,j in enumerate(wave_data):
            final_data[i] = np.array([j>>8, j - ((j >> 8) << 8)])  #MSB, LSB
        
        final_data = final_data.flatten("F")

        return final_data
    
    def process_IQ_waveforms1(self, waveforms1, DAC_Tile, no_of_ctrl_DACs=4): # Made at DYSL-QT
        '''
        INPUT: 
        waveforms -> dict
                        {
                        0: {I: ListOfArrays,
                            Q: ListOfArrays}

                        1: {I: ListOfArrays,
                            Q: ListOfArrays}
                        }
        '''
        # Check value errors
        for dac1 in waveforms1:
            # check if number of pulses in both I and Q are same for all channels
            if len(waveforms1[dac1]["I"]) != len(waveforms1[dac1]["Q"]):
                raise ValueError(f"Number of PULSES in I and Q of channel {dac1} are not equal")
            # else:
            #     print("Number of PULSES equal in I and Q")
            # check if number of samples in each pulse in I and Q are equal
            pulse_I1, pulse_Q1 = waveforms1[dac1].values()
            # Loop through each pulse 
            for pulse_arr_I1, pulse_arr_Q1 in zip(pulse_I1, pulse_Q1):
                if len(pulse_arr_I1) != len(pulse_arr_Q1):
                    raise ValueError(f"Number of SAMPLES in I pulse and Q pulse of channel {dac1} are not equal")
                # else:
                    # print("Number of SAMPLES equal in each pulse in I and Q")
            # If all checks have passed then proceed with data filling, interleaving, type casting and arranging
            
        # Prepare the data for rfsoc
        DDR_freq =  self.sys_config[f"DAC_TILE_{DAC_Tile}"]['sample_freq'] / (4 * 2 * 4) # 8847.36e6 / (4 * 2 * 4)# 9830.4e6 / (4 * 2 * 4)# self.sys_config[f"DAC_TILE_{DAC_Tile}"]['sample_freq'] / (self.sys_config['RFSoC']['IF_interp']*2*4*1) # denominator -> interpolation factor x 2 IQ channels * 4 DACS * 2 mysterious
        ctrl_time = self.sys_config["RFSoC"]["experiment_timings"]["control_period"]
        ctrl_pts = int(round(ctrl_time * DDR_freq / 16) * 16) # int(ctrl_time*DDR_freq)
        ListOfPulses = []
        for dac1 in waveforms1:
            pulse_I1, pulse_Q1 = waveforms1[dac1].values()
            pulse_arr_I1_padded = np.empty(0)
            pulse_arr_Q1_padded = np.empty(0)
            for pulse_arr_I1, pulse_arr_Q1 in zip(pulse_I1, pulse_Q1):
                pulse_arr_I1_padded = np.append(np.append(np.array(([0]*(ctrl_pts-len(pulse_arr_I1)))), pulse_arr_I1), pulse_arr_I1_padded)
                pulse_arr_Q1_padded = np.append(np.append(np.array(([0]*(ctrl_pts-len(pulse_arr_Q1)))), pulse_arr_Q1), pulse_arr_Q1_padded)
            ListOfPulses.append(pulse_arr_I1_padded)
            ListOfPulses.append(pulse_arr_Q1_padded)


        wave_data = np.vstack(ListOfPulses)
        # scale to int16 range
        wave_data = (wave_data * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) / 2 + (np.iinfo(np.int16).max + np.iinfo(np.int16).min) / 2).astype('int16')                      
        # interleave
        wave_data = wave_data.flatten("F")
        # assign to final data
        final_data = wave_data
        # plt.plot(final_data)
        # Separate into bytes
        MSB_LSB_data = np.vstack((final_data - ((final_data >> 8) << 8), final_data >> 8)) # RIGHT
        # MSB_LSB_data = np.vstack((final_data >> 8, final_data - ((final_data >> 8) << 8))) # WRONG
        # interleave MSB and LSB  and type cast to uint8
        final_data = MSB_LSB_data.flatten("F").astype('uint8')

        return final_data
    
    def process_four_ch_data(self,answer):

        return

    # def frequency_planner(self): 
    #     #TODO : Decide sample frequencies and N-zone of different DACS <-> qubits
    #     #TODO: set Nyquist Zones automatically

    #     freq_buffer = 600e6


        # return
    

#TODO: CLEAN THIS    

def link_backend_to_RFSoC(backend,board):


    backend.configuration().dt = 32 * 1/board.sys_config['DAC_TILE_0']['sample_freq']

    return None

def set_NCO_numbers(backend,board,qubit_freq,cavity_freq,int_freq):

    Fs = board.sys_config['DAC_TILE_0']['sample_freq']

    print('Currently only for tile 0 DAC 0, Tile 1 DAC 0 and ADC Tile 0 ADC 0')
    board.sys_config['DAC_TILE_0']['DAC_0']['NCOFreq'] = (Fs-qubit_freq)/1e6 + int_freq/1e6

    board.sys_config['DAC_TILE_0']['DAC_0']['NyquistZone'] = 2
    
    board.sys_config['DAC_TILE_1']['DAC_0']['NCOFreq'] = (Fs)/1e6  - cavity_freq/1e6
    
    board.sys_config['ADC_TILE_0']['ADC_0']['NCOFreq'] = board.FreqInZoneOne(cavity_freq/1e6,0)
     
def Board_init(backend,board,MTS=0):

    #%% Update the clock settings
    clk_file = "int_source.tcs"
    # clk_file = "D:/Python Script/rfsoc/LMKnew_245M76_PL_122M88_SYSREF_7M68_trial1.tcs"
    board.set_clock(clk_file, wait_in_sec = 0.0)
    board.set_clock_dist(wait_in_sec = 0.0)
    
    #%% Disable RTS based pwrmode control
    # board.DisableRTS()

    #%% Set control and readout signal timings
    print(f"{control_total_time} {readout_time} {readout_delay} {marker_start} {marker_width}")
    board.sys_config['RFSoC']['clksource'] = clk_source,                #define clock source
    # board.sys_config['RFSoC']['IF_interp'] : 4,
    board.sys_config['RFSoC']['experiment_timings']['control_period'] = control_total_time               # length of control sequences (sec)
    board.sys_config['RFSoC']['experiment_timings']['readout_period'] = readout_time                # length of readout pulse (sec)
    board.sys_config['RFSoC']['experiment_timings']['readout_delay'] = readout_delay                # delay between end of control and readout pulse begin
    board.sys_config['RFSoC']['experiment_timings']['marker_start'] = marker_start                 # Beginning of marker
    board.sys_config['RFSoC']['experiment_timings']['marker_width'] = marker_width                 # width of the marker (sec)
    board.sys_config['RFSoC']['experiment_timings']['relax_time'] = relax_time                    # relaxation time after readout
    board.sys_config['RFSoC']['experiment_timings']['time_of_flight'] = time_of_flight              # time of flight for ADC to begin collectiong data
    board.sys_config['RFSoC']['experiment_timings']['ADC_base_read_timeoffset_1'] = ADC_base_read_timeoffset_1      # 
    board.sys_config['RFSoC']['experiment_timings']['ADC_base_read_timeoffset_2'] = ADC_base_read_timeoffset_2      # 
    board.sys_config['RFSoC']['experiment_timings']['ADC_readout_window'] = ADC_readout_window # 300e-9 # 230e-9, # 5e-9 
    # board.sys_config['RFSoC']['DAC_TILE_0']['sample_freq'] = Fs
    # board.sys_config['RFSoC']['DAC_TILE_2']['sample_freq'] = Fs
    # board.sys_config['RFSoC']['DAC_TILE_2']['sample_freq'] = Fs
    # board.sys_config['RFSoC']['DAC_TILE_2']['sample_freq'] = Fs
    
    # board.set_timings(DAC_tile=0, SlotsPerMS = 25, wait_in_sec = 0.0) # Obsolete henceforth but kept in ths version
    
    tempVar = 25 # = SlotsPerMS
    board.set_timings_v1(DAC_tile=0, DAC_block=0,SlotsPerMS = tempVar, wait_in_sec = 0.0) # Ch 1 (Ch 8)
    board.set_timings_v1(DAC_tile=0, DAC_block=1,SlotsPerMS = tempVar, wait_in_sec = 0.0) # Ch 2 (Ch 7)
    board.set_timings_v1(DAC_tile=0, DAC_block=2,SlotsPerMS = tempVar, wait_in_sec = 0.0) # Ch 3 (Ch 6)
    board.set_timings_v1(DAC_tile=0, DAC_block=3,SlotsPerMS = tempVar, wait_in_sec = 0.0) # Ch 4 (Ch 5)
    board.set_timings_v1(DAC_tile=2, DAC_block=0,SlotsPerMS = tempVar, wait_in_sec = 0.0) # Ch 5 (Ch 4)
    board.set_timings_v1(DAC_tile=2, DAC_block=1,SlotsPerMS = tempVar, wait_in_sec = 0.0) # Ch 6 (Ch 3)
    board.set_timings_v1(DAC_tile=2, DAC_block=2,SlotsPerMS = tempVar, wait_in_sec = 0.0) # Ch 7 (Ch 2)
    board.set_timings_v1(DAC_tile=2, DAC_block=3,SlotsPerMS = tempVar, wait_in_sec = 0.0) # Ch 8 (Ch 1)


    link_backend_to_RFSoC(backend,board)
    # set_NCO_numbers(backend,board,qubit_freq=qubit_freq,cavity_freq=cavity_freq,int_freq=qubit_if) # commented for test on 20062023!!!!!

    if(~MTS):
        
        #%% Update NCO, etc of Control DACs
        board.program_DAC(DAC_number=0,DAC_tile=0,wait_in_sec = 0.0)
        board.program_DAC(DAC_number=1,DAC_tile=0,wait_in_sec = 0.0)
        board.program_DAC(DAC_number=2,DAC_tile=0,wait_in_sec = 0.0)
        board.program_DAC(DAC_number=3,DAC_tile=0,wait_in_sec = 0.0)
        board.program_DAC(DAC_number=0,DAC_tile=2,wait_in_sec = 0.0)
        board.program_DAC(DAC_number=1,DAC_tile=2,wait_in_sec = 0.0)
        board.program_DAC(DAC_number=2,DAC_tile=2,wait_in_sec = 0.0)
        board.program_DAC(DAC_number=3,DAC_tile=2,wait_in_sec = 0.0)
        # board.program_DAC(DAC_number=0,DAC_tile=2)
        # board.program_DAC(DAC_number=2,DAC_tile=2)

        #%% Update NCO, etc of Readout DACs
        board.program_DAC(DAC_number=0,DAC_tile=1,wait_in_sec = 0.0) # This is for NCO Settings only
        board.program_DAC(DAC_number=1,DAC_tile=1,wait_in_sec = 0.0) # This is for NCO Settings only
        board.program_DAC(DAC_number=2,DAC_tile=1,wait_in_sec = 0.0) # This is for NCO Settings only
        board.program_DAC(DAC_number=3,DAC_tile=1,wait_in_sec = 0.0) # This is for NCO Settings only
        board.program_DAC(DAC_number=0,DAC_tile=3,wait_in_sec = 0.0) # This is for NCO Settings only
        board.program_DAC(DAC_number=1,DAC_tile=3,wait_in_sec = 0.0) # This is for NCO Settings only
        board.program_DAC(DAC_number=2,DAC_tile=3,wait_in_sec = 0.0) # This is for NCO Settings only
        board.program_DAC(DAC_number=3,DAC_tile=3,wait_in_sec = 0.0) # This is for NCO Settings only

        #%% Update NCO, etc of ADCs
        board.program_ADC(ADC_number=0,ADC_tile=0,wait_in_sec = 0.0)
        board.program_ADC(ADC_number=1,ADC_tile=0,wait_in_sec = 0.0)
        board.program_ADC(ADC_number=2,ADC_tile=0,wait_in_sec = 0.0)
        board.program_ADC(ADC_number=3,ADC_tile=0,wait_in_sec = 0.0)
        board.program_ADC(ADC_number=0,ADC_tile=1,wait_in_sec = 0.0)
        board.program_ADC(ADC_number=1,ADC_tile=1,wait_in_sec = 0.0)
        board.program_ADC(ADC_number=2,ADC_tile=1,wait_in_sec = 0.0)
        board.program_ADC(ADC_number=3,ADC_tile=1,wait_in_sec = 0.0)      
    
    #%% MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS
    #% MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS

    if(MTS):
        board.enable_MTS1(mtsIndDAC = 15, mtsIndADC = 3, wait_in_sec = 0.0) # This function sets up MTS for chose DACs and ADCs, sets EventSource to be SYSREF and provides enable to update freq and phase at SYSREF signal 

    #% MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS
    #% MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS MTS    

    #%% Enable readout (i.e. send IQ samples for readpulse)

    # for loopk in np.arange(1):
    # print(f'-------------------------- LOOP {loopk} --------------------------------')
    board.DAC_readout_enable(DAC_number=0, DAC_tile=1, wait_in_sec = 0.0)
    board.DAC_readout_enable(DAC_number=1, DAC_tile=1, wait_in_sec = 0.0)
    board.DAC_readout_enable(DAC_number=2, DAC_tile=1, wait_in_sec = 0.0)
    board.DAC_readout_enable(DAC_number=3, DAC_tile=1, wait_in_sec = 0.0)
    board.DAC_readout_enable(DAC_number=0, DAC_tile=3, wait_in_sec = 0.0)
    board.DAC_readout_enable(DAC_number=1, DAC_tile=3, wait_in_sec = 0.0)
    board.DAC_readout_enable(DAC_number=2, DAC_tile=3, wait_in_sec = 0.0)
    board.DAC_readout_enable(DAC_number=3, DAC_tile=3, wait_in_sec = 0.0)

    return None


def trigger_and_acquire(board,SeqN,EnsN):

    # Test Test Test DAcquisition 22052023
    #
    cprint('TRIGGERING THE BOARD', fg='b', bg='w')
    #
    board.comm_query(f"DAcquisition_en {0}")
    # 
    board.comm_query(f"ReadyValid_en {1}") # 24072023 again
    #
    board.comm_query(f"Ready_en {1}")

    board.comm_query(f"LocalMemTrigger {1} {0} {0} {'0x0000'}")

    board.comm_query(f"LocalMemTriggerDDR {1} {0} {0} {'0x0000'}")
    # #
    #board.DAC_control_dataupload(final_data1, 1, False, 0, 0) # Data uploaded but not triggered
    # #
    #board.DAC_control_dataupload(final_data2, 2, False, 0, 2) # Data uploaded but not triggered
    #
    #
    #  time.sleep(1)
    board.comm_query(f"ReadyValid_en {0}") 
    #
    board.comm_query(f"LocalMemTrigger {1} {0} {0} {0x000F}")
    #
    # time.sleep(1)
    #
    board.comm_query(f"LocalMemTriggerDDR {1} {0} {0} {0x0F00}") 
    #
    # time.sleep(1)
    #
    board.comm_query(f"Valid_en {1}")
    #
    # time.sleep(1)
    #

    # To flush out the sockets
    board.break_connection()
    time.sleep(1)
    board.establish_connection()
    # time.sleep(1)
    # To flush out the sockets

    # Test Test Test DAcquisition 22052023
    board.comm_query(f"DAcquisition_en {1}", buffer=4096, wait_in_sec = 0.05)
    
    cprint('DATA ACQUISITION FROM BOARD', fg='b', bg='w')
    # SeqN = 100 
    # EnsN = 1000 # 100 #47  #1024 # 41
    Ch = 8 # 
    
    SigI, SigQ, ADC_samples = board.ADC_data_capture_PP(board,ADC_tile = 0, ADC_number = 0, n_samples = SeqN * EnsN, BufferSize = 1920) #Buffer size change 1920 for regular pingpong size and 3840 for twice pinpong size

    #% Separate data into channels and take ensemble average
    AlighN = 0 #6 DDR #2 PINGPONG # May have to be changed from system to system
    SigEnsCh = board.DataIntoChannelsAndEns(SigI, SigQ, SeqN, Ch, AlighN)


    return [SigEnsCh,SigI,SigQ]

def only_acquire(board,SeqN,EnsN):

    board.comm_query(f"DAcquisition_en {1}", buffer=4096, wait_in_sec = 0.05)
    
    cprint('DATA ACQUISITION FROM BOARD', fg='b', bg='w')
    # SeqN = 100 
    # EnsN = 1000 # 100 #47  #1024 # 41
    Ch = 8 # 
    
    SigI, SigQ, ADC_samples = board.ADC_data_capture_PP(board,ADC_tile = 0, ADC_number = 0, n_samples = SeqN * EnsN, BufferSize = 1920) #Buffer size change 1920 for regular pingpong size and 3840 for twice pinpong size
    print(len(SigI))
    #% Separate data into channels and take ensemble average
    AlighN = 0 #6 DDR #2 PINGPONG # May have to be changed from system to system
    SigEnsCh = board.DataIntoChannelsAndEns(SigI, SigQ, SeqN, Ch, AlighN)

    return [SigEnsCh,SigI,SigQ] 

def trigger_and_acquire_1(board,SeqN,EnsN,final_data1,final_data2):

    # Test Test Test DAcquisition 22052023
    #
    cprint('TRIGGERING THE BOARD', fg='b', bg='w')
    #
    board.comm_query(f"DAcquisition_en {0}")
    # 
    board.comm_query(f"ReadyValid_en {1}") # 24072023 again
    #
    board.comm_query(f"Ready_en {1}")

    # board.comm_query(f"LocalMemTrigger {1} {0} {0} {'0x0000'}")
    #
    # board.comm_query(f"LocalMemTriggerDDR {1} {0} {0} {'0x0000'}")
    # #
    board.DAC_control_dataupload(final_data1, 1, False, 0, 0) # Data uploaded but not triggered
    # #
    board.DAC_control_dataupload(final_data2, 2, False, 0, 2) # Data uploaded but not triggered
    #
    board.comm_query(f"ReadyValid_en {0}") 
    #
    # time.sleep(1)
    #
    board.comm_query(f"LocalMemTrigger {1} {0} {0} {0x000F}")
    #
    # time.sleep(1)
    #
    board.comm_query(f"LocalMemTriggerDDR {1} {0} {0} {0x0F00}") 
    #
    # time.sleep(1)
    #
    board.comm_query(f"Valid_en {1}")
    #
    # time.sleep(1)
    #

    # To flush out the sockets
    board.break_connection()
    time.sleep(1)
    board.establish_connection()
    time.sleep(1)

    # time.sleep(1)
    # To flush out the sockets

    # # Test Test Test DAcquisition 22052023
    # board.comm_query(f"DAcquisition_en {1}", buffer=4096, wait_in_sec = 0.05)
    
    # cprint('DATA ACQUISITION FROM BOARD', fg='b', bg='w')
    # # SeqN = 100 
    # # EnsN = 1000 # 100 #47  #1024 # 41
    # Ch = 8 # 
    
    # SigI, SigQ, ADC_samples = board.ADC_data_capture_PP(board,ADC_tile = 0, ADC_number = 0, n_samples = SeqN * EnsN, BufferSize = 1920)

    # #% Separate data into channels and take ensemble average
    # AlighN = 0 #6 DDR #2 PINGPONG # May have to be changed from system to system
    # SigEnsCh = board.DataIntoChannelsAndEns(SigI, SigQ, SeqN, Ch, AlighN)


    # return [SigEnsCh,SigI,SigQ]
    return