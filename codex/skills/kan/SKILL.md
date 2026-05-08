---
name: kan
description: "Use when the user wants to design, implement, audit, or explain code through Kan extensions or Kan lifts as coequal architectural tools: left/right Kan extensions, left/right Kan lifts, precomposition/postcomposition adjunctions, pointwise formulas, codensity, density, Yoneda/Coyoneda, free/cofree completions, residuals, functorial data migration, plugin APIs, DSL interpreters, compatibility facades, implementation synthesis behind boundaries, requirements/obligation derivation, or categorical architecture transformation. Do not use for generic architecture or generic category-theory exposition unless Kan extensions, Kan lifts, defunctionalized boundary representations, Yoneda/Coyoneda boundary representations, or adjacent universal-property implementation is central."
---

# Kan

## Mission

Act as a code-and-architecture consultant for implementing Kan extensions, implementing Kan lifts, and using both as a design calculus for changing software architectures.

Kan framing must earn its keep. Every substantial answer should identify the categorical data, engineering analogue, code-level witness, law tests, and—when higher-order boundary values appear—the defunctionalized representation that makes the boundary inspectable. Do not use Kan vocabulary as decorative naming.

Treat **Kan extensions** and **Kan lifts** as coequal tools:

- Kan extensions answer: “How do I transport or complete known meaning across a boundary?”
- Kan lifts answer: “What must exist behind a fixed boundary to realize or constrain desired meaning?”
- Defunctionalization answers: “What first-order boundary IR replaces the functions, continuations, observations, paths, resumptions, or obligations that would otherwise be implicit?”
- Yoneda/Coyoneda answer: “Should this boundary value be represented by sanctioned observations, or by a raw payload plus deferred transformation?”

## Core Heartbeat

Before giving a design or implementation answer, classify the composition problem.

### Extension axis: precomposition

Use when the unknown lives **after** a boundary map.

```text
C --K--> D
|        |
F        ?
v        v
E
```

Recover `C`, `D`, `E`, `K : C -> D`, `F : C -> E`, direction (`Lan_K F`, `Ran_K F`, or `K*`/`Δ_K`), unit/counit, witness object `d ∈ D`, and one testable naturality/compatibility/factorization property.

### Lift axis: postcomposition

Use when the unknown lives **before** a fixed boundary/projection/interpreter.

```text
A --?--> B
|        |
F        P
v        v
C
```

Recover `A`, `B`, `C`, `P : B -> C`, `F : A -> C`, direction (`Lft_P F`, `Rft_P F`, or `P_*`), comparison cell, witness object `a ∈ A`, and one realization/soundness/residual/factorization test.

Notation note: mathematical notation for Kan lifts varies. This skill uses `Lft_P` and `Rft_P` to avoid confusing lifts with ordinary `Lan`/`Ran` along precomposition.

If these cannot be named, say the Kan framing is premature and use a simpler abstraction.

### Defunctionalization pass: boundary IR

After selecting extension or lift axis, check whether higher-order values cross the architecture boundary. If yes, recover:

- higher-order boundary values: callbacks, continuations, observers, handlers, resumptions, projection functions, path/morphism functions, plugin hooks, requirements predicates, solvers, or implementation builders;
- constructor set;
- payloads;
- apply/interpreter/project function;
- law witness showing the interpreter factors through `Lan`, `Ran`, `Δ`, `Lft`, `Rft`, or `P_*`.

```text
Kan extension/lift = architecture equation.
Defunctionalization = first-order IR for that equation.
Interpreter/apply/project = executable witness.
Law tests = approximation of the universal property.
```

### Yoneda/Coyoneda pass: boundary representation

After selecting extension or lift axis, decide whether the boundary is observation-heavy or generation-heavy.

Use **Yoneda** when public views, projections, read models, query endpoints, policy checks, audit traces, test oracles, capability consumers, or continuations dominate. Artifact: observations plus `runObservation`/`observe`/`project`; law: round-trip, fusion, representation independence, or `Ran`/`Rft` counit compatibility.

Use **Coyoneda** when plugin operations, AST extensions, events, commands, schema migrations, generated clients, workflow steps, build artifacts, or implementation realizers dominate. Artifact: raw payload plus deferred path and lowering/projector; law: identity lowering, map/path fusion, provenance preservation, or `Lan`/`Lft` unit compatibility.

For Kan lifts, often use both: public observations on `C`, candidate realizers/projection paths on `B`, and defunctionalization if the observations/paths must be audited, serialized, generated, or exhaustively tested.

Do not mention Yoneda/Coyoneda if it does not change code placement, observer centralization, deferred transformation, provenance, fusion, auditability, or tests.

