# Evidence Ledger Adapter

The Evidence Ledger is Actuating's append-only observation artifact. Ledger
canonicalizes, structurally validates, appends, replays, and projects. Event
bodies retain their domain owners. Ledger never interprets review or Ship,
derives causal generators, selects a Construction, grants mutation, or closes.

The passive definitions under `../definitions/ledger/` are normative for exact
JSON shape. This reference states their ownership and sequencing law without
duplicating every schema field.

## Runtime and version gate

After `$ledger ensure` once for the workflow, require Ledger 1.x,
`ledger-artifact-abi/v1`, and successful checks for the selected Actuating
Ledger definitions. When session evidence is needed, require Seq 1.x,
`seq-observation-abi/v1`, and a successful check of the selected observation
definition.

`construction-contract/v4` is a hard cutover for new selection or mutation.
Construction v1-v3 artifacts may remain historical evidence but cannot authorize
an affected operation. Do not reinterpret old bytes as v4. When the current
passive definition cannot replay a mixed history without weakening validation,
start a fresh goal-local v4 Evidence store and cite the predecessor artifacts as
supporting evidence.

An unbound current-format Evidence log fails closed. Bind an exact valid history
once outside ordinary reads and writes:

```bash
ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation bind-existing \
  --repo <repo> \
  --param goal=<goal-id> \
  --format json
```

Binding validates existing rows and chain integrity and writes only
Ledger-owned binding metadata. Any invalid row blocks.

## Event envelope and kinds

Every durable row is `actuating-evidence-event/v1` with exact sequence,
previous digest, event id, goal id, Construction ref, subject digest, kind,
recording time, body, body digest, and event digest.

The core kinds remain:

```text
goal_contract_registered
goal_contract_carry_forward_registered
counterexample_set_registered
construction_contract_registered
operation_prepared
effect_recorded
operation_observed
operation_aborted
publication_observed
review_campaign_started
review_request_bound
review_attempt_started
review_attempt_completed
review_transport_failed
```

This redesign adds no event kind. Goal, Counterexample, and Construction
registration bodies are exact canonical artifacts. `operation_prepared` records
structural admission. Other bodies are owner evidence; structural admission is
not semantic truth.

## Clean committed subject

Evidence retains only one clean committed Git target:

```text
subject_digest = sha256(
  "actuating-git-subject/v1" || 0x00 ||
  repository_id || 0x00 ||
  commit_oid || 0x00 ||
  tree_oid
)
```

Actuating derives the tuple from `HEAD^{commit}`, `HEAD^{tree}`, and an empty
porcelain-v2 status including untracked files and submodule dirt. Branch
attachment and ignored files are excluded. Ledger stores and compares the opaque
digest; it never invokes Git or decides cleanliness.

A subject change invalidates subject-bound operation, proof, publication, and
review credit. It does not erase Goal, Construction, Counterexample, causal, or
first-review-entry lineage.

## Cumulative Counterexample source

`counterexample_set_registered` upserts stable classes across Sets. The class
register—not the latest Set alone—is the structural source for the complete
applicable Counterexample Theory.

Before successor selection or Goal carry-forward, project:

```bash
ledger project \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --projection goal-carry-forward-context \
  --repo <repo> \
  --param goal=<goal-id> \
  --format json
```

The projection returns the exact retained Goal, active and lineage
Constructions, committed subject, current Set, full stable-class register,
carry-forward marker, and pending operation. Actuating derives the complete
applicable accepted class set and supporting Set refs from this projection.
Ledger does not quotient classes into causal generators or decide applicability.

Missing or incomplete projection data blocks. Never reconstruct cumulative
classes from the latest review wave, guess references, or read raw JSONL as a
substitute.

## Construction registration

Before mutation, Actuating materializes `construction-contract/v4` through
`construction-contract.json` and registers the returned canonical artifact
through `register-construction`.

The Evidence protocol structurally enforces current Goal, subject, predecessor,
Counterexample coverage, proof-family strength for recurrent/high-severity
classes, scope, and completion. The Construction definition additionally owns
causal-basis coverage, semantic-model closure, candidate normality, realization
bindings, factor supersession, and empty unmapped surfaces.

