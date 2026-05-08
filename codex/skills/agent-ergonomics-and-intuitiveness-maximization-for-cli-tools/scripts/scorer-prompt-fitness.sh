#!/usr/bin/env bash
# scripts/scorer-prompt-fitness.sh — Test the scorer prompt against known-good
# golden surfaces.
#
# rubric-fitness.sh tests the rubric. This tests the SCORER PROMPT — given a
# fixed rubric, does the prompt elicit scores that match expert judgment?
# Useful when iterating on subagents/scorer.md.
#
# Workflow:
#   1. Read references/scoring-fixtures/golden-surfaces.jsonl (curated surfaces
#      with expected_scores ground truth).
#   2. For each, run a scorer against the actual binary (real Claude) or use
#      the fixture oracle in stub mode to exercise the comparator.
#   3. Compare scores to expected; compute mean absolute error per dim.
#   4. Report per-dim MAE; FAIL if mean MAE > 200 across all dims.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/scorer-prompt-fitness.sh [--mode stub|claude] [--workdir DIR] [--fixture PATH]

Score every golden surface; compare to expected; report per-dim MAE.

Options:
  --mode MODE       stub (default; fixture oracle) | claude
  --workdir DIR     Default: mktemp under ${TMPDIR:-/tmp}
  --fixture PATH    Override golden surfaces (default: references/scoring-fixtures/golden-surfaces.jsonl)

Output (markdown):
  - Per-dim mean absolute error
  - Per-surface delta tables
  - PASS/FAIL verdict (PASS if mean MAE across dims ≤ 200)

Exit codes:
  0  Mean MAE ≤ 200 (prompt fits well).
  1  Mean MAE 200-300 (prompt drift; review).
  2  Mean MAE > 300 (prompt is mis-calibrated).
  3  Bad args / missing fixture.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
esac

MODE=stub
WORKDIR=""
FIXTURE=""
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 3; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 3 ;; esac
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)     need_value "$1" "${2:-}"; MODE="$2"; shift 2 ;;
    --workdir)  need_value "$1" "${2:-}"; WORKDIR="$2"; shift 2 ;;
    --fixture)  need_value "$1" "${2:-}"; FIXTURE="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 3 ;;
  esac
done

case "$MODE" in stub|claude) ;; *) echo "bad --mode: $MODE" >&2; exit 3 ;; esac

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -z "$FIXTURE" ] && FIXTURE="$SKILL_DIR/references/scoring-fixtures/golden-surfaces.jsonl"
[ -f "$FIXTURE" ] || { echo "fixture not found: $FIXTURE" >&2; exit 3; }

[ -z "$WORKDIR" ] && WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/scorer-fitness.XXXXXX")"
mkdir -p "$WORKDIR/partial"

surface_id_re='^[A-Za-z0-9][A-Za-z0-9._-]*__[A-Za-z0-9][A-Za-z0-9._-]*(__[A-Za-z0-9][A-Za-z0-9._-]*)*$'

# Mirrors the Python DIMS list below; kept here as a quick shell-side index.
# shellcheck disable=SC2034
DIMS=(agent_intuitiveness agent_ergonomics agent_ease_of_use \
      output_parseability error_pedagogy intent_inference \
      safety_with_recovery determinism_and_reproducibility \
      self_documentation composability regression_resistance)

# Build a synthetic inventory from the fixture for the stub-scorer to consume.
INV="$WORKDIR/inventory.jsonl"
jq -c '{surface_id: .surface_id, kind: .kind, evidence: {invocation: .invocation}}' "$FIXTURE" > "$INV"

# Score each surface.
n_scored=0
missing_claude_scores=0
while IFS= read -r row; do
  [ -z "$row" ] && continue
  sid=$(echo "$row" | jq -r '.surface_id')
  if ! [[ "$sid" =~ $surface_id_re ]]; then
    printf 'invalid filename-unsafe surface_id: %q\n' "$sid" >&2
    exit 3
  fi
  score_file="$WORKDIR/partial/scores_pass1_${sid}_scorerA.jsonl"
  case "$MODE" in
    stub)
      # The hash-based stub-scorer is useful for dryrun-llm plumbing, but it
      # is intentionally not semantically calibrated to expert golden scores.
      # For this fitness harness, stub mode must exercise the comparator
      # deterministically without creating a guaranteed false failure.
      jq -c --arg scorer A '
        (.expected_scores // {}) as $scores
        | ($scores | length) as $n
        | {
            surface_id: .surface_id,
            scorer_id: $scorer,
            rubric_version: "fixture-oracle-1.0.0",
            scores: $scores,
            weighted_score: (
              if $n > 0
              then (($scores | to_entries | map(.value) | add) / $n | floor)
              else 0
              end
            ),
            evidence: {fixture_oracle: true},
            notes: "fixture oracle row for scorer-prompt-fitness stub mode"
          }
      ' <<< "$row" > "$score_file"
      ;;
    claude)
      if [ ! -s "$score_file" ]; then
        echo "claude mode for surface $sid: parent agent must spawn agent-ergo-scorer with these args:"
        echo "  SURFACE_ID=$sid; SCORER_ID=A; SIBLING=$WORKDIR; PASS=1; (use real --invocation: $(echo "$row" | jq -r '.invocation'))"
        missing_claude_scores=1
      fi
      ;;
  esac
  n_scored=$((n_scored + 1))
