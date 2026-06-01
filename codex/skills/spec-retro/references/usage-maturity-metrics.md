# Usage Maturity Metrics

Use these fields in the next `$spec-retro` report so activity volume can be separated from spec quality.

## Activity metrics

- tool calls
- skill mentions
- workflow mentions
- outcomes
- sessions
- signals

## Spec-maturity metrics

- evidence_brief_emitted_count
- decision_packet_emitted_count
- gate_pass_count
- gate_fail_count
- no_grill_justification_count
- actual_grill_round_count
- questions_answered_count
- plan_allowed_without_grill_count
- mutation_before_gate_count
- invariant_challenge_count
- challenge_changed_architecture_count
- fresh_eyes_pass_count
- fresh_eyes_changed_spec_count
- lint_pass_count
- lint_fail_count
- requirements_mapped_to_tests_count
- rollback_present_count
- binary_done_state_present_count

## Subagent governance metrics

- spawned_agents
- consumed_agent_results
- rejected_agent_results
- ignored_agent_results
- timed_out_agents
- open_agents_at_close
- agent_budget_exceeded_count

## Churn metrics

- plan_count_per_session
- update_plan_count_per_session
- objective_changed_after_plan
- title_drift_score
- new_decision_after_plan
- return_to_grill_after_plan
- campaign_mode_triggered

The retrospective question is: does `$spec-pipeline` reduce ambiguity before execution, or does it merely make execution faster?
