#!/usr/bin/env bash
set -euo pipefail
topic="${1:-context-merge}"
language="${2:-agnostic}"
cat <<OUT
# Pushout Reconciliation Plan (${topic}, ${language})

## Inputs
- Context A:
- Context B:
- Additional contexts:

## Overlap
- Overlap schema:
- Overlap instance:
- Identity correspondences:
- Attributes safe to identify:
- Attributes not safe to identify:

## Integration
- Target integrated schema:
- Pushout/colimit approximation:
- Conflict policy:
- Provenance survival:

## Laws
- non-overlap preservation:
- explicit overlap identity:
- conflict surfaced or resolved by policy:
- integrated constraints satisfied:
- provenance path survives:

## Falsifiers
- false merge:
- silent conflict collapse:
- lost provenance:
OUT
