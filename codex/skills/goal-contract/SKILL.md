---
name: goal-contract
description: "Compile accepted intent into an exact in-context Goal Contract. Use before multi-step implementation, review closeout, migration, or hard debugging to bind outcomes, laws, authority, scope, compatibility, required observations, and acceptance without selecting architecture, choosing operations, granting mutation, or persisting workflow state."
---

# Goal Contract

## Mission

Compile the current accepted source into the semantic contract consumed by
`$actuating`.

The accepted specification or direct user authority owns required semantics.
`$goal-contract` records them faithfully without extending, reinterpreting, or
selecting how they are implemented.

A Goal Contract is an in-context semantic view, not a durable artifact,
content-addressed identity, Ledger record, mutation capability, or completion
claim.

## Shape

```yaml
goal:
  source:
    ref:
    exact_text_or_digest:
  objective:
    required_outcomes: []
    non_goals: []
  authority:
    source_authority:
    execution_authority:
    mutation_allowed: true | false
  scope:
    repository:
    immutable_base:
    allowed_paths: []
    prohibited_paths: []
  compatibility:
    required_contracts: []
    permitted_breaks: []
    migration_requirements: []
  laws:
    - id:
      statement:
      applicability:
      required_observation:
  acceptance:
    local_completion:
    publication_required: true | false
    review_required: true | false
    required_validation: []
```

Use stable names within the active run. Do not invent a content identity or
predecessor chain.

## Procedure

1. Identify the exact accepted source or direct current user authority.
2. Separate semantic authority from execution authority. Permission to work does
   not decide architecture or prove completion.
3. Distinguish source-fixed artifact or architecture requirements from
   preferences, examples, and proposed means. Only explicit required outcomes,
   hard constraints, and compatibility obligations constrain architecture.
   Never silently promote a suggested means into a Goal law or demote an
   explicit deliverable into a suggestion.
4. Copy required outcomes and explicit non-goals without architectural
   elaboration.
5. Bound repository, immutable base, allowed paths, and prohibited paths.
6. Preserve every required compatibility contract, permitted break, and
   migration obligation.
7. Express each required predicate as one law with applicability and an
   observable result. An unobservable required law blocks.
8. Record mutation, publication, review, and validation posture exactly as
   authorized by the source.
9. Return the complete Goal Contract directly to Actuating.
10. Before any affected mutation, refresh the contract when the accepted source,
    authority, scope, compatibility, or required observations changed.

## Source revisions

A source revision does not require artifact carry-forward.

Recompile the Goal from the current authoritative source, then ask
`$review-fold` to reclassify every currently available applicable finding,
failing test, incident, migration failure, or compatibility failure against the
new Goal.

Do not use source revision to erase unresolved evidence. If relevant owner
evidence cannot be resolved, report the gap and block affected closure or
mutation rather than manufacturing continuity.

## Architecture boundary

The Goal Contract may contain source-fixed architectural constraints. It must
not introduce an architecture merely because the source is underdetermined.

- A named mechanism constrains architecture only when current authority makes it
  a required outcome, hard constraint, or compatibility obligation.
- `$universalist` may nominate only source-permitted choices.
- `$actuating` owns incumbent reconstruction, architecture closure, target
  selection, realization, and closure.
- Review evidence may falsify an implementation or architecture but cannot
  silently change accepted source truth.
- A plan, review, validation pass, or prior implementation never broadens
  source authority.

## Exclusions

Do not include:

- candidate architectures or selected implementation mechanisms;
- review campaigns, attempt state, or clean counts;
- mutation operations or progress;
- publication receipts;
- closure state;
- a Ledger command, definition, or registration packet.

## Handoff

Return:

```text
accepted source
required outcomes and non-goals
authority and mutation posture
repository base and path scope
compatibility obligations
laws and required observations
validation, publication, and review posture
material uncertainty or blockers
```

This handoff is semantic input to Actuating. It grants no mutation and proves no
completion.
