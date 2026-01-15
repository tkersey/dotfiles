#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 \"PROMPT STRING\"" >&2
  exit 1
fi

PROMPT="$*"

PROMPT_PREFIX=$(cat <<'EOF'
Before any tool calls, print:
AGENT_STATUS:
<1-3 lines: intent + what you need next>
END_AGENT_STATUS
EOF
)

PROMPT="${PROMPT_PREFIX}

${PROMPT}"

exec codex \
  --search \
  --enable web_search_request \
  --dangerously-bypass-approvals-and-sandbox \
  exec \
  -m gpt-5.2-codex \
  -c 'model_reasoning_effort="high"' \
  -- \
  "$PROMPT"
