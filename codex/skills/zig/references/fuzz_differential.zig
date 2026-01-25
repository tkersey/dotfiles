const std = @import("std");

fn reference(bytes: []const u8) u64 {
    var n: u64 = 0;
    for (bytes) |b| n += @popCount(b);
    return n;
}

fn optimized(bytes: []const u8) u64 {
    // Replace with the optimized version (SIMD/threads/etc).
    return reference(bytes);
}

fn fuzzTarget(_: void, input: []const u8) anyerror!void {
    const ref = reference(input);
    const got = optimized(input);
    try std.testing.expectEqual(ref, got);
}

test "fuzz target" {
    const seeds = &[_][]const u8{ "", "0", "needle", "\x00\x00\x00", "\xff\xff\xff" };
    try std.testing.fuzz({}, fuzzTarget, .{ .corpus = seeds });
}
