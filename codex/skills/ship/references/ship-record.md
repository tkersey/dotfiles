# Ship Record

~~~yaml
ship_record:
  record_version: SHIP-v1
  source: direct | actuation
  repository:
  branch:
  base_branch:
  base_sha:
  head_sha:
  existing_pr:
    exists:
    url:
    draft:
  validation:
    build:
    lint:
    tests:
    language_specific:
    acceptance:
  pr_readiness:
    mode: ready | draft | update-existing | promote-draft | blocked
    reason:
    draft_allowed_reason:
  action:
    command:
    result:
    pr_url:
  actuation_binding:
    closure_receipt_ref:
    goal_contract_ref:
    construction_ref:
    subject_digest:
    evidence_head:
    review_contract_digest:
~~~

`pr_readiness.mode` reports the selected publication posture. The controlling
decision keeps operation and final state separate:

~~~yaml
pr_decision:
  operation: create | update | update-and-promote | blocked
  final_state: ready | draft | preserve
~~~

`action.result` is successful only after live PR readback matches repository,
base and head identities, URL, open/draft state, and managed proof block.

`actuation_binding` is required when `source=actuation` and omitted for direct
shipping. Ship copies every field verbatim from Actuating's current readiness
receipt. It does not reconstruct them from PR text or interpret them as
architecture, review, or closure authority.

`SHIP-v1` is immutable evidence for one publication epoch. Return the complete
record to Actuating; only Actuating may evaluate publication currentness and
record it in the Evidence Ledger.
