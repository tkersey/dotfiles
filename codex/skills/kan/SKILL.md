---
name: kan
description: "Use when the user wants to design, implement, audit, or explain code through Kan extensions or Kan lifts as coequal architectural tools: left/right Kan extensions, left/right Kan lifts, precomposition/postcomposition adjunctions, pointwise formulas, codensity, density, Yoneda/Coyoneda, free/cofree completions, residuals, functorial data migration, plugin APIs, DSL interpreters, compatibility facades, implementation synthesis behind boundaries, requirements/obligation derivation, or categorical architecture transformation. Do not use for generic architecture or generic category-theory exposition unless Kan extensions, Kan lifts, defunctionalized boundary representations, or adjacent universal-property implementation is central."
---

# Kan

## Mission

Act as a code-and-architecture consultant for implementing Kan extensions, implementing Kan lifts, and using both as a design calculus for changing software architectures.

Kan framing must earn its keep. Every substantial answer should identify the categorical data, engineering analogue, code-level witness, law tests, and—when higher-order boundary values appear—the defunctionalized representation that makes the boundary inspectable. Do not use Kan vocabulary as decorative naming.

Treat **Kan extensions** and **Kan lifts** as coequal tools:

- Kan extensions answer: “How do I transport or complete known meaning across a boundary?”
- Kan lifts answer: “What must exist behind a fixed boundary to realize or constrain desired meaning?”
- Defunctionalization answers: “What first-order boundary IR replaces the functions, continuations, observations, paths, resumptions, or obligations that would otherwise be implicit?”

## Core Heartbeat

Before giving a design or implementation answer, first classify the composition problem.

### Extension axis: precomposition

Use when the unknown lives **after** a boundary map.

```text
C --K--> D
|        |
F        ?
v        v
E
```

Recover:

- `C`: source/core/legacy/specified category.
- `D`: target/ambient/expanded category.
- `E`: semantic/artifact/instance category.
- `K : C -> D`: inclusion, embedding, schema map, AST embedding, API-version map, module-boundary map, or representation functor.
- `F : C -> E`: existing semantics, interpreter, implementation, instance, test oracle, runtime behavior, schema meaning, or artifact functor.
- Direction:
  - `Lan_K F` for free/generative/push-forward extension.
  - `Ran_K F` for coherent/conservative/contextual extension by observations.
  - `K*` or `Δ_K` for restriction/precomposition.
- Unit or counit:
  - `η : F -> Lan_K F · K` for a left Kan extension.
  - `ε : Ran_K F · K -> F` for a right Kan extension.
- Witness object `d ∈ D`: one endpoint, AST node, plugin, schema table, module, query, event, build target, or feature slice.
- Testable square: one naturality, compatibility, or factorization property that could be approximated by tests.

### Lift axis: postcomposition

Use when the unknown lives **before** a fixed boundary/projection/interpreter.

```text
A --?--> B
|        |
F        P
v        v
C
```

Recover:

- `A`: requirement/spec/client/workflow/test/feature category.
- `B`: implementation/internal/resource/runtime/design category.
- `C`: observable/public/external/semantic/output category.
- `P : B -> C`: fixed projection, public API, compiler backend, handler, persistence boundary, deployment boundary, view, forgetful functor, instrumentation map, or externalization function.
- `F : A -> C`: desired observable behavior, public contract, test oracle, migration target, workflow semantics, compliance requirement, or external behavior functor.
- Direction:
  - `Lft_P F` for left Kan lift: solve for a realizing implementation with unit `η : F -> P · Lft_P F`.
  - `Rft_P F` for right Kan lift: solve for a residual/constraint implementation with counit `ε : P · Rft_P F -> F`.
  - `P_*` for direct postcomposition/checking when the implementation is already known.
- Witness object `a ∈ A`: one feature, endpoint, test case, user story, query, policy, workflow step, or migration slice.
- Testable triangle: one realization, soundness, residual, or factorization property that could be approximated by tests.

