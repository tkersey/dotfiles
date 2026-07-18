# Structures and laws

## Product

Use when independent fields must coexist. Laws: projections recover fields; constructor/projection round-trip.

## Coproduct

Use when cases are mutually exclusive. Laws: exhaustive handling; impossible states rejected.

## Refined type / equalizer

Use when repeated predicates should be centralized. Laws: valid accepted, invalid rejected, normalization idempotent.

## Pullback

Use when two values, models, contexts, or interfaces must agree through maps to a shared target.

```text
f : A -> C
g : B -> C
P = A x_C B
```

Practical laws:

- `f(projectA(p)) == g(projectB(p))`;
- mismatches are rejected at construction;
- both projections are preserved;
- every compatible alternate pair factors through the canonical witness object;
- uniqueness is approximated by one opaque constructor/normal form and no unchecked bypass.

Typical software forms: equijoins, authorization contexts, wire/domain compatibility witnesses, synchronized configuration/state, and evidence joined to required claims.

## Pushout

Use when two source worlds must be glued along an explicit overlap.

```text
i : O -> A
j : O -> B
Q = A +_O B
```

Practical laws:

- `injectA(i(o)) == injectB(j(o))`;
- only declared overlap is identified;
- non-overlap structure and provenance survive;
- conflict is surfaced or resolved by named policy;
- every compatible pair of downstream consumers factors through the integrated artifact;
- uniqueness is approximated by canonical IDs/quotients and one public integration path.

Typical software forms: schema/data integration, modular API or language extension, canonical models, and overlap-based context reconciliation.

## Pushout complement / double-pushout rewrite

Use for graph/model transformations with delete-preserve-add structure:

```text
L <- K -> R
```

The pushout complement removes `L-K` from a matched host while preserving `K`; a second pushout adds `R-K`. Laws: preserved interface unchanged, deletions/additions exact, dangling and forbidden-identification cases rejected, failed complement reported as obstruction. Prefer adhesive or adhesive-like categories when local rewrites must compose predictably.

## Exponential

Use when behavior should be supplied rather than branched. Laws: strategy/callback parity against old branch fixtures.

## Free construction / initial algebra

Use when syntax should be separated from execution. Laws: interpreters agree on fixtures; fold/interpreter totality.

## Canonical boundary artifact

Use when a boundary requires free syntax, coherent observations, transported semantics, lifted implementations, pullback witnesses, pushout integration, comonadic spatiality, indexed-description convolution, explicit IR, or residual obligations. Laws depend on the artifact: preservation, coherence, agreement, factorization, projection, locality, decomposition, quotient, lowering, or interpreter equivalence.

## Behavioral coalgebra

Use when behavior unfolds over time. Typical shape:

```text
step : State x Input -> State
observe : State -> Observation
```

Laws: trace observations, invalid-transition rejection, behavioral equivalence.

## Comonadic spatiality

Use when objects are situated in coherent local context rather than merely evolving over time.

```text
C : S -> S
epsilon : C => Id
delta : C => C . C
h : E -> C(E)
```

Software reading:

```text
C(A)       A-valued local views
epsilon    extract the center
delta      local view of local views
h          assign each element its coherent situated neighborhood
```

Laws:

- center/counit: extracting a local view returns the original value;
- neighborhood coherence: nested local views associate;
- coalgebra centeredness/coherence;
- restriction preserves germ meaning;
- labelled halos preserve target, kind, owner, capability, effect, provenance, trust, and time as required;
- locality-sensitive boundaries preserve halos continuously;
- finite/effective representation and invalidation stay within the resource model.

Do not conflate a behavioral coalgebra `X -> F(X)` with a coalgebra `E -> C(E)` for a comonad. The first describes unfolding; the second describes coherent contextual placement.

## Density comonad / spatial basis

Use when local patches generate the spatial world:

```text
P : B -> S
<P> = Lan_P P
```

A subbasis generates the candidate comonad. A basis additionally supports canonical reconstruction of all situated objects/coalgebras from basic patches.

Laws:

- patch restriction/reindexing respects germs;
- basis-density/canonical reconstruction;
- local/global identities and identifications are explicit;
- coverage without density is recorded as subbasis-only;
- unbounded/non-effective basis yields obstruction rather than overclaim.

## Continuous comonadic boundary

Use when a point/value map must also preserve locality. Laws: point map, coalgebra/context transport, cartesian/restriction compatibility, halo and label preservation, and a continuity falsifier. An ordinary comonad map is not automatically a continuous map.

## Pointwise / Hadamard description product

Use when two description families are combined only at the same index:

```text
(F pointwise G)(c) = F(c) x G(c)
```

There is no sum over decompositions. Laws: same-index pairing and interpretation; index changes are natural. Do not call this Day convolution.

## Day convolution

Use when descriptions are indexed by a monoidal world and every legal tensor decomposition should contribute:

```text
(C, tensor, I)
F,G : C -> V
F star G = Lan_tensor(F external-product G)
```

Pointwise, schematically:

```text
(F star G)(c)
  ~= coend_{a,b} C(a tensor b,c) * F(a) * G(b)
```

Software forms:

- graded/Cauchy families;
- static/applicative computation descriptions;
- weighted/formal languages;
- combinatorial species;
- operation/rule collections;
- requirement-indexed context fragments;
- product descriptions of comonadic spatial worlds.

Laws:

- representables preserve tensor: `represent(a) star represent(b) ~= represent(a tensor b)`;
- unit: `J star F ~= F ~= F star J`;
- associativity up to the declared normal form/equivalence;
- decomposition soundness and completeness;
- coend/reindexing quotient coherence;
- interpreter/lax-monoidal preservation;
- static structure does not imply runtime effect commutativity;
- decomposition, aggregation, quotient, and invalidation are effective within the resource model.

## Promonoidal convolution

Use when index composition is partial, relation-valued, nondeterministic, or multi-witnessed:

```text
Compose(a,b;c)
(F star G)(c)
  ~= coend_{a,b} Compose(a,b;c) * F(a) * G(b)
```

Software forms: separation/resource predicates, partially composable grades, capability combinations, interface/rule matches, and provenance-bearing composition.

Laws:

- every composite carries an admissibility witness;
- incompatible pairs fail closed;
- every supported legal witness contributes;
- witness provenance survives when observable;
- residual/internal-hom claims agree with the declared order;
- partiality is not hidden by sentinel values.

## Substitution versus Day versus monadic composition

Distinguish:

```text
Day convolution       combine over index decompositions
operadic substitution recursively insert operations into typed slots
monadic composition   later computation structure depends on earlier results
pointwise product     combine at one unchanged index
```

Use one counterexample that distinguishes the selected product from the nearest alternative.

## Freyd / premonoidal category

Use when pure values and effectful computations share types but order is observable. Laws: pure embedding preserves identity/composition; central operations commute; effect reordering requires observational commutativity.

## Colored operad

Use when typed components assemble hierarchically and a composite remains a component. Laws: port typing, identity wiring, associative substitution, and semantic interpretation preserving substitution.

## PROP / properad / traced structure

Use when multiple outputs or feedback are fundamental rather than conveniently bundled. Laws: network composition/feedback preserves the chosen semantic observations and resource constraints.
