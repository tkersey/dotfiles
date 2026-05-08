#!/usr/bin/env bash
# scripts/stub-scorer.sh — Deterministic non-LLM scorer for harness testing.
#
# Produces a single JSONL line conforming to subagents/scorer.md's output
# schema. Scores are derived from a hash of (surface_id, scorer_id) so they're
# stable across runs but vary across scorers (so inter-rater spread is non-zero
# but bounded).
#
# Use ONLY for testing the dry-run harness pipeline; never confuse with real
# LLM output. The transcript will mark `mode: stub` and the agent_surfaces row
# (if aggregated) lacks meaningful evidence.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/stub-scorer.sh <surface_id> <scorer_id> [--inventory PATH]

Emit one JSONL scorer record. Deterministic from (surface_id, scorer_id).

Args:
  <surface_id>   The surface to "score" (e.g. flag__list__json).
  <scorer_id>    Scorer label (A, B, tiebreaker).
  --inventory P  Optional inventory path; if present, mirrors the kind into notes.

Output:
  Single JSONL line on stdout.

Exit codes:
  0  Record emitted.
  1  Bad args.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

SID="$1"
SCORER="${2:-}"
[ -z "$SCORER" ] && { usage >&2; exit 1; }
shift 2

INVENTORY=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --inventory)
      [ -n "${2:-}" ] || { echo "--inventory requires a value" >&2; exit 1; }
      case "$2" in --*) echo "--inventory requires a value, got option-like token: $2" >&2; exit 1 ;; esac
      INVENTORY="$2"; shift 2
      ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Derive a [0,1000] base score from sha256(surface_id) % 1000, then jitter
# per scorer so two scorers don't agree exactly.
hash_base() {
  printf '%s' "$1" | sha256sum | head -c 8
}
hex_to_int() {
  printf '%d' "0x$1"
}

base_hex=$(hash_base "$SID")
base_int=$(hex_to_int "$base_hex")
base_score=$(( base_int % 1001 ))

scorer_jitter() {
  case "$1" in
    A)          echo 0 ;;
    B)          echo 50 ;;
    tiebreaker) echo 25 ;;
    *)          echo 0 ;;
  esac
}
jitter=$(scorer_jitter "$SCORER")

# Per-dim variation: hash(sid + dim_name) → [-100, +100] offset.
dim_score() {
  local dim="$1"
  local h
  h=$(printf '%s|%s' "$SID" "$dim" | sha256sum | head -c 6)
  local n
  n=$(printf '%d' "0x$h")
  local off=$(( (n % 201) - 100 ))   # -100..+100
  local total=$(( base_score + off + jitter ))
  [ "$total" -lt 0 ] && total=0
  [ "$total" -gt 1000 ] && total=1000
  # Round to nearest 50.
  total=$(( (total + 25) / 50 * 50 ))
  echo "$total"
}

DIMS=(agent_intuitiveness agent_ergonomics agent_ease_of_use \
      output_parseability error_pedagogy intent_inference \
      safety_with_recovery determinism_and_reproducibility \
      self_documentation composability regression_resistance)

# Compute each dim score ONCE; memoize into a parallel array. Three-pass usage
# below (scores_args, sum, evidence) would otherwise recompute the sha256 33
# times per call.
declare -A dim_cache
for d in "${DIMS[@]}"; do
  dim_cache["$d"]=$(dim_score "$d")
done

# Build scores object via jq for safe escaping.
scores_args=()
for d in "${DIMS[@]}"; do
  scores_args+=(--argjson "$d" "${dim_cache[$d]}")
done

kind=""
if [ -n "$INVENTORY" ] && [ -f "$INVENTORY" ]; then
  kind=$(jq -r --arg s "$SID" 'select(.surface_id == $s) | .kind // ""' "$INVENTORY" | head -1)
fi

# Weighted score = mean of all 11 dims (computed by aggregator normally; we
# precompute for stub so partials are self-contained).
sum=0
for d in "${DIMS[@]}"; do
  sum=$(( sum + ${dim_cache[$d]} ))
done
weighted=$(( sum / 11 ))

# Evidence: include for any dim > 700 (per scorer.md spec).
ev_filter='{ }'
ev_keys=()
for d in "${DIMS[@]}"; do
  if [ "${dim_cache[$d]}" -gt 700 ]; then
    ev_keys+=("\"$d\":{\"invocation\":\"<stub>\",\"stdout_excerpt\":\"<stub evidence for $d>\"}")
  fi
done
if [ "${#ev_keys[@]}" -gt 0 ]; then
  ev_filter='{ '$(IFS=,; echo "${ev_keys[*]}")' }'
fi

jq -nc \
  --arg sid "$SID" \
  --arg scorer "$SCORER" \
  --arg rubric "stub-1.0.0" \
  --arg notes "stub scorer; kind=$kind" \
  --argjson weighted "$weighted" \
  --argjson evidence "$ev_filter" \
  "${scores_args[@]}" \
  '{
    surface_id: $sid,
    scorer_id: $scorer,
    rubric_version: $rubric,
    scores: {
      agent_intuitiveness: $agent_intuitiveness,
      agent_ergonomics: $agent_ergonomics,
      agent_ease_of_use: $agent_ease_of_use,
      output_parseability: $output_parseability,
      error_pedagogy: $error_pedagogy,
      intent_inference: $intent_inference,
      safety_with_recovery: $safety_with_recovery,
      determinism_and_reproducibility: $determinism_and_reproducibility,
      self_documentation: $self_documentation,
      composability: $composability,
      regression_resistance: $regression_resistance
    },
    weighted_score: $weighted,
    evidence: $evidence,
    notes: $notes
  }'
