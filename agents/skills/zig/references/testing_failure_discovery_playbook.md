# Zig testing, fuzzing and failure discovery

Select checks for the contract at issue. Use the repository harness when modules,
dependencies, build options or generated imports matter. Honor required checks;
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

## Validate the changed project

Inspect existing build steps and argument placement. For a project selecting Zig
0.17, candidate commands include:

```bash
zig build test
zig build test -Doptimize=debug
zig build test -Doptimize=safe
zig build test -Doptimize=fast
```

Use only options the project exposes and spellings supported by its selected
compiler. An older repository pin is not overridden by these examples. Do not run
every mode for every edit. Use production and additional modes when they
discriminate a relevant failure. Inspect runner timeout and fuzz/Smith interfaces;
retain bounded inputs, seeds, corpus and minimized reproductions.

Without a project harness, run a focused `zig test` or temporary harness that
imports and exercises the project's actual changed code and required dependencies.
The skill's bundled reference suite cannot stand in for that check. If the project
cannot be executed here, report that limit rather than substituting unrelated
green examples. Do not add a repository-wide framework merely to run a few cases.

## Semantic mutations and state transitions

For verifiers and proof-like values, mutate facts promised by the public API:
omission, substitution, equal-length foreign references, wrong domain/version/epoch,
reordering/duplication, unknown sections, noncanonical varints, wrong tags/opcodes,
value/metadata disagreement, lower/upper bounds, extra/missing entities, and wrong
final state/stack. Include valid encodings with invalid semantics. Associate each
case with the governing law, public predicate and expected outcome. A matrix is
useful for complex coverage, not an obligatory reporting format.

For fallible changes, test the guarantee in [transitions](atomic_transition_playbook.md).
Allocation-failure enumeration does not cover publication, I/O or callback errors.
Check full observable rollback only when promised; test partial progress or durable
recovery when that is the contract. Exercise exact-once ownership handling.

## Force compile-time analysis

A top-level declaration can remain unanalyzed. Make negative fixtures instantiate
the rejected type or call in `comptime`, and require the API-specific diagnostic.
Nonzero exit alone can mean missing imports, wrong toolchain or syntax errors.
Pair negatives with valid instantiations of the same API. Exercise materially
different generic branches: floats, empty/nonempty shapes, policies and nested data.
Use the project harness when bare `zig test` would omit its actual inputs.

## Skill-maintenance checks only

Resolve `zig_skill_root` to this loaded skill's directory. For changes to the skill
or its reference examples, the existing maintenance commands are:

```bash
uv run python3 -m unittest discover -s "$zig_skill_root/tests" -p 'test_*.py'
uv run python3 "$zig_skill_root/tests/check_zig_examples.py" --zig zig --optimize debug
uv run python3 "$zig_skill_root/tests/check_zig_examples.py" --zig zig --optimize safe
```

The Python suite tests helpers, contracts, documented runner arguments and failure
classification. Its stub compiler is not Zig correctness evidence. The real
compiler runner discovers the skill's top-level reference test files and checks
forced diagnostic-specific negative fixtures using disposable caches. Its exact
compiler/mode contract is [toolchain.py](../tests/toolchain.py), independent of any
consuming project. Missing/wrong-version compilers are unavailable, never green.

A successful file-level test still does not instantiate every possible generic
body. A compile-only target lane does not execute target code, and a normal test
of the fuzz template is not a sustained campaign. Report what actually ran.

The checks above do not measure model effectiveness. Use the optional
[matched behavioral probes](../tests/behavioral_probes.md) for that separate
question; they are not a stage in ordinary Zig work. Keep version, inputs, command
and relevant environment with reproductions and apply
[evidence context](evidence_context_playbook.md) when reusing results.
