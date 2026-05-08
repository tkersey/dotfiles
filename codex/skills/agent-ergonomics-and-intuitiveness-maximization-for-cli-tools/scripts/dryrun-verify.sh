#!/usr/bin/env bash
# scripts/dryrun-verify.sh — Post-condition checker for dryrun-llm.sh output.
#
# Runs after the dryrun completes; verifies:
#   1. Every per-scorer partial is valid JSONL conforming to scorer schema.
#   2. Every score in [0, 1000].
#   3. Every score > 700 has accompanying evidence (per scorer.md discipline).
#   4. Inter-rater spread per dim is < 200 (warn) / < 350 (fail).
#   5. Aggregated agent_surfaces.dryrun.jsonl validates against schema (if
#      jsonschema is available).
#
# Output is appended to the dryrun report. Exit 0 iff all checks pass.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/dryrun-verify.sh <workdir>

<workdir>  The directory produced by dryrun-llm.sh.

Output: markdown verification block to stdout.
Exit 0 if all post-conditions pass, 1 otherwise.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

WORKDIR="$1"
[ -d "$WORKDIR" ] || { echo "workdir not found: $WORKDIR" >&2; exit 2; }

PARTIAL="$WORKDIR/partial"
SURFACES="$WORKDIR/agent_surfaces.dryrun.jsonl"

DIMS=(agent_intuitiveness agent_ergonomics agent_ease_of_use \
      output_parseability error_pedagogy intent_inference \
      safety_with_recovery determinism_and_reproducibility \
      self_documentation composability regression_resistance)

failures=0
warnings=0

echo
echo "## Post-conditions"
echo

# Check 1: partial JSONL parses.
n_partials=$(find "$PARTIAL" -name "scores_pass1_*.jsonl" 2>/dev/null | wc -l)
parse_fail=0
if [ "$n_partials" -gt 0 ]; then
  while IFS= read -r f; do
    if ! jq -e '.' "$f" >/dev/null 2>&1; then
      parse_fail=$((parse_fail + 1))
      echo "  - PARSE FAIL: $(basename "$f")"
    fi
  done < <(find "$PARTIAL" -name "scores_pass1_*.jsonl")
fi
if [ "$parse_fail" -eq 0 ]; then
  echo "- [OK] all $n_partials partial files parse as JSONL"
else
  echo "- [FAIL] $parse_fail of $n_partials partials failed JSONL parse"
  failures=$((failures + parse_fail))
fi

