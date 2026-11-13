# Owner upgrade and historical migration

Use `ledger context --migrate` only for selected legacy inspection,
historical import, or interrupted migration. Default context lookup is read-only;
`--ensure` may adopt an existing valid Git registration. Existing custody needs no
migration receipt or complete worktree inventory. The skill body selects
`ledger_home`; every command below passes it explicitly to the native host layer.
For a coordinated upgrade of existing installations, start with
[the upgrade guide](personal-store-upgrade.md); already-managed roots normally
need catalog adoption rather than historical migration.

## Automatic owner upgrade

An opted-in owner's canonical workflow includes standing authority for routine
catalog adoption, custody initialization, compatible current-format migration,
and exact restoration. Follow [owner access](canonical-custody.md#owner-access)
first: healthy reads do not select preparation. Run this preparation when an
owner read returns `OwnerPreparationRequired`, when exact archive repair returns
`ArchiveRepairRequiresArchiveEvidence` and the same workspace can supply a
matching live source, when selected target custody needs native transaction
recovery or writer waiting, or before the first authorized semantic write. Do not
request confirmation, an approval token, or separate
migration authorization; permission to capture new semantic records does not gate
preparation needed for a read. The installed `migration.json` is the owner's
protocol opt-in, not a per-run question for the user.

Resolve the owner through:

```bash
ledger context --catalog-root "$ledger_home" --workspace "<workspace-root>" \
  --ensure-owner --definition "<installed-owner-definition>" \
  --owner-manifest "<installed-owner>/migration.json"
```

For a bound-slot restoration after archive evidence is unavailable, also pass
`--store-id "<verified-context.store_id>"` with that same workspace; a changed
association must fail rather than redirect restoration to another store.
If direct-ID ensure returns `OwnerPreparationRequiresWorkspace`, retain that ID
and select the actual associated workspace whose history must be examined. Do
not treat the uninspected history as empty or invent a replacement association.
Explicitly initialized isolated custody with no cataloged workspace associations
remains available by ID; it makes no live-source coverage claim.

Reuse the returned `native_args` for the original operation. A healthy present
managed owner is admitted from its own identity, binding, integrity, and recovery
state, with `source_coverage: not_checked`; disposable worktrees cannot revoke
that readiness. Busy selected custody is retried within the native wait bound;
supported interrupted target transactions use native recovery before reinspection.
Neither condition alone triggers sibling discovery. Malformed or unsupported
recovery state remains blocked. The native host keeps the existing identity and adopts valid
registrations. For a missing owner, it discovers finite source contexts from the
workspace and existing archive manifests, retains one pending target identity,
and invokes native `prepare`. Preparation copies only the selected history and
required native metadata into one bounded workspace; it creates no archive.
It selects a single covering history through native bindings and complete-record
prefixes, including the corresponding archived epoch after a supported replacement. Existing managed
bindings remain unchanged; missing bound slots must
validate against them. A healthy existing managed history needs no archive scan.
Retired-format conversion remains the historical importer procedure below.

A recorded pending identity can resume creation of its empty target under the
existing initialization lock. Retries retain the same root and store ID. One
bounded marker candidate is reused when complete and matching; partial or
conflicting metadata and foreign contents remain explicit blockers. Existing
markers are never replaced. Read-only selection does not finish initialization.

Participating current writers use native recovery, event/binding and journal
locks. For a verified absent selected owner in an accessible source, the host
establishes the actual native advisory resources and acquires shared custody
before accepting its empty snapshot. It retains that custody through preparation.
This may create coordination directories and lock files, reported separately as
`source_coordination_mutated`; source payloads remain untouched. A surviving
binding, selected payload, pending transaction, unavailable root, or other unknown
state cannot be reclassified as an empty source to gain this route.

Existing history without qualified coordination still requires actual writer
quiescence before adding `--confirm-no-legacy-writers`. Missing sidecars do not
prove an active writer, and a process listing does not prove quiescence. Native
guards exclude participating writers; they cannot fence unsupported older writers
that ignore them. A successful preparation protects its source observation and
publication only, not subsequent legacy writes. Updated callers use managed
selectors; affected old callers must be stopped or upgraded for a cutover.

Select strict historical reconciliation when the owner's intended decision needs
it, rather than making every independent capture depend on worktree topology:

```bash
ledger context --catalog-root "$ledger_home" --workspace "<workspace-root>" \
  --store-id "<context.store_id>" --reconcile-owner \
  --definition "$definition" --owner-manifest "$owner_manifest"
```

Successful reconciliation or missing-owner preparation with a workspace reports
`source_coverage: checked` for that observed source family. Healthy selected-owner
access and direct-ID archive repair report `not_checked`. Unknown damage,
unresolved recovery, unavailable worktrees,
divergent histories, and an uncovered extension still block that operation.
Missing owner initialization requires the same source evidence; an unavailable
sibling is never assumed empty. Preserve `source_failure` with its exact path
when returned and resolve that condition before retrying the same selection.
Sources are preserved. Failure never switches capture to a repo-local store.

Read-only owner selection is the normal first read, even when maintenance is
allowed. An explicit user prohibition on file/custody maintenance or an enforced
non-writable environment prevents escalating that read to preparation or repair.
An analysis route or a false/omitted corpus-capture flag alone does not prevent
needed preparation. Automatic preparation grants no new semantic
capture, source-payload mutation, provisioning, publication, or permission changes.
Ordinary ensure still only resolves or adopts a registration. Ledger
1.8.0 or newer within major version 1 is required by the owner-access adapter. General
permission errors do not authorize unrelated permission changes. Native
publication, the subsequent owner operation, catalog association and maintenance
have separate outcomes; later failure never authorizes another publication.
Native publication finalizes its preparation work. Write results report the
operation's observed status; no additional check is triggered. See
[explicit storage inspection](storage-maintenance.md#preparation-housekeeping).

## Skill workflow

After bootstrap, inspect the verified workspace:

```bash
ledger context --catalog-root "$ledger_home" --migrate --workspace "<workspace-root>" \
  --owner-manifest "<installed-owner>/migration.json"
```

Do not turn a recognized legacy-source error into a user-maintained repair
checklist. Select the installed owner declarations and pass each as a repeated
`--owner-manifest`; native Ledger never searches a skill installation. It inventories every
available worktree, and selects equal or complete-record-prefix histories. With
authorized migration and actual writer quiescence, perform the procedure as one
operation rather than requesting approval for each routine substep:

```bash
ledger context --catalog-root "$ledger_home" --migrate --workspace "<workspace-root>" \
  --owner-manifest "<installed-owner>/migration.json" --apply --confirm-no-writers
```

Explicit migration requests authorize the supported lossless procedure, not a
claim that writers have stopped. Automatic current-format preparation uses
`--ensure-owner` above; this separately selected historical importer does not
replace it. Read-only migration inspection reports a plan. Never assert quiescence merely
because no process was noticed; old
`--repo` writers are not fenced by the registration lock. Stop or upgrade those
writers before applying. Unavailable worktrees are not automatically pruned.

When Git metadata was removed but an unmanaged source directory survives, select
that existing directory with the same `--workspace` option. Migration then inventories
that one explicit source, without claiming coverage of other lost copies. Broken
or surviving Git metadata cannot trigger this fallback. The source receives no
lock file or new Git metadata; the migration lock lives in the personal home.
The source/Git association is rechecked along with source bytes before publication.
An existing managed root instead requires catalog adoption with its original ID.

On success, retain the returned `context`, resume the original owner operation,
and verify its own returned result. A migration receipt is not evidence that a
previously missed capture occurred. Later ordinary operations use the low-level
resolver; do not scan or migrate on every native call.

## Supported procedure

Installed sibling skills opt in with `migration.json`, separate from passive
native definitions. The schema is `ledger-owner-migration/v1` and declares an
owner-relative definition, retired source names, and an optional owner-relative
Python importer. The definition must declare static monolithic JSONL event slots.
Repository-local manifests never select executable code. Ledger owns location
policy and transport; the trusted owner constructor alone interprets old records.

Learnings, Negative Ledger, and Review Fold current-format histories opt in. Learnings also
imports its recognized retired files through its owner constructor. Unknown
artifacts are preserved but never mislabeled as semantically imported. Other
owners must explicitly opt in; segmented, dynamic, and document-slot migration
remain outside this route. Missing owners and conflicting claims fail closed.

Before registration, the procedure preserves a complete bounded archive of regular
files and symlink spellings, without following external targets. Unowned named
pipes remain in the source; their type and permissions are retained only in the
archive manifest, without opening or recreating a live channel. Named pipes in
owner event slots, retired sources, or native custody archives remain invalid.
It cold-copies
selected event bytes and native definition/binding/revision archives, excluding
native transaction journals, fencing counters, and advisory lock resources from
active custody. Legacy leases and pending transactions require native recovery.
Native binding maintenance is allowed only on the witnessed selected history;
malformed binding is not treated as missing, and unknown failure codes never
trigger rebind. Native operations must validate the entire history. Event bytes
are checked unchanged across binding maintenance.

When native migration returns `owner-import-required`, invoke the selected
trusted owner constructor with the returned sources, context, and definition.
Ledger never executes the importer. The owner preflights IDs and packets, retains
native receipts, and verifies full-record parity and native health. Save its
scoped result and resume the same native command with `--owner-import-receipt
<absolute-result-file>` for each requested owner. The receipt must bind the exact
archived source hashes, target identity, definition closure, and parity result;
a one-slot owner retains its scalar `revision`. A multi-slot owner supplies
`revisions`, an object mapping every declared slot's relative path to its current
native revision, or null when missing, with no additional keys. Each slot is
validated against current native custody. A generic health result alone does not
establish imported-record equivalence. Source/worktree inventories are rechecked
before publication; native validation must pass. The personal
catalog is published last. No source is deleted, no timestamp winner is selected, and no
histories are concatenated. Divergent or additional managed-versus-local history
requires owner reconciliation, not an empty store or checkout fallback.

The bounded scan currently permits 100,000 filesystem entries and 2 GiB of regular
source bytes. Learnings imposes its own lower import bounds. Exceeding a bound is
an explicit blocker, not permission to omit evidence.

## Completion, retry, and failures

Catalog identity and migration completion are separate. An existing root is
usable without a migration receipt. Only explicit migration inspection asks
whether historical recovery is complete. The `ledger-custody-migration/v2`
receipt binds source inventory, installed owner manifests/importers, native
definition closures, store identity, and byte-count/digest witnesses for the
imported destination prefixes. A valid canonical append preserves that evidence;
replacement/truncation of the witnessed prefix requires reconciliation. Native
doctor still validates current custody during explicit migration verification.
Earlier receipts can be requalified by this maintenance without blocking access.

Archives and sources are preserved on failures. An interrupted registered-store
import resumes by native full-record reconciliation, not by trusting a saved
record count. Fresh migration uses the existing pending registration and root
marker to retain one target identity across interruption. A retry verifies that
identity and resumes its native work. Unrecognized staging or orphan directories
remain explicit blockers; they never justify an empty replacement history.

A successful result accounts for supported histories and explicitly marks
unselected artifacts as archived-only. Unknown framing stays blocked until the
owner receives exact source-digest-bound repair controls; use `--framing-controls`
only for such an approved control file. Preserved anonymous fragments do not
become invented records. Global memory admission remains a separate owner action.

## Exact archive repair

An owner read returning `StoreBindingWithoutSlot` may select exact archive
restoration under standing custody authority. Use its verified existing context:

```bash
ledger context --catalog-root "$ledger_home" --store-id "<context.store_id>" \
  --repair-archive --definition "$definition" --owner-manifest "$owner_manifest"
```

Bootstrap Ledger 1.7.0 or newer first. The store ID must select the same existing
cataloged root and binding; this read-repair route makes no live-source coverage
claim. If the verified identity exists only in an old Git registration, ordinary
`--ensure` may adopt that registration without moving history before the repair.
Retry the owner read after restoration. An explicit no-maintenance constraint
forbids both adoption and repair.

A separately selected repair may include a live workspace. Ledger 1.8.0 can
establish native coordination for an absent selected owner there using the same
empty-source route as preparation. Existing history without qualified writer
coordination still requires actual quiescence before adding
`--confirm-no-legacy-writers`; never infer quiescence from an absent process.
An intact owner returns normally without scanning archives. Plain `context --ensure`
and read-only context lookup never restore records.

This route handles only native `StoreBindingWithoutSlot` for one declared static
event slot, with no pending transactions. It verifies retained archive manifests
and bytes, stages the existing native binding/definition/revision custody, and
requires native doctor to validate the archived slot against that unchanged
custody. A selected workspace's local copy, when present, must match. Native
recovery, binding/event, and journal advisory locks exclude competing publication;
lock contention waits for the active writer, never declaring it dead. Publication
creates the absent slot atomically and never replaces an existing path. The
returned `preparation` field retains the native publication and finalization
result, including failures that occur after commit. No extra post-write check runs.

No binding is rebuilt, source record rewritten, retired directory made writable,
or journal removed. Stale/tampered archives, divergent local bytes, existing
corruption, legacy leases, unknown owners/errors, and unresolved transactions
remain explicit failures. General `AccessDenied` is not a repair trigger. This
restores bytes already certified by the selected root's binding. Automatic owner
upgrade selects this repair when appropriate; other missing current-format owner
history uses its locked migration path.

### Retained source under an older archive layout

`UnsupportedLegacyArchiveLayout` is not an empty archive. Preserve its manifest
and source bytes. Do not skip manifest entries, relabel archived-only records as
admitted, or send an unfamiliar manifest through the current archive importer.

For an exact current-format source tree retained in that archive, a selected
owner read or doctor must first establish `StoreBindingWithoutSlot` against the
existing target binding, with no unresolved transactions. Inspect the source
under that same definition and select only the original target and witnessed
source. Ledger 1.7.0 provides the atomic target restriction:

```bash
ledger prepare --definition "$definition" \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --source-root "<exact-retained-source-root>" --restore-bound-history --format json
```

Use existing writer coordination, or add `--confirm-no-legacy-writers` only after
establishing actual source quiescence. After a valid inspection, repeat the same
selection with `--apply` under standing exact-restoration authority. The flag must
remain present: ordinary preparation can initialize an unbound owner, which this
repair must never do. Native binding, payload, definition, revision, and replay
checks govern restoration; an earlier doctor result alone is not the commit
guard. Retry the owner read afterward. This restores already-bound bytes; a
missing unbound owner still needs its owner-aware import or reconciliation route.

## Release gate

Run the owner historical-import and migration test modules with `LEDGER_BIN` set,
including `test_archive_repair.py` and `test_owner_upgrade.py`, plus the Ledger context
suite. Native tests must pass; mocked native results are not custody evidence.
The Learnings native compatibility test covers the earlier local recovery
protocol and its archived definitions alongside new imports and captures.
Test that first capture from empty sources needs no quiescence assertion, that
native append preserves source payloads, and that a healthy owner remains writable
after adding or removing a worktree. A fresh invocation must retrieve the same
record under its original semantic scope after all checkouts are deleted. Keep
strict reconciliation and missing-owner tests for unknown history, divergence,
actual writer contention, and identity changes; readiness is not source coverage. Existing recovered roots
can be cataloged by their unchanged ID/root without running migration. Never
migrate a live recovered store merely to exercise these changes.
