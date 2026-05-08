#!/usr/bin/env bash
# scripts/score_surface.sh — Stub-score one surface as scaffolding.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/score_surface.sh <tool> <surface_id>

STUB SCRIPT — emits a placeholder JSONL line in the per-scorer **partial**
schema (matching subagents/scorer.md, NOT the post-aggregation final
agent_surfaces.jsonl schema). All 11 dimension scores are 500 (mid-rubric).
Use this script only to seed a partial file for plumbing tests of the
aggregator + validators; the real Phase 2 scoring is LLM-driven via
subagents/scorer.md, and the final agent_surfaces.jsonl row is produced by
scripts/aggregate_scores.sh from ≥ 2 such partials.

Args:
  <tool>          Path or PATH-resolvable name of the CLI (purely advisory;
                  this stub does not invoke the tool).
  <surface_id>    The surface_id to stub-score.

Output:
  One JSONL record on stdout (partial schema; no `pass`, `score_confidence`,
  or `scored_at` — those are added by the aggregator).

Example:
  # Seed two partials so the aggregator has something to merge:
  scripts/score_surface.sh /usr/bin/gh verb__list \
    > <SIBLING>/audit/partial/scores_pass1_verb__list_scorerA.jsonl
  scripts/score_surface.sh /usr/bin/gh verb__list \
    > <SIBLING>/audit/partial/scores_pass1_verb__list_scorerB.jsonl
  scripts/aggregate_scores.sh <SIBLING> verb__list
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

if [ -z "${2:-}" ]; then
  usage >&2
  exit 1
fi

_TOOL="$1"
SURFACE_ID="$2"

# Placeholder partial; matches subagents/scorer.md output (no `pass` /
# `score_confidence` / `scored_at` — those are added by aggregate_scores.sh).
jq -nc --arg sid "$SURFACE_ID" '{
  surface_id: $sid,
  scorer_id: "placeholder",
  rubric_version: "unknown",
  scores: {
    agent_intuitiveness: 500,
    agent_ergonomics: 500,
    agent_ease_of_use: 500,
    output_parseability: 500,
    error_pedagogy: 500,
    intent_inference: 500,
    safety_with_recovery: 500,
    determinism_and_reproducibility: 500,
    self_documentation: 500,
    composability: 500,
    regression_resistance: 500
  },
  weighted_score: 500,
  evidence: {},
  notes: "placeholder; real scoring requires subagents/scorer.md"
}'
