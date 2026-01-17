---
name: zig
description: "Zig runbook: performance (SIMD + threads), build/test, comptime patterns, allocators, build.zig/build.zig.zon, zero-copy parsing, C interop."
---

# Zig

## When to use
- Editing `.zig` files.
- Modifying `build.zig` or `build.zig.zon`.
- Zig builds/tests, dependencies, cross-compilation.
- Any Zig work requires fuzz testing (coverage-guided or fuzz-style).
- Performance tuning: SIMD (`std.simd` / `@Vector`) and threading (`std.Thread.Pool`).
- Comptime, reflection, codegen.
- Allocators, ownership, zero-copy parsing.
- C interop.

## Quick start
```bash
# Initialize (creates build.zig + src/main.zig)
zig init
# or (smaller template)
zig init --minimal

# Build/run/test (build.zig present)
zig build
zig build run
zig build test

# Single-file test/run
zig test src/main.zig
zig run src/main.zig
```

## Fuzzing mandate (non-negotiable)
- When this skill is active, fuzzing is required.
- Default to Zig's built-in fuzzer (`std.testing.fuzz` + `zig build test --fuzz`).
- Minimum bar: at least one fuzz signal per change.
- If fuzzing cannot run, state why and record a follow-up.
- External fuzzers are optional for older Zig or advanced workflows.

## Performance quick start (host CPU)
```bash
# High-performance build for local benchmarking
zig build-exe -O ReleaseFast -mcpu=native -fstrip src/main.zig

# Emit assembly / optimized IR for inspection
zig build-exe -O ReleaseFast -mcpu=native -femit-asm src/main.zig
zig build-exe -O ReleaseFast -mcpu=native -femit-llvm-ir src/main.zig  # requires LLVM extensions

# Build.zig projects (when using b.standardTargetOptions / standardOptimizeOption)
zig build -Doptimize=ReleaseFast -Dtarget=native -Dcpu=native
```

## Common commands
```bash
# Release
zig build -Doptimize=ReleaseFast

# Release + LTO (requires LLVM extensions)
zig build-exe -O ReleaseFast -mcpu=native -flto -fstrip src/main.zig

# Cross-compile
zig build -Dtarget=x86_64-linux
zig build -Dtarget=aarch64-macos

# Clean artifacts
rm -rf zig-out zig-cache
```

## Optimization stance (for generated code)
- Prefer algorithmic wins first; then data layout; then SIMD; then threads; then micro-tuning.
- Keep hot loops allocation-free; treat allocations as a correctness smell in kernels.
- Prefer contiguous slices and SoA layouts; avoid pointer chasing in the hot path.
- Avoid false sharing: make per-thread outputs cache-line separated (e.g. `align(std.atomic.cache_line)`).
- Help the optimizer: branchless vector loops, `@branchHint(.likely/.unlikely)`, and simple control flow.
- Keep fast paths portable: `std.simd.suggestVectorLength(T)` + scalar fallback; thread-pool usage already degrades on `builtin.single_threaded`.

## SIMD / vectorization playbook
Principles:
- Use explicit vectors when you need guaranteed SIMD (`@Vector`); rely on auto-vectorization only as a bonus.
- Derive lane count from `std.simd.suggestVectorLength(T)` so the same code scales across targets.
- Keep vector loops straight-line: no function pointers, no complex branching, no hidden allocations.
- Handle tails (remainder elements) with a scalar loop.
- Alignment matters on some targets (notably ARM); when tuning, consider a scalar prologue until aligned to the block size.

### SIMD template: reduce a slice
```zig
const std = @import("std");

pub fn sumF32(xs: []const f32) f32 {
    if (xs.len == 0) return 0;

    if (!@inComptime()) if (std.simd.suggestVectorLength(f32)) |lanes| {
        const V = @Vector(lanes, f32);

        var i: usize = 0;
        var acc: V = @splat(0);

        while (i + lanes <= xs.len) : (i += lanes) {
            const v: V = xs[i..][0..lanes].*;
            acc += v;
        }

        var total: f32 = @reduce(.Add, acc);
        while (i < xs.len) : (i += 1) total += xs[i];
        return total;
    }

    var total: f32 = 0;
    for (xs) |x| total += x;
    return total;
}
```

### SIMD scanning pattern (mask + reduce)
- Compare a vector against a scalar mask: `matches = block == @as(Block, @splat(value))`.
- Detect any matches: `if (@reduce(.Or, matches)) { ... }`.
- Find the first match index: `std.simd.firstTrue(matches).?`.

