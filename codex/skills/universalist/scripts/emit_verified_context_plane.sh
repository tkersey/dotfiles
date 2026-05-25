#!/usr/bin/env bash
set -euo pipefail
topic="${1:-semantic-consumer}"
language="${2:-agnostic}"
cat <<OUT
# Verified Context Plane Plan (${topic}, ${language})

## Semantic consumer
- Consumer:
- Decision/action/execution:
- Consumption time:

## Operational Source Plane
- Sources:
- Mutation owners:
- Transaction/freshness model:
- Access-control owner:

## Candidate Plane
- Retrieval/extraction methods:
- Candidate source instance:
- Snapshot boundary:

## Verified Context Plane
- Context schema:
- Source-to-context mappings:
- Constraints:
- Entity resolution / reconciliation:
- Provenance requirements:
- Missingness/contradiction representation:

## Publication Plane
- Published context snapshot:
- Context Certificate location:
- Freshness / invalidation triggers:

## Rendering Plane
- Renderer:
- Preserved observables:
- Lossy rendering steps:

## Laws
- schema law:
- mapping law:
- provenance law:
- freshness law:
- publication law:
- rendering law:
- raw source bypass falsifier:
OUT
