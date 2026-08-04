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

AC_AMP_FACTOR = 0.4  # config_builder.py: grft_arr_gen scales every waveform by 0.4


# ---------------------------------------------------------------------------
# Envelope helpers  (complex envelope eps = I + iQ, in MHz / Rabi-rate units)
# ---------------------------------------------------------------------------
def calibrate_f_rabi_per_opx1(amp_scale_x180: float, length_ns: int, rise_ns: int) -> float:
    """MHz Rabi rate per unit OPX waveform sample, fixed by the X180 calibration."""
    from Helper_Functions.helper_functionsv2 import grft_pulse

    a_grft = float(np.sum(grft_pulse(length_ns, rise_ns)))
    a_wf_x180 = AC_AMP_FACTOR * amp_scale_x180 * a_grft
    return 0.5 / (a_wf_x180 * 1e-3)


def drag_grft_envelope_mhz(
    amplitude: float,
    length_ns: int,
    rise_ns: int,
    anharm_hz: float,
    alpha: float,
    detuning: float = 0.0,
    f_rabi_per_opx1: float = 1.0,
) -> np.ndarray:
    """Complex d_X180 envelope (MHz), one sample per ns.

    Matches ``config_builder.py`` / ``drag_grft_pulse_waveforms`` (GRFT + DRAG).
    """
    from Helper_Functions.helper_functionsv2 import drag_grft_pulse_waveforms

    i_wf, q_wf = drag_grft_pulse_waveforms(
        amplitude=amplitude,
        length=length_ns,
        rise=rise_ns,
        anharmonicity=anharm_hz,
        alpha=alpha,
        detuning=detuning,
    )
    return (np.asarray(i_wf, dtype=complex) + 1j * np.asarray(q_wf, dtype=complex)) * f_rabi_per_opx1


def cr_rise_fall_flat_top(
    amp: complex,
    t_flat_ns: float,
    t_rise_ns: float | None = None,
    dt_ns: float = DT_SAMPLE_NS,
) -> np.ndarray:
    """CR envelope matching ``play_flat_top`` in ``Helper_Functions/macros.py``.

    Hardware plays ``rise_wf`` + ``const`` + ``fall_wf`` (``rise_arr`` / flat /
    ``fall_arr`` from ``config_builder.config_add_rise_fall``), each scaled by
    the same OPX amplitude. ``rise_arr`` / ``fall_arr`` already include
    ``AC_AMP_FACTOR``; the flat section is unity. ``amp`` is the flat-top Rabi
    rate in MHz (``amp_mhz`` in the CR experiments), optionally with phase.
    """
    from Helper_Functions.helper_functionsv2 import fall_arr, rise_arr

    if t_rise_ns is None:
        from Configuration_Files.config_dictionaries import cr_tail_ns

        t_rise_ns = float(cr_tail_ns)
    t_rise_ns = int(round(t_rise_ns))

    rise = np.asarray(rise_arr(t_rise_ns), dtype=float)
    fall = np.asarray(fall_arr(t_rise_ns), dtype=float)
    n_flat = max(0, int(round(float(t_flat_ns) / dt_ns)))

    if dt_ns == 1.0:
        env = np.concatenate([rise, np.ones(n_flat, dtype=float), fall])
    else:
        step = int(round(dt_ns))
        if step <= 0:
            raise ValueError(f"dt_ns must be positive, got {dt_ns}")
        rise = rise[::step]
        fall = fall[::step]
        env = np.concatenate([rise, np.ones(n_flat, dtype=float), fall])

    return amp * env.astype(complex)


