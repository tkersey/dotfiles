---
name: zig
description: "Use for Zig 0.16.0 implementation, review, migration, build/package, comptime/codegen, formatting/lint, testing/fuzzing, profiling, hazardous low-level code, FFI/layout, concurrency, cache operations, boundedness/assertion/control-flow review, and semantic failures involving proof binding, borrowed-lifetime escape, fallible mutation atomicity, parser/verifier completeness, repository contract drift, or stale proof context. Verify the installed Zig version before version-sensitive work."
metadata:
  version: "2.1.0"
  activation_cost: medium
  default_depth: adaptive
---
# Zig
## Mission
Produce correct Zig changes by selecting:

```text
the Zig work surface
the semantic failure family
and
the cross-cutting engineering contract
```
The skill is a router first and an expert reference system second.

A green build is not enough when the change trusts proof material, returns
borrowed data, mutates several owners, verifies hostile input, changes generated
or repository artifacts, relies on stale proof, or introduces work that can
grow, wait, retry, recurse, allocate, or fan out without an explicit bound.
## Version and artifact-state pin
Assume Zig `0.16.0` only when the repository or user does not specify another
version.

Before version-sensitive work:
```bash
zig version
git rev-parse --show-toplevel
git rev-parse HEAD
git status --short
```
If the installed version differs from the claimed target, report:
```text
VERSION_MISMATCH
```
Do not claim that commands validate a different Zig version. Record the
repository root, branch/head, dirty state, worktree, target, optimize mode, and
relevant build options before material proof.
## Two-axis routing
### Axis A — work surface
Classify one or more:
```text
migration
API/domain design
build/package/dependency
comptime/reflection/codegen
formatting/lint
testing/fuzzing/failure discovery
hazardous low-level code
allocator/ownership/lifetime
FFI/layout/wire/MMIO
I/O/effects
concurrency/atomics/cancellation
performance/profiling
cache/disk operations
```
### Axis B — semantic failure family
Classify before the first material edit:
```text
claim-binding
lifetime-escape
atomic-transition
verifier-completeness
repo-closure
proof-context
none
```
For material work, emit a compact `zig_semantic_route / ZSR-v1`.

`none` requires a concrete reason such as formatting-only or isolated syntax
migration.

See [semantic_failure_router.md](references/semantic_failure_router.md).
## ZSR-v1
The route binds artifact state, task surfaces, materiality, active families,
owner, counterexample, repair boundary, forbidden shortcuts, required proof,
family contracts, and the pre-edit mutation decision.

Use the full schema in
[semantic_failure_router.md](references/semantic_failure_router.md).
## Cross-cutting engineering constraints
For material implementation or review, apply these priorities in order:

```text
1. safety and semantic correctness
2. predictable performance and bounded resource use
3. developer experience and maintainability
```
These constraints are not a seventh semantic family. Apply them to every
selected route:

```text
all work that can grow, wait, retry, allocate, recurse, or fan out
its numeric or structural bound and terminal failure
independent assertion pairs for safety-relevant invariants
programmer-error versus operating-error treatment
control-flow and function-growth decisions
a network/disk/memory/CPU sketch or a concrete non-applicability reason
narrow exceptions and their rationale
```
New or growing functions target at most 70 physical lines; changed lines target
at most 100 Unicode code points. Existing debt may shrink incrementally but
must not grow silently.

General Zig CLIs may allocate after startup when aggregate memory is bounded,
ownership is explicit, and allocation failure is handled. Long-lived services
and hot data planes should prefer startup allocation, fixed-capacity pools, and
bounded admission.

## Semantic family 1 — claim binding
Trigger for fingerprints, receipts, certificates, proofs, evidence, refs,
cursors, manifests, checkpoints, replay records, attestations, and pass/fail
APIs.

Ask:
```text
What exact authoritative bytes or facts does this claim bind?
What can a caller omit, substitute, reorder, zero, or forge while still passing?
```
Require the authoritative owner, canonical encoding, complete bound-field
inventory, caller-controlled or unbound fields, public/strongest-predicate
parity, and adversarial mutations of every claimed field.

Do not accept caller-supplied fingerprints as proof of caller-supplied objects.

See [claim_binding_playbook.md](references/claim_binding_playbook.md).
## Semantic family 2 — lifetime escape
Trigger when parsed, decoded, arena-backed, container-backed, staged, snapshot,
report, certificate, slice, or ref data escapes its current owner.

Require:
```text
field -> backing owner -> promised lifetime -> invalidator/deinit
      -> borrow/copy/transfer/owner-carried decision -> failure cleanup
```
Escaping runtime-owned slices must be duplicated into the returned owner or
carry or transfer the backing owner.

