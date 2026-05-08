#!/usr/bin/env bash
# scripts/aggregate_scores.sh — Aggregate per-scorer partials into the final
# agent_surfaces.jsonl row(s). Implements the "Aggregation (main agent)" step
# documented in PHASES.md § Phase 2.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/aggregate_scores.sh <sibling> [<surface_id>]

Reads per-scorer partial files at <SIBLING>/audit/partial/scores_pass<N>_<SID>_scorer*.jsonl
and emits one final row per surface to <SIBLING>/audit/agent_surfaces.jsonl.

Each output row matches IO-CONTRACTS.md § agent_surfaces.jsonl:
  - per-dim score = median across scorer values (ignoring nulls)
  - score_confidence.spread_max = max (per-dim max − min) across all dims
  - score_confidence.tiebroken = true if any partial has scorer_id == "tiebreaker"
  - pass = manifest.current_pass; scored_at = current ISO-8601 timestamp
  - rubric_version, notes, weighted_score copied from scorer A
  - evidence shallow-merged across ALL scorers (scorer A wins on key
    collision; later scorers fill in dims A left blank)
    (synthesis tip: scorers should generally produce comparable evidence; if
    they diverge meaningfully, run the tiebreaker)

Args:
  <sibling>       Audit workspace root (absolute path).
  [<surface_id>]  If given, aggregate only that surface. Default: every surface
                  with at least 2 partials in audit/partial/.

Exit codes:
  0  Aggregation complete; final rows written/replaced.
  1  Fewer than 2 partials found for a surface (cannot aggregate).
  2  Missing arguments / sibling / manifest (input error).

Example:
  scripts/aggregate_scores.sh /path/to/__audit verb__list
  scripts/aggregate_scores.sh /path/to/__audit            # all surfaces
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

SIBLING="$1"
SID_FILTER="${2:-}"

AUDIT="$SIBLING/audit"
MANIFEST="$AUDIT/manifest.json"
PARTIAL_DIR="$AUDIT/partial"
OUT="$AUDIT/agent_surfaces.jsonl"

if [ ! -f "$MANIFEST" ]; then
  echo "manifest not found: $MANIFEST" >&2
  exit 2
fi
if [ ! -d "$PARTIAL_DIR" ]; then
  echo "partial dir not found: $PARTIAL_DIR (run scorer subagents first)" >&2
  exit 2
fi

PASS=$(jq -r '.current_pass // 1' "$MANIFEST")
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Discover surfaces for the CURRENT pass only. Filenames are
# `scores_pass<N>_<SID>_scorer<X>.jsonl` (per scorer.md output instruction).
# The `pass<N>` discriminator is critical: Phase 6 re-scorer writes the same
# surface IDs as Phase 2, and without per-pass scoping they'd glob together
# and the median would be computed across pre- and post-apply scores
# (meaningless). We accept the legacy filename `scores_<SID>_scorer<X>.jsonl`
# (no pass) too — those count as pass-1 — so audits scaffolded before this
# change still aggregate correctly.
discover_sids() {
  shopt -s nullglob
  local -A seen=()
  local f base sid
  # Per-pass-discriminated filenames first.
  for f in "$PARTIAL_DIR"/scores_pass"${PASS}"_*_scorer*.jsonl; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .jsonl)
    sid=$(echo "$base" | sed -E "s/^scores_pass${PASS}_//; s/_scorer[A-Za-z0-9]+\$//")
    if [ -z "${seen[$sid]:-}" ]; then
      seen[$sid]=1
      printf '%s\n' "$sid"
    fi
  done
  # Legacy filenames (no pass discriminator) — only when current_pass=1, to
  # avoid mistaking pass-1 partials for pass-2 input on a re-aggregated
  # workspace.
  if [ "$PASS" = "1" ]; then
    for f in "$PARTIAL_DIR"/scores_*_scorer*.jsonl; do
      [ -f "$f" ] || continue
      base=$(basename "$f" .jsonl)
      # Skip per-pass-discriminated names that already matched above.
      case "$base" in scores_pass*_scorer*) continue ;; esac
      sid=$(echo "$base" | sed -E 's/^scores_//; s/_scorer[A-Za-z0-9]+$//')
      if [ -z "${seen[$sid]:-}" ]; then
        seen[$sid]=1
        printf '%s\n' "$sid"
      fi
    done
  fi
  shopt -u nullglob
}