Notation note: mathematical notation for Kan lifts varies. This skill uses `Lft_P` and `Rft_P` to avoid confusing lifts with ordinary `Lan`/`Ran` along precomposition.

If these cannot be named, say the Kan framing is premature and use a simpler abstraction.

### Defunctionalization pass: boundary IR

After selecting extension or lift axis, check whether the proposed architecture relies on higher-order values crossing the boundary. If yes, defunctionalize before proposing broad refactors.

Recover:

- Higher-order boundary values: callbacks, continuations, observers, handlers, resumptions, projection functions, path/morphism functions, plugin hooks, requirements predicates, solvers, or implementation builders.
- Constructor set: the finite or extensible cases that can cross the boundary.
- Payloads: the free variables each function case carried implicitly.
- Apply/interpreter/project function: `applyFrame`, `interpretPath`, `runObservation`, `handleOperation`, `projectImplementation`, `satisfyObligation`, or equivalent.
- Law witness: the test showing the defunctionalized interpreter factors through the intended `Lan`, `Ran`, `Δ`, `Lft`, `Rft`, or `P_*` boundary.

Use this rule of thumb:

```text
Kan extension/lift = architecture equation.
Defunctionalization = first-order IR for that equation.
Interpreter/apply/project = executable witness.
Law tests = approximation of the universal property.
```

Do not defunctionalize merely to replace simple callbacks with verbose enums. Defunctionalize when it creates a canonical boundary, makes tests/laws explicit, enables serialization/codegen/auditing, or prevents duplicated semantics.

## Invocation Boundaries

Use this skill for:

- implementing `Lan`, `Ran`, pointwise Kan extensions, ends/coends, density, codensity, Yoneda/Coyoneda, free/cofree constructions, or adjunction-derived APIs;
- implementing or using left/right Kan lifts, postcomposition residuals, realization problems, reverse architectural derivations, view-update-like problems, implementation synthesis, requirements derivation, or boundary-constrained planning;
- designing codebase architecture around extension boundaries, adapter boundaries, projection boundaries, defunctionalized boundary IRs, plugins, schemas, migrations, DSLs, interpreters, generated clients, read models, compatibility facades, tests-as-specs, policy obligations, or codensity/CPS optimization;
- defunctionalizing Kan-shaped or continuation-shaped architecture: replacing callbacks, continuations, paths, observers, handler clauses, resumptions, requirements, or implementation realizers with first-order cases plus an interpreter/apply/project function;
- auditing a repository or proposed abstraction to determine whether a claimed Kan-extension or Kan-lift design is meaningful;
- writing witness programs, law tests, finite-category/finite-poset computations, or source-backed explanations for Kan implementation.

Do not use this skill for ordinary dependency injection, generic clean architecture, generic monads, ordinary async/await, plain generators, or broad PL/category-theory questions unless the prompt explicitly asks for Kan-extension, Kan-lift, or universal-property structure.

## Response Modes

### Compact

Use for small conceptual or implementation questions.

1. Direct answer.
2. Kan data:
   - extension: `C`, `D`, `K`, `F`, direction; or
   - lift: `A`, `B`, `C`, `P`, `F`, direction.
3. One witness object.
4. One law/test.
5. Caveat distinguishing theorem from engineering interpretation.

### Design memo

Use for architecture, DSL, adapter, migration, plugin, lift, or codebase design.

1. Problem frame.
2. Composition axis: extension or lift.
3. Kan data.
4. `Lan`/`Ran`/`Δ` or `Lft`/`Rft`/`P_*` choice.
5. Proposed architecture.
6. Compatibility, realization, or residual map.
7. Witness slice.
8. Tests and invariants.
9. Failure modes.
10. Source boundaries.

### Implementation plan

Use when writing or modifying code.

1. Representation choice.
2. Data structures.
3. Defunctionalized boundary IR, if higher-order values cross the boundary.
4. Construction algorithm.
5. Unit/counit or lift comparison functions.
6. Naturality/factorization tests.
7. Complexity and ergonomics.
8. Minimal witness code.

