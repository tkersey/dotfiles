# Artifact-kernel Goal Contract v3

Use this reference only for a goal whose immutable protocol marker is
`artifact-kernel-v1`.

## Exact shape

The following is a readable schematic. Materialize it as canonical JSON; do
not add fields.

~~~yaml
artifact:
  schema: goal-contract/v3
  artifact_id:
  goal_id:
  semantic_author:
  created_at:
  predecessor_refs: []
  supporting_refs:
    - accepted-source-ref
    - specification-governance-ref
    - execution-policy-ref

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
- Exclude transport location from identity. Relocation with verified identical
  bytes preserves semantic identity.
- Reject unknown fields unless an explicit schema version declares them as
  extensions.
- Treat every materialized artifact as immutable. A semantic change creates a
  successor and records the predecessor in `predecessor_refs`.
- Record `goal-contract` as the compiling `semantic_author`. The accepted
  specification or direct user authority remains the owner of required
  semantics through `authority.source_ref` and `authority.source_digest`.
  Ledger may canonicalize, fingerprint, validate, and materialize, but does not
  author the payload.
- Preserve supporting provenance as references rather than copied authority.

Use the current Ledger-owned writer or fingerprint implementation. If it is
unavailable, block rather than inventing an identity algorithm or emitting an
unvalidated artifact.

## Field laws

- `objective` contains required outcomes and explicit non-goals only.
- `authority` binds accepted source authority and execution authority
  separately. `mutation_allowed: true` records accepted permission; the Goal
  Contract still grants no capability. A plan-only or gate-only source without
  current execution authority requires `mutation_allowed: false`.
- `scope` may narrow but never broaden the accepted source.
- `compatibility` preserves every source-fixed contract and names only
  source-permitted breaks and required migrations.
- Each `laws` entry is stable, source-derived, applicable, and observable.
- `acceptance` records terminal route, publication requirement, and proof kinds;
  it does not record proof results or closure.

## Forbidden content

Exclude candidate constructions, architecture selection, Counterexample
classification, review bindings or attempts, evidence events, operations,
mutable state, progress, and closure. Those belong to Construction Contract,
Counterexample Set, Evidence Ledger, or deterministic projections.

## Validation claims boundary

Require this explicit claims boundary:

~~~yaml
validated:
  claims_established: []
  explicitly_not_established: []
  authority_granted: false
  storage_mutated: false | true
~~~

A pure artifact validator reports `storage_mutated: false`. Structural
validation is not semantic truth, construction selection, execution authority,
or publication authority.
