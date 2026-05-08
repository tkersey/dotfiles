#!/usr/bin/env bash
# scripts/run_simulation.sh — Phase 3/9 simulation orchestrator (stub).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_simulation.sh <sibling> <pre|post> [pass]

STUB / SCAFFOLD: prepares the output directory for a Phase 3 (pre-pass) or
Phase 9 (post-pass) canonical-task simulation, and emits the spawn
instruction the main agent should follow. The actual simulation is driven
by subagents/canonical-task-simulator.md, spawned with FRESH context (no
prior audit knowledge).

Args:
  <sibling>   Audit workspace root.
  <pre|post>  Whether this is the pre-pass baseline (Phase 3) or the
              post-pass verification (Phase 9).
  [pass]      Pass number (default: 1).

Output:
  Creates audit/agent_simulations/{pre|post}_pass_<N>/. Emits the spawn
  instruction to stdout.

Example:
  scripts/run_simulation.sh /path/to/__audit pre 1
  scripts/run_simulation.sh /path/to/__audit post 2
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

SIBLING="$1"
STAGE="$2"
PASS="${3:-1}"

# Validate <stage> shape — only "pre" and "post" are real stages. Without this
# check, a typo like `prx` would silently create `audit/agent_simulations/
# prx_pass_1/` and the canonical-task simulator subagent would dutifully
# write transcripts there. Phase 9 diff-vs-baseline scripts then fail to
# find the expected pre/post pair without surfacing the original typo.
if [ "$STAGE" != "pre" ] && [ "$STAGE" != "post" ]; then
  echo "stage must be 'pre' or 'post' (got '$STAGE')" >&2
  exit 1
fi

# Validate <pass> shape — must be a non-negative integer. Otherwise
# `run_simulation.sh /path post abc` would create `post_pass_abc/`, and any
# downstream script that reads `current_pass` from manifest.json (and joins
# it as a directory name) would never find the transcripts.
if ! [[ "$PASS" =~ ^[0-9]+$ ]]; then
  echo "pass must be a non-negative integer (got '$PASS')" >&2
  exit 1
fi

DIR="$SIBLING/audit/agent_simulations/${STAGE}_pass_${PASS}"
mkdir -p "$DIR"

cat <<EOF
spawn subagents/canonical-task-simulator.md (FRESH context — no prior audit knowledge):

Output dir: $DIR
Pass: $PASS
Stage: $STAGE

Task list: <from intake; default top 5–10 README examples>

Per task, capture:
  - $DIR/task-NN-<slug>.transcript.jsonl
  - $DIR/task-NN-<slug>.summary.md

After all tasks done:
  - $DIR/summary.md
EOF

exit 0
