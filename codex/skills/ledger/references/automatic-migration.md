# Explicit historical migration

Use `scripts/ensure_custody.py --migrate` only for selected legacy inspection,
historical import, or interrupted migration. Without `--migrate`, the helper
only resolves the personal catalog; existing custody needs no migration receipt
or complete worktree inventory. Both helpers belong to `$ledger`; the context
helper owns storage home, stable root identity, and catalog associations.
For a coordinated upgrade of existing installations, start with
[the upgrade guide](personal-store-upgrade.md); already-managed roots normally
need catalog adoption rather than historical migration.

## Skill workflow

After bootstrap, inspect the verified workspace:

```bash
uv run "$ledger_skill_root/scripts/ensure_custody.py" --migrate --repo "<workspace-root>"
```

Do not turn a recognized legacy-source error into a user-maintained repair
checklist. The helper discovers installed owner declarations, inventories every
available worktree, and selects equal or complete-record-prefix histories. With
authorized migration and actual writer quiescence, perform the procedure as one
operation rather than requesting approval for each routine substep:

```bash
uv run "$ledger_skill_root/scripts/ensure_custody.py" --migrate --repo "<workspace-root>" \
  --apply --confirm-no-writers
```

Explicit migration requests authorize the supported lossless procedure, not a
claim that writers have stopped. For an otherwise authorized capture, use the
same procedure only when the enclosing task grants custody initialization or
migration. Ordinary recall uses the personal catalog without selecting migration.
Read-only migration inspection reports a plan. Never assert quiescence merely
because no process was noticed; old
`--repo` writers are not fenced by the registration lock. Stop or upgrade those
writers before applying. Unavailable worktrees are not automatically pruned.

When Git metadata was removed but an unmanaged source directory survives, select
that existing directory with the same `--repo` option. Migration then inventories
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

Learnings and Negative Ledger current-format histories opt in. Learnings also
imports its recognized retired files through its owner constructor. Unknown
artifacts are preserved but never mislabeled as semantically imported. Other
owners must explicitly opt in; segmented, dynamic, and document-slot migration
remain outside this route. Missing owners and conflicting claims fail closed.

Before registration, the procedure preserves a complete bounded archive of regular
files and symlink spellings, without following external targets. It cold-copies
selected event bytes and native definition/binding/revision archives, excluding
native transaction journals, fencing counters, and advisory lock resources from
active custody. Legacy leases and pending transactions require native recovery.
Native binding maintenance is allowed only on the witnessed selected history;
malformed binding is not treated as missing, and unknown failure codes never
trigger rebind. Native operations must validate the entire history. Event bytes
are checked unchanged across binding maintenance.

Retired imports preflight IDs and packets, retain native receipts, then verify
full-record parity and native health. Source/worktree inventories are rechecked
before publication; staged and final native doctors must pass. The personal
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
record count. Interrupted fresh publication can leave an unregistered staging or
final directory: it remains inspection evidence and is never automatically chosen
as an authoritative root. Repeating the safe procedure may stage a new directory;
orphan cleanup is a separate authorized action.

A successful result accounts for supported histories and explicitly marks
unselected artifacts as archived-only. Unknown framing stays blocked until the
owner receives exact source-digest-bound repair controls; use `--framing-controls`
only for such an approved control file. Preserved anonymous fragments do not
become invented records. Global memory admission remains a separate owner action.

## Release gate

Run the owner historical-import and migration test modules with `LEDGER_BIN` set,
plus the Ledger context
suite. Native tests must pass; mocked native results are not custody evidence.
The Learnings native compatibility test covers the earlier local recovery
protocol and its archived definitions alongside new imports and captures.
Test that a native append preserves the witnessed source snapshot, that normal
access ignores a missing historical worktree/receipt, and that direct native
projection still works after all checkouts are deleted. Existing recovered roots
can be cataloged by their unchanged ID/root without running migration. Never
migrate a live recovered store merely to exercise these changes.
