# Universal Architecture Ecosystem

Universal architecture is the practice of designing software around canonical boundary artifacts:

```text
free syntax
coherent observations
transported semantics
lifted implementations
free builders behind projections
obstruction reports
behavioral coalgebras
effect signatures with handlers
explicit IRs
law tests
```

This extends the ordinary `universalist` construction ladder. Products, coproducts, refined types, pullbacks, exponentials, and free constructions remain the first choices. Escalate only when the pressure sits at a boundary between worlds.

## Core pattern

```text
worlds + boundary + known side + unknown artifact + proof signal
  -> canonical boundary artifact
```

The boundary artifact is valuable only if it changes code shape or tests.

## Ecosystem table

| Universal move | CS intuition | Boundary artifact |
| --- | --- | --- |
| Product | independent fields | record/object with projection tests |
| Coproduct | exclusive cases | ADT/sealed union with exhaustive handling |
| Equalizer/refined type | stable predicate once | checked constructor/wrapper |
| Pullback | two views agree on shared projection | witness pair with preserved projections |
| Exponential | behavior supplied as value | strategy/function seam |
| Free construction / initial algebra | syntax before interpretation | AST/IR plus interpreters |
| Freyd/AFT-style diagnostic | projection supports a free builder or obstruction | builder or obstruction for `P : B -> C` |
| Left Kan-style transport | source semantics moves to target | generation path / transported semantics |
| Right Kan-style observation | target satisfies old views | observation vocabulary / coherent facade |
| Kan lift-style realization | public behavior determines internals | realizer plus projection test |
| Residual obligation | public constraint implies internal checks | obligation IR plus failing counterexample |
| Behavioral coalgebra | ongoing behavior over time | state transition plus observation |
| Algebraic effects | operations need multiple handlers | operation syntax plus handlers |
| Yoneda | object by observations | `Observation` plus `runObservation` |
| Coyoneda | payload plus deferred map | `Generated(payload,path)` plus `lowerGenerated` |
| Defunctionalization | callbacks/functions to data | first-order IR plus `apply` |

## Operating rule

Do not reach for advanced terms first. Ask:

1. Is a product/coproduct/refined type/pullback/exponential/free construction enough?
2. If not, is the smell a boundary artifact smell?
3. Can a single witness slice and law test make the artifact honest?
4. Would the artifact prevent drift, duplication, hidden behavior, lossy projection, or invalid state evolution?

If the answer to 3 or 4 is no, do not escalate.
