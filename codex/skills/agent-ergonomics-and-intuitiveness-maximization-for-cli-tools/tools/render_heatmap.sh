#!/usr/bin/env bash
# tools/render_heatmap.sh — Convenience wrapper for scripts/render_heatmap.sh.
# Auto-detects current pass; writes audit/heatmap.svg.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/render_heatmap.sh [sibling-dir] [pass]

Smart wrapper for scripts/render_heatmap.sh. Auto-detects the audit
workspace (defaults to $PWD) and reads .current_pass from
audit/manifest.json, then writes audit/heatmap.svg.

Args:
  [sibling-dir]   Audit workspace root. Defaults to $PWD.
  [pass]          Pass number override. Defaults to .current_pass.

Run --help on the underlying script for full options:
  scripts/render_heatmap.sh --help

Example:
  cd /path/to/__audit && tools/render_heatmap.sh
  tools/render_heatmap.sh /path/to/__audit 2
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
esac

SIBLING="${1:-$PWD}"
PASS_OVERRIDE="${2:-}"

if [ -f "$SIBLING/audit/manifest.json" ]; then
  AUDIT="$SIBLING/audit"
elif [ -f "audit/manifest.json" ]; then
  AUDIT="audit"
else
  echo "no audit/manifest.json; pass <sibling-dir> as arg" >&2
  echo "(run with --help for usage)" >&2
  exit 2
fi

PASS="${PASS_OVERRIDE:-$(jq -r '.current_pass // 1' "$AUDIT/manifest.json")}"
# Validate integer shape before passing to the underlying script. A legacy
# or buggy manifest could store .current_pass as a string ("null", "abc",
# ""), and the downstream script would either bomb out cryptically or
# write to a file path containing the literal junk. Catch it here.
if ! [[ "$PASS" =~ ^[0-9]+$ ]]; then
  echo "manifest.json .current_pass is not a non-negative integer (got '$PASS')" >&2
  exit 2
fi
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

OUT="$AUDIT/heatmap.svg"
"$SKILL_DIR/scripts/render_heatmap.sh" "$AUDIT/agent_surfaces.jsonl" --pass "$PASS" > "$OUT"
echo "heatmap written: $OUT (pass $PASS)"
