const std = @import("std");

pub const OwnedOrBorrowed = union(enum) {
    borrowed: []const u8,
    owned: []u8,

    pub fn slice(self: OwnedOrBorrowed) []const u8 {
        return switch (self) {
            .borrowed => |bytes| bytes,
            .owned => |bytes| bytes,
        };
    }
};

pub const ValidatedMessage = struct {
    raw: []const u8,

    pub fn payload(self: ValidatedMessage) []const u8 {
        const len = @as(usize, self.raw[0]);
        return self.raw[1 .. 1 + len];
    }
};

pub fn validateMessage(raw: []const u8) !ValidatedMessage {
    if (raw.len == 0) return error.ShortMessage;

    const len = @as(usize, raw[0]);
    if (raw.len != len + 1) return error.LengthMismatch;

    return .{ .raw = raw };
}

test "validated message gates projection" {
    const raw = [_]u8{ 3, 'z', 'i', 'g' };
    const msg = try validateMessage(&raw);

    try std.testing.expectEqualStrings("zig", msg.payload());
}

test "owned or borrowed keeps ownership explicit" {
    var owned = [_]u8{ 'o', 'k' };
    const borrowed = OwnedOrBorrowed{ .borrowed = "zig" };
    const promoted = OwnedOrBorrowed{ .owned = owned[0..] };

    try std.testing.expectEqualStrings("zig", borrowed.slice());
    try std.testing.expectEqualStrings("ok", promoted.slice());
}
