#!/usr/bin/env bash
# tools/explain-score.sh — Debugger view for one surface's scores.
#
# For a given surface_id, print:
#   - the aggregated final scores (from agent_surfaces.jsonl)
#   - per-scorer partial scores (the inputs that produced the median)
#   - any evidence cited (from the merged evidence object)
#   - rubric anchors at 0/250/500/750/1000 for each dim (from SCORING-RUBRIC.md)
#
# Use this to answer "why did surface X get 580 on intent_inference?"
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/explain-score.sh <sibling> <surface_id> [--pass N]

Print everything we know about how this surface's scores were arrived at.

Args:
  <sibling>      Audit workspace root.
  <surface_id>   The surface to explain (e.g. flag__list__json).
  --pass N       Filter to a specific pass. Default: latest pass in file.

Output:
  Multi-section text block to stdout:
    1. Final aggregated row from agent_surfaces.jsonl
    2. Per-scorer partials from audit/partial/scores_*.jsonl
    3. Evidence cited (per dim, with file:line OR invocation+stdout/stderr)
    4. Rubric anchor reference (each dim's 0/250/500/750/1000 anchors,
       extracted from references/rubric/SCORING-RUBRIC.md if present)

Exit codes:
  0  Surface found and reported.
  1  Surface not found in agent_surfaces.jsonl.
  2  Bad args / missing manifest / missing files.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

SIBLING="$1"
if [ -z "${2:-}" ]; then
  usage >&2; exit 2
fi
SID="$2"; shift 2

PASS_FILTER=""
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 2; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 2 ;; esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pass) need_value "$1" "${2:-}"; PASS_FILTER="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

AUDIT="$SIBLING/audit"
SURFACES="$AUDIT/agent_surfaces.jsonl"
[ -f "$SURFACES" ] || { echo "agent_surfaces.jsonl not found at $SURFACES" >&2; exit 2; }

# Default to latest pass.
if [ -z "$PASS_FILTER" ]; then
  PASS_FILTER=$(jq -r '.pass // 1' "$SURFACES" | sort -n | tail -1)
fi

# Fetch the aggregated row.
row=$(jq -c --arg sid "$SID" --argjson pass "$PASS_FILTER" 'select(.surface_id == $sid and (.pass // 1) == $pass)' "$SURFACES" | head -1)
if [ -z "$row" ]; then
  echo "no row for surface_id=$SID at pass=$PASS_FILTER" >&2
  exit 1
fi

cat <<EOF
=== explain-score: $SID (pass $PASS_FILTER) ===

## 1. Final aggregated row
EOF
echo "$row" | jq '.'

cat <<EOF

## 2. Per-scorer partials (the inputs the median was computed from)
EOF
shopt -s nullglob
partials=( "$AUDIT/partial/scores_pass${PASS_FILTER}_${SID}_scorer"*.jsonl )
[ "${#partials[@]}" -eq 0 ] && [ "$PASS_FILTER" = "1" ] && partials=( "$AUDIT/partial/scores_${SID}_scorer"*.jsonl )
shopt -u nullglob

if [ "${#partials[@]}" -eq 0 ]; then
  echo "(no partials found in $AUDIT/partial/ — scorer files may have been archived)"
else
  for p in "${partials[@]}"; do
    echo
    echo "### $(basename "$p")"
    jq '.' "$p"
  done
fi

cat <<EOF

## 3. Evidence cited (per dim)
EOF
echo "$row" | jq -r '
  .evidence // {}
  | to_entries
  | if length == 0 then "(no evidence cited; all dim scores ≤ 700 by validator policy)" else
      map("### \(.key)\n\(.value | tojson)") | join("\n\n")
    end
'

# 4. Rubric anchors (best-effort: extract per-dim sections from SCORING-RUBRIC.md)
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUBRIC="$SKILL_DIR/references/rubric/SCORING-RUBRIC.md"
cat <<EOF

## 4. Rubric anchors (0 / 250 / 500 / 750 / 1000)
EOF
if [ -f "$RUBRIC" ]; then
  for dim in agent_intuitiveness agent_ergonomics agent_ease_of_use output_parseability error_pedagogy intent_inference safety_with_recovery determinism_and_reproducibility self_documentation composability regression_resistance; do
    echo
    echo "### $dim"
    score=$(echo "$row" | jq -r --arg d "$dim" '.scores[$d] // "?"')
    echo "  (this surface scored $score)"
    # Extract just the anchor lines for this dim from SCORING-RUBRIC.md
    awk -v dim="$dim" '
      tolower($0) ~ tolower("^## .*" dim) { found=1; print "  " $0; next }
      found && /^## / { found=0 }
      found && /^- \*\*[01]/    { print "  " $0 }
      found && /^- \*\*250/     { print "  " $0 }
      found && /^- \*\*500/     { print "  " $0 }
      found && /^- \*\*750/     { print "  " $0 }
      found && /^- \*\*1000/    { print "  " $0 }
    ' "$RUBRIC" | head -10
  done
else
  echo "  (rubric file not found at $RUBRIC — falling back to: see references/rubric/SCORING-RUBRIC.md)"
fi
