//! Reference snippets for Zig 0.16 comptime reviews.
//! These examples are intended as small patterns to adapt, then validate with
//! the target project's exact Zig toolchain.

const std = @import("std");

pub fn RingBuffer(comptime T: type, comptime capacity: usize) type {
    if (capacity == 0) @compileError("RingBuffer capacity must be nonzero");

    return struct {
        const Self = @This();

        items: [capacity]T = undefined,
        head: usize = 0,
        len: usize = 0,

        pub fn push(self: *Self, value: T) void {
            self.items[(self.head + self.len) % capacity] = value;
            if (self.len < capacity) {
                self.len += 1;
            } else {
                self.head = (self.head + 1) % capacity;
            }
        }

        pub fn at(self: *const Self, index: usize) ?T {
            if (index >= self.len) return null;
            return self.items[(self.head + index) % capacity];
        }
    };
}

pub fn requireStruct(comptime api: []const u8, comptime T: type) void {
    switch (@typeInfo(T)) {
        .@"struct" => {},
        else => @compileError(api ++ "(" ++ @typeName(T) ++ "): expected struct"),
    }
}

pub fn hasDeclSafe(comptime T: type, comptime name: []const u8) bool {
    return switch (@typeInfo(T)) {
        .@"struct", .@"union", .@"enum", .@"opaque" => @hasDecl(T, name),
        else => false,
    };
}

pub fn hasFieldSafe(comptime T: type, comptime name: []const u8) bool {
    return switch (@typeInfo(T)) {
        .@"struct", .@"union", .@"enum" => @hasField(T, name),
        else => false,
    };
}

pub fn StructPlan(comptime T: type) type {
    requireStruct("StructPlan", T);
    const fields = @typeInfo(T).@"struct".fields;

    return struct {
        pub const field_count = fields.len;

        pub fn fieldName(comptime index: usize) []const u8 {
            if (index >= fields.len) {
                @compileError("StructPlan(" ++ @typeName(T) ++ "): field index out of range");
            }
            return fields[index].name;
        }
    };
}

pub fn UInt(comptime bits: u16) type {
    if (bits == 0) @compileError("UInt bits must be nonzero");
    return @Int(.unsigned, bits);
}

pub fn Pair(comptime A: type, comptime B: type) type {
    const names = [_][]const u8{ "first", "second" };
    const types = [_]type{ A, B };
    const attrs = [_]std.builtin.Type.StructField.Attributes{ .{}, .{} };
    return @Struct(.auto, null, &names, &types, &attrs);
}

pub fn OptionalPayload(comptime T: type) type {
    return switch (@typeInfo(T)) {
        .optional => |info| info.child,
        else => @compileError("OptionalPayload(" ++ @typeName(T) ++ "): expected optional type"),
    };
}

pub fn valueKind(value: anytype) []const u8 {
    return switch (@typeInfo(@TypeOf(value))) {
        .int => "int",
        .float => "float",
        .bool => "bool",
        .pointer => "pointer",
        else => @compileError("valueKind: unsupported value type " ++ @typeName(@TypeOf(value))),
    };
}

test "type factory: RingBuffer" {
    var rb: RingBuffer(u8, 2) = .{};
    rb.push(1);
    rb.push(2);
    rb.push(3);

    try std.testing.expectEqual(@as(?u8, 2), rb.at(0));
    try std.testing.expectEqual(@as(?u8, 3), rb.at(1));
    try std.testing.expectEqual(@as(?u8, null), rb.at(2));
}

test "reflection plan" {
    const S = struct { a: u8, b: u16 };
    const Plan = StructPlan(S);

    try std.testing.expectEqual(@as(usize, 2), Plan.field_count);
    try std.testing.expect(std.mem.eql(u8, Plan.fieldName(0), "a"));
    try std.testing.expect(std.mem.eql(u8, Plan.fieldName(1), "b"));
}

test "generated integer and struct types" {
    const U9 = UInt(9);
    const P = Pair(U9, []const u8);
    const p: P = .{ .first = 511, .second = "zig" };

    try std.testing.expectEqual(@as(U9, 511), p.first);
    try std.testing.expectEqualStrings("zig", p.second);
}

test "optional payload" {
    try std.testing.expect(OptionalPayload(?u32) == u32);
}

test "anytype shape validation" {
    try std.testing.expectEqualStrings("int", valueKind(@as(u32, 1)));
    try std.testing.expectEqualStrings("bool", valueKind(true));
}

// Negative fixtures should live in separate compile-fail files, because these
// intentionally stop compilation:
//
// const BadRing = RingBuffer(u8, 0);
// const BadPlan = StructPlan(u32);
// const BadPayload = OptionalPayload(u8);
// const BadKind = valueKind(.{ .unsupported = true });
