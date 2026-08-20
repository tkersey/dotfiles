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
    materialization_witnesses:  # empty while pending; retained after implement
      - chart_fingerprint:
        field_pointer:
        ref:
        fingerprint:
    contract_reset_admissions:
      - chart_fingerprint:
        admission_reset_refs: []
        admission_reset_fingerprints: []

  runs:  # present only for run, mutate, or compare
    ref:
    fingerprint:
    shrink_selection_trace_ref:
    shrink_selection_trace_fingerprint:

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
    partition_claims:                 # selecting roots only
      - ref:
        fingerprint:
    partition_claim_validation_ref:   # selecting roots only
    partition_claim_validation_fingerprint: # selecting roots only
    holdout_reservation_ref:          # holdout runs only
    holdout_reservation_fingerprint:  # holdout runs only
    holdout_locks:                     # holdout runs only
      - ref:
        fingerprint:
    holdout_lock_validation_ref:       # holdout runs only
    holdout_lock_validation_fingerprint: # holdout runs only
    holdout_consumptions:              # holdout runs only
      - ref:
        fingerprint:
    optimizer_clear_validations:       # holdout runs only
      - phase: pre_reservation | pre_actor
        ref:
        fingerprint:
    baseline_harness_fingerprint:
    candidate_harness_fingerprint:
    generation_attempt_id:
    candidate_metadata_ref:
    candidate_metadata_fingerprint:
    candidate_generation_access_proof_ref:
    candidate_generation_access_proof_fingerprint:
    factor_delta_validation_ref:
    factor_delta_validation_fingerprint:
    semantic_delta_attestation_ref:
    semantic_delta_attestation_fingerprint:
    actor_readable_surface_validation_ref:
    actor_readable_surface_validation_fingerprint:
    actor_context_delta_validation_ref:
    actor_context_delta_validation_fingerprint:
    reset_state_validation_ref:
    reset_state_validation_fingerprint:
    randomness_cohort_commitment_ref:
    randomness_cohort_commitment_fingerprint:
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
      execution_intent_ref:
      execution_intent_fingerprint:
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
      partition_claims:                 # source-bound runs with partition claims
        - ref:
          fingerprint:
      partition_claim_validation_ref:   # source-bound runs with partition claims
      partition_claim_validation_fingerprint: # source-bound runs with partition claims
      holdout_reservation_ref:          # holdout runs only
      holdout_reservation_fingerprint:  # holdout runs only
      holdout_locks:                     # holdout runs only
        - ref:
          fingerprint:
      holdout_lock_validation_ref:       # holdout runs only
      holdout_lock_validation_fingerprint: # holdout runs only
      holdout_consumptions:              # holdout runs only
        - ref:
          fingerprint:
      optimizer_clear_validations:       # holdout runs only
        - phase: pre_reservation | pre_actor
          ref:
          fingerprint:
      harness_id:
      harness_fingerprint:
      factor:
      repeat_id:
      run_purpose: primary | shrink_trial
      parent_mutation_case_id:
      parent_repeat_id:
      mutation_case_id:
      mutation_assignment:
      mutation_assignment_ref:
      mutation_assignment_fingerprint:
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
      actor_process_opaque_id:
      sandbox_instance_id:
      sandbox_created: true | false
      actor_started: true | false
      sandbox_creation_receipt_ref:
      sandbox_creation_receipt_fingerprint:
      actor_launch_receipt_ref:
      actor_launch_receipt_fingerprint:
      randomness_cohort_commitment_ref:
      randomness_cohort_commitment_fingerprint:
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
      resolved_effect_policy_ref:
      resolved_effect_policy_fingerprint:
      tool_access_policy_fingerprint:
      metadata_observation_policy_ref:
      metadata_observation_policy_fingerprint:
      actor_input_ref:
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
      support_results:
        - action_index:
          action_ref:
          action_fingerprint:
          support_class: executable | judgeable | denied | observed_only | unsupported
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

  datasets:  # only datasets emitted before this EER is sealed; otherwise absent
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
`datasets` is absent unless the originating operation emits and seals those
datasets before sealing this EER. A later `mode: export` never fills or rewrites
this block; its immutable export manifest exclusively owns deferred dataset
pairs.
`contract.materialization_witnesses` is empty for a pending design and equals
the root's sorted witness array after implementation, including later run-mode
descendants. Every ref resolves through the closure inventory to the closed
witness schema in the contract profile. Missing, extra, or unequal witness
evidence makes the EER invalid. Each `chart_fingerprint` is the frozen pending
plan identity and joins the witness by `(chart_fingerprint, field_pointer)`.
`contract.contract_reset_admissions` is present in every mode and has one row
for each fully materialized exact-fidelity executable chart, sorted by chart fingerprint. A pending design chart is absent until its implement successor
materializes and proves both resets. Each row
binds the two distinct admission reset refs/fingerprints that established exact
fidelity; other charts are absent. Thus design may retain pre-existing proof and implement retains new proof
without inventing executions. These rows equal the root contract's non-null
`reset_admissions` entries; a pending design slot with a null fingerprint is
not reportable proof. Run modes repeat the same pairs in their chart's
execution rows.
Each admission ref resolves closed exact RFC 8785 `reset-admission/v1` bytes:

```json
{"admission_id":"<admission-id>","chart_fingerprint":"sha256:<hex>","effect_policy_template_fingerprint":"sha256:<hex>","effect_policy_template_ref":"environment/effect-policy.json","observed_prestate_artifact_fingerprint":"sha256:<hex>","observed_prestate_fingerprint":"sha256:<hex>","observed_prestate_ref":"admissions/<admission-id>/prestate.json","reset_recipe_fingerprint":"sha256:<hex>","reset_result_fingerprint":"sha256:<hex>","reset_result_ref":"admissions/<admission-id>/result.json","resolved_effect_policy_fingerprint":"sha256:<hex>","resolved_effect_policy_ref":"admissions/<admission-id>/resolved-effect-policy.json","sandbox_instance_id":"<runner-opaque-id>","schema":"reset-admission/v1","world_fingerprint":"sha256:<hex>"}
```

