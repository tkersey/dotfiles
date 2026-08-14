# Emulator Contract Profile

`emulator-spec.yaml` is the canonical contract owned by `$emulator`.

Its contract fingerprint is the SHA-256 digest of the finalized file's exact UTF-8 bytes.

## Canonical shape

```yaml
emulator_contract:
  packet_version: EC-v1
  contract_id:
  origin: source_faithful | designed | mixed
  source:
    kind: repository | specification | tests | traces | user_design | existing_contract | mixed
    path:
    revision:
    fingerprint:
    evidence_refs: []
    explicit_deviations: []
    discrepancies: []
  target:
    name:
    kind: skill | agent_loop | tool_loop | workflow | library_protocol
  environment:
    reset_semantics: fresh_episode | checkpoint | explicit
    observation_schema:
    action_schema:
    visible_state_schema:
    hidden_state_schema:
    seed_policy:
    terminal_conditions: []
    reward_channels: []
  tools:
    <tool_id>:
      input_schema:
      output_schema:
      permissions:
      side_effect: true | false
      modeled_failures: []
      authority_refs: []
  scenarios:
    - scenario_id:
      case_id:
      description:
      authority_refs: []
      actor_model:
      initial_visible_state:
      hidden_ground_truth:
      user_goal:
      limits:
        max_steps:
        timeout_s:
      expected_behavior: []
      prohibited_behavior: []
      terminal_conditions: []
      hard_oracles: []
      trace_invariants: []
      mutation_dimensions: []
```

## Authority

A normative field cites either source evidence or an explicit user decision.

For source-faithful claims, prefer:

```text
executable tests and captured traces
public runtime interfaces, schemas, and source behavior
non-contradicted normative documentation
examples
```

Record source contradictions under `source.discrepancies`.

For designed or mixed worlds, record intentional departures under `source.explicit_deviations`.

An assumption may explain non-critical description only. It cannot define safety, security, authority, hidden truth, side effects, rewards, or termination.

## Required semantics

The contract must define equivalents of:

```text
reset(scenario_id, seed)
observe()
step(action)
score()
trace()
```

Each scenario defines stable identities, authority references, actor model, initial visible state, hidden truth, goal, limits, terminal conditions, hard oracles, trace invariants, and allowed mutations.

A critical scenario requires a deterministic hard oracle. Safety-critical behavior requires a trace invariant. Reward or final text alone is insufficient.

## Oracles

Prefer:

```text
state_assert
trace_invariant
tool_called / tool_not_called
side_effect_assert
schema_assert
budget_assert
terminal_assert
confirmation_before_side_effect
injection_resistance
```

Model-judged oracles may support criteria that deterministic checks cannot express. They must not be sole authority for safety-critical behavior.

## Rewards

Rewards are optional learning signals. Each channel declares meaning, range, aggregation, and authority.

A reward cannot turn a failed hard oracle into a pass.

## Mutations

Each mutation dimension declares:

```text
id
allowed values or generator
invariants preserved
invariants intentionally violated, if negative
shrink strategy
```

Do not vary undeclared normative behavior and still claim contract conformance.

## Validation gate

Require:

```text
EC-v1, contract id, origin, authority identity and fingerprint, and source revision when applicable
stable scenario and case ids
explicit reset, observation, action, state, and terminal semantics
visible/hidden state separation
tool schemas, permissions, side effects, and modeled failures
seed-controlled nondeterminism
hard oracles for critical scenarios
trace invariants for safety-critical behavior
authority attribution for every normative rule
declared mutation invariants
```

Missing authority or semantics is `source_contract_gap`. Conflicting authority is `contract_ambiguity`.

Do not fill either gap silently.
