# Evidence Ledger Adapter

The Evidence Ledger is Actuating's append-only observation artifact. Ledger is
only its canonicalization, structural-validation, append, replay, and
projection adapter. Event bodies retain their domain owners.

## Current runtime gate

After `$ledger ensure` once for the workflow, require Ledger 1.x,
`ledger-artifact-abi/v1`, and a successful definition check for
`../definitions/ledger/evidence-protocol.json`. Require only the native Ledger
1.0 command surface; no source namespace, positional validator, alias, or
fallback is permitted. Apply the same gate to standalone Goal Contract or
Review Fold handoff.

When Actuating requests session evidence, require Seq 1.x,
`seq-observation-abi/v1`, and a successful check of the explicitly selected
Actuating observation definition. Ledger projects immutable structural facts;
Seq receives them only through an explicit input relation. Neither runtime
interprets the other's store or grants authority.

Construction v1 and v2 stores are unsupported and are not migrated. Start a
fresh goal-local v3 store and ignore legacy data.

An unbound current-format v3 Evidence log fails closed. Bind that exact history
once, outside ordinary reads and writes:

~~~bash
ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation bind-existing \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json
~~~

Supply no artifact input. Binding validates every existing row, event chain,
retained transition, and partition value under the selected definition digest;
it writes only Ledger-owned binding metadata and leaves `evidence.jsonl`
byte-identical. Any invalid row blocks.

Before review, require the current CAS runtime gate from `$cas`, including the
owner-lived workflow-bound review capability required by the static Review
Contract.

## Event envelope

Every durable row has exactly this `actuating-evidence-event/v1` envelope:

~~~json
{
  "schema": "actuating-evidence-event/v1",
  "sequence": 1,
  "previous_digest": "sha256:<64-lower-hex>",
  "event_id": "e-1",
  "goal_id": "<goal-id>",
  "construction_ref": "sha256:<64-lower-hex> or null",
  "subject_digest": "sha256:<64-lower-hex> or null",
  "kind": "<core-kind>",
  "recorded_at": 0,
  "body": {},
  "body_digest": "sha256:<64-lower-hex>",
  "event_digest": "sha256:<64-lower-hex>"
}
~~~

The core kinds are:

~~~text
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
~~~

Artifact-registration bodies are exact canonical artifacts.
`operation_prepared` records structural admission. Every other non-registration
body is owner evidence; Ledger validates only its declared structural contract.

## Committed subject

The Evidence `subject` register contains only a deterministic clean Git commit
target:

~~~text
subject_digest = sha256(
  "actuating-git-subject/v1" || 0x00 ||
  repository_id || 0x00 ||
  commit_oid || 0x00 ||
  tree_oid
)
~~~

Actuating derives the tuple with:

~~~bash
commit_oid="$(git rev-parse --verify 'HEAD^{commit}')"
tree_oid="$(git rev-parse --verify 'HEAD^{tree}')"
test -z "$(git status --porcelain=v2 --untracked-files=all --ignore-submodules=none)"
~~~

Then hash the exact NUL-framed bytes above with SHA-256 and prefix the lowercase
hexadecimal result with `sha256:`. Branch attachment is not part of semantic
identity. Ignored files are not part of the committed candidate. Ship binds the
publication refs and exact remote OIDs separately.

Ledger never invokes Git, decides cleanliness, derives this digest, or judges
whether the commit is the intended implementation. It compares only caller-
supplied digests under the Evidence transition law.

## Transient inputs

`prepare-operation` accepts exactly:

~~~json
{
  "schema": "actuating-operation-request/v1",
  "goal_id": "<goal-id>",
  "construction_ref": "sha256:<64-lower-hex>",
  "subject_digest": "sha256:<64-lower-hex>",
  "body": {
    "schema": "actuating-operation/v1",
    "goal_id": "<goal-id>",
    "construction_ref": "sha256:<64-lower-hex>",
    "expected_subject_digest": "sha256:<64-lower-hex>",
    "step_id": "<step-id>",
    "effect": "inspect|edit|verify",
    "idempotency_key": "<unique-key>",
    "owner_boundary": "<owner>",
    "paths": ["<literal-repository-path>"],
    "proof_obligation_refs": ["<obligation-id>"]
  }
}
~~~