The two rows have different admission and sandbox instance IDs, equal chart,
world, recipe, logical effect-policy-template, and observed-prestate fingerprints, and each
observed prestate equals the chart's expected fingerprint. The template
ref/fingerprint equals the closure-relative chart/world effect-policy pair.
For the inline all-deny variant the ref is null and the fingerprint equals the
contracted derived inline-policy fingerprint. Report projections add archive
prefixes only to non-null static refs. Resolved policies are deterministic substitutions
of only that template's logical sandbox-root roles.
Reset-result and prestate refs resolve exact retained `reset-result/v1` and
`reset-prestate/v1` bytes. `observed_prestate_artifact_fingerprint` hashes the
whole sandbox-specific prestate artifact and therefore differs across
admissions; `observed_prestate_fingerprint` hashes only its normalized
`observed_state_fingerprint` projection and is equal across resets. Result
bytes are independently produced. Each resolved-effect-policy asset is the
deterministic template projection for that admission's sandbox and admits only
its distinct disposable root; resolved fingerprints differ when concrete roots
differ. The reset result's `effect_policy_fingerprint` equals its admission's
resolved-policy fingerprint. Confinement validates the shared template plus
each resolved policy.
The referenced prestate is closed exact RFC 8785 `reset-prestate/v1` bytes:

```json
{"chart_fingerprint":"sha256:<hex>","mutation_assignment_fingerprint":null,"mutation_assignment_ref":null,"mutation_case_id":null,"observed_state_fingerprint":"sha256:<hex>","repeat_id":null,"sandbox_instance_id":"<runner-opaque-id>","schema":"reset-prestate/v1","world_fingerprint":"sha256:<hex>"}
```

The reset result is closed exact RFC 8785 `reset-result/v1` bytes:

```json
{"chart_fingerprint":"sha256:<hex>","effect_policy_fingerprint":"sha256:<hex>","mutation_assignment_fingerprint":null,"mutation_assignment_ref":null,"mutation_case_id":null,"prestate_fingerprint":"sha256:<hex>","prestate_ref":"<reset-prestate-ref>","repeat_id":null,"reset_recipe_fingerprint":"sha256:<hex>","sandbox_instance_id":"<runner-opaque-id>","schema":"reset-result/v1","status":"pass","world_fingerprint":"sha256:<hex>"}
```

Admission resets use null repeat/mutation fields. Execution resets repeat the
exact chart/repeat and, for `mutate`, the case and assignment identities from
the execution row. The prestate pair, sandbox, world, recipe, and effect policy
join the same reset invocation. For a started execution, the reset-result,
execution row, runtime observation, readable inventory, and actor access proof
all repeat the same `sandbox_instance_id`; the execution and access proof also
repeat one `actor_process_opaque_id`. Starting in another sandbox is invalid
unless a separately contracted state-transfer witness is added by a future
designed chart. Reuse across a different mutation tuple is
`invalid_environment`.
For standalone `run`, the referenced prestate's normalized observed-state
fingerprint equals the chart's expected prestate. For `mutate`, it equals the
deterministic expected prestate derived from the chart plus the exact frozen
assignment by the bound reset implementation. An ID-only join with wrong state
is `invalid_environment` and cannot yield a training row.
For `compare`, every execution's `mutation_case_id`, `mutation_assignment`,
`mutation_assignment_ref`, `mutation_assignment_fingerprint`,
`mutation_generator_fingerprint`, and minimized-counterexample fields are null;
a non-null value is `invalid_environment`.
For `run` and `mutate`, primary execution rows equal the complete
`comparison_policy.single_arm_cohort` expansion. `run` has null mutation fields
and empty per-chart `mutation_assignments`; `mutate` rows cover every selected
chart/repeat and that chart entry's case/ref/fingerprint tuple exactly once.
Each execution's archived assignment ref has the cohort ref as its exact
closure-relative suffix, repeats the cohort fingerprint, and resolves the same
exact bytes; the required `roots/<root-digest-hex>/` prefix is not part of
cohort identity. Its inline `mutation_assignment` equals those bytes. Case IDs never
cross chart entries. Missing, extra, or duplicate tuples are
`invalid_environment`.
Every primary row has `run_purpose: primary` and null
`parent_mutation_case_id` and `parent_repeat_id`. A shrink execution has `run_purpose: shrink_trial`,
repeats one tuple from the frozen `single_arm_cohort.shrink_trials`, and binds
its parent primary case/repeat; its `repeat_id` equals frozen `trial_repeat_id`.
Executed shrink trials may be a subset of the frozen
permitted set, but every fresh trial appears once in runs.jsonl and executions;
the shrink-selection trace proves the ordered subset. A minimized artifact with
`source_kind: shrink_trial` must cite the accounted failing shrink-trial row
whose failure the minimized artifact preserves;
the explicit irreducible `source_kind: primary` variant cites its primary row
and requires no nonexistent shrink trial. An unlisted or duplicate shrink
trial is `invalid_environment`.
For `mutate`, the runs block binds closed exact RFC 8785
`shrink-selection-trace/v1` bytes:

```json
{"schema":"shrink-selection-trace/v1","selected_trials":[{"parent_mutation_case_id":"<case-id>","parent_repeat_id":"<repeat-id>","run_id":"<run-id>","sequence":1,"trial_mutation_case_id":"<case-id>","trial_repeat_id":"<repeat-id>"}]}
```

Sequence starts at one and is contiguous; every row joins one frozen shrink
tuple to exactly one shrink execution, in actual selection order. The array may
be empty. The two trace fields are non-null for mutate and null for other modes;
the trace row set equals the executed shrink subset exactly.

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
Rows with `sandbox_created: false` require `actor_started: false`, null process
and sandbox IDs, null receipt pairs, and no runtime observation, inventory, or access proof. Rows
with `sandbox_created: true, actor_started: false` require a non-null unique
sandbox ID, null process ID, non-null sandbox-creation receipt, and null launch
receipt. Because `runtime-observation/v1` is
process-owned, its ref/fingerprint and runtime surface fingerprint are null;
the row retains the inventory and pre-start leakage artifacts actually
produced. When that review exists, the row also retains its exact planned
`actor_context_ref`/fingerprint and the review's `context_fingerprint` equals
it; this proves reviewed bytes, not actor delivery. Access proof remains null.
If no context was constructed, both the context pair and leakage-review pair
are null. This is the admitted mounts-frozen/process-not-
started state. Started rows require both booleans true, non-null process and
sandbox IDs, and both receipt pairs. No other combination is valid.
Across the complete run group, every non-null `actor_process_opaque_id` and
`sandbox_instance_id` is unique to one execution row. Baseline/candidate arms,
repeats, and charts never reuse a process or sandbox; duplicate launch identity
is `comparison_drift` even when run IDs differ.

Every pass or hard failure has a fresh trace. Every invalid, unsupported,
runtime-error, ambiguous, or skipped row records a reason and the evidence
available before termination. No historical run appears as a baseline
execution.