### Loop shaping tips (stdlib-proven)
- Unroll short inner loops with `inline for` to cut bounds checks (see `std.mem.indexOfScalarPos`).
- Use `std.simd.suggestVectorLength(T)` to match stdlib’s preferred alignment and vector width.
- Guard vector paths with `!@inComptime()` and `!std.debug.inValgrind()` when doing anything tricky.

## Threads / parallelism playbook
Principles:
- Only thread if you can amortize scheduling + cache effects (tiny slices usually lose).
- Partition work by contiguous ranges; avoid shared writes and shared locks in the hot path.
- Use a thread pool (`std.Thread.Pool`) + wait group (`std.Thread.WaitGroup`), not "spawn a thread per task".
- Make tasks coarse: ~`cpu_count` to ~`8*cpu_count` tasks, each doing a SIMD inner loop.
- Reduce results at the end; avoid atomics unless you truly need streaming aggregation.

### Thread pool template (data-parallel)
```zig
const std = @import("std");
const builtin = @import("builtin");

fn sumChunk(xs: []const f32, out: *f32) void {
    // Each task uses the SIMD kernel.
    out.* = sumF32(xs);
}

pub fn sumParallel(xs: []const f32) !f32 {
    if (xs.len == 0) return 0;

    // For throughput-oriented programs, prefer std.heap.smp_allocator in ReleaseFast.
    // smp_allocator is unavailable when compiled with -fsingle-threaded.
    const alloc = if (builtin.single_threaded) std.heap.page_allocator else std.heap.smp_allocator;

    var pool: std.Thread.Pool = undefined;
    try pool.init(.{ .allocator = alloc });
    defer pool.deinit();

    const cpu_count = @max(1, std.Thread.getCpuCount() catch 1);
    const task_count = @min(cpu_count * 4, xs.len);
    const chunk_len = (xs.len + task_count - 1) / task_count;

    var partials = try alloc.alloc(f32, task_count);
    defer alloc.free(partials);

    var wg: std.Thread.WaitGroup = .{};

    for (0..task_count) |t| {
        const start = t * chunk_len;
        const end = @min(xs.len, start + chunk_len);
        pool.spawnWg(&wg, sumChunk, .{ xs[start..end], &partials[t] });
    }

    // Let the calling thread help execute queued work.
    pool.waitAndWork(&wg);

    var total: f32 = 0;
    for (partials) |p| total += p;
    return total;
}
```

### Per-thread scratch (no allocator contention)
- Initialize the pool with `.track_ids = true`.
- Use `pool.spawnWgId(&wg, func, args)`; `func` receives `id: usize` first.
- Keep `scratch[id]` aligned to `std.atomic.cache_line` to prevent false sharing.

```zig
const std = @import("std");

const Scratch = struct {
    _: void align(std.atomic.cache_line) = {},
    tmp: [4096]u8 = undefined,
};

fn work(id: usize, input: []const u8, scratch: []Scratch) void {
    // Stable per-thread slot; no locks, no false sharing.
    const buf = scratch[id].tmp[0..];
    _ = buf;
    _ = input;
}

pub fn runParallel(input: []const u8, allocator: std.mem.Allocator) !void {
    var pool: std.Thread.Pool = undefined;
    try pool.init(.{ .allocator = allocator, .track_ids = true });
    defer pool.deinit();

    const scratch = try allocator.alloc(Scratch, pool.getIdCount());
    defer allocator.free(scratch);

    var wg: std.Thread.WaitGroup = .{};
    pool.spawnWgId(&wg, work, .{ input, scratch });
    pool.waitAndWork(&wg);
}
```

## Comptime essentials
- `comptime` parameters drive generics and specialization.
- `comptime { ... }` forces compile-time evaluation.
- `inline for` / `inline while` unroll at compile time.
- `@typeInfo` enables reflection; `@compileError` enforces invariants.
- If compile-time loops blow up, consider `@setEvalBranchQuota` (surgical use only).

### Comptime example
```zig
const std = @import("std");

fn max(comptime T: type, a: T, b: T) T {
    return if (a > b) a else b;
}

test "comptime parameter" {
    const x = max(u32, 3, 5);
    try std.testing.expect(x == 5);
}
```

## Comptime for performance
Patterns:
- Specialize on lane count and unroll factors (`comptime lanes`, `comptime unroll`).
- Generate lookup tables at comptime (e.g., classification maps, shuffle indices).
- Prefer `comptime if` for CPU/arch dispatch (`builtin.cpu.arch`) when you need different kernels.

