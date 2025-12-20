---
name: zig
description: Zig development runbook; use when editing or modifying .zig files, build.zig, or build.zig.zon, or when working on Zig builds, packages, comptime/metaprogramming, reflection/type generation, memory/allocators, C interop, or tests.
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
