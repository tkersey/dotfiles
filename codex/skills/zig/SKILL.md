---
name: zig
description: "Use when implementing or reviewing Zig 0.15.2 code and toolchain workflows: editing .zig files, build.zig/build.zig.zon dependency changes, lint/test/run/fmt/fetch/build commands, profiling and performance work, comptime/reflection/codegen, witness-driven parsing and ownership, FFI boundary hardening, concurrency or lock-free code, dependency provenance, and measured optimization with explicit proof lanes."
---

# Zig

## Zen of Zig
- Communicate intent precisely.
- Edge cases matter.
- Favor reading code over writing code.
- Only one obvious way to do things.
- Runtime crashes are better than bugs.
- Compile errors are better than runtime crashes.
- Incremental improvements.
- Avoid local maximums.
- Reduce the amount one must remember.
- Focus on code rather than style.
- Resource allocation may fail; resource deallocation must succeed.
- Memory is a resource.
- Together we serve the users.

## Operating contract
- Start from the Zen of Zig above. If a recommendation conflicts with it, revisit the recommendation before proceeding.
- Assume Zig 0.15.2 unless the user explicitly requests another version.
- Prefer witness-driven APIs: if a fact matters to safety, zero-copy legality, FFI soundness, or fast-path legality, represent it in a type or constructor, not a loose bool or comment.
- Treat hazard class -> proof obligation mapping as required.
- Prefer minimal incisions with explicit proof signals.
- If the repo already exposes `zig build lint`, treat it as a hard gate. If lint is missing, prefer bootstrapping when safe; otherwise state `LINT_UNAVAILABLE` and compensate with stronger correctness evidence.
- Keep fast paths benchmarked, but keep safety checks on during correctness validation.
- Treat benchmarking and profiling as separate lanes: benchmarks prove the delta, profilers explain where the time or bytes went.

## Baseline requirements
- Confirm toolchain version first:

```bash
zig version
```

- If the version is not `0.15.2`, stop and state the mismatch.
- Treat `build.zig.zon` as the dependency source of truth when packages are involved.
- Before editing, identify which hazard classes apply.
- If the request is performance-focused, run in two lanes:
  - Correctness lane (`Debug` or `ReleaseSafe`).
  - Performance lane (`ReleaseFast`) only after correctness passes.
  - Choose the profiling instrument by symptom before changing code: `zprof` for allocator or leak questions, system or telemetry profilers for CPU or lock contention, and benchmark lanes for regression proof.
  - If a benchmark spans multiple abstraction layers and the aggregate result regresses, add decomposition lanes before changing code so you can separate substrate cost, wrapper cost, and full-path cost on the same workload.

## Hazard classes and required proof
- `parser/decoder/zero-copy`: unit tests, differential fuzz, validated witness, and backing-storage proof.
- `allocator-using`: `std.testing.checkAllAllocationFailures`; if a specific schedule fails, pin a fail-nth regression seed too.
- `ffi/abi`: boundary contract table, wrapper tests, link proof, and centralized raw pointer conversions.
- `optimizer-sensitive`: scalar reference path plus differential checks across `Debug`, `ReleaseSafe`, and `ReleaseFast`.
- `concurrency/shared-state`: deterministic schedule seed or replay harness, documented memory orders, and a sequential spec or witness model when lock-free claims are involved.
- `dependency/provenance`: visible URL/hash plus origin, release, and signer or attestation notes when the pin is security-sensitive or long-lived.
- If multiple hazard classes apply, satisfy all relevant proof lanes.

### Lint bootstrap (recommended when missing)
1. Add `zlinter` for Zig 0.15.x:

```bash
zig fetch --save git+https://github.com/kurtwagner/zlinter#0.15.x
```

2. Add a `lint` step in `build.zig` (all built-in rules baseline):

```zig
const zlinter = @import("zlinter");
// ...
const lint_cmd = b.step("lint", "Lint source code.");
lint_cmd.dependOn(step: {
    var builder = zlinter.builder(b, .{});
    inline for (@typeInfo(zlinter.BuiltinLintRule).@"enum".fields) |f| {
        builder.addRule(.{ .builtin = @enumFromInt(f.value) }, .{});
    }
    break :step builder.build();
});
```

