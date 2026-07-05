# Emulator Contract Profile

Use this profile when a Ghost package is intended to be consumed by `$emulator`.

## Required contract shape

Prefer Ghost's scenario layout:

```yaml
meta:
  kind: scenario
  version: 1
  source_version: "skill:<fingerprint-or-revision>"
  contract_purpose: emulator

scenarios:
  <scenario_id>:
    description:
    initial_state:
    tools:
    task:
    limits:
    constraints:
    evaluation:
```

## Scenario requirements

Each scenario should define:

```yaml
scenario:
  case_id:
  actor_model:
  visible_state:
  hidden_ground_truth:
  tool_surface:
  allowed_tools: []
  denied_tools: []
  user_goal:
  expected_behavior:
  prohibited_behavior:
  hard_oracles: []
  trace_invariants: []
  mutation_hints: []
```

## Oracles

Prefer hard oracles over final-text goldens:

```text
state_assert
trace_invariant
tool_called
tool_not_called
side_effect_assert
schema_assert
budget_assert
confirmation_before_side_effect
injection_resistance
```

Rubric or model-judged oracles are allowed only as supporting evidence. They must not be the sole authority for safety-critical behavior.

## Fidelity labels

Every emulator-targeted Ghost package should declare one or more fidelity labels:

```text
contract-debug       exact and deterministic
production-like      includes noise, retries, latency, and stochastic actors
adversarial          includes hostile or misleading inputs
mutation-ready       includes dimensions that may be varied safely
```

## Contract gaps

If a Ghost package lacks actor models, hidden state, tool behavior, or oracle definitions, `$emulator` should report `source_contract_gap` rather than inventing normative behavior.
