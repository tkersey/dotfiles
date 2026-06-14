---
name: review-compression-compiler
description: "Required packet compiler for review-driven mutation and review distillation. Converts review findings, PR comments, validation failures, repeated CAS findings, lab repair history, and falsified remediation routes into compact `review_compression_packet` / `review_distillation_packet` artifacts with selected normal form, explicit `$universalist` boundary check, `$negative-ledger` route exclusions, NREC-v1 negative route exclusion cards, abstraction rent, scar-tissue disposition, proof matrix, surface budget, route-wave publication, and fixed-point handoff. Use for `$review-compression-compiler`, review compression, review distillation, RCP-v1, RDP-v1, RRW-v1, NREC-v1, same-cluster findings, wrong shape of truth, missing boundary artifact, repeated review decisions, adjacent CAS findings after a fix, add-surface pressure, dirty-tree review accumulation, lab/delivery split, negative route memory, or resolving reviews without code growth. Read-only: do not edit code."
metadata:
  version: "6.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Review findings are **counterexamples**, not tasks.

This skill compiles review findings, PR comments, validation failures, repeated CAS findings, review-lab evidence, and falsified remediation decisions into the smallest proof-carrying normal form that kills the counterexample family without unbounded code accumulation.

It does **not** edit files.

## v6 focus

v5 added Review Distillation Mode and negative-evidence fields. v6 makes `$negative-ledger` decisive:

```text
A repeated review decision is a falsified hypothesis.
```

The compiler must now emit or consume **Negative Route Exclusion Cards** (`NREC-v1`) when a selected route is falsified, when same-cluster recurrence appears, or when an active negative route exclusion affects the next implementation handoff.

Core enforcement:

```text
No route-wave artifact -> no closure.
No required RCP/RDP -> no review-driven production patch.
No negative-route check after repeated-route pressure -> no handoff.
No selected route may violate an active negative exclusion unless reopened, stale, superseded, or explicitly accepted.
No universalist_check on a hot cluster -> no same-cluster production patch.
Same-cluster recurrence falsifies prior universalist not-needed and prior selected route.
Do not deliver the review loop.
No rent -> no new surface.
No proof matrix -> no implementation handoff.
```

## Workflow position

```text
$resolve
  -> $review-adjudication
  -> $review-compression-compiler
  -> $negative-ledger query/map/negative-route-memory
  -> optional $universalist / root-equivalent universal_boundary_packet
  -> optional Review Distillation Mode
  -> $fixed-point-driver
  -> $accretive-implementer
  -> negative-ledger capture/writeback decision
  -> validation / review closure
```

## Activation boundary

Use this skill when any are true:

- two findings appear in the same subsystem, owner, protocol, state machine, proof surface, or invariant family;
- CAS finds an adjacent issue after a previous fix;
- same cluster reappears after a prior packet or normal form;
- prior `universalist_check.decision: not-needed` was falsified;
- prior selected normal form, route, proof matrix, commit-boundary policy, or implementation shape was falsified;
- active negative evidence may exclude the route under consideration;
- existing-owner repair has already been attempted in the same cluster;
- dirty tree contains multiple review-driven repairs;
- exploratory repair work exists and should not be delivered by default;
- the next route would add helper/wrapper/adapter/fallback/flag/branch/state variant/public symbol/compatibility path;
- review findings suggest missing boundary artifact, duplicated projection, protocol/state-machine gap, generated provenance gap, public-contract/internal mismatch, effect/callback IR gap, or wrong shape of truth;
- production or test surface is growing without deletion/collapse evidence;
- `$resolve` needs a machine-auditable route packet before mutation.

Do not use when:

- one isolated bug has one obvious existing owner, no new surface, no boundary smell, no prior failed route, no active exclusion, and one direct proof;
- implementation is already selected and only needs execution;
- the task is final closure proof only;
- the user asks only for explanation.

## Review Distillation Mode

When a hot cluster or dirty repair loop appears, switch from in-place repair to distillation.

```text
Review Lab       = messy exploratory evidence branch/worktree
Delivery Branch  = clean rederived patch from frozen base
```

Core rule:

```text
The lab learns. The delivery branch forgets.
```

This skill does not create or mutate the lab. It emits the packet that governs the lab/delivery split.

## Packet-first rule

