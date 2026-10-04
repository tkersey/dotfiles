# Negative Ledger memory admission

Read [store.md](store.md) before canonical doctor/project operations. Apply the
admission gate before transport; a successful canonical write is independent of
derived admission and survives a later admission failure. This guide grants no
canonical capture, lifecycle or publication authority.

## Memory Admission Gate

A source note is allowed only when:

1. a canonical `NEG-*` record exists;
2. definition-bound doctor passes in resolved canonical custody;
3. `memory-note --param id=NEG-ID` returns a complete current projection;
4. active projections include witness, applicability, exclusion, and reopening;
5. the record is likely to matter in future related work;
6. the note embeds the full bounded projection, stable repository identity,
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
  --repo "<workspace-root>" \
  --id NEG-000001 \
  --kind ledger-projection
```

For a status transition:

```bash
uv run "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit \
  --repo "<workspace-root>" \
  --id NEG-000001 \
  --kind ledger-status-transition
```

The adapter's `--repo` identifies the evidence workspace. It delegates custody
resolution to `$ledger` and passes the managed selector to native doctor/project;
it must not use that workspace as the native storage address. It rejects
incomplete projections, preserves deterministic payload bytes, and invokes the
immutable writer idempotently. It transports an accepted decision, not a judgment
about recurrence, utility, or route applicability.

If context/projection is unavailable, preserve any successful canonical transaction:

```text
memory-note: not-attempted: ledger projection unavailable
```

Do not reconstruct authority from memory/prose, fall back to local history, or
rewrite old immutable notes/provenance during adoption.

