#!/bin/sh
set -eu

. /Users/tk/.dotfiles/codex/hooks/st_hook_common.sh

payload=$(cat)
source_name=$(printf '%s' "$payload" | jq -r '.source // "startup"')
mode="${ST_SESSIONSTART_MODE:-inject}"

[ "$mode" != "off" ] || {
  json_continue
  exit 0
}

case "$source_name" in
  startup|resume)
    ;;
  *)
    json_continue
    exit 0
    ;;
esac

repo_root=$(find_st_root "$PWD" || true)
[ -n "${repo_root:-}" ] || {
  json_continue
  exit 0
}
plan_file=$(st_plan_file "$repo_root")

st_bin=$(resolve_st_bin "import-update-plan" || true)
[ -n "${st_bin:-}" ] || {
  json_continue
  exit 0
}

update_plan_payload=$(cd "$repo_root" && "$st_bin" emit-update-plan --file .step/st-plan.jsonl 2>/dev/null || true)
[ -n "${update_plan_payload:-}" ] || {
  json_continue
  exit 0
}

context=$(cat <<EOF
Repo contains a durable \$st plan at $plan_file.
On SessionStart, the durable store is the source of truth.
Before substantive work, call update_plan exactly once with this payload emitted by st:
$update_plan_payload
Preserve the emitted [st-id] step prefixes so Stop-time sync can round-trip safely back into the durable ledger.
EOF
)

jq -n --arg context "$context" --arg msg "Hydrating \$st plan from durable store" '{
  continue: true,
  systemMessage: $msg,
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: $context
  }
}'
