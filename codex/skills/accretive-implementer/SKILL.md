---
name: accretive-implementer
description: "Right-sized single-writer implementation/remediation: implement, adapt, harden, repair, or validate non-trivial code with the smallest owned surface, contract-first, witness-backed, and surface-budgeted. Trigger for planned features, migrations, correctness-sensitive refactors, review fixes, bugs, regressions, failing tests, single-change hardening, no-change validation, delete/collapse/canonicalize routes, or review-adjudication/fixed-point-driver mutation handoffs. Alias: accretive-implementor. Not for trivial formatting, rote renames, informational questions, broad adjudication, final closure, or speculative code addition."
---

# Accretive Implementer: Right-Sized Single-Writer Implementation

Use this as the general coding skill for **implementation** and **remediation** when mutation is allowed.

The goal is not to add code. The goal is to deliver the smallest sufficient owned surface that satisfies the contract and leaves a witness.

Core rule:

```text
Write the code that makes the invalid state impossible at the rightful owner, and no code beyond that.
```

## Output modes

- **Standard**: normal non-trivial work.
- **Fast**: actionable result with minimal scroll.

## CLI-tail-weighted reporting

Assume the user may only see the last screenful of terminal output.

- Keep early sections terse.
- Put decisive outcome, route, proof, and exact next action in **Execution Bottom Line**.
- **Execution Bottom Line** must be the final section.

## Activation boundary

Use this skill when the current turn asks for a concrete code change, repair, migration, hardening pass, review-fix implementation, or proof/validation route that may become code.

Do not use it when the main task is:

- deciding whether a review claim is actionable: use `review-adjudication`;
- running exhaustive repeated review/fix/ablation closure: use `fixed-point-driver`;
- final readiness or closure proof: use `verification-closure`;
- bounding proof/risk before deciding actionability: use `context-bounded-verification`;
- selecting among possible moves: use `dominance`, `universalist`, `reduce`, or `spec-pipeline` as appropriate;
- asking only for information, explanation, formatting, rote rename, or non-code text edits.

## Declared-use auditability

This skill may be used by native activation, explicit assistant declaration, or root-equivalent companion phase. Treat all three as behaviorally meaningful.

When the assistant declares use of `accretive-implementer` in transcript text, the final **Execution Bottom Line** must include:

```text
right_sized_route:
surface_delta_call:
```

These fields make transcript-declared use auditable even when native skill activation counters miss the workflow.

Allowed `right_sized_route` values:

```text
no-change | validate-only | delete-collapse-canonicalize | mutate-existing-owner | add-new-surface | routed | blocked
```

Allowed `surface_delta_call` values:

```text
smaller | same | larger-with-warrant | larger-without-warrant | none | unknown
```

`larger-without-warrant` is never a successful implementation outcome. It means stop, route to `fixed-point-driver`, or revise the patch.

## Shared doctrine

Operate in **UNTRUSTED-UNTIL-WITNESSED**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **TOTAL**, **REFINEMENT-FIRST**, **CONTRACT-FIRST**, **INVARIANT-FIRST**, **MECHANISTIC**, **SURFACE-ACCOUNTED ACCRETIVE**, **TRACEABLE**, **CANONICAL**, and **SEAM-DISCIPLINED** mode.

### CONTRACT-FIRST

- State what “working” means before editing.
- Prefer an executable contract or proof target when possible.
- If the contract is materially ambiguous, choose the safest bounded interpretation and label the assumption.

### INVARIANT-FIRST

- Name what must remain true and what should become impossible.
- Prefer stronger protection at the truthful boundary.
- If an invariant exists only in prose, treat it as under-enforced.

### WITNESS-BEARING

- Treat every material claim as needing a concrete witness.
- Prefer witnesses that survive inspection: boundary refinement, direct checks, exhaustive handling, constructor discipline, targeted tests, or current artifact inspection.
- If a claim has no witness, downgrade it or route a validating check.

### TOTAL / REFINEMENT-FIRST

- Prefer total helpers and explicit handling of partiality on critical paths.
- Refine raw inputs at the boundary into narrower validated representations before deeper logic depends on them.
- Reject illegal inhabitants and avoid partial eliminators introduced by the change.

### SURFACE-ACCOUNTED ACCRETIVE

Accretive does not mean additive.

A change is accretive only when it improves durable capability, correctness, proof, maintainability, or future-change leverage **after accounting for added surface**.

