#!/bin/sh
set -eu

. "$HOME/.dotfiles/codex/hooks/st_hook_common.sh"

payload=$(cat)

resolve_bin=$(resolve_c3_bin || true)
if [ -n "${resolve_bin:-}" ]; then
  resolve_output=$(printf '%s' "$payload" | "$resolve_bin" guard-hook --cwd "$PWD" 2>/dev/null || true)
  resolve_status=$(printf '%s' "$resolve_output" | jq -r '.status // "allow"' 2>/dev/null || printf allow)
  if [ "$resolve_status" = "block" ]; then
    reason=$(printf '%s' "$resolve_output" | jq -r '.reason // "C³ blocked a direct delivery mutation."' 2>/dev/null || printf 'C³ blocked a direct delivery mutation.')
    jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
    exit 0
  fi
elif c3_root=$(find_c3_root "$PWD" || true); [ -n "${c3_root:-}" ]; then
  reason=$(printf 'Active C³ state exists at %s/.ledger/c3/state.json, but resolve-c3 is unavailable.' "$c3_root")
  jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
  exit 0
fi

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

status=$(printf '%s' "$output" | jq -r '.status // "allow"' 2>/dev/null || printf allow)
if [ "$status" = "block" ]; then
  reason=$(printf '%s' "$output" | jq -r '.reason // "Outside Codex Plan Mode, mirror the exact $st SessionStart payload with update_plan before Bash commands."' 2>/dev/null || printf 'Outside Codex Plan Mode, mirror the exact $st SessionStart payload with update_plan before Bash commands.')
  jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
  exit 0
fi

json_continue
