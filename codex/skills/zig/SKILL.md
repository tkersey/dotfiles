---
name: zig
description: Zig development runbook; use when working with zig/ziglang, .zig files, build.zig/build.zig.zon, zig build/zig test, comptime, allocators, @typeInfo/@compileError, or Zig builds, packages, C interop, or tests.
---

# Zig

## When to use
- Editing or reviewing `.zig` source files
- Modifying `build.zig` or `build.zig.zon`
- Configuring the build system, dependencies, or cross-compilation
- Working with comptime, generics, reflection, or compile-time codegen
- Working with allocators, memory ownership, or C interop
- Writing or debugging Zig tests

## Quick start
```bash
# Initialize a project
zig init-exe
zig init-lib

# Build, run, test
zig build
zig build run
zig build test
zig test src/main.zig

# Add a dependency (writes build.zig.zon)
zig fetch --save https://github.com/user/package/archive/main.tar.gz
```

## Common commands
```bash
# Release build
zig build -Doptimize=ReleaseFast

# Cross-compile
zig build -Dtarget=x86_64-linux
zig build -Dtarget=aarch64-macos

# Clean build artifacts (safe)
rm -rf zig-out zig-cache
```

## Comptime quick start
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

## Comptime toolbox
- `comptime` parameters drive generics and compile-time duck typing.
- `comptime` variables guarantee loads/stores happen at compile time.
- `comptime { ... }` blocks force evaluation and validation at compile time.
- `inline for` / `inline while` unroll and evaluate loops at compile time.
- `@Type` + `@typeInfo` let you build or transform types programmatically.
- `@compileError` and `@compileLog` are for compile-time assertions/debugging.
- `@setEvalBranchQuota` raises the compile-time loop branch limit when needed.

## Comptime patterns
```zig
const std = @import("std");

fn BiggerInt(comptime T: type) type {
    return @Type(.{
        .Int = .{
            .bits = @typeInfo(T).Int.bits + 1,
            .signedness = @typeInfo(T).Int.signedness,
        },
    });
}

fn requireNonZero(comptime n: usize) void {
    if (n == 0) @compileError("n must be > 0");
}

test "comptime type + validation" {
    requireNonZero(4);
    try std.testing.expect(BiggerInt(u8) == u9);
}
```

## Comptime optimization: specialize, then fall back
- **Comptime format strings:** keep format strings known at compile time to remove runtime parsing and catch mismatches early.
- **Static dispatch for small domains:** generate fast paths with `inline` switch for bounded runtime values; fall back to a generic runtime path to control code size.
- **Schema/type constructors:** build types from comptime config to bake structure into code (e.g., table/index layouts).
- **Comptime-known string keys:** compare or route using compile-time strings to reduce branching and enable unrolled checks.
- **Compiler cooperation:** give the compiler concrete constants and predictable control flow, then verify results with measurement.

```zig
const std = @import("std");

comptime {
    _ = std.fmt.comptimePrint("v={d}", .{123});
}

fn staticEql(comptime a: []const u8, b: []const u8) bool {
    if (a.len != b.len) return false;
    for (0..a.len) |i| {
        if (a[i] != b[i]) return false;
    }
    return true;
}

fn dispatch(runtime_val: u32) void {
    switch (runtime_val) {
        inline 0...64 => |v| staticPath(v),
        else => runtimePath(runtime_val),
    }
}

fn staticPath(comptime v: u32) void {
    _ = v; // specialized code per v
}

fn runtimePath(v: u32) void {
    _ = v; // generic fallback
}
```

### Comptime formatting checklist (do/don't)
- **Do:** keep format strings `comptime` and map runtime keys to known formats.
- **Do:** implement `format` on custom types; `fmt` is comptime-checked.
- **Don't:** build dynamic format strings in hot paths; route keys to predeclared formats instead.

