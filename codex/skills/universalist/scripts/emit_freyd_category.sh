#!/usr/bin/env bash
set -euo pipefail
focus="${1:-effect-boundary}"
language="${2:-agnostic}"
cat <<OUT
# Freyd Category / Effect Geometry Report (${focus}, ${language})

## Pressure

Where are pure values and effectful computations being composed as though their laws were identical?

## Pure world C

- objects/types:
- pure transformations:
- product/context structure:

## Effectful world K

- computations:
- observable effects:
- sequencing/evaluation order:

## Pure embedding J : C -> K

- code/module:
- identity/composition preservation:

## Centrality

- pure/central operations:
- effects claimed safe to reorder or parallelize:
- observational commutativity witness:
- noncommuting counterexample:

## Context action

- how values are threaded through computations:

## Higher-order requirement

- effectful functions first-class?:
- strong-monad/closed representation needed?:

## Law tests

- J(id) = id
- J(g . f) = J(g) . J(f)
- pure operations commute with effect context
- reordered effects agree observationally only when certified

## Falsifier
OUT
