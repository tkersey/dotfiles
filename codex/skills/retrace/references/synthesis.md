# Decision Reconstruction: DRR-v1

DRR-v1 separates deterministic source evidence from replay evidence and hindsight.

```yaml
decision_reconstruction_record:
  record_version: DRR-v1
  record_id:
  inquiry_id:
  source_capsule_id:
  question:
  modes: []

  source_governance:
    required:
    gate_id:
    workflow:
    verdict:
    replay_allowed:
    governing_evidence_refs: []
    incidental_evidence_refs: []
    limitations: []

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
    kept_separate: yes

  contradictions: []
  adjudication:
  limitations: []
  confidence:
  allowed_claims: []
  prohibited_claims: []
```

## Source-governance effect

```text
authoritative
  workflow-governed replay claims allowed

declared_uncontrolled
  replay may study why the controller/workflow was not operationally used

incidental / ambiguous / absent
  no valid replay population for workflow-effect claims
```

A classifier row is not itself authoritative. The SGG evidence and provenance decide.

## Route stability

Stable:

```text
all valid pre-decision replays select the historical route
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
no valid outcome-blind replay or source governance blocked replay
```

Always report sample size and lineage modes.

## Skill/workflow effect

Strongest:

```text
historical explicit attribution
+ authoritative governance
+ exact anchor
+ controlled instruction/evidence ablation
+ route change
```

Weak:

```text
fork self-report
consensus without ablation
outcome association
```

## Confidence

Consider source explicitness, governance provenance, anchor exactness, lineage mode, workspace mode, model match, framing diversity, receipt validity, sample size, and counterevidence.
