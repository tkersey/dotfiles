# Storage maintenance

Read before transaction recovery or a version-dependent storage migration.
The semantic owner selects the operation; current user or standing authority
must authorize its effect. Bootstrap readiness alone authorizes neither.
Routine opted-in owner preparation follows
[automatic owner upgrade](automatic-migration.md#automatic-owner-upgrade), whose
standing authority requires no separate approval; this guide governs other
selected recovery and format changes.

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

## Resource pressure and lifecycle maintenance

Read [storage-lifecycle.md](storage-lifecycle.md) for lifecycle design and the
current capability gate. The baseline recovery surface above does not provide
general garbage collection. Do not infer such support from `doctor`, a newer
version number, or a proposed command in an implementation specification.

An inventory failure is not permission to raise bounds, delete old logs, rewrite
bindings, or initialize replacement history. Stop repeating unchanged failing
preparation, retain its exact selected context and diagnostics, and report the
blocked original operation. Healthy existing access remains independent of
historical import completeness; never add broad scans to every projection.

Selected-owner preparation and full historical preservation have different
scopes. The native replacement must certify the selected definition's dependency
closure without recopying unrelated enclosing trees, while the explicit broad
historical route preserves its promised unselected material. Until that release
is installed, do not claim the existing Python inventory has this narrower scope.

A storage cleanup is not proof of restored history. Completion requires the
original owner operation and its expected records, stable store identity, native
integrity checks, and retry qualification. Logical file sizes are not measured
physical blocks recovered. Report maintenance degradation separately from a
semantic transaction that already committed.
