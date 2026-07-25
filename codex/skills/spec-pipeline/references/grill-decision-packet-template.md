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
  architectonic_authority:
    source_fixed_decision_refs: []
    source_bounded_seam_refs: []
    specification_local_seam_refs: []
  architectonic_seams: []
  conceptual_compression_target:
    live_obligations: []
    maximum_independent_owners:
    prohibited_parallel_truth: []
    prohibited_reconstruction_paths: []
  downstream_open_decisions:
    - seam_ref:
      admissible_space:
      required_observation_refs: []
      forbidden_outcomes: []
      default_action:
      invalidators: []
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
- Every consequential architectonic seam has authority and a selected,
  evidence-conditioned, downstream-open, underdetermined, or obstructed disposition.
- A downstream-open seam names its admissible space, deciding observation, forbidden
  outcomes, default or blocker, and invalidators.
- Every retained abstraction owns a distinct live obligation or is explicitly
  provisional.
- If `grill_rounds: 0`, No-Grill Justification says why the brief is decision-complete.
- Planning is blocked if any high-impact question lacks a default or any
  architectonic seam lacks a lawful disposition.
