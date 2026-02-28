---
name: zig
description: "Use when implementing or reviewing Zig 0.15.2 code and toolchain workflows: editing .zig files, build.zig/build.zig.zon changes, zig build/test/run/fmt/fetch commands, comptime/reflection/codegen, allocator ownership and zero-copy parsing, C interop, and performance work (latency, throughput, profiling, SIMD, threading) that must preserve correctness with fuzz and allocation-failure checks."
---

# Zig

## Operating contract
- Assume Zig 0.15.2 unless the user explicitly requests another version.
- Treat correctness as a hard gate before optimization and release work.
- Prefer minimal incisions with explicit proof signals.
- Keep fast paths benchmarked, but keep safety checks on during correctness validation.

## Baseline requirements
- Confirm toolchain version first:

```bash
zig version
```

- If the version is not `0.15.2`, stop and state the mismatch.
- If the request is performance-focused, run in two lanes:
  - Correctness lane (`Debug` or `ReleaseSafe`).
  - Performance lane (`ReleaseFast`) only after correctness passes.

## Core workflow
1. State the contract: domain, invariants, error model, and complexity target.
2. Build or identify a reference path before touching optimized code.
3. Add or extend unit tests around edge cases and regressions.
4. Run fuzz and allocation-failure checks for safety-sensitive paths.
5. Optimize in order: algorithm -> data layout -> vectorization -> threading -> micro-tuning.
6. Re-run correctness gates after each optimization step.
7. Report proof with exact commands and outcomes.

## Correctness gate (required)
- Every Zig change needs at least one correctness signal.
- For parsing, allocation, arithmetic, or safety-sensitive code:
  - `std.testing.fuzz` is required.
  - `std.testing.checkAllAllocationFailures` is required for allocator-using functions.
- Prefer differential fuzzing (optimized path vs reference path).

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

## Performance lane and `$lift` handoff
Use this lane when the request is about speed, latency, throughput, memory, or profiling.

- If you can run a workload: produce baseline + after numbers and bottleneck evidence.
- If you cannot run a workload: mark output `UNMEASURED` and provide exact commands.
- Keep correctness gates before and after each performance change.

### Minimal measured loop
```bash
# 1) correctness first
zig build test

# 2) baseline perf sample
zig build -Doptimize=ReleaseFast -Dtarget=native -Dcpu=native

# 3) variant perf sample (after one change)
zig build -Doptimize=ReleaseFast -Dtarget=native -Dcpu=native
```

When the request is a broader perf pass with explicit reporting format, apply `$lift` conventions (contract -> baseline -> bottleneck -> experiments -> result -> regression guard).

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

# Release-oriented build
zig build -Doptimize=ReleaseFast

# Cross-compile examples
zig build -Dtarget=x86_64-linux
zig build -Dtarget=aarch64-macos

# Cleanup
rm -rf zig-out zig-cache
```

## Comptime and invariants
- Prefer compile-time invariant checks for shape, ABI, and required methods.
- Use `@compileError` to make illegal states unrepresentable at build time.
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

## Zero-copy and ownership checklist
- Parse into spans/slices that point to stable backing storage.
- Do not return slices backed by temporary buffers.
- Make borrowed vs owned states explicit in API types.
- Fail fast on over-capacity streaming tokens instead of truncating.

## SIMD and threading policy
- Use SIMD/threading only when profiling shows CPU-bound hot paths.
- Keep scalar fallback paths and deterministic behavior.
- Avoid hidden allocations inside hot loops.
- Re-run fuzz/tests after vectorization or parallelization changes.

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
```

## `skills-zig` evidence lane
When validating guidance against current Zig production patterns, inspect:
- Source/build/release repo: `/Users/tk/workspace/tk/skills-zig`
- Formula propagation repo: `/Users/tk/workspace/tk/homebrew-tap`

Recommended checks:
```bash
git -C /Users/tk/workspace/tk/skills-zig log --oneline --max-count=30
rg -n "std.testing.fuzz|checkAllAllocationFailures|FailingAllocator" /Users/tk/workspace/tk/skills-zig/apps -g"*.zig"
rg -n "std.simd|@Vector|std.Thread.Pool" /Users/tk/workspace/tk/skills-zig/apps -g"*.zig"
```

Use these results to keep `$zig` guidance aligned with what is true in active Zig repos.

## Pitfalls
- Claiming performance wins without measured baseline/after evidence.
- Running micro-optimizations before removing algorithmic waste.
- Skipping allocation-failure coverage in allocator-heavy code.
- Treating borrowed memory as owned (or vice versa).
- Returning stack-backed slices.
- Assuming regex-like query patterns are portable across all tooling without validation.

## References
- Differential fuzz template: `codex/skills/zig/references/fuzz_differential.zig`
- Type-shape dispatcher example: `codex/skills/zig/references/type_switch.zig`
- `@Type` partial-builder example: `codex/skills/zig/references/partial_type.zig`
- Derive-walk policy pipeline: `codex/skills/zig/references/derive_walk_policy.zig`
