#!/usr/bin/env bash
set -euo pipefail
topic="${1:-context-publication}"
language="${2:-agnostic}"
cat <<OUT
# CQL / Categorical Database Context Report (${topic}, ${language})

## Task and semantic consumer
- task:
- consumer:
- consumption time:

## Source schemas and instances
- operational stores:
- source snapshots:
- source schema(s):
- candidate instance(s):

## Target context schema
- typeside / value theory:
- entities:
- attributes:
- foreign keys:
- equations / constraints:

## Mappings and queries
- source-to-target mappings:
- query / view definitions:
- Delta / Sigma / Pi usage:
- Pi risks or avoidance:

## Verification
- constraints:
- chase/closure:
- theorem/proof/checking obligations:
- missingness/contradiction representation:

## Reconciliation
- overlap schema:
- overlap instance:
- pushout/colimit plan:
- conflict policy:

## Provenance and publication
- lineage plan:
- provenance manifest:
- published context snapshot:
- context certificate:
- rendering law:

## Fit assessment
- why CQL-like tooling fits:
- why operational store remains separate:
- non-fit risks:
OUT
