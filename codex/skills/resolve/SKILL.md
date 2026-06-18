---
name: resolve
description: "Resolve the current branch through a CAS-first, scope-chartered Review Governor with falsifiable one-shot normal forms, branch-liability adjudication, cumulative owner-pressure accounting, a hard growth fuse, durable negative-route ratcheting, mandatory review distillation, and current-head proof/PR closure. Use for `$resolve`, branch review/fix/validate/commit/push/PR-sweep closure, RGR-v3, RGR-V3-MUTATION-PERMIT, same-family recurrence, normal-form falsification, finding liability, owner pressure, production growth, or long CAS loops. Not for one-shot review, PR creation, merge/land, or isolated implementation."
metadata:
  version: "3.0.0"
  activation_cost: high
  default_depth: full
---

# Resolve

## Mission

Drive the current branch to a proof-backed, pushed, PR-swept state without allowing a review system to turn every valid adjacent defect into branch growth.

```text
Reviews sense.
The governor establishes branch liability and system state.
Only a valid permit actuates mutation.
A falsified normal form cannot be renamed and retried.
A tripped fuse ends delivery-branch patching.
```

The key distinction:

```text
valid finding != current branch liability
locally valid patch != system-level normal form
runtime rejection != invalid state unrepresentable by construction
committed increments != controlled accumulation
```

## Governing invariant

A successful resolve run does all of the following:

1. fixes every finding for which the current branch is liable;
2. captures valid adjacent findings that are not branch liabilities without absorbing them into scope;
3. permits at most one ordinary normal-form decision per counterexample family;
4. treats recurrence after that normal form as falsification;
5. trips a hard fuse on semantic or cumulative pressure;
6. permits no post-fuse delivery mutation except deletion/collapse, boundary redesign, or a rederived distilled normal form;
7. closes against a frozen review charter and a final broad holdout;
8. leaves enough state for a future report to determine whether accumulation was actually controlled.

## Activation boundary

Use `$resolve` when the user wants current-branch review resolution through:

```text
sense
-> adjudicate liability
-> govern route
-> permit
-> implement
-> prove
-> review
-> commit/push
-> PR sweep
-> closure
```

Do not use when:

- one-shot review only;
- PR creation only: `$ship`;
- merge/checks/cleanup: `$land`;
- isolated claim adjudication: `$review-adjudication`;
- selected-route implementation only: `$fixed-point-driver` or `$accretive-implementer`;
- final proof only: `$verification-closure`.

## Root ownership

Root owns:

- branch/base/head/fingerprint pins;
- review charter;
- finding identity and liability;
- cluster and counterexample-family identity;
- normal-form register;
- governor fuse;
- route selection;
- mutation permits;
- delivery-branch mutation;
- commits/pushes;
- PR-thread disposition;
- closure report.

Subagents and companion skills are read-only unless a bounded implementation handoff is explicitly issued.

## Backend and proof tuple

CAS-first. Native review is fallback-only after recorded CAS failure or explicit user request.

Every review receipt must bind:

```yaml
review_tuple:
  backend:
  base_ref:
  base_sha:
  head_sha:
  target_fingerprint:
  charter_id:
```

A change to backend, base, head, fingerprint, or charter invalidates prior clean-review receipts.

## Review charter

Run one initial broad sensing review, then freeze the branch's review charter before review-driven mutation expands.

```yaml
review_charter:
  charter_version: RC-v1
  charter_id: "RC-..."
  branch:
  base_sha:
  initial_head_sha:
  objective:
  acceptance_criteria: []
  in_scope_counterexample_families: []
  in_scope_owners: []
  explicit_non_goals: []
  proof_bar: []
  frozen: yes | no
  frozen_at:
```

Rules:

- The initial broad review discovers candidate findings.
- Freeze the charter after the first adjudication/governor pass.
- Every later finding must pass the liability gate.
- A valid adjacent preexisting finding does not automatically enter branch scope.
- Adding a new family to the charter requires an explicit scope-change decision and resets the charter-bound clean streak.

## Review horizon

Default closure horizon:

```text
initial broad sensing review
-> charter freeze
-> targeted review/proof against chartered families
-> 2 consecutive charter-clean current-head reviews
-> 1 final broad holdout current-head review
-> PR sweep
```

A review is `closure-clean` when no unresolved **branch-liable** finding remains.

