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
The closure root is the directory containing the exact `emulator-spec.yaml`
named by the consumer. For a live root it is the atlas root; for an archived
root it is `roots/<root-digest-hex>/`. Every relative reference in the closure
resolves from that closure root, including references nested in subordinate
manifests. Normalize it as a POSIX relative
path before lookup; absolute paths, empty paths, `.`/`..` escape, backslashes,
and conflicting closure-inventory entries for one normalized path are invalid.
Multiple contract fields may reference the same normalized asset only when
every occurrence binds the same fingerprint; the recursively verified closure
inventory contains that path once.

Fingerprints retain the `sha256:<hex>` representation in contract fields. A
fingerprint used in a filename or directory uses only its validated 64-character
lowercase hexadecimal suffix, called `<digest-hex>`; the `sha256:` prefix is
never part of a path component.

Every value used as one filesystem path component, including `atlas_id`,
`chart_id`, `candidate_id`, `comparison_id`, `run_group_id`, `repeat_id`, and
`split.group_id`, is 1-128 lowercase ASCII characters, begins and ends with an
ASCII letter or digit, contains only letters, digits, `.`, `_`, or `-`, and is
neither `.` nor `..`. Validate the component before joining it to a root, then
resolve the destination and prove it remains beneath the owning root before
any create, replace, or removal.

The closure is invalid when a required reference is missing, escapes the atlas
root, has a mismatched digest, or leaves an execution-relevant byte implicit.
External material must be copied into the closure and fingerprinted; no caller
authority makes an absolute or escaping ref valid. Reports record the root
fingerprint, ordered chart fingerprints, and recursively verified closure
inventory.

For `run`, `mutate`, or `compare`, store that inventory at
`reports/<run-group-id>/closure-inventory.json`. For non-executing `design` or
`implement`, store it at
`reports/contracts/<root-digest-hex>/closure-inventory.json` and store the EER
beside it; this content-addressed contract-report namespace is create-new and
does not invent a run group. The inventory uses exact RFC 8785 bytes:

~~~json
{"assets":[{"fingerprint":"sha256:<hex>","mode":"100644","ref":"roots/<root-digest-hex>/<relative-ref>"}],"root_contract_fingerprint":"sha256:<hex>","schema":"emulator-closure-inventory/v1"}
~~~

It includes the archived `emulator-spec.yaml` and every unique regular file
transitively reachable from it, excludes the inventory itself and runtime
outputs, and sorts the duplicate-free `assets` array by `ref`. Each ref begins
with the archive prefix for `root_contract_fingerprint`; its suffix is the
normalized closure-relative path. Mode and fingerprint match the archived
file. A missing reachable file or an extra inventory entry is
`invalid_environment`.

## Root contract

