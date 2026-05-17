#!/usr/bin/env bash
set -euo pipefail
focus="${1:-audit}"
cat <<OUT
# Boundary Normal Form plan (${focus})

## Inventory

- certified boundaries:
- uncertified boundaries:
- primitive exceptions:
- obstructed boundaries:

## Next highest-leverage certificate

- boundary:
- signal:
- worlds:
- expected artifact:
- expected law:
- expected falsifier:
- bypasses to remove:

## Accretive plan

1. Write Composition Certificate.
2. Add/centralize artifact.
3. Add interpreter/projection/lowering/handler.
4. Add positive law.
5. Add falsifier.
6. Remove one bypass.
7. Mark status verified/obstructed/primitive exception.
OUT
