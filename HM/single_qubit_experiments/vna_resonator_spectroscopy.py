import sys
import time
import json
import logging
import re
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from termcolor import cprint

from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from HM.utilities.files_utils import save_json
import pyvisa as visa

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_ch)


class VNASpectroscopy(SingleQubitExperiment):
    """
    VNA-based resonator spectroscopy using a Keysight network analyser.

    Workflow
    --------
    1. Connect to VNA.
    2. Auto-estimate and set electrical delay from a broadband phase sweep.
    3. Locate the cavity via unwrapped-phase derivative.
    4. Estimate and apply a phase offset so the resonance is centred at 0°.
    5. Acquire Re(S11) and Im(S11) at low power and fit a Lorentzian.
    6. Optionally acquire at high power (punch-out) and fit again.
    7. Save figures / data and update JSON config files.

    Key kwargs
    ----------
    turn_off_LOs : bool  Turn off LOs on init (default: False)
    vna_ip        : str   VISA resource string (default: "TCPIP0::192.168.0.27::inst0::INSTR")
    low_power     : float Probe power in dBm          (default: -30)
    high_power    : float Punch-out power in dBm       (default: -10)
    do_punchout   : bool  Measure at high power        (default: False)
    search_f_start: float Broadband search start in Hz (default: 7.0e9)
    search_f_stop : float Broadband search stop in Hz  (default: 7.75e9)
    zoom_half_span: float Half-span around cavity in Hz(default: 15e6)
    n_avgs        : int   VNA averaging count           (default: 200)
    if_bw         : float IF bandwidth in Hz            (default: 1e3)
    n_points      : int   Sweep points                  (default: 2001)
    cmd_delay     : float Seconds to wait after each VNA command (default: 4.0)
    update_config : bool  Also update fr/IF/LO JSON files (default: False)
    save_data     : bool  Save raw data to JSON (default: False)
    query_LOs     : bool  Query hardware LOs on init (default: False)
    """

    VNA_IP_DEFAULT = "TCPIP0::192.168.0.27::hislip0::INSTR"
    # VNA_IP_DEFAULT = "TCPIP0::192.168.0.27::inst0::INSTR"

    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        super().__init__(
            q_no=q_no,
            rr_no=rr_no if rr_no is not None else q_no,
            expt_name="vna_res_spec",
            query_LOs=kwargs.pop("query_LOs", False),
            **kwargs,
        )

        # VNA hardware
        self.vna_ip = kwargs.get("vna_ip", self.VNA_IP_DEFAULT)
        self.cmd_delay = float(kwargs.get("cmd_delay", 3.0))
        self.kna = None
        self._rm = None

        # Measurement powers
        self.low_power = float(kwargs.get("low_power", -30))
        self.high_power = float(kwargs.get("high_power", -10))
        self.do_punchout = bool(kwargs.get("do_punchout", False))

        # Frequency scan parameters
        self.search_f_start = float(kwargs.get("search_f_start", 7.0e9))
        self.search_f_stop = float(kwargs.get("search_f_stop", 7.75e9))
        self.zoom_half_span = float(kwargs.get("zoom_half_span", 15e6))

        # VNA sweep settings
        self.n_avgs = int(kwargs.get("n_avgs", 200))
        self.if_bw = float(kwargs.get("if_bw", 1e3))
        self.n_points = int(kwargs.get("n_points", 2001))

        # Whether to update fr / IF / LO config dicts after measurement
        self.turn_off_LOs = bool(kwargs.get("turn_off_LOs", False))
        self.update_config = bool(kwargs.get("update_config", False))
        # Whether to route Mini-Circuits USB switches before measuring
        self.do_switch = bool(kwargs.get("do_switch", True))

        # Data placeholders
        self.f_data: np.ndarray = None
        self.r_data: np.ndarray = None
        self.i_data: np.ndarray = None
        self.r_data_hp: np.ndarray = None
        self.i_data_hp: np.ndarray = None
        self.cavity_hz: float = None

        # Fit results: [(f0_GHz, err), (kint_MHz, err), (kext_MHz, err)]
        self.fit_results = None
        self.fit_q_vals = None      # [(Qint, err), (Qext, err)]
        self.fit_results_hp = None
        self.fit_q_vals_hp = None

    # ------------------------------------------------------------------
    # VNA connection
    # ------------------------------------------------------------------

    def _turn_off_LOs(self):
        """Store current LO frequencies and states, then turn all LOs off."""
        self.qubit_lo_config = {}
        self.resonator_lo_config = {}
        qubit_ip_dict = self.LO_IP_dict['q_LO']
        resonator_ip_dict = self.LO_IP_dict['rr_LO']
        logger.info(f"q_LO entries: {list(qubit_ip_dict.keys())}")
        logger.info(f"rr_LO entries: {list(resonator_ip_dict.keys())}")

        rm = visa.ResourceManager()   # single RM — do NOT close individual resources mid-loop
        try:
            for q_ip in qubit_ip_dict.values():
                q_lo = rm.open_resource(q_ip)
                state_before = q_lo.query_ascii_values('OUTP:STAT?')[0]
                freq = q_lo.query_ascii_values('SOUR:FREQ:CW?')[0]
                self.qubit_lo_config[q_ip] = {'state': state_before, 'freq': freq}
                q_lo.write('OUTP:STAT OFF')
                state_after = q_lo.query_ascii_values('OUTP:STAT?')[0]
                logger.info(f"q_LO  {q_ip}: {state_before} → {state_after}  (0=off 1=on)")

            for rr_ip in resonator_ip_dict.values():
                rr_lo = rm.open_resource(rr_ip)
                state_before = rr_lo.query_ascii_values('OUTP:STAT?')[0]
                freq = rr_lo.query_ascii_values('SOUR:FREQ:CW?')[0]
                self.resonator_lo_config[rr_ip] = {'state': state_before, 'freq': freq}
                rr_lo.write('OUTP:STAT OFF')
                state_after = rr_lo.query_ascii_values('OUTP:STAT?')[0]
                logger.info(f"rr_LO {rr_ip}: {state_before} → {state_after}  (0=off 1=on)")
        finally:
            rm.close()

        logger.info("All LOs turned off")


    def _turn_on_LOs(self):
        """Restore LOs to the frequencies and states saved by _turn_off_LOs."""
        rm = visa.ResourceManager()   # single RM — do NOT close individual resources mid-loop
        try:
            for q_ip, cfg in self.qubit_lo_config.items():
                q_lo = rm.open_resource(q_ip)
                # freq stored in Hz as returned by SOUR:FREQ:CW? — no unit suffix needed
                q_lo.write(f'SOUR:FREQ:CW {cfg["freq"]}')
                q_lo.write(f'OUTP:STAT {int(cfg["state"])}')
            for rr_ip, cfg in self.resonator_lo_config.items():
                rr_lo = rm.open_resource(rr_ip)
                rr_lo.write(f'SOUR:FREQ:CW {cfg["freq"]}')
                rr_lo.write(f'OUTP:STAT {int(cfg["state"])}')
        finally:
            rm.close()
        logger.info("LOs restored to previous state")

    def _switch_to_vna(self):
        """
        Route the Mini-Circuits USB RF switches so the VNA is connected to
        this qubit's readout resonator port.

        Uses the same keyer() + switch_to_vna() logic as the original script.
        Requires the mcl_RF_Switch_Controller_NET45 DLL to be installed.
        If the DLL is not found, logs a warning and skips switching.
        Set do_switch=False to skip entirely.
        """
        try:
            from Helper_Functions.instrument_helperfunctions import switch_to_vna, check_USB_switch_status
            from Helper_Functions.helper_functionsv2 import keyer
            from Configuration_Files.configuration_4qubitsv3 import dac_mapping
        except (ImportError, Exception) as e:
            logger.warning(f"Switch DLL not available — skipping VNA routing. ({e})")
            logger.warning("Set do_switch=False to suppress this warning.")
            return

        switch_key = keyer(f"q{self.q_no}", dac_mapping)
        logger.info(f"Checking USB switch status before routing to q{self.q_no} (key: {switch_key})")
        check_USB_switch_status()
        switch_to_vna(switch_key)
        logger.info(f"VNA routed to q{self.q_no} via switch key '{switch_key}'")

    def connect(self):
        """Open VISA connection to the VNA."""
        if self.kna is None:
            import pyvisa as visa

            def _normalize_tcpip_resource(raw_resource: str) -> list[str]:
                """
                Build candidate VISA resource strings from user input.
                This is intentionally permissive to handle common shorthand
                forms (IP-only, missing board index, mixed hislip/inst0).
                """
                raw = str(raw_resource).strip().strip('"').strip("'")
                if not raw:
                    return [self.VNA_IP_DEFAULT]

                candidates = []
                seen = set()

                def _add(addr: str):
                    key = addr.upper()
                    if key not in seen:
                        seen.add(key)
                        candidates.append(addr)

                # Full resource provided.
                if "::" in raw:
                    upper_raw = raw.upper()
                    if upper_raw.startswith("TCPIP"):
                        _add(raw)
                    elif upper_raw.startswith("HISLIP"):
                        _add(f"TCPIP0::{raw}::INSTR")
                    else:
                        # Looks like HOST::something form without TCPIP prefix.
                        _add(f"TCPIP0::{raw}")
                        if not upper_raw.endswith("::INSTR") and not upper_raw.endswith("::SOCKET"):
                            _add(f"TCPIP0::{raw}::INSTR")
                else:
                    # Host/IP only.
                    host = raw
                    _add(f"TCPIP0::{host}::inst0::INSTR")
                    _add(f"TCPIP0::{host}::hislip0::INSTR")
                    _add(f"TCPIP::{host}::inst0::INSTR")
                    _add(f"TCPIP::{host}::hislip0::INSTR")

                # If host is parseable, add conservative canonical variants.
                host_match = re.match(r"^(?:TCPIP\d*::)?([^:]+)", raw, flags=re.IGNORECASE)
                if host_match:
                    host = host_match.group(1)
                    _add(f"TCPIP0::{host}::inst0::INSTR")
                    _add(f"TCPIP0::{host}::hislip0::INSTR")

                return candidates

            candidates = _normalize_tcpip_resource(self.vna_ip)
            self._rm = visa.ResourceManager()
            last_error = None
            for addr in candidates:
                try:
                    self.kna = self._rm.open_resource(addr)
                    self.vna_ip = addr
                    logger.info(f"Connected to VNA: {addr}")
                    return
                except visa.errors.VisaIOError as exc:
                    last_error = exc
                    logger.warning(f"VNA connect failed for '{addr}' ({exc}); trying next candidate.")

            # No candidate worked; close RM before bubbling error.
            if self._rm is not None:
                self._rm.close()
                self._rm = None
            raise RuntimeError(
                f"Could not open VNA resource from vna_ip='{self.vna_ip}'. "
                f"Tried: {candidates}. Last VISA error: {last_error}"
            ) from last_error

    def disconnect(self):
        """Close VNA connection."""
        if self.kna is not None:
            self.kna.close()
            self.kna = None
        if self._rm is not None:
            self._rm.close()
            self._rm = None

    # ------------------------------------------------------------------
    # Low-level VNA helpers
    # ------------------------------------------------------------------

    def _write(self, cmd: str, post_delay: float = None):
        self.kna.write(cmd)
        time.sleep(post_delay if post_delay is not None else self.cmd_delay)

    def _query_fdat(self, channel: int = 1) -> np.ndarray:
        data = np.array(self.kna.query_ascii_values(
            f"CALC{channel}:MEAS{channel}:DATA:FDAT?"
        ))
        time.sleep(self.cmd_delay)
        return data

    def _query_freq_array(self, channel: int = 1) -> np.ndarray:
        data = np.array(self.kna.query_ascii_values(
            f"CALC{channel}:MEAS{channel}:X:VAL?"
        ))
        time.sleep(self.cmd_delay)
        return data

    def _set_freq_range(self, f_start: float, f_stop: float):
        self._write(f"SENS1:FREQ:START {f_start}")
        self._write(f"SENS1:FREQ:STOP {f_stop}")

    def _autoscale(self):
        self._write("DISP:MEAS:Y:AUTO", post_delay=self.cmd_delay * 0.5)

    def _setup_measurement(self, s_param: str = "S21", meas_format: str = "COMP", channel: int = 1):
        self._write(f":CALC{channel}:MEAS{channel}:PAR {s_param};", post_delay=0.5)
        self._write(f":CALC{channel}:MEAS{channel}:FORM {meas_format};", post_delay=0.5)

    def _setup_averaging(self, channel: int = 1):
        self._write(f":SENS{channel}:BWID {self.if_bw}", post_delay=0.5)
        self._write(f":SENS{channel}:AVER ON", post_delay=0.5)
        self._write(f":SENS{channel}:AVER:COUN {self.n_avgs}", post_delay=0.5)

    # ------------------------------------------------------------------
    # Electrical delay estimation
    # ------------------------------------------------------------------

    def _estimate_electrical_delay(self) -> float:
        """
        Fit a linear phase slope over both halves of a broadband sweep and
        return the estimated electrical delay in nanoseconds.
        """
        self._set_freq_range(self.search_f_start, self.search_f_stop)
        self._write("CALC1:MEAS1:FORM UPH")
        self._autoscale()

        ph_data = self._query_fdat()
        f_data = self._query_freq_array()

        n = len(f_data)
        d1, cov1 = np.polyfit(f_data[: n // 2], ph_data[: n // 2], 1, cov=True)
        d2, cov2 = np.polyfit(f_data[n // 2 :], ph_data[n // 2 :], 1, cov=True)
        slope = d2[0] if cov1[0][0] > cov2[0][0] else d1[0]
        return -slope * 1e9 / 360.0

    # ------------------------------------------------------------------
    # Cavity finding
    # ------------------------------------------------------------------

    def _find_cavity(self, f_start: float, f_stop: float, smooth_win: int = 30) -> float:
        """
        Sweep f_start→f_stop, return the frequency (Hz) corresponding to the
        largest absolute gradient in unwrapped phase.
        """
        self._set_freq_range(f_start, f_stop)
        self._write("CALC1:MEAS1:FORM UPH")
        time.sleep(self.cmd_delay * 2)

        uph = self._query_fdat()
        f_data = self._query_freq_array()

        weights = np.repeat(1.0, smooth_win) / smooth_win
        filt_diff = np.convolve(np.diff(uph), weights, mode="same")
        return float(f_data[int(np.argmax(np.abs(filt_diff)))])

    # ------------------------------------------------------------------
    # Phase offset estimation
    # ------------------------------------------------------------------

    def _estimate_phase_offset(self) -> float:
        """
        With the VNA zoomed in around the cavity, estimate the phase offset
        (degrees) that centres the unwrapped phase response about 0°.
        """
        self._write("CALC:MEAS:OFFS:PHAS 0")
        self._write("CALC1:MEAS1:FORM UPH")
        self._autoscale()
        time.sleep(self.cmd_delay * 3)

        ph_data = self._query_fdat()
        return float((np.max(ph_data) + np.min(ph_data)) * 0.5)

    # ------------------------------------------------------------------
    # Lorentzian fit
    # ------------------------------------------------------------------

    @staticmethod
    def _lorentzian(x, c, gam, a, y0):
        return y0 + (2 * a / np.pi) * gam / (4 * (x - c) ** 2 + gam ** 2)

    def _fit_lorentzian(self, freq: np.ndarray, ydata: np.ndarray):
        """
        Fit a Lorentzian to real-part cavity data.

        Returns
        -------
        meas_vals : list[tuple]
            [(f0_GHz, f0_err_GHz), (kint_MHz, kint_err_MHz), (kext_MHz, kext_err_MHz)]
        q_vals : list[tuple]
            [(Qint, Qint_err), (Qext, Qext_err)]
        res : ndarray
            Raw fit parameters [c, gam, a, y0]
        errs : ndarray
            Parameter standard errors sqrt(diag(cov))
        """
        ymin, ymax = float(np.min(ydata)), float(np.max(ydata))

        # Initial guesses from FWHM
        half_max = 0.5 * (ymax + ymin)
        above = np.where(ydata > half_max)[0]
        BW_g = float(freq[above[-1]] - freq[above[0]])
        wc_g = float(freq[np.argmax(ydata)])
        a_g = 0.5 * np.pi * (ymax - ymin) * BW_g
        y0_g = ymin

        res, cov = curve_fit(self._lorentzian, freq, ydata, p0=[wc_g, BW_g, a_g, y0_g])
        errs = np.sqrt(np.diag(cov))

        f0, bw = float(res[0]), abs(float(res[1]))
        f0_err, bw_err = float(errs[0]), float(errs[1])
        a, y0 = float(res[2]), float(res[3])
        a_err, y0_err = float(errs[2]), float(errs[3])

        # Peak height and coupling asymmetry
        H = 2 * a / (np.pi * bw)
        H_err = H * (a_err / abs(a) + bw_err / bw)
        y_xc = H + y0
        y_xc_err = H_err + y0_err

        # Reflection coefficient r = (y0 - y_xc) / (y0 + y_xc)
        denom_sum = abs(y0 + y_xc) + 1e-30
        denom_diff = abs(-y0 + y_xc) + 1e-30
        r = (y0 - y_xc) / (y0 + y_xc)
        r_err = abs(r) * (y0_err + y_xc_err) * (1.0 / denom_diff + 1.0 / denom_sum)

        kint = bw / (1.0 + r)
        kext = bw * r / (1.0 + r)
        kint_err = kint * (bw_err / bw + r_err / abs(1.0 + r))
        kext_err = bw_err + kint_err

        Qint = f0 / abs(kint)
        Qext = f0 / abs(kext)
        Qint_err = Qint * (f0_err / f0 + kint_err / abs(kint))
        Qext_err = Qext * (f0_err / f0 + kext_err / abs(kext))

        # Convert to GHz / MHz for output
        f0_GHz      = np.round(f0      * 1e-9, 10)
        f0_err_GHz  = np.round(f0_err  * 1e-9, 10)
        kint_MHz    = np.round(kint    * 1e-6, 10)
        kext_MHz    = np.round(kext    * 1e-6, 10)
        kint_err_MHz= np.round(kint_err* 1e-6, 10)
        kext_err_MHz= np.round(kext_err* 1e-6, 10)

        meas_vals = [
            (f0_GHz,   f0_err_GHz),
            (kint_MHz, kint_err_MHz),
            (kext_MHz, kext_err_MHz),
        ]
        q_vals = [(Qint, Qint_err), (Qext, Qext_err)]
        return meas_vals, q_vals, res, errs

    # ------------------------------------------------------------------
    # Core measurement sequence
    # ------------------------------------------------------------------

    def run_experiment(self):
        """
        Full VNA measurement sequence.

        Steps
        -----
        1. Basic VNA setup: averaging, measurement format, output ON.
        2. Estimate and set electrical delay from broadband phase sweep.
        3. Find cavity via phase-derivative peak.
        4. Zoom in, estimate and apply phase offset.
        5. Re-find cavity centre in zoomed view.
        6. Acquire Re(S11) and Im(S11) at low power.
        7. Optionally acquire at high power (punch-out).
        """
        delay = self.cmd_delay

        # --- Basic setup ---
        self._setup_averaging()
        self._setup_measurement()
        self._write("OUTP ON")
        self._write(f"SENS1:SWE:POIN {self.n_points}")
        self._write("CALC:MEAS:MATH:FUNC NORM")
        self._write("SENS:AVER:CLE")
        self._write("CALC1:MEAS1:FORM PHAS")
        self._autoscale()
        self._write(f":SOUR1:POW {self.low_power}")
        self._write("CALC:MEAS:MATH:FUNC NORM", post_delay=delay * 0.5)

        # Reset delay and phase offset
        self._write("CALC1:MEAS1:CORR:EDEL:TIME 0NS")
        self._write("CALC:MEAS:OFFS:PHAS 0")
        self._write("CALC1:MEAS1:FORM UPH")
        self._autoscale()

        # --- Step 1: electrical delay ---
        e_delay_ns = self._estimate_electrical_delay()
        self._write(f"CALC1:MEAS1:CORR:EDEL:TIME {e_delay_ns}NS")
        self._autoscale()
        logger.info(f"Electrical delay: {e_delay_ns:.3f} ns")

        # --- Step 2: find cavity in broad range ---
        cavity_hz = self._find_cavity(self.search_f_start, self.search_f_stop)
        logger.info(f"Cavity found at {cavity_hz * 1e-9:.6f} GHz")

        # --- Step 3: zoom in and set phase offset ---
        fl_low  = cavity_hz - self.zoom_half_span
        fl_high = cavity_hz + self.zoom_half_span
        self._set_freq_range(fl_low, fl_high)
        self._write(f"CALC1:MEAS1:MARK:X {cavity_hz}", post_delay=0)

        ph_offset = self._estimate_phase_offset()
        self._write(f"CALC:MEAS:OFFS:PHAS {ph_offset}")
        logger.info(f"Phase offset: {ph_offset:.2f} deg")

        # --- Step 4: re-find cavity in zoomed view after phase correction ---
        ph_data = self._query_fdat()
        f_zoom  = self._query_freq_array()
        weights = np.repeat(1.0, 30) / 30
        filt_diff = np.convolve(np.diff(ph_data), weights, mode="same")
        cavity_hz = float(f_zoom[int(np.argmax(np.abs(filt_diff)))])
        self._write(f"CALC1:MEAS1:MARK:X {cavity_hz}", post_delay=0)
        self.cavity_hz = cavity_hz

        # --- Step 5: measure Re(S11) ---
        self._write("CALC1:MEAS1:FORM REAL")
        self._autoscale()
        time.sleep(10)  # extra settle time for averaging

        r_data = self._query_fdat()
        f_data = self._query_freq_array()

        # --- Step 6: measure Im(S11) ---
        self._write("CALC1:MEAS1:FORM IMAG")
        self._autoscale()
        i_data = self._query_fdat()

        self.f_data = f_data
        self.r_data = r_data
        self.i_data = i_data

        # --- Optional punch-out ---
        if self.do_punchout:
            self._run_punchout()

        self._write(f":SOUR1:POW {self.low_power}", post_delay=0)
        self._write("OUTP OFF", post_delay=0)


    def _run_punchout(self):
        """Acquire Re(S11) and Im(S11) at high power."""
        self._write(f":SOUR1:POW {self.high_power}")
        self._write("CALC1:MEAS1:FORM REAL")
        self._autoscale()
        time.sleep(10)

        self.r_data_hp = self._query_fdat()

        self._write("CALC1:MEAS1:FORM IMAG")
        self._autoscale()
        self.i_data_hp = self._query_fdat()

    # ------------------------------------------------------------------
    # Analysis and plotting
    # ------------------------------------------------------------------

    def analyze_and_plot(self):
        """
        Fit a Lorentzian to Re(S11) at low power and produce a figure.
        Stores fit results in self.fit_results / self.fit_q_vals.
        """
        meas_vals, q_vals, res, errs = self._fit_lorentzian(self.f_data, self.r_data)

        self.fit_results = meas_vals
        self.fit_q_vals  = q_vals
        self.fit_res_raw = res

        f0_GHz   = float(meas_vals[0][0])
        kint_MHz = float(meas_vals[1][0])
        kext_MHz = float(meas_vals[2][0])
        bw_MHz   = kint_MHz + kext_MHz

        # Store calibrated frequency / IF for update_config_dicts
        # self.rr_lo is in MHz (set by SingleQubitExperiment)
        self.fr_calibrated     = f0_GHz * 1e3                     # GHz → MHz
        self.rr_if_calibrated  = self.fr_calibrated - self.rr_lo_val_MHz  # MHz
        logger.info(
            f"fr = {self.fr_calibrated:.3f} MHz | rr_LO = {self.rr_lo_val_MHz:.3f} MHz | "
            f"rr_IF = {self.rr_if_calibrated:.3f} MHz"
        )
        self._make_figure(
            f_data=self.f_data,
            r_data=self.r_data,
            i_data=self.i_data,
            res=res,
            meas_vals=meas_vals,
            power=self.low_power,
            title_suffix="Low Power",
        )

        logger.info(
            f"f₀ = {f0_GHz:.6f} GHz | BW = {bw_MHz:.3f} MHz | "
            f"κint = {kint_MHz:.3f} MHz | κext = {kext_MHz:.3f} MHz"
        )
        logger.info(f"Qint = {q_vals[0][0]:.0f} | Qext = {q_vals[1][0]:.0f}")

        if self.do_punchout and self.r_data_hp is not None:
            meas_vals_hp, q_vals_hp, res_hp, _ = self._fit_lorentzian(
                self.f_data, self.r_data_hp
            )
            self.fit_results_hp = meas_vals_hp
            self.fit_q_vals_hp  = q_vals_hp
            self._make_figure(
                f_data=self.f_data,
                r_data=self.r_data_hp,
                i_data=self.i_data_hp,
                res=res_hp,
                meas_vals=meas_vals_hp,
                power=self.high_power,
                title_suffix="High Power (Punch-out)",
            )

        return meas_vals, q_vals

    def _make_figure(
        self,
        f_data: np.ndarray,
        r_data: np.ndarray,
        i_data: np.ndarray,
        res: np.ndarray,
        meas_vals: list,
        power: float,
        title_suffix: str = "",
    ):
        """Plot Re(S11), Im(S11), and Lorentzian fit; save to disk."""
        f0_GHz   = float(meas_vals[0][0])
        kint_MHz = float(meas_vals[1][0])
        kext_MHz = float(meas_vals[2][0])
        bw_MHz   = kint_MHz + kext_MHz
        freq_GHz = f_data * 1e-9

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle(
            f"VNA Resonator Spectroscopy — rr{self.rr_no} (q{self.q_no})  {title_suffix}"
        )

        # Real part + fit
        axes[0].plot(freq_GHz, r_data, label="Re(S11)")
        axes[0].axvline(x=f0_GHz, linestyle="--", color="red", label="Resonance")
        axes[0].axvline(x=self.rr_lo_val_MHz*1e-3, linestyle="--", color="blue", label="RR-LO")
        axes[0].plot(
            freq_GHz,
            self._lorentzian(f_data, *res),
            "r-",
            linewidth=1.8,
            label="Lorentzian fit",
        )
        info = (
            f"f\u2080 = {f0_GHz:.6f} GHz\n"
            f"BW = {bw_MHz:.3f} MHz\n"
            f"\u03baint = {kint_MHz:.3f} MHz\n"
            f"\u03baext = {kext_MHz:.3f} MHz\n"
            f"Qint = {self.fit_q_vals[0][0]:.0f}\n"
            f"Qext = {self.fit_q_vals[1][0]:.0f}"
        )
        axes[0].text(
            0.05, 0.95, info,
            transform=axes[0].transAxes, fontsize=9, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )
        axes[0].set_xlabel("Frequency (GHz)")
        axes[0].set_ylabel("Re(S11)")
        axes[0].set_title(f"Real — {power} dBm")
        axes[0].legend(fontsize=8)
        axes[0].grid(True)

        # Imaginary part
        axes[1].plot(freq_GHz, i_data, color="tab:orange", label="Im(S11)")
        axes[1].axvline(x=f0_GHz, linestyle="--", color="red", label="Resonance")
        axes[1].axvline(x=self.rr_lo_val_MHz*1e-3, linestyle="--", color="blue", label="RR-LO")
        axes[1].set_xlabel("Frequency (GHz)")
        axes[1].set_ylabel("Im(S11)")
        axes[1].set_title(f"Imaginary — {power} dBm")
        axes[1].legend(fontsize=8)
        axes[1].grid(True)

        plt.tight_layout()
        save_path = str(self.path_to_save) + f"_rr{self.rr_no}_{power}dBm.png"
        plt.savefig(save_path, bbox_inches="tight")
        cprint(f"Figure saved: {Path(save_path).as_uri()}", "green")
        plt.show(block=False)

    # ------------------------------------------------------------------
    # Config dict updates
    # ------------------------------------------------------------------

    def update_config_dicts(self):
        """
        Update JSON config files with fitted resonator parameters.

        Always updates
        --------------
        external_bandwidth.json  — Kext in MHz
        internal_bandwidth.json  — Kint in MHz

        If update_config=True, also updates
        ------------------------------------
        fr_vals.json  — f₀ in MHz  (consistent with res_spec.py convention)
        rr_IF.json    — IF = f₀ - rr_LO, in MHz
        rr_LO.json    — LO in GHz  (current value; unchanged)
        """
        if self.fit_results is None:
            raise RuntimeError("No fit results — call analyze_and_plot() first.")

        rr_key   = str(self.rr_no)
        sp_path  = self.system_params_path
        kint_MHz = float(self.fit_results[1][0])
        kext_MHz = float(self.fit_results[2][0])
        f0_MHz   = float(self.fr_calibrated)   # already in MHz

        # --- external_bandwidth.json ---
        ext_path = sp_path + "/external_bandwidth.json"
        with open(ext_path, "r") as fh:
            ext_bw = json.load(fh)
        ext_bw[rr_key] = np.round(kext_MHz, 4)
        with open(ext_path, "w") as fh:
            json.dump(ext_bw, fh, indent=6)
        logger.info(f"external_bandwidth[{rr_key}] = {kext_MHz:.5f} MHz")

        # --- internal_bandwidth.json ---
        int_path = sp_path + "/internal_bandwidth.json"
        with open(int_path, "r") as fh:
            int_bw = json.load(fh)
        int_bw[rr_key] = np.round(kint_MHz, 4)
        with open(int_path, "w") as fh:
            json.dump(int_bw, fh, indent=6)
        logger.info(f"internal_bandwidth[{rr_key}] = {kint_MHz:.5f} MHz")

        if not self.update_config:
            return

        timestamp = self.get_timestamp_str()

        # --- fr_vals.json ---
        fr_path = sp_path + "/fr_vals.json"
        buffer_fr = dict(self.fr_dict)
        buffer_fr["fr_vals"] = dict(buffer_fr.get("fr_vals", {}))
        buffer_fr["fr_vals"][rr_key] = float(f0_MHz)
        buffer_fr["timestamp"] = timestamp
        with open(fr_path, "w") as fh:
            json.dump(buffer_fr, fh, indent=6)
        logger.info(f"fr_vals[{rr_key}] = {f0_MHz:.3f} MHz | timestamp: {timestamp}")

        # --- rr_IF.json ---
        rr_if_path = sp_path + "/rr_IF.json"
        with open(rr_if_path, "r") as fh:
            rr_if_dict = json.load(fh)
        rr_if_dict[rr_key] = np.round(float(self.rr_if_calibrated), 4)
        with open(rr_if_path, "w") as fh:
            json.dump(rr_if_dict, fh, indent=6)
        logger.info(f"rr_IF[{rr_key}] = {self.rr_if_calibrated:.3f} MHz")

        # --- rr_LO.json ---
        rr_lo_path = sp_path + "/rr_LO.json"
        with open(rr_lo_path, "r") as fh:
            rr_lo_dict = json.load(fh)
        rr_lo_GHz = np.round(self.rr_lo_val_MHz * 1e-3, 4)   # rr_lo is in GHz
        rr_lo_dict[rr_key] = float(rr_lo_GHz)
        with open(rr_lo_path, "w") as fh:
            json.dump(rr_lo_dict, fh, indent=6)
        logger.info(f"rr_LO[{rr_key}] = {rr_lo_GHz:.6f} GHz")

    # ------------------------------------------------------------------
    # Save raw data
    # ------------------------------------------------------------------

    def save_experiment_data(self):
        """Save raw VNA data and fit results to a JSON file."""
        if self.fit_results is None:
            raise RuntimeError("No fit results — call analyze_and_plot() first.")

        result = {
            "rr_no": self.rr_no,
            "q_no": self.q_no,
            "low_power_dBm": self.low_power,
            "n_avgs": self.n_avgs,
            "if_bw_Hz": self.if_bw,
            "f_data_Hz": self.f_data,
            "r_data": self.r_data,
            "i_data": self.i_data,
            "fit_results": {
                "f0_GHz":   float(self.fit_results[0][0]),
                "kint_MHz": float(self.fit_results[1][0]),
                "kext_MHz": float(self.fit_results[2][0]),
                "Qint":     float(self.fit_q_vals[0][0]),
                "Qext":     float(self.fit_q_vals[1][0]),
            },
        }
        if self.do_punchout and self.fit_results_hp is not None:
            result["high_power_dBm"] = self.high_power
            result["r_data_hp"] = self.r_data_hp
            result["i_data_hp"] = self.i_data_hp
            result["fit_results_hp"] = {
                "f0_GHz":   float(self.fit_results_hp[0][0]),
                "kint_MHz": float(self.fit_results_hp[1][0]),
                "kext_MHz": float(self.fit_results_hp[2][0]),
                "Qint":     float(self.fit_q_vals_hp[0][0]),
                "Qext":     float(self.fit_q_vals_hp[1][0]),
            }

        json_path = str(self.path_to_save) + f"_rr{self.rr_no}.json"
        save_json(result, json_path)
        cprint(f"Data saved: {Path(json_path).as_uri()}", "green")

    # ------------------------------------------------------------------
    # Top-level orchestration
    # ------------------------------------------------------------------

    def run(self):
        """Switch → (turn off LOs) → connect → measure → analyse → update → (restore LOs) → disconnect."""
        t0 = time.time()
        if self.do_switch:
            self._switch_to_vna()
        if self.turn_off_LOs:
            self._turn_off_LOs()
        self.connect()
        try:
            self.run_experiment()
            self.analyze_and_plot()
            self.update_config_dicts()
            if self.save_data:
                self.save_experiment_data()
        finally:
            self.disconnect()
            if self.turn_off_LOs:
                self._turn_on_LOs()
        elapsed = time.time() - t0
        print(f"Total time: {int(elapsed // 60)}m {elapsed % 60:.1f}s")


def perform_vna_resonator_spectroscopy(q_no: int, rr_no: int = None, **kwargs):
    t0 = time.time()
    vna = VNASpectroscopy(q_no=q_no, rr_no=rr_no, **kwargs)
    vna.run()
    elapsed = time.time() - t0
    print(f"Total time: {int(elapsed // 60)}m {elapsed % 60:.1f}s")
    return vna

# ---------------------------------------------------------------------------
# Quick-run entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # TODO: Do all the LO's actually turn off? 
    q_list = [
        1,
        2,
        3,
        4,
        5,
        6,
    ]
    set_time_start = time.time()
    for q in q_list:
        perform_vna_resonator_spectroscopy(
            q_no=q,
            turn_off_LOs=True,
            # query_LOs=True,
            low_power=-30,
            search_f_start=7.0e9,
            search_f_stop=7.75e9,
            zoom_half_span=15e6,
            n_avgs=50,
            if_bw=1e3,
            update_config=True,
            save_data=False,
        )
    set_time_end = time.time()
    time_in_minutes = int((set_time_end - set_time_start) / 60)
    time_in_seconds = int((set_time_end - set_time_start) % 60)
    cprint(f"Total time taken for the entire set of qubits: {time_in_minutes} minutes, {time_in_seconds} seconds", "green")