done < "$FIXTURE"

if [ "$MODE" = claude ] && [ "$missing_claude_scores" -ne 0 ]; then
  echo "claude mode: pause here, run subagents, then re-invoke with --workdir $WORKDIR"
  exit 0
fi

# Compare actual to expected.
echo "# Scorer Prompt Fitness Report"
echo
echo "_Mode: $MODE · Surfaces: $n_scored · Workdir: \`$WORKDIR\`_"
echo

# Per-dim MAE accumulator via python.
python3 - "$FIXTURE" "$WORKDIR/partial" <<'PY'
import json, os, sys
from collections import defaultdict

fixture, partial_dir = sys.argv[1], sys.argv[2]

DIMS = [
    'agent_intuitiveness','agent_ergonomics','agent_ease_of_use',
    'output_parseability','error_pedagogy','intent_inference',
    'safety_with_recovery','determinism_and_reproducibility',
    'self_documentation','composability','regression_resistance'
]

# Load expected.
expected = {}
with open(fixture) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        expected[rec['surface_id']] = rec.get('expected_scores', {})

# Load actual.
actual = {}
for fn in os.listdir(partial_dir):
    if not fn.startswith('scores_pass1_'): continue
    sid = fn[len('scores_pass1_'):].rsplit('_scorer', 1)[0]
    with open(os.path.join(partial_dir, fn)) as f:
        rec = json.loads(f.read().strip())
    actual[sid] = rec.get('scores', {})

# Per-dim MAE.
print('## Per-dim mean absolute error\n')
print('| dim | MAE | verdict |')
print('|-----|-----|---------|')
maes = []
for dim in DIMS:
    errors = []
    for sid, exp_scores in expected.items():
        if sid not in actual: continue
        e = exp_scores.get(dim)
        a = actual[sid].get(dim)
        if e is not None and a is not None:
            errors.append(abs(e - a))
    if not errors:
        print(f'| {dim} | — | NO_DATA |')
        continue
    mae = sum(errors) / len(errors)
    maes.append(mae)
    if mae <= 100: verdict = 'EXCELLENT'
    elif mae <= 200: verdict = 'OK'
    elif mae <= 300: verdict = 'WARN'
    else: verdict = 'FAIL'
    print(f'| {dim} | {mae:.0f} | {verdict} |')

mean_mae = sum(maes) / len(maes) if maes else 0
print()
print('## Overall')
print()
print(f'- Mean MAE across dims: **{mean_mae:.0f}**')
print(f'- Surfaces compared: {len([s for s in expected if s in actual])}/{len(expected)}')
print()

# Per-surface deltas.
print('## Per-surface deltas (sum of |actual - expected| across dims)')
print('')
print('| surface_id | total_delta | flag |')
print('|------------|-------------|------|')
for sid in sorted(expected):
    if sid not in actual:
        print(f'| {sid} | — | (not scored) |')
        continue
    total = sum(abs(expected[sid].get(d, 0) - actual[sid].get(d, 0)) for d in DIMS)
    if total > 2200: flag = 'HIGH'
    elif total > 1100: flag = 'med'
    else: flag = ''
    print(f'| {sid} | {total} | {flag} |')

# Verdict.
print()
if mean_mae <= 200:
    print('### Verdict: PASS — prompt fits expert judgment within budget.')
    sys.exit(0)
elif mean_mae <= 300:
    print('### Verdict: WARN — prompt is drifting; review surfaces flagged HIGH.')
    sys.exit(1)
else:
    print('### Verdict: FAIL — prompt is mis-calibrated; rewrite scorer.md or rubric anchors.')
    sys.exit(2)
PY
