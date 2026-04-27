#!/usr/bin/env bash
# bench_baseline.sh — Canonical baseline wrapper for same-host repeated runs.
#
# Captures a fingerprint, runs the user's benchmark command under controlled conditions,
# exports hyperfine JSON, and bundles everything under tests/artifacts/perf/<run-id>/.
#
# Usage:
#   bench_baseline.sh --name <scenario> --cmd "<command>" [--runs 20] [--warmup 3]
#                     [--output-dir tests/artifacts/perf] [--taskset 2,3] [--cold]
#
# The wrapper DOES NOT tune the kernel; pair with scripts/profile_init.sh for that
# (which asks before applying).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

name=""
cmd=""
runs=20
warmup=3
output_dir="tests/artifacts/perf"
taskset_cpus=""
cold_cache=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)        name="$2"; shift 2;;
    --cmd)         cmd="$2"; shift 2;;
    --runs)        runs="$2"; shift 2;;
    --warmup)      warmup="$2"; shift 2;;
    --output-dir)  output_dir="$2"; shift 2;;
    --taskset)     taskset_cpus="$2"; shift 2;;
    --cold)        cold_cache=1; shift;;
    -h|--help)
      sed -n '2,20p' "$0"; exit 0;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[[ -n "$name" && -n "$cmd" ]] || { echo "ERROR: --name and --cmd required" >&2; exit 2; }
command -v hyperfine >/dev/null || { echo "ERROR: install hyperfine" >&2; exit 2; }
command -v jq        >/dev/null || { echo "ERROR: install jq" >&2; exit 2; }

run_id="$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short HEAD 2>/dev/null || echo nosha)"
out="${output_dir}/${name}/${run_id}"
mkdir -p "$out"
echo "→ artifacts: $out"

# Fingerprint
if [[ -x "$SCRIPT_DIR/env_fingerprint.sh" ]]; then
  "$SCRIPT_DIR/env_fingerprint.sh" --run-id "$run_id" > "$out/fingerprint.json"
else
  echo "WARN: env_fingerprint.sh not executable; skipping fingerprint" >&2
fi

# Wrap in taskset if requested
runner="$cmd"
if [[ -n "$taskset_cpus" ]]; then
  runner="taskset -c ${taskset_cpus} bash -c \"$cmd\""
fi

# Optional cold cache — requires sudo; ASK the user before using this flag in CI.
prepare_cmd=""
if [[ "$cold_cache" -eq 1 ]]; then
  echo "→ cold-cache mode requires: sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'"
  prepare_cmd='sync && sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"'
fi

# Run hyperfine
set +e
if [[ -n "$prepare_cmd" ]]; then
  hyperfine --warmup "$warmup" --runs "$runs" \
            --prepare "$prepare_cmd" \
            --export-json "$out/hyperfine.json" \
            --export-markdown "$out/hyperfine.md" \
            "$runner"
else
  hyperfine --warmup "$warmup" --runs "$runs" \
            --export-json "$out/hyperfine.json" \
            --export-markdown "$out/hyperfine.md" \
            "$runner"
fi
hf_rc=$?
set -e

# Derive p50/p95/p99 from hyperfine times (sec → ms).
# Uses nearest-rank indexing: ceil(p*N)-1, clamped into bounds.
jq --arg scenario "$name" '
  .results[0] as $r
  | ($r.times | sort) as $t
  | ($t | length) as $n
  | (if $n == 0 then 0 else ($n - 1) end) as $max_i
  | def ceil_num: if . == floor then . else floor + 1 end;
  | def pct_index(p):
      if $n == 0 then null
      else
        (($n * p | ceil_num) - 1) as $idx
        | if $idx < 0 then 0 elif $idx > $max_i then $max_i else $idx end
      end;
  | def pct_ms(p): if $n == 0 then null else ($t[pct_index(p)] * 1000) end;
  {
      scenario: $scenario,
      runs: $n,
      mean_ms: ($r.mean * 1000),
      stddev_ms: ($r.stddev * 1000),
      p50_ms: pct_ms(0.50),
      p95_ms: pct_ms(0.95),
      p99_ms: pct_ms(0.99),
      max_ms: (if $n == 0 then null else ($t[-1] * 1000) end)
    }
' "$out/hyperfine.json" > "$out/summary.json" || true

echo "→ summary.json:"
cat "$out/summary.json" 2>/dev/null || true

# Roll up to a latest-symlink for easy diffing
ln -sfn "$run_id" "${output_dir}/${name}/latest"

exit $hf_rc
