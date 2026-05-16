#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"

if [[ ! -d "$root" ]]; then
  echo "usage: $0 [project-root]" >&2
  exit 2
fi

pattern='@setRuntimeSafety\((false|true)\)|unreachable|catch unreachable|\.\?|undefined|@ptrCast|@alignCast|@addrSpaceCast|@constCast|@volatileCast|@ptrFromInt|@intFromPtr|@fieldParentPtr|@bitCast|@memcpy|@memmove|@memset|\[\*c\]|\[\*\]|allowzero|sentinel|extern ("[^"]+" )?fn|pub extern|export fn|@extern|@export|@cImport|@cVa(Start|Arg|Copy|End)|asm( volatile)?|volatile|packed (struct|union)|extern (struct|union|enum)|@offsetOf|@bitOffsetOf|@bitSizeOf|@sizeOf|@alignOf|@atomicLoad|@atomicStore|@atomicRmw|@cmpxchg(Weak|Strong)|std\.atomic|Atomic|std\.Thread|Thread\.Mutex|Thread\.Condition|Thread\.ResetEvent|@Vector|@shuffle|@select|@reduce|@prefetch|Allocator|std\.heap|arena|deinit\(|errdefer|@panic|@trap'

rg -n --hidden --color never "$pattern" "$root" \
  -g'*.zig' -g'build.zig' \
  -g'!zig-pkg/**' -g'!.zig-cache/**' -g'!zig-out/**'
