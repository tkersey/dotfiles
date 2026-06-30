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

ledger_bin=$(command -v ledger 2>/dev/null || true)
[ -n "$ledger_bin" ] || exit 0
ledger_supports_learnings "$ledger_bin" || exit 0

payload=$(cat)
source_name=$(printf '%s' "$payload" | jq -r '.source // "startup"')
repo_root=$(find_learnings_root "$PWD" || true)
[ -n "${repo_root:-}" ] || exit 0

cd "$repo_root"

limit="${LEARNINGS_SESSIONSTART_LIMIT:-5}"
query="${LEARNINGS_SESSIONSTART_QUERY:-}"

if [ -n "$query" ]; then
  output=$("$ledger_bin" recall --source learnings --query "$query" --limit "$limit" --drop-superseded 2>/dev/null || true)
  [ -n "$output" ] || exit 0
  printf 'Relevant repo learnings for "%s":\n%s\n' "$query" "$output"
  exit 0
fi

output=$("$ledger_bin" recent --source learnings --limit "$limit" 2>/dev/null || true)
[ -n "$output" ] || exit 0
printf 'Recent repo learnings at session %s:\n%s\n' "$source_name" "$output"
