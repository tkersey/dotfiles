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

When Actuating requests a session observation, require Seq 1.x,
`seq-observation-abi/v1`, and a successful check of the explicitly selected
Actuating observation definition. Ledger projects immutable structural facts;
Seq receives them only through an explicit `--input` relation. Neither runtime
interprets the other's store or grants authority.

Construction v1 and v2 stores are unsupported and are not migrated. Start a
fresh goal-local store and ignore the legacy data.

An unbound current-format v3 Evidence log also fails closed. Bind that exact
history once, outside normal reads and writes:

~~~bash
ledger transact \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --operation bind-existing \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json
~~~

Supply no artifact input. The operation validates every existing row, event
chain, retained transition, and partition value under the selected definition
digest; writes only Ledger-owned binding metadata; and leaves
`evidence.jsonl` byte-identical. Any invalid row blocks the binding.

Before review, require `cas --version >= 0.2.83` and exactly `run`, `start`, and
`wait` in `cas review --help`, with no retired action or `review_session` or
`review-session` alias. Compare semantic versions numerically.

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

Artifact-registration bodies are the exact canonical artifact. Adapter-owned
`operation_prepared` records admission. Every other non-registration body is
owner evidence; Ledger validates only its declared structural contract.

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

Evidence operations accept exactly this owner-observation envelope:

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

Unknown or missing keys fail closed. The `body` must exactly match the selected
kind's schema. Supplying this input asserts only that its named owner made the
observation; it grants no authority.

`proof_obligation_refs` contains exactly one locally executable role: an
implementation or acceptance `obligation_id` selects its verifier,
`obligation_id#falsifier` selects its independent falsifier, and a
`retirement_id` selects the retirement verifier. Review and Ship obligations
remain external-owner evidence and cannot be prepared as repository work.

Use this complete owner-appendable body table. Braces name the exact key set;
`digest` means `sha256:` plus 64 lowercase hexadecimal digits, `string` means
nonblank UTF-8, and brackets mean a duplicate-free string array.

| `kind` | Exact `body` |
|---|---|
| `effect_recorded` | `{schema:"effect-recorded/v1", step_id:string, pre_effect_subject_digest:digest, changed_paths:[string]}` |
| `subject_commit_observed` | `{schema:"actuating-subject-commit-observation/v1", repository_id:string, repository_root_digest:digest, head_ref:string, scope:{allowed_paths:[string], prohibited_paths:[string]}, before:{subject_digest:digest, head:string, scoped_worktree_digest:digest}, after:{subject_digest:digest, head:string, parent:string, scoped_worktree_digest:digest}, changed_paths:[string], clean_successor:boolean}` |
| `operation_observed` | `{schema:"operation-observed/v1", step_id:string, status:string, discharged_refs:[string], evidence_refs:[digest]}` |
| `operation_aborted` | `{schema:"operation-aborted/v1", step_id:string, reason:string}` |
| `publication_observed` | `{schema:"publication-observed/v1", status:string, receipt_ref:digest}` |
| `review_campaign_started` | `{schema:"review-campaign-started/v1", campaign_id:digest, review_contract_digest:digest}` |
| `review_request_bound` | `{schema:"review-request-bound/v1", campaign_id:digest, request_id:string, instruction_digest:digest, lens_contract_digest:digest, lens:string, initial_wave:boolean}` |
| `review_attempt_started` | `{schema:"review-attempt-started/v1", request_id:string, attempt_id:string, fresh_attempt:boolean, receipt_ref:digest}` |
| `review_attempt_completed` | `{schema:"review-attempt-completed/v1", request_id:string, attempt_id:string, principal:string, verdict:string, context_match:boolean, fallback:boolean, finding_refs:[digest], receipt_ref:digest}` |
| `review_transport_failed` | `{schema:"review-transport-failed/v1", request_id:string, attempt_id:string, failure_ref:digest, receipt_ref:digest}` |

