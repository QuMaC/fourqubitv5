from dataclasses import dataclass
import datetime
import json
import logging
from typing import Optional

import numpy as np
import pyvisa as visa
import warnings
from termcolor import cprint

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
    paramp_status_dict,
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

logger = logging.getLogger(__name__)


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
    paramp: bool = False


class BaseExperiment:
    def __init__(self, expt_name: str = None, **kwargs):
        self.save_extension = kwargs.get("save_extension", ["png"])
        self.LO_IP_dict = LO_IP_dict.copy()
        self.clock_cycle_dur_ns = kwargs.get("clock_cycle_dur_ns", 4)
        self.save_data = kwargs.get("save_data", False)
        self.expt_name = expt_name if expt_name is not None else "Untitled_experiment"
        self.system_params_path = path_global + "/Configuration_Files/System_Parameters"
        self.config_files_path = path_global + "/Configuration_Files"
        self.rabi_scaling_path = self.config_files_path + "/Pulse_Calibrations/rabi_scaling.json"
        self.single_qubit_experiments_path = single_qubit_experiments_path
        self.simulate = kwargs.get("simulate", False)
        self.query_LOs = kwargs.get("query_LOs", True)
        self.query_paramp = kwargs.get("query_paramp", False)
        self.apply_rabi_scaling = bool(kwargs.get("apply_rabi_scaling", True))

        self.refresh_qm_config = bool(kwargs.get("refresh_qm_config", True))
        self.config = config
        self.qm_ip = qm_ip
        self.cluster_name = cluster_name
        self.path_to_save = get_save_path(suffix=self.expt_name, timestamp=get_timestamp_24h())

        self.dac_mapping = dac_mapping
        self.adc_mapping = adc_mapping
        self.sw_ip = kwargs.get("sw_ip", sw_ip)
        self.switches = kwargs.get("switches", switches)

        self.fr_dict = json.load(open(self.system_params_path + "/fr_vals.json", "r"))
        self.rr_if_dict = rr_IF.copy()
        self.q_if_dict = q_IF.copy()
        self.rr_lo_dict = rr_LO.copy()
        self.q_lo_dict = q_LO.copy()
        self.iq_imbalance_dict = iq_imbalance.copy()
        self.quadrature_rotation_method = str(kwargs.get("quadrature_rotation_method", "pca")).lower()
        self.quadrature_rotation_k = int(kwargs.get("quadrature_rotation_k", 8))
        # Standardized figure registry for all experiments.
        self.figures = {}
        self._saved_lo_states = {"q_LO": {}, "rr_LO": {}}

    def register_figure(self, title: str, figure_obj):
        """Store a matplotlib figure object under a stable title."""
        if title is None:
            title = "untitled_figure"
        self.figures[str(title)] = figure_obj

    def register_figures(self, figure_map: dict):
        """Bulk-register figures from a title -> figure mapping."""
        if not isinstance(figure_map, dict):
            return
        for title, figure_obj in figure_map.items():
            self.register_figure(title, figure_obj)

    def refresh_qm_config_from_disk(self):
        """Rebuild ``self.config`` from disk-backed JSON (see ``qm_config_reload``)."""
        from Configuration_Files.qm_config_reload import reload_qm_config

        reload_qm_config()
        import Configuration_Files.configuration_4qubitsv3 as _cfg

        self.config = _cfg.config
        self.adc_mapping = _cfg.adc_mapping
        self.dac_mapping = _cfg.dac_mapping

    def turn_off_all_los(self):
        """
        Store current LO frequencies and states, then turn all configured LOs off.
        """
        self._saved_lo_states = {"q_LO": {}, "rr_LO": {}}
        qubit_ip_dict = self.LO_IP_dict.get("q_LO", {})
        resonator_ip_dict = self.LO_IP_dict.get("rr_LO", {})
        logger.info(f"q_LO entries: {list(qubit_ip_dict.keys())}")
        logger.info(f"rr_LO entries: {list(resonator_ip_dict.keys())}")

        rm = visa.ResourceManager()
        try:
            for q_ip in qubit_ip_dict.values():
                q_lo = rm.open_resource(q_ip)
                state_before = q_lo.query_ascii_values("OUTP:STAT?")[0]
                freq = q_lo.query_ascii_values("SOUR:FREQ:CW?")[0]
                self._saved_lo_states["q_LO"][q_ip] = {"state": state_before, "freq": freq}
                q_lo.write("OUTP:STAT OFF")
                state_after = q_lo.query_ascii_values("OUTP:STAT?")[0]
                logger.info(f"q_LO  {q_ip}: {state_before} -> {state_after}  (0=off 1=on)")

            for rr_ip in resonator_ip_dict.values():
                rr_lo = rm.open_resource(rr_ip)
                state_before = rr_lo.query_ascii_values("OUTP:STAT?")[0]
                freq = rr_lo.query_ascii_values("SOUR:FREQ:CW?")[0]
                self._saved_lo_states["rr_LO"][rr_ip] = {"state": state_before, "freq": freq}
                rr_lo.write("OUTP:STAT OFF")
                state_after = rr_lo.query_ascii_values("OUTP:STAT?")[0]
                logger.info(f"rr_LO {rr_ip}: {state_before} -> {state_after}  (0=off 1=on)")
        finally:
            rm.close()

        logger.info("All LOs turned off")

    def restore_saved_los(self):
        """
        Restore LOs to frequencies and states saved by turn_off_all_los().
        """
        saved_states = getattr(self, "_saved_lo_states", None)
        has_saved_q = isinstance(saved_states, dict) and bool(saved_states.get("q_LO", {}))
        has_saved_rr = isinstance(saved_states, dict) and bool(saved_states.get("rr_LO", {}))
        has_any_saved_state = has_saved_q or has_saved_rr

        rm = visa.ResourceManager()
        try:
            if has_any_saved_state:
                for q_ip, cfg in saved_states.get("q_LO", {}).items():
                    q_lo = rm.open_resource(q_ip)
                    q_lo.write(f'SOUR:FREQ:CW {cfg["freq"]}')
                    q_lo.write(f'OUTP:STAT {int(cfg["state"])}')
                for rr_ip, cfg in saved_states.get("rr_LO", {}).items():
                    rr_lo = rm.open_resource(rr_ip)
                    rr_lo.write(f'SOUR:FREQ:CW {cfg["freq"]}')
                    rr_lo.write(f'OUTP:STAT {int(cfg["state"])}')
            else:
                # Fallback: if no saved config exists on self, just ensure all LOs are ON.
                logger.warning("No saved LO state found; defaulting to OUTP:STAT ON for all configured LOs.")
                cprint(
                    "WARNING: No saved LO state found. Defaulting to OUTP:STAT ON for all configured LOs.",
                    "red",
                )
                for q_ip in self.LO_IP_dict.get("q_LO", {}).values():
                    q_lo = rm.open_resource(q_ip)
                    q_lo.write("OUTP:STAT ON")
                for rr_ip in self.LO_IP_dict.get("rr_LO", {}).values():
                    rr_lo = rm.open_resource(rr_ip)
                    rr_lo.write("OUTP:STAT ON")
        finally:
            rm.close()
        if has_any_saved_state:
            logger.info("LOs restored to previous state")
        else:
            logger.info("LOs turned on (fallback mode)")

    @staticmethod
    def to_pm_pi(x: float) -> float:
        """Map angle to [-pi, pi]."""
        return (float(x) + np.pi) % (2 * np.pi) - np.pi

    @staticmethod
    def _mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean squared error between two traces."""
        return float(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2))

    @staticmethod
    def calculate_state_fidelity(counts_ideal, counts_measured, is_probability=False):
        """
        Calculate state fidelity between two count dictionaries or probability dictionaries.
        Note: Both inputs need to be either counts or probabilities.

        Args:
            counts_ideal, counts_measured: Dicts with state strings as keys and counts/probabilities as values
                e.g., {'00': 100, '01': 50, '10': 30, '11': 20} for counts
                e.g., {'00': 0.5, '01': 0.25, '10': 0.15, '11': 0.1} for probabilities
            is_probability: If True, treats input as probabilities (no normalization needed)
                If False, treats input as counts (normalization required)

        Note:
            - If a state is present in one dict but not the other, it's treated as having probability 0
            - This is handled automatically by the .get(state, 0) method

        Returns:
            float: Fidelity value between 0 and 1
        """
        all_states = set(counts_ideal.keys()) | set(counts_measured.keys())

        if is_probability:
            p1 = np.array([counts_ideal.get(state, 0) for state in all_states], dtype=float)
            p2 = np.array([counts_measured.get(state, 0) for state in all_states], dtype=float)
        else:
            total1 = sum(counts_ideal.values())
            total2 = sum(counts_measured.values())
            if total1 == 0 or total2 == 0:
                return 0.0
            p1 = np.array([counts_ideal.get(state, 0) / total1 for state in all_states], dtype=float)
            p2 = np.array([counts_measured.get(state, 0) / total2 for state in all_states], dtype=float)

        fidelity = (np.sum(np.sqrt(p1 * p2))) ** 2
        return float(fidelity)

    def rotate_with_angle(
        self,
        data: np.ndarray,
        angle_rad: float,
        flip: bool = True,
        return_x: bool = False,
    ):
        """
        Rotate complex data by a supplied angle (radians): data * exp(1j*angle).
        If flip=True, enforce positive sign at the largest |real| point.
        """
        iq_complex = np.asarray(data, dtype=np.complex128)
        wrapped_angle = self.to_pm_pi(angle_rad)
        rotated_iq = iq_complex * np.exp(1j * wrapped_angle)

        if flip and rotated_iq.size > 0:
            dominant_real_idx = int(np.argmax(np.abs(rotated_iq.real)))
            if rotated_iq.real[dominant_real_idx] < 0:
                rotated_iq = -rotated_iq
                wrapped_angle = self.to_pm_pi(wrapped_angle + np.pi)

        if return_x:
            return rotated_iq, wrapped_angle
        return rotated_iq

    def rotate(self, data: np.ndarray, flip: bool = True, return_x: bool = False):
        """
        Rotate complex data so the signal lies mostly on real axis.

        This implements the FFT-on-variance method:
        find x that minimizes var(imag(data * exp(1j*x))).
        """
        iq_complex = np.asarray(data, dtype=np.complex128)
        if iq_complex.size < 2:
            if return_x:
                return iq_complex.copy(), 0.0
            return iq_complex.copy()

        # Calculate imag variance in steps of 1 degree.
        angle_steps = 360
        imag_var_by_angle = np.zeros(angle_steps, dtype=float)
        for step_idx in range(angle_steps):
            trial_angle = (2 * np.pi / angle_steps) * step_idx
            trial_rotated = iq_complex * np.exp(1j * trial_angle)
            imag_var_by_angle[step_idx] = np.var(trial_rotated.imag)

        # Variance is cos(2x)-like: use phase at harmonic 2.
        variance_spectrum = np.fft.rfft(imag_var_by_angle) / angle_steps
        candidate_a = -np.angle(variance_spectrum[2])
        candidate_a = (candidate_a - np.pi) / 2
        candidate_b = candidate_a + np.pi

        candidate_a = self.to_pm_pi(candidate_a)
        candidate_b = self.to_pm_pi(candidate_b)
        best_angle = candidate_a if np.abs(candidate_a) < np.abs(candidate_b) else candidate_b

        return self.rotate_with_angle(iq_complex, best_angle, flip=flip, return_x=return_x)

    def build_qubit_context(self, q_no: int, rr_no: int = None, query_los: bool = None) -> QubitCtx:
        rr_no = q_no if rr_no is None else rr_no
        query_los = self.query_LOs if query_los is None else query_los
        query_paramp = self.query_paramp 
        if query_paramp:
            paramp_status = self.query_paramp_status(rr_no)
        else:
            paramp_status = paramp_status_dict[f"{rr_no}"]


        q_lo_instr = None
        rr_lo_instr = None
        q_lo_val_MHz_cfg = q_LO[f"{q_no}"] * 1e-6
        rr_lo_val_MHz_cfg = rr_LO[f"{rr_no}"] * 1e-6
        if query_los:
            print("Querying LOs")
            try:
                q_lo_val_MHz, q_lo_instr = self.get_q_lo(q_no)
            except Exception as exc:
                warnings.warn(
                    f"Failed to query q_LO for q{q_no} ({exc}). Falling back to config value."
                )
                q_lo_val_MHz, q_lo_instr = q_lo_val_MHz_cfg, None
            try:
                rr_lo_val_MHz, rr_lo_instr = self.get_rr_lo(rr_no)
            except Exception as exc:
                warnings.warn(
                    f"Failed to query rr_LO for rr{rr_no} ({exc}). Falling back to config value."
                )
                rr_lo_val_MHz, rr_lo_instr = rr_lo_val_MHz_cfg, None
        else:
            print("Using LOs from config")
            q_lo_val_MHz = q_lo_val_MHz_cfg
            rr_lo_val_MHz = rr_lo_val_MHz_cfg

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
            paramp=paramp_status,
        )


    

    def query_paramp_status(self, rr_no: int):
        #need to query the paramp status from the RFSoC
        #use the RFSoC API to query the paramp status
        #return the paramp status
        warnings.warn("NEED TO IMPLEMENT LIVE QUERY OF PARAMP STATUS")
        return paramp_status_dict[f"{rr_no}"]

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
        rr_lo_instr = rm.open_resource(self.LO_IP_dict["rr_LO"][f"{((rr_no - 1) // 2) + 1}"])
        rr_lo_val = rr_lo_instr.query_ascii_values("SOUR:FREQ:CW?")[0]
        rr_lo_val_MHz = rr_lo_val * 1e-6
        return rr_lo_val_MHz, rr_lo_instr

    def get_q_lo(self, q_no: int):
        rm = visa.ResourceManager()
        q_lo_instr = rm.open_resource(self.LO_IP_dict["q_LO"][f"{((q_no - 1) // 2) + 1}"])
        if q_lo_instr.query_ascii_values("OUTP:STAT?")[0] == 0:
            q_lo_instr.write("OUTP:STAT ON")
        q_lo_val = q_lo_instr.query_ascii_values("SOUR:FREQ:CW?")[0]
        q_lo_val_MHz = q_lo_val * 1e-6
        return q_lo_val_MHz, q_lo_instr

    def get_timestamp_str(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _processed_quadratures(
        self,
        I: np.ndarray,
        Q: np.ndarray,
        method: str = None,
        k: int = None,
        scale_with_rabi_bounds: bool = True,
        return_angle: bool = False,
    ):
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
                - "var_fft"      : FFT-on-variance rotation (minimize imag variance).
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
            I0 = I - np.mean(I)
            Q0 = Q - np.mean(Q)
            I_s, Q_s = self._scale_quadratures_with_rabi_bounds(I0, Q0, enabled=scale_with_rabi_bounds)
            if return_angle:
                return I_s, Q_s, 0.0
            return I_s, Q_s

        # Center cloud first (robust and consistent across methods).
        I0 = I - np.mean(I)
        Q0 = Q - np.mean(Q)

        if method == "none":
            I_s, Q_s = self._scale_quadratures_with_rabi_bounds(I0, Q0, enabled=scale_with_rabi_bounds)
            if return_angle:
                return I_s, Q_s, 0.0
            return I_s, Q_s

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

        elif method in {"var_fft", "variance_fft", "fft"}:
            z = I0 + 1j * Q0
            z_rot, angle = self.rotate(z, flip=True, return_x=True)
            I_s, Q_s = self._scale_quadratures_with_rabi_bounds(
                z_rot.real, z_rot.imag, enabled=scale_with_rabi_bounds
            )
            if return_angle:
                return I_s, Q_s, float(angle)
            return I_s, Q_s

        else:
            raise ValueError(
                f"Invalid quadrature rotation method '{method}'. "
                f"Use one of: pca, endpoint, median_angle, var_fft, none."
            )

        # Rotate so dominant axis aligns with I.
        c = np.cos(-theta)
        s = np.sin(-theta)
        I_rot = I0 * c - Q0 * s
        Q_rot = I0 * s + Q0 * c
        I_s, Q_s = self._scale_quadratures_with_rabi_bounds(I_rot, Q_rot, enabled=scale_with_rabi_bounds)
        if return_angle:
            return I_s, Q_s, float(self.to_pm_pi(-theta))
        return I_s, Q_s

    def _scale_quadratures_with_rabi_bounds(self, I: np.ndarray, Q: np.ndarray, enabled: bool = True):
        """
        Scale rotated/centered quadratures using fixed per-qubit bounds from Rabi.
        """
        if (not enabled) or (not self.apply_rabi_scaling):
            return I, Q

        q_no = getattr(self, "q_no", None)
        if q_no is None:
            return I, Q

        try:
            with open(self.rabi_scaling_path, "r") as fh:
                payload = json.load(fh)
            bounds = payload.get("rabi_scalings", {}).get(str(q_no))
            if not isinstance(bounds, dict):
                return I, Q

            i_min = float(bounds["I_min"])
            i_max = float(bounds["I_max"])
            q_min = float(bounds["Q_min"])
            q_max = float(bounds["Q_max"])

            i_span = i_max - i_min
            q_span = q_max - q_min
            if np.isclose(i_span, 0.0) or np.isclose(q_span, 0.0):
                warnings.warn(
                    f"Invalid Rabi scaling span for q{q_no}. Returning unscaled quadratures."
                )
                return I, Q

            I_scaled = (I - i_min) / i_span
            Q_scaled = (Q - q_min) / q_span
            return I_scaled, Q_scaled
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            warnings.warn(
                f"Could not apply Rabi scaling bounds for q{q_no}: {exc}. Returning unscaled quadratures."
            )
            return I, Q




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
        self.paramp = self.qubit.paramp
        self.n_avg = kwargs.get("n_avg", 500 if self.paramp else 2000)


        self.ro_len = kwargs.get("ro_len", ro_len_clk[str(self.rr_no)])
        _default_integ_len = kwargs.get("integ_len", integ_len_clk[str(self.rr_no)])
        self.integ_len = kwargs.get("integ_len", _default_integ_len)
        self.rep_rate_clk = kwargs.get("rep_rate_clk", 2000)



    
