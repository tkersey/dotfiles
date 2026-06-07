# Claim Decision Kernel

The Claim Decision Kernel is the always-on review-adjudication artifact. It is
small enough to emit in root-equivalent flows and strict enough to prevent silent
implementation laundering.

```md
## Claim Decision Kernel

| id/thread | claim | current-state truth | route | warrant id | proof ref | status |
|---|---|---|---|---|---|---|
```

Rules:

- one row per raw claim
- every row has a warrant id
- every route has a proof ref or explicit missing proof marker for `blocked`
- route names come from `schema-v9.yaml`
- a missing kernel means the adjudication is incomplete

The kernel answers only: what route is selected and which warrant authorizes it.
Detailed reasoning lives in triggered annexes.
