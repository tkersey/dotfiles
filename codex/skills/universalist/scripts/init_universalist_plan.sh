#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: init_universalist_plan.sh [--file PATH] [--track NAME] [--signal TEXT] [--construction TEXT] [--seam TEXT] [--force]

Creates a .universalist-plan.md file if one does not already exist.
EOF
  exit 1
}

target=".universalist-plan.md"
track=""
signal=""
construction=""
seam=""
force="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      shift
      [[ $# -gt 0 ]] || usage
      target="$1"
      ;;
    --track)
      shift
      [[ $# -gt 0 ]] || usage
      track="$1"
      ;;
    --signal)
      shift
      [[ $# -gt 0 ]] || usage
      signal="$1"
      ;;
    --construction)
      shift
      [[ $# -gt 0 ]] || usage
      construction="$1"
      ;;
    --seam)
      shift
      [[ $# -gt 0 ]] || usage
      seam="$1"
      ;;
    --force)
      force="true"
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      ;;
  esac
  shift
done

if [[ -e "$target" && "$force" != "true" ]]; then
  echo "Refusing to overwrite existing file: $target" >&2
  echo "Use --force if you want to replace it." >&2
  exit 1
fi

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

cat > "$target" <<EOF
# Universalist Plan

## Track: ${track}
## Signal: ${signal}
## Construction: ${construction}
## Why this construction:
## Seam / files: ${seam}
## Public boundaries touched:
## Wire/storage compatibility plan:
## Verification command(s):
## Runtime-only leftovers:
## Status: planned
## Next seam:

## Change log
- [${timestamp}] initialized
EOF

echo "Wrote $target"
