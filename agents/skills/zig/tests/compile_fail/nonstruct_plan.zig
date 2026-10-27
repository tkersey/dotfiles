// EXPECT: StructPlan(usize): expected struct
const patterns = @import("comptime_patterns.zig");
comptime {
    _ = patterns.StructPlan(usize);
}
