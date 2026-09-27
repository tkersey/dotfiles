//! A bounded representation experiment, not a claimed optimization.
const std = @import("std");
pub const Strategy = enum { direct, plan, runtime_table };

fn Schema(comptime n: usize) type {
    if (n > 1024) @compileError("scaling example supports at most 1024 fields");
    // Fixed ceiling for this experiment's field-name/type construction.
    @setEvalBranchQuota(100_000);
    var names: [n][]const u8 = undefined;
    for (&names, 0..) |*name, i| name.* = std.fmt.comptimePrint("f{d}", .{i});
    const types: [n]type = @splat(u64);
    const attrs: [n]std.builtin.Type.StructField.Attributes = @splat(.{});
    return @Struct(.auto, null, &names, &types, &attrs);
}

fn weights(comptime n: usize) [n]u64 {
    var result: [n]u64 = undefined;
    for (@typeInfo(Schema(n)).@"struct".fields, 0..) |field, i| result[i] = field.name.len;
    return result;
}

fn nameWidth(index: usize) u64 {
    var digits: u64 = 1;
    var value = index;
    while (value >= 10) : (value /= 10) digits += 1;
    return digits + 1; // 'f' plus decimal digits.
}

pub fn checksum(comptime strategy: Strategy, comptime n: usize, input: *const [n]u64) u64 {
    if (n > 1024) @compileError("scaling example supports at most 1024 fields");
    var sum: u64 = 0;
    switch (strategy) {
        .direct => {
            inline for (@typeInfo(Schema(n)).@"struct".fields, 0..) |field, i| {
                sum +%= input[i] *% @as(u64, field.name.len);
            }
        },
        .plan => {
            const plan = comptime weights(n);
            for (input, plan) |value, weight| sum +%= value *% weight;
        },
        .runtime_table => {
            var table: [n]u64 = undefined;
            for (&table, 0..) |*weight, i| weight.* = nameWidth(i);
            for (input, table) |value, weight| sum +%= value *% weight;
        },
    }
    return sum;
}

test "representations agree with an independent formula across decimal boundaries" {
    inline for (.{ 0, 1, 8, 32, 128 }) |n| {
        var input: [n]u64 = undefined;
        for (&input, 0..) |*value, i| value.* = i + 1;
        var expected: u64 = 0;
        for (input, 0..) |value, i| {
            const width: u64 = if (i < 10) 2 else if (i < 100) 3 else 4;
            expected +%= value *% width;
        }
        inline for (.{ Strategy.direct, Strategy.plan, Strategy.runtime_table }) |strategy| {
            try std.testing.expectEqual(expected, checksum(strategy, n, &input));
        }
    }
}
