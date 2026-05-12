#!/usr/bin/env bash
set -euo pipefail
focus="${1:-boundary}"
language="${2:-agnostic}"
cat <<OUT
# World / Boundary Preamble (${focus}, ${language})

## Worlds

### Source / known world
- Objects:
- Transformations:
- Invariants:
- Observations:
- Primitives:
- Composition rules:
- Equality/coherence notion:

### Target / observable / implementation world
- Objects:
- Transformations:
- Invariants:
- Observations:
- Primitives:
- Composition rules:
- Equality/coherence notion:

## Boundary

- Kind:
- Source world:
- Target world:
- Known side:
- Unknown location:
- Preserved:
- Forgotten:
- Generated:
- Observed:
- Candidate artifact:
- Law:
- Falsifier:
OUT
