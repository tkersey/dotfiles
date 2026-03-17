const std = @import("std");

fn duplicateTwice(alloc: std.mem.Allocator, input: []const u8) !void {
    const first = try alloc.dupe(u8, input);
    defer alloc.free(first);

    const second = try alloc.dupe(u8, first);
    defer alloc.free(second);

    try std.testing.expectEqualStrings(input, second);
}

test "check all allocation failures" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        duplicateTwice,
        .{"zig"},
    );
}

test "pin a fail index as regression seed" {
    var failing = std.testing.FailingAllocator.init(
        std.testing.allocator,
        .{ .fail_index = 0 },
    );

    try std.testing.expectError(
        error.OutOfMemory,
        duplicateTwice(failing.allocator(), "zig"),
    );
}
