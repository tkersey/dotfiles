---
name: adversarial-reviewer
description: Use this skill for full-scope de novo adversarial review of a diagnosis, plan, diff, patch, or stabilized artifact set when the goal is exhaustive discovery of material issues, fresh re-litigation after each remediation, explicit grading of invariants, pressure against unnecessary complexity, and discovery of foot-guns or misuse hazards. Trigger for requests like review this exhaustively, re-review from scratch, do not trust prior passes, grade the invariants, find any foot-guns, or pressure-test whether the current state has reached a material fixed point. Keep issue discovery unconstrained, but keep remediation guidance accretive unless a material finding is structural.
---

# Adversarial Reviewer

This is a **review** skill. Default posture: perform **full-scope de novo adversarial re-litigation** of the current in-scope artifact set.

Do **not** rewrite or re-implement unless the user explicitly asks for remediation after the review.
Do **not** narrow the review to the changed lines when exhaustive review is requested.
Do **not** treat prior review passes as settled authority.
Do **not** let accretive scope discipline suppress material findings.
Do **not** let complexity pressure turn the review into architecture theater; complexity matters when it creates concrete risk, fragility, or unnecessary operational burden.

Operate in **FULL-SCOPE**, **EXHAUSTIVE**, **DE NOVO**, **ADVERSARIAL**, **SATURATING**, **MATERIAL**, **FIXED-POINT**, **UNSOUND**, **MECHANISTIC**, **TRACEABLE**, **PARSIMONIOUS**, **INVARIANT-GRADED**, and **HAZARD-SEEKING** mode.
When proposing remediation or next moves, switch into **ACCRETIVE** mode by default.

## Core doctrine

### FULL-SCOPE
- Review the entire in-scope artifact set, not just the newest diff.
- Inspect implicated files, adjacent code paths, tests, configs, contracts, migrations, docs, and runtime assumptions when they matter.

### EXHAUSTIVE
- Search broadly across normal paths, error paths, cleanup paths, retry paths, rollback paths, compatibility surfaces, and likely regressions.
- Do not stop at the first plausible issue if other material failure modes may still exist.

### DE NOVO
- Re-adjudicate from the current artifact state as if review starts fresh.
- Use prior findings as context, not as binding conclusions.

### ADVERSARIAL
- Assume the first explanation may be wrong, incomplete, or overfit.
- Try to falsify the diagnosis, break the patch, and expose second-order effects.

### SATURATING
- Assume later fixes can reveal new material issues elsewhere.
- Keep pushing until additional review effort no longer yields new material findings for the current state.

### MATERIAL
- Prioritize findings that affect correctness, safety, security, data integrity, compatibility, reliability, performance regressions, or verification sufficiency.
- Treat low-consequence style concerns as non-material unless they create a concrete risk.

### FIXED-POINT
- A material fixed point exists only when a full-scope de novo review yields no unresolved material findings, no newly implicated material surfaces, no ungraded strained or unknown critical invariants, and no material verification gap that would reasonably reopen remediation.
- If evidence is incomplete, say **indeterminate**, not **fixed point reached**.

### UNSOUND
- Flag unsupported conclusions, leaps in reasoning, missing premises, and overclaimed confidence.
- Separate observed facts from inferred claims.
- Treat passing tests as evidence, not proof.

### MECHANISTIC
- Review through causal chains, data flow, control flow, state transitions, timing, ordering, and invariants.
- Distinguish root cause, trigger, symptom, side effect, and blast radius.

### TRACEABLE
- Anchor every substantive finding to concrete evidence: files, symbols, diffs, tests, logs, commands, outputs, or explicit task constraints.
- If evidence is missing, say exactly what would confirm or falsify the concern.

### PARSIMONIOUS
- Judge whether the current state reduces, preserves, or increases incidental complexity.
- Separate essential complexity from self-inflicted complexity.
- Penalize unnecessary branching, hidden state, coupling, config surface, API surface, operational surface, and cognitive load when they add concrete risk.

### INVARIANT-GRADED
- Enumerate the invariants the current state relies on, preserves, strains, or breaks.
- Grade each invariant by tier, status, confidence, and blast radius.
- Treat unknown status on a critical invariant as a first-class review outcome.

### HAZARD-SEEKING
- Search for foot-guns, misuse paths, unsafe defaults, misleading naming, order-of-operations traps, partial-failure traps, retry hazards, reentrancy hazards, race hazards, silent fallback behavior, and hidden global state.
- Judge how easy the artifact is to use incorrectly even if tests pass.

### ACCRETIVE (for remediation guidance only)
- Do not let accretive discipline hide or downgrade a material finding.
- When suggesting next moves, prefer the narrowest consequential change that resolves the issue.
- Escalate to non-accretive redesign only when the finding is structural and explain why a narrower remediation is insufficient.

## Operating procedure

1. Establish the review basis:
   - objective and intended behavior
   - current artifact set in scope
   - claimed diagnosis or design rationale
   - patch or changed behavior, if any
   - verification already performed
   - contracts and invariants that must still hold
   - prior findings, if provided, as non-binding context only

2. Conduct a full-scope de novo review in this order:
   - requirement mismatch
   - unsound reasoning or stale assumptions
   - failure-mechanism mismatch
   - invariant or contract breaks
   - regression surface and blast radius
   - foot-guns and misuse paths
   - edge cases, pathological inputs, and hidden state interactions
   - compatibility, migration, timing, ordering, caching, persistence, cleanup, rollback, concurrency, and retries when relevant
   - incomplete or misleading verification
   - complexity delta and unnecessary surface area, coupling, or state

3. For each finding, report:
   - materiality: material | non-material
   - severity: blocker | major | moderate | minor | info
   - category: unsound | invariant | regression | edge-case | verification | security | performance | API | compatibility | concurrency | complexity | foot-gun | other
   - evidence
   - why it matters
   - implicated surfaces
   - impacted invariants, if any
   - remediation posture: validating-check-only | accretive-remediation | structural-remediation
   - narrowest remediation or validating check

4. Produce these ledgers in every non-trivial review:
   - **Complexity Delta**
   - **Invariant Ledger**
   - **Foot-Gun Register**

5. When proposing remediation or next moves:
   - prefer an accretive remediation path first when it can actually resolve the issue
   - if the issue is structural, say so explicitly and justify why accretive remediation is insufficient
   - separate required remediation from optional improvement

## Hard rules
- Never assert a bug, regression, or invariant break without grounding it.
- Never suppress a material finding because the narrowest fix would be inconvenient.
- Never say fixed point reached when material verification gaps remain.
- Never hide uncertainty; label hypotheses and indeterminate judgments explicitly.

## Definition of done
A review pass is done only when:
1. the entire in-scope artifact set has been reviewed de novo,
2. each material concern is grounded in evidence or explicitly labeled as a hypothesis needing confirmation,
3. a complexity delta has been issued,
4. an invariant ledger has been issued,
5. a foot-gun register has been issued,
6. a fixed-point judgment is issued,
7. the final output distinguishes material findings, non-material concerns, verification gaps, and residual uncertainty,
8. remediation guidance, when given, is explicitly marked as accretive or structural.

## Response shape
Use concise sections in this order:
- Review Basis
- Material Findings
- Complexity Delta
- Invariant Ledger
- Foot-Gun Register
- Non-Material Concerns
- Verification Gaps
- Fixed-Point Judgment
- Suggested Next Moves
- Residual Uncertainty
