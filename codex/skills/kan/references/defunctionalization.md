# Defunctionalization and Kan-shaped architecture

## Core relationship

Defunctionalization is not itself a Kan extension or a Kan lift. It is the implementation move that turns Kan-shaped higher-order specifications into first-order code architecture.

```text
Kan extension/lift = universal boundary equation
CPS / higher-order encoding = boundary behavior as functions
Defunctionalization = first-order constructors plus an apply/interpreter/project function
Law tests = executable approximation of the universal property
```

Use this source discipline:

- Mathematical Kan claims come from `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`, and `[KAN-NLAB-LIFT]`.
- Defunctionalization claims come from `[KAN-REYNOLDS-1972]` and `[KAN-DANVY-NIELSEN-2001]`.
- CPS/codensity/control claims come from `[KAN-HINZE-2012]` and `[KAN-DANVY-FILINSKI-1990]`.
- Architecture claims are inferences and need witnesses.

## Why Kan work produces higher-order shapes

Many Kan constructions appear in code as higher-order or hidden-index values.

Right-Kan/codensity-like shape:

```haskell
forall r. (a -> m r) -> m r
```

Programming reading: represent a value by how all relevant consumers/contexts can use it.

Left-Kan/coend-like shape:

```haskell
exists c. (K c -> d, F c)
```

Programming reading: represent a generated target artifact by a hidden source, a path/morphism into the target, and a payload.

Lift-like shape:

```text
find G : A -> B such that P · G compares to F
```

Programming reading: represent implementation realizers or residual obligations behind a fixed projection boundary.

These shapes are semantically useful but operationally hard to audit when left as anonymous functions. Defunctionalization makes them concrete.

## Defunctionalization pass

Run this pass after choosing `Lan`, `Ran`, `Δ`, `Lft`, `Rft`, or `P_*`.

1. **Identify function values crossing the boundary.** Look for callbacks, continuations, observers, handlers, resumptions, route builders, schema projections, plugin hooks, predicates, solvers, code generators, or implementation factories.
2. **Enumerate the cases.** Each distinct function abstraction becomes a constructor or tagged case.
3. **Record payloads.** The free variables of each function become fields in the constructor.
4. **Add one interpreter.** Create `apply`, `interpret`, `project`, `run`, `handle`, `lower`, or `satisfy` as the only execution path.
5. **Centralize the boundary.** Put constructors and interpreter in a boundary module, not scattered feature code.
6. **Add laws.** The interpreter must satisfy the selected Kan witness: unit, counit, restriction, realization, or residual soundness.
7. **Preserve escape hatches deliberately.** If the boundary must remain open, keep an explicit `Custom`/`External` case with a documented loss of law coverage.

## Mapping table

| Kan-shaped boundary | Higher-order thing | Defunctionalized artifact | Interpreter | First law test |
|---|---|---|---|---|
| `Lan_K F` | `Kc -> d`, generator, plugin callback | `PathToTarget` / `GeneratedCase` | `interpretPath` | `interpretPath(id, x) == eta(x)` / old behavior preserved |
| `Ran_K F` | observation function, consumer, query callback | `Observation` / `ViewCase` | `runObservation` | projections commute through `epsilon` |
| Codensity/Ran | continuation callback | `Frame` / `Kont` | `applyFrame` | lowered CPS result equals direct result |
| `Δ_K` | restriction function | `RestrictionCase` | `restrict` | old fixtures equal restricted new behavior |
| `Lft_P F` | implementation builder/realizer | `ImplementationPlan` / `Realizer` | `projectImplementation` | `F(a)` compares to `P(plan(a))` |
| `Rft_P F` | predicate/residual/obligation callback | `Requirement` / `Obligation` | `satisfyObligation` | `P(obligation(a))` compares to `F(a)` soundly |
| Effect handler | operation plus resumption | `Operation` plus `Resume`/handler case | `handleOperation` | handler semantics plus resumption discipline |

## Extension examples

### `Lan`: generated target artifacts

Before:

```typescript
type PluginDefault = (core: CoreNode) => PluginNode;
```

After:

```typescript
type PathToPlugin =
  | { tag: "Identity" }
  | { tag: "EmbedCoreNode"; nodeKind: string }
  | { tag: "PromoteLegacyField"; from: string; to: string };

type GeneratedPluginNode = {
  source: CoreNode;
  path: PathToPlugin;
};

function interpretPath(path: PathToPlugin, source: CoreNode): PluginNode {
  switch (path.tag) {
    case "Identity": return source;
    case "EmbedCoreNode": return embedCoreNode(path.nodeKind, source);
    case "PromoteLegacyField": return promoteLegacyField(path.from, path.to, source);
  }
}
```

The law is unit preservation: old/core behavior after embedding agrees with old behavior.

