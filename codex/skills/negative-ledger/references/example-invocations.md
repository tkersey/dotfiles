# Example Invocations

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
ledger map \
  --route "parser-tolerance" \
  --cluster "parser-compatibility" \
  --artifact "<immutable-artifact-state-id>"
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
Use $negative-ledger capture.
Hypothesis: same-leaf batching improves small-write throughput.
Attempted change: prototype in btree/mutation_run.*
Witness:
- command: zig build bench -- write-small-n
- result: 7% regression
Need:
- ledger capture
- full ledger export
- negative-ledger memory admission if the route is likely to recur
- separate proof lines for both stores
```

Expected flow:

```bash
ledger capture --json capture.json
ledger export --id NEG-000001 --format memory-note |
  memory-note append --extension negative-ledger --kind ledger-projection --json -
```

## Reopen Old Evidence

```md
Use $negative-ledger reopen.
Old record: NEG-000004.
Changed condition: the MVCC bookkeeping path was replaced.
Need:
- append-only ledger status transition
- proof obligations before retrying
- memory-source ledger-status-transition note if the old exclusion is already durable memory
```
