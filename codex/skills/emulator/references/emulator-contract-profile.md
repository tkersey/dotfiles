# Emulator Contract Profile

emulator-spec.yaml is the EC-v1 root of one content-addressed contract closure
owned by $emulator.

## Identity and closure

~~~text
root_contract_fingerprint = SHA-256(exact emulator-spec.yaml UTF-8 bytes)
chart_fingerprint         = SHA-256(exact chart YAML UTF-8 bytes)
atlas_identity            = root fingerprint + ordered chart fingerprints
~~~

The root does not contain its own fingerprint. Every chart entry binds its exact
bytes. Each chart recursively binds every external source map, actor input,
world/reset recipe, fixture, tool manifest, and evaluator asset by relative
reference plus exact SHA-256. Source maps and world manifests likewise bind
their query specs, result envelopes, fixtures, and executable inputs.

The closure is invalid when a required reference is missing, escapes the atlas
root without explicit authority, has a mismatched digest, or leaves an
execution-relevant byte implicit. Reports record the root fingerprint, ordered
chart fingerprints, and recursively verified closure inventory.

## Root contract

~~~yaml
emulator_contract:
  packet_version: EC-v1
  contract_id: EC-<stable-id>
  origin: source_faithful | designed | mixed

  source:
    kind: session | session_corpus | repository | specification | tests | traces | user_design | mixed
    refs: []
    corpus_digest:
    current_session_excluded: true
    limitations: []

  target:
    name:
    kind: agentic_harness | skill | agent_loop | tool_loop | workflow | library_protocol
    harness_roots: []

  atlas:
    charts:
      - chart_id:
        chart_ref:
        chart_fingerprint:
        kind: normative_decision | executable_episode | observational
        split_group:
        partition: discovery | development | holdout
        required: true | false

    partition_policy:
      group_by: root_session_or_task
      frozen_before_candidate_generation: true
      holdout_visible_to_optimizer: false

  comparison_policy:
    baseline_harness_ref:
    candidate_factor_policy: one_semantic_owner
    stochastic_repeats: 3
    deterministic_repeats: 1
    order_blinding: true
    swapped_judge_order: true
    hard_oracle_precedence: true
    protected_regressions_forbidden: true

  output:
    eer: EER-v1
    runs: runs.jsonl
    comparison: comparison.json
    preferences: false
    trajectories: false
    curriculum: false
~~~

corpus_digest binds the selected immutable source set, not a mutable session
directory. harness_roots enumerates every behavior-bearing root under
experiment. The root may contain one chart; the atlas abstraction does not
require scale.

For every chart entry, root `chart_id` equals chart `chart_id`, root `kind`
equals chart `kind`, root `split_group` equals chart `split.group_id`, and root
`partition` equals chart `split.partition`. Any mismatch is
`invalid_environment`; neither copy wins by precedence.

## Chart contract

