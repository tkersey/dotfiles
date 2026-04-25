#!/usr/bin/env bash
# rescue_phase_check.sh — validate the rescue-mission exit criterion.
#
# Per RESCUE-MISSIONS.md §"When to run the main loop vs. more triage":
# all checkboxes must be green before switching to the main loop.
#
# Usage: rescue_phase_check.sh [run-id]

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-rescue}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "$ART"
OUT="$ART/rescue_gate.md"

have() { command -v "$1" >/dev/null 2>&1; }

FAIL=0
{
  printf '# Rescue-mission gate check — %s\n\n' "$RUN_ID"
  printf 'Per RESCUE-MISSIONS.md: all boxes must be ticked before switching to the main loop.\n\n'
  printf '| # | Check | Status | Notes |\n'
  printf '|---|-------|--------|-------|\n'
} > "$OUT"

# 1. Tests pass on main
tests_cmd=""
if   [[ -f Cargo.toml ]]; then tests_cmd="cargo test --no-fail-fast"
elif [[ -f package.json ]]; then tests_cmd="$(jq -r '.scripts.test // ""' package.json)"
elif [[ -f pyproject.toml || -f setup.py ]]; then tests_cmd="pytest -q"
elif [[ -f go.mod ]]; then tests_cmd="go test ./..."
fi
if [[ -n "$tests_cmd" ]]; then
  if $tests_cmd >/tmp/test_out.txt 2>&1; then
    fails=$(grep -ohE '[0-9]+ failed' /tmp/test_out.txt | awk '{s+=$1} END{print s+0}')
    if [[ "${fails:-0}" -eq 0 ]]; then
      echo "| 1 | Tests pass on main | ✅ | |" >> "$OUT"
    else
      echo "| 1 | Tests pass on main | ❌ | $fails failures |" >> "$OUT"
      FAIL=$((FAIL + 1))
    fi
  else
    echo "| 1 | Tests pass on main | ❌ | test runner failed |" >> "$OUT"
    FAIL=$((FAIL + 1))
  fi
else
  echo "| 1 | Tests pass on main | ⚠️  | no recognized test runner |" >> "$OUT"
fi

# 2. Build passes clean
build_cmd=""
if   [[ -f Cargo.toml ]]; then build_cmd="cargo check --all-targets"
elif [[ -f package.json ]]; then build_cmd="$(jq -r '.scripts.build // .scripts[\"type-check\"] // \"npx tsc --noEmit\"' package.json)"
elif [[ -f go.mod ]]; then build_cmd="go build ./..."
fi
if [[ -n "$build_cmd" ]]; then
  if $build_cmd >/tmp/build_out.txt 2>&1; then
    echo "| 2 | Build passes clean | ✅ | |" >> "$OUT"
  else
    echo "| 2 | Build passes clean | ❌ | see /tmp/build_out.txt |" >> "$OUT"
    FAIL=$((FAIL + 1))
  fi
else
  echo "| 2 | Build passes clean | ⚠️  | no recognized build command |" >> "$OUT"
fi

# 3. Golden-path integration test exists
test_roots=()
for dir in tests __tests__ spec e2e; do
  [[ -d "$dir" ]] && test_roots+=("$dir")
done
gpath_count=0
if (( ${#test_roots[@]} > 0 )); then
  gpath_count=$(find "${test_roots[@]}" -type f \( -name '*golden*' -o -name '*integration*' -o -name '*e2e*' \) 2>/dev/null | wc -l | tr -d ' ')
fi
if [[ "${gpath_count:-0}" -ge 1 ]]; then
  echo "| 3 | Golden-path / integration test | ✅ | $gpath_count files |" >> "$OUT"
else
  echo "| 3 | Golden-path / integration test | ❌ | no golden/integration/e2e test found |" >> "$OUT"
  FAIL=$((FAIL + 1))
fi

# 4. Warning ceiling captured
if [[ -f "refactor/artifacts/warning_ceiling.txt" ]]; then
  ceil=$(cat refactor/artifacts/warning_ceiling.txt)
  echo "| 4 | Warning ceiling captured | ✅ | ceiling: $ceil |" >> "$OUT"
else
  echo "| 4 | Warning ceiling captured | ❌ | run: ./scripts/lint_ceiling.sh snapshot |" >> "$OUT"
  FAIL=$((FAIL + 1))
fi

# 5. `any` / `unwrap` counts captured (best-effort)
if have rg; then
  any_count=0
  unwrap_count=0
  if [[ -d src ]]; then
    if find src -type f \( -name '*.ts' -o -name '*.tsx' \) -print -quit 2>/dev/null | grep -q .; then
      any_count=$(rg ':\s*any\b|<any>|\bas any\b' -t ts -t tsx src/ -c 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')
    fi
    if find src -type f -name '*.rs' -print -quit 2>/dev/null | grep -q .; then
      unwrap_count=$(rg '\.unwrap\(\)' -t rust src/ -c 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')
    fi
  fi
  echo "| 5 | any-count / unwrap-count snapshot | ℹ️  | any: $any_count, unwrap: $unwrap_count (capture as ceiling if not yet) |" >> "$OUT"
fi

# 6. Recent clean CI run
if [[ -d .git ]]; then
  last_push=$(git log --format='%ar' -1 2>/dev/null || echo "unknown")
  echo "| 6 | Recent clean CI run | ℹ️  | last push $last_push — verify CI green on this commit |" >> "$OUT"
fi

# Summary
{
  printf '\n---\n\n'
  if [[ $FAIL -eq 0 ]]; then
    printf '## Verdict: READY for main loop\n\n'
    printf 'Rescue gate passes. Switch to the main refactor loop per SKILL.md.\n'
  else
    printf '## Verdict: NOT ready — %d gate(s) failed\n\n' "$FAIL"
    printf 'Continue rescue mission. Do not start the main loop until the table above is green.\n'
    printf 'See RESCUE-MISSIONS.md for per-phase guidance.\n'
  fi
} >> "$OUT"

echo "wrote $OUT"
cat "$OUT"
exit $(( FAIL > 0 ? 1 : 0 ))
