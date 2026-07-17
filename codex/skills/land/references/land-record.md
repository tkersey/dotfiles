# Land Record

Emit one terminal record after live merged-state readback and cleanup attempts.

```yaml
land_record:
  record_version: LAND-v1

  target:
    repository:
    pr_number:
    pr_url:
    base_ref:
    preflight_base_oid:
    head_repository:
    head_ref:
    expected_head_oid:

  decision:
    mode: merge-now | queue-and-wait | auto-merge-and-wait | cleanup-only | blocked
    merge_method: merge | squash | rebase | repo-policy | none
    reason:

  gates:
    target_identity: pass | fail
    review_inventory: pass | fail
    review_decision: pass | fail
    required_checks: pass | fail
    conflict_free: pass | fail
    branch_freshness: pass | fail
    repository_policy: pass | fail
    exact_head: pass | fail

  action:
    command:
    result: merged | queued | auto-enabled | already-merged | blocked | failed
    expected_head_oid:
    admin_override: false

  postcondition:
    state: MERGED | OPEN | CLOSED | unknown
    merged_at:
    merge_commit_oid:
    observed_head_oid:
    head_oid_match: yes | no | unknown
    result: pass | fail

  cleanup:
    associated_worktrees:
      requested: yes | no
      result: cleaned | partial | preserved | not-requested | blocked
      items:
        - path:
          kind: primary | linked | stale
          expected_head_oid:
          observed_head_oid:
          dirty: yes | no | unknown
          locked: yes | no | unknown
          action: switched-to-base | removed | pruned | preserved | not-applicable
          result: pass | fail | blocked
          reason:
    remote_branch:
      requested: yes | no
      observed_oid:
      action: deleted | already-absent | preserved | not-requested | blocked
      reason:
    local_branch:
      requested: yes | no
      observed_oid:
      action: deleted | already-absent | preserved | not-requested | blocked
      reason:
    overall: complete | degraded | not-requested | blocked

  blocker:
    gate:
    reason:
    next_safe_action:
```

## Semantics

- `action.result: queued` and `action.result: auto-enabled` are nonterminal. Do
  not emit the final LAND-v1 until postcondition monitoring reaches `MERGED` or a
  terminal blocker.
- `action.result: merged` is valid only when the live postcondition passes. A
  successful mutation command alone is insufficient.
- `cleanup.overall: degraded` means the PR merged but at least one requested
  branch or worktree cleanup was preserved or blocked. A cleanup blocker does not
  rewrite a successful merge as failed.
- Worktree items are reported independently. Do not collapse a dirty or locked
  worktree into a generic branch-deletion failure.
- `already-absent` is a successful no-op only when requested cleanup proves the
  exact local or remote branch ref was absent before mutation. It must not imply
  that this landing attempt deleted the ref.
- `admin_override` must remain false unless the user explicitly authorized a
  specific bypass in the current landing attempt.
- Copied SHIP-v1 fields may be referenced in surrounding evidence, but LAND-v1
  target, gate, action, and postcondition fields come from fresh live state.
