---
name: zig
description: "Use when implementing, reviewing, migrating, linting, testing, fuzzing, profiling, optimizing, or hardening Zig 0.16.0 code: .zig files, build.zig/build.zig.zon, std.Io/process.Init migration, C interop, expert comptime/metaprogramming/reflection/codegen, allocator ownership, FFI boundaries, concurrency, dependencies, and measured performance work."
---

# Zig

## Governing principles

Start from the Zen of Zig: communicate intent precisely; make edge cases explicit; prefer compile errors over runtime crashes; treat memory and I/O as resources; and serve the user with small, proven improvements.

Assume Zig 0.16.0 unless the user names another version, but verify before executing version-sensitive work. If `zig version` is not `0.16.0`, label the result `VERSION_MISMATCH` and do not claim the commands validate 0.16.0 behavior.

Prefer witness-driven design. If a fact affects safety, ownership, zero-copy legality, FFI soundness, concurrency, or fast-path legality, represent it with a type, constructor, or checked value, not a loose bool, comment, or caller convention.

Keep proof lanes separate:

- Comptime contracts prove what must be known at compile time, what gets generated or specialized, which invalid shapes fail at compile time, and which runtime path remains.
- Formatting/linting proves style and static policy.
- Builds/tests/fuzzing prove correctness.
- Benchmarks prove user-visible performance deltas.
- Profilers explain where time, allocations, locks, or bytes went.

When a lane cannot be run, say so with a stable label: `LINT_UNAVAILABLE`, `TEST_UNAVAILABLE`, `FUZZ_UNAVAILABLE`, `PROFILE_UNAVAILABLE`, `COMPTIME_PROOF_UNAVAILABLE`, or `UNMEASURED`.

## First-pass workflow

1. Classify the request: migration, API design, correctness bug, dependency/build work, lint/tooling, FFI, concurrency, comptime/codegen, or performance.
2. If the request involves `comptime`, `anytype`, reflection, generated types, format/schema derivation, or specialization, produce a comptime contract before producing code.
3. Confirm repo shape: find `build.zig`, `build.zig.zon`, existing `zig build` steps, tests, benchmarks, and lint steps.
4. Confirm toolchain version with `zig version` before executing 0.16.0-sensitive commands.
5. Run the 0.16.0 migration scan when touching code written for 0.15.x or older.
6. Run the comptime audit scan when touching generic, reflective, or generated-type code.
7. Run the systems audit scan when touching allocators, ownership, pointers, casts, C/ABI, packed/extern layout, I/O effects, atomics, concurrency, or low-level performance.
8. Identify hazard classes and proof requirements before editing.
9. Make the smallest change that satisfies the contract.
10. Re-run the appropriate proof lanes and report exact commands plus outcomes.

## Zig 0.16.0 migration scan

Run this before proposing edits in code that may predate 0.16.0:

```bash
rg -n "std\.io|FixedBufferStream|GenericReader|AnyReader|@cImport|@Type\(|std\.Thread\.Pool|Thread\.Mutex|Thread\.Condition|Thread\.ResetEvent|std\.posix\.|std\.os\.windows\.|std\.os\.environ|process\.args|process\.argsAlloc|process\.getEnv|process\.getEnvMap|getCwd|getCwdAlloc|currentPath|ArrayHashMap|AutoArrayHashMap|StringArrayHashMap|PriorityQueue|initEmpty|initFull|std\.meta\.Int|std\.meta\.Tuple|@Vector|std\.testing\.fuzz|std\.testing\.Smith|checkAllAllocationFailures|std\.testing\.io|addTranslateC|zig-pkg|--fork|--test-timeout|comptime|anytype|@typeInfo|@TypeOf|@FieldType|@hasDecl|@hasField|@field|@compileError|@compileLog|@setEvalBranchQuota|@inComptime|inline (for|while|else)|@Struct|@Union|@Enum|@Tuple|@Pointer|@Fn|@Int|@EnumLiteral|\.is_comptime|struct \{ comptime" . \
  -g"*.zig" -g"build.zig" -g"build.zig.zon" \
  -g"!zig-pkg/**" -g"!.zig-cache/**" -g"!zig-out/**"
```

Interpretation:

