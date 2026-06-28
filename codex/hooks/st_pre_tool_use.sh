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

plan_rel=$(st_plan_rel "$repo_root")

if [ -n "${transcript_path:-}" ]; then
  output=$(cd "$repo_root" && "$st_bin" guard-pre-tool-use --file "$plan_rel" --session-id "$session_id" --transcript-path "$transcript_path" 2>/dev/null || true)
else
  output=$(cd "$repo_root" && "$st_bin" guard-pre-tool-use --file "$plan_rel" --session-id "$session_id" 2>/dev/null || true)
fi

status=$(printf '%s' "$output" | jq -r '.status // "allow"' 2>/dev/null || printf allow)
if [ "$status" = "block" ]; then
  reason=$(printf '%s' "$output" | jq -r '.reason // "Outside Codex Plan Mode, mirror the exact $st SessionStart payload with update_plan before Bash commands."' 2>/dev/null || printf 'Outside Codex Plan Mode, mirror the exact $st SessionStart payload with update_plan before Bash commands.')
  jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
  exit 0
fi

json_continue
