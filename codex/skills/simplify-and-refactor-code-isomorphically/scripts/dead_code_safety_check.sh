#!/usr/bin/env bash
# dead_code_safety_check.sh — run the 12-step gauntlet from DEAD-CODE-SAFETY.md.
#
# Before declaring any file/symbol/module dead, run this. Every step must pass.
#
# Usage: dead_code_safety_check.sh <path> [symbol]
#   path:   the file path being considered for deletion
#   symbol: an optional symbol name inside the file (e.g., a function or class)
#
# Writes report to refactor/artifacts/<date>/dead_code_check_<basename>.md
# Exits 0 if all checks pass (safe to propose deletion).
# Exits 1 if any check fails (DO NOT delete).

set -euo pipefail

if [[ $# -lt 1 ]]; then
  cat <<EOF
Usage: $0 <path> [symbol]

Runs the 12-step dead-code safety gauntlet from DEAD-CODE-SAFETY.md.
All 12 checks must pass before proposing deletion.

Example:
  $0 src/lib/sync-pipeline.ts syncPipeline
EOF
  exit 2
fi

PATH_TO_CHECK="$1"
SYMBOL="${2:-$(basename "$PATH_TO_CHECK" | sed -E 's/\.(ts|tsx|rs|py|go|cpp|cc|c|h|hpp)$//')}"
RUN_DATE="$(date +%Y-%m-%d)"
ART="refactor/artifacts/${RUN_DATE}"
mkdir -p "${ART}"
BASE=$(basename "$PATH_TO_CHECK" | sed 's/\//_/g')
OUT="${ART}/dead_code_check_${BASE}.md"

have() { command -v "$1" >/dev/null 2>&1; }
if ! have rg; then
  echo "error: ripgrep (rg) is required for safe dead-code safety checks" >&2
  exit 2
fi
RG=rg
count_excluding_path() {
  awk -v path="$PATH_TO_CHECK" 'index($0, path) == 0 { n++ } END { print n + 0 }'
}

{
  printf '# Dead-code safety check — %s\n\n' "$PATH_TO_CHECK"
  printf "Symbol: \`%s\`\n" "$SYMBOL"
  printf 'Date: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'Script: dead_code_safety_check.sh\n\n'
  printf '**Every check must pass. ANY fail → do NOT delete.**\n\n'
  printf '| # | Check | Count / Signal | Pass? |\n'
  printf '|---|-------|----------------|-------|\n'
} > "$OUT"

FAIL_COUNT=0

# Step 1 — Source imports
STEP1=$($RG -F "${SYMBOL}" --type-add 'source:*{.ts,.tsx,.js,.jsx,.rs,.py,.go,.c,.cc,.cpp,.h,.hpp,.rb,.kt,.swift,.scala}' -t source -l 2>/dev/null | count_excluding_path)
if [[ ${STEP1} -eq 0 ]]; then
  echo "| 1 | Source imports        | 0 | ✅ pass |" >> "$OUT"
else
  echo "| 1 | Source imports        | ${STEP1} | ❌ FAIL |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Step 2 — Dynamic references
STEP2=$({
  $RG "import\(['\"]?.*${SYMBOL}" --type-add 'source:*{.ts,.tsx,.js,.jsx,.rs,.py,.go}' -t source 2>/dev/null || true
  $RG "require\(['\"]?.*${SYMBOL}" -t ts -t tsx -t js -t jsx 2>/dev/null || true
  $RG "importlib\.import_module.*${SYMBOL}|__import__.*${SYMBOL}" -t py 2>/dev/null || true
  $RG "inventory::submit!|libloading::|ctor::ctor" -t rust 2>/dev/null | grep -i "${SYMBOL}" || true
  $RG "plugin\.Open" -t go 2>/dev/null | grep -i "${SYMBOL}" || true
  $RG "dlopen|dlsym|LoadLibrary|GetProcAddress" -t c -t cpp 2>/dev/null | grep -i "${SYMBOL}" || true
} | wc -l)
if [[ ${STEP2} -eq 0 ]]; then
  echo "| 2 | Dynamic references    | 0 | ✅ pass |" >> "$OUT"
else
  echo "| 2 | Dynamic references    | ${STEP2} | ❌ FAIL |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Step 3 — String references
STEP3=$({
  $RG -F "\"${SYMBOL}\"" --type-add 'cfg:*{.json,.yaml,.yml,.toml,.ini,.conf,.cfg,.env,.md}' -t cfg 2>/dev/null || true
  $RG -F "'${SYMBOL}'" --type-add 'cfg:*{.json,.yaml,.yml,.toml,.ini,.conf,.cfg,.env,.md}' -t cfg 2>/dev/null || true
  $RG -F "\`${SYMBOL}\`" --type-add 'cfg:*{.json,.yaml,.yml,.toml,.ini,.conf,.cfg,.env,.md}' -t cfg 2>/dev/null || true
} | count_excluding_path)
if [[ ${STEP3} -eq 0 ]]; then
  echo "| 3 | String references     | 0 | ✅ pass |" >> "$OUT"
else
  echo "| 3 | String references     | ${STEP3} | ❌ FAIL |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Step 4 — Test references
STEP4=0
for dir in tests __tests__ spec test; do
  [[ -d "$dir" ]] || continue
  n=$($RG -F "${SYMBOL}" "$dir" 2>/dev/null | count_excluding_path)
  STEP4=$((STEP4 + n))
done
# also look for *_test.rs, *_test.go, test_*.py at repo root
while IFS= read -r -d '' test_file; do
  if [[ "$test_file" != "$PATH_TO_CHECK" ]] && $RG -F -q "${SYMBOL}" "$test_file" 2>/dev/null; then
    STEP4=$((STEP4 + 1))
  fi
done < <(find . -type f \( -name '*_test.go' -o -name '*_test.rs' -o -name 'test_*.py' -o -name '*.test.ts' -o -name '*.spec.ts' -o -name '*.test.tsx' -o -name '*.spec.tsx' \) -print0 2>/dev/null)
if [[ ${STEP4} -eq 0 ]]; then
  echo "| 4 | Test references       | 0 | ✅ pass |" >> "$OUT"
else
  echo "| 4 | Test references       | ${STEP4} | ❌ FAIL |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Step 5 — Build references
STEP5=0
for f in package.json Cargo.toml pyproject.toml setup.py setup.cfg go.mod Makefile Dockerfile docker-compose.yml turbo.json nx.json rust-toolchain.toml build.rs; do
  [[ -f "$f" ]] && {
    n=$(grep -F -c -e "${SYMBOL}" -e "$(basename "$PATH_TO_CHECK")" "$f" 2>/dev/null || echo 0)
    STEP5=$((STEP5 + n))
  }
done
# CI / GH workflows
if [[ -d .github/workflows ]]; then
  n=$($RG -F "${SYMBOL}" .github/workflows/ 2>/dev/null | wc -l)
  STEP5=$((STEP5 + n))
fi
if [[ ${STEP5} -eq 0 ]]; then
  echo "| 5 | Build references      | 0 | ✅ pass |" >> "$OUT"
else
  echo "| 5 | Build references      | ${STEP5} | ❌ FAIL |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Step 6 — Feature flag lookup
STEP6=$({
  $RG -E "(FEATURE|FLAG|ENABLE|DISABLE)_\w+" -t toml -t yaml -t json -t env 2>/dev/null | grep -F -i -- "${SYMBOL}" || true
  if [[ -f .env ]]; then grep -F -i -- "${SYMBOL}" .env || true; fi
  if [[ -f .env.example ]]; then grep -F -i -- "${SYMBOL}" .env.example || true; fi
} | wc -l)
if [[ ${STEP6} -eq 0 ]]; then
  echo "| 6 | Feature flag lookup   | 0 | ✅ pass |" >> "$OUT"
else
  echo "| 6 | Feature flag lookup   | ${STEP6} | ⚠️  WARN (see below) |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Step 7 — Doc references
STEP7=$({
  $RG -F "${SYMBOL}" --type md 2>/dev/null | awk -v path="$PATH_TO_CHECK" 'index($0, path) == 0' || true
  if [[ -d docs ]]; then $RG -F "${SYMBOL}" docs/ 2>/dev/null || true; fi
  if [[ -d ADR ]]; then $RG -F "${SYMBOL}" ADR/ 2>/dev/null || true; fi
} | wc -l)
if [[ ${STEP7} -eq 0 ]]; then
  echo "| 7 | Doc references        | 0 | ✅ pass |" >> "$OUT"
else
  echo "| 7 | Doc references        | ${STEP7} | ❌ FAIL |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Step 8 — Git history signal
if [[ -e "$PATH_TO_CHECK" ]] && git rev-parse --git-dir >/dev/null 2>&1; then
  LAST_COMMIT=$(git log --follow --format='%h %s' -1 "$PATH_TO_CHECK" 2>/dev/null || echo "unknown")
  AGE_DAYS=$(git log --follow --format='%ar' -1 "$PATH_TO_CHECK" 2>/dev/null || echo "unknown")
  SUSPECT_MSG=0
  echo "$LAST_COMMIT" | grep -qiE 'scaffold|initial|wip|placeholder|intended|stub|future' && SUSPECT_MSG=1
  if [[ ${SUSPECT_MSG} -eq 1 ]]; then
    echo "| 8 | Git history signal    | last: \`${LAST_COMMIT}\` (${AGE_DAYS}) — SUSPECT (scaffold/intended/wip) | ❌ FAIL |" >> "$OUT"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    echo "| 8 | Git history signal    | last: \`${LAST_COMMIT}\` (${AGE_DAYS}) | ✅ pass |" >> "$OUT"
  fi
else
  echo "| 8 | Git history signal    | N/A | ⚠️  skipped |" >> "$OUT"
fi

# Step 9 — Companion file signal
COMPANIONS=()
BASE_NO_EXT="${PATH_TO_CHECK%.*}"
for ext in .test.ts .spec.ts .stories.tsx .mdx .md _test.go _test.rs _test.py; do
  [[ -f "${BASE_NO_EXT}${ext}" ]] && COMPANIONS+=("${BASE_NO_EXT}${ext}")
done
if [[ ${#COMPANIONS[@]} -eq 0 ]]; then
  echo "| 9 | Companion files       | none | ✅ pass |" >> "$OUT"
else
  echo "| 9 | Companion files       | ${COMPANIONS[*]} | ❌ FAIL (companions encode intent) |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Step 10 — Named intent signal
LOWERED=$(echo "$PATH_TO_CHECK" | tr '[:upper:]' '[:lower:]')
if echo "$LOWERED" | grep -qE 'intended|future|planned|todo|stub|wip|scaffold|placeholder|pending|draft|_v[0-9]|_new'; then
  echo "| 10| Named intent signal   | contains intent keyword | ❌ FAIL (name signals intent) |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
else
  echo "| 10| Named intent signal   | no intent keyword | ✅ pass |" >> "$OUT"
fi

# Step 11 — Owner check
if git rev-parse --git-dir >/dev/null 2>&1 && [[ -e "$PATH_TO_CHECK" ]]; then
  OWNER=$(git log --format='%an' "$PATH_TO_CHECK" 2>/dev/null | sort | uniq -c | sort -rn | head -1 | awk '{$1=""; print $0}' | xargs)
  echo "| 11| Owner check           | ${OWNER:-unknown} — NOT YET ASKED | ⚠️  FAIL until asked |" >> "$OUT"
  FAIL_COUNT=$((FAIL_COUNT + 1))
else
  echo "| 11| Owner check           | N/A | ⚠️  skipped |" >> "$OUT"
fi

# Step 12 — User approval
echo "| 12| Explicit user approval| NOT YET GIVEN | ⚠️  FAIL until approved |" >> "$OUT"
FAIL_COUNT=$((FAIL_COUNT + 1))

{
  printf '\n---\n\n'
  if [[ ${FAIL_COUNT} -eq 0 ]]; then
    printf '## Verdict: Technically safe to propose deletion\n\n'
    printf 'All automated checks pass. You may now:\n'
    printf "1. Move \`%s\` to \`refactor/_to_delete/\` (preserves git history).\n" "$PATH_TO_CHECK"
    printf '2. Ask the file owner and the user, presenting this report.\n'
    printf "3. Wait for explicit written approval before any hard delete.\n\n"
  else
    printf '## Verdict: DO NOT DELETE — %d check(s) failed or pending\n\n' "$FAIL_COUNT"
    printf 'Per [DEAD-CODE-SAFETY.md](references/DEAD-CODE-SAFETY.md), any fail is blocking.\n\n'
    printf 'Read the failures above. For each:\n'
    printf '- If real usage: leave the file alone.\n'
    printf '- If false positive: document why in the ledger and still do not delete (AGENTS.md Rule 1).\n\n'
    printf 'Recommended action: leave the file in place, file a bead for follow-up investigation.\n\n'
  fi
} >> "$OUT"

echo "wrote $OUT"
echo "fail count: $FAIL_COUNT"
exit $(( FAIL_COUNT > 0 ? 1 : 0 ))
