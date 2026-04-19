const std = @import("std");

pub fn Partial(comptime S: type) type {
    const info = @typeInfo(S);
    if (info != .@"struct") @compileError("Partial expects a struct type");

    const s = info.@"struct";
    const n = comptime blk: {
        var count: usize = 0;
        for (s.fields) |f| {
            if (!f.is_comptime) count += 1;
        }
        break :blk count;
    };

    var names: [n][]const u8 = undefined;
    var types: [n]type = undefined;
    var attrs: [n]std.builtin.Type.StructField.Attributes = undefined;

    var i: usize = 0;
    inline for (s.fields) |f| {
        if (f.is_comptime) continue;

        const FT = f.type;
        const default_value: ?FT = null;

        names[i] = f.name;
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
