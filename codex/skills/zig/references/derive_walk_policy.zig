const std = @import("std");

pub const Delim = enum(u8) { braces, brackets, parens };

pub const WalkOptions = struct {
    strat: std.hash.Strategy = .Shallow,
    max_depth: usize = 64,
    max_elems: usize = 1_000_000,
};

pub fn walk(comptime T: type, value: T, policy: anytype, comptime opts: WalkOptions) anyerror!void {
    var budget: usize = opts.max_elems;
    try walkImpl(T, value, policy, opts, 0, &budget);
}

fn walkImpl(
    comptime T: type,
    value: T,
    policy: anytype,
    comptime opts: WalkOptions,
    depth: usize,
    budget: *usize,
) anyerror!void {
    if (depth > opts.max_depth) return error.DepthExceeded;

    switch (@typeInfo(T)) {
        .@"struct" => |info| {
            try policy.begin(.braces);
            var first = true;

            inline for (info.fields) |f| {
                if (f.is_comptime) continue;
                if (budget.* == 0) return error.BudgetExceeded;
                budget.* -= 1;

                const name: []const u8 = f.name;
                if (!first) try policy.sep();
                first = false;

                try policy.key(name);
                try policy.assign();
                try walkImpl(f.type, @field(value, f.name), policy, opts, depth + 1, budget);
            }
            try policy.end(.braces);
        },

        .@"union" => |info| {
            if (info.tag_type == null)
                @compileError("walk: untagged union unsupported: " ++ @typeName(T));

            switch (value) {
                inline else => |payload, tag| {
                    const tag_name = @tagName(tag);
                    try policy.tag(tag_name);
                    if (@TypeOf(payload) != void) {
                        try policy.begin(.parens);
                        try walkImpl(@TypeOf(payload), payload, policy, opts, depth + 1, budget);
                        try policy.end(.parens);
                    }
                },
            }
        },

        .@"enum" => try policy.scalar(value),

        .array => |info| {
            try policy.begin(.brackets);
            for (value, 0..) |elem, i| {
                if (budget.* == 0) return error.BudgetExceeded;
                budget.* -= 1;
                if (i != 0) try policy.sep();
                try walkImpl(info.child, elem, policy, opts, depth + 1, budget);
            }
            try policy.end(.brackets);
        },

        .vector => |info| {
            try policy.begin(.brackets);
            var i: usize = 0;
            while (i < info.len) : (i += 1) {
                if (budget.* == 0) return error.BudgetExceeded;
                budget.* -= 1;
                if (i != 0) try policy.sep();
                try walkImpl(info.child, value[i], policy, opts, depth + 1, budget);
            }
            try policy.end(.brackets);
        },

        .pointer => |info| switch (info.size) {
            .one => switch (opts.strat) {
                .Shallow => try policy.ptr(@intFromPtr(value)),
                .Deep, .DeepRecursive => {
                    try policy.prefix("*");
                    try walkImpl(info.child, value.*, policy, opts, depth + 1, budget);
                },
            },

            .slice => switch (opts.strat) {
                .Shallow => {
                    try policy.ptr(@intFromPtr(value.ptr));
                    try policy.prefix("[");
                    try policy.scalar(value.len);
                    try policy.prefix("]");
                },
                .Deep, .DeepRecursive => {
                    try policy.begin(.brackets);
                    for (value, 0..) |elem, j| {
                        if (budget.* == 0) return error.BudgetExceeded;
                        budget.* -= 1;
                        if (j != 0) try policy.sep();
                        try walkImpl(info.child, elem, policy, opts, depth + 1, budget);
                    }
                    try policy.end(.brackets);
                },
            },

            .many, .c => switch (opts.strat) {
                .Shallow => try policy.ptr(@intFromPtr(value)),
                else => @compileError("walk: cannot deep-hash unknown-length pointers: " ++ @typeName(T)),
            },
        },

        .optional => |info| if (value) |payload| {
            try walkImpl(info.child, payload, policy, opts, depth + 1, budget);
        } else {
            try policy.nil();
        },

        .error_union => |info| {
            const payload = value catch |err| {
                try policy.prefix("error.");
                try policy.key(@errorName(err));
                return;
            };
            try walkImpl(info.payload, payload, policy, opts, depth + 1, budget);
        },

        .int, .bool, .float => try policy.scalar(value),

        else => @compileError("walk: define semantics for " ++ @typeName(T)),
    }
}

pub const HashPolicy = struct {
    hasher: *std.hash.Wyhash,

    fn tok(self: *HashPolicy, b: u8) void {
        self.hasher.update(&[_]u8{b});
    }

    pub fn begin(self: *HashPolicy, comptime d: Delim) anyerror!void {
        self.tok(0xA0 ^ @intFromEnum(d));
    }

    pub fn end(self: *HashPolicy, comptime d: Delim) anyerror!void {
        self.tok(0xB0 ^ @intFromEnum(d));
    }

    pub fn sep(self: *HashPolicy) anyerror!void {
        self.tok(0x01);
    }

    pub fn assign(self: *HashPolicy) anyerror!void {
        self.tok(0x02);
    }

    pub fn prefix(self: *HashPolicy, bytes: []const u8) anyerror!void {
        self.tok(0x03);
        std.hash.autoHashStrat(self.hasher, bytes.len, .Shallow);
        self.hasher.update(bytes);
    }

    pub fn key(self: *HashPolicy, bytes: []const u8) anyerror!void {
        self.tok(0x04);
        std.hash.autoHashStrat(self.hasher, bytes.len, .Shallow);
        self.hasher.update(bytes);
    }

    pub fn tag(self: *HashPolicy, bytes: []const u8) anyerror!void {
        self.tok(0x05);
        std.hash.autoHashStrat(self.hasher, bytes.len, .Shallow);
        self.hasher.update(bytes);
    }

    pub fn ptr(self: *HashPolicy, addr: usize) anyerror!void {
        self.tok(0x06);
        std.hash.autoHashStrat(self.hasher, addr, .Shallow);
    }

    pub fn nil(self: *HashPolicy) anyerror!void {
        self.tok(0x07);
    }

    pub fn scalar(self: *HashPolicy, v: anytype) anyerror!void {
        self.tok(0x08);
        const TV = @TypeOf(v);
        switch (@typeInfo(TV)) {
            .float => |info| {
                const U = std.meta.Int(.unsigned, info.bits);
                const bits: U = @bitCast(v);
                std.hash.autoHashStrat(self.hasher, bits, .Shallow);
            },
            else => std.hash.autoHashStrat(self.hasher, v, .Shallow),
        }
    }
};

