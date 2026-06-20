# Zig Skill Upgrade Notes — Semantic Failure Router

Date: 2026-06-20

This release preserves the existing Zig 0.16 systems, comptime, hazardous-code, cache, formatting, linting, testing, FFI, concurrency, and performance resources while replacing the top-level encyclopedia-first workflow with a two-axis router.

## Governing change

Before material mutation, `$zig` now classifies:

```text
Axis A: Zig work surface
Axis B: semantic failure family
```

Semantic families:

```text
claim-binding
lifetime-escape
atomic-transition
verifier-completeness
repo-closure
proof-context
```

## New artifacts

```text
ZSR-v1  zig semantic route
ZPE-v1  zig proof epoch
ZSFA-v1 read-only semantic failure audit
```

## New references

```text
semantic_failure_router.md
claim_binding_playbook.md
atomic_transition_playbook.md
verifier_completeness_playbook.md
repo_closure_playbook.md
proof_epoch.md
decision-contract.yaml
```

## Strengthened references

```text
memory_ownership_playbook.md
  mandatory escape table and owner-carried return pattern

error_failure_playbook.md
  prepare/commit/publish and full observable rollback

testing_failure_discovery_playbook.md
  semantic mutation matrix and epoch-bound reproduction

build_toolchain_playbook.md
  repository registry/golden/generated-artifact closure

implicit_triggers.md
  context-bounded semantic-family cues
```

## New tooling

```text
zig_semantic_route_gate.py
zig_repo_closure_scan.py
zig_proof_epoch.py
regenerate_manifest.py
```

## Updated telemetry

`zig_trigger_audit.py` now records semantic-family opportunity sessions only in a known Zig context.

`zig_ops_scorecard.py` now reports ZSR route evidence and prefers `seq skill-decision-audit` when available instead of treating activation as proof that `$zig` changed the route.

## New specialist

```text
zig_semantic_failure_auditor
```

The specialist is read-only. Root remains the sole writer.

## Structural reduction

`SKILL.md` is below 500 lines and delegates detailed protocols to references.

The previous package had the right knowledge but often loaded the governing failure rule after implementation selection. This release makes the failure family a pre-edit gate.

## Retained prior capabilities

The surrounding existing skill directory continues to provide:

```text
Zig 0.16 migration
comptime/reflection/generated types
hazardous-code/Illegal Behavior auditing
allocator and lifetime engineering
unsafe pointer/zero-copy boundaries
layout/ABI/MMIO/wire formats
I/O/effects
atomics/concurrency
build/package/C translation
cache hygiene
formatting/lint steering
testing/fuzzing/allocation failure
performance/profiling
```

Do not delete unmodified references or scripts when installing this overlay.
