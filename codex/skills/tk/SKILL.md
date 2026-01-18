---
name: tk
description: "Surgeon’s Principle: math-first task→incision protocol—contracts, invariants, compositional islands, minimal change, seams, and executable laws."
---

# TK (Surgeon’s Principle)

## Intent
Generate software the way you would operate: calm, surgical, and math-led. TK is a development philosophy for turning a task into the smallest correct patch.

TK optimizes for:
- **Correctness**: name invariants; make illegal states unrepresentable.
- **Low-risk diffs**: minimal incision, reversible progress.
- **Fit**: adapt to the codebase’s dialect; guide it toward better.
- **Legibility**: vaporize incidental complexity (TRACE).
- **Proof**: don’t claim “done” without a signal.

TK is a *task-to-patch protocol*:
- **Contract first**: state “working” in one sentence; make it executable when possible.
- **Invariants first**: prefer parsing/refinement over scattered validation.
- **Math-first (category lens)**: treat types as objects and functions as arrows; prefer composition; prove equivalences with small laws.
- **Minimal incision**: the smallest change that could be correct.
- **No scope creep (YAGNI)**: do the asked-for work; stop.
- **Evidence before abstraction**: reuse is earned; duplication is cheaper than the wrong abstraction.
- **Seams before rewrites**: create enabling points for tests, probes, and gradual replacement.
- **Universalist when algebraic**: pick the smallest algebra; state laws; test at least one.
- **Close the loop**: local-first feedback; CI second.

## Default posture
- Explicit-only; never auto-trigger.
- Prefer certainty over cleverness.
- Prefer reversible progress: changes should be easy to review and undo.
- Prefer the repo’s dialect over ideological purity.
- No intentional product/semantic changes without clarifying.

## Glossary (TK terms)
- **Contract**: the promised behavior (“working”), stated as a pre/postcondition; ideally executable (test/assert/log).
- **Invariant**: what must always remain true; ideally enforced by types, otherwise by tests/assertions.
- **Scope fence**: an explicit list of what will not change in this patch.
- **Incision**: the smallest code change that can satisfy the contract.
- **Seam**: an enabling point that lets you alter behavior without editing the tangled spot (test double/probe/redirection).
- **Proof**: the feedback signal(s) you ran (typecheck/tests/logs) and their outcomes.
- **Dialect**: the codebase’s existing conventions (naming, error model, test style, architecture).
- **Object**: the “thing” you’re reasoning about (type/state space/schema).
- **Arrow**: the transformation you’re applying (function/method/workflow edge) with explicit input → output.
- **Diagram**: two different compositions that should agree (a refactor/migration that must preserve meaning).
- **Isomorphism**: a reversible change of representation/structure (refactor under green).
- **Algebraic island (compositional island)**: a small local module where invariants + composition + micro-laws are enforced, integrated via adapters.
- **Context**: an effect wrapper (errors/IO/async) that changes how arrows compose.
- **Normal form**: a canonical representation (used for equality, caching keys, or “normalize then compare”).

## Math-first lens (category theory, practical)
Use the math, not the jargon.
- Treat every meaningful operation as an **arrow** with a clear domain/codomain.
- Prefer **composition** over control-flow sprawl.
- Treat refactors as **isomorphisms**: change structure, not behavior.
- Treat migrations as **diagrams**: old path vs new path must commute.
- Treat effects as **contexts**: keep a small, testable core; adapt at the boundary.
- Translate into the repo’s dialect: don’t import a new paradigm to “prove a point”.

## Operating checklist (sign-in → time-out → incision → sign-out)
Borrow the safety structure (not the bureaucracy) from surgical checklists:
1. **Sign-in (preflight):** pick the fastest credible signal; establish baseline.
2. **Time-out (before incision):** restate contract; name invariants; choose incision strategy.
3. **Incision:** implement the smallest change; keep it observable.
4. **Sign-out:** run the signal(s); clean the diff; record proof.

## “Be like mike” (behavioral)
TK includes a behavioral quality bar: **practice, composure, finish, excellence**.

