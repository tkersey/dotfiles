#!/usr/bin/env bash
set -euo pipefail
repo="${1:-.}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
template="$script_dir/../templates/universalist-plan.md"

exec ledger create \
  --source universalist \
  --repo "$repo" \
  --template "$template"
