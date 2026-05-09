# Architecture transformation with Kan extensions and Kan lifts

## Core distinction

Use Kan extensions and Kan lifts to locate the unknown relative to a boundary.

```text
Extension: unknown is after a boundary.

C --K--> D
|        |
F        ?
v        v
E
```

```text
Lift: unknown is before a boundary.

A --?--> B
|        |
F        P
v        v
C
```

Architectural translation:

- `Lan`: freely generate target-side structure.
- `Ran`: derive target-side structure from coherent observations.
- `Lft`: synthesize an internal realization behind a fixed boundary.
- `Rft`: synthesize residual requirements/obligations behind a fixed boundary.
- `Δ_K`: restrict target semantics to the old/source side.
- `P_*`: project/check a known implementation through a fixed boundary.

## Boundary inventory

Before refactoring, list boundaries by type.

| Boundary | Typical functor | Unknown usually wants |
|---|---|---|
| old API into new API | `K : Old -> New` | `Lan`, `Ran`, or `Δ` |
| core AST into extended AST | `K : Core -> Extended` | `Lan` for generated semantics |
| new service projected to legacy clients | `K : LegacyViews -> NewModel` | `Ran` for coherent facade |
| internal service to public API | `P : Internal -> Public` | `Lft` for realization, `Rft` for obligations |
| database to public view | `P : SourceDB -> View` | lift for view updates or reverse migrations |
| implementation to traces | `P : Impl -> Trace` | lift for trace-driven synthesis or residual tests |
| effectful program to handler result | `P : Program -> Runtime` | lift for inverse handler design |
| known implementation to public behavior | `P_*` | direct postcomposition/checking |

## Architecture-change playbook

1. **Name the pressure.** What is causing architectural drift: duplicated adapters, invalid generated code, inconsistent old clients, impossible reverse mapping, tests that do not map to implementation obligations?
2. **Place the unknown.** Is the missing artifact on the target side of an embedding, or inside an implementation side before a projection?
3. **Choose the universal side.** Use `Lan`/`Ran` for extension; use `Lft`/`Rft` for lift.
4. **Pick one witness.** One endpoint, AST node, schema table, event, query, policy, or workflow step.
5. **Write the comparison map.** Unit/counit for extensions; unit/counit-like comparison for lifts.
6. **Centralize the boundary.** Put `K`, `P`, units, counits, projections, and residual checks in named modules.
7. **Generate or synthesize through the boundary.** Do not allow ad hoc bypasses.
8. **Add law tests before bulk migration.** Naturality, factorization, realization, or residual soundness.
9. **Refactor by slices.** Expand only after the witness slice passes.
10. **Document the unsafe analogy.** Mark which parts are mathematical, programming, architecture inference, and repo observation.

## Repository layout

A lift-aware and extension-aware repo can be organized like this:

```text
core/              C, old syntax, old schema, old semantics F
extended/          D, new syntax, new schema, new surface
boundaries/        K embeddings, P projections, adapters, handlers
extensions/        Lan/Ran implementations, generated artifacts, facades
lifts/             Lft/Rft implementations, residual solvers, obligations
interpreters/      concrete target semantics and runtime handlers
laws/              naturality, factorization, realization, residual tests
witnesses/         smallest examples proving the boundary design works
migrations/        rollout scripts and compatibility checks
```

This layout is an architecture inference, not a theorem. Its purpose is to stop universal-property code from dissolving into arbitrary glue.

## Patterns

### Pattern: plugin API as `Lan`

Use when extending a core DSL/AST/interpreter into a plugin surface.

- `C`: core operations.
- `D`: plugin operations.
- `K : C -> D`: inclusion.
- `F : C -> E`: existing interpreter or serializer.
- Candidate: `Lan_K F`.
- Law: old nodes embedded through `K` behave the same through generated plugin semantics.

### Pattern: compatibility facade as `Ran`

Use when a new model must satisfy several old clients.

- `C`: legacy observations.
- `D`: new model/service category.
- `K`: maps each old observation into the new boundary.
- `F`: legacy observable behavior.
- Candidate: `Ran_K F`.
- Law: old-client projections commute on overlapping observations.

### Pattern: public contract to implementation as `Lft`

Use when a desired public behavior must be implemented behind a fixed public projection.

- `A`: endpoint/feature specs.
- `B`: internal implementation designs.
- `C`: public observable behavior.
- `P : B -> C`: public projection of internal implementation.
- `F : A -> C`: desired API contract.
- Candidate: `Lft_P F`.
- Law: `F -> P · Lft_P F` witness for each endpoint.

### Pattern: tests to obligations as `Rft`

Use when tests/specs should derive constraints on implementation options.

- `A`: tests/spec cases.
- `B`: implementation obligations/capabilities.
- `C`: observable behavior.
- `P : B -> C`: behavior exposed by obligations.
- `F : A -> C`: accepted/required behavior.
- Candidate: `Rft_P F`.
- Law: `P · Rft_P F -> F` soundness witness for each test slice.

### Pattern: view update as lift

Use when a target view update must be realized by a source update.

- `B`: source/internal database state.
- `C`: view/public schema state.
- `P : B -> C`: view projection.
- `F : A -> C`: desired view mutation.
- Candidate: `Lft` when the update must be realized; `Rft` when deriving safe approximations/obligations.

### Pattern: observability-driven architecture

Use when traces/logs/metrics define the observable contract.

