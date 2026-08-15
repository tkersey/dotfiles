# Independently Durable Universalist Decision

This module is normative only when a consequential Universalist decision must
remain independently addressable outside a current Actuating Construction.

## Disclosure contract

**Load when:** the consequential analysis is complete, no current Actuating
Construction will carry the complete nomination, adjudication, proof, and
retirement decision, and either the user requests a durable record or
standalone, cross-session, multi-actor, migration, or supersession work must
address the decision directly.

**Do not load when:** Actuating owns the current Construction, the seam is
routine or uncontested, materiality exists without an independent durability
need, or the user asked only for analysis.

**Return:** one Ledger-addressed Universalist plan and, after standalone root
adjudication, exactly one root `SDR-v1` receipt.

Independent durability controls storage. It does not make a candidate more
correct and does not authorize mutation by itself.

## Authority

Universalist owns architecture policy and the meaning of the plan and receipt.

Ledger owns plan identity, addressing, structural validation, canonicalization,
custody, and atomic replacement. A successful Ledger operation is
definition-relative and grants no architecture, mutation, publication, or
closure authority.

Tune's canonical definition owns the structural form of `SDR-v1`.

`references/decision-contract.json` is the machine-readable authority for
triggers, routes, clauses, and required evidence. `SKILL.md` and
`references/consequential-boundary.md` supply operational semantics.

## Bootstrap

Before the first Ledger command in the workflow, load `$ledger` and complete
`$ledger ensure` once. Require Ledger major version 1 and
`ledger-artifact-abi/v1`.

Do not bootstrap per command and do not hand-edit `.ledger/*`.

## Bind an existing current-format plan

For a valid pre-cutover `universalist-plan/v1` document already under
`.ledger/universalist/`, bind that exact file once before projecting or revising
it:

```bash
ledger transact \
  --definition <universalist-skill-root>/definitions/ledger/plan-document.json \
  --operation bind-existing \
  --repo PROJECT_ROOT \
  --param plan_file=PLAN_FILE \
  --format json
```

This validates the existing bytes and writes only Ledger-owned binding
metadata. It fails closed for invalid or already-bound documents and is not a
normal read path.

## Migrate a legacy root plan

For a valid legacy document at
`.ledger/universalist-plan-<PLAN_ID>.md`, perform the explicit one-shot copy into
the canonical address:

```bash
ledger transact \
  --definition <universalist-skill-root>/definitions/ledger/plan-document.json \
  --operation migrate-legacy \
  --repo PROJECT_ROOT \
  --input legacy_plan=PROJECT_ROOT/.ledger/universalist-plan-PLAN_ID.md \
  --param plan_file=plan-PLAN_ID.md \
  --format json
```

This operation never runs during normal reads or writes. It leaves the legacy
file untouched, creates the canonical document atomically, and fails when the
canonical address already exists.

## Allocate a new plan

```bash
ledger transact \
  --definition <universalist-skill-root>/definitions/ledger/plan-document.json \
  --operation create \
  --repo PROJECT_ROOT \
  --input template=<universalist-skill-root>/templates/universalist-plan.md \
  --format json
```

Retain:

```text
generated_outputs.plan_id
generated_outputs.plan_file
effect logical_ref
revision_after
```

Resolve an exact plan or the newest addressed plan with:

```bash
ledger project \
  --definition <universalist-skill-root>/definitions/ledger/plan-document.json \
  --projection path \
  --repo PROJECT_ROOT \
  --param plan_file=PLAN_FILE \
  --format text

ledger project \
  --definition <universalist-skill-root>/definitions/ledger/plan-document.json \
  --projection latest \
  --repo PROJECT_ROOT \
  --format json
```

## Author and revise the plan

Before mutation, author the applicable consequential decision into the plan:

```text
current-context contract
composition context and decision owner/carrier
ordinary candidate
comparison universe
axis and typed hole
latent-structure disposition and transition witness, when material
relevant card dispositions
Boundary Artifact Contract
enforcement matrix
residual obligations
invalidation triggers / proof lease
law and falsifier
specialized mechanic obligations, when selected
```

Admit each revision through the owner definition:

```bash
ledger transact \
  --definition <universalist-skill-root>/definitions/ledger/plan-document.json \
  --operation revise \
  --repo PROJECT_ROOT \
  --input plan=PLAN_DRAFT \
  --param plan_file=PLAN_FILE \
  --param expected_revision=REVISION \
  --format json
```

A stale expected revision blocks replacement. Never overwrite the file directly.

## Materialize and append the root receipt

After standalone root adjudication, author exactly one `SDR-v1` JSON receipt.
Validate and canonicalize it through Tune's canonical definition:

```bash
ledger materialize \
  --definition <tune-skill-root>/definitions/ledger/skill-decision-receipt.json \
  --input contract=<universalist-skill-root>/references/decision-contract.json \
  --input receipt=RECEIPT_JSON \
  --format json
```

Append it atomically to the plan:

```bash
ledger transact \
  --definition <universalist-skill-root>/definitions/ledger/plan-document.json \
  --operation append-receipt \
  --repo PROJECT_ROOT \
  --input contract=<universalist-skill-root>/references/decision-contract.json \
  --input receipt=RECEIPT_JSON \
  --param plan_file=PLAN_FILE \
  --param expected_revision=REVISION \
  --format json
```

Pass every applicable clause explicitly:

- always include the route's general consequential clauses;
- add `UNI-RECOGNITION-001` and trigger `UNI-RECOGNIZE` only when recognition
  materially changes the nomination or transition;
- add `UNI-DOUBLE-001` only when the corresponding specialized mechanic is
  selected;
- add `UNI-ROOT-001` for every independently durable decision;
- add `UNI-RECLASSIFY-001` and trigger `UNI-RECLASSIFY` when the durable
  decision follows material reclassification;
- for `UNI-OBSTRUCT`, use `UNI-OBSTRUCTION-001` instead of
  `UNI-ARTIFACT-001`.

Neither a Ledger pass nor any structural validator proves prose-to-contract
equivalence or grants architecture authority.

## Exactly-once and supersession law

- Emit exactly one root receipt per independently durable changed seam.
- Worker or subagent packets reference the root decision ID; they do not emit
  competing receipts.
- Do not span unrelated seams with one receipt.
- Once emitted, never overwrite a receipt.
- When evidence invalidates the decision, retain the prior receipt, record the
  invalidation, and create an independently durable successor only when the
  durability gate still holds.
- Routine `retain` reclassification does not allocate a new plan or receipt.

## Completion

Return:

```text
Plan id:
Plan file:
Logical reference:
Revision:
Selected route:
Applicable clauses:
Root receipt: emitted / pending
Storage mutation:
Remaining owner action:
```

The plan and receipt make the decision addressable. They do not authorize
implementation, publication, or closure.
