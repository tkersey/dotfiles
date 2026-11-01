# Personal storage context

The [skill body](../SKILL.md#storage-context-ownership) owns location policy.
Pass its selected `ledger_home` as `--catalog-root`. Native host commands implement
catalog lookup, Git discovery, and authorized registration; the storage engine
receives explicit roots and has no Codex-specific default.
For a coordinated upgrade of existing installations, follow
[the upgrade guide](personal-store-upgrade.md). Normal opted-in owner access uses
automatic preparation below.

## Catalog and identity

The selected home retains the existing directory layout. Its `catalog.json` is authoritative:

```text
<storage-home>/
  catalog.json
  catalog.lock
  repos/<stable-store-id>/
    .ledger-root.json
    .ledger/
      <owner-declared logical slots>
      .bindings/
      .definitions/
      .revisions/
      .transactions/
      ...native custody resources...
```

`ledger-personal-catalog/v1` maps stable store IDs to absolute custody roots and
optional `workspace:<absolute-path>` or `git-common-dir:<absolute-path>`
associations to those IDs. Existing managed roots may remain at their exact
registered addresses. The `repos/` directory name is retained for storage
continuity; a live repository does not own or unlock the data.

The native marker remains `ledger-storage-root/v1` with the same `store_id`.
The context's qualified scope remains `ledger-repository:<store_id>`. Catalog
adoption never changes old source records, fingerprints, definition bindings,
event ordering, or immutable source-memory snapshots.

Store IDs and native roots are not names, remote URLs, commit IDs, or path hashes.
Independent histories remain independent. Never concatenate their event logs or
join bare numeric IDs across stores. Record references need store/lineage, owner,
record ID, and the applicable immutable version/evidence.

Low-level identity lookup never creates metadata. Catalog changes use one private advisory
lock and atomic, synced publication. Root/marker/control mismatches, symlink
components, malformed metadata, and alias conflicts fail explicitly. An absent
known root is never replaced with empty custody. Changing the configured home
selects another catalog namespace; an unknown store there is an error, not an
implicit initialization or lookup fallback.

## Normal selection

Before an opted-in owner's projection or capture, including analysis, run
[automatic owner preparation](automatic-migration.md#automatic-owner-upgrade)
with `--ensure-owner --definition` without separate approval. The identity lookup
commands below do not perform that preparation and are not substitutes for it.
Use non-mutating owner selection when file/custody maintenance is explicitly
prohibited, as that owner-preparation policy specifies.

Discover registered identities after a checkout disappears:

```bash
ledger context --catalog-root "$ledger_home" --list-stores
```

The read-only listing returns IDs, roots, and explicit associations. It makes no
native store-health claim and does not initialize an absent catalog.

Prefer the known source's stable identity:

```bash
ledger context --catalog-root "$ledger_home" --store-id "<store-id>"
```

This works without any checkout or Git metadata. A cataloged workspace is an
optional convenience:

```bash
ledger context --catalog-root "$ledger_home" --workspace "<workspace-path>"
```

A live Git worktree can supply its root/common-directory associations, so linked
worktrees share an explicitly attached family. The native host command never enumerates sibling
worktrees during normal access. Plain directories can be associated too. Worktree
moves within a common directory retain that family association. After moving the
common directory or using another clone, select the known ID and explicitly attach
the new workspace; remotes and basenames never infer that decision.

The result remains `ledger-workspace-context/v1` with `repository_id`, `store_id`,
`store_root`, `native_args`, and optional `workspace_root`/`git_common_dir`.
Direct ID selection returns null workspace fields. Workspace facts are evidence
provenance; the native selector supplies custody:

```text
--store-root <context.store_root> --store-id <context.store_id>
```

Use that same selector for native writes, projections, doctor, exact recovery,
and source-note admission. Native operations validate their own owner-defined
custody; context success is not a semantic health or applicability claim.
A failed projection's managed root admission exits 3, never a clear gate.

`ledger context --ensure --workspace ...` performs this lookup and, only for an unregistered
Git workspace with an existing valid registration, automatically catalogs that
same identity. Use this registration-only mode for context resolution without an
owner; use `ledger context` for strictly non-mutating identity lookup. Missing
registration fails in these low-level modes; opted-in owner preparation handles
supported initialization or current-format migration automatically. Adoption
preserves native bytes and rejects catalog conflicts.
Migration receipts and complete legacy inventory are never access prerequisites.
No selector means no implicit default store; select a stable ID or a cataloged
workspace. Callers pass `--catalog-root` and the explicit workspace or store ID.

## Explicit catalog adoption

Import an existing Git registration once:

```bash
ledger context --catalog-root "$ledger_home" \
  --import-registration "<git-common-dir>/ledger-store.json" \
  --workspace "<workspace-path>"
```

The selected metadata must have its original registration schema and an intact
matching root. The native host command records that identity in the personal catalog and
preserves the old file as historical evidence. Ordinary lookup never reads it
as a fallback. Missing sibling worktrees do not block adoption.

When Git metadata is unavailable, select the actual existing root and ID:

```bash
ledger context --catalog-root "$ledger_home" \
  --register-root "<absolute-existing-root>" --store-id "<existing-store-id>"
```

The marker and control directory must already exist. This command does not
rebind, migrate, or claim that all historical records were recovered. Run a
selected owner projection or doctor when the task needs that evidence.

Associate a new workspace with an existing cataloged identity explicitly:

```bash
ledger context --catalog-root "$ledger_home" \
  --store-id "<store-id>" --workspace "<workspace-path>" --attach-workspace
```

Existing conflicting aliases or another root for the same ID are errors; these
commands are not relocation, alias replacement, or history reconciliation.
Repeated identical adoption leaves catalog content unchanged. `--register-root`
and `--import-registration` may also take `--workspace` to publish the association
with the adoption.

## New custody and historical import

Outside automatic owner preparation, explicitly selected new personal history uses:

```bash
ledger context --catalog-root "$ledger_home" --initialize
```

Add `--workspace "<workspace-path>"` only when that workspace should select the new
identity. Retain the returned ID. Initialization with an unknown explicit
`--store-id` is forbidden, and an established broken root cannot be recreated.
This low-level initializer refuses known legacy registration or history in the
selected workspace. Use owner preparation for supported current-format history,
or select the historical importer for retired formats. When attaching a verified
Git family to new custody, initialization
also inspects its linked worktrees before staging and immediately before catalog
publication. Sibling history in `.ledger` requires explicit migration. Pass
each owner-declared retired path with `--legacy-path` when using low-level
initialization; native Ledger does not choose owner-specific retired names.
An unavailable sibling blocks new family custody until its legacy coverage is
resolved. This creation check never gates normal access, direct store selection,
or adoption of an existing identity, and does not apply to a new Git-free store.
The native host command does not claim coverage of other undiscovered sources.

New isolated roots require no global writer shutdown. The manual cold-transport
and historical-import procedures require actual quiescence of affected old and managed writers.
Read [automatic-migration.md](automatic-migration.md) and select `--migrate` for
that maintenance. Its source preservation and owner reconciliation requirements
do not gate unrelated or already-owned canonical data.

The low-level `--initialize --adopt-from <source-worktree> --definition <owner>`
procedure remains explicit cold transport for selected legacy worktree histories.
It additionally requires `--workspace` and `--confirm-no-writers`, complete owner
definitions, native doctor validation, source byte parity, and compatible
complete-record prefixes. It publishes the personal catalog, never a new Git
registration. Prefer owner-aware `--migrate` when retired formats need import.

## Durability and provenance

Keep event bytes and required binding/definition/revision archives with their
root identity. Back up the personal catalog and every referenced custody root,
including roots outside the default home. A JSONL export alone is not a custody
backup. Coherent backup/restore and interrupted native transaction handling are
separate operations; the catalog is not cross-machine synchronization.

Preserve historical workspace/branch/path fields. New supported records use the
stable qualified scope plus current immutable artifact facts, including relevant
dirty code/configuration. Shared visibility never implies shared applicability.
A query-local difference does not globally retire evidence valid elsewhere.