Every meaningful invocation must emit exactly one compact packet containing one of these literal keys:

```yaml
review_compression_packet:
review_distillation_packet:
```

Every falsified or active-exclusion route should also emit or reference at least one:

```yaml
negative_route_exclusion_card:
```

Prose may explain the packet. Prose is not the packet.

## Required Review Compression Packet

Use RCP for ordinary same-cluster review compression that still patches directly from the current delivery state.

```yaml
review_compression_packet:
  packet_version: RCP-v1
  packet_id: "RCP-<cluster-or-item-id>"
  packet_status: accepted | blocked | not-required
  artifact_state_id: "branch/head/base/diff/phase"
  cluster_id: "..."
  trigger:
    reason: second_same_cluster_finding | adjacent_review_after_fix | surface_growth | add_surface_request | repeated_address_route | same_cluster_reappeared | dirty_tree_review_accumulation | boundary_shape_suspected | negative_evidence_active | not-required
    review_item_ids: []
  counterexamples:
    - id: "CE-..."
      source: cas | native-review | pr-comment | validation | human
      bad_state_or_gap: "..."
      expected_contract: "..."
      owner_candidate: "..."
      evidence_ref: "..."
  negative_evidence:
    query_status: not-run | no-applicable-negative-evidence | active | stale | reopened | blocked
    active_exclusions:
      - neg_id: "..."
        excludes_route: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | universalist-not-needed | proof-matrix | commit-boundary | distill-from-lab
        exclusion_rule: "..."
        reopening_criteria: []
    negative_route_exclusion_cards:
      - card_id: "NREC-..."
        status: active | stale | superseded | reopened | unknown
        excluded_route: "..."
        active_against_selected_route: yes | no
    reopened_or_stale: []
    capture_required:
      - hypothesis: "..."
        attempted_change_or_decision: "..."
        observed_outcome: "..."
        failure_class: no-effect | local-regression | global-regression | unsound | too-complex | stale | unknown
    route_ratchet:
      prior_route_checked: yes | no
      active_exclusion_match: yes | no
      handoff_allowed: yes | no
      reason: "..."
  universalist_check:
    considered: yes | no
    trigger:
      same_cluster_findings: 0
      existing_owner_repair_attempted: yes | no
      prior_universalist_not_needed_falsified: yes | no
      missing_boundary_artifact: yes | no
      duplicated_projection: yes | no
      protocol_or_state_machine_missing: yes | no
      generated_provenance_gap: yes | no
      public_contract_drives_internals: yes | no
      effect_or_callback_ir_missing: yes | no
      repeated_existing_owner_repairs: yes | no
    decision: use-universalist | not-needed | blocked
    reason: "..."
    boundary_packet_ref: "none | path-or-inline-id"
  falsification:
    prior_packet_id: "none | RCP-... | RDP-..."
    falsified_hypothesis: "none | ..."
    same_cluster_reappeared_after_prior_decision: yes | no
    prior_decision_invalidated: yes | no
    negative_capture_candidate: yes | no
    negative_route_card_required: yes | no
    next_required_action: negative-ledger-map | universal-boundary-packet | reopen-compiler | distill | block | none
  selected_normal_form:
    kind: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | distill-from-lab | blocked
    owner: "..."
    why_minimum: "..."
    why_no_smaller_form_suffices: "..."
    counterexamples_killed: []
  abstraction_rent:
    required: yes | no
    rent_status: paid | unpaid | not-applicable
    surfaces_added: []
    surfaces_retired: []
    future_patches_prevented: []
  proof_matrix:
    - proof_id: "P-..."
      counterexamples_covered: []
      command_or_test: "..."
      existing_or_new: existing | new | modified | manual
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
  commit_boundary:
    policy: checkpoint_after_local_proof | final_only | none
    reason: "..."
  route_wave_ref:
    required: yes | no
    path_or_inline_id: "..."
  closure_rule:
    if_same_cluster_finding_reappears: reopen_compiler | negative-ledger-map | distill | block | escalate
```

## Required Review Distillation Packet

Use RDP when the review loop itself must not be delivered.