`support_results` is an ordered array with exactly one row for every
successfully projected actor action or tool-action event in the fresh trace;
no separate "consequential" filter exists. `action_index` starts
at zero and is contiguous. `action_ref` resolves retained exact RFC 8785 action-
projection bytes even when no full trace exists, and `action_fingerprint` is
their SHA-256. `support_class` is that action's one exclusive class.
The array is empty exactly when execution ended before any support
classification, including pre-start `runner_unavailable` and malformed output
rejected before a valid action exists. A full-turn or full-episode run retains
all classified actions, including an executable action followed by a denied or
unsupported action; no execution-level scalar may collapse the history.

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
`actor-readable-surface-validation/v1` bytes by ref and fingerprint. The
report-owned artifact uses the exact schema in `session-derived-atlas.md` and
contains one complete unique baseline/candidate inventory pair for every
chart/repeat tuple in the frozen cohort. It is created only after those runtime
inventories exist and is not part of the root closure or static factor-delta
validation. Every pair permits only the root-qualified paths already authorized
by the frozen factor delta. A missing/extra row or a status other than `pass`
or `unavailable_prestart` is `comparison_drift`; the complete closed
`unavailable_prestart` variant is admitted and yields incomplete evidence.
Its derivation-implementation ref/fingerprint equals the evaluator-only asset
frozen before candidate generation. A pre-start execution still has one
`unavailable_prestart` pair row with the closed sandbox-created/actor-started
variant defined by the atlas contract; an inventory is preserved when mounts
were frozen before termination. Omitting that tuple is `comparison_drift`.

Every paired comparison also binds exact
`actor-context-delta-validation/v1` bytes by ref and fingerprint. That artifact
maps each baseline/candidate run pair, removes only each context's `run_id`, and
records either exact equality or the complete set of content fields already
authorized by `factor-delta-validation/v1.runtime_surface_changes`. Missing,
extra, or non-factor context drift is `comparison_drift`.

Its exact RFC 8785 payload is
`{"factor_delta_validation_fingerprint":"sha256:<hex>","pairs":[{"authorized_runtime_surface_fields":["actor_context.messages[0].content"],"baseline_actor_context_fingerprint":"sha256:<hex>","baseline_actor_started":true,"baseline_run_id":"<run-id>","baseline_unavailable_reason":null,"candidate_actor_context_fingerprint":"sha256:<hex>","candidate_actor_started":true,"candidate_run_id":"<run-id>","candidate_unavailable_reason":null,"chart_id":"<chart-id>","normalized_equal":false,"repeat_id":"<repeat-id>","status":"pass"}],"schema":"actor-context-delta-validation/v1"}`.
Pairs sort by `(chart_id, repeat_id, baseline_run_id, candidate_run_id)` and are
complete and unique. Each field array is sorted and duplicate-free. It is empty
when normalized contexts are equal; otherwise it contains every and only
differing message-content field, each of which occurs exactly once in the bound
factor-delta validation with matching before/after value fingerprints and an
approved derivation.
A tuple whose actor never started still has exactly one pair row with
`status: unavailable_prestart`, the affected `*_actor_started: false`, null
actor-context fingerprint only when no context was constructed. If its
execution row retains a planned context and pre-start leakage review, the pair
retains that same non-null context fingerprint while `actor_started` remains
false. `normalized_equal` is null, with an empty
`authorized_runtime_surface_fields` array, and that arm's nonempty pre-launch
`*_unavailable_reason` matching its execution row. Started arms have null
reasons; two failed arms retain two independent reasons. The other arm retains its
observed started flag and context fingerprint. No other row may use that
variant; omitting it or fabricating a context fingerprint is
`comparison_drift`.
An actor that started but failed before context capture uses the distinct
`status: unavailable_postlaunch` variant: the affected `*_actor_started` is
true, context fingerprint is null, normalized equality is null, authorized
field list is empty, and the nonempty reason matches a `runtime_error` or
`invalid_environment` execution row. The other arm retains its observed
fields. This variant is incomplete evidence, not a fabricated context or a
comparison drift. It is invalid for an actor that did not start or one with a
durable context.

Every paired comparison also binds one report-owned exact RFC 8785
`paired-reset-state-validation/v1` artifact. Its complete pair domain contains
one row for every chart/repeat in the frozen cohort whose contracted reset kind
is not `none`, regardless of chart kind or whether support is total or partial,
and joins the
baseline and candidate execution reset results, their referenced prestate
artifacts, and the frozen world/reset/effect-policy identities. After removing
only sandbox- and run-specific identity fields, the two observed prestate
projections MUST be byte-equal and both MUST equal the chart's expected
prestate fingerprint. A factor is never allowed to change world, reset, or
the logical effect-policy template in a harness comparison; any unequal
normalized state, template identity, or non-root resolved-policy projection is
`comparison_drift`.

