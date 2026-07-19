#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
if python3 -c 'import yaml' >/dev/null 2>&1; then
  exec python3 "$@"
fi
if command -v uv >/dev/null 2>&1; then
  exec uv run --with pyyaml -- python3 "$@"
fi
printf '%s\n' 'Universalist requires Python 3 and either PyYAML or uv.' >&2
printf '%s\n' 'Install PyYAML, or install uv and rerun the command.' >&2
exit 2