Evidence operations accept exactly:

~~~json
{
  "schema": "actuating-evidence-input/v1",
  "goal_id": "<goal-id>",
  "construction_ref": "sha256:<64-lower-hex> or null",
  "subject_digest": "sha256:<64-lower-hex> or null",
  "kind": "<owner-appendable-core-kind>",
  "body": {}
}
~~~

Unknown or missing keys fail closed. Supplying an input asserts only that its
named owner made the observation; it grants no authority.

`proof_obligation_refs` contains exactly one locally executable role: an
implementation or acceptance `obligation_id` selects its verifier,
`obligation_id#falsifier` selects its independent falsifier, and a
`retirement_id` selects its retirement verifier. Review and Ship obligations
remain external-owner evidence and cannot be prepared as repository work.

Use this complete owner-appendable body table. `digest` means `sha256:` plus 64
lowercase hexadecimal digits; `string` means nonblank UTF-8; arrays are
duplicate-free.

| `kind` | Exact `body` |
|---|---|
| `effect_recorded` | `{schema:"effect-recorded/v1", step_id:string, pre_effect_subject_digest:digest, changed_paths:[string]}` |
| `operation_observed` | `{schema:"operation-observed/v1", step_id:string, status:string, discharged_refs:[string], evidence_refs:[digest]}` |
| `operation_aborted` | `{schema:"operation-aborted/v1", step_id:string, reason:string}` |
| `publication_observed` | `{schema:"publication-observed/v1", status:string, receipt_ref:digest}` |
| `review_campaign_started` | `{schema:"review-campaign-started/v1", campaign_id:digest, review_contract_digest:digest}` |
| `review_request_bound` | `{schema:"review-request-bound/v1", campaign_id:digest, request_id:string, instruction_digest:digest, lens_contract_digest:digest, lens:string, initial_wave:boolean}` |
| `review_attempt_started` | `{schema:"review-attempt-started/v1", request_id:string, attempt_id:string, fresh_attempt:boolean, receipt_ref:digest}` |
| `review_attempt_completed` | `{schema:"review-attempt-completed/v1", request_id:string, attempt_id:string, principal:string, verdict:string, context_match:boolean, fallback:boolean, finding_refs:[digest], receipt_ref:digest}` |
| `review_transport_failed` | `{schema:"review-transport-failed/v1", request_id:string, attempt_id:string, failure_ref:digest, receipt_ref:digest}` |

## Edit evidence law

An edit operation starts from the exact clean committed subject retained by
Evidence. Dirty implementation state is never appended.

The owner sequence is:

~~~text
prepare-operation on clean parent
-> create one provisional diff
-> inspect complete diff and exact changed paths
-> commit exactly the selected operation
-> require clean one-parent successor
-> derive successor subject
-> record-effect with parent and successor digests
-> observe-edit-operation with proof evidence
~~~

Before `prepare-operation`, Actuating requires:

- an empty porcelain-v2 status including untracked files and submodule dirt;
- the current commit and tree to derive the retained subject;
- no unrelated provisional changes;
- the operation paths to be within Construction scope and disjoint from Goal
  prohibitions.

`one-seam-operator` creates the provisional diff but never stages, commits,
amends, pushes, or publishes. Actuating re-inspects the complete diff, stages
only the selected operation, and creates the successor commit.

Before `record-effect`, Actuating requires:

- successor `HEAD^` equals the prepared parent commit;
- the successor checkout is clean;
- the commit path set is nonempty and exactly equals `pending.paths`;
- every path remains inside Construction scope and outside Goal prohibitions;
- the successor subject differs from the parent subject;
- `effect_recorded.pre_effect_subject_digest` equals the parent subject;
- the event envelope's `subject_digest` equals the successor subject.

`record-effect` consumes the one-shot capability, records the exact path set,
and advances the Evidence subject directly from the parent commit target to the
successor commit target. There is no dirty-state subject, no commit-equivalence
observer, and no separate commit-rebinding event.

`observe-edit-operation` then requires the previously consumed operation and
current successor subject. It records verifier, falsifier, or retirement
results for that exact committed target and clears the pending operation.

