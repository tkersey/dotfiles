# Composition Geometry Selector

Universal Architecture must select not only *what artifact exists*, but *how compositions are allowed to form*. Use the weakest structure that makes legal assembly, description composition, context action, two-dimensional change compatibility, and sequencing explicit.

## Stage 1 — Base composition geometry

| Pressure | Structure | What becomes explicit |
| --- | --- | --- |
| sequential transformations | category | identities and sequential composition |
| independent context / lawful parallelism | monoidal category | side-by-side composition and interchange |
| pure values + ordered call-by-value effects | Freyd/premonoidal category | pure embedding, centrality, evaluation order |
| typed many-input one-output hierarchy | colored operad | ports, operations, substitution, nested assembly |
| genuine many-input many-output networks | PROP/properad | network composition without product bundling |
| feedback and cyclic behavior | traced monoidal / temporal wiring / coalgebra | feedback, state, traces, ongoing interaction |
| consumable or graded resources | linear/graded/resource-sensitive category | ownership, duplication, cost, capability use |

Use ordinary categories first. Add monoidal structure only when side-by-side composition is real. Use a Freyd category when effects invalidate interchange. Use an operad when wiring itself is domain syntax. Escalate to PROPs/properads only when multiple outputs matter structurally, and to traced/coalgebraic structure only when feedback is essential.

## Stage 2 — Description-product selector

Once the base/index world is known, separately decide how descriptions indexed by that world compose.

| Description pressure | Product | What becomes explicit |
| --- | --- | --- |
| combine descriptions at exactly the same index | pointwise / Hadamard | same-index pairing with no decomposition search |
| combine over every witness `a tensor b -> c` | Day convolution | canonical colimit-preserving lift of base composition |
| base composition is partial, relational, or multi-witnessed | promonoidal convolution | admissibility, provenance, and partiality of decompositions |
| recursively insert operations into typed slots | substitution / plethysm | operadic recursive assembly |
| later computation structure depends on an earlier result | endofunctor composition / monadic sequencing | value-dependent control structure |
| descriptions are not meaningfully indexed | ordinary product/coproduct/interface | avoid decorative convolution |

## Stage 3 — Context-action / contextual-morphism selector

After the context world and endpoint worlds are known, decide whether a generalized boundary capability must be stable under context extension.

| Context pressure | Structure | What becomes explicit |
| --- | --- | --- |
| one context world acts on both endpoint worlds | Tambara module | `P(a,b)` lifts coherently to `P(m act a, m act b)` |
| source and target receive different actions | generalized / mixed Tambara module | domain/wire, read/write, or pure/effect framing without forcing identical worlds |
| residual context must be explicit and composable | optic / double / residual IR | decompose, retain residual, rebuild, and quotient coherent residual presentations |
| bare capability must be closed under every legal frame | free Tambara construction | generated contextual closure |
| capability must expose coherent behavior under every frame | cofree/end-based Tambara construction | all-context observation |
| context changes indices or depends on the focus | dependent Tambara / double-category action | indexed context transport without erasing dependencies |
| generalized morphism must be an actual implementation map | representability/module-functor diagnostic | concrete realizer versus relation/specification only |
| context is only an ordinary parameter | reader/environment/adapter | avoid decorative Tambara structure |

## Stage 4 — Two-dimensional composition selector

Use this stage when two semantically different arrow families both compose and a compatibility square between them is itself architecture.

| Two-dimensional pressure | Structure | What becomes explicit |
| --- | --- | --- |
| processes compose while migrations/refinements also compose | double category | horizontal process arrows, vertical change arrows, squares, and interchange |
| one composition is associative/unital only up to coherent isomorphism | pseudo double category | explicit coherence and normalization rather than fake strict equality |
| strict maps induce generalized spans, relations, profunctors, or open-system arrows | equipment / framed bicategory | companions, conjoints, restrictions, and lawful base change |
| generalized horizontal cells are meaningful but horizontal composition is partial or unavailable | virtual double category / virtual equipment | multi-source cells and restrictions without invented composites |
| the two-dimensional calculus also has real side-by-side composition | monoidal double category | tensor compatible with both arrow directions and squares |
| only one arrow family or one isolated compatibility check matters | category / 2-category / typed adapter plus witness | avoid decorative double-category structure |

Double categories are a separate architectural axis, not a synonym for a PROP's horizontal/vertical diagram composition, a double-pushout rewrite, or a commutative square. Select them only when **process composition, change composition, square pasting, and interchange** all change the artifact or proof.

Core distinction:

