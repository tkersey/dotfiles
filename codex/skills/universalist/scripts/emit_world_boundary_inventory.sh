#!/usr/bin/env bash
set -euo pipefail
focus="${1:-architecture}"
language="${2:-agnostic}"
cat <<OUT
# World / Boundary Inventory (${focus}, ${language})

## Worlds

### World 1
- Objects:
- Transformations:
- Invariants:
- Observations:
- Primitives:
- Composition rules:
- Equality/coherence notion:
- Quality diagnostic:

### World 2
- Objects:
- Transformations:
- Invariants:
- Observations:
- Primitives:
- Composition rules:
- Equality/coherence notion:
- Quality diagnostic:

## Boundaries

### Boundary
- Kind: embedding / projection / forgetful / interpreter / compiler / serializer / view / handler / observer / migration / adapter
- Source world:
- Target world:
- Preserved:
- Forgotten:
- Generated:
- Observed:
- Unknown location:
- Candidate artifact:
- Law test:
- Falsifier:

## Drift

- semantic drift:
- observation drift:
- implementation drift:
- generation drift:
- control-flow drift:
- behavioral drift:
- effect drift:

## Candidate artifact

## First witness slice

## Stop condition
OUT
