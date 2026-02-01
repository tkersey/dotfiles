---
name: lift
description: Comprehensive performance optimization for algorithmic and systems-level code, covering latency, throughput, memory/GC, and tail latency. Use when asked to speed up code, reduce latency, improve throughput, lower memory usage, diagnose bottlenecks, design benchmarks, or produce performance experiments and reports.
---

# Lift

## Intent

Deliver aggressive, measurement-driven performance improvements (latency/throughput/memory/GC/tail) with correctness preserved and regressions guarded.

## Double Diamond fit

Lift lives in Define -> Deliver:
- Define: write a performance contract and pick a proof workload.
- Deliver: measure baseline, profile, run tight experiments, then ship with a guard.

## When to use

- "optimize" / "speed up" / "slow"
- "reduce latency" / "p95/p99" / "tail latency"
- "increase throughput" / "QPS"
- "high CPU" / "GC" / "allocations" / "memory blowups"
- "contention" / "locks" / "hot path"

## Hard Rules

- Measure before and after every optimization (numbers + environment + command).
- Optimize the bottleneck, not the loudest hunch (profile/trace/counters required).
- Avoid micro-optimizations until algorithmic wins are exhausted.
- Keep correctness and safety invariants intact.
- Require a correctness signal before and after; never accept a perf win with failing correctness.
- Do not change semantics without explicit user approval.
- Stop and ask before raising resource/cost ceilings (CPU cores, memory footprint, I/O bytes, external calls), unless explicitly requested.
- Stop when ROI is negative or risk exceeds benefit.

## Default policy (non-interactive)

Goal: stay autonomous without inventing SLOs.

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

## Decision Gates

- If the baseline is noisy or unstable, fix measurement first.
- If the complexity class dominates, change the algorithm first.
- If tail latency dominates, treat variance reduction as the primary goal.
- If I/O dominates, reduce bytes, syscalls, or round trips before CPU tuning.
- If the only remaining wins require higher resource/cost ceilings, surface the trade-off and ask.
- Stop when ROI is negative or risk exceeds benefit.

## Deliverable format (chat)

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

## Core References (Load on Demand)

- Read `references/playbook.md` for the master flow and optimization ladder.
- Read `references/measurement.md` for benchmarking and statistical rigor.
- Read `references/algorithms-and-data-structures.md` for algorithmic levers.
- Read `references/systems-and-architecture.md` for CPU, memory, and OS tactics.
- Read `references/latency-throughput-tail.md` for queueing and tail behavior.
- Read `references/optimization-tactics.md` for a tactical catalog by layer.
- Read `references/checklists.md` for fast triage and validation checklists.
- Read `references/anti-patterns.md` to avoid common traps.

## Scripts

- Run `scripts/perf_report.py` to generate a performance report template.
- Run `scripts/bench_stats.py` to summarize benchmark samples and percentiles.

## Assets

- Use `assets/perf-report-template.md` as a ready-to-edit report.
- Use `assets/experiment-log-template.md` to track experiments and results.

## Output Expectations

- Deliver a baseline, bottleneck evidence, hypothesis, experiment plan, and measured result.
- Provide a minimal diff that preserves correctness and includes a regression guard.
- Explain trade-offs in plain language and record the measured delta.