Never return data backed by temporary input, a soon-deinitialized arena or
report, moved staging state, a reallocating container, or a refreshable snapshot
without an explicit epoch.

See [memory_ownership_playbook.md](references/memory_ownership_playbook.md).
## Semantic family 3 — atomic transition
Trigger when a fallible state transition performs any observable mutation
before later allocation, clone, append, persistence, publication, ownership
transfer, or event emission can fail.

Ask:
```text
Can any later operation fail after the first observable mutation?
If so, is every owner and external effect restored exactly?
```
Prefer:
```text
prepare all fallible data
-> commit one non-fallible state transition
-> publish effects after commit
```
Otherwise require rollback covering every owner and effect. Proof must compare
full observable pre-state and post-state at deterministic failure indices.

`errdefer` that frees memory but leaves ledgers, events, counters, refs,
journals, or state owners changed is not atomicity.

See [atomic_transition_playbook.md](references/atomic_transition_playbook.md)
and [error_failure_playbook.md](references/error_failure_playbook.md).
## Semantic family 4 — verifier completeness
Trigger for parsers, decoders, binary formats, protocols, WASM, archives,
inspectors, validators, and `passed()` or `verify()` APIs.

Prove separately:

```text
parser totality:
  arbitrary bytes do not trap; lengths, counts, and varints terminate and stay bounded

semantic completeness:
  the public predicate checks the exact promised property, actual values,
  lower and upper bounds, final state or stack shape, and every relevant entity
```
Use fuzz or differential parsing and a semantic mutation matrix containing
malformed plus valid-but-semantically-invalid inputs.

The public predicate downstream code consumes must equal the strongest relevant
internal predicate.

See
[verifier_completeness_playbook.md](references/verifier_completeness_playbook.md).
## Semantic family 5 — repository closure
Trigger when adding, moving, removing, generating, or renaming:

```text
.zig files
build steps
compile-fail fixtures
examples
goldens
expected output
generated headers or constants
path registries
manifests
checked documentation
```
Ask:
```text
What registry, build manifest, generator, golden, or aggregate check also owns this file or output?
```
Run:
```bash
python3 codex/skills/zig/scripts/zig_repo_closure_scan.py --root .
```
Then inspect repository-specific contracts and run aggregate lint and build
proof. Do not hardcode one repository's registry filename as universal doctrine.

See [repo_closure_playbook.md](references/repo_closure_playbook.md).
## Semantic family 6 — proof context
Final proof binds command and cwd, repository/head/dirty fingerprint, Zig
version, target/mode/options, dependencies/forks, generated artifacts,
cache/sandbox routing, time, and result.

Invalidators include edits or `zig fmt`, regeneration, commit/amend/rebase/merge,
worktree/head change, dependency/fork change, target/mode/option change, or
command change.

Run the repository's focused and aggregate proof commands directly. Record the
exact command, working directory, artifact state, Zig version, options, and
result in the final report. Focused proof may diagnose; closure proof must match
the final context.

A Zig stdlib or test-runner `PermissionDenied` in a review sandbox is an
environment verdict. Rerun the same command with a writable global cache.

## First-pass workflow
1. Pin Zig version and artifact state.
2. Inspect `build.zig`, `build.zig.zon`, build steps, tests, lint, and repository guidance.
3. Classify Axis A and Axis B.
4. Emit ZSR-v1 for material work.
5. Name owner, counterexample, repair boundary, bounds, assertion pairs, forbidden shortcuts, and proof.
6. Run only the scans and playbooks required by active surfaces and families.
7. Make the smallest owner-correct, bounded change.
8. Run focused proof and negative-space tests.
9. Run repository-closure scans when artifacts changed.
10. Run final proof in the final repository context.
11. Report exact commands, outcomes, unavailable lanes, residual risk, exceptions, and proof invalidators.
## Hazardous low-level code
Zig has no Rust-style `unsafe` keyword.

Treat operations as hazardous when correctness depends on invariants not fully
enforced by the type checker, runtime safety, build mode, or ABI.

Examples:
```text
@setRuntimeSafety(false)
unreachable or catch unreachable
undefined
raw pointer or integer casts
many-item and C pointers
extern or packed layout
FFI, asm, MMIO, volatile
atomics and lock-free paths
unchecked, wrapping, or saturating arithmetic
SIMD or vector fast paths
allocator and lifetime boundaries
```
Classify each site:

```text
A/IRREDUCIBLE_BOUNDARY
B/PERF_OR_FOOTPRINT_ONLY
C/REFACTORABLE_TO_WITNESS
```
- A: shrink the boundary and prove caller/callee, target, layout, and wrapper contracts.
- B: keep a safe or reference path, differential proof, and measurements.
- C: move the hazard behind a checked witness or remove it.

