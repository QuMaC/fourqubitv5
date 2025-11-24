import pyvisa as visa

class RhodeandSchwarz_SGS100A():
    def __init__(self, address):
        rm = visa.ResourceManager()
        self.rns = rm.open_resource(address,read_termination='\n',write_termination="\n")
        self.rns.timeout = 100000
        self.rns.write("*RST; *CLS")
        self.rfout_mode = self.rns.query("OUTP:STAT?")

    def output_toggle(self):
        if self.rfout_mode == "0": 
            self.rns.write("OUTP:STAT ON")
            self.rfout_mode = self.rns.query("OUTP:STAT?")
        elif self.rfout_mode == "1":
            self.rns.write("OUTP:STAT OFF")
            self.rfout_mode = self.rns.query("OUTP:STAT?")

    def output_on(self):
        self.rns.write("OUTP:STAT ON")

    def set_power_dB(self,power):
        self.rns.write(f":SOUR:POW:POW {power}")
    
    def set_freq_GHz(self,freq):
        self.rns.write(f":SOUR:FREQ:CW {freq} GHz")

    def set_freq_Hz(self, freq):
        self.rns.write(f":SOUR:FREQ:CW {freq} Hz")

    def check_errors(self):
        print(self.rns.query("SYST:ERR:ALL?"))

    def close_connection(self):
        self.rns.close()

    def set_ref(self,message):
        if message =="INT" : 
            self.rns.write(':SOUR:ROSC:SOUR INT')
        elif message =="EXT" : 
            self.rns.write(':SOUR:ROSC:SOUR EXT')
        else:
            print("Reference can only be 'EXT' or 'INT'")

    def write(self,message):
        self.rns.write(message)

    def query(self,message):
        temp = self.rns.query(message)
        print(temp)
        return temp

class KeysightXSeries():

    def __init__(self, address):
        rm = visa.ResourceManager()
        self.sa = rm.open_resource(address)
        self.sa.timeout = 100000
        self.method = None

    def get_amp(self):
        self.get_single_trigger()
        if self.method == 1:  # Channel power
            sig = self.get_measurement_data()
        elif self.method == 2:  # Marker
            sig = self.query_marker(1)
        else:
            sig = float("NaN")
        return sig

    def set_automatic_video_bandwidth(self, state: int):
        # State should be 1 or 0
        self.sa.write(f"SENS:BAND:VID:AUTO {int(state)}")

    def set_automatic_bandwidth(self, state: int):
        # State should be 1 or 0
        self.sa.write(f"SENS:BAND:AUTO {int(state)}")

    def set_bandwidth(self, bw: int):
        # Sets the bandwidth
        self.sa.write(f"SENS:BAND {int(bw)}")

    def set_sweep_points(self, n_points: int):
        # Sets the number of points for a sweep
        self.sa.write(f"SENS:SWE:POIN {int(n_points)}")

    def set_center_freq(self, freq: int):
        # Sets the central frequency
        self.sa.write(f"SENS:FREQ:CENT {int(freq)}")

    def set_span(self, span: int):
        # Sets the span
        self.sa.write(f"SENS:FREQ:SPAN {int(span)}")

    def set_cont_off(self):
        return self.sa.query("INIT:CONT OFF;*OPC?")

    def set_cont_on(self):
        # Sets continuous mode on
        return self.sa.query("INIT:CONT ON;*OPC?")

    def get_single_trigger(self):
        # Performs a single sweep
        return self.sa.query("INIT:IMM;*OPC?")

    def active_marker(self, marker: int):
        # Active the given marker
        self.sa.write(f"CALC:MARK{int(marker)}:MODE POS")

    def set_marker_freq(self, marker: int, freq: int):
        # Sets the marker's frequency
        self.get_single_trigger()
        self.sa.write(f"CALC:MARK{int(marker)}:X {int(freq)}")

    def query_marker(self, marker: int):
        # Query the marker
        return float(self.sa.query(f"CALC:MARK{int(marker)}:Y?"))

    def get_full_trace(self):
        # Returns the full trace
        ff_SA_Trace_Data = self.sa.query("TRACE:DATA? TRACE1")
        # Data from the Keysight comes out as a string separated by ',':
        # '-1.97854112E+01,-3.97854112E+01,-2.97454112E+01,-4.92543112E+01,-5.17254112E+01,-1.91254112E+01...\n'
        # The code below turns it into an a python list of floats

        # Use split to turn long string to an array of values
        ff_SA_Trace_Data_Array = ff_SA_Trace_Data.split(",")
        amp = [float(i) for i in ff_SA_Trace_Data_Array]
        return amp

    def enable_measurement(self):
        # Sets the measurement to channel power
        self.sa.write(":CONF:CHP")

    def disables_measurement(self):
        # Sets the measurement to none
        self.sa.write(":CONF:CHP NONE")

    def sets_measurement_integration_bw(self, ibw: int):
        # Sets the measurement integration bandwidth
        self.sa.write(f"SENS:CHP:BAND:INT {int(ibw)}")

    def disables_measurement_averaging(self):
        # disables averaging in the measurement
        self.sa.write("SENS:CHP:AVER 0")

    def get_measurement_data(self):
        # Returns the result of the measurement
        # Data from the Keysight comes out as a string separated by ',':
        # '-1.97854112E+01,-3.97854112E+01\n'
        # The code above takes the first value and converts to float.
        return float(self.sa.query("READ:CHP?").split(",")[0])


