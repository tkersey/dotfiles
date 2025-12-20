---
name: zig
description: Zig development runbook; use when editing or modifying .zig files, build.zig, or build.zig.zon, or when working on Zig builds, packages, memory/allocators, C interop, or tests.
---

# Zig

## When to use
- Editing or reviewing `.zig` source files
- Modifying `build.zig` or `build.zig.zon`
- Configuring the build system, dependencies, or cross-compilation
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
