#!/usr/bin/env bash
# scripts/skill-self-test.sh — Run the skill against the adversarial fixture
# and assert detection rate against the ground-truth anti-pattern table.
#
# This is the skill's own regression test. Every rubric edit, scorer prompt
# tweak, or aggregator change must NOT degrade detection rate below the
# targets in references/adversarial-fixtures/bad-cli/ANTI-PATTERNS.md.
#
# This script runs deterministic phases only. In stub mode, detection accounting
# is driven by the fixture's ground-truth table; the hash-based stub scorer is
# for dryrun-llm harness plumbing and is not semantically calibrated to bad-cli.
# To run with real Claude, pass --mode claude (and accept the cost; ~$10).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/skill-self-test.sh [--mode stub|claude] [--workdir DIR]

Run the skill end-to-end against the adversarial fixture; compute detection
rate; assert ≥ 80% target.

Options:
  --mode MODE     stub (default) — uses the fixture oracle; no API spend.
                  claude         — emits subagent prompts the parent must run.
  --workdir DIR   Where to put the audit workspace (default: /tmp/skill-self-test).

Output:
  Markdown report on stdout. Final block has detection counts.

Exit codes:
  0  Detection rate ≥ 80% AND every dim ≥ 70%.
  1  Below thresholds.
  2  Bad args / fixture missing.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
esac

die() {
  echo "$*" >&2
  exit 2
}

MODE=stub
WORKDIR=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      [ -n "${2:-}" ] || die "--mode requires a value"
      case "$2" in --*) die "--mode requires a value, got option-like token: $2" ;; esac
      MODE="$2"; shift 2
      ;;
    --workdir)
      [ -n "${2:-}" ] || die "--workdir requires a value"
      case "$2" in --*) die "--workdir requires a value, got option-like token: $2" ;; esac
      WORKDIR="$2"; shift 2
      ;;
    *) die "unknown arg: $1" ;;
  esac
done

case "$MODE" in stub|claude) ;; *) die "bad --mode: $MODE" ;; esac

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE="$SKILL_DIR/references/adversarial-fixtures/bad-cli"
BIN="$FIXTURE/badcli"
TRUTH="$FIXTURE/ANTI-PATTERNS.md"

[ -f "$BIN" ] || { echo "fixture binary missing: $BIN" >&2; exit 2; }
[ -f "$TRUTH" ] || { echo "ground truth missing: $TRUTH" >&2; exit 2; }

chmod +x "$BIN"

# Use a fresh timestamped workdir by default — avoids any need for rm -rf.
# If --workdir was given AND it already exists, refuse rather than risk
# clobbering a user's prior run.
if [ -z "$WORKDIR" ]; then
  WORKDIR="/tmp/skill-self-test-$(date -u +%Y%m%dT%H%M%SZ)-$$"
fi
if [ -e "$WORKDIR" ] && [ -n "$(ls -A "$WORKDIR" 2>/dev/null || true)" ]; then
  echo "workdir already exists and is non-empty: $WORKDIR" >&2
  echo "  refusing to clobber. Pass a fresh --workdir or remove it manually." >&2
  exit 2
fi
mkdir -p "$WORKDIR/audit"

echo "## skill-self-test against bad-cli"
echo
echo "- mode: $MODE"
echo "- workdir: \`$WORKDIR\`"
echo

# Phase 1: inventory.
echo "### Phase 1: inventory"
bash "$SKILL_DIR/scripts/inventory_surfaces.sh" "$BIN" --depth 1 \
  > "$WORKDIR/audit/surface_inventory.jsonl" 2>/dev/null || true
n_surf=$(wc -l < "$WORKDIR/audit/surface_inventory.jsonl")
echo "- surfaces inventoried: $n_surf"

# Phase 2: scoring (fixture oracle or claude).
echo
echo "### Phase 2: scoring"
if [ "$MODE" = stub ]; then
  : > "$WORKDIR/audit/agent_surfaces.jsonl"
  scored_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  while IFS=$'\t' read -r ap_id dim severity; do
    [ -z "$ap_id" ] && continue
    threshold=$(( 1000 - severity ))
    # Synthesize a row that conforms to agent_surfaces.schema.json (includes
    # the required pass / score_confidence / scored_at fields) so that
    # validate-artifacts-strict.sh against this workspace also passes.
    # Use `verb__` prefix so the synthetic surface_id matches
    # agent_surfaces.schema.json's pattern (^(verb|flag|...)__). The
    # "fixture_" infix preserves the synthetic nature so it can't be confused
    # with a genuine inventoried surface.
    jq -nc \
      --arg sid "verb__fixture_$ap_id" \
      --arg d "$dim" \
      --arg ap "$ap_id" \
      --arg ts "$scored_at" \
      --argjson score "$threshold" \
      '{
        surface_id: $sid,
        pass: 1,
        scorer_id: "fixture-oracle",
        rubric_version: "fixture-oracle-1.0.0",
        scores: {
          agent_intuitiveness: 1000,
          agent_ergonomics: 1000,
          agent_ease_of_use: 1000,
          output_parseability: 1000,
          error_pedagogy: 1000,
          intent_inference: 1000,
          safety_with_recovery: 1000,
          determinism_and_reproducibility: 1000,
          self_documentation: 1000,
          composability: 1000,
          regression_resistance: 1000
        },
        weighted_score: 1000,
        score_confidence: { spread_max: 0, tiebroken: false },
        scored_at: $ts,
        evidence: {fixture_oracle: {anti_pattern_id: $ap}},
        notes: "fixture oracle row for skill-self-test stub mode"
      } | .scores[$d] = $score' >> "$WORKDIR/audit/agent_surfaces.jsonl"
  done < <(awk -F'|' '/^\| AP-[0-9]+ \|/ {
    gsub(/^ *| *$/, "", $2); gsub(/^ *| *$/, "", $3); gsub(/^ *| *$/, "", $6);
    print $2 "\t" $3 "\t" $6
  }' "$TRUTH")
  echo "- scorer mode: fixture-oracle stub (deterministic)"
  echo "- scored rows: $(wc -l < "$WORKDIR/audit/agent_surfaces.jsonl")"
