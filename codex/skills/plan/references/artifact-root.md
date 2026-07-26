# Planning Artifact Root

When Plan persistence is useful, the sole authoritative artifact is:

```text
.ledger/plan/<plan-id>/policy.json
```

It contains canonical EPG-v1 source. A revision updates the same policy identity; a
materially different objective receives another `plan_id`.

Human projections are generated on demand. Compiler normalization and
consumer-owned runtime state, decisions, observations, and receipts are not Plan
artifacts and never belong under `.ledger/plan/`.