- I/O: migrate `std.io`/`FixedBufferStream`/`GenericReader`/`AnyReader` call sites to `std.Io`, `std.Io.Reader`, and `std.Io.Writer`. Thread an `Io` instance through APIs instead of hiding nondeterminism in globals.
- Main/args/env: `pub fn main` may have no first parameter, `std.process.Init.Minimal`, or `std.process.Init`. Use `std.process.Init` for applications that need default allocator, I/O, args, env map, arena, or preopens. Use `Init.Minimal` when only raw args/env are needed. Avoid reaching for global args or env in library code.
- C interop: `@cImport` is deprecated for new code. Prefer a dedicated C header plus `b.addTranslateC(...)`, then import the translated module with `@import("c")`.
- Comptime type construction: `@Type` is gone. Use dedicated builtins such as `@Int`, `@Tuple`, `@Pointer`, `@Fn`, `@Struct`, `@Union`, `@Enum`, and `@EnumLiteral`. Prefer normal syntax for arrays, optionals, error unions, opaques, and explicit error sets instead of inventing generated-type helpers.
- Thread pools: `std.Thread.Pool` is removed. Migrate to `std.Io.async`, `std.Io.concurrent`, or `std.Io.Group.async` according to synchronization needs. When replacing `Thread.Pool`, also migrate `Thread.Mutex`, `Thread.Condition`, `Thread.ResetEvent`, and related synchronization to `std.Io.*` equivalents.
- Current path: replace `std.process.getCwd*` with `std.process.currentPath*` and pass `io`.
- Packages: dependencies are fetched into project-local `zig-pkg/`. Add it to `.gitignore` unless the repo intentionally vendors dependencies. Use `zig build --fork=/absolute/path` for temporary local package overrides.
- Fuzzing: fuzz callbacks now receive `*std.testing.Smith`, not raw `[]const u8`. Keep crash corpora under `testdata/fuzz/` and reproduce with `std.testing.FuzzInputOptions.corpus` plus `@embedFile`.
- Unit timeouts: use `zig build test --test-timeout 500ms` to detect wedged tests during migration.
- Vector iteration: runtime vector indexes are forbidden. Coerce a vector to an array before element-by-element iteration or debugging.
- Profiling/debug info: the new ELF linker is useful for incremental builds, but do not select it for DWARF-dependent profiling unless the debug-info limitation has been resolved in the target toolchain.
- Comptime metadata: audit old assumptions about zero-bit tuple fields being implicitly `comptime`; Zig 0.16.0 reverted that behavior for `std.builtin.StructField.is_comptime` inspection.



## Hazard classes and proof obligations

| Hazard class | Required proof |
| --- | --- |
| `parser/decoder/zero-copy` | Unit tests, round-trip tests, differential fuzzing, validated witness type, backing-storage lifetime proof. |
| `allocator-using` | Explicit ownership/allocator contract, leak check, allocation-failure coverage with `std.testing.checkAllAllocationFailures`, and deterministic fail-index regressions when found. |
| `pointer/unsafe-boundary` | Length/alignment/sentinel/lifetime proof before `@ptrCast`, `@ptrFromInt`, C-pointer, or zero-copy projection escapes. |
| `layout/abi/mmio/wire` | Layout table with `@sizeOf`, `@alignOf`, `@offsetOf`/`@bitOffsetOf`, endian/target assumptions, and target-matrix proof where relevant. |
| `ffi/abi` | Boundary contract table, wrapper tests, link proof, nullability/length/ownership/lifetime proof, centralized raw pointer conversions. |
| `io/effects` | Explicit `std.Io`/allocator/config/env capabilities, fake/constrained test effects, and cancellation/blocking model. |
| `error/failure-path` | Precise error set where feasible, `errdefer` rollback, cleanup-after-failure tests, and no swallowed `error.OutOfMemory`. |
| `optimizer-sensitive` | Scalar/reference path plus differential checks across `Debug`, `ReleaseSafe`, and `ReleaseFast`. |
| `concurrency/shared-state` | Sequential spec or witness model, documented memory orders, deterministic seed/replay/yield harness, timeout/stress lane, and cancellation/lifetime proof. |
| `dependency/provenance` | Visible URL/hash/fingerprint, origin repo, release tag or commit, and signer/attestation notes for security-sensitive or long-lived pins. |
| `comptime/metaprogramming` | Comptime contract, shape validation before reflection, intentional diagnostics, positive and negative fixtures, and compile-time cost/binary-size review when specialization cardinality is nontrivial. |

Satisfy every active hazard class. Do not use a green smoke test as proof for unsafe, FFI, lock-free, layout-sensitive, or optimizer-sensitive code.

## Low-level systems engineering contract

For low-level Zig work, do not merely provide code. Provide the systems contract:

1. ownership and allocator contract;
2. lifetime and cleanup contract;
3. pointer/slice/sentinel/alignment contract;
4. error-set and failure-path contract;
5. I/O/effect capability contract;
6. layout/ABI/endian contract;
7. concurrency/atomic-ordering contract when shared state exists;
8. target/build-mode validation matrix;
9. tests, fuzzing, allocation-failure checks, and profiling evidence.

Use `references/systems_contract_template.md` for structured reviews.

## Systems audit scan

Run this scan before changing low-level code that touches allocation, raw memory, FFI, layout, I/O, concurrency, or performance-sensitive paths:

```bash
scripts/systems_audit_rg.sh
```

Interpretation:

- Allocator hits require ownership, cleanup, and allocation-failure review.
- Pointer/cast hits require length, alignment, sentinel, lifetime, and aliasing proof.
- `extern`/`packed`/offset hits require layout, endian, ABI, and target validation.
- `std.Io`/process/env/current-path hits require explicit effect capability review.
- Atomic/thread/synchronization hits require shared-state invariant and memory-order review.
- `anyerror`, `catch unreachable`, `panic`, and `unreachable` require failure-contract review.
- `@cImport` should usually migrate toward build-system C translation in new Zig 0.16 code.

## Allocator, ownership, and lifetime engineering

Use `references/memory_ownership_playbook.md` for APIs that allocate, free, return buffers, store allocators, use arenas, or mutate containers.

Rules:

- State who owns every allocation and which allocator frees it.
- Prefer accepting `std.mem.Allocator` in libraries; do not hide allocator choice behind globals.
- Use `errdefer` immediately after successful acquisition in multi-step initialization.
- Distinguish borrowed, owned, transferred, arena-owned, and caller-allocated data.
- Treat returned slices as invalidation-sensitive when the backing container can reallocate.
- Avoid arenas as a substitute for ownership reasoning; document reset/deinit boundaries.
- Require leak and allocation-failure coverage for allocator-heavy code.

## Unsafe boundary, pointer, slice, sentinel, and alignment engineering

Use `references/unsafe_boundary_playbook.md` for `@ptrCast`, `@ptrFromInt`, `@alignCast`, `[*]T`, `[*c]T`, sentinel pointers/slices, `volatile`, zero-copy projection, or C-pointer wrapping.

Rules:

- Prefer slices over many-item pointers in Zig-facing APIs.
- Prefer typed APIs, slice narrowing, `std.mem.bytesAsSlice`, and `@bitCast` before raw pointer casts.
- Before any raw cast, prove length, alignment, initialization, lifetime, mutability, and target/ABI assumptions.
- Create sentinel-typed views only after proving the sentinel exists and remains valid.
- Keep C pointers in boundary modules; convert to safe Zig types quickly.
- Use `volatile` for MMIO/side-effecting memory, not thread synchronization.

## Layout, ABI, MMIO, and wire-format engineering

Use `references/layout_abi_playbook.md` for C ABI, `extern`, `packed`, hardware registers, binary formats, network packets, file formats, or target-sensitive layout.

Rules:

- Do not use ordinary `struct` as a wire/disk/C/MMIO layout promise.
- Use `extern` for target C ABI and `packed` for bit-level layout.
- Assert sizes, alignments, offsets, and bit offsets.
- Make endianness explicit for wire and disk formats.
- Avoid passing packed-field pointers as normal aligned pointers.
- Validate ABI/layout across the targets that the claim covers.

## Error-set and failure-path engineering

Use `references/error_failure_playbook.md` when changing fallible APIs or cleanup behavior.

Rules:

- Prefer precise error sets in libraries and domain APIs; avoid `anyerror` unless integration-level widening is justified.
- Distinguish domain/protocol errors, resource errors, environmental errors, and programmer bugs.
- Do not swallow `error.OutOfMemory`.
- Centralize C/system status-to-error translation at boundaries.
- Use `errdefer` for rollback and test cleanup-after-failure.
- Treat `catch unreachable` as a proof obligation, not a convenience.

## Explicit I/O and effect injection

Use `references/io_effects_playbook.md` for `std.Io`, `std.process.Init`, process args/env, current path, filesystem, randomness, time, logging, cancellation, or testability.

Rules:

- In Zig 0.16, thread `std.Io` through APIs that block or introduce nondeterminism.
- Let `main` capture args/env/preopens and pass parsed configuration into core code.
- Prefer explicit capabilities/context over hidden process/global state.
- Tests should use fake or constrained effects such as `std.testing.io`, in-memory buffers, deterministic RNG, and fixed config.
- Document blocking and cancellation behavior for async/task APIs.

## Build, cross-compilation, package, and C toolchain mastery

Use `references/build_toolchain_playbook.md` for `build.zig`, `build.zig.zon`, target matrices, package pins, C/C++ interop, `zig fetch`, `zig-pkg`, and `zig build --fork`.

Rules:

- Inspect `zig build --help` before inventing commands.
- Treat `build.zig.zon` as dependency source of truth.
- Keep `zig-pkg/` out of source control unless intentionally vendoring.
- Use `--fork` for ephemeral local dependency overrides.
- For C translation, match target and cflags; isolate translated imports behind wrappers.
- Validate low-level code in relevant optimization modes and targets, not Debug only.

## Atomics, concurrency, and cancellation

Use `references/atomics_concurrency_playbook.md` for shared state, atomics, synchronization, task groups, cancellation, or lock-free claims.

Rules:

- Prefer ownership transfer, sharding, or locks before lock-free algorithms.
- Identify shared state, invariant, synchronization primitive, and memory order for every atomic operation.
- Use `volatile` only for MMIO/side-effecting memory; use atomics/locks for concurrency.
- Solve pointer lifetime/reclamation before publishing pointers lock-free.
- Stress tests are not proof; add a sequential model or witness where lock-free behavior is claimed.
- Use test timeouts for hang-prone concurrency tests.

## Failure discovery and performance engineering

Use `references/testing_failure_discovery_playbook.md` for tests, fuzzing, allocation-failure coverage, negative compile-time tests, crash reproduction, and optimizer-mode validation.
Use `references/performance_engineering_playbook.md` for benchmarks, allocator profiling, CPU sampling, cache layout, SIMD/vectorization, binary size, and profiling evidence.

Rules:

- Report `UNMEASURED` instead of implying speedups without benchmark evidence.
- Use `zprof` for allocation/leak metrics and system profilers for CPU hotspots.
- Keep benchmark dataset, allocator, optimize mode, and checksum fixed between baseline and variant.
- Preserve fuzz crash corpora and exact reproduction commands.

## Linting and static checks

Use the repo’s existing lint surface first. If `zig build lint` exists, treat it as a hard gate and run the repo-supported invocation. If lint is absent, mark `LINT_UNAVAILABLE` unless the user asked to add tooling or the change safely fits a lint bootstrap.

Baseline built-in checks:

```bash
zig fmt --check .
find . -name '*.zig' \
  -not -path './zig-pkg/*' \
  -not -path './.zig-cache/*' \
  -not -path './zig-out/*' \
  -print0 | xargs -0 zig ast-check
```

Rules:

- `zig fmt` is the canonical formatter. Use `zig fmt` for intentional formatting changes and review the diff.
- `zig ast-check` is a syntax/simple-compile-error lane for `.zig` files. Do not run it on `build.zig.zon`.
- Do not equate `zig ast-check` with a full semantic compile. Follow with `zig build`/`zig test`.
- For third-party linting in Zig 0.16.x, prefer `zlinter#0.16.x`. Use `#master` only when intentionally targeting 0.17.x-dev.
- Do not enable all `zlinter` built-in rules as a permanent CI default without review; upstream calls that mode pedantic and mainly suitable for exploration. Use a curated rule set, then add more rules incrementally.
- Run `--fix` only on a clean working tree or after taking a backup. Re-run until no fixes are applied, then review the diff before proceeding.

`zlinter` bootstrap for Zig 0.16.x:

```bash
zig fetch --save git+https://github.com/kurtwagner/zlinter#0.16.x
```

Minimal curated build step:

```zig
const zlinter = @import("zlinter");

const lint_step = b.step("lint", "Lint Zig source code.");
lint_step.dependOn(step: {
    var builder = zlinter.builder(b, .{});
    builder.addPaths(.{
        .include = &.{ b.path("src/"), b.path("build.zig") },
        .exclude = &.{ b.path("zig-pkg/"), b.path(".zig-cache/"), b.path("zig-out/") },
    });
    builder.addRule(.{ .builtin = .no_deprecated }, .{});
    builder.addRule(.{ .builtin = .no_unused }, .{});
    builder.addRule(.{ .builtin = .no_swallow_error }, .{});
    builder.addRule(.{ .builtin = .require_errdefer_dealloc }, .{});
    builder.addRule(.{ .builtin = .require_exhaustive_enum_switch }, .{});
    break :step builder.build();
});
```

Typical lint commands once configured:

```bash
zig build lint
zig build lint -- --max-warnings 0
zig build lint -- --rule no_unused --rule no_deprecated --fix
```

## Correctness gates

Every Zig change needs at least one correctness signal. Prefer the repo harness over bare `zig test` when generated imports, modules, package dependencies, or custom build flags are involved.

```bash
zig build
zig build test
zig build test --test-timeout 500ms
zig test src/main.zig
```

Use filters carefully. Check `zig build -h` or the relevant step before assuming where `--test-filter`, `--seed`, `--test-timeout`, or runner args belong. If a filtered test is being used to prove a boundary, add one fail-closed probe so you know the filter is active.

For optimizer-sensitive logic, run all relevant modes:

```bash
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
```

For allocator-using functions:

```zig
const std = @import("std");

fn work(allocator: std.mem.Allocator, input: []const u8) !void {
    const copy = try allocator.dupe(u8, input);
    defer allocator.free(copy);
}

test "allocation failure coverage" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        work,
        .{"seed"},
    );
}
```

For fuzzing in Zig 0.16.0:

```zig
const std = @import("std");

fn reference(input: []const u8) !u64 {
    var n: u64 = 0;
    for (input) |b| n += @popCount(b);
    return n;
}

fn optimized(input: []const u8) !u64 {
    return reference(input);
}

fn fuzzTarget(_: void, smith: *std.testing.Smith) !void {
    var storage: [1024]u8 = undefined;
    for (&storage) |*byte| byte.* = smith.value(u8);
    const len = smith.value(usize) % (storage.len + 1);
    const input = storage[0..len];
    try std.testing.expectEqual(try reference(input), try optimized(input));
}

test "differential fuzz" {
    const seeds = &[_][]const u8{ "", "0", "needle", "\x00\x00\x00", "\xff\xff\xff" };
    try std.testing.fuzz({}, fuzzTarget, .{ .corpus = seeds });
}
```

Fuzz commands:

```bash
zig build test --fuzz
zig build test --fuzz -j4
```

On macOS, do not assume integrated fuzzing is fully supported just because the target is Zig 0.16.0. Keep Smith fuzz targets in-tree, preserve crash corpora, and prefer Linux/CI for sustained fuzz campaigns when local platform support blocks progress.

## Boundary witnesses and zero-copy

Separate `scan -> validate -> project`.

Validation should return a small witness type such as `ValidatedFrame`, `BorrowedView`, `NonEmptySlice`, `AlignedBytes`, or `CheckedOffset`. Do not expose typed views, zero-copy projections, `@ptrCast`-based decoding, or SIMD loads until validation succeeds.

Rules:

- Make borrowed vs owned states explicit with separate types or `union(enum)`.
- Do not return slices backed by stack or temporary storage.
- Put one constructor around each invariant cluster.
- Fail fast on over-capacity streaming tokens instead of truncating.
- Keep backing-storage proof adjacent to projection APIs.

## Comptime, reflection, and generated types

Treat comptime-heavy Zig as an architecture and proof problem, not merely as syntax for generics. For every nontrivial comptime use, produce the comptime contract:

1. what must be known at compile time;
2. what type, value, function, plan, parser, table, or path is generated or specialized;
3. what runtime inputs and runtime path remain;
4. what invalid type/value shapes fail at compile time;
5. what compile-time cost, binary-size growth, or specialization cardinality is introduced;
6. what tests or compile-fail fixtures prove the contract.

Use `references/comptime_playbook.md` for deep reviews, migrations, and designs.

### Comptime decision tree

| User need | Preferred pattern | Main failure mode |
| --- | --- | --- |
| Generic container/API | `fn Name(comptime T: type, ...) type` returning a struct; use `@This()` inside the returned type. | Using unconstrained `anytype` and making the contract invisible. |
| Runtime API with compile-time policy | `comptime options: Options`, `comptime mode: enum`, or explicit `comptime T: type`. | High-cardinality value specialization that inflates build time and binary size. |
| Derived behavior from fields/declarations | Centralized `classifyType -> validateType -> derivePlan` reflection layer. | Scattered raw `@typeInfo` switches and cryptic compiler failures. |
| Generated type | Zig 0.16 builtins: `@Int`, `@Tuple`, `@Pointer`, `@Fn`, `@Struct`, `@Union`, `@Enum`, `@EnumLiteral`. | Old `@Type`, `std.meta.Int`, or `std.meta.Tuple` patterns. |
| Compile-time parser/table | Validate grammar at comptime; emit compact runtime plan/table. | Runtime-looking errors hidden as unreadable compile errors. |
| ABI/layout proof | `@sizeOf`, `@alignOf`, `@bitSizeOf`, `@offsetOf`, `@FieldType`, plus `@compileError`. | Trusting layout assumptions without target-sensitive checks. |
| Runtime/comptime dual implementation | Use `@inComptime()` only for genuinely comptime-friendly fallbacks. | Forking behavior unnecessarily or excluding APIs from comptime evaluation. |

### Mental model

Comptime is semantic-analysis-time execution and partial evaluation. It is how Zig implements generics, type factories, compile-time parsers, table generation, reflection-driven derivation, and deliberate specialization. It is not a macro system and not a blanket speed knob.

Rules:

- Prefer explicit `comptime T: type` when the type itself is the API subject.
- Prefer normal runtime parameters when specialization is not semantically required.
- Make all generated/specialized runtime paths understandable after partial evaluation.
- Treat `@compileError` as the public UX of a reflective API.
- Treat `@compileLog` as temporary debugging only; committed compile logs are failures.
- Treat `@setEvalBranchQuota` as a compile-time cost smell unless the workload is deliberate, bounded, and documented.

### Comptime audit scan

Run this scan before changing generic, reflective, generated-type, or schema/format derivation code:

```bash
rg -n "comptime|anytype|@typeInfo|@TypeOf|@FieldType|@hasDecl|@hasField|@field|@compileError|@compileLog|@setEvalBranchQuota|@inComptime|inline (for|while|else)|@Struct|@Union|@Enum|@Tuple|@Pointer|@Fn|@Int|@EnumLiteral|@Type\(|std\.meta\.(Int|Tuple)|\.is_comptime|struct \{ comptime" . \
  -g"*.zig" -g"build.zig" \
  -g"!zig-pkg/**" -g"!.zig-cache/**" -g"!zig-out/**"
```

