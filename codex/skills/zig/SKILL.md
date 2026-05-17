---
name: zig
description: "Use when implementing, reviewing, migrating, formatting/zig fmt steering, linting, testing, fuzzing, profiling, optimizing, or hardening Zig 0.16.0 code, including hazardous-code/Illegal Behavior audits: .zig files, build.zig/build.zig.zon, std.Io/process.Init migration, C interop, expert comptime/metaprogramming/reflection/codegen, allocator ownership, FFI boundaries, concurrency, safety-disabled scopes, raw pointer/layout/ABI hazards, dependencies, cache hygiene/disk-pressure operations, and measured performance work."
---

# Zig

## Governing principles

Start from the Zen of Zig: communicate intent precisely; make edge cases explicit; prefer compile errors over runtime crashes; treat memory and I/O as resources; and serve the user with small, proven improvements.

Assume Zig 0.16.0 unless the user names another version, but verify before executing version-sensitive work. If `zig version` is not `0.16.0`, label the result `VERSION_MISMATCH` and do not claim the commands validate 0.16.0 behavior.

Prefer witness-driven design. If a fact affects safety, ownership, zero-copy legality, FFI soundness, concurrency, fast-path legality, or Illegal Behavior avoidance, represent it with a type, constructor, or checked value, not a loose bool, comment, or caller convention.

Keep proof lanes separate:

- Comptime contracts prove what must be known at compile time, what gets generated or specialized, which invalid shapes fail at compile time, and which runtime path remains.
- Formatting/linting proves canonical layout, formatter steering intent, and static policy.
- Hazardous-code/Illegal Behavior auditing proves that raw operations, disabled safety checks, ABI promises, initialization, ownership, and concurrency invariants are explicit and verified.
- Builds/tests/fuzzing prove correctness.
- Benchmarks prove user-visible performance deltas.
- Profilers explain where time, allocations, locks, or bytes went.
- Cache hygiene proves which Zig cache/output/dependency paths are safe to drain, how much space is reclaimed, and whether the build refetches/rebuilds afterward.

When a lane cannot be run, say so with a stable label: `LINT_UNAVAILABLE`, `TEST_UNAVAILABLE`, `FUZZ_UNAVAILABLE`, `PROFILE_UNAVAILABLE`, `COMPTIME_PROOF_UNAVAILABLE`, `CACHE_PATH_UNDISCOVERED`, `CACHE_REBUILD_UNVERIFIED`, `HAZARD_AUDIT_UNAVAILABLE`, `SAFETY_PROOF_UNAVAILABLE`, or `UNMEASURED`.

## First-pass workflow

1. Classify the request: migration, API design, correctness bug, dependency/build work, cache/disk-pressure work, formatting/lint/tooling, hazardous-code/Illegal Behavior audit, FFI, concurrency, comptime/codegen, or performance.
2. If the request involves `comptime`, `anytype`, reflection, generated types, format/schema derivation, or specialization, produce a comptime contract before producing code.
3. Confirm repo shape: find `build.zig`, `build.zig.zon`, existing `zig build` steps, tests, benchmarks, lint steps, and formatting conventions.
4. Confirm toolchain version with `zig version` before executing 0.16.0-sensitive commands.
5. If running inside a Codex review/subagent sandbox, or if Zig reports global-cache `PermissionDenied`, apply the Codex review sandbox cache protocol before treating the result as a code verdict.
6. Run the 0.16.0 migration scan when touching code written for 0.15.x or older.
7. Run the comptime audit scan when touching generic, reflective, or generated-type code.
8. Run the systems audit scan when touching allocators, ownership, pointers, casts, C/ABI, packed/extern layout, I/O effects, atomics, concurrency, or low-level performance.
9. Run the hazardous-code audit lane when touching `@setRuntimeSafety`, `unreachable`, raw pointer casts, integer-pointer conversions, `undefined`, `extern`/`packed`, FFI, inline assembly, MMIO, atomics, vector/SIMD intrinsics, or ReleaseFast/ReleaseSmall-sensitive code.
10. Run the cache hygiene protocol when the request involves `.zig-cache`, `zig-cache`, `zig-out`, `zig-pkg`, global cache, custom `--cache-dir`/`--global-cache-dir`, disk pressure, or CI cache bloat.
11. For formatting requests, identify the intended layout before running `zig fmt`; use trailing commas, first-row array shaping, comments, or clearer intermediate declarations rather than hand-aligned whitespace.
12. Identify hazard classes and proof requirements before editing.
13. Make the smallest change that satisfies the contract.
14. Re-run the appropriate proof lanes and report exact commands plus outcomes.

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
| `cache/disk-pressure` | Cache/output taxonomy, dry-run inventory, dependency-edit protection, exact reclaimed-size report, and post-drain fetch/build validation. |
| `comptime/metaprogramming` | Comptime contract, shape validation before reflection, intentional diagnostics, positive and negative fixtures, and compile-time cost/binary-size review when specialization cardinality is nontrivial. |
| `formatting/zig-fmt-steering` | Formatter intent described in source-level cues, `zig fmt`/`zig fmt --check` run, and diff reviewed for token-level steering changes such as trailing-comma add/remove. |
| `zig-hazard/illegal-behavior` | Inventory of hazard sites, A/B/C classification, invariant owner, safety-proof comment or witness type, negative fixtures, and Debug/ReleaseSafe/ReleaseFast validation. |

