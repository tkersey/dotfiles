# Actuating Delivery Handoff

## Purpose

A run is not finished just because local proof passed. If the user or accepted
spec asked for PR output, `$actuating` must hand the proved, integrated branch to
`$ship` or explain why delivery is blocked.

The failure this prevents:

```text
proof passed
-> workflow stops
-> no PR even though PR output was requested
```

The required chain is:

```text
proof complete
-> integrated target branch is current
-> ADD-v1 delivery decision
-> $ship receives that branch state
-> ship result or clear delivery blocker
```

## ADD-v1

```yaml
actuation_delivery_decision:
  decision_version: ADD-v1
  verdict: handoff_to_ship | shipping_not_requested | blocked
  run_id:
  plan_id:
  target_branch:
  target_head:
  branch_epoch:
  proof_complete_receipt:
    present: yes | no
    current: yes | no | unknown
    ref:
  integration:
    queue_quiescent: yes | no | unknown
    receipts: []
  integrated_change_set_receipts: []
  cross_plan_dependency_status: clear | blocked | unknown
  pr_intent:
    present: yes | no
    source: user | actuation_run | source_handoff | none
    requested_mode: ready | draft | update-existing | promote-draft | none
  current_pr_state:
    exists: yes | no | unknown
    url:
    draft: yes | no | unknown
  do_not_ship_before: []
  blocked_reasons: []
  ship_handoff:
    next_owner: $ship
    ship_input:
      branch:
      base_branch:
      head_sha:
      existing_pr:
      validation:
      task_state:
      proof_summary:
      user_requested_pr_mode:
      repo_policy_pr_mode:
      actuation:
        run_id:
        plan_id:
        branch_epoch:
        integrated_change_set_receipts: []
        proof_complete_receipt:
        cross_plan_dependency_status:
```

## Handoff rule

Use `handoff_to_ship` only when all hold:

```text
proof-complete receipt present and current
integration queue is quiet for this plan
at least one integrated change-set receipt, or an explicit no-change integrated receipt
target branch/head/epoch are known
cross-plan dependency status is clear
PR delivery intent is present
no do_not_ship_before blocker exists
```

Do not pass worker worktrees, unintegrated patches, claim-local trees, or stale
branch proof to `$ship`.

## Intent sources

PR delivery intent exists when the user asked to open/update/promote a PR, the
accepted source says plan-to-PR, the actuation run requested ready/draft/update,
or a source handoff says `$ship` is next.

No PR intent means `shipping_not_requested`, not `$ship`.

## Blocked delivery

`blocked` is required when proof is missing/stale, integration is not quiet,
change-set receipts are missing for a changeful run, cross-plan status is not
clear, target branch/head/epoch are unknown, or `do_not_ship_before` is nonempty.

## Validator

```bash
uv run python codex/skills/actuating/tools/actuation_delivery_gate.py \
  decide \
  --context .ledger/actuating/<run-id>/delivery-context.json \
  --out .ledger/actuating/<run-id>/delivery-decision.json

uv run python codex/skills/actuating/tools/actuation_delivery_gate.py \
  check \
  --decision .ledger/actuating/<run-id>/delivery-decision.json
```

## Falsifier

```text
proof_complete_but_no_ship_when_pr_intent = 0
ship_handoff_worker_worktree = 0
ship_handoff_integrated_branch = all PR deliveries
```