A final holdout may find a valid adjacent preexisting defect and still be closure-clean when:

- liability is `adjacent_preexisting` or `reviewer_preference`;
- no current acceptance criterion depends on it;
- it is captured as a follow-up or negative/learning artifact;
- no mutation is authorized in the current branch.

Do not turn a broad holdout into an unbounded repository-hardening campaign.

## Evidence discipline

Every finding separates:

```yaml
finding_evidence:
  finding_id:
  source: cas | native_review | pr_comment | validation | user
  observed_fact:
  review_claim:
  proposed_change:
  uncertainty:
  current_artifact_refs: []
```

Review text is a sensor input, not implementation scope.

## Finding liability gate

Before route selection, classify whether the branch is liable.

```yaml
finding_liability:
  liability_version: FL-v1
  finding_id:
  relation:
    introduced_by_current_diff |
    exposed_and_required_by_current_acceptance |
    preexisting_but_blocks_current_invariant |
    adjacent_preexisting |
    reviewer_preference |
    unknown
  evidence_refs: []
  current_acceptance_dependency:
  mutation_allowed: yes | no
  disposition:
    fix_in_branch |
    validate_only |
    capture_followup |
    resolve_thread_only |
    reject |
    blocked
  reason:
```

Mutation is normally allowed only for:

```text
introduced_by_current_diff
exposed_and_required_by_current_acceptance
preexisting_but_blocks_current_invariant
```

Rules:

- `adjacent_preexisting` -> capture follow-up; no production mutation.
- `reviewer_preference` -> reject or resolve thread with proof; no production mutation.
- `unknown` -> validate-only or blocked.
- `preexisting_but_blocks_current_invariant` needs explicit proof that current branch acceptance cannot be met without resolving it.
- A valid finding can be out of scope.

## Cluster and counterexample-family identity

Track both:

```yaml
finding_identity:
  cluster_id:
  counterexample_family:
  owner_candidate:
  failure_surface:
```

A cluster may contain multiple counterexample families.

Do not treat `same cluster` as automatically `same family`.

The semantic fuse uses same-family recurrence after a normal form.

## Normal-form register

A normal form is a falsifiable prediction, not praise for a local patch.

```yaml
normal_form_register:
  - normal_form_id: "NF-..."
    cluster_id:
    counterexample_family:
    owner:
    representation_or_rule:
    closure_prediction:
    selected_at_head:
    selected_route: normal-form-decision | distilled-normal-form
    status: proposed | active | falsified | superseded | closed
    proof_matrix_ids: []
    falsified_by: []
    negative_evidence_id: "none | NEG-..."
```

Rules:

1. At most one ordinary `normal-form-decision` may be active per counterexample family.
2. A same-family finding after that normal form is proof that its closure prediction failed.
3. On failure:
   - set status `falsified`;
   - capture durable negative evidence when the CLI is available;
   - trip the governor fuse;
   - prohibit another ordinary normal-form decision for that family.
4. A new `distilled-normal-form` is allowed only after a passing Review Distillation Receipt and must differ at the representation, boundary, rule, or ownership level—not only by adding another predicate.
5. Cosmetic renaming does not create a new normal form.

## Review compression

Use `$review-compression-compiler`:

- required at the second same-cluster finding;
- blocking at the third same-cluster finding;
- required immediately when a normal form is falsified.

It contributes directly to RGR-v3:

```yaml
review_cluster_compilation:
  cluster_id:
  counterexample_families: []
  branch_liabilities: []
  normal_forms_tried: []
  falsified_route_families: []
  owner_pressure:
  lower_surface_candidates: []
  surfaces_to_retire: []
  proof_matrix:
  fuse_recommendation:
  distillation_required: yes | no
```

It is read-only.

## Cumulative owner pressure

Owner coarseness is derived from cumulative facts, not asserted.

```yaml
owner_pressure:
  pressure_version: OP-v1
  cluster_start_sha:
  owner_symbol:
  owner_file:
  same_cluster_count:
  findings_after_first_fix:
  permits_against_owner:
  owner_mutations_since_cluster_start:
  same_owner_commit_count_since_cluster_start:
  apply_patch_count_since_cluster_start:
  production_insertions_since_cluster_start:
  production_deletions_since_cluster_start:
  production_net_since_cluster_start:
  validation_branches_added:
  evidence_predicates_added:
  helpers_added:
  public_symbols_added:
  compatibility_or_fallback_paths_added:
  tests_added:
  tests_retired_or_merged:
  surfaces_retired_or_collapsed: []
  thresholds:
    max_owner_mutations: 3
    max_same_owner_commits: 3
    max_apply_patch_calls: 10
    max_positive_production_net: 250
  pressure_exceeded: yes | no
  owner_too_coarse: yes | no
  clearance_authority:
    measured_below_budget |
    redesign_warrant |
    none
```

