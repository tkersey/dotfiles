---
name: zig
description: "Use for Zig 0.16.0 implementation, review, migration, build/package, comptime/codegen, testing/fuzzing, profiling, hazardous low-level code, FFI/layout, concurrency, cache operations, and semantic failures involving claim binding, lifetime escape, fallible mutation atomicity, verifier completeness, repository closure, or stale proof context. Verify the installed Zig version before version-sensitive work."
metadata:
  version: "2.1.0"
  activation_cost: medium
  default_depth: adaptive
---
# Zig

## Mission

Route Zig work by both its engineering surface and its semantic failure family,
then make the smallest owner-correct, bounded change.

## Preflight

Before version-sensitive work:

```bash
zig version
git rev-parse --show-toplevel
git rev-parse HEAD
git status --short
```

Assume Zig `0.16.0` only when neither repository nor user specifies another
version. A mismatch is `VERSION_MISMATCH`, not proof under the requested
toolchain.

## Two-axis route

Classify the work surface:

```text
migration | API/domain | build/package | comptime/codegen | formatting/lint
testing/fuzzing | low-level | ownership/lifetime | FFI/layout | I/O/effects
concurrency | performance | cache/disk
```

Classify the semantic family:

```text
claim-binding | lifetime-escape | atomic-transition
verifier-completeness | repo-closure | proof-context | none
```

For material work, retain a compact ZSR-v1 route with owner, counterexample,
repair boundary, forbidden shortcuts, bounds, and required proof.

## Always-live engineering contract

Prioritize:

```text
semantic correctness
bounded and predictable resource use
maintainability and developer experience
```

Name bounds for work that can grow, wait, retry, allocate, recurse, or fan out.
Distinguish programmer error from operating error. Keep safety-relevant
assertions independent. Run proof in the final repository, target, mode, option,
dependency, and generated-artifact context.

## Conditional playbooks

Load only the active family:

- [claim_binding_playbook.md](references/claim_binding_playbook.md) for
  fingerprints, receipts, certificates, manifests, checkpoints, and pass/fail
  APIs.
- [memory_ownership_playbook.md](references/memory_ownership_playbook.md) when
  borrowed, parsed, arena-backed, container-backed, or snapshot data escapes an
  owner.
- [atomic_transition_playbook.md](references/atomic_transition_playbook.md) and
  [error_failure_playbook.md](references/error_failure_playbook.md) when a
  fallible transition mutates before all later failure points are prepared.
- [verifier_completeness_playbook.md](references/verifier_completeness_playbook.md)
  for parsers, protocols, hostile bytes, and public verification predicates.
- [repo_closure_playbook.md](references/repo_closure_playbook.md) when files,
  build steps, fixtures, goldens, manifests, or generated artifacts change.
- [semantic_failure_router.md](references/semantic_failure_router.md) only when
  family selection or the full ZSR-v1 shape is ambiguous.

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it when one linked family
playbook is sufficient. Load it only for hazardous low-level classification,
cross-family work, detailed performance/concurrency/FFI guidance, full
reporting contracts, or an unported edge route. Its frontmatter is archived
source, not a second skill definition.

## Common implementation loop

1. Pin version and artifact state.
2. Inspect build, tests, lint, guidance, and relevant owners.
3. Select both axes.
4. Name the bad trace and strongest cheap enforcement boundary.
5. Prepare the smallest bounded change.
6. Run focused positive and negative proof.
7. Run repository-closure proof when artifacts changed.
8. Re-run final proof in the final context and report invalidators.

A green build alone is not proof when the change trusts claims, returns borrowed
data, mutates multiple owners, parses hostile input, or changes repository
contracts.
