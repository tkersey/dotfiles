# Planning Artifact Root

New planning artifacts:

```text
.ledger/plan/<plan-id>/
```

The `$st` canonical imported state remains:

```text
.ledger/st/plans/<plan-id>/
```

The planning source may be tracked or local according to repository policy.
Runtime claims and projections never belong under `.ledger/plan/`.
