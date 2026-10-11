# Negative Ledger memory admission

Read [store.md](store.md) before canonical projection operations. Apply the
admission gate before transport; a successful canonical write is independent of
derived admission and survives a later admission failure. This guide grants no
canonical capture, lifecycle or publication authority.

## Memory Admission Gate

A source note is allowed only when:

1. a canonical `NEG-*` record exists;
2. `memory-note --param id=NEG-ID` validates the selected native store and returns
   a complete current projection;
3. active projections include witness, applicability, exclusion, and reopening;
4. the record is likely to matter in future related work;
5. the note embeds the full bounded projection, stable repository identity,
   event-chain/projection fingerprints, and any prior projection link.

Do not admit prose-only claims, unpromoted Learnings hits, partial
`current-records` output, every `need-evidence` candidate, or stale history with
no future routing value.

## Admission Workflow

After the source owner accepts admission, load `$memory-source-notes` and resolve
its installed root independently of the target repository:

```bash
memory_source_notes_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/memory-source-notes")"
```

```bash
uv run "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit \
  --store-id "<context.store_id>" \
  --id NEG-000001 \
  --kind ledger-projection
```

For a status transition:

```bash
uv run "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit \
  --store-id "<context.store_id>" \
  --id NEG-000001 \
  --kind ledger-status-transition
```

The adapter delegates `--store-id` resolution to `$ledger` and passes its native
selector to the definition-bound projection. `--repo` may resolve a cataloged
workspace alias; a checkout is not required. It rejects
incomplete projections, preserves deterministic payload bytes, and invokes the
immutable writer idempotently. It transports an accepted decision, not a judgment
about recurrence, utility, or route applicability.

The writer and reader must select the same configured memory root. A persisted
note, reader visibility, and observable compiled attribution are different facts;
absence of a literal `NEG-*` ID from a compact summary does not prove lag. Keep
store/owner/record identity together when reconciling sources. Do not backfill all
canonical records merely because the admission path was repaired.

If context/projection is unavailable, preserve any successful canonical transaction:

```text
memory-note: not-attempted: ledger projection unavailable
```

Do not reconstruct authority from memory/prose, fall back to local history, or
rewrite old immutable notes/provenance during adoption.