# Check 2: scores in [0, 1000].
range_fail=0
if [ "$n_partials" -gt 0 ]; then
  while IFS= read -r f; do
    # Allow null values: tiebreaker partials deliberately set non-disputed
    # dims to null (per scorer-tiebreaker.md schema), and the agent_surfaces
    # schema permits {null | integer 0-1000}. Reject only definite-bad
    # values: numbers that are out-of-range, non-integer, or types that
    # aren't number-or-null.
    bad=$(jq -s -r '
      if any(.[]; (.scores | type) != "object") then "invalid_scores"
      else [
        .[]
        | .scores
        | to_entries[]
        | select(
            (.value | type) != "null"
            and (
              (.value | type) != "number"
              or (.value | floor) != .value
              or .value < 0
              or .value > 1000
            )
          )
      ] | length
      end
    ' "$f" 2>/dev/null || echo "invalid_json")
    if [ "$bad" = "invalid_json" ]; then
      continue
    elif [ "$bad" = "invalid_scores" ]; then
      range_fail=$((range_fail + 1))
      echo "  - RANGE FAIL: $(basename "$f") has missing or non-object scores"
    elif [ "${bad:-0}" -gt 0 ]; then
      range_fail=$((range_fail + 1))
      echo "  - RANGE FAIL: $(basename "$f") has $bad non-integer or out-of-range score(s)"
    fi
  done < <(find "$PARTIAL" -name "scores_pass1_*.jsonl")
fi
if [ "$range_fail" -eq 0 ]; then
  echo "- [OK] all scores in [0, 1000]"
else
  echo "- [FAIL] $range_fail file(s) had missing, non-integer, or out-of-range scores"
  failures=$((failures + range_fail))
fi

# Check 3: scores > 700 require evidence.
evidence_fail=0
evidence_skipped=0
if [ "$n_partials" -gt 0 ]; then
  while IFS= read -r f; do
    missing=$(jq -s -r '
      def evidence_present:
        if . == null then false
        elif (type == "object" or type == "array") then length > 0
        elif type == "string" then length > 0
        else false end;
      if any(.[]; (.scores | type) != "object") then "invalid_scores"
      else [
        .[] as $row
        | ($row.evidence // {}) as $evidence
        | $row.scores
        | to_entries[]
        | select((.value | type) == "number" and .value > 700)
        | .key as $dim
        | select((if ($evidence | type) != "object" then false else ($evidence[$dim] // null | evidence_present) end) | not)
      ]
      | length
      end
    ' "$f" 2>/dev/null || echo "invalid_json")
    if [ "$missing" = "invalid_json" ] || [ "$missing" = "invalid_scores" ]; then
      evidence_skipped=$((evidence_skipped + 1))
      continue
    elif [ "${missing:-0}" -gt 0 ]; then
      evidence_fail=$((evidence_fail + 1))
      echo "  - EVIDENCE FAIL: $(basename "$f") has $missing high-score dim(s) lacking evidence"
    fi
  done < <(find "$PARTIAL" -name "scores_pass1_*.jsonl")
fi
if [ "$evidence_fail" -eq 0 ]; then
  if [ "$evidence_skipped" -gt 0 ]; then
    echo "- [skip] high-score evidence check skipped for $evidence_skipped structurally invalid file(s)"
  else
    echo "- [OK] all scores > 700 have evidence"
  fi
else
  echo "- [FAIL] $evidence_fail file(s) had high-scores without evidence"
  failures=$((failures + evidence_fail))
fi

# Check 4: inter-rater spread per surface (max - min) per dim.
echo
echo "### Inter-rater agreement"
echo
echo "| surface_id | max_spread | verdict |"
echo "|------------|------------|---------|"
spread_fail=0
spread_warn=0
spread_tiebroken=0
# Group partials by surface_id.
sids=$(find "$PARTIAL" -name "scores_pass1_*.jsonl" 2>/dev/null \
       | sed -n 's/.*scores_pass1_\(.*\)_scorer.*\.jsonl$/\1/p' \
       | sort -u)
while IFS= read -r sid; do
  [ -z "$sid" ] && continue
  files=$(find "$PARTIAL" -name "scores_pass1_${sid}_scorer*.jsonl")
  n_files=$(echo "$files" | grep -c .)
  [ "$n_files" -lt 2 ] && continue   # need ≥ 2 to compute spread
  # Compute spread across A+B only (exclude tiebreaker — its job is to
  # resolve disputes, not contribute to the original spread metric). If a
  # tiebreaker partial exists, mark verdict TIEBROKEN instead of FAIL: the
  # dispute was already resolved by an explicit tiebreaker pass.
  rater_files=$(printf '%s\n' "$files" | grep -v '_scorertiebreaker\.jsonl$' || true)
  tiebreaker_file=$(printf '%s\n' "$files" | grep '_scorertiebreaker\.jsonl$' | head -1 || true)
  unresolved_tiebreaks=0
  max_spread=0
  for d in "${DIMS[@]}"; do
    # shellcheck disable=SC2016 # jq variables are resolved by jq, not the shell.
    vals=$(while IFS= read -r f; do
      [ -z "$f" ] && continue
      jq -r --arg d "$d" '
        .scores[$d] // empty
        | select(type == "number" and (floor == .))
      ' "$f" 2>/dev/null || true
    done <<< "$rater_files" | sort -n)
    [ -z "$vals" ] && continue
    lo=$(echo "$vals" | head -1)
    hi=$(echo "$vals" | tail -1)
    spread=$(( hi - lo ))
    [ "$spread" -gt "$max_spread" ] && max_spread=$spread
    if [ "$spread" -ge 350 ]; then
      tie_score=""
      if [ -n "$tiebreaker_file" ]; then
        tie_score=$(jq -r --arg d "$d" '
          .scores[$d] // empty
          | select(type == "number" and (floor == .))
        ' "$tiebreaker_file" 2>/dev/null || true)
      fi
      [ -n "$tie_score" ] || unresolved_tiebreaks=$((unresolved_tiebreaks + 1))
    fi
  done
  if [ "$max_spread" -ge 350 ] && [ "$unresolved_tiebreaks" -eq 0 ]; then
    verdict="TIEBROKEN"
    spread_tiebroken=$((spread_tiebroken + 1))
  elif [ "$max_spread" -ge 350 ]; then
    verdict="FAIL"
    spread_fail=$((spread_fail + 1))
  elif [ "$max_spread" -ge 200 ]; then
    verdict="WARN"
    spread_warn=$((spread_warn + 1))
  else
    verdict="OK"
  fi
  printf '| %s | %s | %s |\n' "$sid" "$max_spread" "$verdict"
done <<< "$sids"
echo
if [ "$spread_fail" -gt 0 ]; then
  echo "- [FAIL] $spread_fail surface(s) had spread ≥ 350 without complete tiebreaker coverage"
  failures=$((failures + spread_fail))
elif [ "$spread_warn" -gt 0 ]; then
  echo "- [WARN] $spread_warn surface(s) had spread ≥ 200 (acceptable but high)"
  [ "$spread_tiebroken" -gt 0 ] && echo "- [OK] $spread_tiebroken high-spread surface(s) covered by tiebreaker partials"
  warnings=$((warnings + spread_warn))
elif [ "$spread_tiebroken" -gt 0 ]; then
  echo "- [OK] $spread_tiebroken high-spread surface(s) covered by tiebreaker partials"
else
  echo "- [OK] all inter-rater spreads under 200"
fi

# Check 5: aggregated agent_surfaces validates.
if [ -f "$SURFACES" ]; then
  echo
  echo "### Aggregated agent_surfaces"
  if python3 -c 'import jsonschema' 2>/dev/null; then
    SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    schema="$SKILL_DIR/assets/schemas/agent_surfaces.schema.json"
    if [ -f "$schema" ]; then
      schema_fails=$(python3 - "$SURFACES" "$schema" <<'PY'
import json, sys
import jsonschema
with open(sys.argv[2]) as f: schema = json.load(f)
v = jsonschema.Draft202012Validator(schema)
fails = 0
with open(sys.argv[1]) as f:
    for n, line in enumerate(f, 1):
        line = line.strip()
        if not line: continue
        try:
            rec = json.loads(line)
        except Exception:
            fails += 1; continue
        errs = list(v.iter_errors(rec))
        if errs:
            fails += 1
            for e in errs[:2]:
                ep = ".".join(str(p) for p in e.absolute_path) or "<root>"
                print(f"  - line {n}: {ep}: {e.message}", file=sys.stderr)
print(fails)
PY
)
      if [ "${schema_fails:-1}" -eq 0 ]; then
        echo "- [OK] aggregated rows validate against schema"
      else
        echo "- [FAIL] $schema_fails aggregated row(s) failed schema validation"
        failures=$((failures + schema_fails))
      fi
    fi
  else
    echo "- [skip] python3 jsonschema not available"
  fi
fi

# Final verdict.
echo
echo "## Verdict"
echo "- failures: $failures"
echo "- warnings: $warnings"
if [ "$failures" -gt 0 ]; then
  echo "- result: FAIL"
  exit 1
fi
echo "- result: PASS"
exit 0
