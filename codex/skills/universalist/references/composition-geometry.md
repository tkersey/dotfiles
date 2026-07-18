# Composition Geometry Selector

Universal Architecture must select not only *what artifact exists*, but *how compositions are allowed to form*. Use the weakest structure that makes legal assembly and sequencing explicit.

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

Core distinction:

```text
Base composition geometry:
  how indices, resources, interfaces, or patches compose.

Description product:
  how functors, presheaves, predicates, plans, or graded families over that world compose.

Runtime semantics:
  how the resulting description executes and which effects may reorder.
```

Do not put Day convolution in the same selector row as Freyd categories or operads. Day usually lifts a selected base geometry into a functor/presheaf category. Operadic substitution and monadic composition are nearby but different products.

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
```

## Selection discipline

Do not grant symmetry, commutation, duplication, discard, feedback, parallelism, decomposition completeness, or quotient safety for free. Each is an architectural law with a witness.

A static/applicative description shape does not prove effect commutativity. Actual execution remains subject to Freyd/resource laws.

## Anti-overreach

Use a plain function/interface when it already captures the exact composition. An operad, Freyd model, or Day convolution is justified only when it changes legal wiring, sequencing, indexed composition, tests, ownership, static validation, simulation, interpretation, or the set of representable states/programs.
