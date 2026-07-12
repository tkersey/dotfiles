#!/usr/bin/env bash
set -euo pipefail
repo="${1:-.}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
template="$script_dir/../templates/universalist-plan.md"
bootstrap="$script_dir/../../ledger/scripts/ensure-ledger"
minimum_version="0.5.3"

version_at_least() {
  local actual_core="${1%%[-+]*}"
  local required_core="${2%%[-+]*}"
  local actual_major actual_minor actual_patch actual_extra
  local required_major required_minor required_patch required_extra

  IFS=. read -r actual_major actual_minor actual_patch actual_extra <<<"$actual_core"
  IFS=. read -r required_major required_minor required_patch required_extra <<<"$required_core"
  if [[ -n "${actual_extra:-}" || -n "${required_extra:-}" ]] ||
    [[ ! "$actual_major" =~ ^[0-9]+$ || ! "$actual_minor" =~ ^[0-9]+$ || ! "$actual_patch" =~ ^[0-9]+$ ]] ||
    [[ ! "$required_major" =~ ^[0-9]+$ || ! "$required_minor" =~ ^[0-9]+$ || ! "$required_patch" =~ ^[0-9]+$ ]]; then
    return 1
  fi

  ((actual_major > required_major)) ||
    ((actual_major == required_major && actual_minor > required_minor)) ||
    ((actual_major == required_major && actual_minor == required_minor && actual_patch >= required_patch))
}

"$bootstrap" >/dev/null
ledger_version="$(ledger --version)"
if ! version_at_least "$ledger_version" "$minimum_version"; then
  printf 'universalist requires ledger >= %s; found %s\n' "$minimum_version" "$ledger_version" >&2
  exit 2
fi
exec ledger create \
  --source universalist \
  --repo "$repo" \
  --template "$template"
