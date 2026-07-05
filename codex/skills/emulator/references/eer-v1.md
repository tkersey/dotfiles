# EER-v1: Emulator Execution Report

`emulator_execution_report / EER-v1` is the default evidence artifact emitted by `$emulator`.

It records what was run, what happened, where implementations diverged, and which findings are reusable.

## Schema

```yaml
emulator_execution_report:
  packet_version: EER-v1
  source_contract:
    kind: ghost_package | ghost_scenario_tests | emulator_contract
    spec_ref:
    tests_ref:
    verify_ref:
    fingerprint:
  target:
    name:
    kind:
  emulator:
    version:
    implementation_ids: []
    seed:
    oracle_version:
  run_summary:
    generated_cases:
    executed_cases:
    passed_cases:
    failed_cases:
    skipped_cases:
  implementations:
    - id:
      kind: deterministic | noisy | adversarial | mutation
      source_contract_fingerprint:
      supported_scenarios: []
      limitations: []
  divergences:
    - divergence_id:
      scenario_id:
      case_id:
      implementations: []
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
  limitations: []
  optional_downstream:
    tune_handoff:
      available: yes | no
      reason:
```

## Interpretation rules

- EER-v1 is behavioral evidence, not proof that a target skill should change.
- A failed emulator run may indicate an emulator bug, a contract ambiguity, an oracle gap, nondeterminism, or a real behavior gap.
- A candidate regression becomes binding only after the downstream owner adopts it.
- `$tune` handoff is optional and requires explicit skill-improvement intent.
