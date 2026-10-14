#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/lean_trust_audit.sh [file-or-directory ...]

Scans Lean files for placeholders and trust-expanding features. This is a lexical audit aid, not a substitute for `lake env lean`, `lake build`, or `#print axioms`.
Includes hidden and ignored source files. Directory scans prune .git, .hg, .svn,
.lake, lake-packages, build, dist, vendor, third_party, third-party, and node_modules.
Other third-party layouts require selecting first-party file or directory targets.
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
  rg -n --hidden --no-ignore --glob '*.lean' --glob '!**/.lake/**' --glob '!**/lake-packages/**' --glob '!**/build/**' --glob '!**/{.git,.hg,.svn,dist,vendor,third_party,third-party,node_modules}/**' -- "$pattern" "$@" || status=$?
  if [[ "$status" -gt 1 ]]; then
    exit "$status"
  fi
else
  find "$@" -type d \( -name .git -o -name .hg -o -name .svn \
    -o -name .lake -o -name lake-packages -o -name build -o -name dist \
    -o -name vendor -o -name third_party -o -name third-party -o -name node_modules \) \
    -prune -o -type f -name '*.lean' -print0 | while IFS= read -r -d '' file; do
      status=0
      grep -nHE -- "$pattern" "$file" || status=$?
      if [[ "$status" -gt 1 ]]; then
        exit "$status"
      fi
    done
fi
