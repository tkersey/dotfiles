---
name: lift
description: "Comprehensive, measurement-driven performance optimization for latency, throughput, memory/GC, and tail behavior. Use when the user asks to optimize/speed up, reduce latency (p95/p99), increase throughput/QPS, lower CPU/memory/allocations/GC pauses, profile hot paths, or run a benchmarked perf pass (including JSONL/query-heavy code). Requires before/after measurement on a runnable workload (or an explicit `UNMEASURED` plan) plus a correctness gate. Zig-first CLI iteration where `bench_stats`/`perf_report` are proven first and wrappers are kept in parity."
---

# Lift

## Intent

Deliver aggressive, measurement-driven performance improvements (latency/throughput/memory/GC/tail) with correctness preserved and regressions guarded.

## Double Diamond fit

Lift lives in Define -> Deliver:
- Define: write a performance contract and pick a proof workload.
- Deliver: measure baseline, profile, run tight experiments, then ship with a guard.

## Hard Rules

- Measure before and after every optimization (numbers + environment + command).
- Optimize the bottleneck, not the loudest hunch (profile/trace/counters required).
- Avoid micro-optimizations until algorithmic wins are exhausted.
- Keep correctness and safety invariants intact.
- Require a correctness signal before and after; never accept a perf win with failing correctness.
- Do not change semantics without explicit user approval.
- If you cannot run a proof workload, label the output `UNMEASURED` and provide exact benchmark/profiling commands; treat all optimization ideas as hypotheses.
- Stop and ask before raising resource/cost ceilings (CPU cores, memory footprint, I/O bytes, external calls), unless explicitly requested.
- Stop when ROI is negative or risk exceeds benefit.
- For Lift-owned CLIs, iterate on Zig binaries first (`bench_stats`, `perf_report`) and prove that execution path before touching wrappers.
- After any Zig CLI contract change, bring Python and any existing Node wrappers along in the same pass by matching flags, outputs, and error behavior.

## Default policy (non-interactive)

Goal: stay autonomous without inventing SLOs.

### Mode selection (measured vs unmeasured)

If you can run a proof workload, operate in measured mode. Otherwise operate in unmeasured mode.

- Measured: run baseline + variant on the same workload; include numbers, bottleneck evidence, and a correctness signal.
- Unmeasured: start with `UNMEASURED: <why>`; do not claim wins; provide the exact commands you would run to produce baseline/after + profiling evidence.

### Contract derivation

If the user did not provide a numeric target:
- Define the contract as: "Improve <metric> on <workload> vs baseline; report delta; do not regress <constraints>."
- Do not invent SLO numbers; treat the goal as "maximize improvement within constraints".

Metric defaults (pick one):
- Request-like: latency p95 (also report p50/p99).
- Batch/offline: throughput (also report CPU% and memory).
- Memory issues: peak RSS + alloc rate / GC pause (also report latency).

### Workload selection (proof signal)

Pick the first runnable, representative workload you can find:
1. User-provided repro/command.
2. Existing repo benchmark/harness (README, scripts, Makefile/justfile/taskfile).
3. A minimal harness around the hot path (microbench) plus a correctness signal.

Stop and ask only if you cannot find or create any runnable proof workload without product ambiguity.

### Experiment hygiene

- Change one variable at a time; keep diffs small and reversible.
- Reject wins smaller than the noise floor; re-run when variance is high.
- Track second-order regressions (memory, tail latency, CPU) even if the primary metric improves.

## Workflow (Opinionated)

0. Preflight
   - Capture environment (hardware/OS/runtime flags).
   - Pick a correctness signal and a performance workload; run each once to verify they work.
1. Performance contract
   - Metric + percentile + workload + environment + constraints.
2. Baseline
   - Warm up; collect enough samples for stable percentiles (keep raw samples when possible).
3. Locate the bottleneck
   - Profile/trace; classify bound (CPU/memory/I/O/lock/tail).
4. Choose the highest-leverage lever
   - Follow the optimization ladder: delete work -> algorithm -> data/layout -> concurrency -> I/O -> micro-arch -> runtime/compiler.
5. Run tight experiments (loop)
   - Hypothesis -> patch -> measure -> accept/reject -> record.
6. Ship with guards
   - Add/extend a benchmark, budget, or alert; document trade-offs.
7. Report
   - Present baseline vs variant and the evidence trail.
8. Wrapper convergence (Zig first)
   - Lock Zig behavior first and capture proof (`<tool> --help` marker check plus one sample run).
   - Update each wrapper that exists (Python today, Node when present) to keep CLI/output parity.
   - Validate parity on the same sample input before shipping.

## Decision Gates

- If the baseline is noisy or unstable, fix measurement first.
- If the complexity class dominates, change the algorithm first.
- If tail latency dominates, treat variance reduction as the primary goal.
- If I/O dominates, reduce bytes, syscalls, or round trips before CPU tuning.
- If the only remaining wins require higher resource/cost ceilings, surface the trade-off and ask.
- Stop when ROI is negative or risk exceeds benefit.

## Deliverable format (chat)

If unmeasured, prefix the response with `UNMEASURED: <reason>` and fill sections with a concrete measurement plan (no claimed deltas).

Output exactly these sections (short, numbers-first):

