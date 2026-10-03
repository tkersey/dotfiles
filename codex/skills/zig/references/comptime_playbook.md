# Zig comptime: representation, staging and derivation

Use for generic APIs, type factories, reflection, generated types, parsers,
serializer/schema derivation, diagnostics, layout checks and specialization.
Consult only the sections that inform the live decision. Bundled examples target
0.17.0; the repository's selected compiler and matching stdlib are authoritative.

## Construct the right representation

Start from desired behavior and laws, not the assumption that more comptime is
better. Compare representations when the choice is consequential:

| Representation | Useful when | Cost or risk |
| --- | --- | --- |
| Ordinary runtime values | Types/shape are fixed and data varies | Branching or lookup, often simplest. |
| Tagged union / checked witness | Alternatives or established invariants should be explicit | Tag/layout cost; lifetime/authority must hold. |
| Generated type | Callers need a genuinely computed static shape | Diagnostics, instantiation count, compile-time complexity. |
| Comptime-derived plan/table | Static structure can feed a shared runtime engine | Plan storage and indirect work versus code-size savings. |
| Runtime interface | Implementations vary without requiring value specialization | Dispatch and explicit ownership/effects. |

Ask which information must remain static to preserve laws and which can become
ordinary data. A strong interface can lower to a simple native representation.
Avoid type generation or universal reflection infrastructure when a struct, union,
function or table is sufficient. Preserve accepted architecture absent new evidence.

## Staging contract

For consequential comptime work, understand compile-time inputs, runtime inputs,
the generated/specialized artifact, remaining runtime work, intentionally rejected
shapes, and compile-time/binary-size cost. Explain decisions that matter; do not
produce a mandatory contract packet for every generic helper.

Comptime is semantic-analysis-time execution and partial evaluation, not a macro
system or blanket optimization switch. Use it for types, field/declaration names,
schema validation and generated plans, or when measurements justify specialization.
Avoid high-cardinality runtime-like comptime parameters, near-duplicate
instantiations and unmeasured forced unrolling.

## Type factories and polymorphism

Use `fn Container(comptime T: type, comptime capacity: usize) type` when type and
capacity are the subject. Reject nonsensical inputs intentionally, use `@This()`
for the returned type, and exercise materially different instantiations. See
[comptime_patterns.zig](comptime_patterns.zig).

Prefer explicit `comptime T: type` when callers deliberately select the type,
such as `decode(T, input)`. Use `anytype` for value-level convenience, tuples,
writer-like objects or scalar polymorphism. At a public generic boundary, make the
implicit contract understandable and diagnose misleading failures. Small internal
helpers do not automatically require a shape validator or diagnostic framework.
A writer-like helper can simply require `writeAll([]const u8) !void`; add adapters
when different dialects create a real boundary, not merely because `anytype` exists.

## Reflection architecture

For recurring derivation, a useful shape is:

```text
classifyType(T) -> descriptor
validateType(T, options) -> intentional rejection of unsupported shapes
derivePlan(T, options) -> static metadata or behavior
runtimeEncode(plan, writer, value) -> required runtime work
```

Centralize shared field/layout/policy semantics when it removes real duplication;
do not impose this architecture on a tiny derivation. Check kind and policy before
looking up declarations/fields, then types and relevant ABI/layout, then derive.
Do not call `@FieldType` before establishing the field exists. Names passed to
`@field` must be comptime-known.

0.17 struct/union metadata is struct-of-arrays. Iterate parallel arrays together,
not obsolete `.fields` records; consume only the columns needed by the operation:

```zig
const info = @typeInfo(T).@"struct";
inline for (info.field_names, info.field_types, info.field_attrs) |name, Field, attrs| {
    if (attrs.is_comptime) continue; // Policy choice, not universal reflection semantics.
    try visit(Field, @field(value, name));
}
```

Keep field order, defaults, alignment and comptime-field policy paired correctly.
A name-only plan can read `field_names` without reconstructing rich descriptors.
This avoids unnecessary source-level work; it is not a measured compiler speedup.
Do not build a multi-version shim when only one compiler version is supported.

```zig
fn hasDeclSafe(comptime T: type, comptime name: []const u8) bool {
    return switch (@typeInfo(T)) {
        .@"struct", .@"union", .@"enum", .@"opaque" => @hasDecl(T, name),
        else => false,
    };
}
```

In 0.17 this discovers **public declarations only**, even in the defining file.
A private custom codec or validation hook may silently stop being selected.
Test the selected hook's behavior, not just successful fallback compilation;
make discoverable hooks public or pass them explicitly according to the API.
Do not use `@hasDecl` as a field-existence test.

Preserve supported schema policies (rename, skip, flatten, tags, defaults, custom
codecs, borrowed/owned data) before fallback derivation. Do not hide allocator,
lifetime, error, effect or ABI behavior in generated code. A context object alone
does not prove that every borrowed field outlives the operation.

## Generated types

Use the dedicated builtins rather than removed `@Type` recipes:

