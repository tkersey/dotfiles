#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 \"PROMPT STRING\"" >&2
  exit 1
fi

PROMPT="$*"

exec codex \
  --search \
  --enable web_search_request \
  --enable skills \
  --yolo \
  --dangerously-bypass-approvals-and-sandbox \
  exec \
  -m gpt-5.2-codex \
  -c 'model_reasoning_effort="high"' \
  -- \
  "$PROMPT"
