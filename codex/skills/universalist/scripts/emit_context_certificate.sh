#!/usr/bin/env bash
set -euo pipefail
topic="${1:-context}"
language="${2:-agnostic}"
cat <<OUT
# Context Certificate scaffold (${topic}, ${language})

## Task

- task:
- task type:
- semantic consumer:
- consumption time:

## Context schema T_q

- entities:
- relations:
- constraints:

## Observables Obs_q

- required observables:
- must preserve:
- may discard:
- uncertainty/missingness to expose:

## Spatial locality, when applicable

- applicable: yes / no
- task point:
- spatial world:
- patch vocabulary / subbasis:
- basis or coverage claim:
- effective halo approximation:
- halo budget / invalidation:
- local points:
- global point:
- local-to-global identity map:
- restriction / germ rules:
- labelled-halo fields:
- continuity requirements:

## Requirement-indexed composition, when applicable

- applicable: yes / no
- requirement index world:
- requirement tensor or promonoidal kernel:
- unit requirement:
- context fragment family:
- selected product: pointwise / Day / promonoidal / ordinary
- nearby product rejected:
- legal requirement decompositions:
- coend/reindexing equivalence:
- fragment schema/provenance combination:
- residual / missing-context operation:
- enumeration / normalization strategy:
- collision policy:
- effectivity/resource bound:

## Source instance I_candidate

- source worlds:
- retrieval/candidate-generation methods:
- source versions:
- freshness requirements:
- provenance roots:

## Mapping M_q

- source-to-context mapping:
- entity resolution:
- evidence extraction:
- joins/links:
- unit/date normalization:

## Constraint closure / chase-like steps

- constraints enforced:
- equalities propagated:
- missing fields represented:
- contradictions represented:
- unsupported claims represented:

## Observational core

- retained data:
- removed data:
- minimality criterion:
- why retained items affect observables:

## Rendering

- renderer:
- token/bandwidth/layout budget:
- ordering/salience:
- lossy steps:
- rendering law:

## Law witnesses

- schema law:
- observable preservation law:
- provenance law:
- freshness law:
- missingness/contradiction law:
- rendering law:
- spatial center/counit law:
- restriction/germ law:
- continuity/halo-preservation law:
- local/global identity and labelled-halo law:
- spatial resource law:
- requirement decomposition soundness/completeness law:
- Day representable/unit/associativity law:
- context-fragment interpretation law:
- residual law:
- convolution resource/effectivity law:

## Falsifier

- missing required context:
- irrelevant distracting context:
- stale context:
- unsupported claim:
- point preserved but locality lost:
- local points collapsed before provenance:
- retrieved set mistaken for semantic halo:
- halo approximation omits an observation-changing dependency:
- invalid germ after boundary transport:
- illegal context decomposition admitted:
- legal context decomposition omitted:
- provenance collapsed under convolution quotient:
- context union mislabeled as Day convolution:

## Status

planned / verified / stale / missing / contradictory / overfull / undercertified / discontinuous / non-effective
OUT