## Core workflow
1. State the contract: domain, invariants, error model, ownership model, authority model, and complexity target.
2. Identify hazard classes and required proof artifacts before touching code.
3. Confirm Zig version and lint availability.
4. If lint exists, run `zig build lint -- --fix`, review the diff, then re-run `zig build lint -- --max-warnings 0`.
5. Build or derive a reference path, schema, or scalar fallback before touching optimized or unsafe code.
6. Add witness types and boundary tests first.
7. Run the required proof lanes for the active hazard classes.
8. Optimize in order: algorithm -> data layout -> zero-copy/batching -> vectorization -> threading -> micro-tuning.
9. Re-run lint, correctness, and perf gates after each optimization step.
10. Report proof with exact commands and outcomes.

## Lint gate
- Every Zig implementation turn should include lint evidence when the repo exposes `zig build lint`.
- Default lint flow:
  - `zig build lint -- --fix`
  - `zig build lint -- --max-warnings 0`
- If `--fix` changes code, review the diff before continuing.
- If lint is unavailable, say `LINT_UNAVAILABLE` and do not pretend the gate passed.

## Correctness gate (required)
- Every Zig change needs at least one correctness signal.
- For parsing, allocation, arithmetic, zero-copy, or safety-sensitive code:
  - `std.testing.fuzz` is required.
  - `std.testing.checkAllAllocationFailures` is required for allocator-using functions.
- FFI, bit-level, SIMD, and lock-free or atomic code need boundary-specific or differential tests in addition to ordinary unit tests.
- Prefer differential fuzzing (optimized path vs reference path).
- Re-run optimizer-sensitive logic under `Debug`, `ReleaseSafe`, and `ReleaseFast`.

### Standard correctness commands
```bash
# Project build/test
zig build
zig build test

# Single-file test
zig test src/main.zig

# Integrated fuzz path (requires a test step in build.zig)
zig build test --fuzz
```

### Allocation-failure pattern
```zig
const std = @import("std");

fn parseWithAlloc(alloc: std.mem.Allocator, input: []const u8) !void {
    _ = alloc;
    _ = input;
}

test "allocation failure coverage" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        parseWithAlloc,
        .{"seed"},
    );
}
```

- When an allocation failure only reproduces at a specific index, pin that fail index as a deterministic regression seed.
- Reference: `codex/skills/zig/references/fail_nth_alloc.zig`

## Boundary witnesses and zero-copy
- Separate `scan -> validate -> project`.
- Validation should return a small witness type such as `ValidatedFrame`, `BorrowedView`, `NonEmptySlice`, or `AlignedBytes`.
- Do not expose typed views, zero-copy projections, or `@ptrCast`-based decoding until validation succeeds.
- Make borrowed vs owned states explicit in API types; use distinct types or `union(enum)` rather than comments.
- Do not return slices backed by temporary or stack storage.
- Fail fast on over-capacity streaming tokens instead of truncating.
- Prefer one constructor per invariant cluster so fast paths can assume validated state.
- Reference: `codex/skills/zig/references/boundary_witness.zig`

## Schema-derived parse/format flows
- For wire or storage formats, prefer one comptime schema or policy surface that emits parser, formatter, docs, round-trip tests, and fuzz seeds from the same description.
- Centralize reflection in one classifier/helper layer instead of scattering raw `@typeInfo` switches across serializers, deserializers, and adapters.
- Guard `@hasDecl` and `@hasField` behind type-shape checks before duck-typing or custom-hook detection; `@hasDecl` is not valid on every Zig type.
- Let explicit custom hooks opt out of auto-derivation first, then fall back to a small `Kind` or policy dispatcher.
- Put rename, flatten, skip, tag, default, and `with` policies in a per-type `pub const` options surface and query it at comptime.
- Precompute wire names and naming-convention transforms at comptime so field matching and emission do not redo string work per value.
- Initialize flattened or defaulted sub-objects in dedicated helpers before parsing so the runtime path only fills observed fields and validates missing ones.

