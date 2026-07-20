---
name: goal-contract
description: "Compile an accepted goal, implementation specification, review campaign, migration, or hard debugging loop into the sole source-bound Goal Contract. Use before multi-step execution to honor the Evidence-owned goal protocol, emit goal-contract/v3 for an existing admitted or new route-selected artifact-kernel-v1 goal, preserve GC-v2 only for frozen legacy-actuating-v1 semantics, and bind outcomes, laws, authority, scope, compatibility, and acceptance without selecting architecture or granting mutation."
---

# Goal Contract

## Mission

Compile accepted intent into the only per-goal semantic-authority document. The
accepted specification or direct user authority owns required semantics;
`$goal-contract` records them without extending or reinterpreting them.

The Goal Contract records whether mutation was authorized. It never grants
mutation, selects a construction, records mutable progress, or performs an
effect.

## Select the protocol before compiling

For an existing Goal ID, read its immutable protocol from the canonical
Evidence Ledger. `goal_contract_registered` derives `artifact-kernel-v1`;
`goal_protocol_registered` derives `legacy-actuating-v1`. Never infer the
protocol from nearby artifacts, convert an in-flight goal, or mix protocols.

For a new Goal ID with no canonical Evidence, take the protocol only from the
accepted execution route. In production Phase 4, an explicit `--goal GOAL_ID
... open` route selects `artifact-kernel-v1`; the unqualified route selects
frozen `legacy-actuating-v1`. An ambiguous or unaccepted route blocks. This
selector is transient control input, not an artifact, Goal field, durable
marker, or authority source.

- `artifact-kernel-v1` — read
  [references/artifact-kernel-v1.md](references/artifact-kernel-v1.md) and emit
  one canonical `goal-contract/v3` artifact.
- `legacy-actuating-v1` — read
  [references/legacy-gc-v2.md](references/legacy-gc-v2.md) and preserve the
  frozen `GC-v2` contract and legacy projection.

Artifact `open` validates the exact `actuation-open/v2` envelope, Goal, K0,
subject, and authority before appending `goal_contract_registered`, the first
durable artifact-kernel protocol fact. Legacy `open` validates its selected
store and appends or confirms `goal_protocol_registered` before `run_opened`.
Any conflicting Evidence or invalid history blocks. Historical custom-store
inventory gates retirement of legacy writers, not explicit opt-in admission.
Never hand-write a marker or create a pre-registration peer artifact.

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
6. Only when the accepted source explicitly grants example-only proof risk for
   one stable High/Critical Counterexample class and Goal law, compile the
   versioned authorization extension from
   [the v3 contract](references/artifact-kernel-v1.md). Generic source identity,
   mutation permission, or a Construction request never implies this grant.
7. Select only the source-authorized terminal route, publication posture, and
   proof kinds.
8. Set `artifact_id` to JSON `null` in the semantic-owner draft, then run
   `ledger materialize goal-contract-v3 --input DRAFT`. Persist the emitted
   canonical document and validate it with `ledger validate goal-contract-v3
   --input FILE|-`. A missing current materializer or validator blocks; it
   never authorizes a GC-v2 fallback.
9. Inspect the complete source-to-contract projection before handing the
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

Use `GC-v2` only when the Evidence Ledger admits an existing goal as
`legacy-actuating-v1` or the accepted route selects that protocol for a new
goal. Preserve its established `$goal-actuating` -> `actuation-open/v1`
projection and validators exactly. Never write a GC-v2 contract for an
`artifact-kernel-v1` goal.
