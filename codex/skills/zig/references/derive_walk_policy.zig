//! Policy-driven structural traversal; bounded failures propagate to callers.
//! Hashes are process-local, non-cryptographic and not canonical fingerprints.
//! Shallow pointers use addresses; floats use bits (including signed zero/NaNs).
//! Host-sized lengths and native scalar hashing are not a portable wire encoding.
//! Equality is still required to resolve hash collisions.
const std = @import("std");

pub const Delim = enum(u8) { braces, brackets, parens };
pub const WalkOptions = struct {
    strat: std.hash.Strategy = .Shallow,
    max_depth: usize = 64,
    // Counts struct fields and sequence elements, not bytes or all visited nodes.
    max_elems: usize = 1_000_000,
};

pub fn walk(comptime T: type, value: T, policy: anytype, comptime opts: WalkOptions) anyerror!void {
    var budget = opts.max_elems;
    try walkImpl(T, value, policy, opts, 0, &budget);
}

fn childOptions(comptime opts: WalkOptions) WalkOptions {
    var child = opts;
    if (child.strat == .Deep) child.strat = .Shallow;
    return child;
}

fn consume(budget: *usize) error{BudgetExceeded}!void {
    if (budget.* == 0) return error.BudgetExceeded;
    budget.* -= 1;
}

