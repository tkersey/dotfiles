# Zig skill upgrade notes — comptime + systems + cache hygiene expert edition

This bundle supersedes the previous `zig_skill_upgrade`, `zig_skill_comptime_expert`, and `zig_skill_ultimate_systems_bundle` bundles.

## High-impact fixes retained from the 0.16.0 upgrade

1. Updated lint guidance from `zlinter#master` to `zlinter#0.16.x` for stable Zig 0.16.x.
2. Split built-in formatting/static checks from third-party linting.
3. Added `zig fmt --check` and `.zig`-only `zig ast-check` baseline.
4. Replaced "enable every zlinter rule" default with a curated-rule default and warning about pedantic all-rules mode.
5. Updated `zprof` guidance from v3-era terminology to v4.0.0 terminology.
6. Updated `zprof` metric names from stale `live_bytes`/`live_peak` to v4 `live_requested`/`peak_requested`.
7. Added release-note-aware profiling caveat for the new ELF linker and DWARF-dependent profilers.
8. Made version mismatch handling explicit instead of silently assuming the installed toolchain validates 0.16.0 behavior.
9. Added stable unavailable-proof labels: `LINT_UNAVAILABLE`, `TEST_UNAVAILABLE`, `FUZZ_UNAVAILABLE`, `PROFILE_UNAVAILABLE`, `COMPTIME_PROOF_UNAVAILABLE`, `UNMEASURED`, `VERSION_MISMATCH`.
10. Reduced duplicate/overlapping workflow text and made the proof lanes more operational.

## Comptime expert subsystem retained and integrated

1. Added a first-class comptime contract requirement for all comptime-heavy work.
2. Added `references/comptime_playbook.md`, a dedicated expert playbook for generics, type factories, reflection, generated types, compile-time parsers, diagnostics, testing, and cost governance.
3. Added a comptime decision tree covering `comptime T: type`, `anytype`, generated types, reflection, `inline for`, `inline else`, ABI/layout assertions, and runtime/comptime dual paths.
4. Added a dedicated comptime audit scan for `comptime`, `anytype`, `@typeInfo`, `@FieldType`, `@hasDecl`, `@hasField`, `@compileError`, `@compileLog`, `@setEvalBranchQuota`, `@inComptime`, inline loops, generated-type builtins, removed `@Type`, `std.meta.Int`, `std.meta.Tuple`, and `.is_comptime` assumptions.
5. Added Zig 0.16 generated-type migration guidance: `@Int`, `@Tuple`, `@Pointer`, `@Fn`, `@Struct`, `@Union`, `@Enum`, and `@EnumLiteral`.
6. Added reflection architecture guidance: `classifyType -> validateType -> derivePlan -> runtime function`.
7. Added `anytype` discipline, inline-loop rules, diagnostics rubric, compile-time cost governance, and positive/negative proof requirements.
8. Added `references/comptime_patterns.zig` with adaptable examples.

## New low-level systems expert subsystem

1. Added a top-level systems engineering contract covering ownership, allocator choice, lifetime/cleanup, pointer/slice/sentinel/alignment, error sets, effects, layout/ABI/endian, concurrency/atomic ordering, validation matrix, tests, fuzzing, and profiling evidence.
2. Added `references/memory_ownership_playbook.md` for allocator strategy, owned/borrowed/transferred/arena-owned data, `defer`/`errdefer`, managed vs unmanaged containers, arena discipline, and allocation-failure testing.
3. Added `references/unsafe_boundary_playbook.md` for pointers, slices, sentinel types, casts, C pointers, alignment, lifetime, zero-copy views, and volatile/MMIO discipline.
4. Added `references/layout_abi_playbook.md` for `extern`, `packed`, ABI, MMIO, wire formats, endian parsing, layout proof tables, and target-matrix validation.
5. Added `references/error_failure_playbook.md` for precise error sets, `anyerror` avoidance, `try`/`catch`, `errdefer`, boundary error mapping, and cleanup-after-failure tests.
6. Added `references/io_effects_playbook.md` for Zig 0.16 `std.Io`, `std.process.Init`, args/env capture, current path, explicit capabilities, cancellation, and deterministic effect testing.
7. Added `references/build_toolchain_playbook.md` for build.zig/build.zig.zon, cross-compilation, package pins, `zig-pkg`, `--fork`, C translation, release modes, and reproducibility.
8. Added `references/atomics_concurrency_playbook.md` for shared-state invariants, atomics, memory order, lock-free review, volatile-vs-atomic distinction, cancellation, and concurrency tests.
9. Added `references/testing_failure_discovery_playbook.md` for unit/build/integration tests, Smith fuzzing, allocation-failure tests, compile-fail fixtures, timeouts, optimizer matrices, and reproduction discipline.
10. Added `references/performance_engineering_playbook.md` for benchmark-first optimization, decomposition, zprof allocation metrics, CPU profiling, cache layout, SIMD, binary size, and linker/debug-info caveats.
11. Added `references/systems_contract_template.md` and `references/systems_patterns.zig` for practical review/report scaffolding and example snippets.
12. Added `scripts/systems_audit_rg.sh` for project-level scans of allocators, ownership, raw pointers, layout, I/O, atomics, error paths, C interop, build modes, and migration cues.
13. Updated `agents/openai.yaml` and trigger-audit notes with memory/allocator, unsafe-boundary, ABI/layout, I/O/effects, atomics, error-set, and performance-routing terms.

