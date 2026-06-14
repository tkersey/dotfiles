# Category pivot mechanics

Universalist chooses a pivot when the current world hides the hard operation. Mechanics elaborate the transfer.

## Mechanical questions

1. Is the current world executable code, raw data, traces, schemas, policies, or local usage sections?
2. What operation is hard: equality, inspection, minimization, synthesis, proof, merge, authorization, replay, serialization?
3. Which world makes it easy?
4. What is the encoding functor/map into that world?
5. What is the interpretation or observation map back?
6. What law preserves the relevant observable?
7. What loss or approximation is explicit?

## Common mechanics

- executable behavior -> syntax/IR: free construction or defunctionalization;
- concrete state -> abstract domain: Galois-connection-like approximation;
- runtime protocol -> coalgebra/traces: step and observe;
- source data -> context schema: data exchange/migration/chase/core;
- usage contexts -> presheaf/site: local sections and gluing;
- resource behavior -> resource model: capabilities and separation;
- partial/bidirectional behavior -> relation/profunctor: compatibility and optics.
