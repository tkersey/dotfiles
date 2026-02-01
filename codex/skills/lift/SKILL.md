---
name: lift
description: Comprehensive performance optimization for algorithmic and systems-level code, covering latency, throughput, memory/GC, and tail latency. Use when asked to speed up code, reduce latency, improve throughput, lower memory usage, diagnose bottlenecks, design benchmarks, or produce performance experiments and reports.
---

# Lift

## Overview

Deliver aggressive, measurement-driven optimization across algorithmic and systems layers. Prioritize correctness, quantify wins, and add regression guards.

## Workflow (Opinionated)

1. Define the performance contract.
   - Specify metric, target, percentile, dataset, environment, and constraints.
   - Refuse to optimize without a measurable goal.
2. Establish a trustworthy baseline.
   - Build a benchmark or workload that matches real usage.
   - Validate noise, warmup, and steady state.
3. Locate the bottleneck.
   - Profile or trace to find hot paths and contention.
   - Classify the bound (CPU, memory, I/O, lock, tail variance).
4. Choose the highest-leverage optimization class.
   - Prefer algorithmic and data-structure changes over micro-tuning.
   - Pick the smallest change that yields the largest win.
5. Run tight experiments.
   - Change one variable at a time and measure with statistics.
   - Reject wins that do not survive noise and variance.
6. Ship with guards.
   - Add a benchmark, budget, or alert to prevent regressions.
   - Document the trade-offs and the measured delta.

## Hard Rules

- Measure before and after every optimization.
- Optimize the bottleneck, not the loudest hunch.
- Avoid micro-optimizations until algorithmic wins are exhausted.
- Keep correctness and safety invariants intact.
- Stop when ROI is negative or risk exceeds benefit.

## Decision Gates

- If the baseline is noisy or unstable, fix measurement first.
- If the complexity class dominates, change the algorithm first.
- If tail latency dominates, treat variance reduction as the primary goal.
- If I/O dominates, reduce bytes, syscalls, or round trips before CPU tuning.

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