## Build and project commands
```bash
# Initialize project
zig init
zig init --minimal

# Format
zig fmt src/main.zig

# Build and run
zig build
zig build run
zig build lint -- --fix
zig build lint -- --max-warnings 0

# Release-oriented build
zig build -Doptimize=ReleaseFast

# Cross-compile examples
zig build -Dtarget=x86_64-linux
zig build -Dtarget=aarch64-macos

# Cleanup
rm -rf zig-out zig-cache
```

## Package management and dependency model
- State the package story explicitly when dependency workflow or "registry" questions come up.
- Zig has a built-in package manager, but no official central registry like `crates.io` or `npm`.
- Treat the ecosystem as decentralized: dependencies are declared in `build.zig.zon`, fetched by URL, and pinned by content hash.
- Prefer direct source archives or VCS-backed release archives over unofficial package indexes unless the user explicitly asks for third-party registries.
- When adding a dependency, update `build.zig.zon`, review the saved hash, and keep the provenance URL visible in the diff.
- Treat the hash as integrity, not complete provenance. For security-sensitive or long-lived pins, also record origin repo, release tag or commit, fetch date, and signer or attestation notes in sidecar docs or commit notes.

### Standard dependency commands
```bash
# Add a dependency and save it into build.zig.zon
zig fetch --save <url>

# Fetch dependencies declared by the build
zig build

# Format package metadata edits too
zig fmt build.zig
```

### Registry-answer template
- Say "Zig has a package manager, but not an official central package registry."
- Point to `build.zig.zon` plus `zig fetch --save` as the normal dependency path.
- Distinguish official decentralized workflow from community-maintained indexes.
- If provenance matters, add that Zig's content hash answers integrity, while signer and attestation evidence answer publisher trust and freshness.

## Comptime and invariants
- Prefer compile-time invariant checks for shape, ABI, required methods, and specialization bounds.
- Use `@compileError` to make illegal states unrepresentable at build time.
- Promote stable runtime facts to witness types or enums once discovered; do not keep rediscovering them with ad hoc checks.
- Keep generated specialization knobs small and measurable.

### Template
```zig
const std = @import("std");

fn assertHasRead(comptime T: type) void {
    if (!std.meta.hasMethod(T, "read")) {
        @compileError(@typeName(T) ++ " must implement read()");
    }
}
```

## Serde-style derive patterns
- Keep runtime loops limited to I/O and data movement.
- Prefer schema-derived policy dispatch over ad hoc reflection spread across format-specific code.
- Use the same per-type options surface for formatting, parsing, round-trip tests, and fuzz seed generation.

### Safe decl template
```zig
const std = @import("std");

fn hasDeclSafe(comptime T: type, comptime name: []const u8) bool {
    return switch (@typeInfo(T)) {
        .@"struct", .@"union", .@"enum", .@"opaque" => @hasDecl(T, name),
        else => false,
    };
}

fn classify(comptime T: type) enum { auto, custom } {
    if (hasDeclSafe(T, "serialize") or hasDeclSafe(T, "deserialize")) {
        return .custom;
    }
    return .auto;
}
```

## FFI and C interop boundary
- Split raw `extern fn` declarations from safe wrappers.
- Maintain a boundary contract table for each nontrivial symbol: nullability, length source, mutability, ownership in/out, lifetime, thread-safety, error mapping, and linkage.
- Centralize `@ptrCast`, sentinel handling, null handling, and errno or result translation in one wrapper layer.
- Mirror C boundary assumptions in Zig wrapper types, asserts, and witness constructors.
- Test the link step (`linkLibC`, `linkSystemLibrary`) and the unhappy paths, not just happy-path calls.
- Do not let borrowed C pointers escape past the documented lifetime or thread domain.
- When a C dependency changes, compare signatures and ABI expectations; if the code is security-sensitive and tooling is available, prefer an `abidiff`-style check before trusting the upgrade.
- Reference: `codex/skills/zig/references/ffi_contract_template.md`

