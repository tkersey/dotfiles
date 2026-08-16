# Emulator Contract Profile

emulator-spec.yaml is the EC-v1 root of one content-addressed contract closure
owned by $emulator.

EC-v1 is intentionally corrected in place because the repository baseline has
no committed instances or consumers. An `existing_contract` using the obsolete
pre-adoption scenario shape is not silently interpreted: explicitly upgrade it
to this closure shape or stop with `contract_ambiguity`. No compatibility layer
is implied by the retained label.

## Identity and closure

~~~text
root_contract_fingerprint = SHA-256(exact emulator-spec.yaml UTF-8 bytes)
chart_fingerprint         = SHA-256(exact chart YAML UTF-8 bytes)
atlas_identity            = root fingerprint + ordered chart fingerprints
atlas_fingerprint         = SHA-256(
  UTF-8("emulator-atlas-identity/v1") || 0x00 ||
  UTF-8(root_contract_fingerprint) ||
  for each ordered chart fingerprint: 0x00 || UTF-8(chart_fingerprint)
)
~~~

The encoded fingerprints include the literal `sha256:` prefix and lowercase
hex text. There is no terminal NUL.

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
    kind: session | session_corpus | repository | specification | tests | traces | user_design | existing_contract | mixed
    refs: []
    corpus_digest:
    current_session_excluded: true | false | not_applicable
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
        source_group_fingerprint:
        source_identity_fingerprints: []
        partition: discovery | development | holdout
        required: true | false

    partition_policy:
      group_by: root_session_or_task
      frozen_before_candidate_generation: true
      holdout_visible_to_optimizer: false
      holdout_lock_root:
      retirement_index:
        ref: holdout-retirements/snapshots/<fingerprint>.json
        fingerprint:
      retirement_markers:
        - ref:
          fingerprint:

  comparison_policy:
    subject: harness | actor | environment_implementation
    pre_candidate_policy:
      ref:
      fingerprint:
    optimizer_policy:
      ref:
      fingerprint:
    baseline_harness:
      ref:
      fingerprint:
    candidate_harnesses:
      - candidate_id:
        ref:
        fingerprint:
    baseline_subject:
      ref:
      fingerprint:
    candidate_subjects:
      - candidate_id:
        ref:
        fingerprint:
    candidate_factor_policy: one_semantic_owner
    stochastic_repeats: 3
    deterministic_repeats: 1
    stochastic_evidence:
      matched_randomness_when_available: true
      uncontrolled_repeat_count:
      improvement_rule:
      frozen_before_candidate_generation: true
    order_blinding: true
    swapped_judge_order: true
    hard_oracle_precedence: true
    protected_regressions_forbidden: true

  output:
    eer: EER-v1
    runs: runs.jsonl
    comparison: comparison.json  # compare mode only
    preferences: false
    trajectories: false
    curriculum: false
    counterexamples: false
~~~

corpus_digest binds the selected immutable source set, not a mutable session
directory. harness_roots enumerates every behavior-bearing root under
experiment. The root may contain one chart; the atlas abstraction does not
require scale.

Both `session` and `session_corpus` require
`current_session_excluded: true`. `mixed` also requires `true` whenever any
component is session-derived, and records each excluded session component;
mixed sources without sessions use `not_applicable`. A pure `user_design`
source requires `false`; every other source kind requires `not_applicable`.

The evaluator-only pre-candidate policy asset includes the ordered selecting
chart entries (`chart_id`, fingerprint, split group, partition, and `required`),
exact source-identity partition-claim refs/fingerprints, factor, partition
snapshot, runtime configuration, repeats, randomness policy, improvement
threshold, the factor-to-targeted-chart predicate, protected dimensions,
non-hard regression tolerance, and candidate budget. It is never
mounted or supplied to candidate optimization. The separately fingerprinted
optimizer policy contains only the selected factor, runtime constraints,
candidate budget, and discovery/development inputs; it contains no holdout IDs,
tags, partitions, fingerprints, evaluator criteria, thresholds, or commitment
digest from which they can be enumerated.
The predicate is an ordered `targeted_chart_rules` array whose entries contain
exact `factor`, `chart_fingerprint`, and boolean `targeted`; every selecting
chart appears exactly once. Post-outcome classification is forbidden.
Before candidate generation, validation requires exact equality between the
two policies' selected factor, runtime constraints, and candidate budget.
Missing or unequal shared fields stop with `comparison_drift`; fingerprints do
not make divergent policy values compatible.
After candidate fingerprints freeze, the final root's selecting chart list,
chart/evaluator fingerprints, partition snapshot, runtime configuration,
repeats, randomness policy, protected dimensions, threshold, and budget MUST
equal the evaluator-only pre-candidate commitment. Candidate manifest refs are
the only comparison inputs added afterward. Any other drift is
`holdout_contaminated`.

`subject: harness` requires fingerprinted baseline and candidate harness
manifests in the recursive root closure.
Designed synthetic comparisons may use `actor` or
`environment_implementation` with fingerprinted baseline and candidate subject
bundles instead; the same one-factor, same-boundary, fresh-arm, and evaluator-
immutability laws apply. Fields that do not apply to the declared subject are
absent rather than filled with invented harness identities. Every candidate
entry names the exact manifest whose fingerprint the corresponding comparison
and runs must repeat.

