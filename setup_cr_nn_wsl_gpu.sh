#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${1:-$ROOT/.venv-cr-nn}"

python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e "$ROOT"
python -m pip install --upgrade "jax[cuda12]"

python - <<'PY'
import jax
from HM.simulator.two_qubit_simulator.engine import two_q_pulse_sim_dynamiqs

print("backend:", jax.default_backend())
print("devices:", jax.devices())
print("x64:", jax.config.x64_enabled)
if jax.default_backend() != "gpu":
    raise SystemExit("JAX did not find the NVIDIA GPU")
PY

cat <<EOF

CR NN GPU environment is ready.

Activate it with:
  source "$VENV/bin/activate"

Recommended before a long run:
  export XLA_PYTHON_CLIENT_PREALLOCATE=false
  export JAX_COMPILATION_CACHE_DIR="\$HOME/.cache/jax-cr-nn"
  sudo sysctl -w vm.max_map_count=1048576
EOF