pub fn FormatPolicy(comptime Writer: type) type {
    return struct {
        w: *Writer,

        pub fn begin(self: *@This(), comptime d: Delim) anyerror!void {
            try self.w.writeAll(switch (d) {
                .braces => "{",
                .brackets => "[",
                .parens => "(",
            });
        }

        pub fn end(self: *@This(), comptime d: Delim) anyerror!void {
            try self.w.writeAll(switch (d) {
                .braces => "}",
                .brackets => "]",
                .parens => ")",
            });
        }

        pub fn sep(self: *@This()) anyerror!void {
            try self.w.writeAll(", ");
        }

        pub fn assign(self: *@This()) anyerror!void {
            try self.w.writeAll("=");
        }

        pub fn prefix(self: *@This(), bytes: []const u8) anyerror!void {
            try self.w.writeAll(bytes);
        }

        pub fn key(self: *@This(), bytes: []const u8) anyerror!void {
            try self.w.writeAll(bytes);
        }

        pub fn tag(self: *@This(), bytes: []const u8) anyerror!void {
            try self.w.print(".{s}", .{bytes});
        }

        pub fn ptr(self: *@This(), addr: usize) anyerror!void {
            try self.w.print("0x{x}", .{addr});
        }

        pub fn nil(self: *@This()) anyerror!void {
            try self.w.writeAll("null");
        }

        pub fn scalar(self: *@This(), v: anytype) anyerror!void {
            // Choose stability > prettiness for fuzz/triage.
            try self.w.print("{any}", .{v});
        }
    };
}

pub fn Pair(comptime A: type, comptime B: type) type {
    return struct {
        a: *A,
        b: *B,

        pub fn begin(self: *@This(), comptime d: Delim) anyerror!void {
            try self.a.begin(d);
            try self.b.begin(d);
        }

        pub fn end(self: *@This(), comptime d: Delim) anyerror!void {
            try self.a.end(d);
            try self.b.end(d);
        }

        pub fn sep(self: *@This()) anyerror!void {
            try self.a.sep();
            try self.b.sep();
        }

        pub fn assign(self: *@This()) anyerror!void {
            try self.a.assign();
            try self.b.assign();
        }

        pub fn prefix(self: *@This(), bytes: []const u8) anyerror!void {
            try self.a.prefix(bytes);
            try self.b.prefix(bytes);
        }

        pub fn key(self: *@This(), bytes: []const u8) anyerror!void {
            try self.a.key(bytes);
            try self.b.key(bytes);
        }

        pub fn tag(self: *@This(), bytes: []const u8) anyerror!void {
            try self.a.tag(bytes);
            try self.b.tag(bytes);
        }

        pub fn ptr(self: *@This(), addr: usize) anyerror!void {
            try self.a.ptr(addr);
            try self.b.ptr(addr);
        }

        pub fn nil(self: *@This()) anyerror!void {
            try self.a.nil();
            try self.b.nil();
        }

        pub fn scalar(self: *@This(), v: anytype) anyerror!void {
            try self.a.scalar(v);
            try self.b.scalar(v);
        }
    };
}

pub fn derivedHash(value: anytype, comptime opts: WalkOptions) u64 {
    var hasher = std.hash.Wyhash.init(0);
    var hp = HashPolicy{ .hasher = &hasher };
    walk(@TypeOf(value), value, &hp, opts) catch unreachable;
    return hasher.final();
}

pub fn derivedFormat(writer: anytype, value: anytype, comptime opts: WalkOptions) anyerror!void {
    const W = @TypeOf(writer.*);
    var fp = FormatPolicy(W){ .w = writer };
    try walk(@TypeOf(value), value, &fp, opts);
}

pub fn derivedHashAndFormat(writer: anytype, value: anytype, comptime opts: WalkOptions) anyerror!u64 {
    var hasher = std.hash.Wyhash.init(0);
    var hp = HashPolicy{ .hasher = &hasher };
    const W = @TypeOf(writer.*);
    var fp = FormatPolicy(W){ .w = writer };
    var both = Pair(@TypeOf(hp), @TypeOf(fp)){ .a = &hp, .b = &fp };
    try walk(@TypeOf(value), value, &both, opts);
    return hasher.final();
}

test "derivedHash matches derivedHashAndFormat" {
    const U = union(enum) {
        a: u32,
        b: []const u8,
    };

    const S = struct {
        n: u16,
        u: U,
        maybe: ?u8,
    };

    const v = S{ .n = 7, .u = .{ .a = 123 }, .maybe = null };
    const opts: WalkOptions = .{ .strat = .Shallow, .max_depth = 64, .max_elems = 1_000_000 };

    const h1 = derivedHash(v, opts);

    var buf: [4096]u8 = undefined;
    var w: std.io.Writer = .fixed(&buf);

    const h2 = try derivedHashAndFormat(&w, v, opts);
    try std.testing.expect(h1 == h2);
    try std.testing.expect(w.end != 0);
}
