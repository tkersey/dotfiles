---
name: fixed-point-driver
description: "Realize one already selected normal form or execution-policy action inside a fenced `$st` workspace claim. Use only with explicit workspace, plan, claim, fencing token, GCR-v2, external worktree, resource boundary, and proof obligations. Emit a bounded realization result/change-set candidate; never widen scope, edit another plan, or advance the shared target branch."
metadata:
  version: "8.0.0"
  activation_cost: medium
  default_depth: standard
---

# Fixed-Point Driver

## Mission

Realize one selected action under global coordination authority.

```text
selected action/normal form
+ current GCR-v2
+ fenced workspace claim
+ isolated worktree
+ hard resource boundary
+ proof obligations
-> one bounded realization result
```

This skill does not select the plan, route, resource set, or integration order.

## Required input

```yaml
fixed_point_slice:
  slice_version: FPS-v2

  workspace:
    workspace_ref:
    workspace_id:
    workspace_sequence:
    target_branch:
    branch_epoch:
    base_head:

  plan:
    plan_id:
    plan_sequence:
    task_refs: []
    policy_action_ref:

  coordination:
    session_id:
    executor:
    claim_ref:
    claim_id:
    fencing_token:
    lease_expires_at:
    gcr_ref:
    worktree_ref:

  semantics:
    owner:
    invariant:
    selected_rows: []
    selected_normal_form:
    alternatives: []

  boundary:
    resources: []
    files: []
    symbols: []
    forbidden_actions: []
    surface_budget:

  proof_obligations: []
  stop_conditions: []

  gate:
    gcr_current:
    claim_current:
    fencing_current:
    worktree_current:
    mutation_allowed:
```

## Mutation gate

Mutation is allowed only when all are true:

```text
GCR-v2 execution_allowed = yes
workspace/plan sequences match
branch epoch and base head match
claim is held by this session/executor
fencing token is current
worktree belongs to claim
resources are nonempty
semantic route/action selected
proof obligations nonempty
```

Any failure returns:

```text
blocked
or
return_to_workspace
```

Never repair authority in prose.

## Worktree rules

The driver operates only in the external worktree named by `worktree_ref`.

It must not:

```text
edit the primary checkout
stage or mutate the shared Git index
checkout/reset the target branch
commit or push the target branch
write under another plan namespace
write under another claim’s artifact paths
```

Local worker commits may be used only if the workspace change-set sealer accepts
them as internal representation.

## Resource enforcement

The hard boundary is the claim’s structured resource set.

Before each new path/symbol mutation, verify it is covered.

If implementation requires an unclaimed resource:

```text
stop
emit requested_resource_expansion
return_to_workspace
```

Do not continue with a “small related edit.”

Unknown or dynamically generated scope requires a workspace-approved
`repo:all / exclusive` claim.

## Procedure

1. Verify GCR, claim, fencing, epoch, and worktree lineage.
2. Inspect only the selected owner/action and required proof surface.
3. Reconfirm the selected normal form fits the claimed resource boundary.
4. Realize the smallest owner-correct change.
5. Keep all added surface within the declared budget.
6. Run focused proof in the claimed worktree.
7. Compute changed paths and map them to resources.
8. Emit FPSR-v2 and a change-set candidate.
9. Stop on any new observation or boundary expansion.
10. Do not integrate.

## New observations

Return to the controller when any appears:

```text
new counterexample class
new authority owner
new required behavior
new plan dependency
resource expansion
branch epoch change
claim/fencing loss
proof obligation absent from the slice
selected normal form no longer sufficient
```

Do not patch the new observation.

## Proof

Focused proof binds:

```text
workspace sequence
plan sequence
branch epoch
base head
claim/fencing
worker tree digest
dependency cut
```

A proof produced after the claim expires may be preserved as evidence but cannot
authorize completion or integration without controller revalidation.

## FPSR-v2

```yaml
fixed_point_slice_result:
  result_version: FPSR-v2

  workspace:
    workspace_id:
    workspace_sequence:
    branch_epoch:
    base_head:

  plan:
    plan_id:
    plan_sequence:
    task_refs: []

  coordination:
    claim_id:
    fencing_token:
    session_id:
    executor:
    worktree_ref:

  semantics:
    owner:
    invariant:
    selected_rows: []
    selected_normal_form:

  realization:
    changed_files: []
    changed_symbols: []
    construct_map: []
    tree_digest:
    patch_digest:

  resources:
    declared: []
    observed: []
    uncovered: []

  budget:
    respected:
    violations: []

  proof_refs: []
  obligations_covered: []
  new_observations: []
  requested_resource_expansion: []

  result:
    valid |
    no_change |
    return_to_frontier |
    return_to_workspace |
    blocked |
    invalid
```

`valid` requires:

```text
current authority lineage
no uncovered resource
budget respected
all required focused obligations covered
no unresolved new observation
```

## Change-set handoff

For a valid result, emit the inputs needed for:

```bash
st changeset seal \
  --workspace .ledger/st \
  --claim <claim-id> \
  --fencing-token <token>
```

The driver does not decide whether the target branch can accept the result.

## Reduction-certificate mode

Existing MBK/RC realization remains supported.

It additionally requires:

```text
workspace claim
resource mapping
branch epoch
external worktree
serialized integration handoff
```

The accepted kernel/RC may restrict semantics more tightly than the resource
claim. Both constraints apply.

## Final report

```text
Fixed-Point Result:
- workspace / plan:
- claim / fencing / worktree:
- selected action / owner / invariant:
- resources declared / observed / uncovered:
- changed files / symbols:
- budget:
- focused proof:
- new observations:
- result:
- change-set handoff:
```

## Hard rules

- Never select a plan or semantic route.
- Never mutate without current GCR-v2 and fencing.
- Never mutate outside the claim.
- Never edit another plan.
- Never edit the primary checkout.
- Never advance the target branch.
- Never continue after resource expansion or new semantic observation.
- Never claim proof without workspace/plan/epoch/tree lineage.
