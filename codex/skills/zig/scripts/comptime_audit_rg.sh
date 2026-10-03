#!/usr/bin/env sh
set -eu

# Comptime/metaprogramming candidate locator; review matches in context.
# Run at a Zig project root. Use zig_0_17_audit_rg.sh for release migration.

rg -n \
  "comptime|anytype|@typeInfo|@TypeOf|@FieldType|@hasDecl|@hasField|@field|@compileError|@compileLog|@setEvalBranchQuota|@inComptime|inline (for|while|else)|@Struct|@Union|@Enum|@Tuple|@Pointer|@Fn|@Int|@EnumLiteral|@Type\(|std\.meta\.(Int|Tuple)|\.is_comptime|field_names|field_types|field_attrs|StructField|FieldAttributes|struct \{ comptime" \
  . \
  -g"*.zig" -g"build.zig" \
  -g"!zig-pkg/**" -g"!.zig-cache/**" -g"!zig-out/**"
