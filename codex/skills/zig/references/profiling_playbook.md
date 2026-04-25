# Zig Profiling Playbook

Use this when the task is about speed, latency, throughput, allocator churn, memory growth, leaks, lock contention, or unexplained regressions.

## Decision tree

- Need to prove a user-visible performance delta: run or add a benchmark/perf harness first.
- Need to explain allocations, frees, live bytes, or leaks: use `zprof`.
- Need to localize CPU time, cache behavior, branchy code, or lock contention: use a system CPU sampler.
- Need long-running timeline telemetry, frame views, locks, context switches, or causality across tasks: consider Tracy after simpler lanes justify instrumentation.

## Benchmark protocol

Keep constant across baseline and variant:

- dataset,
- optimize mode,
- target and CPU flags,
- allocator,
- warmup count,
- sample count,
- process isolation,
- checksum/output validation.

Small deltas need repeated fresh-process runs. Report effect size or interval when noise can exceed the observed delta.

## `zprof` lane

Current researched default for Zig 0.16.0-era allocator profiling: `zprof` v4.0.0.

Install:

```bash
zig fetch --save https://github.com/ANDRVV/zprof/archive/v4.0.0.zip
```

Build wiring:

```zig
const zprof_dep = b.dependency("zprof", .{
    .target = target,
    .optimize = optimize,
});
exe.root_module.addImport("zprof", zprof_dep.module("zprof"));
```

Metrics exposed by upstream v4 docs include:

- `allocated`
- `freed`
- `alloc_count`
- `free_count`
- `live_requested`
- `peak_requested`
- `hasLeaks()`
- `reset()`

Minimal test harness:

```zig
const std = @import("std");
const Zprof = @import("zprof").Zprof;

fn runWorkload(allocator: std.mem.Allocator) !void {
    const data = try allocator.alloc(u8, 1024);
    defer allocator.free(data);
}

test "profile allocator pressure" {
    var prof: Zprof(.{}) = .init(std.testing.allocator, undefined);
    try runWorkload(prof.allocator());

    try std.testing.expect(!prof.profiler.hasLeaks());
    try std.testing.expectEqual(@as(usize, 0), prof.profiler.live_requested.get());
}
```

Operating rules:

- Wrap the allocator boundary closest to the suspected waste.
- Do not use allocator counters as a substitute for wall-clock proof.
- Enable `.thread_safe = true` only when multiple threads share the wrapped allocator.
- Reset between phases when one process captures more than one workload.
- Disable unneeded counters when chasing a narrow question.

## CPU sampling lane

Linux:

```bash
zig build -Doptimize=ReleaseFast -Dtarget=native -Dcpu=native
perf record --call-graph dwarf -- ./zig-out/bin/app
perf report
```

macOS: use Instruments Time Profiler on the optimized binary.

If call stacks are unusable, revisit debug info, frame-pointer, strip, and linker choices before changing source code. Avoid the new ELF linker for DWARF-dependent profiling until the release-note limitation is no longer relevant to the target toolchain.

## Tracy lane

Use Tracy when timeline causality matters: pipelines, frame loops, lock contention, cross-thread context switches, or long-running concurrent systems. Prefer existing repo support. Do not add a heavy telemetry integration for a one-shot allocator question.

## Decomposition rule

When one aggregate benchmark regresses across abstraction layers, add lanes in the same harness:

1. substrate/reference only,
2. wrapper/shell only,
3. full path,
4. optional scalar/reference path.

Keep the same dataset, checksum, warmups, samples, allocator, optimize mode, and target. Optimize from the decomposed result.
