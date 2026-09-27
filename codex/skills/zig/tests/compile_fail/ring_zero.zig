// EXPECT: RingBuffer capacity must be nonzero
const patterns = @import("comptime_patterns.zig");
comptime {
    _ = patterns.RingBuffer(u8, 0);
}
