#!/usr/bin/env bash
# Capture the pre-refactor baseline: tests, goldens, LOC, complexity, lints.
#
# Usage:  ./baseline.sh [run-id]
# Output: refactor/artifacts/<run-id>/{baseline.md, tests_before.txt, loc_before.json, ...}
#
# Detects language by repo file types and chooses appropriate test/lint commands.
# Override via env:  TEST_CMD, LINT_CMD, BIN_PATH, GOLDEN_INPUTS_DIR

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-pass-1}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "${ART}/goldens/inputs" "${ART}/goldens/outputs"

echo "[baseline] run-id: ${RUN_ID}"
echo "[baseline] artifact dir: ${ART}"

#--- detect project type
RUST=0; TS=0; PY=0; GO=0; CPP=0
[[ -f Cargo.toml ]] && RUST=1
[[ -f package.json ]] && TS=1
[[ -f pyproject.toml || -f setup.py || -f requirements.txt ]] && PY=1
[[ -f go.mod ]] && GO=1
[[ -f CMakeLists.txt || -n "$(find . -maxdepth 3 -name '*.cpp' -o -name '*.cc' 2>/dev/null | head -1)" ]] && CPP=1

#--- choose default test command if not overridden
if [[ -z "${TEST_CMD:-}" ]]; then
  if   [[ ${RUST} -eq 1 ]]; then TEST_CMD="cargo test --no-fail-fast"
  elif [[ ${TS}   -eq 1 ]]; then TEST_CMD="$(jq -r '.scripts.test // "echo NO_TEST_SCRIPT && exit 0"' package.json)"
  elif [[ ${PY}   -eq 1 ]]; then TEST_CMD="pytest -q"
  elif [[ ${GO}   -eq 1 ]]; then TEST_CMD="go test ./..."
  elif [[ ${CPP}  -eq 1 ]]; then TEST_CMD="ctest --output-on-failure"
  else TEST_CMD="echo NO_TEST_DETECTED && exit 0"
  fi
fi

#--- choose default lint command if not overridden
if [[ -z "${LINT_CMD:-}" ]]; then
  if   [[ ${RUST} -eq 1 ]]; then LINT_CMD="cargo clippy --all-targets -- -D warnings"
  elif [[ ${TS}   -eq 1 ]]; then LINT_CMD="npx tsc --noEmit"
  elif [[ ${PY}   -eq 1 ]]; then LINT_CMD="mypy --strict src/ 2>/dev/null || mypy ."
  elif [[ ${GO}   -eq 1 ]]; then LINT_CMD="go vet ./..."
  elif [[ ${CPP}  -eq 1 ]]; then LINT_CMD="echo SKIP_CPP_LINT"
  fi
fi

#--- run tests
echo "[baseline] tests: ${TEST_CMD}"
{ ${TEST_CMD}; echo "[baseline] exit=$?"; } 2>&1 | tee "${ART}/tests_before.txt" || true

#--- LOC
if command -v tokei >/dev/null 2>&1; then
  tokei --output json . > "${ART}/loc_before.json" 2>/dev/null || tokei . > "${ART}/loc_before.txt"
fi
if command -v scc >/dev/null 2>&1; then
  scc --by-file --format json . > "${ART}/scc_before.json" 2>/dev/null || true
fi

#--- lint / typecheck
echo "[baseline] lints: ${LINT_CMD}"
{ ${LINT_CMD}; echo "[baseline] exit=$?"; } 2>&1 | tee "${ART}/lint_before.txt" || true

#--- goldens
if [[ -n "${BIN_PATH:-}" && -d "${GOLDEN_INPUTS_DIR:-${ART}/goldens/inputs}" ]]; then
  echo "[baseline] capturing goldens via ${BIN_PATH}"
  for input in "${GOLDEN_INPUTS_DIR:-${ART}/goldens/inputs}"/*; do
    [[ -e "$input" ]] || continue
    name=$(basename "$input")
    "${BIN_PATH}" "$input" > "${ART}/goldens/outputs/${name}.stdout" 2> "${ART}/goldens/outputs/${name}.stderr"
    echo "$?" > "${ART}/goldens/outputs/${name}.exit"
  done
  ( cd "${ART}/goldens/outputs" && find . -type f -exec sha256sum {} \; ) > "${ART}/goldens/checksums.txt"
  echo "[baseline] goldens hashed: $(wc -l < "${ART}/goldens/checksums.txt") files"
else
  echo "[baseline] goldens skipped (set BIN_PATH and provide ${ART}/goldens/inputs/)"
fi

#--- summary
{
  echo "# Baseline — ${RUN_ID}"
  echo
  echo "Captured: $(date -u +'%Y-%m-%d %H:%M UTC')"
  echo "Branch: $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)"
  echo
  echo "## Test"
  echo "- Command: \`${TEST_CMD}\`"
  echo "- Output: tests_before.txt"
  echo
  echo "## LOC"
  if [[ -f "${ART}/loc_before.json" ]]; then
    echo "- Tool: tokei (json)"
  fi
  if [[ -f "${ART}/scc_before.json" ]]; then
    echo "- Complexity: scc"
  fi
  echo
  echo "## Lint / typecheck"
  echo "- Command: \`${LINT_CMD}\`"
  echo "- Output: lint_before.txt"
  echo
  echo "## Goldens"
  if [[ -f "${ART}/goldens/checksums.txt" ]]; then
    echo "- Files: $(wc -l < "${ART}/goldens/checksums.txt")"
    echo "- Checksums: goldens/checksums.txt"
  else
    echo "- (none captured — set BIN_PATH and provide goldens/inputs/)"
  fi
} > "${ART}/baseline.md"

echo "[baseline] done. See ${ART}/baseline.md"
