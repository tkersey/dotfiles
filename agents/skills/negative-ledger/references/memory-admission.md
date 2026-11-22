# Negative Ledger memory admission

Read [store.md](store.md) before canonical projection operations. Apply the
admission gate before transport; a successful canonical write is independent of
derived admission and survives a later admission failure. This guide grants no
canonical capture, lifecycle or publication authority.

## Memory Admission Gate

This gate governs custom source-note admission. Ordinary native memory can carry
a useful project locator or operating preference without a canonical negative
record. Neither path grants exclusion authority. Select a custom source note
only when preserving the bounded projection and its source identity adds value.

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

When an established construction covers the relevant failure and preserves
required behavior, a locator to that owner may be sufficient future guidance.
Withdraw or supersede redundant admitted warnings through the supported note
operation; retain still-useful experiment evidence and canonical exclusions for
other applicable variants. Memory withdrawal changes admitted support, not the
truth of the historical observation or the canonical lifecycle. A new passing
run alone does not justify retirement. Verify reader visibility separately from
any observed downstream consolidation; a persisted correction is not proof that
compiled memory has changed.

## Admission Workflow

For withdrawal or replacement of an existing reminder, use the
[managed reminder update](../../memory-source-notes/SKILL.md#managed-reminder-updates)
after the source owner accepts its scope and evidence. Select
`--source negative-ledger`, the canonical `--id NEG-...`, exact prior
`--prior-note-id MSN-...`, and `--operation retract` or `supersede`.
The adapter derives `ledger-retraction` or `ledger-supersession`; changing an
ordinary projection's `--kind` cannot substitute for this operation. Missing or
conflicting prior identity blocks the memory update, without changing canonical
history or permitting an otherwise excluded retry.

After the source owner accepts admission, load `$memory-source-notes` and resolve
its installed root independently of the target repository. Retain `ledger_home`
selected by `$ledger` for the same context:

```bash
memory_source_notes_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/memory-source-notes")"
```

```bash
uv run "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit \
  --catalog-root "$ledger_home" \
  --store-id "<context.store_id>" \
  --id NEG-000001 \
  --kind ledger-projection
```

For a status transition:

```bash
uv run "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit \
  --catalog-root "$ledger_home" \
  --store-id "<context.store_id>" \
  --id NEG-000001 \
  --kind ledger-status-transition
```

The adapter delegates `--store-id` resolution to `$ledger` and passes its native
selector to the definition-bound projection. `--repo` may resolve a cataloged
workspace alias; a checkout is not required. It rejects
incomplete projections, preserves the canonical payload, and keeps canonical
projection predecessors in source references rather than `MSN-*` relationships.
A first admission after a lifecycle transition needs no prior memory note; a
first snapshot of `reopened` state is a memory assertion, with that canonical
status retained in its payload. The adapter invokes the immutable writer
idempotently. It transports an accepted decision, not a judgment
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

