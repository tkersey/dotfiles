# EER-v1: Emulator Execution Report

`emulator_execution_report / EER-v1` records the exact atlas closure, fresh
subject runs, chart eligibility, hard-oracle and state results, and bounded
recommendation. No deployed report corpus exists, so the EER-v1 label is
corrected in place.

Every `*_ref` in EER-v1, `runs.jsonl`, and `comparison.json` is a normalized
atlas-root-relative POSIX path. A ref to the frozen contract or any static
contract asset MUST begin `roots/<root-digest-hex>/` and resolves from that
immutable archived closure. A fresh execution/output ref begins
`runs/<run-group-id>/` or `reports/<run-group-id>/` and its owning directory is
sealed against replacement before the report is emitted. No report may resolve
a static asset through the mutable live root. For `design` or `implement` only,
non-execution report refs begin
`reports/contracts/<root-digest-hex>/`; that create-new directory contains the
EER and closure inventory and is never a run-group identity.
The one shared holdout reservation MAY instead use
`runs/<cycle-id>/holdout-reservation.json` when that cycle ID
exactly equals the frozen root comparison policy and the reservation bytes bind
the current comparison ID; no other cross-run-group ref is allowed. An emitted
dataset ref MAY use `datasets/<dataset-digest-hex>.<kind>.jsonl`, where `kind`
is `preferences`, `trajectories`, `curriculum`, or `counterexamples`; the
filename digest equals the exact immutable bytes and the file is never replaced.
A deferred export manifest MAY use `exports/<export-digest-hex>.json`; its
filename digest likewise equals its immutable bytes.
All refs obey containment,
conflict, and fingerprint rules; absolute and escaping references are invalid.
Canonical registry locations may appear only inside root-bound validation
assets, never as report refs.

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

  runs:  # present only for run, mutate, or compare
    ref:
    fingerprint:

  comparison:  # present only for one baseline/candidate compare pair
    comparison_id:
    subject: harness
    factor:
    comparison_implementation_ref:
    comparison_implementation_fingerprint:
    atlas_fingerprint:
    storage_domain_id:                 # selecting roots only
    exposure_registry_id:              # selecting roots only
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
    holdout_consumption_refs: []        # holdout runs only
    holdout_consumption_fingerprints: [] # holdout runs only
    baseline_harness_fingerprint:
    candidate_harness_fingerprint:
    candidate_metadata_ref:
    candidate_metadata_fingerprint:
    candidate_generation_access_proof_ref:
    candidate_generation_access_proof_fingerprint:
    factor_delta_validation_ref:
    factor_delta_validation_fingerprint:
    semantic_delta_attestation_ref:
    semantic_delta_attestation_fingerprint:
    actor_context_delta_validation_ref:
    actor_context_delta_validation_fingerprint:
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

  run_summary:  # present only for run, mutate, or compare
    valid_runs:
    invalid_environment_runs:
    unsupported_runs:
    passed_runs:
    hard_failed_runs:
    ambiguous_runs:
    runtime_error_runs:
    skipped_runs:

  executions:  # present only for run, mutate, or compare
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
      storage_domain_id:                 # source-bound runs with partition claims
      exposure_registry_id:              # source-bound runs with partition claims
      partition_snapshot_fingerprint:  # selecting roots only
      partition_validation_ref:        # selecting roots only
      partition_validation_fingerprint: # selecting roots only
      partition_claim_refs: []          # source-bound runs with partition claims
      partition_claim_fingerprints: []  # source-bound runs with partition claims
      partition_claim_validation_ref:   # source-bound runs with partition claims
      partition_claim_validation_fingerprint: # source-bound runs with partition claims
      holdout_reservation_ref:          # holdout runs only
      holdout_reservation_fingerprint:  # holdout runs only
      holdout_lock_refs: []              # holdout runs only
      holdout_lock_fingerprints: []      # holdout runs only
      holdout_lock_validation_ref:       # holdout runs only
      holdout_lock_validation_fingerprint: # holdout runs only
      holdout_consumption_refs: []        # holdout runs only
      holdout_consumption_fingerprints: [] # holdout runs only
      harness_id:
      harness_fingerprint:
      factor:
      repeat_id:
      mutation_case_id:
      mutation_assignment:
      mutation_generator_fingerprint:
      minimized_counterexample_ref:
      minimized_counterexample_fingerprint:
      environment_implementation_ref:
      environment_implementation_fingerprint:
      evaluator_implementation_ref:
      evaluator_implementation_fingerprint:
      runtime_config_ref:
      runtime_fingerprint:
      runtime_observation_ref:
      runtime_observation_fingerprint:
      runtime_surface_fingerprint:
      actor_runner_fingerprint:
      actor_started: true | false
      actor_seed:
      actor_seed_control: fixed | sampled | unavailable
      environment_seed:
      environment_seed_control: fixed | sampled | unavailable
      failure_schedule_ref:
      failure_schedule_fingerprint:
      world_fingerprint:
      reset_recipe_fingerprint:
      admission_reset_refs: []         # exact-fidelity executable charts
      admission_reset_fingerprints: [] # exact-fidelity executable charts
      reset_result_ref:
      reset_result_fingerprint:
      effect_policy_fingerprint:
      tool_access_policy_fingerprint:
      actor_input_fingerprint:
      actor_context_ref:
      actor_context_fingerprint:
      actor_readable_inventory_ref:
      actor_readable_inventory_fingerprint:
      semantic_leakage_prestart_review_ref:
      semantic_leakage_prestart_review_fingerprint:
      semantic_leakage_review_ref:
      semantic_leakage_review_fingerprint:
      actor_access_proof_ref:
      actor_access_proof_fingerprint:
      evaluator_fingerprint:
      residual_judgment_ref:
      residual_judgment_fingerprint:
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

