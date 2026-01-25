const std = @import("std");
const Type = std.builtin.Type;

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

    var fields: [n]Type.StructField = undefined;
    var i: usize = 0;

    inline for (s.fields) |f| {
        if (f.is_comptime) continue;

        const FT = f.type;
        const dv: ?FT = null;

        fields[i] = .{
            .name = f.name,
            .type = ?FT,
            .default_value_ptr = @as(?*const anyopaque, @ptrCast(&dv)),
            .is_comptime = false,
            .alignment = @alignOf(?FT),
        };
        i += 1;
    }

    return @Type(.{ .@"struct" = .{
        .layout = .auto,
        .fields = &fields,
        .decls = &.{},
        .is_tuple = false,
    } });
}

test "Partial example" {
    const S = struct { a: u32, b: []const u8 };
    const P = Partial(S);

    var p: P = .{};
    p.a = 1;
    try std.testing.expect(p.b == null);
}
