#!/usr/bin/env bash
# scripts/diff_scorecards.sh — Compare two passes; emit uplift_diff.md + regression_alerts.md.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/diff_scorecards.sh <agent_surfaces.jsonl> <prior_pass> <new_pass>

Compares two passes' scores in agent_surfaces.jsonl and emits a markdown
uplift table to stdout, with per-dimension regression alerts (drops > 25 pts)
and hard-stop entries (overall drops > 50 pts).

Args:
  <agent_surfaces.jsonl>   Cumulative scoring file (must contain rows for
                           both passes; rows distinguished by .pass field).
  <prior_pass>             The earlier pass number.
  <new_pass>               The later pass number to diff against prior.

Output:
  Markdown to stdout. Redirect to <sibling>/audit/uplift_diff.md.

Exit codes:
  0  Success, no hard stops.
  1  Missing arguments (usage printed).
  2  Input file not found.
  3  At least one surface dropped > 50 pts overall (HARD STOP — investigate
     before continuing the loop).

Example:
  scripts/diff_scorecards.sh audit/agent_surfaces.jsonl 1 2 \
    > audit/uplift_diff.md
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

if [ -z "${2:-}" ] || [ -z "${3:-}" ]; then
  usage >&2
  exit 1
fi

JSONL="$1"
PRIOR="$2"
NEW="$3"

# Validate PRIOR/NEW are non-negative integers BEFORE we render the markdown
# header. Without this check, non-integer inputs (e.g. "abc"/"xyz", or a
# legacy manifest value of "null") produced a half-broken doc: the header
# rendered, then every per-surface row emitted a `jq: error ... cannot be
# parsed as a number` to stderr while the script continued with exit 0.
# The result looked like a successful run to a caller scripting on rc.
if ! [[ "$PRIOR" =~ ^[0-9]+$ ]]; then
  echo "<prior_pass> must be a non-negative integer (got '$PRIOR')" >&2
  exit 1
fi
if ! [[ "$NEW" =~ ^[0-9]+$ ]]; then
  echo "<new_pass> must be a non-negative integer (got '$NEW')" >&2
  exit 1
fi

if [ ! -f "$JSONL" ]; then
  echo "scorecard input not found: $JSONL" >&2
  exit 2
fi

cat <<EOF
# Pass $PRIOR → Pass $NEW Uplift Diff

Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Per-surface uplift

| surface_id | prior weighted | new weighted | Δ | improved dims | regressed dims |
|------------|----------------|--------------|---|---------------|-----------------|
EOF

# For each surface_id appearing in either pass, compute delta
SURFACES=$(jq -r '.surface_id' "$JSONL" | sort -u)

REGRESSIONS=()
HARD_STOPS=()
DELTAS=()
ADDED=()                # surfaces present only in NEW (new verb/flag/etc. introduced)
REMOVED=()              # surfaces present only in PRIOR (deprecated/dropped)

for sid in $SURFACES; do
  prior=$(jq -c --arg sid "$sid" --arg pass "$PRIOR" 'select(.surface_id == $sid and (.pass // 1) == ($pass | tonumber))' "$JSONL" | head -1)
  new=$(jq -c --arg sid "$sid" --arg pass "$NEW" 'select(.surface_id == $sid and (.pass // 1) == ($pass | tonumber))' "$JSONL" | head -1)

  if [ -z "$prior" ] && [ -n "$new" ]; then
    new_w=$(echo "$new" | jq '.weighted_score // 0')
    ADDED+=("$sid:$new_w")
    continue
  fi
  if [ -n "$prior" ] && [ -z "$new" ]; then
    prior_w=$(echo "$prior" | jq '.weighted_score // 0')
    REMOVED+=("$sid:$prior_w")
    continue
  fi
  if [ -z "$prior" ] || [ -z "$new" ]; then
    # Neither pass had this surface — shouldn't happen given the union loop, skip defensively.
    continue
  fi

  prior_w=$(echo "$prior" | jq '.weighted_score // 0')
  new_w=$(echo "$new" | jq '.weighted_score // 0')
  delta=$(( new_w - prior_w ))

  improved_dims=""
  regressed_dims=""
  for dim in agent_intuitiveness agent_ergonomics agent_ease_of_use output_parseability error_pedagogy intent_inference safety_with_recovery determinism_and_reproducibility self_documentation composability regression_resistance; do
    p=$(echo "$prior" | jq ".scores.\"$dim\" // 0")
    n=$(echo "$new" | jq ".scores.\"$dim\" // 0")
    d=$(( n - p ))
    if [ "$d" -gt 25 ]; then
      improved_dims="${improved_dims}${dim} (+${d}); "
    elif [ "$d" -lt -25 ]; then
      regressed_dims="${regressed_dims}${dim} (${d}); "
      REGRESSIONS+=("$sid:$dim:$p:$n:$d")
    fi
  done
  [ -z "$improved_dims" ] && improved_dims="(none)"
  [ -z "$regressed_dims" ] && regressed_dims="(none)"

  printf '| %s | %s | %s | %+d | %s | %s |\n' "$sid" "$prior_w" "$new_w" "$delta" "${improved_dims%; }" "${regressed_dims%; }"

  if [ "$delta" -lt -50 ]; then
    HARD_STOPS+=("$sid:$prior_w:$new_w:$delta")
  fi

  DELTAS+=("$delta")