~~~yaml
environment_chart:
  chart_version: EC-chart-v1
  chart_id:
  kind: normative_decision | executable_episode | observational
  title:
  harness_surface:
  tags: []

  source:
    source_kind: session | repository | user_design | mixed
    session_id:
    root_session_id:
    source_bundle_ref:
    source_bundle_fingerprint:
    source_event_refs: []
    historical_action_refs: []
    correction_refs: []
    outcome_refs: []
    contamination: []
    limitations: []

  split:
    group_id:
    partition: discovery | development | holdout

  cut:
    kind: session_start | decision_boundary | skill_activation | synthesis_boundary
    actor_visible_through:
    evaluator_only_after:
    rationale:
    target_prior_influence: none | bounded | present | unknown

  actor:
    mode: one_step_decision | full_turn | full_episode
    input_ref:
    input_fingerprint:
    allowed_context_refs: []
    forbidden_context_refs: []
    output_schema:
    seed_control: fixed | sampled | unavailable
    seed:

  environment:
    world_fidelity: exact | approximate | transcript_only | absent
    transition_model: total | partial | none
    implementation:
      ref:
      fingerprint:
      environment_seed_control: fixed | sampled | unavailable
      environment_seed:
      failure_schedule_ref:
      failure_schedule_fingerprint:
    reset:
      kind: none | git_worktree | fixture | custom
      recipe_ref:
      recipe_fingerprint:
      expected_fingerprint:
    observations:
      schema:
    actions:
      schema:
    tools: {}
    effects:
      network: deny | fixture_only | allow_recorded
      filesystem: read_only | isolated_write | declared_roots
      external_side_effects: deny | fixture_only | explicit
      policy_ref:
      policy_fingerprint:
    termination:
      terminal_conditions:
        - condition_id:
          predicate:
            kind: json_pointer_equals | asset
            path:
            value:
            predicate_ref:
            predicate_fingerprint:
          authority_refs: []
      max_steps:
      timeout_ms:
    support:
      matcher:
        kind: inline_predicates | asset
        classifier_ref:
        classifier_fingerprint:
      executable:
        - support_id:
          authority_refs: []
          predicate:
            kind: json_pointer_equals
            path:
            value:
      judgeable:
        - support_id:
          authority_refs: []
          predicate:
            kind: json_pointer_equals
            path:
            value:
      denied:
        - support_id:
          authority_refs: []
          predicate:
            kind: json_pointer_equals
            path:
            value:
      observed_only:
        - support_id:
          authority_refs: []
          predicate:
            kind: json_pointer_equals
            path:
            value:
      unsupported_default: true

  mutation:
    dimensions:
      - dimension_id:
        domain:
          - case_id:
            value:
            kind: ordinary | boundary | negative
            expected_preserved_law_refs: []
            expected_violated_law_refs: []
        preserved_law_refs: []
        shrink_strategy:
    generator_ref:
    generator_fingerprint:
    assignment_schema_ref:
    assignment_schema_fingerprint:

  evaluator:
    evaluator_ref:
    evaluator_fingerprint:
    authority:
      class: explicit_user_correction | deterministic_test | state_assertion | trace_invariant | human_attestation | fresh_comparison | ambiguous
      refs: []
      attribution: direct | bounded | ambiguous
    hard_oracles: []
    state_diff: []
    trace_invariants: []
    residual_judge:
      enabled: true | false
      rubric:
      sole_authority: false
    protected_dimensions: []
    success_condition:

  closure:
    assets:
      - ref:
        sha256:
        role: source | actor | world | reset | fixture | tool | evaluator | mutation_generator

  claim:
    class: diagnostic | preference_training | harness_selection | promotion
    maximum_supported_claim:
    invalidators: []
    limitations: []
~~~

Every field affects execution, visibility, evaluation, claim strength, or
provenance. Do not add decorative metadata.

`policy_ref` and `policy_fingerprint` are required for every chart, including an
inert observational or normative chart. The inert policy explicitly binds empty
readable/writable roots, fixtures, recordings, and operations. Other policies
define exact readable/writable roots, fixtures, recordings,
operations, and authority for `read_only`, `isolated_write`, `declared_roots`,
both `fixture_only` uses, `allow_recorded`, and `explicit`. A `full_episode` requires at least one terminal
condition plus positive `max_steps` and `timeout_ms`; other actor modes bind the
smallest applicable limit.

Every executable implementation has an exact identity. Actor and environment
seed-control modes are independent; each seed is present only when its own
control is fixed or sampled and is canonically null when unavailable. Any sampled failure schedule is explicit and
fingerprinted; `unavailable` is recorded rather than replaced with an invented
seed.

Every support entry has a unique ID, at least one authority ref, and a deterministic predicate in the declared
action schema. The inline predicate language is exact canonical-JSON equality
at a JSON Pointer: `path` selects one action value and `value` is the required
canonical value. Multiple conditions require separate, explicitly composed
predicate assets rather than implicit prose. An asset matcher binds its
classifier bytes through `classifier_ref` and `classifier_fingerprint`. A
classifier that is missing, nondeterministic, or cannot prove the five classes
disjoint makes the environment invalid.
Every terminal condition likewise has nonempty authority refs; timeout and step
bounds do not invent permission to terminate successfully. A terminal predicate
uses the same exact JSON-Pointer equality language as inline support, or
`kind: asset` with non-null predicate ref/fingerprint and null inline fields.
Mixed or prose predicates are invalid.