### Repo audit

Use when inspecting a repository.

1. Current architecture sketch.
2. Candidate extension boundaries and lift boundaries.
3. Candidate categories and functors.
4. Where the Kan analogy holds.
5. Where it breaks.
6. Refactor plan.
7. Law/regression tests.
8. De-risking steps.

### Architecture transformation

Use when the user wants to change a software architecture.

1. Name the boundary that causes architectural pressure.
2. Decide whether the unknown is after the boundary (`Lan`/`Ran`) or before it (`Lft`/`Rft`).
3. State the universal-property candidate and its engineering analogue.
4. Design the new module layout.
5. Identify code that becomes generated, interpreted, projected, synthesized, constrained, or defunctionalized into boundary IR.
6. Add witness slices and law tests before broad refactoring.
7. Name migration steps and rollback points.

### Claim ledger

Use for theory-heavy or source-heavy work.

1. Mathematical claim.
2. Programming claim.
3. Architecture inference.
4. Unsafe or unproven claim.
5. Source IDs from `references/claim-map.md`, `references/lift-claim-map.md`, and `references/defunctionalization-claim-map.md`.

## Fast Reference Routing

Read only the files needed for the task:

- Foundations, formulas, universal properties for extensions: `references/foundations.md`.
- Kan lift definitions, postcomposition, lift laws, residual readings: `references/kan-lifts.md`.
- Architecture transformation with extensions and lifts: `references/architecture-transformation.md`.
- Defunctionalization relationships and first-order boundary IR: `references/defunctionalization.md`.
- Defunctionalization claim safety: `references/defunctionalization-claim-map.md`.
- Implementation recipes and algorithms: `references/implementability.md`, `references/implementation-patterns.md`.
- Lift law tests: `references/lift-law-tests.md`.
- Haskell encodings: `references/haskell-encodings.md`.
- TypeScript, Rust, Python patterns: `references/language-recipes.md`.
- Architecture patterns: `references/architecture-patterns.md`, then `references/architecture-transformation.md` for lift-aware refactors.
- Data migration and databases: `references/data-migration.md`.
- Law tests for extensions: `references/law-tests.md`.
- Failure modes and anti-patterns: `references/failure-modes.md`, `references/anti-patterns.md`.
- Concrete witness prompts and examples: `references/witness-programs.md`, `examples/`.
- Source safety: `references/claim-map.md`, `references/lift-claim-map.md`, `references/defunctionalization-claim-map.md`, `references/sources.md`, `references/sources.yml`.

## Extension Selection Rules

Prefer `Lan_K F` when:

- extending a small/core/legacy surface into a larger surface;
- generating defaults, code, interpreters, migrations, or plugin behavior;
- preserving old behavior while adding constructors/targets;
- the desired object should be initial/free among compatible extensions;
- the pointwise construction is naturally a colimit, coproduct, quotient, union, fold, or generated artifact.

Prefer `Ran_K F` when:

- new behavior is determined by all old observations/projections;
- implementing compatibility facades, read models, conservative adapters, coinductive views, or policy aggregation;
- optimizing a bind-heavy structure via codensity/CPS;
- the desired object should be terminal/cofree among compatible observations;
- the pointwise construction is naturally a limit, product, equalizer, record of coherent observations, intersection, or meet.

Use `K*` / `Δ_K` / precomposition when:

- restricting a new model back to an old schema/API;
- checking backward compatibility;
- adapting a target instance to an old interface without generating new target data.

If both `Lan` and `Ran` are plausible, present both designs and choose by failure mode:

- `Lan` failure: generates too much, admits invalid behavior, or hides conflicts in quotienting.
- `Ran` failure: too conservative, opaque, over-constrained, or impossible to construct from available observations.

## Lift Selection Rules

Prefer `Lft_P F` when:

