# DART Interaction Layer

Use DART as the conversational front end for `$cybernetic`.

DART means:

```text
Deconstruct -> Analyze -> Recognize -> Test
```

It structures how the agent gathers and presents the diagnosis. It does not create a second decision authority, replace `cybernetic_context`, select implementation architecture, or grant mutation.

The output of DART must compile into the existing Cybernetic context and packet.

## When to use this layer

Use the DART interaction layer when:

- the user presents an ambiguous situation rather than an already-scoped route;
- classification depends on missing information;
- the system may be mixed across technical, social, operational, or incident subsystems;
- a safe probe, expert validation, process verification, or stabilization action must be selected;
- an analogy or prior pattern is useful but could overfit the current situation.

Skip the expanded DART trace when:

- Cybernetic is only a compact companion lens and the route is already evidenced;
- the task is one clear local defect with a direct owner and proof;
- an active chaotic incident requires immediate containment before fuller diagnosis.

Even when the expanded trace is skipped, preserve the DART ordering internally: scope before classification, classification before analogy, and analogy before intervention.

## Completion contract

A valid DART pass completes all four stages.

```yaml
dart_trace:
  trace_version: DART-CYB-v1

  deconstruct:
    boundary:
      included: []
      excluded: []
      boundary_risk: too_narrow | too_broad | adequate | unknown
    components:
      - component: "..."
        stability: stable | slowly_changing | volatile | episodic | unknown
        change_driver: "..."
        evidence_ref: "..."
    connections:
      - from: "..."
        to: "..."
        relationship: "..."
        latency: "..."
        evidence_ref: "..."
    repeating_pattern: "..."
    missing_information: []

  analyze:
    classification: clear | complicated | complex | chaotic | mixed | unknown
    classification_evidence: []
    subsystem_classifications:
      - subsystem: "..."
        classification: clear | complicated | complex | chaotic | unknown
        reason: "..."
        confidence: high | medium | low | unknown
    alternative_classification:
      classification: clear | complicated | complex | chaotic | mixed | unknown
      condition_that_would_make_it_true: "..."
    confidence: high | medium | low | unknown
    information_that_could_flip_classification: []

  recognize:
    analogous_pattern: "..."
    shared_mechanism: "..."
    transferable_features: []
    important_differences: []
    likely_next_state_if_unchanged: "..."
    early_warning_signals: []
    analogy_confidence: high | medium | low | unknown

  test:
    mode: process_verification | hypothesis_validation | safe_to_fail_probe | emergency_stabilization
    action: "..."
    hypothesis_or_control_goal: "..."
    predicted_observation: "..."
    observation_window: "..."
    success_signal: "..."
    failure_signal: "..."
    stop_condition: "..."
    rollback_or_adapt: "..."
```

Do not fill fields with invented certainty. Use `unknown`, identify missing information, or ask a discriminating question.

## D — Deconstruct

Deconstruct the system before choosing its type.

Identify:

- the boundary and its exclusions;
- actors, components, variables, institutions, interfaces, and decision owners;
- stable, slowly changing, volatile, and episodic components;
- connections and information paths;
- repeating events and the pattern they imply;
- stocks, flows, buffers, queues, delays, and bottlenecks;
- missing observations.

Component stability is evidence, not a classifier by itself. Stable components can still create complex behavior through changing or nonlinear interactions.

### Minimum discriminating question

Ask a clarifying question only when the answer could materially change:

- the system classification;
- the leverage level;
- the mutation policy;
- the downstream owner;
- the safe probe or stabilization action.

Prefer one high-information question over a general interview.

```yaml
discriminating_question:
  question: "..."
  route_if_answer_a: "..."
  route_if_answer_b: "..."
  proceed_without_answer: yes | no
  uncertainty_if_proceeding: "..."
```

Do not ask for information that is merely interesting.

## A — Analyze

Classify the cause-and-effect regime:

