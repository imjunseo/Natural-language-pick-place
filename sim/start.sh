#!/usr/bin/env bash
set -euo pipefail
SIM_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export GZ_SIM_RESOURCE_PATH="$SIM_ROOT/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
exec gz sim -r "$SIM_ROOT/chess_world.sdf"
