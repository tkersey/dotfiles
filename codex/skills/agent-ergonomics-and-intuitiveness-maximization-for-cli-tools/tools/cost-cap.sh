#!/usr/bin/env bash
# tools/cost-cap.sh — Runtime budget check for an in-flight audit.
#
# Reads `.cost_cap` from manifest.json (set at scaffold time or by the user
# via manifest_update.sh). Counts subagent invocations and elapsed wall-time
# from the manifest's per-pass `summary` field. Exits nonzero if either has
# been exceeded — the parent agent should call this between phase boundaries
# and bail if it returns 1.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/cost-cap.sh <sibling> [--phase N] [--max-subagents N] [--max-minutes N]

Checks the audit's running cost against caps. Reads caps from the manifest's
`cost_cap` block by default; CLI args override.

Manifest schema (add to audit/manifest.json):
  "cost_cap": {
    "max_subagents": 500,
    "max_minutes": 120,
    "max_usd_estimated": 50,
    "per_phase": {
      "2": { "max_subagents": 80,  "max_minutes": 30 },
      "4": { "max_subagents": 60,  "max_minutes": 30 },
      "5": { "max_subagents": 100, "max_minutes": 45 },
      "9": { "max_subagents": 30,  "max_minutes": 20 }
    }
  }

Per-phase caps override the global caps WHEN --phase is supplied. Without
--phase, only the global caps apply (legacy behavior preserved).

Why per-phase: a runaway scoring loop in Phase 2 should trip a cap before
ever entering Phase 5. The global cap doesn't catch this because Phase 2
might burn 80% of the global budget by itself before the parent agent
notices. Per-phase caps are the local circuit breaker.

Behavior:
  - Counts spawned subagents via `summary.subagents_spawned` (global) or
    `phase_summary[<phase>].subagents_spawned` (per-phase).
  - Computes elapsed minutes from the current pass's `started_at` (global)
    or `phase_summary[<phase>].started_at` (per-phase).
  - Exits 0 if under all applicable caps, 1 if any cap exceeded.
  - Prints a status line per axis on stdout.

Use this at every phase boundary. The contract: if you exceed a cap, STOP
spawning subagents and prompt the user to either raise the cap or accept
partial results.

Args:
  <sibling>            Audit workspace root.
  --phase N            Check Phase-N caps (defaults to global only).
  --max-subagents N    Override the active (phase or global) max_subagents.
  --max-minutes N      Override the active (phase or global) max_minutes.

Exit codes:
  0  Under all caps.
  1  At least one cap exceeded — main agent must stop spawning.
  2  Bad args / missing manifest.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

SIBLING="$1"; shift
override_subagents=""
override_minutes=""
phase=""
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 2; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 2 ;; esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --phase)         need_value "$1" "${2:-}"; phase="$2";              shift 2 ;;
    --max-subagents) need_value "$1" "${2:-}"; override_subagents="$2"; shift 2 ;;
    --max-minutes)   need_value "$1" "${2:-}"; override_minutes="$2";   shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

MANIFEST="$SIBLING/audit/manifest.json"
if [ ! -f "$MANIFEST" ]; then
  echo "manifest not found: $MANIFEST" >&2
  exit 2
fi

# Read caps + counters via jq. When --phase is supplied, per-phase caps
# override globals (with global as the fallback).
if [ -n "$phase" ]; then
  max_subagents=$(jq -r --arg p "$phase" \
    '.cost_cap.per_phase[$p].max_subagents // .cost_cap.max_subagents // 1000' "$MANIFEST")
  max_minutes=$(jq -r --arg p "$phase" \
    '.cost_cap.per_phase[$p].max_minutes // .cost_cap.max_minutes // 240' "$MANIFEST")
  cur_subagents=$(jq -r --arg p "$phase" \
    '.passes[-1].phase_summary[$p].subagents_spawned // 0' "$MANIFEST")
  started_at=$(jq -r --arg p "$phase" \
    '.passes[-1].phase_summary[$p].started_at // .passes[-1].started_at // ""' "$MANIFEST")
else
  max_subagents=$(jq -r '.cost_cap.max_subagents // 1000' "$MANIFEST")
  max_minutes=$(jq -r '.cost_cap.max_minutes // 240' "$MANIFEST")
  cur_subagents=$(jq -r '.passes[-1].summary.subagents_spawned // 0' "$MANIFEST")
  started_at=$(jq -r '.passes[-1].started_at // ""' "$MANIFEST")
fi
[ -n "$override_subagents" ] && max_subagents="$override_subagents"
[ -n "$override_minutes" ]   && max_minutes="$override_minutes"

if [ -z "$started_at" ] || [ "$started_at" = "null" ]; then
  cur_minutes=0
else
  start_epoch=$(date -d "$started_at" +%s 2>/dev/null || echo 0)
  now_epoch=$(date +%s)
  if [ "$start_epoch" -gt 0 ]; then
    cur_minutes=$(( (now_epoch - start_epoch) / 60 ))
  else
    cur_minutes=0
  fi
fi

# Validate integer shape.
for v in "$max_subagents" "$max_minutes" "$cur_subagents" "$cur_minutes"; do
  if ! [[ "$v" =~ ^[0-9]+$ ]]; then
    echo "non-integer cost-cap value: $v" >&2
    exit 2
  fi
done

scope_label="global"
[ -n "$phase" ] && scope_label="phase-$phase"

exceeded=0
status_lines=()
if [ "$cur_subagents" -gt "$max_subagents" ]; then
  status_lines+=("[$scope_label] EXCEEDED subagents: $cur_subagents > $max_subagents (cap)")
  exceeded=1
else
  status_lines+=("[$scope_label] subagents: $cur_subagents / $max_subagents")
fi
if [ "$cur_minutes" -gt "$max_minutes" ]; then
  status_lines+=("[$scope_label] EXCEEDED wall-time: $cur_minutes min > $max_minutes (cap)")
  exceeded=1
else
  status_lines+=("[$scope_label] wall-time: $cur_minutes / $max_minutes min")
fi

printf '%s\n' "${status_lines[@]}"

if [ "$exceeded" -eq 1 ]; then
  echo "cost-cap: caps exceeded — main agent should stop spawning subagents and prompt user" >&2
  exit 1
fi
echo "cost-cap: under caps"
exit 0
