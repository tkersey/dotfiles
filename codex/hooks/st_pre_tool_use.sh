#!/bin/sh
set -eu

. "$HOME/.dotfiles/codex/hooks/st_hook_common.sh"

payload=$(cat)
session_id=$(printf '%s' "$payload" | jq -r '.session_id // ""')
transcript_path=$(printf '%s' "$payload" | jq -r '.transcript_path // ""')

[ -n "${session_id:-}" ] || {
  json_continue
  exit 0
}

repo_root=$(find_st_root "$PWD" || true)
[ -n "${repo_root:-}" ] || {
  json_continue
  exit 0
}

st_bin=$(resolve_st_bin "guard-pre-tool-use" || true)
[ -n "${st_bin:-}" ] || {
  json_continue
  exit 0
}

if [ -n "${transcript_path:-}" ]; then
  output=$(cd "$repo_root" && "$st_bin" guard-pre-tool-use --file .step/st-plan.jsonl --session-id "$session_id" --transcript-path "$transcript_path" 2>/dev/null || true)
else
  output=$(cd "$repo_root" && "$st_bin" guard-pre-tool-use --file .step/st-plan.jsonl --session-id "$session_id" 2>/dev/null || true)
fi

status=$(printf '%s' "$output" | jq -r '.status // "allow"' 2>/dev/null || printf 'allow')
if [ "$status" = "block" ]; then
  reason=$(printf '%s' "$output" | jq -r '.reason // "Run update_plan with the exact $st SessionStart payload before Bash commands."' 2>/dev/null || printf 'Run update_plan with the exact $st SessionStart payload before Bash commands.')
  jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
  exit 0
fi

json_continue