The exact payload shape is
`{"pairs":[{"baseline_normalized_prestate_fingerprint":"sha256:<hex>","baseline_reset_performed":true,"baseline_reset_result_fingerprint":"sha256:<hex>","baseline_reset_result_ref":"runs/<comparison-id>/reset-results/<run-id>.json","baseline_reset_started":true,"baseline_resolved_effect_policy_fingerprint":"sha256:<hex>","baseline_resolved_effect_policy_ref":"runs/<comparison-id>/resolved-effect-policies/<run-id>.json","baseline_unavailable_reason":null,"candidate_normalized_prestate_fingerprint":"sha256:<hex>","candidate_reset_performed":true,"candidate_reset_result_fingerprint":"sha256:<hex>","candidate_reset_result_ref":"runs/<comparison-id>/reset-results/<run-id>.json","candidate_reset_started":true,"candidate_resolved_effect_policy_fingerprint":"sha256:<hex>","candidate_resolved_effect_policy_ref":"runs/<comparison-id>/resolved-effect-policies/<run-id>.json","candidate_unavailable_reason":null,"chart_fingerprint":"sha256:<hex>","effect_policy_template_fingerprint":"sha256:<hex>","effect_policy_template_ref":null,"repeat_id":"<repeat-id>","reset_recipe_fingerprint":"sha256:<hex>","resolved_policies_normalized_equal":true,"status":"pass","world_fingerprint":"sha256:<hex>"}],"schema":"paired-reset-state-validation/v1"}`.
Pairs sort by `(chart_fingerprint, repeat_id)` and are complete and unique.
`pass` requires both `*_reset_started` and `*_reset_performed` true, non-null result pairs, null
reasons, equal per-arm normalized prestates, one shared chart-owned policy
template, and resolved policies equal after stripping only their verified
sandbox-root substitutions. Raw resolved-policy fingerprints are expected to
differ across sandboxes. The template ref is null exactly for the inline
all-deny fingerprint and otherwise is the archive-qualified chart ref. A tuple whose
runner stops before reset has `status: unavailable_prestart`, the affected
started/performed flags false, null result, resolved-policy, and normalized-prestate fields, and a
nonempty reason matching the execution row; the other arm retains its observed
fields. Two unavailable arms retain two reasons. This variant yields incomplete
evidence and never manufactures reset output. Missing/extra rows, a false flag
with result bytes, or a true flag without them is
`comparison_drift`.
If reset starts but fails before valid result/prestate evidence, use
`status: failed_after_start`, with `*_reset_started: true`,
`*_reset_performed: false`, null result/prestate fields, and a nonempty reason
matching a `runtime_error` or `invalid_environment` execution according to the
observed failure owner. The other arm retains its fields;
this is incomplete environment evidence, not an omitted tuple.

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
Before sandbox or process creation, create-new and fsync one
`execution-intent/v1` file per frozen tuple under the run group's
`execution-intents/<tuple-key-hex>.json` path. `tuple_key` is SHA-256 of exact
RFC 8785 tuple bytes containing comparison/run-group, chart, harness, repeat,
run purpose, and nullable mutation/parent identities—but not run ID. The closed
run-ID set is duplicate-free within the run group. Before tuple-intent
publication, create-new and fsync
`run-id-reservations/<sha256(run-id)-hex>.json` with closed exact bytes
`{"run_id":"<run-id>","schema":"execution-run-id-reservation/v1","tuple_key":"sha256:<tuple-key-hex>"}`.
An existing key or mismatched row is `invalid_environment` before launch. The closed
intent bytes are
`{"run_id":"<run-id>","schema":"execution-intent/v1","tuple_key":"sha256:<tuple-key-hex>","tuple":{"chart_fingerprint":"sha256:<hex>","comparison_id":"<comparison-id-or-null>","harness_fingerprint":"sha256:<hex>","mutation_assignment_fingerprint":"<sha256-or-null>","mutation_case_id":"<case-id-or-null>","parent_mutation_case_id":"<case-id-or-null>","parent_repeat_id":"<repeat-id-or-null>","repeat_id":"<repeat-id>","run_group_id":"<run-group-id>","run_purpose":"primary"}}`.
The shrink-trial variant has the same closed outer shape and exact tuple keys,
with `run_purpose: shrink_trial`, non-null mutation and parent identities, and
the frozen trial repeat ID. These are the only two tagged variants.
For `compare`, `comparison_id` is the exact non-null comparison ID and every
mutation/parent field is null. For `run`, all comparison, mutation, and parent
fields are null. For `mutate`, the mutation pair equals the frozen assignment;
primary rows have null parents and `run_purpose: primary`, while shrink rows
have `run_purpose: shrink_trial` and exact frozen parent identities. No other
field combination is admitted, and the intent tuple equals its execution row.
The row intent fingerprint hashes those bytes and its run ID equals the intent;
the tuple-key filename prevents a new run ID from reserving the same tuple. A crash leaves the tuple reserved: recovery
emits exactly one terminal runtime-error or invalid-environment row for that
reserved tuple and never relaunches it. Every reserved holdout tuple therefore
remains accounted for and can participate in cycle completion; comparison
identity is never discarded in lieu of a terminal row.
Immediately after sandbox allocation and before any later effect, create-new and
fsync exact `sandbox-creation-receipt/v1` bytes
`{"run_id":"<run-id>","sandbox_instance_id":"<opaque-id>","schema":"sandbox-creation-receipt/v1","tuple_key":"sha256:<hex>"}`.
Before actor input delivery, spawn the actor suspended, bind its process
incarnation, and create-new/fsync closed `actor-launch-receipt/v1` bytes. Only
then resume delivery. If the actor exits before `runtime-observation/v1` is
durable, the terminal row uses `actor_started: true`, the receipt-bound process
identity, null runtime observation, status `runtime_error`, and reason
`runtime_observation_unavailable_after_launch`; it fabricates no actor evidence.
The launch receipt is exact
`{"actor_process_incarnation_fingerprint":"sha256:<hex>","actor_process_incarnation_ref":"runs/<run-group-id>/process-incarnations/<digest-hex>.json","actor_process_opaque_id":"<opaque-id>","run_id":"<run-id>","sandbox_creation_receipt_fingerprint":"sha256:<hex>","schema":"actor-launch-receipt/v1","tuple_key":"sha256:<hex>"}`.
Every execution row binds both receipt pairs when `actor_started: true`; a
sandbox-created prestart row binds only the sandbox receipt, and a pre-sandbox
row binds neither.

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
`{"actor_process_opaque_id":"<runner-opaque-id>","credential_binding":{"descriptor_fingerprint":"sha256:<hex>","descriptor_ref":"runs/<run-group-id>/runtime/<run-id>-credential-binding.json","secret_material_recorded":false},"observed_runtime_config":{},"observed_runtime_surface":{},"requested_runtime_fingerprint":"sha256:<hex>","run_id":"<run-id>","runner":{"binary_sha256":"sha256:<hex>","name":"<name>","version":"<version>"},"sandbox_instance_id":"<runner-opaque-id>","schema":"runtime-observation/v1"}`.
`observed_runtime_config` is the closed projection of behavior-bearing,
non-secret requested keys and its canonical digest equals both
`requested_runtime_fingerprint` and the execution's `runtime_fingerprint`.
The observation's run, sandbox, and actor-process identities equal the same
execution row and `actor-access-proof/v1`; copied observations from another
fresh process are `comparison_drift`.
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
bytes. Descriptor bytes are equal across arms unless provider kind, endpoint,
or access-policy fields are deterministic projections of exact approved
runtime-factor keys in factor-delta validation; only those mapped fields may
differ, while opaque binding identity and secret-nonserialization remain equal.
An unmapped descriptor delta is `comparison_drift`.
`actor_runner_fingerprint` is SHA-256 of the exact RFC 8785 `runner` object.
Missing observation is `comparison_drift` except the exact receipt-bound
`runtime_observation_unavailable_after_launch` terminal variant above. Recorded
secret material or unequal observed/requested values is always
`comparison_drift`.

