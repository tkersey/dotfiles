# Zig implicit trigger taxonomy

This reference keeps the verbose Zig trigger list out of `AGENTS.md`. It strengthens, not weakens, implicit `$zig` routing: do not wait for the user to type `$zig`. Use the `zig` skill whenever the request, changed files, error output, or repo surface includes Zig-specific evidence.

Trigger on:

- `.zig`, `build.zig`, `build.zig.zon`, `zig build`, `zig test`, `zig fmt`, `zig ast-check`, `zlinter`, `zls`, `zig fetch`, `zig-pkg`, `.zig-cache`, `zig-cache`, `zig-out`, `ZIG_GLOBAL_CACHE_DIR`, `--cache-dir`, or `--global-cache-dir`.
- Zig 0.16 migration cues such as `std.Io`, `std.process.Init`, `@cImport`, `addTranslateC`, removed `@Type`, `std.meta.Int`, `std.meta.Tuple`, `std.Thread.Pool`, `std.testing.Smith`, or `--test-timeout`.
- Comptime, reflection, or codegen cues such as `comptime`, `anytype`, `@typeInfo`, `@FieldType`, `@hasDecl`, `@hasField`, `inline for`, generated types, format/schema derivation, specialization, `@compileError`, `@compileLog`, or `@setEvalBranchQuota`.
- Low-level hazard cues such as allocator ownership, `errdefer`, raw pointers, slices, sentinels, alignment, `@ptrCast`, `@alignCast`, `@ptrFromInt`, `undefined`, `unreachable`, `@setRuntimeSafety`, `extern`, `packed`, FFI/C ABI, MMIO, atomics, concurrency, `ReleaseFast`, or `ReleaseSmall`.
- Zig-project performance and cache cues such as benchmarks, profiling, `zprof`, allocator/live-byte metrics, disk pressure, cache drains, dependency fetches, or CI cache bloat.

Do not wait for a `.zig` filename when the project is known to be Zig and the issue is build, test, package, cache, performance, migration, or safety behavior.

Combine `zig` with `context-bounded-verification` or `invariant-ace` when behavior or hazard risk is material. The `zig` skill owns Zig-specific proof lanes, version checks, trigger classification, migration scans, systems scans, cache-hygiene protocol, and reporting labels.
