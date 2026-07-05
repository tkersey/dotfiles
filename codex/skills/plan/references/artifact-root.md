# Planning Artifact Root

New planning artifacts:

```text
.ledger/plan/<plan-id>/
```

The canonical plan artifact remains:

```text
.ledger/plan/<plan-id>/
```

Recommended plan artifact layout:

```text
.ledger/plan/<plan-id>/policy.json
.ledger/plan/<plan-id>/projection.md
.ledger/plan/<plan-id>/synthesis-receipt.json
.ledger/plan/<plan-id>/revisions/
```

The planning source may be tracked or local according to repository policy.

Runtime claims and projections never belong under `.ledger/plan/`.
