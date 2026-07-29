# Planning Artifact Root

When Plan persistence is useful, the sole authoritative artifact is:

```text
.ledger/plan/<plan-id>/policy.json
```

It contains canonical EPG-v1 source. A revision updates the same policy identity; a
materially different objective receives another `plan_id`.

Ledger alone creates, replaces, reads, and diagnoses this document through
`plan/plan-policy-document`. Its `create` and `revise` operations reuse the imported
`plan/execution-policy-graph` validator. `revise` requires the exact current
revision and a retry-stable request ID. Plan must verify that the requested
`plan_id`, the EPG's `plan_id`, and the returned logical reference agree.

Human projections are generated on demand. Ledger validation metadata and
consumer-owned runtime state, decisions, observations, and receipts are not Plan
artifacts and never belong under `.ledger/plan/`.
