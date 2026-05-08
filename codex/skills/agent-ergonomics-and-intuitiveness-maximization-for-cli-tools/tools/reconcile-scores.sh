#!/usr/bin/env bash
# tools/reconcile-scores.sh — Detect scorer disagreements and emit action plan.
#
# Reconciliation policy (from references/methodology/RECONCILIATION-POLICY.md):
#   - per-dim spread < 100: agreement; take median of A+B.
#   - per-dim spread 100-199: noted but accepted; take median.
#   - per-dim spread 200-299: WARN; record disagreement_band=high; still median.
#   - per-dim spread ≥ 300: TIEBREAKER REQUIRED. Spawn `agent-ergo-scorer-tiebreaker`
#     subagent with both A's and B's evidence visible (NOT raw scores) to break.
#   - any-dim spread ≥ 500: STOP — escalate to user. Rubric is mis-anchored.
#
# This script reads partials, computes per-(surface, dim) spreads, and emits:
#   1. A list of (surface_id, dim, A_score, B_score, spread, action) rows.
#   2. A list of "tiebreaker_needed" surface_ids (any dim ≥ 300).
#   3. A list of "user_escalation_needed" surfaces (any dim ≥ 500).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/reconcile-scores.sh <sibling> [--pass N] [--format md|json]

Read all per-scorer partials at <sibling>/audit/partial/scores_pass<N>_*_scorer*.jsonl,
compute per-dim spreads, emit reconciliation actions per the policy.

Args:
  <sibling>     Audit workspace root.
  --pass N      Filter to a specific pass (default: latest pass).
  --format F    'md' (default) human-readable; 'json' machine-readable.

Output:
  Markdown report or JSONL stream:
    {surface_id, dim, scorer_A, scorer_B, spread, action}
    action ∈ {accept, accept_warn, tiebreaker, escalate}

Exit codes:
  0  No tiebreakers / escalations needed.
  1  Tiebreakers needed (parent must spawn).
  2  User escalation needed (≥ 500-pt spread on some dim).
  3  Bad args / no partials.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 3 ;;
esac

SIBLING="$1"; shift
PASS=""
FORMAT=md
while [ "$#" -gt 0 ]; do
  case "$1" in
    --pass)
      [ -n "${2:-}" ] || { echo "--pass requires a value" >&2; exit 3; }
      case "$2" in --*) echo "--pass requires a value, got option-like token: $2" >&2; exit 3 ;; esac
      PASS="$2"; shift 2
      ;;
    --format)
      [ -n "${2:-}" ] || { echo "--format requires a value" >&2; exit 3; }
      case "$2" in --*) echo "--format requires a value, got option-like token: $2" >&2; exit 3 ;; esac
      FORMAT="$2"; shift 2
      ;;
    *) echo "unknown arg: $1" >&2; exit 3 ;;
  esac
done

case "$FORMAT" in md|json) ;; *) echo "bad --format: $FORMAT" >&2; exit 3 ;; esac

PARTIAL="$SIBLING/audit/partial"
[ -d "$PARTIAL" ] || { echo "no partial dir: $PARTIAL" >&2; exit 3; }

# Determine pass.
if [ -z "$PASS" ]; then
  PASS=$(find "$PARTIAL" -name "scores_pass*_*_scorer*.jsonl" 2>/dev/null \
         | sed -n 's/.*scores_pass\([0-9]*\)_.*/\1/p' \
         | sort -nu | tail -1)
  [ -z "$PASS" ] && PASS=1
fi

DIMS=(agent_intuitiveness agent_ergonomics agent_ease_of_use \
      output_parseability error_pedagogy intent_inference \
      safety_with_recovery determinism_and_reproducibility \
      self_documentation composability regression_resistance)

# Group partials by surface_id.
sids=$(find "$PARTIAL" -name "scores_pass${PASS}_*_scorer*.jsonl" 2>/dev/null \
       | sed -n "s|.*scores_pass${PASS}_\(.*\)_scorer.*\.jsonl$|\1|p" \
       | sort -u)
[ -z "$sids" ] && { echo "no partials for pass $PASS" >&2; exit 3; }

