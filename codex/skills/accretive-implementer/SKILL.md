---
name: accretive-implementer
description: Use this skill for non-trivial coding tasks where the job is to implement, adapt, harden, or repair code in a narrow, reviewable, contract-first, evidence-backed, witness-bearing way. Trigger for planned features, net-new code, implementation from a design or plan, migrations, refactors with correctness pressure, review-driven changes, bug fixes, regressions, failing tests, or single-change hardening tasks. Accept handoff agendas from review-adjudication or fixed-point-driver without re-adjudicating them unless the evidence is stale or contradictory. In implementation mode, realize the requested behavior through the canonical existing architecture with minimal blast radius. In remediation mode, diagnose the likely failure mechanism before editing. Do not trigger for trivial formatting, rote renames, or purely informational questions that do not require code changes or verification.
---

# Accretive Implementer

Use this as the general coding skill for both **implementation** and **remediation**.

## Output modes
- **Standard**: use for normal non-trivial work.
- **Fast**: use when the user wants the actionable result with minimal scroll.

## CLI-tail-weighted reporting
Assume the user may only see the last screenful of terminal output.
- Keep early sections terse.
- Put decisive outcome and next action in **Execution Bottom Line**.
- **Execution Bottom Line** must be the final section.

## Shared doctrine
Operate in **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **TOTAL**, **REFINEMENT-FIRST**, **CONTRACT-FIRST**, **INVARIANT-FIRST**, **MECHANISTIC**, **ACCRETIVE**, **TRACEABLE**, and **SEAM-DISCIPLINED** mode.

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
- Prefer witnesses that survive inspection: boundary refinement, direct checks, exhaustive handling, constructor discipline, or targeted tests.
- If a claim has no witness, downgrade it or route a validating check.

### TOTAL / REFINEMENT-FIRST
- Prefer total helpers and explicit handling of partiality on critical paths.
- Refine raw inputs at the boundary into narrower validated representations before deeper logic depends on them.
- Reject illegal inhabitants and avoid partial eliminators introduced by the change.

### MECHANISTIC / ACCRETIVE / SEAM-DISCIPLINED
- Explain the intended behavior or failure mechanism as a causal chain.
- Choose the stable boundary before cutting.
- State why the change should not be smaller and should not be larger.
- Prefer the narrowest truthful change that realizes the contract or repairs the defect.

## Entry branches
- **Implementation mode**: feature work, plans, migrations, refactors, or net-new behavior.
- **Remediation mode**: bugs, regressions, failing tests, review findings, soundness defects, or broken invariants.

If both are present, start in remediation mode for the broken path, then continue in implementation mode only for the smallest follow-on change required to realize the requested outcome.

## Agenda intake
Accept handoff from:
- **review-adjudication**: `Act On`, `Need Evidence`, `Handoff Agenda`, `PR Why Ledger`
- **fixed-point-driver**: routed findings, one-change challenge result, or validation tasks

Rules:
- Treat accepted agenda items as in-scope.
- Treat rebutted, deferred, stale, or out-of-scope items as out-of-scope unless new evidence changes them.
- Do not redo broad adjudication here. Only reopen it if the agenda is stale, contradictory, or mechanically impossible.

## Non-trivial task gate
Before editing code on a non-trivial task, determine internally:
- **Contract**: one sentence for what working means.
- **Invariants**: what must remain true and what should become impossible.
- **Chosen Cut**:
  - stable boundary
  - not smaller
  - not larger
  - proof signal

Surface these sections when the task is non-trivial, the seam is non-obvious, or upstream evidence is contested.

## Terrain defaults
### Brownfield defaults
- minimize surface area
- prefer characterization or a tight repro when behavior is unclear
- prefer seams and adapters at boundaries over scattered repairs
- if uncertainty is high, cut temporary observability first, then behavior

### Greenfield defaults
- start with the boundary and choose a normal form early
- prefer one obvious path for each rule
- defer abstraction until it earns itself
- bake in the smallest fast proof signal that makes the contract executable

## Operating procedure
1. Restate the task as objective, scope, constraints, and done condition.
2. Choose the branch and terrain.
3. Establish **Contract + Invariants + Chosen Cut**.
4. Run a quick **truth-surface audit** when claims, enforcement, tests, and artifacts may drift.
5. Implement or remediate accretively.
6. Verify with the fastest credible proof signal you can actually run.
7. Surface assumptions, witnesses, and residual risk near the end.

## Output contract
### Standard
Use concise sections in this order:
- Objective
- Branch
- Agenda Intake (only when upstream agenda materially shaped the work)
- Contract (non-trivial or non-obvious cases)
- Invariants (non-trivial or non-obvious cases)
- Chosen Cut (non-trivial or non-obvious cases)
- Changes
- Verification
- Assumptions
- Witnesses
- Risks
- Execution Bottom Line

### Fast
Use concise sections in this order:
- Objective
- Branch
- Changes
- Verification
- Witnesses
- Execution Bottom Line

## Hard rules
- Never guess when evidence is missing.
- Never claim a guarantee without a witness.
- Never broaden scope without saying why.
- Never add abstraction before the concrete shape earns it.
- Never leave a new illegal inhabitant or partial eliminator unremarked on.
- Never bury the exact next move below the fold.

## Resources
- [contract-and-cut-playbook.md](references/contract-and-cut-playbook.md)
- [terrain-defaults.md](references/terrain-defaults.md)
- [structural-proof-patterns.md](references/structural-proof-patterns.md)
- [one-change-mode.md](references/one-change-mode.md)
- [common-soundness.md](../../../references/common-soundness.md)
- [common-ledgers.md](../../../references/common-ledgers.md)
- [common-cli-reporting.md](../../../references/common-cli-reporting.md)