## New cache hygiene and disk-pressure subsystem

1. Added a top-level cache hygiene lane for Zig disk-pressure reports, stale caches, `No space left on device`, CI cache bloat, `.zig-cache`, `zig-cache`, `zig-out`, `zig-pkg`, global cache, `--cache-dir`, and `--global-cache-dir`.
2. Added `references/cache_hygiene_playbook.md` with cache/output taxonomy, safe drain order, dependency-edit protection, dry-run policy, result labels, fast triage commands, cache relocation guidance, CI rules, and review checklist.
3. Added `references/cache_ci_policy.md` with CI cache key inputs, recommended layout, drain order, and anti-patterns.
4. Added `scripts/zig_cache_report.sh` for non-destructive inventory of project-local and global Zig cache/output candidates.
5. Added `scripts/zig_cache_drain.sh`, a guarded dry-run-first drain script with `--yes`, `--include-zig-out`, `--include-zig-pkg`, `--include-global`, `--global-path`, and `--older-than` controls.
6. Added `scripts/zig_cache_rebuild_probe.sh` to verify `zig build --fetch=needed` and `zig build --summary all` after cache draining.
7. Added cache result labels: `CACHE_AUDITED`, `CACHE_DRY_RUN_ONLY`, `CACHE_LOCAL_DRAINED`, `CACHE_OUTPUT_DRAINED`, `CACHE_GLOBAL_DRAINED`, `CACHE_ZIG_PKG_DRAINED`, `CACHE_ZIG_PKG_SKIPPED`, `CACHE_MODIFIED_DEPENDENCY_UNTOUCHED`, `CACHE_ACTIVE_BUILD_REFUSED`, `CACHE_REBUILD_VERIFIED`, `CACHE_REBUILD_UNVERIFIED`, and `CACHE_PATH_UNDISCOVERED`.
8. Updated `SKILL.md`, `agents/openai.yaml`, and trigger-audit notes so cache/disk-pressure work routes to the Zig skill and is handled as operational systems work, not as blind `rm -rf`.

## Files in this bundle

- `SKILL.md` — drop-in replacement.
- `references/comptime_playbook.md` — expert comptime reference.
- `references/comptime_patterns.zig` — comptime examples and review snippets.
- `references/memory_ownership_playbook.md` — allocator and ownership reference.
- `references/unsafe_boundary_playbook.md` — pointer/cast/sentinel/alignment reference.
- `references/layout_abi_playbook.md` — layout/ABI/MMIO/wire-format reference.
- `references/error_failure_playbook.md` — error-set and failure-path reference.
- `references/io_effects_playbook.md` — Zig 0.16 explicit I/O/effects reference.
- `references/build_toolchain_playbook.md` — build/cross-compilation/package/C interop reference.
- `references/atomics_concurrency_playbook.md` — concurrency/atomics/cancellation reference.
- `references/testing_failure_discovery_playbook.md` — testing/fuzzing/failure-discovery reference.
- `references/performance_engineering_playbook.md` — performance/profiling/cache-layout reference.
- `references/cache_hygiene_playbook.md` — Zig cache taxonomy, dry-run drain protocol, dependency-edit protection, and post-drain validation reference.
- `references/cache_ci_policy.md` — CI cache key, TTL, and drain-order guidance.
- `references/systems_contract_template.md` — systems review/report template.
- `references/systems_patterns.zig` — systems engineering code patterns.
- `references/linting_playbook.md` — modular lint reference.
- `references/profiling_playbook.md` — profiling reference.
- `references/boundary_witness.zig` — scan/validate/project witness example.
- `references/fuzz_differential.zig` — Smith fuzzing template.
- `references/fail_nth_alloc.zig` — allocation-failure coverage template.
- `references/ffi_contract_template.md` — FFI review table.
- `agents/openai.yaml` — refreshed agent description/prompt.
- `scripts/comptime_audit_rg.sh` — comptime audit command.
- `scripts/systems_audit_rg.sh` — systems hazard audit command.
- `scripts/zig_cache_report.sh` — non-destructive cache/output inventory command.
- `scripts/zig_cache_drain.sh` — guarded dry-run-first cache drain command.
- `scripts/zig_cache_rebuild_probe.sh` — post-drain fetch/build validation command.
- `scripts/zig_trigger_audit_update_notes.md` — trigger terms to add to trigger-audit routing.
- `SOURCES.md` — primary source anchors used for the 0.16.0/comptime/systems upgrade.

## Validation note

The markdown and scripts were assembled in this environment, but the Zig snippets were not compiled here because a Zig 0.16.0 toolchain is not installed in the container. Validate in the target repository with `zig version`, `zig fmt --check`, `.zig`-only `zig ast-check`, `zig test`, and the repo's `zig build`/`zig build test` steps. For low-level changes, also run relevant `Debug`, `ReleaseSafe`, `ReleaseFast`, target-matrix, allocation-failure, fuzzing, and profiling lanes. For cache drains, validate first with `scripts/zig_cache_report.sh`, then use `scripts/zig_cache_drain.sh` in dry-run mode before any destructive run, and finish with `scripts/zig_cache_rebuild_probe.sh` when dependency/global cache state was touched.
