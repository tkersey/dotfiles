#!/usr/bin/env bash
set -euo pipefail
mode="${1:-boundary-diagnostic}"
language="${2:-agnostic}"
case "$mode" in
  boundary-diagnostic|diagnostic)
    cat <<OUT
# Freyd/AFT Boundary Diagnostic (${language})

## Lift shape

- A = public cases / requirements:
- B = internal implementation world:
- C = observable behavior world:
- P : B -> C = projection/observer:
- F : A -> C = required behavior:

## What P forgets or observes

## Constraint structure available in B

- products / combined requirements:
- equalities / agreement checks:
- pullbacks / shared interfaces:
- workflow or state composition:
- validation or normalization:

## Does P preserve those constraints?

## Solution-set-like template family

For each public requirement, list bounded implementation templates.

## Candidate Free : C -> B / realizer / obligation artifact

## Law classification

- exact: P(Free(c)) == c
- covering: c embeds into P(Free(c))
- sound: P(Free(c)) satisfies c
- approximate: documented approximation

## Obstruction, if any

## First witness test
OUT
    ;;
  free-builder|builder)
    cat <<OUT
# Free Builder Plan (${language})

## Required behavior type C

## Internal realizer type B

## Builder

free : RequiredBehavior -> FreeRealizer

## Projection

project : FreeRealizer -> PublicBehavior

## Template cases

## Tests

project(free(required(case))) satisfies required(case)

## Negative fixtures

- missing evidence
- unsupported template
- projection loses data
OUT
    ;;
  obstruction|no-exact-lift)
    cat <<OUT
# No-Exact-Lift Obstruction Report (${language})

## Required behavior that cannot be realized

## Projection P that loses or hides evidence

## Missing internal data / structure / template

## Options

1. enrich B
2. enrich P
3. weaken F
4. introduce obligation IR

## Failing witness

## Smallest next seam
OUT
    ;;
  *) echo "Unknown mode: $mode" >&2; exit 2 ;;
esac
