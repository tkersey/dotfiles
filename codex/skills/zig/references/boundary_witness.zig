//! Boundary-witness example: scan -> validate -> project.
//! Adapt to the target parser/protocol, then validate with Zig 0.16.x.

const std = @import("std");

pub const ValidatedFrame = struct {
    bytes: []const u8,

    pub fn parse(input: []const u8) !ValidatedFrame {
        if (input.len < 2) return error.TooShort;

        const payload_len: usize = (@as(usize, input[0]) << 8) | @as(usize, input[1]);
        if (input.len != payload_len + 2) return error.LengthMismatch;

        return .{ .bytes = input };
    }

    pub fn payload(self: ValidatedFrame) []const u8 {
        return self.bytes[2..];
    }
};

test "validated frame witness" {
    const frame = try ValidatedFrame.parse(&.{ 0, 3, 'z', 'i', 'g' });
    try std.testing.expectEqualSlices(u8, "zig", frame.payload());
    try std.testing.expectError(error.TooShort, ValidatedFrame.parse(&.{1}));
    try std.testing.expectError(error.LengthMismatch, ValidatedFrame.parse(&.{ 0, 4, 'z', 'i', 'g' }));
}
