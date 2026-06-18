---
name: resolve
description: "Resolve the current branch through a cleanroom Review Compiler: review feedback mutates only a disposable review lab, counterexample contract, proof matrix, and delivery patch recipe; the delivery branch is frozen until a minimal rederived patch and ablation certificate exist. Use for `$resolve`, branch review/fix/validate/commit/push/PR-sweep closure, review lab, counterexample_contract / CEC-v1, delivery_patch_recipe / DPR-v1, ablation_certificate / ABL-CERT-v1, frozen delivery base, branch liability, review charter, CAS closure, PR sweep, and non-accumulating review resolution. Not for one-shot review, PR creation, merge/land, or isolated implementation."
metadata:
  version: "4.0.0"
  activation_cost: high
  default_depth: full
---

# Resolve

## Mission

`$resolve` is now a **cleanroom Review Compiler**.

```text
Accrete knowledge, not code.
Review lab learns. Delivery branch is recompiled.
```

Review feedback must not directly mutate the delivery branch after the first finding-bearing review wave.

Review feedback may accumulate only in:

```text
review lab ledger
counterexample contract
proof matrix
delivery patch recipe
ablation certificate
```

The delivery branch receives a final minimal patch rederived from a frozen base. It must not inherit the review lab's wound-by-wound repair history.

## Why this exists

The prior Review Governor made review resolution more disciplined but still allowed many locally plausible permits to produce large aggregate growth. A recent 12-hour report found five true `$resolve` sessions with **132 `apply_patch` calls**, **24 commits**, and a supplemental repo delta of **+1,439 / -146**, net **+1,293** lines, overwhelmingly in `src/world.zig`. The report’s core diagnosis was that `$resolve` noticed recurrence and then repeatedly converted recurrence into permission to add more code. 

The correction is architectural:

```text
review feedback writes to the lab
the compiler writes to delivery
```

A gate asks, “May I do this patch?”

A compiler asks, “What is the smallest program that satisfies the accumulated constraints?”

## Core law

```text
After the first finding-bearing review wave, the delivery branch is read-only until $resolve emits:
  1. counterexample_contract / CEC-v1
  2. delivery_patch_recipe / DPR-v1
  3. ablation_certificate / ABL-CERT-v1
  4. current proof for the rederived delivery patch
```

If the first review wave is completely clean, no lab is required.

If the first finding-bearing wave contains exactly one trivial branch-liable finding and no recurrence risk, `$resolve` may use Fast Path. Any second finding, same-family recurrence, positive production pressure, or PR-thread reopening exits Fast Path and freezes delivery.

## Activation boundary

Use `$resolve` when the user wants the current branch driven through:

```text
review -> branch-liability classification -> lab learning -> compiled patch -> proof -> review closure -> push -> PR sweep
```

Do not use `$resolve` for:

- one-shot review;
- PR creation only: use `$ship`;
- merge/land: use `$land`;
- selected implementation task only: use `$fixed-point-driver` / `$accretive-implementer`;
- claim adjudication only: use `$review-adjudication`;
- final proof only: use `$verification-closure`.

## Cleanroom topology

```text
delivery branch:
  frozen, read-only after first finding-bearing review wave
  receives only compiled minimal patch

review lab:
  disposable branch/worktree/scratch record
  may explore, patch, test, falsify, and discard

counterexample compiler:
  converts raw findings into branch-liable counterexample families

delivery compiler:
  emits minimal delivery patch recipe from frozen base

ablation pass:
  tries to delete every new helper, branch, fallback, test wound, and predicate

holdout review:
  verifies final patch without expanding scope
```

## Fast Path

Fast Path is allowed only when all are true:

```yaml
fast_path:
  first_review_findings: 0 | 1
  branch_liability: introduced_by_current_diff | exposed_and_required_by_current_acceptance
  same_cluster_recurrence: no
  same_family_recurrence: no
  expected_production_net: zero | negative | bounded_trivial_positive
  public_surface_change: no
  fallback_or_compat_path: no
  new_helper_or_wrapper: no
  proof_is_existing_or_single_existing_test_extension: yes
```

Fast Path still requires evidence discipline and current proof.

Fast Path is revoked immediately by:

- second finding-bearing review wave;
- PR sweep finding a live defect;
- same-cluster recurrence;
- any new helper/wrapper/adapter;
- positive production net that is not trivial;
- test wound catalog growth;
- branch-liability ambiguity.

When revoked, freeze delivery and enter cleanroom mode.

## Delivery freeze

After the first finding-bearing review wave outside Fast Path:

```yaml
delivery_freeze:
  freeze_version: DF-v1
  freeze_id: "DF-..."
  branch:
  frozen_base_sha:
  frozen_head_sha:
  review_backend:
  target_fingerprint:
  charter_id:
  frozen_at:
  delivery_mutation_allowed: no
```

Rules:

- No `apply_patch`, file edit, commit, or production-affecting mutation may happen on the delivery branch after freeze.
- Lab mutation may occur only in an explicitly marked lab context.
- If no separate worktree/branch can be created, use transcript-local scratch state and defer code edits until delivery recipe is ready.
- A checkpoint commit after freeze is not a delivery patch unless produced from a compiled recipe.

## Review charter

A broad review can discover. It must not expand forever.

```yaml
review_charter:
  charter_version: RC-v2
  charter_id:
  objective:
  frozen_delivery_base:
  in_scope_counterexample_families: []
  in_scope_owners: []
  explicit_non_goals: []
  proof_bar: []
  frozen: yes | no
```

After the charter is frozen:

- new valid adjacent findings are classified for liability;
- out-of-scope findings become follow-ups;
- only branch-liable findings can enter the delivery recipe;
- adding a new family to the charter is a scope change and resets charter-bound proof.

## Finding liability

A finding can be true and still not belong in this branch.

```yaml
finding_liability:
  relation:
    introduced_by_current_diff |
    exposed_and_required_by_current_acceptance |
    preexisting_but_blocks_current_invariant |
    adjacent_preexisting |
    reviewer_preference |
    unknown
  mutation_allowed: yes | no
  disposition:
    include_in_contract |
    validate_only |
    capture_followup |
    resolve_thread_only |
    reject |
    blocked
  evidence_refs: []
  reason:
```

Only these normally enter the contract:

```text
introduced_by_current_diff
exposed_and_required_by_current_acceptance
preexisting_but_blocks_current_invariant
```

`adjacent_preexisting`, `reviewer_preference`, and `unknown` do not authorize delivery mutation.

## Counterexample Contract

The counterexample contract is the source of truth for what delivery must satisfy.

```yaml
counterexample_contract:
  contract_version: CEC-v1
  contract_id: "CEC-..."
  frozen_delivery_base:
  charter_id:
  branch_liabilities:
    - finding_id:
      relation:
      counterexample_family:
      observed_fact:
      required_behavior:
      proof_obligation:
      evidence_refs: []
  non_branch_liabilities:
    - finding_id:
      relation:
      disposition:
      followup_ref:
      reason:
  counterexample_families:
    - family_id:
      findings: []
      canonical_owner_candidate:
      failure_surface:
      acceptance_dependency:
      required_behavior:
      proof_obligations: []
  proof_matrix:
    - proof_id:
      family_id:
      existing_or_new: existing | extended | new
      command_or_test:
      wound_specific: yes | no
  followups_captured: []
  gate:
    all_findings_classified: pass | fail
    non_branch_liabilities_not_in_recipe: pass | fail
    proof_obligations_present: pass | fail
```

No delivery recipe without CEC-v1.

## Review Lab Ledger

The lab is for learning, not shipping.

```yaml
review_lab_ledger:
  ledger_version: RLL-v1
  lab_id: "RLL-..."
  frozen_delivery_base:
  lab_context:
    kind: branch | worktree | scratch-record
    ref:
  findings_explored: []
  routes_tried:
    - route_id:
      route_family:
      counterexample_family:
      implementation_shape:
      result: falsified | useful | discarded | superseded
      evidence_refs: []
  routes_falsified: []
  temporary_tests: []
  temporary_code: []
  discarded_from_delivery: yes
```

Rules:

- Lab commits are exploratory.
- Do not cherry-pick lab commits by default.
- Lab work must be compiled into counterexamples, proof obligations, and a delivery recipe.
- The lab may grow. Delivery must not.

## Route-falsification rule

A normal form is now a lab hypothesis or compile product, not a local patch label.

```yaml
normal_form_hypothesis:
  normal_form_id:
  counterexample_family:
  selected_boundary:
  closure_prediction:
  route_family:
  status: proposed | useful | falsified | superseded | compiled
  falsified_by: []
  negative_evidence_id:
```

If a same-family finding appears after a lab route or prior delivery route:

- mark the route family falsified;
- capture negative evidence when ledger CLI is available;
- exclude that route family from the delivery recipe unless reopened/stale/superseded;
- require the next candidate to differ at leverage level.

## Negative-ledger integration

Use `.ledger/negative-ledger.jsonl` through `ledger`.

Preferred hardened command:

```bash
ledger gate \
  --root . \
  --cluster "$CLUSTER" \
  --route "$ROUTE" \
  --route-family "$ROUTE_FAMILY" \
  --counterexample-family "$FAMILY" \
  --failure-surface "$SURFACE" \
  --owner "$OWNER" \
  --artifact "$HEAD_SHA" \
  --same-cluster-count "$N" \
  --require-capture-on-recurrence \
  --format yaml
```

Compatibility fallback:

```bash
ledger map --route "$ROUTE" --cluster "$CLUSTER" --artifact "$HEAD_SHA"
ledger show --id NEG-...
ledger capture --json <capture-file>
```

Delivery recipe cannot select a falsified route family unless it is explicitly reopened, stale, superseded, or accepted with user authority.

## Delivery Patch Recipe

A delivery patch recipe is the only authority for delivery mutation.

```yaml
delivery_patch_recipe:
  recipe_version: DPR-v1
  recipe_id: "DPR-..."
  frozen_base:
  counterexample_contract_id:
  selected_boundary:
    owner:
    representation_or_rule:
    why_this_boundary:
    why_not_lower_surface:
  selected_route:
    route:
      delete-collapse-canonicalize |
      compiled-normal-form |
      boundary-redesign |
      validate-only |
      blocked
    leverage_level:
      parameter | predicate | representation | boundary | protocol | information-flow | rule | goal
  branch_liabilities_included: []
  branch_liabilities_excluded: []
  falsified_routes_excluded: []
  surfaces_to_retire:
    - surface:
      action: delete | collapse | canonicalize | privatize | decommission
      proof_obligation:
  permitted_new_surface:
    - surface:
      reason:
      cannot_be_replaced_by_retirement:
      proof_obligation:
  forbidden_lab_artifacts: []
  expected_surface_delta:
    production_net: negative | zero | bounded_positive | unknown
    test_net: negative | zero | bounded_positive | unknown
    helpers_added:
    branches_added:
    public_symbols_added:
    fallback_or_compat_paths_added:
  proof_matrix: []
  gate:
    derived_from_contract: pass | fail
    lower_surface_routes_considered: pass | fail
    falsified_routes_excluded: pass | fail
    delivery_mutation_allowed: yes | no
```

Rules:

- No delivery mutation without DPR-v1.
- Recipe must be derived from frozen base, not from lab patch history.
- Recipe may include positive production net only when it names why surface retirement cannot satisfy the contract.
- A recipe is invalid if it includes non-branch-liable findings.
- A recipe is invalid if it preserves lab scaffolding without naming it as required new surface.

## Delivery rederivation

After DPR-v1 passes:

```yaml
delivery_rederivation:
  rederivation_version: REDERIVE-v1
  frozen_base:
  recipe_id:
  delivery_branch:
  lab_commits_cherry_picked: no
  changes_applied_from_recipe: []
  lab_artifacts_excluded: []
  status: pending | complete | blocked
```

Hard rule:

```text
Do not cherry-pick lab commits by default.
```

If cherry-pick is explicitly used, the final patch must still be ablated and certified as recipe-equivalent.

## Ablation Certificate

Before final review closure, prove the delivery recipe is not carrying unnecessary surface.

```yaml
ablation_certificate:
  certificate_version: ABL-CERT-v1
  recipe_id:
  delivery_head:
  ablation_attempts:
    - target:
      kind: helper | branch | predicate | fallback | compatibility_path | test | wrapper | public_symbol | file | state_variant
      action: delete | collapse | merge | privatize | table-drive | remove
      result: removed | survived | blocked
      proof:
      reason_if_survived:
  removed_from_recipe: []
  survived_ablation:
    - surface:
      why_needed:
      proof_ref:
  tests_merged_or_retired: []
  production_surface:
    insertions:
    deletions:
    net:
  test_surface:
    insertions:
    deletions:
    net:
  gate:
    every_new_surface_challenged: pass | fail
    wound_tests_compacted: pass | fail | not-required
    production_net_justified: pass | fail
    final_delivery_patch_allowed: yes | no
```

Rules:

- Try to delete every added helper.
- Try to remove every added branch.
- Try to merge wound-specific tests into a family matrix.
- Try to remove fallback and compatibility paths.
- Try to replace predicate accretion with representation/boundary constraints.
- If proof still passes without a surface, that surface was not needed.
- No closure without ABL-CERT-v1.

## Cleanroom permit

Delivery mutation uses one permit, not one permit per review wound.

```yaml
RGR-V4-COMPILED-DELIVERY-PERMIT:
  permit_version: RGR-CDP-v1
  permit_id:
  frozen_delivery_base:
  counterexample_contract_id:
  delivery_patch_recipe_id:
  ablation_certificate_required: yes
  branch_liabilities_included: []
  non_branch_liabilities_excluded: []
  falsified_routes_excluded: []
  selected_route:
  permitted_scope: []
  forbidden_actions: []
  expected_surface_delta:
  proof_matrix:
  stale_if: []
  handoff_allowed: yes | no
```

