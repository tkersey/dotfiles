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

Review-Closure Abstraction Ladder:
- receipts: structured=N, root_equivalent_structured=N, missing=N, prose_only=N
- rungs_selected: complexity-mitigator=N, simplify-isomorphic=N, reduce=N, universalist=N, fixed-point-driver=N, accretive-implementer=N
- no_direct_address_to_patch: yes|no
- selected_routes:
- blocked_by_route_selector:

Cluster normalization:
- checkpoints_triggered:
- checkpoints_closed:
- checkpoints_open:
- clusters:
  - cluster_id:
    selected_normal_form_route:
    required_skill:
    status:

Surface delta:
- production_insertions:
- production_deletions:
- production_net:
- test_insertions:
- test_deletions:
- test_net:
- duplicate_or_shadow_surfaces_retired:
- surface_delta_call:

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

Do not use `resolved` when validation is blocked, review streak is under three, PR sweep is incomplete for a PR-backed branch, actionable comments remain, a mutation-capable item lacks a structured receipt, a cluster checkpoint is open, or surface delta is `larger-without-warrant`.