A deletion, collapse, canonicalization, stricter boundary, better witness, or no-code proof can be the most accretive move.

Every additive move must pass:

```text
why not no-code?
why not validate-only?
why not delete/collapse/canonicalize?
why not mutate the existing owner?
why does this new surface earn itself?
```

## Entry branches

- **Implementation mode**: feature work, plans, migrations, refactors, or net-new behavior.
- **Remediation mode**: bugs, regressions, failing tests, review findings, soundness defects, broken invariants, or stale/duplicate truth surfaces.

If both are present, start in remediation mode for the broken path, then continue in implementation mode only for the smallest follow-on change required to realize the requested outcome.

## Artifact-state preflight

Before non-trivial edits or upstream-agenda implementation, record internally:

```yaml
artifact_state_id:
  branch: <branch-or-unknown>
  head: <sha-or-current-tree>
  diff_scope: <changed paths or target paths>
  dirty_state: clean | dirty | unknown
  agenda_source: user-direct | review-adjudication | fixed-point-driver | other | none
```

If an upstream agenda was produced for a different artifact state, treat it as stale and do not mutate until refreshed or explicitly revalidated.

## Mutation authority

This skill may edit only when one of these is true:

- the current user request explicitly asks to implement, fix, repair, migrate, harden, apply, or change code;
- `review-adjudication` supplies an active, current-state Resolution Warrant with permitted action `mutate-code`;
- `fixed-point-driver` supplies a current-state implementation handoff with permitted route, permitted scope, forbidden actions, surface budget, ablation status, and proof required.

If the handoff is stale, lacks artifact-state identity, lacks permitted action, or only asks for validation/proof/no-change/defer, do not mutate. Produce the smallest validation, proof, no-change, defer, routed, or blocked report instead.

## Agenda intake

Accept handoff from:

- **review-adjudication**: active Resolution Warrants, Handoff Agenda, PR Why Ledger, Governing Invariant Candidate, and explicit forbidden actions.
- **fixed-point-driver**: routed findings, one-change challenge result, validation task, Truth-Owner Normal Form rewrite, ablation status, surface budget, and proof required.

Rules:

- Treat current, active, permitted agenda items as in-scope.
- Treat rebutted, deferred, stale, expired, blocked, validation-only, proof-only, no-change, or out-of-scope rows as out-of-scope for mutation unless new evidence changes them.
- Do not redo broad adjudication here.
- Reopen adjudication only if the agenda is stale, contradictory, mechanically impossible, locally valid but globally incoherent, or lacks a mutation warrant for the requested edit.
- Preserve forbidden actions and surface budgets from the handoff.

### Required fixed-point handoff shape

When `fixed-point-driver` routes mutation here, require this shape or reconstruct it root-equivalently before editing:

```yaml
implementation_handoff:
  target_skill: accretive-implementer
  artifact_state_id: "..."
  truth_unit_ids: []
  selected_rewrite: delete | privatize | merge | tighten-owner | reuse-owner | add-escrow | validate-only | no-change | blocked
  permitted_route: no-change | validate-only | delete-collapse-canonicalize | mutate-existing-owner | add-new-surface | routed | blocked
  permitted_scope: []
  forbidden_actions: []
  surface_budget:
    production_surface: zero_or_negative | bounded_positive | explicit_expansion
    added_helpers_allowed: yes | no
    added_wrappers_adapters_allowed: yes | no
    added_flags_or_fallbacks_allowed: yes | no
    public_symbols_allowed: yes | no
    compatibility_paths_allowed: yes | no
  ablation_status: not-required | local-preflight | external-clearance-required | blocked
  addition_escrow_policy: not-allowed | allowed-with-rent-payment | required
  proof_required: []
  stale_if: []
```

If `ablation_status: external-clearance-required` or `blocked`, do not add production code until the fixed-point or ablation gate clears.

## Right-Sized Implementation Kernel

Before editing, choose exactly one route:

1. `no-change`
2. `validate-only`
3. `delete-collapse-canonicalize`
4. `mutate-existing-owner`
5. `add-new-surface`

Prefer routes in that order.

A route may move right only when all routes to its left are insufficient and the insufficiency is named.

### Route definitions

