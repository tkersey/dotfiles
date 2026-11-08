#!/usr/bin/env bash
set -euo pipefail

skill_root=$(cd -- "$(dirname -- "$0")/.." && pwd)
seq_bin=${SEQ_BIN:-${1:-seq}}
if command -v jaq >/dev/null 2>&1; then
  json_bin=jaq
else
  json_bin=jq
fi
fixture="$skill_root/tests/fixtures/tool-evidence.jsonl"
temp=$(mktemp -d "${TMPDIR:-/tmp}/seq-tool-evidence.XXXXXX")
trap 'rm -rf -- "$temp"' EXIT
export SEQ_CACHE_DIR="$temp/cache"

for owner in seq tune; do
  if [ "$owner" = seq ]; then
    definition="$skill_root/definitions/seq/tool-search.json"
    metadata=rows
    raw=rows-raw
    params=()
  else
    definition="$skill_root/../tune/definitions/seq/skill-decision-audit.json"
    metadata=tools
    raw=tools-raw
    params=(--param exclude_session_id=)
  fi

  "$seq_bin" definition check --definition "$definition" --format json |
    "$json_bin" -e '.valid and (.authority_granted | not)' >/dev/null

  # The only matching text is in the earlier, superseded output of this call.
  "$seq_bin" observe --definition "$definition" --path "$fixture" \
    --param needle=STARTING "${params[@]}" --projection "$metadata" \
    --format json >"$temp/metadata.json"
  "$json_bin" -e '
    (.data.rows | length) == 1 and
    (.data.rows[0] | .call_id == "progress" and
      .lifecycle_status == "completed" and
      (has("arguments_json") | not) and
      (has("input_text") | not) and
      (has("command_text") | not) and
      (has("output_text") | not) and
      (has("output_parts_json") | not))
  ' "$temp/metadata.json" >/dev/null

  "$seq_bin" observe --definition "$definition" --path "$fixture" \
    --param needle=starting "${params[@]}" --projection "$raw" \
    --format json >"$temp/progress.json"
  "$json_bin" -e '
    (.data.rows | length) == 1 and
    (.data.rows[0] | .call_id == "progress" and
      (.output_text | contains("finished")) and
      (.output_text | contains("starting") | not) and
      (.output_parts_json | length) == 2 and
      (.output_parts_json[0] |
        .process_results[0].process_status == "running" and
        .process_results[0].session_id == 41 and
        .process_results[0].exit_code == null and
        .process_results[0].output == "starting") and
      (.output_parts_json[1] |
        .process_results[0].process_status == "failed" and
        .process_results[0].exit_code == 7) and
      all(.output_parts_json[];
        (.source_event_id | startswith("sha256:")) and
        .line_number > 0 and .timestamp != null and
        .payload_pointer == "/output/0/text"))
  ' "$temp/progress.json" >/dev/null

  # Wrapper success and the inner failure must remain independently visible.
  "$seq_bin" observe --definition "$definition" --path "$fixture" \
    --param needle=UnavailableWorktree "${params[@]}" --projection "$raw" \
    --format json >"$temp/failure.json"
  "$json_bin" -e '
    (.data.rows | length) == 2 and
    any(.data.rows[]; .call_id == "batch" and
      .exit_code == 0 and .lifecycle_status == "completed" and
      (.output_parts_json[0].process_results[0] |
        .process_status == "failed" and .exit_code == 3 and
        .json_pointer == "" and .output == "UnavailableWorktree") and
      (.output_parts_json[1].process_results[0] |
        .process_status == "completed" and .exit_code == 0)) and
    any(.data.rows[]; .call_id == "readback" and
      (.output_parts_json[0].process_results | length) == 1 and
      (.output_parts_json[0].process_results[0] |
        .process_status == "completed" and .exit_code == 0 and
        (.output | contains("UnavailableWorktree"))))
  ' "$temp/failure.json" >/dev/null

  "$seq_bin" observe --definition "$definition" --path "$fixture" \
    --param 'needle=not an execution' "${params[@]}" --projection "$raw" \
    --format json >"$temp/quoted.json"
  "$json_bin" -e '
    (.data.rows | length) == 1 and
    (.data.rows[0] | .call_id == "quoted" and
      (.output_parts_json[0].process_results | length) == 0)
  ' "$temp/quoted.json" >/dev/null
done

tune_definition="$skill_root/../tune/definitions/seq/skill-decision-audit.json"
if "$seq_bin" observe --definition "$tune_definition" --path "$fixture" \
  --param needle=starting --projection tools --format json \
  >"$temp/missing-exclusion.json" 2>&1; then
  echo 'missing exclusion parameter unexpectedly accepted' >&2
  exit 1
fi
"$json_bin" -e '.code == "MissingParameter"' \
  "$temp/missing-exclusion.json" >/dev/null

for projection in evidence tools tools-raw; do
  "$seq_bin" observe --definition "$tune_definition" --path "$fixture" \
    --param needle= --param exclude_session_id=seq-tool-evidence-fixture \
    --projection "$projection" --format json >"$temp/excluded.json"
  "$json_bin" -e '(.data.rows | length) == 0' \
    "$temp/excluded.json" >/dev/null
done

"$seq_bin" observe --definition "$tune_definition" --path "$fixture" \
  --param 'needle=evidence marker' --param exclude_session_id= \
  --projection evidence --format json >"$temp/public-evidence.json"
"$json_bin" -e '
  (.data.rows | length) == 1 and
  (.data.rows[0] | .private == false and .text == "Public evidence marker")
' "$temp/public-evidence.json" >/dev/null

echo 'seq tool evidence: pass'
