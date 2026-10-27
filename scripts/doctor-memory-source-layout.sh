#!/usr/bin/env sh
set -eu

# Resolve the checked-in tool, not the target workspace\'s Git checkout.
script_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec uv run python \
  "$script_root/agents/skills/memory-source-notes/scripts/memory_source_layout.py" \
  doctor "$@"
