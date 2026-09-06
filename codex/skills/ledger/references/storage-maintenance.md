# Storage maintenance

Read before transaction recovery or a version-dependent storage migration.
The semantic owner selects the operation; current user or standing authority
must authorize its effect. Bootstrap readiness alone authorizes neither.

## Exact transaction recovery

Lease expiry is not authority transfer. Inspect one transaction and require the
exact resource, lock identity, fencing token, owner, and witnessed lease state
before reclaiming:

```bash
ledger recovery inspect \
  --repo <repo> \
  --transaction <dtx-id> \
  --format json

ledger recovery reclaim \
  --repo <repo> \
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

Ledger 1.1 documents an explicit `migrate-segmented` maintenance command; it is
not part of the 1.0.3 baseline. Check the installed native help and capabilities
and inspect the selected definition with `definition check` and
`definition describe` before relying on this surface. Missing support blocks that migration,
not unrelated baseline operations; never emulate the command or silently raise
the minimum version for every consumer.

Only after the owner selects the applicable migration and its effect is
explicitly authorized:

```bash
ledger migrate-segmented \
  --definition <owner-selected-protocol-definition.json> \
  --repo <repo> \
  --format json
```

A newer installed binary is not a request to migrate. Do not change an owner's
definition or store format just to enable this command. Preserve the native
result and verify the resulting store through the selected definition's doctor
and required projections. Migration does not reconcile divergent histories or
grant workflow authority. Never repair a failed migration by hand-editing stores
or metadata; use only the runtime's exact supported maintenance surface.

The [Ledger 1.1.1 runtime documentation](https://github.com/tkersey/skills-zig/blob/ledger-v1.1.1/apps/ledger/README.md)
describes the command and segmented storage. Use the installed version's
supported surface rather than assuming every Ledger 1.x binary provides it.
