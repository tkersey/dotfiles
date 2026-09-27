# Zig comptime: representation, staging and derivation

Use for generic APIs, type factories, reflection, generated types, parsers,
serializer/schema derivation, diagnostics, layout checks and specialization.
Consult only the sections that inform the live decision. Examples target Zig
0.16.0; the repository's actual toolchain and installed stdlib remain authoritative.

## Construct the right representation

Start from the desired behavior and laws, not from the assumption that more
comptime is better. Compare representations when the choice is consequential:

| Representation | Useful when | Cost or risk |
| --- | --- | --- |
| Ordinary runtime values | Types/shape are already fixed and data varies | Runtime branching or lookup, often simplest. |
| Tagged union / checked witness | Alternatives or established invariants should be explicit | Tag/layout cost; witness lifetime/authority must hold. |
| Generated type | Callers need a genuinely computed static shape | Diagnostics, instantiation count, compile-time complexity. |
| Comptime-derived plan/table | Static structure can feed a shared runtime engine | Plan size and indirect work versus code-size savings. |
| Runtime interface | Implementations vary without needing value specialization | Dispatch cost and explicit ownership/effects. |

Ask which information must remain static to preserve the laws and which can become
ordinary data. A strong interface may lower to a simple native representation.
Avoid type generation or a universal reflection framework when a struct, union,
function, or table is sufficient. Preserve accepted architecture absent new evidence.

## Staging contract

For consequential comptime work, understand compile-time inputs, runtime inputs,
the generated/specialized artifact, remaining runtime work, intentionally rejected
shapes, and compile-time/binary-size cost. Explain decisions that matter; do not
produce a mandatory contract packet for every generic helper.

Comptime is semantic-analysis-time execution and partial evaluation, not a macro
system or a blanket optimization switch. Use it when types, field/declaration
names, schema validation, or generated plans require it, or when measurements
justify specialization. Avoid high-cardinality runtime-like comptime parameters,
near-duplicate instantiations, and unmeasured forced unrolling.

## Type factories and polymorphism

Use `fn Container(comptime T: type, comptime capacity: usize) type` when type and
capacity are the subject. Reject nonsensical parameters intentionally, use
`@This()` for the returned type, and exercise materially different instantiations.
See [comptime_patterns.zig](comptime_patterns.zig) for executable examples.

Prefer explicit `comptime T: type` when callers deliberately select the type, such
as `decode(T, input)`. Use `anytype` when value-level convenience, tuples, writer-like
objects, or scalar polymorphism are the API. At a public generic boundary, make
its implicit contract understandable and provide helpful diagnostics where default
errors are misleading. Small internal helpers do not automatically need a bespoke
shape validator, diagnostic framework, or an explanation of why explicit T is worse.

For example, a writer-like helper may simply require `writeAll([]const u8) !void`.
Use adapters/validation when supporting different dialects creates a real boundary,
not merely because the code contains `anytype`.

## Reflection architecture

For recurring derivation, prefer a coherent choke point:

```text
classifyType(T) -> descriptor
validateType(T, options) -> intentional rejection of unsupported shapes
derivePlan(T, options) -> static metadata or behavior
runtimeEncode(plan, writer, value) -> required runtime work
```

Centralize shared field/layout/policy semantics when this removes real duplication;
do not impose a multi-stage framework on a tiny derivation. Check kind and policy
before looking up declarations/fields, then field types and relevant ABI/layout,
then derive. Do not call `@FieldType` before establishing the field exists.
Field names used by `@field` must be known at compile time.

```zig
fn hasDeclSafe(comptime T: type, comptime name: []const u8) bool {
    return switch (@typeInfo(T)) {
        .@"struct", .@"union", .@"enum", .@"opaque" => @hasDecl(T, name),
        else => false,
    };
}
```

For schema/serializer APIs, preserve explicit custom hooks and field policy before
fallback derivation. Relevant policies include rename, skip, flatten, tags,
defaults, custom codecs and borrowed/owned data. Do not hide allocator, lifetime,
error, effect or ABI behavior inside generated code. A context object is not proof
that every borrowed field outlives the generated operation.

## Zig 0.16 generated types

Use dedicated type-creating builtins rather than removed `@Type` recipes:

| Construct | Zig 0.16 form |
| --- | --- |
| Enum-literal type | `@EnumLiteral()` |
| Integer | `@Int(.signed/.unsigned, bits)` |
| Tuple | `@Tuple(&.{ T0, T1 })` |
| Pointer | `@Pointer(size, attrs, Element, sentinel)` |
| Function | `@Fn(param_types, param_attrs, ReturnType, attrs)` |
| Struct | `@Struct(layout, BackingInt, field_names, field_types, field_attrs)` |
| Union | `@Union(layout, ArgType, field_names, field_types, field_attrs)` |
| Enum | `@Enum(TagInt, mode, field_names, field_values)` |