- `no-change`: current artifacts already satisfy the contract, or the requested mutation is unsupported, stale, out of scope, or harmful.
- `validate-only`: proof must precede production mutation; add/run only proof, repro, characterization, or diagnostic work.
- `delete-collapse-canonicalize`: remove, collapse, privatize, decommission, or canonicalize existing surface while preserving behavior.
- `mutate-existing-owner`: change the canonical owner in place.
- `add-new-surface`: add new production surface only when the previous routes cannot satisfy the contract.

For any `add-new-surface` route, provide:

- why `no-change` fails;
- why `validate-only` is insufficient;
- why `delete-collapse-canonicalize` is insufficient;
- why the existing owner cannot absorb the change;
- what surface budget is consumed;
- what proof demonstrates the new surface earns itself.

If this cannot be answered, do not add code. Return `validate-only`, `blocked`, or route to `fixed-point-driver`.

## Surface Budget Gate

Before non-trivial implementation, choose the smallest sufficient surface delta.

Default for remediation: net production surface should be zero or negative unless the defect cannot be fixed at the existing owner.

Adding any of these requires explicit justification:

- helper
- wrapper
- adapter
- fallback
- flag
- knob
- branch
- state variant
- public symbol
- compatibility path
- parser tolerance
- catch-and-continue path
- default/coercion behavior
- new abstraction

For each added surface, record:

- why no existing owner can absorb the behavior;
- what invalid state or duplicate owner it prevents;
- what surface it retires, replaces, or makes unnecessary;
- the proof signal that the addition is smaller than the alternatives.

## Ablation Preflight

Before adding code, ask:

- Can the contract be satisfied by deleting dead, dominated, duplicate, vestigial, pass-through, or non-canonical surface?
- Can the change be made at the existing canonical owner instead of adding a second owner?
- Can a stricter constructor, parser, type, schema, fixture, or invariant boundary make downstream defensive code unnecessary?
- Can the requested behavior be proven already true with a better witness?
- If a helper/wrapper/adapter is proposed, what existing surface does it retire or simplify?

If ablation is plausible but not locally decidable, route to `fixed-point-driver` or an ablation auditor before adding production surface.

Escalate out of this skill when any are true:

- the proposed fix adds a new owner for a rule that already has an owner;
- more than one helper/wrapper/adapter is being added;
- a flag, fallback, compatibility path, or parser tolerance is being introduced;
- the change preserves a duplicate path because deletion feels risky;
- the patch would make review easier now but leave additive scaffold behind;
- two or more findings orbit the same invariant.

## Non-trivial task gate

Before editing code on a non-trivial task, determine internally:

- **Contract**: one sentence for what working means.
- **Invariants**: what must remain true and what should become impossible.
- **Right-sized route**: `no-change` | `validate-only` | `delete-collapse-canonicalize` | `mutate-existing-owner` | `add-new-surface`.
- **Chosen Cut**:
  - stable boundary
  - why not smaller
  - why not larger
  - proof signal
- **Truth surface**: claim, owner, enforcement, proof, and generated artifacts that must agree.
- **Surface budget**: surface added, removed, preserved, or justified.

Surface these sections when the task is non-trivial, the seam is non-obvious, upstream evidence is contested, or production code changed.

Before the final **Execution Bottom Line**, ensure the implementation can answer:

```text
Governing invariant / truth unit:
Canonical owner or chosen cut:
Right-sized route:
Witness / proof signal:
Surface delta:
What invalid state or overbroad behavior remains impossible:
```

## Terrain defaults

### Brownfield defaults

- minimize surface area
- prefer characterization or a tight repro when behavior is unclear
- prefer the existing primitive or canonical helper before a bespoke wrapper
- prefer seams and adapters at boundaries over scattered caller-side repairs
- if uncertainty is high, cut temporary observability first, then behavior
- delete, collapse, or canonicalize duplicate truth surfaces before adding another path
- no production additions until the ablation preflight is answered

### Greenfield defaults

- start with the boundary and choose a normal form early
- prefer one obvious path for each rule
- defer abstraction until it earns itself
- bake in the smallest fast proof signal that makes the contract executable
- prefer adding a stronger constructor or state model over adding downstream defensive branches

## Operating procedure

1. Restate objective, scope, constraints, done condition, and mutation authority.
2. Choose branch and terrain.
3. Record artifact-state preflight for non-trivial work.
4. Choose the right-sized route.
5. Establish **Contract + Invariants + Chosen Cut + Surface Budget**.
6. Run ablation preflight before adding code.
7. Run a quick truth-surface audit when claims, enforcement, tests, and artifacts may drift.
8. Implement, validate, route, or no-change according to the selected route.
9. Verify with the fastest credible proof signal you can actually run.
10. Surface assumptions, witnesses, surface delta, and residual risk near the end.

