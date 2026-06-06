#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/lean_trust_audit.sh [file-or-directory ...]

Scans Lean files for placeholders and trust-expanding features. This is a lexical audit aid, not a substitute for `lake env lean`, `lake build`, or `#print axioms`.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$#" -eq 0 ]]; then
  set -- .
fi

pattern='\b(sorry|admit|axiom|unsafe|partial|noncomputable|native_decide)\b|@\[(implemented_by|csimp)\]|implemented_by|csimp|decide[[:space:]]+\+native|extern'

if command -v rg >/dev/null 2>&1; then
  rg -n --glob '*.lean' --glob '!.lake/**' --glob '!lake-packages/**' --glob '!build/**' "$pattern" "$@" || true
else
  find "$@" -type f -name '*.lean' \
    ! -path '*/.lake/*' ! -path '*/lake-packages/*' ! -path '*/build/*' \
    -print0 | xargs -0 grep -nE "$pattern" || true
fi
