---
name: actuating
description: "Closed-loop plan-to-PR execution controller. Use for `$actuating`, plan-to-PR, or executing EPG-v1 policies. Validate the current execution policy/state, select one EPD-v1 action, materialize only its commitment horizon into canonical `$st`, require a current GCR-v1 and prepared ASL-v1 for material mutation, realize through `$fixed-point-driver`, record ETR-v1 predicted-versus-observed evidence, advance policy state atomically, and repeat until a proven success terminal permits `$ship`. Never flatten dormant policy branches into tasks or degrade graph failure into prose mutation."
metadata:
  version: "4.0.0"
  activation_cost: high
  default_depth: standard
---

# Actuating

## Mission

Interpret one bounded execution-policy tick at a time.

```text
EPG-v1 + current EPS-v1
-> deterministic EPD-v1 selection
-> one commitment-horizon materialization
-> canonical `$st` graph
-> current GCR-v1
-> prepared ASL-v1
-> bounded FPS-v1 realization
-> focused proof and observations
-> ETR-v1
-> atomic next EPS-v1
-> repeat or terminal
```

The hard invariant is:

```text
No material repository mutation without:
  source-current EPG/EPS/EPD lineage
  current executable GCR-v1
  valid prepared ASL-v1
  valid bounded FPS-v1
```

## Authority split

```text
EPG-v1
  strategy, invariants, belief model, observations, actions, policy, shield,
  progress potential, terminal states

EPS-v1
  current evidence state and completed/failed action history

EPD-v1
  selected action or terminal; prediction and selection rationale

$st / GCR-v1
  durable task/proof graph, current commitment horizon, execution permission

VMX-v1 / PDAG-v1 / ASL-v1
  semantic frontier, proof frontier, route, mutation boundary, surface budget

FPS-v1 / FPSR-v1
  one selected bounded realization and its observed result

ETR-v1
  predicted-versus-observed transition evidence and next-state proposal

$actuating
  runtime orchestration, materialization, proof, transition, and delivery gate
```

No layer may silently override another layer's authority.

## Modes

### Policy runtime

Default for EPG-v1 material work.

Require:

```text
valid source-current EPG-v1
valid current EPS-v1
valid EPD-v1 selected from that exact state
```

### Legacy material plan

Existing plan-to-PR work without EPG may continue through:

```text
plan -> `$st` -> GCR -> VMX/ASL -> FPS/FPSR -> proof -> `$ship`
```

Do not fabricate EPG history for an in-flight legacy run.

### Graph repair

Enter when graph compile/currentness/debt/projection fails.

Allowed:

```text
read/search
policy/state inspection
st intake/graph/debt repair
proof/frontier analysis
```

Forbidden:

```text
delivery mutation
task completion
policy success transition
ship
```

### Simple bounded execution

Allowed only for small work with no material policy/graph.

A material EPG run may not silently fall back to simple or ledger mode.

## 0. Pin the run

Maintain `ASR-v4` or equivalent run state:

```yaml
actuation_state:
  run_version: ASR-v4
  run_id:
  policy_ref:
  policy_digest:
  policy_state_ref:
  current_decision_ref:
  artifact_state:
  st_plan_ref:
  current_gcr_ref:
  active_asl_ref:
  fixed_point_result_refs: []
  transition_receipts: []
  proof_state:
  ship_state:
```

After compaction, resume from durable EPG/EPS/GCR/ASL/proof state, not prose.

## 1. Validate and select one action

```bash
python3 codex/skills/plan/tools/execution_policy_gate.py policy.json

python3 codex/skills/plan/tools/policy_select.py \
  --policy policy.json \
  --state state.json \
  --out decision.json
```

EPD-v1 has no mutation authority.

It records:

```text
eligible rules/actions
shielded actions and reasons
selected action or terminal
expected effects and observations
GCR/ASL requirements
```

## 2. Handle terminal decisions

### success

Do not ship solely because EPD selected success.

Require:

```text
terminal predicates satisfied in current EPS
all referenced proof current
no active action/materialization
source and artifact state current
canonical `$st` graph proof-complete
all required ETRs valid
```

