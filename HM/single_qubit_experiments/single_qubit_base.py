from Configuration_Files.config_dictionaries import q_IF, q_LO, rr_IF, rr_LO, path_global, elec_delay_ns, phase_offset_rad
from Configuration_Files.configuration_4qubitsv3 import LO_IP_dict, adc_mapping, ro_len_clk, integ_len_clk
import datetime
from HM.utilities.files_utils import timestamp_to_datetime, get_save_path, get_timestamp_24h
import pyvisa as visa
import json
from Configuration_Files.configuration_4qubitsv3 import config, qm_ip, cluster_name

class SingleQubitExperiment:
    def __init__(self, q_no: int, rr_no: int = None, expt_name: str = None, **kwargs):
        self.LO_IP_dict = LO_IP_dict.copy()
        self.clock_cycle_dur_ns = kwargs.get("clock_cycle_dur_ns", 4)
        self.save_data = kwargs.get("save_data", False)
        self.expt_name = expt_name if expt_name is not None else "Untitled_experiment"
        self.system_params_path = path_global + '/Configuration_Files/System_Parameters'
        self.conig_files_path = path_global + '/Configuration_Files'
        self.simulate = kwargs.get("simulate", False)
        self.query_LOs = kwargs.get("query_LOs", True)
        self.paramp = kwargs.get("paramp", False)
        self.q_no = q_no if q_no is not None else rr_no
        self.rr_no = rr_no if rr_no is not None else q_no
        self.rr_str = f"rr{rr_no}"
        self.q_str = f"q{q_no}"
        self.elec_delay_ns = elec_delay_ns.get(str(rr_no), 0.0)
        self.phase_offset_rad = phase_offset_rad.get(str(rr_no), 0.0)
        self.config = config
        self.qm_ip = qm_ip
        self.cluster_name = cluster_name
        self.fq = self.get_q_fq(q_no)
        self.fr = self.get_rr_fr(rr_no)
        self.rr_if = self.get_rr_if(rr_no)
        self.q_if = self.get_q_if(q_no)
        self.path_to_save = get_save_path(suffix=self.expt_name, timestamp=get_timestamp_24h())
        ## basic config dicts
        self.fr_dict = json.load(open(self.system_params_path + '/fr_vals.json', 'r'))
        self.rr_if_dict = rr_IF.copy()
        self.q_if_dict = q_IF.copy()
        self.rr_lo_dict = rr_LO.copy()
        self.q_lo_dict = q_LO.copy()
        if self.query_LOs:
            print("Querying LOs")
            self.q_lo = self.get_q_lo(q_no)
            self.rr_lo = self.get_rr_lo(rr_no)
        else:
            print("Using LOs from config")
            self.q_lo = q_LO[f"{q_no}"]*1e-6 # Convert to MHz
            self.rr_lo = rr_LO[f"{rr_no}"]*1e-6 # Convert to MHz
        self.out = adc_mapping[self.rr_str]
        #### This pulse is just to find the resonator freq, we don't need to optimize for the best readout (Yet)
        ### KWARGS ###
        self.ro_len = kwargs.get("ro_len", ro_len_clk[str(rr_no)])
        _default_integ_len = kwargs.get("integ_len", integ_len_clk[str(rr_no)])
        self.integ_len = kwargs.get("integ_len", _default_integ_len)
        self.rep_rate_clk = kwargs.get("rep_rate_clk", 2000)

        if self.paramp:
            self.n_avg = kwargs.get("n_avg", 500)
        else:
            self.n_avg = kwargs.get("n_avg", 2000)

        


    def get_q_fq(self, q_no: int, return_datetime: bool = False):
        with open(self.system_params_path + '/fq_vals.json') as f:
            fq_vals = json.load(f)

        if return_datetime:
            timestamp = fq_vals["timestamp"]
            datetime_obj = timestamp_to_datetime(timestamp)
            return fq_vals[f"fq_vals"][f"{q_no}"], datetime_obj
        else:
            return fq_vals[f"fq_vals"][f"{q_no}"]

    def get_rr_fr(self, rr_no: int, return_datetime: bool = False):
        with open(self.system_params_path + '/fr_vals.json') as f:
            fr_vals = json.load(f)
        if return_datetime:
            timestamp = fr_vals["timestamp"]
            datetime_obj = timestamp_to_datetime(timestamp)
            return fr_vals[f"fr_vals"][f"{rr_no}"], datetime_obj
        else:
            return fr_vals[f"fr_vals"][f"{rr_no}"]
    
    def get_rr_if(self, rr_no: int):
        self.rr_if_dict = rr_IF.copy()
        return self.rr_if_dict[f"{rr_no}"]
    def get_q_if(self, q_no: int):
        self.q_if_dict = q_IF.copy()
        return self.q_if_dict[f"{q_no}"]

    def get_rr_lo(self, rr_no: int):
        rm = visa.ResourceManager()
        rr_lo = rm.open_resource(LO_IP_dict[f'rr_LO'][f'{((rr_no-1) // 2)+1}'])
        rr_lo_val = rr_lo.query_ascii_values('SOUR:FREQ:CW?')[0]
        rr_lo_val_MHz = rr_lo_val*1e-6 # Convert Hz to MHz
        return rr_lo_val_MHz

    def get_q_lo(self, q_no: int):
        rm = visa.ResourceManager()
        q_lo = rm.open_resource(LO_IP_dict[f'q_LO'][f'{((q_no-1) // 2)+1}'])
        #if lo is off turn it on 
        if q_lo.query_ascii_values('OUTP:STAT?')[0] == 0:
            q_lo.write('OUTP:STAT ON')
        q_lo_val = q_lo.query_ascii_values('SOUR:FREQ:CW?')[0]
        q_lo_val_MHz = q_lo_val*1e-6 # Convert Hz to MHz
        return q_lo_val_MHz

    def get_timestamp_str(self):
        """"
        get timestamp in  "%Y-%m-%d %H:%M:%S"
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")