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

command -v ledger >/dev/null 2>&1 || exit 0

payload=$(cat)
source_name=$(printf '%s' "$payload" | jq -r '.source // "startup"')
repo_root=$(find_learnings_root "$PWD" || true)
[ -n "${repo_root:-}" ] || exit 0

cd "$repo_root"

limit="${LEARNINGS_SESSIONSTART_LIMIT:-5}"
query="${LEARNINGS_SESSIONSTART_QUERY:-}"

if [ -n "$query" ]; then
  output=$(ledger recall --source learnings --query "$query" --limit "$limit" --drop-superseded 2>/dev/null || true)
  [ -n "$output" ] || exit 0
  printf 'Relevant repo learnings for "%s":\n%s\n' "$query" "$output"
  exit 0
fi

output=$(ledger recent --source learnings --limit "$limit" 2>/dev/null || true)
[ -n "$output" ] || exit 0
printf 'Recent repo learnings at session %s:\n%s\n' "$source_name" "$output"
