# Example Invocations

## Capture and Admit a Failed Route

```md
Use $negative-ledger capture.
Hypothesis: same-leaf batching improves small-write throughput.
Attempted change: prototype in btree/mutation_run.*
Witness:
- command: zig build bench -- write-small-n
- result: 7% regression
Need:
- `$ledger run -- capture`
- full `$ledger run -- export`
- negative-ledger memory admission if the route is likely to recur
- separate proof lines for both stores
```

Expected flow:

```text
$ledger run -- capture --json capture.json
$ledger run -- export --id NEG-000001 --format memory-note
memory-note append --extension negative-ledger --kind ledger-projection \
  --json <export-output>
```

## Reopen Old Evidence

```md
Use $negative-ledger reopen.
Old record: NEG-000004.
Changed condition: the MVCC bookkeeping path was replaced.
Need:
- append-only negative-ledger status transition
- proof obligations before retrying
- memory-source ledger-status-transition note if the old exclusion is already durable memory
```
