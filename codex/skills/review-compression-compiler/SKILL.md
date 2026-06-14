---
name: review-compression-compiler
description: "Required packet compiler for review-driven mutation. Converts review findings, PR comments, validation failures, and repeated CAS findings into a compact `review_compression_packet` with selected normal form, abstraction rent, proof matrix, surface budget, and implementation handoff. Use for `$review-compression-compiler`, review compression, RCP-v1, same-cluster findings, adjacent CAS findings after a fix, add-surface pressure, dirty-tree review accumulation, or resolving reviews without code growth. Read-only: do not edit code."
metadata:
  version: "2.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Review findings are **counterexamples**, not tasks.

This skill compiles a stream of review findings, PR comments, validation failures, and repeated CAS findings into the smallest proof-carrying normal form that kills the counterexample family without unbounded code accumulation.

It does **not** edit files.

## What changed in v2

The packet is now small, mandatory, and gateable.

The v1 idea improved language but did not reliably emit the artifact. v2 optimizes for enforcement:

```text
No packet → no review-driven production patch.
No rent → no new surface.
No proof matrix → no implementation handoff.
No checkpoint commit after green slice → no long dirty-tree review churn.
```

## Core principle

```text
Review resolution is a compression problem, not a fix queue.
```

The unit of work is the defect family, not the comment.

## Activation boundary

Use this skill when any are true:

- two findings appear in the same subsystem, owner, protocol, state machine, proof surface, or invariant family;
- CAS finds an adjacent issue after a previous fix;
- a review item would add helper/wrapper/adapter/fallback/flag/branch/state variant/public symbol/compatibility path;
- the branch has a growing dirty tree from review-driven repairs;
- all decision-bearing review items are selecting `address`;
- production or test surface is growing without deletion/collapse evidence;
- the same cluster reappears after a selected normal form;
- `$resolve` needs a machine-auditable route packet before mutation.

Do not use when:

- one isolated bug has one obvious existing owner, no new surface, and one direct proof;
- implementation is already selected and only needs execution;
- the task is final closure proof only;
- the user asks only for explanation.

## Workflow position

```text
$resolve
  -> $review-adjudication
  -> $review-compression-compiler
  -> $fixed-point-driver
  -> $accretive-implementer
  -> validation / review closure
```

`$resolve` owns branch state. This skill owns counterexample compression. `$fixed-point-driver` owns normal-form remediation routing. `$accretive-implementer` owns single-writer execution after route selection.

## Packet-first rule

Every meaningful invocation must emit exactly one compact packet containing the literal key:

```yaml
review_compression_packet:
```

The packet may be inline in the transcript, written to a durable run ledger, or both. If a packet is written to a file, echo the path and include a compact inline summary with `packet_id`, `packet_status`, `selected_normal_form.kind`, `abstraction_rent.rent_status`, and `proof_matrix`.

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
    reason: second_same_cluster_finding | adjacent_review_after_fix | surface_growth | add_surface_request | repeated_address_route | same_cluster_reappeared | dirty_tree_review_accumulation | not-required
    review_item_ids: []
  counterexamples:
    - id: "CE-..."
      source: cas | native-review | pr-comment | validation | human
      bad_state_or_gap: "..."
      expected_contract: "..."
      owner_candidate: "..."
      evidence_ref: "..."
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

## Status rules

### `accepted`

Allowed only when:

- selected normal form has owner and proof matrix;
- implementation handoff has surface budget and forbidden actions;
- abstraction rent is `paid` or `not-applicable`;
- artifact state is current.

### `not-required`

Allowed only when all are true:

- item is isolated;
- same-cluster count is 1;
- route is existing-owner or no-change/validate-only;
- no helper/wrapper/adapter/fallback/flag/branch/public surface is added;
- direct proof is available.

`not-required` still emits the packet.

### `blocked`

Use when owner, artifact state, rent, proof, or safe route is missing.

Blocked packets must name the blocker and must not hand off mutation.

## Trigger rules

`same_cluster_findings >= 2` always requires `packet_status: accepted | blocked`. It cannot be `not-required`.

Any `add-new-surface` route requires `abstraction_rent.required: yes`.

Any route that adds public surface, fallback, compatibility path, or parser tolerance must set `surface_budget.production_surface: explicit_expansion` unless the new surface is fully private and bounded.

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

Use `final_only` only for truly tiny isolated fixes where another review immediately follows and dirty state will not accumulate.

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
- `abstraction_rent_auditor`
- `proof_matrix_minimizer`
- `review_compression_packet_auditor`
- `shadow_branch_evidence_scout`

Workers are advisory. The compiler/root owns synthesis and packet status.

## Shadow resolution mode

Optional high-cost mode.

Use only when the same cluster keeps reappearing after fixes and exploratory fixes would create scar tissue. A shadow branch/worktree may be used as evidence by another workflow; this skill only compresses the evidence into a normal-form packet.

## Hard rules

- Do not edit files.
- Do not produce patch hunks.
- Do not treat review comments as tasks.
- Do not emit prose instead of `review_compression_packet`.
- Do not select `add-new-surface` with unpaid rent.
- Do not hand off implementation without proof matrix.
- Do not allow same-cluster recurrence to become another local patch.
- Do not carry a large green dirty tree through repeated review cycles when a checkpoint commit is available.
- Do not override `$resolve` branch state or `$fixed-point-driver` implementation authority.

## Resources

- [packet-contract.md](references/packet-contract.md)
- [counterexample-corpus.md](references/counterexample-corpus.md)
- [normal-form-selection.md](references/normal-form-selection.md)
- [abstraction-rent.md](references/abstraction-rent.md)
- [proof-matrix.md](references/proof-matrix.md)
- [rcp-gate.md](references/rcp-gate.md)
- [resolve-integration.md](references/resolve-integration.md)
- [audit-queries.md](references/audit-queries.md)