Satisfy every active hazard class. Do not use a green smoke test as proof for hazardous pointer work, FFI, lock-free, layout-sensitive, optimizer-sensitive, or allocation-sensitive code.

## Zig hazardous-code and Illegal Behavior audit

Do not model Zig safety work as Rust `unsafe` removal. Zig has no `unsafe` keyword. Model it as a hazardous-code audit: find every operation whose correctness depends on invariants that the type checker, runtime safety checks, build mode, or ABI cannot fully enforce, then make those invariants explicit.

Trigger this lane for requests about unsafe-equivalent Zig code, Illegal Behavior, `@setRuntimeSafety`, raw pointers, pointer/integer casts, `undefined`, packed or extern layout, FFI, inline assembly, atomics, MMIO, allocator/lifetime bugs, zero-copy parsing, manual vector/SIMD paths, `ReleaseFast`/`ReleaseSmall` safety differences, or “prove this cannot crash/corrupt memory”.

### Mental model

A Zig hazard site is any source location where a wrong invariant can turn into:

- Unchecked Illegal Behavior;
- safety-checked Illegal Behavior that becomes unchecked because the build mode or `@setRuntimeSafety(false)` disables checks;
- ABI/layout mismatch with C, hardware, file, or wire format;
- lifetime, ownership, initialization, or allocator misuse;
- data race, invalid atomic ordering, or cancellation/lifetime bug;
- silent logic corruption from `undefined`, wrong endian assumptions, wrong sentinel assumptions, or invalid pointer provenance.

For each hazard site, separate the layers:

```text
caller obligations -> validation/witness -> hazardous operation -> projected safe API -> verification lane
```

The preferred end state is not always “remove the hazard.” It is “small hazardous core, explicit proof, safe wrapper, reproducible verification.”

### Classification buckets

Every hazard site must be classified exactly once, with a falsifiable justification:

| Bucket | Meaning | Required result |
| --- | --- | --- |
| `A/IRREDUCIBLE_BOUNDARY` | Zig cannot express the operation safely because it crosses an ABI, hardware, OS, allocator, inline-asm, MMIO, atomic primitive, or representation boundary. | Thin boundary module, caller/callee contract table, hardened safety-proof comment, wrapper tests, layout/target proof, and a reason safe alternatives fail. |
| `B/PERF_OR_FOOTPRINT_ONLY` | A safer Zig formulation exists, but the hazard is kept for measured speed, code size, allocation shape, or target-specific behavior. | Safe/reference implementation, feature or build option to exercise it when practical, benchmark/profile evidence, differential tests, and Debug/ReleaseSafe/ReleaseFast proof. |
| `C/REFACTORABLE_TO_WITNESS` | The hazard can be removed or moved behind a checked value/witness without violating the API or performance budget. | Concrete rewrite plan, witness constructor, equivalence tests, negative fixtures, and migration notes. |