aggregate_one() {
  local sid="$1"
  shopt -s nullglob
  # Match per-pass-discriminated partials FIRST, then legacy (pass-1 only).
  local partials=( "$PARTIAL_DIR"/scores_pass"${PASS}"_"${sid}"_scorer*.jsonl )
  if [ "${#partials[@]}" -eq 0 ] && [ "$PASS" = "1" ]; then
    partials=( "$PARTIAL_DIR"/scores_"${sid}"_scorer*.jsonl )
  fi
  shopt -u nullglob

  if [ "${#partials[@]}" -lt 2 ]; then
    echo "WARN: $sid has ${#partials[@]} partial(s); aggregation needs ≥2. Skipping." >&2
    return 1
  fi

  # Pre-aggregation validation. Without these checks (per cross-model review
  # round G4-V1, V2), the aggregator silently:
  #   (a) accepts partials whose .surface_id mismatches the filename, then
  #       emits the row under the WRONG sid — the original surface drops to
  #       <2 partials and is silently skipped without telling the user;
  #   (b) accepts string-typed scores (e.g. {"intent_inference":"high"}),
  #       which jq's median filter treats as null → median computed from
  #       the OTHER partial alone, with no signal that one was malformed.
  # Fail fast with a clear pointer to the offending file.
  for p in "${partials[@]}"; do
    local p_sid
    p_sid=$(jq -r '.surface_id // ""' "$p" 2>/dev/null)
    if [ -z "$p_sid" ]; then
      echo "VIOLATION: $p has no .surface_id (or malformed JSON)" >&2
      return 1
    fi
    if [ "$p_sid" != "$sid" ]; then
      echo "VIOLATION: $p .surface_id=$p_sid mismatches filename-derived sid=$sid" >&2
      return 1
    fi
    # Each dim score must be either null/absent OR an integer in [0,1000].
    local bad_dim
    bad_dim=$(jq -r '
      . as $r
      | ["agent_intuitiveness","agent_ergonomics","agent_ease_of_use",
         "output_parseability","error_pedagogy","intent_inference",
         "safety_with_recovery","determinism_and_reproducibility",
         "self_documentation","composability","regression_resistance"]
      | map(. as $d
          | ($r.scores[$d] // null) as $v
          | if $v == null then empty
            elif ($v | type) != "number" or $v < 0 or $v > 1000 or ($v | floor) != $v then $d
            else empty end
        )
      | if length > 0 then .[0] else "" end
    ' < "$p" 2>/dev/null || echo "")
    if [ -n "$bad_dim" ]; then
      echo "VIOLATION: $p has non-integer or out-of-range score on dim '$bad_dim'" >&2
      return 1
    fi
  done

  # Concatenate all partials onto one input stream for jq, then compute median +
  # spread per dim. The 11-dim list is hard-coded to match IO-CONTRACTS.
  #
  # Care points:
  #   - jq's `add` on a list containing null returns null (null + n = null), so
  #     filter nulls before summing for weighted_score.
  #   - For 2-element median we floor the average so output stays integer.
  #   - $by_dim's per-dim list is sorted, so spread = last - first.
  # shellcheck disable=SC2016 # jq variables are resolved by jq, not the shell.
  local merged_jq='
    [inputs]
    | . as $partials
    | (["agent_intuitiveness","agent_ergonomics","agent_ease_of_use","output_parseability",
        "error_pedagogy","intent_inference","safety_with_recovery","determinism_and_reproducibility",
        "self_documentation","composability","regression_resistance"]) as $dims
    | (reduce $dims[] as $d ({};
        . + { ($d): (
            [ $partials[]
              | .scores[$d]
              | select(. != null)
            ] | sort
        ) })) as $by_dim
    | (reduce $dims[] as $d ({};
        . + { ($d): (
            ($by_dim[$d] | length) as $n
            | if $n == 0 then null
              elif $n % 2 == 1 then $by_dim[$d][($n-1)/2]
              else (($by_dim[$d][$n/2 - 1] + $by_dim[$d][$n/2]) / 2 | floor)
              end
        ) })) as $median
    | (reduce $dims[] as $acc_d (0;
        . as $acc
        | ($by_dim[$acc_d] | length) as $n
        | if $n < 2 then $acc
          else (($by_dim[$acc_d][-1] - $by_dim[$acc_d][0])) as $sp
               | if $sp > $acc then $sp else $acc end
          end
      )) as $spread_max
    | ($partials | map(select(.scorer_id == "tiebreaker")) | length > 0) as $tiebroken
    | ($partials[0]) as $first
    | ([$median[] | select(. != null)]) as $present_scores
    | (if ($present_scores | length) == 0 then 0
       else ($present_scores | add) / ($present_scores | length) | floor
       end) as $weighted
    # Merge evidence across ALL scorers, not just $first. Scorer B may have
    # cited an invocation/stdout for a dim that scorer A left blank — taking
    # only $first.evidence silently dropped that, which the validator would
    # then flag as score > 700 with no evidence even though one of the
    # scorers DID cite the run. Shallow-merge: walk partials in REVERSE and
    # +-fold (jqs + makes the right side win on key collision), so that
    # the FIRST scorer evidence for each dim survives, and later scorers
    # only fill in dims the earlier ones omitted.
    | ($partials | reverse | map(.evidence // {}) | add // {}) as $merged_evidence
    | {
        surface_id:        $first.surface_id,
        pass:              ($pass | tonumber),
        rubric_version:    $first.rubric_version,
        scores:            $median,
        weighted_score:    $weighted,
        score_confidence:  { spread_max: $spread_max, tiebroken: $tiebroken },
        evidence:          $merged_evidence,
        notes:             ($first.notes // ""),
        scored_at:         $now
      }
  '

  # Idempotency: if a row for (sid, current_pass) already exists in $OUT,
  # remove it before appending the new one. The previous pure-append (`>>`)
  # produced duplicate (surface_id, pass) rows on every re-run, which
  # validate_scorecard.sh then rejected as a "duplicate (sid,pass)"
  # violation — meaning a re-run silently corrupted the scorecard. Phase 6
  # re-scoring (which calls re-scorer subagents that write fresh partials)
  # also compounded this. Detect-and-replace fixes both flows: re-running
  # aggregation against unchanged inputs is now byte-identical (modulo
  # scored_at) per the PHASES.md idempotency claim.
  local new_row
  new_row=$(jq -nc --arg pass "$PASS" --arg now "$NOW" \
             "$merged_jq" "${partials[@]}")
  if [ -f "$OUT" ]; then
    local tmp
    tmp=$(mktemp /tmp/aerg_aggregate.XXXXXX)
    jq -c --arg sid "$sid" --argjson pass "$PASS" \
      'select(.surface_id != $sid or .pass != $pass)' "$OUT" > "$tmp"
    mv "$tmp" "$OUT"
  fi
  printf '%s\n' "$new_row" >> "$OUT"
}

if [ -n "$SID_FILTER" ]; then
  aggregate_one "$SID_FILTER"
  echo "aggregated: $SID_FILTER → $OUT"
else
  count=0
  skipped=0
  # Increment `count` only when aggregate_one actually appended a row.
  # Previously the counter advanced for every discovered SID — including
  # those skipped by aggregate_one for "needs ≥ 2 partials" — so the final
  # message said "aggregated N surface(s) → $OUT" when the file might still
  # not exist (because every surface was skipped). To a caller scripting on
  # the printed count, that looked like success.
  while IFS= read -r sid; do
    [ -z "$sid" ] && continue
    if aggregate_one "$sid"; then
      count=$((count + 1))
    else
      skipped=$((skipped + 1))
    fi
  done < <(discover_sids)
  if [ "$skipped" -gt 0 ]; then
    echo "aggregated $count surface(s), skipped $skipped (insufficient partials) → $OUT"
    exit 1
  elif [ "$count" -eq 0 ]; then
    echo "no aggregatable surfaces found in $PARTIAL_DIR" >&2
    exit 1
  else
    echo "aggregated $count surface(s) → $OUT"
  fi
fi

exit 0
