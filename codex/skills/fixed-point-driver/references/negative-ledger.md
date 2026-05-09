# Negative Ledger integration moved

The reusable negative-evidence protocol now lives in the standalone skill:

```text
codex/skills/negative-ledger/SKILL.md
codex/skills/negative-ledger/references/negative-ledger-contract.md
codex/skills/negative-ledger/references/learnings-source.md
codex/skills/negative-ledger/agents/negative-ledger-mapper.md
```

`fixed-point-driver` keeps a Negative Evidence Ledger as an optional campaign ledger, but the standalone `$negative-ledger` skill owns capture, query, mapping, reopening, compaction, and handoff semantics.

Use `$learnings` / the `learnings` CLI as the preferred durable source and persistence layer when available. Do not create a separate `.negative-ledger.jsonl` unless the user explicitly asks for independent storage.
