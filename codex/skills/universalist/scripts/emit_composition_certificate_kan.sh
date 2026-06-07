#!/usr/bin/env bash
set -euo pipefail
mode="${1:-elaboration}"
language="${2:-agnostic}"
cat <<OUT
# Kan Composition Certificate elaboration (${mode}, ${language})

## Certificate fields

- worlds:
- boundary kind:
- known side:
- unknown location:
- canonical artifact:
- interpreter/projection/lowering/handler:
- law witness:
- falsifier:
- bypass policy:

## Kan mechanics

- axis: extension / lift / representation / control-flow
- candidate: Lan / Ran / Delta / Lft / Rft / Yoneda / Coyoneda / defunctionalized IR / Freyd builder / obstruction
- formal data:
- comparison/unit/counit/cell:

## Implementation witness

- artifact data type/module:
- interpreter/projection/lowering/apply function:
- positive test:
- negative witness:

## Certificate status

verified / obstructed / approximate / planned / primitive exception
OUT
