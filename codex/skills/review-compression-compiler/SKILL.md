---
name: review-compression-compiler
description: "Compile review findings, PR comments, validation failures, and repeated CAS findings into a clustered counterexample corpus, candidate normal forms, abstraction-rent audit, proof matrix, and minimum-surface implementation handoff. Use for `$review-compression-compiler`, review compression, hot review clusters, repeated same-cluster findings, adjacent CAS findings after a fix, review-driven code growth, add-new-surface pressure, resolving reviews without code accumulation, or `$resolve` cluster normalization. Read-only: do not edit code."
metadata:
  version: "1.0.0"
  activation_cost: high
  default_depth: strict
---

# Review Compression Compiler

## Mission

Review findings are **counterexamples**, not tasks.

This skill compiles a stream of review findings, PR comments, validation failures, and repeated CAS findings into the smallest proof-carrying normal form that kills the counterexample family without unbounded code accumulation.

```text
review findings -> counterexample corpus -> cluster owner map -> candidate normal forms -> selected normal form -> proof matrix -> implementation handoff
```

Do not edit code. Do not stage, commit, push, or resolve PR threads. The output is a packet consumed by `$resolve`, `$fixed-point-driver`, and eventually `$accretive-implementer`.

## Core principle

```text
Review resolution is a compression problem, not a fix queue.
```

The unit of work is the **defect family**, not the individual comment.

A review item may justify:

- no production change;
- validation-only proof;
- deletion/collapse/canonicalization;
- refactor at the existing owner;
- mutation at the existing owner;
- new surface only when it pays abstraction rent.

## Activation boundary

Use this skill when any are true:

- two findings appear in the same subsystem, owner, protocol, state machine, proof surface, or invariant family;
- CAS finds an adjacent issue after a previous fix;
- a review item would add helper/wrapper/adapter/fallback/flag/branch/state variant/public symbol/compatibility path;
- all decision-bearing review items are selecting `address`;
- production or test surface is growing without deletion/collapse evidence;
- the same cluster reappears after a selected normal form;
- `$resolve` needs a machine-auditable route packet before mutation;
- `$fixed-point-driver` needs a compressed cluster packet instead of a queue of review comments.

Do not use when:

- one isolated bug has one obvious existing owner and one direct proof;
- the task is final closure proof only;
- the user asks only for explanation;
- implementation is already selected and only needs execution;
- no review, PR, validation, or counterexample corpus exists.

## Workflow position

Normal chain:

```text
$resolve
  -> $review-adjudication
  -> $review-compression-compiler
  -> $fixed-point-driver
  -> $accretive-implementer
  -> validation / review closure
```

`$resolve` owns branch state. This skill owns counterexample compression. `$fixed-point-driver` owns normal-form remediation routing. `$accretive-implementer` owns single-writer execution after route selection.

## Inputs

Require as much of this as available:

```yaml
review_compression_input:
  artifact_state_id: "branch/head/base/diff/phase"
  source_skill: resolve | fixed-point-driver | review-adjudication | other
  current_objective: "..."
  cluster_trigger:
    reason: second_same_cluster_finding | adjacent_review_after_fix | surface_growth | add_surface_request | repeated_address_route | same_cluster_reappeared | explicit_user_request
    review_item_ids: []
  review_items:
    - id:
      source: cas | native-review | pr-comment | validation | human
      text:
      file:
      line_range:
      evidence_ref:
      adjudication_route:
      permitted_action:
  current_patch_sites: []
  known_owner_candidates: []
  validation_commands: []
  forbidden_actions: []
  surface_budget_hint: {}
```

If artifact state is unknown or stale, return a blocked packet.

## Compiler pipeline

### 1. Lift counterexamples

Turn every review item into a `review_counterexample` row.

```yaml
review_counterexample:
  id:
  source:
  observed_bad_state_or_gap:
  expected_contract:
  producer_candidate:
  transition_candidate:
  validator_candidate:
  consumer_or_proof_surface:
  owner_candidate:
  related_prior_findings: []
  evidence_ref:
  confidence: high | medium | low
```

### 2. Build cluster owner map

Group by subsystem, owner, protocol, state machine, parser/validator, lifecycle, retry/idempotency path, cache/index, impossible-state family, truth owner, or proof surface.

```yaml
cluster_owner_map:
  producers: []
  transitions: []
  validators: []
  consumers: []
  proof_surfaces: []
  duplicate_or_shadow_surfaces: []
  local_patches_already_attempted: []
```

### 3. Generate candidate normal forms

Generate at least these candidate classes unless clearly not applicable:

```text
no-change-proof
validate-only
delete-collapse-canonicalize
refactor-existing-owner
mutate-existing-owner
add-new-surface
blocked
```

### 4. Score by compression, not patch size

Select the normal form that minimizes code model size while satisfying the contract.

Prefer lower-cost routes:

```text
no-change-proof
-> validate-only
-> delete-collapse-canonicalize
-> refactor-existing-owner
-> mutate-existing-owner
-> add-new-surface
-> blocked when safe route cannot be proven
```

Use this objective:

```text
minimize:
  production_surface
+ duplicate_owner_penalty
+ abstraction_variance
+ future_review_risk
+ proof_complexity
+ public_surface_penalty
+ fallback_tolerance_penalty

subject to:
  all selected counterexamples killed or explicitly routed
  existing behavior preserved
  owner named
  proof executable
  forbidden actions respected
```

### 5. Charge abstraction rent

Any new helper, wrapper, adapter, fallback, flag, branch, state variant, public symbol, compatibility path, parser tolerance, catch-and-continue path, or new abstraction must pay rent.

