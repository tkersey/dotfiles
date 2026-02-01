# Lift Playbook

## Table of contents

1. Doctrine
2. Performance contract
3. Optimization ladder
4. Measurement loop
5. Bottleneck classification
6. Experiment design
7. Shipping and guarding
8. Stop conditions

## 1. Doctrine

- Treat performance as a product requirement, not a code style.
- Preserve correctness and safety invariants before speed.
- Measure reality, not intuition.
- Optimize the current bottleneck, not the loudest hunch.
- Prefer fewer, larger wins over many small tweaks.
- Keep changes reversible and well scoped.

## 2. Performance contract

Define a concrete target before changing code.

- Metric: latency, throughput, memory, GC pause, startup time, or tail percentile.
- Target: absolute value and percentile (p50, p95, p99) with acceptable variance.
- Dataset: production-like size, shape, and skew.
- Environment: hardware, OS, runtime, flags, and load profile.
- Constraints: accuracy, determinism, power, latency budget, cost budget.

## 3. Optimization ladder

Move down the ladder only after higher tiers are exhausted.

1. Delete work.
   - Skip unnecessary computation, I/O, or allocation.
2. Change the algorithm.
   - Reduce complexity class or shrink the input.
3. Change data structures and layout.
   - Improve locality, cache usage, and access patterns.
4. Improve concurrency.
   - Parallelize, pipeline, and reduce contention.
5. Reduce I/O and serialization cost.
   - Minimize bytes, syscalls, and round trips.
6. Tune micro-architecture.
   - Branch prediction, SIMD, alignment, prefetch.
7. Tune compiler or runtime.
   - Flags, JIT warmup, GC tuning, inlining.

## 4. Measurement loop

- Baseline: measure steady-state with a clean harness.
- Profile: identify hot paths and contention.
- Hypothesize: pick one change with a clear causal model.
- Experiment: change one variable, run multiple samples.
- Validate: confirm effect size and statistical stability.
- Guard: add benchmarks or budgets to prevent regressions.

## 5. Bottleneck classification

Use evidence to classify the bound and pick the correct playbook.

- CPU-bound: high utilization, hot loops, low I/O wait.
- Memory-bound: cache misses, bandwidth saturation, stalls.
- I/O-bound: high wait on disk, network, or syscalls.
- Lock-bound: time in mutexes, high contention, convoying.
- Tail-bound: high variance, spikes, head-of-line blocking.

## 6. Experiment design

- Change one variable at a time.
- Control for warmup, caching, and background noise.
- Run enough samples to separate signal from noise.
- Prefer reversible changes and feature flags.

## 7. Shipping and guarding

- Add a microbenchmark or macrobenchmark that represents real load.
- Add a performance budget or alert to detect regressions.
- Record the before/after numbers and environment.

## 8. Stop conditions

- Stop when ROI is negative or risk exceeds benefit.
- Stop when the remaining bottleneck is outside your control.
- Stop when correctness or maintainability would be compromised.
