# Migration Workflow

## Learnings

Default target:

```text
.ledger/learnings/events.jsonl
```

Dry run:

```bash
ledger migrate --source learnings --dry-run
```

Copy first:

```bash
ledger migrate --source learnings --mode copy
```

Required preflight before append or commit closeout:

```bash
ledger doctor --source learnings
```

If the doctor reports `legacy-only`, run the dry run and copy migration before
any `ledger capture --source learnings`:

```bash
ledger migrate --source learnings --dry-run --mode copy
ledger migrate --source learnings --mode copy
ledger doctor --source learnings
```

Do not delete `.learnings.jsonl` or `.ledger/learnings/learnings.jsonl` by default. After migration, normal `ledger capture --source learnings` writes the namespaced `.ledger` event store.

## Negative Ledger

Default target:

```text
.ledger/negative-ledger/events.jsonl
```

Dry run:

```bash
ledger migrate --dry-run
```

Copy first:

```bash
ledger migrate \
  --from .ledger/negative-ledger.jsonl \
  --to .ledger/negative-ledger/events.jsonl \
  --mode copy
```

## Safety

- Resolve the git root before migration.
- Reject invalid JSONL.
- Preserve row or event order.
- Prefer copy before move.
- Use source-specific doctors after migration.
- Leave memory-source notes and Phase 2 compiled memory untouched.