Ledger validates the `review_attempt_started.receipt_ref` only as the digest of
the exact CAS start receipt. Actuating evaluates whether five distinct,
current start receipts satisfy the initial-wave barrier. Every `finding_refs`
entry on `review_attempt_completed` is the digest of the exact canonical CAS
finding-row bytes; row IDs and best-effort fingerprints remain provenance
rather than Counterexample identity. Counterexample `follow-up` classes remain
recorded and routed but do not block the current Goal; only applicable accepted
debt and blockers constrain current mutation or closure.

Before assigning semantic review meaning, Actuating must dereference each CAS
`receipt_ref`, verify its content digest, exact request fingerprint, current
tuple, attempt identity, and owner fields, and derive the verdict and quality
predicate from that receipt. The convenience fields in an Evidence event never
earn credit by themselves; a mismatch with the cited CAS receipt blocks the
attempt. Likewise, proof discharge requires Actuating to dereference every
`evidence_ref` and verify that it is output from the exact verifier selected by
the current Construction. Ledger checks only digest shape and prepared
obligation membership.

An executor makes verifier provenance replayable with this immutable supporting
attachment; it is evidence, not a fifth authoritative artifact family:

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
the digest of every cited immutable output. Before discharging an obligation,
Actuating resolves those exact bytes, recomputes every digest, requires the
receipt's `verifier.argv` to equal the current Construction obligation, requires
its tuple and `step_id` to match the prepared operation and live subject, and
evaluates `exit_status` plus the referenced outputs. Missing or unresolvable
attachment bytes block proof; an event's `status` string cannot substitute for
them. Attachment location is transport metadata and never participates in
identity. The source owner must retain those immutable bytes in its existing
durable evidence route before Actuating cites them. Ledger neither ingests nor
owns CAS, Ship, or verifier attachments; adding a second Ledger attachment
store would duplicate their custody boundary.

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

ledger project \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --projection goal-carry-forward-context \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json

ledger project \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --projection structural-facts \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json

ledger doctor \
  --definition <actuating-skill-root>/definitions/ledger/evidence-protocol.json \
  --repo REPO \
  --param goal=GOAL_ID \
  --format json
~~~

For deterministic Ledger-to-Seq transport, emit the definition-declared
relation directly and observe it through the Actuating artifact kernel:

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

The payload is `actuating-structural-facts/v1`: one bounded relation row
containing structural identities, counts, event-kind counts, the current
pending-operation value, and the exact Evidence head. Seq verifies the input
schema and emits `actuating-artifact-kernel-observation/v1`; Actuating alone
interprets those facts.

For a Goal carry-forward, use `goal-carry-forward-context` instead. Its payload
is `actuating-goal-carry-forward-context/v1` and exports the exact retained
`goal`, `construction_ref`, `subject_digest`, `counterexamples`, full
`counterexample_classes`, `carry_forward`, `lineage_construction`, and
`pending_operation` values. It is the sanctioned source for the current Goal
artifact and the active Counterexample Set references. From a payload-only
projection, derive those references exactly with:

~~~bash
jaq '[.counterexample_classes[]
      | select(.value.status == "accepted"
            or .value.status == "blocked"
            or .value.status == "follow-up")
      | "counterexample-set:\(.source)"]
     | unique | sort' goal-carry-forward-context.json
~~~

Do not guess supporting references, reconstruct the current Goal from an older
artifact, or read the event log directly. An unavailable, invalid, or
incomplete context projection is a fail-closed owner-side obstruction, not
permission to retry registration. Like every Ledger projection, this view is
discardable and grants no semantic, execution, mutation, review, or closure
authority.

Observe physical run evidence independently, selecting an exact session or a
bounded repository/time window:

~~~bash
seq observe \
  --definition <actuating-skill-root>/definitions/seq/run-audit.json \
  --session-id SESSION_ID \
  --projection turn-metadata \
  --format json
~~~

Use `tool-metadata` for tool lifecycle structure. Opt into `turns` or `tools`
only when the evidence question requires raw message, command, or output text.
The definition returns evidence and provenance only; it does not recreate the
retired native verdict or transfer Actuating authority into Seq.