Use the hazardous-code, unsafe-boundary, layout, concurrency, ownership,
arithmetic, and systems references.
## Work-surface routing
| Surface | Required reference or proof |
| --- | --- |
| Migration | Scan old APIs and use the current Zig 0.16 toolchain. |
| Build/package/C translation | [build_toolchain_playbook.md](references/build_toolchain_playbook.md) |
| Comptime/reflection | [comptime_playbook.md](references/comptime_playbook.md) |
| Ownership/allocators | [memory_ownership_playbook.md](references/memory_ownership_playbook.md) |
| Errors/failure paths | [error_failure_playbook.md](references/error_failure_playbook.md) |
| Pointers/zero-copy | [unsafe_boundary_playbook.md](references/unsafe_boundary_playbook.md) |
| Layout/ABI/wire/MMIO | [layout_abi_playbook.md](references/layout_abi_playbook.md) |
| I/O/effects | [io_effects_playbook.md](references/io_effects_playbook.md) |
| Atomics/concurrency | [atomics_concurrency_playbook.md](references/atomics_concurrency_playbook.md) |
| Testing/fuzzing | [testing_failure_discovery_playbook.md](references/testing_failure_discovery_playbook.md) |
| Performance | [performance_engineering_playbook.md](references/performance_engineering_playbook.md) |
| Formatting/lint | [linting_playbook.md](references/linting_playbook.md) |
| Cache/disk pressure | [cache_hygiene_playbook.md](references/cache_hygiene_playbook.md) |
## Correctness lanes
Use the repository's own build steps first.

Baseline candidates:
```bash
zig fmt --check .
find . -name '*.zig' \
  -not -path './zig-pkg/*' \
  -not -path './.zig-cache/*' \
  -not -path './zig-out/*' \
  -print0 | xargs -0 zig ast-check
zig build
zig build test
```
`zig ast-check` is syntax and AST proof, not a semantic compile.

For hazardous, optimizer-sensitive, or safety-mode-dependent code, include
relevant modes:

```bash
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
zig build test -Doptimize=ReleaseSmall
```
Add target, allocation-failure, fuzz, differential, timeout, layout, and
benchmark lanes only when they prove an active obligation.

Stable unavailable labels:
```text
VERSION_MISMATCH
LINT_UNAVAILABLE
TEST_UNAVAILABLE
FUZZ_UNAVAILABLE
PROFILE_UNAVAILABLE
COMPTIME_PROOF_UNAVAILABLE
HAZARD_AUDIT_UNAVAILABLE
SAFETY_PROOF_UNAVAILABLE
REPO_CLOSURE_UNAVAILABLE
TIGER_STYLE_UNAVAILABLE
CACHE_REVIEW_SANDBOX_PERMISSION_DENIED
UNMEASURED
```
## Formatting and lint
`zig fmt` is canonical but steerable through syntax-level cues:

```text
trailing commas
first-row array shape
++-composed chunks
real explanatory comments
intermediate declarations
```
Do not fight it with hand-aligned whitespace.

Use repository lint first. For stable Zig 0.16.x third-party linting, use the
repository-pinned compatible `zlinter` release and curated rules rather than an
indiscriminate all-rules default.

## Cache and sandbox
Inventory before deletion.

Treat:
```text
.zig-cache or zig-cache  disposable local build cache
zig-out                  generated output and install prefix
zig-pkg                  dependency working state; inspect modifications and forks
global cache             shared infrastructure
```
Default destructive cache operations to dry-run and refuse while active Zig
builds are detected.

In review or subagent sandboxes, rerun cache permission failures with a writable
global cache before making a code verdict.
## Reporting
```yaml
zig_result:
  artifact_state:
  zig_version:
  task_surfaces: []
  semantic_families: []
  route_ref:
  owner:
  repair_boundary:
  bounds: []
  assertion_pairs: []
  files_changed: []
  proof:
    focused: []
    closure: []
  repository_closure:
  unavailable_lanes: []
  residual_risk: []
  outcome:
```
## Optional read-only specialist
Use `zig_semantic_failure_auditor` when several failure families overlap or the
correct boundary is ambiguous.

The root remains the sole writer and final decision owner.
## Hard rules
- Verify the Zig version.
- Route by work surface and semantic family before material mutation.
- No trusted proof without complete claim binding.
- No escaping borrow without an owner and lifetime decision.
- No observable partial mutation after failure.
- No unbounded growing, waiting, retry, recursion, or fanout without an explicit contract.
- Parser safety and semantic verifier completeness are separate.
- Discover repository contracts for changed artifacts.
- Proof belongs to an exact context and becomes stale when it changes.
- Environment failures are not code failures.
- Benchmark performance claims.
- Preserve user changes and repository conventions.
- Report unavailable proof and explicit exceptions honestly.
