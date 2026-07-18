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

## Context actions and Tambara modules, when applicable
- ambient context worlds/categories:
- tensors/units/partial or dependent composition:
- endpoint worlds and source/target actions:
- underlying profunctors/generalized capabilities:
- Tambara forms: ordinary / mixed / two-sided / dependent
- frame/strength operations:
- unit/associativity/naturality/coherence laws:
- optic/residual representations and normal forms:
- free contextual closures:
- cofree/all-context observation surfaces:
- representability/module-functor witnesses:
- nonrepresentability obstructions:
- Day-center/Cayley hypotheses, if claimed:
- Context Certificate agreements:
- effect-order/resource owners:
- effective residual/framing implementations:

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
- spatial Tambara actions / halo framing:
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
- context frame count / residual size:
- framing normalization / cache / invalidation:
- representability/realizer cost:

## Laws, falsifier, obstruction
- soundness:
- adequacy/completeness:
- observation law:
- Day representable/unit/associativity law:
- decomposition soundness/completeness:
- coend/quotient coherence:
- description interpretation/lax-monoidal law:
- promonoidal admissibility/residual law:
- Tambara unit/associativity/naturality law:
- context reindexing/coherence law:
- context-framing interpretation law:
- optic residual/domain law:
- free/cofree contextual closure law:
- representability/module-functor law:
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
- local capability / context frame:
- residual / optic path:
- local/spatial context:
- negative decomposition/collision/framing witness:
- verification commands:
- stop point:
OUT
