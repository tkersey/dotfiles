# Ledger canonical custody

Read this guide for selected canonical storage/context or maintenance work. The
entrypoint owns bootstrap, authority, and definition-relative result semantics.

## Storage-context ownership

The [skill body](../SKILL.md#storage-context-ownership) owns personal storage
location policy. Pass its selected `ledger_home` explicitly. Native `ledger context`
implements catalog identity and associations; [storage-context.md](storage-context.md)
describes selection and authorized migration. Consumers select semantic
definitions and operations; they do not derive another physical storage path.

Learnings, Negative Ledger, and Review Fold use personal managed custody. Existing independent
histories retain their store IDs and owner-defined slots. A worktree is optional
evidence provenance and a lookup association, not the lifetime of the history.
Other owners opt into personal custody explicitly; session/worktree-specific
protocols are not silently moved. Pure validation/materialization needs no store.

Resolve a known stable identity without Git:

```bash
ledger context --catalog-root "$ledger_home" --store-id "<store-id>"
```

For an opted-in owner, use automatic owner preparation below before its first
projection or capture. For context resolution without an owner, ensure the
selected workspace association:

```bash
ledger context --catalog-root "$ledger_home" --workspace "<workspace-path>" --ensure
```

Retain `repository_id`, `store_id`, `store_root`, and `native_args` from the
`ledger-workspace-context/v1` result. `workspace_root` and `git_common_dir` are
nullable provenance. Normal native operations use the returned selector:

```bash
ledger project --definition "$definition" --projection "<owner-projection>" \
  --store-root "<context.store_root>" --store-id "<context.store_id>" --format json
```

`transact`, `doctor`, segmented migration, and exact recovery use the same
selector. Native Ledger checks the selected root and validates the relevant
owner custody. Use `doctor` for diagnosis or a selected integrity check; do not
surround every validated transaction with redundant full-store checks.

Ensure first resolves the catalog. If the selected Git workspace is unregistered,
it automatically imports its existing valid Git registration using the locked
catalog adoption operation. Only catalog metadata changes; identity, native
custody, and the original registration stay intact. Missing registrations,
invalid roots, and conflicts still fail; ensure never initializes empty history.
Reuse successful context within the session. Default `ledger context` lookup remains strictly
read-only and is the route when the user explicitly prohibits file/custody
maintenance or the environment enforces non-writable access.
Neither lookup nor registration adoption enumerates sibling worktrees, inspects
legacy logs, or demands a migration receipt. An absent
historical source limits a recovery claim, not access to intact owned data.
Git-bound workspace aliases require their registered common-directory identity
to remain verifiable. After checkout deletion, use direct `--store-id` access.
Legacy catalogs without per-workspace provenance conservatively reject plain
paths associated with a Git-bound store; explicit adoption of a live Git
workspace records its identity. Explicitly registered plain workspaces remain
usable even when their store also has Git associations.
Native invalid rows, bindings, root identity mismatches, and recovery errors
remain failures. Never turn one into an empty store or a legacy `--repo` retry.

For new supported records, retain `repository_id` as stable source scope and
collect actual workspace/artifact facts separately. Sharing a personal history
does not broaden applicability. Preserve old IDs, source fields, fingerprints,
and immutable memory snapshots. Resolve qualified sources by selected store,
semantic owner, record identity, and version/evidence rather than a disposable
checkout path or bare `NEG` number.

## Explicit adoption and migration

Cataloging an existing managed root is metadata adoption, not history import.
Use [storage-context.md](storage-context.md) to import an old Git registration or
register an existing absolute root and its expected ID. This preserves the root,
its records, and its native custody; it requires no legacy worktree coverage.
Catalog associations never infer a merge from names, remotes, or branches.

New custody outside automatic owner preparation requires a selected
`ledger context --initialize` operation, optionally with a
workspace association. It creates a fresh private identity; it cannot recreate
an absent selected store or replace an existing alias. A known selected legacy
registration/history requires explicit adoption or import instead. New isolated
custody needs no claim that unrelated historical writers have stopped.

For selected legacy inspection/import or interrupted import recovery, follow
[automatic-migration.md](automatic-migration.md). `ledger context --migrate`
selects this maintenance. `--apply --confirm-no-writers` adds its authorized
effect with actual quiescence of the affected writers. Unavailable historical
worktrees can block that import's completeness; they do not block normal access.

Preserve sources and distinguish imported records from archived-only material.
An import receipt witnesses specific source snapshots and retained destination
prefixes; later valid appends do not undo that evidence. Do not delete sources,
concatenate divergent logs, rewrite provenance, or bulk-admit recovered rows to
global memory. Owners opt in through separate installed migration declarations;
native definitions remain passive.

## Storage custody and recovery

Event bytes and required binding/definition/revision custody stay together under
the selected root. Native reads fail closed for unbound existing stores. A
separately selected `bind-existing` validates the complete current-format source;
`rebind-existing` validates an authoritative replacement and changes stale binding
metadata. Neither chooses among divergent histories or blesses unknown damage.
`InvalidStoreBinding` alone is not proof that initial binding is appropriate.

Writes use owner-selected `ledger transact` operations. Never hand-edit, compact,
reinterpret, or skip canonical records. Explicit cold transport is not an alternate
semantic writer. Fail closed on unknown closure, ABI, operator, binding, integrity,
replay, projection, or recovery state.

Before the first projection or capture for an owner that opts in, use
[automatic owner upgrade](automatic-migration.md#automatic-owner-upgrade) with
`--ensure-owner --definition` automatically, without separate approval or a
new-record capture requirement. It initializes managed custody, transports compatible
current-format history, or restores a missing static slot against its unchanged
native binding. It waits for active writers under native locks. Continue with the
returned managed selector; never fall back to a local store on failure. Analysis
and review use this same preparation. Explicit no-maintenance owner selection uses
`--read-only --definition` and never creates or repairs custody.

Lease expiry does not transfer authority. Recovery is bound to one transaction's
resource, lock identity, fencing token, owner, and witnessed lease state. Read
[storage-maintenance.md](storage-maintenance.md) before recovery or version-dependent
migration. There is no broad reclaim or repair mode.