def assemble_cr_half_from_flat_knobs(
    flat_knobs: np.ndarray,
    flat_len_ns: float,
    t_rise_ns: float | int,
    dt_ns: float = DT_SAMPLE_NS,
    n_link_samples: int = 8,
) -> tuple[np.ndarray, dict[str, int]]:
    """Build one CR-half complex envelope (MHz) from flat-top knobs.

    GRAPE optimizes only ``flat_knobs`` (complex, one per flat segment).  The
    lab rise/fall templates are rescaled to meet the flat region at its edges:

    - rise ends at the mean of the first ``n_link_samples`` flat samples
    - fall starts at the mean of the last ``n_link_samples`` flat samples
      (independent of rise)

  ``n_link_samples`` defaults to 8.  When the flat top is shorter than
    ``n_link_samples``, all available flat samples are used.

    Returns ``(waveform, slice_indices)`` where ``slice_indices`` has keys
    ``rise``, ``flat``, ``fall`` giving sample ranges on the sim grid.
    """
    from Helper_Functions.helper_functionsv2 import fall_arr, rise_arr

    flat_knobs = np.asarray(flat_knobs, dtype=complex).reshape(-1)
    n_knobs = flat_knobs.size
    if n_knobs < 1:
        raise ValueError("flat_knobs must have at least one entry")

    t_rise_ns = int(round(float(t_rise_ns)))
    rise = np.asarray(rise_arr(t_rise_ns), dtype=float)
    fall = np.asarray(fall_arr(t_rise_ns), dtype=float)

    if dt_ns != 1.0:
        step = int(round(dt_ns))
        if step <= 0:
            raise ValueError(f"dt_ns must be positive, got {dt_ns}")
        rise = rise[::step]
        fall = fall[::step]

    n_flat = max(1, int(round(float(flat_len_ns) / dt_ns)))
    flat = np.empty(n_flat, dtype=complex)
    for i in range(n_knobs):
        start = (i * n_flat) // n_knobs
        end = ((i + 1) * n_flat) // n_knobs
        if end <= start:
            end = min(start + 1, n_flat)
        flat[start:end] = flat_knobs[i]

    n_link = max(1, min(int(n_link_samples), n_flat))
    u_rise_end = np.mean(flat[:n_link])
    u_fall_start = np.mean(flat[-n_link:])

    rise_end = float(rise[-1])
    fall_start = float(fall[0])
    if abs(rise_end) < 1e-12:
        raise ValueError("rise template ends at zero; cannot anchor to flat edge")
    if abs(fall_start) < 1e-12:
        raise ValueError("fall template starts at zero; cannot anchor to flat edge")

    rise_part = (rise / rise_end) * u_rise_end
    fall_part = (fall / fall_start) * u_fall_start

    wf = np.concatenate([rise_part.astype(complex), flat, fall_part.astype(complex)])

    n_rise = len(rise_part)
    n_fall = len(fall_part)
    slices = {
        "rise": (0, n_rise),
        "flat": (n_rise, n_rise + n_flat),
        "fall": (n_rise + n_flat, n_rise + n_flat + n_fall),
    }

    if not np.allclose(rise_part[-1], u_rise_end):
        raise RuntimeError("rise/flat-edge continuity check failed")
    if not np.allclose(fall_part[0], u_fall_start):
        raise RuntimeError("fall/flat-edge continuity check failed")

    return wf, slices


def seed_flat_knobs_from_calibrated_cr(
    n_flat_knobs: int,
    flat_len_ns: float,
    amp_mhz: float,
    phase_rad: float,
    t_rise_ns: float | int,
    dt_ns: float = DT_SAMPLE_NS,
) -> np.ndarray:
    """Initial flat knobs by subsampling a calibrated ``cr_rise_fall_flat_top`` pulse."""
    amp = float(amp_mhz) * np.exp(1j * float(phase_rad))
    wf = cr_rise_fall_flat_top(
        amp=amp,
        t_flat_ns=flat_len_ns,
        t_rise_ns=t_rise_ns,
        dt_ns=dt_ns,
    )
    _, slices = assemble_cr_half_from_flat_knobs(
        flat_knobs=np.array([amp], dtype=complex),
        flat_len_ns=flat_len_ns,
        t_rise_ns=t_rise_ns,
        dt_ns=dt_ns,
    )
    flat_start, flat_end = slices["flat"]
    flat_samples = wf[flat_start:flat_end]
    n_flat = flat_samples.size
    n_knobs = int(n_flat_knobs)
    if n_knobs < 1:
        raise ValueError("n_flat_knobs must be >= 1")

    knobs = np.empty(n_knobs, dtype=complex)
    for i in range(n_knobs):
        j0 = (i * n_flat) // n_knobs
        j1 = ((i + 1) * n_flat) // n_knobs
        if j1 <= j0:
            knobs[i] = flat_samples[j0]
        else:
            knobs[i] = np.mean(flat_samples[j0:j1])
    return knobs


def flat_pulse(amp: complex, duration_ns: float,
               dt_ns: float = DT_SAMPLE_NS) -> np.ndarray:
    """Constant complex envelope."""
    n = int(round(duration_ns / dt_ns))
    return amp * np.ones(n, dtype=complex)


