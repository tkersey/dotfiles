# Ledger canonical custody

Read this guide only for selected canonical storage/context or maintenance work,
before its first decision or effect. The entrypoint owns bootstrap, authority,
and definition-relative result semantics; this remains Ledger-owned policy.

## Storage-context ownership

This skill, its [context reference](storage-context.md), and
[scripts/ledger_context.py](../scripts/ledger_context.py) are the single source of
truth for where Ledger-managed evidence lives. Do not duplicate physical roots,
lookup rules, registration, or migration policy in `AGENTS.md` or consumers.
Owners still declare logical slot names and semantic storage scope.

Repository-lifetime Learnings and Negative Ledger histories use one managed
custody root for a Git repository/worktree family. A worktree is evidence
provenance, not the owner of an independent history. Other owners opt into this
scope explicitly; do not silently relocate worktree- or session-specific data.
Pure validation/materialization needs neither a workspace nor a managed store.

For a canonical operation, resolve the verified workspace:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" --repo "<workspace-root>"
```

Retain the returned `workspace_root`, `repository_id`, `store_id`, `store_root`,
and `native_args`. For normal durable operations, pass the returned selector:

```bash
ledger doctor --definition "$definition" \
  --store-root "<context.store_root>" --store-id "<context.store_id>" --format json
```

`transact`, `project`, segmented migration, and exact recovery use the same
selector. Resolve again after a workspace change; the native CLI rechecks the
root marker on each operation. Never replace a failed managed selector with
`--repo`, another checkout, a symlink, or an empty store.

Normal context resolution is read-only. Before an authorized first capture,
stop or upgrade writers that could still use legacy `--repo` custody. Fresh
initialization requires `--initialize --confirm-no-writers`; the flag is an
operator's quiescence assertion, not a lock on old executables. The helper checks
all registered worktrees for legacy history twice before publishing a fresh
registration. Existing registration always wins over changed environment defaults.
A missing established root is a continuity error, not first use. For supported
legacy history, prefer the automated procedure below over manual cold-adoption
choreography. Do not initialize simply to make a recall succeed.

Use workspace/branch/path and immutable artifact facts as provenance. New
repository-scoped records should carry the returned stable `repository_id`
where their owner schema supports it. Do not substitute the custody directory
for the code workspace, rewrite old provenance, or broaden applicability because
history is shared. Definition-relative source locators are resolved through this
context, not by assuming they name files beneath a disposable checkout.

## Ensure usable custody

At the first canonical use of this integration for a repository family, or when
unregistered custody, unaccounted legacy sources, or interrupted migration is
encountered, read [automatic-migration.md](automatic-migration.md) and
inspect with `scripts/ensure_custody.py --repo "<workspace-root>"` through `uv run`.
Do this even for a pre-existing registration that has not been qualified by the
migration helper: registration alone is not evidence of historical recovery.
Cache a verified result for the unchanged context during the session; subsequent
native operations use the normal resolver, not repeated migration scans.

For an authorized migration, the helper's `--apply --confirm-no-writers` bundles
supported discovery, source selection, cold transport, native binding maintenance,
owner historical import, verification, and final registration. Do not ask the user
to perform each routine substep or stop at archiving identifiable Learnings.
The quiescence assertion must be established, never inferred from a process scan.
Read-only recall produces a plan, not mutation. Divergent histories, unavailable
worktrees, unknown damage, or missing authority remain precise blockers.

Retain the returned context and receipt, then resume and verify the original
owner operation. Report imported history separately from archived-only artifacts.
Do not delete sources, silently rewrite provenance, or bulk-admit recovered rows
to global memory. Native definitions remain passive; installed owners opt into
migration through separate declarations, not repository-provided executable hooks.

## Storage custody and recovery

All event bytes and required binding/definition/revision custody stay together
under the selected root. Normal reads fail closed for unbound existing stores.
A separately authorized `bind-existing` operation validates an entire existing
current-format store once. A separately authorized `rebind-existing` validates
an authoritative replacement and changes only stale binding metadata.
Neither operation chooses between divergent histories or blesses an unknown
replacement. Diagnose missing binding separately from malformed/stale custody;
`InvalidStoreBinding` alone is not proof that initial binding is appropriate.

Normal writes use owner-selected `ledger transact` operations. Never hand-edit,
compact, reinterpret, or skip records. The context reference and automated
migration reference permit only their explicit cold transport; neither is an
alternate semantic reader or writer. Fail closed on unknown closure, ABI,
operator, binding, integrity, replay, projection, or recovery state.

Lease expiry does not transfer authority. Recovery is explicitly authorized and
bound to one transaction's resource, lock identity, fencing token, owner, and
witnessed lease state. Read [storage-maintenance.md](storage-maintenance.md)
before recovery or version-dependent migration. No broad reclaim/repair mode.

