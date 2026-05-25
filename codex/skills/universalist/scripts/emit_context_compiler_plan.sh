#!/usr/bin/env bash
set -euo pipefail
kind="${1:-semantic-consumer}"
language="${2:-agnostic}"
cat <<OUT
# Context Compiler Plan (${kind}, ${language})

## Pipeline

Task q
  -> select_schema(q) = T_q
  -> select_observables(q) = Obs_q
  -> build_candidate_source_instance(q) = I_candidate
  -> migrate_{M_q}(I_candidate)
  -> chase / deterministic closure
  -> provenance + missingness + contradiction structure
  -> observational_core_{Obs_q}
  -> render(Context(q))
  -> semantic consumer

## Modules

- task classifier:
- schema registry:
- observable selector:
- source-instance builder:
- mapping engine:
- constraint/closure engine:
- provenance engine:
- contradiction/missingness engine:
- observational-core minimizer:
- renderer:
- certificate logger:

## First witness task

- task:
- source data:
- required observables:
- expected context object:
- expected rendering:

## Verification

- source-to-context mapping test:
- schema constraint test:
- provenance path test:
- freshness test:
- minimality/falsifier test:
- rendering preservation test:
OUT
