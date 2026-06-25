---
name: actuating
description: "Plan-to-PR execution controller for one named plan inside the multi-plan `$st` workspace. Use for `$actuating`, implementing a material plan, resuming an actuation run, or driving one execution-policy action. Require explicit workspace, plan, session, claim, fencing token, branch epoch, and current GCR-v2. Workers produce fenced change sets; target-branch integration is serialized through `$st`."
metadata:
  version: "5.0.0"
  activation_cost: high
  default_depth: standard
---

# Actuating

## Mission

Drive one plan through bounded, proof-carrying execution without conflicting
with other plans or agents.

```text
named plan
-> session binding
-> workspace allocation
-> fenced claim
-> GCR-v2
-> bounded semantic/action slice
-> isolated realization
-> focused proof
-> sealed change set
-> serialized integration
-> branch-epoch proof refresh
-> delivery
```

## Artifact root

Persist actuation control under:

```text
.ledger/actuating/<run-id>/
```

References to plan/claim/proof remain authoritative at their owning paths under:

```text
.ledger/st/
```

Never create new actuation artifacts under `.step/`.

## Required run identity

```yaml
actuation_run:
  run_id:
  workspace: .ledger/st
  plan_id:
  session_id:
  executor:
  target_branch:
  actuation_root: .ledger/actuating/<run-id>
```

One run controls one plan and one current session binding.

It may observe other plans through workspace receipts but may not mutate their
graphs.

## Capability gate

Require:

```text
st workspace_v1
st workspace_claim_v1
st fencing_token_v1
st session_view_v1
st changeset_v1
st serialized_integration_v1
st gcr_v2
```

If any required capability is unavailable:

```text
analysis, plan repair, and proof planning allowed
material mutation and delivery forbidden
```

## Phase 1 — bind the plan and session

```bash
st session bind \
  --workspace .ledger/st \
  --session <session-id> \
  --executor <executor-id> \
  --plan <plan-id>
```

Do not infer the plan when multiple plans are active.

## Phase 2 — compile current plan state

For a healthy existing plan:

```bash
st graph audit \
  --workspace .ledger/st \
  --plan <plan-id> \
  --gate implementation-ready \
  --format json
```

For a new plan, complete the `$st` intake path under:

```text
.ledger/st/plans/<plan-id>/intake/
```

Plan-local graph readiness does not yet grant mutation.

## Phase 3 — workspace allocation and claim

Inspect global allocation:

```bash
st workspace aperture \
  --workspace .ledger/st \
  --executors <executor-id> \
  --format json
```

Claim the selected work:

```bash
st claim \
  --workspace .ledger/st \
  --plan <plan-id> \
  --session <session-id> \
  --ids <ids> \
  --lease-seconds 900
```

Record:

```text
claim ID
fencing token
workspace sequence
plan sequence
branch epoch
resource set
external worktree metadata ref
```

If claim is denied, do not “work around” it by narrowing paths in prose or
opening another plan file.

## Phase 4 — GCR-v2

```bash
st compile aperture \
  --workspace .ledger/st \
  --plan <plan-id> \
  --session <session-id> \
  --claim <claim-id> \
  --limit 7
```

Material mutation requires:

```text
execution_allowed = yes
current workspace/plan sequence
current branch epoch
current held claim
current fencing token
no conflicting claim
current session view
no unwaived blocking debt
```

Validate exported GCR when needed:

```bash
python3 codex/skills/st/tools/gcr_v2_gate.py gcr.json
```

`update_plan` remains projection only.

## Phase 5 — prepare one bounded slice

The slice references:

```text
workspace/plan/session
claim and fencing
GCR-v2
selected task IDs
selected execution-policy action or semantic route
owner and invariant
patch/resource boundary
proof obligations
stop/new-observation conditions
```

No slice may widen the claim.

A wider boundary requires:

```text
release or amend claim through `$st`
re-run conflict analysis
obtain new fencing authority
compile a new GCR-v2
```

## Phase 6 — realize in the claimed worktree

Invoke `$fixed-point-driver` with:

```text
external worktree ref
claim ID and fencing token
resource roots
base head and branch epoch
selected normal form/action
proof obligations
surface budget
```

Workers must not:

```text
write the primary checkout
stage the shared Git index
commit/push the target branch
edit another plan
write outside claimed resources
```

## Phase 7 — proof and transition

Run focused proof in the worker tree.

Record proof under:

```text
.ledger/st/proof/<plan-id>/
```

Proof receipts bind:

```text
claim
branch epoch
tree digest
dependency cut
```

A new observation that changes route, owner, required resources, or accepted
behavior stops realization and returns to the plan/policy frontier.

## Phase 8 — seal the change set

```bash
st changeset seal \
  --workspace .ledger/st \
  --claim <claim-id> \
  --fencing-token <token>
```

Validate:

```bash
python3 codex/skills/st/tools/changeset_gate.py changeset.json
```

Require every changed path to be covered by the claim.

## Phase 9 — integrate

```bash
st integrate enqueue \
  --workspace .ledger/st \
  --changeset <changeset-id>
```

The workspace integrator—not the worker—advances the target branch.

After integration:

```text
branch epoch advances
foreign proof invalidation is computed
plan/session views become stale as needed
next GCR-v2 must bind the new epoch
```

If integration rebases or materially changes the patch, rerun affected proof.

## Phase 10 — close the plan

After all plan work is integrated:

```bash
st graph audit \
  --workspace .ledger/st \
  --plan <plan-id> \
  --gate proof-complete \
  --format json
```

Final plan delivery additionally requires:

```text
integration queue quiescent for the plan
current target-branch epoch
current final-tree proof
no cross-plan blocker
current PR/review state
```

Other active plans need not be complete unless their cross-plan dependencies
block this plan’s terminal predicates.

## Projection

Prime only the bound session:

```bash
st prime \
  --workspace .ledger/st \
  --plan <plan-id> \
  --session <session-id> \
  --claim <claim-id> \
  --mode aperture
```

Project only the emitted native-plan rows.

Never publish another session’s view.

## Heartbeats and compaction

Before long proof or likely compaction:

```bash
st heartbeat \
  --workspace .ledger/st \
  --claim <claim-id> \
  --fencing-token <token>
```

Persist actuation checkpoint:

```text
.ledger/actuating/<run-id>/current.json
```

On resume, verify:

```text
claim still held
fencing current
workspace/plan sequence current
branch epoch current
worktree still bound to claim
```

Any mismatch returns to workspace allocation.

## Shipping

`$ship` receives the integrated target-branch state, not a worker worktree.

Pass:

```text
plan ID
integrated change-set receipts
current target branch/head/epoch
proof-complete plan receipt
cross-plan dependency status
explicit PR mode
```

`$actuating` does not merge.

## Final report

```text
Actuation:
- run / workspace / plan:
- session / executor:
- claim / fencing / resources:
- GCR-v2:
- selected action/tasks:
- worker worktree:
- focused proof:
- change set:
- integration receipt / branch epoch:
- stale foreign proof:
- plan graph closure:
- PR mode / PR:
```

## Hard rules

- One actuation run owns one plan.
- No plan inference when several plans are active.
- No material mutation without current GCR-v2.
- No mutation without current fenced claim.
- No boundary widening outside `$st`.
- No worker writes to primary checkout or shared target branch.
- No direct commit/push by worker agents.
- Integration is serialized.
- Proof is branch-epoch bound.
- All new artifacts live under `.ledger/`.
