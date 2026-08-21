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
    invocation_mode: design | implement | run | mutate | compare | export
    evidence_mode: design | implement | run | mutate | compare
    source_eer_ref:  # non-null only when invocation_mode is export
    source_eer_fingerprint:
    atlas_chart_fingerprints: []
    closure_inventory_ref:
    closure_inventory_fingerprint:

  comparison:  # present only for one baseline/candidate compare pair
    comparison_id:
    factor:
    baseline_harness_fingerprint:
    candidate_harness_fingerprint:
    recommendation: adopt | reject | insufficient_evidence
    study_relation: paired_replay_delta | observed_association
    outcome: improved | regressed | noninferior | ambiguous | invalid
    evidence_relation: paired_replay_delta | observed_association | regression | insufficient_evidence
    authority_granted: false

  run_group_id:  # non-null for standalone run/mutate; null otherwise

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
      run_group_id:
      comparison_id:
      chart_id:
      chart_fingerprint:
      chart_kind:
      partition:
      split_group:
      harness_id:
      harness_fingerprint:
      repeat_id:
      factor:
      randomness_cohort_ref:
      randomness_cohort_fingerprint:
      mutation_assignment_ref:
      mutation_assignment_fingerprint:
      implementation_fingerprint:
      runtime_fingerprint:
      actor_seed:
      actor_seed_control: fixed | sampled | unavailable
      environment_seed:
      environment_seed_control: fixed | sampled | unavailable
      failure_schedule_ref:
      failure_schedule_fingerprint:
      failure_schedule_control: fixed | sampled | unavailable | none
      world_fingerprint:
      actor_input_fingerprint:
      actor_readable_inventory_fingerprint:
      actor_access_proof_ref:
      evaluator_fingerprint:
      support_result:
      status: pass | hard_fail | unsupported_counterfactual | invalid_environment | runtime_error | ambiguous | skipped
      termination_reason:
      terminal_condition_id:
      terminal_evidence_ref:
      terminal_evidence_fingerprint:
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
For each paired chart/repeat, baseline and candidate rows bind the same
`randomness_cohort_ref`/fingerprint. The ref resolves exact
`randomness-cohort/v1` bytes containing chart fingerprint, repeat ID, actor and
environment seed controls plus realized seeds, failure-schedule control and
fingerprint, and every runner-declared outcome-affecting randomness source.
Controlled realized values are equal across arms. If any required source is
`unavailable`, `paired_replay_delta` is forbidden; only adequately repeated
`observed_association` may describe the study. A mismatch is
`comparison_drift`.
Fixed realized seeds equal the chart values. Sampled seeds and schedules are
deterministic projections of chart-bound sampling policies plus repeat ID;
unavailable values are null.

The EC-v1 root is reusable and does not contain an operation mode.
`invocation_mode` is the selected request route. `evidence_mode` selects report
and row ownership. They are equal except for deferred export: then
`invocation_mode: export`, `evidence_mode` equals the referenced source EER's
run/mutate/compare mode, and the source EER pair is non-null and resolves exact
sealed bytes. The source pair is null otherwise.
An export EER projects contract identity, chart fingerprints, closure inventory,
comparison/run-group ownership, executions, chart comparisons, limitations,
and evidence fields byte-identically from that source EER; only authorized
dataset refs are new. Current atlas state cannot replace source evidence.

`run` mode omits `comparison` and emits executions plus applicable datasets and
limitations. It does not invent a candidate fingerprint or recommendation.
Each `compare` EER binds exactly one baseline/candidate pair. When a request
evaluates multiple candidates, emit one EER and one `comparison.json` per
candidate so every delta and recommendation has a single arm owner.

## runs.jsonl

Each fresh run emits one append-only row. Compare rows live under their
comparison directory and bind non-null `comparison_id` and `factor`. Standalone
`run`/`mutate` rows live under `runs/<run-group-id>/`, bind non-null
`run_group_id`, and omit `comparison_id` and `factor`.

