# Artifact-kernel Goal Contract v3

Use this reference for an existing goal whose immutable Evidence marker is
`artifact-kernel-v1`, or for a new goal whose accepted explicit `--goal` route
selects that protocol. A new goal has no marker yet; `open` creates the first
durable protocol fact only after validating the Goal and K0.

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

    extensions: # omit unless the accepted source explicitly grants this risk
      high-critical-example-proof-risk-authority/v1:
        authorizations:
          - counterexample_class_ref:
            law_family: authority | state-machine | identity | persistence | concurrency
            law_ref:
~~~

## Envelope laws

- Use canonical JSON and a content-addressed `artifact_id`.
- Exclude transport location from identity. Relocation with verified identical
  bytes preserves semantic identity.
- Reject unknown fields unless an explicit schema version declares them as
  extensions.
- Treat every materialized artifact as immutable. An initial Goal has no
  predecessor. A semantic change creates a successor under a fresh Goal ID with
  exactly one predecessor in `predecessor_refs`; pair it with a fresh initial
  Construction and admit it through Actuating `open`.
- Record `goal-contract` as the compiling `semantic_author`. The accepted
  specification or direct user authority remains the owner of required
  semantics through `authority.source_ref` and `authority.source_digest`.
  Ledger may canonicalize, fingerprint, validate, and materialize, but does not
  author the payload.
- Preserve supporting provenance as references rather than copied authority.

Set the semantic-owner draft's `artifact_id` to JSON `null`, then materialize it
through `ledger materialize goal-contract-v3 --input DRAFT`. Ledger emits the
canonical content-addressed document without storing it or granting authority.
If that current surface is unavailable, block rather than inventing an identity
algorithm or emitting an unvalidated artifact.

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

Omit `extensions` for an ordinary Goal. The only current extension is
`high-critical-example-proof-risk-authority/v1`. Its `authorizations` array is
nonempty; every entry contains exactly one nonblank stable
`counterexample_class_ref`, one eligible `law_family`, and one `law_ref` that
names a law in this Goal. The exact `law_family` is `authority`,
`state-machine`, `identity`, `persistence`, or `concurrency`; no other family is
eligible. Class entries are unique. Presence of the exact class-family-law tuple
is the accepted source's explicit grant for the narrow High/Critical
example-proof exception; the Goal's content identity already binds that grant
to `authority.source_ref` and `authority.source_digest`. Generic source
identity, `mutation_allowed: true`, a supporting reference, or Construction
prose never implies the grant. An authorization selects no proof or architecture
and remains unused only while the current Construction carries a direct strong
implementation or acceptance proof for its law. Otherwise Ledger derives
pending risk-authority debt that blocks edits and closure until a current
Counterexample and lawful successor exception consume the grant.

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