Misclassification is a serious error. “Fast” is not `A`; it is `B` until measurement shows otherwise. “Existing SAFETY comment says so” is not proof; trace the invariant through callers and build modes. If a site mixes categories, split the inner hazard from the outer boundary and classify each part.

### Full hazardous-code audit workflow

For a full audit request, after confirming the target path and write policy, create an audit directory such as `<project>/.zig-hazard-audit/` unless the user asks for a report-only chat response. Keep project source files read-only until remediation is explicitly authorized.

Required phases:

1. **Scope** — record Zig version, target triples, build modes, packages, public APIs in scope, and hazards explicitly out of scope.
2. **Enumerate** — run `scripts/zig_hazard_audit_rg.sh` or the equivalent scan, then inspect `build.zig`, `build.zig.zon`, generated imports, translated C, and target-specific source directories.
3. **Normalize** — group hits into stable site IDs by file, line, operation, public reachability, target condition, and owning invariant.
4. **Per-site write-up** — name the invariant, who establishes it, what happens if it is false, and which proof lanes cover it.
5. **Synthesize** — cluster sites by shared invariant: pointer/provenance, layout/ABI, initialization, allocator/lifetime, FFI, concurrency, IO/effects, vector/perf, or build-mode safety.
6. **Classify** — assign `A`, `B`, or `C`; repeat until no `A` can be defeated by a safer witness design and no `B` lacks measurements.
7. **Plan** — for `A`, shrink and document the boundary; for `B`, provide safe/reference path plus measurements; for `C`, produce a witness-based rewrite.
8. **Verify** — run formatting/static, build/test, optimization-mode, allocation-failure, fuzz/differential, target/layout, and profile lanes as applicable.
9. **Report** — include counts by bucket, highest-risk public surfaces, exact commands, unavailable lanes, residual risk, and next recommended remediation.
10. **Remediate only after authorization** — edit the active checkout or ordinary branch only; preserve user changes; do not widen scope silently.

### Hazard inventory scan

Use the script when present:

```bash
scripts/zig_hazard_audit_rg.sh .
```

Equivalent manual scan:

```bash
rg -n --hidden \
  "@setRuntimeSafety\((false|true)\)|unreachable|catch unreachable|\.\?|undefined|@ptrCast|@alignCast|@addrSpaceCast|@constCast|@volatileCast|@ptrFromInt|@intFromPtr|@fieldParentPtr|@bitCast|@memcpy|@memmove|@memset|\[\*c\]|\[\*\]|allowzero|sentinel|extern (\"[^\"]+\" )?fn|pub extern|export fn|@extern|@export|@cImport|@cVa(Start|Arg|Copy|End)|asm( volatile)?|volatile|packed (struct|union)|extern (struct|union|enum)|@offsetOf|@bitOffsetOf|@bitSizeOf|@sizeOf|@alignOf|@atomicLoad|@atomicStore|@atomicRmw|@cmpxchg(Weak|Strong)|std\.atomic|Atomic|std\.Thread|Thread\.Mutex|Thread\.Condition|Thread\.ResetEvent|@Vector|@shuffle|@select|@reduce|@prefetch|Allocator|std\.heap|arena|deinit\(|errdefer|@panic|@trap" \
  -g"*.zig" -g"build.zig" \
  -g"!zig-pkg/**" -g"!.zig-cache/**" -g"!zig-out/**"
```

Interpretation:

- `@setRuntimeSafety(false)` is a proof amplifier. Require a local invariant comment and tests showing invalid states are rejected before entering the disabled-safety scope. Prefer narrowing the scope to the smallest block.
- `unreachable`, `catch unreachable`, `.?`, invalid enum/error casts, exact arithmetic, and unchecked shifts require a closed-world proof or an error-returning alternative.
- `undefined` is valid only when every byte or field is overwritten before observation. Prefer helper constructors that make initialization order obvious; test early-return and error paths.
- Raw pointer operations require proof of non-nullness, address validity, alignment, length, initialized bytes, aliasing/mutability, lifetime, provenance, sentinel existence, and target address space.
- `[*]T` and `[*c]T` should usually be converted to slices, optional pointers, or opaque handles at the boundary. Keep many-item and C pointers out of core APIs.
- `@ptrCast`, `@alignCast`, and `@ptrFromInt` should be behind a constructor such as `AlignedBytes`, `MappedRegister`, `CheckedOffset`, or `BorrowedFrame`.
- `extern` and `packed` layout require target-specific size, alignment, offset/bit-offset, endian, and call-convention proof.
- `volatile` is for MMIO or side-effecting memory, not thread synchronization. Concurrency requires atomics, locks, ownership transfer, or `std.Io` primitives.
- Atomics require a shared-state invariant, memory-order table, sequential model, and target/build-mode test lane.
- `@prefetch`, vectors, `@shuffle`, `@select`, `@reduce`, and unchecked hot loops are usually `B/PERF_OR_FOOTPRINT_ONLY` until differential tests and measurements justify them.
- Allocator and deinit hits require ownership, cleanup, leak, allocation-failure, and error-path rollback proof.

### Proof obligations by hazard surface

| Surface | Required proof |
| --- | --- |
| Safety-disabled scope | Smallest possible scope, precondition witness, invalid-input rejection before entry, Debug/ReleaseSafe/ReleaseFast tests, and performance evidence if kept for speed. |
| Pointer/provenance | Source allocation or MMIO mapping, address range, alignment, initialized bytes, lifetime, aliasing/mutability, sentinel if any, and no slice `.ptr` corruption. |
| `undefined`/initialization | Write-before-read table, error/early-return cleanup, no observation through formatting/logging/comparison, and tests that exercise partial-initialization failure paths. |
| Layout/ABI/wire/MMIO | `@sizeOf`, `@alignOf`, `@offsetOf`/`@bitOffsetOf`, backing integer, endian rule, target matrix, and C/header or hardware register source. |
| FFI/C/asm | Boundary contract, translated-header provenance, nullability, ownership transfer, allocator domain, callback/threading model, errno/status mapping, and panic/unwind policy. |
| Atomics/concurrency | Shared-state invariant, memory order per operation, happens-before story, cancellation/deinit ordering, stress/replay test, and sequential reference model where possible. |
| Allocator/lifetime | Allocator identity, owner/freeing side, borrowed-vs-owned states, `errdefer` rollback, leak check, and `checkAllAllocationFailures` coverage. |
| Vector/SIMD/perf | Scalar reference path, differential tests across odd lengths/alignment/tails, target feature gate, benchmarks, and ReleaseSafe/ReleaseFast comparison. |

### Verification matrix for hazard work

Always prefer the repo’s build steps, but a hazard review should consider this matrix:

```bash
zig version
zig fmt --check .
find . -name '*.zig' -not -path './zig-pkg/*' -not -path './.zig-cache/*' -not -path './zig-out/*' -print0 | xargs -0 zig ast-check
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
zig build test -Doptimize=ReleaseSmall
zig build test --test-timeout 500ms
```

Add target lanes for any claim that depends on ABI, endian, pointer width, vector feature, OS API, or C calling convention. Add allocation-failure, fuzzing, and benchmark lanes only where they prove an active obligation; do not use them as decorative checkboxes.

### Safety-proof comment shape

Use comments as reviewable proof, not as a substitute for validation:

```zig
// SAFETY/ZIG-HAZARD:
// Boundary: @ptrCast from validated byte storage to Header.
// Established by: HeaderBytes.validate() checks len >= @sizeOf(Header),
// alignment >= @alignOf(Header), backing storage lifetime >= returned view,
// and endian fields are read with explicit little-endian helpers.
// Caller obligation: keep the original buffer alive and immutable while HeaderView exists.
// Verification: layout_asserts test, fuzz corpus testdata/fuzz/header/, and
// Debug/ReleaseSafe/ReleaseFast differential test against parseHeaderScalar().
const header: *const Header = @ptrCast(aligned.ptr);
```

If the proof cannot be stated locally, introduce a witness type or move the hazardous operation closer to the validator.

### Remediation rules

