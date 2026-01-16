---
name: zig
description: "Zig runbook: build/test, comptime patterns, allocators, build.zig/build.zig.zon, zero-copy parsing, C interop."
---

# Zig

## When to use
- Editing `.zig` files.
- Modifying `build.zig` or `build.zig.zon`.
- Zig builds/tests, dependencies, cross-compilation.
- Comptime, reflection, codegen.
- Allocators, ownership, zero-copy parsing.
- C interop.

## Quick start
```bash
# Initialize
zig init-exe
zig init-lib

# Build/run/test
zig build
zig build run
zig build test
zig test src/main.zig
```

## Common commands
```bash
# Release
zig build -Doptimize=ReleaseFast

# Cross-compile
zig build -Dtarget=x86_64-linux
zig build -Dtarget=aarch64-macos

# Clean artifacts
rm -rf zig-out zig-cache
```

## Comptime essentials
- `comptime` parameters drive generics.
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

## Build essentials (`build.zig`)
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
- Leak detection: use `std.testing.allocator` and `defer` frees.
- Allocation counting: wrap an allocator and assert zero allocations for a “zero-copy” path.
- OOM injection: run under `std.testing.FailingAllocator`.
- Exhaustive OOM: `std.testing.checkAllAllocationFailures`.

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
- Make ownership explicit; always free heap allocations.
- Avoid returning slices backed by stack memory.
- `[*c]T` is nullable; `[*]T` is non-null.
- Use `zig fetch --save` to populate `build.zig.zon` hashes.

## Activation cues
- "zig" / "ziglang" / ".zig"
- "build.zig" / "build.zig.zon"
- "zig build" / "zig test"
- "comptime" / "allocator" / "@typeInfo" / "@compileError"
