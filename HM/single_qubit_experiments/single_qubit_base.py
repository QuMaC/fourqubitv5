from Configuration_Files.config_dictionaries import q_IF, q_LO, rr_IF, rr_LO, path_global, elec_delay_ns, phase_offset_rad, single_qubit_experiments_path, amp_scale, ro_amp, pi_len_ns, piby2_len_ns, pi_12_len_ns, piby2_12_len_ns, iq_imbalance
from Configuration_Files.configuration_4qubitsv3 import switches, sw_ip, LO_IP_dict, adc_mapping, ro_len_clk, integ_len_clk, dac_mapping
import datetime
from HM.utilities.files_utils import timestamp_to_datetime, get_save_path, get_timestamp_24h
import pyvisa as visa
from termcolor import cprint
from HM.utilities.files_utils import save_json
import json
from Configuration_Files.configuration_4qubitsv3 import config, qm_ip, cluster_name
import numpy as np
class SingleQubitExperiment:
    def __init__(self, q_no: int, rr_no: int = None, expt_name: str = None, **kwargs):
        
        self.LO_IP_dict = LO_IP_dict.copy()
        self.clock_cycle_dur_ns = kwargs.get("clock_cycle_dur_ns", 4)
        self.save_data = kwargs.get("save_data", False)
        self.expt_name = expt_name if expt_name is not None else "Untitled_experiment"
        self.system_params_path = path_global + '/Configuration_Files/System_Parameters'
        self.config_files_path = path_global + '/Configuration_Files'
        self.single_qubit_experiments_path = single_qubit_experiments_path
        self.simulate = kwargs.get("simulate", False)
        self.query_LOs = kwargs.get("query_LOs", True)
        self.paramp = kwargs.get("paramp", False)
        self.q_no = q_no if q_no is not None else rr_no
        if self.q_no is None:
            raise ValueError("q_no or rr_no must be provided")
        if rr_no is None:
            self.rr_no = self.q_no
            rr_no = self.q_no
        else:
            self.rr_no = rr_no
        
        self.rr_str = f"rr{rr_no}"
        self.q_str = f"q{q_no}"
        self.elec_delay_ns = elec_delay_ns.get(str(rr_no), 0.0)
        self.phase_offset_rad = phase_offset_rad.get(str(rr_no), 0.0)
        self.config = config
        self.qm_ip = qm_ip
        self.cluster_name = cluster_name
        self.fq = self.get_q_fq(self.q_no)
        self.fr = self.get_rr_fr(self.rr_no)
        self.rr_if = self.get_rr_if(self.rr_no)
        self.q_if = self.get_q_if(self.q_no)
        self.path_to_save = get_save_path(suffix=self.expt_name, timestamp=get_timestamp_24h())
        ## basic config dicts
        self.fr_dict = json.load(open(self.system_params_path + '/fr_vals.json', 'r'))
        self.rr_if_dict = rr_IF.copy()
        self.q_if_dict = q_IF.copy()
        self.rr_lo_dict = rr_LO.copy()
        self.q_lo_dict = q_LO.copy()
        if self.query_LOs:
            print("Querying LOs")
            self.q_lo_val_MHz, self.q_lo_instr = self.get_q_lo(self.q_no)
            self.rr_lo_val_MHz, self.rr_lo_instr = self.get_rr_lo(self.rr_no)
        else:
            print("Using LOs from config")
            self.q_lo_val_MHz = q_LO[f"{self.q_no}"]*1e-6 # Convert to MHz
            self.rr_lo_val_MHz = rr_LO[f"{self.rr_no}"]*1e-6 # Convert to MHz
        self.out = adc_mapping[self.rr_str]
        self.dac_mapping = dac_mapping
        self.adc_mapping = adc_mapping
        #### This pulse is just to find the resonator freq, we don't need to optimize for the best readout (Yet)
        ### KWARGS ###
        self.ro_len = kwargs.get("ro_len", ro_len_clk[str(self.rr_no)])
        _default_integ_len = kwargs.get("integ_len", integ_len_clk[str(self.rr_no)])
        self.integ_len = kwargs.get("integ_len", _default_integ_len)
        self.rep_rate_clk = kwargs.get("rep_rate_clk", 2000)

        if self.paramp:
            self.n_avg = kwargs.get("n_avg", 500)
        else:
            self.n_avg = kwargs.get("n_avg", 2000)

        self.sw_ip = kwargs.get("sw_ip", sw_ip)
        self.switches = kwargs.get("switches", switches)

        self.X180_amp = amp_scale[f'{self.q_no}']['X180']
        self.Y180_amp = amp_scale[f'{self.q_no}']['Y180']
        self.X90_amp = amp_scale[f'{self.q_no}']['X90']
        self.Y90_amp = amp_scale[f'{self.q_no}']['Y90']

        self.ro_amp = ro_amp[f'{self.rr_no}']

        self.pi_len_ns = pi_len_ns[f'{self.q_no}']
        self.piby2_len_ns = piby2_len_ns[f'{self.q_no}']
        self.pi_12_len_ns = pi_12_len_ns[f'{self.q_no}']
        self.piby2_12_len_ns = piby2_12_len_ns[f'{self.q_no}']


        self.iq_imbalance_dict = iq_imbalance.copy()
        self.quadrature_rotation_method = str(kwargs.get("quadrature_rotation_method", "pca")).lower()
        self.quadrature_rotation_k = int(kwargs.get("quadrature_rotation_k", 8))


    def get_q_fq(self, q_no: int, return_datetime: bool = False):
        with open(self.system_params_path + '/fq_vals.json') as f:
            fq_vals = json.load(f)

        if return_datetime:
            timestamp = fq_vals["timestamp"]
            datetime_obj = timestamp_to_datetime(timestamp)
            return fq_vals[f"fq_vals"][f"{q_no}"], datetime_obj
        else:
            return fq_vals[f"fq_vals"][f"{q_no}"]
    

    def save_json(self, data: dict, path: str):
        save_json(data, path)
    
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
        self.rr_if_val_in_MHz = self.rr_if_dict[f"{rr_no}"]*1e-6
        return self.rr_if_dict[f"{rr_no}"]
    def get_q_if(self, q_no: int):
        self.q_if_dict = q_IF.copy()
        self.q_if_val_in_MHz = self.q_if_dict[f"{q_no}"]*1e-6
        return self.q_if_dict[f"{q_no}"]

    def get_rr_lo(self, rr_no: int):
        rm = visa.ResourceManager()
        rr_lo_instr = rm.open_resource(LO_IP_dict[f'rr_LO'][f'{((rr_no-1) // 2)+1}'])
        rr_lo_val = rr_lo_instr.query_ascii_values('SOUR:FREQ:CW?')[0]
        rr_lo_val_MHz = rr_lo_val*1e-6 # Convert Hz to MHz
        return rr_lo_val_MHz, rr_lo_instr

    def get_q_lo(self, q_no: int):
        rm = visa.ResourceManager()
        q_lo_instr = rm.open_resource(LO_IP_dict[f'q_LO'][f'{((q_no-1) // 2)+1}'])
        #if lo is off turn it on 
        if q_lo_instr.query_ascii_values('OUTP:STAT?')[0] == 0:
            q_lo_instr.write('OUTP:STAT ON')
        q_lo_val = q_lo_instr.query_ascii_values('SOUR:FREQ:CW?')[0]
        q_lo_val_MHz = q_lo_val*1e-6 # Convert Hz to MHz
        return q_lo_val_MHz, q_lo_instr

    def get_timestamp_str(self):
        """"
        get timestamp in  "%Y-%m-%d %H:%M:%S"
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def _processed_quadratures(self, I: np.ndarray, Q: np.ndarray, method: str = None, k: int = None):
        """
        Rotate IQ traces onto a dominant analysis quadrature.

        Parameters
        ----------
        I, Q : np.ndarray
            Raw quadrature traces.
        method : str, optional
            Rotation method. One of:
                - "pca"          : principal-axis rotation (default, most robust).
                - "endpoint"     : axis from mean(last-k) - mean(first-k).
                - "median_angle" : legacy median-angle rotation.
                - "none"         : return centered (unrotated) data.
            If None, uses self.quadrature_rotation_method.
        k : int, optional
            Endpoint window size for method="endpoint". If None, uses
            self.quadrature_rotation_k.
        """
        I = np.asarray(I, dtype=float)
        Q = np.asarray(Q, dtype=float)
        method = (self.quadrature_rotation_method if method is None else str(method)).lower()
        k = self.quadrature_rotation_k if k is None else int(k)

        if I.size != Q.size:
            raise ValueError("I and Q must have the same length")
        if I.size < 2:
            return I.copy(), Q.copy()

        if method == "none":
            return I - np.mean(I), Q - np.mean(Q)

        # Center cloud first (robust and consistent across methods).
        I0 = I - np.mean(I)
        Q0 = Q - np.mean(Q)

        if method == "pca":
            xy = np.column_stack([I0, Q0])
            cov = np.cov(xy.T)
            eigvals, eigvecs = np.linalg.eigh(cov)
            axis = eigvecs[:, int(np.argmax(eigvals))]
            theta = np.arctan2(axis[1], axis[0])

        elif method == "endpoint":
            n = I0.size
            k = max(2, min(k, n // 2))
            z = I0 + 1j * Q0
            z_lo = np.mean(z[:k])
            z_hi = np.mean(z[-k:])
            delta = z_hi - z_lo
            if np.abs(delta) < 1e-15:
                theta = 0.0
            else:
                theta = np.angle(delta)

        elif method == "median_angle":
            z = I0 + 1j * Q0
            theta = np.median(np.unwrap(np.angle(z)))

        else:
            raise ValueError(
                f"Invalid quadrature rotation method '{method}'. "
                f"Use one of: pca, endpoint, median_angle, none."
            )

        # Rotate so dominant axis aligns with I.
        c = np.cos(-theta)
        s = np.sin(-theta)
        I_rot = I0 * c - Q0 * s
        Q_rot = I0 * s + Q0 * c
        return I_rot, Q_rot

