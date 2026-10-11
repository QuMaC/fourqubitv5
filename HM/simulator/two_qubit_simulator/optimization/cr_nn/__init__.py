"""Physics-trained neural pulse generator for robust echoed CR."""

from .config import CRNNConfig, normalize_inputs
from .model import CRPulseMLP, center_crop_flat, flat_knobs_200

__all__ = [
    "CRNNConfig",
    "CRPulseMLP",
    "center_crop_flat",
    "flat_knobs_200",
    "normalize_inputs",
]