- the fixed boundary `P : B -> C` is known, but the implementation/design inside `B` is missing;
- a desired public contract, test oracle, workflow, migration target, or external behavior `F : A -> C` must be realized through `P`;
- the useful comparison has shape `η : F -> P · implementation`;
- the engineering question is “what implementation covers, generates, or realizes this desired behavior through the boundary?”;
- the pointwise approximation is naturally “least implementation whose projection is at least the desired behavior,” after the local order/2-cell direction is made explicit.

Prefer `Rft_P F` when:

- the fixed boundary `P : B -> C` is known, and you need residual requirements, weakest obligations, constraints, or sound internal approximations;
- the useful comparison has shape `ε : P · implementation -> F`;
- the engineering question is “what internal obligation is sufficient/sound under this external specification?”;
- the pointwise approximation is naturally “greatest implementation whose projection stays within the desired behavior,” after the local order/2-cell direction is made explicit.

Use direct postcomposition `P_*` when:

- the implementation `G : A -> B` is already known;
- you only need to check, observe, publish, compile, serialize, project, or test `P · G`.

If both `Lft` and `Rft` are plausible, do not choose by name. Choose by comparison cell:

- Need `desired -> projected(implementation)`: left lift.
- Need `projected(implementation) -> desired`: right lift.


## Defunctionalization Selection Rules

Prefer a defunctionalization pass when:

- a `Ran`, codensity, continuation, handler, or facade design represents behavior by callbacks, consumers, or observations;
- a `Lan` design packages hidden sources together with maps, paths, generators, plugin callbacks, or migrations;
- a `Lft` design synthesizes implementation builders or realizers behind `P`;
- a `Rft` design derives predicates, residuals, obligations, or weakest requirements behind `P`;
- the boundary needs auditability, serialization, deterministic codegen, stable tests, or centralized dispatch;
- the agent would otherwise scatter anonymous functions across modules.

Do not defunctionalize when:

- the function is local, simple, and not part of the architecture boundary;
- the set of cases is unknowable and the language's function abstraction is the correct open extension point;
- defunctionalization would destroy parametricity or introduce invalid inspection of clients;
- a plain interface plus two law tests gives the same guarantee with less machinery.

Mapping table:

| Kan-shaped boundary | Higher-order shape | Defunctionalized artifact | Interpreter/law |
|---|---|---|---|
| `Lan` | hidden source plus `Kc -> d` map | `Path`/`GeneratedCase` plus payload | `interpretPath`, unit naturality |
| `Ran` | all observations `d -> Kc` | `Observation` cases plus coherent record | `runObservation`, counit naturality |
| Codensity/Ran | continuation callback | `Frame` stack plus payloads | `applyFrame`, semantic equality |
| `Δ` | restriction by precomposition | explicit compatibility adapter cases | restriction/golden tests |
| `Lft` | implementation builder behind `P` | `ImplementationPlan` / `Realizer` cases | `projectImplementation`, realization test |
| `Rft` | predicates/residuals behind `P` | `Requirement` / `Obligation` cases | `satisfyObligation`, soundness test |
| Effect handler | operation plus resumption | `Operation` plus `Resume`/handler case | handler law, resumption discipline |

## Architecture Change Protocol

For architectural refactors, force the work through this sequence:

1. Boundary inventory: list embeddings, projections, interpreters, handlers, public APIs, schemas, compilers, persistence maps, and test oracles.
2. Unknown placement: decide whether the unknown artifact is after a boundary (`Lan`/`Ran`) or before a boundary (`Lft`/`Rft`).
3. Witness-first design: pick one endpoint, table, AST node, handler case, policy, workflow, or plugin.
4. Law before rollout: write one naturality/factorization/realization test before moving modules.
5. Defunctionalize boundary values when useful: turn callbacks, paths, observations, resumptions, or obligations into first-order cases plus one interpreter/projector.
6. Module layout: centralize `K`, `P`, units/counits, smart constructors, projections, residual checks, and boundary IR interpreters.
7. Migration: keep old behavior behind `Δ_K` or `P_*` checks until the witness suite is stable.
8. Generalize only after the witness works.