Then compute explicit PR mode and call `$ship`.

### blocked

Report the exact evidence, shield/controller reason, and required next authority.

### return_to_spec

Stop material execution and return to `$spec-pipeline`.

### return_to_grill

Stop and route the unresolved judgment to `$grill-me`.

### rollback

Execute only the policy-declared rollback. Repository-mutating rollback still requires GCR and ASL.

## 3. Materialize only the commitment horizon

For a selected action, compile semantic intake containing exact:

```text
policy ID/revision/digest
state ID/digest
decision ID
selected action ID and kind
owner and preconditions
required prior actions
mutation boundary and lock roots
expected effects and observations
proof obligations and rollback
```

Compatibility path:

```bash
st intake scaffold --source decision.json --out .step/st-intake.md
# Map EPD fields exactly; do not change policy semantics.
st intake check \
  --input .step/st-intake.md \
  --gate implementation-ready \
  --format json
st intake normalize \
  --input .step/st-intake.md \
  --out .step/st-intake.normalized.md
st intake apply \
  --file .step/st-plan.jsonl \
  --input .step/st-intake.normalized.md \
  --gate implementation-ready
st compile aperture --file .step/st-plan.jsonl --limit 7
```

Do not materialize dormant policy branches as ready or blocked tasks.

See [execution-policy-runtime.md](references/execution-policy-runtime.md).

## 4. Enforce GCR-v1

A repository-mutating action requires a current CLI-emitted GCR proving:

```text
implementation-ready graph
execution_allowed = yes
selected tasks bound to current policy/state/decision/action
no blocking unwaived graph debt
proof obligations present
projection current
```

Failure enters graph-repair mode.

`update_plan` remains a projection, never policy or graph truth.

## 5. Compile the semantic frontier

Use VMX-v1 when the selected action touches a multidimensional invariant space:

```text
parser/verifier behavior
state loading/restoration
versioned formats
continuation/frame transitions
multi-field acceptance predicates
authority/proof binding
repeated adjacent counterexamples
```

A new semantic row updates the policy/frontier before another patch.

Validate:

```bash
python3 codex/skills/actuating/tools/validation_matrix_gate.py matrix.json
```

## 6. Prepare policy-bound ASL-v1

ASL remains the mutation capability for one semantic slice.

In EPG mode add `policy_control`:

```yaml
policy_control:
  mode: epg
  policy_id:
  policy_revision:
  policy_digest:
  state_id:
  state_digest:
  decision_id:
  action_id:
  action_kind:
  policy_current: yes
  decision_selected: yes
  commitment_horizon_sequence:
  expected_effects:
  expected_observation_refs: []
  failure_observation_refs: []
```

ASL also binds:

```text
GCR and `$st` task refs
owner/invariant and VMX rows
selected/rejected route
normal form
patch boundary and forbidden actions
surface budget
PDAG proof obligations
next frontier
```

Validate and persist:

```bash
python3 codex/skills/actuating/tools/actuation_slice_gate.py slice.json

python3 codex/skills/actuating/tools/actuation_checkpoint.py \
  write \
  --input slice.json \
  --root .step/actuating
```

ASL does not duplicate policy state or `$st` task status.

See [actuation-slice-contract.md](references/actuation-slice-contract.md).

## 7. Activate language/domain routes

Before mutation, activate the route that constrains owner, hazards, boundary, or proof.

For material Zig work:

```text
ASL references ZSR-v1
PDAG references current ZPE-v1 proof epochs
```

Language skills do not own policy, task state, or delivery.

## 8. Compile policy-bound FPS-v1

FPS-v1 is the existing bounded realization handoff.

In EPG mode include matching `policy_control` and carry:

```text
GCR/ASL/task refs
owner/invariant/selected rows
selected normal form and rejected alternatives
patch boundary and forbidden actions
surface budget
proof obligations and stop conditions
expected effects/observations from EPD
```

Validate input and result:

```bash
python3 codex/skills/fixed-point-driver/tools/fixed_point_slice_gate.py \
  --input fps.json \
  --result fps-result.json
```

