---
name: goal-contract
description: "Compile accepted intent into the sole source-bound goal-contract/v3 artifact. Use before multi-step implementation, review closeout, migration, or hard debugging to bind outcomes, laws, authority, scope, compatibility, and acceptance without selecting architecture, choosing operations, or granting mutation."
---

# Goal Contract

## Mission

Compile accepted intent into the only per-goal semantic-authority document.
The accepted specification or direct user authority owns required semantics;
`$goal-contract` records them without extending or reinterpreting them.

The Goal Contract records whether mutation was authorized. It never grants
mutation, selects a Construction, chooses an operation, records mutable
progress, or performs an effect.

Read [the exact v3 contract](references/artifact-kernel-v1.md).

## Procedure

1. Identify the accepted specification or direct user authority and preserve
   its exact source reference and digest.
2. Separate semantic source authority from execution authority. A plan, review,
   gate, or validator pass never implies mutation permission.
3. Copy required outcomes and non-goals without architectural elaboration.
4. Bound repository scope with the exact repository, base reference, allowed
   paths, and prohibited paths.
5. Preserve required compatibility contracts, expressly permitted breaks, and
   migration requirements.
6. Compile every required predicate into one stable law with applicability and
   a required observation. An unobservable required law blocks.
7. Select only the source-authorized terminal route, publication posture, and
   proof kinds.
8. Set the draft `artifact_id` to JSON `null`. After `$ledger ensure`, request
   the workflow's current Actuating adapter gate. When invoked standalone,
   require `ledger --version` to be at least `0.11.0` and verify that
   `ledger --source actuation --help` exposes only the current six-command
   adapter before materialization. Ledger canonicalizes and validates
   structure; it does not author semantics or grant authority.
9. Inspect the complete source-to-Goal projection before handing the immutable
   artifact to `$actuating` for Construction selection.

## Source-authority laws

- `$universalist` may elaborate only source-permitted, underdetermined
  architecture choices. The selected result belongs in a Construction
  Contract, not the Goal Contract.
- `$plan` may supply execution policy but never mutation authority.
- Review evidence may falsify a Construction but cannot change accepted source
  truth or authorize a repair.
- A conflict with source-fixed semantics, non-goals, compatibility,
  architecture constraints, proof requirements, authority, or publication
  posture blocks or requests a source revision.
- A changed semantic decision creates an immutable successor Goal with the
  same `goal_id`, exactly one predecessor `artifact_id`, a new content-addressed
  `artifact_id`, and a fresh initial Construction. Never edit the predecessor
  in place.

## Exclusions

Do not put candidate constructions, selected architecture, Counterexample
classification, review bindings or attempts, operations, evidence events,
mutable progress, campaign state, or closure state in a Goal Contract.

## Handoff

Return:

~~~text
Goal Contract identity
accepted source identity
execution-authority identity
mutation posture
scope
laws and observations
compatibility obligations
acceptance route
~~~

The handoff is semantic input to Actuating. It is not an operation request or
proof of completion.