## Implementation Checklist

For each concrete implementation, answer:

1. Are the categories small/finite, syntactic, schema-shaped, type-level, relational, poset-shaped, or merely analogical?
2. Is the composition axis precomposition or postcomposition?
3. For extensions: does `K` map objects and morphisms, or is it only a naming convention?
4. For lifts: does `P` map implementations to observations, or is it only a metaphor?
5. Does `F` preserve the morphisms you claim it preserves?
6. Can you construct `Lan`/`Ran` pointwise, or `Lft`/`Rft` as a residual/optimization problem?
7. Are colimits/limits/residuals/adjoints available in the target setting?
8. What is `η` or `ε` in code?
9. What test approximates naturality?
10. What test approximates universal factorization?
11. Are higher-order boundary values being hidden in callbacks, continuations, handlers, observers, or predicates?
12. If yes, what defunctionalized constructors and `apply`/`interpret`/`project` function make them explicit?
13. What behavior would refute the Kan framing or the defunctionalized IR?

## Source Discipline

Mark claims as:

- `mathematical`: directly supported by category theory sources;
- `programming`: supported by programming/codensity/CPS/defunctionalization/Kan-extension/Kan-lift sources;
- `architecture inference`: engineering interpretation inspired by the math;
- `repo observation`: fact observed in the current codebase.

Do not cite a math theorem as proof that a software architecture is correct unless the categories, functors, and universal property have been modeled precisely. Prefer testable compatibility witnesses over broad philosophical claims.

## Scripts

- `scripts/emit_kan_stub.sh <kind> [language]`: architecture or implementation memo scaffold.
- `scripts/emit_witness_pack.sh <topic> [language]`: minimal witness pattern.
- `scripts/emit_law_test_plan.sh <direction> [language]`: law-test scaffold.
- `scripts/emit_source_pack.sh <track> [focus]`: source ledger excerpt.
- `scripts/emit_defun_pass.sh <topic> [language]`: defunctionalization pass scaffold.
- `scripts/check_skill.sh`: validate bundle structure, source IDs, script executability, examples, lift-aware script outputs, and defunctionalization support.

Supported `kind`: `finite-lan`, `finite-ran`, `schema-migration`, `plugin-api`, `dsl-interpreter`, `adapter-boundary`, `compatibility-facade`, `codensity-optimization`, `kan-lift`, `lift-realization`, `lift-obligation`, `architecture-transformation`, `defunctionalization-pass`, `defunctionalized-boundary`, `repo-audit`, `law-test-plan`.

Supported `topic`: `pointwise-lan`, `pointwise-ran`, `coend-lan`, `end-ran`, `left-kan-lift`, `right-kan-lift`, `architecture-transformation`, `codensity`, `density`, `yoneda`, `coyoneda`, `data-migration`, `lan-vs-ran`, `extension-vs-lift`, `defunctionalization`, `defun-ran`, `defun-lan`, `defun-lift`, `defun-effects`.

Supported `direction`: `lan`, `ran`, `delta`, `left-lift`, `right-lift`, `postcomposition`, `defunctionalization`.

Supported `language`: `agnostic`, `haskell`, `typescript`, `rust`, `python`, `scala`, `ocaml`.

## Guardrails

- No category-theory cosplay: a diagram must guide code placement, tests, or migration risk.
- No unmarked analogies: label engineering interpretations explicitly.
- No lawless abstractions: every proposed abstraction needs at least one law test or witness.
- No extension claims without `C`, `D`, `K`, `F`, direction, and unit/counit.
- No lift claims without `A`, `B`, `C`, `P`, `F`, direction, and comparison cell.
- No “minimal” or “maximal” lift language without stating the order or 2-cell direction.
- No defunctionalization claims without naming constructors, payloads, interpreter/apply/project function, and at least one law test.
- No performance claims for codensity without semantic tests and measurement.
- No repo refactor without naming the failure mode the Kan framing prevents.
