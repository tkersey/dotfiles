# Actuating Delivery Handoff

## Purpose

`$actuating` includes delivery when the run, source request, or user intent asks for
PR output. A proof-complete plan graph is not the terminal state for a plan-to-PR
actuation run.

The delivery handoff prevents this regression:

```text
proof-complete graph audit
-> stop
-> no PR despite plan-to-PR intent
```

and enforces this terminal chain:

```text
proof-complete graph audit
-> serialized integration complete
-> current target-branch head/epoch
-> ADD-v1 delivery decision
-> $ship receives integrated target-branch state
-> SHIP-v1 or delivery-blocked reason
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
integration queue quiescent for the plan
at least one integrated change-set receipt or explicit no-change integrated receipt
target branch/head/epoch known
cross-plan dependency status clear
PR delivery intent present
no do_not_ship_before blocker
```

Then immediately invoke `$ship` with the integrated target-branch state.

Do not pass:

```text
worker worktree
unintegrated patch
claim-local tree
proof from a stale branch epoch
```

## Intent sources

PR delivery intent exists when any of these is true:

```text
user asked to open/update/promote a PR
user asked for plan-to-PR execution
actuation_run.pr_mode is ready|draft|update-existing|promote-draft
source handoff says next_owner: $ship
prior workflow explicitly requested draft PR visibility
```

No PR intent means `shipping_not_requested`, not `$ship`.

## Blocked delivery

`blocked` is required when:

```text
proof-complete receipt missing or stale
integration queue not quiescent
integrated change-set receipts missing for a changeful run
cross-plan dependency is blocked or unknown
current target branch/head/epoch unknown
do_not_ship_before is nonempty
current PR state cannot be inspected and mode requires update/promote
```

A blocked delivery result must name the missing condition. It must not silently
fall back to proof-complete as terminal.

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

The delivery repair is working when future actuation reports show:

```text
proof_complete_but_no_ship_when_pr_intent = 0
ship_handoff_worker_worktree = 0
ship_handoff_integrated_branch = all PR deliveries
```
