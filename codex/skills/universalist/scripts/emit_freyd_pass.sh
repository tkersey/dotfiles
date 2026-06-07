#!/usr/bin/env bash
set -euo pipefail
focus="${1:-boundary-diagnostic}"
language="${2:-agnostic}"
cat <<OUT
# Freyd/AFT boundary diagnostic (${focus}, ${language})

## Projection
- P : B -> C0:
- What P observes:
- What P forgets:

## Constraint structure in B
- products/pullbacks/equalizers/joins/meets/workflow composition/validations:

## Preservation test
- Law:

## Solution-set-like templates
- Template family:

## Free builder or obstruction
- Candidate Free : C0 -> B:
- Projection law: P(Free(required(case))) satisfies required(case)
- Obstruction if no builder:
OUT