- Prefer “validate then project” over “cast then check.”
- Prefer slices over many-item pointers in Zig-facing code.
- Prefer explicit optional pointers over `allowzero` unless address zero is a real hardware/ABI value.
- Prefer endian-aware loads/stores over pointer reinterpretation for wire/disk formats.
- Prefer ordinary `struct` plus serialization code over `extern`/`packed` when no ABI promise is required.
- Prefer `std.Io` capabilities, owned tasks, and cancellation-aware groups over hidden global effects or migrated thread-pool assumptions.
- Keep FFI and MMIO hazard cores small and wrap them in safe Zig APIs with checked constructors.
- Treat `ReleaseFast` and `ReleaseSmall` as proof lanes, not just performance modes, because many safety checks are disabled there.

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
scripts/zig_hazard_audit_rg.sh .
```

Interpretation:

- Allocator hits require ownership, cleanup, and allocation-failure review.
- Pointer/cast hits require length, alignment, sentinel, lifetime, provenance, and aliasing proof.
- `extern`/`packed`/offset hits require layout, endian, ABI, and target validation.
- `std.Io`/process/env/current-path hits require explicit effect capability review.
- Atomic/thread/synchronization hits require shared-state invariant and memory-order review.
- `anyerror`, `catch unreachable`, `panic`, and `unreachable` require failure-contract review.
- `@cImport` should usually migrate toward build-system C translation in new Zig 0.16 code.
- `@setRuntimeSafety(false)`, `undefined`, `unreachable`, `catch unreachable`, and unchecked hot paths require a hazardous-code classification, not just a local explanation.

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

Use `references/unsafe_boundary_playbook.md` and `references/hazardous_code_audit_playbook.md` for `@ptrCast`, `@ptrFromInt`, `@alignCast`, `[*]T`, `[*c]T`, sentinel pointers/slices, `volatile`, zero-copy projection, safety-disabled scopes, `undefined`, or C-pointer wrapping.

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

## Cache hygiene and disk-pressure operations

Use `references/cache_hygiene_playbook.md` when the user reports disk pressure, stale Zig caches, `No space left on device`, CI cache bloat, or asks about `.zig-cache`, `zig-cache`, `zig-out`, `zig-pkg`, the global cache, `--cache-dir`, or `--global-cache-dir`.

Do not blindly delete paths. Produce a cache contract:

1. which Zig version and cache layout are in use;
2. which paths are local build cache, generated output, dependency working tree, or global shared cache;
3. which paths are safe to delete immediately;
4. which paths require modification/fork checks;
5. how much space will be reclaimed;
6. how the build will be refetched/revalidated afterward;
7. how future builds should route or bound cache growth.

Rules:

- Inventory before deletion with `scripts/zig_cache_report.sh` or equivalent `du`/`zig env` commands.
- Treat `.zig-cache` and `zig-cache` as disposable local build cache.
- Treat `zig-out` as generated output/install prefix, not merely cache; delete only if the outputs are no longer needed.
- Treat `zig-pkg` as a Zig 0.16 dependency working tree; do not delete it automatically if modified, forked, vendored, or intentionally committed.
- Treat global cache as shared infrastructure; drain explicitly and preferably by age/size policy.
- Default destructive scripts to dry-run. Require explicit `--yes` for deletion.
- Refuse cache drains while active Zig builds are detected.
- After touching dependency/global cache state, run `zig build --fetch=needed` or `zig build --fetch=all`, then `zig build --summary all` or the repo's normal build lane.
- For recurring disk pressure, recommend `--cache-dir` and `--global-cache-dir` routing instead of repeated manual deletion.

Useful commands:

```bash
scripts/zig_cache_report.sh .
scripts/zig_cache_drain.sh --root .
scripts/zig_cache_drain.sh --root . --yes
scripts/zig_cache_drain.sh --root . --include-zig-out --include-global --older-than 14
scripts/zig_cache_rebuild_probe.sh .
```

Cache result labels:

- `CACHE_AUDITED`
- `CACHE_DRY_RUN_ONLY`
- `CACHE_LOCAL_DRAINED`
- `CACHE_OUTPUT_DRAINED`
- `CACHE_GLOBAL_DRAINED`
- `CACHE_ZIG_PKG_DRAINED`
- `CACHE_ZIG_PKG_SKIPPED`
- `CACHE_MODIFIED_DEPENDENCY_UNTOUCHED`
- `CACHE_ACTIVE_BUILD_REFUSED`
- `CACHE_REVIEW_SANDBOX_PERMISSION_DENIED`
- `CACHE_REBUILD_VERIFIED`
- `CACHE_REBUILD_UNVERIFIED`
- `CACHE_PATH_UNDISCOVERED`

Use `references/cache_ci_policy.md` for CI cache keys, TTLs, and drain order.

### Codex review sandbox cache protocol

Use this protocol when Zig proof commands run inside native Codex review, a Codex subagent, or any sandbox where writable roots may exclude the default Zig global cache. Typical failure evidence includes:

- `unable to load 'test_runner.zig': PermissionDenied`;
- `unable to load 'std.zig': PermissionDenied`;
- `unable to load 'ubsan_rt.zig': PermissionDenied`;
- `failed to check cache: manifest_create PermissionDenied`;
- a Zig command showing `--global-cache-dir /Users/.../.cache/zig` inside a restricted review/subprocess sandbox.

Before the first Zig proof command in that environment, prefer an explicit writable global cache:

```bash
ZIG_GLOBAL_CACHE_DIR=/private/tmp/zig-cache-review zig build test --summary all
ZIG_GLOBAL_CACHE_DIR=/private/tmp/zig-cache-review zig build lint -- --max-warnings 0
```

If `/private/tmp` is unavailable but the repository root is writable, use a repo-local global cache:

```bash
mkdir -p .zig-cache/global
ZIG_GLOBAL_CACHE_DIR="$PWD/.zig-cache/global" zig build test --summary all
```

The same rule applies to focused proof lanes:

```bash
ZIG_GLOBAL_CACHE_DIR=/private/tmp/zig-cache-review zig build test --summary all -- --test-filter "<filter>"
```

Do not treat default-global-cache `PermissionDenied` as a code verdict. Classify it as `CACHE_REVIEW_SANDBOX_PERMISSION_DENIED`, rerun the exact affected proof with a writable global cache, and keep the local code verdict separate from the review transport/environment verdict. If the rerun passes, report both the original cache failure and the successful writable-cache proof. If the rerun fails for a non-cache reason, adjudicate the new failure normally.

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

## Linting, formatting, and static checks

Use the repo's existing lint surface first. If `zig build lint` exists, treat it as a hard gate and run the repo-supported invocation. If lint is absent, mark `LINT_UNAVAILABLE` unless the user asked to add tooling or the change safely fits a lint bootstrap.

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
- Treat `zig fmt` as steerable. Add or remove syntax-level layout cues before formatting instead of fighting the formatted result with manual whitespace.
- For call-like comma-separated constructs, a trailing comma is a layout decision: without it, `zig fmt` may collapse the construct to one line; with it, `zig fmt` expands to one item per line.
- For arrays and array literals, a trailing comma plus an intentional first line break can request columnar layout. `zig fmt` uses the first row width as the column shape and aligns later rows.
- Use `++` to compose array chunks when a single array needs mixed layout, such as a compact command prefix followed by aligned `--flag`, `value` pairs.
- Comments are layout anchors. Keep real explanatory comments; avoid dummy comments whose only purpose is to pin formatter output.
- Prefer format-shaping only when it makes the domain structure clearer. Do not change data shape or introduce misleading grouping merely to obtain a preferred layout.
- `zig ast-check` is a syntax/simple-compile-error lane for `.zig` files. Do not run it on `build.zig.zon`.
- Do not equate `zig ast-check` with a full semantic compile. Follow with `zig build`/`zig test`.
- For third-party linting in Zig 0.16.x, prefer `zlinter#0.16.x`. Use `#master` only when intentionally targeting 0.17.x-dev.
- Do not enable all `zlinter` built-in rules as a permanent CI default without review; upstream calls that mode pedantic and mainly suitable for exploration. Use a curated rule set, then add more rules incrementally.
- Run `--fix` only on a clean working tree or after taking a backup. Re-run until no fixes are applied, then review the diff before proceeding.