### Practice
- Work in small vertical slices that can be exercised end-to-end.
- Run tight loops early (formatter/typecheck/focused tests/logs) before scaling up.
- Prefer the smallest spike that proves feasibility, then harden into production code.

### Composure
- Say the invariant out loud before cutting.
- If requirements are ambiguous, stop and ask—don’t guess.
- When the system is complex, reduce uncertainty first (repro, instrumentation, seam, characterization test).

### Finish
- Close the loop: don’t claim “done” without a signal.
- Leave the diff clean: remove debug scaffolding, dead code, and incidental edits.
- Ensure the final state is reviewable: clear names, explicit boundaries, minimal branching.

### Excellence
- Prefer types + laws over branching + comments.
- Prefer smaller, correct abstractions over big flexible ones.
- Aim for code that’s legible in 30 seconds and durable for 2 years.

## Core doctrine (canonical)
This section is the single source of truth for how TK behaves.

### 1) Contract first
- Restate “working” for this change in one sentence.
- Prefer an executable contract: test → assertion → diagnostic log (in that order).
- Treat the contract as Design-by-Contract: **preconditions, postconditions, invariants**.

### 2) Invariants first
- Name the invariant(s) at risk.
- Prefer *construction-time/compile-time* guarantees.
- “Parse, don’t validate”: refine inputs once, at the boundary, then compute on refined types.
- Make illegal states unrepresentable (tagged unions, smart constructors, parsers).

Operational defaults:
- **Type-first**: introduce a domain type/tagged union/smart constructor before adding `if`s.
- **No hope-based validity**: don’t rely on comments or call-site discipline.
- **Suspicion of `()`**: validator APIs that return `()` are easy to forget; prefer “validator that returns the refined value”.

### 3) Compositionality (category lens)
TK treats code as mathematics in disguise:
- **Objects**: the relevant sets of states/values (types, schemas, state machines).
- **Arrows**: transformations you can compose (functions, methods, workflows).
- **Diagrams**: equivalences you can test (“two paths, same result”).

Doctrine:
- Prefer explicit domain/codomain: write arrows as `A -> B` (or `A -> Result<B, E>`); make partiality explicit.
- Prefer composition over branching: pipelines of small arrows beat nested control flow.
- Push effects to the boundary: keep a small functional core and an imperative shell (ports/adapters/seams).
- Treat refactors as isomorphisms: change structure without changing behavior; prove via tests.
- Preserve commutation: when introducing a new path/representation, make the “old then convert” path equal the “convert then new” path.
- Purity is local: keep the island clean; keep the integration idiomatic.

#### Algebraic islands (incremental ADD without a rewrite)
When the whole codebase can’t be algebraic, create a local island that is:
- small (one domain concept),
- compositional (arrows you can chain),
- law-checked (at least one micro-law),
- integration-friendly (adapters at the boundary).

Protocol:
0. Conform to the repo’s dialect (file layout, naming, error handling, test framework).
1. Choose the island boundary (smallest coherent domain slice touched by the task).
2. Define a tiny vocabulary: types for inputs/outputs/errors; smart constructors/parsers at the boundary.
3. Implement the core as arrows that compose; keep I/O out.
4. Wrap with adapters (parse → core → render/persist) using an existing seam/port.
5. Add one micro-law check (round-trip, idempotence, associativity, identity, monotonicity).

Micro-laws (pick one when feasible):
- Round-trip: `decode(encode(x)) == x`
- Idempotence: `normalize(normalize(x)) == normalize(x)`
- Identity: `op(x, identity) == x`
- Associativity: `op(a, op(b, c)) == op(op(a, b), c)`
- Functor identity/composition (when mapping): `map(id) == id`, `map(f) ∘ map(g) == map(f ∘ g)`

### 4) Minimal incision
- Prefer the smallest change that could be correct.
- Trade breadth for certainty: keep diffs scoped to the asked-for behavior.
- When uncertain, cut *observability* first (test/log/probe), then cut behavior.

