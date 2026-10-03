# Zig profiling tools

Use for runtime latency, throughput, allocation churn, leaks, contention or an
unexplained regression. Choose evidence for the question rather than traversing
a fixed tool sequence. [Performance engineering](performance_engineering_playbook.md)
owns benchmark interpretation and the distinction between cold compilation,
configuration-cache hits, persistent incremental rebuilds and program runtime.

## Select a measurement

| Question | Candidate |
| --- | --- |
| User-visible latency/throughput or size delta | A representative benchmark or artifact comparison with a correctness guard. |
| Allocation count, live bytes, leak or waste | Repository-compatible allocator instrumentation such as zprof. |
| CPU time, branches, cache or lock contention | A supported system profiler and appropriate counters. |
| Cross-task timing/causality | Existing timeline telemetry, or justified instrumentation such as Tracy. |

Keep baseline/variant workload, mode, target/CPU, allocator, warmup and sampling
conditions comparable. Small differences need enough samples and process isolation
to distinguish signal from noise. Record relevant variance/confounders; profiling
overhead can change the behavior being measured.

## Allocator instrumentation

Use the project's pinned [zprof](https://github.com/ANDRVV/zprof) or an existing
allocator wrapper. Inspect compatibility with the selected compiler and its actual
module/options/accessors. The older v4.0.0 recipe was researched for 0.16-era code;
it is not a verified 0.17 default and should not drive an automatic installation.

Measure the quantities needed: allocation/free counts, allocated/freed bytes,
live and peak requested bytes, leaks and contention. Do not mistake requested
bytes for process RSS or allocator counters for wall-clock evidence. Instrument
the allocator boundary closest to the suspected waste, keeping allocator lifetime
and ownership unchanged. Use the wrapper's synchronization when it is shared
across threads; that does not synchronize arbitrary user data. Reset between
phases only after respecting live-allocation semantics of the actual tool.
Disable irrelevant counters when overhead obscures the question.

## CPU sampling

Build through the repository's real release/profiling configuration. For Zig 0.17
use supported lower-case mode names such as `fast` or `safe`; do not assume the
project exposes custom CPU/LTO options. Keep sufficient debug information for the
sampling method. A Linux sampling command, when supported, is:

```bash
perf record --call-graph dwarf -- ./zig-out/bin/app
perf report
```

On macOS, Instruments Time Profiler is an alternative for the actual optimized
binary. When stacks are unusable, investigate debug info, stripping, frame-pointer,
backend and linker choices before attributing the issue to application code.
Check the selected toolchain's current target support rather than carrying a
blanket ban on a new linker from an older release. Keep the shipping and profiling
configurations distinct when their needs conflict.

## Timeline and decomposition

Use Tracy or comparable telemetry when pipelines, frames, locks or cross-thread
causality are the real question. Prefer existing repository support. A one-off
allocation question rarely justifies a new heavy telemetry integration.

When an aggregate regression spans layers, split substrate, wrapper and full-path
measurements where that isolates the cause. Keep comparable input and independent
correctness checks. A reference/scalar lane can separate algorithmic from wrapper
cost, but do not add empty lanes or infer that every regression needs this exact
decomposition. Optimize from observed mechanisms and recheck the affected contract.