~~~yaml
emulator_contract:
  packet_version: EC-v1
  contract_id: EC-<stable-id>
  origin: source_faithful | designed | mixed
  operation_mode: design | implement | run | mutate | compare

  source:
    kind: session | session_corpus | repository | specification | tests | traces | user_design | existing_contract | mixed
    refs: []
    corpus_digest:
    current_session_excluded: true | false | not_applicable
    limitations: []

  target:
    name:
    kind: agentic_harness | skill | agent_loop | tool_loop | workflow | library_protocol
    harness_roots:
      - root_id:
        precedence:
        mount_path:

  atlas:
    instance_id:  # required for session-derived roots or any root with holdout
    charts:
      - chart_id:
        chart_ref:
        chart_fingerprint:
        kind: normative_decision | executable_episode | observational
        split_group:
        source_group_fingerprint:
        source_identity_descriptors: []
        source_identity_fingerprints: []
        partition: discovery | development | holdout
        required: true | false

    partition_policy:
      group_by: root_session_or_task
      frozen_before_candidate_generation: true
      holdout_visible_to_optimizer: false
      storage_domain_root:
      storage_domain_id:
      exposure_registry_root:
      exposure_registry_id:
      holdout_lock_root:
      partition_claims:
        - ref: partitions/claims/<holdout-key>.partition.json
          fingerprint:
      partition_claim_validation:
        ref: partitions/partition-claim-validation.json
        fingerprint:
      retirement_index:
        ref: holdout-retirements/snapshots/<digest-hex>.json
        fingerprint:
      retirement_markers:
        - ref:
          fingerprint:

  comparison_policy:  # required only for run, mutate, and compare
    execution_mode: single_arm | paired_compare
    cycle_id:  # paired_compare only
    subject: harness
    pre_candidate_policy:
      ref:
      fingerprint:
    optimizer_policy:
      ref:
      fingerprint:
    comparison_implementation:
      ref:
      fingerprint:
    baseline_harness:
      harness_id:
      ref:
      fingerprint:
      capture_provenance_ref:
      capture_provenance_fingerprint:
    candidate_harnesses:
      - candidate_id:
        harness_id:
        ref:
        fingerprint:
        capture_provenance_ref:
        capture_provenance_fingerprint:
        candidate_metadata_ref: harnesses/candidates/<candidate-id>/candidate.yaml
        candidate_metadata_fingerprint:
        candidate_generation_access_proof_ref:
        candidate_generation_access_proof_fingerprint:
        factor_delta_validation_ref:
        factor_delta_validation_fingerprint:
        semantic_delta_attestation_ref:
        semantic_delta_attestation_fingerprint:
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

  closure:
    assets:
      - ref:
        fingerprint:
        file_type: regular
        mode:
        role: partition_claim | partition_validation | access_proof | factor_delta_validation | harness_capture_provenance | comparison_implementation | mutation_generator | other

  output:
    eer: EER-v1
    runs: runs.jsonl
    comparison: comparison.json  # compare mode only
    preferences: true | false
    trajectories: true | false
    curriculum: true | false
    counterexamples: true | false
~~~

`corpus_digest` is SHA-256 of exact RFC 8785 bytes of
`{"schema":"emulator-corpus/v1","source_bundle_fingerprints":[...]}` where the
array is the byte-lexicographically sorted, duplicate-free fingerprints of all
selected source bundles. It binds the selected immutable source set, not a mutable session
directory. `harness_roots` is the ordered runtime layering contract. Each entry
has a stable `root_id`, a unique nonnegative integer `precedence`, and a
nonempty normalized POSIX-relative logical `mount_path`; `.` denotes the
runtime root. Absolute paths, backslashes, empty paths, and any `..` segment
are invalid. Before materialization, resolve every effective
`mount_path/path` destination and prove it remains beneath the isolated runtime
root. These values, not a source-worktree path,
determine lookup and override order. Materialize roots in ascending precedence;
a higher numeric precedence overrides a lower one at the same effective mount
path. Distinct root declarations have unique `root_id` and precedence values.
It enumerates every behavior-bearing root
under experiment. The root may contain one chart; the atlas abstraction does
not require scale.

`atlas.instance_id` is required for any session-derived root or any root with a
holdout chart. It is SHA-256 of the exact UTF-8 sequence
`"emulator-atlas-instance/v1" NUL storage_domain_id NUL canonical-atlas-root-realpath`.
It is absent for a pure designed root with no holdout. Any holdout additionally
requires the user-global exposure registry; there is no registry-free holdout
identity.

Both `session` and `session_corpus` require
`current_session_excluded: true`. Determine this requirement over the complete
recursive source closure, not only the root `source.kind`: `mixed`,
`existing_contract`, or any other wrapper requires `true` whenever a reachable
chart, source bundle, or nested contract is session-derived, and records each
excluded session component. A closure with no session-derived component uses
`false` only for a pure `user_design` source and `not_applicable` otherwise.
No wrapper may hide a nested session source behind `not_applicable`.

