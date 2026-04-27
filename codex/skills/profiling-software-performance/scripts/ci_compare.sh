#!/usr/bin/env bash
# ci_compare.sh — Compare baseline vs candidate summary.json emitted by bench_baseline.sh.
# Exits non-zero if selected metrics regress by more than the allowed percentage (default 5%).
#
# Usage:
#   ci_compare.sh baseline/summary.json candidate/summary.json
#       [--max-pct 5] [--metrics p50_ms,p95_ms,p99_ms] [--min-samples 20]
#       [--baseline-fingerprint baseline/fingerprint.json]
#       [--candidate-fingerprint candidate/fingerprint.json]
#       [--allow-fingerprint-mismatch]
#
# Intended to be wired into CI as the final gate (see references/CI-REGRESSION-GATES.md).

set -euo pipefail

[[ $# -ge 2 ]] || { echo "usage: $0 baseline.json candidate.json [--max-pct N]" >&2; exit 2; }
baseline="$1"; candidate="$2"; shift 2
max_pct=5
metrics="p50_ms,p95_ms,p99_ms"
min_samples=20
baseline_fp=""
candidate_fp=""
allow_fp_mismatch=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-p95-pct|--max-pct) max_pct="$2"; shift 2;;
    --metrics) metrics="$2"; shift 2;;
    --min-samples) min_samples="$2"; shift 2;;
    --baseline-fingerprint) baseline_fp="$2"; shift 2;;
    --candidate-fingerprint) candidate_fp="$2"; shift 2;;
    --allow-fingerprint-mismatch) allow_fp_mismatch=1; shift;;
    *) echo "unknown: $1" >&2; exit 2;;
  esac
done

command -v jq >/dev/null || { echo "ERROR: install jq" >&2; exit 2; }

check_samples() {
  local file="$1" label="$2" runs
  runs=$(jq -r '.runs // empty' "$file")
  if [[ -n "$runs" ]]; then
    awk -v r="$runs" -v min="$min_samples" -v label="$label" 'BEGIN {
      if (r < min) {
        printf "ERROR: %s has only %s runs; min-samples is %s\n", label, r, min > "/dev/stderr"
        exit 1
      }
    }' || exit 2
  fi
}

check_fingerprints() {
  [[ -n "$baseline_fp" || -n "$candidate_fp" ]] || return 0
  [[ -n "$baseline_fp" && -n "$candidate_fp" ]] || { echo "ERROR: provide both fingerprint paths or neither" >&2; exit 2; }

  local mismatch=0
  local fields=(
    '.hardware.cpu_model'
    '.hardware.cpu_threads_total'
    '.storage.filesystem'
    '.os.kernel'
    '.build_profile.name'
    '.build_profile.opt_level'
    '.build_profile.lto'
    '.build_profile.codegen_units'
    '.build_profile.debug'
    '.build_profile.strip'
    '.build_profile.frame_pointers'
    '.workload_isolation.taskset'
    '.workload_isolation.cgroup'
    '.workload_isolation.rch'
    '.workload_isolation.bare'
    '.workload_isolation.cache_state'
    '.tuning_applied.governor'
    '.tuning_applied.no_turbo'
    '.tuning_applied.smt_active'
  )

  echo "fingerprint compatibility:"
  for field in "${fields[@]}"; do
    b_val=$(jq -r "$field // \"\"" "$baseline_fp")
    c_val=$(jq -r "$field // \"\"" "$candidate_fp")
    if [[ "$b_val" != "$c_val" ]]; then
      printf '  MISMATCH %-38s baseline=%s candidate=%s\n' "$field" "$b_val" "$c_val"
      mismatch=1
    fi
  done

  if [[ "$mismatch" -eq 1 && "$allow_fp_mismatch" -ne 1 ]]; then
    echo "FAIL — fingerprint mismatch; rerun on comparable host/config or pass --allow-fingerprint-mismatch for advisory comparisons"
    exit 1
  fi
  [[ "$mismatch" -eq 0 ]] && echo "  OK"
}

compare_metric() {
  local metric="$1" b_val c_val delta_pct exceeds
  b_val=$(jq -r --arg m "$metric" '.[$m] // empty' "$baseline")
  c_val=$(jq -r --arg m "$metric" '.[$m] // empty' "$candidate")
  [[ -n "$b_val" && -n "$c_val" ]] || { echo "ERROR: missing $metric field" >&2; exit 2; }

  delta_pct=$(awk -v b="$b_val" -v c="$c_val" 'BEGIN {
    if (b == 0) {
      if (c == 0) print "0.00"; else print "inf"
    } else {
      printf "%.2f", (c-b)/b*100.0
    }
  }')
  exceeds=$(awk -v b="$b_val" -v c="$c_val" -v m="$max_pct" 'BEGIN {
    if (b == 0) { print (c > 0) ? 1 : 0 }
    else { print (((c-b)/b*100.0) > m) ? 1 : 0 }
  }')

  echo "$metric baseline  : ${b_val} ms"
  echo "$metric candidate : ${c_val} ms"
  echo "$metric delta     : ${delta_pct}%"
  echo "$metric threshold : +${max_pct}% regression"

  if [[ "$exceeds" -eq 1 ]]; then
    echo "FAIL — $metric regressed beyond ${max_pct}% threshold"
    return 1
  fi
  return 0
}

check_samples "$baseline" "baseline"
check_samples "$candidate" "candidate"
check_fingerprints

failed=0
IFS=',' read -ra metric_list <<< "$metrics"
for metric in "${metric_list[@]}"; do
  compare_metric "$metric" || failed=1
done

if [[ "$failed" -eq 1 ]]; then
  exit 1
fi
echo "PASS — selected metrics within regression threshold"
