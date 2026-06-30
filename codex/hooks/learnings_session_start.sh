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

ledger_bin=$(command -v ledger 2>/dev/null || true)
[ -n "$ledger_bin" ] || exit 0

sources=""
if ledger_supports_source "$ledger_bin" learnings ".ledger/learnings/events.jsonl"; then
  sources="${sources} learnings"
fi
if ledger_supports_source "$ledger_bin" synesthesia ".ledger/synesthesia/events.jsonl"; then
  sources="${sources} synesthesia"
fi
[ -n "$sources" ] || exit 0

payload=$(cat)
source_name=$(printf '%s' "$payload" | jq -r '.source // "startup"')
repo_root=$(find_source_memory_root "$PWD" || true)
[ -n "${repo_root:-}" ] || exit 0

cd "$repo_root"

limit="${LEARNINGS_SESSIONSTART_LIMIT:-5}"
query="${LEARNINGS_SESSIONSTART_QUERY:-}"

if [ -n "$query" ]; then
  emitted=false
  for source in $sources; do
    if [ "$source" = "learnings" ]; then
      output=$("$ledger_bin" recall --source learnings --query "$query" --limit "$limit" --drop-superseded 2>/dev/null || true)
    else
      output=$("$ledger_bin" recall --source synesthesia --query "$query" --limit "$limit" 2>/dev/null || true)
    fi
    [ -n "$output" ] || continue
    printf 'Relevant repo %s for "%s":\n%s\n' "$source" "$query" "$output"
    emitted=true
  done
  [ "$emitted" = "true" ] || exit 0
  exit 0
fi

emitted=false
for source in $sources; do
  output=$("$ledger_bin" recent --source "$source" --limit "$limit" 2>/dev/null || true)
  [ -n "$output" ] || continue
  printf 'Recent repo %s at session %s:\n%s\n' "$source" "$source_name" "$output"
  emitted=true
done
[ "$emitted" = "true" ] || exit 0
