#!/usr/bin/env bash
# scripts/estimate.sh — Pre-pass cost/time estimator.
#
# Runs a quick inventory dry-run against the target CLI, projects the full-pass
# subagent count, wall-time, and Anthropic API spend. Prints a 5-line summary
# the user confirms before scaffolding. Without this estimate, a user can
# trigger a pass that spawns thousands of subagents (e.g. gh has ~1900 surfaces
# × 2 scorers = 3800 subagents) without realizing the budget cost.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/estimate.sh <tool-binary> [--mode audit-only|full|mini]
                                         [--depth N]
                                         [--tokens-per-subagent N]
                                         [--cost-per-million N]

Estimate the wall-time and API spend of a full-pass agent-ergonomics audit
against <tool-binary>, BEFORE scaffolding anything.

Args:
  <tool-binary>             Path or PATH-resolvable binary name.
  --mode MODE               audit-only | full | mini. Default: full.
                            Affects which phases the estimate covers:
                              mini       = Phase 1+2 only
                              audit-only = Phase 1+2+3+4 (no apply, no re-score)
                              full       = all 10 phases
  --depth N                 Inventory recursion depth. Default: 2.
  --tokens-per-subagent N   Mean token budget per subagent invocation. Default:
                            8000 (covers prompt + response).
  --cost-per-million N      USD per million input+output tokens (mixed). Default:
                            7.50 (Claude Sonnet 4.x mid-2026 pricing approx).

Output:
  5-line summary on stdout, one per category. Human-readable, no JSON.

Exit codes:
  0  Estimate produced.
  1  Missing args or tool unreachable.
EOF
}

MODE="full"
DEPTH=2
TOKENS_PER_SUBAGENT=8000
COST_PER_MILLION="7.50"

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

TOOL="$1"; shift

die() {
  echo "$*" >&2
  exit 1
}
need_value() {
  [ -n "${2:-}" ] || die "$1 requires a value"
  case "$2" in --*) die "$1 requires a value, got option-like token: $2" ;; esac
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)               need_value "$1" "${2:-}"; MODE="$2"; shift 2 ;;
    --depth)              need_value "$1" "${2:-}"; DEPTH="$2"; shift 2 ;;
    --tokens-per-subagent) need_value "$1" "${2:-}"; TOKENS_PER_SUBAGENT="$2"; shift 2 ;;
    --cost-per-million)   need_value "$1" "${2:-}"; COST_PER_MILLION="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

case "$DEPTH" in ''|*[!0-9]*) die "bad --depth: $DEPTH (expected positive integer)" ;; esac
[ "$DEPTH" -gt 0 ] || die "bad --depth: $DEPTH (expected positive integer)"
case "$TOKENS_PER_SUBAGENT" in
  ''|*[!0-9]*) die "bad --tokens-per-subagent: $TOKENS_PER_SUBAGENT (expected positive integer)" ;;
esac
[ "$TOKENS_PER_SUBAGENT" -gt 0 ] || die "bad --tokens-per-subagent: $TOKENS_PER_SUBAGENT (expected positive integer)"
if ! awk -v c="$COST_PER_MILLION" 'BEGIN { exit !(c ~ /^[0-9]+([.][0-9]+)?$/) }'; then
  die "bad --cost-per-million: $COST_PER_MILLION (expected non-negative number)"
fi

if ! command -v "$TOOL" >/dev/null 2>&1 && [ ! -x "$TOOL" ]; then
  echo "tool not found: $TOOL" >&2
  exit 1
fi

# Quick inventory dry-run (suppress stderr so the estimate prints clean).
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SURFACES=$(/usr/bin/timeout 180 bash "$SKILL_DIR/scripts/inventory_surfaces.sh" "$TOOL" --depth "$DEPTH" 2>/dev/null | /usr/bin/wc -l)

if [ "$SURFACES" -lt 1 ]; then
  echo "estimate: inventory dry-run produced 0 surfaces — tool may not respond to --help" >&2
  exit 1
fi

# Subagent multipliers per mode (rough; calibrated against jq+gh smokes):
#   Phase 1: surfaces / 10 inventorist subagents (one per subtree) — call it N/10
#   Phase 2: 2 scorers per surface (sometimes + tiebreaker) — call it 2.2 × surfaces
#   Phase 3: 2 stresser subagents (naive + savvy) — fixed cost 2
#   Phase 4: 1 recommender per below-quartile surface (~25% of surfaces) — surfaces × 0.25
#   Phase 5: 1 applier per recommendation (~50% of recs) — surfaces × 0.25 × 0.5
#   Phase 6: re-scorer per applied surface — surfaces × 0.25 × 0.5
#   Phase 7: 3 fresh-eyes rounds × ~2 = 6
#   Phase 8: light, fold into Phase 5
#   Phase 9: 5–10 task simulators — fixed 8
#   Phase 10: 2 (handoff + benchmark) — fixed 2
case "$MODE" in
  mini)
    SUBAGENTS=$(( SURFACES / 10 + (SURFACES * 22 / 10) ))
    PHASES_RUN="1, 2"
    ;;
  audit-only)
    SUBAGENTS=$(( SURFACES / 10 + (SURFACES * 22 / 10) + 2 + (SURFACES * 25 / 100) ))
    PHASES_RUN="1, 2, 3, 4"
    ;;
  full)
    SUBAGENTS=$(( SURFACES / 10 + (SURFACES * 22 / 10) + 2 + (SURFACES * 25 / 100) + (SURFACES * 25 / 200) + (SURFACES * 25 / 200) + 6 + 8 + 2 ))
    PHASES_RUN="all 10 phases"
    ;;
  *) echo "invalid mode: $MODE (use mini|audit-only|full)" >&2; exit 1 ;;
esac

# Token & cost projections.
TOKENS=$(( SUBAGENTS * TOKENS_PER_SUBAGENT ))
TOKENS_M=$(printf '%.2f' "$(echo "$TOKENS / 1000000" | /usr/bin/bc -l)")
COST_USD=$(printf '%.2f' "$(echo "$TOKENS_M * $COST_PER_MILLION" | /usr/bin/bc -l)")

# Wall-time projection: ~30s per subagent (parallel × ~6 = effective 5s),
# plus phase overhead. Mini ~5min, audit-only ~30min, full ~2h on 100-surface tool.
WALLTIME_MIN=$(( SUBAGENTS * 5 / 60 ))
[ "$WALLTIME_MIN" -lt 5 ] && WALLTIME_MIN=5

cat <<EOF
estimate (mode: $MODE; phases: $PHASES_RUN)
  surfaces inventoried (depth $DEPTH): $SURFACES
  projected subagent invocations:      $SUBAGENTS
  projected token spend:               ~${TOKENS_M}M (\$${COST_USD} at \$${COST_PER_MILLION}/M)
  projected wall-time:                 ~${WALLTIME_MIN} min (with default parallelism)
  override: pass --mode mini for the smallest viable audit (Phase 1+2 only)
EOF
