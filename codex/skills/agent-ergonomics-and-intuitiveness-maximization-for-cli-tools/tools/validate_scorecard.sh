#!/usr/bin/env bash
# tools/validate_scorecard.sh — Reject scorecards with > 700 scores lacking evidence.
# Also enforces other IO-CONTRACTS.md schema rules.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/validate_scorecard.sh <agent_surfaces.jsonl>

Validates an agent_surfaces.jsonl scorecard against IO-CONTRACTS.md rules:
  - Every row has a surface_id, pass, rubric_version, weighted_score.
  - Every row has a non-null integer score for all 11 dimensions.
  - Any score > 700 has matching non-empty evidence.
  - No duplicate (surface_id, pass) pairs.

Args:
  <agent_surfaces.jsonl>   Path to the scorecard file to validate.

Exit codes:
  0  Clean.
  1  At least one violation; per-row stderr message printed.
  2  Missing args, or scorecard file not found (input error, distinct
     from "violations found" so callers can tell them apart).

Example:
  tools/validate_scorecard.sh audit/agent_surfaces.jsonl
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

JSONL="$1"

if [ ! -f "$JSONL" ]; then
  echo "scorecard not found: $JSONL" >&2
  exit 2
fi

if ! jq . "$JSONL" >/dev/null 2>&1; then
  echo "VIOLATION: scorecard contains invalid JSON" >&2
  echo "1 violation(s)" >&2
  exit 1
fi

violations=0
fail() {
  echo "VIOLATION: $1" >&2
  violations=$((violations + 1))
}