| Classification | Evidence shape | First mode |
|---|---|---|
| clear | stable, repeatable, directly observable | process verification |
| complicated | discoverable through analysis or specialist knowledge | hypothesis validation |
| complex | emergent, path-dependent, visible mainly in hindsight | safe-to-fail probe |
| chaotic | active instability, broken information, or unbounded harm | emergency stabilization |
| mixed | materially different subsystem regimes | split by subsystem |

Record evidence for the classification and one credible alternative. A classification without a possible falsifier is a label, not a diagnosis.

For mixed systems, do not collapse the answer into one overall type. Classify the relevant subsystems separately and state the cross-subsystem coupling.

## R — Recognize

Use analogies to generate hypotheses, not to import conclusions.

A valid analogy names:

- the shared mechanism;
- the features that transfer;
- the important disanalogies;
- the conditions required for transfer;
- what is likely to happen next if the pattern continues;
- an observation that would invalidate the analogy.

When no useful analogue is available, say so. Do not force an archetype.

## T — Test

Match the test mode to the system type.

### Clear: process verification

Verify that the known process, invariant, or checklist is being followed. The result should distinguish execution error from a defective standard.

### Complicated: hypothesis validation

Test competing causal hypotheses with analysis, specialist review, or a targeted measurement. Do not select an intervention merely because it is plausible.

### Complex: safe-to-fail probe

Use a bounded, reversible, observable probe. Register the expected observation before the probe, avoid premature scale-up, and adapt from the result.

### Chaotic: emergency stabilization

Act to contain harm immediately, but monitor concurrently.

```yaml
chaotic_response:
  immediate_containment: "..."
  concurrent_monitoring: "..."
  containment_expiry_or_review: "..."
  durable_fix_selection: deferred
  reclassification_trigger: "..."
```

`No time to test` does not mean `no observation`. Stabilization needs live feedback so the action can be stopped, reversed, or replaced.

## Sentinel indicators

Prefer a low-cost signal that reveals an important latent system property.

```yaml
sentinel_indicator:
  signal: "..."
  latent_property_revealed: "..."
  why_diagnostic: "..."
  expected_range: "..."
  false_positive_risk: "..."
  false_negative_risk: "..."
  collection_cost: low | medium | high | unknown
  decision_trigger: "..."
```

Treat data as observations produced by a measurement system, not as direct access to truth. Scan for instrumentation gaps, proxy substitution, sampling bias, reporting incentives, and delayed effects.

## Compile into Cybernetic

The DART trace is evidence and interaction structure. Cybernetic remains the leverage and routing owner.

Compile:

```text
D boundary + components
  -> cybernetic system_boundary, hidden_structure, stocks_and_flows

A classification
  -> cybernetic system_type and required mode

R mechanism + trajectory
  -> repeating_patterns, mental_models, feedback hypotheses, confidence

T action + registered observation
  -> intervention_design and test_or_monitoring_plan
```

The final Cybernetic output must still decide:

- leverage level;
- whole-system effects;
- incentives and gameability;
- durable local mutation policy;
- temporary containment policy when relevant;
- downstream owner;
- monitoring and stop conditions.

## Rendering modes

### Standalone user analysis

Render the result in plain language:

```text
Deconstruct
Analyze
Recognize
Test
Cybernetic Bottom Line
```

Do not expose a large YAML packet unless the user or a downstream machine contract needs it.

### Companion-skill handoff

Emit compact `cybernetic_context` plus `dart_trace_ref` when the trace is material.

### Machine or policy handoff

Emit the complete versioned packet and bind it to the current subject and evidence state.

## Guardrails

- DART is not a second authority.
- Do not activate Cybernetic for every local task merely because every task can be described as a system.
- Do not treat component stability as proof of a clear or complicated system.
- Do not use recognition as permission to copy a prior solution.
- Do not call an unregistered action an experiment.
- Do not scale a complex-system probe before reading its feedback.
- Do not let emergency containment silently become the durable fix.
- Do not treat data, mentors, or elapsed time as infallible evidence.
- Do not replace Cybernetic's mixed-system, incentive, reversibility, blast-radius, and downstream-owner disciplines with a simpler DART summary.