A sampled failure schedule uses the archived static
`randomness-cohort-commitment/v1` schedule ref and exact fingerprint; both are
null when no schedule exists. Execution rows repeat that canonical static asset
identity after archive-prefix normalization and do not create a run-owned copy.
Matched-schedule claims compare the referenced bytes, not a free-standing digest.
The root and EER comparison bind the exact pre-candidate
`randomness-cohort-commitment/v1` pair defined in
`session-derived-atlas.md`; every execution row repeats it. Each row's seed
controls, seed values, and schedule pair equal its committed chart/repeat row.
Missing commitment, post-candidate creation, or any mismatch is
`comparison_drift`.
For every paired chart/repeat whose frozen `randomness_matching` requires
matching, controllable actor seeds and environment seeds are equal across arms,
and sampled failure-schedule bytes/fingerprints are equal. A one-arm seed,
schedule, or control-mode delta is `comparison_drift`; `unavailable` remains
explicit and relies on the frozen repeat cohort rather than an invented seed.

Selecting runs bind the exact validation artifact that proves the atlas's
current pointer resolved to the root-bound immutable partition snapshot, plus
every source-identity partition claim and the artifact validating those claims
against the frozen pre-candidate policy. The canonical
`partition-validation/v1` payload and run-group path are defined in
`session-derived-atlas.md`; a different payload is invalid. Selecting rows
set `partition_snapshot_fingerprint` to that artifact's
`resolved_snapshot_fingerprint`. When a valid disjoint advance exists this is
the current successor snapshot, while `root_snapshot_fingerprint` remains the
separately bound predecessor inside the validation artifact. Holdout runs
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
Every executable row also binds the exact run-owned resolved-effect-policy
ref/fingerprint whose digest equals the reset result, inventory, and access
proof. This applies to `run`, `mutate`, and both compare arms; paired validation
reuses the two row-owned pairs rather than owning their only preimages.
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
and leaves comparison-only fields null. The displayed row is specifically a
pure designed, non-holdout example, so registry and partition-claim fields are
omitted. Every field annotated `selecting roots only` or `holdout runs only` is
omitted—not serialized as null/empty—when inapplicable; the YAML shape above is
a field-domain catalog, not a demand to emit mode-inapplicable keys. A
session-derived discovery/development row MUST instead populate
its storage domain, exposure registry, complete claim pairs, and claim-
validation pair as required above:

