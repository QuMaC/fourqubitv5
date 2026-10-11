"""Configuration and input scaling for the echoed-CR neural pulse model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

jax.config.update("jax_enable_x64", True)


@dataclass(frozen=True)
class CRNNConfig:
    """One serializable contract for training, inference, and evaluation."""

    qubit_pair: tuple[int, int] = (1, 2)
    target_gate: str = "zx_m90"
    n_levels: int = 4
    dt_sample_ns: float = 1.0
    durations_ns: tuple[int, ...] = tuple(range(80, 201, 10))
    max_flat_samples: int = 200

    robustness_min_mhz: float = 0.0
    robustness_max_mhz: float = 0.300
    amp_min_mhz: float = 30.0
    amp_max_mhz: float = 100.0
    coupling_center_mhz: float = 3.216328
    coupling_half_span_mhz: float = 1.0

    t_rise_ns: int = 16
    n_link_samples: int = 8
    seed_amp_mhz: float = 21.0
    seed_phase_rad: float = 0.0
    envelope: str = "bessel4_350mhz"

    hidden_width: int = 1024
    hidden_layers: int = 5
    output_size: int = 400
    init_output_scale: float = 1e-3

    fidelity_metric: str = "mean_minus_spread"
    spread_penalty_lambda: float = 0.3
    leakage_weight: float = 0.0

    optimizer: str = "adan"
    learning_rate: float = 2e-4
    weight_decay: float = 0.0
    batch_size: int = 1
    train_steps: int = 10_000
    random_seed: int = 7
    checkpoint_every: int = 100
    log_every: int = 10
    keep_checkpoints: int = 3

    def validate(self) -> None:
        if tuple(self.qubit_pair) != (1, 2):
            raise ValueError("the first CR NN is locked to qubit_pair=(1, 2)")
        if self.target_gate != "zx_m90":
            raise ValueError("the first CR NN is locked to target_gate='zx_m90'")
        if self.n_levels != 4:
            raise ValueError("the first CR NN is locked to four transmon levels")
        if self.dt_sample_ns != 1.0:
            raise ValueError("CR NN training requires dt_sample_ns=1.0")
        if self.durations_ns != tuple(range(80, 201, 10)):
            raise ValueError("durations_ns is locked to 80:10:200 ns")
        if self.max_flat_samples != 200:
            raise ValueError("max_flat_samples is locked to 200")
        if not self.durations_ns:
            raise ValueError("durations_ns must be non-empty")
        if tuple(sorted(set(self.durations_ns))) != tuple(self.durations_ns):
            raise ValueError("durations_ns must be sorted and unique")
        if min(self.durations_ns) < 1:
            raise ValueError("every duration must be positive")
        if max(self.durations_ns) > self.max_flat_samples:
            raise ValueError("duration exceeds max_flat_samples")
        if any(int(t) != t for t in self.durations_ns):
            raise ValueError("durations must be integer nanoseconds")
        if any((self.max_flat_samples - int(t)) % 2 for t in self.durations_ns):
            raise ValueError("center cropping requires even max-duration differences")
        if self.output_size != 2 * self.max_flat_samples:
            raise ValueError("output_size must equal 2 * max_flat_samples")
        if self.robustness_min_mhz < 0.0:
            raise ValueError("robustness half-width cannot be negative")
        if not np.isclose(self.robustness_min_mhz, 0.0) or not np.isclose(
            self.robustness_max_mhz, 0.300
        ):
            raise ValueError("robustness range is locked to [0, 0.300] MHz")
        if self.robustness_max_mhz <= self.robustness_min_mhz:
            raise ValueError("invalid robustness interval")
        if not np.isclose(self.amp_min_mhz, 30.0) or not np.isclose(
            self.amp_max_mhz, 100.0
        ):
            raise ValueError("amplitude range is locked to [30, 100] MHz")
        if self.amp_min_mhz <= abs(self.seed_amp_mhz):
            raise ValueError("amp_min_mhz must exceed the calibrated seed amplitude")
        if self.amp_max_mhz <= self.amp_min_mhz:
            raise ValueError("invalid amplitude interval")
        if self.coupling_half_span_mhz <= 0.0:
            raise ValueError("coupling_half_span_mhz must be positive")
        if not np.isclose(self.coupling_center_mhz, 3.216328) or not np.isclose(
            self.coupling_half_span_mhz, 1.0
        ):
            raise ValueError("J12 is locked to 3.216328 +/- 1 MHz")
        if self.coupling_min_mhz <= 0.0:
            raise ValueError("coupling range must stay positive")
        if self.t_rise_ns != 16 or self.n_link_samples != 8:
            raise ValueError("rise and link settings are locked to 16 ns and 8 samples")
        if not np.isclose(self.seed_amp_mhz, 21.0) or not np.isclose(
            self.seed_phase_rad, 0.0
        ):
            raise ValueError("the calibrated seed is locked to +21 MHz at zero phase")
        if self.envelope != "bessel4_350mhz":
            raise ValueError("the transfer function is locked to bessel4_350mhz")
        if self.t_rise_ns < 1 or self.n_link_samples < 1:
            raise ValueError("rise and link lengths must be positive")
        if self.hidden_width < 1 or self.hidden_layers < 1:
            raise ValueError("the MLP must have at least one hidden neuron and layer")
        if self.fidelity_metric != "mean_minus_spread":
            raise ValueError("the first CR NN is locked to mean_minus_spread")
        if not np.isclose(self.spread_penalty_lambda, 0.3):
            raise ValueError("spread_penalty_lambda is locked to 0.3")
        if not np.isclose(self.leakage_weight, 0.0):
            raise ValueError("the initial leakage weight is locked to zero")
        if self.optimizer.lower() != "adan":
            raise ValueError("the first CR NN is locked to Adan")
        if self.batch_size < 1 or self.train_steps < 1:
            raise ValueError("batch_size and train_steps must be positive")
        if self.checkpoint_every < 1 or self.log_every < 1:
            raise ValueError("checkpoint_every and log_every must be positive")

    @property
    def coupling_min_mhz(self) -> float:
        return self.coupling_center_mhz - self.coupling_half_span_mhz

    @property
    def coupling_max_mhz(self) -> float:
        return self.coupling_center_mhz + self.coupling_half_span_mhz

    @property
    def input_size(self) -> int:
        return 4

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["qubit_pair"] = list(self.qubit_pair)
        out["durations_ns"] = list(self.durations_ns)
        return out

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "CRNNConfig":
        known = {f.name for f in fields(cls)}
        extra = set(values) - known
        if extra:
            raise ValueError(f"unknown CRNNConfig fields: {sorted(extra)}")
        data = dict(values)
        if "qubit_pair" in data:
            data["qubit_pair"] = tuple(int(v) for v in data["qubit_pair"])
        if "durations_ns" in data:
            data["durations_ns"] = tuple(int(v) for v in data["durations_ns"])
        config = cls(**data)
        config.validate()
        return config


def normalize_inputs(
    config: CRNNConfig,
    duration_ns,
    robustness_mhz,
    amp_bound_mhz,
    coupling_mhz,
) -> jnp.ndarray:
    """Map physical request coordinates to approximately [-1, 1]."""

    def scale(value, low: float, high: float):
        value = jnp.asarray(value, dtype=jnp.float64)
        return 2.0 * (value - low) / (high - low) - 1.0

    return jnp.stack(
        [
            scale(duration_ns, min(config.durations_ns), max(config.durations_ns)),
            scale(
                robustness_mhz,
                config.robustness_min_mhz,
                config.robustness_max_mhz,
            ),
            scale(amp_bound_mhz, config.amp_min_mhz, config.amp_max_mhz),
            scale(
                coupling_mhz,
                config.coupling_min_mhz,
                config.coupling_max_mhz,
            ),
        ],
        axis=-1,
    )


def physical_input_array(
    duration_ns,
    robustness_mhz,
    amp_bound_mhz,
    coupling_mhz,
) -> np.ndarray:
    """Return the four physical coordinates in their documented order."""
    return np.stack(
        np.broadcast_arrays(
            np.asarray(duration_ns, dtype=float),
            np.asarray(robustness_mhz, dtype=float),
            np.asarray(amp_bound_mhz, dtype=float),
            np.asarray(coupling_mhz, dtype=float),
        ),
        axis=-1,
    )