For every chart entry, root `chart_id` equals chart `chart_id`, root `kind`
equals chart `kind`, root `split_group` equals chart `split.group_id`, root
`partition` equals chart `split.partition`, and the root's group and ordered
source-identity fingerprints equal the chart's recomputed values. Any mismatch is
`invalid_environment`; neither copy wins by precedence. An observational chart
MUST have root `required: false` because it cannot participate in selection.
Root `chart_id` values are unique; duplicates are `invalid_environment` even
when their fingerprints happen to match.

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
    source_kind: session | session_corpus | repository | specification | tests | traces | user_design | existing_contract | mixed
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
    source_group_fingerprint:
    source_identity_fingerprints: []
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
    action_projection:
      source: decision_output | tool_call_event | actor_action_event
      kind: json_pointer
      path:
      cardinality: exactly_one_per_support_check

  environment:
    world_fidelity: exact | approximate | transcript_only | absent
    transition_model: total | partial | none
    world_ref:
    world_fingerprint:
    approximation:
      difference_inventory_ref:
      difference_inventory_fingerprint:
      equivalence_witness_ref:
      equivalence_witness_fingerprint:
    implementation:
      ref:
      fingerprint:
      seed_control: fixed | sampled | unavailable
      seed:
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
    tools:
      asset_ref:
      asset_fingerprint:
      allowed: []
      denied: []
      schemas: {}
    effects:
      network: deny | fixture_only | replay_recorded
      filesystem: read_only | isolated_write | declared_roots
      external_side_effects: deny | fixture_only | explicit
      policy_ref:
      policy_fingerprint:
    termination:
      terminal_conditions: []
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
      judgeable: []
      denied: []
      observed_only: []
      unsupported_default: true

  mutation:
    dimensions:
      - dimension_id:
        domain: []
        preserved_law_refs: []
        shrink_strategy:
    generator_ref:
    generator_fingerprint:

  evaluator:
    evaluator_ref:
    evaluator_fingerprint:
    implementation_ref:
    implementation_fingerprint:
    authority:
      class: explicit_user_correction | deterministic_test | state_assertion | trace_invariant | human_attestation | fresh_comparison | ambiguous
      refs: []
      attribution: direct | bounded | ambiguous
    hard_oracles: []
    state_diff: []
    trace_invariants: []
    reward:
      enabled: true | false
      definition_ref:
      definition_fingerprint:
      channels: []
      aggregation:
      authority_refs: []
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
        file_type: regular
        mode:
        role: source | actor | world | reset | fixture | tool | evaluator | reward | partition

  claim:
    class: diagnostic | preference_training | harness_selection | promotion
    maximum_supported_claim:
    invalidators: []
    limitations: []
~~~

Every field affects execution, visibility, evaluation, claim strength, or
provenance. Do not add decorative metadata.

For `transition_model: total`, support predicates exhaustively and exclusively
cover every action admitted by `actions.schema`, and `unsupported_default` is
`false`. A total chart that can fall through to `unsupported` is
`invalid_environment` rather than partially total.

Closure assets are regular, non-symlink files unless a chart explicitly defines
and fingerprints symlink semantics. Each regular asset binds its executable
mode as well as exact bytes; file-type or mode drift is
`invalid_environment`.

When `reward.enabled` is true, the exact definition asset, named channels,
aggregation rule, and authority refs are mandatory and the asset appears in the
recursive closure. When false, the definition fields are null and channels and
authority refs are empty. Reward never supplies missing oracle authority.
`fresh_comparison` records relative fresh evidence only; it is never the sole
authority for an oracle or success condition and requires at least one
independent correction, test, assertion, invariant, or human-attestation ref.

`policy_ref` and `policy_fingerprint` are required whenever effects use
`read_only`, `replay_recorded`, `declared_roots`, or `explicit`; the referenced asset defines
the exact recordings, roots, operations, and authority. They are absent only
for fully closed effect modes. A `read_only` policy enumerates every readable
root and excludes evaluator-only, session, credential, and unrelated host
paths. A `full_episode` requires at least one terminal
condition plus positive `max_steps` and `timeout_ms`; other actor modes bind the
smallest applicable limit.

`network: replay_recorded` is replay-only: the runner may return only the exact
fingerprinted recorded responses named by the effect-policy asset and MUST NOT
contact a live endpoint. Live network access is outside EC-v1 and requires a
separately authorized designed contract rather than reinterpretation of this
mode.

Every executable implementation has an exact identity. Its seed-control mode,
seed when controlled, and any sampled failure schedule are explicit and
fingerprinted; `unavailable` is recorded rather than replaced with an invented
seed.

For `subject: environment_implementation`, the shared chart omits the singular
implementation ref/fingerprint and each arm resolves them from its frozen
subject bundle. Other subject kinds use the chart implementation block. The
actor's `action_projection` deterministically extracts exactly one action from
the validated output before support classification; projection failure is
`hard_fail`.

Executable charts also bind exactly one canonical `world_ref` and
`world_fingerprint`; closure assets may contain supporting world material but
do not create an alternate world identity.

Every support entry has a unique ID and deterministic predicate in the declared
action schema plus nonempty authority references to source evidence, evaluator
authority, or an explicit designed-chart decision. The inline predicate language is exact canonical-JSON equality
at a JSON Pointer: `path` selects one action value and `value` is the required
canonical value. Multiple conditions require separate, explicitly composed
predicate assets rather than implicit prose. An asset matcher binds its
classifier bytes through `classifier_ref` and `classifier_fingerprint`. A
classifier that is missing, nondeterministic, or cannot prove the five classes
disjoint makes the environment invalid.

Mutation dimensions are optional outside `mode: mutate`. Mutation requires at
least one finite or otherwise bounded domain, preserved-law references, and a
deterministic shrink strategy. An external generator is fingerprinted and
included in the chart closure. No mutation widens action support or source
authority.

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
for harness comparison: fingerprinted baseline and candidate harness manifests
for actor or environment comparison: fingerprinted baseline and candidate subject bundles
same-comparison fingerprints and one semantic factor for compare mode
predetermined stochastic evidence rule and matched randomness when available
fingerprinted pre-candidate policy snapshot for compare mode
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