def gaussian_flat_top(amp: complex, t_rise_ns: float, t_flat_ns: float,
                      sigma_ns: float,
                      dt_ns: float = DT_SAMPLE_NS) -> np.ndarray:
    """Gaussian rise, flat top, Gaussian fall (continuous midpoint sampling).

    Legacy helper kept for quick demos. For hardware-matched CR pulses use
    ``cr_rise_fall_flat_top`` instead (``rise_arr`` / flat / ``fall_arr``).
    """
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
# Arbitrary waveform loading (from .npz files, e.g. GRAPE-optimized pulses)
# ---------------------------------------------------------------------------
# (I_key, Q_key) pairs tried in order when auto-detecting a complex envelope
# stored as separate real/imag arrays. The first pair matches the GRAPE dump
# written by optimization/cr_grape.py (``cr_half_opt_I`` / ``cr_half_opt_Q``).
_NPZ_IQ_KEY_PAIRS = (
    ("cr_half_opt_I", "cr_half_opt_Q"),
    ("cr_half_seed_I", "cr_half_seed_Q"),
    ("I", "Q"),
    ("i_wf", "q_wf"),
    ("wf_I", "wf_Q"),
)
# Single-array keys tried in order when the envelope is stored as one complex
# (or real) array rather than separate I/Q parts.
_NPZ_COMPLEX_KEYS = (
    "waveform",
    "wf",
    "envelope",
    "cr_half_opt",
    "cr_half",
    "pulse",
)


def load_waveform_npz(
    path: str,
    *,
    key: str | None = None,
    i_key: str | None = None,
    q_key: str | None = None,
) -> np.ndarray:
    """Load a complex envelope (eps = I + iQ, in MHz / Rabi-rate units) from an
    ``.npz`` file.

    The envelope is returned on whatever sample grid it was saved on; it is the
    caller's job to make sure that grid matches the timeline ``dt_ns`` (the
    GRAPE dumps are written on a 1 ns grid).

    Key resolution order:
      1. explicit ``key`` -- a single (complex or real) array,
      2. explicit ``i_key`` + ``q_key`` -- real and imaginary parts,
      3. auto-detected I/Q pairs (e.g. the GRAPE ``cr_half_opt_I/Q``),
      4. auto-detected single complex/real array (e.g. ``waveform``).
    """
    with np.load(path, allow_pickle=False) as data:
        available = set(data.files)

        if key is not None:
            if key not in available:
                raise KeyError(
                    f"key {key!r} not found in {path}; available: {sorted(available)}"
                )
            return np.asarray(data[key], dtype=complex).reshape(-1)

        if i_key is not None or q_key is not None:
            if i_key is None or q_key is None:
                raise ValueError("provide both i_key and q_key, or neither")
            missing = {k for k in (i_key, q_key) if k not in available}
            if missing:
                raise KeyError(
                    f"keys {sorted(missing)} not found in {path}; "
                    f"available: {sorted(available)}"
                )
            real = np.asarray(data[i_key], dtype=float).reshape(-1)
            imag = np.asarray(data[q_key], dtype=float).reshape(-1)
            return real + 1j * imag

        for ik, qk in _NPZ_IQ_KEY_PAIRS:
            if ik in available and qk in available:
                real = np.asarray(data[ik], dtype=float).reshape(-1)
                imag = np.asarray(data[qk], dtype=float).reshape(-1)
                return real + 1j * imag

        for ck in _NPZ_COMPLEX_KEYS:
            if ck in available:
                return np.asarray(data[ck], dtype=complex).reshape(-1)

    raise KeyError(
        f"could not auto-detect a waveform in {path}; available keys: "
        f"{sorted(available)}. Pass key=, or i_key= and q_key=, explicitly."
    )


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

    def add_arb(self, channel: str, npz_path: str, start_ns: float = 0.0, *,
                key: str | None = None,
                i_key: str | None = None,
                q_key: str | None = None,
                amp_scale: float = 1.0,
                phase_rad: float = 0.0) -> float:
        """Load an arbitrary complex envelope from an ``.npz`` file and place it
        on `channel` starting at `start_ns` (the "arb pulse" command).

        The loaded envelope (eps = I + iQ, in MHz) is optionally rescaled and
        phase-shifted: ``eps -> amp_scale * exp(i*phase_rad) * eps``. The npz
        must be on the same sample grid as this timeline's ``dt_ns`` (the GRAPE
        dumps are 1 ns/sample). See ``load_waveform_npz`` for key resolution.
        Returns the end time in ns (handy for back-to-back scheduling)."""
        wf = load_waveform_npz(npz_path, key=key, i_key=i_key, q_key=q_key)
        if amp_scale != 1.0 or phase_rad != 0.0:
            wf = wf * (float(amp_scale) * np.exp(1j * float(phase_rad)))
        return self.add(channel, start_ns, wf)

    def finalize(self) -> dict[str, np.ndarray]:
        """Zero-pad every channel to the common length and return the dict."""
        L = max((len(b) for b in self._buf.values()), default=0)
        out = {}
        for ch in self.channels:
            self._grow(ch, L)
            out[ch] = self._buf[ch].copy()
        return out
