---
name: lift
description: "Comprehensive, measurement-driven performance optimization for latency, throughput, memory/GC, and tail behavior. Use when the user asks to optimize/speed up, reduce latency (p95/p99), increase throughput/QPS, lower CPU/memory/allocations/GC pauses, profile hot paths, or run a benchmarked perf pass (including JSONL/query-heavy code). Requires before/after measurement on a runnable workload (or an explicit `UNMEASURED` plan) plus a correctness gate. Zig-only CLI iteration where `bench_stats`/`perf_report` are proven before shipping."
---

# Lift

## Intent

Deliver aggressive, measurement-driven performance improvements (latency/throughput/memory/GC/tail) with correctness preserved and regressions guarded.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `bench_stats`/`perf_report` helper CLI path, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for `bench_stats` and `perf_report`, build/test wiring, and release tags.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): Homebrew formula updates/checksum bumps for released `lift` binaries.

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
- For Lift-owned CLIs, use Zig binaries only (`bench_stats`, `perf_report`) and prove compatibility via marker checks before use.
- After any Zig CLI contract change, update docs and release/tap propagation in the same pass so install guidance matches runtime behavior.
- When running `$lift` on `$lift` with `$ms`, require a runnable proof bundle before done: Zig marker checks plus one sample invocation per CLI.

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
8. CLI proof (Zig only)
   - Lock Zig behavior and capture proof (`<tool> --help` marker check plus one sample run).
   - Keep install/run guidance in sync with the released `lift` binary behavior before shipping.

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

- Prefer this brew-aware launcher pattern for Lift CLIs (Zig-only, fail-closed):

```bash
run_lift_tool() {
  local subcommand="${1:-}"
  if [ -z "$subcommand" ]; then
    echo "usage: run_lift_tool <bench-stats|perf-report> [args...]" >&2
    return 2
  fi
  shift || true

  local bin=""
  local marker=""
  case "$subcommand" in
    bench-stats)
      bin="bench_stats"
      marker="bench_stats.zig"
      ;;
    perf-report)
      bin="perf_report"
      marker="perf_report.zig"
      ;;
    *)
      echo "unknown lift subcommand: $subcommand" >&2
      return 2
      ;;
  esac

  install_lift_direct() {
    local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
    if ! command -v zig >/dev/null 2>&1; then
      echo "zig not found. Install Zig from https://ziglang.org/download/ and retry." >&2
      return 1
    fi
    if [ ! -d "$repo" ]; then
      echo "skills-zig repo not found at $repo." >&2
      echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
      return 1
    fi
    if ! (cd "$repo" && zig build -Doptimize=ReleaseSafe); then
      echo "direct Zig build failed in $repo." >&2
      return 1
    fi
    if [ ! -x "$repo/zig-out/bin/$bin" ]; then
      echo "direct Zig build did not produce $repo/zig-out/bin/$bin." >&2
      return 1
    fi
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/$bin" "$HOME/.local/bin/$bin"
  }

  local os="$(uname -s)"
  if command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"; then
    "$bin" "$@"
    return
  fi

  if [ "$os" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "homebrew is required on macOS: https://brew.sh/" >&2
      return 1
    fi
    if ! brew install tkersey/tap/lift; then
      echo "brew install tkersey/tap/lift failed." >&2
      return 1
    fi
  elif ! (command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"); then
    if ! install_lift_direct; then
      return 1
    fi
  fi

  if command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"; then
    "$bin" "$@"
    return
  fi
  echo "missing compatible $bin binary after install attempt." >&2
  if [ "$os" = "Darwin" ]; then
    echo "expected install path: brew install tkersey/tap/lift" >&2
  else
    echo "expected direct path: SKILLS_ZIG_REPO=<skills-zig-path> zig build -Doptimize=ReleaseSafe" >&2
  fi
  return 1
}

run_lift_tool bench-stats --input samples.txt --unit ms
run_lift_tool perf-report --title "Perf pass" --owner "team" --system "service" --output /tmp/perf-report.md
```

- Direct Zig CLI commands:
  - `bench_stats --input samples.txt --unit ms`
  - `perf_report --title "Perf pass" --owner "team" --system "service" --output /tmp/perf-report.md`

- Zig proof snippet:
  - `command -v bench_stats && bench_stats --help 2>&1 | grep -q bench_stats.zig`
  - `command -v perf_report && perf_report --help 2>&1 | grep -q perf_report.zig`

- Sample invocation proof snippet:
  - `bench_stats --input samples.txt --unit ms`
  - `perf_report --title "Perf pass" --owner "team" --system "service" --output /tmp/perf-report.md`

## Assets

- Use `assets/perf-report-template.md` as a ready-to-edit report.
- Use `assets/experiment-log-template.md` to track experiments and results.

## Output Expectations

- Deliver a baseline, bottleneck evidence, hypothesis, experiment plan, and measured result.
- Provide a minimal diff that preserves correctness and includes a regression guard.
- Explain trade-offs in plain language and record the measured delta.
