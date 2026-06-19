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

resolve_tool="$HOME/.dotfiles/codex/skills/resolve/tools/review_compile.py"
if [ -f "$resolve_tool" ]; then
  resolve_output=$(python3 "$resolve_tool" hook-context --cwd "$PWD" 2>/dev/null || true)
  resolve_active=$(printf '%s' "$resolve_output" | jq -r '.active // false' 2>/dev/null || printf false)
  if [ "$resolve_active" = "true" ]; then
    resolve_context=$(printf '%s' "$resolve_output" | jq -r '.context // ""' 2>/dev/null || true)
    if [ -n "${resolve_context:-}" ]; then
      contexts="${contexts}${resolve_context}
"
      messages="${messages}Hydrating active C³ review compiler state. "
    fi
  fi
fi

repo_root=$(find_st_root "$PWD" || true)
if [ -n "${repo_root:-}" ] && [ -n "${session_id:-}" ]; then
  st_bin=$(resolve_st_bin "guard-session-start" || true)
  if [ -n "${st_bin:-}" ]; then
    update_plan_payload=$(cd "$repo_root" && "$st_bin" guard-session-start --file .step/st-plan.jsonl --session-id "$session_id" 2>/dev/null || true)
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