Rules:

- `owner_too_coarse: no` is valid only with `measured_below_budget`.
- If pressure is exceeded, `continue_owner` is invalid.
- A redesign warrant may authorize boundary redesign or distillation, not another ordinary branch/predicate addition.
- Count the semantic owner/symbol when possible; file concentration is a backstop.

## Production-net gate

Classify the proposed change honestly:

```yaml
production_net_gate:
  gate_version: PNG-v1
  expected_production_net: negative | zero | positive | unknown
  change_kind:
    representation_elimination |
    surface_reduction |
    predicate_accretion |
    helper_accretion |
    test_accretion |
    mixed
  invalid_state_unrepresentable_by_construction: yes | no
  representation_change_evidence:
  deletion_or_collapse_offset:
    - surface:
      action: delete | collapse | canonicalize | privatize | decommission
  positive_net_warrant:
    none |
    representation_elimination |
    explicit_scope_expansion |
    distilled_boundary_redesign
  allowed: yes | no
  reason:
```

Definitions:

- Adding a runtime guard, validation branch, predicate, helper, or error path is not representation elimination.
- Detecting/rejecting an invalid state is not the same as making it unrepresentable.
- A test does not offset production growth.
- After fuse trip, positive production net is allowed only when:
  - the change is true representation elimination with construction-level proof; or
  - a passing distillation/boundary-redesign receipt shows it is the lowest total-system-surface route and names surfaces retired.
- Otherwise require production net `<= 0`.

## Governor fuse

The fuse is a state transition, not a warning.

```yaml
governor_fuse:
  fuse_version: GF-v1
  semantic_triggers:
    same_family_after_normal_form: yes | no
    normal_form_falsified: yes | no
  quantitative_triggers:
    same_cluster_count_gte_3: yes | no
    findings_after_first_fix_gte_2: yes | no
    owner_mutations_gte_3: yes | no
    same_owner_commits_gte_3: yes | no
    apply_patch_calls_gte_10: yes | no
    production_net_gt_250: yes | no
  fuse_state: open | tripped
  tripped_at:
  trip_reasons: []
  delivery_mutation_frozen: yes | no
  allowed_routes:
    - proof-only-no-mutation
    - capture-followup
    - delete-collapse-canonicalize
    - review-distillation-mode
    - boundary-redesign
    - blocked
```

Hard rules:

- `same_family_after_normal_form: yes` always trips the fuse.
- Any default quantitative threshold trips the fuse unless a repo-specific stricter threshold is already documented.
- Once tripped, ordinary `normal-form-decision`, raw `mutate-existing-owner`, predicate accretion, helper accretion, and one-wound test accretion are prohibited.
- The fuse remains tripped until a passing Review Distillation Receipt yields a rederived route or the run blocks.
- No delivery-branch mutation after trip without a distillation or deletion/boundary-redesign permit.

## Negative-ledger ratchet

Use the repo-local durable ledger.

Preferred command after the hardened CLI is available:

```bash
ledger gate \
  --root . \
  --cluster "$CLUSTER" \
  --route "$ROUTE" \
  --route-family "$ROUTE_FAMILY" \
  --counterexample-family "$COUNTEREXAMPLE_FAMILY" \
  --failure-surface "$FAILURE_SURFACE" \
  --owner "$OWNER" \
  --artifact "$HEAD_SHA" \
  --same-cluster-count "$N" \
  --require-capture-on-recurrence \
  --format yaml
```

Compatibility fallback for the current CLI:

```bash
ledger map --route "$ROUTE" --cluster "$CLUSTER" --artifact "$HEAD_SHA"
ledger show --id <matching-id>
ledger capture --json <capture-file>
```

Fallback rules:

- A cluster-only match is related evidence, not automatically a route exclusion.
- Confirm exact route/family/applicability with `ledger show`.
- If a same-family finding recurs after a permitted route, `ledger capture` is mandatory before another permit.
- Missing store or failed query blocks mutation.
- `no active exclusion` is not sufficient after recurrence unless a record is created or referenced.

