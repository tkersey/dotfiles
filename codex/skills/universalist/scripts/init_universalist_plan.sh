#!/usr/bin/env bash
set -euo pipefail
plan="${1:-.universalist-plan.md}"
if [ -e "$plan" ]; then
  echo "plan already exists: $plan" >&2
  exit 0
fi
cat > "$plan" <<'EOF'
# Universalist Plan

## Track:
## Signal:
## Construction:
## Canonical boundary artifact:
## Why this construction:
## Seam / files:
## Public boundaries touched:
## Wire/storage compatibility plan:
## Verification command(s):
## Runtime-only leftovers:
## Status: planned
## Next seam:
EOF
echo "created $plan"
