"""
Pulses but made in JAX, 
things to remember:
The idea in this file is that we make all pusles with jnp
each pulse requires static traceable structure, 
static here refers to the concept of a tape being fixed. Once every 
value is traceable we can use backward mode differentiation.
This is the core idea of this file.
"""

from __future__ import annotations

from functools import partial
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np

from Helper_Functions.helper_functionsv2 import fall_arr, rise_arr

CHANNEL_NAMES = ("q1_drive", "q2_drive", "cr_drive")
DEFAULT_ECHO_CHANNEL = "q1_drive"

def _templates_1ns(t_rise_ns: int) -> tuple[jnp.ndarray, jnp.ndarray]:
    t_rise_ns = int(t_rise_ns)
    rise = jnp.asarray(np.asarray(rise_arr(t_rise_ns)), dtype= np.float64)
    fall = jnp.asarray(np.asarray(fall_arr(t_rise_ns)), dtype= np.float64)

    return rise, fall

def _expand_knobs_to_flat(knobs: jnp.ndarray, n_flat: int) -> jnp.ndarray:
    """Hold each knob for k = n_flat // n_knobs samples. n_knobs must divide n_flat"""
    n_knobs = int(knobs.shape[0])
    n_flat = int(n_flat)

    if n_knobs < 1 or n_flat < 1:
        raise ValueError("n_knobs and n_flat must be at least 1")
    if n_flat % n_knobs != 0:
        raise ValueError("n_knobs must divide n_flat")

    return jnp.repeat(knobs, n_flat // n_knobs)

def assemble_cr_half_jax(
    knobs: jnp.ndarray,
    *,
    rise: jnp.ndarray,
    fall: jnp.ndarray,
    n_flat: int,
    n_link_samples: int,
) -> tuple[jnp.ndarray, dict[str, tuple[int, int]]]:
    
    knobs = jnp.asarray(knobs).reshape(-1)
    flat = _expand_knobs_to_flat(knobs, n_flat)

    n_link = max(1, min(int(n_link_samples), n_flat))
    u_rise_end = jnp.mean(flat[:n_link])
    u_fall_start = jnp.mean(flat[-n_link:])

    rise_end = rise[-1]
    fall_start = fall[0]

    rise_part = (rise/rise_end) * u_rise_end
    fall_part = (fall/fall_start) * u_fall_start

    wf = jnp.concatenate([rise_part.astype(knobs.dtype), flat, fall_part.astype(knobs.dtype)])

    n_rise = int(rise.shape[0])
    n_fall = int(fall.shape[0])

    slices = {
        "rise": (0, n_rise),
        "flat": (n_rise, n_rise + n_flat),
        "fall": (n_rise + n_flat, n_rise + n_flat + n_fall),
    }

    return wf, slices


def echoed_timeline_jax(
    cr_plus: jnp.ndarray, 
    x_pi: jnp.ndarray,
    *,
    channel_names: tuple[str, ...] = CHANNEL_NAMES,
    echo_channel: str = DEFAULT_ECHO_CHANNEL,
) -> dict[str, jnp.ndarray]:
    

    cr_plus = jnp.asarray(cr_plus).reshape(-1)
    x_pi = jnp.asarray(x_pi).reshape(-1)
    n_cr = int(cr_plus.shape[0])
    n_x = int(x_pi.shape[0])

    zeroes_cr = jnp.zeros((n_cr,), dtype=cr_plus.dtype)
    zeroes_x = jnp.zeros((n_x,), dtype=cr_plus.dtype)

    cr_drive = jnp.concatenate([cr_plus, zeroes_x, -cr_plus, zeroes_x])
    echo = jnp.concatenate([zeroes_cr, x_pi, zeroes_cr, x_pi])
    L = int(cr_drive.shape[0])

    idle = jnp.zeros((L,), dtype=cr_plus.dtype)

    if echo_channel not in channel_names:
        raise ValueError(f"echo_channel {echo_channel} not in channel_names {channel_names}")

    out = {}

    for name in channel_names:
        if name == "cr_drive":
            out[name] = cr_drive
        elif name == echo_channel:
            out[name] = echo
        else:
            out[name] = idle

    return out


    