#!/usr/bin/env bash
# callsite_census.sh — enumerate every place a symbol is referenced.
#
# Run during Phase B (map) before scoring. Gives you the full impact surface
# of any refactor touching the symbol.
#
# Usage: callsite_census.sh <symbol> [run-id]
# Writes: refactor/artifacts/<run-id>/census_<symbol>.md

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <symbol> [run-id]"
  exit 2
fi

SYMBOL="$1"
RUN_ID="${2:-$(date +%Y-%m-%d)-pass-1}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "$ART"
SAFE_SYM="${SYMBOL//[^a-zA-Z0-9_]/_}"
OUT="${ART}/census_${SAFE_SYM}.md"

have() { command -v "$1" >/dev/null 2>&1; }
if ! have rg; then
  echo "error: ripgrep (rg) is required for safe callsite census scans" >&2
  exit 2
fi

SRC_TYPES='src:*{.ts,.tsx,.js,.jsx,.rs,.py,.go,.c,.cc,.cpp,.h,.hpp,.java,.rb,.kt,.swift,.scala}'
CFG_TYPES='cfg:*{.json,.yaml,.yml,.toml,.md}'

{
  printf "# Callsite census — \`%s\`\n\n" "$SYMBOL"
  printf 'Run: %s\n' "$RUN_ID"
  printf 'Generated: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$OUT"

emit_section() {
  local section="$1"
  local output="${2:-}"
  printf '\n## %s\n\n' "$section" >> "$OUT"
  if [[ -n "$output" ]]; then
    count=$(printf '%s\n' "$output" | wc -l | tr -d ' ')
    printf "%d hit(s):\n\n\`\`\`\n%s\n\`\`\`\n" "$count" "$output" >> "$OUT"
  else
    printf '_no hits_\n' >> "$OUT"
  fi
}

source_hits=$(rg -w -F -n --type-add "$SRC_TYPES" -t src -- "$SYMBOL" 2>/dev/null | head -100 || true)
emit_section "Source code — word-boundary match" "$source_hits"

import_hits=$(rg -n -F --type-add "$SRC_TYPES" -t src -- "$SYMBOL" 2>/dev/null | grep -E '(import|from|use)' | head -50 || true)
emit_section "Imports of this symbol" "$import_hits"

string_hits=$(rg -F -n --type-add "$CFG_TYPES" -t cfg -- "\"$SYMBOL\"" 2>/dev/null | head -30 || true)
emit_section "String literal references" "$string_hits"

test_dirs=()
for dir in tests __tests__ spec test; do
  [[ -d "$dir" ]] && test_dirs+=("$dir")
done
test_hits=""
if (( ${#test_dirs[@]} > 0 )); then
  test_hits=$(rg -w -F -n -- "$SYMBOL" "${test_dirs[@]}" 2>/dev/null | head -30 || true)
fi
emit_section "Tests" "$test_hits"

build_hits=$(grep -l -F -- "$SYMBOL" package.json Cargo.toml pyproject.toml go.mod Makefile Dockerfile 2>/dev/null || true)
emit_section "Build files" "$build_hits"

ci_hits=""
if [[ -d .github/workflows ]]; then
  ci_hits=$(rg -F -n -- "$SYMBOL" .github/workflows/ 2>/dev/null || true)
fi
emit_section "CI / workflows" "$ci_hits"

config_hits=$(rg -F -n -- "$SYMBOL" .env* config/ 2>/dev/null | head -20 || true)
emit_section "Config / env" "$config_hits"

doc_hits=$(rg -F -n --type md -- "$SYMBOL" 2>/dev/null | head -30 || true)
emit_section "Docs" "$doc_hits"

# Per-file aggregate
printf '\n## Per-file impact\n\n' >> "$OUT"
if temp=$(rg -w -F -l --type-add "$SRC_TYPES" -t src -- "$SYMBOL" 2>/dev/null); then
  if [[ -n "$temp" ]]; then
    printf 'files touched by this symbol:\n\n' >> "$OUT"
    printf '| file | hits |\n|------|------|\n' >> "$OUT"
    echo "$temp" | while read -r f; do
      count=$(rg -w -F -c -- "$SYMBOL" "$f" 2>/dev/null || echo 0)
      printf "| \`%s\` | %s |\n" "$f" "$count" >> "$OUT"
    done
  fi
fi

# Summary
printf '\n## Summary\n\n' >> "$OUT"
total=$(rg -w -F -c --type-add "$SRC_TYPES" -t src -- "$SYMBOL" 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')
files=$(rg -w -F -l --type-add "$SRC_TYPES" -t src -- "$SYMBOL" 2>/dev/null | wc -l | tr -d ' ')
{
  printf "Symbol: \`%s\`\n\n" "$SYMBOL"
  printf '| Metric | Count |\n|--------|-------|\n'
  printf '| Total source hits | %s |\n' "${total:-0}"
  printf '| Unique source files | %s |\n' "${files:-0}"
  printf '\n'
  if [[ "${files:-0}" -gt 10 ]]; then
    printf '⚠️  **Widely-used symbol**: >10 files reference this. Refactor is Tier-2 or Tier-3.\n'
    printf 'Consider: is renaming / extracting / moving worth the blast radius?\n'
  elif [[ "${files:-0}" -gt 3 ]]; then
    printf '**Moderately-used**: 4-10 files. Safe for Tier-2 refactor. Audit each caller.\n'
  else
    printf '**Narrowly-used**: ≤3 files. Tier-1 refactor safe.\n'
  fi
} >> "$OUT"

echo "wrote $OUT"