### Comptime specialization example (SIMD dot product)
```zig
const std = @import("std");

fn Dot(comptime lanes: usize) type {
    return struct {
        pub fn dot(a: []const f32, b: []const f32) f32 {
            const V = @Vector(lanes, f32);

            var i: usize = 0;
            var acc: V = @splat(0);

            while (i + lanes <= a.len) : (i += lanes) {
                const av: V = a[i..][0..lanes].*;
                const bv: V = b[i..][0..lanes].*;
                acc += av * bv;
            }

            var total: f32 = @reduce(.Add, acc);
            while (i < a.len) : (i += 1) total += a[i] * b[i];
            return total;
        }
    };
}

pub fn dotAuto(a: []const f32, b: []const f32) f32 {
    const lanes = std.simd.suggestVectorLength(f32) orelse 1;
    return Dot(lanes).dot(a, b);
}
```

## Build essentials (`build.zig`)
```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "my-app",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    b.installArtifact(exe);

    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());

    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);

    if (b.args) |args| run_cmd.addArgs(args);
}
```

## Package management (`build.zig.zon`)
```zig
.{
    .name = "my-project",
    .version = "0.1.0",
    .dependencies = .{
        .@"some-package" = .{
            .url = "https://github.com/user/package/archive/main.tar.gz",
            .hash = "1220abcdef...",
        },
    },
    .paths = .{ "build.zig", "build.zig.zon", "src" },
}
```

## Memory / allocators (performance-first)
Rules of thumb:
- Debugging correctness/leaks: `std.testing.allocator` in tests, or `std.heap.DebugAllocator` in apps.
- Throughput + multithreading (ReleaseFast): `std.heap.smp_allocator` (singleton, designed for MT + ReleaseFast).
- Short-lived "build a result then throw away": `std.heap.ArenaAllocator` on top of a fast backing allocator.
- Scratch buffers: `std.heap.FixedBufferAllocator` or `std.heap.stackFallback(N, fallback)`.
- Fixed-size objects: `std.heap.MemoryPool` / `std.heap.MemoryPoolAligned`.

### Debug allocator (leak checking)
```zig
const std = @import("std");

pub fn main() !void {
    var dbg = std.heap.DebugAllocator(.{}){};
    defer _ = dbg.deinit();
    const allocator = dbg.allocator();

    const bytes = try allocator.alloc(u8, 100);
    defer allocator.free(bytes);
}
```

### Smp allocator + arena reset (hot loop friendly)
```zig
const std = @import("std");
const builtin = @import("builtin");

pub fn buildManyThings() !void {
    const backing = if (builtin.single_threaded) std.heap.page_allocator else std.heap.smp_allocator;

    var arena = std.heap.ArenaAllocator.init(backing);
    defer arena.deinit();
    const a = arena.allocator();

    var i: usize = 0;
    while (i < 1000) : (i += 1) {
        _ = arena.reset(.retain_capacity);
        _ = try a.alloc(u8, 4096);
    }
}
```

## Inspecting codegen / benchmarking
- Emit assembly: `zig build-exe -O ReleaseFast -mcpu=native -femit-asm src/main.zig`
- Emit optimized LLVM IR: `zig build-exe -O ReleaseFast -mcpu=native -femit-llvm-ir src/main.zig` (LLVM extensions)
- Track compile time: `--time-report`
- Prevent DCE in benches: `std.mem.doNotOptimizeAway(x)`
- Time loops: `std.time.Timer`, `std.time.nanoTimestamp`

## Zero-copy parsing playbook
Principles:
- Treat input as immutable bytes; parse into views, not copies.
- Make ownership explicit (borrowed vs owned).
- Store spans/offsets into a stable base buffer.
- Never return slices into temporary buffers.

### Borrowed/owned token (copy-on-write escape hatch)
```zig
const std = @import("std");

pub const ByteView = union(enum) {
    borrowed: []const u8,
    owned: []u8,

    pub fn slice(self: ByteView) []const u8 {
        return switch (self) {
            .borrowed => |s| s,
            .owned => |s| s,
        };
    }

    pub fn toOwned(self: ByteView, allocator: std.mem.Allocator) ![]u8 {
        return switch (self) {
            .owned => |s| s,
            .borrowed => |s| try allocator.dupe(u8, s),
        };
    }

    pub fn deinit(self: *ByteView, allocator: std.mem.Allocator) void {
        if (self.* == .owned) allocator.free(self.owned);
        self.* = .{ .borrowed = &.{} };
    }
};
```

### POSIX mmap (stable base buffer)
```zig
const std = @import("std");

pub const MappedFile = struct {
    data: []const u8,
    owns: bool,

    pub fn open(path: []const u8) !MappedFile {
        const file = try std.fs.cwd().openFile(path, .{});
        defer file.close();
        const size = (try file.stat()).size;
        const map = try std.posix.mmap(
            null,
            size,
            std.posix.PROT.READ,
            .{ .TYPE = .PRIVATE },
            file.handle,
            0,
        );
        return .{ .data = map, .owns = true };
    }

    pub fn close(self: *MappedFile) void {
        if (self.owns) std.posix.munmap(self.data);
        self.* = .{ .data = &.{}, .owns = false };
    }
};
```