`$fixed-point-driver` may realize, prove no-change, block, or return to frontier.

It may not invent another policy branch, expand scope, or patch a newly discovered observation.

See [policy-action-handoff.md](references/policy-action-handoff.md).

## 9. Run tiered proof

### Action proof

After one realization, prove the selected policy action, semantic rows, and `$st` obligations.

### Policy-wave proof

Run affected aggregate proof when multiple evidence actions close one policy branch or shared dependency cut.

### Terminal proof

Before `$ship`, run complete current-head repository closure proof.

Use PDAG-v1 and proof epochs for dependency and freshness.

Do not run the full repository suite after every micro-action unless the selected obligation or dependency cut requires it.

## 10. Emit ETR-v1

Combine FPSR and actual evidence into one transition receipt:

```bash
python3 codex/skills/plan/tools/transition_receipt_gate.py \
  --policy policy.json \
  --state state.json \
  --decision decision.json \
  --receipt receipt.json
```

ETR records separately:

```text
prediction
actual observations/effects
proof
potential before/after
surprise classification
result
```

Never rewrite observed evidence to match the prediction.

Classify surprise:

```text
none
expected_variance
new_branch
model_failure
intent_failure
```

`model_failure` blocks another material action under the unchanged policy.

`intent_failure` returns to `$spec-pipeline`.

Use `policy_transition_skeptic` when prediction and observation differ materially.

See [policy-state-transition.md](references/policy-state-transition.md).

## 11. Advance EPS atomically

```bash
python3 codex/skills/plan/tools/policy_checkpoint.py apply \
  --policy policy.json \
  --state state.json \
  --decision decision.json \
  --receipt receipt.json \
  --out next-state.json
```

The checkpoint tool revalidates EPG, EPS, EPD, and ETR before writing.

After a successful transition:

```text
record obligation proof in `$st`
complete/block only current materialized tasks
archive/retire the old horizon
recompile GCR
select the next policy action
```

## 12. Resume after compaction

Resume from:

```text
ASR-v4
EPG-v1
current EPS-v1
latest EPD/ETR
current GCR
active ASL/VMX/PDAG/FPSR
current artifact state
```

Verify all digests and fingerprints first.

Reread only changed skill contracts or the active reference.

Do not reconstruct the policy frontier from prose or `update_plan`.

## 13. Learn from transitions

Use ETR and `$seq` evidence to improve:

```text
prediction calibration
probe information value
unknown-resolution latency
route rework
proof sufficiency
semantic-surface growth
rollback frequency
```

Use `$negative-ledger` only for controller-proven failed action models with reopening criteria.

Use `$retrace` to compare actions from equivalent historical evidence states.

## 14. Ship gate

Call `$ship` only after a success terminal and:

```text
policy/source/state current
no active action or open commitment horizon
all terminal obligations and proof current
canonical `$st` graph proof-complete
all required ASL/FPSR/ETR artifacts valid
no unresolved model/intent failure
explicit PR mode
```

Default after full completion:

```text
ready
```

`$ship` does not merge.

## Decision observability

Emit SDR-v1-compatible receipts for:

```text
policy action selection
shield block
action realization result
surprise classification
policy revision/authority return
terminal and PR-mode decision
```

Decision contract: [decision-contract.yaml](references/decision-contract.yaml).

## Output

```text
Actuation Bottom Line:
- policy / state / decision:
- selected action or terminal:
- GCR / ASL / materialized tasks:
- predicted vs observed effects:
- surprise classification:
- potential before / after:
- focused / wave / final proof:
- next policy state:
- PR mode / PR:
- blocker / return route:
```

## Hard rules

- No material mutation without EPG/EPS/EPD lineage in policy mode.
- No repository mutation without a current executable GCR.
- No non-trivial repository mutation without a prepared ASL and FPS.
- Materialize only the current commitment horizon.
- EPD is selection evidence, not mutation authority.
- Never hide prediction failure or new observations.
- New branch returns to policy; model failure revises policy; intent failure returns to source authority.
- Root remains sole delivery writer.
- No ship without a proven success terminal and explicit PR mode.
- Do not merge or land.