| Construct | 0.17 form |
| --- | --- |
| Enum-literal type | `@EnumLiteral()` |
| Integer | `@Int(.signed/.unsigned, bits)` |
| Tuple | `@Tuple(&.{ T0, T1 })` |
| Pointer | `@Pointer(size, attrs, Element, sentinel)` |
| Function | `@Fn(param_types, param_attrs, ReturnType, attrs)` |
| Struct | `@Struct(layout, BackingInt, field_names, field_types, field_attrs)` |
| Union | `@Union(layout, ArgType, field_names, field_types, field_attrs)` |
| Enum | `@Enum(TagInt, mode, field_names, field_values)` |
| SPIR-V resource type | `@SpirvType(options)`, only for the supported SPIR-V target |

Metadata lives under `std.lang.Type`. Struct and union constructor attributes are
`Type.Struct.FieldAttributes` and `Type.Union.FieldAttributes`; do not retain
`std.builtin.Type.StructField.Attributes`. Constructor slices/arrays must have
matching lengths and compatible types. Prefer ordinary `[len]T`, `[len:sentinel]T`,
`?T`, `E!T`, `opaque {}` and `error{...}` syntax when sufficient.

Use `@Int`/`@Tuple` rather than legacy `std.meta.Int`/`Tuple` recipes. Inspect
actual signatures instead of assuming every replacement preserves old metadata.
`i0` is removed; do not "repair" an uninhabited enum by assigning it an inhabited
backing type. Type construction must preserve the intended inhabitants.

Use `@sizeOf`, `@alignOf`, `@bitSizeOf`, `@offsetOf` and field/tag types for
relevant layout assertions; native layout does not establish wire stability.
[partial_type.zig](partial_type.zig) demonstrates generated optional runtime
fields and defaults; [type_switch.zig](type_switch.zig) exercises type dispatch.

## Inline loops, dispatch and dual paths

Use `inline for`/`inline while` when iteration values must remain comptime-known
for types, fields or semantic construction. Performance-only unrolling needs
measurements. Prefer exhaustive `switch` with `inline else` for tagged-union
payload dispatch when it avoids a manual loop plus `unreachable`:

```zig
fn payloadLen(value: anytype) usize {
    return switch (value) {
        inline else => |payload| payload.len,
    };
}
```

Use `@inComptime()` for a legitimate comptime-friendly alternative, not to hide
an unsupported function. Keep safe/reference paths for low-level differential
checks. Explicit array coercion can support vector-element iteration where needed;
keep logical bit casts separate from target memory representation.

## Parsers, derived plans and diagnostics

For a static format/schema, validate grammar once, produce a compact plan and
keep runtime work explicit. Intentional rejection should identify the API,
offending type/value or input position, expected shape and useful recovery.
Remove `@compileLog` before claiming a normal successful build.

Do not require extensibility just to provide an escape hatch. Mention hooks only
when they exist in the supported API. Force diagnostic analysis rather than
leaving a lazy unused constant. The [runner](../tests/check_zig_examples.py) checks
positive files and separate compile-fail fixtures; unrelated errors are not passes.

## Cost and scaling experiments

Count type/policy/value instantiations, repeated reflection/parsing, plan storage,
branch-quota use, generated code and build/link cost. Do not raise
`@setEvalBranchQuota` without understanding a bounded workload. Hoist reusable
plans only where semantics match. Textual duplication does not establish repeated
compiler execution, and a cached declaration does not establish a measured win.

[comptime_scaling.zig](comptime_scaling.zig) compares direct reflection/unrolling,
a comptime plan feeding a runtime loop, and a runtime table. It uses runtime-input
kernels and an independent formula in its tests. The optional driver builds
exported kernels at several sizes:

```bash
uv run python3 "$zig_skill_root/tests/measure_comptime.py" --zig zig --sizes 8 32 128
```

Compare compiler version, target/CPU/mode and cache state. The driver records cold
direct compile wall time and object bytes, not peak memory, application runtime,
configure-cache performance or incremental-rebuild latency. Supply `--cpu` for
controlled cross-machine comparisons. For other metrics use an appropriate
profiler/harness with external input, warmup, repeated samples and a checksum.
Inspect emitted code: optimizers may make variants equivalent. Include variance
and confounders; never infer runtime gains from build time or object size alone.

## Coverage and migration

Exercise valid simple types, actual policies/hooks, runtime behavior, float/empty/
nested branches and relevant modes. Negative cases include invalid shape,
unsupported fields, missing required hooks, invalid policies and ABI assumptions.
A successful file does not instantiate every possible generic body.

Use the comptime locator for broad staging questions and the
[0.17 locator](../scripts/zig_0_17_audit_rg.sh) for migration candidates. Neither
proves completeness. Exclude dependencies/caches/outputs appropriately. Primary
references: [0.17 language reference](https://ziglang.org/documentation/0.17.0/)
and [0.17 migration map](zig_0_17_migration.md).
