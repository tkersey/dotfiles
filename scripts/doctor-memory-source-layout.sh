#!/bin/sh
set -eu

CODEX_HOME=${CODEX_HOME:-"$HOME/.codex"}
ROOT="$CODEX_HOME/memories"
EXT="$ROOT/extensions"
FAIL=0

check_real_dir() {
  path=$1
  required=$2
  if [ -L "$path" ]; then
    echo "FAIL symlink: $path"
    FAIL=1
    return
  fi
  if [ ! -d "$path" ]; then
    if [ "$required" = yes ]; then
      echo "FAIL missing directory: $path"
      FAIL=1
    else
      echo "WARN missing directory: $path"
    fi
    return
  fi
  echo "OK real directory: $path"
}

check_real_dir "$ROOT" yes
check_real_dir "$EXT" yes

for extension in harness learnings negative-ledger synesthesia; do
  dir="$EXT/$extension"
  check_real_dir "$dir" yes
  if [ -f "$dir/instructions.md" ]; then
    echo "OK instructions: $extension"
  else
    echo "FAIL missing instructions: $dir/instructions.md"
    FAIL=1
  fi
  check_real_dir "$dir/notes" no
  check_real_dir "$dir/resources" no
done

for untouched in ad_hoc chronicle; do
  if [ -d "$EXT/$untouched" ]; then
    echo "OK untouched extension present: $untouched"
  else
    echo "INFO untouched extension absent: $untouched"
  fi
done

if command -v memory-note >/dev/null 2>&1; then
  echo "OK CLI: memory-note"
  memory-note doctor >/dev/null 2>&1 || {
    echo "FAIL memory-note doctor"
    FAIL=1
  }
else
  echo "WARN CLI unavailable: memory-note"
fi

if command -v ledger >/dev/null 2>&1; then
  echo "OK CLI: ledger"
else
  echo "WARN CLI unavailable: ledger"
fi

if [ -d "$ROOT/.git" ]; then
  echo "OK memory git baseline exists"
  git -C "$ROOT" status --short || {
    echo "FAIL cannot inspect memory workspace git status"
    FAIL=1
  }
else
  echo "WARN memory git baseline missing; Codex should initialize it on Phase 2 startup"
fi

exit "$FAIL"
