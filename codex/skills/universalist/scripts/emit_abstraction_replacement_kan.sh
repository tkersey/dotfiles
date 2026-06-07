#!/usr/bin/env bash
set -euo pipefail
focus="${1:-replacement}"
language="${2:-agnostic}"
cat <<OUT
# Abstraction Replacement Elaboration (${focus}, ${language})

## Exactness gap

- impossible states admitted:
- valid states omitted:
- redundant meanings:
- local inconsistency:

## Construction selector

Choose one:
- product / coproduct / equalizer / pullback
- free syntax / initial algebra
- coequalizer / quotient / normalization
- Kan extension / transported semantics
- Kan lift / realizer / residual obligation
- Yoneda observation vocabulary
- Coyoneda payload + path
- defunctionalized IR
- effect signature + handlers
- behavioral coalgebra
- Exact Context / Context Certificate

## Law tests

- positive:
- negative / falsifier:
- uniqueness or normalization:

## Implementation witness

- first file:
- first constructor/schema/IR:
- interpreter/projection:
- stop point:
OUT
