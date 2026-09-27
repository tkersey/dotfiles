//! Small Zig 0.16 patterns. Validate with the project's exact toolchain.
const std = @import("std");

fn wrappedSlot(capacity: usize, head: usize, offset: usize) usize {
    std.debug.assert(capacity > 0 and head < capacity and offset <= capacity);
    const tail = capacity - head;
    return if (offset >= tail) offset - tail else head + offset;
}

pub fn RingBuffer(comptime T: type, comptime capacity: usize) type {
    if (capacity == 0) @compileError("RingBuffer capacity must be nonzero");
    return struct {
        const Self = @This();
        items: [capacity]T = undefined,
        head: usize = 0,
        len: usize = 0,

        fn slot(self: *const Self, offset: usize) usize {
            // Avoid head + offset overflow even for large capacities.
            return wrappedSlot(capacity, self.head, offset);
        }

        pub fn push(self: *Self, value: T) void {
            self.items[self.slot(self.len)] = value;
            if (self.len < capacity) {
                self.len += 1;
            } else {
                self.head = if (self.head == capacity - 1) 0 else self.head + 1;
            }
        }

        pub fn at(self: *const Self, index: usize) ?T {
            if (index >= self.len) return null;
            return self.items[self.slot(index)];
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

test "ring overwrites oldest values and rejects out-of-range reads" {
    var rb: RingBuffer(u8, 2) = .{};
    rb.push(1);
    rb.push(2);
    rb.push(3);
    try std.testing.expectEqual(@as(?u8, 2), rb.at(0));
    try std.testing.expectEqual(@as(?u8, 3), rb.at(1));
    try std.testing.expectEqual(@as(?u8, null), rb.at(2));
    var one: RingBuffer(u32, 1) = .{};
    one.push(99);
    one.push(100);
    try std.testing.expectEqual(@as(?u32, 100), one.at(0));
}

test "ring index arithmetic handles large capacity" {
    const capacity = std.math.maxInt(usize);
    try std.testing.expectEqual(@as(usize, 0), wrappedSlot(capacity, capacity - 1, 1));
    try std.testing.expectEqual(capacity - 1, wrappedSlot(capacity, capacity - 1, capacity));
}

test "reflection plan including empty shape" {
    const S = struct { a: u8, b: u16 };
    const Plan = StructPlan(S);
    try std.testing.expectEqual(@as(usize, 2), Plan.field_count);
    try std.testing.expectEqualStrings("a", Plan.fieldName(0));
    try std.testing.expectEqualStrings("b", Plan.fieldName(1));
    try std.testing.expectEqual(@as(usize, 0), StructPlan(struct {}).field_count);
    try std.testing.expect(!hasDeclSafe(u32, "missing"));
    try std.testing.expect(hasFieldSafe(S, "a"));
}

test "generated integer and struct types" {
    const U9 = UInt(9);
    const P = Pair(U9, []const u8);
    const p: P = .{ .first = 511, .second = "zig" };
    try std.testing.expectEqual(@as(U9, 511), p.first);
    try std.testing.expectEqualStrings("zig", p.second);
}

test "optional payload and supported value shapes" {
    try std.testing.expect(OptionalPayload(?u32) == u32);
    try std.testing.expectEqualStrings("int", valueKind(@as(u32, 1)));
    try std.testing.expectEqualStrings("float", valueKind(@as(f64, 1.5)));
    try std.testing.expectEqualStrings("bool", valueKind(true));
    const n: u8 = 1;
    try std.testing.expectEqualStrings("pointer", valueKind(&n));
}
