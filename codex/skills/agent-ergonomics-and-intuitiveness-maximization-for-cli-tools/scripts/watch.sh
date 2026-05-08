#!/usr/bin/env bash
# scripts/watch.sh — Re-score on every file save.
#
# Use case: dev is iterating on a recommendation, wants live feedback. Watches
# the target source dir; on every modify, re-runs `tools/rescore_surface.sh`
# for the affected surface(s) and prints the delta.
#
# This is a developer convenience, not part of the audit pipeline. It does NOT
# spawn LLM subagents — it shells out to the SKILL's deterministic re-score
# script (which uses the cached scoring state). For LLM re-scoring, use the
# full Phase 6 procedure.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/watch.sh <sibling> <target-source-dir> [--surface SID] [--debounce-ms 500]

Watch <target-source-dir> for changes. On each save, re-score either:
  - the surfaces touched by the changed file (default; uses
    surface_inventory.jsonl `evidence.path` to map file → surface_id), or
  - a single surface specified via --surface.

Prerequisites:
  - inotifywait (apt: inotify-tools) — hard dependency.
  - <sibling>/audit/agent_surfaces.jsonl exists.
  - <sibling>/audit/surface_inventory.jsonl exists.

Args:
  <sibling>             Audit workspace root.
  <target-source-dir>   Directory to watch (typically <target>/src).
  --surface SID         Re-score only this surface, ignore file→surface mapping.
  --debounce-ms N       Coalesce events within N ms (default 500).

Behavior:
  - Each event prints: timestamp, changed file, affected surface_id(s),
    new weighted_score, Δ vs prior.
  - Exit on Ctrl-C.

Exit codes:
  0  Watch loop exited cleanly (Ctrl-C).
  1  Bad args / missing inputs.
  2  inotifywait not installed.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

if [ -z "${2:-}" ]; then usage >&2; exit 1; fi
SIBLING="$1"
SRC_DIR="${2%/}"  # strip trailing slash so prefix-strip below works
shift 2

SURFACE_OVERRIDE=""
DEBOUNCE_MS=500
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --surface)     need_value "$1" "${2:-}"; SURFACE_OVERRIDE="$2"; shift 2 ;;
    --debounce-ms) need_value "$1" "${2:-}"; DEBOUNCE_MS="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

if ! command -v inotifywait >/dev/null 2>&1; then
  echo "inotifywait not found. Install with: sudo apt install inotify-tools" >&2
  exit 2
fi

[ -d "$SRC_DIR" ] || { echo "src dir not found: $SRC_DIR" >&2; exit 1; }
INV="$SIBLING/audit/surface_inventory.jsonl"
SURF="$SIBLING/audit/agent_surfaces.jsonl"
[ -f "$INV" ] || { echo "inventory not found: $INV" >&2; exit 1; }
[ -f "$SURF" ] || { echo "scorecard not found: $SURF" >&2; exit 1; }

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESCORE="$SKILL_DIR/tools/rescore_surface.sh"

map_file_to_surfaces() {
  local f="$1"
  jq -r --arg f "$f" '
    select((.evidence.path // "") | endswith($f) or . == $f)
    | .surface_id
  ' "$INV" 2>/dev/null | sort -u
}

current_weighted() {
  local sid="$1"
  # Filter by latest pass explicitly rather than relying on file order (records
  # may be appended out-of-order across re-score runs).
  local latest_pass
  latest_pass=$(jq -r '.pass // 1' "$SURF" 2>/dev/null | sort -n | tail -1)
  jq -r --arg s "$sid" --argjson p "${latest_pass:-1}" \
    'select(.surface_id == $s and (.pass // 1) == $p) | .weighted_score // 0' \
    "$SURF" 2>/dev/null | tail -1
}

echo "watching $SRC_DIR (Ctrl-C to exit)..."
LAST_EVENT_NS=0

inotifywait -m -r -e modify,create,move "$SRC_DIR" --format '%w%f' --quiet \
  | while IFS= read -r changed_path; do

  # Debounce: skip if last event was within DEBOUNCE_MS.
  now_ns=$(date +%s%N)
  delta_ms=$(( (now_ns - LAST_EVENT_NS) / 1000000 ))
  if [ "$delta_ms" -lt "$DEBOUNCE_MS" ] && [ "$LAST_EVENT_NS" -gt 0 ]; then
    continue
  fi
  LAST_EVENT_NS=$now_ns

  # Resolve which surfaces to re-score.
  if [ -n "$SURFACE_OVERRIDE" ]; then
    sids="$SURFACE_OVERRIDE"
  else
    rel_path="${changed_path#"$SRC_DIR"/}"
    sids=$(map_file_to_surfaces "$rel_path")
    if [ -z "$sids" ]; then
      sids=$(map_file_to_surfaces "$(basename "$changed_path")")
    fi
  fi

  if [ -z "$sids" ]; then
    printf '%s  %s  (no surface mapping)\n' "$(date +%T)" "$changed_path"
    continue
  fi

  while IFS= read -r sid; do
		[ -z "$sid" ] && continue
		prior=$(current_weighted "$sid")
		if [ -x "$RESCORE" ]; then
			(cd "$SIBLING" && bash "$RESCORE" "$sid" >/dev/null 2>&1) || true
		fi
		new=$(current_weighted "$sid")
    # Guard arithmetic: if either side is empty/non-numeric, report "?".
    if [[ "$prior" =~ ^-?[0-9]+$ ]] && [[ "$new" =~ ^-?[0-9]+$ ]]; then
      delta=$((new - prior))
      sign=""
      [ "$delta" -gt 0 ] && sign="+"
      printf '%s  %-40s  %s  %s → %s (%s%s)\n' \
        "$(date +%T)" "$(basename "$changed_path")" "$sid" "$prior" "$new" "$sign" "$delta"
    else
      printf '%s  %-40s  %s  ?  (no score yet)\n' \
        "$(date +%T)" "$(basename "$changed_path")" "$sid"
    fi
  done <<< "$sids"
done
