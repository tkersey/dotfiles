# Evidence Ledger Adapter

The Evidence Ledger is Actuating's append-only observation artifact. Ledger
canonicalizes, structurally validates, appends, replays, and projects. Event
bodies retain their domain owners. Ledger never derives causal generators,
selects a Construction, grants mutation, interprets review or Ship, or closes.

The passive definitions under `../definitions/ledger/` are normative.

## Runtime and version gate

After `$ledger ensure` once for the workflow, require Ledger 1.1.0 or newer
within major version 1, `ledger-artifact-abi/v1`, the segmented event-log
capability flags, and successful checks for every selected Actuating Ledger
definition. When session evidence is needed, require Seq 1.x,
`seq-observation-abi/v1`, and a successful check of the selected observation
definition.

`construction-contract/v5` is a hard cut. v1-v4 artifacts and Evidence logs are
historical only. v5 uses:

```text
actuation-v5/{goal}/evidence.jsonl
```

Do not replay older event bodies under the v5 definition or reinterpret their
Construction bytes.

An unbound v5 log fails closed. Bind one exact valid history once:

```bash
ledger transact \
  --definition <actuating-root>/definitions/ledger/evidence-protocol.json \
  --operation bind-existing \
  --repo <repo> \
  --param goal=<goal-id> \
  --format json
```

## Clean committed subject

Evidence retains one clean committed Git target:

```text
subject_digest = sha256(
  "actuating-git-subject/v1" || 0x00 ||
  repository_id || 0x00 ||
  commit_oid || 0x00 ||
  tree_oid
)
```

Actuating derives it from the exact commit, tree, and clean worktree. Ledger
stores and compares the opaque digest.

A subject change invalidates subject-bound operation, proof, publication, and
review credit. It does not erase Goal, Construction, Counterexample, or first
review-entry lineage.

## Construction registration packet

Before mutation, materialize `construction-contract/v5` and every predecessor
`actuating-verifier-receipt/v1` wrapped by `actuating-construction-registration-receipt/v1` metadata. Register them together:

```yaml
schema: actuating-construction-registration/v2
goal_id:
construction_ref:
subject_digest:
body:
  schema: actuating-construction-registration-body/v2
  construction: {}
  receipts: []
```

The event body retains this exact registration packet. The retained
`construction` state stores only its `construction` member.

Each receipt is canonical JSON with a content-addressed `receipt_ref` and binds:

```text
Goal
claim
obligation
purpose
predecessor Construction; initial registration has no predecessor receipt packet
exact predecessor subject
step
exact verifier argv
exit status
output digests
```

The v5 construction registration independently recomputes each wrapper
`receipt_ref`; a copied or altered receipt is rejected.

Construction registration exact-matches:

- Goal, repository, scope, completion, and proof-kind coverage;
- predecessor Construction and factor inventory when one exists;
- complete accepted Counterexample coverage;
- every carrier claim's predecessor subject;
- every claim receipt ref, claim id, obligation, and purpose;
- receipt Goal, predecessor Construction, subject, and successful exit status;
- recurrence proof strength and concrete structural resolution;
- total semantic-element, carrier-claim, factor, realization, supersession, and
  retirement laws owned by the Construction definition.

The registration packet adds no event kind or authority artifact.

## Baseline and successor admission

When no current Construction exists, `predecessor_refs` and predecessor factors
are empty. Carrier claims bind the exact existing code subject with
`predecessor_construction_ref: null`, but the registration packet carries no
predecessor receipts. The initial Construction introduces the first complete
relation and earns closure only from current-subject successor evidence.

For a successor, every claim and receipt binds the one exact predecessor
Construction. `predecessor_factors` exact-match that Construction's successor
factors. Accepted-review successors also bind the exact current Counterexample
Set and unchanged review subject.

There is no branch on a repair mode. Admission examines only state topology and
the actual relation.

## Mutation gate

`prepare-operation` admits an edit only when:

```text
Goal allows mutation
normal_form.disposition == normal
no active Counterexample class is blocked
no carrier claim is unresolved
all accepted classes, laws, and implementation obligations are covered
paths and owner match the Construction
```

A mode, change-kind, or summary disposition cannot grant mutation.

The existing one-shot capability and clean-parent sequence remain:

```text
clean parent
-> prepare operation
-> provisional diff
-> Actuating inspects complete diff and exact paths
-> one-parent clean successor
-> record-effect
-> observe-edit-operation
```

## Successor evidence

Predecessor receipts justify selection. They do not prove realization.

After each verification operation, `operation_observed.evidence_refs` cites
canonical `actuating-verifier-receipt/v1` attachments bound to:

```text
current v5 Construction
exact successor subject
element carrier claim or retirement
successor-realization, successor-closure, or retirement purpose
exact verifier and result
```

Before Ship or fresh review, Actuating resolves all cited bytes and proves:

- every semantic element's selected factor and construction surface exists;
- every claimed closed owner excludes unchecked bypasses;
- every selected factor carries at least one semantic element;
- every proof obligation has current evidence;
- every retired factor is absent or lawfully successor-mapped;
- unmapped production and proof surfaces remain empty.

An event status string is not proof.

## Cumulative Counterexample source

`counterexample_set_registered` retains stable classes across Sets. The class
register, not the latest Set alone, supplies the complete current theory.

Before successor selection or Goal carry-forward, project:

```bash
ledger project \
  --definition <actuating-root>/definitions/ledger/evidence-protocol.json \
  --projection goal-carry-forward-context \
  --repo <repo> \
  --param goal=<goal-id> \
  --format json
```

Missing or incomplete projection data blocks. Do not reconstruct cumulative
classes from the latest review wave or raw JSONL.

## Review and publication evidence

The static Review Contract remains unchanged. Actuating validates the current
CAS capability, exact Goal/Construction/subject/publication tuple, five request
bindings, and instruction/lens digests before dispatch. CAS owns attempt
execution and receipts; Ledger records refs and order.

Every finding passes through `$review-fold`. Raw findings never authorize
mutation.

Ship owns publication and adoption receipts. `publication_observed` records
their content-addressed refs; Actuating resolves and exact-matches them. No
Construction or Ledger event may substitute for a Ship-owned public effect.
