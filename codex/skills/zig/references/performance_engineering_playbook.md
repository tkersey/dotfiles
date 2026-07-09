# Zig performance, profiling, cache-layout, and measurement playbook

Use this playbook when users ask for speedups, latency, throughput, allocation pressure, binary size, CPU hotspots, memory growth, cache behavior, SIMD/vectorization, LTO, or profiling.

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

## LTO measurement lane

Link-time optimization is a candidate release optimization, not proof by itself.

Add an LTO lane when the hypothesis is cross-module inlining, dead-code removal, devirtualization-like specialization through visible calls, or binary-size reduction. Do not add it for semantic correctness, debug-only work, or failure triage unless the repository already ships with LTO.

Compare explicit variants:

```bash
# repository-specific commands are preferred when available
zig build -Doptimize=ReleaseFast
zig build -Doptimize=ReleaseFast -Dlto=thin
zig build -Doptimize=ReleaseFast -Dlto=full
zig build -Doptimize=ReleaseSmall -Dlto=thin

# direct compiler probes are acceptable for isolated artifacts
zig build-exe src/main.zig -O ReleaseFast -fno-lto
zig build-exe src/main.zig -O ReleaseFast -flto=thin
zig build-exe src/main.zig -O ReleaseFast -flto=full
```

Only use `-Dlto=...` when the repository exposes that build option. Otherwise, inspect `build.zig` and either use the repo’s existing knob or propose a small enum option in the build-toolchain playbook.

For each LTO result, record:

```text
lto mode: none|thin|full
Zig version, target triple, CPU, optimize mode
use_lld/use_new_linker/use_llvm when known
binary size and stripped/debug-info state
build/link time and memory pressure when relevant
benchmark metric and variance
correctness guard/checksum
```

Prefer `.thin` for large projects or CI lanes where link time and memory are constraints. Test `.full` only when the link is tractable or the artifact justifies the cost. If LTO changes profiler symbolization, call graph quality, sanitizer behavior, or debug-info availability, separate the profiling lane from the shipping-performance lane.

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

Also compare `ReleaseSmall` with explicit LTO variants when the repository supports them, because LTO can change dead-code elimination and cross-module specialization.

Examine specialization cardinality from comptime generics. Excessive value-specialization can improve hot paths while harming build time and binary size.

## Linker/debug-info caveat

Profiling workflows that need DWARF call graphs require binaries with suitable debug info. Do not enable linker/incremental/LTO settings that drop or destabilize debug information when the profiler depends on it.

## Review checklist

- Baseline and variant are measured under the same conditions.
- Correctness guard prevents benchmarking wrong output.
- Optimization mode matches the claim.
- LTO is off/thin/full intentionally and recorded when relevant.
- Allocation and CPU questions use the right profiler.
- Cache/SIMD claims have evidence.
- Build time and binary size are considered for comptime specialization and LTO.
- Results include exact commands and remaining noise.