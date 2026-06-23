---
name: fixed-point-driver
description: "Realize one bounded route and prove it. In `$actuating` mode require ARH-v1; in kernel mode consume kernel/RC-v1; in simple standalone mode permit one unambiguous owner/route frame without quotienting. Implement only the named scope/operators, enforce the surface budget, map constructs and proof to the invariant, and return when new evidence changes class, owner, route, or scope. Never invent a behavioral quotient, normal form, or delivery plan."
metadata:
  version: "6.0.0"
  activation_cost: medium
  default_depth: standard
---

# Fixed-Point Driver

## Mission

Reach one bounded realization:

```text
selected route
-> smallest sufficient owned change
-> focused proof
-> no orphan construct
-> no new observation
```

The driver is a realization authority.

It is not a route-selection authority.

## Modes

### Actuating mode

When called by `$actuating`, require:

```text
actuation_realization_handoff / ARH-v1
```

No ARH means:

```text
result = blocked
reason = selected_route_missing
```

### Kernel / RC-v1 mode

Consume `kernel_realization_handoff` and the accepted reduction certificate.

### Simple standalone mode

For one bounded task outside `$actuating`, the root/driver may form:

```yaml
fixed_point_frame:
  frame_version: FPF-v1
  goal:
  canonical_owner:
  selected_route:
  permitted_scope: []
  forbidden_actions: []
  non_goals: []
  surface_budget:
  proof_obligations: []
```

This mode is allowed only when:

```text
one canonical owner is evident
no behavioral quotient is proposed
no competing material route remains
no delivery workflow is being bypassed
```

When owner/route/distinctions are materially ambiguous:

```text
result = blocked
reason = selection_required
```

See [general-frame.md](references/general-frame.md).

## ARH-v1 contract

Required:

```yaml
actuation_realization_handoff:
  handoff_version: ARH-v1
  run_id:
  slice_id:
  gcr_id:
  afr_id:
  st_task_ids: []
  artifact_state:
  selected_route:
  canonical_owner:
  permitted_scope: []
  forbidden_actions: []
  non_goals: []
  surface_budget:
  counterexample_class:
  invariant:
  proof_obligations: []
  proof_dag_ref:
```

Validate:

```bash
python3 codex/skills/fixed-point-driver/tools/arh_gate.py <handoff.json>
```

## Allowed realization routes

```text
reuse_existing_owner
delete_or_collapse
canonicalize
representation_change
bounded_new_surface
```

`no_change`, `validate_only`, and `blocked` do not authorize implementation.

## Realization procedure

1. Verify artifact state, GCR/AFR IDs, selected task IDs, route, owner, permitted scope, surface budget, and proof obligations.
2. Inspect only enough current code to realize the route.
3. Use `$accretive-implementer` for narrow owned writing when useful.
4. Apply one coherent change inside the boundary.
5. Track every added/retired construct against the route/invariant.
6. Run focused proof named by the handoff.
7. Produce FPSR-v1.
8. Stop.

## Surface budget

Count at least:

```text
helpers
branches
fields
public symbols
fallback paths
test families
surfaces retired
```

Every construct must map to:

```text
selected counterexample class
governing invariant
accepted route
proof obligation
```

An unmapped construct is an orphan.

## New observation rule

A new observation includes:

```text
counterexample not covered by selected class
different canonical owner
required file/symbol outside permitted scope
new behavioral distinction
route no longer sufficient
proof obligation changed
surface budget insufficient
```

On any new observation:

```text
stop writing
preserve current patch/result
return_to_frontier
```

Do not patch the new observation incrementally.

## Proof

The driver runs focused proof only unless the handoff explicitly names an affected aggregate proof.

It does not own final full-repository closure or shipping.

Proof must bind:

```text
command
artifact fingerprint
toolchain/target/options when relevant
result
evidence ref
invalidators
```

## FPSR-v1

```yaml
fixed_point_slice_result:
  result_version: FPSR-v1
  run_id:
  slice_id:
  gcr_id:
  afr_id:
  artifact_state_before:
  artifact_state_after:
  selected_route:
  canonical_owner:
  permitted_scope: []
  files_changed: []
  construct_map:
    - construct:
      kind:
      class_id:
      invariant:
      route:
      proof_ids: []
  surfaces:
    helpers_added:
    branches_added:
    fields_added:
    public_symbols_added:
    fallback_paths_added:
    test_families_added:
    surfaces_retired: []
  proof:
    obligations: []
    commands: []
    evidence_refs: []
    status:
  orphan_constructs: []
  scope_violations: []
  budget_violations: []
  new_observations: []
  patch_ref:
  result:
    valid |
    return_to_frontier |
    blocked |
    invalid
  reason:
```

Validate:

```bash
python3 codex/skills/fixed-point-driver/tools/fpsr_gate.py <result.json>
```

## Certified kernel realization

When handed a certified kernel:

- work only in the named realization worktree and permitted owners;
- implement the accepted kernel and RC-v1;
- apply only certified factor/quotient/ablation/normalization operators;
- retire named superseded surfaces;
- prove the stated preservation relation;
- run recomposition audit;
- return on any new observation or failed congruence;
- never mutate delivery outside the named realization surface.

See [reduction-certificate.md](references/reduction-certificate.md).

## Handoff to root

`valid` means:

```text
selected route realized
scope and budget respected
focused proof passed
no orphan construct
no new observation
```

Root then records proof in `$st`, completes eligible tasks, and recompiles the GCR.

The driver does not:

```text
complete durable tasks
publish update_plan
commit/push
ship
land
```

## Hard rules

- Never select or invent the route.
- Never change the canonical owner.
- Never expand permitted scope.
- Never add a distinction absent from the handoff.
- Never exceed the surface budget.
- Never continue after a new observation.
- Never use implementation convenience as equivalence evidence.
- Never self-authorize delivery or closure.