**Performance contract**
- Metric + percentile:
- Workload command:
- Dataset:
- Environment:
- Constraints:

**Baseline**
- Samples + warmup:
- Results (min/p50/p95/p99/max):
- Notes on variance/noise (or estimated noise floor):

**Bottleneck evidence**
- Tool + key finding:
- Hot paths / contention points:
- Bound classification:

**Experiments**
- <1-3 entries> Hypothesis -> change -> measurement delta -> decision

**Result**
- Variant results (min/p50/p95/p99/max):
- Delta vs baseline:
- Confidence (noise/variance):
- Trade-offs / regressions checked:

**Regression guard**
- Benchmark/budget added:
- Threshold (if any):

**Validation**
- Correctness command(s) -> pass/fail
- Performance command(s) -> numbers

**Residual risks / next steps**
- <bullets>

`lift_compliance: mode=<measured|unmeasured>; workload=<yes|no>; baseline=<yes|no>; after=<yes|no>; correctness=<yes|no>; bottleneck_evidence=<yes|no>`

## Core References (Load on Demand)

- Read `references/playbook.md` for the master flow and optimization ladder.
- Read `references/measurement.md` for benchmarking and statistical rigor.
- Read `references/profiling-tools.md` for a profiler/tool matrix and evidence artifacts.
- Read `references/algorithms-and-data-structures.md` for algorithmic levers.
- Read `references/systems-and-architecture.md` for CPU, memory, and OS tactics.
- Read `references/latency-throughput-tail.md` for queueing and tail behavior.
- Read `references/optimization-tactics.md` for a tactical catalog by layer.
- Read `references/checklists.md` for fast triage and validation checklists.
- Read `references/anti-patterns.md` to avoid common traps.

## Scripts

- Prefer this brew-aware launcher pattern for Lift CLIs:

```bash
CODEX_SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_SKILLS_HOME="${CLAUDE_HOME:-$HOME/.claude}"
LIFT_SCRIPTS_DIR="$CODEX_SKILLS_HOME/skills/lift/scripts"
[ -d "$LIFT_SCRIPTS_DIR" ] || LIFT_SCRIPTS_DIR="$CLAUDE_SKILLS_HOME/skills/lift/scripts"

run_lift_tool() {
  local subcommand="${1:-}"
  if [ -z "$subcommand" ]; then
    echo "usage: run_lift_tool <bench-stats|perf-report> [args...]" >&2
    return 2
  fi
  shift || true

  local bin=""
  local marker=""
  local fallback_py=""
  local fallback_node=""
  case "$subcommand" in
    bench-stats)
      bin="bench_stats"
      marker="bench_stats.zig"
      fallback_py="$LIFT_SCRIPTS_DIR/bench_stats.py"
      fallback_node="$LIFT_SCRIPTS_DIR/bench_stats.mjs"
      ;;
    perf-report)
      bin="perf_report"
      marker="perf_report.zig"
      fallback_py="$LIFT_SCRIPTS_DIR/perf_report.py"
      fallback_node="$LIFT_SCRIPTS_DIR/perf_report.mjs"
      ;;
    *)
      echo "unknown lift subcommand: $subcommand" >&2
      return 2
      ;;
  esac

  if command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"; then
    "$bin" "$@"
    return
  fi
  if [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
    if ! brew install tkersey/tap/lift; then
      echo "brew install tkersey/tap/lift failed; refusing silent fallback." >&2
      return 1
    fi
    if command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"; then
      "$bin" "$@"
      return
    fi
    echo "brew install tkersey/tap/lift did not produce a compatible $bin binary." >&2
    return 1
  fi
  if [ -f "$fallback_node" ] && command -v node >/dev/null 2>&1; then
    node "$fallback_node" "$@"
    return
  fi
  if [ -f "$fallback_py" ]; then
    uv run python "$fallback_py" "$@"
    return
  fi
  echo "lift binary missing and wrapper fallback not found (node: $fallback_node, python: $fallback_py)" >&2
  return 1
}

run_lift_tool bench-stats --input samples.txt --unit ms
run_lift_tool perf-report --title "Perf pass" --owner "team" --system "service" --output /tmp/perf-report.md
```

- Equivalent wrapper fallback commands remain valid:
  - Python (always present in this skill folder):
    - `uv run python scripts/perf_report.py --title "Perf pass" --owner "team" --system "service" --output /tmp/perf-report.md`
    - `uv run python scripts/bench_stats.py --input samples.txt --unit ms`
  - Node (optional; only if you add `scripts/*.mjs` wrappers):
    - `node scripts/perf_report.mjs --title "Perf pass" --owner "team" --system "service" --output /tmp/perf-report.md`
    - `node scripts/bench_stats.mjs --input samples.txt --unit ms`

- Zig proof snippet:
  - `command -v bench_stats && bench_stats --help 2>&1 | grep -q bench_stats.zig`
  - `command -v perf_report && perf_report --help 2>&1 | grep -q perf_report.zig`

## Assets

- Use `assets/perf-report-template.md` as a ready-to-edit report.
- Use `assets/experiment-log-template.md` to track experiments and results.

## Output Expectations

- Deliver a baseline, bottleneck evidence, hypothesis, experiment plan, and measured result.
- Provide a minimal diff that preserves correctness and includes a regression guard.
- Explain trade-offs in plain language and record the measured delta.
