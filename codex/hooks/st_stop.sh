#!/bin/sh
set -eu

. "$HOME/.dotfiles/codex/hooks/st_hook_common.sh"

payload=$(cat)
stop_hook_active=$(printf '%s' "$payload" | jq -r '.stop_hook_active // false')
last_message=$(printf '%s' "$payload" | jq -r '.last_assistant_message // ""')
transcript_path=$(printf '%s' "$payload" | jq -r '.transcript_path // ""')
mode="${ST_STOP_MODE:-block}"

[ "$mode" != "off" ] || {
  json_continue
  exit 0
}

[ "$stop_hook_active" = "true" ] && {
  json_continue
  exit 0
}

resolve_bin=$(resolve_c3_bin || true)
if [ -n "${resolve_bin:-}" ]; then
  resolve_output=$(printf '%s' "$payload" | "$resolve_bin" stop-guard --cwd "$PWD" 2>/dev/null || true)
  resolve_status=$(printf '%s' "$resolve_output" | jq -r '.status // "allow"' 2>/dev/null || printf allow)
  if [ "$resolve_status" = "block" ]; then
    reason=$(printf '%s' "$resolve_output" | jq -r '.reason // "C³ run is not closed."' 2>/dev/null || printf 'C³ run is not closed.')
    jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
    exit 0
  fi
elif c3_root=$(find_c3_root "$PWD" || true); [ -n "${c3_root:-}" ]; then
  reason=$(printf 'Active C³ state exists at %s/.ledger/c3/state.json, but resolve-c3 is unavailable.' "$c3_root")
  jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
  exit 0
fi

repo_root=$(find_st_root "$PWD" || true)
[ -n "${repo_root:-}" ] || {
  json_continue
  exit 0
}

looks_like_wrap_up "$last_message" || {
  json_continue
  exit 0
}

if ! git -C "$repo_root" rev-parse --show-toplevel >/dev/null 2>&1; then
  json_continue
  exit 0
fi

has_non_plan_changes "$repo_root" || {
  json_continue
  exit 0
}

[ -n "${transcript_path:-}" ] && [ -f "$transcript_path" ] || {
  json_continue
  exit 0
}

st_bin=$(resolve_st_bin "reconcile-codex" || true)
[ -n "${st_bin:-}" ] || {
  json_continue
  exit 0
}

plan_file=$(st_plan_file "$repo_root")

if output=$(cd "$repo_root" && "$st_bin" reconcile-codex --file .step/st-plan.jsonl --transcript-path "$transcript_path" 2>&1); then
  json_continue
  exit 0
fi

reason=$(printf 'Repo uses durable $st at %s and Stop-time sync from the latest update_plan failed.\n%s\n' "$plan_file" "$output")

if [ "$mode" = "warn" ]; then
  jq -n --arg msg "$reason" '{continue: true, systemMessage: $msg}'
  exit 0
fi

jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
