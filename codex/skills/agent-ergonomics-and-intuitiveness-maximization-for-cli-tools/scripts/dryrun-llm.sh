#!/usr/bin/env bash
# scripts/dryrun-llm.sh — End-to-end LLM scorer dry-run harness.
#
# This is the long-missing "actually invoke the LLM" entry point. It picks N
# representative surfaces from the inventory, spawns 2 scorer subagents per
# surface (or a stub for offline testing), captures transcripts, aggregates,
# verifies post-conditions, and reports.
#
# Use case: before committing to a $200 full-pass, run `dryrun-llm.sh` on 10
# surfaces with a $5 budget to validate (a) the prompt produces well-formed
# output, (b) inter-rater agreement is reasonable, (c) cost projection holds.
#
# The stub mode (default --mode stub) produces deterministic synthetic scores
# without any LLM call. Use this to verify the HARNESS itself before paying
# real money. Switch to --mode claude when you've validated the harness.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/dryrun-llm.sh <sibling> [opts]

Run a small LLM scorer dry-run against a subset of surfaces.

Args:
  <sibling>             Audit workspace root.

Options:
  --surfaces N          Number of surfaces to sample (default 10).
  --mode MODE           stub | claude (default: stub).
                        - stub: scripts/stub-scorer.sh (deterministic, no API).
                        - claude: real Claude API via subagent (requires Task tool
                          in the parent agent context — this script will print
                          the kickoff prompts the parent must run).
  --budget-usd N        Hard cap on estimated spend (default 5). Halts before
                        spawning if the projected cost exceeds.
  --workdir DIR         Workdir for transcripts (default: <sibling>/audit/dryrun/<ts>/).
  --kinds K1,K2         Restrict surface sampling to these kinds (default: verb,flag,error).
  --skip-verify         Skip post-condition checks (NOT recommended).

Output:
  Workdir contains:
    transcript_<surface>_<scorer>.jsonl  — full per-call I/O
    partial/scores_pass1_<surface>_scorer<X>.jsonl — scorer output
    agent_surfaces.dryrun.jsonl  — aggregated rows
    dryrun-report.md  — summary (post-conditions, IRR, cost, ETA full-pass)

Exit codes:
  0  Dry-run completed; all post-conditions pass.
  1  Post-condition failure (output schema, IRR too low, etc.).
  2  Budget exceeded before any work.
  3  Bad args / missing inputs.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 3 ;;
esac

die() {
  echo "$*" >&2
  exit 3
}

SIBLING="$1"; shift
N_SURFACES=10
MODE=stub
BUDGET_USD=5
WORKDIR=""
KINDS="verb,flag,error"
SKIP_VERIFY=0
need_value() {
  [ -n "${2:-}" ] || die "$1 requires a value"
  case "$2" in --*) die "$1 requires a value, got option-like token: $2" ;; esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --surfaces)
      need_value "$1" "${2:-}"
      N_SURFACES="$2"; shift 2
      ;;
    --mode)
      need_value "$1" "${2:-}"
      MODE="$2"; shift 2
      ;;
    --budget-usd)
      need_value "$1" "${2:-}"
      BUDGET_USD="$2"; shift 2
      ;;
    --workdir)
      need_value "$1" "${2:-}"
      WORKDIR="$2"; shift 2
      ;;
    --kinds)
      need_value "$1" "${2:-}"
      KINDS="$2"; shift 2
      ;;
    --skip-verify)  SKIP_VERIFY=1; shift ;;
    *) die "unknown arg: $1" ;;
  esac
done

case "$MODE" in stub|claude) ;; *) die "bad --mode: $MODE" ;; esac
case "$N_SURFACES" in
  ''|*[!0-9]*) die "bad --surfaces: $N_SURFACES (expected positive integer)" ;;
esac
[ "$N_SURFACES" -gt 0 ] || die "bad --surfaces: $N_SURFACES (expected positive integer)"
[ -n "$KINDS" ] || die "--kinds must not be empty"
if ! awk -v b="$BUDGET_USD" 'BEGIN { exit !(b ~ /^[0-9]+([.][0-9]+)?$/) }'; then
  die "bad --budget-usd: $BUDGET_USD (expected non-negative number)"
fi

INV="$SIBLING/audit/surface_inventory.jsonl"
[ -f "$INV" ] || { echo "no inventory: $INV" >&2; exit 3; }