`prepare-operation` validates the exact current Goal, Construction,
caller-owned `expected_subject_digest`, scope, effect, and obligation
references; appends `operation_prepared`; returns the raw `AKC2-...` token once
as `generated_outputs.capability`; and persists only its digest. The durable
event envelope retains the expected subject. The capability is
evidence-custody binding, not mutation authority. `record-effect` consumes it
for edits only when `pre_effect_subject_digest` equals the current structural
subject. `observe-readonly-operation` consumes it for inspect or verify.
`observe-edit-operation` requires the prior effect consumption and rejects a
second raw capability. Post-edit observation exact-matches the recorded result
subject. Missing, mismatched, reused, or unexpectedly supplied capability
material fails closed.

Immediately before an edit, inspection, or verifier, Actuating requires the
executor to recompute the live subject with the exact repository-native
procedure Actuating supplied for that operation and exact-match
`expected_subject_digest`. A
mismatch takes `operation_aborted` without performing the effect. The executor
then echoes the subject it actually observed in the applicable owner event.
Ledger compares opaque digests only: it never invokes Git, derives repository
identity, or decides whether the subject procedure is semantically adequate.

~~~bash
uv run --no-project python <loaded-actuating-skill-root>/scripts/subject_observation.py \
  --repo REPO --repository-id ID --allow PATH [--allow PATH ...] [--prohibit PATH ...]
~~~

Resolve `<loaded-actuating-skill-root>` to the absolute directory containing
the active `SKILL.md`, never the target repo. `--no-project` prevents pre-check
environment or lockfile effects.

`actuating-subject-observation/v1` binds repository id and canonical-root digest, commit and symbolic HEAD, structural scope roots, sorted index, worktree state,
recursive gitlinks, deletions, and selected ignored or unignored files; unborn
HEAD is `unborn:<symbolic-ref>`. It excludes `.git`, `.ledger`, prohibited, and
out-of-scope paths; control-root, noncanonical, symlinked, hard-linked,
index-flagged, platform-ambiguous, or unequal captures fail closed.

After a completed edit is committed without further semantic change, prove the
provenance transition with:

~~~bash
uv run --no-project python <loaded-actuating-skill-root>/scripts/subject_commit_observation.py \
  --repo REPO --before PRE_COMMIT_SUBJECT_OBSERVATION
~~~

The observer validates the prior observation's content digest, double-captures
the successor, and requires the same repository root, repository identity,
symbolic ref, and scope; exactly one parent equal to the prior HEAD; identical
scoped worktree meaning before and after the commit; nonempty commit paths all
inside the scope; and a clean scoped successor. Pass its exact output as the
`body` of `subject_commit_observed` to `record-subject-commit`, with the outer
subject equal to `after.subject_digest`. The reducer additionally binds the
repository and exact scope to the current Goal and advances only `subject`.
This is not a no-effect refresh and cannot represent semantic source drift.

Before an effect, `operation_aborted` is the capabilityless recovery path:
reject any raw capability, exact-match the current tuple and pending `step_id`,
require a nonblank reason, then terminate the pending operation and invalidate
its stored capability digest. This permits recovery when `prepare-operation`
persisted admission but its one-time raw output was lost, without adding
another command or granting an effect. After `record-effect`, abort is
inadmissible: the owner must record `operation_observed` so the changed subject
and proof disposition remain explicit.

When the observed live subject has drifted, the current goal remains blocked;
`operation_aborted` does not pretend that an external change was an authorized
effect. A direct clean commit proved by the typed subject-commit observation is
the sole provenance-only exception. Every other drift requires fresh accepted
authority compiled as a Goal successor before a Construction may bind the new
subject. No generic no-effect subject-refresh event is inferred by Ledger.

The `structural-facts` projection is a discardable structural aid. The generic
projection envelope must report `authority_granted:false` and
`storage_mutated:false`; its store metadata carries the former path/revision
observation. Ledger never executes work, dispatches or interprets reviews,
computes credit, interprets Ship, chooses a Construction or next action, or
emits a semantic closure decision or receipt.
