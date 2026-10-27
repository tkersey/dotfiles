//! Allocation-failure coverage template for Zig 0.16.x.

const std = @import("std");

fn work(allocator: std.mem.Allocator, input: []const u8) !void {
    const copy = try allocator.dupe(u8, input);
    defer allocator.free(copy);

    // Add the code path under test here. Keep ownership explicit.
    try std.testing.expectEqualSlices(u8, input, copy);
}

test "allocation failure coverage" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        work,
        .{"seed"},
    );
}
