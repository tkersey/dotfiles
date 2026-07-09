# Source Anchors

## Official Zig sources

- Zig 0.16.0 language reference: https://ziglang.org/documentation/0.16.0/
- Zig 0.16.0 release notes: https://ziglang.org/download/0.16.0/release-notes.html
- Zig build system guide: https://ziglang.org/learn/build-system/
- Zig download/release index: https://ziglang.org/download/
- LLVM Link Time Optimization design: https://llvm.org/docs/LinkTimeOptimization.html

Relevant official areas:

```text
allocators and ownership
slices/pointers/sentinels/alignment
Illegal Behavior and runtime safety
undefined
error sets, try/catch/errdefer
atomics
extern/packed layout
build modes
build system, target options, linker options, and LTO
comptime/reflection/type construction
Smith fuzzing
std.Io and process.Init
C translation and package workflows
```

## Existing third-party/tooling anchors retained

- Zlinter 0.16.x documentation
- zprof documentation
- Matklad, “Steering Zig Fmt”

Repository pins remain authoritative for exact compatible versions.

## Local operational evidence

The 2026-06-20 local `$seq` report identified recurring Zig-session failure signatures in:

```text
proof/authority binding
borrowed slice escape
fallible mutation atomicity
parser/verifier completeness
generated artifact and repository registry drift
stale proof epochs
cache/sandbox environment mismatches
```

The report explicitly states that the installed `seq` surface proved recurring signatures and associated outcomes, not causal influence from `$zig`.

This release therefore changes routing and instrumentation rather than claiming the prior skill caused or failed to cause those outcomes.

## Design sources

The semantic router also preserves the existing skill’s own proven doctrine:

```text
witness-driven design
owner-first invariants
small hazardous core
safe/reference differential paths
repository build steps before invented commands
explicit unavailable-proof labels
```
