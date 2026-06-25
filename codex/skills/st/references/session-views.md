# Session Views

Projection is session state, not plan state.

```yaml
session_view:
  view_version: SVW-v1
  session_id:
  executor:
  workspace_id:
  plan_id:
  claim_id:
  fencing_token:
  workspace_sequence:
  plan_sequence:
  branch_epoch:
  selected_item_ids: []
  projection_digest:
  projection_target:
    codex |
    opencode
  updated_at:
```

## Rules

- One session is bound to one current plan at a time.
- A session may switch plans only after releasing its old claim and creating a
  new binding event.
- `prime`, `reconcile-codex`, and `assert-projection` operate on the caller's
  view.
- No command may infer a session from process ID alone.
- View state is always local-excluded.
- A stale view cannot authorize mutation.
