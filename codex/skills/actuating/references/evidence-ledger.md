# Evidence Ledger Adapter

The Evidence Ledger is Actuating's append-only observation artifact. Ledger is
only its canonicalization, structural-validation, append, replay, and
projection adapter. Event bodies retain their domain owners.

## Current runtime gate

After `$ledger ensure` once for the workflow, require `ledger --version >=
0.11.7` and exactly these `ledger --source actuation --help` actions:

~~~text
append prepare state project doctor path
~~~

Reject missing or extra actions and retired `open`, `observe`, `close`, or
`decide`; apply the same gate to standalone Goal Contract or Review Fold handoff.

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
  "expected_subject_digest": "sha256:<64-lower-hex>",
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
ledger --source actuation --goal GOAL_ID prepare --input operation.json
ledger --source actuation --goal GOAL_ID append --input artifact-or-evidence.json
ledger --source actuation --goal GOAL_ID append --input effect-evidence.json --capability AKC2-...
ledger --source actuation --goal GOAL_ID state
ledger --source actuation --goal GOAL_ID project
ledger --source actuation --goal GOAL_ID doctor
ledger --source actuation --goal GOAL_ID path
~~~

Place optional `--repo PATH` before `--goal`. `prepare` validates the exact
current Goal, Construction, caller-owned `expected_subject_digest`, scope,
effect, and obligation references; appends `operation_prepared`; returns the raw
`AKC2-...` capability once; and persists only its digest. The durable event
envelope retains the expected subject. The capability is evidence-custody
binding, not mutation authority. `effect_recorded` consumes it for edits only
when `pre_effect_subject_digest` equals the current structural subject. A
successful `operation_observed` consumes it for inspect or verify against the
event envelope's current subject. Post-edit observation exact-matches the
recorded result subject. Missing, mismatched, reused, or unexpectedly supplied
capability material fails closed.

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

`operation_aborted` is the capabilityless recovery path: reject any raw
capability, exact-match the current tuple and pending `step_id`, require a
nonblank reason, then terminate the pending operation and invalidate its stored
capability digest. This permits recovery when `prepare` persisted admission but
its one-time raw output was lost, without adding another command or granting an
effect.

When the observed live subject has drifted, the current goal remains blocked;
`operation_aborted` does not pretend that an external change was an authorized
effect. Recovery requires fresh accepted authority compiled as a Goal successor
before a Construction may bind the new subject. No no-effect subject-refresh
event is inferred by Ledger.

`state` and `project` are discardable structural aids and must report
`authority_granted:false` and `semantic_decision_established:false`. Ledger
never executes work, dispatches or interprets reviews, computes credit,
interprets Ship, chooses a Construction or next action, or emits a semantic
closure decision or receipt.
