#!/usr/bin/env bash
set -euo pipefail
kind="${1:-generic}"
language="${2:-agnostic}"
cat <<OUT
# Composition Certificate scaffold (${kind}, ${language})

## Worlds

Source world:
- objects:
- transformations:
- invariants:
- observations:
- primitives:
- composition rules:

Target world:
- objects:
- transformations:
- invariants:
- observations:
- primitives:
- composition rules:

## Boundary

- name:
- kind: embedding / projection / forgetful / interpreter / compiler / serializer / view / handler / observer / migration / adapter
- function or module:
- preserved:
- forgotten:
- generated:
- observed:

## Unknown

- location: after boundary / behind boundary / inside syntax / behavior / effects / observation / generation / callback

## Canonical artifact

- artifact:
- why this artifact:
- nearby alternative rejected:

## Composition grammar

- geometry: category / monoidal / Freyd-premonoidal / operad / PROP-properad / traced-coalgebraic / resource-sensitive
- colors / port types:
- primitive operations / components:
- substitution / wiring rules:
- symmetry / ordering / centrality:
- multiple-output / feedback / resource requirements:
- forbidden wiring / effect reorderings:
- semantic algebras / interpretations:

## Effect geometry

- pure world/category:
- effectful world/category:
- pure embedding J:
- central operations:
- evaluation order:
- context action / value threading:
- certified commuting or parallel operations:
- noncommuting witness:

## Primitive effects

- allowed primitives:
- where they enter:
- containment rule:

## Interpreter / projection / lowering / handler

- function:
- owner module:
- bypass prevention:

## Law witness

- positive law test:
- falsifier / negative witness:

## Status

planned / implemented / verified / obstructed / primitive exception
OUT
