#!/usr/bin/env bash
# scripts/preview.sh — 30-second preview of what an audit would target.
#
# Runs a quick inventory + language detection without scaffolding anything.
# Output is a one-page summary the user inspects before deciding whether
# to commit to a full pass. Reduces activation energy from "spend an hour"
# to "see if it's worth it in 30 seconds."
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/preview.sh <target-dir-or-binary> [--depth N]

Reports what a full audit would find, without writing anything to disk.
Inputs:
  <target-dir-or-binary>  EITHER a target source-repo directory (we'll
                          discover the binary from it) OR a binary path
                          directly (we'll skip language detection).
  --depth N               Inventory recursion depth. Default: 2.

Output: one-page summary on stdout (~20 lines). No side effects.

Exit codes:
  0  Preview produced.
  1  Bad args / target unreachable.
EOF
}

DEPTH=2

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

TARGET="$1"; shift

need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --depth) need_value "$1" "${2:-}"; DEPTH="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Two paths: directory (run discover-cli.sh first) vs binary (skip discovery).
binary=""
language=""
if [ -d "$TARGET" ]; then
  cli_json=$(/usr/bin/timeout 10 bash "$SKILL_DIR/scripts/discover-cli.sh" "$TARGET" 2>/dev/null || echo '{}')
  language=$(echo "$cli_json" | /usr/bin/jq -r '.languages[0] // "unknown"')
  binary=$(echo "$cli_json" | /usr/bin/jq -r '.binaries[0] // ""')
  # Resolve the binary: try PATH, target/release, target top-level.
  for candidate in "$binary" "$TARGET/target/release/$binary" "$TARGET/$binary"; do
    if [ -n "$candidate" ] && command -v "$candidate" >/dev/null 2>&1; then
      binary="$(command -v "$candidate")"
      break
    elif [ -n "$candidate" ] && [ -x "$candidate" ]; then
      binary="$candidate"
      break
    fi
  done
elif command -v "$TARGET" >/dev/null 2>&1 || [ -x "$TARGET" ]; then
  binary="$TARGET"
  language="(binary-only; skipped language detection)"
else
  echo "target not a directory or executable: $TARGET" >&2
  exit 1
fi

if [ -z "$binary" ] || ! { command -v "$binary" >/dev/null 2>&1 || [ -x "$binary" ]; }; then
  echo "could not resolve target binary from $TARGET" >&2
  exit 1
fi

# Quick inventory.
inv_tmp=$(mktemp /tmp/aerg_preview.XXXXXX)
/usr/bin/timeout 60 bash "$SKILL_DIR/scripts/inventory_surfaces.sh" "$binary" --depth "$DEPTH" > "$inv_tmp" 2>/dev/null || true
total=$(/usr/bin/wc -l < "$inv_tmp")
flags=$(/usr/bin/jq -c 'select(.kind == "flag")' "$inv_tmp" 2>/dev/null | /usr/bin/wc -l)
verbs=$(/usr/bin/jq -c 'select(.kind == "verb")' "$inv_tmp" 2>/dev/null | /usr/bin/wc -l)
top_verbs=$(/usr/bin/jq -r 'select(.kind == "verb" and (.subtree | tostring | contains(" ") | not)) | .name' "$inv_tmp" 2>/dev/null | /usr/bin/sort -u | /usr/bin/head -8 | /usr/bin/tr '\n' ' ')

# Archetype guess from heuristics (not a full classifier; just a hint).
archetype="generic-cli"
if [ "$verbs" -gt 50 ]; then
  archetype="multi-tool-family"
elif [ "$flags" -gt 100 ] && [ "$verbs" -le 5 ]; then
  archetype="single-binary-with-many-flags (e.g. ffmpeg, curl style)"
elif [ "$verbs" -le 1 ]; then
  archetype="single-action-tool (e.g. jq, ripgrep style)"
elif [ "$verbs" -gt 5 ] && [ "$verbs" -le 20 ]; then
  archetype="standard-multi-verb-cli (e.g. gh, cargo style)"
fi

cat <<EOF
preview: $binary
  language detected:  $language
  total surfaces:     $total ($verbs verbs, $flags flags; depth=$DEPTH)
  top-level verbs:    ${top_verbs:-(none)}
  archetype guess:    $archetype

Estimate the full-pass cost: scripts/estimate.sh $binary --mode full
Run a small audit:           scripts/estimate.sh $binary --mode mini
Scaffold a full workspace:   scripts/scaffold-workspace.sh <sibling> $TARGET
EOF
: > "$inv_tmp" 2>/dev/null || true