```zig
const LogFmt = enum { short, long, fallback };

fn parseLogFmt(key: []const u8) LogFmt {
    const map = std.StaticStringMap(LogFmt).initComptime(.{
        .{ "short", .short },
        .{ "long", .long },
    });
    return map.get(key) orelse .fallback;
}

fn logByKey(writer: anytype, key: []const u8, value: i64) !void {
    return switch (parseLogFmt(key)) {
        .short => writer.print("v={d}\n", .{value}),
        .long => writer.print("value={d}ms\n", .{value}),
        .fallback => writer.print("{d}\n", .{value}),
    };
}
```

### ORM-style type constructor (schema at comptime)
```zig
pub fn DBType(comptime schema: anytype) type {
    return struct {
        pub const tables = schema.tables;
        pub const indexes = schema.indexes;
    };
}

const DB = DBType(.{
    .tables = .{ .account = Account, .transfer = Transfer },
    .indexes = .{ .transfer = .{ .debit_account, .credit_account } },
});
```

## Comptime guardrails
- Keep compile-time loops bounded; increase the branch quota only where needed.
- Avoid `extern` calls in comptime blocks; they cannot run at compile time.
- Use `@compileError` to enforce invariants on comptime parameters.

## Comptime diagnostics
```zig
test "comptime log" {
    comptime @compileLog("compile-time value =", 42);
}
```

## Build essentials (build.zig)
```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "my-app",
        .root_source_file = .{ .path = "src/main.zig" },
        .target = target,
        .optimize = optimize,
    });

    b.installArtifact(exe);

    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());

    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);
}
```

## Package management (build.zig.zon)
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
    .paths = .{
        "build.zig",
        "build.zig.zon",
        "src",
    },
}
```

## Memory / allocators
```zig
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const bytes = try allocator.alloc(u8, 100);
    defer allocator.free(bytes);
}
```

## Zero-copy playbook (0.15.2, POSIX-first)
- **Mindset:** Treat input as immutable bytes; parse into views, not copies.
- **Borrowed vs owned:** Make ownership explicit and easy to reason about.
- **Decode lazily:** Only allocate when you must transform (escapes, compression, transcoding).
- **Offsets over copies:** Store spans as `(start, len)` into a stable base buffer.
- **Lifetime boundaries:** Never return slices into temporary buffers (stack or reuse buffers).

### Borrowed/owned API template (copy-on-write escape hatch)
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

### POSIX mmap (zero-copy file base)
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

### Lazy decode pattern (borrow unless escaped)
```zig
fn parseName(raw: []const u8, allocator: std.mem.Allocator) !ByteView {
    if (std.mem.indexOf(u8, raw, "#") == null) {
        return .{ .borrowed = raw };
    }
    var out: std.ArrayList(u8) = .empty;
    errdefer out.deinit(allocator);
    // ...decode escapes into out...
    return .{ .owned = try out.toOwnedSlice(allocator) };
}
```

### Streaming/network zero-copy pattern (sliding window)
```zig
const std = @import("std");

pub fn pump(reader: anytype, buf: []u8, parse: anytype) !void {
    var start: usize = 0;
    var end: usize = 0;
    while (true) {
        if (end == buf.len) {
            // Compact: keep unconsumed bytes, slide to front.
            const remaining = end - start;
            std.mem.copyForwards(u8, buf[0..remaining], buf[start..end]);
            start = 0;
            end = remaining;
        }
        const n = try reader.read(buf[end..]);
        if (n == 0) break;
        end += n;

        // parse should return how many bytes it consumed from buf[start..end]
        const consumed = try parse(buf[start..end]);
        start += consumed;
    }
}
```

### zpdf-inspired patterns to emulate
- **Base buffer is immutable:** hold `data: []const u8` for the entire doc lifetime.
- **Ownership flag:** track when you own the base buffer (mmap) vs borrowed memory.
- **Arena for object graph:** allocate parsed objects in a long-lived arena to avoid per-node frees.
- **Streams as slices:** stream bytes are views into the base buffer when length is known.
- **Decode on demand:** only allocate when escapes/filters require transformation.

### Zero-copy guardrails
- Avoid returning slices into temporary read buffers (ring/stack). If you must, wrap in a view that carries the owning buffer.
- Keep parse results stable: if you need to reuse a mutable buffer, copy just the token you must keep.
- Document lifetime rules in types and doc comments: callers should not guess.
- Prefer `[]const u8` views and `Span`/offsets; delay `[]u8` allocations until required.

### Strict no-alloc-by-default contract
- **Rule:** Borrowed APIs take no allocator and never allocate.
- **Fallback:** If transformation is required, return `error.AllocationRequired` or a token with deferred decode.
- **Naming:** use `*Borrowed`/`*Owned` or `toOwned` to make allocation opt-in at call sites.

```zig
const NameToken = struct {
    raw: []const u8,
    has_escapes: bool,
};