This permit authorizes applying the compiled recipe to delivery.

It does not authorize ad hoc review-derived mutation.

## Review horizon

Closure review is not a work queue.

```text
initial broad sensing review
-> delivery freeze if findings exist
-> lab learning / contract / recipe / ablation
-> targeted charter review on delivery patch
-> final broad holdout review
-> PR sweep
```

A final broad holdout finding is handled through the liability gate. It expands branch scope only if the current branch is liable.

## PR sweep

PR sweep is a sensor, not an automatic patch queue.

For every live PR item:

```yaml
pr_thread_disposition:
  thread_id:
  current: yes | no
  liability:
  disposition:
    covered_by_recipe |
    add_to_counterexample_contract |
    capture_followup |
    resolve_thread_only |
    blocked
```

If it adds to the counterexample contract, update the recipe. Do not patch delivery directly.

## Reporting

Every final report emits:

```yaml
resolve_compiler_report:
  report_version: RCR-v1
  delivery_freeze:
    required:
    emitted:
    frozen_base:
  review_lab:
    used:
    lab_patch_count:
    lab_commits:
    lab_surface_added:
    lab_surface_discarded:
  counterexample_contract:
    branch_liabilities:
    non_branch_liabilities:
    families:
    followups_captured:
  delivery_recipe:
    emitted:
    selected_route:
    falsified_routes_excluded:
    surfaces_to_retire:
    permitted_new_surface:
  rederivation:
    from_frozen_base:
    lab_commits_cherry_picked:
  ablation:
    certificate_emitted:
    surfaces_removed:
    surfaces_survived:
    tests_merged_or_retired:
  delivery_surface:
    production_insertions:
    production_deletions:
    production_net:
    test_insertions:
    test_deletions:
    test_net:
  review_horizon:
    targeted_reviews:
    final_holdout_reviews:
    holdout_findings_added_to_scope:
    holdout_followups_captured:
  compliance:
    delivery_mutations_before_recipe:
    review_derived_delivery_patches:
    recipe_missing:
    ablation_missing:
    non_branch_liability_mutated:
  outcome:
    resolved:
    blocked:
    open_blocker:
```

Key metrics:

```text
lab churn discarded / delivery surface shipped
delivery production net
delivery mutations before recipe
holdout findings added to scope
non-branch-liable findings mutated
```

## Companion roles

- `$review-adjudication`: liability classification and claim discipline.
- `$review-compression-compiler`: compiler front-end from findings to counterexample families.
- `$negative-ledger`: failed route-family memory.
- `$fixed-point-driver`: applies only compiled delivery permits.
- `$accretive-implementer`: narrow actuator under DPR/CDP, not raw review fixes.
- `$reduce`: ablation and surface retirement.
- `$universalist`: boundary/representation redesign when recipe requires it.
- `$cybernetic`: system classification when review loop is complex or incentives are wrong.
- `$verification-closure`: final proof of delivery patch, charter review, holdout, PR sweep.

## Subagents

Preferred read-only workers:

```text
review_lab_cartographer
counterexample_contract_auditor
delivery_recipe_auditor
ablation_certificate_auditor
```

Root owns mutation.

## Hard rules

- Accrete knowledge, not code.
- Review feedback cannot directly mutate delivery after first finding-bearing wave.
- Lab may grow; delivery must be recompiled.
- No delivery mutation without CEC-v1 + DPR-v1.
- No closure without ABL-CERT-v1.
- No lab commit cherry-pick by default.
- No non-branch-liable finding in delivery recipe.
- No final broad holdout as unbounded work queue.
- No normal-form label without derivation from counterexample contract.
- No positive delivery surface without ablation challenge.
- No resolved claim without RCR-v1 report.

## Resources

- [cleanroom-review-compiler.md](references/cleanroom-review-compiler.md)
- [delivery-freeze.md](references/delivery-freeze.md)
- [counterexample-contract.md](references/counterexample-contract.md)
- [review-lab-ledger.md](references/review-lab-ledger.md)
- [delivery-patch-recipe.md](references/delivery-patch-recipe.md)
- [ablation-certificate.md](references/ablation-certificate.md)
- [compiled-delivery-permit.md](references/compiled-delivery-permit.md)
- [review-horizon.md](references/review-horizon.md)
- [reporting-contract.md](references/reporting-contract.md)
- [compiler-tooling.md](references/compiler-tooling.md)
