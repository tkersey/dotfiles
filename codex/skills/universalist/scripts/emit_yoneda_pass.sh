#!/usr/bin/env bash
set -euo pipefail
focus="${1:-observation}"
language="${2:-agnostic}"
cat <<OUT
# Yoneda/Coyoneda pass (${focus}, ${language})

## Yoneda observations
- Observation constructors:
- Subject:
- runObservation signature:
- Coherence/representation law:

## Coyoneda generated paths
- Raw payloads:
- Path constructors:
- Generated record:
- lowerGenerated signature:
- Lowering/provenance law:

## Combined law
runObservation(obs, lowerGenerated(generated)) == expected(obs)
OUT
