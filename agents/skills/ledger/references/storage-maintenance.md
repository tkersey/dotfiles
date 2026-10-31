# Storage maintenance

Read before transaction recovery or a version-dependent storage migration.
The semantic owner selects the operation; current user or standing authority
must authorize its effect. Bootstrap readiness alone authorizes neither.
Routine opted-in owner preparation follows
[automatic owner upgrade](automatic-migration.md#automatic-owner-upgrade), whose
standing authority requires no separate approval; this guide governs other
selected recovery and format changes.

## Preparation housekeeping

Ledger 1.6 provides `prepare` for selected static monolithic history and `maintain`
for preparation-owned working files. Both inspect by default. The adapter uses
native preparation under existing opted-in owner authority; it never copies a
second archive or substitutes a Python algorithm after native failure. Native
publication transfers its sole staged payload into canonical history, so it leaves
no duplicate preparation payload. Maintenance preserves native audit journals
under their existing lifetime rules and reports unresolved work.

```bash
ledger maintain --store-root <context.store_root> --store-id <context.store_id> --format json
```

Add `--apply` only within authorized custody maintenance. Native state determines
release; unresolved publication, ambiguous ownership and exhausted bounds retain
the affected work. Canonical history, archives, caches, foreign files and persistent
coordination resources are outside cleanup. Logical reclaimed bytes are not a
claim about physical disk blocks. Native preparation and maintenance report their
own outcome separately from any subsequent owner operation.

After installing the qualified Homebrew runtime, `./install --ledger-maintenance`
installs the user LaunchAgent `com.tkersey.ledger.maintenance`. Its default hourly
sweep considers at most 128 cataloged stores, with per-store limits of 256 MiB
working bytes, 512 files and 2 GiB read bytes; pressure defaults to less than 5 GiB
free. `maintenance.json` owns these values. The installed LaunchAgent selects its
configuration and cadence; cadence changes require reinstalling the agent.
The wrapper retains one bounded last-run record and reports health through CLI
results. Cleanup runs quietly. Inspect and explicit no-maintenance execution
persist no health updates.

Verify actual scheduled execution on the target host; successful installation
alone does not prove it. Normal invocation reports stale or missing last-run
evidence. A manual sweep cannot certify scheduled execution, and recorded
execution does not establish that launchd remains enabled. Inspect with
`scripts/install_maintenance.py` without `--apply`;
use `scripts/maintain_custody.py` without `--apply` for a nonmutating sweep.

## Exact transaction recovery

Lease expiry is not authority transfer. Inspect one transaction and require the
exact resource, lock identity, fencing token, owner, and witnessed lease state
before reclaiming:

```bash
ledger recovery inspect \
  --store-root <context.store_root> --store-id <context.store_id> \
  --transaction <dtx-id> \
  --format json

ledger recovery reclaim \
  --store-root <context.store_root> --store-id <context.store_id> \
  --transaction <dtx-id> \
  --resource <path> \
  --lock-id <dlk-id> \
  --fencing-token <u64> \
  --format json
```

For an original legacy lease only, add `--confirm-no-legacy-writers` with actual
operator authority and an inspectable basis for that assertion. Do not add it
for an interrupted current recovery. There is no broad reclaim or repair mode.

## Version-dependent segmented migration

Ledger documents an explicit `migrate-segmented` maintenance command. Check the
installed native help and capabilities
and inspect the selected definition with `definition check` and
`definition describe` before relying on this surface. Missing support blocks that migration,
not unrelated baseline operations; never emulate the command or silently raise
the minimum version for every consumer.

Only after the owner selects the applicable migration and its effect is
explicitly authorized:

```bash
ledger migrate-segmented \
  --definition <owner-selected-protocol-definition.json> \
  --store-root <context.store_root> --store-id <context.store_id> \
  --format json
```

A newer installed binary is not a request to migrate. Do not change an owner's
definition or store format just to enable this command. Preserve the native
result and verify the resulting store through the selected definition's doctor
and required projections. Migration does not reconcile divergent histories or
grant workflow authority. Never repair a failed migration by hand-editing stores
or metadata; use only the runtime's exact supported maintenance surface.

Use the installed version's supported surface. Explicit legacy maintenance may
instead select an unmanaged `--repo` root when the owner requires it. It is
never a retry path after a managed context or custody error.
