---
name: zig
description: >-
  Implement, debug, review, migrate, and optimize Zig code and build systems.
  Use when the task requires Zig-specific language or toolchain expertise.
metadata:
  version: "3.2.0"
  activation_cost: low
  default_depth: adaptive
---
# Zig

Complete the requested Zig work against the repository's actual toolchain and
contracts. Choose representations that preserve required laws, ownership, failure
guarantees and performance without unnecessary machinery. Construction does not
require an existing defect; correct existing code is a valid review outcome.

## Working contract

For version-sensitive work, resolve the requested target and repository pin,
then compare with `zig version`. A minimum version is not an exact pin, and a
development build is not a release. Use `0.17.0` for otherwise unpinned work;
verify the official release index when asked for latest. Match help, documentation
and stdlib to the selected compiler. Do not silently upgrade a pinned project or
claim validation by a compiler that was not used.

Read the references needed for the task. Their lenses, examples and templates
support judgment; they do not impose a fixed sequence or a closed set of designs.
User requirements, repository contracts, safety obligations and authorized effects
remain binding. Produce inventories or structured reports when requested or needed
by a known consumer, not as prerequisites to ordinary work. Establish consequential
invariants using the relevant code, types, contracts and evidence; an empty form
is neither a safety defect nor permission to waive a real obligation.

## Reference map

| Task or uncertainty | Reference |
| --- | --- |
| Version selection, 0.16-to-0.17 migration, silent semantic changes | [0.17 migration map](references/zig_0_17_migration.md) |
| Overlapping semantic concerns; choosing an owner or repair boundary | [Semantic lenses](references/semantic_failure_router.md) |
| Resource bounds, assertion pairs, control flow, Tiger Style | [Engineering contracts](references/engineering_contracts.md) |
| Constructive API design, comptime, reflection, generated types and specialization cost | [Comptime playbook](references/comptime_playbook.md) |
| Build, packages, dependencies, C translation, targets and LTO | [Build/toolchain](references/build_toolchain_playbook.md) |
| Allocation, borrowing, lifetime escape and ownership transfer | [Ownership](references/memory_ownership_playbook.md) |
| Errors, cleanup, failure guarantees and partial progress | [Error handling](references/error_failure_playbook.md), [state transitions](references/atomic_transition_playbook.md) |
| Proof-like values, fingerprints and authoritative claim binding | [Claim binding](references/claim_binding_playbook.md) |
| Parser safety and semantic validation of hostile input | [Verifier completeness](references/verifier_completeness_playbook.md) |
| Raw pointers, unchecked operations and safe/reference alternatives | [Hazard audit](references/hazardous_code_audit_playbook.md), [boundary design](references/unsafe_boundary_playbook.md) |
| Layout, ABI, wire formats and MMIO | [Layout/ABI](references/layout_abi_playbook.md) |
| Explicit I/O capabilities, deterministic effects and cancellation | [I/O/effects](references/io_effects_playbook.md) |
| Atomics, concurrency, synchronization and liveness | [Concurrency](references/atomics_concurrency_playbook.md) |
| Tests, allocation failure, fuzzing and forced compile-fail instantiation | [Failure discovery](references/testing_failure_discovery_playbook.md) |
| Performance, allocation pressure, SIMD, binary size and profiling | [Performance](references/performance_engineering_playbook.md), [profiling tools](references/profiling_playbook.md) |
| Formatting and repository-pinned lint | [Linting](references/linting_playbook.md) |
| File registries, generated artifacts, examples and aggregate checks | [Repository closure](references/repo_closure_playbook.md) |
| Validation reuse, changed inputs, unavailable lanes and sandbox diagnostics | [Evidence context](references/evidence_context_playbook.md) |
| Cache inventory, disk pressure and guarded cleanup | [Cache hygiene](references/cache_hygiene_playbook.md), [CI cache policy](references/cache_ci_policy.md) |

The optional `zig_semantic_failure_auditor` provides read-only independent
challenge for a concrete uncertainty. It is not a required stage; the receiving
workflow retains selection, implementation and closure authority.

## Verification and completion

Use the project's checks for the changed project. Select additional evidence to
resolve specific uncertainty, including contracts that still compile but change
meaning during migration. The bundled example runner validates the skill's
examples, not a consuming project. Distinguish source arguments, compiler checks,
native execution, cross-compilation, sampled fuzzing and measured performance.
Reuse checks while relevant inputs and assumptions remain established; rerun
affected checks after relevant changes or when applicability is unknown.

For implementation requests, finish the authorized change, relevant verification
and delivery; fix introduced failures and rerun affected checks without stopping
for approval at each disposable local test. Preserve user edits and review-only
scope. When a real safety, authority or dependency boundary blocks one action,
continue independent authorized work and state the actual limitation.

Return the result, consequential decisions, commands/outcomes and residual risks
in the receiving workflow's format. Do not claim unrun checks, performance gains
or model-efficacy improvements.
