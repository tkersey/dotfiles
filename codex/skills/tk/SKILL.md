---
name: tk
description: "Surgeon's Principle: math-first task-to-incision protocol: contracts, invariants, compositional islands, minimal change, seams, executable laws."
---

# TK (Surgeon's Principle)

## Intent
Build software like surgery: calm, math-led, minimal. TK turns a task into the smallest correct patch.

TK optimizes for:
- Correctness: name invariants; make illegal states unrepresentable.
- Low-risk diffs: minimal incision, reversible progress.
- Fit: follow the repo's dialect; nudge it better.
- Legibility: remove incidental complexity (TRACE).
- Proof: no "done" without a signal.

TK is a task-to-patch protocol:
- Contract first: define "working" in one sentence; make it executable.
- Invariants first: parse/refine at boundaries, not scattered validation.
- Math-first (category lens): types as objects, functions as arrows; compose; prove with small laws.
- Minimal incision: smallest change that could be correct.
- No scope creep (YAGNI): do the asked work; stop.
- Evidence before abstraction: reuse is earned; duplication beats wrong abstraction.
- Seams before rewrites: create enabling points for tests, probes, gradual replacement.
- Universalist when algebraic: choose the smallest algebra; state laws; test at least one.
- Close the loop: local-first feedback; CI second.

## Default posture
- Explicit-only; no auto-trigger.
- Prefer certainty over cleverness.
- Prefer reversible progress: changes easy to review/undo.
- Prefer the repo's dialect over ideological purity.
- No intentional product/semantic changes without clarifying.

## Glossary (TK terms)
- Contract: promised behavior as pre/postconditions; ideally executable (test/assert/log).
- Invariant: what must always hold; enforced by types or tests/assertions.
- Scope fence: explicit list of what will not change.
- Incision: smallest change that satisfies the contract.
- Seam: enabling point to change behavior without editing the tangle (test double/probe/redirection).
- Proof: feedback signals run (typecheck/tests/logs) and outcomes.
- Dialect: repo conventions (naming, error model, tests, architecture).
- Object: thing under reasoning (type/state space/schema).
- Arrow: transformation with explicit input -> output (function/method/workflow edge).
- Diagram: two compositions that must agree (refactor/migration preserves meaning).
- Isomorphism: reversible representation/structure change (refactor under green).
- Algebraic island: small module with invariants + composition + micro-laws, integrated via adapters.
- Context: effect wrapper (errors/IO/async) that affects composition.
- Normal form: canonical representation (equality, cache keys, normalize-then-compare).

## Math-first lens (category theory, practical)
Use the math, not the jargon.
- Treat each meaningful operation as an arrow with clear domain/codomain.
- Prefer composition over control-flow sprawl.
- Treat refactors as isomorphisms: change structure, not behavior.
- Treat migrations as diagrams: old path vs new path must commute.
- Treat effects as contexts: small testable core; adapt at the boundary.
- Translate to the repo's dialect; don't import a paradigm to prove a point.

## Operating checklist (sign-in -> time-out -> incision -> sign-out)
Borrow the safety structure, not the bureaucracy:
1. Sign-in (preflight): pick the fastest credible signal; establish baseline.
2. Time-out (before incision): restate contract; name invariants; choose strategy.
3. Incision: implement the smallest change; keep it observable.
4. Sign-out: run signal(s); clean the diff; record proof.

## Be like mike (behavioral)
TK includes a behavioral bar: practice, composure, finish, excellence.

### Practice
- Work in small vertical slices you can exercise end-to-end.
- Run tight loops early (formatter/typecheck/focused tests/logs).
- Prefer the smallest spike that proves feasibility, then harden.

### Composure
- Say the invariant out loud before cutting.
- If requirements are ambiguous, stop and ask.
- When the system is complex, reduce uncertainty first (repro, instrumentation, seam, characterization test).

### Finish
- Close the loop; don't claim "done" without a signal.
- Leave the diff clean: remove debug scaffolding, dead code, incidental edits.
- Ensure the final state is reviewable: clear names, explicit boundaries, minimal branching.

### Excellence
- Prefer types + laws over branching + comments.
- Prefer smaller, correct abstractions over big flexible ones.
- Aim for code legible in 30 seconds and durable for 2 years.

## Core doctrine (canonical)
Source of truth for TK behavior.

### 1) Contract first
- Restate "working" in one sentence.
- Prefer an executable contract: test -> assertion -> diagnostic log.
- Treat the contract as Design by Contract: preconditions, postconditions, invariants.

### 2) Invariants first
- Name invariant(s) at risk.
- Prefer construction/compile-time guarantees.
- Parse, don't validate: refine inputs once at the boundary, then compute on refined types.
- Make illegal states unrepresentable (tagged unions, smart constructors, parsers).