## Concurrency and weak-memory lane
- Prefer ownership transfer, sharding, or message passing before lock-free shared-state designs.
- For shared mutable state, write down the invariant, owner transitions, and memory order for each atomic before editing code.
- Use seeded schedule fuzzing, deterministic yield injection, or replayable interleavings; check failing seeds into `testdata/`.
- For lock-free claims, add a sequential spec and, when feasible, a litmus-style or witness model in a sidecar test or notes file.
- Stress tests alone are not proof of concurrent correctness.
- Re-run concurrent code under multiple optimize modes and on Linux or CI when platform behavior differs.

## Profiling stack
Use this section when the request is about speed, latency, throughput, memory growth, leaks, or hotspot analysis.

- Start by naming the symptom precisely:
  - allocation churn, live-bytes growth, leaks, or unexplained allocator pressure -> use `zprof`
  - unknown CPU hotspot, cache issue, branchy slow path, or lock contention -> use a system sampler first and optionally telemetry tooling if the repo already supports it
  - broad regression proof or before/after validation -> use the repo benchmark or perf harness first
- Do not flatten all profiling into one tool. `zprof` is the default allocator profiler, not a substitute for CPU sampling.
- If the repo already ships benchmark or perf steps, run those before adding new instrumentation so you preserve the existing proof surface.

