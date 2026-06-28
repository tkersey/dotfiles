#!/bin/sh
set -eu

. "$HOME/.dotfiles/codex/hooks/st_hook_common.sh"

payload=$(cat)
source_name=$(printf '%s' "$payload" | jq -r '.source // "startup"')
session_id=$(printf '%s' "$payload" | jq -r '.session_id // ""')
mode="${ST_SESSIONSTART_MODE:-inject}"

[ "$mode" != "off" ] || {
  json_continue
  exit 0
}

case "$source_name" in
  startup|resume) ;;
  *)
    json_continue
    exit 0
    ;;
esac

contexts=""
messages=""

repo_root=$(find_st_root "$PWD" || true)
if [ -n "${repo_root:-}" ] && [ -n "${session_id:-}" ]; then
  st_bin=$(resolve_st_bin "guard-session-start" || true)
  if [ -n "${st_bin:-}" ]; then
    plan_rel=$(st_plan_rel "$repo_root")
    update_plan_payload=$(cd "$repo_root" && "$st_bin" guard-session-start --file "$plan_rel" --session-id "$session_id" 2>/dev/null || true)
    if [ -n "${update_plan_payload:-}" ]; then
      plan_file=$(st_plan_file "$repo_root")
      st_context=$(cat <<EOF
Repo contains a durable \$st plan at $plan_file.
On SessionStart, the durable store is the source of truth.
Do not call update_plan while Codex is in Plan Mode. After Plan Mode, import or compile the proposed plan into \$st first.
Before substantive execution outside Plan Mode, mirror only the exact native projection payload emitted by st.
If material graph work has no current GCR-v1 for the durable seq/fingerprints, run st compile aperture before execution.
Mirror plan_sync.codex.plan by calling update_plan exactly once with this payload emitted by st:
$update_plan_payload
Preserve the emitted [st-id] step prefixes so later durable reconciliation remains exact.
EOF
)
      contexts="${contexts}${st_context}
"
      messages="${messages}Hydrating \$st plan from durable state."
    fi
  fi
fi

[ -n "${contexts:-}" ] || {
  json_continue
  exit 0
}

jq -n --arg context "$contexts" --arg msg "$messages" '{
  continue: true,
  systemMessage: $msg,
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: $context
  }
}'