done

COUNT=${#DELTAS[@]}
if [ "$COUNT" -gt 0 ]; then
  # Compute real median (not mean): sort, pick middle value
  sorted=$(printf '%s\n' "${DELTAS[@]}" | sort -n)
  if [ $((COUNT % 2)) -eq 1 ]; then
    MEDIAN_DELTA=$(echo "$sorted" | sed -n "$((COUNT / 2 + 1))p")
  else
    a=$(echo "$sorted" | sed -n "$((COUNT / 2))p")
    b=$(echo "$sorted" | sed -n "$((COUNT / 2 + 1))p")
    MEDIAN_DELTA=$(( (a + b) / 2 ))
  fi
  TOTAL_DELTA=0
  for d in "${DELTAS[@]}"; do TOTAL_DELTA=$((TOTAL_DELTA + d)); done
  MEAN_DELTA=$(( TOTAL_DELTA / COUNT ))
  echo
  echo "**Median uplift across $COUNT scored surfaces:** $MEDIAN_DELTA pts"
  echo "**Mean uplift across $COUNT scored surfaces:** $MEAN_DELTA pts"
fi

if [ ${#ADDED[@]} -gt 0 ]; then
  echo
  echo "## Added surfaces (present in pass $NEW only)"
  echo
  echo "| surface_id | weighted_score |"
  echo "|------------|----------------|"
  for a in "${ADDED[@]}"; do
    IFS=':' read -r sid w <<< "$a"
    printf '| %s | %s |\n' "$sid" "$w"
  done
fi

if [ ${#REMOVED[@]} -gt 0 ]; then
  echo
  echo "## Removed surfaces (present in pass $PRIOR only — possibly deprecated)"
  echo
  echo "| surface_id | prior_weighted_score |"
  echo "|------------|----------------------|"
  for r in "${REMOVED[@]}"; do
    IFS=':' read -r sid w <<< "$r"
    printf '| %s | %s |\n' "$sid" "$w"
  done
fi

if [ ${#REGRESSIONS[@]} -gt 0 ]; then
  echo
  echo "## Regressions (per-dim drop > 25 pts)"
  echo
  echo "| surface_id | dim | prior | new | Δ |"
  echo "|------------|-----|-------|-----|---|"
  for r in "${REGRESSIONS[@]}"; do
    IFS=':' read -r sid dim p n d <<< "$r"
    printf '| %s | %s | %s | %s | %d |\n' "$sid" "$dim" "$p" "$n" "$d"
  done
fi

# Hard-stop check (drop > 50 pts overall)
if [ ${#HARD_STOPS[@]} -gt 0 ]; then
  echo
  echo "## ⚠️  HARD STOPS (drop > 50 pts overall)"
  echo
  echo "| surface_id | prior weighted | new weighted | Δ |"
  echo "|------------|----------------|--------------|---|"
  for h in "${HARD_STOPS[@]}"; do
    IFS=':' read -r sid pw nw d <<< "$h"
    printf '| %s | %s | %s | %d |\n' "$sid" "$pw" "$nw" "$d"
  done
  echo
  echo "Investigate root cause before continuing. See methodology/TROUBLESHOOTING.md § Phase 6."
  exit 3
fi

exit 0