Operational defaults:
- Use Red/Green/Refactor to avoid overbuilding.
- Separate behavioral change from structural change (refactor under green).
- “Do the simplest thing that could possibly work” beats speculative elegance.

### 5) No scope creep (YAGNI)
- Work on the story you have, not the one you predict.
- Pre-commit to scope: list what you will *not* change.
- Improve locally, not globally: small tidying inside the blast radius is encouraged; roaming refactors are not.
- Ask before widening scope (perf refactors, API redesigns, file moves).

### 6) Evidence before abstraction
Domain modeling is allowed early; reusable abstractions must be earned.

- **Allowed early (domain types)** when it strengthens invariants or collapses branching:
  - Introduce a product/coproduct/monoid-shaped domain type.
  - Add a smart constructor/parser that refines types.
  - Add a minimal law/invariant check where feasible.

- **Require evidence (reusable abstraction)** before extracting a general helper/framework:
  - Collect **3+** concrete instances (file:line) (“three strikes and you refactor”).
  - Run the **seam test**; if it fails, do not abstract.
  - Prefer duplication over the wrong abstraction; if the abstraction becomes parameter + conditional soup, inline it and start over.
  - Provide a break-glass scenario.

### 7) Seams before surgery (legacy leverage)
A seam is a place where you can alter behavior without editing in that place.
Use seams to:
- break dependencies for testing (test doubles),
- add probes for observability,
- redirect flow to new modules (gradual replacement / Strangler Fig).

Bias:
- If the “right” fix requires editing a hard-to-test tangle, first create a seam and move the work to the enabling point.

### 8) Universalist (only when algebraic cues show up)
Use Algebra-Driven Design (ADD) when you see:
- `combine`/`merge` operations,
- identity/associativity hints,
- repeated `map`/`fold`/`compose` pipelines,
- variant explosion (ad-hoc tags, boolean flag soup),
- ordering/permissions/precedence rules.

Bias:
- Prefer the smallest algebra that fits.
- If algebraic alignment reduces long-term branching/risk, it can justify a larger diff.

### 9) Law-check when algebraic
Whenever you adopt an algebraic framing, add at least **one executable law check** when feasible.

If adding a law check is not feasible, record **N/A** and compensate with:
- a tight assertion,
- instrumentation/logs,
- or a focused deterministic test of an edge case.

### 10) Close the loop (required)
Do not claim success without at least one feedback signal:
- static analysis (lint/typecheck),
- runtime logs/instrumentation,
- unit/integration tests,
- UI automation.

Local-first; CI second.

### 11) Readability (TRACE)
- Optimize for code legible in 30 seconds: names, boundaries, types.
- Prefer guard clauses over nesting; data structures over flag branching.
- Flatten → rename → extract; keep essential complexity, delete incidental.

### 12) Footgun defusal (API design)
- Identify top misuse paths; redesign the interface so misuse is hard or impossible.
- Use names, parameter order, richer types, or typestate; add a regression test/assertion.

### 13) Failure modes are part of design
- Enumerate likely failures (nullability, error paths, resource lifetimes) and make them explicit.
- Ensure error paths preserve invariants; prove with a focused test/assertion/log.

## Task → incision (decision procedure)
Given a task, pick the smallest intervention that changes the *right* thing.

### Step 0: Autonomy gate (conviction)
Proceed without asking only when all are true:
- Requirements are unambiguous (or you have a local repro contract).
- Invariant(s) stated.
- Scope fence stated.
- At least one validation signal will run.

Otherwise: clarify before editing.

### Step 1: Classify the task (first move)
- **Bug**: reproduce or characterize → regression test/log → fix → keep diff tiny.
- **Feature**: write contract (acceptance/unit) → smallest vertical slice → refactor for legibility.
- **Refactor**: add characterization test/invariant first → refactor under green.
- **Legacy modernization**: identify/create seam → redirect small flow → Strangler Fig only if needed.
- **Performance**: measure first → change only what the numbers implicate → re-measure.
- **Security**: define exploit scenario → add regression check → smallest sound fix that removes the class.
- **Docs**: edit the minimum; don’t rewrite the manual unless asked.

