# Retrace Artifact Root

New retrace artifacts belong under:

```text
.ledger/retrace/<inquiry-id>/
```

Do not create new `.retrace/` roots.

When replaying legacy execution-controller decisions, preserve:

```text
workspace ID/sequence
plan ID/sequence
claim/fencing
branch epoch
session view
actuation-authority receipt
```
