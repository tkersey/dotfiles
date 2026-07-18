#!/usr/bin/env bash
set -euo pipefail

dir="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$dir/.." && pwd)"
cd "$root"

status=0
check_command() {
  local command_name="$1"
  local required="$2"
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'ok      %-12s %s\n' "$command_name" "$($command_name --version 2>/dev/null | head -1 || true)"
  elif [[ "$required" == required ]]; then
    printf 'missing %-12s required\n' "$command_name" >&2
    status=1
  else
    printf 'missing %-12s optional for isolated package checks\n' "$command_name"
  fi
}

check_command uv required
check_command python3 required
check_command bash required
check_command ledger optional
check_command seq optional

uv run --with pyyaml python3 scripts/validate_universal_registry.py --check-references || status=1
UNIVERSALIST_SKIP_EXTERNAL="${UNIVERSALIST_SKIP_EXTERNAL:-1}" bash scripts/check_universalist.sh || status=1

if [[ "$status" -ne 0 ]]; then
  echo 'universalist doctor: failed' >&2
  exit "$status"
fi

echo 'universalist doctor: ok'
