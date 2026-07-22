# Universal Architecture Ecosystem

Universal architecture is the practice of designing software around canonical boundary artifacts, compositional change calculi, lawful composition of indexed descriptions, lawful context actions on generalized morphisms, and effective spatial structure when locality is semantic:

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
double categories, equipments, compatibility squares, and interchange
pointwise, Day, and promonoidal description products
Tambara modules and optic/residual-context morphisms
comonadic spaces, density bases, halos, germs, and continuous boundaries
explicit IRs
law tests
```

This extends the ordinary construction ladder. Products, coproducts, refined types, pullbacks, exponentials, free constructions, labelled graphs, context objects, profunctors, explicit residual records, one compatibility witness, and pointwise products remain first choices. Escalate only when pressure sits at a boundary, when two independently compositional arrow directions require typed square compatibility, when locality changes correctness, when indexed descriptions need a canonical product, or when a generalized morphism must survive context action.

## Core patterns

```text
worlds + boundary + known side + unknown artifact + proof signal
  -> canonical boundary artifact
```

Two-dimensional refinement:

```text
horizontal processes + vertical changes + typed squares + both pastings
+ interchange/coherence + double-functor lowering + resource/invalidation law
  -> compositional change architecture
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

Contextual-morphism refinement:

```text
context world + endpoint actions + profunctor + frame + laws + realizer/effect owner
  -> ordinary / Tambara / mixed / free-cofree / dependent / representable morphism
```

The artifact, square calculus, spatial model, description product, or context action is valuable only if it changes code shape, tests, analysis, migration/refactor composition, representable states/morphisms, or resources.

## Ecosystem table

| Universal move | CS intuition | Boundary/spatial/description/context artifact |
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
| Freyd category | pure values coexist with ordered effects | pure embedding + premonoidal sequencing + centrality law |
| Colored operad | typed components assemble hierarchically | ports/colors + substitution grammar + semantic algebras |
| PROP/properad | multiple-input/multiple-output network wiring | explicit network composition |
| Double category | processes and changes compose independently | horizontal/vertical arrow IR + typed squares + pasting + interchange |
| Pseudo double category | composition is canonical only up to coherence | square normal form + associator/unitor witnesses |
| Equipment / framed bicategory | strict maps reindex generalized boundaries | companion/conjoint/restriction API + base-change laws |
| Virtual double category | generalized cells exist without total loose composition | multi-source cell IR + explicit partiality |
| Double functor | one two-dimensional architecture has several semantics | compiler/simulator/query/cost/security interpretation |
| Pointwise/Hadamard product | descriptions combine at one unchanged index | same-index pair/map + naturality law |
| Day convolution | descriptions combine over every tensor decomposition | indexed family + decomposition/normalization + lax-monoidal interpreter |
| Promonoidal convolution | composition is partial or relation-valued | admissibility kernel + witnessed composites + residuals |
| Free applicative / static Day monoid | full computation shape known before results | inspectable plan + analysis/execution interpreters |
| Resource convolution | predicates combine over legal resource splits | separating assertion + disjointness/admissibility law |
| Tambara module | generalized capability survives context action | profunctor + frame/strength + coherence laws |
| Mixed Tambara module | context acts differently on source and target | separate endpoint actions + framed profunctor |
| Optic/double | focus plus residual rebuilds a whole | residual IR + decompose/rebuild + Tambara interpreter |
| Free/cofree Tambara | all legal frames generated or observed | effective context basis + closure/observation laws |
| Dependent Tambara | context changes endpoint indices | double-category action + typed frame transport |
| Tambara representability | generalized morphism is or is not a real map | module functor/adapter witness or obstruction |
| Density comonad | local patches generate situated context | subbasis/basis + coalgebras + reconstruction |
| Comonad coalgebra | object is coherently situated | centered local view + neighborhood coherence |
| Halo / germ | effective neighborhood and locally valid value | labelled locality index + restriction law |
| Continuous comonadic map | boundary preserves neighborhoods | point map + context transport + halo/label law |
| Spatial Day convolution | locality descriptions compose through product patches | external-product subbasis + combined halos |
| Spatial Tambara framing | transformation survives halo/context extension | halo action + framed profunctor + continuity law |
| Yoneda | object by observations | `Observation` plus `runObservation` |
| Coyoneda | payload plus deferred map | `Generated(payload,path)` plus `lowerGenerated` |
| Defunctionalization | callbacks/functions to data | first-order IR plus `apply` |

## Operating rule

Do not reach for advanced terms first. Ask:

1. Is a product/coproduct/refined type/pullback/exponential/free construction, labelled graph, context object, profunctor/adapter, residual record, one compatibility witness, or pointwise product enough?
2. If not, is the smell boundary artifact, two-dimensional process/change composition, locality, indexed-description composition, or context framing?
3. For double categories, can two semantically distinct arrow families, both compositions, typed squares, both pastings, interchange/coherence, an interpreter, and resources be named?
4. For equipment, can companions, conjoints, or restrictions and base-change laws be realized for admitted strict maps?
5. For spatiality, can points, patches, local/global identity, effective halo, and continuity be named?
6. For description composition, can index world, tensor/kernel, descriptions, decompositions, quotient, interpreter, and resource bound be named?
7. For contextual morphisms, can context world, endpoint actions, profunctor, frame, laws, representability, and effect owner be named?
8. Can one witness slice and law test make it honest?
9. Would it prevent drift, hidden behavior, mismatched squares, noncompositional migrations, invalid states, lost provenance, illegal composition, locality loss, or framing inconsistency?

If the answer to the applicable structure, witness, or value question is no, do not escalate. Record an ordinary solution or obstruction.