Interpretation:

- `@Type(`, `std.meta.Int`, and `std.meta.Tuple` are Zig 0.15-era migration cues.
- `.is_comptime` and `struct { comptime` need extra care because Zig 0.16.0 changed zero-bit tuple-field behavior.
- `@compileLog` should be removed or explicitly marked as active debugging.
- `@setEvalBranchQuota` requires a cost note and preferably a bounded input argument or table size.
- `inline for` and `inline while` need a semantic reason or benchmark proof.

### Reflection architecture

For nontrivial reflection, centralize the machinery in `reflect.zig`, `meta.zig`, or a clearly named derivation module:

```text
classifyType(T) -> small enum or descriptor
validateType(T, Options) -> intentional @compileError diagnostics
derivePlan(T, Options) -> comptime metadata table/runtime plan
runtime function -> consumes only the derived plan and runtime values
```

Do not scatter raw `@typeInfo` switches across business logic. Validate shape before calling `@FieldType`, `@field`, `@hasDecl`, or `@hasField` in ways that assume structs/unions/enums.

Safe declaration and field checks:

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

fn requireStruct(comptime api: []const u8, comptime T: type) void {
    switch (@typeInfo(T)) {
        .@"struct" => {},
        else => @compileError(api ++ "(" ++ @typeName(T) ++ "): expected struct"),
    }
}
```

### `anytype` discipline

When reviewing `anytype`, infer and name the hidden typeclass.

Require the answer to identify:

- required fields, declarations, methods, operators, sentinel behavior, allocator behavior, or error behavior;
- whether the value type or the value itself must be comptime-known;
- valid examples and invalid examples;
- intentional diagnostics for unsupported shapes.

Prefer replacing `anytype` with `comptime T: type` plus a typed runtime parameter when the type is the API subject:

```zig
fn encode(comptime T: type, writer: anytype, value: T) !void {
    validateEncodable(T);
    try encodeValue(T, writer, value);
}
```

Use `anytype` when the value-level syntax is the point, such as `std.debug.print`-style argument tuples or polymorphic writers. Even then, validate with `@TypeOf(value)` and `@compileError` before relying on operations that may not exist.

### Inline loop and inline switch rules

Use `inline for` or `inline while` only when one of these is true:

- the loop variable must be comptime-known for semantics, usually because it is used as a type, field name, declaration name, or compile-time metadata value;
- a benchmark proves forced unrolling is measurably faster for the target workload.

Prefer `inline else` or `inline switch` for tagged-union/enum handling when exhaustiveness should be compiler-checked. `inline for` over enum fields often requires a manual `unreachable`; `inline else` can express the same dispatch while preserving exhaustiveness checking.

### Generated types in Zig 0.16.0

Use Zig 0.16 type constructors instead of removed `@Type` forms:

| Old pattern | Zig 0.16 pattern |
| --- | --- |
| `@Type(.{ .int = ... })` | `@Int(.signed/.unsigned, bits)` |
| `std.meta.Int` | `@Int` |
| `std.meta.Tuple` | `@Tuple` |
| `@Type(.{ .pointer = ... })` | `@Pointer` |
| `@Type(.{ .@"fn" = ... })` | `@Fn` |
| `@Type(.{ .@"struct" = ... })` | `@Struct` |
| `@Type(.{ .@"union" = ... })` | `@Union` |
| `@Type(.{ .@"enum" = ... })` | `@Enum` |
| `@Type(.enum_literal)` or `@TypeOf(.foo)` as a constructor | `@EnumLiteral()` |
| Reified error sets | Explicit `error{...}` declarations |

Do not generate types unless a named static type, ordinary array syntax, optional syntax, error-union syntax, opaque declaration, or explicit error-set declaration cannot express the shape more clearly.

Common replacements:

```zig
fn Array(comptime len: usize, comptime Elem: type, comptime sentinel: ?Elem) type {
    return if (sentinel) |s| [len:s]Elem else [len]Elem;
}

fn UInt(comptime bits: u16) type {
    return @Int(.unsigned, bits);
}