# Workdir. Append PID so two concurrent dry-runs in the same second don't
# share a workdir and clobber each other's partials/transcripts.
TS=$(date -u +%Y%m%dT%H%M%SZ)-$$
[ -z "$WORKDIR" ] && WORKDIR="$SIBLING/audit/dryrun/$TS"
mkdir -p "$WORKDIR/partial" "$WORKDIR/transcripts"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STUB="$SKILL_DIR/scripts/stub-scorer.sh"
VERIFIER="$SKILL_DIR/scripts/dryrun-verify.sh"
surface_id_re='^[A-Za-z0-9][A-Za-z0-9._-]*__[A-Za-z0-9][A-Za-z0-9._-]*(__[A-Za-z0-9][A-Za-z0-9._-]*)*$'

# Sample up to N matching surfaces, stratified across requested kinds. Keep N
# as a strict cap: budget projection and scorer fan-out are derived from the
# sampled line count.
sampled="$WORKDIR/sampled_surfaces.jsonl"
: > "$sampled"
IFS=',' read -ra kind_arr <<< "$KINDS"
sample_kinds=()
declare -A seen_kinds=()
for kind in "${kind_arr[@]}"; do
  [ -n "$kind" ] || die "--kinds contains an empty entry"
  [ -n "${seen_kinds[$kind]:-}" ] && continue
  seen_kinds[$kind]=1
  sample_kinds+=("$kind")