fn parseNameBorrowed(self: *Parser) !NameToken {
    const raw = self.scanName();
    return .{ .raw = raw, .has_escapes = hasEscapes(raw) };
}

fn decodeNameOwned(tok: NameToken, allocator: std.mem.Allocator) ![]u8 {
    if (!tok.has_escapes) return allocator.dupe(u8, tok.raw);
    return try decodeName(tok.raw, allocator);
}
```

### Testing zero-copy behavior
- **Leak detection:** use `std.testing.allocator` and `defer` frees to keep tests honest.
- **Allocation counting:** wrap an allocator and assert `alloc_count == 0` for zero-copy paths.
- **OOM injection:** run parsers under `std.testing.FailingAllocator` to validate error handling.
- **Exhaustive OOM:** use `std.testing.checkAllAllocationFailures` to probe every allocation site.
- **Regression trap:** add a test that fails if a "zero-copy" code path allocates.

```zig
const CountingAllocator = struct {
    child: std.mem.Allocator,
    count: usize = 0,

    pub fn allocator(self: *CountingAllocator) std.mem.Allocator {
        return .{
            .ptr = self,
            .vtable = &.{
                .alloc = alloc,
                .resize = resize,
                .free = free,
            },
        };
    }

    fn alloc(ctx: *anyopaque, len: usize, a: std.mem.Alignment, ra: usize) ?[*]u8 {
        const self: *CountingAllocator = @ptrCast(@alignCast(ctx));
        self.count += 1;
        return self.child.rawAlloc(len, a, ra);
    }

    fn resize(ctx: *anyopaque, buf: []u8, a: std.mem.Alignment, new_len: usize, ra: usize) bool {
        const self: *CountingAllocator = @ptrCast(@alignCast(ctx));
        return self.child.rawResize(buf, a, new_len, ra);
    }

    fn free(ctx: *anyopaque, buf: []u8, a: std.mem.Alignment, ra: usize) void {
        const self: *CountingAllocator = @ptrCast(@alignCast(ctx));
        self.child.rawFree(buf, a, ra);
    }
};

test "zero-copy path does not allocate" {
    var counter = CountingAllocator{ .child = std.testing.allocator };
    _ = counter;
    // call your zero-copy parser with counter.allocator()
    // then assert counter.count == 0
}
```

## C interop
```zig
const c = @cImport({
    @cInclude("stdio.h");
});

pub fn main() void {
    _ = c.printf("Hello from C!\n");
}
```

## Testing
```zig
const std = @import("std");
const testing = std.testing;

fn add(a: i32, b: i32) i32 {
    return a + b;
}

test "addition" {
    try testing.expectEqual(@as(i32, 4), add(2, 2));
}
```

## Pitfalls / gotchas
- Always free heap allocations; make ownership explicit with `defer allocator.free(...)`.
- Avoid returning slices backed by stack memory.
- `[*c]T` is a nullable C pointer; `[*]T` is non-null Zig many-item pointer.
- `build.zig.zon` dependency hashes must match; use `zig fetch --save` to populate them.

## References
- Zig standard library docs
- Zig language reference
- Zig Guide: comptime

## Activation cues
- "zig" / "ziglang"
- ".zig"
- "build.zig" / "build.zig.zon"
- "zig build" / "zig test"
- "comptime"
- "allocator"
- "@typeInfo" / "@compileError"
