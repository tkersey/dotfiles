//! Semantic tripwires for the 0.17 baseline; not a comprehensive migration proof.
const std = @import("std");
const patterns = @import("comptime_patterns.zig");

const Hooks = struct {
    pub const visible = 1;
    const private = 2;
    field: u8,
};

test "declaration discovery is public-only even in the defining file" {
    try std.testing.expect(@hasDecl(Hooks, "visible"));
    try std.testing.expect(!@hasDecl(Hooks, "private"));
    try std.testing.expect(patterns.hasDeclSafe(Hooks, "visible"));
    try std.testing.expect(!patterns.hasDeclSafe(Hooks, "private"));
    try std.testing.expect(!patterns.hasDeclSafe(Hooks, "field"));
    try std.testing.expect(patterns.hasFieldSafe(Hooks, "field"));
}

fn checkLogicalBits() !void {
    const bytes: [2]u8 = .{ 0x12, 0x34 };
    const vector: @Vector(2, u8) = bytes;
    try std.testing.expectEqual(@as(u16, 0x3412), @as(u16, @bitCast(bytes)));
    try std.testing.expectEqual(@as(u16, 0x3412), @as(u16, @bitCast(vector)));
    // Wire byte order is a separate choice, not inferred from @bitCast.
    try std.testing.expectEqual(@as(u16, 0x1234), std.mem.readInt(u16, &bytes, .big));
    try std.testing.expectEqual(@as(u16, 0x3412), std.mem.readInt(u16, &bytes, .little));
}

test "logical bits and explicit wire endian agree with independent constants" {
    try checkLogicalBits();
    try comptime checkLogicalBits();
}

test "backing conversions preserve explicit types and bits" {
    const Tag = enum(u8) { ready = 3, done = 9 };
    const done: Tag = @fromBackingInt(@as(u8, 9));
    try std.testing.expectEqual(Tag.done, done);
    try std.testing.expectEqual(@as(u8, 3), @backingInt(Tag.ready));
    const Flags = packed struct(u8) { enabled: bool, rest: u7 = 0 };
    const flags: Flags = @fromBackingInt(@as(u8, 1));
    try std.testing.expect(flags.enabled);
    try std.testing.expectEqual(@as(u8, 1), @backingInt(flags));
}

test "array splat and ceiling division" {
    const values: [4]u8 = @splat(7);
    try std.testing.expectEqualSlices(u8, &.{ 7, 7, 7, 7 }, &values);
    try std.testing.expectEqual(@as(i32, 2), @divCeil(@as(i32, 5), 3));
    try std.testing.expectEqual(@as(i32, -1), @divCeil(@as(i32, -5), 3));
}

test "float slice equality does not turn NaN into a reflexive value" {
    const values: [2]f64 = .{ 1.0, std.math.nan(f64) };
    try std.testing.expect(!std.mem.eql(f64, &values, &values));
}
