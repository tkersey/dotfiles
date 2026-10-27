#!/usr/bin/env sh
set -eu

# Audit Zig low-level systems hazards. Run from repository root.
rg -n \
'Allocator|std\.mem\.Allocator|alloc\(|create\(|dupe\(|free\(|destroy\(|defer|errdefer|ArenaAllocator|FixedBufferAllocator|FailingAllocator|checkAllAllocationFailures|\[\*c\]|\[\*\]|\[:|\[\*:|@ptrCast|@ptrFromInt|@intFromPtr|@alignCast|@constCast|@volatileCast|allowzero|volatile|extern struct|extern union|extern fn|packed struct|packed union|@sizeOf|@alignOf|@offsetOf|@bitOffsetOf|@bitSizeOf|readInt|writeInt|std\.Io|process\.Init|process\.args|process\.getEnv|currentPath|std\.atomic|atomic\.Value|@atomicLoad|@atomicStore|@atomicRmw|@cmpxchg|Thread|Mutex|RwLock|Semaphore|futex|error\{|anyerror|catch unreachable|catch \{|try |unreachable|panic|@setRuntimeSafety|@cImport|addTranslateC|zig-pkg|--fork|ReleaseSafe|ReleaseFast|ReleaseSmall' \
. -g'*.zig' -g'build.zig' -g'build.zig.zon' \
  -g'!zig-pkg/**' -g'!.zig-cache/**' -g'!zig-out/**'
