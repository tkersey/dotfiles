#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$script_dir/_python_with_yaml.sh" "$script_dir/doctor.py" --scope pullback-pushout "$@"
