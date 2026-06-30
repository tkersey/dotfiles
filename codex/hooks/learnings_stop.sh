#!/bin/sh
set -eu

find_source_memory_root() {
  dir="${1:-$PWD}"
  while [ "$dir" != "/" ]; do
    if [ -f "$dir/.ledger/learnings/events.jsonl" ] ||
      [ -f "$dir/.ledger/learnings/learnings.jsonl" ] ||
      [ -f "$dir/.learnings.jsonl" ] ||
      [ -f "$dir/.ledger/synesthesia/events.jsonl" ]; then
      printf '%s\n' "$dir"
      return 0
    fi
    dir=$(dirname "$dir")
  done
  return 1
}

ledger_supports_source() {
  bin="${1:?ledger binary required}"
  source="${2:?source required}"
  marker="${3:?marker required}"
  "$bin" --help 2>/dev/null | grep -Fq -- "--source SOURCE" &&
    "$bin" capture --source "$source" --help 2>/dev/null | grep -Fq "$marker"
}

looks_like_wrap_up() {
  printf '%s' "${1:-}" | grep -Eiq '\b(done|completed|implemented|updated|changed|configured|wired|fixed|added|removed|created|verification|verified|validated|testing|tested|tests|pass(ed)?|smoke|setup)\b'
}

has_completion_proof() {
  message="${1:-}"
  sources="${2:-}"
  case " $sources " in
    *" learnings "*)
      printf '%s\n' "$message" | grep -Eiq '^(appended:[[:space:]]id=|0 records appended:[[:space:]].+|duplicate-skip:[[:space:]].+|learnings:[[:space:]](appended:[[:space:]]id=|0 records appended:[[:space:]].+|duplicate-skip:[[:space:]].+))' || return 1
      ;;
  esac
  case " $sources " in
    *" synesthesia "*)
      printf '%s\n' "$message" | grep -Eiq '^synesthesia:[[:space:]](appended:[[:space:]]id=|0 records appended:[[:space:]].+|duplicate-skip:[[:space:]].+)' || return 1
      ;;
  esac
  return 0
}

json_continue() {
  jq -n '{continue: true}'
}

payload=$(cat)
stop_hook_active=$(printf '%s' "$payload" | jq -r '.stop_hook_active // false')
last_message=$(printf '%s' "$payload" | jq -r '.last_assistant_message // ""')
mode="${LEARNINGS_STOP_MODE:-block}"

[ "$mode" != "off" ] || {
  json_continue
  exit 0
}

[ "$stop_hook_active" = "true" ] && {
  json_continue
  exit 0
}

ledger_bin=$(command -v ledger 2>/dev/null || true)
[ -n "$ledger_bin" ] || {
  json_continue
  exit 0
}

sources=""
if ledger_supports_source "$ledger_bin" learnings ".ledger/learnings/events.jsonl"; then
  sources="${sources} learnings"
fi
if ledger_supports_source "$ledger_bin" synesthesia ".ledger/synesthesia/events.jsonl"; then
  sources="${sources} synesthesia"
fi
[ -n "$sources" ] || {
  json_continue
  exit 0
}

repo_root=$(find_source_memory_root "$PWD" || true)
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

non_learning_changes=$(
  {
    git -C "$repo_root" diff --name-only
    git -C "$repo_root" diff --cached --name-only
    git -C "$repo_root" ls-files --others --exclude-standard
  } | awk 'NF' | sort -u | grep -Ev '(^|/)\.learnings\.jsonl$|(^|/)\.ledger/learnings/(events|learnings)\.jsonl$|(^|/)\.ledger/synesthesia/events\.jsonl$' || true
)

[ -n "$non_learning_changes" ] || {
  json_continue
  exit 0
}

learnings_touched=$(
  {
    git -C "$repo_root" diff --name-only
    git -C "$repo_root" diff --cached --name-only
    git -C "$repo_root" ls-files --others --exclude-standard
  } | awk 'NF' | sort -u | grep -E '(^|/)\.learnings\.jsonl$|(^|/)\.ledger/learnings/(events|learnings)\.jsonl$|(^|/)\.ledger/synesthesia/events\.jsonl$' || true
)

[ -z "$learnings_touched" ] || {
  json_continue
  exit 0
}

has_completion_proof "$last_message" "$sources" && {
  json_continue
  exit 0
}

reason='Repo has source-memory stores and this turn appears to be wrapping up with file changes. Run `ledger doctor --source learnings` and `ledger capture --source learnings ...` before final handoff, and evaluate Synesthesia with `ledger doctor --source synesthesia`; if no durable sensory mapping or boundary exists, report `synesthesia: 0 records appended: <reason>`.'

if [ "$mode" = "warn" ]; then
  jq -n --arg msg "$reason" '{continue: true, systemMessage: $msg}'
  exit 0
fi

jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