- `B`: implementation traces available through instrumentation.
- `C`: public observability semantics.
- `P : B -> C`: observability projection.
- `F : A -> C`: required trace contract.
- Candidate: lift through `P`.
- Law: every synthesized implementation slice projects to accepted traces, or every residual obligation is sound.

## Yoneda/Coyoneda representation layer

After the boundary has been classified, use Yoneda/Coyoneda to normalize the local representation of values crossing that boundary.

| Refactor pressure | Local pass | Boundary artifact | Interpreter/law |
|---|---|---|---|
| old clients observe new model | Yoneda | `Observation` cases | `runObservation`, projection coherence |
| public contract defines visible behavior | Yoneda | `PublicObservation` | observed projection equals required observation |
| core payload generates target artifact | Coyoneda | `Generated` plus `Path` | `lower`, identity/fusion/unit law |
| internal candidate realizes public behavior | Coyoneda | `CandidateRealizer` plus `ProjectionPath` | `projectImplementation`, lift realization law |
| observers or paths need auditability | Defunctionalized Yoneda/Coyoneda | constructors plus payloads | semantic preservation plus selected Kan law |

Practical rule:

```text
Ran/Rft/P_* boundaries tend to expose Yoneda pressure.
Lan/Lft boundaries tend to expose Coyoneda pressure.
Kan lifts often need both: observations on C, realizers/paths on B.
```

Use this layer only if it changes code shape: centralizes observers, defers transformations, preserves provenance, enables map/path fusion, or creates law-testable boundary data.

## Defunctionalization layer

After choosing `Lan`, `Ran`, `Δ`, `Lft`, or `Rft`, look for hidden functions at the boundary. Architecture-changing Kan work often becomes practical only after those functions are defunctionalized.

| Refactor pressure | Hidden function | Boundary IR | Interpreter/projector |
|---|---|---|---|
| plugin defaults drift | `Core -> Plugin` callback | `PathToPlugin` | `interpretPath` |
| old queries drift | `NewModel -> LegacyResult` callback | `Observation` | `runObservation` |
| bind-heavy continuation layer | continuation callback | `Frame`/`Kont` | `applyFrame` |
| public contract lacks internal shape | `Spec -> Implementation` builder | `ImplementationPlan` | `projectImplementation` |
| tests do not constrain architecture | `Implementation -> Bool` predicate | `Obligation` | `satisfyObligation` |

Defunctionalization should create a new module only when it centralizes a real architecture boundary. A good module exposes constructors, one interpreter/projector, and law tests. A bad module exposes a large enum that merely mirrors arbitrary implementation detail.

Prompt shape:

```text
Use $kan. After choosing extension vs lift, run a defunctionalization pass.
Identify boundary functions, replace them with first-order cases, name the interpreter,
and give one law test showing the interpreter factors through the chosen boundary.
```

## Agent workflow

For agent-assisted architecture work, ask the agent to produce:

1. the boundary map (`K` or `P`);
2. the candidate universal construction;
3. one witness slice;
4. a small executable law test;
5. a patch plan;
6. a rollback plan;
7. a claim ledger that separates theorem, programming encoding, and architecture inference.

Good prompt shape:

```text
Use $kan. Treat this as an architecture transformation.
Find the boundary, decide extension vs lift, produce one witness slice,
and give me the first law test before proposing the full refactor.
```

## Failure modes prevented

- ad hoc glue paths that bypass the canonical adapter;
- plugin APIs that reimplement core semantics inconsistently;
- read models that satisfy one old query while breaking another;
- public contracts with no derivation to internal obligations;
- tests that validate behavior but do not constrain architecture;
- view updates whose source-side effects are guessed by convention;
- generated clients or migrations with no compatibility witness.

## Outside-in lift refactor pattern

Use this when a mature system must change internally while keeping externally visible behavior stable.

Data:

- `A`: public commitments, contract cases, golden tests, reports, policies, or user stories.
- `B`: internal architecture choices: domain model, service graph, workflow engine, storage model, handlers, resources.
- `C`: observable behavior: responses, traces, views, rendered output, policy results.
- `P : B -> C`: projection from internals to public behavior.
- `F : A -> C`: required behavior.

Process:

1. Treat every external commitment as input, not as after-the-fact validation.
2. Centralize `P` before moving modules.
3. Derive an obligation ledger before implementation.
4. Choose exact, covering, sound, approximate, or no-exact-lift classification per witness.
5. Refactor one witness slice through `P`.
6. Generalize only after all bypass paths are removed.

This is the architecture-preimage problem: find a good internal object whose projection is the public behavior already owed.

## No-exact-lift pattern

When no candidate internal design can project to the required behavior, do not force a fake lift.

Emit:

```text
No exact lift for witness a.
Required observation:
Current P can produce:
Missing internal artifact:
Repair options:
Witness test:
```

Repair options:

- enrich `B` with missing data, transition, resource, or capability;
- change `P` so existing internal information becomes observable;
- weaken or negotiate `F`;
- add an external dependency;
- accept an approximate lift with documented residual risk.

## Contract-first prompt

```text
Use $kan.
Treat this as an outside-in Kan lift refactor.
A = public contract/golden-test cases.
B = internal architecture choices.
C = observable behavior.
P = projection from internals to public behavior.
F = required public behavior.

First derive the obligation ledger and no-exact-lift obstructions.
Then implement one witness slice only, with projection tests before module movement.
```