```json
{
  "schema": "emulator-run/v1",
  "run_id": "run-...",
  "execution_intent_ref": "runs/run-group-.../execution-intents/<tuple-digest-hex>.json",
  "execution_intent_fingerprint": "sha256:...",
  "run_group_id": "run-group-...",
  "comparison_id": null,
  "contract_fingerprint": "sha256:...",
  "atlas_fingerprint": "sha256:...",
  "chart_id": "chart-...",
  "chart_fingerprint": "sha256:...",
  "chart_kind": "normative_decision",
  "partition": "development",
  "split_group": "group-...",
  "harness_id": "baseline",
  "harness_fingerprint": "sha256:...",
  "factor": null,
  "repeat_id": "repeat-1",
  "run_purpose": "primary",
  "parent_mutation_case_id": null,
  "parent_repeat_id": null,
  "mutation_case_id": null,
  "mutation_assignment": null,
  "mutation_assignment_ref": null,
  "mutation_assignment_fingerprint": null,
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
  "actor_process_opaque_id": "<runner-opaque-id>",
  "sandbox_instance_id": "<runner-opaque-id>",
  "sandbox_created": true,
  "actor_started": true,
  "randomness_cohort_commitment_ref": null,
  "randomness_cohort_commitment_fingerprint": null,
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
  "resolved_effect_policy_ref": "runs/run-group-.../resolved-effect-policies/run-....json",
  "resolved_effect_policy_fingerprint": "sha256:...",
  "tool_access_policy_fingerprint": "sha256:...",
  "metadata_observation_policy_ref": "roots/<root-digest-hex>/environment/metadata-observation-policy.json",
  "metadata_observation_policy_fingerprint": "sha256:...",
  "actor_input_ref": "roots/<root-digest-hex>/actors/chart-....md",
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
  "support_results": [
    {
      "action_index": 0,
      "action_ref": "runs/run-group-.../actions/run-...-000000.json",
      "action_fingerprint": "sha256:...",
      "support_class": "judgeable"
    }
  ],
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

Every non-pass status has a nonempty `status_reason`. Actor output that violates
the declared `actor.output_schema`, a failed required state assertion, and a
failed trace invariant each map to `hard_fail` before comparison or residual
judgment. Output that passed that schema but cannot be projected through the
chart's admitted total cardinality-one `action_projection` is a contract-owned
`invalid_environment`, never an agent failure. Mutation runs record the
case identity and assignment plus a non-null
`mutation_generator_fingerprint`. With an external generator it equals the
verified chart asset fingerprint. With finite built-in enumeration it equals
SHA-256 of `"emulator-finite-mutation-generator/v1" NUL chart_fingerprint NUL`
plus the exact complete mutation-declaration bytes defined by the contract
profile. In either route, `mutation_case_id` is SHA-256 of
`"emulator-mutation-case/v1" NUL chart_fingerprint NUL mutation_generator_fingerprint NUL`
plus the exact `mutation-assignment/v1` bytes. A minimized failure ref resolves
closed exact RFC 8785 `emulator-minimized-counterexample/v1` bytes:

```json
{"assignment_fingerprint":"sha256:<hex>","assignment_ref":"<archived-assignment-ref>","chart_fingerprint":"sha256:<hex>","evaluator_evidence":[{"fingerprint":"sha256:<hex>","ref":"runs/<run-group-id>/oracle-results/<run-id>.json"}],"irreducibility_evidence":[{"assignment_fingerprint":"sha256:<hex>","evidence_fingerprint":"sha256:<hex>","evidence_ref":"runs/<run-group-id>/oracle-results/<descendant-run-id>.json","run_id":"<descendant-run-id>","status":"pass"}],"mutation_case_id":"sha256:<case-digest-hex>","payload_fingerprint":"sha256:<hex>","payload_ref":"runs/<run-group-id>/counterexample-payloads/<case-digest-hex>.json","schema":"emulator-minimized-counterexample/v1","shrink_selection_trace_fingerprint":null,"shrink_selection_trace_ref":null,"source_kind":"primary","source_run_id":"<run-id>"}
```

Every identity equals the originating execution, assignment, chart, and
evaluator result; the payload pair binds the actual minimized bytes.
`source_kind: shrink_trial` requires the all-non-null shrink pair and a selected
trial row; `primary` requires both fields null. In either variant,
`irreducibility_evidence` is the sorted complete applicable strict-descendant
set derived from the chart's shrink graphs. Applicability is decided by the
frozen graph before execution; inapplicable assignments are not graph members
and cannot be asserted by an exporter. Every descendant is a fresh hard-oracle
passing run with the closed row
`{"assignment_fingerprint":"sha256:<hex>","evidence_fingerprint":"sha256:<hex>","evidence_ref":"runs/<run-group-id>/oracle-results/<run-id>.json","run_id":"<run-id>","status":"pass"}`.
For sampled/unavailable controls, use the distinct closed
`status: cohort_pass` row:
`{"aggregation":{"result":"nonfailure","rule":"<frozen-rule>"},"assignment_fingerprint":"sha256:<hex>","evidence_fingerprints":["sha256:<hex>"],"evidence_refs":["runs/<run-group-id>/oracle-results/<run-id>.json"],"run_ids":["<run-id>"],"status":"cohort_pass"}`.
Its arrays cover the complete frozen repeat cohort and are same-length ordered
pairs; no run may fail. The irreducibility array is thus a closed tagged union,
not one shared row shape. No failing descendant may
remain. An empty descendant set is valid. Thus minimality means no smaller
failing applicable assignment, not merely trial selection or absence of any
smaller case. Export copies this
wrapper pair and rejects a case/path/digest-only join.
One passing repeat is insufficient for sampled/unavailable controls. Single-run
irreducibility is admitted only when all relevant controls are fixed/deterministic.

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
  "partition_claims": [{"fingerprint":"sha256:...","ref":"roots/<root-digest-hex>/partitions/claims/<digest-hex>.partition.json"}],
  "partition_claim_validation_ref": "roots/<root-digest-hex>/partitions/partition-claim-validation.json",
  "partition_claim_validation_fingerprint": "sha256:...",
  "holdout_reservation_ref": "runs/<cycle-id>/holdout-reservation.json",
  "holdout_reservation_fingerprint": "sha256:...",
  "holdout_locks": [{"fingerprint":"sha256:...","ref":"runs/cmp-.../holdout-locks/<digest-hex>.lock"}],
  "holdout_lock_validation_ref": "runs/cmp-.../holdout-lock-validation.json",
  "holdout_lock_validation_fingerprint": "sha256:...",
  "holdout_consumptions": [{"fingerprint":"sha256:...","ref":"runs/cmp-.../holdout-consumption/<digest-hex>.json"}],
  "optimizer_clear_validations": [{"fingerprint":"sha256:...","phase":"pre_actor","ref":"runs/cmp-.../optimizer-clear-validation-pre_actor.json"},{"fingerprint":"sha256:...","phase":"pre_reservation","ref":"runs/cmp-.../optimizer-clear-validation-pre_reservation.json"}],
  "baseline_harness_fingerprint": "sha256:...",
  "candidate_harness_fingerprint": "sha256:...",
  "generation_attempt_id": "generation-attempt-...",
  "candidate_metadata_ref": "roots/<root-digest-hex>/harnesses/candidates/candidate-1/candidate.yaml",
  "candidate_metadata_fingerprint": "sha256:...",
  "candidate_generation_access_proof_ref": "roots/<root-digest-hex>/harnesses/candidates/candidate-1/generation-access-proof.json",
  "candidate_generation_access_proof_fingerprint": "sha256:...",
  "factor_delta_validation_ref": "roots/<root-digest-hex>/harnesses/candidates/candidate-1/factor-delta-validation.json",
  "factor_delta_validation_fingerprint": "sha256:...",
  "semantic_delta_attestation_ref": null,
  "semantic_delta_attestation_fingerprint": null,
  "actor_readable_surface_validation_ref": "reports/cmp-.../actor-readable-surface-validation.json",
  "actor_readable_surface_validation_fingerprint": "sha256:...",
  "actor_context_delta_validation_ref": "reports/cmp-.../actor-context-delta-validation.json",
  "actor_context_delta_validation_fingerprint": "sha256:...",
  "reset_state_validation_ref": "reports/cmp-.../paired-reset-state-validation.json",
  "reset_state_validation_fingerprint": "sha256:...",
  "randomness_cohort_commitment_ref": "roots/<root-digest-hex>/comparison/randomness-cohort-commitment.json",
  "randomness_cohort_commitment_fingerprint": "sha256:...",
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

`holdout_locks` and `holdout_consumptions` are arrays of closed exact
`ref`/`fingerprint` objects, sorted by ref with unique refs. Each fingerprint
binds the bytes at its paired ref; comparison and every affected execution row
repeat the same complete arrays. Parallel ref and fingerprint arrays are
invalid.
`optimizer_clear_validations` is empty for non-holdout runs and contains
exactly the `pre_actor` and `pre_reservation` phase rows for holdout runs, sorted
by phase with unique phases. Each pair resolves the run-local
`optimizer-clear-validation/v1` evidence defined by the atlas; comparison and
every affected execution repeat both exact rows. Missing, duplicate, stale, or
unresolved gate evidence is `source_contaminated` and cannot select.

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
compared. The comparison's `generation_attempt_id` equals the root candidate
entry, candidate metadata, access proof, and pre-candidate commitment. Each candidate has a distinct
complete baseline/candidate manifest-diff validation; evidence from one
candidate cannot validate another.

Use one exclusive precedence rule. First evaluate every comparison-eligible,
environment-valid, determinate row: required selecting holdouts plus explicitly
designated discovery/development regression guards. Observational and other
diagnostic rows cannot affect recommendation. If any comparison-eligible row proves
a new candidate `hard_fail`, protected
regression, or contracted non-hard regression beyond tolerance, the candidate
is `reject` even when another required holdout is invalid, unsupported,
skipped, or ambiguous. A decisive witnessed regression is not erased by
incomplete coverage: decisive regression yields `reject` before incomplete-
coverage handling. If no decisive regression exists, any invalid,
unsupported, skipped, or ambiguous required holdout yields
`insufficient_evidence`; it cannot be silently excluded. Otherwise `adopt`
applies only when all adoption conditions hold. Every other case yields
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
  fingerprinted minimized failing artifact. The chart partition is
  discovery/development and every retirement/successor field is null. EC-v1 has
  no identity-preserving post-retirement holdout mutation route, so active or
  retired holdout charts never yield counterexample training rows.
- Active holdouts and hidden evaluator material are never exported.
- Historical assistant responses are not chosen labels merely because they
  occurred.

Each preference JSONL row is exact RFC 8785 `emulator-preference/v1`:

```json
{"authority":"explicit_user_correction","chart_fingerprint":"sha256:<hex>","chart_id":"<chart-id>","chosen_action_fingerprint":"sha256:<hex>","chosen_action_index":0,"chosen_action_ref":"<indexed-support-result-action-ref>","contract_fingerprint":"sha256:<hex>","hard_oracle_evidence":[{"fingerprint":"sha256:<hex>","ref":"runs/<run-group-id>/oracle-results/<run-id>.json"}],"harness_fingerprint":"sha256:<hex>","harness_id":"<harness-id>","harness_surface":"question_policy","limitations":[],"rejected_action_fingerprint":"sha256:<hex>","rejected_action_ref":"<archived-chart-historical-action-ref>","retirement_marker_fingerprint":null,"retirement_marker_ref":null,"retirement_snapshot_fingerprint":null,"retirement_snapshot_ref":null,"run_id":"<run-id>","run_row_fingerprint":"sha256:<hex>","runs_jsonl_fingerprint":"sha256:<hex>","runs_jsonl_ref":"runs/<run-group-id>/runs.jsonl","schema":"emulator-preference/v1","source_evidence":[{"fingerprint":"sha256:<hex>","ref":"roots/<root-digest-hex>/source/<chart-id>/source-maps/<source-id>.yaml"}],"state_fingerprint":"sha256:<hex>","state_ref":"<archived-chart-actor-input-ref>","successor_root_fingerprint":null,"successor_root_ref":null}
```

Refs/fingerprints resolve exact eligible bytes; static refs use the archived
root. `state_ref`/fingerprint are the row's `actor_input_ref` identity and equal
the archived form of the chart's exact `actor.input_ref`/fingerprint.
`rejected_action_ref`/fingerprint equal the chart source's singular
`rejected_historical_action_ref`/fingerprint and identify one exact
action asset entry and that entry's own fingerprint in the chart's
`session-source-bundle/v1.assets`; the separate source-bundle fingerprint
continues to bind the manifest. No conventional path or bundle-as-action
fingerprint is synthesized. The
`authority` value is copied exactly from the chart evaluator's directly
attributed authority and is one of `explicit_user_correction`,
`deterministic_test`, `state_assertion`, `trace_invariant`, or
`human_attestation`. `ambiguous` and `fresh_comparison` are not source-bound
preference authority. The displayed row is the explicit-correction variant;
the closed schema admits every listed value without renaming it. The
chosen-action artifact is the exact selected action projection, not a
whole trace. `chosen_action_index` is a nonnegative index into that run's
`support_results`; the indexed result is `judgeable` or `executable`, passed its
bound hard oracles, and its exact action projection equals the chosen-action
ref/fingerprint pair exactly; no duplicate chosen-action artifact is created at
export time. Because that pair is embedded in the sealed run row, retirement
dependency mapping owns it transitively. A one-step chart therefore uses index zero; a
full-turn or full-episode row must select the one specifically evaluated action
and cannot substitute another action from the trace. Authority, chart,
contract, harness, and surface equal the run and chart. `source_evidence` copies every actual ref/fingerprint entry from the
chart bundle's sorted `source_maps` array; it never reconstructs a legacy
singular path. `run_id`, `run_row_fingerprint`, and the sealed `runs_jsonl` pair bind
the same fresh passing row as the chosen action and hard-oracle evidence.
Evidence arrays sort by ref and are duplicate-free. Retirement fields
are all null for discovery/development rows and all non-null for a holdout
retired for training, binding the exact training-authorized marker, successor
snapshot, and non-null `successor_root_ref`/fingerprint. The successor root
transitively owns both retirement assets and its
`retirement_predecessor_root_fingerprint` equals the marker's
`prior_root_fingerprint`.
Mixed nullability or extra fields are invalid.

Trajectory rows are exact RFC 8785 `emulator-trajectory/v1` bytes containing
chart ID/fingerprint, contract and harness fingerprints, the sealed
`runs.jsonl` ref/fingerprint plus run ID and canonical run-row fingerprint,
world fingerprint, both reset recipe and reset-result fingerprints, trace ref/fingerprint, sorted hard-oracle
ref/fingerprint pairs, nullable all-or-none training-retirement marker/snapshot
pairs, and limitations. Curriculum rows are exact
`emulator-curriculum/v1` bytes containing chart ID/fingerprint, contract
fingerprint, the five fields copied exactly from
`claim.curriculum_metadata`, world fidelity, maximum supported claim, and
limitations; no hidden evaluator payload is admitted and missing chart metadata
makes the row ineligible. A pending exact-fidelity executable chart is also
ineligible until the implement successor binds both reset admissions; design
never exports an unproved `world_fidelity: exact` curriculum row. Counterexample rows are exact
`emulator-counterexample/v1` bytes containing chart ID/fingerprint, contract
and harness fingerprints, sealed `runs.jsonl` and canonical run-row identity,
mutation case ID, assignment
ref/fingerprint, generator fingerprint, minimized artifact ref/fingerprint,
sorted evaluator-evidence ref/fingerprint pairs, and limitations. Every object
is closed; arrays are sorted and duplicate-free, static refs use the archived
root, and active holdout rows remain forbidden. `run_row_fingerprint` is
SHA-256 of the exact RFC 8785 `emulator-run/v1` JSONL row bytes excluding the
line terminator; `run_id` selects that unique row, and
`runs_jsonl_ref`/fingerprint bind the sealed containing file.
Every dataset row has nullable `successor_root_ref`/fingerprint. Both are null
for ordinary discovery/development rows and both are non-null for a retired
holdout row, where they bind the exact successor root that contains the cited
retirement marker and snapshot. One dataset file is successor-homogeneous:
every row has the same successor pair, including the all-null ordinary case.
One export manifest may bind only dataset files with that same pair and repeats
it exactly. Rows with different successor roots, or ordinary and retired rows,
are emitted in separate dataset files and separate manifests.
For curriculum, `consumption_purpose` and both retirement ref/fingerprint pairs
are null with the successor pair for ordinary rows; all are non-null with
`consumption_purpose: training` for a retired holdout row.
Trajectory `reward` is null exactly when run reward was disabled. When enabled,
it copies the run's nested `reward.definition_fingerprint`, `reward.channels`,
and `reward.aggregate` values into identically named fields;
no exporter recomputes or drops the learning signal.

```json
{"chart_fingerprint":"sha256:<hex>","chart_id":"<chart-id>","contract_fingerprint":"sha256:<hex>","hard_oracle_evidence":[{"fingerprint":"sha256:<hex>","ref":"runs/<run-group-id>/oracle-results/<run-id>.json"}],"harness_fingerprint":"sha256:<hex>","limitations":[],"reset_recipe_fingerprint":"sha256:<hex>","reset_result_fingerprint":"sha256:<hex>","retirement_marker_fingerprint":null,"retirement_marker_ref":null,"retirement_snapshot_fingerprint":null,"retirement_snapshot_ref":null,"reward":{"aggregate":0,"channels":{},"definition_fingerprint":"sha256:<hex>"},"run_id":"<run-id>","run_row_fingerprint":"sha256:<hex>","runs_jsonl_fingerprint":"sha256:<hex>","runs_jsonl_ref":"runs/<run-group-id>/runs.jsonl","schema":"emulator-trajectory/v1","successor_root_fingerprint":null,"successor_root_ref":null,"trace_fingerprint":"sha256:<hex>","trace_ref":"runs/<run-group-id>/traces/<run-id>.json","world_fingerprint":"sha256:<hex>"}
{"chart_fingerprint":"sha256:<hex>","chart_id":"<chart-id>","consumption_purpose":null,"contract_fingerprint":"sha256:<hex>","difficulty":"bounded","failure_cluster":"<cluster>","family":"<family>","limitations":[],"maximum_supported_claim":"diagnostic","prerequisite_chart_tags":[],"required_tools":[],"retirement_marker_fingerprint":null,"retirement_marker_ref":null,"retirement_snapshot_fingerprint":null,"retirement_snapshot_ref":null,"schema":"emulator-curriculum/v1","successor_root_fingerprint":null,"successor_root_ref":null,"world_fidelity":"exact"}
{"assignment_fingerprint":"sha256:<hex>","assignment_ref":"<archived-cohort-mutation-assignment-ref>","chart_fingerprint":"sha256:<hex>","chart_id":"<chart-id>","consumption_purpose":null,"contract_fingerprint":"sha256:<hex>","evaluator_evidence":[{"fingerprint":"sha256:<hex>","ref":"runs/<run-group-id>/oracle-results/<run-id>.json"}],"generator_fingerprint":"sha256:<hex>","harness_fingerprint":"sha256:<hex>","limitations":[],"minimized_artifact_fingerprint":"sha256:<hex>","minimized_artifact_ref":"runs/<run-group-id>/counterexamples/<case-digest-hex>.json","mutation_case_id":"sha256:<case-digest-hex>","retirement_marker_fingerprint":null,"retirement_marker_ref":null,"retirement_snapshot_fingerprint":null,"retirement_snapshot_ref":null,"run_id":"<run-id>","run_row_fingerprint":"sha256:<hex>","runs_jsonl_fingerprint":"sha256:<hex>","runs_jsonl_ref":"runs/<run-group-id>/runs.jsonl","schema":"emulator-counterexample/v1","successor_root_fingerprint":null,"successor_root_ref":null}
```

Every row retains chart, authority, closure, harness, and evidence provenance.

A deferred `export` never edits a sealed EER. It emits immutable eligible
dataset files plus exact RFC 8785 `emulator-export-manifest/v1` bytes at
`exports/<export-digest-hex>.json`. The manifest binds the originating EER ref
and fingerprint, runs ref and fingerprint, root contract fingerprint, output
authorization booleans, and sorted dataset ref/fingerprint pairs. Its filename
digest is recomputed from the exact bytes. Missing or mismatched originating
evidence makes export `invalid_environment`; the manifest grants no publication
authority.

For `run`, `mutate`, or `compare`, the manifest has this exact execution-origin
payload:

```json
{"contract_fingerprint":"sha256:<hex>","datasets":[{"fingerprint":"sha256:<dataset-digest-hex>","kind":"preferences","ref":"datasets/<dataset-digest-hex>.preferences.jsonl"}],"export_selection":{"counterexamples":false,"curriculum":false,"preferences":true,"trajectories":false},"originating_eer_fingerprint":"sha256:<hex>","originating_eer_ref":"reports/<run-group-id>/EER-v1.yaml","output_authorization":{"counterexamples":false,"curriculum":false,"preferences":true,"trajectories":false},"runs_fingerprint":"sha256:<hex>","runs_ref":"runs/<run-group-id>/runs.jsonl","schema":"emulator-export-manifest/v1","successor_root_fingerprint":null,"successor_root_ref":null}
```

For `design` or `implement`, it instead has this exact contract-origin payload
and does not invent a run group:

```json
{"contract_fingerprint":"sha256:<hex>","datasets":[{"fingerprint":"sha256:<dataset-digest-hex>","kind":"curriculum","ref":"datasets/<dataset-digest-hex>.curriculum.jsonl"}],"export_selection":{"counterexamples":false,"curriculum":true,"preferences":false,"trajectories":false},"originating_eer_fingerprint":"sha256:<hex>","originating_eer_ref":"reports/contracts/<root-digest-hex>/EER-v1.yaml","output_authorization":{"counterexamples":false,"curriculum":true,"preferences":false,"trajectories":false},"runs_fingerprint":null,"runs_ref":null,"schema":"emulator-export-manifest/v1","successor_root_fingerprint":null,"successor_root_ref":null}
```

For a retired holdout export, use the execution-origin shape with non-null
`successor_root_ref`/fingerprint. The originating EER and runs refs are the
static successor-owned snapshot refs named by the sealed cycle-completion arm,
not the former runtime paths. Resolve the arm's admitted reference mapping and
rewrite every embedded ref covered by the sealed mapping in each emitted
dataset row—whether originating under `runs/`, `reports/`, or a prior
`roots/` archive—to its
mapped static successor pair, then prefix that closure-relative ref with the
exact `roots/<successor-root-digest-hex>/` archive prefix before hashing the
emitted row; the mapped fingerprint must be unchanged. Export
using only the successor closure must therefore resolve the EER, runs, and every
row dependency after runtime directories are absent. A missing, ambiguous, or
unmapped ref makes export `invalid_environment`.

Both are the same closed schema; only the mode-constrained originating EER path,
runs nullability, authorized dataset set, and their values differ. `datasets`
is sorted by `kind`, duplicate-free, and contains every and only
emitted dataset whose matching authorization is `true`; kind/ref suffixes are
fixed by the dataset schemas, and `<dataset-digest-hex>` is the lowercase hex
component of that entry's `fingerprint`. `originating_eer_ref` and fingerprint identify
the exact sealed EER, and `contract_fingerprint` equals that EER's root
contract. For `run`, `mutate`, and `compare`, both runs fields are non-null and
identify the exact sealed `runs.jsonl`; for `design` and `implement`, both are
null. Mixed nullability is invalid. `export_selection` exactly records the
current request's four booleans; omitted values are false.
`output_authorization` is their fieldwise AND with the originating contract
snapshot, and `datasets` contains every and only eligible true result. The export filename digest is
SHA-256 of these exact canonical bytes, so no two payload preimages share one
manifest identity.
