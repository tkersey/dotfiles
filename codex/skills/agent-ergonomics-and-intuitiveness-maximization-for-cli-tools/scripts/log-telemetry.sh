#!/usr/bin/env bash
# scripts/log-telemetry.sh — Append a telemetry record to audit/telemetry.jsonl.
#
# Subagents and phase scripts call this on completion to log:
#   {subagent, phase, surface_id?, started_at, completed_at, duration_s,
#    input_tokens?, output_tokens?, exit_status, error_if_any?}
#
# This is the foundation for cost-cap enforcement, performance debugging,
# and the round-L #3 visibility goal. Without it, "what cost $200?" is
# detective work; with it, `jq '.input_tokens + .output_tokens' telemetry.jsonl`
# answers it in 200ms.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/log-telemetry.sh <sibling> <subagent> <phase> [opts]

Appends a telemetry record to <sibling>/audit/telemetry.jsonl. flock-guarded
so parallel subagent calls don't corrupt the file.

Required args:
  <sibling>    Audit workspace root.
  <subagent>   Subagent name (e.g. scorer, recommender, applier, intent-runner).
  <phase>      Phase number 0..10 (or "preflight" for pre-Phase-0).

Options:
  --surface-id ID         Surface scored / acted on (per-surface subagents).
  --started-at ISO        ISO 8601 timestamp; defaults to now − duration.
  --duration-s N          Wall-time in seconds (integer).
  --input-tokens N        Token usage if known.
  --output-tokens N       Token usage if known.
  --exit-status N         0 for success; non-zero for error.
  --error STR             Short error tag (e.g. "rate_limit", "context_overflow").

Output:
  Single appended JSONL record. Idempotent against simultaneous callers via
  flock on <sibling>/audit/telemetry.jsonl.lock.

Exit codes:
  0  Record appended.
  1  Bad args / missing workspace.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

SIBLING="$1"; shift
SUBAGENT="${1:-}"
PHASE="${2:-}"
if [ -z "$SUBAGENT" ] || [ -z "$PHASE" ]; then
  usage >&2; exit 1
fi
shift 2

SURFACE_ID=""
STARTED_AT=""
DURATION_S=""
INPUT_TOKENS=""
OUTPUT_TOKENS=""
EXIT_STATUS=0
ERROR=""

need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}
need_any_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --surface-id)    need_value "$1" "${2:-}"; SURFACE_ID="$2"; shift 2 ;;
    --started-at)    need_value "$1" "${2:-}"; STARTED_AT="$2"; shift 2 ;;
    --duration-s)    need_value "$1" "${2:-}"; DURATION_S="$2"; shift 2 ;;
    --input-tokens)  need_value "$1" "${2:-}"; INPUT_TOKENS="$2"; shift 2 ;;
    --output-tokens) need_value "$1" "${2:-}"; OUTPUT_TOKENS="$2"; shift 2 ;;
    --exit-status)   need_value "$1" "${2:-}"; EXIT_STATUS="$2"; shift 2 ;;
    --error)         need_any_value "$1" "${2:-}"; ERROR="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

AUDIT="$SIBLING/audit"
[ -d "$AUDIT" ] || { echo "no audit dir: $AUDIT" >&2; exit 1; }

OUT="$AUDIT/telemetry.jsonl"
LOCK="${OUT}.lock"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
[ -z "$STARTED_AT" ] && STARTED_AT="$NOW"

# Build the record via jq for safe escaping.
RECORD=$(jq -nc \
  --arg subagent "$SUBAGENT" \
  --arg phase    "$PHASE" \
  --arg sid      "$SURFACE_ID" \
  --arg started  "$STARTED_AT" \
  --arg ended    "$NOW" \
  --arg dur      "$DURATION_S" \
  --arg in_tok   "$INPUT_TOKENS" \
  --arg out_tok  "$OUTPUT_TOKENS" \
  --arg exit_s   "$EXIT_STATUS" \
  --arg err      "$ERROR" '
  {
    subagent: $subagent,
    phase: $phase,
    surface_id: (if $sid == "" then null else $sid end),
    started_at: $started,
    completed_at: $ended,
    duration_s: (if $dur == "" then null else ($dur | tonumber) end),
    input_tokens: (if $in_tok == "" then null else ($in_tok | tonumber) end),
    output_tokens: (if $out_tok == "" then null else ($out_tok | tonumber) end),
    exit_status: ($exit_s | tonumber),
    error: (if $err == "" then null else $err end)
  }')

if ! command -v flock >/dev/null 2>&1; then
  echo "log-telemetry.sh requires flock(1)" >&2
  exit 1
fi
exec 9>"$LOCK"
flock 9
printf '%s\n' "$RECORD" >> "$OUT"
flock -u 9
exec 9>&-

# Bump manifest's spawned-counter so cost-cap.sh sees it.
if [ -f "$AUDIT/manifest.json" ]; then
  bash "$(dirname "${BASH_SOURCE[0]}")/manifest_update.sh" "$SIBLING" \
    '.passes[-1].summary.subagents_spawned = ((.passes[-1].summary.subagents_spawned // 0) + 1)' \
    >/dev/null 2>&1 || true
fi