### Steering `zig fmt`

Use `zig fmt` layout cues intentionally:

```zig
// No trailing comma: prefer compact call layout when it fits.
f(1, 2,
    3);

// zig fmt:
f(1, 2, 3);

// Trailing comma: force one argument per line.
f(1, 2,
    3,
);

// zig fmt:
f(
    1,
    2,
    3,
);
```

For array data, use an early line break plus a trailing comma to communicate a table shape:

```zig
const matrix = .{ 1, 2, 3,
    4, 5, 6, 7, 8, 9, 10, 11,
};
```

`zig fmt` preserves the intent as aligned rows with the first row defining the column count. For heterogeneous command vectors or option tables, compose chunks with `++` so each chunk can have its own readable shape:

```zig
try run(&(.{ "aws", "s3", "sync", path, url } ++ .{
    "--include",            "*.html",
    "--include",            "*.xml",
    "--metadata-directive", "REPLACE",
    "--cache-control",      "max-age=0",
}));
```

Review protocol:

```bash
zig fmt path/to/file.zig
git diff -- path/to/file.zig
zig fmt --check .
```

When a diff is formatting-only, identify the intentional token-level steering change, usually a trailing-comma add/remove, first-row array break, meaningful comment, or introduction of an intermediate declaration. Do not claim `zig fmt` proves semantics; follow with the repo's build/test lanes.

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

