# EER-v1: Emulator Execution Report

`emulator_execution_report / EER-v1` records the exact atlas closure, fresh
subject runs, chart eligibility, hard-oracle and state results, and bounded
recommendation. No deployed report corpus exists, so the EER-v1 label is
corrected in place.

## Schema

```yaml
emulator_execution_report:
  packet_version: EER-v1

  contract:
    ref:
    fingerprint:
    operation_mode: design | implement | run | mutate | compare
    atlas_chart_fingerprints: []
    closure_inventory_ref:
    closure_inventory_fingerprint:

  runs:
    ref:
    fingerprint:

  comparison:  # present only for one baseline/candidate compare pair
    comparison_id:
    subject: harness
    factor:
    atlas_fingerprint:
    partition_snapshot_fingerprint:  # selecting roots only
    partition_validation_ref:        # selecting roots only
    partition_validation_fingerprint: # selecting roots only
    partition_claim_refs: []          # selecting roots only
    partition_claim_fingerprints: []  # selecting roots only
    partition_claim_validation_ref:   # selecting roots only
    partition_claim_validation_fingerprint: # selecting roots only
    holdout_reservation_ref:          # holdout runs only
    holdout_reservation_fingerprint:  # holdout runs only
    holdout_lock_refs: []              # holdout runs only
    holdout_lock_fingerprints: []      # holdout runs only
    holdout_lock_validation_ref:       # holdout runs only
    holdout_lock_validation_fingerprint: # holdout runs only
    actor_access_proof_ref:
    actor_access_proof_fingerprint:
    baseline_harness_fingerprint:
    candidate_harness_fingerprint:
    factor_delta_validation_ref:
    factor_delta_validation_fingerprint:
    recommendation: adopt | reject | insufficient_evidence
    evidence_relation: paired_replay_delta | observed_association | regression | insufficient_evidence
    reason:
    authority_granted: false
    evaluated_runs:
      baseline: []
      candidate: []
    eligible_chart_ids: []
    excluded_charts: []
    targeted_improvements: []
    protected_regressions: []
    hard_oracle_delta: {}
    state_delta: {}
    reward_delta: {}
    trace_invariant_delta: {}
    cost_delta: {}
    residual_preference: {}
    chart_comparisons:
      - chart_id:
        eligibility:
        baseline_runs: []
        candidate_runs: []
        hard_delta:
        state_delta:
        reward_delta:
        protected_regressions: []
        residual_preference:
        result: improved | regressed | noninferior | ambiguous | invalid

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
    - schema: emulator-run/v1
      run_id:
      run_group_id:
      comparison_id:
      contract_fingerprint:
      atlas_fingerprint:
      chart_id:
      chart_fingerprint:
      chart_kind:
      partition:
      split_group:
      partition_snapshot_fingerprint:  # selecting roots only
      partition_validation_ref:        # selecting roots only
      partition_validation_fingerprint: # selecting roots only
      partition_claim_refs: []          # selecting roots only
      partition_claim_fingerprints: []  # selecting roots only
      partition_claim_validation_ref:   # selecting roots only
      partition_claim_validation_fingerprint: # selecting roots only
      holdout_reservation_ref:          # holdout runs only
      holdout_reservation_fingerprint:  # holdout runs only
      holdout_lock_refs: []              # holdout runs only
      holdout_lock_fingerprints: []      # holdout runs only
      holdout_lock_validation_ref:       # holdout runs only
      holdout_lock_validation_fingerprint: # holdout runs only
      harness_id:
      harness_fingerprint:
      factor:
      repeat_id:
      mutation_case_id:
      mutation_assignment:
      mutation_generator_fingerprint:
      minimized_counterexample_ref:
      minimized_counterexample_fingerprint:
      implementation_fingerprint:
      runtime_fingerprint:
      actor_seed:
      actor_seed_control: fixed | sampled | unavailable
      environment_seed:
      environment_seed_control: fixed | sampled | unavailable
      failure_schedule_fingerprint:
      world_fingerprint:
      reset_recipe_fingerprint:
      admission_reset_refs: []         # exact-fidelity executable charts
      admission_reset_fingerprints: [] # exact-fidelity executable charts
      reset_result_ref:
      reset_result_fingerprint:
      effect_policy_fingerprint:
      actor_input_fingerprint:
      actor_readable_inventory_ref:
      actor_readable_inventory_fingerprint:
      actor_access_proof_ref:
      actor_access_proof_fingerprint:
      evaluator_fingerprint:
      support_result:
      status: pass | hard_fail | unsupported_counterfactual | invalid_environment | runtime_error | ambiguous | skipped
      termination_reason:
      status_reason:
      hard_oracle_results_ref:
      hard_oracle_results_fingerprint:
      state_diff_ref:
      state_diff_fingerprint:
      trace_invariant_results_ref:
      trace_invariant_results_fingerprint:
      trace_ref:
      trace_fingerprint:
      reward:  # null when reward is disabled
        definition_fingerprint:
        channels: {}
        aggregate:
      cost:
      limitations: []

  datasets:
    preferences_ref:
    preferences_fingerprint:
    trajectories_ref:
    trajectories_fingerprint:
    curriculum_ref:
    curriculum_fingerprint:
    counterexamples_ref:
    counterexamples_fingerprint:

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

Every execution row binds its root contract and atlas fingerprints. A selecting
root also binds its current partition-snapshot fingerprint and validation
artifact; roots without holdout omit partition-snapshot, validation, and
reservation fields. Every comparison binds the exact declared harness bundle,
chart, root closure, world/reset, actor
input, actor-readable inventory, evaluator, runtime, repeat, effect policy, and
split fingerprints. Selecting and training claims require an access proof that the actor
could not read evaluator-only roots; both its reference and exact fingerprint
are recorded and verified. Every emitted dataset reference has a companion
fingerprint.

Selecting runs bind the exact validation artifact that proves the atlas's
current pointer resolved to the root-bound immutable partition snapshot, plus
every source-identity partition claim and the artifact validating those claims
against the frozen pre-candidate policy. Holdout runs additionally bind the exclusive pre-exposure reservation, every canonical
cross-atlas lock ref and fingerprint, and a validation artifact proving those
locks matched the root, source groups, and reservation before exposure. Missing
or mismatched evidence makes selecting use invalid rather than silently reusing
a stale or consumed group.

The report binds the exact emitted `runs.jsonl` bytes. Its parsed rows MUST equal
`executions` in order and content. Every executable run also binds the observed
reset-result/pre-state artifact; a missing or mismatched result is
`invalid_environment`, even when the reset recipe itself is unchanged.
Every exact-fidelity executable run additionally binds the two distinct,
byte-identical-prestate admission reset artifacts required before chart
admission; missing or duplicate proof refs invalidate the fidelity claim.

`run` mode omits `comparison` and emits executions plus applicable datasets and
limitations. It does not invent a candidate fingerprint or recommendation.
Each `compare` EER binds exactly one baseline/candidate pair. When a request
evaluates multiple candidates, emit one EER and one `comparison.json` per
candidate so every delta and recommendation has a single arm owner.

## runs.jsonl

Each fresh run emits one append-only row under `runs/<run-group-id>/`. Compare
mode uses the comparison ID as the run-group ID; standalone run mode uses an
independent run-group ID, stores its report under `reports/<run-group-id>/`,
and leaves comparison-only fields null:

```json
{
  "schema": "emulator-run/v1",
  "run_id": "run-...",
  "run_group_id": "run-group-...",
  "comparison_id": null,
  "contract_fingerprint": "sha256:...",
  "atlas_fingerprint": "sha256:...",
  "chart_id": "chart-...",
  "chart_fingerprint": "sha256:...",
  "chart_kind": "normative_decision",
  "partition": "development",
  "split_group": "group-...",
  "harness_id": "candidate-1",
  "harness_fingerprint": "sha256:...",
  "factor": null,
  "repeat_id": 1,
  "mutation_case_id": null,
  "mutation_assignment": null,
  "mutation_generator_fingerprint": null,
  "minimized_counterexample_ref": null,
  "minimized_counterexample_fingerprint": null,
  "implementation_fingerprint": "sha256:...",
  "runtime_fingerprint": "sha256:...",
  "actor_seed": null,
  "actor_seed_control": "unavailable",
  "environment_seed": null,
  "environment_seed_control": "unavailable",
  "failure_schedule_fingerprint": null,
  "world_fingerprint": null,
  "reset_recipe_fingerprint": null,
  "admission_reset_refs": [],
  "admission_reset_fingerprints": [],
  "reset_result_ref": null,
  "reset_result_fingerprint": null,
  "effect_policy_fingerprint": "sha256:...",
  "actor_input_fingerprint": "sha256:...",
  "actor_readable_inventory_ref": "actor-readable-inventory.json",
  "actor_readable_inventory_fingerprint": "sha256:...",
  "actor_access_proof_ref": "traces/run-...-access.json",
  "actor_access_proof_fingerprint": "sha256:...",
  "evaluator_fingerprint": "sha256:...",
  "support_result": "judgeable",
  "status": "pass",
  "termination_reason": "decision_emitted",
  "status_reason": null,
  "hard_oracle_results_ref": "oracle-results/run-....json",
  "hard_oracle_results_fingerprint": "sha256:...",
  "state_diff_ref": null,
  "state_diff_fingerprint": null,
  "trace_invariant_results_ref": "oracle-results/run-...-trace.json",
  "trace_invariant_results_fingerprint": "sha256:...",
  "trace_ref": "traces/run-....json",
  "trace_fingerprint": "sha256:...",
  "reward": null,
  "cost": {
    "input_tokens": null,
    "output_tokens": null,
    "latency_ms": null
  },
  "limitations": []
}
```

The EER comparison block is authoritative and contains the complete comparison
payload. `comparison.json` is the deterministic JSON projection of that block
plus `schema`, `contract_fingerprint`, `eer_ref`, and `eer_fingerprint`; it adds
no independent value. Any projection mismatch is `invalid_environment`.

These rows are not a new global event store.

Every non-pass status has a nonempty `status_reason`. Malformed actor/action
output, a failed required state assertion, and a failed trace invariant each map
to `hard_fail` before comparison or residual judgment. Mutation runs record the
case identity and assignment plus either the external generator identity or the
chart-bound finite-enumeration identity; a minimized failure binds its
counterexample artifact by reference and fingerprint.

## comparison.json

```json
{
  "schema": "emulator-comparison/v1",
  "comparison_id": "cmp-...",
  "contract_fingerprint": "sha256:...",
  "subject": "harness",
  "factor": "question_policy",
  "atlas_fingerprint": "sha256:...",
  "partition_snapshot_fingerprint": "sha256:...",
  "partition_validation_ref": "partition-validation.json",
  "partition_validation_fingerprint": "sha256:...",
  "partition_claim_refs": ["partition-claims/<digest>.json"],
  "partition_claim_fingerprints": ["sha256:..."],
  "partition_claim_validation_ref": "partition-claim-validation.json",
  "partition_claim_validation_fingerprint": "sha256:...",
  "holdout_reservation_ref": "holdout-reservation.json",
  "holdout_reservation_fingerprint": "sha256:...",
  "holdout_lock_refs": ["holdout-locks/<digest>.lock"],
  "holdout_lock_fingerprints": ["sha256:..."],
  "holdout_lock_validation_ref": "holdout-lock-validation.json",
  "holdout_lock_validation_fingerprint": "sha256:...",
  "actor_access_proof_ref": "actor-access-proof.json",
  "actor_access_proof_fingerprint": "sha256:...",
  "baseline_harness_fingerprint": "sha256:...",
  "candidate_harness_fingerprint": "sha256:...",
  "factor_delta_validation_ref": "factor-delta-validation.json",
  "factor_delta_validation_fingerprint": "sha256:...",
  "evaluated_runs": {
    "baseline": [],
    "candidate": []
  },
  "eer_ref": "EER-v1.yaml",
  "eer_fingerprint": "sha256:...",
  "eligible_chart_ids": [],
  "excluded_charts": [
    {"chart_id": "...", "reason": "unsupported_counterfactual"}
  ],
  "targeted_improvements": [],
  "protected_regressions": [],
  "hard_oracle_delta": {},
  "state_delta": {},
  "reward_delta": {},
  "trace_invariant_delta": {},
  "cost_delta": {},
  "residual_preference": {
    "result": "candidate | baseline | tie | ambiguous",
    "order_stable": true,
    "evidence_refs": [],
    "evidence_fingerprints": []
  },
  "chart_comparisons": [
    {
      "chart_id": "chart-...",
      "eligibility": true,
      "baseline_runs": [],
      "candidate_runs": [],
      "hard_delta": {},
      "state_delta": {},
      "reward_delta": {},
      "protected_regressions": [],
      "residual_preference": {},
      "result": "improved | regressed | noninferior | ambiguous | invalid"
    }
  ],
  "recommendation": "adopt | reject | insufficient_evidence",
  "evidence_relation": "paired_replay_delta | observed_association | regression | insufficient_evidence",
  "reason": "",
  "authority_granted": false
}
```

Residual evidence refs and fingerprints are ordered, same-length pairs. Each
fingerprint binds the exact judgment-result bytes. Missing, mismatched, or
mutable unbound judgment evidence makes the residual preference `ambiguous` and
cannot support `adopt`.

## Evaluation order

```text
1. environment and recursive closure validity
2. actor output and action schema validity
3. exclusive action support
4. hard oracles
5. required state assertions and state diff
6. trace invariants
7. protected dimensions
8. contracted reward channels
9. cost and latency
10. residual blinded model or human judgment
```

Hard failures and protected regressions cannot be repaired by later stages. A
residual judge is never sole authority, receives hard-oracle results, is blinded
to harness identity, and is run in both presentation orders. Order disagreement
is `ambiguous`.

When reward is enabled, each run records the contracted per-channel values and
aggregate exactly as defined by the fingerprinted reward asset. Reward is a
learning signal, never an override for a hard failure, protected regression, or
unsupported transition. Fresh trajectory exports preserve the same reward
definition fingerprint and observed values.

## Recommendation authority

`adopt` requires complete environment-valid baseline and candidate arms for
every required chart and repeat, no new candidate `hard_fail` of any kind, no
protected regression, at least one targeted untouched holdout improvement,
order-stable residual preference when used, and evaluation of the exact
candidate harness fingerprint. Every required run and chart comparison must be
determinate; an `ambiguous` required row or comparison prevents adoption.
Stochastic adoption additionally requires the
predetermined repeat/improvement rule and matched randomness when available;
uncontrolled evidence that cannot satisfy the frozen rule is insufficient.

The comparison's factor-delta validation ref and fingerprint MUST exactly
equal the fields on the root `candidate_harnesses` entry for its candidate ID
and the same fields in that candidate's metadata. Each candidate has a distinct
complete baseline/candidate manifest-diff validation; evidence from one
candidate cannot validate another.

Use one exclusive precedence rule. Any new candidate `hard_fail`, protected
regression, or contracted non-hard regression beyond tolerance yields `reject`,
even when other evidence is incomplete. Otherwise `adopt` applies only when all
adoption conditions hold. Every other case yields `insufficient_evidence`.

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
- Counterexample rows require a fresh valid mutation case, exact assignment,
  external-generator or chart-bound finite-enumeration identity, and a
  fingerprinted minimized failing artifact.
- Active holdouts and hidden evaluator material are never exported.
- Historical assistant responses are not chosen labels merely because they
  occurred.

Every row retains chart, authority, closure, harness, and evidence provenance.
