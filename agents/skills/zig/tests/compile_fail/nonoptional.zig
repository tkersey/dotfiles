// EXPECT: OptionalPayload(u8): expected optional type
const patterns = @import("comptime_patterns.zig");
comptime {
    _ = patterns.OptionalPayload(u8);
}
