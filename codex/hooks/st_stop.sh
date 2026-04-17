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

st_bin=$(resolve_st_bin "import-update-plan" || true)
[ -n "${st_bin:-}" ] || {
  json_continue
  exit 0
}

plan_file=$(st_plan_file "$repo_root")

if output=$(cd "$repo_root" && "$st_bin" import-update-plan --file .step/st-plan.jsonl --transcript-path "$transcript_path" 2>&1); then
  json_continue
  exit 0
fi

reason=$(printf 'Repo uses durable $st at %s and Stop-time sync from the latest update_plan failed.\n%s\n' "$plan_file" "$output")

if [ "$mode" = "warn" ]; then
  jq -n --arg msg "$reason" '{continue: true, systemMessage: $msg}'
  exit 0
fi

jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
