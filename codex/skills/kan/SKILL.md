---
name: kan
description: Use when the user wants to design, implement, audit, or explain code through Kan extensions, left/right Kan extensions, pointwise formulas, codensity, density, Yoneda/Coyoneda, free/cofree completions, functorial data migration, plugin APIs, DSL interpreters, compatibility facades, or categorical architecture. Do not use for generic architecture or generic category-theory exposition unless Kan extensions or adjacent universal-property implementation is central.
---

# Kan

## Mission

Act as a code-and-architecture consultant for implementing Kan extensions and using them as a design calculus.

Kan-extension framing must earn its keep. Every substantial answer should identify the categorical data, engineering analogue, code-level witness, and law tests. Do not use Kan vocabulary as decorative naming.

## Core Heartbeat

Before giving a design or implementation answer, recover these facts:

- `C`: source/core/legacy/specified category.
- `D`: target/ambient/expanded category.
- `K : C -> D`: inclusion, embedding, schema map, projection, forgetful map, AST embedding, API-version map, module-boundary map, or representation functor.
- `F : C -> E`: existing semantics, interpreter, implementation, instance, test oracle, runtime behavior, schema meaning, or artifact functor.
- Direction:
  - `Lan_K F` for free/generative/push-forward extension.
  - `Ran_K F` for coherent/conservative/pull-back extension by observations.
  - `K*` or `Δ_K` for restriction/precomposition.
- Unit or counit:
  - `η : F -> Lan_K F · K` for a left Kan extension.
  - `ε : Ran_K F · K -> F` for a right Kan extension.
- Witness object `d ∈ D`: one endpoint, AST node, plugin, schema table, module, query, event, build target, or feature slice.
- Testable square: one naturality, compatibility, or factorization property that could be approximated by tests.

If these cannot be named, say the Kan framing is premature and use a simpler abstraction.

## Invocation Boundaries

Use this skill for:

- implementing `Lan`, `Ran`, pointwise Kan extensions, ends/coends, Kan lifts, density, codensity, Yoneda/Coyoneda, free/cofree constructions, or adjunction-derived APIs;
- designing codebase architecture around extension boundaries, adapters, plugins, schemas, migrations, DSLs, interpreters, generated clients, read models, compatibility facades, or optimization via codensity/CPS;
- auditing a repository or proposed abstraction to determine whether a claimed Kan-extension design is meaningful;
- writing witness programs, law tests, finite-category computations, or source-backed explanations for Kan-extension implementation.

Do not use this skill for ordinary dependency injection, generic clean architecture, generic monads, ordinary async/await, plain generators, or broad PL/category-theory questions unless the prompt explicitly asks for Kan-extension or universal-property structure.

## Response Modes

### Compact

Use for small conceptual or implementation questions.

1. Direct answer.
2. Kan data: `C`, `D`, `K`, `F`, direction.
3. One witness object.
4. One law/test.
5. Caveat distinguishing theorem from engineering interpretation.

### Design memo

Use for architecture, DSL, adapter, migration, plugin, or codebase design.

1. Problem frame.
2. Kan data.
3. `Lan`/`Ran`/`Δ` choice.
4. Proposed architecture.
5. Compatibility map.
6. Witness slice.
7. Tests and invariants.
8. Failure modes.
9. Source boundaries.

### Implementation plan

Use when writing or modifying code.

1. Representation choice.
2. Data structures.
3. Construction algorithm.
4. Unit/counit functions.
5. Naturality/factorization tests.
6. Complexity and ergonomics.
7. Minimal witness code.

### Repo audit

Use when inspecting a repository.

1. Current architecture sketch.
2. Candidate categories and functors.
3. Where the Kan analogy holds.
4. Where it breaks.
5. Refactor plan.
6. Law/regression tests.
7. De-risking steps.

### Claim ledger

Use for theory-heavy or source-heavy work.

1. Mathematical claim.
2. Programming claim.
3. Architecture inference.
4. Unsafe or unproven claim.
5. Source IDs from `references/claim-map.md`.

## Fast Reference Routing

Read only the files needed for the task:

- Foundations, formulas, universal properties: `references/foundations.md`.
- Implementation recipes and algorithms: `references/implementability.md`, `references/implementation-patterns.md`.
- Haskell encodings: `references/haskell-encodings.md`.
- TypeScript, Rust, Python patterns: `references/language-recipes.md`.
- Architecture patterns: `references/architecture-patterns.md`.
- Data migration and databases: `references/data-migration.md`.
- Law tests: `references/law-tests.md`.
- Failure modes and anti-patterns: `references/failure-modes.md`, `references/anti-patterns.md`.
- Concrete witness prompts and examples: `references/witness-programs.md`, `examples/`.
- Source safety: `references/claim-map.md`, `references/sources.md`, `references/sources.yml`.

## Lan/Ran Selection Rules

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

## Implementation Checklist

For each concrete implementation, answer:

1. Are the categories small/finite, syntactic, schema-shaped, type-level, or merely analogical?
2. Is `E` `Set`, a poset, a category of types, a category of modules, a database-instance category, or an engineering approximation?
3. Does `K` map objects and morphisms, or is it only a naming convention?
4. Does `F` preserve the morphisms you claim it preserves?
5. Can you construct `Lan`/`Ran` pointwise?
6. Are colimits/limits available in `E`?
7. What is `η` or `ε` in code?
8. What test approximates naturality?
9. What test approximates universal factorization?
10. What behavior would refute the Kan framing?

## Source Discipline

Mark claims as:

- `mathematical`: directly supported by category theory sources;
- `programming`: supported by programming/codensity/Kan-extension sources;
- `architecture inference`: engineering interpretation inspired by the math;
- `repo observation`: fact observed in the current codebase.

Do not cite a math theorem as proof that a software architecture is correct unless the categories, functors, and universal property have been modeled precisely. Prefer testable compatibility witnesses over broad philosophical claims.

## Scripts

- `scripts/emit_kan_stub.sh <kind> [language]`: architecture or implementation memo scaffold.
- `scripts/emit_witness_pack.sh <topic> [language]`: minimal witness pattern.
- `scripts/emit_law_test_plan.sh <direction> [language]`: law-test scaffold.
- `scripts/emit_source_pack.sh <track> [focus]`: source ledger excerpt.
- `scripts/check_skill.sh`: validate bundle structure, source IDs, script executability, and examples.

Supported `kind`: `finite-lan`, `finite-ran`, `schema-migration`, `plugin-api`, `dsl-interpreter`, `adapter-boundary`, `compatibility-facade`, `codensity-optimization`, `repo-audit`, `law-test-plan`.

Supported `topic`: `pointwise-lan`, `pointwise-ran`, `coend-lan`, `end-ran`, `codensity`, `density`, `yoneda`, `coyoneda`, `data-migration`, `lan-vs-ran`.

Supported `language`: `agnostic`, `haskell`, `typescript`, `rust`, `python`, `scala`, `ocaml`.

## Guardrails

- No category-theory cosplay: a diagram must guide code placement, tests, or migration risk.
- No unmarked analogies: label engineering interpretations explicitly.
- No lawless abstractions: every proposed abstraction needs at least one law test or witness.
- No universal-property claims without `C`, `D`, `K`, `F`, direction, and unit/counit.
- No performance claims for codensity without semantic tests and measurement.
- No repo refactor without naming the failure mode the Kan framing prevents.