done
kind_filter=$(printf '%s\n' "${sample_kinds[@]}" | jq -R . | jq -s .)
base_quota=$(( N_SURFACES / ${#sample_kinds[@]} ))
quota_remainder=$(( N_SURFACES % ${#sample_kinds[@]} ))
for idx in "${!sample_kinds[@]}"; do
  quota="$base_quota"
  [ "$idx" -lt "$quota_remainder" ] && quota=$((quota + 1))
  [ "$quota" -eq 0 ] && continue
  jq -c --arg k "${sample_kinds[$idx]}" 'select(.kind == $k)' "$INV" 2>/dev/null \
    | shuf -n "$quota" >> "$sampled" || true
done

# If a sparse kind could not fill its quota, top up from the remaining matching
# surfaces without exceeding N.
n_sampled=$(wc -l < "$sampled")
if [ "$n_sampled" -lt "$N_SURFACES" ]; then
  remaining=$((N_SURFACES - n_sampled))
  sampled_ids=$(jq -r '.surface_id // empty' "$sampled" | jq -R . | jq -s .)
  jq -c --argjson kinds "$kind_filter" --argjson seen "$sampled_ids" \
    'select(.kind as $k | $kinds | index($k))
     | select(.surface_id as $sid | ($seen | index($sid) | not))' \
    "$INV" 2>/dev/null \
    | shuf -n "$remaining" >> "$sampled" || true
fi
n_sampled=$(wc -l < "$sampled")
[ "$n_sampled" -eq 0 ] && { echo "no surfaces matched kinds: $KINDS" >&2; exit 3; }

# Cost projection. The unit is per-SCORER-per-surface (NOT per-surface):
# total = n_surfaces × per_scorer_usd × 2_scorers. Stub mode is free.
# Calibrate `claude` rate from real telemetry once you have it; the 0.50
# default is a conservative initial estimate for a mid-sized 11-dim scorer
# call against a small CLI surface (~8K input + ~400 output tokens).
case "$MODE" in
  stub)   per_scorer_usd=0.00 ;;
  claude) per_scorer_usd=0.50 ;;
esac
projected=$(awk -v n="$n_sampled" -v u="$per_scorer_usd" 'BEGIN{ printf "%.2f", n * u * 2 }')  # 2 scorers
echo "dryrun: $n_sampled surfaces × 2 scorers @ \$$per_scorer_usd/scorer = projected \$$projected (budget: \$$BUDGET_USD)"
if awk -v p="$projected" -v b="$BUDGET_USD" 'BEGIN{ exit !(p > b) }'; then
  echo "  BUDGET EXCEEDED — refusing to start. Lower --surfaces or raise --budget-usd." >&2
  exit 2
fi

# Stub a minimal manifest (the aggregator reads .current_pass).
if [ ! -f "$WORKDIR/manifest.stub.json" ]; then
  jq -nc '{schema_version:"1.0.0",tool_name:"dryrun",tool_repo:"/dev/null",audit_workspace:"/dev/null",current_pass:1,passes:[{pass:1,started_at:"2026-01-01T00:00:00Z",summary:{},artifacts:{}}]}' \
    > "$WORKDIR/manifest.stub.json"
fi

# Run scorers per surface.
n_run=0
echo "=== running scorers ==="
while IFS= read -r surface_rec; do
  [ -z "$surface_rec" ] && continue
  sid=$(echo "$surface_rec" | jq -r '.surface_id')
  if ! [[ "$sid" =~ $surface_id_re ]]; then
    printf 'invalid filename-unsafe surface_id: %q\n' "$sid" >&2
    exit 3
  fi
  printf '  %s ' "$sid"
  for scorer_id in A B; do
    out_partial="$WORKDIR/partial/scores_pass1_${sid}_scorer${scorer_id}.jsonl"
    transcript="$WORKDIR/transcripts/transcript_${sid}_scorer${scorer_id}.jsonl"
    case "$MODE" in
      stub)
        if ! bash "$STUB" "$sid" "$scorer_id" --inventory "$INV" \
          > "$out_partial" 2>"$transcript.stderr"; then
          printf 'stub scorer failed for surface_id %q scorer %s; see %s\n' "$sid" "$scorer_id" "$transcript.stderr" >&2
          exit 1
        fi
        # Build a synthetic transcript record for parity with claude mode.
        jq -nc \
          --arg sid "$sid" --arg sc "$scorer_id" --arg mode "$MODE" \
          --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
          --slurpfile out "$out_partial" \
          '{surface_id:$sid, scorer_id:$sc, mode:$mode, ts:$ts, output:$out[0]}' \
          > "$transcript"
        ;;
      claude)
        # In claude mode, the parent agent must spawn the actual scorer
        # subagent via the Task tool. This script CANNOT do that itself; it
        # just emits the kickoff prompt the parent should use, then halts
        # below before aggregate/verify (which would otherwise produce a
        # bogus "PASS" against zero partials).
        cat <<EOF
PARENT-AGENT-MUST-RUN: spawn agent-ergo-scorer with these inputs:
  SURFACE_ID=$sid
  SCORER_ID=$scorer_id
  SIBLING=$WORKDIR
  TARGET_SHA=(use the target's HEAD sha)
  RUBRIC_VERSION=(git SHA of references/rubric/SCORING-RUBRIC.md)
  PASS=1
  Output: $out_partial
EOF
        ;;
    esac
    printf '%s ' "$scorer_id"
  done
  echo
  n_run=$((n_run + 1))
done < "$sampled"

# Claude mode halts here — partials don't yet exist; aggregate/verify against
# nothing would produce a bogus "PASS" verdict. Parent agent must spawn the
# emitted prompts, then re-run aggregate_scores.sh + dryrun-verify.sh against
# the same workdir manually.
if [ "$MODE" = claude ]; then
  echo
  echo "claude mode: $((n_run * 2)) scorer prompts emitted above. To complete:"
  echo "  1. Spawn each prompt via the parent agent's Task tool."
  echo "  2. Confirm partials land at: $WORKDIR/partial/"
  echo "  3. Run: scripts/aggregate_scores.sh $WORKDIR"
  echo "  4. Run: scripts/dryrun-verify.sh $WORKDIR"
  exit 0
fi

# Aggregate (only if partials exist).
if compgen -G "$WORKDIR/partial/scores_pass1_*.jsonl" > /dev/null; then
  echo "=== aggregating ==="
  # The aggregator expects files at <sibling>/audit/partial/. Copy our manifest
  # to where the aggregator will look.
  mkdir -p "$WORKDIR/audit/partial"
  cp "$WORKDIR/partial/"scores_pass1_*.jsonl "$WORKDIR/audit/partial/"
  cp "$WORKDIR/manifest.stub.json" "$WORKDIR/audit/manifest.json"
  # Inventory needed by aggregator for evidence-merge schema.
  cp "$INV" "$WORKDIR/audit/surface_inventory.jsonl"
  if ! bash "$SKILL_DIR/scripts/aggregate_scores.sh" "$WORKDIR" >/dev/null; then
    echo "aggregation failed for dry-run workdir: $WORKDIR" >&2
    exit 1
  fi
  if [ -f "$WORKDIR/audit/agent_surfaces.jsonl" ]; then
    cp "$WORKDIR/audit/agent_surfaces.jsonl" "$WORKDIR/agent_surfaces.dryrun.jsonl"
  fi
fi

# Verify (unless skipped).
report="$WORKDIR/dryrun-report.md"
{
  echo "# Dry-Run Report"
  echo
  echo "- Workdir: \`$WORKDIR\`"
  echo "- Mode: $MODE"
  echo "- Surfaces sampled: $n_sampled"
  echo "- Scorers per surface: 2"
  echo "- Projected spend: \$$projected (budget \$$BUDGET_USD)"
  echo
} > "$report"

if [ "$SKIP_VERIFY" -eq 0 ] && [ -x "$VERIFIER" ]; then
  echo "=== verifying ==="
  if bash "$VERIFIER" "$WORKDIR" >> "$report" 2>&1; then
    verify_rc=0
  else
    verify_rc=1
  fi
else
  verify_rc=0
fi

echo
echo "=== summary ==="
/usr/bin/cat "$report"

exit "$verify_rc"
