---
name: fixed-point-driver
description: "Realize one already selected bounded action and prove it. In EPG mode consume policy-bound FPS-v1; in legacy `$actuating` mode consume ordinary FPS-v1; in kernel mode consume kernel/RC-v1; in standalone mode permit one unambiguous frame. Implement only the named owner, boundary, and surface budget, map constructs and proof to obligations, report observed effects, and return immediately when evidence changes the policy, owner, route, class, or scope. Never invent a policy branch, behavioral quotient, normal form, or delivery plan."
metadata:
  version: "7.0.0"
  activation_cost: medium
  default_depth: standard
---

# Fixed-Point Driver

## Mission

```text
selected bounded action
-> smallest sufficient owned realization
-> focused proof
-> observed effects
-> no orphan construct
-> no unmodeled continuation
```

The driver is a realization authority.

It is not a policy, route-selection, task, or delivery authority.

## Modes

### EPG policy-action mode

Consume `fixed_point_slice / FPS-v1` with a current `policy_control` block.

The handoff binds EPG/EPS/EPD/GCR/ASL identities and one selected action.

### Legacy actuating mode

Consume ordinary FPS-v1 compiled from ASL-v1.

### Kernel / RC-v1 mode

Consume an accepted kernel and reduction certificate.

### Simple standalone mode

Permit one bounded frame only when owner, route, scope, and proof are unambiguous and no delivery workflow is bypassed.

## FPS-v1

Required general shape:

```yaml
fixed_point_slice:
  slice_version: FPS-v1
  slice_id:
  artifact_state:
  st_task_refs: []
  graph_control_ref:
  actuation_slice_ref:
  semantic_route_refs: []
  owner:
  invariant:
  selected_rows: []
  selected_normal_form:
  alternatives:
    - route:
      rejected_because:
  patch_boundary:
    files: []
    symbols: []
  forbidden_actions: []
  surface_budget:
  proof_obligations: []
  stop_conditions: []
  gate:
    prepared:
    mutation_allowed:
```

EPG mode additionally requires:

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
  commitment_horizon_sequence:
  expected_effects:
  expected_observation_refs: []
  failure_observation_refs: []
```

Validate:

```bash
python3 codex/skills/fixed-point-driver/tools/fixed_point_slice_gate.py \
  --input fps.json
```

## Mutation gate

Mutation is permitted only when:

```text
FPS validates
prepared = yes
mutation_allowed = yes
artifact state is current
GCR and ASL refs exist
owner/invariant are named
selected row or exact bounded obligation exists
normal form is selected
patch boundary is non-empty
proof obligations are non-empty
```

In EPG mode also require current, matching policy/state/decision/action lineage.

## Realization procedure

1. Verify artifact, GCR, ASL, and optional policy identities.
2. Verify owner, route, boundary, surface budget, proof, and stop conditions.
3. Inspect only enough code/evidence to realize the selected action.
4. Apply one coherent change inside the boundary.
5. Map every changed construct to action, owner, invariant, selected rows, obligations, and proof.
6. Enforce the hard surface budget.
7. Run focused proof.
8. Record actual observations/effects without rewriting the prediction.
9. Emit FPSR-v1.
10. Stop.

Use `$accretive-implementer` for narrow owned writing when useful.

## Surface budget

Account for at least:

```text
files
production net
helpers
branches
fields/state variants
public symbols
protocol/fallback cases
test families
surfaces retired
```

Every construct maps to:

```text
selected action/route
accepted obligation or evidence purpose
canonical owner
proof obligation
```

An unmapped construct is orphan surface.

## New observation rule

Return immediately when realization discovers:

```text
new counterexample/observation class
new authority owner
new EPG branch
required boundary expansion
new accepted behavioral distinction
selected prediction no longer fits
proof obligation changed
surface budget insufficient
```

Do not append-patch the new observation.

In EPG mode return:

```text
result = return_to_frontier
policy_result.new_observations non-empty
```

Root decides whether to continue policy selection, revise EPG, return to source authority, or rollback.

## FPSR-v1

```yaml
fixed_point_slice_result:
  result_version: FPSR-v1
  slice_id:
  artifact_state:
  owner:
  invariant:
  selected_rows: []
  realization_patch_ref:
  changed_files: []
  changed_symbols: []
  construct_map:
    - construct:
      owner:
      invariant:
      row_refs: []
      obligation_refs: []
      proof_refs: []
  surface_delta:
  proof_refs: []
  obligations_covered: []
  budget:
    respected:
    violations: []
  new_observations: []
  result:
    valid |
    no_change |
    return_to_frontier |
    blocked |
    invalid

  policy_result:
    policy_id:
    policy_revision:
    policy_digest:
    state_id:
    decision_id:
    action_id:
    observed_effects:
      facts_added: []
      unknowns_resolved: []
      obligations_closed: []
    observations:
      - observation_id:
        outcome:
        evidence_ref:
    prediction_invalidated:
```

`policy_result` is required only when the input has `policy_control`.

Validate input/result together:

```bash
python3 codex/skills/fixed-point-driver/tools/fixed_point_slice_gate.py \
  --input fps.json \
  --result fps-result.json
```

## Result laws

### valid

Requires:

```text
identity and route unchanged
changed files/symbols inside boundary
surface budget respected
all constructs mapped
focused proof passed
required obligations covered
no new observation
```

### no_change

Requires current proof that the selected obligation already holds.

### return_to_frontier

Requires at least one new observation or prediction invalidation.

### blocked

External/tool/dependency/authority blocker without contract violation.

### invalid

Scope, budget, orphan, proof, identity, or lineage violation.

## EPG observation discipline

The driver reports observations; it does not interpret the next policy state.

It must not:

```text
change the EPG prediction after seeing the result
select another policy action
advance EPS
classify an intent failure as success
continue under a stale decision
```

Root combines FPSR and independent evidence into ETR-v1.

## Kernel / RC-v1 mode

Preserve the existing reduction laws:

```text
no quotient without congruence
no retained distinction without a witness
no ablation without obligation discharge
no normal form without recomposition
no preservation overclaim
```

Work only in the named realization surface and return on new evidence.

See [reduction-certificate.md](references/reduction-certificate.md).

## Standalone mode

Use FPF-v1 only for one bounded, unambiguous task outside `$actuating`.

Reject standalone mode when there is more than one plausible owner/route, a behavioral quotient decision, scope expansion, or delivery authority.

See [general-frame.md](references/general-frame.md).

## Handoff to root

Root consumes FPSR, records proof in `$st`, and—in EPG mode—builds ETR-v1.

The driver does not:

```text
advance EPS
complete durable `$st` tasks
publish update_plan
commit/push
ship
land
```

## Hard rules

- Never invent or select a policy branch.
- Never change the canonical owner or route.
- Never expand boundary or budget silently.
- Never add an unmodeled behavioral distinction.
- Never continue after a new observation.
- Never claim proof without obligation coverage.
- Never self-authorize task completion, delivery, or policy transition.
