#!/bin/sh
set -eu

PACKAGE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TARGET=${1:-}

if [ -z "$TARGET" ]; then
  echo "usage: $0 /path/to/dotfiles" >&2
  exit 2
fi

if [ ! -d "$TARGET/codex" ]; then
  echo "target does not look like the dotfiles repo: $TARGET" >&2
  exit 2
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP="$TARGET/.memory-source-backups/$STAMP"
mkdir -p "$BACKUP"

find "$PACKAGE_ROOT/codex" -type f ! -name 'AGENTS.memory-source-routing.md' | while IFS= read -r src; do
  rel=${src#"$PACKAGE_ROOT/"}
  dst="$TARGET/$rel"
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    mkdir -p "$BACKUP/$(dirname "$rel")"
    cp -a "$dst" "$BACKUP/$rel"
    if [ -L "$dst" ]; then
      rm "$dst"
    fi
  fi
  mkdir -p "$(dirname "$dst")"
  cp -p "$src" "$dst"
  echo "installed $rel"
done

mkdir -p "$TARGET/codex"
cp -p "$PACKAGE_ROOT/codex/AGENTS.memory-source-routing.md" \
  "$TARGET/codex/AGENTS.memory-source-routing.md"

echo "backup: $BACKUP"
echo "manual merge required: codex/AGENTS.memory-source-routing.md"
