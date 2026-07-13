#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "$0")" && pwd)"
"$dir/check_universalist.sh" "$@"
bash "$dir/check_pullback_pushout_mechanics.sh"