`operation_mode` is the operation that authored or executed the closure and is
immutable for the closure and report. The `$emulator` `export` request reads an
existing closure and emits eligible outputs without rewriting it; it preserves
the originating `operation_mode` rather than creating an export-identity
variant. `comparison_policy` is absent for non-executing `design` and
`implement` roots. It is required for `run`, `mutate`, and `compare`: `run` and
`mutate` require `single_arm`, while `compare` requires `paired_compare`.
`single_arm` roots MUST NOT select a holdout chart. Holdout execution is valid
only in `paired_compare` under the reservation, locking, and consumption
protocol; a holdout in `run` or `mutate` is an invalid contract rather than an
unreserved execution route.
`paired_compare` roots MUST NOT select a mutation assignment or mutation case;
EC-v1 mutation evidence is single-arm only.
Export preserves whichever state the existing root has. `execution_mode` does
not replace the operation mode.

The four output booleans bind user authorization to emit each eligible dataset.
They are frozen before execution. Export may emit only a dataset whose boolean
is `true`, and still applies the chart-level eligibility and privacy rules; it
does not rewrite `false` to `true`. Missing authorization is a valid empty
export, not permission inferred from the export request.

The evaluator-only pre-candidate policy asset includes the ordered selecting
chart entries (`chart_id`, fingerprint, split group, partition, and `required`),
exact atlas-relative source-identity partition-claim snapshot
refs/fingerprints and their validation asset, factor, partition
snapshot, runtime configuration, repeats, randomness policy, improvement
threshold, the factor-to-targeted-chart predicate, protected dimensions and
their evaluator-result bindings, exact factor-owner paths, runtime-configuration
keys, and deterministically derived runtime-surface fields,
non-hard regression tolerance, candidate budget, exact baseline harness
fingerprint, exact immutable optimizer-input inventory ref/fingerprint,
predeclared candidate-output roots and pre-state inventory ref/fingerprint,
exact optimizer tool/effect policy ref/fingerprint and required complete trace
schema,
exact candidate-generation runner ref/fingerprint, and exact
comparison-implementation ref/fingerprint. It is never
mounted or supplied to candidate optimization. The separately fingerprinted
optimizer policy contains only the selected factor, its exact factor-owner
paths, non-holdout structured byte selectors, runtime-configuration keys,
approved derived runtime-surface fields, runtime constraints, candidate budget, and
discovery/development inputs; it contains no holdout IDs,
tags, partitions, fingerprints, evaluator criteria, thresholds, or commitment
digest from which they can be enumerated.
The predicate is an ordered `targeted_chart_rules` array whose entries contain
exact `factor`, `chart_fingerprint`, and boolean `targeted`; every selecting
chart appears exactly once. Post-outcome classification is forbidden.
Before candidate generation, validation requires exact equality between the
two policies' selected factor, factor-owner paths, structured byte selectors,
runtime-configuration keys, approved derived runtime-surface fields, runtime
constraints, and candidate budget.
Missing or unequal shared fields stop with `comparison_drift`; fingerprints do
not make divergent policy values compatible.
Every factor-owner file path is the root-qualified pair
`{"root_id":"<root-id>","path":"<logical-path>"}`; a flat path is invalid
because layered roots may contain the same logical name.
After candidate fingerprints freeze, the final root's selecting chart list,
chart/evaluator fingerprints, partition snapshot, runtime configuration,
repeats, randomness policy, protected dimensions, threshold, and budget MUST
equal the evaluator-only pre-candidate commitment. Candidate manifest refs are
added afterward together with the corresponding derived per-candidate
factor-delta validation refs and fingerprints. Those validation assets MUST be
deterministic functions only of the frozen baseline manifest, candidate
manifest, pre-candidate factor-owner declaration, and—only for a mixed-owner
file—the separately fingerprinted post-diff human semantic-delta attestation
named by both the candidate metadata and validation asset. The attestation can
classify the complete frozen diff but cannot add owner paths, selectors, policy,
or evaluator authority. Any other drift is
`holdout_contaminated`.

