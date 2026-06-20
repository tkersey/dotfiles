#!/bin/sh
set -eu

DOTFILES=${1:-}
CODEX_HOME=${CODEX_HOME:-"$HOME/.codex"}
MEMORY_ROOT="$CODEX_HOME/memories"
EXT_ROOT="$MEMORY_ROOT/extensions"

if [ -z "$DOTFILES" ] || [ ! -d "$DOTFILES/codex/memories/extensions" ]; then
  echo "usage: $0 /path/to/dotfiles" >&2
  exit 2
fi

for path in "$MEMORY_ROOT" "$EXT_ROOT"; do
  if [ -L "$path" ]; then
    echo "refusing to deploy through symlink: $path" >&2
    exit 3
  fi
done

mkdir -p "$EXT_ROOT"

for extension in harness learnings negative-ledger synesthesia; do
  source="$DOTFILES/codex/memories/extensions/$extension/instructions.md"
  live="$EXT_ROOT/$extension"
  if [ ! -f "$source" ]; then
    echo "missing source instructions: $source" >&2
    exit 4
  fi
  if [ -L "$live" ]; then
    echo "refusing to deploy into symlinked extension directory: $live" >&2
    exit 3
  fi
  mkdir -p "$live/notes" "$live/resources"
  install -m 0600 "$source" "$live/instructions.md"
  echo "deployed $extension/instructions.md"
done

printf '%s\n' "Chronicle and ad_hoc were not modified. Existing notes/resources were preserved."
