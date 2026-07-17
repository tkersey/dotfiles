# Universal Architecture Ecosystem

Universal architecture is the practice of designing software around canonical boundary artifacts and effective spatial structure when locality is semantic:

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
comonadic spaces, density bases, halos, germs, and continuous boundaries
explicit IRs
law tests
```

This extends the ordinary `universalist` construction ladder. Products, coproducts, refined types, pullbacks, exponentials, free constructions, labelled graphs, and plain context objects remain the first choices. Escalate only when the pressure sits at a boundary between worlds or when locality inside a world changes correctness.

## Core pattern

```text
worlds + boundary + known side + unknown artifact + proof signal
  -> canonical boundary artifact
```

Spatial refinement:

```text
points + local patches + local/global identity + effective halo + continuity law
  -> locality-preserving world/boundary design
```

The artifact or spatial model is valuable only if it changes code shape or tests.

## Ecosystem table

| Universal move | CS intuition | Boundary/spatial artifact |
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
| Density comonad | local patches generate a space of situated context | subbasis/basis + coalgebras + reconstruction |
| Comonad coalgebra | object is coherently situated in local context | centered local view with nested-neighborhood coherence |
| Halo / germ | effective neighborhood and locally valid value | labelled locality index + restriction law |
| Continuous comonadic map | boundary preserves neighborhoods, not only points | point map + context transport + halo/label law |
| Yoneda | object by observations | `Observation` plus `runObservation` |
| Coyoneda | payload plus deferred map | `Generated(payload,path)` plus `lowerGenerated` |
| Defunctionalization | callbacks/functions to data | first-order IR plus `apply` |

## Operating rule

Do not reach for advanced terms first. Ask:

1. Is a product/coproduct/refined type/pullback/exponential/free construction, labelled graph, or plain context object enough?
2. If not, is the smell a boundary artifact smell or a locality/spatiality smell?
3. For spatiality, can points, patches, local/global identity, an effective halo, and restriction/continuity laws be named?
4. Can a single witness slice and law test make the artifact honest?
5. Would the artifact prevent drift, duplication, hidden behavior, lossy projection, invalid state evolution, premature identity collapse, or locality loss?

If the answer to 3, 4, or 5 is no, do not escalate. Record an ordinary solution or an obstruction.