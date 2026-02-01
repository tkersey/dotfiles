# Measurement and Benchmarking

## Table of contents

1. Metrics and distributions
2. Benchmark types
3. Noise control
4. Sampling vs tracing
5. Statistical sanity
6. Microbenchmark pitfalls
7. Reporting results

## 1. Metrics and distributions

- Track latency distributions, not just averages.
- Report p50, p90, p95, p99, and max for latency.
- Track throughput, CPU, memory, and GC pause time in parallel.
- Measure steady state and cold start separately.

## 2. Benchmark types

- Microbench: isolate a hot function; use for tight loops and data layout.
- Macrobench: full workflow; use for user-visible latency and throughput.
- Soak: long-running tests to catch leaks and JIT or GC drift.

## 3. Noise control

- Pin CPU frequency or use performance mode when possible.
- Minimize background load and jitter.
- Warm up caches, JITs, and allocators before measuring.
- Use consistent datasets and randomized order where needed.

## 4. Sampling vs tracing

- Use sampling profilers for low overhead and broad hotspots.
- Use tracing when you need call order, wait reasons, or latency sources.
- Validate profiler overhead with a baseline run.

## 5. Statistical sanity

- Run enough samples to separate signal from noise.
- Prefer medians and percentiles over means for skewed distributions.
- Report variance or confidence interval when variance is high.
- Reject wins smaller than the noise floor.

## 6. Microbenchmark pitfalls

- Avoid timing too-small code blocks; loop inside the benchmark.
- Avoid dead-code elimination; ensure results are used.
- Avoid measuring allocation and I/O unless intended.
- Avoid cross-run cache contamination; control for warm and cold.

## 7. Reporting results

- Record environment, dataset, and run conditions.
- Record baseline and variant side by side.
- Provide deltas in absolute and percentage terms.
- Note any trade-offs or regressions.
