# EER-v1: Emulator Execution Report

`emulator_execution_report / EER-v1` records the exact atlas closure, fresh
harness runs, chart eligibility, hard-oracle and state results, and bounded
recommendation. No deployed report corpus exists, so the EER-v1 label is
corrected in place.

## Schema

```yaml
emulator_execution_report:
  packet_version: EER-v1

  contract:
    ref:
    fingerprint:
    atlas_chart_fingerprints: []
    closure_inventory_ref:
    closure_inventory_fingerprint:

  comparison:  # present only for one baseline/candidate compare pair
    comparison_id:
    factor:
    baseline_harness_fingerprint:
    candidate_harness_fingerprint:
    recommendation: adopt | reject | insufficient_evidence
    evidence_relation: paired_replay_delta | observed_association | regression | insufficient_evidence
    authority_granted: false

  run_summary:
    valid_runs:
    invalid_environment_runs:
    unsupported_runs:
    passed_runs:
    hard_failed_runs:
    ambiguous_runs:
    runtime_error_runs:
    skipped_runs:

  executions:
    - run_id:
      chart_id:
      chart_fingerprint:
      chart_kind:
      partition:
      split_group:
      harness_id:
      harness_fingerprint:
      repeat_id:
      implementation_fingerprint:
      runtime_fingerprint:
      seed:
      seed_control: fixed | sampled | unavailable
      failure_schedule_fingerprint:
      world_fingerprint:
      actor_input_fingerprint:
      actor_readable_inventory_fingerprint:
      actor_access_proof_ref:
      evaluator_fingerprint:
      support_result:
      status: pass | hard_fail | unsupported_counterfactual | invalid_environment | runtime_error | ambiguous | skipped
      termination_reason:
      status_reason:
      hard_oracle_results_ref:
      state_diff_ref:
      trace_ref:
      cost:
      limitations: []

  chart_comparisons:
    - chart_id:
      eligibility:
      baseline_runs: []
      candidate_runs: []
      hard_delta:
      state_delta:
      protected_regressions: []
      residual_preference:
      result: improved | regressed | noninferior | ambiguous | invalid

  datasets:
    preferences_ref:
    trajectories_ref:
    curriculum_ref:

  limitations: []
```

## Status and accounting laws

Every fresh run appears exactly once.

```text
valid_runs = passed_runs + hard_failed_runs + ambiguous_runs

total execution rows =
  valid_runs
  + invalid_environment_runs
  + unsupported_runs
  + runtime_error_runs
  + skipped_runs
```

`unsupported_counterfactual` and `invalid_environment` are not agent failures.
The former means an attempted action had `observed_only` or `unsupported`
support; the latter means the chart, closure, visibility, reset, or comparison
boundary was malformed or unverifiable.

Every pass or hard failure has a fresh trace. Every invalid, unsupported,
runtime-error, ambiguous, or skipped row records a reason and the evidence
available before termination. No historical run appears as a baseline
execution.

Every comparison binds exact chart, root closure, harness, world/reset, actor
input, actor-readable inventory, evaluator, runtime, repeat, effect policy, and
split fingerprints. Selecting and training claims require an access proof that
the actor could not read evaluator-only roots.

`run` mode omits `comparison` and emits executions plus applicable datasets and
limitations. It does not invent a candidate fingerprint or recommendation.
Each `compare` EER binds exactly one baseline/candidate pair. When a request
evaluates multiple candidates, emit one EER and one `comparison.json` per
candidate so every delta and recommendation has a single arm owner.

## runs.jsonl

Each fresh run emits one append-only row within its comparison directory:

```json
{
  "schema": "emulator-run/v1",
  "run_id": "run-...",
  "comparison_id": "cmp-...",
  "chart_id": "chart-...",
  "chart_fingerprint": "sha256:...",
  "chart_kind": "normative_decision",
  "partition": "holdout",
  "split_group": "group-...",
  "harness_id": "candidate-1",
  "harness_fingerprint": "sha256:...",
  "factor": "question_policy",
  "repeat_id": 1,
  "implementation_fingerprint": "sha256:...",
  "runtime_fingerprint": "sha256:...",
  "seed": null,
  "seed_control": "unavailable",
  "failure_schedule_fingerprint": null,
  "world_fingerprint": null,
  "actor_input_fingerprint": "sha256:...",
  "actor_readable_inventory_fingerprint": "sha256:...",
  "actor_access_proof_ref": "traces/run-...-access.json",
  "evaluator_fingerprint": "sha256:...",
  "support_result": "judgeable",
  "status": "pass",
  "termination_reason": "decision_emitted",
  "status_reason": null,
  "hard_oracle_results_ref": "oracle-results/run-....json",
  "state_diff_ref": null,
  "trace_ref": "traces/run-....json",
  "cost": {
    "input_tokens": null,
    "output_tokens": null,
    "latency_ms": null
  },
  "limitations": []
}
```

These rows are not a new global event store.

## comparison.json

```json
{
  "schema": "emulator-harness-comparison/v1",
  "comparison_id": "cmp-...",
  "contract_fingerprint": "sha256:...",
  "factor": "question_policy",
  "baseline_harness_fingerprint": "sha256:...",
  "candidate_harness_fingerprint": "sha256:...",
  "eligible_chart_ids": [],
  "excluded_charts": [
    {"chart_id": "...", "reason": "unsupported_counterfactual"}
  ],
  "targeted_improvements": [],
  "protected_regressions": [],
  "hard_oracle_delta": {},
  "state_delta": {},
  "cost_delta": {},
  "residual_preference": {
    "result": "candidate | baseline | tie | ambiguous",
    "order_stable": true,
    "evidence_refs": []
  },
  "recommendation": "adopt | reject | insufficient_evidence",
  "reason": "",
  "authority_granted": false
}
```

## Evaluation order

```text
1. environment and recursive closure validity
2. exclusive action support
3. hard oracles
4. state diff
5. trace invariants
6. protected dimensions
7. cost and latency
8. residual blinded model or human judgment
```

Hard failures and protected regressions cannot be repaired by later stages. A
residual judge is never sole authority, receives hard-oracle results, is blinded
to harness identity, and is run in both presentation orders. Order disagreement
is `ambiguous`.

## Recommendation authority

`adopt` requires complete environment-valid baseline and candidate arms for
every required chart and repeat, no new hard-oracle failure of any kind, no
protected regression, at least one targeted untouched holdout improvement,
order-stable residual preference when used, and evaluation of the exact
candidate fingerprint.

A missing or invalid required arm, tie, unsupported required chart, evaluator
disagreement, closure/access proof gap, or insufficient untouched holdout
coverage yields `insufficient_evidence`. Any new candidate hard-oracle failure
or protected regression yields `reject`.

`recommendation` remains the adoption disposition enum. `evidence_relation`
records `paired_replay_delta`, `observed_association`, `regression`, or
`insufficient_evidence`; it is not a causal claim. Neither field grants
mutation, merge, release, or publication authority.

## Datasets

Dataset references appear only when rows were emitted:

- Preference rows require direct authority, an exact source-bound rejected
  action, and a fresh passing chosen action that passed hard oracles.
- Trajectory rows require fresh valid executable runs with reset and complete
  observable trace evidence.
- Active holdouts and hidden evaluator material are never exported.
- Historical assistant responses are not chosen labels merely because they
  occurred.

Every row retains chart, authority, closure, harness, and evidence provenance.
