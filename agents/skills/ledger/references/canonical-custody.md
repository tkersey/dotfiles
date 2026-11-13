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

For an opted-in owner, follow [owner access](#owner-access) before its first
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
Reuse successful context within the session. Default `ledger context` lookup
remains strictly read-only, including when custody maintenance is prohibited.
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

## Owner access

Bootstrap Ledger 1.8.0 or newer with `ensure-ledger --min-version 1.8.0` before
owner selection. Start a canonical read with the owner's installed definition
and migration manifest:

```bash
ledger context --catalog-root "$ledger_home" --workspace "<workspace-path>" \
  --read-only --definition "$definition" --owner-manifest "$owner_manifest"
```

Use a known `--store-id` instead of `--workspace` when no workspace is selected;
[retained pending identities](storage-context.md#normal-selection) have separate
publication constraints. Success requires a present owner slot with valid
identity, binding, integrity, and recovery state. Its `owner_health` identifies the selected slot and
revision; `source_coverage: not_checked` makes no sibling-history claim. Retain
that qualification with the projection: known records
remain useful, but absent records do not prove no prior occurrence. Owners must
also qualify current lifecycle claims when an unreconciled source could contain a
later transition; selected-history validity alone does not decide that authority.

Handle only the returned condition:

- `OwnerPreparationRequired`: when maintenance is allowed, run
  [automatic owner upgrade](automatic-migration.md#automatic-owner-upgrade) with
  the same selection, definition, and manifest, then use its returned selector.
  A missing owner in an ID with workspace associations needs the actual workspace
  for source discovery. If direct-ID preparation returns
  `OwnerPreparationRequiresWorkspace`, preserve the ID and supply that workspace;
  unknown or unavailable history remains a blocker.
- `TransactionRecoveryRequired`, `EventStoreBusy`, or `LockBusy`: when custody
  maintenance is allowed, use `--ensure-owner` with the same selection. It waits
  for participating writers and uses native recovery for supported interrupted
  target transactions, then checks that owner again. Malformed journals, unknown
  recovery state, and contention beyond the bounded wait remain blockers.
- `StoreBindingWithoutSlot`: retain the verified context returned with the
  error, then select [exact archive repair](automatic-migration.md#exact-archive-repair)
  by that same store ID. Adopt an existing uncataloged registration only as that
  route specifies. If repair returns `ArchiveRepairRequiresArchiveEvidence` and
  a workspace was selected, use [automatic owner upgrade](automatic-migration.md#automatic-owner-upgrade)
  with that same workspace, verified store ID, definition, and manifest to restore
  a matching live source under native binding and writer checks. Preserve other repair failures;
  do not infer writer quiescence or select a different store. Retry the owner read
  after successful restoration.
- Other identity, integrity, binding, recovery, or unknown failures remain actual
  blockers. Do not reinterpret them as an absent owner or attempt another store.

An explicit no-file/custody-maintenance constraint or enforced non-writable
environment prevents both escalation routes. A false semantic-capture flag does
not. Preserve the actual failed operation or constraint; do not manufacture an
empty projection or merely assert that history was unavailable.

Before the first authorized semantic write, use `--ensure-owner --definition
--owner-manifest` under the owner-upgrade guidance even if a prior read succeeded.
For a present healthy owner, ensure checks the selected identity, custody, and
recovery state without enumerating sibling worktrees. Valid target recovery and
writer waiting also stay within that selected custody. It reports
`source_coverage: not_checked`, equally for workspace and direct-ID selection.
An independently justified new capture can proceed under its owner's gate;
absence claims, sequence identity across unreconciled lineages, and lifecycle
decisions cannot borrow historical completeness from that success.

When such a premise requires live-source reconciliation, select
`--reconcile-owner` with the same definition, manifest, and verified store ID,
plus the workspace supplying the source family. This retains strict source
coverage, divergence, and writer checks. Unknown or unavailable sources remain
blockers to that claim. A checked source snapshot is point-in-time evidence,
not a fence against later legacy writers. Reuse successful readiness only while
its relevant premises remain unchanged. All operations retain the same managed
identity and their separate semantic authority.

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

Use [owner access](#owner-access) for canonical reads and the first semantic write.
Only the selected preparation or exact restoration may change custody; successful
lookup does not grant that effect or choose a different lineage.

Lease expiry does not transfer authority. Recovery is bound to one transaction's
resource, lock identity, fencing token, owner, and witnessed lease state. Read
[storage-maintenance.md](storage-maintenance.md) before recovery or version-dependent
migration. There is no broad reclaim or repair mode.

