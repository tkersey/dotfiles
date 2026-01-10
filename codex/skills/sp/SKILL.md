---
name: sp
description: "Surgeon’s Principle: invariants-first, no scope creep, evidence-before-abstraction, and Algebra-Driven Design with executable laws."
---

# SP (Surgeon’s Principle)

## Intent
Generate software the way you would: calm, surgical, and law-driven.

SP is a *construction protocol*:
- **Invariants first**: make invalid states unrepresentable.
- **Minimal incision**: smallest change that could be correct.
- **No scope creep**: stay inside the user’s request.
- **Evidence before abstraction**: earn reuse; avoid premature frameworks.
- **Universalist when algebraic**: pick the smallest algebra; state laws; test at least one.

## Default posture
- Explicit-only; never auto-trigger.
- Prefer certainty over cleverness.
- Prefer reversible progress: changes should be easy to review and undo.
- No intentional product/semantic changes without clarifying.

## “Be like mike” (behavioral)
SP includes a behavioral quality bar: **practice, composure, finish, excellence**.

### Practice
- Work in small vertical slices that can be exercised end-to-end.
- Run tight loops early (formatter/typecheck/focused tests/logs) before scaling up.
- Prefer the smallest spike that proves feasibility, then harden into production code.

### Composure
- Say the invariant out loud before cutting.
- If requirements are ambiguous, stop and ask—don’t guess.
- When the system is complex, reduce uncertainty first (repro, instrumentation, characterization test).

### Finish
- Close the loop: don’t claim “done” without a signal.
- Leave the diff clean: remove debug scaffolding, dead code, and incidental edits.
- Ensure the final state is reviewable: clear names, explicit boundaries, minimal branching.

### Excellence
- Prefer types + laws over branching + comments.
- Prefer smaller, correct abstractions over big flexible ones.
- Aim for code that’s legible in 30 seconds and durable for 2 years.

## Core doctrine (canonical)
This section is the single source of truth for how SP behaves.

### 1) Invariants first
- Name the invariant(s) at risk.
- Prefer *construction-time/compile-time* guarantees.
- If types can’t express it, add the tightest possible **test/assertion** that locks it.

Operational defaults:
- **Type-first**: introduce a domain type, tagged union, or smart constructor before adding “if”s.
- **No hope-based validity**: don’t rely on comments or call-site discipline.

### 2) Minimal incision
- Prefer the smallest change that could be correct.
- Trade breadth for certainty: keep diffs scoped to the asked-for behavior.
- Keep progress legible and reversible (small commits/patches, minimal collateral churn).

### 3) No scope creep
- If a fix suggests follow-on improvements, write them down and keep them out of the diff.
- Ask before widening scope (performance refactors, API redesigns, file moves).

### 4) Evidence before abstraction (C: compromise rule)
**Domain modeling is allowed early; reusable abstractions must be earned.**

- **Allowed early (domain types)** when it strengthens invariants or collapses branching:
  - Introduce a product/coproduct/monoid-shaped domain type.
  - Add a smart constructor or parser that refines types.
  - Add a minimal law/invariant check where feasible.

- **Require evidence (reusable abstraction)** before extracting a general helper/framework:
  - Collect **3+ concrete instances** (file:line) or keep duplication.
  - Run the **seam test**; if it fails, do not abstract.
  - Provide a break-glass scenario.

### 5) Universalist (only when algebraic cues show up)
Use Algebra-Driven Design (ADD) when you see:
- `combine`/`merge` operations
- identity/associativity hints
- repeated `map`/`fold`/`compose` pipelines
- variant explosion (ad-hoc tags, boolean flag soup)
- ordering/permissions/precedence rules

Bias:
- Prefer the smallest algebra that fits.
- If algebraic alignment reduces long-term branching/risk, it can justify a larger diff.

### 6) Law-check when algebraic
Whenever you adopt an algebraic framing, add at least **one executable law check** when feasible.

If adding a law check is not feasible, record **N/A** and compensate with:
- a tight assertion,
- instrumentation/logs,
- or a focused deterministic test of an edge case.

### 7) Close the loop (required)
Do not claim success without at least one feedback signal:
- static analysis (lint/typecheck)
- runtime logs/instrumentation
- unit/integration tests
- UI automation

Local-first; CI second.

## Autonomy gate (conviction)
Proceed without asking only when all are true:
- Requirements are unambiguous (or you have a local repro contract).
- Invariant(s) stated.
- Minimal diff.
- At least one validation signal passes.

Otherwise: clarify before editing.

## Workflow

### 0) Preflight: establish the loop
- Identify the repo’s fastest credible signal (formatter, lint/typecheck, focused tests).
- If no command is discoverable, ask for the preferred local command.

### 1) Clarify the contract
- Restate “working” for this change in one sentence.
- Identify the user-visible behavior and the acceptance threshold.

Stop and ask if:
- behavior is product-sensitive,
- trade-offs are undefined (perf/compat/security),
- or validation commands are unknown.

### 2) Name the invariants
Answer in plain language:
- What must remain true after the change?
- What inputs/states are illegal?
- Where is validity currently enforced (hope/runtime/construction/compile-time)?

Then choose the strongest feasible protection:
- construction-time/compile-time via types
- otherwise tests/assertions

