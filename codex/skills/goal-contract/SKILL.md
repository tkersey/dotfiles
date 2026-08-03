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
8. Set the draft `artifact_id` to JSON `null`. After `$ledger ensure`, resolve
   the active `$goal-contract` and `$actuating` skill roots. Require Ledger
   1.x, `ledger-artifact-abi/v1`, and successful `ledger definition check`
   results for their canonical Goal and Evidence definitions.
9. Materialize the authored draft, then register the returned canonical
   artifact through the Evidence protocol before handoff:

   ~~~bash
   ledger materialize \
     --definition <goal-contract-skill-root>/definitions/ledger/goal-contract.json \
     --input contract=<goal-contract-draft.json> \
     --format json

   ledger transact \
     --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
     --operation <register-goal|register-goal-carry-forward> \
     --repo <repo> \
     --input goal_registration=<goal-registration.json> \
     --param goal=<goal-id> \
     --format json
   ~~~

   The registration packet is passive JSON containing
   `schema:"actuating-goal-registration/v1"`, the exact `goal_id`, and the
   materialization result's parsed `canonical_content` as `body`. Use
   `register-goal-carry-forward` only for the source-revision transition that
   must preserve the predecessor Construction while `$review-fold` classifies
   carried Counterexamples; otherwise use `register-goal`.
10. Require `ledger-materialization-result/v1` with a non-null `artifact_id`
    equal to `artifact.artifact_id`, then
    `ledger-transaction-result/v1` for the selected registration operation
    with one appended event.
    Retain the complete canonical artifact and registration event identity as
    the current Goal Contract. Ledger canonicalizes, identifies, and registers
    its structure; it does not author semantics or grant authority.
11. Inspect the complete source-to-Goal projection before handing the returned
    immutable artifact and exact identity to `$actuating` for Construction
    selection.

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
  same `goal_id`, exactly one predecessor `artifact_id`, and a new
  content-addressed `artifact_id`. A direct clean commit of the exact
  already-observed scoped worktree does not change source authority and uses
  Actuating's typed subject-commit provenance transition instead. Any other
  subject drift or source-bound scope change requires a successor Goal. Neither
  transition resets Construction or Counterexample lineage: return the current
  Construction identity to Actuating, which selects a successor with exactly
  one predecessor.
  Only the first Construction in the current authoritative v3 lineage for the
  `goal_id` may be initial with no predecessor. When an explicit source revision
  occurs while accepted or blocked Counterexamples remain unresolved, or
  brings a `follow-up` class within the successor Goal's scope, use the
  carry-forward transition: cite every Set carrying those classes in the
  successor Goal's `supporting_refs` as
  `counterexample-set:<artifact_id>`; require a successor Set to cite that exact
  Goal as `goal-contract:<artifact_id>` and each carried Set as
  `counterexample-set:<artifact_id>`, evaluate the predecessor Construction,
  preserve Set lineage, and assign every carried class a disposition; then
  re-axiomatize before Actuating selects a successor Construction or permits an
  affected mutation. Never edit a predecessor in place or use source revision
  to erase review debt.

## Exclusions

Do not put candidate constructions, selected architecture, Counterexample
classification, review bindings or attempts, operations, evidence events,
mutable progress, campaign state, or closure state in a Goal Contract.

## Handoff

Return:

~~~text
Goal Contract identity
goal registration event identity
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
