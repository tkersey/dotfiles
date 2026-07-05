# Actuating Pre-Mutation Interlock

## Purpose

`$actuating` is a transaction controller. It does not merely advise implementation.

The interlock prevents this failure shape:

```text
plan pressure
-> local decomposition
-> patch attempts
-> update_plan projection
-> proof attempts
-> retrospective control language
```

and enforces this shape:

```text
plan pressure
-> actuation session binding
-> claimed resources
-> actuation-authority receipt execution_allowed=yes
-> APMA-v1 mutation-authorized
-> bounded slice
-> isolated realization
-> proof receipt
-> sealed changeset
-> serialized integration
```

## APMA-v1

APMA-v1 is the local pre-mutation authority receipt.

```yaml
actuation_pre_mutation_authority:
  version: APMA-v1
  verdict: mutation-authorized
  issued_at:
  run_id:
  workspace:
    workspace_id:
    target_branch:
    head:
    workspace_sequence:
    branch_epoch:
    working_tree_fingerprint:
  plan:
    plan_id:
    plan_sequence:
    selected_task_ids: []
  coordination:
    claim_id:
    session_id:
    executor:
    coordination_token:
    lease_current:
    coordination_current:
    resources: []
  authority:
    authority_id:
    execution_allowed: yes
    projection_view_id:
    projection_digest:
  intended_resources: []
  resource_coverage: []
```

APMA-v1 is derived from a current actuation-authority receipt plus the exact intended edit resource.
It is not hand-authored.

## Authority record

When a material mutation needs local authority, persist a current APMA-v1 record under `.ledger/actuating/<run-id>/apma-v1.json` and check it immediately before mutation. A failed or missing authority check means no patch.

## What it validates

The gate requires:

```text
actuation-authority receipt receipt_version
actuation-authority receipt execution_allowed=yes
no denial reasons
claim id
session id
executor
coordination token
lease_current=true
coordination_current=true
workspace sequence equality
plan sequence equality
branch epoch equality
projection selected IDs equals plan selected IDs
projection session equals coordination session
nonempty selected task IDs
nonempty claim resources
no conflicting claims
graph gate passed
no graph debt
intended write/exclusive resource covered by claim resource
```

## Unsupported authority path

If the available authority path invalidates its own session, view, sequence, or artifact preconditions, stop actuation, do not mutate product files, release any held claim when safe, and record the run as blocked on authority tooling.

## Direct implementation fallback

Direct implementation can be valid when no concurrent workspace coordination is needed, but it must not be presented as `$actuating`.

Use an explicit transition:

```text
$actuating blocked: authority receipt path self-invalidating.
Leaving $actuating before direct implementation.
No actuation authority is claimed for subsequent edits.
```

## Falsifier

The interlock is working when future `seq actuation-audit` true/control rows show:

```text
mutations_without_authority = 0
apply_patch_calls are covered by APMA-v1
no graph_bypass verdicts
no projection_inversion verdicts
```