Operational defaults:
- Type-first: introduce domain types/unions/smart constructors before adding ifs.
- No hope-based validity: don't rely on comments or caller discipline.
- Suspicion of (): validators returning () are easy to ignore; prefer ones that return the refined value.

### 3) Compositionality (category lens)
TK treats code as math in disguise:
- Objects: sets of states/values (types, schemas, state machines).
- Arrows: composable transformations (functions, methods, workflows).
- Diagrams: equivalences you can test (two paths, same result).

Doctrine:
- Make domain/codomain explicit: A -> B (or A -> Result<B, E>); make partiality explicit.
- Prefer composition over branching: pipelines of small arrows beat nested control flow.
- Push effects to the boundary: small functional core + imperative shell (ports/adapters/seams).
- Treat refactors as isomorphisms: change structure, not behavior; prove via tests.
- Preserve commutation: old->convert equals convert->new.
- Purity is local: keep the island clean; keep integration idiomatic.

#### Algebraic islands (incremental ADD without a rewrite)
When the whole codebase can't be algebraic, create a local island that is:
- small (one domain concept),
- compositional (arrows you can chain),
- law-checked (at least one micro-law),
- integration-friendly (adapters at the boundary).

Protocol:
0. Conform to the repo's dialect (layout, naming, errors, tests).
1. Choose the island boundary (smallest coherent domain slice touched).
2. Define a tiny vocabulary: input/output/error types; smart constructors/parsers at the boundary.
3. Implement the core as composable arrows; keep I/O out.
4. Wrap with adapters (parse -> core -> render/persist) via an existing seam/port.
5. Add one micro-law check (round-trip, idempotence, associativity, identity, monotonicity).

Micro-laws (pick one when feasible):
- Round-trip: decode(encode(x)) == x
- Idempotence: normalize(normalize(x)) == normalize(x)
- Identity: op(x, identity) == x
- Associativity: op(a, op(b, c)) == op(op(a, b), c)
- Functor identity/composition: map(id) == id, map(f) o map(g) == map(f o g)

### 4) Minimal incision
- Prefer the smallest change that could be correct.
- Trade breadth for certainty: keep diffs scoped to asked behavior.
- When uncertain, cut observability first (test/log/probe), then behavior.

Operational defaults:
- Use Red/Green/Refactor to avoid overbuilding.
- Separate behavioral change from structural change (refactor under green).
- Do the simplest thing that could possibly work beats speculative elegance.

### 5) No scope creep (YAGNI)
- Work on the story you have, not the one you predict.
- Pre-commit to scope: list what you will not change.
- Improve locally, not globally: tidy inside the blast radius; avoid roaming refactors.
- Ask before widening scope (perf refactors, API redesigns, file moves).

### 6) Evidence before abstraction
Domain modeling is allowed early; reusable abstractions must be earned.

Allowed early (domain types) when it strengthens invariants or collapses branching:
- Introduce a product/coproduct/monoid-shaped domain type.
- Add a smart constructor/parser that refines types.
- Add a minimal law/invariant check where feasible.

Require evidence (reusable abstraction) before extracting a general helper/framework:
- Collect 3+ concrete instances (file:line) ("three strikes and you refactor").
- Run the seam test; if it fails, do not abstract.
- Prefer duplication to the wrong abstraction; if it becomes parameter+conditional soup, inline and re-extract.
- Provide a break-glass scenario.

### 7) Seams before surgery (legacy leverage)
A seam lets you alter behavior without editing the tangle.
Use seams to:
- break dependencies for testing (test doubles),
- add probes for observability,
- redirect flow to new modules (gradual replacement / Strangler Fig).

Bias:
- If the right fix requires editing a hard-to-test tangle, create a seam first and move the work there.

### 8) Universalist (only when algebraic cues show up)
Use Algebra-Driven Design (ADD) when you see:
- combine/merge operations,
- identity/associativity hints,
- repeated map/fold/compose pipelines,
- variant explosion (ad-hoc tags, boolean flag soup),
- ordering/permissions/precedence rules.

Bias:
- Prefer the smallest algebra that fits.
- If algebraic alignment reduces long-term branching/risk, it can justify a larger diff.

### 9) Law-check when algebraic
When you adopt an algebraic framing, add at least one executable law check when feasible.

If adding a law check is not feasible, record N/A and compensate with:
- a tight assertion,
- instrumentation/logs,
- or a focused deterministic edge-case test.

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
- Flatten -> rename -> extract; keep essential complexity, delete incidental.

### 12) Footgun defusal (API design)
- Identify top misuse paths; redesign so misuse is hard or impossible.
- Use names, parameter order, richer types, or typestate; add a regression test/assertion.

