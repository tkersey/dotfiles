#!/usr/bin/env sh
set -eu

# Read-only candidate locator. Matches include valid code; review in context.
# Run at the relevant project root. No matches is success; rg errors propagate.
pattern='@bitCast|@hasDecl|@intFromEnum|@enumFromInt|@cImport|@cInclude|@cDefine|@cUndef|@Type\(|std\.builtin|StructField|UnionField|\.fields|\.is_comptime|\.field_attrs|OptimizeMode|Release(Safe|Fast|Small)|\.Debug|runtime_safety|builtin\.(cpu|os|abi|object_format)|DebugAllocator|heap\.Check|stackFallback|StackFallbackAllocator|fmt\.allocPrint|zon\.(parse|from|update)|bit_set|DynamicBitSet|StaticBitSet|errdefer[[:space:]]*\||void[[:space:]]*\{|\*\*|\bi0\b|link_once|addTranslateC|findProgram|build_root|b\.args|addPrefixed|addArtifactArg|addFileArg|addOutputFileArg|addOptionPath|build.runner|cache.poison|ZIG_LOCAL_PKG_DIR|pkg.path'
if rg -n --glob '*.zig' --glob '*.zon' \
    --glob '!**/.zig-cache/**' --glob '!**/zig-cache/**' \
    --glob '!**/zig-out/**' --glob '!**/zig-pkg/**' \
    --glob '!**/vendor/**' --glob '!**/node_modules/**' \
    -- "$pattern" .; then
    exit 0
else
    status=$?
    [ "$status" -eq 1 ] && exit 0
    exit "$status"
fi