## Successful outcomes

A successful run may be any of:

- `implemented`: code changed and proof ran or was blocked with an exact blocker.
- `validated-no-change`: no production code changed because current behavior already satisfies the contract.
- `validation-only`: no production code changed because proof must precede mutation.
- `delete-collapse-canonicalize`: production surface was reduced or canonicalized with preservation proof.
- `routed`: ablation, fixed-point, adjudication, or verification is required before safe implementation.
- `blocked`: mutation lacks authority, evidence, artifact-state freshness, or proof route.

Do not add code merely to avoid reporting a non-implementation outcome.

## Output contract

### Standard

Use concise sections in this order:

- Objective
- Branch
- Mutation Authority
- Artifact State (non-trivial or upstream-agenda cases)
- Agenda Intake (only when upstream agenda materially shaped the work)
- Contract (non-trivial or non-obvious cases)
- Invariants (non-trivial or non-obvious cases)
- Right-Sized Route (non-trivial, non-obvious, transcript-declared, root-equivalent, or code-changing cases)
- Chosen Cut (non-trivial or non-obvious cases)
- Surface Budget / Ablation Preflight (when production code changed or additive route was considered)
- Changes
- Verification
- Assumptions
- Witnesses
- Surface Delta Receipt (when production code changed)
- Risks
- Execution Bottom Line

### Fast

Use concise sections in this order:

- Objective
- Branch
- Contract / Cut (one line when the task is non-trivial, agenda-driven, correctness-sensitive, transcript-declared, root-equivalent, or code-changing)
- Changes
- Verification
- Witnesses
- Execution Bottom Line

## Surface Delta Receipt

When non-trivial production code changes, include:

| surface | count | notes |
|---|---:|---|
| production files touched |  |  |
| production insertions |  |  |
| production deletions |  |  |
| public symbols added |  |  |
| helpers/wrappers/adapters added |  |  |
| flags/branches/state variants added |  |  |
| duplicate/shadow paths retired |  |  |
| tests/proofs added |  |  |
| net surface call | smaller/same/larger-with-warrant/larger-without-warrant |  |

If counts are not available, use `unknown` and explain why. Do not invent counts.

## Execution Bottom Line contract

The final section must be self-contained and include:

```text
Execution Bottom Line:
- outcome:
- right_sized_route:
- surface_delta_call:
- governing invariant / truth unit:
- selected owner or cut:
- proof receipt:
- open gate:
- exact next action:
```

In Fast mode, compress values to one line each, but do not omit `right_sized_route` or `surface_delta_call`.

## Hard rules

- Never guess when evidence is missing.
- Never claim a guarantee without a witness.
- Never broaden scope without saying why.
- Never add abstraction before the concrete shape earns it.
- Never add production surface without answering the right-sized route ladder.
- Never leave a new illegal inhabitant or partial eliminator unremarked on.
- Never preserve duplicate truth owners without a warrant.
- Never treat `accretive` as permission to add code.
- Never omit `right_sized_route` and `surface_delta_call` after transcript-declared use.
- Never treat `larger-without-warrant` as a successful outcome.
- Never bury the exact next move below the fold.

## Resources

- [right-sized-kernel.md](references/right-sized-kernel.md)
- [surface-budget.md](references/surface-budget.md)
- [fixed-point-handoff.md](references/fixed-point-handoff.md)
- [doctrine-alpha.md](references/doctrine-alpha.md)
- [contract-and-cut-playbook.md](references/contract-and-cut-playbook.md)
- [structural-proof-patterns.md](references/structural-proof-patterns.md)
- [tail-proof.md](references/tail-proof.md)
- [terrain-defaults.md](references/terrain-defaults.md)
- [fresh-eyes-pass.md](references/fresh-eyes-pass.md)
- [one-change-mode.md](references/one-change-mode.md)
- [common-ledgers.md](references/common-ledgers.md)
- [common-soundness.md](references/common-soundness.md)
- [common-cli-reporting.md](references/common-cli-reporting.md)
- [type-theoretic-soundness.md](references/type-theoretic-soundness.md)
- [example-invocations.md](references/example-invocations.md)