fn walkImpl(comptime T: type, value: T, policy: anytype, comptime opts: WalkOptions, depth: usize, budget: *usize) anyerror!void {
    if (depth > opts.max_depth) return error.DepthExceeded;
    switch (@typeInfo(T)) {
        .@"struct" => |info| {
            try policy.begin(.braces);
            var first = true;
            inline for (info.field_names, info.field_types, info.field_attrs) |name, Field, attrs| {
                if (attrs.@"comptime") continue;
                try consume(budget);
                if (!first) try policy.sep();
                first = false;
                try policy.key(name);
                try policy.assign();
                try walkImpl(Field, @field(value, name), policy, opts, depth + 1, budget);
            }
            try policy.end(.braces);
        },
        .@"union" => |info| {
            if (info.tag_type == null) @compileError("walk: untagged union unsupported: " ++ @typeName(T));
            switch (value) {
                inline else => |payload, tag| {
                    try policy.tag(@tagName(tag));
                    if (@TypeOf(payload) != void) {
                        try policy.begin(.parens);
                        try walkImpl(@TypeOf(payload), payload, policy, opts, depth + 1, budget);
                        try policy.end(.parens);
                    }
                },
            }
        },
        .array => |info| {
            try policy.begin(.brackets);
            for (value, 0..) |elem, i| {
                try consume(budget);
                if (i != 0) try policy.sep();
                try walkImpl(info.child, elem, policy, opts, depth + 1, budget);
            }
            try policy.end(.brackets);
        },
        .vector => |info| {
            const array: [info.len]info.child = value;
            try walkImpl(@TypeOf(array), array, policy, opts, depth, budget);
        },
        .pointer => |info| switch (info.size) {
            .one => switch (opts.strat) {
                .Shallow => try policy.ptr(@intFromPtr(value)),
                .Deep, .DeepRecursive => {
                    try policy.prefix("*");
                    try walkImpl(info.child, value.*, policy, childOptions(opts), depth + 1, budget);
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
                    for (value, 0..) |elem, i| {
                        try consume(budget);
                        if (i != 0) try policy.sep();
                        try walkImpl(info.child, elem, policy, childOptions(opts), depth + 1, budget);
                    }
                    try policy.end(.brackets);
                },
            },
            .many, .c => switch (opts.strat) {
                .Shallow => try policy.ptr(@intFromPtr(value)),
                else => @compileError("walk: cannot traverse unknown-length pointers: " ++ @typeName(T)),
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
        .@"enum", .int, .bool, .float => try policy.scalar(value),
        else => @compileError("walk: define semantics for " ++ @typeName(T)),
    }
}

pub const HashPolicy = struct {
    hasher: *std.hash.Wyhash,
    fn tok(self: *HashPolicy, byte: u8) void {
        self.hasher.update(&.{byte});
    }
    pub fn begin(self: *HashPolicy, comptime d: Delim) anyerror!void {
        self.tok(0xA0 ^ @backingInt(d));
    }
    pub fn end(self: *HashPolicy, comptime d: Delim) anyerror!void {
        self.tok(0xB0 ^ @backingInt(d));
    }
    pub fn sep(self: *HashPolicy) anyerror!void {
        self.tok(0x01);
    }
    pub fn assign(self: *HashPolicy) anyerror!void {
        self.tok(0x02);
    }
    fn text(self: *HashPolicy, tag_byte: u8, bytes: []const u8) void {
        self.tok(tag_byte);
        std.hash.autoHashStrat(self.hasher, bytes.len, .Shallow);
        self.hasher.update(bytes);
    }
    pub fn prefix(self: *HashPolicy, bytes: []const u8) anyerror!void {
        self.text(0x03, bytes);
    }
    pub fn key(self: *HashPolicy, bytes: []const u8) anyerror!void {
        self.text(0x04, bytes);
    }
    pub fn tag(self: *HashPolicy, bytes: []const u8) anyerror!void {
        self.text(0x05, bytes);
    }
    pub fn ptr(self: *HashPolicy, addr: usize) anyerror!void {
        self.tok(0x06);
        std.hash.autoHashStrat(self.hasher, addr, .Shallow);
    }
    pub fn nil(self: *HashPolicy) anyerror!void {
        self.tok(0x07);
    }
    pub fn scalar(self: *HashPolicy, value: anytype) anyerror!void {
        self.tok(0x08);
        switch (@typeInfo(@TypeOf(value))) {
            .float => |info| {
                const U = @Int(.unsigned, info.bits);
                const bits: U = @bitCast(value);
                std.hash.autoHashStrat(self.hasher, bits, .Shallow);
            },
            else => std.hash.autoHashStrat(self.hasher, value, .Shallow),
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
        pub fn scalar(self: *@This(), value: anytype) anyerror!void {
            try self.w.print("{any}", .{value});
        }
    };
}

// Pair is sequential, not transactional: B may fail after A observes an event.
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
        pub fn scalar(self: *@This(), value: anytype) anyerror!void {
            try self.a.scalar(value);
            try self.b.scalar(value);
        }
    };
}

pub fn derivedHash(value: anytype, comptime opts: WalkOptions) anyerror!u64 {
    var hasher = std.hash.Wyhash.init(0);
    var policy = HashPolicy{ .hasher = &hasher };
    try walk(@TypeOf(value), value, &policy, opts);
    return hasher.final();
}

// On failure the writer may contain a prefix; caller owns its recovery policy.
pub fn derivedFormat(writer: anytype, value: anytype, comptime opts: WalkOptions) anyerror!void {
    var policy = FormatPolicy(@TypeOf(writer.*)){ .w = writer };
    try walk(@TypeOf(value), value, &policy, opts);
}

// No hash is returned on failure, but writer output can be partial.
pub fn derivedHashAndFormat(writer: anytype, value: anytype, comptime opts: WalkOptions) anyerror!u64 {
    var hasher = std.hash.Wyhash.init(0);
    var hp = HashPolicy{ .hasher = &hasher };
    var fp = FormatPolicy(@TypeOf(writer.*)){ .w = writer };
    var both = Pair(@TypeOf(hp), @TypeOf(fp)){ .a = &hp, .b = &fp };
    try walk(@TypeOf(value), value, &both, opts);
    return hasher.final();
}

test "limits propagate rather than becoming unreachable" {
    try std.testing.expectError(error.BudgetExceeded, derivedHash([_]u8{1}, .{ .max_elems = 0 }));
    try std.testing.expectError(error.DepthExceeded, derivedHash([_]u8{1}, .{ .max_depth = 0 }));
    _ = try derivedHash([_]u8{}, .{ .max_elems = 0, .max_depth = 0 });
}

test "formatting has an independent expected output" {
    var buf: [128]u8 = undefined;
    var writer: std.Io.Writer = .fixed(&buf);
    const value = [_]u8{ 1, 2 };
    const hash = try derivedHashAndFormat(&writer, value, .{});
    try std.testing.expectEqualStrings("[1, 2]", buf[0..writer.end]);
    try std.testing.expectEqual(try derivedHash(value, .{}), hash);
}

test "writer failure preserves documented partial output" {
    var buf: [2]u8 = undefined;
    var writer: std.Io.Writer = .fixed(&buf);
    try std.testing.expectError(error.WriteFailed, derivedFormat(&writer, [_]u8{ 1, 2 }, .{}));
    try std.testing.expect(writer.end > 0);
    var other: std.Io.Writer = .fixed(&buf);
    try std.testing.expectError(error.WriteFailed, derivedHashAndFormat(&other, [_]u8{ 1, 2 }, .{}));
}

test "float branch is instantiated and uses bitwise identity" {
    const positive = try derivedHash(@as(f32, 0.0), .{});
    const negative = try derivedHash(@as(f32, -0.0), .{});
    try std.testing.expect(positive != negative);
    _ = try derivedHash(@as(f64, 1.5), .{});
}

test "shallow identity versus deep content" {
    var value: u32 = 1;
    const shallow = try derivedHash(&value, .{});
    const deep = try derivedHash(&value, .{ .strat = .Deep });
    value = 2;
    try std.testing.expectEqual(shallow, try derivedHash(&value, .{}));
    try std.testing.expect(deep != try derivedHash(&value, .{ .strat = .Deep }));
}

test "deep stops at nested pointers but recursive traversal reads them" {
    var value: u32 = 1;
    const pointer = &value;
    const once = try derivedHash(&pointer, .{ .strat = .Deep });
    const recursive = try derivedHash(&pointer, .{ .strat = .DeepRecursive });
    value = 2;
    try std.testing.expectEqual(once, try derivedHash(&pointer, .{ .strat = .Deep }));
    try std.testing.expect(recursive != try derivedHash(&pointer, .{ .strat = .DeepRecursive }));
}

test "nested shapes, union tags, slices, vectors and errors" {
    const U = union(enum) { a: u32, b: []const u8, empty };
    const S = struct { n: u16, u: U, maybe: ?u8 };
    _ = try derivedHash(S{ .n = 7, .u = .{ .b = "zig" }, .maybe = 3 }, .{ .strat = .DeepRecursive });
    _ = try derivedHash(@as(U, .empty), .{});
    _ = try derivedHash(@as(?u8, null), .{});
    _ = try derivedHash(@as(error{Bad}!u8, error.Bad), .{});
    _ = try derivedHash(@as(error{Bad}!u8, 3), .{});
    _ = try derivedHash(@as(@Vector(2, u8), .{ 1, 2 }), .{});
}

test "parallel reflection arrays preserve field order and comptime skipping" {
    const S = struct { comptime fixed: u8 = 7, value: u8 };
    var buf: [32]u8 = undefined;
    var writer: std.Io.Writer = .fixed(&buf);
    try derivedFormat(&writer, S{ .value = 9 }, .{});
    try std.testing.expectEqualStrings("{value=9}", buf[0..writer.end]);
}
