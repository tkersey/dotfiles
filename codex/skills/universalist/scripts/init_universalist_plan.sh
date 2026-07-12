#!/usr/bin/env bash
set -euo pipefail
repo="${1:-.}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
template="$script_dir/../templates/universalist-plan.md"
bootstrap="$script_dir/../../ledger/scripts/ensure-ledger"

"$bootstrap" >/dev/null
exec ledger create \
  --source universalist \
  --repo "$repo" \
  --template "$template"
