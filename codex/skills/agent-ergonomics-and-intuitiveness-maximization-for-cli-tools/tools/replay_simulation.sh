#!/usr/bin/env bash
# tools/replay_simulation.sh — Convenience wrapper for scripts/replay_simulation.sh.
# Picks task from agent_simulations/post_pass_<N>/ by task slug.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/replay_simulation.sh <task-slug-or-id> [sibling-dir]

Smart wrapper for scripts/replay_simulation.sh. Looks up the task
transcript by slug under audit/agent_simulations/post_pass_<current>/,
auto-detects the tool binary from manifest.json, and replays.

Args:
  <task-slug-or-id>   Substring of the transcript filename to match.
  [sibling-dir]       Audit workspace root. Defaults to $PWD.

Env:
  TOOL_BIN            Override the tool binary path (otherwise computed
                      from manifest.json's tool_repo/tool_name fields).

Run --help on the underlying script for full options:
  scripts/replay_simulation.sh --help

Example:
  cd /path/to/__audit && tools/replay_simulation.sh task-01-list
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

TASK="$1"
SIBLING="${2:-$PWD}"

if [ -f "$SIBLING/audit/manifest.json" ]; then
  AUDIT="$SIBLING/audit"
else
  if [ $# -ge 2 ]; then
    echo "manifest.json not found under explicit sibling dir: $SIBLING/audit/manifest.json" >&2
    exit 2
  fi
  AUDIT="$PWD/audit"
fi

if [ ! -f "$AUDIT/manifest.json" ]; then
  echo "manifest.json not found: $AUDIT/manifest.json" >&2
  exit 2
fi

CURRENT_PASS=$(jq -r '.current_pass // 1' "$AUDIT/manifest.json" 2>/dev/null || echo 1)
# `// 1` only fires inside jq when .current_pass is missing/null. If jq
# itself fails (file unreadable), `|| echo 1` recovers. But if .current_pass
# was stored as a non-numeric string ("null", "abc", ""), `// 1` doesn't
# kick in and we'd build a `post_pass_<garbage>/` path. Validate integer
# shape and fall back to 1 instead of letting the garbage propagate.
if ! [[ "$CURRENT_PASS" =~ ^[0-9]+$ ]]; then
  CURRENT_PASS=1
fi

# Find the transcript
candidate="$AUDIT/agent_simulations/post_pass_${CURRENT_PASS}/${TASK}.transcript.jsonl"
if [ ! -f "$candidate" ]; then
  candidate=$(find "$AUDIT/agent_simulations/post_pass_${CURRENT_PASS}" -maxdepth 1 -type f -name '*.transcript.jsonl' -print 2>/dev/null \
    | awk -v needle="$TASK" 'index($0, needle) { print }' \
    | sort \
    | head -1 || true)
fi

if [ -z "$candidate" ] || [ ! -f "$candidate" ]; then
  echo "transcript not found for task: $TASK" >&2
  exit 2
fi

# Find the tool binary. The previous one-liner did:
#   TOOL_BIN="${TOOL_BIN:-$(jq -r '.tool_repo' ...)/target/release/$(jq -r '.tool_name' ...)}"
# If either field was missing from manifest.json, jq emitted the literal
# string "null" and TOOL_BIN became `null/target/release/null` — the
# downstream replay then errored with "No such file" pointing at a path the
# user never typed, which is hard to debug. Validate explicitly and report
# the actual missing field.
if [ -z "${TOOL_BIN:-}" ]; then
  TOOL_REPO=$(jq -r '.tool_repo // ""' "$AUDIT/manifest.json" 2>/dev/null)
  TOOL_NAME=$(jq -r '.tool_name // ""' "$AUDIT/manifest.json" 2>/dev/null)
  if [ -z "$TOOL_REPO" ] || [ "$TOOL_REPO" = "null" ]; then
    echo "manifest.json missing .tool_repo; set TOOL_BIN env var or fix manifest" >&2
    exit 2
  fi
  if [ -z "$TOOL_NAME" ] || [ "$TOOL_NAME" = "null" ]; then
    echo "manifest.json missing .tool_name; set TOOL_BIN env var or fix manifest" >&2
    exit 2
  fi
  TOOL_BIN="$TOOL_REPO/target/release/$TOOL_NAME"
fi

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$SKILL_DIR/scripts/replay_simulation.sh" "$candidate" "$TOOL_BIN"
