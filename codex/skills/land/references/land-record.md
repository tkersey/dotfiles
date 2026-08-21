# Land Record

Emit one terminal record after review reconciliation, live merged-state readback,
and cleanup attempts.

```yaml
land_record:
  record_version: LAND-v2

  target:
    repository:
    pr_number:
    pr_url:
    base_ref:
    preflight_base_oid:
    head_repository:
    head_ref:
    expected_head_oid:

  epochs:
    - head_oid:
      supersedes_head_oid:
      reason: initial | review-repair | authorized-branch-update
      result: superseded | admitted | merged | obstructed

  review_reconciliation:
    initial_unresolved_thread_ids: []
    records:
      - thread_id:
        concern_ref:
        observed_head_oid:
        resolved_head_oid:
        law_authority: entailed | strengthening | preference |
          new-requirement | underdetermined
        current_applicability: still-present | transformed-applicable |
          already-excluded | not-comparable | unknown
        disposition: fixed-and-evidenced |
          already-satisfied-and-evidenced | obsolete-and-evidenced |
          reviewer-withdrawn | nonblocking-by-authority
        evidence_refs: []
        resolution_readback: true | false
    unresolved_after: []
    result: complete | not-needed | obstructed

  decision:
    mode: reconcile-reviews | rebind-successor-head | merge-now |
      queue-and-wait | auto-merge-and-wait | cleanup-only | obstructed |
      complete
    workflow_status: continue | ready | obstructed | terminal
    merge_admission: ready | not-ready | not-applicable
    merge_method: merge | squash | rebase | none
    reason:

  gates:
    target_identity: pass | fail | not-applicable
    pr_state: pass | fail | not-applicable
    review_inventory: pass | fail | not-applicable
    review_reconciliation: pass | fail | not-applicable
    review_decision: pass | fail | not-applicable
    required_checks: pass | fail | not-applicable
    conflict_free: pass | fail | not-applicable
    branch_freshness: pass | fail | not-applicable
    repository_policy: pass | fail | not-applicable
    exact_head: pass | fail | not-applicable

  action:
    command:
    result: merged | queued | auto-enabled | already-merged |
      obstructed | failed
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
      result: cleaned | partial | preserved | not-requested | obstructed
      items:
        - path:
          kind: primary | linked | stale
          expected_head_oid:
          observed_head_oid:
          dirty: yes | no | unknown
          locked: yes | no | unknown
          action: switched-to-base | removed | pruned | preserved |
            not-applicable
          result: pass | fail | obstructed
          reason:
    remote_branch:
      requested: yes | no
      observed_oid:
      action: deleted | already-absent | preserved | not-requested |
        obstructed
      reason:
    local_branch:
      requested: yes | no
      observed_oid:
      action: deleted | already-absent | preserved | not-requested |
        obstructed
      reason:
    overall: complete | degraded | not-requested | obstructed

  obstructions:
    - code:
      gate:
      evidence_refs: []
      reason:
      next_safe_action:
```

## Semantics

- `LAND-v2` is terminal. Nonterminal preflight returns
  `LAND-PREFLIGHT-v2` with `verdict: continue`; do not emit a final record while
  review reconciliation or queue monitoring can still progress.
- Every thread resolved by this landing appears exactly once in
  `review_reconciliation.records`. Bare thread IDs, aggregate counts, and
  `isOutdated` are not disposition evidence.
- `fixed-and-evidenced` requires a successor head. A current substantive concern
  cannot be reported fixed at the same head on which it was observed.
- `review_reconciliation.result: complete` requires
  `unresolved_after: []`, complete current-head evidence for every record, and
  successful live resolution readback.
- A new head appends a new epoch and supersedes the old epoch. Evidence from a
  superseded head cannot establish current merge admission.
- `action.result: queued` and `action.result: auto-enabled` are nonterminal. Do
  not emit final `LAND-v2` until monitoring reaches `MERGED` or an exact terminal
  obstruction.
- `action.result: merged` is valid only when the live postcondition passes. A
  successful mutation command alone is insufficient.
- `cleanup.overall: degraded` means the PR merged but at least one requested
  cleanup surface was preserved or obstructed. Cleanup does not rewrite a
  successful merge as failed.
- Worktree, remote-ref, and local-ref outcomes are independent.
- `already-absent` is a successful no-op only after proving exact ref absence. It
  never implies that this landing deleted the ref.
- `admin_override` is always false. Administrator bypass is outside ordinary
  `$land`.
- `obstructions` is plural and lossless. Do not collapse independent review,
  admission, postcondition, or cleanup failures into one generic blocker.
