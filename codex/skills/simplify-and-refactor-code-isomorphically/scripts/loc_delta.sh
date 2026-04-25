#!/usr/bin/env bash
# Compute source-line diff for a path between two git refs without worktrees.
#
# Usage:  ./loc_delta.sh [--net-only] [base-ref] [target-ref] [path]
#         (defaults: HEAD~1 → HEAD on whole repo)

set -euo pipefail

NET_ONLY=0
args=()
for arg in "$@"; do
  case "$arg" in
    --net-only) NET_ONLY=1 ;;
    *) args+=("$arg") ;;
  esac
done
set -- "${args[@]}"

BASE="${1:-HEAD~1}"
TARGET="${2:-HEAD}"
PATH_FILTER="${3:-.}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "error: loc_delta.sh must run inside a git repository" >&2
  exit 2
fi

if ! git rev-parse --verify --quiet "${BASE}^{commit}" >/dev/null; then
  echo "error: base ref not found: ${BASE}" >&2
  exit 2
fi
if ! git rev-parse --verify --quiet "${TARGET}^{commit}" >/dev/null; then
  echo "error: target ref not found: ${TARGET}" >&2
  exit 2
fi

numstat=$(git diff --numstat "${BASE}" "${TARGET}" -- "${PATH_FILTER}")
added=$(printf '%s\n' "$numstat" | awk '$1 ~ /^[0-9]+$/ {s+=$1} END{print s+0}')
deleted=$(printf '%s\n' "$numstat" | awk '$2 ~ /^[0-9]+$/ {s+=$2} END{print s+0}')
delta=$(( added - deleted ))

if (( NET_ONLY )); then
  echo "$delta"
  exit 0
fi

echo "Base ref:    ${BASE}"
echo "Target ref:  ${TARGET}"
echo "Path:        ${PATH_FILTER}"
echo "Added:       ${added}"
echo "Deleted:     ${deleted}"
echo "Net delta:   ${delta}"

echo
echo "Per-extension delta:"
if [[ -n "$numstat" ]]; then
  printf '%s\n' "$numstat" | awk '
    $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9]+$/ {
      path=$3
      sub(/^.*\//, "", path)
      if (path ~ /\./) {
        ext=path
        sub(/^.*\./, ".", ext)
      } else {
        ext="[no extension]"
      }
      add[ext]+=$1
      del[ext]+=$2
    }
    END {
      for (ext in add) {
        printf "  %-14s +%6d -%6d (%+d)\n", ext, add[ext], del[ext], add[ext]-del[ext]
      }
    }' | sort
else
  echo "  no text-file changes"
fi
