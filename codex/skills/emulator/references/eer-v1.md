# EER-v1: Emulator Execution Report

`emulator_execution_report / EER-v1` records what contract and environment ran, what each episode did, where agents or implementations diverged, and which findings are reusable.

## Schema

```yaml
emulator_execution_report:
  packet_version: EER-v1
  source_contract:
    kind: emulator_contract
    spec_ref:
    contract_id:
    fingerprint:
    source_revision:
    authority_refs: []
  target:
    name:
    kind:
  emulator:
    version:
    implementation_ids: []
    seed:
    seed_policy:
    oracle_version:
  agents:
    - id:
      fingerprint:
      limitations: []
  run_summary:
    generated_cases:
    executed_cases:
    passed_cases:
    failed_cases:
    skipped_cases:
  executions:
    - episode_id:
      scenario_id:
      case_id:
      implementation_id:
      agent_id:
      agent_fingerprint:
      seed:
      status: pass | fail | skip
      termination_reason:
      reward_total:
      action_trace_ref:
      oracle_results_ref:
      trace_ref:
      skipped_reason:
  implementations:
    - id:
      kind: deterministic | noisy | adversarial | mutation
      contract_fingerprint:
      supported_scenarios: []
      limitations: []
  divergences:
    - divergence_id:
      scenario_id:
      case_id:
      implementations: []
      agents: []
      observed_difference:
      likely_source:
        contract_ambiguity | emulator_bug | oracle_gap | nondeterminism | behavior_gap | source_contract_gap
      evidence_refs: []
  counterexamples:
    - counterexample_id:
      scenario_id:
      case_id:
      minimal_inputs:
      violated_oracles: []
      trace_ref:
      reproducible_command:
  candidate_regressions:
    - case_id:
      source_counterexample:
      why_reusable:
      required_oracles: []
  datasets:
    trajectories_ref:
    counterexamples_ref:
    curriculum_ref:
  limitations: []
  optional_downstream:
    tune_handoff:
      available: yes | no
      reason:
```

## Accounting rules

- Every episode appears in `executions`.
- Summary counts equal execution counts.
- Every pass or failure has a trace and recorded action sequence.
- Every skip has a reason.
- Every execution binds contract, implementation, agent, scenario, case, seed, and oracle identities.
- Every counterexample binds violated oracles and reproducible evidence.
- Dataset references appear only for emitted datasets.

## Interpretation

EER-v1 is behavioral evidence, not proof that a target skill or production system should change.

A failed episode may indicate an emulator bug, contract ambiguity, oracle gap, nondeterminism, behavior gap, or missing source contract.

Reward never overrides a failed hard oracle.

A candidate regression becomes binding only after adoption into `emulator-spec.yaml`.

`$tune` handoff requires explicit skill-improvement intent.
