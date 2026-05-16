# Zig Hazardous-Code and Illegal Behavior Audit Playbook

## Purpose

Use this playbook when a Zig task resembles an “unsafe code audit” in Rust, but do not import Rust's model literally. Zig does not mark hazardous code with an `unsafe` keyword. The audit target is any operation whose correctness depends on invariants that are not fully enforced by the Zig type checker, runtime safety checks, build mode, or ABI.

The goal is a small hazardous core, explicit invariants, safe wrappers, and repeatable verification. Removing the hazardous operation is good when possible, but shrinking and proving a truly irreducible boundary is also a successful outcome.

## Source anchors

Primary Zig 0.16.0 source areas to consult when updating this playbook or justifying a classification:

- Language reference: Illegal Behavior, Build Mode, `@setRuntimeSafety`, `undefined`, pointers, slices, pointer casts, `volatile`, `extern struct`, `packed struct`, atomics, C interop, memory/allocator sections.
- 0.16.0 release notes: `std.Io` migration, `Thread.Pool` removal, `@cImport` moving toward the build system, Smith fuzzing interface, project-local `zig-pkg` and cache behavior.
- Existing skill references: `memory_ownership_playbook.md`, `unsafe_boundary_playbook.md`, `layout_abi_playbook.md`, `error_failure_playbook.md`, `io_effects_playbook.md`, `build_toolchain_playbook.md`, `atomics_concurrency_playbook.md`, `testing_failure_discovery_playbook.md`, `performance_engineering_playbook.md`, and `systems_contract_template.md`.

## What counts as a Zig hazard site?

A hazard site is any source location where a false invariant can cause memory corruption, Unchecked Illegal Behavior, build-mode-dependent Safety-Checked Illegal Behavior, ABI mismatch, data races, invalid lifetime use, or silent logic corruption.

Common hazard triggers:

| Surface | Examples | Primary risk |
| --- | --- | --- |
| Safety checks and impossible states | `@setRuntimeSafety(false)`, `unreachable`, `catch unreachable`, `.?`, invalid enum/error casts, exact arithmetic builtins, unchecked shifts. | Safety-checked Illegal Behavior becomes unchecked, especially in ReleaseFast/ReleaseSmall. |
| Raw pointer/provenance | `@ptrCast`, `@ptrFromInt`, `@intFromPtr`, `@alignCast`, `@fieldParentPtr`, `@addrSpaceCast`, `@constCast`, `@volatileCast`, `[*]T`, `[*c]T`, `allowzero`, slice `.ptr` mutation. | Invalid address, null, length, alignment, lifetime, aliasing, address-space, or sentinel proof. |
| Initialization | `undefined`, partial aggregate initialization, output buffers, manual `@memcpy`, `@memset`, `@memmove`, self-referential setup. | Read-before-write, double cleanup, leaked cleanup on error path, nonsense value with a valid type. |
| Layout/ABI/wire/MMIO | `extern struct`, `extern union`, `extern enum`, `packed struct`, `packed union`, `@bitCast`, `@offsetOf`, `@bitOffsetOf`, `@sizeOf`, `@alignOf`. | Wrong target ABI, bit offset, endian, padding, packed-field pointer, or layout promise. |
| C/FFI/asm | `extern fn`, `pub extern`, `export fn`, `@extern`, `@export`, `@cImport`, `@cVa*`, `asm`, `callconv`, `anyopaque`. | Nullability, ownership, allocator domain, errno/status mapping, callback threading, unwinding/panic, C ABI drift. |
| MMIO and volatile | `*volatile T`, `volatile` loads/stores, address constants, register overlays. | Treating volatile as synchronization, wrong register width/endian, non-atomic read/modify/write, invalid aliasing. |
| Atomics/concurrency | `@atomicLoad`, `@atomicStore`, `@atomicRmw`, `@cmpxchgWeak`, `@cmpxchgStrong`, `std.atomic`, shared state with `std.Thread` or `std.Io` tasks. | Wrong memory order, lifetime/reclamation, cancellation/deinit race, false single-threaded assumption. |
| Allocator/lifetime | `Allocator`, `std.heap`, arenas, manual `deinit`, `errdefer`, returned slices, container reallocation. | Wrong allocator frees, use-after-free, invalidated borrowed slice, leak, missing rollback on failure. |
| Vector/SIMD/perf | `@Vector`, `@shuffle`, `@select`, `@reduce`, `@prefetch`, hand-unrolled pointer loops, target features. | Tail bugs, alignment assumptions, out-of-bounds, target-feature mismatch, folklore performance. |