For `design` and `implement`, `runs`, `run_summary`, `executions`, and
`comparison` are absent; the EER reports only the frozen contract closure,
eligible non-run outputs, and limitations. These modes do not invent a run
group, an empty `runs.jsonl`, or runtime counters. For `run`, `mutate`, and
`compare`, the three run sections are required and the parsed `runs.jsonl` rows
must equal `executions` as specified below.
For `compare`, every execution's `mutation_case_id`, `mutation_assignment`,
`mutation_generator_fingerprint`, and minimized-counterexample fields are null;
a non-null value is `invalid_environment`.

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

Discovery/development session runs bind their published registry claim
snapshots and validation even though they have no holdout reservation.

Each started selecting or training run binds both the pre-start and post-run
`semantic-leakage-review/v1` artifacts required by
`session-derived-atlas.md`. Their inventory and context fingerprints equal the
row's readable inventory and actor context. The pre-start rows map every
readable entry and delivered message; the post-run rows additionally map every
tool observation and bind the pre-phase review fingerprint. Missing, stale,
partial, `leak`, or `uncertain` review evidence is
`historical_leakage` and makes the run ineligible.

Every paired comparison also binds exact
`actor-context-delta-validation/v1` bytes by ref and fingerprint. That artifact
maps each baseline/candidate run pair, removes only each context's `run_id`, and
records either exact equality or the complete set of content fields already
authorized by `factor-delta-validation/v1.runtime_surface_changes`. Missing,
extra, or non-factor context drift is `comparison_drift`.

