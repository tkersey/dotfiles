# Evidence Ledger Adapter

The Evidence Ledger is Actuating's append-only observation artifact. Ledger is
only its canonicalization, structural-validation, append, replay, and
projection adapter. Event bodies retain their domain owners.

## Current runtime gate

After completing `$ledger ensure` once for the workflow, require
`ledger --version >= 0.11.0`. Inspect `ledger --source actuation --help` and
require exactly these actions:

~~~text
append prepare state project doctor path
~~~

Reject the route when any action is missing, any other actuation action is
advertised, or a retired `open`, `observe`, `close`, or `decide` action remains.
The same gate is required when a standalone Goal Contract or Review Fold
handoff enters Actuating.

Before review dispatch, require `cas --version >= 0.2.83` and inspect
`cas review --help`. Its action set must be exactly `run`, `start`, and `wait`;
the `review_session` and `review-session` aliases and every retired review
action must be absent. Compare semantic versions numerically, never
lexicographically.

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

`prepare` accepts exactly:

~~~json
{
  "schema": "actuating-operation/v1",
  "goal_id": "<goal-id>",
  "construction_ref": "sha256:<64-lower-hex>",
  "step_id": "<step-id>",
  "effect": "inspect|edit|verify",
  "idempotency_key": "<unique-key>",
  "owner_boundary": "<owner>",
  "paths": ["<literal-repository-path>"],
  "proof_obligation_refs": ["<obligation-id>"]
}
~~~

`append` accepts an artifact or exactly this owner-observation envelope:

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

Use this complete owner-appendable body table. Braces name the exact key set;
`digest` means `sha256:` plus 64 lowercase hexadecimal digits, `string` means
nonblank UTF-8, and brackets mean a duplicate-free string array.

| `kind` | Exact `body` |
|---|---|
| `effect_recorded` | `{schema:"effect-recorded/v1", step_id:string, changed_paths:[string]}` |
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
identity.

## Commands and capability law

~~~bash
ledger --source actuation --goal GOAL_ID prepare --input operation.json
ledger --source actuation --goal GOAL_ID append --input artifact-or-evidence.json
ledger --source actuation --goal GOAL_ID append --input effect-evidence.json --capability AKC2-...
ledger --source actuation --goal GOAL_ID state
ledger --source actuation --goal GOAL_ID project
ledger --source actuation --goal GOAL_ID doctor
ledger --source actuation --goal GOAL_ID path
~~~

Place optional `--repo PATH` before `--goal`. `prepare` validates the exact
current Goal, Construction, scope, effect, and obligation references; appends
`operation_prepared`; returns the raw `AKC2-...` capability once; and persists
only its digest. The capability is evidence-custody binding, not mutation
authority. `effect_recorded` consumes it for edits; a successful
`operation_observed` consumes it for inspect or verify. Missing, mismatched,
reused, or unexpectedly supplied capability material fails closed.

`operation_aborted` is the capabilityless recovery path: reject any raw
capability, exact-match the current tuple and pending `step_id`, require a
nonblank reason, then terminate the pending operation and invalidate its stored
capability digest. This permits recovery when `prepare` persisted admission but
its one-time raw output was lost, without adding another command or granting an
effect.

`state` and `project` are discardable structural aids and must report
`authority_granted:false` and `semantic_decision_established:false`. Ledger
never executes work, dispatches or interprets reviews, computes credit,
interprets Ship, chooses a Construction or next action, or emits a semantic
closure decision or receipt.
