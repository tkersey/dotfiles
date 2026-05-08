#!/usr/bin/env bash
# tools/explain-rec.sh — Debugger view for one recommendation.
#
# Counterpart to explain-score.sh. For a given recommendation_id, print:
#   - the rec body (title, summary, diff_sketch, expected_uplift, risk)
#   - the surfaces it covers and their CURRENT scores per touched dim
#   - the applied_changes record (commit_sha, files_changed) if applied
#   - the regression test path + last run result if discoverable
#   - the anchor / counter-example refs cited
#
# Use this to answer "what is rec R-007 actually doing and is it landed?"
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/explain-rec.sh <sibling> <recommendation_id> [--pass N]

Print everything we know about a recommendation: definition, covered surfaces
+ their CURRENT scores on touched dims, applied-status, regression test info.

Args:
  <sibling>             Audit workspace root.
  <recommendation_id>   The rec to explain (e.g. R-007).
  --pass N              Filter scores to a specific pass. Default: latest.

Output:
  Multi-section text block to stdout:
    1. Recommendation body
    2. Covered surfaces × dim scores (table, current pass)
    3. Applied-status (commit_sha, files, applied_at) or "not yet applied"
    4. Regression test path + last-run result (if test_path exists)
    5. Anchor / counter-example references cited

Exit codes:
  0  Recommendation found and reported.
  1  Recommendation not found in recommendations.jsonl.
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
RID="$2"; shift 2

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
RECS="$AUDIT/recommendations.jsonl"
APPLIED="$AUDIT/applied_changes.jsonl"
SURFACES="$AUDIT/agent_surfaces.jsonl"

[ -f "$RECS" ] || { echo "recommendations.jsonl not found at $RECS" >&2; exit 2; }

rec=$(jq -c --arg rid "$RID" 'select(.recommendation_id == $rid)' "$RECS" | head -1)
if [ -z "$rec" ]; then
  echo "no row for recommendation_id=$RID" >&2
  echo "  (available IDs:)" >&2
  jq -r '.recommendation_id' "$RECS" 2>/dev/null | head -10 >&2
  exit 1
fi

cat <<EOF
=== explain-rec: $RID ===

## 1. Recommendation body
EOF
echo "$rec" | jq '.'

# 2. Covered surfaces × dim scores
cat <<EOF

## 2. Covered surfaces × dims this rec targets
EOF
covered_sids=$(echo "$rec" | jq -r '.surface_ids // [] | .[]')
touched_dims=$(echo "$rec" | jq -r '.expected_uplift_per_dim // {} | keys | .[]')

if [ -z "$covered_sids" ]; then
  echo "  (rec lists no surface_ids — likely a cross-cutting/process rec)"
elif [ ! -f "$SURFACES" ]; then
  echo "  (agent_surfaces.jsonl not found at $SURFACES; cannot show scores)"
elif [ -z "$touched_dims" ]; then
  echo "  (rec lists no expected_uplift_per_dim; cannot show targeted dims)"
else
  if [ -z "$PASS_FILTER" ]; then
    PASS_FILTER=$(jq -r '.pass // 1' "$SURFACES" | sort -n | tail -1)
  fi
  # Header row.
  hdr="| surface_id |"
  while IFS= read -r d; do
    hdr+=" $d |"
  done <<< "$touched_dims"
  hdr+=" weighted |"
  echo "$hdr"

  sep="|------------|"
  while IFS= read -r _; do sep+="------|"; done <<< "$touched_dims"
  sep+="----------|"
  echo "$sep"

  while IFS= read -r sid; do
    [ -z "$sid" ] && continue
    row=$(jq -c --arg s "$sid" --argjson p "$PASS_FILTER" \
      'select(.surface_id == $s and (.pass // 1) == $p)' "$SURFACES" | head -1)
    if [ -z "$row" ]; then
      out="| $sid |"
      while IFS= read -r _; do out+=" — |"; done <<< "$touched_dims"
      out+=" — |"
      echo "$out"
      continue
    fi
    out="| $sid |"
    while IFS= read -r d; do
      v=$(echo "$row" | jq -r --arg d "$d" '.scores[$d] // "—"')
      out+=" $v |"
    done <<< "$touched_dims"
    w=$(echo "$row" | jq -r '.weighted_score // "—"')
    out+=" $w |"
    echo "$out"
  done <<< "$covered_sids"
fi

# 3. Applied-status
cat <<EOF

## 3. Applied-status
EOF
if [ -f "$APPLIED" ]; then
  applied_row=$(jq -c --arg rid "$RID" 'select(.recommendation_id == $rid)' "$APPLIED" | head -1)
  if [ -n "$applied_row" ]; then
    echo "$applied_row" | jq '{recommendation_id, commit_sha, applied_at, files_changed: (.files_changed // [] | map(.path)), test_path}'
  else
    deferred=$(echo "$rec" | jq -r '.deferred_reason // ""')
    if [ -n "$deferred" ] && [ "$deferred" != "null" ]; then
      echo "  status: DEFERRED — $deferred"
    else
      echo "  status: NOT YET APPLIED"
    fi
  fi
else
  echo "  (applied_changes.jsonl not found — nothing applied yet)"
fi

# 4. Regression test status
cat <<EOF

## 4. Regression test
EOF
test_path=""
if [ -n "${applied_row:-}" ]; then
  test_path=$(echo "$applied_row" | jq -r '.test_path // ""')
fi
if [ -z "$test_path" ]; then
  test_path=$(echo "$rec" | jq -r '.test_path // ""')
fi
if [ -n "$test_path" ] && [ "$test_path" != "null" ]; then
  full="$SIBLING/$test_path"
  if [ -f "$full" ]; then
    echo "  test: $test_path (exists)"
    if /usr/bin/timeout 30 bash "$full" >/dev/null 2>&1; then
      echo "  result: PASSING"
    else
      echo "  result: FAILING"
    fi
  else
    echo "  test: $test_path (FILE MISSING — was the rec rolled back?)"
  fi
else
  echo "  (no test_path declared)"
fi

# 5. Anchors / counter-examples
cat <<EOF

## 5. Anchors / counter-examples cited
EOF
echo "$rec" | jq -r '
  [
    if (.anchor_quote // "") != "" then "  anchor_quote: \(.anchor_quote)" else empty end,
    if (.anchor_pattern // "") != "" then "  anchor_pattern: \(.anchor_pattern)" else empty end,
    if (.counter_example // "") != "" then "  counter_example: \(.counter_example)" else empty end,
    if (.operators_applied // []) != [] then "  operators: \((.operators_applied // []) | join(", "))" else empty end,
    if (.triangulation // null) != null then "  triangulation: \(.triangulation)" else empty end
  ] | if length == 0 then "  (none cited — rec is freestanding)" else join("\n") end
'