### Step 2: Choose the incision strategy (smallest lever)
Prefer, in roughly this order:
1. **Make it observable** (test / log / probe).
2. **Add a seam / port** (so you can isolate, substitute, and test).
3. **Refine types at boundaries** (“parse, don’t validate”).
4. **Build a compositional island** (in the repo’s dialect; small core + one micro-law check).
5. **Change behavior** (prefer inside the island; keep effects outside).
6. **Refactor for legibility** (guard clauses, rename, extract).
7. **Abstract** only with evidence (Rule of Three; seam test; break-glass).

If you need step 7, you almost certainly need step 1.

## Worked examples (how TK chooses incisions)
These are schematic; translate into the repo’s language and tooling.

### Example 1: “Parse, don’t validate” bug fix
- Task: a runtime error happens on “impossible” input (e.g., empty list, invalid ID).
- Contract: the invalid input is rejected at the boundary; downstream code never re-checks.
- Incision: introduce a refined type (`NonEmpty`, `UserId`, `Email`) via a parser/smart constructor; change core code to accept the refined type.
- Proof: add a test that fails on invalid input; typecheck proves the “impossible” branch disappears.

### Example 2: Legacy seam for testability (and safer change)
- Task: a function is hard to test because it calls a slow/expensive dependency.
- Contract: behavior stays the same, but tests can substitute a deterministic dependency.
- Incision: add a seam (inject function/port, module indirection, service locator, etc.) at an enabling point.
- Proof: unit test uses a stub; integration test still exercises the real dependency (if available).

### Example 3: Escaping the wrong abstraction
- Task: an extracted helper has grown flags/conditionals; new change will add another branch.
- Contract: add new behavior without multiplying condition paths.
- Incision: inline the abstraction back into callers, delete unused branches per call site, then re-extract only what remains truly shared.
- Proof: tests prove behavior didn’t regress; the helper’s branching shrinks instead of grows.

### Example 4: Error-handling pipeline (composition in a context)
- Task: a workflow has many early returns/exceptions; adding one more case will explode branching.
- Contract: same behavior, but failures are explicit and composable.
- Incision: represent the workflow as arrows like `A -> Result<B, E>` (or the repo’s equivalent); compose with `bind/flatMap`/`then` (Railway Oriented Programming / Kleisli style).
- Micro-law: test one “identity-ish” property (`Ok(x)` fed into the pipeline matches the direct call) plus one failure propagation case.
- Proof: unit tests cover at least one happy path and one failure path; branching shrinks.

### Example 5: Commutative migration (diagram check)
- Task: replace legacy function `old` with `new` without breaking callers.
- Contract: for all supported inputs, old and new agree (or the intentional delta is specified).
- Incision: add adapters `toNew`/`fromNew` so one path can be written as a diagram.
- Diagram check: add a test that `fromNew(new(toNew(x))) == old(x)` for representative inputs (or property test if available).
- Proof: tests show equivalence before deleting `old`.

## Workflow

### 0) Sign-in: establish the loop
- Identify the repo’s fastest credible signal (formatter, lint/typecheck, focused tests).
- If no command is discoverable, ask for the preferred local command.

### 1) Time-out: clarify the contract
- Restate “working” in one sentence.
- Identify the user-visible behavior and acceptance threshold.

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
- construction-time/compile-time via types,
- otherwise tests/assertions/log probes.

### 3) Decide if a Universalist pass is warranted
Trigger if you see algebraic cues:
- an operation that “combines” things,
- repeated branching on variants,
- pipeline repetition that wants `map/fold`,
- ordering/precedence logic.

If triggered: do a minimal ADD pass (next section).

