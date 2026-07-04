---
name: ledger
description: "Coordinate repo-local source-memory stores under `.ledger/`: status, migration, doctor, harvest planning, and memory admission handoff without bypassing source-specific authority."
metadata:
  version: "1.0.0"
---

# Ledger

## Mission

Coordinate repo-local source-memory stores under `.ledger/`.

Use `$ledger` for source-memory migration, cross-store doctor, harvest planning, and memory admission coordination. Do not use it to bypass source-specific authority.

Canonical stores:

- `.ledger/learnings/events.jsonl`
- `.ledger/negative-ledger/events.jsonl`
- `.ledger/synesthesia/events.jsonl` when present

Source-store state model:

```text
missing -> legacy-only -> migrated/current -> invalid
```

`legacy-only` is an actionable preflight state. It means reads may use
compatibility fallback, but writes and commit closeout must first run the owning
source migration. For learnings, that owner is
`ledger migrate --source learnings --mode copy`; for negative evidence, that
owner is `ledger migrate --mode copy`. Synesthesia can report `notes-only`
during transition; copy import is explicit through
`ledger migrate --source synesthesia --mode copy`.

Compiled Codex memory is still owned by Phase 2. Memory-source notes are admission snapshots, not canonical stores.

## Trigger Cues

- `$ledger`;
- ledger status;
- source memory stores;
- migrate learnings;
- memory harvesting;
- harvest stores for memories;
- why memories are not being captured;
- doctor `.ledger`;
- cross-store memory digest.

## Authority

`$ledger` may coordinate, inspect, and recommend. Writes are delegated to source-specific tools:

- `$learnings` / `ledger --source learnings` for `.ledger/learnings/events.jsonl`;
- `$negative-ledger` / `ledger` for `.ledger/negative-ledger/events.jsonl`;
- `$synesthesia` / `ledger --source synesthesia` for `.ledger/synesthesia/events.jsonl`; current Synesthesia notes remain transition evidence;
- `$memory-source-notes` / `memory-note` for immutable admission snapshots.

Never write `memory_summary.md`, `MEMORY.md`, or memory-root `skills/*`.

## Read-Only Workflow

1. Resolve the git root.
2. Inspect `.ledger/`, previous `.ledger/learnings/learnings.jsonl`, legacy `.learnings.jsonl`, and current Synesthesia notes when present.
3. Classify each store as `migrated`, `legacy-only`, `current`, `legacy-path`, `notes-only`, `missing`, or `invalid`.
4. Run source doctors when available.
5. If any required source is `legacy-only` or Synesthesia is `notes-only` and import is requested, report the exact owning migration
   command before any harvest or append recommendation.
6. Report harvest candidates and recommended source-specific commands.

See [source-store-layout.md](references/source-store-layout.md), [migration-workflow.md](references/migration-workflow.md), and [harvest-workflow.md](references/harvest-workflow.md).

## Output Shape

```md
## Ledger status

- learnings: migrated | legacy-only | missing | invalid
- negative-ledger: current | legacy-path | missing | invalid
- synesthesia: notes-only | ledger-present | missing | invalid

## Harvest candidates

- learnings:
- negative-ledger:
- synesthesia:

## Recommended actions

1. ...

## Proof

- commands run:
- source stores read:
- writes attempted:
- memory-note admissions:
```

## Guardrails

- Do not mutate a source store except through its owning CLI.
- Do not treat memory-source notes as the canonical store.
- Do not admit every source-store event to memory.
- Do not block a route from Negative Ledger memory without current ledger verification.
- Do not turn Synesthesia decorative language into memory.
