# Source anchors

Primary sources used for this upgrade:

- Zig 0.16.0 language reference: https://ziglang.org/documentation/0.16.0/
- Zig 0.16.0 release notes: https://ziglang.org/download/0.16.0/release-notes.html
- Zig build system guide: https://ziglang.org/learn/build-system/
- Zlinter 0.16.x README: https://raw.githubusercontent.com/KurtWagner/zlinter/0.16.x/README.md
- zprof repository/README: https://github.com/ANDRVV/zprof
- Matklad, "Steering Zig Fmt" (2026-05-08): https://matklad.github.io/2026/05/08/steering-zig-fmt.html

Official Zig 0.16.0 anchors reviewed:

- Compile-time parameters, variables, expressions, generic data structures, and `print` case study.
- `inline for`, `inline while`, `inline switch`, and `inline else` guidance.
- `@typeInfo`, `@typeName`, `@TypeOf`, `@FieldType`, `@hasDecl`, `@hasField`, and `@field`.
- `@compileLog`, `@setEvalBranchQuota`, and `@inComptime`.
- Replacement of `@Type` with `@EnumLiteral`, `@Int`, `@Tuple`, `@Pointer`, `@Fn`, `@Struct`, `@Union`, and `@Enum`.
- Zig 0.16.0 notes on no `@Array`, `@Optional`, `@ErrorUnion`, or `@ErrorSet` generated-type builtin.
- Zig 0.16.0 zero-bit tuple-field `is_comptime` behavior.
- Zig 0.16.0 Smith fuzzing interface, multiprocess fuzzing, and crash-corpus guidance.
- Choosing an allocator, `FixedBufferAllocator`, `DebugAllocator`, `std.testing.allocator`, `std.testing.FailingAllocator`, and lifetime/ownership sections.
- Pointer types, slices, sentinel pointers/slices, alignment, pointer casts, `@ptrCast`, and alternatives such as `std.mem.bytesAsSlice` and `@bitCast`.
- `volatile` as MMIO/side-effecting memory and not concurrency synchronization.
- `extern struct`, `packed struct`, packed field pointer hazards, layout introspection builtins, and MMIO examples.
- Error sets, error unions, `try`, `catch`, `errdefer`, inferred/merged error sets, and global `anyerror` guidance.
- Atomics builtins and compare-exchange guidance.
- Zig build system, cross-compilation, C translation, `@cImport` deprecation in the 0.16.0 release notes, `addTranslateC`, package `--fork`, project-local `zig-pkg`, `--test-timeout`, and build error-style changes.
- `std.Io`, `std.process.Init`/"Juicy Main", non-global args/env, preopens, current path, cancellation, and `std.testing.io`.
- Build modes: Debug, ReleaseSafe, ReleaseFast, and ReleaseSmall.


Additional hazardous-code / Illegal Behavior anchors reviewed for this update:

- Zig has no Rust-style `unsafe` keyword; hazardous Zig code must be found by operations and invariants rather than by a single marker.
- Illegal Behavior is either safety-checked or unchecked. Safety-checked Illegal Behavior panics when checks are enabled, but safety checks are disabled by default in `ReleaseFast` and `ReleaseSmall`, and can be controlled per scope with `@setRuntimeSafety`.
- `@setRuntimeSafety(false)` is a build-mode-sensitive proof obligation; invalid states must be rejected before entering the disabled-safety scope.
- `undefined` means "not a meaningful value" and must be overwritten before use; once coerced to a type, Zig cannot detect that it was undefined.
- Pointers, many-item pointers, C pointers, sentinels, `allowzero`, pointer arithmetic, `@ptrFromInt`, `@intFromPtr`, `@ptrCast`, `@alignCast`, `@constCast`, `@volatileCast`, and `@addrSpaceCast` require explicit non-null, address, alignment, lifetime, sentinel, mutability, and provenance reasoning.
- Slices have bounds checking and are generally preferred over pointers in Zig-facing APIs; mutating a slice pointer without updating length can create a bad slice state.
- `volatile` is for MMIO/side-effecting memory and is unrelated to atomics or concurrency.
- `extern struct` promises target C ABI layout; `packed struct` promises bit-level/backing-integer layout and has special pointer behavior for non-byte-aligned fields.
- Atomic builtins require documented memory orders and shared-state invariants.
- Allocator use requires caller-selected allocator contracts, leak detection, `error.OutOfMemory` propagation, and allocation-failure testing.
- FFI and C translation require nullability, length, ownership, callback/threading, allocator-domain, status/error, and panic/unwind contracts.

Additional formatting anchors reviewed for this update:

- `zig fmt` is intentionally steerable through syntactic cues already present in the file.
- For call-like comma-separated constructs, a trailing comma selects expanded one-item-per-line layout; no trailing comma allows compact layout when possible.
- For arrays, a trailing comma plus the first intentional line break can request aligned columnar layout.
- Array concatenation with `++` can compose differently shaped chunks, such as a compact command prefix followed by aligned option/value rows.
- Meaningful comments can anchor layout; dummy comments should not be used solely to pin formatter output.

Additional cache hygiene anchors reviewed for this update:

- `.zig-cache` is a generated local build cache and can be deleted to force rebuilds.
- `zig-out` is the build install prefix/output selected by `zig build --prefix`/`-p`, not merely a cache.
- `zig build --cache-dir` and `zig build --global-cache-dir` are documented advanced build options for overriding local/global cache paths.
- Zig 0.16 fetches package dependencies into project-local `zig-pkg` and stores canonical package archives under the global cache, so `zig-pkg` requires dependency-edit/fork/vendor checks before deletion.
- Zig 0.16 `zig build --fetch=needed`, `--fetch=all`, and `--fork=[path]` are relevant to post-drain dependency refetch and local override workflows.