Its exact RFC 8785 payload is
`{"factor_delta_validation_fingerprint":"sha256:<hex>","pairs":[{"authorized_runtime_surface_fields":["actor_context.messages[0].content"],"baseline_actor_context_fingerprint":"sha256:<hex>","baseline_run_id":"<run-id>","candidate_actor_context_fingerprint":"sha256:<hex>","candidate_run_id":"<run-id>","chart_id":"<chart-id>","normalized_equal":false,"repeat_id":"<repeat-id>"}],"schema":"actor-context-delta-validation/v1"}`.
Pairs sort by `(chart_id, repeat_id, baseline_run_id, candidate_run_id)` and are
complete and unique. Each field array is sorted and duplicate-free. It is empty
when normalized contexts are equal; otherwise it contains every and only
differing message-content field, each of which occurs exactly once in the bound
factor-delta validation with matching before/after value fingerprints and an
approved derivation.

Comparison-wide access proof maps every execution row that can contribute agent
evidence to that row's nonempty `actor_access_proof_ref` and fingerprint. A row terminated before process launch records
`actor_started: false`, null proof fields, and a pre-launch termination reason;
only `invalid_environment`, `runtime_error`, or `skipped` may do so. A started
row whose runner fails before access proof is durable may record null proof
fields only with `status: runtime_error | invalid_environment` and reason
`access_proof_unavailable_after_start`; it is ineligible for selection or
training. All other started rows require a nonempty proof. The baseline/candidate
run-ID lists are duplicate-free, disjoint, and their union still equals all
comparison execution rows. Every baseline-listed row's harness fingerprint
equals the root baseline; every candidate-listed row's harness fingerprint
equals the one candidate for that pair. Every mapped proof verifies its corresponding fresh process;
there is no singleton comparison-level proof that can stand in for other runs.
The execution rows are also an exact one-to-one realization of the frozen
chart × harness-arm × repeat cohort. Missing, extra, or duplicate cohort tuples
invalidate comparison; favorable retry selection is impossible within one
comparison identity.

Every execution separately binds the environment-transition implementation and
the evaluator implementation declared by its chart. Missing or unequal
evaluator implementation bytes are `invalid_environment`. When residual
judgment is enabled, the execution also binds that judgment result by ref and
fingerprint; those fields are null when no residual judgment ran.

`runtime_config_ref` names the archived harness bundle's
`runtime-config.json`; `runtime_fingerprint` is SHA-256 of that asset's exact
RFC 8785 bytes and those bytes equal the selected harness manifest's inline
`runtime_config`. The observed process configuration must equal the same bytes.
The baseline and candidate runtime fingerprints are equal except for keys
admitted by a runtime-factor delta validation. `actor_runner_fingerprint`
binds the runner implementation and version and is always equal across arms;
runner identity is not a selectable harness factor. A mismatch is
`comparison_drift`, never candidate improvement.

Each started execution also binds a run-owned `runtime-observation/v1` artifact
by ref and fingerprint. Its exact RFC 8785 payload is
`{"credential_binding":{"descriptor_fingerprint":"sha256:<hex>","descriptor_ref":"runs/<run-group-id>/runtime/<run-id>-credential-binding.json","secret_material_recorded":false},"observed_runtime_config":{},"observed_runtime_surface":{},"requested_runtime_fingerprint":"sha256:<hex>","runner":{"binary_sha256":"sha256:<hex>","name":"<name>","version":"<version>"},"schema":"runtime-observation/v1"}`.
`observed_runtime_config` is the closed projection of behavior-bearing,
non-secret requested keys and its canonical digest equals both
`requested_runtime_fingerprint` and the execution's `runtime_fingerprint`.
`observed_runtime_surface` follows the runner-owned closed schema bound by
`actor_runner_fingerprint` and MUST include resolved model/version and reasoning
mode, OS/runtime identity, locale, timezone, working-directory policy,
behavior-bearing environment projection, tool-manifest fingerprint, and sorted
dependency/lock fingerprints. Its canonical digest is the execution's
`runtime_surface_fingerprint`; corresponding values are equal across arms
except exact runtime-factor keys or runtime-surface fields declared in the
pre-candidate factor-owner policy and proved by factor-delta validation to be
deterministically derived solely from approved factor-owned path changes or
runtime-configuration keys. This
exception includes dependency/lock fingerprints only when their changed lock
assets are themselves approved factor-owned paths; it never admits ambient or
unmapped surface drift. Missing
or unmodeled behavior-bearing runtime state makes the run
`invalid_environment`, not silently nondeterministic.
Credentials, tokens, values, and their digests are never serialized. The
runner emits the referenced exact RFC 8785 sanitized
`credential-binding-descriptor/v1` bytes containing provider kind, non-secret
endpoint identity, access-policy fingerprint, and a runner-derived opaque
binding ID (or `kind: none`). The observation fingerprint recomputes from those
bytes, and descriptor bytes MUST be equal across arms.
`actor_runner_fingerprint` is SHA-256 of the exact RFC 8785 `runner` object.
Missing observation, recorded secret material, or unequal observed/requested
values is `comparison_drift`.

