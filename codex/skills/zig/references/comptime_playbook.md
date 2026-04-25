# Zig comptime expert playbook

This playbook is for implementation, review, and migration of comptime-heavy Zig 0.16.0 code. Use it for generic APIs, type factories, reflection, generated types, compile-time parsers, schema/serializer derivation, ABI/layout assertions, and deliberate specialization.

## 1. Operating principle

For comptime-heavy code, do not merely produce code. Produce the comptime contract:

1. **Comptime inputs:** which types, values, options, strings, or declarations must be known at compile time.
2. **Runtime inputs:** which values remain runtime values.
3. **Generated/specialized artifact:** type, function path, parser plan, metadata table, ABI witness, or validation policy.
4. **Runtime path:** what code remains after comptime specialization.
5. **Invalid shapes:** what fails via intentional `@compileError`.
6. **Cost:** specialization count, compile-time work, binary-size risk, and branch-quota risk.
7. **Proof:** positive tests, negative compile-fail fixtures, and benchmark evidence when speed is claimed.

## 2. Mental model

Zig comptime is semantic-analysis-time execution and partial evaluation. It is used for generics, type factories, reflection-driven derivation, table generation, compile-time parsers, layout checks, and controlled specialization. It is not a macro system and not a blanket optimization knob.

Use comptime when it is semantically required:

- a type must be constructed or selected;
- a field/declaration name must be known;
- a format/schema/table must be validated before runtime;
- invalid shapes should be rejected during compilation;
- the caller's type should drive generated behavior;
- a measured benchmark proves specialization or unrolling is worth the cost.

Avoid comptime when:

- a runtime table is simpler and performance is unproven;
- the comptime parameter has many possible runtime-like values;
- specialization creates many near-identical functions;
- the API can be expressed with a normal runtime parameter;
- the only motivation is “maybe faster”;
- it obscures ownership, lifetime, allocator, error, or ABI behavior;
- the diagnostics become worse than explicit code.

## 3. Decision tree

| Problem | Use | Avoid |
| --- | --- | --- |
| Generic container | `fn Container(comptime T: type, comptime capacity: usize) type` | `anytype` where the API subject is the type |
| Generic function | `comptime T: type` plus typed value | repeated `@TypeOf(value)` when the caller should choose `T` |
| Polymorphic value syntax | `anytype` with explicit shape validation | assuming operations exist and letting compiler internals produce the error |
| Schema/serializer derivation | `validateType -> derivePlan -> runtime encode/decode` | scattered `@typeInfo` switches |
| Format string/parser | comptime parser plus runtime emission | reparsing at runtime or emitting cryptic compile errors |
| ABI/layout proof | `@sizeOf`, `@alignOf`, `@bitSizeOf`, `@offsetOf`, `@FieldType` | layout assumptions with no target-sensitive check |
| Generated type | Zig 0.16 builtins such as `@Struct`/`@Enum`/`@Int` | removed `@Type` patterns |
| Dispatch over union/enum | `inline else` when exhaustiveness matters | `inline for` with manual `unreachable` unless necessary |
| Runtime/comptime dual path | `@inComptime()` for a comptime-friendly fallback | using it to hide a function from comptime evaluation |

## 4. Type factories

Canonical pattern:

```zig
fn RingBuffer(comptime T: type, comptime capacity: usize) type {
    if (capacity == 0) @compileError("RingBuffer capacity must be nonzero");

    return struct {
        const Self = @This();

        items: [capacity]T = undefined,
        head: usize = 0,
        len: usize = 0,

        pub fn push(self: *Self, value: T) void {
            self.items[(self.head + self.len) % capacity] = value;
            if (self.len < capacity) {
                self.len += 1;
            } else {
                self.head = (self.head + 1) % capacity;
            }
        }
    };
}
```

Review checklist:

- Reject nonsensical compile-time values early.
- Keep generated type state simple and visible.
- Use `@This()` inside returned anonymous structs.
- Prefer naming the generated type at the call site, for example `const U8Ring = RingBuffer(u8, 256);`.
- Test at least two instantiations if the implementation depends on size/type behavior.

## 5. `comptime T: type` vs `anytype`

Prefer `comptime T: type` when the type is the API subject:

```zig
fn decode(comptime T: type, input: []const u8) !T {
    validateDecodable(T);
    return decodeValue(T, input);
}
```

Use `anytype` when the value-level syntax is the API, such as print-style argument tuples, writer-like objects, scalar polymorphism, or call-site convenience. Even then, document the implicit typeclass.

When reviewing `anytype`, require:

- the hidden contract in prose;
- validation using `@TypeOf(value)` or `@typeInfo`;
- a custom `@compileError` for unsupported shapes;
- valid and invalid tests;
- an explanation of why explicit `T` is worse.

Bad:

