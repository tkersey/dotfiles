#!/usr/bin/env bash
# tools/diff_scorecards.sh — Convenience wrapper for scripts/diff_scorecards.sh.
# Auto-detects current sibling and pass numbers from audit/manifest.json.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/diff_scorecards.sh [sibling-dir]

Smart wrapper for scripts/diff_scorecards.sh. Auto-detects the audit
workspace (defaults to $PWD or its audit/ subdir) and reads .current_pass
from audit/manifest.json to diff (current_pass - 1) → current_pass.

Args:
  [sibling-dir]   Audit workspace root. Defaults to $PWD; falls back to
                  searching for ./audit/manifest.json.

Run --help on the underlying script for full options:
  scripts/diff_scorecards.sh --help

Example:
  cd /path/to/__audit && tools/diff_scorecards.sh
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
esac

SIBLING="${1:-$PWD}"
if [ -f "$SIBLING/audit/manifest.json" ]; then
  AUDIT="$SIBLING/audit"
elif [ -f "audit/manifest.json" ]; then
  AUDIT="audit"
  SIBLING="$PWD"
else
  echo "no audit/manifest.json found; pass <sibling-dir> as argument" >&2
  echo "(run with --help for usage)" >&2
  exit 2
fi

CURRENT=$(jq -r '.current_pass // 1' "$AUDIT/manifest.json")
# `jq -r '.current_pass // 1'` only substitutes for actual JSON null/missing.
# A legacy or buggy emitter could store the field as a non-numeric string
# (e.g. "null", "abc", or empty after a typo). Bash's arithmetic substitution
# then tries to dereference that as a variable name under `set -u`, crashing
# with the confusing "unbound variable: $abc" instead of a clear schema error.
# Verify integer shape first.
if ! [[ "$CURRENT" =~ ^[0-9]+$ ]]; then
  echo "manifest.json .current_pass is not a non-negative integer (got '$CURRENT')" >&2
  exit 2
fi
PRIOR=$((CURRENT - 1))

if [ "$PRIOR" -lt 1 ]; then
  echo "no prior pass to diff against (current pass: $CURRENT)" >&2
  exit 2
fi

# Find the scripts/diff_scorecards.sh
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$SKILL_DIR/scripts/diff_scorecards.sh" "$AUDIT/agent_surfaces.jsonl" "$PRIOR" "$CURRENT"