if [ "$FORMAT" = md ]; then
  echo "# Score Reconciliation Report"
  echo
  echo "_Pass: ${PASS}_"
  echo
  echo "## Per-(surface, dim) actions"
  echo
  echo "| surface | dim | A | B | spread | action |"
  echo "|---------|-----|---|---|--------|--------|"
fi

tiebreakers=0
escalations=0
warns=0

while IFS= read -r sid; do
  [ -z "$sid" ] && continue
  files=$(find "$PARTIAL" -name "scores_pass${PASS}_${sid}_scorer*.jsonl" 2>/dev/null)
  n_files=$(echo "$files" | grep -c .)
  [ "$n_files" -lt 2 ] && continue
  # Identify scorer A and scorer B for spread calculation. If a tiebreaker
  # partial exists, we'll consult it to decide if the dispute is already
  # resolved. The aggregator handles the 3-way median elsewhere; this
  # script's job is reporting which (surface, dim) pairs still need action.
  files_sorted=$(echo "$files" | sort)
  fa=""
  fb=""
  ftie=""
  while IFS= read -r f; do
    case "$f" in
      *_scorertiebreaker.jsonl) ftie="$f" ;;
      *)
        if [ -z "$fa" ]; then
          fa="$f"
        elif [ -z "$fb" ]; then
          fb="$f"
        fi
        ;;
    esac
  done <<< "$files_sorted"
  [ -z "$fa" ] || [ -z "$fb" ] && continue
  for dim in "${DIMS[@]}"; do
    a=$(jq -r --arg d "$dim" '.scores[$d] // empty' "$fa")
    b=$(jq -r --arg d "$dim" '.scores[$d] // empty' "$fb")
    [ -z "$a" ] && continue
    [ -z "$b" ] && continue
    diff=$(( a > b ? a - b : b - a ))
    # Determine action. If a tiebreaker partial exists with a non-null
    # score for THIS dim, the dispute has already been resolved — the
    # action is "tiebroken" rather than "tiebreaker" (which means "needed").
    tie_score=""
    if [ -n "$ftie" ]; then
      tie_score=$(jq -r --arg d "$dim" '
        .scores[$d] // empty
        | select(type == "number" and (floor == .))
      ' "$ftie" 2>/dev/null || true)
    fi
    if [ "$diff" -ge 500 ]; then
      action="escalate"
      escalations=$((escalations + 1))
    elif [ "$diff" -ge 300 ]; then
      if [ -n "$tie_score" ]; then
        action="tiebroken"
        # Tiebroken disputes are resolved — not counted toward needs-action.
      else
        action="tiebreaker"
        tiebreakers=$((tiebreakers + 1))
      fi
    elif [ "$diff" -ge 200 ]; then
      action="accept_warn"
      warns=$((warns + 1))
    else
      action="accept"
    fi
    case "$FORMAT" in
      md)
        if [ "$action" != "accept" ]; then
          printf '| %s | %s | %s | %s | %s | %s |\n' "$sid" "$dim" "$a" "$b" "$diff" "$action"
        fi
        ;;
      json)
        jq -nc --arg s "$sid" --arg d "$dim" --argjson a "$a" --argjson b "$b" \
          --argjson sp "$diff" --arg ac "$action" \
          '{surface_id: $s, dim: $d, scorer_A: $a, scorer_B: $b, spread: $sp, action: $ac}'
        ;;
    esac
  done
done <<< "$sids"

if [ "$FORMAT" = md ]; then
  echo
  echo "## Summary"
  echo "- accept_warn (200-299): $warns"
  echo "- tiebreaker (300-499): $tiebreakers"
  echo "- escalate (≥ 500): $escalations"
  echo
  if [ "$escalations" -gt 0 ]; then
    echo "❗ ESCALATE TO USER — rubric anchors are mis-tuned."
  elif [ "$tiebreakers" -gt 0 ]; then
    echo "⚠️  $tiebreakers (surface, dim) pair(s) need tiebreaker subagent."
  else
    echo "✅ All disagreements within accept thresholds."
  fi
fi

# Exit code: 0 = clean, 1 = tiebreaker, 2 = escalate.
if [ "$escalations" -gt 0 ]; then exit 2; fi
if [ "$tiebreakers" -gt 0 ]; then exit 1; fi
exit 0
