# Zig testing, fuzzing, allocation-failure, and negative-proof playbook

Use this playbook for correctness hardening, parser/data-structure tests, fuzzing, allocation failure, compile-fail fixtures, failure reproduction, or bug-minimization workflows.

## Expert objective

A robust Zig test strategy covers:

1. normal behavior;
2. edge cases and invariants;
3. domain failures;
4. allocation/resource failures;
5. fuzz/differential exploration;
6. compile-time negative tests when APIs reject types/shapes;
7. optimizer-mode and target-specific hazards;
8. reproduction commands for discovered failures.

## Test lanes

| Lane | Purpose |
| --- | --- |
| Unit test | Local behavior and invariants. |
| Build-system test | Correct modules/deps/options. |
| Integration test | Files/network/process effects. |
| Allocation-failure test | `OutOfMemory` cleanup coverage. |
| Fuzz test | Explore parsers/state machines. |
| Differential test | Compare optimized/custom path to reference. |
| Compile-fail fixture | Prove invalid comptime/type shapes fail intentionally. |
| Timeout test | Detect deadlocks/hangs. |
| Optimize-mode matrix | Catch safety/optimizer differences. |

## Commands

Start with the repo harness:

```bash
zig build test
zig build test --test-timeout 500ms
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
```

For local files only, `zig test path/to/file.zig` can be useful, but do not rely on it when the build system wires modules, C imports, packages, or options.

## Fuzzing with Smith

For Zig 0.16, fuzz callbacks use `*std.testing.Smith`. A good fuzz target:

- constrains generated size to avoid meaningless huge work;
- preserves interesting seeds/corpus;
- compares against a reference implementation when possible;
- keeps crash reproduction fixtures under `testdata/fuzz/`;
- uses `@embedFile` or explicit corpus options for regression.

Suggested categories:

- parsers/decoders;
- binary protocols;
- state machines;
- allocators/containers;
- escaping/unescaping;
- unicode/path handling;
- zero-copy validators.

## Allocation failure

Use `std.testing.checkAllAllocationFailures` for functions with bounded allocation behavior. For unbounded loops, use targeted `FailingAllocator` tests around known allocation points.

Review:

- Does failure after each allocation deinit prior allocations?
- Does the function leave the object unchanged after failed mutation?
- Are partial inserts rolled back?
- Are moved/owned values freed exactly once?

## Negative tests

For comptime-heavy APIs, invalid code should fail with intentional diagnostics. Options:

- put compile-fail snippets in comments with exact command;
- create a separate fixture directory that CI compiles expecting failure;
- use a build step that runs invalid cases and checks error text if the repo already supports this pattern.

Negative tests should cover:

- unsupported type shape;
- missing required declaration/method;
- illegal field type;
- invalid comptime value;
- removed Zig-version construct in migration work.

## Reproduction discipline

When a failure is found, preserve:

- exact Zig version;
- target/optimize mode;
- seed/corpus file;
- command;
- minimized input if available;
- expected vs actual behavior;
- whether the failure is safety panic, assertion, compile error, timeout, or wrong result.

## Review checklist

- Tests run through the build system when dependencies/modules exist.
- Fuzz targets have bounded work and corpus reproduction.
- Allocation-failure tests cover cleanup.
- Domain error cases have explicit fixtures.
- Compile-time negative cases exist for reflective/generic APIs.
- Optimizer-sensitive code is tested in multiple modes.
- Timeouts are used for concurrency/hang-prone tests.
- Failure reproduction details are captured.
