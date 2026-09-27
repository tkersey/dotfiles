// EXPECT: valueKind: unsupported value type [1]u8
const patterns = @import("comptime_patterns.zig");
comptime {
    _ = patterns.valueKind([_]u8{1});
}
