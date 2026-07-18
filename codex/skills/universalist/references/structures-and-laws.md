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

Use when a boundary requires free syntax, coherent observations, transported semantics, lifted implementations, pullback witnesses, pushout integration, comonadic spatiality, indexed-description convolution, Tambara/contextual-morphism structure, explicit IR, or residual obligations. Laws depend on the artifact: preservation, coherence, agreement, factorization, projection, locality, decomposition, framing, quotient, lowering, or interpreter equivalence.

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

## Tambara module / context-stable profunctor

Use when an ambient context world acts on two endpoint worlds and a generalized transformation must remain valid under that action.

```text
(M, tensor, I)
L : M x C -> C
R : M x D -> D
P : C^op x D -> V
frame_m : P(a,b) -> P(L(m,a), R(m,b))
```

Software forms:

- one validation/observation/update capability reused under many contexts;
- generalized relations stable under environment, evidence, capability, or residual framing;
- profunctor optics;
- context-aware adapters between mixed endpoint worlds;
- contextualized specifications that may not be representable by a function.

Laws:

- unit: `frame_I(p) ~= p`;
- associativity: `frame_(m tensor n)(p) ~= frame_m(frame_n(p))`;
- endpoint naturality: `dimap(f,g,frame_m(p)) ~= frame_m(dimap(f,g,p))`;
- context reindexing/dinaturality preserves observations;
- interpretation: `interpret(frame_m(p)) == frameSemantics(m,interpret(p))`;
- framing does not grant effect commutativity, duplication, discard, or parallelism;
- effective context/residual representation stays within the resource model.

## Mixed Tambara module

Use when one ambient context world acts differently on source and target endpoint worlds:

```text
L : M x C -> C
R : M x D -> D
```

Typical software boundaries: domain/wire, read/write, logical/physical, plain/effectful reconstruction, or indexed source/target representations. Laws include both actions' coherence and the mixed interpretation law. Do not force identical endpoint types or actions merely to reuse an ordinary encoding.

## Optic / residual-context representation

Use when a boundary explicitly decomposes a whole into residual context plus focus and rebuilds the whole after updating the focus:

```text
exists m.
  decompose : s -> L(m,a)
  rebuild   : R(m,b) -> t
```

Tambara interpretation:

```text
p
  -> frame_m(p)
  -> dimap(decompose,rebuild,frame_m(p))
```

Laws:

- coherent residual reindexing is quotiented;
- interpretation agrees with direct behavior;
- hidden residual identity is unobservable;
- separate lens/prism/traversal/business laws hold;
- representation theorem claims state enrichment/parametricity hypotheses.

## Free Tambara construction

Use when a bare profunctorial capability must be closed under every legal context frame. The free construction is coend-like: generate residual/context frames, endpoint paths, and quotient coherent reindexings.

Laws:

- every supported legal frame is generated;
- equivalent context presentations normalize together;
- required provenance survives the quotient;
- generated contextual closure interprets like direct framing;
- context enumeration and normalization are effective.

## Cofree / all-context Tambara construction

Use when a capability must expose coherent behavior under every supported frame. The end-based all-context construction makes Tambara structure coalgebraic.

Laws:

- identity context returns the original capability;
- nested context observations cohere;
- all supported contexts are represented symbolically, lazily, or through an effective basis;
- missing or non-effective context coverage yields obstruction.

## Dependent Tambara module

Use when context changes indices or depends on the focused object. Model the action with a double category and horizontal naturality rather than erasing the indices.

Typical software forms: state-indexed protocols, schema-indexed fields, capability-indexed operations, dependent records, and context-sensitive syntax.

Laws:

- index transport is explicit and type-preserving;
- dependent framing composes horizontally;
- vertical/horizontal coherence holds;
- one invalid index transition is rejected;
- effective representation does not collapse into untyped dynamic tags.

## Representability / module-functor diagnostic

Tambara modules are generalized morphisms and need not be concrete functions. Use this diagnostic when the architecture requires an actual context-preserving implementation map.

Record:

- candidate module functor/realizer;
- right-adjoint/Cauchy-completeness or equivalent representability witness;
- representation and round-trip law;
- nonrepresentability obstruction.

Do not synthesize a function from a lawful relation without evidence.

## Day center and Tambara strength

Under suitable closedness or rigidity assumptions, strong Tambara modules correspond to central objects in the Day-convolution functor category.

```text
Day centrality    descriptions move coherently through convolution
Tambara strength generalized morphisms move coherently through context action
```

State the hypotheses and executable consequence. Do not claim the equivalence in arbitrary nonclosed/nonrigid settings.

## Substitution versus Day versus Tambara versus monadic composition

Distinguish:

```text
Day convolution       combine over index decompositions
operadic substitution recursively insert operations into typed slots
Tambara framing       lift a generalized morphism through context action
monadic composition   later computation structure depends on earlier results
pointwise product     combine at one unchanged index
```

Use one counterexample that distinguishes the selected construction from the nearest alternative.

## Freyd / premonoidal category

Use when pure values and effectful computations share types but order is observable. Laws: pure embedding preserves identity/composition; central operations commute; effect reordering requires observational commutativity.

## Colored operad

Use when typed components assemble hierarchically and a composite remains a component. Laws: port typing, identity wiring, associative substitution, and semantic interpretation preserving substitution.

## PROP / properad / traced structure

Use when multiple outputs or feedback are fundamental rather than conveniently bundled. Laws: network composition/feedback preserves the chosen semantic observations and resource constraints.
