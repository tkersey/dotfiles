#!/usr/bin/env bash
set -euo pipefail
file="${1:-.universalist-plan.md}"
if [ -e "$file" ]; then
  echo "$file already exists" >&2
  exit 0
fi
cat > "$file" <<'OUT'
# Universalist Plan

## Track:
## Signal:
## Construction:
## Canonical boundary artifact:
## Freyd/AFT boundary diagnostic:
## Why this construction:
## Seam / files:
## Public boundaries touched:
## Wire/storage compatibility plan:
## Verification command(s):
## Runtime-only leftovers:
## Status: planned
## Next seam:
OUT
echo "created $file"
