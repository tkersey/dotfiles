---
name: plan
description: "Compile accepted intent or a `$spec-pipeline` PSC-v1 source contract into a source-bound execution policy and immutable `plan_id`, then exhaustively refine it to a policy-synthesis fixed point before handoff to the multi-plan `$st` workspace under `.ledger/st/`. Use for `$plan`, spec-to-execution lowering, adaptive probes, stabilization plans, or plan revision. Preserve semantic authority; never mutate the repository or silently select an existing `$st` plan."
metadata:
  version: "4.2.0"
  activation_cost: medium
  default_depth: balanced
---

# Plan

## Mission

Compile accepted intent into an execution policy that can inhabit one independent
`$st` plan namespace, then refine that policy until no material execution
improvement remains.

```text
source contract
-> plan source contract gate
-> plan identity
-> belief/unknowns
-> guarded actions
-> proof and rollback
-> policy synthesis fixed point
-> execution policy
-> `$st plan create/import`
```

The best old `$plan` behavior is still mandatory:

```text
iterate until exhausted
```

The bad old artifact ceremony is not:

```text
no public iteration footers
no self-reported rewrite ratios
no synthetic round logs as readiness proof
```

## Accepted source contracts

`$plan` may start from one of:

```text
direct user-authorized execution objective
plan_source_contract / PSC-v1 from `$spec-pipeline`
revision request for an existing plan_id
```

A `$spec-pipeline` tail-call must pass:

```yaml
plan_source_contract:
  contract_version: PSC-v1
  source_owner: spec-pipeline
  spec_id:
  implementation_spec:
  decision_packet:
  sgr_v2:
  proof_bar:
  non_goals: []
  target_branch:
  do_not_execute_before: []
```

Validate PSC-v1 before planning:

```bash
uv run python codex/skills/plan/tools/plan_source_contract_gate.py <psc-file>
```

Fail closed when:

```text
source_owner != spec-pipeline
SGR-v2 missing
SGR-v2 mode not in {full, repair}
SGR-v2 status != complete
SGR-v2 lane != spec_to_plan
SGR-v2 gate.plan_allowed != yes
SGR-v2 lint.verdict != pass
SGR-v2 execution_handoff.ready_for_plan != yes
SGR-v2 execution_handoff.next_owner != $plan
SGR-v2 auto_plan_handoff.eligible != yes
do_not_execute_before is non-empty
implementation_spec missing
proof_bar missing
target_branch missing
```

A semantic gap returns to `$spec-pipeline` or `$grill-me`. `$plan` must not
repair missing semantics by inventing scope, non-goals, compatibility, or proof
bar.

See [03-plan-source-contract.md](references/cli-specs/03-plan-source-contract.md)
and [04-plan-source-contract-gate.md](references/cli-specs/04-plan-source-contract-gate.md).

## Artifact root

All persisted planning artifacts use:

```text
.ledger/plan/<plan-id>/
```

Recommended:

```text
.ledger/plan/<plan-id>/policy.json
.ledger/plan/<plan-id>/projection.md
.ledger/plan/<plan-id>/synthesis-receipt.json
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

Do not choose an existing plan merely because it is active or recently used. PSC
source digest and objective identity participate in plan identity selection.

## Authority boundary

```text
$spec-pipeline
  semantics, scope, non-goals, architecture, compatibility, proof bar

$plan
  execution policy, evidence gates, bounded actions, rollback, plan identity,
  exhaustive policy refinement

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

Regime classification is revisited during synthesis. If a lens proves the chosen
regime is wrong, revise the policy or return to the source authority.

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

## Policy synthesis fixed point

Before emitting a plan, run an internal exhaustive refinement loop.

A complete sweep evaluates these lenses:

```text
source fidelity
semantic authority and non-goals
system regime classification
facts, unknowns, and observation coverage
action and resource-boundary completeness
policy closure over reachable states
safety, rollback, and irreversible-risk control
proof and terminal-state sufficiency
simplicity, surface minimization, and `$st` compileability
```

Rules:

- No fixed iteration cap.
- A material improvement restarts the sweep from the earliest affected lens.
- A material blocker routes to `return_to_spec`, `return_to_grill`, or `blocked`.
- Stop only after one complete zero-material-delta sweep.
- Then run an independent fresh-eyes pass.
- Emit only the final plan, not the draft history.

