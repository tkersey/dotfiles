#!/usr/bin/env bash
set -euo pipefail
repo="${1:-.}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
template="$script_dir/../templates/universalist-plan.md"
ledger_runtime="$script_dir/../../ledger/scripts/ledger-runtime"

exec "$ledger_runtime" run --min-version 0.5.0 -- create \
  --source universalist \
  --repo "$repo" \
  --template "$template"
