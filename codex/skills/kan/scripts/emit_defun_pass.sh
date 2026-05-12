#!/usr/bin/env bash
set -euo pipefail
focus="${1:-boundary-ir}"
language="${2:-agnostic}"
cat <<OUT
# Defunctionalization pass (${focus}, ${language})

## Higher-order values crossing boundary
- callback / continuation / selector / handler / predicate / builder:
- captured free variables:

## First-order constructors
- Case:
- Payload fields:

## Interpreter
- apply / interpret / project / satisfy:

## Law
apply(encodedCase, input) == oldFunction(input)
OUT