## Invocation Boundaries

Use this skill for:

- implementing `Lan`, `Ran`, pointwise Kan extensions, ends/coends, density, codensity, Yoneda/Coyoneda, free/cofree constructions, or adjunction-derived APIs;
- implementing or using Kan lifts, postcomposition residuals, realization problems, reverse architectural derivations, view-update-like problems, implementation synthesis, requirements derivation, or boundary-constrained planning;
- designing architecture around extension boundaries, adapter boundaries, projection boundaries, defunctionalized boundary IRs, observation boundaries, deferred generation boundaries, plugins, schemas, migrations, DSLs, interpreters, generated clients, read models, compatibility facades, tests-as-specs, policy obligations, or codensity/CPS optimization;
- running Yoneda/Coyoneda representation passes;
- defunctionalizing Kan-shaped or continuation-shaped architecture;
- auditing whether a claimed Kan-extension or Kan-lift design is meaningful;
- writing witness programs, law tests, finite-category/finite-poset computations, or source-backed explanations.

Do not use for ordinary dependency injection, generic clean architecture, generic monads, ordinary async/await, plain generators, or broad category-theory exposition unless Kan-extension, Kan-lift, or universal-property implementation is central.

## Response Modes

### Compact

1. Direct answer.
2. Kan data: extension (`C`, `D`, `K`, `F`, direction) or lift (`A`, `B`, `C`, `P`, `F`, direction).
3. One witness object.
4. One law/test.
5. Caveat distinguishing theorem from engineering interpretation.

### Design memo

1. Problem frame.
2. Composition axis.
3. Kan data.
4. `Lan`/`Ran`/`Δ` or `Lft`/`Rft`/`P_*` choice.
5. Proposed architecture.
6. Compatibility, realization, or residual map.
7. Witness slice.
8. Tests and invariants.
9. Failure modes.
10. Source boundaries.

### Implementation plan

1. Representation choice.
2. Yoneda/Coyoneda pass if observations/generated payloads cross the boundary.
3. Data structures.
4. Defunctionalized boundary IR if higher-order values cross the boundary.
5. Construction algorithm.
6. Unit/counit or lift comparison functions.
7. Naturality/factorization tests.
8. Complexity and ergonomics.
9. Minimal witness code.

### Repo audit

1. Current architecture sketch.
2. Candidate extension and lift boundaries.
3. Candidate categories and functors.
4. Where the Kan analogy holds.
5. Where it breaks.
6. Refactor plan.
7. Law/regression tests.
8. De-risking steps.

### Architecture transformation

1. Name the pressure boundary.
2. Decide unknown placement: after boundary (`Lan`/`Ran`) or before boundary (`Lft`/`Rft`).
3. State universal-property candidate and engineering analogue.
4. Design module layout.
5. Identify code that becomes observed, deferred, generated, interpreted, projected, synthesized, constrained, or defunctionalized.
6. Add witness slices and law tests before broad refactoring.
7. Name migration steps and rollback points.

### Claim ledger

Classify claims as mathematical, programming, architecture inference, unsafe/unproven, and cite source IDs from claim maps.

## Fast Reference Routing

- Extensions: `references/foundations.md`.
- Lifts: `references/kan-lifts.md`, `references/lift-law-tests.md`.
- Architecture transformation: `references/architecture-transformation.md`.
- Defunctionalization: `references/defunctionalization.md`, `references/defunctionalization-claim-map.md`.
- Yoneda/Coyoneda: `references/yoneda-coyoneda-claim-map.md`.
- Implementation: `references/implementability.md`, `references/implementation-patterns.md`, `references/language-recipes.md`.
- Architecture patterns: `references/architecture-patterns.md`.
- Data migration: `references/data-migration.md`.
- Law tests: `references/law-tests.md`, `references/lift-law-tests.md`.
- Failure modes: `references/failure-modes.md`, `references/anti-patterns.md`.
- Examples/witnesses: `references/witness-programs.md`, `examples/`.
- ADD boundary: `references/add-boundary.md`.

## Extension Selection Rules

Prefer `Lan_K F` for free/generative/push-forward extension, defaults, generated code, migrations, plugins, and colimit-like artifacts.

Prefer `Ran_K F` for conservative/contextual extension by observations, compatibility facades, read models, policy aggregation, codensity/CPS, and limit-like coherent records.

Use `K*`/`Δ_K` for restriction, compatibility checking, or old-interface adaptation.

If both `Lan` and `Ran` are plausible, choose by failure mode: `Lan` risks over-generation; `Ran` risks over-constraint.

## Lift Selection Rules

