---
name: review-compression-compiler
description: "Required packet compiler for review-driven mutation. Converts review findings, PR comments, validation failures, and repeated CAS findings into a compact `review_compression_packet` with selected normal form, explicit `$universalist` boundary check, abstraction rent, proof matrix, surface budget, and implementation handoff. Use for `$review-compression-compiler`, review compression, RCP-v1, same-cluster findings, wrong shape of truth, missing boundary artifact, adjacent CAS findings after a fix, add-surface pressure, dirty-tree review accumulation, or resolving reviews without code growth. Read-only: do not edit code."
metadata:
  version: "3.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Review findings are **counterexamples**, not tasks.

This skill compiles review findings, PR comments, validation failures, and repeated CAS findings into the smallest proof-carrying normal form that kills the counterexample family without unbounded code accumulation.

It does **not** edit files.

## v3 focus

v2 made `review_compression_packet` compact and enforceable. v3 adds a missing structural question:

```text
Is this cluster still an existing-owner repair,
or is it evidence that the boundary artifact / shape of truth is wrong?
```

That is the `$universalist` check.

A hot review cluster may be an owner bug. It may also mean the current representation lacks the right seam, protocol artifact, context certificate, explicit IR, or canonical composition boundary. v3 makes that decision visible and auditable.

## Core rule

```text
Review resolution is a compression problem, not a fix queue.
No packet -> no review-driven production patch.
No universalist_check on a hot cluster -> no same-cluster production patch.
No rent -> no new surface.
No proof matrix -> no implementation handoff.
```

## Activation boundary

Use this skill when any are true:

- two findings appear in the same subsystem, owner, protocol, state machine, proof surface, or invariant family;
- CAS finds an adjacent issue after a previous fix;
- an existing-owner repair has already been attempted in the same cluster;
- the next route would add helper/wrapper/adapter/fallback/flag/branch/state variant/public symbol/compatibility path;
- review findings suggest a missing boundary artifact, duplicated projection, protocol/state-machine gap, generated provenance gap, public-contract/internal mismatch, effect/callback IR gap, or wrong shape of truth;
- the branch has a growing dirty tree from review-driven repairs;
- all decision-bearing review items are selecting `address`;
- production or test surface is growing without deletion/collapse evidence;
- `$resolve` needs a machine-auditable route packet before mutation.

Do not use when:

- one isolated bug has one obvious existing owner, no new surface, no boundary smell, and one direct proof;
- implementation is already selected and only needs execution;
- the task is final closure proof only;
- the user asks only for explanation.

## Workflow position

```text
$resolve
  -> $review-adjudication
  -> $review-compression-compiler
  -> optional $universalist / root-equivalent universal boundary packet
  -> $fixed-point-driver
  -> $accretive-implementer
  -> validation / review closure
```

`$resolve` owns branch state. This skill owns counterexample compression. `$universalist` owns missing-boundary / wrong-shape-of-truth analysis. `$fixed-point-driver` owns normal-form remediation routing. `$accretive-implementer` owns single-writer execution after route selection.

## Packet-first rule

Every meaningful invocation must emit exactly one compact packet containing the literal key:

```yaml
review_compression_packet:
```

The packet may be inline, written to a durable run ledger, or both. If a packet is written to a file, echo the path and include a compact inline summary with `packet_id`, `packet_status`, `selected_normal_form.kind`, `universalist_check.decision`, `abstraction_rent.rent_status`, and `proof_matrix`.

Prose may explain the packet. Prose is not the packet.

## Required compact packet

Use this shape. Do not replace it with a long essay.

```yaml
review_compression_packet:
  packet_version: RCP-v1
  packet_id: "RCP-<cluster-or-item-id>"
  packet_status: accepted | blocked | not-required
  artifact_state_id: "branch/head/base/diff/phase"
  cluster_id: "..."
  trigger:
    reason: second_same_cluster_finding | adjacent_review_after_fix | surface_growth | add_surface_request | repeated_address_route | same_cluster_reappeared | dirty_tree_review_accumulation | boundary_shape_suspected | not-required
    review_item_ids: []
  counterexamples:
    - id: "CE-..."
      source: cas | native-review | pr-comment | validation | human
      bad_state_or_gap: "..."
      expected_contract: "..."
      owner_candidate: "..."
      evidence_ref: "..."
  universalist_check:
    considered: yes | no
    trigger:
      same_cluster_findings: 0
      existing_owner_repair_attempted: yes | no
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
  selected_normal_form:
    kind: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
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
  closure_rule:
    if_same_cluster_finding_reappears: reopen_compiler | block | escalate
```

## Universalist check rules

`universalist_check` is required in every packet.

`considered: yes` is required when any are true:

- `same_cluster_findings >= 2`;
- an existing-owner repair was already attempted in the cluster;
- same cluster reappeared after a selected normal form;
- selected route would add public surface, fallback, compatibility path, parser tolerance, state variant, or new abstraction;
- any trigger field under `universalist_check.trigger` is `yes`;
- the candidate normal form is `add-new-surface`.