For optimizer-sensitive or hazardous-code logic, run all relevant modes. Treat ReleaseFast and ReleaseSmall as safety proof lanes because runtime safety checks may be disabled there:

```bash
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
zig build test -Doptimize=ReleaseSmall
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

Validation should return a small witness type such as `ValidatedFrame`, `BorrowedView`, `NonEmptySlice`, `AlignedBytes`, or `CheckedOffset`. Do not expose typed views, zero-copy projections, `@ptrCast`-based decoding, `@setRuntimeSafety(false)` fast paths, or SIMD loads until validation succeeds.

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
| `std.meta.Int(.signed, bits)` | `@Int(.signed, bits)` |
| `std.meta.Int(.unsigned, bits)` | `@Int(.unsigned, bits)` |
| `std.meta.Tuple(&.{ T, U })` | `@Tuple(&.{ T, U })` |
| generated pointer type through `@Type` | `@Pointer(...)` |
| generated function type through `@Type` | `@Fn(...)` |
| generated struct/union/enum through `@Type` | `@Struct(...)`, `@Union(...)`, `@Enum(...)` |
| enum literal type through `@Type` | `@EnumLiteral()` |

Prefer normal syntax for arrays, optionals, error unions, opaques, and explicit error sets. In migrations, remove old `@Type` helpers instead of building compatibility wrappers unless a large API requires a staged migration.

### Diagnostics and negative proof

Compile-time APIs need deliberate diagnostics:

- Validate shape before projecting fields, declarations, payloads, or tags.
- Put `@compileError` at the public API boundary with the API name and `@typeName(T)`.
- Keep error messages actionable: expected shape, actual shape, and one valid example.
- Use positive fixtures for supported types and negative compile-fail fixtures or documented manual probes for unsupported shapes.
- Remove `@compileLog` before committing unless the user explicitly asked for active debugging output.

### Compile-time cost governance

Specialization is a design cost:

- Name which values are truly required at comptime and keep everything else runtime.
- Avoid high-cardinality comptime values such as user strings, file contents, or runtime-like data unless the generated artifact is the point.
- Treat `@setEvalBranchQuota` as a smell. It is acceptable for a bounded compile-time parser/table generator when the bound is stated and tested.
- For large generated tables or many specializations, report binary-size/build-time risk and consider a compact runtime plan.

## Reporting expectations

When answering Zig work, report:

- active hazard classes and hazardous-code bucket counts when relevant;
- version observed or `VERSION_MISMATCH`;
- exact commands run and outcomes;
- proof lanes unavailable with stable labels;
- format-steering tokens changed when formatting is relevant;
- remaining risk and the next proof lane needed;
- any `@setRuntimeSafety(false)`, raw pointer, `undefined`, FFI, layout, atomic, or ReleaseFast/ReleaseSmall-sensitive hazard that remains.

Never imply that formatting, linting, `ast-check`, a smoke test, or a benchmark alone proves unsafe memory, ABI layout, allocation failure handling, concurrency correctness, or FFI soundness.