```zig
fn writeAll(writer: anytype, bytes: []const u8) !void {
    try writer.writeAll(bytes);
}
```

Better as a public API note:

```zig
// Requires writer to expose `writeAll([]const u8) !void`.
// If the API should support multiple writer dialects, add a validation layer
// or adapter rather than letting arbitrary method lookup be the only contract.
```

## 6. Reflection architecture

For derivation APIs, use one reflection choke point:

```text
classifyType(T) -> Kind or descriptor
validateType(T, Options) -> @compileError for invalid shapes
derivePlan(T, Options) -> comptime plan/table
runtimeEncode(plan, writer, value) -> runtime work only
```

Do not duplicate raw `@typeInfo` switches in each runtime function. Centralize:

- layout checks;
- field iteration;
- hook detection;
- field policy application;
- naming transforms;
- default/skip/flatten/rename/tag handling;
- ABI and ownership rules.

Safe helpers:

```zig
fn hasDeclSafe(comptime T: type, comptime name: []const u8) bool {
    return switch (@typeInfo(T)) {
        .@"struct", .@"union", .@"enum", .@"opaque" => @hasDecl(T, name),
        else => false,
    };
}

fn hasFieldSafe(comptime T: type, comptime name: []const u8) bool {
    return switch (@typeInfo(T)) {
        .@"struct", .@"union", .@"enum" => @hasField(T, name),
        else => false,
    };
}
```

## 7. Reflection validation order

Use this order:

1. **Kind check:** is `T` a struct, union, enum, pointer, slice, optional, etc.?
2. **Policy check:** do options allow this kind?
3. **Field/declaration check:** does the required field or hook exist?
4. **Field type check:** is each field type supported?
5. **Layout/ABI check:** if raw layout matters, verify size, alignment, tag/backing type, and offsets.
6. **Derive plan:** produce the table used by runtime code.

Do not call `@FieldType(T, field)` until field existence and shape have been established. Do not use `@field(value, name)` in a runtime path unless `name` is comptime-known by design.

## 8. Custom hooks before auto-derived fallback

For serializer/schema/CLI/ORM-like APIs, prefer:

1. explicit custom hook;
2. explicit policy/options;
3. auto-derived behavior;
4. intentional `@compileError`.

Example policy surface:

```text
Options
- rename: function or map
- skip: field list or predicate
- flatten: field list
- tag: enum/union tag policy
- default: default-provider policy
- with: custom field codec
- ownership: borrowed/owned policy for pointer-like fields
```

This keeps comptime derivation flexible without encoding hidden conventions.

## 9. Generated types in Zig 0.16.0

Zig 0.16.0 replaced `@Type` with individual type-creating builtins. Use:

- `@EnumLiteral()` for uncoerced enum literal type;
- `@Int(.signed/.unsigned, bits)` for integer types;
- `@Tuple(&.{ T0, T1, ... })` for tuples;
- `@Pointer(size, attrs, Element, sentinel)` for pointer types;
- `@Fn(param_types, param_attrs, ReturnType, attrs)` for function types;
- `@Struct(layout, BackingInt, field_names, field_types, field_attrs)` for struct types;
- `@Union(layout, ArgType, field_names, field_types, field_attrs)` for union types;
- `@Enum(TagInt, mode, field_names, field_values)` for enum types.

Migration table:

| Old | New |
| --- | --- |
| `@Type(.{ .int = ... })` | `@Int` |
| `std.meta.Int` | `@Int` |
| `std.meta.Tuple` | `@Tuple` |
| `@Type(.{ .pointer = ... })` | `@Pointer` |
| `@Type(.{ .@"fn" = ... })` | `@Fn` |
| `@Type(.{ .@"struct" = ... })` | `@Struct` |
| `@Type(.{ .@"union" = ... })` | `@Union` |
| `@Type(.{ .@"enum" = ... })` | `@Enum` |
| `@Type(.enum_literal)` | `@EnumLiteral()` |
| Reified error sets | explicit `error{...}` declarations |

Prefer ordinary syntax where the language offers it:

```zig
[len]T          // array
[len:sentinel]T // sentinel array
?T              // optional
E!T             // error union
opaque {}       // opaque
error{A, B}     // explicit error set
```

Generated types should be a last resort for genuinely dynamic compile-time shape construction.

## 10. `inline for`, `inline while`, and `inline else`

Use inline loops only when the loop variable must be comptime-known or when a benchmark proves forced unrolling helps.

Semantic uses:

- iterate over reflected fields;
- use an iteration value as a type;
- use a field/declaration name in `@field`/`@FieldType`;
- build a table during analysis;
- implement a compile-time parser.

Performance-only uses require benchmark evidence.

Prefer `inline else` for tagged-union dispatch when possible:

```zig
fn payloadLen(any: anytype) usize {
    return switch (any) {
        inline else => |payload| payload.len,
    };
}
```

