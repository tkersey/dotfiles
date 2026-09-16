#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/lean_trust_audit.sh [file-or-directory ...]

Scans Lean files for placeholders and trust-expanding features. This is a lexical audit aid, not a substitute for `lake env lean`, `lake build`, or `#print axioms`.
Findings are printed for review; both findings and no matches exit 0. Scan errors exit nonzero.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$#" -eq 0 ]]; then
  set -- .
fi

# POSIX ERE boundaries work with both ripgrep and macOS/BSD grep; no GNU \b.
pattern='(^|[^[:alnum:]_])(sorry|admit|axiom|unsafe|partial|noncomputable|native_decide|bv_decide|bv_check|implemented_by|csimp|extern)([^[:alnum:]_]|$)|(^|[^[:alnum:]_])decide[[:space:]]+\+native'

if command -v rg >/dev/null 2>&1; then
  status=0
  rg -n --glob '*.lean' --glob '!**/.lake/**' --glob '!**/lake-packages/**' --glob '!**/build/**' -- "$pattern" "$@" || status=$?
  if [[ "$status" -gt 1 ]]; then
    exit "$status"
  fi
else
  find "$@" -type f -name '*.lean' \
    ! -path '*/.lake/*' ! -path '*/lake-packages/*' ! -path '*/build/*' \
    -print0 | while IFS= read -r -d '' file; do
      status=0
      grep -nHE -- "$pattern" "$file" || status=$?
      if [[ "$status" -gt 1 ]]; then
        exit "$status"
      fi
    done
fi
