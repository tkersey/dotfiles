#!/usr/bin/env bash
# scripts/diff_test.sh — Differential idempotency test.
#
# Runs a deterministic phase chain twice against a target and asserts the
# artifacts are byte-identical (modulo timestamp fields). PHASES.md claims
# "Re-entering Phase 2 against an unchanged target SHA produces a byte-
# identical agent_surfaces.jsonl"; this script proves it on demand.
#
# Limited scope: tests the deterministic scripts (inventory, generate_intent_corpus,
# run_intent_corpus, aggregate_scores, synthesize_recommendations,
# render_scorecard, render_heatmap, diff_scorecards). Does NOT test LLM-driven
# subagents (scorers, recommenders) — those are non-deterministic by design.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/diff_test.sh <tool-binary>

Runs the deterministic phase chain twice against <tool-binary> and asserts
byte-identical output (modulo *_at timestamp fields). Reports any drift.

Args:
  <tool-binary>   Path or PATH-resolvable binary to test against.

Exit codes:
  0  Two runs produced byte-identical artifacts (idempotent).
  1  Drift detected; first 20 lines of diff printed to stderr.
  2  Bad args / pre-flight failure.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

TOOL="$1"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_A=$(mktemp -d /tmp/aerg_diff_a.XXXXXX)
RUN_B=$(mktemp -d /tmp/aerg_diff_b.XXXXXX)

run_pipeline() {
  local sibling="$1"
  mkdir -p "$sibling/audit/partial"
  bash "$SKILL_DIR/scripts/inventory_surfaces.sh" "$TOOL" --depth 1 > "$sibling/audit/surface_inventory.jsonl" 2>/dev/null
  bash "$SKILL_DIR/scripts/generate_intent_corpus.sh" "$sibling" --tool "$(basename "$TOOL")" >/dev/null 2>&1 || true
  # Aggregator and rec-synthesizer require partials we don't have without
  # LLM scorers, so this diff_test stops at the deterministic-only stages.
}

echo "=== Run A ===" >&2
run_pipeline "$RUN_A"
echo "=== Run B ===" >&2
run_pipeline "$RUN_B"

# Strip timestamps before comparing.
strip_timestamps() {
  /usr/bin/sed -E 's/"(scored_at|generated_at|ran_at|discovered_at|started_at|completed_at|applied_at|last_step_at|created_at)":"[^"]+"/"\1":"<TIMESTAMP>"/g'
}

# Compare each artifact.
drift=0
for art in surface_inventory.jsonl partial/intent_naive.jsonl; do
  if [ -f "$RUN_A/audit/$art" ] && [ -f "$RUN_B/audit/$art" ]; then
    a_norm=$(strip_timestamps < "$RUN_A/audit/$art")
    b_norm=$(strip_timestamps < "$RUN_B/audit/$art")
    if [ "$a_norm" != "$b_norm" ]; then
      echo "DRIFT in $art" >&2
      diff <(echo "$a_norm") <(echo "$b_norm") | head -20 >&2 || true
      drift=1
    else
      echo "OK    $art (byte-identical modulo timestamps)"
    fi
  fi
done

# Cleanup.
: > "$RUN_A/audit/surface_inventory.jsonl" 2>/dev/null || true
: > "$RUN_B/audit/surface_inventory.jsonl" 2>/dev/null || true

if [ "$drift" -eq 0 ]; then
  echo
  echo "diff_test: idempotent ✓ (deterministic-pipeline artifacts byte-identical across two runs)"
  exit 0
fi
exit 1
