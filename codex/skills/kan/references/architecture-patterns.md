# Architecture patterns

## Pattern: plugin API as `Lan`

Problem: you have a core DSL/AST/interpreter and want third-party plugins or exporters without duplicating core semantics.

Kan data:

- `C`: core syntax/semantic operations.
- `D`: extended plugin surface.
- `K : C -> D`: inclusion of core operations into plugin operations.
- `F : C -> E`: existing interpreter, serializer, validator, or evaluator.
- Candidate: `Lan_K F`.
- Unit: old behavior embeds into the new plugin semantics.

Architecture:

- keep core semantics centralized;
- expose plugin nodes through a generated/default interpreter layer;
- force plugin authors through smart constructors or capability interfaces;
- test that all old programs behave the same after `K`.

Failure mode prevented: each exporter reimplements old semantics differently.

## Pattern: compatibility facade as `Ran`

Problem: new model/service must satisfy several old clients or read APIs.

Kan data:

- `C`: legacy observations/client views.
- `D`: new model/service category.
- `K`: maps each old observation into the new representation boundary.
- `F`: legacy observable behavior.
- Candidate: `Ran_K F`.
- Counit: projecting the new facade back to old client behavior.

Architecture:

- represent facade as a coherent record of observations;
- make old-client projections explicit;
- validate compatibility across overlapping observations;
- expose partial/inconsistent observations as typed validation failures.

Failure mode prevented: adapter satisfies one client while silently breaking another.

## Pattern: schema migration with `Σ`, `Δ`, `Π`

For a schema mapping `K : S -> T`:

- `Δ_K`: restrict target instance to source schema; use for backward compatibility checks.
- `Σ_K = Lan_K`: push source data forward, merging/quotienting where paths identify data.
- `Π_K = Ran_K`: migrate by coherent matching of all target observations; often conservative and constraint-heavy.

Use `Σ` for generative migration and `Π` for compatibility/query-style migration. Sources: `[KAN-SPIVAK-WISNESKY-FQL-2014]`, `[KAN-SCHULTZ-WISNESKY-AQL-2015]`.

## Pattern: DSL interpreter extension

Problem: add constructs to a DSL while preserving existing interpreters.

`Lan` design:

- `C`: old AST constructors.
- `D`: new AST constructors.
- `K`: inclusion.
- `F`: old interpreter family.
- `Lan_K F`: generated/default interpreter behavior for new syntax.

Tests:

```text
oldEval(expr) == newEval(K(expr))
oldPretty(expr) == newPretty(K(expr))
```

A new construct needs an explicit semantic clause or a default translation to old syntax.

## Pattern: read model as `Ran`

Problem: build a read model from an event stream or domain object such that all existing queries remain valid.

`Ran` design:

- observations are old queries;
- the read model is a coherent family of query results;
- updates are accepted only when overlapping query constraints commute.

Test overlapping projections, not just endpoint snapshots.

## Pattern: generated client as `Lan`

Problem: generate clients for a richer API from a smaller OpenAPI/protobuf/core interface.

`Lan` design:

- source operations map into target SDK operations;
- generated code is initial/default among clients respecting source semantics;
- unit tests assert old endpoint behavior is preserved by generated target calls.

## Pattern: policy aggregation as poset `Ran`

Problem: a new policy must be at least as restrictive as all applicable legacy policies.

Model policies as a poset. If order means “allows no more than,” `Ran` often computes a meet over constraints. If order means “requires at least,” check order direction carefully.

## Pattern: build graph completion as poset `Lan`

Problem: derive status of aggregate build targets from source targets.

Model target status in a join-semilattice. `Lan` computes the least aggregate status above all source statuses mapping into a target.

## Pattern: codensity boundary

Problem: interpreter/free-monad pipeline is semantically clean but slow.

- Keep the public API in direct style.
- Internally convert to codensity/CPS representation.
- Lower at the boundary.
- Test semantic equality and benchmark.

Source: `[KAN-HINZE-2012]`.

## Pattern: category-driven layering

A practical repository decomposition:

```text
core/        C and F live here
boundary/    K and unit/counit adapters live here
generated/   Lan outputs or codegen products
facade/      Ran-compatible views
laws/        naturality and factorization tests
```

This layout is an engineering interpretation, not a mathematical theorem.
