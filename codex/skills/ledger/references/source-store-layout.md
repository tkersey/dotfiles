# Source Store Layout

Canonical repo-local source stores live under:

```text
.ledger/<source>/<store>
```

Current stores:

```text
.ledger/learnings/learnings.jsonl
.ledger/negative-ledger/events.jsonl
```

Future or optional stores:

```text
.ledger/synesthesia/events.jsonl
.ledger/harness/events.jsonl
```

Legacy stores:

```text
.learnings.jsonl
.ledger/negative-ledger.jsonl
```

Legacy stores are read only for migration or compatibility. Normal writes go to the namespaced `.ledger/<source>/` store.

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
