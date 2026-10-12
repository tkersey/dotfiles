# Source Store Layout

## Canonical custody

Address source records only through their owning passive Ledger definition:

| Source | Definition | Selection |
|---|---|---|
| Learnings | `learnings/definitions/ledger/learnings-protocol.json` | `$ledger` personal store context |
| Negative Ledger | `negative-ledger/definitions/ledger/negative-evidence-protocol.json` | The same managed context contract |
| Synesthesia | `synesthesia/definitions/ledger/synesthesia-protocol.json` | Explicit unmanaged `--repo` root |

For the managed sources, retain `$ledger`'s returned `native_args` and
`repository_id`. Direct `--store-id` selection needs no workspace or Git.
A registered workspace is an optional alias, not canonical custody. Do not
duplicate the catalog, root discovery, import, or maintenance policy here.
Canonical namespaces such as `.ledger/learnings/events.jsonl` are relative to
the selected native store root. A path embedded in an old immutable snapshot
does not select the current working directory as its authority.

Normal reads use `ledger project` or `ledger doctor`; writes use
`ledger transact`, always with the owner's definition and explicit operation.
Native custody/definition failures stop that source operation. Do not fall back
to a legacy worktree or inspect an unbound alternate store.

## Selected memory layout

Ask the native writer for `memory-note-layout/v1`:

```bash
memory-note path --extension learnings --format json
```

The native writer resolves the effective Codex configuration through local
app-server `config/read`. Consumers use `scripts/memory_layout.py` to validate
the returned paths and pin the returned `--codex-home` and `--memory-version`
for the whole operation. An explicit version selects a known active-session
layout. Python and shell consumers do not parse TOML or infer the version from
existing directories.

| Returned field | Content/owner |
|---|---|
| `notes_dir` | Immutable admission envelopes; native `memory-note` writes |
| `instructions_path` | Current tracked extension instructions copied as a regular file |
| `resources_dir` | Disposable Synesthesia digest and consolidation aids |
| `memory_root` | The selected Phase 2 workspace |

Version v1 selects `<codex_home>/memories`; v2 selects
`<codex_home>/memories_v2`. These describe the native result, not a parallel
consumer resolver. Ordinary append, read, doctor, digest, and instruction-copy
commands touch only the selected layout. A missing selected file never enables
a legacy fallback.

Phase 2 v2 produces only `<memory_root>/memory_summary.md`, under its compact
context budget. Detailed source evidence stays in notes. Version v1 may also
produce `MEMORY.md` and memory-root `skills/*`. Ordinary work must not create or
edit any compiled artifact. The copy deployment command writes only the three
controlled `instructions.md` files; it leaves notes and resources untouched.

## Explicit version cutover

Coordinate source identity, writer versions, and rollback through the Ledger
[upgrade guide](../../ledger/references/personal-store-upgrade.md). Existing notes
already in the selected version stay in place.

Inspect both versions explicitly only during requested storage maintenance.
An empty old note directory requires no migration; do not manufacture notes to
fill it. For admitted notes that are stranded in v1:

```bash
memory-note migrate --extension learnings \
  --codex-home "<selected-codex-home>" \
  --from-memory-version v1 --memory-version v2 --dry-run

memory-note migrate --extension learnings \
  --codex-home "<selected-codex-home>" \
  --from-memory-version v1 --memory-version v2
```

The native maintenance operation copies unchanged envelope bytes and filenames,
retaining note IDs, timestamps, fingerprints, and relationships. A matching ID
with identical bytes is skipped. ID/content or filename conflicts stop the
preflight; distinct note IDs remain distinct even when their fingerprints
match. Originals are retained as migration evidence. They are not read or
written by ordinary selected-root operations.

Never re-export and re-append historical envelopes to move them, manually edit
their scope/IDs, or admit canonical rows as part of a location migration.
Copy current extension instructions into the selected root separately and
regenerate only disposable source digests there. Do not copy compiled memory
between versions as a substitute for the selected compiler.

For the three controlled extension instructions, use the pinned native layout:

```bash
uv run "$memory_source_notes_skill_root/scripts/memory_source_layout.py" sync-instructions \
  --codex-home "<selected-codex-home>" --memory-version v2
```

Use `v1` instead when that is the selected reader layout. This command copies
tracked instructions as regular files; it does not migrate or append notes.

## Verification boundaries

Keep these observations separate:

1. Native append or migration success proves an immutable file outcome.
2. Selected-root list/show plus matching envelope bytes proves tool visibility.
3. A fresh Codex session's read of that root proves reader visibility.
4. An exact note ID in the selected compiler output proves a literal reference.
5. A later witnessed decision using the knowledge is evidence of behavioral value.

No lower stage proves a higher one. V2 may paraphrase, route, or omit material;
a missing literal note ID alone cannot establish compiler lag or rejection.
Reconciliation reports unavailable inputs per source and preserves healthy
results from the other sources. It never grants eligibility or operational
route authority.