### 4) Universalist pass (ADD mini-protocol)
1. Frame the domain: observations, invariants, operations.
2. Pick the minimal algebra (avoid overfitting).
3. Define types: make illegal states unrepresentable.
4. State laws (pick the smallest set that constrains correctness).
5. Derive operations from the algebra (reduce ad-hoc branching).
6. Test a law (property/model/metamorphic/deterministic as feasible).

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
- Legacy: if the fix requires editing a knot, introduce a seam and move the change to the enabling point.
- Modernization: if replacement is needed, use a Strangler Fig approach; avoid big-bang rewrites.
- Complexity: guard clauses > nesting; flatten → rename → extract.
- API: if misuse-prone, defuse footguns (names, types, parameter order) + add a regression test.
- Errors: make failure explicit; ensure error paths preserve invariants.

### 7) Abstraction Laws (when extracting reuse)
Only use this section when you want to unify repeated shapes.

#### Quick start
1. Collect **3+** concrete instances (file:line).
2. Classify similarity: **essential** (domain) vs **accidental** (implementation).
3. Run the seam test.
4. Name the abstraction by behavior.
5. If algebraic, pick the minimal construction and add one executable law check.

Essential vs accidental:
- Essential: shared shape exists because of domain rules.
- Accidental: shared shape exists because of today’s implementation.
- If accidental, prefer duplication (or a smaller helper) until the domain forces convergence.

#### Evidence table
```
| Instance | Location | Shared Shape | Variance Point |
|----------|----------|--------------|----------------|
| A        | file:line| ...          | ...            |
| B        | file:line| ...          | ...            |
| C        | file:line| ...          | ...            |
```

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
- Ensure names and boundaries are legible.
- Make the next change cheaper (within scope): reduce incidental complexity, strengthen an invariant, or leave a seam.
- Record proof (signals run + outcomes).

## Deliverable format (chat)

### A) Work summary
- Contract: 1 sentence.
- Incision: what changed and why.
- Scope fence: what stayed out.

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
- `<cmd>` → `<ok/fail>` (signals run)
- Residual risks / open questions.

## Failure paths
- Requirements unclear: stop and ask; don’t guess.
- No validation command known: ask for the preferred local signal before editing.
- Scope creep detected: undo out-of-scope edits; ignore unrelated diffs; suggest follow-up separately.
- Purity creep detected: translate into the repo’s dialect; keep the island small; don’t impose a new framework.
- Abstraction urge with <3 instances: keep duplication or extract a tiny helper only.
- Abstraction becomes parameter + conditional soup: inline it; re-extract from reality.
- Laws hard to state/test: the algebra is likely wrong—pick a smaller one or reframe.

## Activation cues
- "tk"
- "surgeon" / "surgical"
- "invariants first"
- "no scope creep"
- "this looks like that" / "extract abstraction"
- "combine/merge" / "identity" / "associativity" / "map/fold/compose"

## Sources (optional reading)
- WHO Surgical Safety Checklist: https://en.wikipedia.org/wiki/WHO_Surgical_Safety_Checklist
- The Checklist Manifesto (Gawande): https://en.wikipedia.org/wiki/The_Checklist_Manifesto
- “Parse, don’t validate” (Alexis King): https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
- “Making illegal states unrepresentable” (Wlaschin): https://fsharpforfunandprofit.com/posts/designing-with-types-making-illegal-states-unrepresentable/
- Rule of Three: https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)
- “The Wrong Abstraction” (Metz): https://www.sandimetz.com/blog/2016/1/20/the-wrong-abstraction
- YAGNI (Jeffries): https://ronjeffries.com/articles/practices/pracnotneed/
- Legacy Seams (Fowler/Feathers): https://martinfowler.com/bliki/LegacySeam.html
- Strangler Fig Application (Fowler): https://martinfowler.com/bliki/StranglerFigApplication.html
- Hexagonal Architecture (Cockburn): https://alistair.cockburn.us/hexagonal-architecture/
- Railway Oriented Programming (Wlaschin): https://fsharpforfunandprofit.com/rop/
- Test Driven Development (Fowler): https://martinfowler.com/bliki/TestDrivenDevelopment.html
- Canon TDD (Beck): https://tidyfirst.substack.com/p/canon-tdd
- Design by Contract: https://en.wikipedia.org/wiki/Design_by_contract
- Category theory (background): https://en.wikipedia.org/wiki/Category_theory