### Span-based parsing (offsets, not copies)
```zig
const Span = struct {
    base: []const u8,
    start: usize,
    len: usize,

    pub fn slice(self: Span) []const u8 {
        return self.base[self.start..][0..self.len];
    }
};
```

## Testing
- Run correctness tests in Debug or ReleaseSafe; run perf checks in ReleaseFast.
- Leak detection: use `std.testing.allocator` and `defer` frees.
- Allocation counting: wrap an allocator and assert zero allocations for a “zero-copy” path.
- OOM injection: run under `std.testing.FailingAllocator`.
- Exhaustive OOM: `std.testing.checkAllAllocationFailures`.

## Fuzz testing (required)
### Built-in fuzzer (default, Zig 0.14+)
Use `std.testing.fuzz` in a `test` block and run the build runner with
`zig build test --fuzz`. The build runner rebuilds tests with `-ffuzz` and
starts the integrated fuzzer; it also serves a small web UI with live coverage.
The fuzzer is alpha quality in Zig 0.14.0, but it is the default path.

Suggested template (optional):
```zig
const std = @import("std");

fn fuzzTarget(ctx: []const u8, input: []const u8) !void {
    if (std.mem.eql(u8, ctx, input)) return error.Match;
}

test "fuzz target" {
    try std.testing.fuzz(@as([]const u8, "needle"), fuzzTarget, .{});
}
```

### Allocation-failure fuzzing (mandatory for allocators)
`std.testing.checkAllAllocationFailures` exhaustively injects `error.OutOfMemory` across
all allocations in a test function. The test function must take an allocator as its first
argument, return `!void`, and reset shared state each run.

```zig
const std = @import("std");

fn parseWithAlloc(alloc: std.mem.Allocator, bytes: []const u8) !void {
    _ = alloc;
    _ = bytes;
}

test "allocation failure fuzz" {
    const input = "seed";
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        parseWithAlloc,
        .{input},
    );
}
```

### Allocator pressure tricks (recommended)
- Cap per-allocation size relative to input length to surface pathological allocations.
- Wrap with `std.testing.FailingAllocator` to validate `errdefer` and cleanup paths.
- Use deterministic seeds and store crashing inputs under `testdata/fuzz/`.

### Fast in-tree randomized fuzz (fallback when `--fuzz` is unavailable)
Use randomized inputs inside `test` blocks for quick coverage on every change.

```zig
const std = @import("std");

fn parse(bytes: []const u8) !void {
    _ = bytes;
}

test "fuzz parse" {
    var prng = std.rand.DefaultPrng.init(0x9e3779b97f4a7c15);
    const rng = prng.random();

    var i: usize = 0;
    while (i < 10_000) : (i += 1) {
        const len = rng.intRangeAtMost(usize, 0, 4096);
        var buf = try std.testing.allocator.alloc(u8, len);
        defer std.testing.allocator.free(buf);
        rng.bytes(buf);
        _ = parse(buf) catch {};
    }
}
```

### External harnesses (optional)
If your Zig version lacks the built-in fuzzer or you need AFL++/libFuzzer features,
export a C ABI entrypoint and drive it from an external fuzzer. Example outline:
- Export a stable entrypoint: `export fn fuzz_target(ptr: [*]const u8, len: usize) void`.
- Build a static library with `zig build-lib`.
- Link it from an external harness (AFL++ via `cargo-afl`) and run with a seed corpus.

## C interop
```zig
const c = @cImport({
    @cInclude("stdio.h");
});

pub fn main() void {
    _ = c.printf("Hello from C!\n");
}
```

## Pitfalls
- Multithreading: false sharing, oversubscription, shared allocator contention.
- SIMD: misaligned loads on some targets, reading past the end, non-associative FP reductions.
- `std.heap.GeneralPurposeAllocator` is deprecated (alias of `DebugAllocator`); keep for existing code, prefer explicit allocator choices for new code.
- Make ownership explicit; always free heap allocations.
- Avoid returning slices backed by stack memory.
- `[*c]T` is nullable; `[*]T` is non-null.
- Use `zig fetch --save` to populate `build.zig.zon` hashes.

## Activation cues
- "zig" / "ziglang" / ".zig"
- "build.zig" / "build.zig.zon"
- "zig build" / "zig test"
- "comptime" / "allocator" / "@typeInfo" / "@compileError"
- "SIMD" / "@Vector" / "std.simd"
- "thread" / "std.Thread" / "Thread.Pool" / "WaitGroup"
