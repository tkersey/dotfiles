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

require_seq_identity() {
  local capabilities
  capabilities="$(seq capabilities --format json 2>/dev/null)" || {
    printf '%s\n' 'universalist resolved a seq command that is not Skills Seq: capabilities unavailable' >&2
    exit 2
  }
  python3 - "$capabilities" <<'PY'
import json, sys
try:
    payload=json.loads(sys.argv[1])
except Exception as exc:
    raise SystemExit(f'invalid Skills Seq capabilities JSON: {exc}')
features=payload.get('features', payload)
if features.get('skill_contract_v1') is not True:
    raise SystemExit('resolved seq command lacks Skills Seq skill_contract_v1')
PY
  seq skill-contract --help >/dev/null 2>&1 || {
    printf '%s\n' 'resolved seq command lacks the Skills Seq skill-contract surface' >&2
    exit 2
  }
}

require_ledger_identity() {
  local create_help emit_help
  create_help="$(ledger create --help 2>&1)" || {
    printf '%s\n' 'resolved ledger command lacks the Universalist plan-create surface' >&2
    exit 2
  }
  emit_help="$(ledger emit --help 2>&1)" || {
    printf '%s\n' 'resolved ledger command lacks the Universalist decision-receipt surface' >&2
    exit 2
  }
  for token in --source --repo --template; do
    [[ "$create_help" == *"$token"* ]] || {
      printf 'resolved ledger create command is missing %s\n' "$token" >&2
      exit 2
    }
  done
  for token in --contract --selected-route --write-plan; do
    [[ "$emit_help" == *"$token"* ]] || {
      printf 'resolved ledger emit command is missing %s\n' "$token" >&2
      exit 2
    }
  done
}

"$bootstrap" >/dev/null
require_version ledger "$minimum_ledger_version"
require_version seq "$minimum_seq_version"
require_ledger_identity
require_seq_identity

exec ledger create \
  --source universalist \
  --repo "$repo" \
  --template "$template"
