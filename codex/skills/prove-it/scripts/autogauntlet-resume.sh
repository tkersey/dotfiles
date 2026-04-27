#!/usr/bin/env bash
set -euo pipefail

# Minimal CLI loop for Codex-style noninteractive continuation.
# Run this from the same project/session after the first prove-it turn exists.
# It assumes `codex exec resume --last` resumes the latest conversation.

PROMPT='Continue prove-it from the checkpoint. Execute exactly the next uncompleted numbered round only. Stop only if the Terminality Check is terminal.'
MAX_TURNS="${MAX_TURNS:-10}"
OUT_DIR="${OUT_DIR:-.prove-it-runs}"
mkdir -p "$OUT_DIR"

for i in $(seq 1 "$MAX_TURNS"); do
  out_file="$OUT_DIR/turn-$i.txt"
  codex exec resume --last "$PROMPT" | tee "$out_file"

  if grep -Eq 'Status:[[:space:]]*COMPLETE|Action:[[:space:]]*STOP|Terminal verdict:[[:space:]]*(PROVEN|DISPROVEN|ROUND_10_COMPLETE|USER_STOPPED)' "$out_file"; then
    exit 0
  fi
done

printf 'Reached MAX_TURNS=%s without a terminal checkpoint. Inspect %s.\n' "$MAX_TURNS" "$OUT_DIR" >&2
exit 1