A sampled failure schedule binds both a run-owned `failure_schedule_ref` and
its exact fingerprint; both are null when no schedule exists. Matched-schedule
claims compare the referenced bytes, not a free-standing digest.

Selecting runs bind the exact validation artifact that proves the atlas's
current pointer resolved to the root-bound immutable partition snapshot, plus
every source-identity partition claim and the artifact validating those claims
against the frozen pre-candidate policy. The canonical
`partition-validation/v1` payload and run-group path are defined in
`session-derived-atlas.md`; a different payload is invalid. Holdout runs
additionally bind the exclusive pre-exposure reservation, every canonical
cross-atlas lock's atlas-relative snapshot ref and fingerprint, and a validation
artifact proving those snapshots matched the canonical locks, root, storage
domain, source groups, and reservation before exposure. They also bind
atlas-relative snapshots of every global consumption marker created before
first actor exposure. Missing
or mismatched evidence makes selecting use invalid rather than silently reusing
a stale or consumed group.

The report binds the exact emitted `runs.jsonl` bytes. Its parsed rows MUST equal
`executions` in order and content. Every executable run also binds the observed
reset-result/pre-state artifact; a missing or mismatched result is
`invalid_environment`, even when the reset recipe itself is unchanged.
Every exact-fidelity executable run additionally binds the two distinct,
byte-identical-prestate admission reset artifacts required before chart
admission; missing or duplicate proof refs invalidate the fidelity claim.