```text
Base composition geometry:
  how indices, resources, interfaces, contexts, or patches compose.

Description product:
  how functors, presheaves, predicates, plans, or graded families over that world compose.

Context action / contextual morphism:
  how a generalized transformation remains valid when context is added around its endpoints.

Two-dimensional composition:
  how one arrow family of processes and another arrow family of changes compose,
  with squares certifying their compatibility and interchange making local change compositional.

Runtime semantics:
  how the resulting description executes and which effects may reorder.
```

Do not put Day convolution, Tambara modules, double categories, Freyd categories, and operads in one undifferentiated selector:

```text
Day convolution    product on indexed descriptions
Tambara module     profunctor stable under context action
double category    two arrow directions plus compatibility squares and interchange
Freyd category     ordered effectful runtime composition
operad             grammar of hierarchical component substitution
```

## Day fit diagnostic

Require:

```text
index category/world
tensor or promonoidal kernel
unit
indexed description families
target semantic category
variance
legal decompositions
coend/reindexing quotient
effective enumeration/normalization
```

Use Day convolution only when all lawful decompositions should contribute and coherent changes of intermediate presentation should not create distinct public composites. Use promonoidal convolution when composition is partial or relation-valued.

## Tambara fit diagnostic

Require:

```text
ambient context category/world M
tensor/unit or explicit partial/dependent context composition
source action L : M x C -> C
target action R : M x D -> D
underlying profunctor P : C^op x D -> V
frame operation alpha_m
unit and associativity
endpoint naturality and context coherence
interpreter/observation law
effective context/residual representation
```

Use Tambara mechanics only when the same local/generalized capability must survive several lawful context extensions. Use mixed Tambara when endpoint actions differ, dependent Tambara when indices change, and an ordinary adapter/profunctor/context parameter when no framing algebra is gained.

## Double-category fit diagnostic

Require:

```text
horizontal arrow family with identities and composition
vertical arrow family with identities and composition
distinct architectural meaning for the two families
square/cell semantics with four typed boundaries
horizontal square pasting
vertical square pasting
interchange or an explicit coherent comparison
interpreter/double-functor lowering
effective square representation, normalization, and invalidation
```

Use a pseudo double category when selected composites are canonical only up to coherent isomorphism. Use an equipment only when tight maps actually admit useful companions, conjoints, or restrictions. Use a virtual double category when loose/proarrow composition is partial or intentionally absent.

## Core law shapes

```text
Operadic substitution:
interpret(substitute(f,g1,...,gn))
  == compose(interpret(f), interpret(g1), ..., interpret(gn))

Freyd effect order:
J(id) = id
J(g . f) = J(g) . J(f)
reorder(m,n) is legal only when observe(m;n) == observe(n;m)

Day representable preservation:
represent(a) star represent(b)
  ~= represent(a tensor b)

Day interpretation:
interpret(F star G)
  == combine(interpret(F), interpret(G))

Tambara unit:
frame_I(p) ~= p

Tambara associativity:
frame_(m tensor n)(p)
  ~= frame_m(frame_n(p))

Tambara interpretation:
interpret(frame_m(p))
  == frameSemantics(m, interpret(p))

Double-category interchange:
normalize((alpha pasteH beta) pasteV (gamma pasteH delta))
  ==
normalize((alpha pasteV gamma) pasteH (beta pasteV delta))

Double-functor interpretation:
interpret preserves both arrow compositions, squares, both pasting operations,
and the declared coherence/interchange equivalence.
```

## Selection discipline

Do not grant symmetry, commutation, duplication, discard, feedback, parallelism, decomposition completeness, quotient safety, context framing, representability, square pasting, or interchange for free. Each is an architectural law with a witness.

A static/applicative description shape does not prove effect commutativity. Tambara framing does not prove effect commutativity, resource duplication, or safe parallelism. Double-category interchange does not prove that effectful operations commute; it must preserve the selected effect, authority, failure, provenance, and resource observations. Actual execution remains subject to Freyd/resource laws.

## Anti-overreach

Use a plain function/interface when it already captures the exact composition. An operad, Freyd model, Day convolution, Tambara module, or double category is justified only when it changes legal wiring, sequencing, indexed composition, context framing, process/change compatibility, tests, ownership, static validation, simulation, interpretation, migration, invalidation, or the set of representable states/programs.

Do not call a `Context<T>` wrapper, reader parameter, dependency-injection container, repeated middleware call, or ordinary optic record a Tambara module without the ambient action, profunctor, framing laws, and falsifier.

Do not call two categories and a few commuting diagrams a double category without typed horizontal and vertical arrows, squares, both square-pasting operations, interchange/coherence, and an effective lowering. Prefer a 2-category or one explicit compatibility witness when the second arrow family is not independent.
