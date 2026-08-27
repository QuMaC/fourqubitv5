"""
constants.py
============
Shared constants for the two-qubit pulse-level engines. Both the qutip
engine (two_q_pulse_sim.py) and the dynamiqs engine
(two_q_pulse_sim_dynamiqs.py) import from here so neither depends on the
other.
"""

import numpy as np

TWOPI = 2.0 * np.pi
DT_SAMPLE_NS = 4  # OPX clock
