# Source Store Layout

Canonical repo-local sources are addressed through their owning definitions:

```text
$learnings          definitions/ledger/learnings-protocol.json
$negative-ledger    definitions/ledger/negative-evidence-protocol.json
$synesthesia        definitions/ledger/synesthesia-protocol.json
$actuating          definitions/ledger/evidence-protocol.json
```

Current source-memory stores:

```text
.ledger/learnings/events.jsonl
.ledger/negative-ledger/events.jsonl
```

Synesthesia store:

```text
.ledger/synesthesia/events.jsonl
```

Operational, non-memory store:

```text
.ledger/actuation/<safe-goal-id>/evidence.jsonl
```

Normal reads use `ledger project` or `ledger doctor`; writes use
`ledger transact`, always with the owning definition. An existing current-format
store must be bound once through that definition's explicit `bind-existing`
operation. Normal reads and writes reject an unbound store and never inspect an
alternate path.

Memory-source notes live outside the repo:

```text
~/.codex/memories/extensions/<source>/notes/*.md
```

They are immutable admission snapshots. Phase 2 owns compiled outputs:

```text
~/.codex/memories/memory_summary.md
~/.codex/memories/MEMORY.md
~/.codex/memories/skills/*
```
