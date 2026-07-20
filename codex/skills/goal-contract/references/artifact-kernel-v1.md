# Goal Contract v3

Materialize one immutable canonical JSON document with this shape:

~~~yaml
artifact:
  schema: goal-contract/v3
  artifact_id:
  goal_id:
  semantic_author: goal-contract
  created_at:
  predecessor_refs: []
  supporting_refs: []

  payload:
    objective:
      required_outcomes: []
      non_goals: []
    authority:
      source_ref:
      source_digest:
      execution_authority_ref:
      execution_authority_digest:
      mutation_allowed: true | false
    scope:
      repository:
      base_ref:
      allowed_paths: []
      prohibited_paths: []
    compatibility:
      required_contracts: []
      permitted_breaks: []
      migration_requirements: []
    laws:
      - law_id:
        statement:
        applicability:
        required_observation:
    acceptance:
      terminal_route: complete | ready-to-ship
      publication_required: true | false
      required_proof_kinds: []
~~~

## Envelope laws

- Use canonical JSON and a content-addressed `artifact_id`.
- `goal_id` matches `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`. Reuse a valid
  accepted-source goal identity; otherwise allocate one stable opaque identity
  once. Never derive it from mutable Goal content or substitute an
  `artifact_id` digest.
- Exclude transport location from identity. Relocation with verified identical
  bytes preserves semantic identity.
- Reject unknown fields.
- Treat every materialized Goal as immutable. A semantic change creates a
  successor with the same `goal_id`, exactly one predecessor `artifact_id`,
  and a new content-addressed `artifact_id`.
- Record `goal-contract` as the compiling `semantic_author`. The accepted
  source remains the owner of required semantics through `source_ref` and
  `source_digest`.
- Preserve supporting provenance as references rather than copied authority.

Ledger may materialize canonical bytes and validate this envelope. It does not
author the payload, store mutable goal state, choose a Construction, grant
mutation, or decide closure.

## Field laws

- `objective` contains required outcomes and explicit non-goals only.
- `authority` binds accepted source authority and execution authority
  separately. `mutation_allowed: true` records permission but grants no
  operation authority by itself.
- `scope` may narrow but never broaden the accepted source.
- `allowed_paths` and `prohibited_paths` are duplicate-free canonical literal
  repository-path sets. `.` is allowed; every other path is relative and has
  no empty, `.` or `..` component, trailing slash, or backslash.
- The `.git` root and the Artifact Kernel control store, including slash
  descendants, are reserved under ASCII case-folding. Root scope cannot
  re-admit them.
- `compatibility` preserves every source-fixed contract and names only
  source-permitted breaks and required migrations.
- Every law is stable, source-derived, applicable, and observable.
- `acceptance` records the terminal route, publication requirement, and proof
  kinds; it records no proof result or closure judgment.

## Forbidden content

Exclude candidate constructions, architecture selection, Counterexample
classification, review attempts, evidence events, operations, mutable state,
progress, and closure.

## Validation claims boundary

Every validator result must distinguish structural claims from authority:

~~~yaml
validated:
  claims_established: []
  explicitly_not_established: []
  authority_granted: false
  storage_mutated: false
~~~

Structural validation is not semantic truth, Construction selection, execution
authority, publication authority, or completion.
