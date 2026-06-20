# Zig Testing, Fuzzing, Mutation, and Failure Discovery

Use for correctness hardening, parsers/verifiers, data structures, state transitions, fuzzing, allocation failure, compile-fail fixtures, optimizer/target behavior, or reproductions.

## Test lanes

| Lane | Purpose |
| --- | --- |
| Unit | Local behavior and invariants. |
| Build-system | Modules/deps/options/generated imports. |
| Integration | Files/network/process/effects. |
| Allocation-failure | OOM cleanup and atomicity. |
| Fuzz | Parser totality/state exploration. |
| Differential | Custom/optimized path versus reference. |
| Semantic mutation | Verifier completeness and claim binding. |
| Compile-fail | Invalid comptime/type shapes fail intentionally. |
| Timeout/stress | Hangs/deadlocks/liveness. |
| Optimize/target matrix | Safety, ABI, endian, optimizer differences. |
| Proof-epoch | Bind result to exact artifact context. |

Prefer repository build steps over bare `zig test` when modules/options/dependencies exist.

## Core commands

```bash
zig build test
zig build test --test-timeout 500ms
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
```

Inspect `zig build --help` before assuming runner argument placement.

## Fuzzing

A good Zig 0.16 Smith target:

- bounds generated work;
- keeps corpus/reproduction;
- compares to a reference when possible;
- captures exact version/target/mode/seed;
- tests parsers/state machines/zero-copy validators.

Fuzzing proves exploration and totality better than semantic completeness.

## Semantic mutation matrix

For proof/certificate/verifier code, mutate one trusted fact at a time.

Typical rows:

```text
claimed field changed
field omitted
zero/minimal evidence
foreign equal-length ref
reordered/duplicated evidence
wrong version/domain/authority/epoch
wrong opcode/tag
unknown/duplicate section
malformed/noncanonical varint
metadata mismatch
lower/upper bound violation
extra/missing entity
wrong final stack/state/result
stale generated constant
valid encoding with invalid semantics
```

Each row names:

```yaml
mutation_case:
  case_id:
  governing_claim_or_law:
  baseline:
  mutation:
  public_predicate:
  expected_failure:
  proof_command:
```

## Allocation and atomicity failure

Review:

- each allocation index;
- object unchanged after failed mutation;
- partial insert rollback;
- event/ledger/outbox rollback;
- moved value freed exactly once;
- no escaped ref/receipt;
- failure after first observable mutation.

`checkAllAllocationFailures` is useful but may not enumerate non-allocation failures; add targeted fail points where needed.

## Negative compile-time proof

Use repository-supported compile-fail fixtures for:

```text
unsupported type shape
missing declaration/method
illegal field
invalid comptime value
removed Zig API
contract diagnostic
```

Check intended error text when the repository supports stable diagnostics.

## Property/state-machine proof

Prefer law-level tests for recurring families.

Examples:

```text
encode/decode round trip
commit/publish visibility law
rollback preserves observable state
public verifier equals strongest predicate
proof fingerprint changes with every claimed field
```

## Reproduction record

Preserve:

```text
Zig version
repo/head/dirty fingerprint
target/optimize/options
dependency/fork state
seed/corpus/input
command
expected/actual
failure class
proof epoch
```

## Checklist

- Repository harness used.
- Active semantic family has direct proof.
- Fuzz target is bounded and reproducible.
- Semantic mutation matrix exists for verifiers/claims.
- Allocation and state atomicity failures are covered.
- Compile-time invalid cases fail intentionally.
- Optimizer/target-sensitive paths use a matrix.
- Final proof epoch matches final tree/context.
