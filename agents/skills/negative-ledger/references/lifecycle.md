# Negative Ledger lifecycle

Read [store.md](store.md) before canonical operations. A transition to `active`
requires the complete proof-bearing promotion in [capture.md](capture.md), not
a status-only event. For disputed breadth, narrowing or supersession, apply its
[scope challenge](capture.md#exclusion-scope-challenge) first. Preserve an active
exact applicable gate until a legal owner transition changes it.

## Lifecycle Transitions

Use append-only status events. Every transition requires JSON proof with reason
and structured source references:

```json
{
  "neg_id": "NEG-000001",
  "from": "active",
  "to": "accepted_risk",
  "reason": "The prior evidence was accepted as a bounded risk.",
  "criterion_ids": [],
  "criterion_changes": [],
  "source_refs": [{"kind": "review", "ref": "PR 123 acceptance"}]
}
```

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation transition \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input transition=transition.json \
  --format json
```

Reopening requires a proved before/after change for a criterion already present:

```json
{
  "neg_id": "NEG-000001",
  "from": "stale",
  "to": "reopened",
  "reason": "The implementation and representative fixture changed.",
  "criterion_ids": ["artifact-or-fixture-changed"],
  "criterion_changes": [{
    "criterion_id": "artifact-or-fixture-changed",
    "before": "commit abc123 with fixture v1",
    "after": "commit def456 with fixture v2"
  }],
  "source_refs": [
    {"kind": "git", "ref": "commit:def456"},
    {"kind": "test", "ref": "zig build test-ledger --summary all"}
  ]
}
```

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation transition \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input transition=reopen-proof.json \
  --format json
```

Ledger rejects illegal edges, promotion without a complete active record,
unknown criteria, and unchanged before/after claims before append. Never rewrite
old events. Concurrent worktrees do not weaken these transition preconditions.

