#!/usr/bin/env bash
set -euo pipefail
focus="${1:-component-wiring}"
language="${2:-agnostic}"
cat <<OUT
# Operadic Architecture Report (${focus}, ${language})

## Pressure

What typed component wiring or hierarchical assembly is currently hidden in an accidental call graph?

## Colors / port types

## Primitive operations / components

- operation:
- inputs:
- output:

## Composite operation

## Substitution / wiring rules

## Symmetry / order

- symmetric / nonsymmetric / partially commutative:
- order-sensitive effects:

## Richer geometry

- genuine multiple outputs -> PROP/properad?:
- feedback/cycles -> traced/temporal/coalgebraic?:
- consumable resources -> linear/graded?:

## Semantic algebras

- production:
- test:
- simulation:
- cost/security/trace/documentation:

## Forbidden wiring

## First witness composition

## Law

interpret(substitute(f,g1,...,gn)) == compose(interpret(f), interpret(g1), ..., interpret(gn))

## Falsifier
OUT
