#!/usr/bin/env bash
# tools/provenance-query.sh — Query the provenance ledger.
#
# Use cases:
#   - "Why did this score get assigned?" → query by artifact_id.
#   - "Which scores came from rubric v1.1?" → query by rubric_version.
#   - "Which artifacts used model X?" → query by model.
#   - "Show every artifact citing src/cli.rs" → query by evidence_source.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/provenance-query.sh <sibling> [opts]

Filter and report provenance records.

Filters (any combination):
  --kind KIND               score|recommendation|applied_change|intent_corpus_entry
  --artifact-id ID          Specific artifact ID (e.g. R-007, verb__list__pass1__scorerA).
  --rubric-version V        Filter by rubric version.
  --model M                 Filter by model identifier.
  --scorer-id X             Filter by scorer subagent ID.
  --evidence-contains STR   Match records whose evidence_sources include STR.
  --since ISO               Only records with ts >= ISO.
  --until ISO               Only records with ts <= ISO.

Output:
  --format json    JSONL output (default).
  --format table   Markdown table (kind, id, model, rubric, ts).
  --format count   Just print count of matches.

Exit codes:
  0  Query produced output (even if empty).
  1  Bad args / missing ledger.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

SIBLING="$1"; shift

KIND=""
AID=""
RUBRIC=""
MODEL=""
SCORER=""
EV_SUB=""
SINCE=""
UNTIL=""
FORMAT=json

# Helper: guard against `$2: unbound variable` under `set -u` when a flag is
# passed as the LAST argument with no value. ${2:-} substitutes empty; the
# -n test then produces a graceful error before the bare `$2` access below.
need() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in
    --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --kind)               need "$1" "${2:-}"; KIND="$2"; shift 2 ;;
    --artifact-id)        need "$1" "${2:-}"; AID="$2"; shift 2 ;;
    --rubric-version)     need "$1" "${2:-}"; RUBRIC="$2"; shift 2 ;;
    --model)              need "$1" "${2:-}"; MODEL="$2"; shift 2 ;;
    --scorer-id)          need "$1" "${2:-}"; SCORER="$2"; shift 2 ;;
    --evidence-contains)  need "$1" "${2:-}"; EV_SUB="$2"; shift 2 ;;
    --since)              need "$1" "${2:-}"; SINCE="$2"; shift 2 ;;
    --until)              need "$1" "${2:-}"; UNTIL="$2"; shift 2 ;;
    --format)             need "$1" "${2:-}"; FORMAT="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

case "$FORMAT" in json|table|count) ;; *) echo "bad --format: $FORMAT" >&2; exit 1 ;; esac

LEDGER="$SIBLING/audit/provenance.jsonl"
[ -f "$LEDGER" ] || { echo "no provenance ledger: $LEDGER" >&2; exit 1; }

# Build jq filter using --arg for safe substitution. Concatenating user-
# supplied filter values directly into the jq source could break the filter
# if the value contains quotes, backslashes, or jq operators. --arg makes
# every user value a plain string the jq filter references by name.
FILTER='.'
JQ_ARGS=()
if [ -n "$KIND" ];   then FILTER="$FILTER | select(.artifact_kind == \$kind)";   JQ_ARGS+=(--arg kind   "$KIND"); fi
if [ -n "$AID" ];    then FILTER="$FILTER | select(.artifact_id == \$aid)";      JQ_ARGS+=(--arg aid    "$AID"); fi
if [ -n "$RUBRIC" ]; then FILTER="$FILTER | select(.rubric_version == \$rv)";    JQ_ARGS+=(--arg rv     "$RUBRIC"); fi
if [ -n "$MODEL" ];  then FILTER="$FILTER | select(.model == \$model)";          JQ_ARGS+=(--arg model  "$MODEL"); fi
if [ -n "$SCORER" ]; then FILTER="$FILTER | select(.scorer_subagent_id == \$sc)"; JQ_ARGS+=(--arg sc     "$SCORER"); fi
if [ -n "$EV_SUB" ]; then FILTER="$FILTER | select((.evidence_sources // []) | map(contains(\$ev)) | any)"; JQ_ARGS+=(--arg ev "$EV_SUB"); fi
if [ -n "$SINCE" ];  then FILTER="$FILTER | select(.ts >= \$since)";              JQ_ARGS+=(--arg since  "$SINCE"); fi
if [ -n "$UNTIL" ];  then FILTER="$FILTER | select(.ts <= \$until)";              JQ_ARGS+=(--arg until  "$UNTIL"); fi

case "$FORMAT" in
  json)
    jq -c "${JQ_ARGS[@]}" "$FILTER" "$LEDGER"
    ;;
  table)
    echo "| kind | artifact_id | model | rubric | scorer | ts |"
    echo "|------|-------------|-------|--------|--------|-----|"
    jq -r "${JQ_ARGS[@]}" "$FILTER | \"| \(.artifact_kind) | \(.artifact_id) | \(.model // \"-\") | \(.rubric_version // \"-\") | \(.scorer_subagent_id // \"-\") | \(.ts) |\"" "$LEDGER"
    ;;
  count)
    jq -c "${JQ_ARGS[@]}" "$FILTER" "$LEDGER" | wc -l
    ;;
esac
