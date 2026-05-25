#!/usr/bin/env bash
set -euo pipefail
topic="${1:-published-context}"
language="${2:-agnostic}"
cat <<OUT
# Context Publication Boundary (${topic}, ${language})

## Boundary
Operational Source Snapshot -> Verified Context Snapshot -> Published Context -> Semantic Consumer

## Source snapshot
- snapshot ID:
- source versions:
- freshness requirements:
- access-control assumptions:

## Verified context snapshot
- schema:
- mappings:
- constraints:
- reconciliation:
- provenance manifest:

## Published context
- consumer:
- task:
- observables:
- rendering:
- certificate:

## Laws
- publication derives from stable source snapshot:
- constraints pass or failures represented:
- provenance path exists for every evidence-bearing fact:
- semantic consumer reads published context, not raw live store:

## Falsifier
- direct raw source read:
- stale snapshot consumed:
- missing provenance:
- contradiction collapsed:
OUT
