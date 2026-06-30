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

print_learnings_store() {
  if [ -f ".ledger/learnings/events.jsonl" ]; then
    printf 'learnings\tpresent\t.ledger/learnings/events.jsonl\n'
  elif [ -f ".ledger/learnings/learnings.jsonl" ] || [ -f ".learnings.jsonl" ]; then
    printf 'learnings\tlegacy-only\t.ledger/learnings/events.jsonl\n'
  else
    printf 'learnings\tmissing\t.ledger/learnings/events.jsonl\n'
  fi
}

print_synesthesia_store() {
  if [ -f ".ledger/synesthesia/events.jsonl" ]; then
    printf 'synesthesia\tpresent\t.ledger/synesthesia/events.jsonl\n'
    return
  fi
  codex_home="${CODEX_HOME:-$HOME/.codex}"
  notes_dir="$codex_home/memories/extensions/synesthesia/notes"
  if [ -d "$notes_dir" ] && find "$notes_dir" -type f -name '*.md' | grep -q .; then
    printf 'synesthesia\tnotes-only\t.ledger/synesthesia/events.jsonl\n'
    return
  fi
  printf 'synesthesia\tmissing\t.ledger/synesthesia/events.jsonl\n'
}

printf 'memory-source-layout\trepo_root\t%s\n' "$repo_root"
print_learnings_store
print_store "negative-ledger" ".ledger/negative-ledger/events.jsonl" "true"
print_synesthesia_store
print_store "harness" ".ledger/harness/events.jsonl" "true"

if [ -f ".learnings.jsonl" ]; then
  printf 'learnings-legacy\tlegacy_present\t.learnings.jsonl\n'
fi

if [ -f ".ledger/learnings/learnings.jsonl" ]; then
  printf 'learnings-previous\tlegacy_present\t.ledger/learnings/learnings.jsonl\n'
fi

if [ -f ".ledger/negative-ledger.jsonl" ]; then
  printf 'negative-ledger-legacy\tlegacy_present\t.ledger/negative-ledger.jsonl\n'
fi
