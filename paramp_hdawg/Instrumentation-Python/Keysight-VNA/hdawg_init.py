#### Includes for paramp bias kit for labone


#%%
def ch_op_on(daq,ch,en):
    str1 = '/dev8099/sigouts/'
    str2 = '/on'
    ch1 = ch-1
    str = str1 + f'{ch1}' + str2
    print(str)

    daq.setInt(str,en)



def set_range(daq,ch,range):
    str1 = '/dev8099/sigouts/'
    str2 = '/range'

    ch1 = ch-1
    str = str1 + f'{ch1}' + str2
    print(str)

    daq.setDouble(str,range)



def phaseset(daq,ch,phase):

    str1 = '/dev8099/sines/'
    str2 = '/phaseshift'
    ch1 = ch-1
    str = str1 + f'{ch1}' + str2

    daq.setDouble(str, phase)

def ch_amp_en(daq,ch,en):
    str1 = '/dev8099/sines/'
    str2 = '/enables/'

    ch1 = ch-1

    str = str1 + f'{ch1}' + str2 + f'{(ch1)%2}'
    print(str)
    
    daq.setInt(str,en)

    return 0


def ampset(daq,ch,amp):

    str1 = '/dev8099/sines/'
    str2 = '/amplitudes/'

    ch1 = ch-1

    str = str1 + f'{ch1}' + str2 + f'{(ch1)%2}'
    print(str + f'{amp}')

    daq.setDouble(str,amp)
    
def init_code_paramp(daq):

    for i in range(1,9,1):
        ch_amp_en(daq,i,1)
        set_range(daq,i,5)
        phaseset(daq,i,-90)
        ampset(daq,i,0)
        
def all_ch_on(daq):
    for i in range(1,9,1):
        ch_op_on(daq,i,1)

def all_ch_off(daq):
    for i in range(1,9,1):
        ch_op_on(daq,i,0)


def set_offset(daq,ch,val):
    
    str1 = '/dev8099/sigouts/'
    str2 = '/offset'
    
    ch1 = ch-1
    
    str = str1 + f'{ch1}' + str2
    print(str+f'{val}')
    
    daq.setDouble(str,val)

def set_output(daq, ch, val):
    
    if abs(val) > 3.4:
        if val > 0:
            set_offset(daq, ch, 3.4)
            ampset(daq, ch, val - 3.4)
        else:
            set_offset(daq, ch, -3.4)
            ampset(daq, ch, val + 3.4)
    else:
        set_offset(daq, ch, val)
        ampset(daq, ch, 0)
        
        
    

#%%

# RFSoC commands

def change_current(board,curr,DAC_no,Tile):
    curr = int(curr*1000)
    # DAC_no = 3
    # Tile = 1

    board.comm_query(f"SetDACVOP {Tile} {DAC_no} {curr}",wait_in_sec = wait_in_sec)  

    return 0

#%%

def gen_pulses(fs_IF, N, f_c, f_sep,  Amp1_offset, Amp1, tot_pwr1):

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

def DAC_prog(board, Type, Tile, Block, F_sample, DAC_current, Cavity_freqs, wave_data):
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