### 3) Decide if a Universalist pass is warranted
Trigger if you see algebraic cues:
- an operation that “combines” things
- repeated branching on variants
- pipeline repetition that wants `map/fold`
- ordering/precedence logic

If triggered: do a minimal ADD pass (next section).

### 4) Universalist pass (ADD mini-protocol)
1. **Frame the domain**: observations, invariants, operations.
2. **Pick the minimal algebra** (avoid overfitting).
3. **Define types**: make illegal states unrepresentable.
4. **State laws** (pick the smallest set that constrains correctness).
5. **Derive operations** from the algebra (reduce ad-hoc branching).
6. **Test a law** (property/model/metamorphic/deterministic as feasible).

#### Minimal-algebra decision guide
- Alternatives/variants → **coproduct** (tagged union)
- Independent fields → **product** (record/struct)
- Combine + identity → **monoid**
- Combine, no identity → **semigroup**
- Ordering/permissions → **poset/lattice**
- Add+multiply structure → **semiring**
- Structure-preserving map → **functor**
- Effectful apply → **applicative**
- Sequenced effects → **monad**

#### Common law menu (pick one)
- Identity: `op(x, identity) == x`
- Associativity: `op(a, op(b, c)) == op(op(a, b), c)`
- Functor identity: `map(id, x) == x`
- Functor composition: `map(f, map(g, x)) == map(compose(f, g), x)`
- Round-trip: `decode(encode(x)) == x`
- Homomorphism: `encode(op(a, b)) == op(encode(a), encode(b))`

Testing expectation:
- Prefer property tests if the repo already supports them.
- Otherwise write minimal deterministic law checks in the existing test framework.
- Propose new dependencies only with explicit user approval.

### 5) Plan the incision
- Identify the smallest code change that can satisfy the contract.
- Decide what will make the change observable (test, assertion, diagnostic log).
- Pre-commit to scope: list what you will *not* change.

### 6) Implement in a surgeon loop
Repeat until done:
1. Hypothesis: what change should work?
2. Smallest incision: implement with minimal collateral.
3. Make it observable: add/adjust a test/assertion/log.
4. Re-check: run the tightest local signal.

Heuristics:
- Bug: reproduce if possible; otherwise characterization test/instrumentation first.
- Feature: smallest end-to-end slice users can exercise (vertical slice > scaffolding).
- Refactor: preserve behavior; add characterization test/invariant first.

### 7) Abstraction Laws (when extracting reuse)
Only use this section when you want to unify repeated shapes.

#### Quick start
1. Collect **3+** concrete instances (file:line).
2. Classify similarity: **essential** (domain) vs **accidental** (implementation).
3. Run the seam test.
4. Name the abstraction by behavior.
5. If algebraic, pick the minimal construction and add one executable law check.

#### Evidence table
```
| Instance | Location | Shared Shape | Variance Point |
|----------|----------|--------------|----------------|
| A        | file:line| ...          | ...            |
| B        | file:line| ...          | ...            |
| C        | file:line| ...          | ...            |
```

#### Essential vs accidental
- Essential: shared shape exists because of domain rules.
- Accidental: shared shape exists because of today’s implementation.
- If accidental, prefer duplication (or a smaller helper) until the domain forces convergence.

#### Seam test (yes/no)
1. Can callers use the abstraction without knowing the concrete variant?
2. Can you describe it in one sentence without naming a current implementation?
3. Would a new instance fit without adding flags or branching?

If any answer is “no”, extract a smaller helper or keep duplication.

#### Abstraction template
```
Name: <behavioral name>
Fixed parts:
- ...
Variance points:
- ...
Interface sketch:
- ...
Break-glass:
- <next likely change that makes this harmful>
```

### 8) Validate
Run at least one signal; prefer fastest-first:
- Formatter
- Lint/typecheck
- Focused tests
- Build / full suite (as appropriate)

If a category doesn’t exist, record **N/A** and run the closest substitute.

### 9) Finish (don’t skip)
- Remove debug scaffolding.
- Confirm the diff matches the promised scope.
- Make sure names and boundaries are legible.
- Record proof (signals run + outcomes).

## Deliverable format (chat)

### A) Work summary
- Contract: 1 sentence.
- Incision: what changed and why.

### B) Invariants
- Invariant(s) stated.
- How enforced: types vs tests/assertions.

### C) Universalist pass (only if triggered)
- Minimal algebra chosen.
- Laws named.
- One law check run (or **N/A** + compensating signal).

### D) Abstraction Laws (only if extracting reuse)
- Evidence table (3+ instances).
- Seam test verdict.
- Proposed abstraction + break-glass scenario.

### E) Proof
- `<cmd>` → `<ok/fail>` (list the signal(s) you ran)
- Residual risks / open questions.

## Failure paths
- Requirements unclear: stop and ask; don’t guess.
- No validation command known: ask for the preferred local signal before editing.
- Scope creep detected: revert/undo unrelated changes; suggest follow-up separately.
- Abstraction urge with <3 instances: keep duplication or extract a tiny helper only.
- Laws hard to state/test: the algebra is likely wrong—pick a smaller one or reframe.

## Activation cues
- "sp"
- "surgeon" / "surgical"
- "invariants first"
- "no scope creep"
- "this looks like that" / "extract abstraction"
- "combine/merge" / "identity" / "associativity" / "map/fold/compose"