`comparison_implementation` binds the exact aggregation, delta, precedence,
and recommendation implementation. Its ref/fingerprint MUST equal the
pre-candidate commitment and is repeated in each pairwise EER and
`comparison.json`. It is evaluator-only, immutable across arms, and cannot be
modified by a candidate. Missing or unequal bytes are
`evaluator_contaminated`; no recommendation is eligible.

Comparisons are harness comparisons. `subject` is therefore exactly `harness`,
and the recursive root closure contains fingerprinted baseline and candidate
harness manifests. Actor/runtime and environment-implementation identities are
run facts, not selectable comparison subjects. Every candidate entry names the
exact harness manifest whose fingerprint the corresponding comparison and runs
must repeat. It also binds the deterministic
`harnesses/candidates/<candidate-id>/candidate.yaml` metadata bytes; candidate
metadata, actual candidate-generation access proof, factor-delta validation,
and pairwise EER repeat the same candidate, baseline, factor, and manifest
identities.
The candidate metadata, root candidate entry, factor-delta validation, and
pairwise EER also repeat the same semantic-delta-attestation ref/fingerprint;
both fields are null when no mixed-owner file changes and both are non-null
otherwise.
Every baseline and candidate entry separately binds its evaluator-only capture
provenance asset. That asset proves how logical regular files and safely
recreated internal symlinks were captured
but is not part of the harness behavior fingerprint or factor delta.
For `execution_mode: single_arm`, `baseline_harness` is the single frozen
execution subject and all candidate and candidate-generation fields are absent.
For `execution_mode: paired_compare`, both arms and the applicable candidate policies are
mandatory. This is a mode-neutral subject binding, not invented comparison
state for a standalone run.

For every chart entry, root `chart_id` equals chart `chart_id`, root `kind`
equals chart `kind`, root `split_group` equals chart `split.group_id`, root
`partition` equals chart `split.partition`, and the root's group, ordered
source-identity descriptors, and fingerprints equal the chart's recomputed values. Any mismatch is
`invalid_environment`; neither copy wins by precedence. An observational chart
MUST have root `required: false` because it cannot participate in selection.
Every structurally selection-eligible, non-observational holdout chart MUST have
root `required: true`. Root `required: false` is otherwise limited to
discovery/development or structurally selection-ineligible charts. Eligibility
is true exactly when the frozen chart has `claim.class: harness_selection |
promotion`, its maximum claim is at least that class, evaluator attribution is
`direct`, and it has at least one hard oracle, state assertion, or trace
invariant. It is computed from those declared fields and frozen before hidden
historical suffixes, evaluator details, or outcomes are inspected. A
required holdout that becomes invalid, unsupported, skipped, or ambiguous makes
the comparison `insufficient_evidence`; it is not an excludable chart.
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
    source_identity_descriptors: []
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
      unsupported_default: true | false

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
      correction_review:
        reviewed_subject_ref:
        reviewed_subject_fingerprint:
        human_review_ref:
        human_review_fingerprint:
        reviewed_pattern_ref:
        reviewed_pattern_fingerprint:
        applicability_ref:
        applicability_fingerprint:
        reviewer_independence: true | false
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
    protected_dimensions:
      - dimension_id:
        evaluator_result_ids: []
    success_condition:

  closure:
    assets:
      - ref:
        sha256:
        file_type: regular
        mode:
        role: source | actor | world | reset | fixture | tool | evaluator | reward | partition | mutation_generator

  claim:
    class: diagnostic | preference_training | harness_selection | promotion
    maximum_supported_claim: diagnostic | preference_training | harness_selection | promotion
    invalidators: []
    limitations: []
~~~