Prefer ordinary `[len]T`, `[len:sentinel]T`, `?T`, `E!T`, `opaque {}` and
`error{...}` syntax where sufficient. Migrate deprecated `std.meta.Int`/`Tuple`
helpers toward `@Int`/`@Tuple`; do not call a deprecated helper removed merely
because its replacement is preferred. Audit old reified error sets and tuple
comptime-field metadata against the exact release. Inspect actual builtin
signatures rather than mechanically adapting another version's snippet.

Use `@sizeOf`, `@alignOf`, `@bitSizeOf`, `@offsetOf`, and relevant field/tag types
for target-sensitive layout assertions; do not infer wire-format stability from
a native struct layout. [partial_type.zig](partial_type.zig) demonstrates computed
optional fields; [type_switch.zig](type_switch.zig) demonstrates type dispatch.

## Inline loops, dispatch and dual paths

Use `inline for`/`inline while` when an iteration value must remain comptime-known
for types, fields or semantic construction. Performance-only forced unrolling
needs measurements. Prefer an exhaustive `switch` with `inline else` for tagged
union payload dispatch when it avoids a manual loop plus `unreachable`.

```zig
fn payloadLen(value: anytype) usize {
    return switch (value) {
        inline else => |payload| payload.len,
    };
}
```

Use `@inComptime()` for a legitimate comptime-friendly alternative, not to hide an
unsupported function. Keep safe/reference paths when a low-level optimization
requires differential checks. Runtime vector indexing can use an explicit array
coercion where required by the target version.

## Parsers, derived plans and diagnostics

For a static format/schema, validate the grammar once, produce a compact plan,
and keep runtime work explicit. Reject invalid input with the API name, offending
type/value or input position, expected shape, and useful recovery advice. Remove
`@compileLog` before claiming a normal successful build.

Do not require extensibility mechanisms merely to provide an "escape hatch";
mention a hook or policy only when it exists and is part of the supported API.
Test the intended diagnostic through forced analysis, not a lazy unused constant.
The [example runner](../tests/check_zig_examples.py) includes positive controls and
separate compile-fail fixtures. An unrelated compiler/import error is not a pass.

## Cost and scaling experiments

Count type/policy/value instantiations, repeated reflection/parsing, plan storage,
branch-quota use, generated code and build/link cost. Avoid raising
`@setEvalBranchQuota` without understanding a bounded workload. Hoist reusable
plans when they share semantics; do not assume textual duplication means repeated
compiler execution, or that a cached declaration implies a measured speedup.

[comptime_scaling.zig](comptime_scaling.zig) is a worked comparison of direct
reflection/unrolling, a comptime plan feeding a runtime loop, and a runtime table.
It exposes a runtime-input kernel so compilation cannot replace the workload with
a known constant result. Its tests compare the variants with an independent formula.
The optional measurement driver builds exported kernels at several shape sizes:

```bash
uv run python3 "$zig_skill_root/tests/measure_comptime.py" --zig zig --sizes 8 32 128
```

Compare compile wall time and artifact bytes under identical version/target/mode
and declared cache state. The driver records those metrics, not compiler peak
memory or runtime latency. For those questions, add a platform profiler and a
runtime harness with externally supplied data, warmup, samples and an observable
checksum. Inspect emitted code: the optimizer may make variants equivalent.
Do not infer a runtime win from build time or object size. Report unmeasured metrics
as unavailable, and include variance/confounders in any claimed improvement.

## Coverage and migration

Exercise valid simple types, policy/hook paths that exist, runtime behavior,
float/empty/nested branches and applicable modes. Negative cases include invalid
shape, unsupported field, missing required hook, bad policy/value, obsolete
constructs and invalid ABI assumptions. A successful test file does not instantiate
all possible generic bodies. Record actual coverage rather than claiming completeness.

For migration, the bundled comptime scan is a locator for `@Type`, `std.meta.Int`,
`std.meta.Tuple`, constructor builtins, `.is_comptime`, `@compileLog` and branch
quotas. Review each hit in context, excluding dependency/cache/output trees where
appropriate. References: [0.16 language reference](https://ziglang.org/documentation/0.16.0/)
and [0.16 release notes](https://ziglang.org/download/0.16.0/release-notes.html).
