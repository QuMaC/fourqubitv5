import pyvisa as visa
from Configuration_Files.configuration_4qubitsv3 import *


rm = visa.ResourceManager()

srs = rm.open_resource('TCPIP0::192.168.0.203::inst0::INSTR')

out_stat = srs.query_ascii_values('ENBR?') ## Output check(?) vs 0/1 for off/on

freq = srs.query_ascii_values('FREQ? MHz') ## Obvious

power = srs.query_ascii_values('AMPR?') ## Power check(?) vs setting