```yaml
review_distillation_packet:
  packet_version: RDP-v1
  packet_id: "RDP-<cluster-id>"
  packet_status: accepted | blocked
  artifact_state_id: "branch/head/base/diff/phase"
  cluster_id: "..."
  delivery_base:
    branch: "..."
    head_sha: "..."
    base_sha: "..."
    diff_digest: "..."
    proof_state: "..."
  review_lab:
    branch_or_worktree: "..."
    head_sha: "..."
    exploratory_commits: []
    lab_status: active | complete | unavailable | not-created
  counterexample_corpus:
    - id: "CE-..."
      bad_state_or_gap: "..."
      expected_contract: "..."
      owner_candidate: "..."
      lab_evidence_ref: "..."
  negative_evidence:
    query_status: not-run | no-applicable-negative-evidence | active | stale | reopened | blocked
    active_exclusions: []
    negative_route_exclusion_cards: []
    captured_failures: []
    durable_writeback:
      status: appended | duplicate-skip | not-attempted | unavailable
      ids: []
  scar_tissue_inventory:
    - lab_surface: "..."
      origin_counterexample: "..."
      fate: discard | distill | transplant-with-rent | blocked
      reason: "..."
      negative_evidence_ref: "none | NEG-... | NREC-..."
  universalist_check:
    considered: yes | no
    decision: use-universalist | not-needed | blocked
    boundary_packet_ref: "none | path-or-inline-id"
    reason: "..."
  selected_normal_form:
    kind: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
    owner: "..."
    why_clean_model: "..."
    why_lab_history_is_not_delivered: "..."
    counterexamples_killed: []
  abstraction_rent:
    required: yes | no
    rent_status: paid | unpaid | not-applicable
    surfaces_added: []
    surfaces_retired: []
    future_patches_prevented: []
  proof_matrix:
    - proof_id: "P-..."
      counterexamples_covered: []
      delivered_test_or_command: "..."
      lab_tests_discarded_or_merged: []
  delivery_patch_plan:
    allowed_files: []
    forbidden_files: []
    expected_surface_delta: negative | zero | bounded-positive | expansion | unknown
    must_not_cherry_pick_lab_commits: true
  dominance_check:
    lab_counterexamples_covered_by_delivery: yes | no | unknown
    delivery_surface_smaller_or_warranted: yes | no | unknown
    no_unpaid_lab_surface_transplanted: yes | no | unknown
  implementation_handoff:
    target_skill: fixed-point-driver
    permitted_scope: []
    forbidden_actions: []
    surface_budget: {}
    stale_if: []
  route_wave_ref:
    required: yes
    path_or_inline_id: "..."
  closure_rule:
    if_same_cluster_finding_reappears: reopen_distillation | negative-ledger-map | block | escalate
```

## Negative Route Exclusion Card

Use NREC when a route failure should constrain future remediation.

```yaml
negative_route_exclusion_card:
  card_version: NREC-v1
  neg_id: "NEG-..."
  card_id: "NREC-..."
  artifact_state_id: "..."
  cluster_id: "..."
  excluded_route: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | universalist-not-needed | proof-matrix | commit-boundary | distill-from-lab
  hypothesis: "..."
  attempted_change_or_decision: "..."
  falsifying_evidence:
    - kind: cas-review | validation | pr-comment | route-wave | rcp | rdp | commit | learning | lab | test | diff
      ref: "..."
      summary: "..."
  applicability:
    current_status: active | stale | superseded | reopened | unknown
    conditions: []
  exclusion_rule: "..."
  reopening_test: "..."
  next_allowed_routes:
    - delete-collapse-canonicalize
    - refactor-existing-owner
    - use-universalist
    - distill-from-lab
    - blocked
  confidence: high | medium | low | unknown
```

## Negative evidence rules

`negative_evidence.query_status` cannot be `not-run` when any are true:

- same cluster reappears after repair;
- prior selected normal form is falsified;
- prior universalist-not-needed is falsified;
- add-surface route failed or became unsound;
- public bypass, compatibility/tolerance path, or proof matrix choice caused a CAS counterexample;
- one-change candidate resembles a prior failed route;
- Review Distillation Mode is active.

Every falsified route creates a negative route exclusion card unless proven unrelated, stale, or superseded.

The next packet must either:

1. avoid the active excluded route;
2. prove negative evidence stale/superseded/reopened;
3. or block.

## Negative evidence compaction

If the same exclusion family appears three or more times, compact into a route-family exclusion:

