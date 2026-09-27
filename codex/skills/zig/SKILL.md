---
name: zig
description: >-
  Implement, debug, review, and optimize Zig code and build systems.
  Use for Zig-specific language, toolchain, ownership, comptime,
  interoperability, or performance work.
metadata:
  version: "3.0.0"
  activation_cost: low
  default_depth: adaptive
---
# Zig

Complete the requested Zig work against the repository's actual toolchain and
contracts. Prefer the simplest representation that preserves the required laws,
ownership, failure guarantees, and performance. Use this document as a reference
map, not an itinerary. A new feature need not begin as a defect investigation.

## Working contract

Inspect what the task needs. For version-sensitive work, establish the repository's
pinned version and compare it with `zig version`; use `0.16.0` only when neither the
repository nor user specifies a target. Check installed help and stdlib sources
before adapting version-sensitive examples. Report a mismatch without claiming
that a different compiler validated the target; continue independent work.

Honor repository conventions, user changes, review-only scope, and authorization
for external or destructive effects. A required safety argument can block an
unsafe action; an unfilled routing form cannot. Resolve consequential uncertainty
with inspection, bounded disposable probes, or focused tests within task scope.

The references supply non-exhaustive lenses, not a closed taxonomy. Consult only
those relevant to a live decision or risk. Ordinary construction, explanation,
and small edits do not require a semantic-family classification, ZSR-v1 packet,
resource sketch, specialist invocation, or a separate Zig reporting protocol.
When an actual consumer requires a structured artifact, honor that interface.

## Reference map

| Task or uncertainty | Reference |
| --- | --- |
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

The optional `zig_semantic_failure_auditor` is read-only. Use it for a concrete
ambiguity or independent challenge, not as a required stage. The receiving
workflow retains selection, execution, and closure authority.

## Verification and completion

Use the repository's own checks and the active workflow's required verification.
Choose additional lanes to resolve specific uncertainty: allocation failures for
cleanup/atomicity, semantic mutations for claim checking, compile-fail cases for
invalid type shapes, target/mode matrices for low-level assumptions, and measured
comparisons for performance claims. A successful build is not evidence for an
unexercised contract; a fuzz run is sampled evidence, not a proof of totality.

Reuse evidence only when its relevant inputs and assumptions remain established.
Rerun affected checks after relevant changes or when relevance is unknown; do not
repeat checks solely to produce a new receipt. The evidence-context reference
owns the distinction between changed provenance and changed validation inputs.

For implementation requests, finish the requested change and relevant checks,
correct failures introduced by the change, and rerun affected checks. Do not stop
at a route, plan, or first implementation. Do not convert a review or explanation
into an unauthorized edit. Continue independent authorized work when one lane is
unavailable, and state the actual limitation.

Return the result, consequential decisions, exact commands/outcomes, and residual
risks in the receiving workflow's format. Omit empty fields and duplicate reports.
Do not claim tests, benchmarks, model comparisons, or unavailable lanes were run.