Required gate projection:

```yaml
negative_route_gate:
  gate_version: NRG-v2 | compatibility-v1
  query_or_map: yes | no
  ledger_available: yes | no
  command:
  exit_code: 0 | 2 | 3
  records_scanned:
  active_exclusion_match: yes | no | unknown
  exclusion_id: "none | NEG-..."
  prior_normal_form_falsified: yes | no
  capture_required: yes | no
  capture_created: yes | no
  captured_neg_id: "none | NEG-..."
  eliminated_route_family:
  route_changed_at_leverage_level: yes | no
  handoff_allowed: yes | no
```

After a normal form is falsified:

```text
capture_created must be yes
route_changed_at_leverage_level must be yes
```

A second permit in the same family with `route_changed_at_leverage_level: no` is invalid.

## Proof matrix gate

```yaml
proof_matrix_gate:
  gate_version: PMG-v1
  counterexample_family:
  family_matrix_present: yes | no
  one_test_per_wound: yes | no
  existing_tests_extended: []
  tests_added: []
  tests_retired_or_merged: []
  proof_commands: []
  allowed: yes | no
```

After recurrence:

- one-test-per-wound without a family matrix is blocked;
- prefer table/invariant/authority/version matrices;
- prefer extending/compacting existing tests;
- test growth never independently warrants production growth.

## Review distillation state transition

When the fuse trips, mutation mode ends and distillation mode begins.

```text
Review lab learns.
Delivery branch forgets the exploratory patch history.
```

Produce:

```yaml
review_distillation_receipt:
  receipt_version: RDR-v1
  cluster_id:
  counterexample_family:
  frozen_delivery_base:
  lab_artifact:
    kind: worktree | branch | scratch-record
    ref:
  branch_liability_boundary:
  canonical_owner:
  normal_forms_falsified: []
  route_families_eliminated: []
  counterexamples: []
  surfaces_to_retire: []
  candidate_routes:
    - route:
      leverage_level:
      expected_production_net:
      surfaces_retired: []
      rejected_because:
  selected_route:
    route: delete-collapse-canonicalize | distilled-normal-form | boundary-redesign | blocked
    leverage_level:
    why_not_lower_surface:
  proof_matrix:
  delivery_rederivation:
    rederive_from_frozen_base: yes | no
    cherry_pick_lab_commits: no
    permitted_scope: []
    forbidden_actions: []
  gate:
    distillation_complete: pass | fail
    delivery_mutation_allowed: yes | no
```

Trigger is mandatory when:

- a normal form is falsified;
- same cluster reaches 3;
- cumulative pressure trips the fuse;
- CAS repeatedly finds adjacent same-family defects after green proof;
- the dirty tree contains multiple review-driven repairs.

If a separate worktree/branch is unavailable, use a frozen-base scratch record, but the final delivery patch must still be rederived and must not blindly preserve the repair sequence.

## Route set

Before fuse trip:

```text
no-change
validate-only
resolve-thread-only
capture-followup
delete-collapse-canonicalize
normal-form-decision
blocked
```

After fuse trip:

```text
proof-only-no-mutation
capture-followup
delete-collapse-canonicalize
review-distillation-mode
boundary-redesign
blocked
```

After passing distillation:

```text
delete-collapse-canonicalize
distilled-normal-form
boundary-redesign
blocked
```

`add-new-surface` is not a route. It is an explicit scope expansion requiring user/upstream authority and a separate architecture decision.

## RGR-v3

Every finding-bearing wave updates one canonical record:

```yaml
review_governor_record:
  record_version: RGR-v3
  resolve_run_id:
  artifact_state:
    branch:
    base_sha:
    head_sha:
    review_backend:
    target_fingerprint:
  review_charter:
  findings: []
  finding_liabilities: []
  finding_identity:
  review_cluster_compilation:
  normal_form_register: []
  owner_pressure:
  production_net_gate:
  governor_fuse:
  negative_route_gate:
  proof_matrix_gate:
  review_distillation_receipt: null
  selected_route:
    route:
    owner:
    normal_form_id:
    why_this_route:
    why_not_lower_surface:
    forbidden_actions: []
    permitted_scope: []
  mutation_permit:
    required: yes | no
    emitted: yes | no
  outcome:
    actual_production_insertions:
    actual_production_deletions:
    actual_production_net:
    actual_test_insertions:
    actual_test_deletions:
    actual_test_net:
    family_recurred_after: yes | no | unknown
  gate:
    liability_gate: pass | fail
    normal_form_gate: pass | fail | not-required
    owner_pressure_gate: pass | fail
    production_net_gate: pass | fail
    fuse_gate: pass | fail
    negative_route_gate: pass | fail
    proof_matrix_gate: pass | fail
    distillation_gate: pass | fail | not-required
    implementation_handoff_allowed: yes | no
```

