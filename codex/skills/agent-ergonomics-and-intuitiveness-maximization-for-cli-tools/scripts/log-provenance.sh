#!/usr/bin/env bash
# scripts/log-provenance.sh — Append a provenance record.
#
# Subagents and applier scripts call this when they produce an artifact, so
# we have a per-artifact record of (model, prompt_hash, rubric_version,
# evidence_sources, ts). Without this, "why did we score surface X at 580?"
# is unanswerable 6 months later.
#
# Schema: assets/schemas/provenance.schema.json
# Storage: <sibling>/audit/provenance.jsonl (flock-guarded append)
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/log-provenance.sh <sibling> <kind> <artifact_id> [opts]

Required args:
  <sibling>       Audit workspace root.
  <kind>          One of: score, recommendation, applied_change, intent_corpus_entry.
  <artifact_id>   Unique ID for the artifact within its kind.

Options:
  --model NAME              Model identifier (e.g. claude-opus-4-7).
  --prompt-hash SHA         sha256:... of the full prompt text.
  --prompt-file PATH        Compute prompt-hash from this file's contents.
  --rubric-version V        SCORING-RUBRIC version (semver or git SHA).
  --scorer-id X             Scorer subagent ID (A, B, tiebreaker).
  --evidence FILE:LINE      Citation. Repeatable.
  --wall-time-ms N          Wall-clock time in ms.
  --input-tokens N          Input token count.
  --output-tokens N         Output token count.
  --skill-version V         Version of the skill itself.
  --notes STR               Free-form annotation.

Output:
  Single appended JSONL record. flock-guarded.

Exit codes:
  0  Record appended.
  1  Bad args / missing inputs.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

if [ -z "${2:-}" ] || [ -z "${3:-}" ]; then
  usage >&2; exit 1
fi
SIBLING="$1"
KIND="$2"
AID="$3"
shift 3

case "$KIND" in
  score|recommendation|applied_change|intent_corpus_entry) ;;
  *) echo "bad kind: $KIND" >&2; exit 1 ;;
esac

MODEL=""
PROMPT_HASH=""
PROMPT_FILE=""
RUBRIC_VERSION=""
SCORER_ID=""
EVIDENCE=()
WALL_MS=""
IN_TOK=""
OUT_TOK=""
SKILL_VERSION=""
NOTES=""

# Helper: a flag without its value triggers `$2: unbound variable` under
# `set -u` BEFORE we can produce a graceful error. Guard each consumer with a
# defaulted-test against ${2:-} so the test happens before the unsafe access.
require_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in
    --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --model)            require_value "$1" "${2:-}"; MODEL="$2"; shift 2 ;;
    --prompt-hash)      require_value "$1" "${2:-}"; PROMPT_HASH="$2"; shift 2 ;;
    --prompt-file)      require_value "$1" "${2:-}"; PROMPT_FILE="$2"; shift 2 ;;
    --rubric-version)   require_value "$1" "${2:-}"; RUBRIC_VERSION="$2"; shift 2 ;;
    --scorer-id)        require_value "$1" "${2:-}"; SCORER_ID="$2"; shift 2 ;;
    --evidence)         require_value "$1" "${2:-}"; EVIDENCE+=("$2"); shift 2 ;;
    --wall-time-ms)     require_value "$1" "${2:-}"; WALL_MS="$2"; shift 2 ;;
    --input-tokens)     require_value "$1" "${2:-}"; IN_TOK="$2"; shift 2 ;;
    --output-tokens)    require_value "$1" "${2:-}"; OUT_TOK="$2"; shift 2 ;;
    --skill-version)    require_value "$1" "${2:-}"; SKILL_VERSION="$2"; shift 2 ;;
    --notes)            require_value "$1" "${2:-}"; NOTES="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Compute prompt hash if file given.
if [ -n "$PROMPT_FILE" ]; then
  [ -f "$PROMPT_FILE" ] || { echo "prompt file not found: $PROMPT_FILE" >&2; exit 1; }
  if [ -n "$PROMPT_HASH" ]; then
    echo "specify either --prompt-hash OR --prompt-file, not both" >&2; exit 1
  fi
  PROMPT_HASH="sha256:$(sha256sum "$PROMPT_FILE" | head -c 64)"
fi

AUDIT="$SIBLING/audit"
[ -d "$AUDIT" ] || { echo "no audit dir: $AUDIT" >&2; exit 1; }

OUT="$AUDIT/provenance.jsonl"
LOCK="${OUT}.lock"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Build evidence array as JSON.
ev_json="[]"
if [ "${#EVIDENCE[@]}" -gt 0 ]; then
  ev_json=$(printf '%s\n' "${EVIDENCE[@]}" | jq -R . | jq -s .)
fi

RECORD=$(jq -nc \
  --arg kind     "$KIND" \
  --arg aid      "$AID" \
  --arg model    "$MODEL" \
  --arg ph       "$PROMPT_HASH" \
  --arg rv       "$RUBRIC_VERSION" \
  --arg sid      "$SCORER_ID" \
  --argjson ev   "$ev_json" \
  --arg wall     "$WALL_MS" \
  --arg in_tok   "$IN_TOK" \
  --arg out_tok  "$OUT_TOK" \
  --arg sv       "$SKILL_VERSION" \
  --arg notes    "$NOTES" \
  --arg ts       "$NOW" '
  {
    artifact_kind: $kind,
    artifact_id: $aid,
    ts: $ts
  }
  + (if $model != "" then {model: $model} else {} end)
  + (if $ph != "" then {prompt_hash: $ph} else {} end)
  + (if $rv != "" then {rubric_version: $rv} else {} end)
  + (if $sid != "" then {scorer_subagent_id: $sid} else {} end)
  + (if ($ev | length) > 0 then {evidence_sources: $ev} else {} end)
  + (if $wall != "" then {wall_time_ms: ($wall | tonumber)} else {} end)
  + (if $in_tok != "" then {input_tokens: ($in_tok | tonumber)} else {} end)
  + (if $out_tok != "" then {output_tokens: ($out_tok | tonumber)} else {} end)
  + (if $sv != "" then {skill_version: $sv} else {} end)
  + (if $notes != "" then {notes: $notes} else {} end)
')

if ! command -v flock >/dev/null 2>&1; then
  echo "log-provenance.sh requires flock(1)" >&2
  exit 1
fi
exec 9>"$LOCK"
flock 9
printf '%s\n' "$RECORD" >> "$OUT"
flock -u 9
exec 9>&-
