from dataclasses import dataclass
import datetime
import json
from typing import Optional

import numpy as np
import pyvisa as visa

from Configuration_Files.config_dictionaries import (
    amp_scale,
    elec_delay_ns,
    iq_imbalance,
    path_global,
    phase_offset_rad,
    pi_12_len_ns,
    pi_len_ns,
    piby2_12_len_ns,
    piby2_len_ns,
    q_IF,
    q_LO,
    ro_amp,
    rr_IF,
    rr_LO,
    single_qubit_experiments_path,
)
from Configuration_Files.configuration_4qubitsv3 import (
    LO_IP_dict,
    adc_mapping,
    cluster_name,
    config,
    dac_mapping,
    integ_len_clk,
    qm_ip,
    ro_len_clk,
    sw_ip,
    switches,
)
from HM.utilities.files_utils import get_save_path, get_timestamp_24h, save_json, timestamp_to_datetime


@dataclass
class QubitCtx:
    q_no: int
    rr_no: int
    q_str: str
    rr_str: str
    fq: float
    fr: float
    q_if: float
    rr_if: float
    q_lo_val_MHz: float
    rr_lo_val_MHz: float
    out: int
    elec_delay_ns: float
    phase_offset_rad: float
    X180_amp: float
    Y180_amp: float
    X90_amp: float
    Y90_amp: float
    ro_amp: float
    pi_len_ns: float
    piby2_len_ns: float
    pi_12_len_ns: float
    piby2_12_len_ns: float
    q_lo_instr: Optional[object] = None
    rr_lo_instr: Optional[object] = None