Tool permission is fail closed. `allowed` and `denied` are duplicate-free and
disjoint. Every allowed tool has exactly one schema in `schemas`; a tool name
not present in `allowed` is denied even if a schema happens to exist. Every
action projection that selects a tool resolves that exact name before support
classification. An action classified `executable` may select only an allowed
tool. An action selecting a denied or unlisted tool is `denied`; contradictory
lists, missing allowed-tool schemas, or an executable predicate that can select
an unallowed tool make the chart `invalid_environment`.

Every field affects execution, visibility, evaluation, claim strength, or
provenance. Do not add decorative metadata.

For `transition_model: total`, support predicates exhaustively and exclusively
cover every action admitted by `actions.schema`, `unsupported_default` is
`false`, and every admitted action not classified `denied` is `executable`.
`judgeable` and `observed_only` are invalid in a total chart because neither
supplies a next-state transition. A total chart that can fall through to
`unsupported` or lacks executable coverage is `invalid_environment` rather
than partially total.
For `transition_model: none`, `support.executable` is empty. Any nonempty
executable set requires `partial` or `total` plus a fingerprinted transition
implementation; otherwise the chart is `invalid_environment`.

Support classification has exactly one authoritative representation. With
`matcher.kind: inline_predicates`, `classifier_ref` and
`classifier_fingerprint` are null, the five inline lists are authoritative,
and admission proves that every valid action matches at most one explicit
predicate. For `partial` or `none`, `unsupported_default` is `true` and an
action matching none receives exactly the `unsupported` class from that
fallback. For `total`, it is `false` only with the exhaustive coverage proof
required above, so no action can fall through. With
`matcher.kind: asset`, all five inline lists are empty,
`unsupported_default` is `false`, and the bound classifier asset is a total
function from every action admitted by `actions.schema` to exactly one of
`executable`, `judgeable`, `denied`, `observed_only`, or `unsupported`.
Mixed representations, a zero-class result after fallback, or a multiple-class
result make the chart `invalid_environment`. Thus every admitted valid action
has exactly one support class before evaluation, while `step` remains defined
only for `executable`.

For a correction-derived chart to enter holdout or contribute to
`harness_selection`, `promotion`, or `preference_training`, `correction_review`
binds one `correction-review-subject/v1` ref/fingerprint and exactly one
authority route. That subject is the canonical chart projection with the whole
`correction_review` subtree removed, so the finalized chart may bind the review
without the review fingerprinting the finalized chart back. The direct route
has non-null `human_review_ref` and fingerprint and null pattern/applicability
fields. The reused-pattern route has null human-review fields and non-null
reviewed-pattern and applicability ref/fingerprint pairs.
`reviewer_independence` is `true` in either route. The bound review or
reviewed-pattern asset identifies an evaluator-informed reviewer who is
independent of candidate generation; optimizer blindness is proved separately
by the candidate-generation access boundary. Applicability is
evaluator-produced evidence that the reviewed subject satisfies that already
reviewed pattern, not a chart-author declaration. Missing, mixed,
self-authored, cyclic, or non-independent authority limits the chart to
diagnostic/development use.

Closure assets are regular, non-symlink files. Each regular asset binds its executable
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
`read_only`, `isolated_write`, `fixture_only`, `replay_recorded`, `declared_roots`, or `explicit`; the referenced asset defines
the exact recordings, roots, operations, and authority. They are absent only
for fully closed effect modes. A `read_only` policy enumerates every readable
root and excludes evaluator-only, session, credential, and unrelated host
paths. A `full_episode` requires at least one terminal
condition plus positive `max_steps` and `timeout_ms`; other actor modes bind the
smallest applicable limit.

Every protected dimension names at least one hard-oracle, state-assertion, or
trace-invariant result ID from the same evaluator. Every eligible baseline and
candidate run emits all named results. Missing coverage is
`invalid_environment`; an empty or model-judgment-only binding cannot protect a
dimension.

`network: replay_recorded` is replay-only: the runner may return only the exact
fingerprinted recorded responses named by the effect-policy asset and MUST NOT
contact a live endpoint. Live network access is outside EC-v1 and requires a
separately authorized designed contract rather than reinterpretation of this
mode.

