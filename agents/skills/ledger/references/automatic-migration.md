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
and exact restoration. Perform this preparation automatically before its first
projection or capture, including analysis and review. Do not request confirmation,
an approval token, or separate migration authorization; permission to capture new
semantic records does not gate it. The installed `migration.json` is the owner's
protocol opt-in, not a per-run question for the user.

Resolve the owner through:

```bash
ledger context --catalog-root "$ledger_home" --workspace "<workspace-root>" \
  --ensure-owner --definition "<installed-owner-definition>" \
  --owner-manifest "<installed-owner>/migration.json"
```

Reuse the returned `native_args` for the original operation. The native host command keeps an
existing store's identity, adopts valid registrations, and initializes a private
managed root only when evidence establishes a genuinely new owner. It discovers
finite source contexts from the catalog, workspace and existing archive manifests,
then invokes native `prepare`. Preparation copies only the selected history and
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
locks. The native engine validates protected history before publication. Empty
source roots without the required coordination need actual writer quiescence;
only then add `--confirm-no-legacy-writers` to `--ensure-owner`. The native host command never
infers quiescence from a missing process, infers abandoned ownership from lock
age, or reclaims a legacy lease. Unknown damage, pending recovery, unavailable worktree
coverage, divergent histories, or a local extension beyond an existing managed
log remain explicit reconciliation failures. Sources are preserved. Failure never
switches capture back to a repo-local store. Updated callers use managed selectors;
old callers must also be upgraded before they can resume new local writes.

Only an explicit user prohibition on file/custody maintenance or an enforced
non-writable environment selects `--read-only` instead of `--ensure-owner`.
An analysis route or a false/omitted corpus-capture flag alone does not select it.
This mode creates no catalog, custody, or records and reports when preparation is
unavailable under that constraint. Automatic preparation grants no new semantic
capture, source mutation, provisioning, publication, or permission changes.
Ordinary ensure still only resolves or adopts a registration. Ledger
1.6.0 or newer within major version 1 is required by this adapter. General
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
a generic health result alone does not establish imported-record equivalence. Source/worktree inventories are rechecked
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

Automatic owner preparation includes exact archive restoration. A caller selecting
that same repair directly uses `ledger context --catalog-root "$ledger_home" --repair-archive
--definition <installed-owner-definition> --owner-manifest <installed-owner>/migration.json`
with the normal workspace or store ID.
Bootstrap Ledger 1.6.0 or newer within major version 1 first. When a supplied live
workspace lacks qualified writer coordination, actually quiesce its writers and
add `--confirm-no-legacy-writers`; never infer quiescence from an absent process.
An intact owner store
returns normally without scanning archives. Ordinary ensure and read-only context
lookup never restore records.

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

## Release gate

Run the owner historical-import and migration test modules with `LEDGER_BIN` set,
including `test_archive_repair.py` and `test_owner_upgrade.py`, plus the Ledger context
suite. Native tests must pass; mocked native results are not custody evidence.
The Learnings native compatibility test covers the earlier local recovery
protocol and its archived definitions alongside new imports and captures.
Test that a native append preserves the witnessed source snapshot, that normal
access ignores a missing historical worktree/receipt, and that direct native
projection still works after all checkouts are deleted. Existing recovered roots
can be cataloged by their unchanged ID/root without running migration. Never
migrate a live recovered store merely to exercise these changes.
