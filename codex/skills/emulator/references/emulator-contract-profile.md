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

  environment:
    world_fidelity: exact | approximate | transcript_only | absent
    transition_model: total | partial | none
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
    support:
      executable: []
      judgeable: []
      denied: []
      observed_only: []
      unsupported_default: true

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
        role: source | actor | world | reset | fixture | tool | evaluator

  claim:
    class: diagnostic | preference_training | harness_selection | promotion
    maximum_supported_claim:
    invalidators: []
    limitations: []
~~~

Every field affects execution, visibility, evaluation, claim strength, or
provenance. Do not add decorative metadata.

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
state assertion. A whole-harness comparison cuts at session start with no target
prior influence.

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
root/chart ID, kind, and split metadata equality
complete baseline and candidate harness manifests
same-comparison fingerprints and one semantic factor
hard-oracle precedence and protected dimensions
claim class no stronger than authority, attribution, world, and freshness
~~~

Missing authority is oracle_gap; conflicting authority is contract_ambiguity;
closure, leakage, or boundary drift is invalid_environment. Do not fill any gap
silently.
