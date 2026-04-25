//! Systems-engineering review snippets for Zig 0.16-style code.
//! These are adaptable patterns, not a standalone library.

const std = @import("std");

pub const OwnedBytes = struct {
    allocator: std.mem.Allocator,
    bytes: []u8,

    pub fn initCopy(allocator: std.mem.Allocator, src: []const u8) !OwnedBytes {
        const bytes = try allocator.dupe(u8, src);
        return .{ .allocator = allocator, .bytes = bytes };
    }

    pub fn deinit(self: *OwnedBytes) void {
        self.allocator.free(self.bytes);
        self.* = undefined;
    }
};

pub const BoundedSlice = struct {
    bytes: []const u8,

    pub fn init(bytes: []const u8, max_len: usize) !BoundedSlice {
        if (bytes.len > max_len) return error.TooLong;
        return .{ .bytes = bytes };
    }
};

pub fn requireAlignedSlice(comptime T: type, bytes: []u8) ![]T {
    if (bytes.len % @sizeOf(T) != 0) return error.LengthNotMultiple;
    const addr = @intFromPtr(bytes.ptr);
    if (addr % @alignOf(T) != 0) return error.Unaligned;
    return std.mem.bytesAsSlice(T, bytes);
}

pub const Header = extern struct {
    magic: u32,
    version: u16,
    flags: u16,
};

test "layout proof: Header" {
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(Header));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(Header, "magic"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(Header, "version"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(Header, "flags"));
}

pub const ControlRegister = packed struct(u32) {
    enable: bool,
    mode: u3,
    reserved: u28 = 0,
};

pub fn writeControl(reg: *volatile ControlRegister, value: ControlRegister) void {
    // Prefer whole-register volatile access over taking pointers to packed fields.
    reg.* = value;
}

pub const ParseError = error{
    Empty,
    InvalidMagic,
    UnsupportedVersion,
};

pub fn parseHeader(bytes: []const u8) ParseError!Header {
    if (bytes.len == 0) return error.Empty;
    if (bytes.len < @sizeOf(Header)) return error.InvalidMagic;

    // For portable wire formats, prefer explicit endian parsing over direct casts.
    const magic = std.mem.readInt(u32, bytes[0..4], .little);
    if (magic != 0x2147495a) return error.InvalidMagic; // "ZIG!" little-endian example

    return .{
        .magic = magic,
        .version = std.mem.readInt(u16, bytes[4..6], .little),
        .flags = std.mem.readInt(u16, bytes[6..8], .little),
    };
}

pub const AtomicCounter = struct {
    value: std.atomic.Value(usize) = .init(0),

    pub fn increment(self: *AtomicCounter) usize {
        // Monotonic is enough for a standalone statistic with no publication semantics.
        return self.value.fetchAdd(1, .monotonic);
    }

    pub fn load(self: *AtomicCounter) usize {
        return self.value.load(.monotonic);
    }
};

pub fn cloneTwo(allocator: std.mem.Allocator, a: []const u8, b: []const u8) !struct { a: []u8, b: []u8 } {
    const owned_a = try allocator.dupe(u8, a);
    errdefer allocator.free(owned_a);

    const owned_b = try allocator.dupe(u8, b);
    errdefer allocator.free(owned_b);

    return .{ .a = owned_a, .b = owned_b };
}

fn cloneTwoHarness(allocator: std.mem.Allocator, a: []const u8, b: []const u8) !void {
    const pair = try cloneTwo(allocator, a, b);
    defer allocator.free(pair.a);
    defer allocator.free(pair.b);
}

test "allocation-failure proof: cloneTwo" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        cloneTwoHarness,
        .{ "a", "b" },
    );
}
