---
name: goal-contract
description: "Compile an accepted goal, implementation specification, review campaign, migration, or hard debugging loop into the sole source-bound Goal Contract. Use before multi-step execution to honor the immutable Evidence-owned goal protocol, emit goal-contract/v3 for an admitted artifact-kernel-v1 goal, preserve GC-v2 only for frozen legacy-actuating-v1 goals, and bind outcomes, laws, authority, scope, compatibility, and acceptance without selecting architecture or granting mutation."
---

# Goal Contract

## Mission

Compile accepted intent into the only per-goal semantic-authority document. The
accepted specification or direct user authority owns required semantics;
`$goal-contract` records them without extending or reinterpreting them.

The Goal Contract records whether mutation was authorized. It never grants
mutation, selects a construction, records mutable progress, or performs an
effect.

## Select the protocol first

Read the goal's immutable protocol marker before compiling anything:

- `artifact-kernel-v1` — read
  [references/artifact-kernel-v1.md](references/artifact-kernel-v1.md) and emit
  one canonical `goal-contract/v3` artifact.
- `legacy-actuating-v1` — read
  [references/legacy-gc-v2.md](references/legacy-gc-v2.md) and preserve the
  frozen `GC-v2` contract and legacy projection.

Do not infer the protocol from nearby artifacts, convert an in-flight goal, or
mix legacy and artifact-kernel semantics. Read it from the canonical Evidence
Ledger. An existing `goal_contract_registered` event derives
`artifact-kernel-v1`; `goal_protocol_registered` derives
`legacy-actuating-v1`. Production Phase 3 blocks every new artifact-kernel goal
until the historical custom-store inventory permits Phase 4. Legacy `open`
validates its selected store and appends or confirms the legacy marker before
`run_opened`; invalid history or a conflicting protocol blocks. Never
hand-write or infer the marker. It is goal metadata; do not add it as an unknown
Goal Contract field.

## Artifact-kernel procedure

Before the first native Ledger command, load `$ledger` and complete `$ledger ensure`
once.

1. Set `semantic_author` to `goal-contract`, the compiling skill. Bind the
   current accepted specification or direct user authority through
   `authority.source_ref` and `authority.source_digest`; bind execution
   authority separately.
2. Copy required outcomes and non-goals without architectural elaboration.
3. Bound repository scope with an exact base reference, allowed paths, and
   prohibited paths.
4. Preserve required compatibility contracts, permitted breaks, and migration
   requirements exactly.
5. Compile each required semantic predicate into one stable law with an
   applicability rule and required observation. An unobservable law blocks.
6. Select only the source-authorized terminal route, publication posture, and
   proof kinds.
7. Materialize canonical JSON through the current Ledger-owned
   canonicalization and fingerprint boundary. Validate with `ledger validate
   goal-contract-v3 --input FILE|-` when that contract is available. A missing
   v3 writer or validator blocks; it never authorizes a GC-v2 fallback.
8. Inspect the complete source-to-contract projection before handing the
   immutable artifact to `$actuating` for Construction Contract selection.

Ledger validation establishes only its declared structural claims. It does not
make Ledger the semantic author and never grants mutation authority.

## Source-authority laws

- `$universalist` may elaborate only source-permitted, underdetermined
  architecture choices, and records the selected result in a Construction
  Contract rather than this artifact.
- `$plan` may supply execution policy but never mutation authority.
- A conflict with source-fixed semantics, non-goals, compatibility,
  architecture constraints, proof requirements, authority, or publication
  posture blocks or requests source revision.
- A changed semantic decision produces an immutable successor with an explicit
  predecessor reference; never edit a materialized contract in place.

## Exclusions

Do not put candidate constructions, implementation architecture, review request
state, attempt history, evidence history, mutable progress, operations, closure
state, or derived campaign state in a Goal Contract.

## Legacy compatibility

Use `GC-v2` only when the Evidence Ledger admits the existing goal as
`legacy-actuating-v1`. Preserve its established `$goal-actuating` -> `actuation-open/v1`
projection and validators exactly. Never write a GC-v2 contract for an
`artifact-kernel-v1` goal.
