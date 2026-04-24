# Measurement and Benchmarking

## Required Baseline Fields

Capture all of the following before changing code:

- command and arguments
- dataset and input size/shape/skew
- git commit or build identifier
- hardware, OS, kernel, runtime, compiler flags
- concurrency/load level and warmup policy
- sample count and raw sample location when possible
- primary metric and secondary metrics
- correctness command and result

## Metrics

- Latency: p50, p90, p95, p99, max, and sample count.
- Throughput: QPS/items/sec/MB/sec plus CPU and memory.
- Batch duration: wall time, CPU time, peak RSS, I/O bytes.
- Memory: peak RSS, allocation rate, live heap, GC pause, object churn.
- Tail: p99/max, queue depth, saturation, retries, timeout/cancel counts.
- Startup: cold and warm separately.

## Default Commands

```bash
# Wall-clock distribution
hyperfine --warmup 3 --runs 10 'command'
hyperfine --warmup 3 --runs 30 --export-json baseline.json 'command'

# Memory and CPU summary
/usr/bin/time -v command 2>&1 | tee time.txt

# Linux counters
perf stat -d -- command 2>&1 | tee perf-stat.txt

# Store raw samples for CLI stats
hyperfine --warmup 3 --runs 30 --export-csv samples.csv 'command'
```

When Lift CLIs are available:

```bash
bench_stats --input samples.txt --unit ms
perf_report --title "Perf pass" --owner "team" --system "service" --output perf-report.md
```

## Noise Control

- Warm caches, JITs, allocators, and connection pools before measurement.
- Keep CPU governor, thermal state, and background load stable when possible.
- Use the same machine, build mode, dataset, and dependency versions.
- Randomize run order when comparing variants that can influence cache state.
- Treat p99 from tiny samples as unstable; increase sample count or label
  inconclusive.
- Prefer medians and percentiles over means for skewed distributions.
- Report a noise floor; reject changes smaller than noise.

## Microbenchmark Pitfalls

- Avoid measuring code that the compiler can eliminate.
- Do not benchmark tiny code blocks without looped harness overhead control.
- Avoid unrealistic input sizes and distributions.
- Separate setup cost from measured operation unless setup is part of the workload.
- Do not extrapolate microbenchmarks to system latency without macrobench proof.

## Statistical Sanity

For each accepted result, record:

- sample count and warmup count
- baseline and variant distribution
- absolute and percent delta
- variance/noise floor
- whether confidence is high, medium, low, or inconclusive

If confidence intervals overlap or variance is high, report the result as
inconclusive and rerun with more samples or a cleaner harness.

## Reporting Template

```text
baseline: n=<samples>, p50=<>, p95=<>, p99=<>, max=<>
variant:  n=<samples>, p50=<>, p95=<>, p99=<>, max=<>
delta:    p95 <absolute>, <percent>; secondary regressions: <yes/no>
noise:    <estimated>; confidence: <high|medium|low|inconclusive>
```
