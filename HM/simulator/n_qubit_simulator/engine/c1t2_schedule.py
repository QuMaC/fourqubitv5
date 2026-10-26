"""Saved c1t2 GRAPE half to a finalized n-qubit timeline dictionary."""

from __future__ import annotations

import json
from pathlib import Path

import jax.numpy as jnp
import numpy as np

from HM.simulator.n_qubit_simulator.engine.n_q_pulse_sim_dynamiqs import (
    _configure_jax,
)
from HM.simulator.n_qubit_simulator.engine.pulses_jax import (
    _templates_1ns,
    assemble_cr_half_jax,
    echoed_timeline_jax,
)


_SOURCE_TO_DEST = {
    "q1_drive": "q1_drive",
    "q2_drive": "q2_drive",
    "cr_drive": "cr_c1_t2",
}


def load_grape_sidecar(npz_path: str) -> dict:
    """Read the JSON written next to a GRAPE ``.npz``."""

    json_path = Path(npz_path).with_suffix(".json")
    if not json_path.is_file():
        raise FileNotFoundError(
            f"expected sidecar {json_path}. The NPZ alone does not store "
            "n_levels or the rise and flat lengths."
        )
    with json_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    config = payload["config"]
    qubit_pair = tuple(int(qubit_id) for qubit_id in config["qubit_pair"])
    if qubit_pair != (1, 2):
        raise ValueError(
            f"Phase 2 parity is the c1t2 archive, got qubit_pair {qubit_pair}"
        )
    n_levels = int(config["n_levels"])
    if n_levels < 2:
        raise ValueError(f"sidecar n_levels must be at least 2, got {n_levels}")
    return {
        "n_levels": n_levels,
        "flat_len_ns": float(config["flat_len_ns"]),
        "t_rise_ns": int(config["t_rise_ns"]),
        "n_link_samples": int(config["n_link_samples"]),
        "n_flat_knobs": int(config["n_flat_knobs"]),
        "qubit_pair": qubit_pair,
        "json_path": str(json_path),
    }


def load_optimized_cr_half(npz_path: str) -> tuple[jnp.ndarray, jnp.ndarray]:
    """Return ``(cr_half, flat_knobs_opt)`` from the saved I/Q arrays."""

    with np.load(npz_path, allow_pickle=False) as data:
        required = ("cr_half_opt_I", "cr_half_opt_Q", "flat_knobs_opt", "t_ns")
        missing = [key for key in required if key not in data.files]
        if missing:
            raise KeyError(
                f"{npz_path} is missing {missing}; available {sorted(data.files)}"
            )
        real = np.asarray(data["cr_half_opt_I"], dtype=np.float64).reshape(-1)
        imag = np.asarray(data["cr_half_opt_Q"], dtype=np.float64).reshape(-1)
        knobs = np.asarray(data["flat_knobs_opt"]).reshape(-1)
        t_ns = np.asarray(data["t_ns"], dtype=np.float64).reshape(-1)

    if real.shape != imag.shape:
        raise ValueError("cr_half_opt_I and cr_half_opt_Q differ in length")
    if t_ns.shape != real.shape:
        raise ValueError("t_ns length does not match the saved CR half")
    if t_ns.size > 1 and float(np.max(np.abs(np.diff(t_ns) - 1.0))) > 1e-9:
        raise ValueError("Phase 2 expects the saved CR half on a 1 ns grid")

    waveform = jnp.asarray(real + 1j * imag)
    return waveform, jnp.asarray(knobs)


def rebuild_cr_half(knobs: jnp.ndarray, sidecar: dict) -> jnp.ndarray:
    """Assemble the half the same way the JAX GRAPE path does."""

    n_flat = int(round(sidecar["flat_len_ns"]))
    if int(knobs.shape[0]) != int(sidecar["n_flat_knobs"]):
        raise ValueError(
            f"flat_knobs_opt length {int(knobs.shape[0])} does not match "
            f"sidecar n_flat_knobs {sidecar['n_flat_knobs']}"
        )
    rise, fall = _templates_1ns(sidecar["t_rise_ns"])
    waveform, _slices = assemble_cr_half_jax(
        knobs,
        rise=rise,
        fall=fall,
        n_flat=n_flat,
        n_link_samples=sidecar["n_link_samples"],
    )
    return waveform


