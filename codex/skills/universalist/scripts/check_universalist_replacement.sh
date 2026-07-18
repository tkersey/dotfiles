#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "$0")" && pwd)"
"$dir/check_universalist.sh" "$@"
bash "$dir/check_pullback_pushout_mechanics.sh"
bash "$dir/check_comonadic_spatiality.sh"
bash "$dir/check_day_convolution.sh"
bash "$dir/check_tambara_modules.sh"
