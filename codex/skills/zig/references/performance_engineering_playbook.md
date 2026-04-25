# Zig performance, profiling, cache-layout, and measurement playbook

Use this playbook when users ask for speedups, latency, throughput, allocation pressure, binary size, CPU hotspots, memory growth, cache behavior, SIMD/vectorization, or profiling.

## Expert objective

Do not guess about performance. Produce a measurement contract:

1. workload and dataset;
2. baseline command/result;
3. optimization hypothesis;
4. benchmark command/result;
5. profiler evidence if needed;
6. correctness guard/checksum;
7. optimize mode, target, CPU, allocator, and build flags;
8. remaining noise/confounders.

## Benchmark before optimizing

Minimum benchmark shape:

- warmup;
- repeated samples;
- fixed dataset;
- checksum or invariant check;
- fixed allocator;
- ReleaseFast or relevant production optimize mode;
- baseline and variant run under the same environment.

Report `UNMEASURED` rather than implying a speedup without numbers.

## Decompose regressions

When a regression spans abstraction layers, build lanes such as:

1. substrate only;
2. wrapper only;
3. full path;
4. reference/scalar path;
5. optimized path.

Use the same dataset and checksum across lanes. Optimize the lane that actually regressed.

## Allocation pressure

Hot-path allocation is often the first systems-performance issue in Zig.

Measure:

- allocation count;
- allocated/freed bytes;
- live requested bytes;
- peak requested bytes;
- leaks;
- allocator contention when shared across threads.

Use `zprof` for allocator metrics and system profilers for CPU/time. Do not confuse allocation metrics with wall-clock proof.

## CPU profiling

Use system profilers when wall time regresses and allocation is not the explanation:

```bash
perf record --call-graph dwarf -- ./zig-out/bin/app
perf report
```

On macOS, use Instruments Time Profiler. For long-running concurrent/timeline questions, consider Tracy only when the repo already supports it or instrumentation cost is justified.

## Cache and layout

Review:

- array-of-structs vs struct-of-arrays;
- hot/cold field splitting;
- pointer chasing and allocation locality;
- branch-heavy code paths;
- bounds checks and slice shapes;
- false sharing between threads;
- packed layout costs vs space savings;
- endian/unaligned loads in parsers.

Only claim cache or branch improvements when benchmark/profiler data supports them.

## SIMD/vector guidance

Use vectors/SIMD only when:

- the scalar reference path exists;
- tests compare scalar and vector outputs;
- target CPU features are explicit or guarded;
- ReleaseFast benchmark proves benefit;
- alignment and tail handling are correct.

For debug iteration over vector elements in Zig 0.16, coerce to an array when runtime indexing is needed.

## Binary size

For size claims:

```bash
zig build -Doptimize=ReleaseSmall
ls -lh zig-out/bin/*
```

Also examine specialization cardinality from comptime generics. Excessive value-specialization can improve hot paths while harming build time and binary size.

## Linker/debug-info caveat

Profiling workflows that need DWARF call graphs require binaries with suitable debug info. Do not enable linker/incremental settings that drop debug information when the profiler depends on it.

## Review checklist

- Baseline and variant are measured under the same conditions.
- Correctness guard prevents benchmarking wrong output.
- Optimization mode matches the claim.
- Allocation and CPU questions use the right profiler.
- Cache/SIMD claims have evidence.
- Build time and binary size are considered for comptime specialization.
- Results include exact commands and remaining noise.
