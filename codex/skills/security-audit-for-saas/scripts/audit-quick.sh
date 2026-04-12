#!/usr/bin/env bash
# audit-quick.sh
#
# 60-second security surface audit for a SaaS project.
# Runs all the quick-scan scripts and emits a summary report.
#
# Usage: ./audit-quick.sh [repo-root]
# Exit 0 = clean
# Exit >0 = findings (see report)

set -u

REPO_ROOT="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Quick Security Audit: $REPO_ROOT"
echo "║   Time: $(date -Iseconds)"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

TOTAL_FINDINGS=0

# Run each scanner
for scanner in leak-scan.sh find-fail-open.sh; do
  if [ -x "$SCRIPT_DIR/$scanner" ]; then
    echo "══════════════════════════════════════════════════════════════"
    echo "Running: $scanner"
    echo "══════════════════════════════════════════════════════════════"
    "$SCRIPT_DIR/$scanner" "$REPO_ROOT" || TOTAL_FINDINGS=$((TOTAL_FINDINGS + $?))
    echo
  fi
done

# API auth mapping
if [ -x "$SCRIPT_DIR/api-auth-mapper.sh" ]; then
  echo "══════════════════════════════════════════════════════════════"
  echo "API Route Auth Mapping"
  echo "══════════════════════════════════════════════════════════════"
  if ! "$SCRIPT_DIR/api-auth-mapper.sh" "$REPO_ROOT"; then
    echo "⚠ API route auth mapping could not complete"
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
  fi
  echo
fi

# Quick file existence checks
echo "══════════════════════════════════════════════════════════════"
echo "File Existence Checks"
echo "══════════════════════════════════════════════════════════════"

check_file() {
  local path="$1"
  local desc="$2"
  if [ -e "$REPO_ROOT/$path" ]; then
    echo "✓ $desc: $path"
  else
    echo "✗ $desc: MISSING ($path)"
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
  fi
}

check_file "src/env.ts" "Centralized env access"
check_file "src/lib/csrf.ts" "CSRF module"
check_file "src/lib/rate-limit.ts" "Rate limit module"
check_file ".gitignore" ".gitignore"

# Verify .env.local not tracked
if [ -d "$REPO_ROOT/.git" ]; then
  if tracked_files=$(cd "$REPO_ROOT" && git ls-files 2>/dev/null); then
    if printf '%s\n' "$tracked_files" | grep -q '^\.env\.local$'; then
      echo "✗ CRITICAL: .env.local tracked in git"
      TOTAL_FINDINGS=$((TOTAL_FINDINGS + 10))
    else
      echo "✓ .env.local not tracked"
    fi
  else
    echo "⚠ Could not inspect tracked files with git ls-files"
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
  fi
fi

# Check for common security files
check_file "tests/integration/security" "Security test suite"
check_file "supabase/migrations" "Supabase migrations (for RLS)"

echo
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Quick Audit Summary"
echo "╚══════════════════════════════════════════════════════════════╝"
echo
if [ "$TOTAL_FINDINGS" -eq 0 ]; then
  echo "✓ No findings in quick scan."
  echo
  echo "NEXT STEPS:"
  echo "  1. Run full 15-domain sweep (see SKILL.md)"
  echo "  2. Apply cognitive operators (see references/OPERATORS.md)"
  echo "  3. Run red team exercises (see references/ATTACK-SCENARIOS.md)"
  exit 0
else
  echo "⚠ Found $TOTAL_FINDINGS potential issues in quick scan."
  echo
  echo "NEXT STEPS:"
  echo "  1. Review each finding above"
  echo "  2. Run the full comprehensive audit (see references/PROMPT-ARCHETYPES.md Archetype 1)"
  echo "  3. Create beads for each confirmed finding"
  exit 1
fi
