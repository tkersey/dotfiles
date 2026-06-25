# Workspace Resource Claims

## WCL-v1

```yaml
workspace_claim:
  claim_version: WCL-v1
  claim_id:
  workspace_id:
  workspace_sequence:
  plan_id:
  plan_sequence:
  session_id:
  executor:
  item_ids: []
  resources:
    - root:
      mode:
        read |
        write |
        exclusive
  branch:
  branch_epoch:
  base_head:
  claimed_at:
  lease_seconds:
  lease_expires_at:
  heartbeat_at:
  fencing_token:
  state:
    held |
    released |
    stale |
    integrated
```

## Resource grammar

```text
path:<normalized-repository-path>
symbol:<path>#<symbol>
generated:<artifact-name>
schema:<schema-name>
service:<service-name>
git:index
git:branch:<branch-name>
repo:all
```

## Path conflicts

Normalize paths before comparison.

```text
path:a
path:a/b
```

overlap.

```text
path:src/a.zig
symbol:src/a.zig#parse
```

overlap.

Sibling files do not overlap.

## Modes

```text
read/read           compatible
read/write          conflict
write/write         conflict
exclusive/anything  conflict
```

## Fencing

A fencing token is allocated monotonically by the workspace.

Every guarded operation carries:

```text
claim_id
fencing_token
expected_workspace_sequence
expected_plan_sequence
expected_branch_epoch
```

Reclaimed tokens never become valid again.

## Unknown scope

When resource inference is incomplete:

```text
repo:all / exclusive
```

The system may later narrow the resource set after explicit inspection, but it
must not grant optimistic concurrency.