`considered: no` is allowed only for isolated, no-new-surface, direct existing-owner or proof-only routes with no boundary smell.

`decision: use-universalist` means run `$universalist` or emit a root-equivalent universal boundary packet before `$fixed-point-driver` receives a mutation handoff.

`decision: blocked` means no production mutation until the missing boundary/artifact question is resolved.

## Universal boundary packet

When `decision: use-universalist`, require either an actual `$universalist` output or this root-equivalent packet:

```yaml
universal_boundary_packet:
  packet_version: UBP-v1
  artifact_state_id: "..."
  cluster_id: "..."
  boundary_smell:
    missing_boundary_artifact: yes | no
    duplicated_projection: yes | no
    protocol_or_state_machine_missing: yes | no
    generated_provenance_gap: yes | no
    public_contract_drives_internals: yes | no
    effect_or_callback_ir_missing: yes | no
  candidate_boundary_artifact:
    kind: protocol | state-machine | context-certificate | explicit-ir | effect-signature | canonical-projection | none
    owner: "..."
    seam: "..."
  decision: climb | not-needed | blocked
  reason: "..."
  proof_signal: []
```

If `decision: climb`, selected normal form should be `refactor-existing-owner`, `delete-collapse-canonicalize`, or a warranted `add-new-surface` whose rent is paid.

## Status rules

### `accepted`

Allowed only when:

- selected normal form has owner and proof matrix;
- implementation handoff has surface budget and forbidden actions;
- abstraction rent is `paid` or `not-applicable`;
- universalist_check is complete and not blocked;
- artifact state is current.

### `not-required`

Allowed only when all are true:

- item is isolated;
- same-cluster count is 1;
- route is existing-owner or no-change/validate-only;
- no helper/wrapper/adapter/fallback/flag/branch/public surface is added;
- no boundary smell exists;
- direct proof is available.

`not-required` still emits the packet.

### `blocked`

Use when owner, artifact state, rent, proof, universalist decision, or safe route is missing.

Blocked packets must name the blocker and must not hand off mutation.

## Trigger rules

`same_cluster_findings >= 2` always requires `packet_status: accepted | blocked` and `universalist_check.considered: yes`.

Any `add-new-surface` route requires both:

```yaml
universalist_check.considered: yes
abstraction_rent.required: yes
```

Any route that adds public surface, fallback, compatibility path, parser tolerance, state variant, or new abstraction must set:

```yaml
surface_budget.production_surface: explicit_expansion
```

unless the surface is private, bounded, and explicitly retires more surface than it adds.

Any repeated same-cluster finding after implementation must follow `closure_rule`; do not patch locally again.

## Abstraction rent

Rent is paid only when new surface:

- retires existing surface;
- prevents named future patches;
- makes an illegal state uninhabitable at the owner;
- localizes unavoidable external obligation;
- replaces multiple local repairs with one canonical owner;
- or carries explicit user/upstream expansion authority.

Unpaid rent blocks `add-new-surface`.

## Proof matrix

Do not create one test per wound by default. Prefer a proof matrix that covers the family:

- invariant test;
- authority-boundary test;
- state-transition table;
- round-trip/canonicalization check;
- rejection matrix;
- one representative regression plus table;
- existing test extension over duplicate new tests.

## Commit boundary policy

When an accepted packet produces a green local repair slice, prefer:

```text
commit_boundary.policy: checkpoint_after_local_proof
```

Use it when:

- CAS has produced same-cluster churn;
- dirty tree is accumulating multiple review repairs;
- local proof is green for the selected normal form;
- no unrelated changes are staged.

The checkpoint commit is not final closure. It creates a stable reviewed tuple for the next CAS pass and prevents one giant dirty-tree review loop.

## Validation

When a packet is saved to a file, validate it when possible:

```bash
python codex/skills/review-compression-compiler/tools/rcp_gate.py path/to/packet.yml
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
- `review_compression_packet_auditor`
- `shadow_branch_evidence_scout`

Workers are advisory. The compiler/root owns synthesis and packet status.

## Hard rules

- Do not edit files.
- Do not produce patch hunks.
- Do not treat review comments as tasks.
- Do not emit prose instead of `review_compression_packet`.
- Do not omit `universalist_check`.
- Do not select `not-required` for a same-cluster hot path.
- Do not select `add-new-surface` with unpaid rent or skipped universalist_check.
- Do not hand off implementation without proof matrix.
- Do not allow same-cluster recurrence to become another local patch.
- Do not override `$resolve` branch state or `$fixed-point-driver` implementation authority.

## Resources

- [packet-contract.md](references/packet-contract.md)
- [universalist-check.md](references/universalist-check.md)
- [counterexample-corpus.md](references/counterexample-corpus.md)
- [normal-form-selection.md](references/normal-form-selection.md)
- [abstraction-rent.md](references/abstraction-rent.md)
- [proof-matrix.md](references/proof-matrix.md)
- [rcp-gate.md](references/rcp-gate.md)
- [resolve-integration.md](references/resolve-integration.md)
- [audit-queries.md](references/audit-queries.md)
