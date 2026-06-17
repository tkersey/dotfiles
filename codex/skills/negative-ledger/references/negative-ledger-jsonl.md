# Negative Ledger JSONL Store

Use `.ledger/negative-ledger.jsonl` as the repo-local durable store for negative evidence.

Do not store `$negative-ledger` state under `.step`. Do not treat `.learnings.jsonl` as the primary negative-ledger store.

## Read path

Use the `ledger` CLI before choosing or repeating a route in search-heavy work.

### Initialize the store

```bash
ledger init
```

### Query active records

```bash
ledger query
ledger handoff
ledger show --id NEG-000001
```

### Map current route

```bash
ledger map \
  --route "<selected-route>" \
  --cluster "<cluster-id>" \
  --artifact "<artifact-state-id>"
```

Interpret exit codes:

- `0`: map succeeded and no active exact exclusion blocks the route.
- `2`: active exact exclusion matched; route is blocked unless reopened/stale/superseded/accepted.
- `3`: operational gate source is missing; same-cluster mutation is blocked.

Fuzzy candidates are suggest-only and cannot block by themselves.

## Capture path

Append through `ledger capture`; do not hand-edit `.ledger/negative-ledger.jsonl`.

```bash
ledger capture --json capture.json
```

Minimum capture payload:

```json
{
  "hypothesis": "route fails under current artifact",
  "route_id": "review-route",
  "cluster_id": "same-cluster",
  "artifact_state_id": "HEAD",
  "source_refs": [
    { "kind": "test", "ref": "zig build test" }
  ],
  "observed_outcome": "the same counterexample recurred",
  "failure_class": "no-effect",
  "reopening_criteria": ["new artifact state invalidates the old witness"]
}
```

Captures without witness evidence are stored as `need-evidence`, not active exclusions.

## Historical learnings

`learnings` rows may be candidate source evidence. To promote one into an active ledger entry, verify:

- the row has inspectable evidence anchors, not just narrative;
- the component/path/benchmark/invariant still matches the current artifact state;
- the old failure mechanism is still possible;
- the exclusion rule is narrow;
- reopening criteria are explicit.

If those checks fail, capture `stale`, `superseded`, `unknown`, or `need-evidence`; do not create an active exclusion.

## Capture proof line

When a durable write is attempted, report one proof line:

- `ledger-capture: neg_id=NEG-... status=active`
- `ledger-capture: neg_id=NEG-... status=need-evidence`
- `ledger-capture: not-attempted: evidence not durable enough`
