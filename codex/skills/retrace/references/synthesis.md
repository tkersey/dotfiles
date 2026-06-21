# Decision Reconstruction: DRR-v1

```yaml
decision_reconstruction_record:
  record_version: DRR-v1
  record_id:
  inquiry_id:
  source_capsule_id:

  question:
  modes: []

  historical_evidence:
    explicit_at_time: []
    trace_inferred: []
    unknown: []

  fork_population:
    valid_receipts: []
    invalid_receipts: []
    model_distribution: {}
    horizon_distribution: {}
    workspace_distribution: {}

  rationale_reconstruction:
    consensus: []
    disagreements: []
    confidence:

  counterfactual:
    selected_route_distribution: {}
    historical_route_stability:
      stable |
      mixed |
      unstable |
      unavailable
    strongest_alternative:
    route_flip_conditions: []

  skill_and_instruction_effects:
    historically_explicit: []
    ablation_supported: []
    fork_self_report_only: []
    unsupported: []

  hindsight:
    lessons: []
    kept_separate: yes | no

  contradictions: []
  adjudication:
  limitations: []
  confidence:
  allowed_claims: []
  prohibited_claims: []
```

## Route stability

Stable:

```text
all valid pre-decision replays select historical route
```

Mixed:

```text
several supported routes selected
```

Unstable:

```text
most valid pre-decision replays select another route
```

Unavailable:

```text
exact outcome-blind anchor unavailable
```

Small samples must be reported.

## Skill effect

A skill-effect claim is strongest when:

```text
source explicitly attributes route to skill
and/or
controlled instruction ablation changes route
```

Fork self-report without ablation is weak.

## Confidence

Consider:

- source explicitness;
- anchor exactness;
- workspace exactness;
- model match;
- fork agreement;
- counterevidence;
- framing diversity;
- receipt validity;
- sample size.
