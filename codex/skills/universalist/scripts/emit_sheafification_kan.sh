#!/usr/bin/env bash
set -euo pipefail
focus="${1:-abstraction}"
language="${2:-agnostic}"
cat <<OUT
# Sheafification Kan Report (${focus}, ${language})

## Handoff from universalist

- abstraction:
- usage site:
- local sections:
- overlaps:
- sheaf failure:
- possibility-envelope gap:
- witness slice:

## Categorical repair

- construction:
- data required:
- unit/counit/comparison/factorization if applicable:
- nearby alternatives rejected:

## Replacement artifact

- representation:
- constructors/schema/IR:
- interpreter/projection/lowering:

## Laws

- compatibility law:
- existence/gluing law:
- uniqueness/normalization law:
- falsifier:

## Migration

- files:
- adapter compatibility:
- bypass removal:
OUT
