# Personal storage context

This reference and `../scripts/ledger_context.py` own the Codex integration's
location policy. The native CLI takes explicit roots and has no Codex/Git default.

## Catalog and identity

The personal home is `${CODEX_HOME:-$HOME/.codex}/ledger`; an absolute
`LEDGER_HOME` selects another home. Its `catalog.json` is authoritative:

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

Normal reads never create metadata. Catalog changes use one private advisory
lock and atomic, synced publication. Root/marker/control mismatches, symlink
components, malformed metadata, and alias conflicts fail explicitly. An absent
known root is never replaced with empty custody. Changing the configured home
selects another catalog namespace; an unknown store there is an error, not an
implicit initialization or lookup fallback.

## Normal selection

Discover registered identities after a checkout disappears:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" --list-stores
```

The read-only listing returns IDs, roots, and explicit associations. It makes no
native store-health claim and does not initialize an absent catalog.

Prefer the known source's stable identity:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" --store-id "<store-id>"
```

This works without any checkout or Git metadata. A cataloged workspace is an
optional convenience:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" --repo "<workspace-path>"
```

A live Git worktree can supply its root/common-directory associations, so linked
worktrees share an explicitly attached family. The helper never enumerates sibling
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

`ensure_custody.py` without `--migrate` performs this same read-only resolution.
Migration receipts and complete legacy inventory are never access prerequisites.
No selector means no implicit default store; select a stable ID or a cataloged
workspace. Caller code uses `resolve(repo=None, store_id=...)`.

## Explicit catalog adoption

Import an existing Git registration once:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" \
  --import-registration "<git-common-dir>/ledger-store.json" \
  --repo "<workspace-path>"
```

The selected metadata must have its original registration schema and an intact
matching root. The helper records that identity in the personal catalog and
preserves the old file as historical evidence. Ordinary lookup never reads it
as a fallback. Missing sibling worktrees do not block adoption.

When Git metadata is unavailable, select the actual existing root and ID:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" \
  --register-root "<absolute-existing-root>" --store-id "<existing-store-id>"
```

The marker and control directory must already exist. This command does not
rebind, migrate, or claim that all historical records were recovered. Run a
selected owner projection or doctor when the task needs that evidence.

Associate a new workspace with an existing cataloged identity explicitly:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" \
  --store-id "<store-id>" --repo "<workspace-path>" --attach-workspace
```

Existing conflicting aliases or another root for the same ID are errors; these
commands are not relocation, alias replacement, or history reconciliation.
Repeated identical adoption leaves catalog content unchanged. `--register-root`
and `--import-registration` may also take `--repo` to publish the association
with the adoption.

## New custody and historical import

For an authorized new personal history:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" --initialize
```

Add `--repo "<workspace-path>"` only when that workspace should select the new
identity. Retain the returned ID. Initialization with an unknown explicit
`--store-id` is forbidden, and an established broken root cannot be recreated.
Known legacy registration or history in the selected workspace requires explicit
adoption/import; the helper does not claim coverage of undiscovered sources.

New isolated roots require no global writer shutdown. Legacy cold transport and
historical import do require actual quiescence of affected old and managed writers.
Read [automatic-migration.md](automatic-migration.md) and select `--migrate` for
that maintenance. Its source preservation and owner reconciliation requirements
do not gate unrelated or already-owned canonical data.

The low-level `--initialize --adopt-from <source-worktree> --definition <owner>`
procedure remains explicit cold transport for selected legacy worktree histories.
It additionally requires `--repo` and `--confirm-no-writers`, complete owner
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