fn Pair(comptime A: type, comptime B: type) type {
    const names = [_][]const u8{ "first", "second" };
    const types = [_]type{ A, B };
    const attrs = [_]std.builtin.Type.StructField.Attributes{ .{}, .{} };
    return @Struct(.auto, null, &names, &types, &attrs);
}
```

### Diagnostics rubric

Bad:

```zig
@compileError("unsupported type");
```

Good:

```zig
@compileError(
    "deriveJson(" ++ @typeName(T) ++ "): expected struct with public fields; " ++
    "define pub fn jsonSerialize or pass Options.custom_serialize"
);
```

A good comptime diagnostic names:

- the API that rejected the input;
- the offending type or comptime value;
- the unsupported shape or invariant;
- the intended escape hatch;
- the smallest action the caller can take.

Avoid dumping raw `std.builtin.Type` unless the user is actively debugging internals.

### Compile-time cost governance

Audit cost when the comptime code reflects over many types, parses large strings, emits generated types, or specializes by value:

- How many specializations are generated?
- Are compile-time value parameters high cardinality?
- Is a large string/table parsed for every instantiation?
- Is reflection repeated in multiple generic functions?
- Can derived metadata be centralized in one type-level plan?
- Does `@setEvalBranchQuota` hide unbounded work?
- Does the generated code increase binary size?
- Did the code build in Debug and at least one Release mode?

Avoid comptime when a runtime table is clearer, performance is unproven, or specialization would generate many near-identical functions.

### Positive and negative proof

Comptime-heavy libraries need positive and negative fixtures.

Positive proof:

- valid type derives successfully;
- valid custom hook overrides default behavior;
- runtime behavior matches the derived plan;
- comptime and runtime calls agree when both are supported.

Negative proof:

- invalid type produces intentional `@compileError`;
- missing hook produces a clear diagnostic;
- bad field/ABI/policy combination is rejected;
- removed Zig 0.15-era constructs are absent.

If the environment cannot run compile-fail tests, report `COMPTIME_PROOF_UNAVAILABLE` and include the exact invalid fixture the user should build locally.

### Expert review checklist

- Identify comptime inputs and runtime inputs.
- State why comptime is required: type construction, shape validation, table generation, ABI proof, or measured specialization.
- Reject unsupported shapes with `@compileError` before using `@field`, `@FieldType`, `@hasDecl`, or `@hasField` unsafely.
- Prefer explicit `comptime T: type` when the type is the API subject.
- Avoid unconstrained `anytype`; document the implicit typeclass.
- Use `inline for` only for semantic comptime iteration or benchmark-proven unrolling.
- Prefer `inline else` for tagged-union exhaustiveness when applicable.
- For Zig 0.16, replace removed `@Type` patterns with `@Int`, `@Tuple`, `@Pointer`, `@Fn`, `@Struct`, `@Union`, `@Enum`, and `@EnumLiteral`.
- Treat `@compileLog` as temporary debugging only.
- Treat `@setEvalBranchQuota` as a cost smell unless bounded and justified.
- Add positive and negative tests for derived APIs.
- Measure binary size/build time if specialization cardinality is nontrivial.

## FFI and C interop

For new Zig 0.16.0 code, prefer build-system C translation:

```zig
const translate_c = b.addTranslateC(.{
    .root_source_file = b.path("src/c.h"),
    .target = target,
    .optimize = optimize,
});
translate_c.linkLibC();
translate_c.linkSystemLibrary("sqlite3", .{});

