#!/usr/bin/env bash
# honest_gate.sh — Walk the 14 questions in references/HONEST-GATE-CHECKLIST.md
# and emit a JSON attestation paired with the bench result.
#
# Usage:
#   honest_gate.sh --scenario NAME --result-dir DIR [--non-interactive ANSWERS_FILE]
#
# Each answer is one of: pass | fail | waive:<reason>. Answers are written to
# DIR/honest_gate_attestation.json with a SHA256 of fingerprint.json and the
# attesting user/CI run-id (from $USER and $GITHUB_RUN_ID if present).

set -euo pipefail

scenario=""
result_dir=""
ans_file=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scenario)        scenario="$2"; shift 2;;
    --result-dir)      result_dir="$2"; shift 2;;
    --non-interactive) ans_file="$2"; shift 2;;
    -h|--help) sed -n '2,12p' "$0"; exit 0;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[[ -n "$scenario" && -n "$result_dir" ]] || { echo "usage: $0 --scenario NAME --result-dir DIR" >&2; exit 2; }
[[ -d "$result_dir" ]] || { echo "result-dir not found: $result_dir" >&2; exit 2; }

questions=(
  "1_written_scenario:Scenario written down with metric and the claim you want to make?"
  "2_same_build_profile:Both implementations on the same build profile (release-perf / LTO=true)?"
  "3_api_matched:API surfaces matched (prepared-vs-prepared, batched-vs-batched)?"
  "4_pragmas_identical:Tuning knobs / PRAGMAs identical and enforced (gate fails on divergence)?"
  "5_realistic_workload:Workload is a realistic slice of the actual use case?"
  "6_same_fixture:Same fixture / golden copy on both sides, reset per iteration?"
  "7_warmup_symmetric:Warmup symmetric (same N iterations, discarded both sides)?"
  "8_N_sufficient:N >= 20 samples after warmup AND >= 10 seconds wall clock?"
  "9_host_quiet:Host quiet (no parallel heavy jobs, governor=performance, fingerprint captured)?"
  "10_variance_envelope:Three repeat runs hold p95 drift <= 10% (variance_envelope.py)?"
  "11_three_tier_reporting:Reporting uses 3 tiers (BelowParity / ParityToMargin / HealthyMargin)?"
  "12_losses_published:Every workload x concurrency cell published, including losses?"
  "13_apples_flagged:Apples-to-oranges axes flagged in-source (in-code comment near the bench)?"
  "14_reproducible:Result reproducible from spec (HarnessSettings + git SHA + host)?"
)

declare -A answers
ask() {
  local key="$1" prompt="$2"
  local ans=""
  if [[ -n "$ans_file" ]]; then
    ans=$(awk -v k="$key" 'index($0, k"=")==1 {print substr($0, length(k)+2); exit}' "$ans_file")
    if [[ -z "$ans" ]]; then
      echo "non-interactive: missing answer for $key in $ans_file" >&2
      exit 2
    fi
  else
    while true; do
      printf "  %s\n  [pass | fail | waive:<reason>]> " "$prompt"
      read -r ans
      [[ "$ans" =~ ^(pass|fail|waive:.+)$ ]] && break
      echo "  invalid; expected pass / fail / waive:<reason>"
    done
  fi
  answers[$key]="$ans"
}

echo "=== honest_gate for: $scenario ==="
echo "result_dir: $result_dir"
echo

for q in "${questions[@]}"; do
  key="${q%%:*}"
  prompt="${q#*:}"
  echo "Q$key"
  ask "$key" "$prompt"
  echo
done

# Hash fingerprint if present
fp_path="$result_dir/fingerprint.json"
fp_sha="missing"
if [[ -f "$fp_path" ]]; then
  fp_sha=$(sha256sum "$fp_path" | awk '{print $1}')
fi

git_sha=$(git rev-parse HEAD 2>/dev/null || echo "no-git")
attester="${GITHUB_RUN_ID:-${USER:-unknown}}"
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)

out="$result_dir/honest_gate_attestation.json"
{
  for q in "${questions[@]}"; do
    key="${q%%:*}"
    printf '%s\t%s\n' "$key" "${answers[$key]}"
  done
} | python3 -c '
import json
import sys

scenario, ts, git_sha, fp_sha, attester = sys.argv[1:6]
answers = {}
for line in sys.stdin:
    key, value = line.rstrip("\n").split("\t", 1)
    answers[key] = value

print(json.dumps({
    "scenario": scenario,
    "timestamp": ts,
    "git_sha": git_sha,
    "host_fingerprint_sha256": fp_sha,
    "attested_by": attester,
    "questions": answers,
}, indent=2, sort_keys=True))
' "$scenario" "$ts" "$git_sha" "$fp_sha" "$attester" > "$out"

echo "wrote attestation: $out"

# Summarize
fails=$(printf '%s\n' "${answers[@]}" | grep -c '^fail$' || true)
waives=$(printf '%s\n' "${answers[@]}" | grep -c '^waive:' || true)
echo
echo "summary: ${#answers[@]} questions, $fails fail, $waives waive"
exit "$fails"
