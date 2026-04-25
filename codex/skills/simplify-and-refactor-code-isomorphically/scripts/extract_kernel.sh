#!/usr/bin/env bash
# extract_kernel.sh -- print the marker-delimited operational kernel.
#
# Usage:
#   extract_kernel.sh [kernel-file]
#
# Defaults to references/TRIANGULATED-KERNEL.md relative to this script.
# Prints the kernel block, including markers, to stdout. Read-only.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KERNEL_FILE="${1:-$SKILL_DIR/references/TRIANGULATED-KERNEL.md}"

START='<!-- KERNEL-START -->'
END='<!-- KERNEL-END -->'

if [[ ! -f "$KERNEL_FILE" ]]; then
  echo "error: kernel file not found: $KERNEL_FILE" >&2
  exit 2
fi

if ! grep -qxF "$START" "$KERNEL_FILE"; then
  echo "error: missing start marker: $START" >&2
  exit 3
fi

if ! grep -qxF "$END" "$KERNEL_FILE"; then
  echo "error: missing end marker: $END" >&2
  exit 4
fi

awk -v start="$START" -v end="$END" '
  $0 == start { in_block = 1 }
  in_block { print }
  $0 == end { found_end = 1; exit }
  END {
    if (!found_end) {
      exit 5
    }
  }
' "$KERNEL_FILE"
