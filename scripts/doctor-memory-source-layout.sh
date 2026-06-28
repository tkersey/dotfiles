#!/usr/bin/env sh
set -eu

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

status_for_file() {
  path="$1"
  optional="$2"
  if [ -f "$path" ]; then
    printf 'present'
  elif [ "$optional" = "true" ]; then
    printf 'missing_optional'
  else
    printf 'missing'
  fi
}

print_store() {
  name="$1"
  path="$2"
  optional="$3"
  status="$(status_for_file "$path" "$optional")"
  printf '%s\t%s\t%s\n' "$name" "$status" "$path"
}

printf 'memory-source-layout\trepo_root\t%s\n' "$repo_root"
print_store "learnings" ".ledger/learnings/learnings.jsonl" "false"
print_store "negative-ledger" ".ledger/negative-ledger/events.jsonl" "true"
print_store "synesthesia" ".ledger/synesthesia/events.jsonl" "true"
print_store "harness" ".ledger/harness/events.jsonl" "true"

if [ -f ".learnings.jsonl" ]; then
  printf 'learnings-legacy\tlegacy_present\t.learnings.jsonl\n'
fi

if [ -f ".ledger/negative-ledger.jsonl" ]; then
  printf 'negative-ledger-legacy\tlegacy_present\t.ledger/negative-ledger.jsonl\n'
fi
