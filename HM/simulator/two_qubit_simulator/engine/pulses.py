"""
pulses.py
=========
Envelope helpers and the Timeline builder for the two-qubit pulse-level
simulators. These produce the dict of channel -> complex envelope arrays
(eps = I + iQ, in MHz / Rabi-rate units, on the dt_sample grid) that the
engines consume; they are engine-agnostic (qutip / dynamiqs).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from HM.simulator.two_qubit_simulator.engine.constants import (
    DT_SAMPLE_NS,
    TWOPI,
)


# ---------------------------------------------------------------------------
# Envelope helpers  (complex envelope eps = I + iQ, in MHz / Rabi-rate units)
# ---------------------------------------------------------------------------
def flat_pulse(amp: complex, duration_ns: float,
               dt_ns: float = DT_SAMPLE_NS) -> np.ndarray:
    """Constant complex envelope."""
    n = int(round(duration_ns / dt_ns))
    return amp * np.ones(n, dtype=complex)


def gaussian_flat_top(amp: complex, t_rise_ns: float, t_flat_ns: float,
                      sigma_ns: float,
                      dt_ns: float = DT_SAMPLE_NS) -> np.ndarray:
    """Gaussian rise, flat top, Gaussian fall. `amp` may be complex to set the
    I/Q phase. Sampled at sample midpoints, piecewise-constant -- the same
    convention the solver assumes. Mirrors helper_functionsv2.rise_arr."""
    total_ns = 2 * t_rise_ns + t_flat_ns
    n = int(round(total_ns / dt_ns))
    env = np.zeros(n, dtype=complex)
    flat_end = t_rise_ns + t_flat_ns
    for k in range(n):
        t = (k + 0.5) * dt_ns
        if t < t_rise_ns:
            env[k] = np.exp(-0.5 * ((t - t_rise_ns) / sigma_ns) ** 2)
        elif t < flat_end:
            env[k] = 1.0
        else:
            env[k] = np.exp(-0.5 * ((t - flat_end) / sigma_ns) ** 2)
    return amp * env


def flat_pulse_for_rotation(angle_rad: float, duration_ns: float,
                            phase_rad: float = 0.0,
                            dt_ns: float = DT_SAMPLE_NS) -> np.ndarray:
    """A flat pulse whose area drives a single-qubit rotation of `angle_rad`
    on the {0,1} subspace (ignoring leakage / no DRAG). Convenient for sanity
    checks; for the real Bell sequence use calibrated amplitudes from the
    JSONs instead."""
    duration_us = duration_ns * 1e-3
    amp = angle_rad / (TWOPI * duration_us)
    return flat_pulse(amp * np.exp(1j * phase_rad), duration_ns, dt_ns)


def apply_virtual_z(waveform: np.ndarray, phase_rad: float) -> np.ndarray:
    """Virtual-Z is a frame change, realised by phase-shifting every pulse
    played AFTER it on that qubit's drive lines. Call this on each subsequent
    waveform before adding it to the Timeline. Sign convention: a virtual-Z of
    +theta shifts subsequent drive phases by -theta."""
    return np.asarray(waveform, dtype=complex) * np.exp(-1j * phase_rad)


# ---------------------------------------------------------------------------
# Timeline builder
# ---------------------------------------------------------------------------
class Timeline:
    """Assembles equal-length complex waveform arrays, one per channel.
    add() places a waveform at a start time; overlapping adds sum. The "circuit"
    for now IS this timeline -- no gate-level abstraction."""

    def __init__(self, channels: Sequence[str], dt_ns: float = DT_SAMPLE_NS):
        self.channels = list(channels)
        self.dt_ns = dt_ns
        self._buf = {ch: np.zeros(0, dtype=complex) for ch in self.channels}

    def _grow(self, ch: str, length: int) -> None:
        if len(self._buf[ch]) < length:
            pad = np.zeros(length - len(self._buf[ch]), dtype=complex)
            self._buf[ch] = np.concatenate([self._buf[ch], pad])

    def add(self, channel: str, start_ns: float,
            waveform: np.ndarray) -> float:
        """Place `waveform` on `channel` starting at start_ns. Returns the end
        time in ns (handy for back-to-back scheduling)."""
        if channel not in self._buf:
            raise KeyError(f"unknown channel {channel!r}")
        start = int(round(start_ns / self.dt_ns))
        wf = np.asarray(waveform, dtype=complex)
        end = start + len(wf)
        self._grow(channel, end)
        self._buf[channel][start:end] += wf
        return end * self.dt_ns

    def finalize(self) -> dict[str, np.ndarray]:
        """Zero-pad every channel to the common length and return the dict."""
        L = max((len(b) for b in self._buf.values()), default=0)
        out = {}
        for ch in self.channels:
            self._grow(ch, L)
            out[ch] = self._buf[ch].copy()
        return out