## Mandatory radical candidate

Before finalization, run one radical creativity pass.

Question:

```text
What is the single smartest, most radically innovative, accretive, useful,
compelling, and execution-improving change available to this plan?
```

The pass must produce a candidate or explicitly say `none`.

Then classify the candidate:

```text
adopt
  improves execution without violating source authority or minimality

reject
  clever but unsafe, unnecessary, source-expanding, or surface-increasing

defer
  promising but outside the current execution horizon; record trigger

return_to_spec
  changes semantics, scope, architecture, compatibility, authority, or proof bar

none
  no non-obvious candidate survived generation
```

Creativity is mandatory. Accretion is not.

Never add content merely because finalization is near. A rejected radical
candidate is a successful creativity pass when the rejection is evidence-based.

## Policy synthesis receipt

Emit or persist one compact `PSR-v1` receipt:

```yaml
policy_synthesis_receipt:
  receipt_version: PSR-v1
  plan_id:
  revision:
  source_digest:
  source_contract:
    kind: direct | PSC-v1 | revision
    source_owner:
    spec_id:
    sgr_digest:
  initial_policy_digest:
  final_policy_digest:
  passes:
    - pass_id:
      lens:
      candidate_digest_before:
      candidate_digest_after:
      findings: []
      material_changes: []
      disposition:
        changed |
        clean |
        blocked |
        return_to_spec |
        return_to_grill
  radical_candidate:
    candidate:
    disposition:
      adopt |
      reject |
      defer |
      return_to_spec |
      none
    reason:
    affected_refs: []
  convergence:
    complete_clean_sweep:
    independent_press_pass_clean:
    unresolved_errors:
    untreated_material_risks:
    improvements_exhausted:
```

The receipt proves synthesis happened; it does not expose private reasoning.

The final `<proposed_plan>` should include a concise `Policy Synthesis Receipt`
section or a reference to the persisted receipt.

Validate:

```bash
uv run python codex/skills/plan/tools/policy_synthesis_receipt_gate.py   .ledger/plan/<plan-id>/synthesis-receipt.json
```

See [05-policy-synthesis-receipt.md](references/cli-specs/05-policy-synthesis-receipt.md).

## Multi-plan handoff

Create/import explicitly:

```bash
st plan create   --workspace .ledger/st   --plan <plan-id>   --source .ledger/plan/<plan-id>/policy.json

st plan import-policy   --workspace .ledger/st   --plan <plan-id>   --input .ledger/plan/<plan-id>/policy.json
```

The handoff records:

```yaml
st_handoff:
  workspace: .ledger/st
  plan_id:
  policy_ref:
  policy_digest:
  synthesis_receipt_ref:
  synthesis_receipt_digest:
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

Do not flatten another plan's tasks into the current plan merely to express a
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
policy synthesis fixed point reached
radical candidate evaluated
independent press pass clean
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
Policy Synthesis Receipt
`$st` Workspace Handoff
```

Do not include internal iteration logs.

The synthesis receipt should summarize the fixed point in compact form:

```text
lenses swept
material changes accepted
radical candidate disposition
clean sweep result
fresh-eyes result
remaining blockers
```

## Fast readiness response

When the user asks only whether an existing plan is ready:

- validate source currentness;
- validate policy structure;
- validate PSR-v1 convergence;
- validate radical candidate disposition;
- validate `$st` handoff readiness.

If all pass and no revision is requested, reply exactly:

```text
Plan is ready.
```

Do not use self-attested readiness without PSR/source evidence.

## Hard rules

- Persist only under `.ledger/plan/`.
- Every plan has an explicit immutable plan ID.
- Validate PSC-v1 before planning from `$spec-pipeline`.
- Never infer the target `$st` plan.
- Never merge separate objectives into one plan for convenience.
- Never create cross-plan edges outside `$st`.
- Never grant mutation authority.
- Unknown scope means exclusive scope.
- Exhaustive policy synthesis is mandatory before emission.
- No fixed iteration cap.
- Do not expose full internal iteration logs.
- Mandatory radical creativity candidate; optional adoption.
- No arbitrary addition after convergence.
