#!/usr/bin/env bash
# <SIBLING>/audit/regression_tests/R-<NNN>__<short>.test.sh
# Pins: <one-line summary of the contract this rec established>
# Anchor: [Q-NNN] from references/exemplars/QUOTE-BANK.md
# Pattern: Pattern <N> from references/rubric/REGRESSION-TEST-PATTERNS.md
# Bead: <br-NNN>
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/<tool>}"

# === Test body ===

# Example: pin a "did you mean" hint for a typo
stderr=$("$TOOL" list --jsno 2>&1 >/dev/null) || true
if ! echo "$stderr" | grep -qE 'did you mean.*--json'; then
  echo "REGRESSION: --jsno typo no longer produces 'did you mean --json' hint" >&2
  echo "Recommendation R-NNN added levenshtein-1 hint; restore it." >&2
  exit 1
fi

# === End ===
echo "OK"
