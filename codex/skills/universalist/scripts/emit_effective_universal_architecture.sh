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
- state / behavioral coalgebra / protocol:
- canonical constructions:
- base composition geometries:
- presentation strategies:

## Description composition, when applicable
- index worlds/categories:
- tensors / promonoidal kernels:
- units:
- indexed description families:
- selected products: pointwise / Day / promonoidal / substitution / endofunctor composition
- atomic/representable embeddings:
- legal decomposition/admissibility witnesses:
- coend/reindexing equivalences:
- executable representations:
- enumeration / aggregation / normalization:
- lax-monoidal interpreters:
- residuals/internal homs:
- effect-order restrictions:
- collision/provenance policy:
- complexity/resource bounds:

## Spatial worlds, when applicable
- points:
- local patch vocabularies / subbases:
- basis / reconstruction claims:
- local points / global points / identification maps:
- comonads or practical spatial approximations:
- coalgebras / situated objects:
- representative and labelled halos:
- germ / restriction semantics:
- continuous locality-preserving boundaries:
- spatial Day products / external-product patches:
- topological/category shadows and forgotten observations:
- effective representation / invalidation:

## Resource model
- time / space:
- latency / throughput:
- concurrency / failure:
- security / capability:
- persistence / deployment:
- halo size / traversal / basis reconstruction:
- spatial index freshness / invalidation:
- description support / decomposition count:
- quotient / normalization cost:
- convolution cache / invalidation:

## Laws, falsifier, obstruction
- soundness:
- adequacy/completeness:
- observation law:
- Day representable/unit/associativity law:
- decomposition soundness/completeness:
- coend/quotient coherence:
- description interpretation/lax-monoidal law:
- promonoidal admissibility/residual law:
- effect-order law:
- center/counit and neighborhood coherence:
- restriction/germ law:
- basis-density/reconstruction law:
- continuity/labelled-halo law:
- local/global identity/provenance law:
- resource claim:
- strongest falsifier:
- obstruction / approximation:

## Witness seam
- first end-to-end slice:
- indexed description / composite:
- local/spatial context:
- negative decomposition/collision witness:
- verification commands:
- stop point:
OUT