Every executable implementation has an exact identity. Its seed-control mode,
seed when controlled, and any sampled failure schedule are explicit and
fingerprinted; `unavailable` is recorded rather than replaced with an invented
seed.

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

Mutation dimensions are optional outside `operation_mode: mutate`. Mutation requires at
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
| executable | Call step, record transition, then evaluate | pass, hard_fail, or ambiguous |
| judgeable | Do not call step; evaluate the decision | pass, hard_fail, or ambiguous |
| denied | Do not call step; emit deterministic contract failure | hard_fail |
| observed_only | Preserve historical evidence only | attempted fresh transition is unsupported_counterfactual |
| unsupported | No honest execution or judgment exists | attempted fresh transition is unsupported_counterfactual |

unsupported_counterfactual is a run status, not an agent failure and not an
invalid_environment alias. invalid_environment is reserved for malformed,
drifted, leaked, incomplete, or unverifiable environment construction.
This intentionally resolves the source-level wording conflict in favor of the
dedicated status: support can be honest and partial even when the requested
counterfactual is unavailable.

## World fidelity and claims

| World/evaluator condition | Maximum default claim |
|---|---|
| Exact resettable world + deterministic authority + fresh paired untouched holdout | promotion evidence, subject to all protected laws |
| Exact or behaviorally adequate approximate world + fresh paired untouched holdout | harness_selection |
| Direct correction + leakage-free judgeable decision + fresh passing action | preference_training; selection only after an untouched holdout comparison |
| Bounded attribution or transcript-only decision | development/diagnostic unless fresh evidence discriminates |
| Ambiguous attribution, absent world, observational chart, or model-only judgment | diagnostic |
| Missing actor-readable proof, active holdout exposure, evaluator drift, or closure mismatch | no selecting claim; invalid_environment |

promotion means the evidence packet may support a separately authorized adoption
decision. It never grants mutation authority. Historical outcomes alone never
select or promote.
Every `harness_selection` claim requires an untouched
holdout at the frozen partition snapshot; discovery/development evidence may
nominate or train but cannot select.

`maximum_supported_claim` is the author-time ceiling proved by the chart's
authority, attribution, world fidelity, visibility proof, and partition.
`claim.class` is the use requested for the chart and cannot exceed that ceiling:

- `diagnostic` admits discovery/development diagnosis only;
- `preference_training` additionally requires direct preference authority and
  an eligible fresh passing chosen action, and is forbidden while the chart is
  active holdout;
- `harness_selection` additionally requires a fresh paired untouched-holdout
  comparison under the frozen boundary;
- `promotion` additionally requires an exact resettable world, deterministic
  authority, and satisfaction of every report-level adoption condition.

A fresh run realizes no stronger claim than both fields and its actually proved
authority. `promotion` is a comparison-level evidence strength: no single
chart, historical outcome, discovery run, or development run realizes it by
itself.

## Required validation

Require:

~~~text
EC-v1 root and ordered chart identities
recursive closure verification for all execution-relevant bytes
canonical source-bundle manifest and immutable corpus selection
exclusive support classifications and unsupported default
actor/evaluator projection separation
canonical observed actor-readable inventory and per-process access proof for selecting use
exact delivered actor context bound to each access proof
post-generation access proof bound to the actual fresh optimizer context and process
group-safe frozen partitions and holdout blindness
atlas-instance identity bound through holdout reservation, locks, and consumption
holdout charts absent from single-arm run and mutate roots
mutation cases absent from paired compare roots and execution rows
root/chart split metadata equality
implementation/seed identity plus contracted effects, termination, support matcher, and mutation domains when used
fingerprinted baseline and candidate harness manifests
same-comparison fingerprints and one semantic factor for compare mode
closed selector semantics and complete factor-delta validation for candidate changes
unchanged manifest path/type/mode/symlink surface across harness arms
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
