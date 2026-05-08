# Spec Handoff Packet Template

```yaml
spec_handoff_packet:
  handoff_sentence: "We are building X, for Y, by changing Z, while explicitly not doing A/B/C, and success means P/Q/R proofs pass."
  goal:
  problem_layer:
  target_user_or_maintainer:
  change_surface:
  scope:
  non_goals:
  locked_decisions:
  primary_invariant:
  success_criteria:
  proof_bar:
  compatibility_posture:
  rollout_rollback_posture:
  open_questions:
  deferred_questions:
  default_assumptions:
  strictness_profile: fast | balanced | strict
  plan_allowed: false
```

`plan_allowed` becomes true only when the handoff sentence is concrete and material open questions have defaults or deferrals.