## Three-bucket classification

Every hazard site receives exactly one classification. Hybrid sites should be split into smaller sites rather than receiving a vague mixed label.

### `A/IRREDUCIBLE_BOUNDARY`

The operation crosses a boundary Zig cannot safely express directly. Examples: FFI to C, OS syscalls, MMIO registers, inline assembly, custom allocator implementation internals, explicit atomics where a safe abstraction would hide an essential memory order, externally mandated packed/extern layouts, or pointer projection from a proven hardware/map address.

Required write-up:

```text
This is irreducible because <boundary or language limitation>.
Safer alternatives considered:
1. <alternative> fails because <specific reason>.
2. <alternative> fails because <specific reason>.
3. <alternative> fails because <specific reason>.
The invariant is established by <validator/witness/caller contract>.
If false, the failure mode is <IB/corruption/ABI mismatch/etc>.
```

Required remediation:

- Keep the hazardous operation in a boundary module or tiny function.
- Add a `SAFETY/ZIG-HAZARD` comment with caller/callee obligations.
- Add tests or compile-time assertions that prove the contract where possible.
- Add target/build-mode matrix if ABI, endian, alignment, or safety checks matter.

### `B/PERF_OR_FOOTPRINT_ONLY`

A safer formulation exists, but the project deliberately keeps a hazardous operation for speed, memory footprint, code size, target features, or allocation shape.

Examples: `@setRuntimeSafety(false)` around a hot loop, `@prefetch`, manual vectorization, pointer iteration instead of slices, `@ptrCast` for a fast parser after a scalar validator exists, or exact arithmetic chosen to avoid checks after prevalidation.

Required write-up:

```text
Safe/reference path: <function or design>.
Hazard kept for: <speed/code-size/allocation/target-feature>.
Measurements required: <bench/profile/size>.
Invalid states are rejected before the hazard by: <witness/check>.
```

Required remediation:

- Provide a scalar/reference path for differential tests.
- Gate the hazardous fast path behind target/build options when practical.
- Measure with a fixed dataset, checksum, optimize mode, and target.
- If the safer formulation is within the perf budget, reclassify to `C`.

### `C/REFACTORABLE_TO_WITNESS`

The hazardous operation can be removed, replaced with safer Zig, or moved behind a constructor/witness that makes the invariant explicit.

Examples: many-item pointer to slice, C pointer converted to optional pointer and length at the boundary, endian-aware parse instead of struct overlay, `undefined` replaced by explicit builder, `catch unreachable` replaced by precise error handling, or `@alignCast` moved into an `AlignedBytes` constructor.

Required remediation:

- Write the concrete replacement or wrapper, not just a sketch.
- Introduce a witness type when the invariant matters to later code.
- Add equivalence, negative, allocation-failure, fuzz, or target tests according to the active hazard.
- Preserve allocator identity, public API, target behavior, and build options unless the user authorizes a breaking change.

## Audit phases

### Phase 0 — Scope and permissions

Record:

- target path and whether an audit directory may be created;
- Zig version and whether it matches the skill's assumed version;
- build modes and target triples in scope;
- local source, generated Zig, translated C, dependency packages, and vendored code in or out of scope;
- whether remediation is audit-only, plan-only, or authorized active-checkout editing.

For full audits, create `<project>/.zig-hazard-audit/` after permission. Do not edit source files until remediation is explicitly authorized.

### Phase 1 — Enumerate

Run the script or equivalent scan:

```bash
scripts/zig_hazard_audit_rg.sh . > .zig-hazard-audit/hazard-rg.txt
```

Also inspect:

- `build.zig` and `build.zig.zon` for target features, optimize modes, C translation, `addCSource*`, package pins, and custom build options;
- generated Zig files if checked in or produced by build steps;
- translated C headers and FFI wrappers;
- target-specific directories such as `x86_64`, `aarch64`, `wasm`, `freestanding`, `linux`, `windows`, or embedded board names;
- public APIs that expose slices, pointers, handles, FFI types, or packed/extern values.

### Phase 2 — Normalize inventory

Each inventory row should contain:

```text
site_id
file:line:column
operation kind
public reachability
bucket candidate
invariant owner
build-mode sensitivity
when compiled: target/os/feature condition
proof lanes required
notes
```

Do not let a single line hide multiple hazards. For example, `@ptrCast(@alignCast(bytes.ptr))` is at least two proof obligations: alignment and type/provenance projection.