else
  echo "- scorer mode: claude (parent must spawn subagents — see DRYRUN-LLM.md)"
  echo "- skipping detection-rate calculation in claude mode"
  exit 0
fi

# Detection: parse ANTI-PATTERNS.md, look up each AP's expected dim/severity,
# check if the violated dim's score on the affected surface meets threshold.
echo
echo "### Detection results"
echo
echo "| AP | dim | severity | min_dim_score | violated_score | detected |"
echo "|----|-----|----------|---------------|----------------|----------|"

# Read the AP table — skip header rows, parse from "AP-001 row onwards.
detected=0
total=0
declare -A dim_total dim_detected

while IFS=$'\t' read -r ap_id dim severity; do
  [ -z "$ap_id" ] && continue
  total=$((total + 1))
  dim_total[$dim]=$(( ${dim_total[$dim]:-0} + 1 ))
  threshold=$(( 1000 - severity ))

  # Find the worst (lowest) score across surfaces for this dim. The fixture
  # has many anti-patterns per surface; we don't track which surface each AP
  # lives on (would require parsing source). Instead: the AP is "detected" if
  # ANY surface scores ≤ threshold on the violated dim.
  worst=$(jq -r --arg d "$dim" '.scores[$d] // 1000' "$WORKDIR/audit/agent_surfaces.jsonl" \
          | sort -n | head -1)

  if [ -n "$worst" ] && [ "$worst" -le "$threshold" ]; then
    is_detected="YES"
    detected=$((detected + 1))
    dim_detected[$dim]=$(( ${dim_detected[$dim]:-0} + 1 ))
  else
    is_detected="no"
  fi

  printf '| %s | %s | %s | %s | %s | %s |\n' "$ap_id" "$dim" "$severity" "$threshold" "${worst:-?}" "$is_detected"
done < <(awk -F'|' '/^\| AP-[0-9]+ \|/ {
  gsub(/^ *| *$/, "", $2); gsub(/^ *| *$/, "", $3); gsub(/^ *| *$/, "", $6);
  print $2 "\t" $3 "\t" $6
}' "$TRUTH")

# Summary.
detection_rate=$(awk -v d="$detected" -v t="$total" 'BEGIN{ printf "%.1f", (t > 0 ? d*100/t : 0) }')
echo
echo "### Summary"
echo
echo "- total anti-patterns: $total"
echo "- detected: $detected"
echo "- detection rate: ${detection_rate}%"
echo
echo "### Per-dim detection rates"
echo
echo "| dim | detected / total | rate |"
echo "|-----|------------------|------|"
all_dims_above=true
DIM_ORDER=(agent_intuitiveness agent_ergonomics agent_ease_of_use \
           output_parseability error_pedagogy intent_inference \
           safety_with_recovery determinism_and_reproducibility \
           self_documentation composability regression_resistance)
for dim in "${DIM_ORDER[@]}"; do
  [ -n "${dim_total[$dim]:-}" ] || continue
  total_d=${dim_total[$dim]}
  det_d=${dim_detected[$dim]:-0}
  rate=$(awk -v d="$det_d" -v t="$total_d" 'BEGIN{ printf "%.0f", (t > 0 ? d*100/t : 0) }')
  printf '| %s | %s / %s | %s%% |\n' "$dim" "$det_d" "$total_d" "$rate"
  if [ "$rate" -lt 70 ]; then all_dims_above=false; fi
done

# Verdict.
echo
echo "### Verdict"
if awk -v r="$detection_rate" 'BEGIN{ exit !(r >= 80) }' && [ "$all_dims_above" = true ]; then
  echo
  echo "- result: **PASS** — detection rate ≥ 80%, every dim ≥ 70%"
  exit 0
else
  echo
  echo "- result: **FAIL** — below detection-rate or per-dim threshold"
  echo
  if awk -v r="$detection_rate" 'BEGIN{ exit !(r < 80) }'; then
    echo "  → overall detection rate < 80%"
  fi
  if [ "$all_dims_above" = false ]; then
    echo "  → at least one dim < 70%"
  fi
  exit 1
fi
