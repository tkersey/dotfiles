---
name: plan
description: "Compile accepted intent into a source-bound execution policy and an immutable `plan_id`, ready for import into the multi-plan `$st` workspace under `.ledger/st/`. Use for `$plan`, spec-to-execution lowering, adaptive probes, stabilization plans, or plan revision. Preserve semantic authority; never mutate the repository or silently select an existing `$st` plan."
metadata:
  version: "4.0.0"
  activation_cost: medium
  default_depth: balanced
---

# Plan

## Mission

Compile intent into an execution policy that can inhabit one independent `$st`
plan namespace.

```text
source contract
-> plan identity
-> belief/unknowns
-> guarded actions
-> proof and rollback
-> execution policy
-> `$st plan create/import`
```

## Artifact root

All persisted planning artifacts use:

```text
.ledger/plan/<plan-id>/
```

Recommended:

```text
.ledger/plan/<plan-id>/policy.json
.ledger/plan/<plan-id>/projection.md
.ledger/plan/<plan-id>/revisions/
```

Do not write new planning artifacts under `.step/`.

## Plan identity

Every plan has:

```yaml
plan_identity:
  plan_id:
  alias:
  revision:
  source_digest:
  target_repository:
  target_branch:
  target_st_workspace: .ledger/st
```

`plan_id` is stable across revisions of one objective.

A materially different objective receives a new plan ID.

Do not choose an existing plan merely because it is active or recently used.

## Authority boundary

```text
$spec-pipeline
  semantics, scope, non-goals, architecture, compatibility, proof bar

$plan
  execution policy, evidence gates, bounded actions, rollback, plan identity

$st
  durable graph, plan namespace, scheduling, resource coordination, proof state

$actuating
  one plan/session/claim execution controller
```

A semantic gap returns to `$spec-pipeline` or `$grill-me`.

## Planning regimes

```text
deterministic
  compile known actions

adaptive
  compile probes and evidence-conditioned decision routes

stabilization
  compile containment and observability before normal work
```

## Execution policy

The authoritative plan artifact should identify:

```text
policy ID/revision
plan ID
source and artifact state
terminal predicates
safety invariants
facts and unknowns
observable evidence
bounded actions
resource predictions
proof obligations
rollback
policy rules
progress potential
commitment horizon
invalidators
```

Every mutation action predicts resources using the `$st` grammar:

```text
path:
symbol:
generated:
schema:
service:
repo:all
```

Unknown scope becomes `repo:all / exclusive`.

## Multi-plan handoff

Create/import explicitly:

```bash
st plan create \
  --workspace .ledger/st \
  --plan <plan-id> \
  --source .ledger/plan/<plan-id>/policy.json

st plan import-policy \
  --workspace .ledger/st \
  --plan <plan-id> \
  --input .ledger/plan/<plan-id>/policy.json
```

The handoff records:

```yaml
st_handoff:
  workspace: .ledger/st
  plan_id:
  policy_ref:
  policy_digest:
  target_branch:
  proposed_resources: []
  mutation_allowed: no
```

`$plan` never emits GCR or mutation authority.

## Cross-plan relationships

A plan may propose, but not create, cross-plan relations:

```yaml
proposed_cross_plan_dependency:
  from:
  to:
  type:
  reason:
```

Only the `$st` workspace may accept and persist one.

Do not flatten another plan’s tasks into the current plan merely to express a
dependency.

## Readiness

A plan is ready for `$st` when:

```text
source current
plan ID stable
terminal conditions testable
every mutation action has resource predictions
unknowns are gated
proof/rollback complete
no semantic drift
target branch explicit
```

Readiness does not mean execution is safe.

Execution still requires:

```text
workspace import
plan audit
global resource claim
GCR-v2
```

## Output

When emitting a plan, include one `<proposed_plan>` block with:

```text
Plan Identity
Source and Terminal Contract
Policy State and Unknowns
Actions and Resource Predictions
Decision/Observation Rules
Proof, Rollback, and Invalidators
`$st` Workspace Handoff
```

Do not include internal iteration logs.

## Hard rules

- Persist only under `.ledger/plan/`.
- Every plan has an explicit immutable plan ID.
- Never infer the target `$st` plan.
- Never merge separate objectives into one plan for convenience.
- Never create cross-plan edges outside `$st`.
- Never grant mutation authority.
- Unknown scope means exclusive scope.