### Phase 3 — Per-site write-up

Use this minimum shape:

```text
## site-0007: src/parser.zig:143 @ptrCast

Operation:
Invariant:
Who establishes the invariant:
Who relies on it:
Failure mode if false:
Public API reachability:
Build-mode sensitivity:
Classification:
Proof lanes:
Planned remediation:
```

### Phase 4 — Synthesize invariant clusters

Group by invariant rather than by syntax. Typical clusters:

- buffer length + offset validity;
- alignment and byte reinterpretation;
- sentinel existence;
- borrow/lifetime of returned views;
- allocator ownership and cleanup;
- `extern`/`packed` layout promise;
- FFI nullability/ownership;
- MMIO register access;
- atomic memory order and reclamation;
- vector tail/alignment;
- safety-disabled fast path.

### Phase 5 — Classify

Assign `A`, `B`, or `C`. Then challenge the result:

- Can `A` be made into `C` with a witness type?
- Is `B` folklore because the safe path is unmeasured?
- Does `C` accidentally change allocator identity, API stability, target behavior, or timing side-channel posture?
- Does the proof rely on Debug safety checks that disappear in ReleaseFast/ReleaseSmall?

Repeat until no high-risk classification flips.

### Phase 6 — Plan remediation

For each bucket:

- `A`: shrink the hazardous core, document the boundary, add layout or contract tests.
- `B`: add safe/reference path, differential tests, measurement harness, and target/build gates.
- `C`: add witness constructor or safe rewrite, equivalence tests, negative fixtures, and migration notes.

### Phase 7 — Verify

Baseline:

```bash
zig version
zig fmt --check .
find . -name '*.zig' -not -path './zig-pkg/*' -not -path './.zig-cache/*' -not -path './zig-out/*' -print0 | xargs -0 zig ast-check
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
zig build test -Doptimize=ReleaseSmall
```

Add as needed:

- target matrix: `zig build test -Dtarget=<triple>`;
- allocation failure: `std.testing.checkAllAllocationFailures`;
- fuzzing: `std.testing.fuzz` with Smith plus stored corpora;
- layout: compile-time assertions and C/header cross-checks;
- performance: benchmarks in Debug excluded; ReleaseFast/ReleaseSafe compared against fixed datasets;
- concurrency: deterministic seed, cancellation path, and stress lane.

### Phase 8 — Report

Report:

```text
Bucket counts: A/B/C
Highest-risk public APIs
Remaining boundary hazards
Fast paths requiring measurement
Witness rewrites recommended
Commands run and results
Unavailable proof lanes
Residual risk
Next action
```

## Pattern-specific guidance

### Safety-disabled scopes

`@setRuntimeSafety(false)` is justified only after validation proves the invalid states cannot reach the scope. It should be in the smallest block possible. The proof must mention why ReleaseFast/ReleaseSmall are safe, not just why Debug passes.

Template:

```zig
fn sumChecked(input: []const u32) u64 {
    // Precondition checked here.
    if (input.len > max_len) return error.TooLong;

    return sumFast(input);
}

fn sumFast(input: []const u32) u64 {
    @setRuntimeSafety(false);
    // SAFETY/ZIG-HAZARD: input length and accumulator bound were checked by sumChecked.
    // Differential tests compare this against sumScalar in Debug/ReleaseSafe/ReleaseFast.
    ...
}
```

If the disabled scope can be reached from any other call path, the proof fails. Make the fast function private or require a witness parameter.

### Pointer and slice projection

Prefer this shape:

```text
scan bytes -> validate length/alignment/sentinel/endian/lifetime -> construct witness -> project typed view
```

Do not project first and validate later. Do not mutate `slice.ptr` without updating `slice.len`; prefer deriving a new slice.

Witness examples:

- `AlignedBytes(T)` proves alignment and length for a byte range.
- `CheckedOffset` proves `offset + size <= buffer.len` without overflow.
- `BorrowedFrame` proves a backing buffer outlives projected views.
- `MappedRegister(T)` proves address, volatility, width, and target.
- `SentinelSlice(T, sentinel)` proves a sentinel exists within bounds.

### `undefined` and initialization

`undefined` means the value is not meaningful and must be overwritten before use. It is allowed for buffers and performance-sensitive initialization, but every exit path must be reviewed.

Checklist:

- Which bytes/fields are intentionally undefined?
- Where is each byte/field written?
- Can logging, comparison, hashing, error handling, `defer`, or cleanup observe it early?
- If construction fails halfway, what gets deinitialized?
- Would an explicit builder or array list be clearer?

