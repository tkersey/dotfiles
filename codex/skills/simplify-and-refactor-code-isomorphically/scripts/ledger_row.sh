#!/usr/bin/env bash
# ledger_row.sh — produce a LEDGER.md row from the current git state.
#
# Run after a commit completes. Extracts the LOC delta, reads the commit
# message for the isomorphism card, emits an append-ready markdown row.
#
# Usage: ledger_row.sh [run-id] [candidate-id]
#   Defaults: <date>-pass-1, D?

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-pass-1}"
CAND="${2:-D?}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "$ART"
LEDGER="$ART/LEDGER.md"

have() { command -v "$1" >/dev/null 2>&1; }

SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "nocommit")
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | tr '\n' ' ' | sed 's/ $//')

# Source-line delta against parent. Avoid temp worktrees; total LOC is captured
# by baseline artifacts, while ledger needs a per-commit delta signal.
if git rev-parse HEAD~1 >/dev/null 2>&1; then
  loc_before="parent"
  loc_after="HEAD"
  loc_delta=$(git diff --numstat HEAD~1 HEAD -- \
    | awk '$1 ~ /^[0-9]+$/ && $2 ~ /^[0-9]+$/ {s+=$1-$2} END{print s+0}')
else
  loc_before="?"
  loc_after="?"
  loc_delta="?"
fi

# Test counts (best-effort: parse the last test-output file if present)
TESTS_BEFORE="?"
TESTS_AFTER="?"
if [[ -f "$ART/tests_before.txt" ]]; then
  TESTS_BEFORE=$(grep -ohE '[0-9]+ passed' "$ART/tests_before.txt" | awk '{ s+=$1 } END{ print s+0 }')
fi
if [[ -f "$ART/tests_after.txt" ]]; then
  TESTS_AFTER=$(grep -ohE '[0-9]+ passed' "$ART/tests_after.txt" | awk '{ s+=$1 } END{ print s+0 }')
fi

# Goldens check
GOLDENS="?"
[[ -f "$ART/goldens/checksums.txt" ]] && GOLDENS="✓ hashed (verify externally)"

# Create ledger if missing
if [[ ! -f "$LEDGER" ]]; then
  cat > "$LEDGER" <<EOF
# Refactor Ledger — ${RUN_ID}

| Order | ID  | Commit  | File(s)      | LOC before | LOC after | Δ    | Tests       | Goldens | Lints |
|-------|-----|---------|--------------|------------|-----------|------|-------------|---------|-------|
EOF
fi

# Determine order (row count of existing table body)
ORDER=$(grep -c '^|' "$LEDGER" 2>/dev/null | awk '{print $1-2}')
(( ORDER < 1 )) && ORDER=1

# Emit row
ROW=$(printf '| %d | %s | %s | %s | %s | %s | %s | %s/%s | %s | 0Δ |\n' \
  "$ORDER" "$CAND" "$SHA" "$CHANGED_FILES" "$loc_before" "$loc_after" "$loc_delta" "$TESTS_BEFORE" "$TESTS_AFTER" "$GOLDENS")

# Append using flock if available, else plain
if have flock; then
  {
    flock 9
    printf '%s' "$ROW" >&9
  } 9>>"$LEDGER"
else
  printf '%s' "$ROW" >> "$LEDGER"
fi

echo "appended to $LEDGER:"
echo "  $ROW"