`run` and `mutate` modes omit `comparison` and emit executions plus applicable
datasets and limitations under one frozen harness subject. Neither invents a
candidate fingerprint or recommendation.
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
  "storage_domain_id": null,
  "exposure_registry_id": null,
  "chart_id": "chart-...",
  "chart_fingerprint": "sha256:...",
  "chart_kind": "normative_decision",
  "partition": "development",
  "split_group": "group-...",
  "harness_id": "baseline",
  "harness_fingerprint": "sha256:...",
  "factor": null,
  "repeat_id": "repeat-1",
  "mutation_case_id": null,
  "mutation_assignment": null,
  "mutation_generator_fingerprint": null,
  "minimized_counterexample_ref": null,
  "minimized_counterexample_fingerprint": null,
  "environment_implementation_ref": "roots/<root-digest-hex>/worlds/chart-.../implementation.json",
  "environment_implementation_fingerprint": "sha256:...",
  "evaluator_implementation_ref": "roots/<root-digest-hex>/evaluators/chart-...-implementation.json",
  "evaluator_implementation_fingerprint": "sha256:...",
  "runtime_config_ref": "roots/<root-digest-hex>/harnesses/baseline/runtime-config.json",
  "runtime_fingerprint": "sha256:...",
  "runtime_observation_ref": "runs/run-group-.../runtime/run-...-observation.json",
  "runtime_observation_fingerprint": "sha256:...",
  "runtime_surface_fingerprint": "sha256:...",
  "actor_runner_fingerprint": "sha256:...",
  "actor_started": true,
  "actor_seed": null,
  "actor_seed_control": "unavailable",
  "environment_seed": null,
  "environment_seed_control": "unavailable",
  "failure_schedule_ref": null,
  "failure_schedule_fingerprint": null,
  "world_fingerprint": null,
  "reset_recipe_fingerprint": null,
  "admission_reset_refs": [],
  "admission_reset_fingerprints": [],
  "reset_result_ref": null,
  "reset_result_fingerprint": null,
  "effect_policy_fingerprint": "sha256:...",
  "tool_access_policy_fingerprint": "sha256:...",
  "actor_input_fingerprint": "sha256:...",
  "actor_context_ref": "runs/run-group-.../actor-context/run-....json",
  "actor_context_fingerprint": "sha256:...",
  "actor_readable_inventory_ref": "runs/run-group-.../actor-readable-inventory/run-....json",
  "actor_readable_inventory_fingerprint": "sha256:...",
  "semantic_leakage_prestart_review_ref": "runs/run-group-.../semantic-leakage-review/run-...-prestart.json",
  "semantic_leakage_prestart_review_fingerprint": "sha256:...",
  "semantic_leakage_review_ref": "runs/run-group-.../semantic-leakage-review/run-....json",
  "semantic_leakage_review_fingerprint": "sha256:...",
  "actor_access_proof_ref": "runs/run-group-.../traces/run-...-access.json",
  "actor_access_proof_fingerprint": "sha256:...",
  "evaluator_fingerprint": "sha256:...",
  "residual_judgment_ref": null,
  "residual_judgment_fingerprint": null,
  "support_result": "judgeable",
  "status": "pass",
  "termination_reason": "decision_emitted",
  "status_reason": null,
  "hard_oracle_results_ref": "runs/run-group-.../oracle-results/run-....json",
  "hard_oracle_results_fingerprint": "sha256:...",
  "state_diff_ref": null,
  "state_diff_fingerprint": null,
  "trace_invariant_results_ref": "runs/run-group-.../oracle-results/run-...-trace.json",
  "trace_invariant_results_fingerprint": "sha256:...",
  "trace_ref": "runs/run-group-.../traces/run-....json",
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
  "comparison_implementation_ref": "roots/<root-digest-hex>/comparison/implementation.json",
  "comparison_implementation_fingerprint": "sha256:...",
  "atlas_fingerprint": "sha256:...",
  "storage_domain_id": "sha256:...",
  "exposure_registry_id": "sha256:...",
  "partition_snapshot_fingerprint": "sha256:...",
  "partition_validation_ref": "runs/cmp-.../partition-validation.json",
  "partition_validation_fingerprint": "sha256:...",
  "partition_claim_refs": ["roots/<root-digest-hex>/partitions/claims/<digest-hex>.partition.json"],
  "partition_claim_fingerprints": ["sha256:..."],
  "partition_claim_validation_ref": "roots/<root-digest-hex>/partitions/partition-claim-validation.json",
  "partition_claim_validation_fingerprint": "sha256:...",
  "holdout_reservation_ref": "runs/<cycle-id>/holdout-reservation.json",
  "holdout_reservation_fingerprint": "sha256:...",
  "holdout_lock_refs": ["runs/cmp-.../holdout-locks/<digest-hex>.lock"],
  "holdout_lock_fingerprints": ["sha256:..."],
  "holdout_lock_validation_ref": "runs/cmp-.../holdout-lock-validation.json",
  "holdout_lock_validation_fingerprint": "sha256:...",
  "holdout_consumption_refs": ["runs/cmp-.../holdout-consumption/<digest-hex>.json"],
  "holdout_consumption_fingerprints": ["sha256:..."],
  "baseline_harness_fingerprint": "sha256:...",
  "candidate_harness_fingerprint": "sha256:...",
  "candidate_metadata_ref": "roots/<root-digest-hex>/harnesses/candidates/candidate-1/candidate.yaml",
  "candidate_metadata_fingerprint": "sha256:...",
  "candidate_generation_access_proof_ref": "roots/<root-digest-hex>/harnesses/candidates/candidate-1/generation-access-proof.json",
  "candidate_generation_access_proof_fingerprint": "sha256:...",
  "factor_delta_validation_ref": "roots/<root-digest-hex>/harnesses/candidates/candidate-1/factor-delta-validation.json",
  "factor_delta_validation_fingerprint": "sha256:...",
  "semantic_delta_attestation_ref": null,
  "semantic_delta_attestation_fingerprint": null,
  "actor_context_delta_validation_ref": "reports/cmp-.../actor-context-delta-validation.json",
  "actor_context_delta_validation_fingerprint": "sha256:...",
  "evaluated_runs": {
    "baseline": [],
    "candidate": []
  },
  "eer_ref": "reports/cmp-.../EER-v1.yaml",
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
The comparison implementation ref/fingerprint equals the final root and the
evaluator-only pre-candidate commitment. It covers aggregation, precedence,
and recommendation logic; missing, changed, or candidate-readable
implementation evidence is `evaluator_contaminated` and cannot yield `adopt`.

