# Upgrade existing Ledger and memory use

This upgrade retains existing identities and immutable evidence. It changes how
installed callers select custody and memory layout. Use one coordinated cutover;
installation alone neither imports old history nor migrates notes.

- [Release and writer cutover](#release-and-writer-cutover)
- [Adopt managed histories](#adopt-already-managed-histories-before-initializing-anything)
- [Import unmanaged history](#import-unmanaged-surviving-history-only-when-needed)
- [Keep existing admissions](#keep-existing-admissions-and-select-the-right-memory-version)
- [Preserve historical meaning](#preserve-historical-meaning-across-the-cutover)
- [Rollback](#rollback-without-abandoning-new-history)

| Existing state | Upgrade route | What is retained |
|---|---|---|
| Managed root with a Git `ledger-store.json` registration | First-use ensure automatically imports that registration into the personal catalog | Exact root, store ID, native custody, and old registration |
| Managed root whose Git registration is gone | Register its actual root and marker's existing ID | The same identity and native bytes; no replacement store |
| Unmanaged `.ledger` or recognized retired Learnings files in live worktrees | Explicit owner-aware migration of the Git family | Source copies, bounded archive, original supported records and IDs |
| Surviving unmanaged directory after Git metadata was removed | Explicit migration selecting that directory | The same preservation guarantees for that selected source; no claim about other lost copies |
| Existing notes already in the selected memory version | Keep them in place | Exact envelopes, note IDs, fingerprints, and relationships |
| Existing notes in the other memory version | Native immutable migration for each used extension | Original bytes and IDs in both locations; identical copies skip on retry |

## Release and writer cutover

Release and install the native changes before activating the new definitions and
adapters: Ledger **1.5.0 or later within major version 1**, with
`ledger-artifact-abi/v1`, and memory-note **0.3.0**. Merely merging the native PR
does not update installed executables or a Homebrew formula. In the updated
Ledger skill, verify the selected executable with:

```bash
"$ledger_skill_root/scripts/ensure-ledger" --min-version 1.5.0
memory-note version
```

Add `--install` to the first command when provisioning is authorized. It must
recheck the installed version after upgrading. Run `ledger definition check`
with each selected owner definition before using the changed definitions; a
healthy `doctor` alone does not establish projection compatibility. Ledger 1.4
cannot compile the new Negative definition, including its older projections.

Finish or stop affected old sessions, background admissions, and legacy native
writers before any cold migration. Keep old unmanaged `--repo` writers stopped
afterward: they can still append to their retained local history, which would
diverge from managed custody. A catalog or migration lock cannot fence them.
Start fresh sessions with the updated skills and explicit personal selectors.
For registration-only adoption, native custody does not move, but every caller
still needs to select the preserved identity through the updated resolver.

Before moving evidence, take a coherent backup of the selected personal catalog,
every referenced full native root, and affected extension notes/instructions.
Include custom roots outside the default home and native binding, definition,
revision, and transaction resources. A JSONL export is not a custody backup.

## Adopt already-managed histories before initializing anything

Use the same configured Ledger home as before: absolute `LEDGER_HOME`, otherwise
`${CODEX_HOME:-$HOME/.codex}/ledger`. Changing that home selects another catalog.
`--list-stores` lists only cataloged identities; an empty result is not evidence
that pre-upgrade histories are absent.

Inspect retained Git registrations and known roots first. Older default roots
remain under `<ledger-home>/repos/<store-id>/.ledger-root.json`; custom roots
remain wherever their registration points. Match the marker's original ID and
the actual `.ledger` directory. Do not automatically select `.migrating-*`,
`.initializing-*`, or an orphan from an interrupted publication. These require
inspection of their provenance and completion state.

When a registration survives, the ordinary ensure path adopts it automatically:

```bash
uv run "$ledger_skill_root/scripts/ensure_custody.py" --repo "<workspace-path>"
```

This performs registration-only adoption, not cold migration. It needs no writer
quiescence because native custody stays in place. Strictly read-only tasks use
`ledger_context.py` and cannot perform this catalog update. The explicit
`ledger_context.py --import-registration ... --repo ...` maintenance route remains
available for a specifically selected registration.

When only the managed root survives:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" \
  --register-root "<exact-existing-root>" --store-id "<existing-marker-store-id>"
```

Register each independent root separately. Neither route needs sibling worktree
coverage, rewrites records, rebinds native custody, or requires a migration
receipt. Repeated identical adoption leaves catalog content unchanged. Do not
run `--initialize` or re-import source rows to replace an already-managed store.

After adoption, `--store-id` works with no checkout. An optional explicit
`--attach-workspace` associates a new workspace with the known store. Retain the
returned `native_args` for every owner operation. Read a known full record and
its owner projection to verify the selected identity and history.

## Import unmanaged surviving history only when needed

Inspect the supported source first:

```bash
uv run "$ledger_skill_root/scripts/ensure_custody.py" \
  --migrate --repo "<legacy-workspace-or-surviving-directory>"
```

For a verified Git worktree, migration inventories the complete known family.
Unavailable worktrees and divergent histories remain explicit blockers. If Git
metadata is entirely gone, the explicitly selected existing directory is one
source. Broken Git metadata does not silently reduce a family to one directory.
The plain source receives no migration lock or Git metadata; custody controls
are in the personal home. Source selection and bytes are rechecked before
catalog publication.
Apply holds the personal catalog association lock from its final pre-mutation
identity check through publication. Competing attachments wait and then must
respect the published association. This lock does not fence legacy writers.

After actual writer quiescence and authorized migration, repeat the command with
`--apply --confirm-no-writers`. Supported current Ledger histories and the
Learnings owner's two recognized retired paths use the same archive, native
validation, ID preservation, and retry procedure. Unknown artifacts are
preserved as evidence without being declared semantically imported. See
[historical migration](automatic-migration.md) for bounds, divergence, interrupted
publication, and native recovery. Do not create a new Git repository merely to
make an old directory eligible for recovery.

## Keep existing admissions and select the right memory version

From the intended configuration context, ask the native writer for the layout:

```bash
memory-note path --extension learnings --format json
```

Pin its returned home and version for subsequent operations. The plain-text
`path` default remains compatible with old shell callers; integrations request
JSON explicitly. The envelope and fingerprint formats are unchanged. An
explicit `--memory-version v1` preserves offline access to old notes without
starting Codex. Implicit selection uses Codex's effective configuration, including
its absent/null v1 default. Missing or malformed configuration is an error, not
permission to guess from directories.

Inspect both versions explicitly during this cutover. If notes already live in
the selected v2 root and v1 is empty, leave those notes in place. If retained
admissions need to move, use `memory-note migrate` with explicit home, source
version, and destination version, first with `--dry-run`. Repeat for each used
extension. The [source memory layout guide](../../memory-source-notes/references/source-store-layout.md)
contains the exact commands and instruction-copy procedure.

Upgrade every memory writer using that home. An old sentinel can indicate a
live old writer; resolve it before migration. The new persistent lock marker
intentionally prevents 0.2.0 writers from resuming. Do not remove it to run mixed
writers. Byte conflicts, malformed notes, and destination capacity conflicts
stop before note publication. The native limit remains 10,000 notes per directory
and 1 MiB per note; retaining the source does not reduce the history-byte budget.
Old `show --format raw` added a newline, so redirected copies can conflict with
the original stored bytes. Preserve and inspect both copies; do not normalize
or recapture them to force migration through.

Deploy the tracked extension instructions as regular files beside the selected
notes, using `memory_source_layout.py sync-instructions` with the pinned home
and version. Do not copy or edit compiled memory outputs. No location migration
bulk-admits canonical records or gives old notes new IDs.

## Preserve historical meaning across the cutover

Old Learnings IDs, fingerprints, claims, applicability, and full-record exports
remain readable and searchable. The new capture fingerprint includes scope and
application, so deduplication is not automatic across the old and new fingerprint
domains. Before recapturing an old claim or retrying an uncertain old capture,
use recall and compare its complete claim, application, and scope. Preserve old
hashes and use a supported correction/supersession when the meaning changes.

New Negative capture requires a stable `capture_key`. An old unkeyed call fails
without appending under the new definition. A fresh key does not identify a
possibly successful pre-upgrade operation: inspect its prior receipt or known
canonical record before attempting it again. Within the new protocol, retries
retain the same key, packet, selector, and definition closure.

Catalog adoption preserves historical source scopes in immutable note exports.
Reconciliation can associate a legacy-scoped note through an exact current
canonical export. For Negative status changes, it can also use the immediate
predecessor fingerprint supplied by the native fold, with matching source,
record, and scope. That note is reported as `stale-note`, not current admission
or route authority. Arbitrary older ancestry without a canonical witness stays
unresolved; bare IDs and similar text never join histories across stores.

Verify stored IDs/bytes and known source records, then verify reader visibility
from a fresh Codex session using the selected root. Native storage and protocol
tests do not prove that an installed Codex binary or its compiler consumed a
note, nor that later behavior used it.

## Rollback without abandoning new history

Prefer keeping the new custody resolver and native executables while reverting
the selected policy or memory version. Continue using the same catalog, roots,
and IDs. To return to v1 memory, quiesce admissions and use the new binary's
explicit v2-to-v1 migration, inspect its result, select v1 for both writer and
reader, deploy instructions, and start a fresh session. Source copies remain.

A source-only rollback to the old Git-dependent resolver cannot discover roots
created only in the catalog. It can treat them as unregistered and create a
second identity if initialized. Existing imported Git registrations were
preserved, but that does not make every older caller catalog-aware. Do not use
old initialization as a rollback procedure.

The tested Ledger binary rollback pairs the previous **1.4 runtime and previous
definitions**. That pair reads old and new appended event shapes; the 1.4 runtime
with the new Negative definition fails. This does not qualify arbitrary older
versions or automatic cross-version deduplication. Keep the personal resolver
and stop newer writers if using that pair for an explicit fallback.

An actual memory-note 0.2.0 downgrade needs a separate quiescent cutover after
reverse migration, including reviewed retirement of the recognized persistent
lock markers. The [native upgrade guide](https://github.com/tkersey/skills-zig/blob/95313a7ef025ced7c8ab76ba5412b879cabbd521/apps/memory-note/README.md#upgrade-existing-020-use)
documents that route. Never blindly remove locks or restore an old snapshot over
post-upgrade captures; preserve and reconcile all later evidence first.