```yaml
negative_compaction:
  compacted_card_id: "NREC-FAMILY-..."
  hypothesis_family: "..."
  excluded_route_family: "..."
  evidence_refs: []
  current_applicability: active | stale | superseded | reopened | unknown
  reopening_test: "..."
  safest_next_frontier: "..."
```

## Durable writeback policy

Do not write every local failure to `.learnings.jsonl`.

```yaml
negative_writeback_policy:
  in_wave_only:
    - one-off same-session route failure
    - low confidence
    - unclear applicability
  route_wave_artifact:
    - same-cluster recurrence
    - proof matrix gap
    - failed selected normal form
  durable_learnings:
    - repeated across sessions
    - generalizable to future branches
    - benchmark/regression/revert/public-bypass pattern
    - current proof anchors exist
```

Root owns durable writeback.

## Universalist-not-needed falsification

A prior `universalist_check.decision: not-needed` is falsified when the same cluster produces a new review/CAS/validation/PR counterexample after the repair or normal form was applied.

When falsified, the next packet cannot use `universalist_check.decision: not-needed` unless a full `$universalist` output or root-equivalent `universal_boundary_packet` explains why the boundary artifact is still unnecessary despite the recurrence.

## Route-wave publication

Every accepted or blocked RCP/RDP packet should be published into the current resolve route-wave artifact.

Suggested path:

```text
.step/proof/resolve/<resolve-run-id>/review-wave-<n>.route.yml
```

## Validation

When a packet is saved to a file, validate when possible:

```bash
python codex/skills/review-compression-compiler/tools/rcp_gate.py path/to/packet.yml
python codex/skills/review-compression-compiler/tools/rdp_gate.py path/to/distillation.yml
python codex/skills/review-compression-compiler/tools/nrec_gate.py path/to/nrec.yml
```

A failed gate means no mutation handoff.

## Specialist workers

Read-only workers may help:

- `review_counterexample_lifter`
- `review_cluster_cartographer`
- `normal_form_scout`
- `universal_boundary_scout`
- `abstraction_rent_auditor`
- `proof_matrix_minimizer`
- `negative_evidence_route_auditor`
- `negative_route_exclusion_card_auditor`
- `lab_scar_tissue_auditor`
- `review_compression_packet_auditor`
- `route_wave_artifact_auditor`
- `shadow_branch_evidence_scout`

Workers are advisory. The compiler/root owns synthesis and packet status.

## Hard rules

- Do not edit files.
- Do not produce patch hunks.
- Do not treat review comments as tasks.
- Do not emit prose instead of RCP/RDP/NREC when required.
- Do not omit negative_evidence for falsified routes or distillation.
- Do not ignore active negative exclusions.
- Do not repeat an actively excluded route unless reopened/stale/superseded or explicitly accepted.
- Do not omit `universalist_check`.
- Do not ignore falsified `universalist_check.decision: not-needed`.
- Do not select `not-required` for a same-cluster hot path.
- Do not select `add-new-surface` with unpaid rent or skipped universalist_check.
- Do not hand off implementation without proof matrix.
- Do not deliver lab history; deliver only distilled normal form.
- Do not close or hand off with no route-wave publication path.
- Do not override `$resolve` branch state or `$fixed-point-driver` implementation authority.

## Resources

- [packet-contract.md](references/packet-contract.md)
- [review-distillation-mode.md](references/review-distillation-mode.md)
- [negative-evidence-integration.md](references/negative-evidence-integration.md)
- [negative-route-exclusion-card.md](references/negative-route-exclusion-card.md)
- [negative-evidence-compaction.md](references/negative-evidence-compaction.md)
- [negative-writeback-policy.md](references/negative-writeback-policy.md)
- [route-wave-artifact.md](references/route-wave-artifact.md)
- [falsification-rules.md](references/falsification-rules.md)
- [universalist-check.md](references/universalist-check.md)
- [scar-tissue-ledger.md](references/scar-tissue-ledger.md)
- [counterexample-corpus.md](references/counterexample-corpus.md)
- [normal-form-selection.md](references/normal-form-selection.md)
- [abstraction-rent.md](references/abstraction-rent.md)
- [proof-matrix.md](references/proof-matrix.md)
- [gates.md](references/gates.md)
- [resolve-integration.md](references/resolve-integration.md)
- [audit-queries.md](references/audit-queries.md)
