#!/usr/bin/env bash
set -euo pipefail
mode="${1:-report}"
language="${2:-agnostic}"
cat <<OUT
# Context Compilation Report (${mode}, ${language})

## Task q and semantic consumer

- task:
- consumer: model / human / policy engine / planner / workflow / ranker / tool selector
- consumption time:

## Source worlds and source schema S

- source worlds:
- candidate source instance I_candidate:
- retrieval/tool/memory/log methods:
- source versions:
- freshness requirements:

## Task context schema T_q

- entities:
- relations:
- constraints:

## Observables Obs_q

- required observables:
- distinctions to preserve:
- missingness/contradictions to expose:
- may discard:

## Mapping M_q

- source-to-context mapping:
- Delta/restriction/projection:
- Sigma/merge/coalesce:
- Pi/join/compatible completion:

## Chase / closure

- deterministic constraints:
- equality/entity resolution:
- unit/date normalization:
- unsupported claim detection:

## Provenance / missingness / contradiction

- Claim -> Evidence -> Source paths:
- DerivedFact -> Derivation -> Inputs paths:
- MissingEvidence objects:
- Contradiction objects:
- AmbiguousEntity objects:

## Observational core

- retained items:
- discarded items:
- minimality law:

## Rendering

- prompt/report/JSON/tool-arg/dashboard renderer:
- token/bandwidth/layout budget:
- lossy rendering declarations:
- rendering law:

## Context Certificate

- schema law:
- observable preservation law:
- provenance law:
- freshness law:
- missingness/contradiction law:
- rendering law:
- falsifiers:
OUT