For a static asset ref, canonical asset identity is `(closure-relative suffix,
fingerprint)`: strip the exact `roots/<root-digest-hex>/` prefix required in a
report before comparison. The comparison's factor-delta validation asset
identity MUST equal the closure-relative fields on the root
`candidate_harnesses` entry for its candidate ID and the same fields in that
candidate's metadata. Literal prefixed and unprefixed ref strings are not
compared. Each candidate has a distinct
complete baseline/candidate manifest-diff validation; evidence from one
candidate cannot validate another.

Use one exclusive precedence rule. An invalid, unsupported, skipped, or
ambiguous required holdout yields `insufficient_evidence` before regression
disposition; it cannot be silently excluded. Once every required holdout is
valid and determinate, any new candidate `hard_fail`, protected regression, or
contracted non-hard regression beyond tolerance yields `reject`. Otherwise
`adopt` applies only when all adoption conditions hold. Every other case yields
`insufficient_evidence`.

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

A deferred `export` never edits a sealed EER. It emits immutable eligible
dataset files plus exact RFC 8785 `emulator-export-manifest/v1` bytes at
`exports/<export-digest-hex>.json`. The manifest binds the originating EER ref
and fingerprint, runs ref and fingerprint, root contract fingerprint, output
authorization booleans, and sorted dataset ref/fingerprint pairs. Its filename
digest is recomputed from the exact bytes. Missing or mismatched originating
evidence makes export `invalid_environment`; the manifest grants no publication
authority.

The manifest has exactly this payload:

```json
{"contract_fingerprint":"sha256:<hex>","datasets":[{"fingerprint":"sha256:<hex>","kind":"preferences","ref":"datasets/preferences.jsonl"}],"originating_eer_fingerprint":"sha256:<hex>","originating_eer_ref":"reports/<run-group-id>/EER-v1.yaml","output_authorization":{"counterexamples":false,"curriculum":false,"preferences":true,"trajectories":false},"runs_fingerprint":"sha256:<hex>","runs_ref":"runs/<run-group-id>/runs.jsonl","schema":"emulator-export-manifest/v1"}
```

`datasets` is sorted by `kind`, duplicate-free, and contains every and only
emitted dataset whose matching authorization is `true`; kind/ref suffixes are
fixed by the dataset schemas. `originating_eer_ref` and fingerprint identify
the exact sealed EER, and `contract_fingerprint` equals that EER's root
contract. For `run`, `mutate`, and `compare`, both runs fields are non-null and
identify the exact sealed `runs.jsonl`; for `design` and `implement`, both are
null. Mixed nullability is invalid. The output-authorization object exactly
equals the originating contract snapshot. The export filename digest is
SHA-256 of these exact canonical bytes, so no two payload preimages share one
manifest identity.