### 13) Failure modes are part of design
- Enumerate likely failures (nullability, error paths, resource lifetimes) and make them explicit.
- Ensure error paths preserve invariants; prove with a focused test/assertion/log.

## Task -> incision (decision procedure)
Given a task, choose the smallest intervention that changes the right thing.

### Step 0: Autonomy gate (conviction)
Proceed without asking only when all are true:
- Requirements are unambiguous (or you have a local repro contract).
- Invariant(s) stated.
- Scope fence stated.
- At least one validation signal will run.

Otherwise: clarify before editing.

### Step 1: Classify the task (first move)
- Bug: reproduce/characterize -> regression test/log -> fix; keep diff tiny.
- Feature: write contract (acceptance/unit) -> smallest vertical slice -> refactor for legibility.
- Refactor: add characterization test/invariant first -> refactor under green.
- Legacy modernization: identify/create seam -> redirect small flow -> Strangler Fig only if needed.
- Performance: measure first -> change only what numbers implicate -> re-measure.
- Security: define exploit scenario -> add regression check -> smallest sound fix that removes the class.
- Docs: edit the minimum; don't rewrite the manual unless asked.

### Step 2: Choose the incision strategy (smallest lever)
Prefer, in roughly this order:
1. Make it observable (test/log/probe).
2. Add a seam/port (isolate, substitute, test).
3. Refine types at boundaries (parse, don't validate).
4. Build a compositional island (repo dialect; small core + one micro-law).
5. Change behavior (prefer inside the island; keep effects outside).
6. Refactor for legibility (guard clauses, rename, extract).
7. Abstract only with evidence (Rule of Three; seam test; break-glass).

If you need step 7, you almost certainly need step 1.

## Worked examples (how TK chooses incisions)
Schematic only; translate into the repo's language and tooling.

### Example 1: "Parse, don't validate" bug fix
- Task: runtime error on "impossible" input (empty list, invalid ID).
- Contract: invalid input rejected at boundary; downstream code never re-checks.
- Incision: add refined type (NonEmpty, UserId, Email) via parser/smart constructor; core code takes refined type.
- Proof: test fails on invalid input; typecheck proves the "impossible" branch disappears.

### Example 2: Legacy seam for testability (and safer change)
- Task: function is hard to test due to slow/expensive dependency.
- Contract: behavior unchanged; tests can substitute a deterministic dependency.
- Incision: add a seam (inject function/port/module indirection/service locator) at an enabling point.
- Proof: unit test uses stub; integration test still exercises real dependency (if available).

### Example 3: Escaping the wrong abstraction
- Task: extracted helper has grown flags/conditionals; new change adds another branch.
- Contract: add behavior without multiplying condition paths.
- Incision: inline helper into callers, delete unused branches per call site, then re-extract shared core.
- Proof: tests show no regression; helper branching shrinks.

### Example 4: Error-handling pipeline (composition in a context)
- Task: workflow has many early returns/exceptions; adding one more case explodes branching.
- Contract: same behavior, failures explicit and composable.
- Incision: model workflow as arrows A -> Result<B, E> (or repo equivalent); compose with bind/flatMap/then.
- Micro-law: test an identity-ish property (Ok(x) through pipeline matches direct call) plus failure propagation.
- Proof: tests cover a happy path and a failure path; branching shrinks.

### Example 5: Commutative migration (diagram check)
- Task: replace legacy function old with new without breaking callers.
- Contract: for supported inputs, old and new agree (or delta specified).
- Incision: add adapters toNew/fromNew so one path is a diagram.
- Diagram check: test fromNew(new(toNew(x))) == old(x) for reps (or property test).
- Proof: tests show equivalence before deleting old.

## Workflow

### 0) Sign-in: establish the loop
- Identify the repo's fastest credible signal (formatter, lint/typecheck, focused tests).
- If no command is discoverable, ask for the preferred local command.

### 1) Time-out: clarify the contract
- Restate "working" in one sentence.
- Identify user-visible behavior and acceptance threshold.

Stop and ask if:
- behavior is product-sensitive,
- trade-offs are undefined (perf/compat/security),
- or validation commands are unknown.

### 2) Name the invariants
Answer in plain language:
- What must remain true after the change?
- What inputs/states are illegal?
- Where is validity enforced (hope/runtime/construction/compile-time)?

Then choose the strongest feasible protection:
- construction/compile-time via types,
- otherwise tests/assertions/log probes.

### 3) Decide if a Universalist pass is warranted
Trigger on algebraic cues:
- an operation that combines things,
- repeated branching on variants,
- pipeline repetition that wants map/fold,
- ordering/precedence logic.

If triggered: do a minimal ADD pass (next section).

### 4) Universalist pass (ADD mini-protocol)
1. Frame the domain: observations, invariants, operations.
2. Pick the minimal algebra (avoid overfitting).
3. Define types: make illegal states unrepresentable.
4. State laws (smallest set that constrains correctness).
5. Derive operations from the algebra (reduce ad-hoc branching).
6. Test a law (property/model/metamorphic/deterministic as feasible).

#### Minimal-algebra decision guide
- Alternatives/variants -> coproduct (tagged union)
- Independent fields -> product (record/struct)
- Combine + identity -> monoid
- Combine, no identity -> semigroup
- Ordering/permissions -> poset/lattice
- Add+multiply structure -> semiring
- Structure-preserving map -> functor
- Effectful apply -> applicative
- Sequenced effects -> monad

#### Common law menu (pick one)
- Identity: op(x, identity) == x
- Associativity: op(a, op(b, c)) == op(op(a, b), c)
- Functor identity: map(id, x) == x
- Functor composition: map(f, map(g, x)) == map(compose(f, g), x)
- Round-trip: decode(encode(x)) == x
- Homomorphism: encode(op(a, b)) == op(encode(a), encode(b))

Testing expectation:
- Prefer property tests if the repo already supports them.
- Otherwise write minimal deterministic law checks in the existing test framework.
- Propose new dependencies only with explicit user approval.

### 5) Plan the incision
- Identify the smallest change that can satisfy the contract.
- Decide what will make the change observable (test/assertion/diagnostic log).
- Pre-commit to scope: list what you will not change.

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
- Modernization: if replacement is needed, use Strangler Fig; avoid big-bang rewrites.
- Complexity: guard clauses > nesting; flatten -> rename -> extract.
- API: if misuse-prone, defuse footguns (names, types, parameter order) + add a regression test.
- Errors: make failure explicit; ensure error paths preserve invariants.

### 7) Abstraction Laws (when extracting reuse)
Only use this section when you want to unify repeated shapes.

#### Quick start
1. Collect 3+ concrete instances (file:line).
2. Classify similarity: essential (domain) vs accidental (implementation).
3. Run the seam test.
4. Name the abstraction by behavior.
5. If algebraic, pick the minimal construction and add one executable law check.

Essential vs accidental:
- Essential: shared shape exists because of domain rules.
- Accidental: shared shape exists because of today's implementation.
- If accidental, prefer duplication (or a tiny helper) until the domain forces convergence.

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

If any answer is "no", extract a smaller helper or keep duplication.

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
- Build/full suite (as appropriate)

If a category doesn't exist, record N/A and run the closest substitute.

### 9) Finish (don't skip)
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
- One law check run (or N/A + compensating signal).

### D) Abstraction Laws (only if extracting reuse)
- Evidence table (3+ instances).
- Seam test verdict.
- Proposed abstraction + break-glass scenario.

### E) Proof
- <cmd> -> <ok/fail> (signals run)
- Residual risks / open questions.

## Failure paths
- Requirements unclear: stop and ask; don't guess.
- No validation command known: ask for the preferred local signal before editing.
- Scope creep detected: undo out-of-scope edits; ignore unrelated diffs; suggest follow-up separately.
- Purity creep detected: translate into repo dialect; keep the island small; don't impose a new framework.
- Abstraction urge with <3 instances: keep duplication or extract a tiny helper only.
- Abstraction becomes parameter+conditional soup: inline; re-extract from reality.
- Laws hard to state/test: algebra likely wrong; pick a smaller one or reframe.

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
- Parse, don't validate (Alexis King): https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
- Making illegal states unrepresentable (Wlaschin): https://fsharpforfunandprofit.com/posts/designing-with-types-making-illegal-states-unrepresentable/
- Rule of Three: https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)
- The Wrong Abstraction (Metz): https://www.sandimetz.com/blog/2016/1/20/the-wrong-abstraction
- YAGNI (Jeffries): https://ronjeffries.com/articles/practices/pracnotneed/
- Legacy Seams (Fowler/Feathers): https://martinfowler.com/bliki/LegacySeam.html
- Strangler Fig Application (Fowler): https://martinfowler.com/bliki/StranglerFigApplication.html
- Hexagonal Architecture (Cockburn): https://alistair.cockburn.us/hexagonal-architecture/
- Railway Oriented Programming (Wlaschin): https://fsharpforfunandprofit.com/rop/
- Test Driven Development (Fowler): https://martinfowler.com/bliki/TestDrivenDevelopment.html
- Canon TDD (Beck): https://tidyfirst.substack.com/p/canon-tdd
- Design by Contract: https://en.wikipedia.org/wiki/Design_by_contract
- Category theory (background): https://en.wikipedia.org/wiki/Category_theory
