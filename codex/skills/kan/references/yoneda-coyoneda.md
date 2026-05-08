# Yoneda and Coyoneda for Kan-oriented architecture

## Role in the skill

Yoneda and Coyoneda are not replacement top-level architecture choices. They are representation passes that run after the boundary has been classified as an extension, lift, restriction, or direct projection.

Use this hierarchy:

```text
Kan extensions/lifts: choose the architectural boundary equation.
Yoneda/Coyoneda: choose the local representation of observations or generated payloads at that boundary.
Defunctionalization: make those representations first-order and editable.
Law tests: check that the representation still factors through the intended boundary.
```

Engineering slogan:

```text
Yoneda makes observations first-class.
Coyoneda makes deferred generation first-class.
```

## Yoneda shape

Haskell-shaped form:

```haskell
newtype Yoneda f a = Yoneda { runYoneda :: forall b. (a -> b) -> f b }
```

Programming reading:

```text
Represent a value by how it responds uniformly to all allowed maps/observations out of it.
```

Architecture reading:

- do not leak internal representation;
- expose a sanctioned observation interface;
- delay mapping until the observation boundary;
- centralize query/projection behavior;
- make compatibility facades and read models observation-indexed.

Use a Yoneda pass when the boundary is observation-heavy:

- `Ran` compatibility facades;
- read models and query APIs;
- public contract observations in a Kan lift;
- policy checks, test oracles, audit views;
- capability consumers and continuation/codensity-like APIs.

Sources: `[KAN-MILEWSKI-YONEDA]`, `[KAN-HASKELL-YONEDA]`, `[KAN-HASKELL-KAN-EXTENSIONS]`.

## Coyoneda shape

Haskell-shaped form:

```haskell
data Coyoneda f a = forall b. Coyoneda (b -> a) (f b)
```

Programming reading:

```text
Package a raw source payload together with a deferred map into the target shape.
```

Architecture reading:

- do not interpret generated payloads too early;
- preserve provenance of the source artifact;
- turn ad hoc mapping pipelines into explicit path/morphism data;
- make non-functorial-looking APIs mappable by wrapping the raw operation and deferred map;
- lower through one interpreter when the boundary is reached.

Use a Coyoneda pass when the boundary is generation-heavy:

- `Lan` plugin APIs, AST extensions, generated clients, schema migrations;
- event envelopes and workflow steps;
- candidate internal realizers in a Kan lift;
- build artifacts and code-generation manifests;
- deferred transformations that should be optimized, audited, serialized, or tested.

Sources: `[KAN-MILEWSKI-YONEDA]`, `[KAN-HASKELL-COYONEDA]`, `[KAN-HASKELL-KAN-EXTENSIONS]`.

## Relationship to Kan extensions and lifts

### `Lan` plus Coyoneda

A pointwise left Kan extension has the engineering shape:

```text
source payload + path Kc -> d, modulo source equations
```

Coyoneda localizes that shape:

```text
raw payload + deferred map/path to target
```

If a `Lan` design proposes generated/default artifacts, run the Coyoneda pass:

1. Identify the raw source payload.
2. Identify the deferred map/path into the target artifact.
3. Decide whether that map should remain a function or be defunctionalized into a first-order `Path`.
4. Lower through one interpreter.
5. Test map fusion and old-behavior preservation through the `Lan` unit.

### `Ran` plus Yoneda

A pointwise right Kan extension has the engineering shape:

```text
coherent family of observations indexed by arrows d -> Kc
```

Yoneda localizes that shape:

```text
value represented by sanctioned observations/maps out of it
```

If a `Ran` design proposes a facade, read model, query API, or compatibility view, run the Yoneda pass:

1. Identify sanctioned observations.
2. Ensure observations are uniform and cannot inspect forbidden internals.
3. Centralize projection through a single observer runner.
4. Test observation coherence and counit compatibility.
5. Defunctionalize observations when auditability, serialization, or law tests require it.

### Kan lifts

For a lift-shaped architecture:

```text
A --?--> B
|        |
F        P
v        v
C
```

Use both passes:

- Yoneda side: model `C` as public observations, tests, traces, queries, responses, or policies.
- Coyoneda side: model candidate `B`-side realizers as source implementation payloads plus deferred projection paths through `P`.

Then defunctionalize:

```text
PublicObservation      = defunctionalized Yoneda side
CandidateRealizer      = defunctionalized Coyoneda side
projectImplementation  = interpreter for P
law test               = projectImplementation(realizer(a)) satisfies F(a)
```

## Yoneda/Coyoneda pass

Run this pass after selecting `Lan`, `Ran`, `Delta`, `Lft`, `Rft`, or `P_*`.

### Observation-heavy boundary: try Yoneda

Ask:

1. What observations are sanctioned?
2. Which modules currently duplicate these observations ad hoc?
3. Can the value be represented by how it answers those observations?
4. What uniformity/naturality law says observations are representation-independent?
5. Should observations remain functions, or should they be defunctionalized into an `Observation` type?

Implementation artifacts:

```text
Observation case type
runObservation / observe / project function
coherence validator
counterexample fixtures for inconsistent observations
```

### Generation-heavy boundary: try Coyoneda

Ask:

1. What is the raw source payload?
2. What deferred transformation maps it into the target?
3. Is the transformation composable/fusable?
4. Can the transformation be defunctionalized into a `Path`, `ProjectionPath`, or `GeneratedCase`?
5. What lowering function interprets the path at the boundary?

Implementation artifacts:

```text
Generated / Deferred case type
Path or ProjectionPath case type
lower / interpretPath function
map-fusion and provenance tests
```

### Lift boundary: use both

Ask:

1. What public observations define `F : A -> C`?
2. What candidate internal realizers could project through `P : B -> C`?
3. What deferred projection path connects each realizer to each observation?
4. What residual obligations appear when no exact realizer exists?
5. What law test checks `P(realizer(a))` against `F(a)`?

## Law tests

### Yoneda tests

- Lower/lift round trip: converting a concrete value to Yoneda and observing with identity recovers the original representation, where identity observation is available.
- Map fusion: two deferred maps observed together equal observing their composition.
- Uniform observation: observers cannot branch on hidden implementation representation.
- `Ran` counit compatibility: old projections through the Yoneda-style facade equal legacy observations.

### Coyoneda tests

- Lowering: `lower(Coyoneda id payload)` equals the original payload when the identity path is in scope.
- Map fusion: accumulating two maps and lowering equals lowering after composed map.
- Provenance: generated target artifacts retain source payload identity/path until lowering.
- `Lan` unit compatibility: lowering the identity/generated path on an old/core artifact agrees with old behavior.

### Lift tests

- Yoneda observation side: every public observation in `F(a)` is explicit and runnable.
- Coyoneda realizer side: each candidate implementation has a deferred projection path through `P`.
- Realization: for witness `a`, `projectImplementation(realizer(a), observation)` satisfies `F(a, observation)`.
- Residual: if no exact realizer exists, an explicit obligation is emitted and tested.

## Failure modes

- Yoneda cosplay: wrapping a value in an observer API while still leaking the raw representation everywhere.
- Coyoneda cosplay: storing `payload + function` without gaining provenance, fusion, deferral, or tests.
- Defunctionalization too early: replacing an open callback API with a closed enum before the extension set is known.
- Missing law: no round-trip, map-fusion, unit/counit, or realization test.
- Wrong layer: using Yoneda/Coyoneda to avoid identifying the real `K` or `P` boundary.

Use Yoneda/Coyoneda only when they change code placement, tests, or migration risk.
