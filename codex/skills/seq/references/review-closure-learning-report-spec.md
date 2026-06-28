# Review-Closure Learning Report Spec

When reporting review-closure workflow performance, prefer decision-impact and outcome evidence over invocation counts.

Report shape:

```yaml
review_closure_learning_report:
  report_version: RLR-v1
  window:
  denominator:
  core_outcomes:
  material_improvement:
  cluster_trajectory: []
  finding_to_route_matrix: []
  decision_impact: []
  skill_obligation_matrix: []
  companion_receipts:
  cas_lane_attribution:
  recommendation_carry_forward: []
  report_confidence:
  report_value_score:
  next_experiments:
    - hypothesis:
      change:
      expected_metric_move:
      next_report_measure:
```

Key question:

```text
Did a skill change a route or improve an outcome?
```

Not:

```text
Did a skill appear?
```
