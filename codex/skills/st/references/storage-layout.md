# `.ledger/st/` Storage Layout

```text
.ledger/
  st/
    workspace.jsonl
    plans/
      <plan-id>/
        plan.jsonl
        intake/
        policy/
    proof/
      <plan-id>/
    runtime/
      claims.jsonl
      branch-state.json
      sessions/
      views/
    worktrees/
    changesets/
    integration/
      queue.jsonl
      receipts/
      scratch/
    transactions/
    locks/
    migration/
```

## Authority split

```text
workspace.jsonl
  plan registry, cross-plan dependencies, workspace policy, branch state refs,
  global sequence, schema/version lineage

plans/<plan-id>/plan.jsonl
  complete plan graph and its existing `$st` feature set

runtime/
  ephemeral claims, leases, sessions, views, branch epochs

proof/
  proof logs and receipts grouped by plan

changesets/
  sealed worker output

integration/
  serialized target-branch application

transactions/
  prepare/commit/recovery records

locks/
  short-lived lock metadata and fencing counters
```

## External worktrees

Actual detached Git worktrees should not be nested inside the primary checkout.

Store only worktree metadata under:

```text
.ledger/st/worktrees/<claim-id>.json
```

The metadata records the externally located worktree path, creation head, branch
epoch, claim, and cleanup state.

## Path invariants

- Every canonical path is normalized relative to repository root.
- Symlink components are rejected for workspace-controlled storage.
- `..` traversal is rejected.
- Runtime references to external worktrees must be absolute and separately
  validated.
- No new durable artifact is written beneath `.step/`.