Rent is paid only when the new surface:

- retires existing surface;
- prevents named future patches;
- makes an illegal state uninhabitable at the owner;
- localizes an unavoidable external obligation;
- or is explicitly accepted as expansion by the user/upstream authority.

Unpaid rent blocks `add-new-surface`.

### 6. Minimize proof matrix

Do not create one test per wound by default. Prefer a proof matrix that covers the counterexample family.

The proof matrix should map:

```text
selected normal form -> counterexamples killed -> proof commands/tests -> omitted duplicate tests
```

### 7. Emit implementation handoff

The selected normal form must produce a handoff for `$fixed-point-driver`, not direct edits.

## Specialist workers

Use read-only custom agents when useful and available:

```text
review_counterexample_lifter
review_cluster_cartographer
normal_form_scout
abstraction_rent_auditor
proof_matrix_minimizer
shadow_branch_evidence_scout
```

Every worker is read-only and advisory. Root/compiler owns synthesis.

Reject stale, wrong-scope, wrapper-leaking, no-evidence, or acknowledgement-only packets.

## Output packet

Emit exactly one packet.

```yaml
review_compression_packet:
  packet_version: RCP-v1
  packet_status: accepted | blocked | not-required
  artifact_state_id: "..."
  cluster_id: "..."
  cluster_trigger:
    reason: second_same_cluster_finding | adjacent_review_after_fix | surface_growth | add_surface_request | repeated_address_route | same_cluster_reappeared | explicit_user_request | not-required
    review_item_ids: []
  counterexamples:
    - id:
      source: cas | native-review | pr-comment | validation | human
      observed_bad_state_or_gap:
      expected_contract:
      producer_candidate:
      transition_candidate:
      validator_candidate:
      consumer_or_proof_surface:
      owner_candidate:
      related_prior_findings: []
      evidence_ref:
      confidence: high | medium | low
  cluster_owner_map:
    producers: []
    transitions: []
    validators: []
    consumers: []
    proof_surfaces: []
    duplicate_or_shadow_surfaces: []
    local_patches_already_attempted: []
  candidate_normal_forms:
    - id:
      kind: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
      owner:
      counterexamples_killed: []
      production_surface_delta: negative | zero | bounded-positive | expansion | unknown
      surfaces_retired: []
      surfaces_added: []
      abstraction_rent_required: yes | no
      proof_required: []
      risks: []
      rejected_because:
  selected_normal_form:
    id:
    kind: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
    owner:
    why_this_is_minimum:
    why_no_smaller_form_suffices:
    why_no_lower_abstraction_route_works:
    counterexamples_killed: []
    surfaces_retired: []
    surfaces_added: []
    abstraction_rent:
      required: yes | no
      rent_status: paid | unpaid | not-applicable
      reason:
    proof_required: []
  proof_matrix:
    - proof_id:
      counterexamples_covered: []
      command_or_test:
      existing_or_new: existing | new | modified | manual
      fixture_risk: low | medium | high | unknown
      duplicate_test_risk: low | medium | high | unknown
  implementation_handoff:
    target_skill: fixed-point-driver
    permitted_scope: []
    forbidden_actions: []
    surface_budget:
      production_surface: zero_or_negative | bounded_positive | explicit_expansion
      added_helpers_allowed: yes | no
      added_wrappers_adapters_allowed: yes | no
      added_flags_or_fallbacks_allowed: yes | no
      public_symbols_allowed: yes | no
      compatibility_paths_allowed: yes | no
    stale_if: []
  closure_rule:
    if_same_cluster_finding_reappears: reopen_compiler | block | escalate
  packet_status_reason:
```

## Packet validity

- `accepted` requires a selected normal form, proof requirement, owner, and implementation handoff.
- `add-new-surface` requires abstraction rent with `rent_status: paid` or explicit user/upstream expansion.
- `blocked` must name the missing evidence, stale state, or unsafe route.
- `not-required` is allowed only when the item is isolated, existing-owner, no new surface, no cluster, and no repeated evidence.
- Do not emit an implementation patch.
- Do not treat green tests as proof unless they cover the selected counterexamples.

## Shadow resolution mode

Optional and high-cost.

Use only when:

- same cluster repeatedly reappears after fixes;
- exploratory fixes are useful but should not become committed architecture;
- review churn is likely to produce scar tissue.

In shadow mode:

```text
1. root creates disposable branch/worktree;
2. exploratory fixes may happen there under another workflow;
3. findings and diffs are harvested as evidence;
4. compiler emits final normal form;
5. main branch receives only the compressed patch.
```

This skill does not mutate the shadow branch. It may consume shadow diffs via `shadow_branch_evidence_scout`.

## Hard rules

- Do not edit files.
- Do not produce patch hunks.
- Do not treat review comments as tasks.
- Do not select `add-new-surface` with unpaid abstraction rent.
- Do not create one test per wound when a proof matrix can cover the family.
- Do not let an implementation handoff omit forbidden actions or surface budget.
- Do not close a hot cluster with prose-only reasoning.
- Do not override `$resolve` branch state or `$fixed-point-driver` implementation authority.

## Resources

- [packet-contract.md](references/packet-contract.md)
- [counterexample-corpus.md](references/counterexample-corpus.md)
- [normal-form-selection.md](references/normal-form-selection.md)
- [abstraction-rent.md](references/abstraction-rent.md)
- [proof-matrix.md](references/proof-matrix.md)
- [shadow-resolution-mode.md](references/shadow-resolution-mode.md)
- [resolve-integration.md](references/resolve-integration.md)
