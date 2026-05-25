#!/usr/bin/env bash
set -euo pipefail
topic="${1:-context-boundary}"
language="${2:-agnostic}"
cat <<OUT
# CQL / Categorical Database Fit Assessment (${topic}, ${language})

## Boundary
- Source worlds:
- Target context schema:
- Semantic consumer:
- Publication cadence:

## Use CQL-like tooling if
- explicit schemas:
- source-to-target mappings:
- constraints/invariants:
- provenance/lineage:
- cross-source integration:
- snapshot publication acceptable:

## Avoid CQL as primary substrate if
- low-latency mutable writes:
- distributed multi-writer state:
- row-level dynamic authorization:
- streaming-first semantics:
- schema instability:

## Recommended mode
- lightweight / SQL / Datalog / CQL / hybrid:
- operational store:
- verified context plane:
- publication boundary:

## Law tests
- schema/mapping law:
- constraint law:
- provenance law:
- publication law:
- rendering law:

## Falsifiers
- raw source bypass:
- stale snapshot:
- unmapped source fact:
- lost provenance:
- unresolved conflict:
OUT