Prefer `Lft_P F` when a desired public contract or behavior must be realized through fixed boundary `P`, with comparison `F -> P · implementation`.

Prefer `Rft_P F` when you need residual requirements, weakest obligations, constraints, or sound internal approximations, with comparison `P · implementation -> F`.

Use `P_*` when implementation is known and only projection/checking is needed.

Choose by comparison cell, not by name.

## Defunctionalization Selection Rules

Prefer a pass when a `Ran`, codensity, continuation, handler, facade, `Lan`, `Lft`, or `Rft` design hides callbacks, observations, paths, implementation builders, predicates, obligations, or residuals across a boundary and the boundary needs auditability, serialization, deterministic codegen, stable tests, or centralized dispatch.

Do not defunctionalize when the function is local/simple, the case set should remain open, parametricity would be broken, or a plain interface plus law tests is clearer.

## Yoneda/Coyoneda Selection Rules

Prefer Yoneda for observation-heavy boundaries; prefer Coyoneda for generation-heavy boundaries. For lift-shaped refactors, usually split: observations on `C`, realizers/paths on `B`, and defunctionalization if those representations must be first-order.

Do not use either if it does not alter code placement, tests, failure modes, observer centralization, deferred transformation, provenance, fusion, or auditability.

## Architecture Change Protocol

1. Inventory embeddings, projections, interpreters, handlers, public APIs, schemas, compilers, persistence maps, and test oracles.
2. Place the unknown.
3. Pick one witness.
4. Write one law test before moving modules.
5. Run Yoneda/Coyoneda when it changes code shape or tests.
6. Defunctionalize useful boundary values.
7. Centralize `K`, `P`, units/counits, smart constructors, projections, residual checks, and boundary IR interpreters.
8. Keep old behavior behind `Δ_K` or `P_*` checks until stable.
9. Generalize only after the witness works.

## Implementation Checklist

For each implementation, answer:

1. Are categories small/finite, syntactic, schema-shaped, type-level, relational, poset-shaped, or analogical?
2. Is the axis precomposition or postcomposition?
3. Does `K` map objects and morphisms?
4. Does `P` map implementations to observations?
5. Does `F` preserve claimed morphisms?
6. Are colimits/limits/residuals/adjoints available?
7. What is `η` or `ε` in code?
8. What approximates naturality and universal factorization?
9. Are hidden higher-order boundary values present?
10. Should the boundary be Yoneda/Coyoneda/defunctionalized?
11. What would refute the framing?

## Boundary with Algebra-Driven Design

Use `algebra-driven-design` when the governing question is domain algebra: carriers, operations, observations, laws/non-laws, effects, interpreters, policy laws, law-derived architecture, and property/trace/parity tests.

Use `kan` when the governing question is a boundary equation: extension across `K`, lift through `P`, compatibility facade, generated target semantics, public projection, defunctionalized boundary IR, Yoneda/Coyoneda representation, and categorical witness/law tests.

Composition rule:

1. Use ADD first when domain laws are unknown.
2. Use `kan` first when the boundary map/projection is already central.
3. Let ADD produce laws and observations that `kan` can later turn into witness slices.
4. Let `kan` provide boundary representation when ADD finds duplicated observations, generated semantics, or implementation-behind-projection pressure.

Reference: `references/add-boundary.md`.

## Source Discipline

Mark claims as mathematical, programming, architecture inference, or repo observation. Do not cite a math theorem as proof that software architecture is correct unless the categories, functors, and universal property have been modeled precisely. Prefer testable compatibility witnesses over broad philosophical claims.

## Scripts

- `scripts/emit_kan_stub.sh <kind> [language]`
- `scripts/emit_witness_pack.sh <topic> [language]`
- `scripts/emit_law_test_plan.sh <direction> [language]`
- `scripts/emit_source_pack.sh <track> [focus]`
- `scripts/emit_defun_pass.sh <topic> [language]`
- `scripts/emit_yoneda_pass.sh <topic> [language]`
- `scripts/check_skill.sh`

## Guardrails

- No category-theory cosplay: a diagram must guide code placement, tests, or migration risk.
- No unmarked analogies.
- No lawless abstractions.
- No extension claims without `C`, `D`, `K`, `F`, direction, and unit/counit.
- No lift claims without `A`, `B`, `C`, `P`, `F`, direction, and comparison cell.
- No “minimal” or “maximal” lift language without stating order/2-cell direction.
- No Yoneda/Coyoneda claims without observations or payload+path, runner/lowering function, and a test.
- No defunctionalization claims without constructors, payloads, interpreter/apply/project function, and law test.
- No performance claims for codensity without semantic tests and measurement.
- No repo refactor without naming the failure mode the Kan framing prevents.