while IFS= read -r row; do
  [ -z "$row" ] && continue

  row_type=$(echo "$row" | jq -r 'type')
  if [ "$row_type" != "object" ]; then
    fail "row is not a JSON object"
    continue
  fi

  sid_check=$(echo "$row" | jq -r '
    def sid_pattern: "^[A-Za-z0-9][A-Za-z0-9._-]*__[A-Za-z0-9][A-Za-z0-9._-]*(__[A-Za-z0-9][A-Za-z0-9._-]*)*$";
    if (has("surface_id") | not) or .surface_id == null or .surface_id == "" then ["missing", ""]
    elif (.surface_id | type) != "string" then ["invalid_type", (.surface_id | tostring)]
    elif (.surface_id | test(sid_pattern) | not) then ["invalid_format", .surface_id]
    else ["ok", .surface_id] end
    | @tsv
  ')
  IFS=$'\t' read -r sid_status sid <<< "$sid_check"
  if [ "$sid_status" = "missing" ]; then
    fail "row missing surface_id"
    continue
  elif [ "$sid_status" = "invalid_type" ]; then
    fail "row has non-string surface_id: $sid"
    continue
  elif [ "$sid_status" = "invalid_format" ]; then
    fail "$sid: invalid surface_id format"
    continue
  fi

  pass_check=$(echo "$row" | jq -r '
    if (has("pass") | not) or .pass == null then ["missing", ""]
    elif (.pass | type) != "number" or (.pass | floor) != .pass or .pass < 1 then ["invalid", (.pass | tostring)]
    else ["ok", (.pass | tostring)] end
    | @tsv
  ')
  IFS=$'\t' read -r pass_status pass <<< "$pass_check"
  rubric=$(echo "$row" | jq -r '.rubric_version // ""')
  # `pass` must be a positive integer per IO-CONTRACTS (passes start at 1).
  # Validate JSON type too: `jq -r` renders both number 1 and string "1" as
  # `1`, and downstream pass arithmetic assumes a real JSON integer.
  if [ "$pass_status" = "missing" ]; then
    fail "$sid: missing pass field"
  elif [ "$pass_status" != "ok" ]; then
    fail "$sid: .pass must be a positive JSON integer (got '$pass')"
  fi
  if [ -z "$rubric" ]; then fail "$sid: missing rubric_version"; fi

  weighted_check=$(echo "$row" | jq -r '
    if (has("weighted_score") | not) or .weighted_score == null then ["missing", ""]
    elif (.weighted_score | type) != "number"
      or (.weighted_score | floor) != .weighted_score
      or .weighted_score < 0
      or .weighted_score > 1000
    then ["invalid", (.weighted_score | tostring)]
    else ["ok", (.weighted_score | tostring)] end
    | @tsv
  ')
  IFS=$'\t' read -r weighted_status weighted <<< "$weighted_check"
  if [ "$weighted_status" = "missing" ]; then
    fail "$sid: missing weighted_score"
  elif [ "$weighted_status" != "ok" ]; then
    fail "$sid: weighted_score must be a JSON integer in [0,1000] (got '$weighted')"
  fi

  # score_confidence and scored_at are required per IO-CONTRACTS.md § agent_surfaces.jsonl
  # (the post-aggregation final-row schema, not the per-scorer partials).
  #
  # NOTE: use jq's `has(key)` for presence checks — `// ""` triggers on `false`
  # boolean values too, so `tiebroken: false` would be flagged as missing.
  conf_status=$(echo "$row" | jq -r '
    if (has("score_confidence") | not) or .score_confidence == null then "missing"
    elif (.score_confidence | type) != "object" then "invalid_type"
    else "ok" end
  ')
  if [ "$conf_status" = "missing" ]; then
    fail "$sid: missing score_confidence (required after Phase 2 aggregation; see IO-CONTRACTS.md)"
  elif [ "$conf_status" = "invalid_type" ]; then
    fail "$sid: score_confidence must be an object"
  else
    spread_check=$(echo "$row" | jq -r '
      if (.score_confidence | has("spread_max") | not) or .score_confidence.spread_max == null then ["missing", ""]
      elif (.score_confidence.spread_max | type) != "number"
        or (.score_confidence.spread_max | floor) != .score_confidence.spread_max
        or .score_confidence.spread_max < 0
      then ["invalid", (.score_confidence.spread_max | tostring)]
      else ["ok", (.score_confidence.spread_max | tostring)] end
      | @tsv
    ')
    IFS=$'\t' read -r spread_status spread <<< "$spread_check"
    if [ "$spread_status" = "missing" ]; then
      fail "$sid: score_confidence.spread_max missing"
    elif [ "$spread_status" != "ok" ]; then
      fail "$sid: score_confidence.spread_max must be a non-negative JSON integer (got '$spread')"
    fi

    tiebroken_check=$(echo "$row" | jq -r '
      if (.score_confidence | has("tiebroken") | not) or .score_confidence.tiebroken == null then ["missing", ""]
      elif (.score_confidence.tiebroken | type) != "boolean" then ["invalid", (.score_confidence.tiebroken | tostring)]
      else ["ok", (.score_confidence.tiebroken | tostring)] end
      | @tsv
    ')
    IFS=$'\t' read -r tiebroken_status tiebroken <<< "$tiebroken_check"
    if [ "$tiebroken_status" = "missing" ]; then
      fail "$sid: score_confidence.tiebroken missing"
    elif [ "$tiebroken_status" != "ok" ]; then
      fail "$sid: score_confidence.tiebroken must be a JSON boolean (got '$tiebroken')"
    fi
  fi

  has_scored_at=$(echo "$row" | jq 'has("scored_at")')
  if [ "$has_scored_at" != "true" ]; then fail "$sid: missing scored_at timestamp"; fi

  for dim in agent_intuitiveness agent_ergonomics agent_ease_of_use output_parseability error_pedagogy intent_inference safety_with_recovery determinism_and_reproducibility self_documentation composability regression_resistance; do
    score_check=$(echo "$row" | jq -r --arg dim "$dim" '
      if (.scores | type) != "object" or (.scores | has($dim) | not) or .scores[$dim] == null then ["missing", ""]
      else .scores[$dim] as $score
        | if ($score | type) != "number" or ($score | floor) != $score then ["non_integer", ($score | tostring)]
          elif $score < 0 or $score > 1000 then ["out_of_range", ($score | tostring)]
          else ["ok", ($score | tostring)] end
      end
      | @tsv
    ')
    IFS=$'\t' read -r score_status score <<< "$score_check"
    if [ "$score_status" = "missing" ]; then
      fail "$sid: missing score for $dim"
      continue
    fi
    if [ "$score_status" = "non_integer" ]; then
      fail "$sid: non-integer JSON score for $dim: $score"
      continue
    fi
    if [ "$score_status" = "out_of_range" ]; then
      fail "$sid: out-of-range score for $dim: $score"
      continue
    fi
    if [ "$score" -gt 700 ]; then
      ev_present=$(echo "$row" | jq -r --arg dim "$dim" '
        def present:
          if . == null then false
          elif (type == "object" or type == "array") then length > 0
          elif type == "string" then length > 0
          else false end;
        (.evidence // {}) as $evidence
        | if ($evidence | type) != "object" then false
          else ($evidence[$dim] // null) | present end
      ')
      if [ "$ev_present" != "true" ]; then
        fail "$sid: score $score on $dim has no evidence"
      fi
    fi
  done
done < "$JSONL"

# Check for duplicate (surface_id, pass) pairs
dupes=$(jq -r '
  select(type == "object")
  | select((.surface_id | type) == "string")
  | select((.pass | type) == "number" and (.pass | floor) == .pass)
  | .surface_id + ":" + (.pass | tostring)
' "$JSONL" | sort | uniq -d)
if [ -n "$dupes" ]; then
  while IFS= read -r dupe; do
    fail "duplicate (surface_id, pass): $dupe"
  done <<< "$dupes"
fi

if [ "$violations" -gt 0 ]; then
  echo
  echo "$violations violation(s)" >&2
  exit 1
fi

echo "validate_scorecard: OK"
exit 0
