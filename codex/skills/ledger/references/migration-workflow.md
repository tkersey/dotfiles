# Migration Workflow

## Learnings

Default target:

```text
.ledger/learnings/learnings.jsonl
```

Dry run:

```bash
learnings migrate --dry-run
```

Copy first:

```bash
learnings migrate --mode copy
```

Do not delete `.learnings.jsonl` by default. After migration, normal `learnings append` writes the namespaced `.ledger` store.

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
