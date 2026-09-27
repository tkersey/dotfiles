# Zig testing, fuzzing and failure discovery

Select checks for the contract at issue. Use the repository harness when modules,
dependencies, build options, or generated imports matter. Honor required checks;
additional checks should resolve a specific uncertainty rather than fill a matrix.

| Lane | What it can establish |
| --- | --- |
| Unit/property | Exercised behavior and law instances; not incidental configuration snapshots. |
| Build/integration | Actual module, dependency, option and effect integration. |
| Allocation/non-allocation failure | Cleanup and the advertised state-transition guarantee. |
| Fuzz | Sampled parser/state exploration, counterexamples and reproductions. |
| Differential | Agreement with a sufficiently independent reference on tested inputs. |
| Semantic mutation | Rejection of particular malformed or semantically invalid claims. |
| Compile-fail | The intended unsupported shape is analyzed and rejected for the intended reason. |
| Timeout/stress | Observed termination, cancellation and contention behavior. |
| Mode/target matrix | Relevant ABI, endian, optimizer and runtime-safety assumptions. |

A fuzz campaign does not prove totality. Two wrappers sharing the same faulty
implementation are not independent oracles. Keep source-level arguments,
compiler-enforced properties, empirical results and unexecuted suggestions distinct.

## Repository commands

Inspect existing build steps and argument placement before using commands such as:

```bash
zig build test
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
```

Do not run every mode for every edit. Use production mode and additional modes when
they discriminate a relevant failure. Inspect the installed runner's timeout and
fuzz/Smith interfaces; retain bounded inputs, seeds, corpus and minimized repros.

## Semantic mutations and state transitions

For verifiers and proof-like values, mutate the facts promised by the public API:
omission, substitution, equal-length foreign refs, wrong domain/version/epoch,
reordering/duplication, unknown sections, noncanonical varints, wrong tags/opcodes,
actual-value/metadata disagreement, lower/upper bounds, extra/missing entities,
and wrong final state/stack. Include valid encodings with invalid semantics.
Each case should name the governing law, mutation, public predicate and expected
outcome. A structured matrix is useful for complex coverage, not mandatory prose.

For fallible state changes, test the guarantee in [transitions](atomic_transition_playbook.md).
Allocation-failure enumeration does not cover publication, I/O, or callback errors.
Check full observable rollback only when promised; test partial progress or durable
recovery when that is the contract. Always test exact-once ownership handling.

## Force compile-time analysis

A top-level declaration can remain unanalyzed. Make negative fixtures instantiate
the rejected type or call in `comptime`, and require an API-specific diagnostic.
Nonzero exit alone can mean missing imports, the wrong toolchain, or syntax errors.
Pair negatives with valid instantiations that exercise the same API. Test materially
different generic branches: floats, empty/nonempty shapes, policies, and nested data.

The bundled runner provides an executable fallback when a repository has no harness:

```bash
uv run python3 "$zig_skill_root/tests/check_zig_examples.py" --zig zig --optimize Debug
```

It uses disposable caches, runs the reference test files, and checks forced
compile-fail fixtures. Missing/wrong-version compilers are unavailable, never green.
A file-level `zig test` still does not instantiate every possible generic shape;
report exactly which cases ran. Do not add a new repository framework merely to
run a few isolated compile-fail cases.

## Skill-maintenance checks

```bash
uv run python3 -m unittest discover -s "$zig_skill_root/tests" -p 'test_*.py'
```

These tests exercise helper behavior, contracts and runner failure classification.
They do not measure model effectiveness. Use the matched probes in
[behavioral evaluation](../tests/behavioral_probes.md) for that separate question.
Keep version, input, command and relevant environment with reproductions; apply
[evidence context](evidence_context_playbook.md) for reuse and reporting.
