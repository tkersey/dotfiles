const std = @import("std");

pub fn Partial(comptime S: type) type {
    const info = @typeInfo(S);
    if (info != .@"struct") @compileError("Partial expects a struct type");

    const s = info.@"struct";
    const n = comptime blk: {
        var count: usize = 0;
        for (s.field_attrs) |attrs| {
            if (!attrs.is_comptime) count += 1;
        }
        break :blk count;
    };

    var names: [n][]const u8 = undefined;
    var types: [n]type = undefined;
    var attrs: [n]std.lang.Type.Struct.FieldAttributes = undefined;

    var i: usize = 0;
    inline for (s.field_names, s.field_types, s.field_attrs) |name, FT, attributes| {
        if (attributes.is_comptime) continue;

        const default_value: ?FT = null;

        names[i] = name;
        types[i] = ?FT;
        attrs[i] = .{
            .default_value_ptr = @as(?*const anyopaque, @ptrCast(&default_value)),
            .@"align" = @alignOf(?FT),
        };
        i += 1;
    }

    return @Struct(.auto, null, &names, &types, &attrs);
}

test "Partial example" {
    const S = struct {
        a: u32,
        b: []const u8,
    };

    const P = Partial(S);
    var p: P = .{};
    p.a = 1;
    try std.testing.expect(p.b == null);
}

test "Partial preserves runtime field order and excludes comptime fields" {
    const S = struct {
        first: u16,
        comptime fixed: u8 = 7,
        last: ?u32,
    };
    const P = Partial(S);
    const p: P = .{};
    const info = @typeInfo(P).@"struct";
    try std.testing.expectEqual(@as(usize, 2), info.field_names.len);
    try std.testing.expectEqualStrings("first", info.field_names[0]);
    try std.testing.expectEqualStrings("last", info.field_names[1]);
    try std.testing.expect(p.first == null and p.last == null);
    try std.testing.expect(!@hasField(P, "fixed"));
    try std.testing.expectEqual(@as(usize, 0), @typeInfo(Partial(struct {})).@"struct".field_names.len);
}
