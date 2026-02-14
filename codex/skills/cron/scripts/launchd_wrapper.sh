#!/bin/sh
set -eu

LABEL="com.openai.codex.automation-runner"
LOCK_DIR="$HOME/Library/Caches/$LABEL"
LOCK_FILE="$LOCK_DIR/run.lock"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/automation_runner.py"

mkdir -p "$LOCK_DIR"

if [ ! -x "$SCRIPT" ]; then
  echo "error: runner script is not executable: $SCRIPT" >&2
  exit 1
fi

if /usr/bin/lockf -k -s -t 0 "$LOCK_FILE" "$SCRIPT" --once; then
  exit 0
fi

rc=$?
if [ "$rc" -eq 75 ]; then
  echo "$(date -u +%FT%TZ) skip: lock held" >&2
  exit 0
fi

exit "$rc"
