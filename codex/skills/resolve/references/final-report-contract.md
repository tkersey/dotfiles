# Resolve Final Report Contract

Final report must end with `Resolve Bottom Line`.

## Shape

```text
Resolve:
- status: resolved | blocked | partial
- resolve_run_id:
- branch:
- final_commit:
- pushed_to:
- PR:

Review closure:
- backend_class:
- base_ref:
- base_sha:
- head_sha:
- target_fingerprint:
- clean_review_streak:
- review_receipts:

Validation:
- commands_passed:
- commands_blocked_or_not_available:
- validation_mode: full | partial | manual-only | blocked

Adjudication:
- review_items: address=N, delete-collapse-canonicalize=N, validate-only=N, resolve-thread-only=N, do-not-address=N, blocked=N
- pr_items: address=N, delete-collapse-canonicalize=N, validate-only=N, resolve-thread-only=N, do-not-address=N, blocked=N

Implementation:
- fixed_point_runs:
- implementation_handoffs:
- accretive_implementer_routes:
- surface_delta_calls:
- ablation_statuses:

PR sweep:
- inventory_status: complete | incomplete | no_pr | blocked
- unresolved_actionable_comments:

Parallelism:
- sidecars_used:
- stale_or_rejected_results:

Resolve Bottom Line:
- status:
- strongest proof:
- open blocker:
- exact next action:
```

## Status rules

- `resolved`: all completion criteria passed.
- `blocked`: the skill stopped before completion due to explicit blocker.
- `partial`: only when some safe work completed but final completion criteria did not pass.

Do not use `resolved` when validation is blocked, review streak is under three, PR sweep is incomplete for a PR-backed branch, or actionable comments remain.
