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

## Falsifier

- missing required context:
- irrelevant distracting context:
- stale context:
- unsupported claim:

## Status

planned / verified / stale / missing / contradictory / overfull / undercertified
OUT
