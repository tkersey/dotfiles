# Ensure usable custody

Use `scripts/ensure_custody.py` when repository custody is unregistered, supported
legacy sources have not been accounted for, or a prior migration was interrupted.
The existing `ledger_context.py` remains a read-only resolver during normal use.
Both helpers belong to `$ledger`; only the original context helper defines the
physical storage home, root identity, and Git-family registration policy.

## Skill workflow

After bootstrap, inspect the verified workspace:

```bash
uv run "$ledger_skill_root/scripts/ensure_custody.py" --repo "<workspace-root>"
```

Do not turn a recognized legacy-source error into a user-maintained repair
checklist. The helper discovers installed owner declarations, inventories every
available worktree, and selects equal or complete-record-prefix histories. With
authorized migration and actual writer quiescence, perform the procedure as one
operation rather than requesting approval for each routine substep:

```bash
uv run "$ledger_skill_root/scripts/ensure_custody.py" --repo "<workspace-root>" \
  --apply --confirm-no-writers
```

Explicit migration requests authorize the supported lossless procedure, not a
claim that writers have stopped. For an otherwise authorized capture, use the
same procedure only when the enclosing task grants custody initialization or
migration. Read-only recall stays read-only: report the plan and precise missing
authority. Never assert quiescence merely because no process was noticed; old
`--repo` writers are not fenced by the registration lock. Stop or upgrade those
writers before applying. Unavailable worktrees are not automatically pruned.

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
before publication; staged and final native doctors must pass. Registration is
published last. No source is deleted, no timestamp winner is selected, and no
histories are concatenated. Divergent or additional managed-versus-local history
requires owner reconciliation, not an empty store or checkout fallback.

The bounded scan currently permits 100,000 filesystem entries and 2 GiB of regular
source bytes. Learnings imposes its own lower import bounds. Exceeding a bound is
an explicit blocker, not permission to omit evidence.

## Completion, retry, and failures

Registration and migration completion are separate. An existing registration
without a verified migration receipt is inspected, not declared complete. The
receipt binds the source inventory, installed owner manifests/importers, native
definition closures, and destination event digests. Unchanged verified input and
destination state returns without mutation; changed destination bytes invalidate
the shortcut and require reconciliation. Ordinary canonical appends do not change
the root identity.

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

Merge the owner historical-import change before this orchestration change. Run
both new test modules with `LEDGER_BIN` set, plus the existing Ledger context
suite. Native tests must pass; mocked native results are not custody evidence.
The Learnings native compatibility test covers the earlier local recovery
protocol and its archived definitions alongside new imports and captures.
Qualify an existing recovered store with read-only doctor and full-record
projections. Normal context resolution continues to use its existing
registration, including stores adopted by the earlier scoped helper. Never
migrate an already-recovered live store merely to exercise these changes.
