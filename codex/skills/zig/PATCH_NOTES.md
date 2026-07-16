# Zig Skill Upgrade Notes — Tiger Style Contract

Date: 2026-07-16

Version: 2.1.0

This release keeps the two-axis semantic failure router and adds a cross-cutting
Tiger Style contract adapted from TigerBeetle for general Zig repositories.

## Governing change

Material Zig implementation and review now select:

```text
Axis A: Zig work surface
Axis B: semantic failure family
Cross-cutting contract: safety, bounded performance, developer experience
```

Tiger Style is not a seventh failure family. It constrains every material route.

## New artifact

```text
ZTS-v1  Zig Tiger Style contract
```

ZTS-v1 binds the exact artifact state to:

```text
bounds and terminal failures
independent assertion pairs
programmer-error versus operating-error treatment
control-flow and function-growth review
network/disk/memory/CPU sketch
narrow proof-bearing exceptions
pre-edit mutation gate
```

## New reference

```text
tiger_style_playbook.md
```

The playbook adapts TigerBeetle's server-oriented rules rather than copying them
blindly. Long-lived services and hot data planes prefer startup allocation and
fixed-capacity pools. Short-lived CLIs may allocate after startup when input,
aggregate memory, ownership, cleanup, and allocation failure are explicit and
bounded.

## New tooling

```text
zig_tiger_style_gate.py
```

The gate has two surfaces:

```bash
python3 codex/skills/zig/scripts/zig_tiger_style_gate.py validate zts.json
python3 codex/skills/zig/scripts/zig_tiger_style_gate.py audit \
  --root . \
  --base main \
  --head WORKTREE
```

The source audit is a changed-code ratchet. It blocks newly introduced or grown
violations including unbounded permanent loops without rationale, direct
recursion, `catch unreachable` without proof, new functions above 70 lines,
lines above 100 columns, unresolved merge reminders, and malformed exceptions.
It reports migration warnings for paired assertions, legacy long functions,
implicit safety-relevant options, empty catches, compound assertions, and
non-obvious while-loop bounds.

## Updated contracts

- `SKILL.md` is version 2.1.0 and remains below 500 lines.
- `decision-contract.yaml` adds boundedness cues and requires ZTS-v1 for material code.
- `implicit_triggers.md` recognizes Tiger Style and bounded-resource cues only in known Zig context.
- The final result schema now reports Tiger Style evidence, bounds, assertion pairs, and exceptions.
- `zig_ops_scorecard.py` now distinguishes ZSR-v1 route sessions from ZTS-v1 contract and exception sessions.

## Validation

The gate carries unit and temporary-Git integration tests for contract
validation, diff parsing, line rules, exception scoping, recursion, function
length ratcheting, assertion-pair warnings, URL handling, and structured exit
semantics.

---

# Zig Skill Upgrade Notes — Semantic Failure Router

Date: 2026-06-20

This release preserves the existing Zig 0.16 systems, comptime,
hazardous-code, cache, formatting, linting, testing, FFI, concurrency, and
performance resources while replacing the top-level encyclopedia-first
workflow with a two-axis router.

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
```

## Updated telemetry

`zig_trigger_audit.py` now records semantic-family opportunity sessions only in
a known Zig context.

`zig_ops_scorecard.py` now reports ZSR route evidence and prefers
`seq skill-decision-audit` when available instead of treating activation as
proof that `$zig` changed the route.

## New specialist

```text
zig_semantic_failure_auditor
```

The specialist is read-only. Root remains the sole writer.

## Structural reduction

`SKILL.md` is below 500 lines and delegates detailed protocols to references.

The previous package had the right knowledge but often loaded the governing
failure rule after implementation selection. This release makes the failure
family a pre-edit gate.

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