def calibrate_f_rabi_per_opx1(
    amp_scale_x180: float,
    length_ns: int,
    rise_ns: int,
) -> float:
    """MHz Rabi rate per unit OPX waveform sample, from the X180 calibration."""

    from Helper_Functions.helper_functionsv2 import grft_pulse

    ac_amp_factor = 0.4
    a_grft = float(np.sum(grft_pulse(length_ns, rise_ns)))
    a_wf_x180 = ac_amp_factor * amp_scale_x180 * a_grft
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
    """Complex d_X180 envelope in MHz, one sample per ns."""

    from Helper_Functions.helper_functionsv2 import drag_grft_pulse_waveforms

    i_wf, q_wf = drag_grft_pulse_waveforms(
        amplitude=amplitude,
        length=length_ns,
        rise=rise_ns,
        anharmonicity=anharm_hz,
        alpha=alpha,
        detuning=detuning,
    )
    return (
        np.asarray(i_wf, dtype=complex) + 1j * np.asarray(q_wf, dtype=complex)
    ) * f_rabi_per_opx1


def build_q1_x_pi() -> jnp.ndarray:
    """Calibrated control Xπ used as the echoed-CR echo."""

    from Configuration_Files.config_dictionaries import (
        amp_scale,
        anharmonicities,
        drag_dict,
        pi_len_ns,
        pi_rise_grft_ns,
    )

    qubit_key = "1"
    amplitude = float(amp_scale[qubit_key]["X180"])
    length_ns = int(pi_len_ns[qubit_key])
    rise_ns = int(pi_rise_grft_ns)
    waveform = drag_grft_envelope_mhz(
        amplitude=amplitude,
        length_ns=length_ns,
        rise_ns=rise_ns,
        anharm_hz=float(anharmonicities[qubit_key]) * 1e6,
        alpha=float(drag_dict[qubit_key]["alpha"]),
        detuning=float(drag_dict[qubit_key]["det"]),
        f_rabi_per_opx1=calibrate_f_rabi_per_opx1(
            amplitude, length_ns, rise_ns
        ),
    )
    return jnp.asarray(waveform)


def echoed_c1t2_timeline(
    cr_plus: jnp.ndarray,
    x_pi: jnp.ndarray | None = None,
) -> dict[str, jnp.ndarray]:
    """Echoed pair timeline on ``q1_drive``, ``q2_drive``, and ``cr_drive``."""

    if x_pi is None:
        x_pi = build_q1_x_pi()
    return echoed_timeline_jax(cr_plus, x_pi)


def embed_c1t2_timeline(
    pair_timeline: dict[str, jnp.ndarray],
    channel_names,
) -> dict[str, jnp.ndarray]:
    """Place the pair timeline onto an n-qubit channel registry.

    ``cr_drive`` is written to ``cr_c1_t2``. Every channel that is not the
    Q1 drive, the Q2 drive, or ``cr_c1_t2`` stays an explicit zero buffer of
    the echoed length.
    """

    channel_names = tuple(channel_names)
    missing = [
        dest for dest in _SOURCE_TO_DEST.values() if dest not in channel_names
    ]
    if missing:
        raise KeyError(f"channel registry is missing {missing}")

    length = int(jnp.asarray(pair_timeline["cr_drive"]).shape[0])
    for source in _SOURCE_TO_DEST:
        source_length = int(jnp.asarray(pair_timeline[source]).shape[0])
        if source_length != length:
            raise ValueError(
                f"{source} has length {source_length}, expected {length}"
            )

    out = {
        name: jnp.zeros(length, dtype=jnp.complex128)
        for name in channel_names
    }
    for source, dest in _SOURCE_TO_DEST.items():
        out[dest] = jnp.asarray(pair_timeline[source], dtype=jnp.complex128)
    return out
