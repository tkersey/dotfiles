# Action Contract

Each action is a falsifiable bounded transition.

```yaml
action:
  action_id:
  kind:
  owner:
  preconditions:
    all: []
    any: []
    none: []
  requires_actions: []
  mutation_boundary:
    kind:
    paths: []
    symbols: []
  lock_roots: []
  expected_effects:
    facts_added: []
    unknowns_resolved: []
    obligations_closed: []
    potential_delta: {}
  expected_observation_refs: []
  failure_observation_refs: []
  proof_obligations: []
  rollback:
  utility:
    obligation_reduction:
    information_gain:
    downstream_unlock:
    proof_gain:
    execution_cost:
    irreversible_risk:
    semantic_surface_growth:
    rework_risk:
  repeatable:
```

## Kinds

```text
inspect
probe
decide
mutate
prove
stabilize
deploy
rollback
```

## Laws

- Every action has an accountable owner.
- Every action predicts at least one observable or state effect.
- Repository mutation has a nonempty boundary and lock root.
- Mutate/deploy/stabilize actions have proof and rollback.
- A probe resolves or materially narrows a named unknown.
- A decide action consumes named evidence and resolves a named unknown.
- An action whose failure produces no modeled observation is incomplete.
- Utility cannot override a safety-shield denial.