Prose may explain the record. Prose is not the record.

## Mutation permit

After recurrence or whenever mutation pressure is material, emit immediately before mutation:

```yaml
RGR-V3-MUTATION-PERMIT:
  permit_version: RGR-MP-v2
  permit_id: "RGR-MP-..."
  artifact_state:
    branch:
    base_sha:
    head_sha:
    review_backend:
    target_fingerprint:
  charter_id:
  finding_id:
  cluster_id:
  counterexample_family:
  finding_liability:
    relation:
    mutation_allowed:
    disposition:
  normal_form:
    normal_form_id:
    status:
    prior_normal_form_falsified: yes | no
  governor_fuse:
    fuse_state: open | tripped
    delivery_mutation_frozen: yes | no
    trip_reasons: []
  selected_route:
    route:
    leverage_level:
  owner_pressure:
    pressure_exceeded: yes | no
    owner_too_coarse: yes | no
    clearance_authority:
  production_net_gate:
    expected_production_net:
    change_kind:
    invalid_state_unrepresentable_by_construction: yes | no
    positive_net_warrant:
    deletion_or_collapse_offset: []
    allowed: yes | no
  negative_route_gate:
    gate_version:
    ledger_available:
    active_exclusion_match:
    prior_normal_form_falsified:
    capture_required:
    capture_created:
    captured_neg_id:
    route_changed_at_leverage_level:
    handoff_allowed:
  proof_matrix_gate:
    family_matrix_present:
    one_test_per_wound:
    allowed:
  distillation:
    required: yes | no
    receipt_version: "none | RDR-v1"
    gate: pass | fail | not-required
  forbidden_actions: []
  permitted_scope: []
  surface_budget:
    max_positive_production_net:
    max_new_helpers:
    max_new_branches:
    max_new_public_symbols:
    max_new_files:
  stale_if: []
  handoff_allowed: yes | no
```

Hard failures:

- branch liability does not permit mutation;
- normal form is falsified and selected route is another ordinary normal form;
- fuse is tripped but distillation/deletion/boundary redesign has not passed;
- owner pressure exceeded but route continues the same owner;
- change kind is predicate/helper/test accretion after fuse trip;
- expected positive net lacks valid representation/distillation warrant and retirement offset;
- negative evidence excludes route;
- prior normal form was falsified but no capture was created;
- route did not change at leverage level after falsification;
- one-test-per-wound without family matrix;
- missing or stale charter/tuple.

## Implementation handoff

Never hand raw findings to an implementer.

```yaml
implementation_handoff:
  permit_id:
  selected_route:
  leverage_level:
  owner:
  normal_form_id:
  permitted_scope: []
  forbidden_actions: []
  surface_budget:
  deletion_or_collapse_offset: []
  proof_matrix:
  fuse_state:
  distillation_receipt:
  stale_if: []
```

`$fixed-point-driver` and `$accretive-implementer` must stop and return when:

- budget is exhausted;
- a new same-family finding appears;
- implementation needs a route not named in the permit;
- the owner must expand beyond the permit;
- actual change kind differs from the permitted change kind.

## Commit and review cadence

- Commit coherent green slices for recoverability.
- Do not interpret smaller commits as proof of lower accumulation.
- Update cumulative owner pressure after every patch group and commit.
- A commit does not reset cluster/family counters, owner pressure, or the fuse.
- A push invalidates current-head proof.
- Do not keep pushing ordinary local fixes after fuse trip.

## PR sweep

Perform a complete current-head PR thread/comment sweep.

Each item gets:

- evidence;
- liability;
- disposition.

Out-of-charter adjacent findings are captured, not silently absorbed.

Any branch-liable mutation resets current-head review proof.

## Closure

A resolve run is complete only when:

