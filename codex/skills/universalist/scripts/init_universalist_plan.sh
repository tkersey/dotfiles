#!/usr/bin/env bash
set -euo pipefail
repo="${1:-.}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
template="$script_dir/../templates/universalist-plan.md"
bootstrap="$script_dir/../../ledger/scripts/ensure-ledger"
minimum_ledger_version="0.10.4"
minimum_seq_version="0.3.51"

extract_version() {
  local raw="$1"
  if [[ "$raw" =~ ([0-9]+\.[0-9]+\.[0-9]+) ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}

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

require_version() {
  local command_name="$1"
  local minimum="$2"
  local raw actual
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'universalist requires %s >= %s; command not found\n' "$command_name" "$minimum" >&2
    exit 2
  fi
  raw="$($command_name --version 2>&1)"
  if ! actual="$(extract_version "$raw")" || ! version_at_least "$actual" "$minimum"; then
    printf 'universalist requires %s >= %s; found %s\n' "$command_name" "$minimum" "$raw" >&2
    exit 2
  fi
}

"$bootstrap" >/dev/null
require_version ledger "$minimum_ledger_version"
require_version seq "$minimum_seq_version"

exec ledger create \
  --source universalist \
  --repo "$repo" \
  --template "$template"