const exe = b.addExecutable(.{
    .name = "app",
    .root_module = b.createModule(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{.{
            .name = "c",
            .module = translate_c.createModule(),
        }},
    }),
});
```

Boundary rules:

- Keep raw `extern fn` declarations or translated C imports in a small boundary module.
- Maintain a contract table for each nontrivial symbol: nullability, length source, mutability, ownership in/out, lifetime, thread-safety, error mapping, and linkage.
- Centralize `@ptrCast`, sentinel conversion, null checks, errno/result translation, and cleanup.
- Test happy paths, invalid/null inputs, out-param initialization, cleanup, and link wiring.
- If the C dependency changes, compare signatures and ABI expectations before trusting the upgrade.

## Concurrency and weak-memory lane

Prefer ownership transfer, sharding, or message passing before lock-free shared state.

For shared mutable state, write down:

- invariant,
- owner transitions,
- memory order for each atomic,
- cancellation and lifetime model,
- replay or deterministic seed strategy.

When migrating from `std.Thread.Pool`, choose:

- `std.Io.async` for independent asynchronous work,
- `std.Io.Group.async` for shared-lifetime task groups,
- `std.Io.concurrent` when tasks must synchronize with the caller or async is semantically wrong.

Stress tests are not correctness proof for lock-free code. Add a sequential spec or witness model when lock-free behavior is claimed.

## Dependency and package workflow

Treat `build.zig.zon` as the dependency source of truth when packages are involved.

```bash
zig fetch --save https://example.invalid/pkg.tar.gz
zig fetch --save git+https://github.com/example/pkg#v1.2.3
zig build
zig build --fork=/absolute/path/to/local/clone
```

Rules:

- Review URL, hash/fingerprint, package name, and paths in every dependency diff.
- Keep `zig-pkg/` out of source control unless intentionally vendoring.
- Do not edit `.zig-cache` as a dependency override.
- Use `--fork` for temporary local debugging of ecosystem breakage.
- For security-sensitive pins, record origin repo, release tag/commit, fetch date, and signer or attestation evidence.

## Performance and profiling

Use this lane for speed, latency, throughput, allocation pressure, memory growth, leaks, or hotspot analysis.

First name the symptom:

- End-to-end latency/throughput/regression: benchmark first.
- Allocation churn, live bytes, leaks, or allocator pressure: use `zprof`.
- CPU hotspots, cache misses, branchy paths, or lock contention: use a system CPU sampler.
- Long-running concurrent or frame-oriented telemetry: consider Tracy only when the workload shape justifies instrumentation or the repo already supports it.

Minimum measured loop:

```bash
zig build test
zig build -Doptimize=ReleaseSafe -Dtarget=native -Dcpu=native
zig build -Doptimize=ReleaseFast -Dtarget=native -Dcpu=native
zig build bench -- --samples 10 --warmup 3
```

If no benchmark exists, either add a small harness with a checksum/regression guard or report `UNMEASURED` with exact commands the user can run.

`zprof` lane:

- Use current upstream release guidance; as of the researched 0.16.0 update, the latest release is v4.0.0.
- `zprof` wraps any Zig allocator and tracks logical allocation metrics. It is not a CPU profiler and does not replace wall-clock benchmarks.
- Metrics in v4 use fields such as `allocated`, `freed`, `alloc_count`, `free_count`, `live_requested`, and `peak_requested`.
- Enable `.thread_safe = true` only when multiple threads share the wrapped allocator; otherwise prefer one profiler per subsystem/thread for attribution.
- Keep child allocator, dataset, work count, and optimize mode fixed between baseline and variant.
- Use `profiler.reset()` between phases when one process captures multiple workloads.

Install/wire example:

```bash
zig fetch --save https://github.com/ANDRVV/zprof/archive/v4.0.0.zip
```

```zig
const zprof_dep = b.dependency("zprof", .{
    .target = target,
    .optimize = optimize,
});
exe.root_module.addImport("zprof", zprof_dep.module("zprof"));
```

Minimal usage:

```zig
const std = @import("std");
const Zprof = @import("zprof").Zprof;

fn runWorkload(allocator: std.mem.Allocator) !void {
    const data = try allocator.alloc(u8, 1024);
    defer allocator.free(data);
}

test "profile allocator pressure" {
    var prof: Zprof(.{}) = .init(std.testing.allocator, undefined);
    try runWorkload(prof.allocator());

    try std.testing.expect(!prof.profiler.hasLeaks());
    try std.testing.expectEqual(@as(usize, 0), prof.profiler.live_requested.get());
}
```

CPU sampling lane:

```bash
# Linux
perf record --call-graph dwarf -- ./zig-out/bin/app
perf report

# macOS
# Use Instruments Time Profiler on the optimized binary.
```

If allocator counters are flat and wall time regresses, switch to CPU sampling instead of guessing.

Benchmark decomposition rule: when a regression spans abstraction layers, add 2-4 lanes in the same harness with the same dataset, warmup, sample count, checksum, allocator, and optimize mode: substrate only, wrapper/shell only, full path, and optionally reference/scalar path. Optimize from the decomposed result, not from the aggregate number alone.

## Reporting contract

Always end Zig implementation/review work with:

- version observed,
- changed files or proposed changes,
- active hazard classes,
- commands run,
- results and failures,
- unavailable proof lanes with stable labels,
- remaining risk.

Do not claim correctness, lint cleanliness, fuzz coverage, or speedup without evidence.

## References inside this skill

- `codex/skills/zig/references/linting_playbook.md`
- `codex/skills/zig/references/profiling_playbook.md`
- `codex/skills/zig/references/comptime_playbook.md`
- `codex/skills/zig/references/comptime_patterns.zig`
- `codex/skills/zig/references/memory_ownership_playbook.md`
- `codex/skills/zig/references/unsafe_boundary_playbook.md`
- `codex/skills/zig/references/layout_abi_playbook.md`
- `codex/skills/zig/references/error_failure_playbook.md`
- `codex/skills/zig/references/io_effects_playbook.md`
- `codex/skills/zig/references/build_toolchain_playbook.md`
- `codex/skills/zig/references/atomics_concurrency_playbook.md`
- `codex/skills/zig/references/testing_failure_discovery_playbook.md`
- `codex/skills/zig/references/performance_engineering_playbook.md`
- `codex/skills/zig/references/systems_contract_template.md`
- `codex/skills/zig/references/systems_patterns.zig`
- `codex/skills/zig/references/boundary_witness.zig`
- `codex/skills/zig/references/fuzz_differential.zig`
- `codex/skills/zig/references/fail_nth_alloc.zig`
- `codex/skills/zig/references/ffi_contract_template.md`