class BaseExperiment:
    def __init__(self, expt_name: str = None, **kwargs):
        self.LO_IP_dict = LO_IP_dict.copy()
        self.clock_cycle_dur_ns = kwargs.get("clock_cycle_dur_ns", 4)
        self.save_data = kwargs.get("save_data", False)
        self.expt_name = expt_name if expt_name is not None else "Untitled_experiment"
        self.system_params_path = path_global + "/Configuration_Files/System_Parameters"
        self.config_files_path = path_global + "/Configuration_Files"
        self.single_qubit_experiments_path = single_qubit_experiments_path
        self.simulate = kwargs.get("simulate", False)
        self.query_LOs = kwargs.get("query_LOs", True)
        self.paramp = kwargs.get("paramp", False)

        self.config = config
        self.qm_ip = qm_ip
        self.cluster_name = cluster_name
        self.path_to_save = get_save_path(suffix=self.expt_name, timestamp=get_timestamp_24h())

        self.dac_mapping = dac_mapping
        self.adc_mapping = adc_mapping
        self.sw_ip = kwargs.get("sw_ip", sw_ip)
        self.switches = kwargs.get("switches", switches)

    def build_qubit_context(self, q_no: int, rr_no: int = None, query_los: bool = None) -> QubitCtx:
        rr_no = q_no if rr_no is None else rr_no
        query_los = self.query_LOs if query_los is None else query_los

        q_lo_instr = None
        rr_lo_instr = None
        if query_los:
            print("Querying LOs")
            q_lo_val_MHz, q_lo_instr = self.get_q_lo(q_no)
            rr_lo_val_MHz, rr_lo_instr = self.get_rr_lo(rr_no)
        else:
            print("Using LOs from config")
            q_lo_val_MHz = q_LO[f"{q_no}"] * 1e-6
            rr_lo_val_MHz = rr_LO[f"{rr_no}"] * 1e-6

        return QubitCtx(
            q_no=q_no,
            rr_no=rr_no,
            q_str=f"q{q_no}",
            rr_str=f"rr{rr_no}",
            fq=self.get_q_fq(q_no),
            fr=self.get_rr_fr(rr_no),
            q_if=self.get_q_if(q_no),
            rr_if=self.get_rr_if(rr_no),
            q_lo_val_MHz=q_lo_val_MHz,
            rr_lo_val_MHz=rr_lo_val_MHz,
            out=adc_mapping[f"rr{rr_no}"],
            elec_delay_ns=elec_delay_ns.get(str(rr_no), 0.0),
            phase_offset_rad=phase_offset_rad.get(str(rr_no), 0.0),
            X180_amp=amp_scale[f"{q_no}"]["X180"],
            Y180_amp=amp_scale[f"{q_no}"]["Y180"],
            X90_amp=amp_scale[f"{q_no}"]["X90"],
            Y90_amp=amp_scale[f"{q_no}"]["Y90"],
            ro_amp=ro_amp[f"{rr_no}"],
            pi_len_ns=pi_len_ns[f"{q_no}"],
            piby2_len_ns=piby2_len_ns[f"{q_no}"],
            pi_12_len_ns=pi_12_len_ns[f"{q_no}"],
            piby2_12_len_ns=piby2_12_len_ns[f"{q_no}"],
            q_lo_instr=q_lo_instr,
            rr_lo_instr=rr_lo_instr,
        )

    def get_q_fq(self, q_no: int, return_datetime: bool = False):
        with open(self.system_params_path + "/fq_vals.json") as f:
            fq_vals = json.load(f)

        if return_datetime:
            timestamp = fq_vals["timestamp"]
            datetime_obj = timestamp_to_datetime(timestamp)
            return fq_vals["fq_vals"][f"{q_no}"], datetime_obj
        return fq_vals["fq_vals"][f"{q_no}"]

    def save_json(self, data: dict, path: str):
        save_json(data, path)

    def get_rr_fr(self, rr_no: int, return_datetime: bool = False):
        with open(self.system_params_path + "/fr_vals.json") as f:
            fr_vals = json.load(f)
        if return_datetime:
            timestamp = fr_vals["timestamp"]
            datetime_obj = timestamp_to_datetime(timestamp)
            return fr_vals["fr_vals"][f"{rr_no}"], datetime_obj
        return fr_vals["fr_vals"][f"{rr_no}"]

    def get_rr_if(self, rr_no: int):
        self.rr_if_dict = rr_IF.copy()
        self.rr_if_val_in_MHz = self.rr_if_dict[f"{rr_no}"] * 1e-6
        return self.rr_if_dict[f"{rr_no}"]

    def get_q_if(self, q_no: int):
        self.q_if_dict = q_IF.copy()
        self.q_if_val_in_MHz = self.q_if_dict[f"{q_no}"] * 1e-6
        return self.q_if_dict[f"{q_no}"]

    def get_rr_lo(self, rr_no: int):
        rm = visa.ResourceManager()
        rr_lo_instr = rm.open_resource(LO_IP_dict["rr_LO"][f"{((rr_no - 1) // 2) + 1}"])
        rr_lo_val = rr_lo_instr.query_ascii_values("SOUR:FREQ:CW?")[0]
        rr_lo_val_MHz = rr_lo_val * 1e-6
        return rr_lo_val_MHz, rr_lo_instr

    def get_q_lo(self, q_no: int):
        rm = visa.ResourceManager()
        q_lo_instr = rm.open_resource(LO_IP_dict["q_LO"][f"{((q_no - 1) // 2) + 1}"])
        if q_lo_instr.query_ascii_values("OUTP:STAT?")[0] == 0:
            q_lo_instr.write("OUTP:STAT ON")
        q_lo_val = q_lo_instr.query_ascii_values("SOUR:FREQ:CW?")[0]
        q_lo_val_MHz = q_lo_val * 1e-6
        return q_lo_val_MHz, q_lo_instr

    def get_timestamp_str(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SingleQubitExperiment(BaseExperiment):
    def __init__(self, q_no: int, rr_no: int = None, expt_name: str = None, **kwargs):
        super().__init__(expt_name=expt_name, **kwargs)

        self.q_no = q_no if q_no is not None else rr_no
        if self.q_no is None:
            raise ValueError("q_no or rr_no must be provided")
        self.rr_no = self.q_no if rr_no is None else rr_no

        self.qubit = self.build_qubit_context(self.q_no, self.rr_no)

        # Backward-compatible aliases used by existing single-qubit scripts.
        self.rr_str = self.qubit.rr_str
        self.q_str = self.qubit.q_str
        self.elec_delay_ns = self.qubit.elec_delay_ns
        self.phase_offset_rad = self.qubit.phase_offset_rad
        self.fq = self.qubit.fq
        self.fr = self.qubit.fr
        self.rr_if = self.qubit.rr_if
        self.q_if = self.qubit.q_if
        self.q_lo_val_MHz = self.qubit.q_lo_val_MHz
        self.rr_lo_val_MHz = self.qubit.rr_lo_val_MHz
        self.q_lo_instr = self.qubit.q_lo_instr
        self.rr_lo_instr = self.qubit.rr_lo_instr
        self.out = self.qubit.out
        self.X180_amp = self.qubit.X180_amp
        self.Y180_amp = self.qubit.Y180_amp
        self.X90_amp = self.qubit.X90_amp
        self.Y90_amp = self.qubit.Y90_amp
        self.ro_amp = self.qubit.ro_amp
        self.pi_len_ns = self.qubit.pi_len_ns
        self.piby2_len_ns = self.qubit.piby2_len_ns
        self.pi_12_len_ns = self.qubit.pi_12_len_ns
        self.piby2_12_len_ns = self.qubit.piby2_12_len_ns

        self.ro_len = kwargs.get("ro_len", ro_len_clk[str(self.rr_no)])
        _default_integ_len = kwargs.get("integ_len", integ_len_clk[str(self.rr_no)])
        self.integ_len = kwargs.get("integ_len", _default_integ_len)
        self.rep_rate_clk = kwargs.get("rep_rate_clk", 2000)
        self.n_avg = kwargs.get("n_avg", 500 if self.paramp else 2000)

        self.fr_dict = json.load(open(self.system_params_path + "/fr_vals.json", "r"))
        self.rr_if_dict = rr_IF.copy()
        self.q_if_dict = q_IF.copy()
        self.rr_lo_dict = rr_LO.copy()
        self.q_lo_dict = q_LO.copy()
        self.iq_imbalance_dict = iq_imbalance.copy()
        self.quadrature_rotation_method = str(kwargs.get("quadrature_rotation_method", "pca")).lower()
        self.quadrature_rotation_k = int(kwargs.get("quadrature_rotation_k", 8))


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

