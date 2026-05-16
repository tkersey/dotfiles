//! Adaptable Zig hazard-audit patterns. These are review snippets, not a library.

const std = @import("std");

pub const CheckedOffset = struct {
    offset: usize,
    len: usize,

    pub fn init(buffer_len: usize, offset: usize, len: usize) !CheckedOffset {
        if (offset > buffer_len) return error.OutOfBounds;
        if (len > buffer_len - offset) return error.OutOfBounds;
        return .{ .offset = offset, .len = len };
    }

    pub fn slice(self: CheckedOffset, bytes: []const u8) []const u8 {
        return bytes[self.offset .. self.offset + self.len];
    }
};

pub fn AlignedBytes(comptime T: type) type {
    return struct {
        bytes: []align(@alignOf(T)) const u8,

        pub fn init(bytes: []const u8) !@This() {
            if (bytes.len < @sizeOf(T)) return error.TooSmall;
            const aligned: []align(@alignOf(T)) const u8 = @alignCast(bytes);
            return .{ .bytes = aligned[0..@sizeOf(T)] };
        }

        pub fn view(self: @This()) *const T {
            // SAFETY/ZIG-HAZARD:
            // AlignedBytes.init checked len >= @sizeOf(T) and alignment >= @alignOf(T).
            // Caller must still choose T only for in-memory data where typed loads are legal;
            // use endian-aware scalar parsing for wire/disk formats instead.
            return @ptrCast(self.bytes.ptr);
        }
    };
}

test "CheckedOffset rejects overflow and out-of-bounds ranges" {
    try std.testing.expectError(error.OutOfBounds, CheckedOffset.init(4, 5, 0));
    try std.testing.expectError(error.OutOfBounds, CheckedOffset.init(4, 3, 2));
    const checked = try CheckedOffset.init(4, 1, 2);
    try std.testing.expectEqualSlices(u8, &.{ 2, 3 }, checked.slice(&.{ 1, 2, 3, 4 }));
}
