# Grill Decision Packet Template

```yaml
spec_decision_packet:
  goal:
  problem_layer:
  target_user_or_maintainer:
  scope:
  non_goals:
  locked_decisions:
    - id:
      decision:
      rationale:
      consequence:
  tradeoffs_accepted:
  primary_invariant:
  success_criteria:
  proof_bar:
  compatibility_posture:
  rollout_rollback_posture:
  open_questions:
    - id:
      question:
      owner:
      default_action:
      consequence:
  deferred_questions:
  default_assumptions:
  clarification_receipt:
    grill_rounds:
    no_grill_justification:
```

Completion bar:

- Each material ambiguity is answered, researched, assumed, deferred, or immaterial.
- Each open question has owner, default, and consequence.
- If `grill_rounds: 0`, No-Grill Justification says why the brief is decision-complete.
- Planning is blocked if any high-impact question lacks a default.