### `zprof` default lane
Deep-research default: prefer [`zprof`](https://github.com/ANDRVV/zprof) first for allocator-focused profiling. As of 2026-04-04, upstream `v3.0.1` is current, `build.zig.zon` declares `minimum_zig_version = "0.15.1"`, and the library wraps any Zig allocator while exposing `allocated`, `alloc_count`, `free_count`, `live_peak`, `live_bytes`, plus `hasLeaks()` and `reset()`.

Installation path to encourage by default:

```bash
# Verify if a newer upstream tag exists when freshness matters.
gh api repos/ANDRVV/zprof/releases/latest --jq '{tag_name,published_at,html_url}'

# Current researched example
zig fetch --save https://github.com/ANDRVV/zprof/archive/v3.0.1.zip
```

`build.zig` wiring:

```zig
const zprof_dep = b.dependency("zprof", .{
    .target = target,
    .optimize = optimize,
});
exe.root_module.addImport("zprof", zprof_dep.module("zprof"));
```

Minimal usage pattern:

```zig
const std = @import("std");
const Zprof = @import("zprof").Zprof;

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();

    var prof: Zprof(.{}) = .init(gpa.allocator(), undefined);
    const allocator = prof.allocator();

    const buf = try allocator.alloc(u8, 4096);
    defer allocator.free(buf);

    std.debug.print(
        "allocs={d} frees={d} live={d} peak={d}\n",
        .{
            prof.profiler.alloc_count.get(),
            prof.profiler.free_count.get(),
            prof.profiler.live_bytes.get(),
            prof.profiler.live_peak.get(),
        },
    );
}
```

`zprof` operating rules:
- Wrap the allocator boundary closest to the suspected waste so the counters stay local and explanatory.
- Keep workload, dataset, optimize mode, and child allocator identical across baseline and variant runs.
- Use `prof.profiler.reset()` between phases if one process captures multiple steps.
- Enable `.thread_safe = true` only when multiple threads truly share the wrapped allocator; otherwise prefer one profiler per thread or per subsystem to keep attribution sharp.
- Disable unneeded counters when chasing a narrow question so overhead stays low and the signal is easier to read.
- Pair `zprof` with ordinary benchmarks. Allocator counters can explain why a variant regressed, but they do not prove the user-visible delta by themselves.
- Pair `zprof` with correctness gates. A lower allocation count is not a win if it changes semantics or hides a leak elsewhere.

### CPU and telemetry lane
- If `zprof` counters stay flat while wall time regresses, switch to a CPU sampler instead of guessing.
- On Linux, prefer `perf record` and `perf report` for sampled call stacks on optimized binaries.
- On macOS, prefer Instruments Time Profiler for sampled CPU hotspots.
- For long-running concurrent or frame-oriented systems where time-series causality matters, consider Tracy if the repo already supports it or the user explicitly wants instrumentation. Tracy is strong for CPU, locks, context switches, and telemetry; it is not the first move for a small allocator-only question.
- Do not add heavy profiler integrations before a smaller benchmark or allocator-profile pass rules them in.

## Performance lane and `$lift` handoff
Use this lane when the request is about speed, latency, throughput, memory, or profiling.

- If you can run a workload: produce baseline + after numbers and bottleneck evidence.
- If you cannot run a workload: mark output `UNMEASURED` and provide exact commands.
- Keep correctness gates before and after each performance change.
- Pick the profiling stack deliberately: benchmark for proof, `zprof` for allocator questions, CPU samplers for hot-path localization, and telemetry tools only when the workload shape justifies them.
- Use statistical discipline for small deltas: fixed dataset, warmups, repeated fresh-process runs, and sample counts. If the delta is small enough to be noisy, report an effect size or interval, not just one median.
- Prefer causal or progress-point instrumentation when the workload is concurrent or pipeline-shaped and flat hotspots are misleading.
- Optimize in order: algorithm -> data layout -> zero-copy/batching -> vectorization -> threading -> micro-tuning.
- Keep scalar fallbacks and differential tests after vectorization or threading changes.
- For large hot Linux binaries, consider a post-link layout or PGO/BOLT-style lane before invasive source rewrites.

### Minimal measured loop
```bash
# 1) correctness first
zig build test

# 2) safe native build for reference behavior
zig build -Doptimize=ReleaseSafe -Dtarget=native -Dcpu=native

# 3) fast native build for perf work
zig build -Doptimize=ReleaseFast -Dtarget=native -Dcpu=native

# 4) if the repo exposes a benchmark step, prefer it
zig build bench -- --samples 10 --warmup 3

# 5) allocator-focused lane when bytes or leaks are the question
gh api repos/ANDRVV/zprof/releases/latest --jq '{tag_name,published_at,html_url}'
```

When the request is a broader perf pass with explicit reporting format, apply `$lift` conventions (contract -> baseline -> bottleneck -> experiments -> result -> regression guard).

### Benchmark decomposition rule
Use this when a Zig perf regression crosses abstraction layers and one aggregate benchmark is not enough to localize the cost.

- Keep the same dataset, warmup, sample count, checksum, allocator, and optimize mode across all lanes.
- Add 2-4 lanes inside the same harness to isolate:
  - substrate only
  - wrapper or shell only
  - full path
- Name the lanes concretely (for example `raw_reset_only`, `effect_passthrough`, `full_raw`, `full_effect`) and keep their output adjacent so the subtraction is obvious.
- Optimize from the decomposed result, not from the aggregate delta alone.
- Once the bottleneck is understood, either keep the extra lanes as regression guards or gate them behind an explicit benchmark mode; do not leave noisy one-off instrumentation in the default path without a reason.
- When a pipeline exposes throughput or latency progress points, keep them stable across baseline and variant runs.

## SIMD and threading policy
- Use SIMD or threading only when profiling shows a CPU-bound hot path.
- Keep scalar fallback paths and deterministic behavior.
- Avoid hidden allocations or synchronization inside hot loops.
- Re-run fuzz, differential tests, and any schedule-sensitive tests after vectorization or parallelization changes.

## macOS fuzz caveat
`zig build test --fuzz` may fail on macOS (`InvalidElfMagic`) in Zig 0.15.2.

If this occurs:
- State the local limitation explicitly.
- Keep `std.testing.fuzz` targets in-tree.
- Run fuzz on Linux/CI or an external harness.
- Add deterministic regression seeds under `testdata/fuzz/`.

## Trigger-audit workflow (`$seq` backed)
Use this to measure whether Zig intent is being routed to `$zig`.

```bash
# Run audit on full history
uv run python codex/skills/zig/scripts/zig_trigger_audit.py --root ~/.codex/sessions

# Time-windowed audit
uv run python codex/skills/zig/scripts/zig_trigger_audit.py \
  --root ~/.codex/sessions \
  --since 2026-02-01T00:00:00Z \
  --strict-implicit \
  --format json \
  --output /tmp/zig-audit.json

# Regression tests for the audit script
uv run python codex/skills/zig/scripts/test_zig_trigger_audit.py
```

Notes:
- The audit uses literal `contains` matching to avoid regex parser limitations in `seq` for dotted literals (for example `.zig`, `build.zig`, `std.simd`).
- Keep strict-implicit mode enabled when evaluating precision-sensitive routing changes.
- Lint and FFI cues (`zig build lint`, `zlinter`, `extern fn`, `linkSystemLibrary`, `linkLibC`) are tracked as Zig intent.

## Monthly drift scorecard
Generate a compact scorecard that combines:
- `$zig` SKILL size.
- Trigger-audit counts/rates.
- Routing-gap invoked-rate metrics for safe Zig cues.
- Recommendation hints when drift is detected.

```bash
uv run python codex/skills/zig/scripts/zig_ops_scorecard.py \
  --root ~/.codex/sessions \
  --since 2026-02-01T00:00:00Z \
  --format text

# Regression tests for the scorecard script
uv run python codex/skills/zig/scripts/test_zig_ops_scorecard.py
```

Notes:
- The scorecard should tolerate local `seq routing-gap` builds that do not yet support `--since`.

## `skills-zig` evidence lane
When validating guidance against current Zig production patterns, inspect:
- Source/build/release repo: `/Users/tk/workspace/tk/skills-zig`
- Formula propagation repo: `/Users/tk/workspace/tk/homebrew-tap`

Recommended checks:
```bash
git -C /Users/tk/workspace/tk/skills-zig log --oneline --max-count=30
rg -n "std.testing.fuzz|checkAllAllocationFailures|FailingAllocator" /Users/tk/workspace/tk/skills-zig/apps -g"*.zig"
rg -n "extern fn|linkSystemLibrary|linkLibC|sqlite3_" /Users/tk/workspace/tk/skills-zig/apps /Users/tk/workspace/tk/skills-zig/build.zig -g"*.zig"
rg -n "std.atomic|compareExchange|fetchAdd|Thread|spawn" /Users/tk/workspace/tk/skills-zig/apps -g"*.zig"
rg -n "std.simd|@Vector|std.Thread.Pool" /Users/tk/workspace/tk/skills-zig/apps -g"*.zig"
rg -n "perf_hub|CountingAllocator|warmup|samples" /Users/tk/workspace/tk/skills-zig/apps /Users/tk/workspace/tk/skills-zig/tools -g"*.zig"
rg -n "@typeInfo|@hasDecl|@hasField|@Type|comptime" /Users/tk/workspace/tk/skills-zig/apps -g"*.zig"
```

Use these results to keep `$zig` guidance aligned with what is true in active Zig repos.

## Pitfalls
- Claiming performance wins without measured baseline/after evidence.
- Treating allocator counters as a substitute for CPU hotspot data, or CPU samples as a substitute for allocation evidence.
- Treating a validated fact as a comment instead of a witness type.
- Exposing zero-copy or FFI views before validation and lifetime checks.
- Running micro-optimizations before removing algorithmic or data-movement waste.
- Skipping allocation-failure coverage in allocator-heavy code.
- Claiming lock-free or concurrent correctness from stress tests alone.
- Skipping `zig build lint` when the repo exposes it, or pretending lint passed when unavailable.
- Running `zig build lint -- --fix` on a dirty tree without reviewing the resulting diff.
- Scattering `@typeInfo` and trait-probe logic across format-specific code instead of centralizing the classifier and policy layer first.
- Treating borrowed memory as owned (or vice versa).
- Returning stack-backed slices.
- Treating URL+hash as complete supply-chain provenance.
- Assuming regex-like query patterns are portable across all tooling without validation.

## References
- Boundary witness template: `codex/skills/zig/references/boundary_witness.zig`
- Deterministic fail-nth allocation pattern: `codex/skills/zig/references/fail_nth_alloc.zig`
- FFI contract template: `codex/skills/zig/references/ffi_contract_template.md`
- Profiling playbook: `codex/skills/zig/references/profiling_playbook.md`
- Differential fuzz template: `codex/skills/zig/references/fuzz_differential.zig`
- Type-shape dispatcher example: `codex/skills/zig/references/type_switch.zig`
- `@Type` partial-builder example: `codex/skills/zig/references/partial_type.zig`
- Derive-walk policy pipeline: `codex/skills/zig/references/derive_walk_policy.zig`
