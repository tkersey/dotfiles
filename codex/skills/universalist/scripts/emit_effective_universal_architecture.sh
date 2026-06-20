#!/usr/bin/env bash
set -euo pipefail
focus="${1:-system}"
language="${2:-agnostic}"
cat <<OUT
# Effective Universal Architecture Certificate — ${focus} (${language})

## System and observations
- capability:
- external worlds:
- required observable behavior:
- equivalence notion:

## Effective computational substrate
- program representation:
- evaluator / interpreter / compiler:
- recursion / partiality mechanism:
- state / interaction:
- target runtime:

## Concrete Primitive Register
- primitive:
- handler:
- failures:
- resources:
- observations / test double:

## Categorical architecture
- worlds and boundaries:
- syntax and semantics:
- effects and handlers:
- state / coalgebra / protocol:
- canonical constructions:
- presentation strategy:

## Resource model
- time / space:
- latency / throughput:
- concurrency / failure:
- security / capability:
- persistence / deployment:

## Laws, falsifier, obstruction
- soundness:
- adequacy/completeness:
- observation law:
- resource claim:
- strongest falsifier:
- obstruction / approximation:

## Witness seam
- first end-to-end slice:
- verification commands:
- stop point:
OUT