Only the canonical materialization plus appended registration event makes a
Construction current. A document, validator pass, or review finding alone grants
no mutation.

## Operation and capability law

`prepare-operation` accepts one exact `actuating-operation-request/v1` binding
Goal, Construction, expected clean subject, unique step and idempotency keys,
effect, owner, literal paths, and exactly one executable proof or retirement
reference.

```bash
ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation prepare-operation \
  --repo <repo> \
  --input operation=<operation.json> \
  --param goal=<goal-id> \
  --format json
```

Ledger returns a one-shot `AKC2-...` capability and retains only its digest. The
capability binds evidence custody; it does not itself authorize mutation.

For an edit, the owner sequence is:

```text
clean parent
-> prepare one operation
-> one-seam-operator creates one provisional diff
-> Actuating inspects complete diff and exact paths
-> commit exactly the operation
-> require one-parent clean successor
-> derive successor subject
-> record-effect parent -> successor
-> observe-edit-operation with proof evidence
```

`record-effect` requires the parent digest and changed-path set to exact-match
the pending operation, consumes the capability, and advances directly to the
clean committed successor. `observe-edit-operation` then records verifier,
falsifier, or retirement evidence and clears the operation. There is no dirty
subject or commit-rebinding event.

Inspect and verify operations run on the exact clean subject and use
`observe-readonly-operation`; the commit, tree, and subject must remain
unchanged. A correctness-bearing generated change requires a separately
selected edit and fresh proof.

Before a successor commit, abandon a provisional operation with
`operation_aborted`. After a successor commit exists, abort cannot hide it:
record the lawful effect or report the exact obstruction and stop.

Every cited verifier attachment is content-addressed and binds step, Goal,
Construction, subject, exact argv, exit status, and output digests. Actuating
resolves and evaluates those bytes. An event status string is not proof.

## Structural projections

The `structural-facts` projection returns one bounded row containing current
Goal and Construction refs, subject, Evidence head, event counts, stable-class
count, and pending operation. Seq may consume that row through
`definitions/seq/artifact-kernel.json`; neither runtime adds semantic meaning.

```bash
ledger project \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --projection structural-facts \
  --repo <repo> \
  --param goal=<goal-id> \
  --payload-only \
  --format json > structural-facts.json

seq observe \
  --definition <actuating-skill-root>/definitions/seq/artifact-kernel.json \
  --input facts=structural-facts.json \
  --projection structural-facts \
  --format json
```

## Review evidence

Before dispatch, Actuating validates the static Review Contract, current CAS
preflight/capabilities, exact current Goal/Construction/subject/publication
tuple, five request bindings, and instruction/lens digests. A noncanonical
closure-grade binding is rejected before its findings can authorize mutation.

CAS owns attempt execution and receipts. Actuating dereferences each receipt and
checks request, attempt, instructions, principal, backend, workflow binding,
base/head/target tuple, and structured verdict before granting credit. Ledger
records receipt references and canonical event order only.

Every finding passes through `$review-fold`. A canonical Counterexample Set may
join the cumulative class register; raw findings do not. Duplicate witnesses,
review attempts, and campaigns remain provenance rather than class identity.

The one-shot `review_campaign_started` identity binds Goal, Construction,
subject, and Review Contract. A material Goal, Construction, or subject change
clears the current campaign and all semantic review credit. The static
concurrent 1+4 topology, request-local recovery, and five-consecutive-standard-
clean theorem remain Actuating policy, not Ledger state-machine interpretation.

## Publication evidence

Ship owns publication and adoption receipts. `publication_observed` records a
content-addressed receipt reference; Actuating resolves and exact-matches the
repository, refs/OIDs, subject, Goal, Construction, and actuation binding.

For a new campaign, `SHIP-OBSERVATION-v1` recorded before campaign binding may
later be ratified by `SHIP-ADOPTION-v1`. For a historical campaign predating
that route, require exact provider evidence and an
`actuating-publication-campaign-causality/v1` attachment proving publication
completed before campaign declaration by one Seq source-order observation.
Endpoint equality or unrelated wall clocks are insufficient.

`publication-review-events` filters the raw publication and campaign rows in
canonical Ledger order. Ledger does not decide their causal meaning.