```text
review charter is frozen and current
all branch-liable findings are discharged
all normal forms are closed/falsified/superseded with no active ambiguity
no mutation occurred after fuse trip without passing distillation/deletion/boundary permit
2 charter-clean current-head reviews exist
1 final broad holdout is closure-clean
full validation passes on current head
branch is committed and pushed
PR sweep is complete
worktree is clean
```

## Reporting

Every final report emits:

```yaml
resolve_learning_report:
  report_version: RLR-v4
  review_horizon:
    initial_broad_reviews:
    charter_freezes:
    targeted_reviews:
    charter_clean_reviews:
    final_holdout_reviews:
    new_findings_after_charter_freeze:
    new_findings_added_to_branch_scope:
  finding_liability:
    introduced_by_current_diff:
    acceptance_required:
    preexisting_blocker:
    adjacent_preexisting:
    reviewer_preference:
    unknown:
    captured_followup:
  normal_form_accounting:
    proposed:
    active:
    closed:
    falsified:
    superseded:
    repeated_after_falsification:
  growth_fuse:
    required:
    tripped:
    trip_reasons: []
    mutations_after_trip:
    production_net_after_trip:
  owner_pressure:
    peak_owner_mutations:
    peak_same_owner_commits:
    peak_apply_patch_calls:
    peak_positive_production_net:
    owners_over_budget: []
  production_surface:
    insertions:
    deletions:
    net:
    validation_branches_added:
    evidence_predicates_added:
    helpers_added:
    public_symbols_added:
    compatibility_paths_added:
    surfaces_retired_or_collapsed:
  tests:
    insertions:
    deletions:
    net:
    one_test_per_wound_blocked:
    tests_retired_or_merged:
  negative_ledger:
    maps_or_gates:
    captures:
    active_exclusions:
    route_families_excluded:
    permits_with_leverage_change:
  distillation:
    required:
    receipts_emitted:
    rederived_delivery_patches:
  compliance:
    permits_required:
    permits_emitted:
    mutations_without_permit:
    mutations_after_fuse_without_distillation:
  outcome:
    resolved:
    blocked:
    open_blocker:
```

The decisive metrics are:

```text
same-family findings after normal form
production net after fuse trip
mutations after fuse trip
adjacent valid findings absorbed into branch scope
route changes caused by negative evidence
```

Do not claim improvement merely because permits, commits, or reviews were numerous.

## Companion skills

- `$review-adjudication`: evidence and branch liability.
- `$review-compression-compiler`: cluster/family compression and distillation input.
- `$negative-ledger`: durable route/falsified-normal-form memory.
- `$cybernetic`: system/feedback classification when recurrence implies structure.
- `$universalist`: boundary redesign when the representation/shape of truth is wrong.
- `$reduce`: deletion/collapse/canonicalization when surface is the failure.
- `$fixed-point-driver`: implement only permitted normal-form/subtractive route.
- `$accretive-implementer`: narrow implementation under hard budget.
- `$verification-closure`: final current-head charter/holdout/PR closure.

## Preferred subagents

Use sparingly:

```text
review_liability_auditor
resolve_fuse_auditor
```

They are read-only. Root owns decisions and mutation.

## Non-negotiables

- Valid does not mean branch-liable.
- One ordinary normal form per counterexample family.
- Same-family recurrence falsifies the normal form.
- Falsification trips the fuse.
- A tripped fuse freezes delivery mutation.
- Runtime guards are predicate accretion, not representation elimination.
- Owner coarseness is measured cumulatively.
- Commits do not reset accumulation counters.
- Negative-ledger consultation without capture/route change after falsification is insufficient.
- A final broad review is a holdout, not an invitation to absorb the repository.
- No resolved claim without RLR-v4.

## Resources

- [finding-liability-gate.md](references/finding-liability-gate.md)
- [normal-form-register.md](references/normal-form-register.md)
- [governor-fuse.md](references/governor-fuse.md)
- [owner-pressure-gate.md](references/owner-pressure-gate.md)
- [production-net-gate.md](references/production-net-gate.md)
- [review-charter.md](references/review-charter.md)
- [review-distillation-mode.md](references/review-distillation-mode.md)
- [negative-ledger-ratchet.md](references/negative-ledger-ratchet.md)
- [reporting-contract.md](references/reporting-contract.md)
- [governor-tooling.md](references/governor-tooling.md)
