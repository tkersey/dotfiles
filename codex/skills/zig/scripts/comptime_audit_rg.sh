#!/usr/bin/env sh
set -eu

# Comptime/metaprogramming audit for Zig 0.16.x migration and review.
# Run at a Zig project root.

rg -n \
  "comptime|anytype|@typeInfo|@TypeOf|@FieldType|@hasDecl|@hasField|@field|@compileError|@compileLog|@setEvalBranchQuota|@inComptime|inline (for|while|else)|@Struct|@Union|@Enum|@Tuple|@Pointer|@Fn|@Int|@EnumLiteral|@Type\(|std\.meta\.(Int|Tuple)|\.is_comptime|struct \{ comptime" \
  . \
  -g"*.zig" -g"build.zig" \
  -g"!zig-pkg/**" -g"!.zig-cache/**" -g"!zig-out/**"