If the provisional diff is abandoned before commit, or the parent target is no
longer current, use `operation_aborted`; it consumes no raw capability and
clears the pending operation. After a successor commit exists, abort is
inadmissible: Actuating must either record the lawful effect or report the exact
commit/scope obstruction and stop rather than hiding a repository mutation.

## Inspect and verify evidence law

Inspect and verify operations run only on the exact clean committed subject.
`observe-readonly-operation` consumes the one-shot capability when:

- the pre-operation commit, tree, and subject match the current Evidence
  subject;
- the exact selected argv ran;
- the checkout remains clean afterward;
- the commit, tree, and subject remain unchanged;
- the cited evidence bytes are retained and content-addressed.

A verifier that changes correctness-bearing repository state has not proved the
prepared subject. Its result is discarded; Actuating must select an edit,
commit the generated change, and rerun proof on the new clean target.

## Verifier evidence

An executor makes verifier provenance replayable with this immutable supporting
attachment; it is evidence, not another authoritative artifact family:

~~~yaml
verifier_receipt:
  schema: actuating-verifier-receipt/v1
  step_id:
  goal_contract_ref:
  construction_ref:
  subject_digest:
  verifier:
    argv: []
  exit_status:
  output_digests: []
~~~

`evidence_refs` contains the SHA-256 digest of the canonical JSON receipt and
every cited immutable output. Before discharging an obligation, Actuating
resolves the exact bytes, recomputes every digest, requires `verifier.argv` to
equal the current Construction obligation, exact-matches Goal, Construction,
step, and committed subject, and evaluates exit status and outputs. Missing or
unresolvable bytes block proof; an event's `status` string cannot substitute for
them. Attachment location is transport metadata and never participates in
identity. Ledger neither ingests nor owns CAS, Ship, or verifier attachments.

## Commands and capability law

~~~bash
ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation prepare-operation \
  --repo REPO \
  --input operation=operation.json \
  --param goal=GOAL_ID \
  --format json

ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation record-effect \
  --repo REPO \
  --input evidence=effect-evidence.json \
  --param goal=GOAL_ID \
  --param capability=AKC2-... \
  --format json

ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation observe-readonly-operation \
  --repo REPO \
  --input evidence=observation.json \
  --param goal=GOAL_ID \
  --param capability=AKC2-... \
  --format json

ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation observe-edit-operation \
  --repo REPO \
  --input evidence=observation.json \
  --param goal=GOAL_ID \
  --format json

ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation abort-operation \
  --repo REPO \
  --input evidence=aborted.json \
  --param goal=GOAL_ID \
  --format json

ledger project \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --projection structural-facts \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json

ledger project \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --projection goal-carry-forward-context \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json

ledger doctor \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json
~~~

`prepare-operation` validates the current Goal, Construction, caller-owned
`expected_subject_digest`, scope, effect, and obligation reference; appends
`operation_prepared`; returns the raw `AKC2-...` token once; and persists only
its digest. The capability is evidence-custody binding, not mutation authority.

`record-effect` consumes it for edits only when the body parent digest equals
the current structural subject and the changed path set exactly equals the
pending path set. It advances the structural subject to the event envelope's
successor digest. `observe-readonly-operation` consumes it for inspect or
verify. `observe-edit-operation` requires prior effect consumption and rejects
a second raw capability. Missing, mismatched, reused, or unexpectedly supplied
capability material fails closed.

## Structural projections

For deterministic Ledger-to-Seq transport:

~~~bash
ledger project \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --projection structural-facts \
  --repo REPO \
  --param goal=GOAL_ID \
  --payload-only \
  --format json > structural-facts.json

seq observe \
  --definition <actuating-skill-root>/definitions/seq/artifact-kernel.json \
  --input facts=structural-facts.json \
  --projection structural-facts \
  --format json
~~~

The payload is `actuating-structural-facts/v1`: one bounded relation row with
structural identities, counts, event-kind counts, pending operation, and exact
Evidence head. Seq verifies the input schema and emits
`actuating-artifact-kernel-observation/v1`; Actuating interprets the facts.

