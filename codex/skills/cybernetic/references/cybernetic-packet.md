# Cybernetic Packet

Use `cybernetic_context` for compact handoffs and `cybernetic_packet` for fuller analysis.

The canonical full packet fields remain defined in `SKILL.md`. This reference adds the optional DART interaction trace and epistemic records without creating another authority.

See [dart-interaction-layer.md](dart-interaction-layer.md) for the stage completion contract.

## Compact

```yaml
cybernetic_context:
  required:
  trigger:
  dart_trace_ref: # optional
  system_type:
  pattern:
  feedback_loop:
  leverage_level:
  selected_intervention:
    status: selected | observe_more | stabilize | blocked | no_action
    route:
    downstream_skill:
  local_patch_allowed:
  temporary_containment:
    allowed: yes | no | not_applicable
    expiry_or_review:
    durable_followup_owner:
  monitoring_or_probe:
```

## Optional DART trace

```yaml
dart_trace:
  trace_version: DART-CYB-v1
  deconstruct:
    boundary:
    components: []
    connections: []
    repeating_pattern:
    missing_information: []
  analyze:
    classification:
    classification_evidence: []
    subsystem_classifications: []
    alternative_classification:
    confidence:
    information_that_could_flip_classification: []
  recognize:
    analogous_pattern:
    shared_mechanism:
    transferable_features: []
    important_differences: []
    likely_next_state_if_unchanged:
    early_warning_signals: []
    analogy_confidence:
  test:
    mode: process_verification | hypothesis_validation | safe_to_fail_probe | emergency_stabilization
    action:
    hypothesis_or_control_goal:
    predicted_observation:
    observation_window:
    success_signal:
    failure_signal:
    stop_condition:
    rollback_or_adapt:
```

## Epistemic claim record

Use this record for consequential causal claims:

```yaml
cybernetic_claim:
  statement:
  status: observed | inferred | hypothesized | unknown
  evidence_refs: []
  confidence: high | medium | low | unknown
  competing_explanations: []
  disconfirming_observation:
```

## Learning update

A probe should compare the registered prediction with the actual observation.

```yaml
cybernetic_learning_update:
  hypothesis_ref:
  predicted_observation:
  actual_observation:
  prediction_error:
  model_update:
  classification_update:
  intervention_update:
  next_review:
```

## Full

```yaml
cybernetic_packet:
  packet_version: CYB-v1
  objective:
  system_boundary:
  system_type:
  dart_trace_ref: # optional
  observed_events: []
  repeating_patterns: []
  hidden_structure:
  stocks_and_flows:
  feedback_loops:
  incentives_and_gameability:
  leverage_map:
  intervention_design:
  test_or_monitoring_plan:
  decision:
```

DART compiles into this packet. It does not replace the packet's leverage, incentives, whole-system, reversibility, blast-radius, mutation-policy, or downstream-owner decisions.