This usually produces clearer exhaustiveness behavior than an `inline for` over enum fields plus manual `unreachable`.

## 11. Compile-time parsers and tables

For format strings, schemas, mini-grammars, generated lookup tables, and binary layouts:

- parse/validate once at comptime;
- reject invalid grammar with contextual `@compileError`;
- produce a compact plan/table;
- keep runtime code as data movement or straightforward dispatch;
- include malformed-input compile-fail fixtures.

A good compile-time parser diagnostic includes:

- API name;
- input snippet or index;
- expected grammar element;
- recovery advice.

## 12. Diagnostics discipline

Comptime diagnostics are part of the public API.

Bad:

```zig
@compileError("unsupported type");
```

Good:

```zig
@compileError(
    "deriveJson(" ++ @typeName(T) ++ "): expected struct; " ++
    "define pub fn jsonSerialize or pass Options.custom_serialize"
);
```

Rubric:

| Property | Requirement |
| --- | --- |
| API name | name the rejecting function/type |
| Offending type/value | include `@typeName(T)` or the comptime value |
| Shape | say what was expected and what failed |
| Escape hatch | custom hook, explicit option, wrapper type, or explicit field policy |
| Noise control | avoid raw `std.builtin.Type` dumps unless debugging |

`@compileLog` is for active debugging. Leaving it in committed code intentionally causes compilation failure, so remove it before claiming proof.

## 13. Compile-time cost governance

Ask:

- How many `T` instantiations exist?
- Are policy values high-cardinality?
- Is a long string parsed for every call site?
- Is field reflection repeated in many functions?
- Can a derived plan be cached in a type-level declaration?
- Does the code raise `@setEvalBranchQuota`?
- Did binary size or compile time change?
- Was the code checked in Debug and at least one Release mode?

Use `@setEvalBranchQuota` only when the comptime workload is intentional, bounded, and documented. The default branch limit exists to catch runaway or unexpectedly expensive comptime execution.

## 14. Positive and negative tests

Positive tests:

- one simple valid type;
- one type using a custom hook;
- one type exercising field policies;
- one runtime behavior check against the derived plan;
- one alternate optimization mode when layout or optimizer behavior matters.

Negative tests:

- invalid type shape;
- unsupported field type;
- missing required hook;
- bad field policy;
- stale 0.15-era generated-type construct;
- bad ABI/layout assumption.

Compile-fail fixtures can be separate small files invoked by the build system. When compile-fail infrastructure is absent, provide the fixture text and report `COMPTIME_PROOF_UNAVAILABLE`.

## 15. Migration audit for Zig 0.16.0

Scan for:

```bash
rg -n "@Type\(|std\.meta\.(Int|Tuple)|@EnumLiteral|@Int|@Tuple|@Pointer|@Fn|@Struct|@Union|@Enum|\.is_comptime|struct \{ comptime|@compileLog|@setEvalBranchQuota" . \
  -g"*.zig" -g"build.zig" \
  -g"!zig-pkg/**" -g"!.zig-cache/**" -g"!zig-out/**"
```

Migration notes:

- Replace removed `@Type` patterns with the dedicated Zig 0.16 constructors.
- Replace `std.meta.Int` with `@Int` and `std.meta.Tuple` with `@Tuple`.
- Do not reify error sets; declare `error{...}` explicitly.
- Do not reify tuples with comptime fields through old struct-field metadata.
- Audit any code that relies on `std.builtin.StructField.is_comptime` for zero-bit tuple fields.
- Prefer normal syntax for arrays, optionals, error unions, and opaques.

## 16. Review template

Use this template in review responses:

```text
Comptime contract
- Comptime inputs:
- Runtime inputs:
- Generated/specialized artifact:
- Runtime path after specialization:
- Invalid cases rejected at compile time:
- Cost/specialization risk:
- Proof commands/fixtures:

Design notes
- Reflection choke point:
- anytype/typeclass contract:
- Zig 0.16 generated-type migration:
- Diagnostics quality:
- Inline loop/switch justification:
```

## 17. Official-reference anchors

Primary Zig 0.16.0 references used for this playbook:

- Zig language reference, comptime parameters, variables, and expressions: https://ziglang.org/documentation/0.16.0/
- Zig language reference, inline loops and `inline else`: https://ziglang.org/documentation/0.16.0/
- Zig language reference, `@typeInfo`, `@FieldType`, `@hasDecl`, `@hasField`, `@compileLog`, `@setEvalBranchQuota`, and `@inComptime`: https://ziglang.org/documentation/0.16.0/
- Zig 0.16.0 release notes, `@Type` replacement and generated-type builtins: https://ziglang.org/download/0.16.0/release-notes.html
- Zig 0.16.0 release notes, zero-bit tuple-field comptime behavior: https://ziglang.org/download/0.16.0/release-notes.html