For a Goal carry-forward or successor Construction, use
`goal-carry-forward-context`. Its payload exports the exact retained Goal,
active Construction and ref, committed subject, Counterexamples, full class
register, carry-forward marker, lineage Construction, and pending operation. It
is the sanctioned source for current Goal, Construction, and active Set refs.
Derive supporting references exactly from classes whose status is `accepted`,
`blocked`, or `follow-up`; never guess, reconstruct an older Goal, or read the
event log directly. An unavailable or incomplete projection is a fail-closed
owner obstruction.

Observe physical run evidence independently:

~~~bash
seq observe \
  --definition <actuating-skill-root>/definitions/seq/run-audit.json \
  --session-id SESSION_ID \
  --projection turn-metadata \
  --format json
~~~

Use `tool-metadata` for tool lifecycle structure and opt into raw turns or tools
only when the evidence question requires them. Seq returns evidence and
provenance only.

## Review evidence

Every `review_attempt_started.receipt_ref` is the digest of an exact CAS start
receipt. Actuating evaluates whether five distinct current start receipts
satisfy the initial barrier. Each `finding_refs` entry is the digest of exact
canonical CAS finding-row bytes; row IDs and best-effort fingerprints remain
provenance rather than Counterexample identity.

Before assigning review meaning, Actuating dereferences each CAS receipt,
verifies its digest, request fingerprint, attempt identity, instructions,
principal, and exact Ship-confirmed base/head/target tuple, then derives verdict
and quality. Convenience fields in Evidence never earn credit by themselves.
A mismatch blocks the attempt.

The review campaign is bound to the current committed subject and static Review
Contract, while CAS additionally proves the exact published `baseSha` and
`headSha`. Normally Ship first proves that the local clean verified commit is
the remote PR head. When an already-public subject is adopted after review,
Ship must instead prove that the provider-authored publication event for the
exact repository, canonical head ref, and base/head tuple preceded the credited
campaign; tuple equality or an arbitrary older matching event earns no
retrospective credit. A local dirty change after publication
does not alter the remote review target; it merely blocks another Actuating
operation or publication until resolved into a clean selected commit.

`review_campaign_started` is a one-shot transition for the current Goal,
Construction, subject, and Review Contract. The reducer stores its deterministic
campaign id, rejects another start while that tuple remains current, and
requires every `review_request_bound.campaign_id` to equal the stored id. A
material subject, Construction, or Goal transition clears the register. Thus a
campaign id names one admitted occurrence rather than aliasing several events.

The `structural-facts` projection is a discardable structural aid. Its envelope
reports `authority_granted:false` and `storage_mutated:false`. Ledger never
executes work, dispatches or interprets reviews, computes credit, interprets
Ship, chooses a Construction or next action, or emits semantic closure.

The read-only `publication-review-events` projection returns the goal's raw
`publication_observed` and `review_campaign_started` rows in canonical Ledger
order:

~~~bash
ledger project \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --projection publication-review-events \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json
~~~

Ledger only filters and preserves event order. Actuating dereferences the Ship
and supporting causal-order attachments and decides whether one publication
precedes one exact campaign.

For a historical campaign, the supporting attachment has this exact semantic
schema and owner:

~~~yaml
schema: actuating-publication-campaign-causality/v1
owner: actuating
seq:
  definition_id: actuating/run-audit
  definition_digest: sha256-digest
  observation_digest: sha256-digest
  corpus_digest: sha256-digest
  session_id: string
publication:
  call_id: string
  lifecycle_status: completed
  exit_code: 0
  finalized_line: positive-integer
  provider_event_ref: sha256-digest
campaign:
  call_id: string
  lifecycle_status: completed
  exit_code: 0
  declared_line: positive-integer
  campaign_id: sha256-digest
  campaign_event_digest: sha256-digest
relation: publication-finalized-before-campaign-declared
~~~

Actuating recomputes the attachment digest, dereferences the exact Seq
observation and `publication-review-events` campaign row, exact-matches both
call lifecycles and event digests, and requires
`publication.finalized_line < campaign.declared_line` in the same corpus and
session. Seq supplies physical source evidence only; Actuating owns the
relation's meaning. Independent wall clocks, endpoint equality, an arbitrary
provider event, or an unverified digest earn no credit.
