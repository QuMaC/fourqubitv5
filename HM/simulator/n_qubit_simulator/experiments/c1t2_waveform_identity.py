"""Prove the local c1t2 timeline matches the trusted 2Q assembler.

Run from fourqubitv5 after setting C1T2_NPZ_PATH:

    python -m HM.simulator.n_qubit_simulator.experiments.c1t2_waveform_identity
"""

from __future__ import annotations

import jax.numpy as jnp

from HM.simulator.n_qubit_simulator.engine.c1t2_schedule import (
    echoed_c1t2_timeline,
    embed_c1t2_timeline,
    load_grape_sidecar,
    load_optimized_cr_half,
    rebuild_cr_half,
)
from HM.simulator.two_qubit_simulator.engine.pulses_jax import (
    echoed_timeline_jax as echoed_timeline_2q,
)


# Local robust c1t2 archive. The sibling .json sits beside this file.
C1T2_NPZ_PATH = (
    "/home/hm/IITB/TIFR/Software/Hari_6_qubit/fourqubitv5/HM/simulator/"
    "two_qubit_simulator/optimization/optimization_tests/results/"
    "robust_lp350mhz/"
    "cr_grape_robust_zz0p15MHz_mms_l0p3_20261003_191251.npz"
)


def main() -> None:
    if not C1T2_NPZ_PATH:
        raise SystemExit(
            "Set C1T2_NPZ_PATH in c1t2_waveform_identity.py to a local "
            "GRAPE .npz. The sibling .json must have the same stem."
        )

    sidecar = load_grape_sidecar(C1T2_NPZ_PATH)
    saved_half, knobs = load_optimized_cr_half(C1T2_NPZ_PATH)
    rebuilt = rebuild_cr_half(knobs, sidecar)
    half_error = float(jnp.max(jnp.abs(saved_half - rebuilt)))
    print("sidecar", sidecar["json_path"])
    print("n_levels", sidecar["n_levels"])
    print("flat_len_ns", sidecar["flat_len_ns"])
    print("half samples", int(saved_half.shape[0]))
    print("rebuilt half max abs error", half_error)
    assert half_error == 0.0 or half_error < 1e-12

    local_pair = echoed_c1t2_timeline(saved_half)
    n_half = int(saved_half.shape[0])
    n_echo = int((local_pair["q1_drive"].shape[0] - 2 * n_half) // 2)
    x_pi = local_pair["q1_drive"][n_half : n_half + n_echo]
    trusted_pair = echoed_timeline_2q(saved_half, x_pi)
    for name in ("q1_drive", "q2_drive", "cr_drive"):
        error = float(jnp.max(jnp.abs(local_pair[name] - trusted_pair[name])))
        print("pair channel", name, "max abs error", error)
        assert error < 1e-12

    channels = (
        "q1_drive",
        "q2_drive",
        "q4_drive",
        "q6_drive",
        "cr_c1_t2",
        "cr_c1_t4",
        "cr_c1_t6",
    )
    embedded = embed_c1t2_timeline(local_pair, channels)
    assert float(jnp.max(jnp.abs(embedded["cr_c1_t2"] - trusted_pair["cr_drive"]))) < 1e-12
    assert float(jnp.max(jnp.abs(embedded["q1_drive"] - trusted_pair["q1_drive"]))) < 1e-12
    assert float(jnp.max(jnp.abs(embedded["q2_drive"] - trusted_pair["q2_drive"]))) < 1e-12
    for name in ("q4_drive", "q6_drive", "cr_c1_t4", "cr_c1_t6"):
        assert float(jnp.max(jnp.abs(embedded[name]))) == 0.0

    print("WAVEFORM IDENTITY OK")


if __name__ == "__main__":
    main()
