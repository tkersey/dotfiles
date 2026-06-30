#!/bin/sh
set -eu

find_learnings_root() {
  dir="${1:-$PWD}"
  while [ "$dir" != "/" ]; do
    if [ -f "$dir/.ledger/learnings/events.jsonl" ] ||
      [ -f "$dir/.ledger/learnings/learnings.jsonl" ] ||
      [ -f "$dir/.learnings.jsonl" ]; then
      printf '%s\n' "$dir"
      return 0
    fi
    dir=$(dirname "$dir")
  done
  return 1
}

ledger_supports_learnings() {
  bin="${1:?ledger binary required}"
  "$bin" --help 2>/dev/null | grep -Fq -- "--source SOURCE" &&
    "$bin" capture --source learnings --help 2>/dev/null | grep -Fq ".ledger/learnings/events.jsonl"
}

looks_like_wrap_up() {
  printf '%s' "${1:-}" | grep -Eiq '\b(done|completed|implemented|updated|changed|configured|wired|fixed|added|removed|created|verification|verified|validated|testing|tested|tests|pass(ed)?|smoke|setup)\b'
}

has_completion_proof() {
  printf '%s' "${1:-}" | grep -Eiq '(0 records appended:[[:space:]].+|duplicate-skip:[[:space:]].+)'
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

ledger_supports_learnings "$ledger_bin" || {
  json_continue
  exit 0
}

repo_root=$(find_learnings_root "$PWD" || true)
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
  } | awk 'NF' | sort -u | grep -Ev '(^|/)\.learnings\.jsonl$|(^|/)\.ledger/learnings/(events|learnings)\.jsonl$' || true
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
  } | awk 'NF' | sort -u | grep -E '(^|/)\.learnings\.jsonl$|(^|/)\.ledger/learnings/(events|learnings)\.jsonl$' || true
)

[ -z "$learnings_touched" ] || {
  json_continue
  exit 0
}

has_completion_proof "$last_message" && {
  json_continue
  exit 0
}

reason='Repo has a learnings source store and this turn appears to be wrapping up with file changes. Run `ledger doctor --source learnings` and `ledger capture --source learnings ...` before final handoff, or report `duplicate-skip: <reason>` / `0 records appended: <reason>`.'

if [ "$mode" = "warn" ]; then
  jq -n --arg msg "$reason" '{continue: true, systemMessage: $msg}'
  exit 0
fi

jq -n --arg reason "$reason" '{continue: true, decision: "block", reason: $reason}'
