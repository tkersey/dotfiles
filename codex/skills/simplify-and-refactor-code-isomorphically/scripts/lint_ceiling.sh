#!/usr/bin/env bash
# lint_ceiling.sh — enforce warning-count ceiling (per R-013).
#
# Use in CI / pre-commit to prevent warning-count from growing during rescue
# or continuous-refactor. Auto-detects language.
#
# Usage:
#   lint_ceiling.sh snapshot <ceiling-file>     # capture current count
#   lint_ceiling.sh check <ceiling-file>        # verify count ≤ ceiling
#   lint_ceiling.sh relax <ceiling-file> <n>    # after a fix, lower ceiling by n

set -euo pipefail

CMD="${1:-}"
CEILING_FILE="${2:-refactor/artifacts/warning_ceiling.txt}"

count_warnings() {
  local n=0
  if [[ -f Cargo.toml ]] && command -v cargo >/dev/null; then
    n=$(cargo clippy --all-targets 2>&1 | grep -c '^warning:' || true)
  elif [[ -f package.json ]] && command -v npx >/dev/null; then
    n=$(npx --no-install tsc --noEmit 2>&1 | grep -c 'error TS' || true)
  elif [[ -f pyproject.toml || -f setup.py ]] && command -v mypy >/dev/null; then
    n=$(mypy --strict src/ 2>&1 | grep -c ': error:' || true)
  elif [[ -f go.mod ]] && command -v go >/dev/null; then
    n=$(go vet ./... 2>&1 | wc -l | tr -d ' ' || echo 0)
  else
    echo "no recognized project type; nothing to count" >&2
    n=0
  fi
  echo "$n"
}

case "$CMD" in
  snapshot)
    mkdir -p "$(dirname "$CEILING_FILE")"
    count_warnings > "$CEILING_FILE"
    ceil=$(cat "$CEILING_FILE")
    echo "captured ceiling: $ceil (in $CEILING_FILE)"
    ;;

  check)
    if [[ ! -f "$CEILING_FILE" ]]; then
      echo "no ceiling set yet; run: lint_ceiling.sh snapshot $CEILING_FILE" >&2
      exit 2
    fi
    ceiling=$(cat "$CEILING_FILE")
    current=$(count_warnings)
    if [[ $current -le $ceiling ]]; then
      echo "PASS: $current warnings ≤ ceiling $ceiling"
      exit 0
    else
      echo "FAIL: $current warnings > ceiling $ceiling (grew by $((current - ceiling)))"
      echo "      Per R-013, the warning count must not grow."
      echo "      Either: (a) fix the new warnings introduced in this change,"
      echo "              (b) if intentional, relax the ceiling explicitly:"
      echo "                   $0 relax $CEILING_FILE -$((current - ceiling))"
      exit 1
    fi
    ;;

  relax)
    DELTA="${3:-}"
    if [[ -z "$DELTA" ]]; then
      echo "usage: lint_ceiling.sh relax <ceiling-file> <signed-delta>"
      exit 2
    fi
    if [[ ! -f "$CEILING_FILE" ]]; then
      echo "no ceiling set yet"
      exit 2
    fi
    ceiling=$(cat "$CEILING_FILE")
    new_ceiling=$((ceiling + DELTA))
    echo "ceiling: $ceiling → $new_ceiling (delta $DELTA)"
    echo "$new_ceiling" > "$CEILING_FILE"
    ;;

  *)
    cat <<EOF
Usage: $0 <command> [args]

Commands:
  snapshot <file>         Capture current warning count as the ceiling
  check <file>            Verify warning count ≤ ceiling (exit 1 if not)
  relax <file> <delta>    Adjust ceiling (negative to lower after a cleanup)

Default ceiling file: refactor/artifacts/warning_ceiling.txt
EOF
    exit 2
    ;;
esac
