# Universal Architecture Ecosystem

Universal architecture is the practice of designing software around canonical boundary artifacts, lawful composition of indexed descriptions, and effective spatial structure when locality is semantic:

```text
free syntax
coherent observations
transported semantics
lifted implementations
free builders behind projections
obstruction reports
behavioral coalgebras
effect signatures with handlers
Freyd/premonoidal effect geometry
operadic composition grammars
pointwise, Day, and promonoidal description products
comonadic spaces, density bases, halos, germs, and continuous boundaries
explicit IRs
law tests
```

This extends the ordinary `universalist` construction ladder. Products, coproducts, refined types, pullbacks, exponentials, free constructions, labelled graphs, plain context objects, and pointwise products remain the first choices. Escalate only when the pressure sits at a boundary between worlds, when locality inside a world changes correctness, or when descriptions indexed by a composed world need a canonical product.

## Core patterns

```text
worlds + boundary + known side + unknown artifact + proof signal
  -> canonical boundary artifact
```

Spatial refinement:

```text
points + local patches + local/global identity + effective halo + continuity law
  -> locality-preserving world/boundary design
```

Description-composition refinement:

```text
index world + tensor/kernel + indexed descriptions + quotient + interpreter + resource law
  -> pointwise / Day / promonoidal / substitutional / sequential product
```

The artifact, spatial model, or description product is valuable only if it changes code shape, tests, static analysis, representable programs/states, or resource accounting.

## Ecosystem table

| Universal move | CS intuition | Boundary/spatial/description artifact |
| --- | --- | --- |
| Product | independent fields | record/object with projection tests |
| Coproduct | exclusive cases | ADT/sealed union with exhaustive handling |
| Equalizer/refined type | stable predicate once | checked constructor/wrapper |
| Pullback | two views agree on shared projection | witness pair with preserved projections |
| Pushout | two sources glue along explicit overlap | canonical integrated artifact with factorization/provenance |
| Exponential | behavior supplied as value | strategy/function seam |
| Free construction / initial algebra | syntax before interpretation | AST/IR plus interpreters |
| Freyd/AFT-style diagnostic | projection supports a free builder or obstruction | builder or obstruction for `P : B -> C` |
| Left Kan-style transport | source semantics moves to target | generation path / transported semantics |
| Right Kan-style observation | target satisfies old views | observation vocabulary / coherent facade |
| Kan lift-style realization | public behavior determines internals | realizer plus projection test |
| Residual obligation | public constraint implies internal checks | obligation IR plus failing counterexample |
| Behavioral coalgebra | ongoing behavior over time | state transition plus observation |
| Algebraic effects | operations need multiple handlers | operation syntax plus handlers |
| Freyd category | pure values coexist with ordered call-by-value effects | pure embedding + premonoidal sequencing + centrality law |
| Colored operad | typed components assemble hierarchically | ports/colors + substitution grammar + semantic algebras |
| PROP/properad | multiple-input/multiple-output network wiring | explicit network composition |
| Pointwise/Hadamard product | descriptions combine at one unchanged index | same-index pair/map + naturality law |
| Day convolution | descriptions combine over every tensor decomposition | indexed family + decomposition/normalization + lax-monoidal interpreter |
| Promonoidal convolution | composition is partial or relation-valued | admissibility kernel + witnessed composites + residuals |
| Free applicative / static Day monoid | full computation shape known before results | inspectable plan + analysis/execution interpreters |
| Resource convolution | predicates combine over legal resource splits | separating assertion + disjointness/admissibility law |
| Density comonad | local patches generate a space of situated context | subbasis/basis + coalgebras + reconstruction |
| Comonad coalgebra | object is coherently situated in local context | centered local view with nested-neighborhood coherence |
| Halo / germ | effective neighborhood and locally valid value | labelled locality index + restriction law |
| Continuous comonadic map | boundary preserves neighborhoods, not only points | point map + context transport + halo/label law |
| Spatial Day convolution | two locality descriptions compose through product patches | external-product subbasis + combined halos + continuous projections |
| Yoneda | object by observations | `Observation` plus `runObservation` |
| Coyoneda | payload plus deferred map | `Generated(payload,path)` plus `lowerGenerated` |
| Defunctionalization | callbacks/functions to data | first-order IR plus `apply` |

## Operating rule

Do not reach for advanced terms first. Ask:

1. Is a product/coproduct/refined type/pullback/exponential/free construction, labelled graph, plain context object, or pointwise product enough?
2. If not, is the smell a boundary artifact smell, a locality/spatiality smell, or an indexed-description composition smell?
3. For spatiality, can points, patches, local/global identity, an effective halo, and restriction/continuity laws be named?
4. For description composition, can an index world, tensor/unit or promonoidal kernel, indexed family, legal decompositions, quotient/normal form, interpreter, and resource bound be named?
5. Can a single witness slice and law test make the artifact honest?
6. Would the artifact prevent drift, duplication, hidden behavior, lossy projection, invalid state evolution, premature identity collapse, locality loss, illegal decomposition, or semantic collision?

If the answer to the applicable structure question, witness question, or value question is no, do not escalate. Record an ordinary solution or an obstruction.
