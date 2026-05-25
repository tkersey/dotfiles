#!/usr/bin/env bash
set -euo pipefail
topic="${1:-publication-boundary}"
language="${2:-agnostic}"
cat <<OUT
# Verified Context Publication Plan (${topic}, ${language})

## Boundary
Operational Source Snapshot -> Verified Context Snapshot -> Published Context -> Semantic Consumer

## Operational source plane
- stores:
- write/transaction owners:
- authorization owners:
- snapshot method:

## Verified context plane
- schema:
- mappings:
- constraints:
- provenance:
- reconciliation:

## Publication
- published context shape:
- certificate:
- validity interval:
- invalidation triggers:

## Rendering / consumer
- rendering form:
- observables preserved:
- consumer:

## Laws
- source snapshot stability:
- schema/constraint law:
- provenance law:
- freshness law:
- no raw live-store bypass:
OUT
