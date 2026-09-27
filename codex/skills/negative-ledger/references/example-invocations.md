# Example Invocations

Resolve the verified workspace through `$ledger` first and retain
`context.store_root` and `context.store_id` for every canonical operation below.
The admission adapter's `--repo` names the evidence workspace; it resolves
managed custody internally.

## Implicit Route Check Before Retry

```md
The same parser-tolerance repair failed review again. Check what we already tried before choosing another route.
```

Expected disposition:

```text
mapped
```

Expected flow:

```bash
negative_ledger_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json")"

ledger project \
  --definition "$negative_ledger_definition" \
  --projection route-gate \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --param "artifact=<full-commit-id>" \
  --param "identity=parser-tolerance" \
  --format json
```

Do not capture merely because the cue activated the skill. Capture only after the current failure has an inspectable witness and a future-routing delta.

## Transient Failure Is No-Op

```md
A unit test is red while the first implementation is still incomplete.
```

Expected disposition:

```text
no-op
```

A transient implementation failure is not durable negative evidence unless it falsifies a named route under representative conditions.

## Capture and Admit a Failed Route

```md
Use $negative-ledger to capture this failed route.
Hypothesis: same-leaf batching improves small-write throughput.
Attempted change: prototype in btree/mutation_run.*
Witness:
- command: zig build bench -- write-small-n
- result: 7% regression
Need:
- canonical Ledger capture transaction
- complete current-record projection
- negative-ledger memory admission if the route is likely to recur
- separate proof lines for both stores
```

Expected flow:

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation capture \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input capture=capture.json \
  --format json

memory_source_notes_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/memory-source-notes")"
uv run "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit --repo "<workspace-root>" --id NEG-000001 --kind ledger-projection
```

## Reopen Old Evidence

```md
Use $negative-ledger to reopen the old evidence.
Old record: NEG-000004.
Changed condition: the MVCC bookkeeping path was replaced.
Need:
- append-only canonical status transition
- criterion-bound before/after proof and structured source references
- memory-source ledger-status-transition note if the old exclusion is already durable memory
```

Expected proof packet and flow:

```json
{
  "neg_id": "NEG-000004",
  "from": "stale",
  "to": "reopened",
  "reason": "The MVCC bookkeeping path changed.",
  "criterion_ids": ["bookkeeping-path-changed"],
  "criterion_changes": [
    {
      "criterion_id": "bookkeeping-path-changed",
      "before": "commit abc123 used the old bookkeeping path",
      "after": "commit def456 uses the replacement path"
    }
  ],
  "source_refs": [
    {"kind": "git", "ref": "commit:def456"}
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