### Layout and ABI

For every `extern` or `packed` type used as an ABI/wire/MMIO promise, record:

```zig
comptime {
    std.debug.assert(@sizeOf(Header) == 16);
    std.debug.assert(@alignOf(Header) == 4);
    std.debug.assert(@offsetOf(Header, "len") == 4);
    std.debug.assert(@bitOffsetOf(Flags, "ready") == 0);
}
```

For wire/disk formats, prefer endian-aware loads/stores over direct pointer reinterpretation unless the layout proof and target constraints are explicit.

### FFI boundaries

Each FFI boundary needs:

| Field | Required note |
| --- | --- |
| Symbol and header | Which header or extern declaration defines it. |
| Link proof | How build.zig links or translates it. |
| Nullability | Which pointers can be null and how Zig represents that. |
| Lengths | Which pointer+len pairs belong together. |
| Ownership | Who allocates, frees, and with which allocator/domain. |
| Lifetime | Whether returned pointers are borrowed, owned, thread-local, static, or invalidated by another call. |
| Errors | errno/status mapping and whether `error.OutOfMemory` can occur. |
| Threading | Callback thread, signal handler, reentrancy, and cancellation assumptions. |
| Panic/unwind | Zig panics must not cross C ABI boundaries unless the boundary explicitly handles them. |

### Atomics and concurrency

Every atomic operation needs a memory-order table:

| Operation | Location | Order | Synchronizes with | Invariant |
| --- | --- | --- | --- | --- |
| load | `state` | Acquire | Release store in `publish` | initialized payload visible |
| store | `state` | Release | Acquire load in `read` | publish after payload write |

If a pointer is published, the lifetime/reclamation proof is mandatory. Stress tests are not enough; add a sequential model or witness where possible.

### Vector/SIMD and fast loops

Do not let a fast path be the only specification. Keep a scalar/reference function and compare:

- empty input;
- length 1;
- length just below, equal to, and just above vector width;
- unaligned slices when supported;
- maximum/minimum values;
- target feature disabled/enabled.

If `@prefetch` is used, remember it does not dereference the pointer and is performance-only; do not treat it as validating memory.

## Review anti-patterns

| Anti-pattern | Why it fails | Better approach |
| --- | --- | --- |
| “No `unsafe`, therefore safe.” | Zig has no `unsafe` marker; hazards are syntax- and build-mode-dependent. | Inventory hazard operations and invariants. |
| “Debug test passed.” | Debug/ReleaseSafe may catch safety-checked IB that ReleaseFast/ReleaseSmall do not. | Run optimize-mode matrix and reject invalid states before hazards. |
| “It is fine because `unreachable` documents impossibility.” | `unreachable` is a claim, not proof. | Replace with precise error handling or prove a closed-world invariant. |
| “The C header says so.” | Translation can hide nullability, ownership, callbacks, and allocation domains. | Write an FFI contract table and wrapper tests. |
| “Packed struct is convenient for parsing.” | Packed layout is target/endianness-sensitive and packed-field pointers have special properties. | Use endian-aware parsing unless ABI/wire proof is explicit. |
| “`volatile` makes it thread-safe.” | Volatile is for MMIO/side effects, not synchronization. | Use atomics, locks, ownership transfer, or `std.Io` primitives. |
| “`undefined` is faster.” | It is only safe if every byte is overwritten before observation. | Prove write-before-read or use explicit initialization. |
| “Performance requires this.” | Without measurement, this is folklore. | Classify as `B`, add safe path, and benchmark. |

## Output checklist

- [ ] Zig version and target matrix recorded.
- [ ] Hazard scan run and interpreted.
- [ ] Every hazard site has a site ID and invariant owner.
- [ ] Every public-reachable hazard is marked.
- [ ] Every site classified as `A`, `B`, or `C` with falsifiable justification.
- [ ] `A` sites have boundary contracts and hardened safety-proof comments.
- [ ] `B` sites have safe/reference paths and measurements or are labeled `UNMEASURED`.
- [ ] `C` sites have witness rewrites and proof fixtures.
- [ ] Debug/ReleaseSafe/ReleaseFast/ReleaseSmall implications are considered.
- [ ] Allocator, layout, FFI, atomics, and vector claims have dedicated proof lanes.
- [ ] Unavailable proof lanes are labeled `SAFETY_PROOF_UNAVAILABLE` or a more specific stable label.
