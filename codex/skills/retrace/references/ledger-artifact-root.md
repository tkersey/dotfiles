# Retrace Artifact Root

New retrace artifacts belong under:

```text
.ledger/retrace/<inquiry-id>/
```

Do not create new `.retrace/` roots.

When replaying `$st` decisions, preserve:

```text
workspace ID/sequence
plan ID/sequence
claim/fencing
branch epoch
session view
GCR-v2
```