```json
{
  "schema": "emulator-run/v1",
  "run_id": "run-...",
  "run_group_id": null,
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
  "randomness_cohort_ref": "runs/cmp-.../randomness/<chart-fingerprint-hex>/repeat-1.json",
  "randomness_cohort_fingerprint": "sha256:...",
  "mutation_assignment_ref": null,
  "mutation_assignment_fingerprint": null,
  "implementation_fingerprint": "sha256:...",
  "runtime_fingerprint": "sha256:...",
  "actor_seed": null,
  "actor_seed_control": "unavailable",
  "environment_seed": 7,
  "environment_seed_control": "fixed",
  "failure_schedule_ref": null,
  "failure_schedule_fingerprint": null,
  "failure_schedule_control": "none",
  "world_fingerprint": null,
  "actor_input_fingerprint": "sha256:...",
  "actor_readable_inventory_fingerprint": "sha256:...",
  "actor_access_proof_ref": "traces/run-...-access.json",
  "evaluator_fingerprint": "sha256:...",
  "support_result": "judgeable",
  "status": "pass",
  "termination_reason": "decision_emitted",
  "terminal_condition_id": null,
  "terminal_evidence_ref": null,
  "terminal_evidence_fingerprint": null,
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
The displayed row is the compare variant. In standalone mode `run_group_id` is
non-null and the comparison/factor keys are absent; in compare mode
`run_group_id` is null and comparison/factor are non-null. Mixed ownership is
invalid. `contract.evidence_mode` selects the variant and cannot be inferred
from omitted fields.
The report-level standalone `run_group_id` equals every execution and runs.jsonl
row it summarizes. Mutation assignment fields are non-null for every mutate row
after assignment creation and resolve one `mutation-assignment/v1` artifact.
A mutate attempt failing before assignment records both null only with
`status: invalid_environment` and `status_reason: mutation_assignment_unavailable`.
They are null for non-mutate rows.
Actor/environment seed keys are always serialized and are null exactly when
their corresponding control is `unavailable`. A sampled control may also have a
null seed only on a pre-allocation `invalid_environment` row with
`status_reason: seed_allocation_unavailable`; all other sampled rows bind the
realized seed.

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
  "study_relation": "paired_replay_delta | observed_association",
  "outcome": "improved | regressed | noninferior | ambiguous | invalid",
  "evidence_relation": "paired_replay_delta | observed_association | regression | insufficient_evidence",
  "reason": "",
  "authority_granted": false
}
```

`comparison.json.evidence_relation` equals the EER comparison field exactly;
the standalone artifact is not a lossy projection.

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
For `full_episode`, `status: pass` requires non-null terminal condition ID and
evidence resolving the declared predicate result. Reaching only max steps or
timeout without a true terminal condition is `hard_fail` when the healthy actor
exhausted the bound, and `runtime_error` only when infrastructure failed to
deliver the contracted budget.

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

Recommendation precedence is total: witnessed new hard failure, protected
regression, or ordinary targeted outcome regression yields `reject` first, even when coverage is also incomplete; absent
such regression, incomplete or indeterminate required evidence yields
`insufficient_evidence`; only then may `adopt` be considered. `reject` pairs
with `evidence_relation: regression`; `insufficient_evidence` pairs with
`insufficient_evidence`; `adopt` pairs with `paired_replay_delta` for matched
cohorts or `observed_association` for adequately repeated uncontrolled
stochastic evidence. All other pairs are invalid.
`study_relation` independently preserves paired versus uncontrolled study
design for every outcome, including regressions; `outcome` preserves direction.
Both fields are identical in EER and comparison.json.
Admissible four-field tuples are exactly:

- `adopt + improved + paired_replay_delta + paired_replay_delta`;
- `adopt + improved + observed_association + observed_association`;
- `reject + regressed + <either study_relation> + regression`;
- `insufficient_evidence + noninferior|ambiguous|invalid + <either study_relation> + insufficient_evidence`.

No other recommendation/outcome/study/evidence combination is valid.

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
