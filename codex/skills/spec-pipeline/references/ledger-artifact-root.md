# `.ledger/` Artifact Convention

All new machine-owned workflow artifacts live under:

```text
.ledger/<owner>/
```

Examples:

```text
.ledger/plan/
.ledger/actuating/
.ledger/review-closure/
.ledger/retrace/
.ledger/seq/
.ledger/negative-ledger/
```

Specifications and user-facing source documents may remain under `docs/`.

A specification handoff to `$plan` should provide an immutable source digest
and proposed `plan_id`; `$plan` owns the policy artifact and `$actuating` owns execution.
