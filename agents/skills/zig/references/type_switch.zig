const std = @import("std");

pub fn typeSwitch(comptime T: type, comptime R: type, v: anytype) R {
    return switch (@typeInfo(T)) {
        .@"struct" => |info| v.onStruct(T, info),
        .@"union" => |info| v.onUnion(T, info),
        .@"enum" => |info| v.onEnum(T, info),
        .array => |info| v.onArray(T, info),
        .vector => |info| v.onVector(T, info),
        .pointer => |info| v.onPointer(T, info),
        .optional => |info| v.onOptional(T, info),
        .error_union => |info| v.onErrorUnion(T, info),
        .int => |info| v.onInt(T, info),
        .float => |info| v.onFloat(T, info),
        .bool => v.onBool(T),
        else => v.onOther(T),
    };
}

test "typeSwitch example" {
    const Type = std.lang.Type;
    const Kind = enum { int, float, ptr, array, struct_, other };

    const visitor = struct {
        fn onStruct(_: @This(), comptime _: type, _: Type.Struct) Kind {
            return .struct_;
        }

        fn onUnion(_: @This(), comptime _: type, _: Type.Union) Kind {
            return .other;
        }

        fn onEnum(_: @This(), comptime _: type, _: Type.Enum) Kind {
            return .other;
        }

        fn onArray(_: @This(), comptime _: type, _: Type.Array) Kind {
            return .array;
        }

        fn onVector(_: @This(), comptime _: type, _: Type.Vector) Kind {
            return .other;
        }

        fn onPointer(_: @This(), comptime _: type, _: Type.Pointer) Kind {
            return .ptr;
        }

        fn onOptional(_: @This(), comptime _: type, _: Type.Optional) Kind {
            return .other;
        }

        fn onErrorUnion(_: @This(), comptime _: type, _: Type.ErrorUnion) Kind {
            return .other;
        }

        fn onInt(_: @This(), comptime _: type, _: Type.Int) Kind {
            return .int;
        }

        fn onFloat(_: @This(), comptime _: type, _: Type.Float) Kind {
            return .float;
        }

        fn onBool(_: @This(), comptime _: type) Kind {
            return .other;
        }

        fn onOther(_: @This(), comptime _: type) Kind {
            return .other;
        }
    }{};

    try std.testing.expectEqual(Kind.ptr, typeSwitch([]const u8, Kind, visitor));
    try std.testing.expectEqual(Kind.struct_, typeSwitch(struct { x: u8 }, Kind, visitor));
    try std.testing.expectEqual(Kind.int, typeSwitch(u32, Kind, visitor));
    try std.testing.expectEqual(Kind.float, typeSwitch(f32, Kind, visitor));
    try std.testing.expectEqual(Kind.array, typeSwitch([2]u8, Kind, visitor));
    inline for (.{ union(enum) { x: u8 }, enum { x }, @Vector(2, u8), ?u8, error{Bad}!u8, bool, void }) |T| {
        try std.testing.expectEqual(Kind.other, typeSwitch(T, Kind, visitor));
    }
}
