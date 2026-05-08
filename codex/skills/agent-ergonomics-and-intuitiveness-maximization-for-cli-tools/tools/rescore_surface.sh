#!/usr/bin/env bash
# tools/rescore_surface.sh — Re-run scoring for a single surface_id.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/rescore_surface.sh <surface_id>

Emits the spawn instruction for re-scoring one surface. The actual scoring
is LLM-driven via subagents/scorer.md (× 2 + reconciliation-policy tiebreaker
only for 300-499 point spreads).
Useful after a targeted change to a single surface — avoids re-running the
whole Phase 2 swarm.

Args:
  <surface_id>   Content-derived ID (e.g. verb__list, flag__list__json).
                 Use tools/compute_surface_id.sh to compute from descriptors.

Output:
  Spawn instructions on stdout. Reads audit/manifest.json for rubric_version
  if available.

Example:
  tools/rescore_surface.sh verb__list
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

SURFACE_ID="$1"

cat <<EOF
To re-score $SURFACE_ID:

1. Spawn subagents/scorer.md with:
   - SURFACE_ID=$SURFACE_ID
   - SCORER_ID=A
   - RUBRIC_VERSION=$(jq -r '.rubric_version // "unknown"' audit/manifest.json 2>/dev/null || echo unknown)

2. Spawn a second scorer (independent) with SCORER_ID=B.

3. Reconcile per references/methodology/RECONCILIATION-POLICY.md:
   - spread 200-299: accept_warn
   - spread 300-499: spawn subagents/scorer-tiebreaker.md without raw A/B scores
   - spread >= 500: halt and escalate rubric anchors

4. Append the median to audit/agent_surfaces.jsonl with pass=current+1 (or update with current pass if re-running same SHA).

5. If the score changed, run tools/diff_scorecards.sh to update uplift_diff.md.
EOF
