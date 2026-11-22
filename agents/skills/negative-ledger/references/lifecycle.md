# Negative Ledger lifecycle

Read [store.md](store.md) before canonical operations. A transition to `active`
requires the complete proof-bearing promotion in [capture.md](capture.md), not
a status-only event. For disputed breadth, narrowing or supersession, apply its
[scope challenge](capture.md#exclusion-scope-challenge) first. Preserve an active
exact applicable gate until a legal owner transition changes it.

## Construction and continued relevance

An adequate construction may remove the need to remember a warning in its
covered domain. Establish the relevant invariant, enforced boundary, permitted
operations, and preservation of required-valid behavior from inspectable
implementation and verification. A repaired example or a passing test alone does
not establish that the failure family is unavailable.

Check the old record's scope before changing lifecycle. A new implementation
does not make a true historical failure false, nor make an exclusion stale for
maintained variants it still covers. If only a memory reminder has lost value,
use [memory withdrawal](memory-admission.md) without inventing a canonical status
change. If the exclusion itself is overbroad, retain the still-supported narrow
case and use proof-bearing supersession. Reopening requires a real change to an
existing criterion; a discovered error in the old claim is not such a change.

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

