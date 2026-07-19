#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

uv run --with pyyaml python3 scripts/compile_universal_problem.py --validate-registry >/dev/null
PYTHONDONTWRITEBYTECODE=1 uv run --with pyyaml python3 tests/test_universal_problem_compiler.py
PYTHONDONTWRITEBYTECODE=1 uv run --with pyyaml python3 tests/test_emitters.py

typescript_decoder="$(python3 scripts/emit_boundary_adapter.py decoder typescript)"
[[ "$typescript_decoder" == *'DecodeResult<CoreShape>'* ]]
[[ "$typescript_decoder" != *'input as CoreShape'* ]]
[[ "$typescript_decoder" != *'return input'* ]]

python_decoder="$(python3 scripts/emit_boundary_adapter.py decoder python)"
[[ "$python_decoder" == *'CoreShape | DecodeError'* ]]
[[ "$python_decoder" != *'typing import Any'* ]]
[[ "$python_decoder" != *'return value'* ]]

if python3 scripts/emit_boundary_adapter.py typescript decoder >/dev/null 2>&1; then
  echo "adapter argument order must fail closed" >&2
  exit 1
fi

scaffold="$(python3 scripts/emit_scaffold.py boundary typescript)"
for heading in \
  '## Ordinary candidate' \
  '## Universal shadow' \
  '## Material architectural delta' \
  '## Boundary and compatibility plan' \
  '## Runtime-only leftovers'; do
  [[ "$scaffold" == *"$heading"* ]] || {
    echo "scaffold missing $heading" >&2
    exit 1
  }
done

echo "check_universal_problem: ok"
