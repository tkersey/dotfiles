# Source Store Layout

Canonical repo-local sources are addressed only through their owning passive
Ledger definitions:

```text
$learnings          definitions/ledger/learnings-protocol.json
$negative-ledger    definitions/ledger/negative-evidence-protocol.json
$synesthesia        definitions/ledger/synesthesia-protocol.json
```

Current canonical stores:

```text
.ledger/learnings/events.jsonl
.ledger/negative-ledger/events.jsonl
.ledger/synesthesia/events.jsonl
```

Normal reads use `ledger project` or `ledger doctor`; writes use
`ledger transact`, always with the owning definition and an explicit operation.
An existing current-format store must be bound once through that definition's
explicit `bind-existing` operation. Normal reads and writes reject an unbound
store and never inspect an alternate path.

Memory-source notes live outside the repository:

```text
${CODEX_HOME:-$HOME/.codex}/memories/extensions/<source>/notes/*.md
```

They are immutable, derived admission snapshots. They do not replace the
canonical store or inherit operational authority from it.

Phase 2 alone owns compiled outputs:

```text
${CODEX_HOME:-$HOME/.codex}/memories/memory_summary.md
${CODEX_HOME:-$HOME/.codex}/memories/MEMORY.md
${CODEX_HOME:-$HOME/.codex}/memories/skills/*
```

Reconciliation may read all three layers. It must not write any of them,
reinterpret source eligibility, or match repository-scoped notes by basename.
