"""
Reload JSON-backed calibration modules and rebuild the QM ``config`` dict.

Call this (or BaseExperiment.refresh_qm_config_from_disk) after calibration
scripts write to JSON so ``open_qm`` uses updated pulses, CR phase, readout
weights, etc.
"""
import importlib


def reload_qm_config():
    """
    Reload ``config_dictionaries`` then ``configuration_4qubitsv3``.

    Returns
    -------
    dict
        The new ``config`` object from ``configuration_4qubitsv3``.
    """
    import Configuration_Files.config_dictionaries as _cd
    import Configuration_Files.configuration_4qubitsv3 as _cfg

    importlib.reload(_cd)
    importlib.reload(_cfg)
    return _cfg.config
