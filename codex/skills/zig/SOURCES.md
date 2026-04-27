# Source anchors

Primary sources used for this upgrade:

- Zig 0.16.0 language reference: https://ziglang.org/documentation/0.16.0/
- Zig 0.16.0 release notes: https://ziglang.org/download/0.16.0/release-notes.html
- Zig build system guide: https://ziglang.org/learn/build-system/
- Zlinter 0.16.x README: https://raw.githubusercontent.com/KurtWagner/zlinter/0.16.x/README.md
- zprof repository/README: https://github.com/ANDRVV/zprof

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

Additional cache hygiene anchors reviewed for this update:

- `.zig-cache` is a generated local build cache and can be deleted to force rebuilds.
- `zig-out` is the build install prefix/output selected by `zig build --prefix`/`-p`, not merely a cache.
- `zig build --cache-dir` and `zig build --global-cache-dir` are documented advanced build options for overriding local/global cache paths.
- Zig 0.16 fetches package dependencies into project-local `zig-pkg` and stores canonical package archives under the global cache, so `zig-pkg` requires dependency-edit/fork/vendor checks before deletion.
- Zig 0.16 `zig build --fetch=needed`, `--fetch=all`, and `--fork=[path]` are relevant to post-drain dependency refetch and local override workflows.
