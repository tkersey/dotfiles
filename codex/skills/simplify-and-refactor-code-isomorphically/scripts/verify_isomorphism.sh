#!/usr/bin/env bash
# Run the five verification gates after a refactor commit.
#
# Usage:  ./verify_isomorphism.sh [run-id]
# Returns exit 0 if all gates pass, exit 1 if any fails.
# Reads baseline from refactor/artifacts/<run-id>/

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-pass-1}"
ART="refactor/artifacts/${RUN_ID}"

if [[ ! -d "${ART}" ]]; then
  echo "[verify] no baseline at ${ART} — run baseline.sh first" >&2
  exit 2
fi

fail=0

echo "[verify] gate 1/5 — tests"
TEST_CMD="${TEST_CMD:-}"
if [[ -z "${TEST_CMD}" ]]; then
  if   [[ -f Cargo.toml ]]; then TEST_CMD="cargo test --no-fail-fast"
  elif [[ -f package.json ]]; then TEST_CMD="$(jq -r '.scripts.test // "echo NO_TEST_SCRIPT"' package.json)"
  elif [[ -f pyproject.toml || -f setup.py ]]; then TEST_CMD="pytest -q"
  elif [[ -f go.mod ]]; then TEST_CMD="go test ./..."
  fi
fi
{ ${TEST_CMD}; } 2>&1 | tee "${ART}/tests_after.txt" || true
# Compare pass count, not just exit code
if [[ -f "${ART}/tests_before.txt" ]]; then
  base_pass=$(grep -ohE '[0-9]+ passed' "${ART}/tests_before.txt" | awk '{ s+=$1 } END { print s+0 }')
  curr_pass=$(grep -ohE '[0-9]+ passed' "${ART}/tests_after.txt"  | awk '{ s+=$1 } END { print s+0 }')
  if [[ "${base_pass}" != "${curr_pass}" ]]; then
    echo "[verify] FAIL — test pass count changed: ${base_pass} -> ${curr_pass}"
    fail=$((fail + 1))
  else
    echo "[verify] PASS — tests ${curr_pass}/${curr_pass}"
  fi
fi

echo "[verify] gate 2/5 — goldens"
if [[ -f "${ART}/goldens/checksums.txt" ]]; then
  if [[ -n "${BIN_PATH:-}" ]]; then
    fail_g=0
    for input in "${ART}/goldens/inputs"/*; do
      [[ -e "$input" ]] || continue
      name=$(basename "$input")
      diff <("${BIN_PATH}" "$input" 2>/dev/null) "${ART}/goldens/outputs/${name}.stdout" >/dev/null \
        || { echo "[verify]   golden DIFF on $name"; fail_g=$((fail_g + 1)); }
    done
    if [[ ${fail_g} -gt 0 ]]; then
      echo "[verify] FAIL — ${fail_g} golden(s) differ"
      fail=$((fail + 1))
    else
      echo "[verify] PASS — all goldens identical"
    fi
  else
    echo "[verify] SKIP — set BIN_PATH to verify goldens"
  fi
else
  echo "[verify] SKIP — no goldens captured"
fi

echo "[verify] gate 3/5 — typecheck/lints (warning count must not grow)"
LINT_CMD="${LINT_CMD:-}"
if [[ -z "${LINT_CMD}" ]]; then
  if   [[ -f Cargo.toml ]]; then LINT_CMD="cargo clippy --all-targets -- -D warnings"
  elif [[ -f package.json ]]; then LINT_CMD="npx tsc --noEmit"
  elif [[ -f pyproject.toml || -f setup.py ]]; then LINT_CMD="mypy --strict src/"
  elif [[ -f go.mod ]]; then LINT_CMD="go vet ./..."
  fi
fi
{ ${LINT_CMD}; } 2>&1 | tee "${ART}/lint_after.txt" || true
if [[ -f "${ART}/lint_before.txt" ]]; then
  before_warn=$(grep -cE 'warning|error' "${ART}/lint_before.txt" || true)
  after_warn=$(grep -cE 'warning|error' "${ART}/lint_after.txt"  || true)
  if [[ "${after_warn}" -gt "${before_warn}" ]]; then
    echo "[verify] FAIL — lint warnings grew: ${before_warn} -> ${after_warn}"
    fail=$((fail + 1))
  else
    echo "[verify] PASS — lint warnings ${before_warn} -> ${after_warn}"
  fi
fi

echo "[verify] gate 4/5 — LOC delta"
if command -v tokei >/dev/null 2>&1; then
  tokei --output json . > "${ART}/loc_after.json" 2>/dev/null || true
  if [[ -f "${ART}/loc_before.json" ]]; then
    base=$(jq '.Total.code' "${ART}/loc_before.json")
    curr=$(jq '.Total.code' "${ART}/loc_after.json")
    delta=$(( curr - base ))
    echo "[verify]   LOC ${base} -> ${curr} (${delta})"
    [[ ${delta} -le 0 ]] && echo "[verify] PASS — net negative LOC" || echo "[verify] WARN — net positive LOC"
  fi
fi

echo "[verify] gate 5/5 — no new lint disables"
if git diff HEAD~1 -- "*.rs" "*.ts" "*.tsx" "*.py" "*.go" 2>/dev/null \
   | grep -E '^\+.*(#\[allow|//\s*eslint-disable|#\s*type:\s*ignore|//\s*noqa)' >/dev/null; then
  echo "[verify] FAIL — diff introduces new lint disables (#[allow], eslint-disable, noqa, type:ignore)"
  fail=$((fail + 1))
else
  echo "[verify] PASS — no new lint disables"
fi

echo
if [[ ${fail} -eq 0 ]]; then
  echo "[verify] ALL GATES PASS"
  exit 0
else
  echo "[verify] ${fail} GATE(S) FAILED — DO NOT COMMIT"
  exit 1
fi