### `Ran`: coherent observations

Before:

```typescript
type LegacyQuery = (model: NewModel) => LegacyResult;
```

After:

```typescript
type Observation =
  | { tag: "ById"; id: string }
  | { tag: "ByEmail"; email: string }
  | { tag: "Balance"; accountId: string };

function runObservation(model: NewModel, obs: Observation): LegacyResult {
  switch (obs.tag) {
    case "ById": return byId(model, obs.id);
    case "ByEmail": return byEmail(model, obs.email);
    case "Balance": return balance(model, obs.accountId);
  }
}
```

The law is coherence: overlapping observations agree where the legacy model required them to agree.

## Lift examples

### `Lft`: public behavior to implementation plan

Before:

```typescript
type BuildImplementation = (spec: PublicCase) => InternalService;
```

After:

```typescript
type ImplementationPlan =
  | { tag: "UseCachedReadModel"; cache: string }
  | { tag: "UseTransactionalWrite"; table: string }
  | { tag: "CallExternalCapability"; capability: string };

function projectImplementation(plan: ImplementationPlan, input: PublicCase): PublicBehavior {
  switch (plan.tag) {
    case "UseCachedReadModel": return projectCached(plan.cache, input);
    case "UseTransactionalWrite": return projectWrite(plan.table, input);
    case "CallExternalCapability": return projectCapability(plan.capability, input);
  }
}
```

The law is realization: the projected plan satisfies the desired public behavior.

### `Rft`: tests/specs to residual obligations

Before:

```typescript
type ObligationPredicate = (impl: InternalDesign) => boolean;
```

After:

```typescript
type Obligation =
  | { tag: "NeedsField"; table: string; field: string }
  | { tag: "NeedsAuditEvent"; event: string }
  | { tag: "NeedsIdempotencyKey"; scope: string };

function satisfyObligation(design: InternalDesign, obligation: Obligation): boolean {
  switch (obligation.tag) {
    case "NeedsField": return hasField(design, obligation.table, obligation.field);
    case "NeedsAuditEvent": return emits(design, obligation.event);
    case "NeedsIdempotencyKey": return hasIdempotency(design, obligation.scope);
  }
}
```

The law is soundness: satisfying the residual obligations is sufficient for the projected behavior to stay within the accepted spec slice.

## Yoneda/Coyoneda before defunctionalization

Yoneda and Coyoneda often identify which functions are worth defunctionalizing.

- Yoneda pass: observations such as `a -> b`, selectors, public queries, policy checks, or test oracles become `Observation` constructors plus `runObservation`.
- Coyoneda pass: deferred maps such as `b -> a`, migration functions, projection paths, or generated artifact transformations become `Path`/`ProjectionPath` constructors plus `lower` or `interpretPath`.

Use this practical order:

```text
1. Choose Kan extension/lift boundary.
2. Run Yoneda/Coyoneda pass to decide observation vs deferred-generation representation.
3. Defunctionalize only the observations/maps that need auditability, serialization, codegen, or exhaustive tests.
4. Tie the interpreter back to the selected unit/counit/realization/soundness law.
```

This prevents defunctionalization from becoming arbitrary enum extraction. The Yoneda/Coyoneda pass explains what the cases mean at the boundary.

## Architecture payoff

Defunctionalization changes architecture when it creates one of these durable modules:

```text
boundaries/paths.*          # Lan/coend path IR
boundaries/observations.*   # Ran/end observation IR
boundaries/frames.*         # codensity/continuation IR
boundaries/restrictions.*   # Delta compatibility IR
lifts/plans.*               # left-lift realizer IR
lifts/obligations.*         # right-lift residual IR
interpreters/apply.*        # one interpreter/projector per IR
laws/*                      # law and regression tests
```

The point is not replacing every function. The point is making architectural meanings explicit enough that agents, reviewers, and tests can reason about them.

## Failure modes

- **Cosmetic enum extraction.** Constructors are introduced but no law or interpreter centralizes semantics.
- **Lost openness.** A callback extension point was intentionally open; defunctionalization closes it without a `Custom` escape hatch.
- **Invalid inspection.** Defunctionalized cases let code branch on contexts that were supposed to remain parametric.
- **Duplicated interpreters.** Multiple `apply` functions appear and drift semantically.
- **No quotient/coherence handling.** `Lan` paths or `Ran` observations are explicit but their equations are not tested.
- **Unstable constructor set.** The boundary changes faster than the case language, creating churn.

## Good answer shape

A defunctionalization-enriched Kan answer should say:

```text
Boundary: K or P
Construction: Lan/Ran/Delta/Lft/Rft/P_*
Higher-order boundary values: ...
Defunctionalized cases: ...
Payloads: ...
Interpreter/projector: ...
Law test: ...
Refutation: ...
```
