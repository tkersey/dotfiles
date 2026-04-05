# Zig Profiling Playbook

Use this reference when the request is about profiling, memory growth, leaks, allocator churn, or unexplained performance regressions.

## Decision tree
- Need proof that a change helped or hurt end-to-end latency or throughput: run the repo benchmark or perf harness first.
- Need to know whether allocations, frees, live bytes, or leaks explain the regression: use `zprof`.
- Need to know where CPU time goes after allocator counters look normal: use a CPU sampler.
- Need long-running, concurrent, or frame-style telemetry with timelines, locks, and context switches: consider Tracy only after smaller lanes justify it.

## `zprof` default
Why it is the default allocator profiler:
- Zero-dependency Zig allocator wrapper.
- Upstream exposes `allocated`, `alloc_count`, `free_count`, `live_peak`, and `live_bytes`.
- Upstream also exposes `hasLeaks()` and `reset()`.
- Upstream `build.zig.zon` declares `minimum_zig_version = "0.15.1"`, so it fits the `$zig` default `0.15.2` toolchain.

Current researched install example:

```bash
gh api repos/ANDRVV/zprof/releases/latest --jq '{tag_name,published_at,html_url}'
zig fetch --save https://github.com/ANDRVV/zprof/archive/v3.0.1.zip
```

`build.zig`:

```zig
const zprof_dep = b.dependency("zprof", .{
    .target = target,
    .optimize = optimize,
});
exe.root_module.addImport("zprof", zprof_dep.module("zprof"));
```

Minimal instrumentation:

```zig
const std = @import("std");
const Zprof = @import("zprof").Zprof;

fn runWorkload(allocator: std.mem.Allocator) !void {
    const buf = try allocator.alloc(u8, 1024);
    defer allocator.free(buf);
}

test "profile allocator pressure" {
    var prof: Zprof(.{}) = .init(std.testing.allocator, undefined);
    const allocator = prof.allocator();

    try runWorkload(allocator);

    try std.testing.expectEqual(@as(usize, 0), prof.profiler.live_bytes.get());
    try std.testing.expectEqual(@as(bool, false), prof.profiler.hasLeaks());
}
```

## Experiment protocol
- Wrap one allocator boundary at a time.
- Keep child allocator, input dataset, optimize mode, and work count fixed.
- Capture baseline counters before changing code.
- Re-run the same workload after the change.
- Compare counters and wall-clock measurements together.
- If counters improved but time did not, stop guessing and switch to CPU sampling.

## CPU sampling lane
- Linux: prefer `perf record --call-graph dwarf` followed by `perf report`.
- macOS: prefer Instruments Time Profiler.
- Use optimized binaries for hotspot localization, but keep a correctness lane in `Debug` or `ReleaseSafe`.

## Tracy lane
- Use when you need timeline-style telemetry, frame views, locks, context switches, or long-running concurrent diagnosis.
- Prefer it when the repo already has Tracy support or the user explicitly wants that integration.
- Do not make Tracy the first move for small one-shot allocator questions.
