#!/usr/bin/env bash
# multi_agent_swarm.sh — launch an NTM swarm for an accepted candidate list.
# See references/AGENT-COORDINATION.md.
#
# Usage: multi_agent_swarm.sh [run-id] [num-panes]
# Preconditions:
#   - beads (br) installed and repo already has accepted candidate beads labeled "refactor"
#   - agent-mail MCP optional (falls back to non-exclusive reservations if missing)
#   - ntm installed
#
# The script:
#   1. Verifies prerequisites
#   2. Reads ready refactor beads
#   3. Spawns N NTM panes (default 4)
#   4. Sends marching orders to each

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-pass-1}"
NUM_PANES="${2:-4}"
ART="refactor/artifacts/${RUN_ID}"
PROJECT_ROOT="$(pwd)"

have() { command -v "$1" >/dev/null 2>&1; }

if ! have ntm; then
  echo "error: ntm not installed. Run solo sequential mode instead:" >&2
  echo "  ./scripts/baseline.sh && ./scripts/dup_scan.sh && ... (one candidate at a time)" >&2
  exit 2
fi

if ! have br; then
  echo "error: br (beads_rust) not installed. Required to coordinate candidates." >&2
  echo "If beads isn't in use, fall back to serial mode — one candidate per commit." >&2
  exit 2
fi

# Check there are ready refactor beads
ready_count=$(br ready --json 2>/dev/null | grep -c '"label":\s*"refactor"' || echo "0")
if (( ready_count == 0 )); then
  echo "No ready refactor-labeled beads found." >&2
  echo "Create beads via: br create --title '[refactor Dn] ...' --type task --priority 2 --label refactor" >&2
  echo "(See references/AGENT-COORDINATION.md for the full orchestrator recipe.)" >&2
  exit 0
fi

echo "Found $ready_count ready refactor beads."
echo "Spawning $NUM_PANES NTM panes..."

MARCHING_ORDERS=$(cat <<EOF
You are a refactor swarm worker. Read AGENTS.md first.

Your run: ${RUN_ID}
Artifact dir: ${ART}

Loop:
  1. br ready --json         # pick highest-priority unblocked refactor bead
  2. br update <id> --status=in_progress
  3. If agent-mail is available, reserve the candidate's paths:
        file_reservation_paths(project_key=${PROJECT_ROOT}, agent_name=<your-name>,
                               paths=[<candidate paths>],
                               ttl_seconds=3600, exclusive=true,
                               reason="refactor-<id>")
     If a FILE_RESERVATION_CONFLICT occurs: revert the bead to open, pick another.
  4. Apply the skill's loop on that candidate:
       ./scripts/isomorphism_card.sh <id> ${RUN_ID}
       # read the card carefully; fill every row
       # Edit-only changes; NO Write; NO sed/codemod
       ./scripts/verify_isomorphism.sh ${RUN_ID}
       # if any gate fails: revert and mark bead blocked
  5. Commit: refactor(<scope>): <title>
        [isomorphism card verbatim]
        LOC: <path> <before>→<after>. Tests <pass>/<fail>/<skip> unchanged.
        Beads: <id>
  6. Append row to ${ART}/LEDGER.md (use flock to serialize)
  7. release_file_reservations(...)
  8. br close <id> --reason "Completed ledger row appended"
  9. If no ready beads remain: exit

Invariants (AGENTS.md):
  - no file deletion without user approval — move to refactor/_to_delete/ and ASK
  - no script-based code changes
  - one lever per commit
  - never pause on "unexpected changes" from other agents
EOF
)

for i in $(seq 1 "$NUM_PANES"); do
  name="refactor-worker-$(printf '%02d' "$i")"
  echo "  spawning $name..."
  ntm spawn "$name" --dir "$PROJECT_ROOT" >/dev/null 2>&1 || { echo "  warn: could not spawn $name"; continue; }
  ntm send "$name" "$MARCHING_ORDERS" >/dev/null 2>&1 || echo "  warn: could not send to $name"
done

echo ""
echo "Swarm launched. Monitor progress:"
echo "  watch -n 10 'br list --status in_progress --json | wc -l'"
echo "  ntm list"
echo ""
echo "For stuck-pane recovery: see references/AGENT-COORDINATION.md § Recovery"