Mutation dimensions are optional outside `operation_mode: mutate`. Mutation requires at
least one finite or otherwise bounded domain, preserved-law references, and a
deterministic shrink strategy. An external generator is fingerprinted and
included in the chart closure. No mutation widens action support or source
authority.
Every generated assignment emits a closed case classification naming its exact
dimension cases, `ordinary | boundary | negative` kind, expected preserved
laws, and expected violated laws. Combination-only violations are declared on
the assignment classification rather than guessed from one dimension.
`assignment_schema_ref` resolves the closed
`mutation-assignment/v1` schema with exact fields `assignment_id`, sorted
`case_ids`, canonical `values`, aggregate `kind`, sorted
`expected_preserved_law_refs`, and sorted `expected_violated_law_refs`. Every
mutate run binds the resulting assignment ref/fingerprint in runs.jsonl and
EER; omission is `invalid_environment`.

## Chart classes

### Normative decision

Use for one bounded decision such as ask/act, inspect/invent, route/respond,
verify/declare, continue/stop, or respect/broaden scope. Default to
one_step_decision with transition_model none or partial and at least one
judgeable or denied class.

Recommended output:

~~~yaml
decision:
  action_class: inspect | ask | act | plan | tool | verify | stop | respond | handoff
  content:
  tool:
  arguments:
  relied_on_facts: []
  unresolved_blocker:
~~~

It evaluates the decision, not prose imitation, and cannot claim downstream task
completion without an executable world.

### Executable episode

Requires a reset recipe, world fingerprint, actor-visible task, executable
support, tool/effect contract, fresh trace, and deterministic hard oracle or
state assertion. It also requires contracted terminal conditions, positive
step/timeout bounds, and an implementation identity. A whole-harness comparison
cuts at session start with no target prior influence.

### Observational

Preserves a failure signature, useful pattern, ambiguity, or blocked
reconstruction. It is diagnostic only and cannot select a candidate, yield a
preference row, yield a trajectory, or count as promotion pass/failure.

## Exclusive action support

The five support classes are disjoint. Validate that every declared action
matches at most one list. Overlap, malformed predicates, or an unverified
classification is invalid_environment.

| Support | Runtime behavior | Status |
|---|---|---|
| executable | Call step, record transition, then evaluate | pass or hard_fail |
| judgeable | Do not call step; evaluate the decision | pass or hard_fail |
| denied | Do not call step; emit deterministic contract failure | hard_fail |
| observed_only | Preserve historical evidence only | attempted fresh transition is unsupported_counterfactual |
| unsupported | No honest execution or judgment exists | attempted fresh transition is unsupported_counterfactual |

unsupported_counterfactual is a run status, not an agent failure and not an
invalid_environment alias. invalid_environment is reserved for malformed,
drifted, leaked, incomplete, or unverifiable environment construction.

## World fidelity and claims

| World/evaluator condition | Maximum default claim |
|---|---|
| Exact resettable world + deterministic authority + fresh paired untouched holdout | promotion evidence, subject to all protected laws |
| Exact or behaviorally adequate approximate world + fresh paired authority | harness_selection |
| Direct correction + leakage-free judgeable decision + fresh passing action | preference_training and harness_selection |
| Bounded attribution or transcript-only decision | development/diagnostic unless fresh evidence discriminates |
| Ambiguous attribution, absent world, observational chart, or model-only judgment | diagnostic |
| Missing actor-readable proof, active holdout exposure, evaluator drift, or closure mismatch | no selecting claim; invalid_environment |

promotion means the evidence packet may support a separately authorized adoption
decision. It never grants mutation authority. Historical outcomes alone never
select or promote.

## Required validation

Require:

~~~text
EC-v1 root and ordered chart identities
recursive closure verification for all execution-relevant bytes
exact source bundle and immutable corpus selection
exclusive support classifications and unsupported default
actor/evaluator projection separation
actor-readable inventory, fingerprint, and tool-access proof for selecting use
group-safe frozen partitions and holdout blindness
root/chart split metadata equality
implementation/seed identity plus contracted effects, termination, support matcher, and mutation domains when used
complete baseline and candidate harness manifests for compare mode
same-comparison fingerprints and one semantic factor for compare mode
hard-oracle precedence and protected dimensions
claim class no stronger than authority, attribution, world, and freshness
~~~

Comparison-only validation and artifacts apply only to `compare`. `design`,
`implement`, `mutate`, and single-harness `run` remain valid without inventing a
candidate or recommendation; they still satisfy closure, environment, trace,
and claim laws applicable to their mode.

Missing authority is oracle_gap; conflicting authority is contract_ambiguity;
closure, leakage, or boundary drift is invalid_environment. Do not fill any gap
silently.
