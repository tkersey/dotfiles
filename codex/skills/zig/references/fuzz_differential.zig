//! Zig 0.16 Smith fuzzing template for differential checks.
//! Keep crash corpora in testdata/fuzz/ and reproduce with corpus fixtures.

const std = @import("std");

fn reference(input: []const u8) !u64 {
    var n: u64 = 0;
    for (input) |b| n += @popCount(b);
    return n;
}

fn optimized(input: []const u8) !u64 {
    // Replace with the optimized implementation under test.
    return reference(input);
}

fn fuzzTarget(_: void, smith: *std.testing.Smith) !void {
    var storage: [1024]u8 = undefined;
    var len: usize = 0;

    while (len < storage.len and !smith.eosWeightedSimple(7, 1)) : (len += 1) {
        storage[len] = smith.value(u8);
    }

    const input = storage[0..len];
    try std.testing.expectEqual(try reference(input), try optimized(input));
}

test "differential fuzz" {
    const seeds = &[_][]const u8{ "", "0", "needle", "\x00\x00\x00", "\xff\xff\xff" };
    try std.testing.fuzz({}, fuzzTarget, .{ .corpus = seeds });
}
